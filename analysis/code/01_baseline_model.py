"""
Step 3a: Baseline models

Before trusting anything fancy, we need a floor to beat. Two dumb-simple
baselines, computed per position:

1. PERSISTENCE baseline: "next season = this season."
   The simplest possible prediction. If XGBoost can't beat this, it isn't
   learning anything useful.

2. SHRINKAGE baseline: "next season = blend of this season's rate and the
   position average, weighted by how many games we saw them play."
   A player who played 2 games isn't as reliable a signal as one who played
   17 -- small samples should regress toward the position mean. This is a
   classic sabermetrics trick (same idea as "regression to the mean" in
   batting averages) and it's a genuinely strong baseline for sports data,
   often close to what fancier models achieve.

Both baselines predict `next_total_fantasy_points`, the same target the
XGBoost models in step 3b will predict, so they're directly comparable in
the backtest.
"""

import pandas as pd
import numpy as np

SHRINKAGE_K = 6  # "worth of games" the position-average prior counts for.
                  # Higher K = more shrinkage toward the mean for small samples.


def add_baseline_predictions(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # --- Baseline 1: persistence ---
    df["pred_persistence"] = df["total_fantasy_points"]

    # --- Baseline 2: shrinkage toward position-season mean ---
    # Position averages computed only from the training rows passed in --
    # caller is responsible for only passing in "seasons before the test
    # season" so this doesn't leak future information.
    pos_avg = df.groupby("position")["total_fantasy_points"].transform("mean")
    weight = df["games_played"] / (df["games_played"] + SHRINKAGE_K)
    df["pred_shrinkage"] = weight * df["total_fantasy_points"] + (1 - weight) * pos_avg

    return df


if __name__ == "__main__":
    train = pd.read_csv("data/train_dataset.csv")
    train = add_baseline_predictions(train)
    print(train[["player_name", "season", "position", "games_played",
                 "total_fantasy_points", "pred_persistence", "pred_shrinkage",
                 "next_total_fantasy_points"]].sample(10, random_state=1))
