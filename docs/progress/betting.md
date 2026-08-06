# 2026 Fantasy Draft Model — Full Progress Summary

This is a full walkthrough of everything built so far, the bugs found and fixed along
the way, and — most importantly — an unresolved issue discovered in the last step that
should be resolved before you trust the draft board.

---

## The Goal

Turn `gold.playergame` (26 seasons of NFL box-score data, 1999–2025) into a ranked
2026 fantasy draft board for a **12-team, full-PPR, 1QB/2RB/2WR/1TE/1FLEX** league —
using your own historical stats plus real 2026 ADP data, rather than trusting a
generic public projection source.

---

## Step 1 — SQL Feature Aggregation (`01_player_season_features.sql`)

Rolled the game-level table up to one row per `(player_id, season)`: volume stats
(targets, carries, attempts), efficiency (yards/target, catch rate, etc.), team
context (pace, red zone rate), a within-season trend signal (last 4 games vs. season
average), and later, target share / rush share.

**Two real bugs found and fixed here:**

1. **Alias collision (`ILLEGAL_AGGREGATION` error).** Writing `sum(targets) AS
   targets` caused ClickHouse to substitute the alias back into later expressions
   that also referenced `targets`, producing an aggregate nested inside another
   aggregate. Fixed by renaming output columns (`total_targets`, `total_receptions`,
   etc.) so they never collide with the source column name.

2. **Duplicate rows from `ReplacingMergeTree`.** The first real CSV export showed
   players with `games_played = 80` in a single season — impossible (max is ~17).
   `gold.playergame` uses `ReplacingMergeTree`, which only *logically* dedupes
   matching `(player_id, game_id)` rows once ClickHouse merges them in the
   background, or when queried with `FINAL`. Without `FINAL`, every unmerged
   duplicate insert gets counted. Fixed by adding `FROM gold.playergame FINAL` to
   the query. (Flagged as an option: running `OPTIMIZE TABLE gold.playergame FINAL`
   once would physically merge duplicates on disk, making future queries fast
   *without* needing `FINAL` every time — your call whether that's worth doing.)

Also caught: the `adp` column uses `0` as a placeholder for "no market data" rather
than a true NULL — handled by treating `0` as missing everywhere downstream.

---

## Step 2 — Train/Backtest Dataset (`02_build_train_dataset.py`)

Reshaped player-season rows into a supervised learning problem: for every player in
season *N*, attach what they actually did in season *N+1* as the label. This is what
lets us later check "if we'd built this model last year, would it have been right?"

Key design decision: **players who didn't play the following season (retired, cut,
missed the year) are kept as `label = 0` with a `played_next_season = False` flag,
not dropped.** Dropping them would have biased the model toward optimistic aging
curves, since it would only ever learn from players whose careers continued.

Filtered to fantasy-relevant positions only (QB/RB/WR/TE) — 13,209 of 21,877 total
player-seasons, since defensive positions, kickers, etc. aren't relevant to a
fantasy draft board and would just add noise.

---

## Step 3 — Baseline + First Model (`03_baseline_model.py`, `04_train_and_backtest.py`)

Before trusting anything fancy, built two dumb-simple baselines every real model
needs to beat:
- **Persistence**: predict next season = same as this season
- **Shrinkage**: blend this season's rate toward the position average, weighted by
  games played (small samples regress toward the mean)

First XGBoost pass — one model per position, predicting total fantasy points — came
back **roughly tied with the persistence baseline**, and actually lost to it for RB
and TE:

| Model | QB | RB | TE | WR |
|---|---|---|---|---|
| Persistence | 0.684 | **0.718** | **0.732** | 0.750 |
| First XGBoost | 0.688 | 0.699 | 0.699 | 0.748 |

*(Spearman rank correlation, backtested on 2021–2024, higher = better)*

**Not good enough to ship.** Diagnosed why: the model only saw a single season
snapshot per prediction, with no sense of a player's trajectory, and it was
predicting one blended number (total points) that conflates two very different
things — per-game rate (learnable) and games played (mostly injury luck, noisy).

---

## Step 3 (continued) — Enhanced Features + Two-Target Model

