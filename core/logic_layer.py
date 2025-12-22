import numpy as np
import pandas as pd
from typing import Dict, Any, Optional, List, Tuple

class LogicLayer:

    @staticmethod
    def min_max_normalize(series: pd.Series) -> pd.Series:
        return (series - series.min()) / (series.max() - series.min() + 1e-9)

    @staticmethod
    def calculate_ecoscore(brand_data: pd.DataFrame, full_dataset: pd.DataFrame) -> Dict[str, Any]:
        df = full_dataset.copy()
        current_year = 2025
        df["recency_weight"] = 1 / (current_year - df["Year"] + 1)

        df["carbon_norm"] = 1 - LogicLayer.min_max_normalize(df["Carbon_Emissions_tCO2e"])
        df["water_norm"] = 1 - LogicLayer.min_max_normalize(df["Water_Usage_Million_Litres"])
        df["waste_norm"] = 1 - LogicLayer.min_max_normalize(df["Landfill_Waste_Tonnes"])
        df["release_norm"] = 1 - LogicLayer.min_max_normalize(df["Release_Cycles_Per_Year"])
        df["child_labor_norm"] = 1 - LogicLayer.min_max_normalize(df["Child_Labor_Incidents"])
        df["hours_norm"] = 1 - LogicLayer.min_max_normalize(df["Working_Hours_Per_Week"])
        df["wage_norm"] = LogicLayer.min_max_normalize(df["Avg_Worker_Wage_USD"])
        df["transparency_norm"] = LogicLayer.min_max_normalize(df["Transparency_Index"])
        df["compliance_norm"] = LogicLayer.min_max_normalize(df["Compliance_Score"])
        df["ethical_norm"] = LogicLayer.min_max_normalize(df["Ethical_Rating"])
        df["sustainability_norm"] = LogicLayer.min_max_normalize(df["Sustainability_Score"])
        df["env_cost_norm"] = 1 - LogicLayer.min_max_normalize(df["Env_Cost_Index"])

        weights = {
            "carbon": 0.12, "water": 0.08, "waste": 0.08, "release": 0.05,
            "child_labor": 0.10, "hours": 0.05, "wage": 0.10,
            "transparency": 0.08, "compliance": 0.08, "ethical": 0.10,
            "sustainability": 0.10, "env_cost": 0.06
        }

        df["row_score"] = (
            weights["carbon"] * df["carbon_norm"] +
            weights["water"] * df["water_norm"] +
            weights["waste"] * df["waste_norm"] +
            weights["release"] * df["release_norm"] +
            weights["child_labor"] * df["child_labor_norm"] +
            weights["hours"] * df["hours_norm"] +
            weights["wage"] * df["wage_norm"] +
            weights["transparency"] * df["transparency_norm"] +
            weights["compliance"] * df["compliance_norm"] +
            weights["ethical"] * df["ethical_norm"] +
            weights["sustainability"] * df["sustainability_norm"] +
            weights["env_cost"] * df["env_cost_norm"]
        ) * 100

        brand_name = brand_data.iloc[0]["Brand"]
        brand_df = df[df["Brand"].str.lower() == brand_name.lower()].copy()
        total_weight = brand_df["recency_weight"].sum()
        ecoscore = (brand_df["row_score"] * brand_df["recency_weight"]).sum() / total_weight

        latest_row = brand_df.loc[brand_df["Year"].idxmax()]
        avg_metrics = brand_df.agg({
            "Carbon_Emissions_tCO2e": "mean",
            "Water_Usage_Million_Litres": "mean",
            "Landfill_Waste_Tonnes": "mean",
            "Avg_Worker_Wage_USD": "mean",
            "Transparency_Index": "mean",
            "Release_Cycles_Per_Year": "mean",
            "Child_Labor_Incidents": "sum",
            "Working_Hours_Per_Week": "mean",
            "Compliance_Score": "mean",
            "Ethical_Rating": "mean",
            "Sustainability_Score": "mean",
        })

        return {
            "brand": latest_row["Brand"],
            "ecoscore": round(ecoscore, 1),
            "data_points": len(brand_df),
            "years_covered": f"{int(brand_df['Year'].min())}-{int(brand_df['Year'].max())}",
            "carbon": round(avg_metrics["Carbon_Emissions_tCO2e"], 1),
            "water": round(avg_metrics["Water_Usage_Million_Litres"], 1),
            "waste": round(avg_metrics["Landfill_Waste_Tonnes"], 1),
            "wage": round(avg_metrics["Avg_Worker_Wage_USD"], 2),
            "transparency": round(avg_metrics["Transparency_Index"], 1),
            "release_cycles": round(avg_metrics["Release_Cycles_Per_Year"], 1),
            "child_labor_total": int(avg_metrics["Child_Labor_Incidents"]),
            "working_hours": round(avg_metrics["Working_Hours_Per_Week"], 1),
            "compliance": round(avg_metrics["Compliance_Score"], 1),
            "ethical_rating": round(avg_metrics["Ethical_Rating"], 2),
            "sustainability_raw": round(avg_metrics["Sustainability_Score"], 1),
        }

    @staticmethod
    def get_verdict(score: float) -> Tuple[str, str]:
        if score >= 85:
            return "Excellent", "🌟"
        elif score >= 70:
            return "Good", "✅"
        elif score >= 65:
            return "Moderate", "⚠️"
        elif score >= 30:
            return "Poor", "🔶"
        else:
            return "Very Poor", "❌"

    @staticmethod
    def calculate_category_scores(brand_result: Dict[str, Any]) -> Dict[str, float]:
        carbon_score = max(0, min(100, 100 - (brand_result['carbon'] / 200) * 100))
        water_score = max(0, min(100, 100 - (brand_result['water'] / 300) * 100))
        labor_score = (brand_result['ethical_rating'] / 5) * 100
        waste_score = max(0, min(100, 100 - (brand_result['waste'] / 100) * 100))
        transparency_score = brand_result['transparency']

        return {
            "carbon": round(carbon_score, 1),
            "water": round(water_score, 1),
            "labor": round(labor_score, 1),
            "waste": round(waste_score, 1),
            "transparency": round(transparency_score, 1)
        }

    @staticmethod
    def get_sustainable_alternatives(current_score: float, all_brands: List[str],
                                     data_layer) -> List[str]:
        better_brands = []
        for brand in all_brands:
            brand_data = data_layer.get_brand_data(brand)
            if brand_data is not None:
                result = LogicLayer.calculate_ecoscore(brand_data, data_layer.df)
                if result['ecoscore'] > current_score + 15:
                    better_brands.append((brand, result['ecoscore']))

        better_brands.sort(key=lambda x: x[1], reverse=True)
        return [b[0] for b in better_brands[:5]]
