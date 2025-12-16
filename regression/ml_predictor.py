import joblib
import numpy as np
import os

_model = None
_scaler = None
_feature_cols = None
_feature_stats = None

def load_model():
    global _model, _scaler, _feature_cols, _feature_stats

    if _model is None:
        model_dir = os.path.join(os.path.dirname(__file__), "..", "model")
        _model = joblib.load(os.path.join(model_dir, "ecoscore_model.joblib"))
        _scaler = joblib.load(os.path.join(model_dir, "scaler.joblib"))
        _feature_cols = joblib.load(os.path.join(model_dir, "feature_cols.joblib"))
        _feature_stats = joblib.load(os.path.join(model_dir, "feature_stats.joblib"))

    return _model, _scaler, _feature_cols, _feature_stats

def predict_ecoscore(
    carbon_emissions: float = None,
    water_usage: float = None,
    landfill_waste: float = None,
    worker_wage: float = None,
    working_hours: float = None,
    child_labor_incidents: int = None,
    release_cycles: int = None,
    monthly_production: float = None,
    avg_item_price: float = None,
    env_cost_index: float = None,
    transparency_index: float = None,
    return_rate: float = None,
) -> dict:
    """
    Predict EcoScore using the trained ML model.

    Parameters (all optional - missing values use dataset median):
    - carbon_emissions: tCO2e emissions
    - water_usage: Million liters
    - landfill_waste: Tonnes
    - worker_wage: USD average wage
    - working_hours: Hours per week
    - child_labor_incidents: Count of incidents
    - release_cycles: Fashion cycles per year (higher = more fast fashion)
    - monthly_production: Tonnes produced monthly
    - avg_item_price: USD average price
    - env_cost_index: Environmental cost index (0-1)
    - transparency_index: Transparency score (0-100)
    - return_rate: Return rate percentage

    Returns:
    - dict with ecoscore, verdict, and confidence info
    """
    model, scaler, feature_cols, feature_stats = load_model()

    input_map = {
        "Carbon_Emissions_tCO2e": carbon_emissions,
        "Water_Usage_Million_Litres": water_usage,
        "Landfill_Waste_Tonnes": landfill_waste,
        "Avg_Worker_Wage_USD": worker_wage,
        "Working_Hours_Per_Week": working_hours,
        "Child_Labor_Incidents": child_labor_incidents,
        "Release_Cycles_Per_Year": release_cycles,
        "Monthly_Production_Tonnes": monthly_production,
        "Avg_Item_Price_USD": avg_item_price,
        "Env_Cost_Index": env_cost_index,
        "Transparency_Index": transparency_index,
        "Return_Rate_Percent": return_rate,
    }

    features = []
    provided_count = 0
    for col in feature_cols:
        val = input_map.get(col)
        if val is not None:
            features.append(val)
            provided_count += 1
        else:
            features.append(feature_stats[col]["50%"])

    X = np.array(features).reshape(1, -1)
    X_scaled = scaler.transform(X)

    score = model.predict(X_scaled)[0]
    score = max(0, min(100, score))

    if score >= 85:
        verdict, emoji = "Excellent", "🌟"
    elif score >= 70:
        verdict, emoji = "Good", "✅"
    elif score >= 65:
        verdict, emoji = "Moderate", "⚠️"
    elif score >= 30:
        verdict, emoji = "Poor", "🔶"
    else:
        verdict, emoji = "Very Poor", "❌"

    confidence = "high" if provided_count >= 8 else "medium" if provided_count >= 4 else "low"

    return {
        "ecoscore": round(score, 1),
        "verdict": verdict,
        "emoji": emoji,
        "confidence": confidence,
        "features_provided": provided_count,
        "features_total": len(feature_cols),
    }


def get_prediction_prompt_for_llm():
    """
    Returns a description of the predict_ecoscore function for LLM to understand.
    """
    return """
You have access to an ML model that predicts EcoScores. To use it, extract these metrics from user input:

FUNCTION: predict_ecoscore()
PARAMETERS (all optional):
- carbon_emissions: CO2 emissions in tCO2e
- water_usage: Water usage in million liters
- landfill_waste: Waste in tonnes
- worker_wage: Average worker wage in USD
- working_hours: Working hours per week
- child_labor_incidents: Number of child labor incidents
- release_cycles: Fashion release cycles per year (12+ = fast fashion)
- monthly_production: Monthly production in tonnes
- avg_item_price: Average item price in USD
- env_cost_index: Environmental cost index (0-1 scale)
- transparency_index: Transparency score (0-100)
- return_rate: Product return rate percentage

RETURNS: ecoscore (0-100), verdict, confidence level

When user provides partial info, call with available parameters. Missing values use industry medians.
"""


if __name__ == "__main__":
    result = predict_ecoscore(
        carbon_emissions=10000,
        water_usage=200,
        landfill_waste=500,
        worker_wage=150,
        working_hours=48,
        child_labor_incidents=2,
        release_cycles=20,
    )
    print(f"Test prediction: {result}")