**Fix 1: lag/trajectory features** (`05_enhanced_features.py`) — added prior-season
ppg, two-seasons-ago ppg, year-over-year trend, cumulative career averages, games
played to date, and a rookie-season flag, all computed only from data known *before*
the prediction point (no leakage).

**Fix 2: split the target** (`06_two_target_backtest.py`) — instead of one model
predicting total points, two models per position: one predicts next season's **ppg**
(rate), one predicts next season's **games played** (availability), multiplied
together for the final total.

Result — now beating baseline on every position, both metrics:

| Metric | Model | QB | RB | TE | WR |
|---|---|---|---|---|---|
| Spearman | Persistence | 0.684 | 0.718 | 0.732 | 0.750 |
| | Two-target XGBoost | **0.706** | **0.736** | **0.738** | **0.768** |
| MAE | Persistence | 68.6 | 45.0 | 28.4 | 37.5 |
| | Two-target XGBoost | **61.3** | **40.5** | **25.1** | **31.9** |

**Fix 3: target share / rush share** — added `team_pass_att_sum` /
`team_rush_att_sum` to the SQL (they already existed in your source table, just
hadn't been pulled through) to compute each player's share of team pass/rush volume
— a stronger predictor of repeat value than raw counts since it captures role
independent of how pass-heavy the team is. Modest additional lift on top of the lag
features, most notably for QB and RB:

| Metric | Model | QB | RB | TE | WR |
|---|---|---|---|---|---|
| Spearman | Two-target + share features | **0.714** | **0.743** | 0.738 | 0.767 |

**Where the backtest landed:** a real, validated improvement over baseline on every
position — not a leap, but genuine. Spearman ~0.71–0.77 is roughly the practical
ceiling for this kind of data; a huge share of fantasy variance (injuries, role
changes, coaching decisions) is fundamentally unpredictable months in advance, by
any model. The actual edge comes from being *slightly* better than ADP at the
margin, not from approaching a "perfect" prediction.

---

## Step 5 — 2026 Projections (`07_generate_2026_projections.py`)

Retrained the two-target model on **all** available labeled transitions (every
season through 2024→2025, the most recent complete one), then applied it to each
returning player's 2025 stats to project 2026 ppg, games, and total points.

**Known limitation, not yet fixed:** this only covers players who played in 2025.
**2026 rookies are structurally invisible** to this model — they have no prior-season
row to project from. A separate draft-capital-based rookie model is still on the
to-do list.

Output: 567 returning players projected.

---

## Step 6 — VORP + Draft Board (`08_vorp_draft_board.py`)

Converted raw point projections into position-adjusted draft value using your actual
league settings (12 teams, full PPR, 1QB/2RB/2WR/1TE/1FLEX):

- **Replacement level** computed per position as the projected points of the last
  plausible starter league-wide, accounting for FLEX eligibility (RB/WR/TE all
  compete for the 12 league-wide FLEX slots, allocated ~40% RB / 45% WR / 15% TE
  based on typical PPR flex usage patterns)
- **VORP** = projected points − replacement level points, which is what makes a WR1
  comparable to an RB1 in draft order (raw points aren't directly comparable across
  positions because scarcity differs by position)
- Final board ranked by VORP, not raw points

First pass looked sane on the surface — RBs clustered near the top (matches
real-world scarcity intuition), QBs correctly pushed down despite huge raw point
totals.

---

## Step 6b — Joining Real 2026 ADP (`09_fetch_2026_adp.sql`, `10_join_adp_value_board.py`)

You pulled 2026 ADP from `silver.adp`, filtered to your exact league format (12-team,
PPR). Two data-quality issues found and fixed on the way in:

1. **Exact duplicate rows** (246 of 492) — every player appeared twice, most likely
   because the export dropped an `id`/`ffc_player_id` column that used to make rows
   unique upstream. Fixed with a straightforward de-dupe.

2. **Name suffix mismatches** between sources — e.g. `"Deebo Samuel Sr."` in the ADP
   table vs `"Deebo Samuel"` in the stats warehouse. Fixed with a normalized join key
   that strips suffixes (Jr./Sr./II/III/IV/V) and punctuation before matching.

**A more serious gap surfaced during this check:** cross-referencing the ADP top-60
against the stats warehouse showed **3 established veteran stars completely missing
from `gold.playergame`** — not a naming issue, they're not in the table under any
name variant:

- **Justin Jefferson** (WR, ADP 13.3)
- **DeVonta Smith** (WR, ADP 28.9)
- **Lamar Jackson** (QB, ADP 54.0)

This isn't a team-wide gap — their own teammates (Jordan Addison, Mark Andrews, Zay
Flowers) are all present and populated normally. It's specific to these individual
players. **This is worth investigating in the warehouse ETL directly** — something
is dropping these three specifically, and there may be others further down the list
not yet checked. (One other top-60 name, Jeremiyah Love, is *expected* to be missing
— he's a 2025 rookie with no prior-season row, consistent with the known rookie
limitation above, not a bug.)

