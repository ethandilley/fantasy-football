"""
Step 2: Build train/backtest dataset from player_season_features.csv

For every player-season N, attach the player's outcome in season N+1 as the
label. This produces a supervised learning table: "given what we knew after
season N, what did the player do in season N+1?"

Outputs:
  - train_dataset.csv      : rows with a known N+1 outcome (for training/backtesting)
  - predict_2026_input.csv : rows from season 2025 (features only, no label yet
                              since 2026 hasn't happened) -- the input to the
                              final projection step
"""

import pandas as pd

FANTASY_POSITIONS = ["Quarterback", "Running Back", "Wide Receiver", "Tight End"]

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
]

ID_COLS = ["player_id", "player_name", "position", "season", "team_name", "team_id", "status"]


def build(input_csv: str, train_out: str, predict_out: str):
    df = pd.read_csv(input_csv, na_values=["\\N"])
    df = df[df["position"].isin(FANTASY_POSITIONS)].copy()

    # adp uses 0 as a fill value for "no market data" rather than a true NULL
    df["adp"] = df["adp"].replace(0, pd.NA)

    max_season = df["season"].max()

    # next-season outcome table, renamed with next_ prefix
    next_season = df[["player_id", "season", "total_fantasy_points", "ppg", "games_played"]].copy()
    next_season["season"] = next_season["season"] - 1  # shift back so it joins on the PRIOR season
    next_season = next_season.rename(columns={
        "total_fantasy_points": "next_total_fantasy_points",
        "ppg": "next_ppg",
        "games_played": "next_games_played",
    })

    merged = df.merge(next_season, on=["player_id", "season"], how="left")

    # played_next_season: False means retired/cut/missed the year entirely.
    # Kept as label=0 rather than dropped -- silently dropping these would bias
    # the model toward always-optimistic aging curves, since it would never see
    # the players whose careers ended.
    merged["played_next_season"] = merged["next_total_fantasy_points"].notna()
    merged["next_total_fantasy_points"] = merged["next_total_fantasy_points"].fillna(0.0)
    merged["next_ppg"] = merged["next_ppg"].fillna(0.0)
    merged["next_games_played"] = merged["next_games_played"].fillna(0)

    # Rows where season == max_season have no next-season data available at all
    # (season+1 doesn't exist yet) -- these aren't "player missed the year",
    # they're "the future hasn't happened." Split them out as the prediction set.
    predict_set = merged[merged["season"] == max_season].copy()
    train_set = merged[merged["season"] < max_season].copy()

    train_cols = ID_COLS + FEATURE_COLS + ["adp", "next_total_fantasy_points", "next_ppg", "next_games_played", "played_next_season"]
    predict_cols = ID_COLS + FEATURE_COLS + ["adp"]

    train_set[train_cols].to_csv(train_out, index=False)
    predict_set[predict_cols].to_csv(predict_out, index=False)

    print(f"Loaded {len(df)} fantasy-position player-seasons ({df['season'].min()}-{max_season})")
    print(f"Train/backtest rows: {len(train_set)}  (seasons {train_set['season'].min()}-{train_set['season'].max()})")
    print(f"  -> played_next_season True: {train_set['played_next_season'].sum()}, False: {(~train_set['played_next_season']).sum()}")
    print(f"Predict-2026 input rows: {len(predict_set)}  (season {max_season} only)")
    print(f"Saved: {train_out}")
    print(f"Saved: {predict_out}")


if __name__ == "__main__":
    build(
        input_csv="data/player_season_features.csv",
        train_out="data/train_dataset.csv",
        predict_out="data/predict_2026_input.csv",
    )
