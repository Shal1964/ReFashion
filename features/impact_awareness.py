from typing import Dict, Any
from core.data_layer import DataLayer
from core.llm_formatter import LLMFormatter

class FashionImpactAwareness:

    IMPACT_TOPICS = {
        "fast_fashion": "Environmental and social impacts of rapid production cycles",
        "water_usage": "Water consumption in textile production",
        "carbon_emissions": "Greenhouse gas emissions from fashion industry",
        "textile_waste": "Landfill waste and disposal issues",
        "labor_rights": "Worker conditions and fair wages",
        "microplastics": "Synthetic fiber pollution in oceans",
        "chemical_pollution": "Dyes and treatment chemicals"
    }

    def __init__(self, data_layer: DataLayer, llm_formatter: LLMFormatter):
        self.data_layer = data_layer
        self.llm_formatter = llm_formatter

    def get_fast_fashion_summary(self) -> Dict[str, Any]:
        impact_data = self.data_layer.get_fast_fashion_impacts()

        summary = self.llm_formatter.summarize_fast_fashion_impacts(impact_data)

        return {
            "success": True,
            "topic": "Fast Fashion Impact",
            "data": impact_data,
            "structured_summary": summary
        }

    def get_industry_overview(self) -> Dict[str, Any]:
        stats = self.data_layer.get_industry_stats()

        prompt = """Create an industry overview with:
1. Table showing key industry averages
2. Bullet points (3-4) highlighting major concerns
3. Checklist of what consumers can do

Keep concise and factual."""

        formatted = self.llm_formatter._call_llm(prompt, context=stats)

        return {
            "success": True,
            "topic": "Fashion Industry Overview",
            "data": stats,
            "structured_overview": formatted or "Unable to generate overview"
        }

    def get_topic_info(self, topic: str) -> Dict[str, Any]:
        topic_lower = topic.lower().replace(" ", "_")

        if topic_lower not in self.IMPACT_TOPICS:
            return {
                "success": False,
                "message": f"Topic must be one of: {', '.join(self.IMPACT_TOPICS.keys())}"
            }

        if topic_lower == "fast_fashion":
            return self.get_fast_fashion_summary()

        stats = self.data_layer.get_industry_stats()

        prompt = f"""Explain {topic} impact in fashion industry.

Format as:
1. Brief definition (1 sentence)
2. Table with relevant statistics
3. Bullet points (3-4) showing key facts
4. Checklist (2-3) of mitigation actions

Use data provided. Keep structured and concise."""

        context = {
            "topic": self.IMPACT_TOPICS[topic_lower],
            "industry_stats": stats
        }

        formatted = self.llm_formatter._call_llm(prompt, context=context)

        return {
            "success": True,
            "topic": topic,
            "description": self.IMPACT_TOPICS[topic_lower],
            "structured_info": formatted or "Unable to generate information"
        }

    def get_available_topics(self) -> Dict[str, Any]:
        return {
            "success": True,
            "topics": [
                {"id": key, "description": value}
                for key, value in self.IMPACT_TOPICS.items()
            ]
        }
