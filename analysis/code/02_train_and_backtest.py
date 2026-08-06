"""
Step 3b: Position-specific XGBoost models + backtest

WHAT THIS DOES
---------------
Trains one XGBoost regression model per position (QB/RB/WR/TE), each
predicting `next_total_fantasy_points` from this season's stats. Then
backtests: for each of the last several seasons, train only on data that
would have been available *before* that season, predict it, and compare
against what actually happened. This is the only honest way to know if the
model is any good -- training and testing on overlapping seasons would let
the model "see the future" and look artificially accurate.

Two metrics per backtest year, per position:
  - MAE (mean absolute error in fantasy points) -- how far off in raw points
  - Spearman rank correlation -- how well the model orders players relative
    to each other, which is what actually matters for drafting. You don't
    need to nail Christian McCaffrey's exact point total; you need to know
    he should be drafted before the WR3 on your board.

Both baselines from 03_baseline_model.py are included in the comparison, so
you can see whether XGBoost is actually earning its complexity.
"""

import pandas as pd
import numpy as np
from xgboost import XGBRegressor
from scipy.stats import spearmanr

SHRINKAGE_K = 6

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

FANTASY_POSITIONS = ["Quarterback", "Running Back", "Wide Receiver", "Tight End"]
TARGET = "next_total_fantasy_points"
BACKTEST_SEASONS = [2021, 2022, 2023, 2024]  # predict each of these using only prior data


def add_baseline_predictions(df: pd.DataFrame) -> pd.DataFrame:
    """Same baselines as 03_baseline_model.py, duplicated here so this
    script runs standalone without a cross-file import."""
    df = df.copy()
    df["pred_persistence"] = df["total_fantasy_points"]
    pos_avg = df.groupby("position")["total_fantasy_points"].transform("mean")
    weight = df["games_played"] / (df["games_played"] + SHRINKAGE_K)
    df["pred_shrinkage"] = weight * df["total_fantasy_points"] + (1 - weight) * pos_avg
    return df


def train_position_models(train_df: pd.DataFrame) -> dict:
    """One XGBoost model per position, trained on the rows given."""
    models = {}
    for pos in FANTASY_POSITIONS:
        sub = train_df[train_df["position"] == pos]
        X = sub[FEATURE_COLS]
        y = sub[TARGET]
        model = XGBRegressor(
            n_estimators=300,
            max_depth=4,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42,
            n_jobs=-1,
        )
        model.fit(X, y)
        models[pos] = model
    return models


def evaluate(df: pd.DataFrame, pred_col: str) -> dict:
    """MAE and Spearman rank correlation, per position, for one prediction column."""
    results = {}
    for pos in FANTASY_POSITIONS:
        sub = df[df["position"] == pos]
        if len(sub) < 5:
            continue
        mae = (sub[pred_col] - sub[TARGET]).abs().mean()
        rho, _ = spearmanr(sub[pred_col], sub[TARGET])
        results[pos] = {"mae": mae, "spearman": rho, "n": len(sub)}
    return results


def run_backtest(train_dataset_path: str):
    full = pd.read_csv(train_dataset_path)
    full = add_baseline_predictions(full)  # baselines don't need training, computed row-wise

    all_rows = []

    for test_season in BACKTEST_SEASONS:
        # Only use data strictly before the test season to train --
        # this is what prevents the model from "seeing the future."
        train_slice = full[full["season"] < test_season]
        test_slice = full[full["season"] == test_season].copy()

        if len(test_slice) == 0:
            print(f"Skipping {test_season}: no rows in that season (check BACKTEST_SEASONS)")
            continue

        models = train_position_models(train_slice)

        # predict on the test slice
        for pos in FANTASY_POSITIONS:
            mask = test_slice["position"] == pos
            if mask.sum() == 0:
                continue
            X_test = test_slice.loc[mask, FEATURE_COLS]
            test_slice.loc[mask, "pred_xgboost"] = models[pos].predict(X_test)

        for pred_col, label in [
            ("pred_persistence", "Persistence baseline"),
            ("pred_shrinkage", "Shrinkage baseline"),
            ("pred_xgboost", "XGBoost"),
        ]:
            metrics = evaluate(test_slice, pred_col)
            for pos, m in metrics.items():
                all_rows.append({
                    "test_season": test_season,
                    "model": label,
                    "position": pos,
                    "mae": round(m["mae"], 1),
                    "spearman": round(m["spearman"], 3),
                    "n": m["n"],
                })

    results_df = pd.DataFrame(all_rows)
    return results_df, models  # last-trained models (on data through 2024) kept for projection step


if __name__ == "__main__":
    results, final_models = run_backtest("data/train_dataset.csv")

    pd.set_option("display.width", 120)
    pd.set_option("display.max_rows", 200)

    print("\n=== Backtest results by season / model / position ===\n")
    print(results.to_string(index=False))

    print("\n=== Summary: average Spearman rank correlation across all backtest seasons ===\n")
    summary = results.groupby(["model", "position"])["spearman"].mean().unstack().round(3)
    print(summary)

    print("\n=== Summary: average MAE across all backtest seasons ===\n")
    summary_mae = results.groupby(["model", "position"])["mae"].mean().unstack().round(1)
    print(summary_mae)

    # save the final models (trained on all data through 2024, the latest
    # complete backtest year) for the projection step
    import pickle
    with open("weights/position_models.pkl", "wb") as f:
        pickle.dump(final_models, f)
    print("\nSaved trained models to position_models.pkl")
