import os
import requests
from typing import Dict, Any, List, Optional
from enum import Enum

class OutputFormat(Enum):
    TABLE = "table"
    BULLETS = "bullets"
    CHECKLIST = "checklist"
    NUMBERED = "numbered"

class LLMFormatter:

    STRICT_SYSTEM_PROMPT = """You are a structured sustainability data formatter. Your role is STRICTLY LIMITED to:

1. Explaining EcoScore results (interpreting numerical scores and metrics)
2. Summarizing fast fashion impacts (presenting statistical data)
3. Providing structured recommendations (actionable steps based on data)
4. Formatting output using tables, bullet points, checklists, or numbered lists

CRITICAL CONSTRAINTS:
- DO NOT engage in free-form conversation
- DO NOT answer questions outside these 4 functions
- DO NOT write long paragraphs (max 2-3 sentences per point)
- ALWAYS use structured formatting (tables/bullets/checklists)
- Be concise, factual, and data-driven
- Separate facts from recommendations clearly

Output format instructions:
- Use markdown tables for comparisons and metrics
- Use bullet points (•) for lists of facts
- Use checkboxes (- [ ]) for actionable recommendations
- Use numbered lists (1. 2. 3.) for sequential steps
- Keep each point to 1-2 lines maximum

If asked something outside your scope, respond ONLY with:
"I can only help with: (1) EcoScore explanations, (2) Fast fashion impact summaries, (3) Sustainability recommendations, (4) Product comparisons."
"""

    def __init__(self, api_key: str, api_url: str, model_name: str):
        self.api_key = api_key
        self.api_url = api_url
        self.model_name = model_name

    def _call_llm(self, user_prompt: str, context: Optional[Dict[str, Any]] = None) -> Optional[str]:
        messages = [{"role": "system", "content": self.STRICT_SYSTEM_PROMPT}]

        if context:
            context_str = f"DATA CONTEXT:\n{self._format_context(context)}\n\n"
            user_prompt = context_str + user_prompt

        messages.append({"role": "user", "content": user_prompt})

        payload = {
            "model": self.model_name,
            "messages": messages,
            "temperature": 0.2,
            "max_tokens": 500,
            "stream": False,
        }

        try:
            response = requests.post(
                self.api_url,
                headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                json=payload,
                timeout=30,
            )

            if response.status_code != 200:
                return None

            return response.json().get("choices", [{}])[0].get("message", {}).get("content", "")
        except Exception:
            return None

    def _format_context(self, context: Dict[str, Any]) -> str:
        lines = []
        for key, value in context.items():
            if isinstance(value, dict):
                lines.append(f"{key}:")
                for k, v in value.items():
                    lines.append(f"  - {k}: {v}")
            else:
                lines.append(f"{key}: {value}")
        return "\n".join(lines)

    def explain_ecoscore(self, brand: str, score: float, metrics: Dict[str, Any]) -> str:
        prompt = f"""Explain the EcoScore for {brand} (score: {score}/100).

Format as:
1. Brief score interpretation (1 sentence)
2. Table showing key metrics vs industry average
3. Bullet points (3-4) highlighting strengths or weaknesses

Keep it concise and structured."""

        return self._call_llm(prompt, context={"brand_metrics": metrics}) or "Unable to generate explanation."

    def summarize_fast_fashion_impacts(self, impact_data: Dict[str, Any]) -> str:
        prompt = """Summarize fast fashion environmental and social impacts.

Format as:
1. Title: "Fast Fashion Impact Summary"
2. Table with key statistics (carbon, water, waste, labor)
3. Checklist (3-4 items) of main concerns

Be factual and data-driven."""

        return self._call_llm(prompt, context=impact_data) or "Unable to generate summary."

    def provide_recommendations(self, brand: str, score: float,
                               alternatives: List[str]) -> str:
        prompt = f"""Provide sustainability recommendations for someone considering {brand} (score: {score}/100).

Format as:
- [ ] Checklist item 1 (actionable recommendation)
- [ ] Checklist item 2
- [ ] Checklist item 3

Then list better alternatives as bullets.

Keep each item to 1 line."""

        context = {"current_brand": brand, "ecoscore": score, "alternatives": alternatives}
        return self._call_llm(prompt, context=context) or "Unable to generate recommendations."

    def format_comparison_table(self, brands_data: List[Dict[str, Any]]) -> str:
        prompt = """Create a comparison table for these brands.

Format as markdown table with columns:
| Brand | EcoScore | Carbon | Water | Labor Rating | Verdict |

Add 1-2 sentence summary after table."""

        return self._call_llm(prompt, context={"brands": brands_data}) or "Unable to create comparison."

    def format_product_advice(self, product_type: str,
                             sustainability_factors: Dict[str, Any]) -> str:
        prompt = f"""Provide structured advice for buying sustainable {product_type}.

Format as:
1. Numbered checklist (what to look for)
2. Bullet points (what to avoid)
3. Table of material recommendations

Keep concise."""

        return self._call_llm(prompt, context=sustainability_factors) or "Unable to generate advice."
