import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, r2_score
import joblib
import os

def load_and_prepare_data():
    df = pd.read_csv("true_cost_fast_fashion.csv")
    return df

def min_max_col(series):
    return (series - series.min()) / (series.max() - series.min() + 1e-9)

def create_features_and_target(df):
    feature_cols = [
        "Carbon_Emissions_tCO2e",
        "Water_Usage_Million_Litres",
        "Landfill_Waste_Tonnes",
        "Avg_Worker_Wage_USD",
        "Working_Hours_Per_Week",
        "Child_Labor_Incidents",
        "Release_Cycles_Per_Year",
        "Monthly_Production_Tonnes",
        "Avg_Item_Price_USD",
        "Env_Cost_Index",
        "Transparency_Index",
        "Return_Rate_Percent",
    ]

    df = df.copy()

    df["carbon_norm"] = 1 - min_max_col(df["Carbon_Emissions_tCO2e"])
    df["water_norm"] = 1 - min_max_col(df["Water_Usage_Million_Litres"])
    df["waste_norm"] = 1 - min_max_col(df["Landfill_Waste_Tonnes"])
    df["release_norm"] = 1 - min_max_col(df["Release_Cycles_Per_Year"])
    df["child_labor_norm"] = 1 - min_max_col(df["Child_Labor_Incidents"])
    df["hours_norm"] = 1 - min_max_col(df["Working_Hours_Per_Week"])
    df["wage_norm"] = min_max_col(df["Avg_Worker_Wage_USD"])
    df["transparency_norm"] = min_max_col(df["Transparency_Index"])
    df["env_cost_norm"] = 1 - min_max_col(df["Env_Cost_Index"])

    weights = {
        "carbon": 0.15,
        "water": 0.10,
        "waste": 0.10,
        "release": 0.08,
        "child_labor": 0.15,
        "hours": 0.07,
        "wage": 0.12,
        "transparency": 0.10,
        "env_cost": 0.13,
    }

    df["target_ecoscore"] = (
        weights["carbon"] * df["carbon_norm"] +
        weights["water"] * df["water_norm"] +
        weights["waste"] * df["waste_norm"] +
        weights["release"] * df["release_norm"] +
        weights["child_labor"] * df["child_labor_norm"] +
        weights["hours"] * df["hours_norm"] +
        weights["wage"] * df["wage_norm"] +
        weights["transparency"] * df["transparency_norm"] +
        weights["env_cost"] * df["env_cost_norm"]
    ) * 100

    X = df[feature_cols].copy()
    y = df["target_ecoscore"].copy()

    X = X.fillna(X.median())

    return X, y, feature_cols

def train_model():
    print("Loading data...")
    df = load_and_prepare_data()

    print("Creating features and computing target EcoScore...")
    X, y, feature_cols = create_features_and_target(df)

    print(f"Dataset size: {len(X)} samples")
    print(f"Features: {len(feature_cols)}")
    print(f"Target range: {y.min():.1f} - {y.max():.1f}")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    print("Fitting scaler...")
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    print("Training Gradient Boosting model...")
    model = GradientBoostingRegressor(
        n_estimators=200,
        max_depth=5,
        learning_rate=0.1,
        min_samples_split=10,
        min_samples_leaf=5,
        subsample=0.8,
        random_state=42
    )
    model.fit(X_train_scaled, y_train)

    print("\nEvaluating model...")
    y_pred_train = model.predict(X_train_scaled)
    y_pred_test = model.predict(X_test_scaled)

    print(f"Train MAE: {mean_absolute_error(y_train, y_pred_train):.2f}")
    print(f"Test MAE: {mean_absolute_error(y_test, y_pred_test):.2f}")
    print(f"Train R²: {r2_score(y_train, y_pred_train):.3f}")
    print(f"Test R²: {r2_score(y_test, y_pred_test):.3f}")

    print("\nFeature Importances:")
    importances = pd.DataFrame({
        "feature": feature_cols,
        "importance": model.feature_importances_
    }).sort_values("importance", ascending=False)
    print(importances.to_string(index=False))

    print("\nSaving model artifacts...")
    os.makedirs("model", exist_ok=True)
    joblib.dump(model, "model/ecoscore_model.joblib")
    joblib.dump(scaler, "model/scaler.joblib")
    joblib.dump(feature_cols, "model/feature_cols.joblib")

    feature_stats = X.describe().to_dict()
    joblib.dump(feature_stats, "model/feature_stats.joblib")

    print("Model saved to model/ directory")
    print("\nDone!")

    return model, scaler, feature_cols

if __name__ == "__main__":
    train_model()
