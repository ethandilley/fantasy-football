import numpy as np
import pandas as pd
import joblib

from clickhouse_connect import get_client
from sklearn.metrics import mean_absolute_error, mean_squared_error


# ─────────────────────────────────────────────
# LOAD MODEL
# ─────────────────────────────────────────────
MODEL_PATH = "test.pkl"
model = joblib.load(MODEL_PATH)


# ─────────────────────────────────────────────
# LOAD 2025 DATA ONLY
# ─────────────────────────────────────────────
client = get_client(
    host="localhost",
    port=8123,
    username="default",
    password="default"
)

df_2025 = client.query_df("""
SELECT *
FROM gold.playergame FINAL
WHERE season = 2025
""")


# ─────────────────────────────────────────────
# USE YOUR EXISTING FEATURE FUNCTION
# (import it if it's in another file)
# ─────────────────────────────────────────────
def build_playergame_features(df):
    df = df.copy()

    df["game_date"] = pd.to_datetime(df["game_date"])

    df["opp_team_id"] = np.where(
        df["home_away"] == "home",
        df["away_team_id"],
        df["home_team_id"]
    )

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

    df = df.sort_values(["player_id", "game_date"])
    g = df.groupby("player_id")

    df["avg_fantasy_points_last3"] = g["fantasy_points_ppr"].shift(1).rolling(3).mean()
    df["avg_fantasy_points_last5"] = g["fantasy_points_ppr"].shift(1).rolling(5).mean()

    for col in ["passing_yards", "rushing_yards", "receiving_yards", "targets"]:
        df[f"avg_{col}_last3"] = g[col].shift(1).rolling(3).mean()

    df = df.sort_values(["player_id", "season", "game_date"])
    df["games_played_this_season"] = df.groupby(["player_id", "season"]).cumcount()

    lag_cols = [
        "fantasy_points_ppr",
        "passing_yards",
        "rushing_yards",
        "receiving_yards",
        "targets",
        "rushing_attempts",
    ]

    for col in lag_cols:
        for lag in [1, 2, 3]:
            df[f"{col}_lag{lag}"] = g[col].shift(lag)

    return df


# ─────────────────────────────────────────────
# BUILD FEATURES
# ─────────────────────────────────────────────
df_2025 = build_playergame_features(df_2025)


# ─────────────────────────────────────────────
# PREP INPUTS
# ─────────────────────────────────────────────
TARGET = "fantasy_points_ppr"
DROP_COLS = ["player_name", "game_id"]

X_2025 = df_2025.drop(columns=DROP_COLS + [TARGET])
y_2025 = df_2025[TARGET]


# one-hot encode (must match training)
X_2025 = pd.get_dummies(X_2025, dummy_na=True)


# ─────────────────────────────────────────────
# ALIGN COLUMNS TO MODEL EXPECTATION
# (critical step)
# ─────────────────────────────────────────────
model_features = model.get_booster().feature_names

X_2025 = X_2025.reindex(columns=model_features, fill_value=0)


# ─────────────────────────────────────────────
# PREDICT
# ─────────────────────────────────────────────
df_2025["predicted_fp"] = model.predict(X_2025)


# ─────────────────────────────────────────────
# EVALUATE
# ─────────────────────────────────────────────
rmse = mean_squared_error(y_2025, df_2025["predicted_fp"]) ** 0.5
mae = mean_absolute_error(y_2025, df_2025["predicted_fp"])

print("\n====================")
print("2025 MODEL PERFORMANCE")
print("====================")
print("RMSE:", rmse)
print("MAE :", mae)


# ─────────────────────────────────────────────
# BIGGEST ERRORS
# ─────────────────────────────────────────────
df_2025["error"] = df_2025["predicted_fp"] - df_2025["fantasy_points_ppr"]
df_2025["abs_error"] = df_2025["error"].abs()

print("\nTop 25 worst predictions:")
print(
    df_2025.sort_values("abs_error", ascending=False)[
        ["player_name", "week", "fantasy_points_ppr", "predicted_fp", "abs_error"]
    ].head(25)
)


# ─────────────────────────────────────────────
# OPTIONAL: SAVE FOR ANALYSIS
# ─────────────────────────────────────────────
# ─────────────────────────────────────────────
# CLEAN OUTPUT TABLE ONLY
# ─────────────────────────────────────────────
# keep only predictions > 8
df_2025 = df_2025[df_2025["predicted_fp"] > 12]

output = df_2025[[
    "player_name",
    "week",
    "season",
    "fantasy_points_ppr"
]].copy()

output["predicted_fantasy_points"] = df_2025["predicted_fp"]
output["error"] = output["predicted_fantasy_points"] - output["fantasy_points_ppr"]

output = output.sort_values("error", key=lambda x: x.abs(), ascending=False)

print(output.head(50))

# optional save
output.to_csv("2025_predictions_clean.csv", index=False)

# ─────────────────────────────────────────────
# PLAYER-SEASON TOTALS (2025)
# ─────────────────────────────────────────────

season_summary = df_2025.groupby(["player_name", "season"], as_index=False).agg(
    real_fantasy_points=("fantasy_points_ppr", "sum"),
    predicted_fantasy_points=("predicted_fp", "sum"),
)

season_summary["error"] = (
    season_summary["predicted_fantasy_points"]
    - season_summary["real_fantasy_points"]
)

season_summary["abs_error"] = season_summary["error"].abs()

season_summary = season_summary.sort_values("abs_error", ascending=False)

print(season_summary.head(50))

season_summary.to_csv("2025_season_summary.csv", index=False)
