from typing import Dict, Any, Optional, List
from core.data_layer import DataLayer
from core.logic_layer import LogicLayer
from core.llm_formatter import LLMFormatter

class EcoScoreCalculator:

    def __init__(self, data_layer: DataLayer, llm_formatter: LLMFormatter):
        self.data_layer = data_layer
        self.llm_formatter = llm_formatter
        self.logic = LogicLayer()

    def calculate_brand_score(self, brand_name: str) -> Optional[Dict[str, Any]]:
        brand_data = self.data_layer.get_brand_data(brand_name)
        if brand_data is None:
            return None

        result = self.logic.calculate_ecoscore(brand_data, self.data_layer.df)
        verdict, emoji = self.logic.get_verdict(result['ecoscore'])
        category_scores = self.logic.calculate_category_scores(result)

        return {
            "raw_data": result,
            "verdict": verdict,
            "emoji": emoji,
            "category_scores": category_scores,
            "brand": result['brand'],
            "ecoscore": result['ecoscore']
        }

    def get_explanation(self, brand_name: str) -> Dict[str, Any]:
        score_data = self.calculate_brand_score(brand_name)
        if score_data is None:
            return {
                "success": False,
                "message": f"Brand '{brand_name}' not found in database."
            }

        industry_stats = self.data_layer.get_industry_stats()

        metrics_context = {
            "brand_data": score_data['raw_data'],
            "industry_average": industry_stats,
            "category_breakdown": score_data['category_scores']
        }

        explanation = self.llm_formatter.explain_ecoscore(
            brand_name,
            score_data['ecoscore'],
            metrics_context
        )

        return {
            "success": True,
            "brand": brand_name,
            "score": score_data['ecoscore'],
            "verdict": score_data['verdict'],
            "emoji": score_data['emoji'],
            "raw_data": score_data['raw_data'],
            "category_scores": score_data['category_scores'],
            "explanation": explanation
        }

    def compare_brands(self, brand_names: List[str]) -> Dict[str, Any]:
        comparisons = []
        for brand in brand_names:
            score_data = self.calculate_brand_score(brand)
            if score_data:
                comparisons.append({
                    "brand": brand,
                    "ecoscore": score_data['ecoscore'],
                    "verdict": score_data['verdict'],
                    "carbon": score_data['raw_data']['carbon'],
                    "water": score_data['raw_data']['water'],
                    "labor_rating": score_data['raw_data']['ethical_rating']
                })

        if not comparisons:
            return {"success": False, "message": "No valid brands found"}

        comparison_table = self.llm_formatter.format_comparison_table(comparisons)

        return {
            "success": True,
            "brands": comparisons,
            "formatted_comparison": comparison_table
        }
