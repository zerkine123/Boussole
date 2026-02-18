import json
from groq import Groq
from app.schemas.search import SearchIntent
from app.core.config import settings


class SearchService:
    def __init__(self):
        api_key = settings.GROQ_API_KEY
        if not api_key:
            print("WARNING: GROQ_API_KEY not found in environment variables")
            self.client = None
        else:
            self.client = Groq(api_key=api_key)
            self.model = "llama-3.3-70b-versatile"

    async def analyze_query(self, query: str) -> SearchIntent:
        if not self.client:
            return SearchIntent(
                intent="unknown",
                confidence=0.0,
                filters={}
            )

        prompt = f"""You are an AI assistant for an Algerian Data Analytics Platform called Boussole.
Analyze the following user search query and extract structured intent.

User Query: "{query}"

Output JSON format:
{{
    "intent": "analytics" | "market" | "navigation" | "general_q" | "unknown",
    "topic": "string (e.g. agriculture, energy, housing, startups)",
    "subtopic": "string (e.g. greenhouses, solar, apartments)",
    "location": "string (Wilaya code 01-58 or 'all')",
    "filters": {{ "key": "value" }},
    "confidence": float (0.0-1.0)
}}

Rules:
1. Location: If a wilaya name is mentioned (e.g. Algiers, Oran), map it to its code (Algiers->01, Oran->02).
2. Intent: 
   - 'analytics': asking for data, statistics, numbers, trends.
   - 'market': asking for prices, buying/selling, products.
   - 'navigation': asking to go to a specific page.
3. If query is vague, set confidence lower.

Examples:
- "greenhouses in Algiers" -> {{ "intent": "analytics", "topic": "agriculture", "subtopic": "greenhouses", "location": "01", "confidence": 0.95 }}
- "price of iphone 15" -> {{ "intent": "market", "topic": "electronics", "subtopic": "phones", "filters": {{ "brand": "apple" }}, "confidence": 0.9 }}

Respond ONLY with valid JSON. No markdown, no code blocks, just the JSON object."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=256,
            )
            
            text = response.choices[0].message.content.strip()
            # Clean response text (sometimes it has markdown code blocks)
            if text.startswith("```json"):
                text = text[7:]
            if text.startswith("```"):
                text = text[3:]
            if text.endswith("```"):
                text = text[:-3]
            
            data = json.loads(text.strip())
            return SearchIntent(**data)
        except Exception as e:
            print(f"Error analyzing query with Groq: {e}")
            return SearchIntent(
                intent="unknown",
                confidence=0.0,
                filters={}
            )
