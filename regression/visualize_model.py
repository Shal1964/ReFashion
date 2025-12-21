import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, r2_score
import joblib
import matplotlib.pyplot as plt
import seaborn as sns
import os

def load_model_artifacts():
    model_path = os.path.join(os.path.dirname(__file__), "..", "model")
    model = joblib.load(os.path.join(model_path, "ecoscore_model.joblib"))
    scaler = joblib.load(os.path.join(model_path, "scaler.joblib"))
    feature_cols = joblib.load(os.path.join(model_path, "feature_cols.joblib"))
    return model, scaler, feature_cols

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

def generate_training_visualization():
    csv_path = os.path.join(os.path.dirname(__file__), "..", "true_cost_fast_fashion.csv")
    df = pd.read_csv(csv_path)

    model, scaler, feature_cols = load_model_artifacts()

    X, y, _ = create_features_and_target(df)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    X_train_scaled = scaler.transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    y_pred_train = model.predict(X_train_scaled)
    y_pred_test = model.predict(X_test_scaled)

    train_r2 = r2_score(y_train, y_pred_train)
    test_r2 = r2_score(y_test, y_pred_test)
    train_mae = mean_absolute_error(y_train, y_pred_train)
    test_mae = mean_absolute_error(y_test, y_pred_test)

    importances = pd.DataFrame({
        "feature": feature_cols,
        "importance": model.feature_importances_
    }).sort_values("importance", ascending=False)

    sns.set_style("whitegrid")
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle("ML Model Training Results", fontsize=16, fontweight='bold', y=0.995)

    axes[0, 0].scatter(y_train, y_pred_train, alpha=0.5, s=30, color='#B7D292', edgecolors='#9cb87a', linewidth=0.5, label='Train')
    axes[0, 0].scatter(y_test, y_pred_test, alpha=0.5, s=30, color='#FF9999', edgecolors='#FF6666', linewidth=0.5, label='Test')
    min_val = min(y_train.min(), y_test.min(), y_pred_train.min(), y_pred_test.min())
    max_val = max(y_train.max(), y_test.max(), y_pred_train.max(), y_pred_test.max())
    axes[0, 0].plot([min_val, max_val], [min_val, max_val], 'k--', lw=2, alpha=0.7)
    axes[0, 0].set_xlabel('Actual EcoScore', fontsize=11, fontweight='bold')
    axes[0, 0].set_ylabel('Predicted EcoScore', fontsize=11, fontweight='bold')
    axes[0, 0].set_title('Predicted vs Actual', fontsize=12, fontweight='bold', pad=10)
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)

    residuals_train = y_train - y_pred_train
    residuals_test = y_test - y_pred_test
    axes[0, 1].scatter(y_pred_train, residuals_train, alpha=0.5, s=30, color='#B7D292', edgecolors='#9cb87a', linewidth=0.5, label='Train')
    axes[0, 1].scatter(y_pred_test, residuals_test, alpha=0.5, s=30, color='#FF9999', edgecolors='#FF6666', linewidth=0.5, label='Test')
    axes[0, 1].axhline(y=0, color='k', linestyle='--', lw=2, alpha=0.7)
    axes[0, 1].set_xlabel('Predicted EcoScore', fontsize=11, fontweight='bold')
    axes[0, 1].set_ylabel('Residuals', fontsize=11, fontweight='bold')
    axes[0, 1].set_title('Residual Plot', fontsize=12, fontweight='bold', pad=10)
    axes[0, 1].legend()
    axes[0, 1].grid(True, alpha=0.3)

    top_features = importances.head(10)
    colors = plt.cm.YlGn(np.linspace(0.4, 0.8, len(top_features)))
    axes[1, 0].barh(range(len(top_features)), top_features['importance'], color=colors, edgecolor='#2d3436', linewidth=0.8)
    axes[1, 0].set_yticks(range(len(top_features)))
    axes[1, 0].set_yticklabels([f.replace('_', ' ').title() for f in top_features['feature']], fontsize=9)
    axes[1, 0].set_xlabel('Importance', fontsize=11, fontweight='bold')
    axes[1, 0].set_title('Top 10 Feature Importances', fontsize=12, fontweight='bold', pad=10)
    axes[1, 0].invert_yaxis()
    axes[1, 0].grid(True, alpha=0.3, axis='x')

    metrics_data = {
        'Metric': ['Train R²', 'Test R²', 'Train MAE', 'Test MAE'],
        'Value': [f'{train_r2:.3f}', f'{test_r2:.3f}', f'{train_mae:.2f}', f'{test_mae:.2f}']
    }
    axes[1, 1].axis('tight')
    axes[1, 1].axis('off')
    table = axes[1, 1].table(cellText=[[m, v] for m, v in zip(metrics_data['Metric'], metrics_data['Value'])],
                              colLabels=['Metric', 'Value'],
                              cellLoc='left',
                              loc='center',
                              colWidths=[0.5, 0.3])
    table.auto_set_font_size(False)
    table.set_fontsize(11)
    table.scale(1, 2.5)

    for i in range(len(metrics_data['Metric']) + 1):
        if i == 0:
            table[(i, 0)].set_facecolor('#9cb87a')
            table[(i, 1)].set_facecolor('#9cb87a')
            table[(i, 0)].set_text_props(weight='bold', color='white')
            table[(i, 1)].set_text_props(weight='bold', color='white')
        else:
            color = '#f0f7e8' if i % 2 == 0 else '#ffffff'
            table[(i, 0)].set_facecolor(color)
            table[(i, 1)].set_facecolor(color)
            table[(i, 0)].set_text_props(weight='bold')

    axes[1, 1].set_title('Model Performance Metrics', fontsize=12, fontweight='bold', pad=20)

    info_text = f"Dataset: {len(X)} samples | Features: {len(feature_cols)} | Algorithm: Gradient Boosting"
    fig.text(0.5, 0.02, info_text, ha='center', fontsize=10, style='italic', color='#636e72')

    plt.tight_layout(rect=[0, 0.03, 1, 0.99])

    return fig, {
        'train_r2': train_r2,
        'test_r2': test_r2,
        'train_mae': train_mae,
        'test_mae': test_mae,
        'n_samples': len(X),
        'n_features': len(feature_cols)
    }
