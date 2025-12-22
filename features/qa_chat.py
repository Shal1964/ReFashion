from typing import Dict, Any, List
import requests
from core.llm_formatter import LLMFormatter

class QuestionAnswerChat:

    QA_SYSTEM_PROMPT = """You are a sustainable fashion expert assistant. You help users understand sustainability concepts related to fashion and clothing.

Your expertise covers:
• EcoScore metrics and what they mean
• Fast fashion impacts (environmental, social, economic)
• Sustainable materials and fabrics
• Ethical labor practices in fashion
• Brand sustainability practices
• Shopping tips for conscious consumers
• Clothing care and longevity
• Fashion industry terminology

RESPONSE GUIDELINES:
• Keep answers focused on sustainable fashion topics
• Use bullet points and structured formatting when helpful
• Provide specific, actionable information
• Keep responses concise (2-4 paragraphs max)
• If asked about specific brands, remind them to use the EcoScore Calculator feature
• If asked for shopping advice, suggest using the Conscious Shopping Assistant feature

Topics you SHOULD answer:
✓ "What does EcoScore measure?"
✓ "Why is water usage important in fashion?"
✓ "What makes a fabric sustainable?"
✓ "How can I make my clothes last longer?"
✓ "What is fast fashion?"
✓ "What certifications should I look for?"

Topics you should REDIRECT:
→ "Is Brand X sustainable?" → Redirect to Feature 1: EcoScore Calculator
→ "Should I buy this product?" → Redirect to Feature 2: Product Advisor
→ "What brands are best?" → Redirect to Feature 4: Shopping Assistant

Be friendly, educational, and helpful while staying focused on sustainable fashion education.
"""

    def __init__(self, llm_formatter: LLMFormatter):
        self.llm_formatter = llm_formatter
        self.conversation_history = []

    def ask_question(self, question: str, include_history: bool = False) -> Dict[str, Any]:
        """
        Answer a user's question about sustainable fashion.

        Args:
            question: The user's question
            include_history: Whether to include conversation history (for follow-ups)

        Returns:
            Dict with success status and answer
        """
        messages = [{"role": "system", "content": self.QA_SYSTEM_PROMPT}]

        if include_history and self.conversation_history:
            messages.extend(self.conversation_history[-4:])

        messages.append({"role": "user", "content": question})

        try:
            response = self._call_llm_direct(messages)

            if response:
                self.conversation_history.append({"role": "user", "content": question})
                self.conversation_history.append({"role": "assistant", "content": response})

                return {
                    "success": True,
                    "question": question,
                    "answer": response
                }
            else:
                return {
                    "success": False,
                    "message": "Unable to get response. Please try again."
                }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error: {str(e)}"
            }

    def _call_llm_direct(self, messages: List[Dict[str, str]]) -> str:
        """Call LLM API directly with messages."""
        payload = {
            "model": self.llm_formatter.model_name,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 800,
            "stream": False,
        }

        try:
            response = requests.post(
                self.llm_formatter.api_url,
                headers={
                    "Authorization": f"Bearer {self.llm_formatter.api_key}",
                    "Content-Type": "application/json"
                },
                json=payload,
                timeout=30,
            )

            if response.status_code != 200:
                return None

            return response.json().get("choices", [{}])[0].get("message", {}).get("content", "")
        except Exception:
            return None

    def clear_history(self):
        """Clear conversation history."""
        self.conversation_history = []

    def get_suggested_questions(self) -> List[str]:
        """Get a list of suggested questions users can ask."""
        return [
            "What does EcoScore measure and why is it important?",
            "How does fast fashion harm the environment?",
            "What are the most sustainable fabrics?",
            "How can I make my clothes last longer?",
            "What certifications should I look for when shopping?",
            "Why is water usage a big concern in fashion?",
            "What are microplastics and how do clothes contribute?",
            "How can I tell if a brand is greenwashing?",
            "What's the difference between organic and conventional cotton?",
            "How do I care for sustainable fabrics?"
        ]
