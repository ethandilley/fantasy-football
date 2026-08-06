"""
Step 5: Generate 2026 projections

Retrains the two-target model (ppg rate x games played) on ALL available
labeled transitions (1999->2000 through 2024->2025 -- every season through
the most recently completed one), since the backtest already validated this
architecture works. No need to hold out 2024 anymore; use everything.

Then applies it to each returning player's 2025 season stats to project
2026 per-game rate, games played, and total fantasy points.

IMPORTANT LIMITATION: this only covers players who played in 2025 (they
have a row to project FROM). Incoming 2026 rookies have no NFL history in
this table and are structurally invisible to this model -- they'd need a
separate draft-capital-based projection, not built yet (see project plan).
"""

import pandas as pd
import numpy as np
from xgboost import XGBRegressor

FANTASY_POSITIONS = ["Quarterback", "Running Back", "Wide Receiver", "Tight End"]
MAX_GAMES = 17

FEATURE_COLS = [
    "height", "weight", "age", "draft_year", "draft_round", "draft_selection",
    "games_played", "last_week_played",
    "total_fantasy_points", "ppg", "ppg_stddev", "ppg_last4",
    "pass_att", "pass_cmp", "pass_yds", "pass_td", "pass_int",
    "yds_per_att", "completion_pct", "pass_td_rate",
    "rush_att", "rush_yds", "rush_td", "yds_per_carry", "rush_td_rate",
    "total_targets", "total_receptions", "rec_yds", "rec_td",
    "catch_rate", "yds_per_target", "yds_per_reception",
    "total_fumbles", "total_fumbles_lost",
    "team_plays_pg", "team_yards_per_play", "team_drives_pg",
    "team_rz_conv_rate", "team_possession_secs", "team_turnovers_pg",
    "target_share", "rush_share",
    "prior_season_ppg", "prior_season_games", "two_seasons_ago_ppg",
    "ppg_trend_1yr", "career_games_to_date", "seasons_played_to_date",
    "is_rookie_season", "career_ppg_to_date",
]


def train_final_models(train_df: pd.DataFrame) -> dict:
    models = {}
    for pos in FANTASY_POSITIONS:
        sub = train_df[train_df["position"] == pos]
        X = sub[FEATURE_COLS]

        ppg_model = XGBRegressor(
            n_estimators=300, max_depth=4, learning_rate=0.05,
            subsample=0.8, colsample_bytree=0.8, random_state=42, n_jobs=-1,
        )
        ppg_model.fit(X, sub["next_ppg"])

        games_model = XGBRegressor(
            n_estimators=200, max_depth=3, learning_rate=0.05,
            subsample=0.8, colsample_bytree=0.8, random_state=42, n_jobs=-1,
        )
        games_model.fit(X, sub["next_games_played"])

        models[pos] = {"ppg_model": ppg_model, "games_model": games_model}
    return models


def generate_projections(train_csv: str, predict_csv: str, output_csv: str):
    train_df = pd.read_csv(train_csv)
    predict_df = pd.read_csv(predict_csv)

    models = train_final_models(train_df)

    results = []
    for pos in FANTASY_POSITIONS:
        sub = predict_df[predict_df["position"] == pos].copy()
        if len(sub) == 0:
            continue
        X = sub[FEATURE_COLS]
        sub["proj_ppg_2026"] = models[pos]["ppg_model"].predict(X)
        sub["proj_games_2026"] = np.clip(models[pos]["games_model"].predict(X), 0, MAX_GAMES)
        sub["proj_total_points_2026"] = sub["proj_ppg_2026"] * sub["proj_games_2026"]
        results.append(sub)

    out = pd.concat(results, ignore_index=True)
    out = out.sort_values("proj_total_points_2026", ascending=False)

    keep_cols = [
        "player_id", "player_name", "position", "team_name", "age",
        "total_fantasy_points", "ppg", "games_played",  # their 2025 actuals, for reference
        "proj_ppg_2026", "proj_games_2026", "proj_total_points_2026",
    ]
    out[keep_cols].to_csv(output_csv, index=False)

    print(f"Generated projections for {len(out)} returning players (2025 -> 2026)")
    print(f"NOTE: rookies entering the league in 2026 are NOT included -- they have")
    print(f"      no 2025 row in this table to project from.")
    print(f"\nTop 10 by projected 2026 total points:")
    print(out[keep_cols].head(10).to_string(index=False))
    print(f"\nSaved: {output_csv}")


if __name__ == "__main__":
    generate_projections(
        train_csv="data/enhanced_train_dataset.csv",
        predict_csv="data/enhanced_predict_2026_input.csv",
        output_csv="data/projections_2026.csv",
    )
