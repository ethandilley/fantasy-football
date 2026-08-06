"""
Step 3c: Enhanced feature engineering

WHY: the first model only saw one season snapshot per prediction, so it had
no sense of a player's TRAJECTORY -- a 24-year-old trending up and a
32-year-old about to decline can look identical if their raw stats happen
to match this season. This script adds lag features (what happened in
PRIOR seasons, known at prediction time) so the model can see the arc, not
just a single point on it.

It also splits the problem into two targets instead of one:
  - next_ppg          : per-game rate next season (skill/role -- predictable)
  - next_games_played  : availability next season (injury luck -- noisy)
Final projected total = predicted ppg * predicted games. This is a standard
trick in sports projections: don't let injury-driven noise in games played
pollute the part of the prediction that's actually learnable (rate of
production when on the field).

INPUT:  player_season_features.csv (the raw SQL export, all positions)
OUTPUT: enhanced_train_dataset.csv       (rows with known next-season outcome)
        enhanced_predict_2026_input.csv  (season==2025 rows, features only)
"""

import pandas as pd
import numpy as np

FANTASY_POSITIONS = ["Quarterback", "Running Back", "Wide Receiver", "Tight End"]

BASE_FEATURE_COLS = [
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
]

# lag/trajectory features added on top of the base snapshot
LAG_FEATURE_COLS = [
    "prior_season_ppg", "prior_season_games",
    "two_seasons_ago_ppg",
    "ppg_trend_1yr",            # this season vs prior season
    "career_games_to_date",     # cumulative games entering this season (+ this season)
    "seasons_played_to_date",   # experience, including this season
    "is_rookie_season",
    "career_ppg_to_date",       # cumulative average ppg across career so far
]

FEATURE_COLS = BASE_FEATURE_COLS + LAG_FEATURE_COLS


def add_lag_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.sort_values(["player_id", "season"]).copy()
    g = df.groupby("player_id")

    df["prior_season_ppg"] = g["ppg"].shift(1)
    df["prior_season_games"] = g["games_played"].shift(1)
    df["two_seasons_ago_ppg"] = g["ppg"].shift(2)
    df["ppg_trend_1yr"] = df["ppg"] - df["prior_season_ppg"]

    # cumulative career totals INCLUDING the current season (known at
    # prediction time -- this season has already happened)
    df["career_games_to_date"] = g["games_played"].cumsum()
    df["seasons_played_to_date"] = g.cumcount() + 1
    df["career_ppg_to_date"] = g["ppg"].transform(lambda s: s.expanding().mean())

    df["is_rookie_season"] = (df["seasons_played_to_date"] == 1).astype(int)

    return df


def add_share_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    # this player's volume ÷ team's total volume in the same games.
    # NaN (not 0) when the team total is missing/zero, so it doesn't get
    # silently treated as "played but got 0% share" for e.g. kickers/punters
    # or rows with missing team totals.
    df["target_share"] = np.where(
        df["team_pass_att_sum"] > 0, df["total_targets"] / df["team_pass_att_sum"], np.nan
    )
    df["rush_share"] = np.where(
        df["team_rush_att_sum"] > 0, df["rush_att"] / df["team_rush_att_sum"], np.nan
    )
    return df


def build(input_csv: str, train_out: str, predict_out: str):
    df = pd.read_csv(input_csv, na_values=["\\N"])
    df = df[df["position"].isin(FANTASY_POSITIONS)].copy()
    df["adp"] = df["adp"].replace(0, pd.NA)

    df = add_share_features(df)
    df = add_lag_features(df)

    max_season = df["season"].max()

    next_season = df[["player_id", "season", "total_fantasy_points", "ppg", "games_played"]].copy()
    next_season["season"] = next_season["season"] - 1
    next_season = next_season.rename(columns={
        "total_fantasy_points": "next_total_fantasy_points",
        "ppg": "next_ppg",
        "games_played": "next_games_played",
    })

    merged = df.merge(next_season, on=["player_id", "season"], how="left")

    merged["played_next_season"] = merged["next_total_fantasy_points"].notna()
    merged["next_total_fantasy_points"] = merged["next_total_fantasy_points"].fillna(0.0)
    merged["next_ppg"] = merged["next_ppg"].fillna(0.0)
    merged["next_games_played"] = merged["next_games_played"].fillna(0)

    predict_set = merged[merged["season"] == max_season].copy()
    train_set = merged[merged["season"] < max_season].copy()

    id_cols = ["player_id", "player_name", "position", "season", "team_name", "team_id", "status"]
    train_cols = id_cols + FEATURE_COLS + ["adp", "next_total_fantasy_points", "next_ppg", "next_games_played", "played_next_season"]
    predict_cols = id_cols + FEATURE_COLS + ["adp"]

    train_set[train_cols].to_csv(train_out, index=False)
    predict_set[predict_cols].to_csv(predict_out, index=False)

    print(f"Train/backtest rows: {len(train_set)}")
    print(f"  -> with prior season data (non-rookie): {(~train_set['is_rookie_season'].astype(bool)).sum()}")
    print(f"  -> rookie-season rows (no lag history): {train_set['is_rookie_season'].sum()}")
    print(f"Predict-2026 input rows: {len(predict_set)}")
    print(f"Saved: {train_out}")
    print(f"Saved: {predict_out}")


if __name__ == "__main__":
    build(
        input_csv="data/player_season_features.csv",
        train_out="data/enhanced_train_dataset.csv",
        predict_out="data/enhanced_predict_2026_input.csv",
    )
