# Future Work: Adding Betting Lines to the Draft Model

Not part of the current build. Revisit after the core stats-only model (SQL → features →
position models → VORP/ADP board) is working and backtested.

---

## Why bother

The current model is purely backward-looking — it only knows what already happened in
box scores. Betting markets bake in information the model structurally can't see:
coaching changes, free agency, scheme fit, injury news, roster overhaul. This is the
single highest-leverage addition once the base model exists.

---

## Three tiers, by value and effort

### 1. Team win totals / implied team point totals (2026 season) — **do this first**
- **Value**: high. Captures forward-looking team-quality signal (coaching, roster
  changes) that historical stats can't.
- **Effort**: low. ~32 numbers a year, manually entered or scraped once before the
  season. Join on `team_id` + `season`.
- **Action**: add `team_win_total`, `implied_team_points` as features in the 2026
  projection step (Step 5 in the main plan). No historical backfill required to start
  using it; backfilling a few past years helps validate how predictive it's been.

### 2. Historical game-level lines (spread, total) — **moderate effort, lower value**
- **Value**: marginal for season-long projection. You already have decent proxies in
  `gold.playergame` (`team_yards_per_play`, `total_plays`, `possession_time_seconds`)
  that correlate with what a spread/total captures. Mostly useful for cleaning up
  game-script noise in efficiency stats, not a big projection-accuracy win.
- **Effort**: moderate — not the modeling, the data sourcing and join:
  - Need an external historical odds source (paid API like Sportradar/OddsAPI, or a
    scraped/archived historical odds dataset). Not available in this sandbox — source
    and load this yourself.
  - Real friction is team-name normalization across 26 seasons (abbreviation drift,
    relocations like STL → LA Rams) when joining to `game_id`.
  - Schema: new `gold.gamelines` table (`game_id`, `spread`, `total`,
    `implied_team_total`), joined into the existing feature aggregation SQL.

### 3. Player-level season props (e.g., O/U rushing yards) — **opportunistic, hardest to backtest**
- **Value**: potentially very high for the players who have them — sportsbooks price
  in depth chart, scheme fit, and contract situation better than a box-score model
  can. Coverage is narrow though (mostly RB1/WR1-caliber and starting QBs), so it
  won't help rank the WR3/WR4 tier where a lot of draft value lives.
- **Effort**: hard to use historically — most books don't publish archived season-long
  prop lines, only current ones. This makes it a forward-only, going-forward addition:
  a late-stage ensemble input for the current draft year rather than something to
  retrain the core model on.
- **Action**: once the core model is stable, treat as a manual override/blend layer
  for star players only, not a full retrain.

---

## Suggested order when picking this back up

1. Add team win totals as a 2026-only feature — cheap, real signal, no data
   engineering lift.
2. Re-run backtest to see if win totals actually move rank-correlation before
   investing further.
3. If worthwhile, evaluate sourcing historical spread/total data and tackle the
   team-name normalization join.
4. Revisit player props opportunistically for star players once a source is
   identified.

## Open question to resolve before starting
- Where's the data coming from? (Paid odds API vs. scraped historical archive vs.
  manual entry for win totals only) — this determines whether step 3 above is a
  quick add or a real mini-project.