---

## ⚠️ Unresolved: Likely Scoring Formula Mismatch (found just now, not yet fixed)

Building the value-gap column (model VORP rank vs. ADP rank) surfaced something
that doesn't pass the smell test: the model ranks **four QBs in the top 20 overall
picks** (Burrow, Allen, Nix, Mahomes). That's not how single-QB PPR leagues actually
draft — with only 1 starting QB slot, elite QBs normally go in the back half of round
1 at the earliest, and most QBs go rounds 4–8+.

Investigated by reconstructing fantasy points directly from raw stats (passing
yards, TDs, INTs, rushing, receiving) using a standard full-PPR formula, and
comparing to your table's `total_fantasy_points` column:

- **Receiving-only players match exactly** (e.g. Ja'Marr Chase 2024: reported
  403.00 vs. recomputed 403.00) — confirms receiving scoring is standard full-PPR.
- **QB seasons consistently run high** — Patrick Mahomes 2022 (reported 493.40 vs.
  standard-4pt-TD recompute of 411.40), Joe Burrow 2024, and Baker Mayfield 2024 all
  match **exactly** once passing touchdowns are valued at **6 points instead of the
  standard 4**.

So: your warehouse's `fantasy_points` column appears to use **6-point passing TDs**,
not the 4-point standard most ADP markets (and most default "full PPR" leagues)
assume. That single formula difference is enough to explain why the model is
inflating QB value relative to the market — it's not a modeling problem, it's a
scoring-rules mismatch between the data the model was trained on and the ADP it's
being compared against.

**This needs to be resolved before the value-gap column (and the "Bo Nix is a huge
value pick" type results) can be trusted.** Two ways to fix it, your call:

1. **Confirm your actual league uses 6-point passing TDs** — if so, the model is
   correct and it's the ADP comparison that's mismatched (ADP would need to come
   from a 6pt-passing-TD source instead).
2. **If your league uses standard 4-point passing TDs** (more common), recompute
   `total_fantasy_points` from the raw component stats using the correct formula and
   retrain — this would likely pull QBs back down into a more realistic draft range
   and is probably the more consequential fix at this point in the project.

---

## Files Produced So Far

| File | What it is |
|---|---|
| `01_player_season_features.sql` | Aggregation query (with `FINAL` + alias fixes) |
| `02_build_train_dataset.py` | Builds season N → season N+1 training pairs |
| `03_baseline_model.py` | Persistence + shrinkage baselines |
| `04_train_and_backtest.py` | First XGBoost pass (superseded by two-target version) |
| `05_enhanced_features.py` | Adds lag/trajectory + target/rush share features |
| `06_two_target_backtest.py` | Final validated model architecture |
| `07_generate_2026_projections.py` | Generates 2026 point projections |
| `08_vorp_draft_board.py` | VORP calculation + position-adjusted ranking |
| `09_fetch_2026_adp.sql` | Pulls 2026 ADP matching your league format |
| `10_join_adp_value_board.py` | Joins ADP, computes market value gap |
| `2026_draft_model_plan.md` | Original project plan |
| `future_work_betting_lines.md` | Deferred: adding betting-market data later |

---

## Open Items, In Priority Order

1. **Resolve the passing-TD scoring mismatch** (above) — highest priority, affects
   every QB ranking on the board
2. **Investigate why Justin Jefferson, DeVonta Smith, and Lamar Jackson are missing**
   from `gold.playergame` entirely
3. **Build the rookie projection model** — currently the board has zero 2026 rookies
4. Re-run the full pipeline once the scoring formula is confirmed/fixed, to get a
   trustworthy final board
