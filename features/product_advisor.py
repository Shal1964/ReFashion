from typing import Dict, Any, List, Optional
from core.data_layer import DataLayer
from core.logic_layer import LogicLayer
from core.llm_formatter import LLMFormatter

try:
    from regression.ml_predictor import predict_ecoscore
    ML_AVAILABLE = True
except Exception:
    ML_AVAILABLE = False

class ProductSustainabilityAdvisor:

    PRODUCT_CATEGORIES = {
        "t-shirt": {"carbon_intensive": False, "water_intensive": True},
        "jeans": {"carbon_intensive": True, "water_intensive": True},
        "jacket": {"carbon_intensive": True, "water_intensive": False},
        "dress": {"carbon_intensive": False, "water_intensive": True},
        "shoes": {"carbon_intensive": True, "water_intensive": False},
        "sweater": {"carbon_intensive": False, "water_intensive": True}
    }

    SUSTAINABLE_MATERIALS = {
        "organic cotton": {"score": 85, "impact": "Low water, no pesticides"},
        "recycled polyester": {"score": 75, "impact": "Reduces plastic waste"},
        "hemp": {"score": 90, "impact": "Minimal water, fast growing"},
        "linen": {"score": 88, "impact": "Low water, biodegradable"},
        "tencel": {"score": 82, "impact": "Sustainable wood pulp"},
        "recycled cotton": {"score": 80, "impact": "Reduces waste, saves water"}
    }

    AVOID_MATERIALS = {
        "virgin polyester": {"score": 30, "impact": "Petroleum-based, microplastics"},
        "conventional cotton": {"score": 45, "impact": "High water, pesticides"},
        "acrylic": {"score": 25, "impact": "Synthetic, non-biodegradable"},
        "nylon": {"score": 35, "impact": "Energy-intensive production"}
    }

    def __init__(self, data_layer: DataLayer, llm_formatter: LLMFormatter):
        self.data_layer = data_layer
        self.llm_formatter = llm_formatter
        self.logic = LogicLayer()
        self.ml_available = ML_AVAILABLE

    def analyze_product(self, product_type: str, brand: str,
                       materials: Optional[List[str]] = None) -> Dict[str, Any]:
        product_type_lower = product_type.lower()

        brand_score = None
        if brand:
            brand_data = self.data_layer.get_brand_data(brand)
            if brand_data is not None:
                result = self.logic.calculate_ecoscore(brand_data, self.data_layer.df)
                brand_score = result['ecoscore']

        material_scores = []
        if materials:
            for material in materials:
                material_lower = material.lower()
                if material_lower in self.SUSTAINABLE_MATERIALS:
                    material_scores.append({
                        "name": material,
                        "score": self.SUSTAINABLE_MATERIALS[material_lower]["score"],
                        "impact": self.SUSTAINABLE_MATERIALS[material_lower]["impact"],
                        "verdict": "recommended"
                    })
                elif material_lower in self.AVOID_MATERIALS:
                    material_scores.append({
                        "name": material,
                        "score": self.AVOID_MATERIALS[material_lower]["score"],
                        "impact": self.AVOID_MATERIALS[material_lower]["impact"],
                        "verdict": "avoid"
                    })

        overall_score = 0
        if brand_score and material_scores:
            avg_material = sum(m["score"] for m in material_scores) / len(material_scores)
            overall_score = (brand_score * 0.4 + avg_material * 0.6)
        elif brand_score:
            overall_score = brand_score
        elif material_scores:
            overall_score = sum(m["score"] for m in material_scores) / len(material_scores)

        sustainability_factors = {
            "product_type": product_type,
            "brand": brand,
            "brand_ecoscore": brand_score,
            "materials_analysis": material_scores,
            "overall_score": round(overall_score, 1) if overall_score > 0 else None
        }

        advice = self.llm_formatter.format_product_advice(
            product_type,
            sustainability_factors
        )

        return {
            "success": True,
            "product_type": product_type,
            "brand": brand,
            "overall_score": round(overall_score, 1) if overall_score > 0 else None,
            "brand_score": brand_score,
            "material_analysis": material_scores,
            "structured_advice": advice
        }

    def get_material_recommendations(self, use_case: str) -> Dict[str, Any]:
        recommended = [
            {"name": name, **data}
            for name, data in self.SUSTAINABLE_MATERIALS.items()
        ]
        recommended.sort(key=lambda x: x["score"], reverse=True)

        avoid = [
            {"name": name, **data}
            for name, data in self.AVOID_MATERIALS.items()
        ]
        avoid.sort(key=lambda x: x["score"])

        context = {
            "use_case": use_case,
            "recommended_materials": recommended,
            "materials_to_avoid": avoid
        }

        formatted = self.llm_formatter._call_llm(
            f"Create a structured guide for choosing sustainable materials for {use_case}. Format as table with materials, scores, and impacts.",
            context=context
        )

        return {
            "success": True,
            "use_case": use_case,
            "recommended": recommended,
            "avoid": avoid,
            "formatted_guide": formatted or "Unable to generate guide"
        }

    def predict_custom_product(self, **metrics) -> Dict[str, Any]:
        """
        Use ML model to predict EcoScore for custom product metrics.

        Parameters: Same as ml_predictor.predict_ecoscore()
        - carbon_emissions, water_usage, landfill_waste, worker_wage, etc.

        Returns: ML prediction with ecoscore, verdict, confidence
        """
        if not self.ml_available:
            return {
                "success": False,
                "message": "ML model not available. Install required packages."
            }

        try:
            result = predict_ecoscore(**metrics)
            return {
                "success": True,
                "ml_prediction": result,
                "metrics_provided": result['features_provided'],
                "total_metrics": result['features_total']
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"ML prediction failed: {str(e)}"
            }
