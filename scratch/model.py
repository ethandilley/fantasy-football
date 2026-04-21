"""
train_gbt_model.py

Train a gradient boosted model (XGBoost) on playergame_features
"""

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error
from xgboost import XGBRegressor
from xgboost.callback import EarlyStopping

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────
DATA_PATH = "test.csv"
MODEL_PATH = "test.pkl"

TARGET = "fantasy_points_ppr"

DROP_COLS = [
    "player_name",
    "game_id",
]

RANDOM_STATE = 42


# ─────────────────────────────────────────────
# LOAD DATA
# ─────────────────────────────────────────────
def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    return df


# ─────────────────────────────────────────────
# SPLIT DATA (TIME-BASED)
# ─────────────────────────────────────────────
def time_split(df: pd.DataFrame):
    df = df.sort_values(["season", "week"])

    train = df[df["season"] < 2023]
    val = df[df["season"] == 2023]
    test = df[df["season"] == 2024]

    return train, val, test


# ─────────────────────────────────────────────
# PREP FEATURES
# ─────────────────────────────────────────────
def prepare_features(train, val, test):
    X_train = train.drop(columns=DROP_COLS + [TARGET])
    y_train = train[TARGET]

    X_val = val.drop(columns=DROP_COLS + [TARGET])
    y_val = val[TARGET]

    X_test = test.drop(columns=DROP_COLS + [TARGET])
    y_test = test[TARGET]

    # one-hot encoding
    X_train = pd.get_dummies(X_train, dummy_na=True)
    X_val = pd.get_dummies(X_val, dummy_na=True)
    X_test = pd.get_dummies(X_test, dummy_na=True)

    # align columns
    X_train, X_val = X_train.align(X_val, join="left", axis=1, fill_value=0)
    X_train, X_test = X_train.align(X_test, join="left", axis=1, fill_value=0)

    return X_train, y_train, X_val, y_val, X_test, y_test


# ─────────────────────────────────────────────
# TRAIN MODEL
# ─────────────────────────────────────────────


def train_model(X_train, y_train, X_val, y_val):
    model = XGBRegressor(
        n_estimators=500,  # reduce since no early stopping
        learning_rate=0.05,
        max_depth=6,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        eval_metric="rmse",
        n_jobs=-1,
    )

    model.fit(
        X_train,
        y_train,
        eval_set=[(X_val, y_val)],
        verbose=50,
    )

    return model


# ─────────────────────────────────────────────
# EVALUATE
# ─────────────────────────────────────────────
def evaluate(model, X, y, label="set"):
    preds = model.predict(X)

    rmse = mean_squared_error(y, preds) ** 0.5
    mae = mean_absolute_error(y, preds)

    print(f"{label} RMSE: {rmse:.4f}")
    print(f"{label} MAE:  {mae:.4f}")

    return preds


# ─────────────────────────────────────────────
# FEATURE IMPORTANCE
# ─────────────────────────────────────────────
def show_feature_importance(model, X_train):
    importance = pd.Series(
        model.feature_importances_, index=X_train.columns
    ).sort_values(ascending=False)

    print("\nTop 20 Features:")
    print(importance.head(20))


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
def main():
    print("Loading data...")
    df = load_data(DATA_PATH)

    print("Splitting data...")
    train, val, test = time_split(df)

    print("Preparing features...")
    X_train, y_train, X_val, y_val, X_test, y_test = prepare_features(train, val, test)

    print("Training model...")
    model = train_model(X_train, y_train, X_val, y_val)

    print("\nEvaluating...")
    evaluate(model, X_val, y_val, label="Validation")
    evaluate(model, X_test, y_test, label="Test")

    show_feature_importance(model, X_train)

    print("\nSaving model...")
    joblib.dump(model, MODEL_PATH)

    print("Done.")


if __name__ == "__main__":
    main()
