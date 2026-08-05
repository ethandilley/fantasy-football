# 2026 Fantasy Draft Model — Project Plan

## Objective

Build a data pipeline that turns `gold.playergame` (26 seasons of NFL play-by-box-score data, 1999–present) into a **ranked 2026 draft board**: projected fantasy points per player, converted into draft value versus current ADP.

---

## Pipeline Overview

```
gold.playergame (ClickHouse)
        │
        ▼
1. Player-season feature aggregation (SQL)
        │
        ▼
2. Train/backtest dataset construction (Python)
        │
        ▼
3. Position-specific projection models (Python)
        │
        ▼
4. Backtesting & validation
        │
        ▼
5. 2026 projections
        │
        ▼
6. VORP calculation + ADP value board
        │
        ▼
Final: ranked draft board (CSV / interactive artifact)
```

---

## Step 1 — Player-Season Feature Aggregation

**Status: done** (`01_player_season_features.sql`)

Rolls the game-level table up to one row per `(player_id, season)`. Captures:

- **Volume**: targets, rush attempts, pass attempts — the stickiest year-over-year predictor
- **Efficiency**: yards/target, yards/carry, completion %, TD rates — noisier, needs regression toward the mean
- **Team context**: team yards/play, red zone conversion rate, possession time — a good offense lifts everyone in it
- **Trend**: last-4-games PPG vs season PPG, to catch role changes a season average would hide
- **Availability**: games played, last week played
- **Player attributes**: age, draft capital, position, status
- **ADP**: joined where available, NULL for seasons without market data

**Output**: `player_season_features.csv` (~1 row per player per season, ~26 seasons)

**Your action**: run the SQL against ClickHouse, export to CSV, upload here.

---

## Step 2 — Train/Backtest Dataset Construction

**Goal**: reshape the player-season table into a supervised learning problem.

- For every player-season *N*, the **label** is that same player's `total_fantasy_points` (or PPG) in season *N+1* — i.e., "given what we knew after season N, what happened next season?"
- Features are everything from season *N* (volume, efficiency, team context, trend, age, draft capital)
- Players who didn't play in season *N+1* (retired, cut, injured all year) become **zero or dropped-row** cases — need a deliberate decision here: dropping them silently would bias the model optimistic, since it would only ever learn from players who stuck around
- Join in age at time of *N+1* so the model can learn age-curve effects (e.g., RBs declining earlier than WRs)
- Split by season for validation, not randomly — random shuffling would let the model "see the future," e.g., train on 2015 while testing on 2012

**Output**: a wide feature/label table, one row per player-season-transition, ready for modeling.

---

## Step 3 — Position-Specific Projection Models

Fantasy production means different things for QB/RB/WR/TE, so train **separate models per position group**.

**Approach**:
- Start with **gradient boosting regression** (XGBoost or LightGBM) — handles nonlinear effects (age curves, volume thresholds, injury risk) without much manual feature crafting
- Compare against a **simple weighted-average baseline** (e.g., 60% last season + 30% two seasons ago + 10% three seasons ago, with shrinkage for small samples) — if the fancy model can't beat this, that's a signal to simplify
- Rookies are a gap: no prior-season row exists in this table. Handle separately using only draft capital + position + a league-average rookie curve by draft round, since there's no play-level history to lean on. Flag rookie projections as lower-confidence.

**Output**: one trained model per position, plus the baseline for comparison.

---

## Step 4 — Backtesting & Validation

Before trusting any 2026 number:

- Train on seasons through *N-1*, predict season *N*, compare to what actually happened — repeat for at least 3-4 historical seasons (e.g., predict 2022, 2023, 2024, 2025 in turn, each time only using data available before that season)
- Metrics: mean absolute error in points/game, and — more importantly for drafting — **rank correlation** (Spearman) between predicted and actual finish, since draft value is about relative ordering, not exact point totals
- Sanity-check by position: check the model isn't just predicting "same as last year" for everyone (that's the baseline's job to beat)
- Look at the worst misses individually — big breakouts and big busts — to see if there's a pattern the feature set is missing (e.g., offensive coordinator change, new starting QB) before finalizing

**Output**: a short backtest report — error metrics per position per season, and a list of the model's best/worst historical predictions for a gut check.

---

## Step 5 — 2026 Projections

- Feed the model each player's **2025 season row** (their most recent completed season) as input
- Apply the age-curve adjustment for the age they'll be in 2026
- Rookies: use draft capital-based rookie model once 2026 draft picks are known (this step may need to wait until after the actual NFL draft in April 2026, or be re-run then)
- Output: raw projected fantasy points and points/game per player for 2026

---

## Step 6 — VORP + Draft Value Board

This is the step that turns a spreadsheet of point projections into an actual draft strategy.

- Determine **replacement level** per position for your league format (depends on # teams and starting lineup requirements — need this from you)
- Compute **VORP** = projected points − replacement-level points, per player
- Rank all players by VORP (this is what makes a WR1 comparable to an RB1 — raw points aren't, since positional scarcity differs)
- Join current-season ADP; compute `ADP rank − VORP rank` → **positive gap = market undervaluing them relative to the model (good value pick)**, negative = market overvaluing
- Final output: a sortable draft board — projected points, VORP, ADP, value gap, position, team, injury/availability flag

---

## Open Questions / Inputs Needed From You

| # | Question | Why it matters |
|---|---|---|
| 1 | League format — # teams, PPR/half-PPR/standard, starting lineup (e.g., 1 QB/2 RB/2 WR/1 TE/1 FLEX)? | Determines replacement level and VORP baselines |
| 2 | Is 2025 season data complete in the warehouse? | Determines whether Step 5 can run now or needs to wait |
| 3 | Any known 2026 team changes (coaching, scheme, injuries) not captured in historical stats? | Model can't see this — may need manual adjustment overlay |
| 4 | Dynasty/keeper league, or fresh redraft? | Changes whether we weight youth/upside vs. proven production |

---

## Deliverables Checklist

- [x] `01_player_season_features.sql` — feature aggregation query
- [ ] `player_season_features.csv` — exported data (your action)
- [ ] Train/backtest dataset builder (Python)
- [ ] Position models (QB/RB/WR/TE) + baseline
- [ ] Backtest report
- [ ] 2026 projections
- [ ] VORP + ADP value draft board (final deliverable)

---

## Tech Stack

- **SQL**: ClickHouse, for the initial aggregation (already your warehouse)
- **Python**: pandas for data wrangling, XGBoost/LightGBM for modeling, scikit-learn for backtesting utilities
- **Output**: CSV + an interactive sortable draft board (rendered inline)
