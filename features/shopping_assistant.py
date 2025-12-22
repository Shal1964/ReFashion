from typing import Dict, Any, List, Optional
from core.data_layer import DataLayer
from core.logic_layer import LogicLayer
from core.llm_formatter import LLMFormatter

class ConsciousShoppingAssistant:

    SHOPPING_CRITERIA = {
        "budget": ["under_50", "50_100", "100_200", "over_200"],
        "priority": ["environmental", "ethical_labor", "durability", "transparency"],
        "category": ["basics", "workwear", "activewear", "formal", "casual"]
    }

    def __init__(self, data_layer: DataLayer, llm_formatter: LLMFormatter):
        self.data_layer = data_layer
        self.llm_formatter = llm_formatter
        self.logic = LogicLayer()

    def get_brand_recommendations(self, min_score: float = 70,
                                  max_results: int = 10) -> Dict[str, Any]:
        all_brands = self.data_layer.get_brand_list()
        recommendations = []

        for brand in all_brands:
            brand_data = self.data_layer.get_brand_data(brand)
            if brand_data is not None:
                result = self.logic.calculate_ecoscore(brand_data, self.data_layer.df)
                if result['ecoscore'] >= min_score:
                    recommendations.append({
                        "brand": brand,
                        "ecoscore": result['ecoscore'],
                        "verdict": self.logic.get_verdict(result['ecoscore'])[0],
                        "carbon": result['carbon'],
                        "transparency": result['transparency'],
                        "ethical_rating": result['ethical_rating']
                    })

        recommendations.sort(key=lambda x: x['ecoscore'], reverse=True)
        recommendations = recommendations[:max_results]

        formatted = self.llm_formatter.format_comparison_table(recommendations)

        return {
            "success": True,
            "criteria": f"EcoScore >= {min_score}",
            "count": len(recommendations),
            "recommendations": recommendations,
            "formatted_table": formatted
        }

    def get_alternatives_for_brand(self, brand_name: str,
                                   count: int = 5) -> Dict[str, Any]:
        brand_data = self.data_layer.get_brand_data(brand_name)
        if brand_data is None:
            return {
                "success": False,
                "message": f"Brand '{brand_name}' not found"
            }

        current_result = self.logic.calculate_ecoscore(brand_data, self.data_layer.df)
        current_score = current_result['ecoscore']

        alternatives = self.logic.get_sustainable_alternatives(
            current_score,
            self.data_layer.get_brand_list(),
            self.data_layer
        )[:count]

        alt_details = []
        for alt_brand in alternatives:
            alt_data = self.data_layer.get_brand_data(alt_brand)
            if alt_data is not None:
                alt_result = self.logic.calculate_ecoscore(alt_data, self.data_layer.df)
                alt_details.append({
                    "brand": alt_brand,
                    "ecoscore": alt_result['ecoscore'],
                    "improvement": round(alt_result['ecoscore'] - current_score, 1),
                    "verdict": self.logic.get_verdict(alt_result['ecoscore'])[0]
                })

        recommendations_text = self.llm_formatter.provide_recommendations(
            brand_name,
            current_score,
            [a['brand'] for a in alt_details]
        )

        return {
            "success": True,
            "current_brand": brand_name,
            "current_score": current_score,
            "alternatives": alt_details,
            "structured_recommendations": recommendations_text
        }

    def get_shopping_checklist(self, product_category: str) -> Dict[str, Any]:
        prompt = f"""Create a conscious shopping checklist for buying {product_category}.

Format as:
## Before You Buy
- [ ] Checklist item 1
- [ ] Checklist item 2
- [ ] Checklist item 3

## What to Look For
• Bullet point 1
• Bullet point 2
• Bullet point 3

## Red Flags to Avoid
• Warning 1
• Warning 2
• Warning 3

Keep each point to one line."""

        context = {
            "category": product_category,
            "sustainable_materials": ["organic cotton", "recycled polyester", "hemp", "linen"],
            "certifications": ["GOTS", "Fair Trade", "B Corp", "OEKO-TEX"]
        }

        checklist = self.llm_formatter._call_llm(prompt, context=context)

        return {
            "success": True,
            "category": product_category,
            "checklist": checklist or "Unable to generate checklist"
        }

    def compare_purchase_options(self, brands: List[str]) -> Dict[str, Any]:
        if len(brands) < 2:
            return {
                "success": False,
                "message": "Need at least 2 brands to compare"
            }

        comparisons = []
        for brand in brands:
            brand_data = self.data_layer.get_brand_data(brand)
            if brand_data is not None:
                result = self.logic.calculate_ecoscore(brand_data, self.data_layer.df)
                comparisons.append({
                    "brand": brand,
                    "ecoscore": result['ecoscore'],
                    "verdict": self.logic.get_verdict(result['ecoscore'])[0],
                    "carbon": result['carbon'],
                    "water": result['water'],
                    "labor_rating": result['ethical_rating'],
                    "transparency": result['transparency']
                })

        if not comparisons:
            return {
                "success": False,
                "message": "No valid brands found in database"
            }

        comparison_table = self.llm_formatter.format_comparison_table(comparisons)

        best_option = max(comparisons, key=lambda x: x['ecoscore'])

        return {
            "success": True,
            "brands_compared": len(comparisons),
            "comparisons": comparisons,
            "best_choice": best_option['brand'],
            "formatted_comparison": comparison_table
        }
