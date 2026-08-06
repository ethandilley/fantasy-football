"""
Step 3d: Two-target model with enhanced (lag) features, backtested

Predicts next season in two pieces and multiplies them together:
  1. next_ppg            -- per-game rate (the learnable, skill-driven part)
  2. next_games_played    -- availability (noisy, injury-driven, but a player's
                              age/position/recent durability still carries
                              *some* signal, e.g. RBs decline in availability
                              earlier than WRs)
  final_prediction = pred_ppg * pred_games, capped at 17 games

Same backtest structure as before: train only on seasons strictly before the
test year, so nothing leaks from the future.
"""

import pandas as pd
import numpy as np
from xgboost import XGBRegressor
from scipy.stats import spearmanr

FANTASY_POSITIONS = ["Quarterback", "Running Back", "Wide Receiver", "Tight End"]
BACKTEST_SEASONS = [2021, 2022, 2023, 2024]
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


def add_baseline_predictions(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["pred_persistence"] = df["total_fantasy_points"]
    return df


def train_two_target_models(train_df: pd.DataFrame) -> dict:
    """Returns {position: {"ppg_model":..., "games_model":...}}"""
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


def evaluate(df: pd.DataFrame, pred_col: str, target_col: str) -> dict:
    results = {}
    for pos in FANTASY_POSITIONS:
        sub = df[df["position"] == pos]
        if len(sub) < 5:
            continue
        mae = (sub[pred_col] - sub[target_col]).abs().mean()
        rho, _ = spearmanr(sub[pred_col], sub[target_col])
        results[pos] = {"mae": mae, "spearman": rho, "n": len(sub)}
    return results


def run_backtest(train_dataset_path: str):
    full = pd.read_csv(train_dataset_path)
    full = add_baseline_predictions(full)

    all_rows = []
    final_models = None

    for test_season in BACKTEST_SEASONS:
        train_slice = full[full["season"] < test_season]
        test_slice = full[full["season"] == test_season].copy()
        if len(test_slice) == 0:
            continue

        models = train_two_target_models(train_slice)
        final_models = models  # keep the last (trained through 2024) for projection

        for pos in FANTASY_POSITIONS:
            mask = test_slice["position"] == pos
            if mask.sum() == 0:
                continue
            X_test = test_slice.loc[mask, FEATURE_COLS]
            pred_ppg = models[pos]["ppg_model"].predict(X_test)
            pred_games = np.clip(models[pos]["games_model"].predict(X_test), 0, MAX_GAMES)
            test_slice.loc[mask, "pred_two_target"] = pred_ppg * pred_games

        for pred_col, label in [
            ("pred_persistence", "Persistence baseline"),
            ("pred_two_target", "Two-target XGBoost (enhanced)"),
        ]:
            metrics = evaluate(test_slice, pred_col, "next_total_fantasy_points")
            for pos, m in metrics.items():
                all_rows.append({
                    "test_season": test_season, "model": label, "position": pos,
                    "mae": round(m["mae"], 1), "spearman": round(m["spearman"], 3), "n": m["n"],
                })

    return pd.DataFrame(all_rows), final_models


if __name__ == "__main__":
    results, final_models = run_backtest("data/enhanced_train_dataset.csv")

    pd.set_option("display.width", 120)
    pd.set_option("display.max_rows", 200)

    print("\n=== Backtest results by season / model / position ===\n")
    print(results.to_string(index=False))

    print("\n=== Summary: average Spearman rank correlation across all backtest seasons ===\n")
    print(results.groupby(["model", "position"])["spearman"].mean().unstack().round(3))

    print("\n=== Summary: average MAE across all backtest seasons ===\n")
    print(results.groupby(["model", "position"])["mae"].mean().unstack().round(1))

    import pickle
    with open("weights/position_models_v2.pkl", "wb") as f:
        pickle.dump(final_models, f)
    print("\nSaved trained models to position_models_v2.pkl")
