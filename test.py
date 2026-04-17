import numpy as np
import pandas as pd
from clickhouse_connect import get_client

client = get_client(host="localhost", port=8123, username="default", password="default")
df = client.query_df("select * from gold.playergame final")


def build_playergame_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # ─────────────────────────────────────────────
    # Step 0: Prep
    # ─────────────────────────────────────────────
    df["game_date"] = pd.to_datetime(df["game_date"])

    # opponent team
    df["opp_team_id"] = np.where(
        df["home_away"] == "home", df["away_team_id"], df["home_team_id"]
    )

    # ─────────────────────────────────────────────
    # Step 1: Fantasy points
    # ─────────────────────────────────────────────
    df["fantasy_points_ppr"] = (
        df["passing_yards"] * 0.04
        + df["passing_tds"] * 4
        - df["interceptions"]
        + df["rushing_yards"] * 0.1
        + df["rushing_tds"] * 6
        + df["receptions"]
        + df["receiving_yards"] * 0.1
        + df["receiving_tds"] * 6
        - df["fumbles_lost"] * 2
    ).round(2)

    # ─────────────────────────────────────────────
    # Step 2: Player rolling features (NO leakage)
    # ─────────────────────────────────────────────
    df = df.sort_values(["player_id", "game_date"])
    g = df.groupby("player_id")

    df["avg_fantasy_points_last3"] = g["fantasy_points_ppr"].shift(1).rolling(3).mean()
    df["avg_fantasy_points_last5"] = g["fantasy_points_ppr"].shift(1).rolling(5).mean()

    for col in ["passing_yards", "rushing_yards", "receiving_yards", "targets"]:
        df[f"avg_{col}_last3"] = g[col].shift(1).rolling(3).mean()

    # games played THIS season before current game
    df = df.sort_values(["player_id", "season", "game_date"])
    df["games_played_this_season"] = df.groupby(["player_id", "season"]).cumcount()

    # ─────────────────────────────────────────────
    # Step 2B: Lag features (NO leakage)
    # ─────────────────────────────────────────────

    lag_cols = [
        "fantasy_points_ppr",
        "passing_yards",
        "rushing_yards",
        "receiving_yards",
        "targets",
        "rushing_attempts",
    ]

    lags = [1, 2, 3]

    g = df.groupby("player_id")

    for col in lag_cols:
        for lag in lags:
            df[f"{col}_lag{lag}"] = g[col].shift(lag)

    # ─────────────────────────────────────────────
    # Step 3: Team-game aggregation (CRITICAL FIX)
    # ─────────────────────────────────────────────
    team_game = (
        df.groupby(["team_id", "game_id", "game_date"], as_index=False)
        .agg(
            {
                "net_passing_yards": "first",  # already team-level
                "team_rushing_yards": "first",
            }
        )
        .sort_values(["team_id", "game_date"])
    )

    tg = team_game.groupby("team_id")

    team_game["opp_avg_passing_yards_allowed_last3"] = (
        tg["net_passing_yards"].shift(1).rolling(3).mean()
    )

    team_game["opp_avg_rushing_yards_allowed_last3"] = (
        tg["team_rushing_yards"].shift(1).rolling(3).mean()
    )

    team_game["opp_avg_receiving_yards_allowed_last3"] = (
        tg["net_passing_yards"].shift(1).rolling(3).mean()
    )

    # ─────────────────────────────────────────────
    # Step 4: Join opponent defense
    # ─────────────────────────────────────────────
    df = df.merge(
        team_game[
            [
                "team_id",
                "game_id",
                "opp_avg_passing_yards_allowed_last3",
                "opp_avg_rushing_yards_allowed_last3",
                "opp_avg_receiving_yards_allowed_last3",
            ]
        ],
        left_on=["opp_team_id", "game_id"],
        right_on=["team_id", "game_id"],
        how="left",
        suffixes=("", "_opp"),
    )

    # ─────────────────────────────────────────────
    # Step 5: Final schema (matches your DDL)
    # ─────────────────────────────────────────────
    lag_feature_cols = [
        "fantasy_points_ppr_lag1",
        "fantasy_points_ppr_lag2",
        "fantasy_points_ppr_lag3",
        "passing_yards_lag1",
        "rushing_yards_lag1",
        "receiving_yards_lag1",
        "targets_lag1",
        "rushing_attempts_lag1",
    ]

    features = df[
        [
            # existing columns...
            "player_id",
            "game_id",
            "season",
            "week",
            "player_name",
            "position",
            "team_id",
            "home_away",
            "weather_condition",
            "temperature",
            "wind_speed",
            # rolling
            "avg_fantasy_points_last3",
            "avg_fantasy_points_last5",
            "avg_passing_yards_last3",
            "avg_rushing_yards_last3",
            "avg_receiving_yards_last3",
            "avg_targets_last3",
            # opponent
            "opp_avg_passing_yards_allowed_last3",
            "opp_avg_rushing_yards_allowed_last3",
            "opp_avg_receiving_yards_allowed_last3",
            # lag features 👇
            *lag_feature_cols,
            "games_played_this_season",
            "fantasy_points_ppr",
        ]
    ].copy()
    features.to_csv("test.csv")

    return features


values = build_playergame_features(df)
print(values)
