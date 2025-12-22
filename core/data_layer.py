import pandas as pd
import numpy as np
from typing import Optional, Dict, List, Any

class DataLayer:
    def __init__(self, csv_path: str):
        self.df = pd.read_csv(csv_path)
        self._cached_brands = None

    def get_brand_list(self) -> List[str]:
        if self._cached_brands is None:
            self._cached_brands = sorted(self.df["Brand"].dropna().unique().tolist())
        return self._cached_brands

    def detect_brand(self, text: str) -> Optional[str]:
        if not text:
            return None
        text_lower = f" {text.lower()} "
        for brand in self.get_brand_list():
            if f" {brand.lower()} " in text_lower:
                return brand
        return None

    def get_brand_data(self, brand_name: str) -> Optional[pd.DataFrame]:
        brand_rows = self.df[self.df["Brand"].str.lower() == brand_name.lower()]
        if brand_rows.empty:
            return None
        return brand_rows

    def get_industry_stats(self) -> Dict[str, Any]:
        return {
            "avg_carbon": float(self.df["Carbon_Emissions_tCO2e"].mean()),
            "avg_water": float(self.df["Water_Usage_Million_Litres"].mean()),
            "avg_waste": float(self.df["Landfill_Waste_Tonnes"].mean()),
            "avg_wage": float(self.df["Avg_Worker_Wage_USD"].mean()),
            "avg_transparency": float(self.df["Transparency_Index"].mean()),
            "total_brands": len(self.df["Brand"].unique()),
            "data_year_range": f"{int(self.df['Year'].min())}-{int(self.df['Year'].max())}"
        }

    def get_fast_fashion_impacts(self) -> Dict[str, Any]:
        high_release_brands = self.df[self.df["Release_Cycles_Per_Year"] >= 12]

        return {
            "total_carbon": float(high_release_brands["Carbon_Emissions_tCO2e"].sum()),
            "total_water": float(high_release_brands["Water_Usage_Million_Litres"].sum()),
            "total_waste": float(high_release_brands["Landfill_Waste_Tonnes"].sum()),
            "avg_worker_wage": float(high_release_brands["Avg_Worker_Wage_USD"].mean()),
            "total_child_labor_incidents": int(high_release_brands["Child_Labor_Incidents"].sum()),
            "brands_analyzed": len(high_release_brands["Brand"].unique()),
            "avg_working_hours": float(high_release_brands["Working_Hours_Per_Week"].mean())
        }
