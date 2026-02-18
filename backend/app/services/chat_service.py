from groq import Groq
from typing import List
from app.schemas.chat import ChatMessage
from app.core.config import settings

SYSTEM_PROMPT = """You are Boussole AI, the intelligent assistant for the Boussole platform — an Algerian Data Analytics SaaS.

Your role:
- Help users understand Algerian market data, economic trends, and business statistics.
- Answer questions about sectors: Agriculture, Energy, Manufacturing, Services, Tourism, Innovation, Consulting.
- Provide context about Algeria's 58 Wilayas and their economic profiles.
- Help interpret data from the Data Explorer.
- Suggest relevant metrics, reports, or data points users should look at.

Key facts you know:
- Algeria has ~2.4 million registered business entities (~2.1M individuals, ~274K companies).
- There are ~8,000 startups, with ~2,500 officially labeled.
- 192 official incubators exist across the country.
- ~5,000 consulting agencies operate nationally.
- Agriculture saw 12% growth in 2024.
- Major economic centers: Algiers (01), Oran (31), Constantine (25), Sétif (19).

Guidelines:
- Be concise but informative.
- Use data and numbers when possible.
- If you don't know something specific, say so honestly.
- Respond in the same language the user writes in (French, English, or Arabic).
- Format responses with markdown when helpful (bold, lists, etc.).
"""


class ChatService:
    def __init__(self):
        api_key = settings.GROQ_API_KEY
        if not api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")
        
        self.client = Groq(api_key=api_key)
        self.model = "llama-3.3-70b-versatile"

    async def get_completion(self, message: str, history: List[ChatMessage] = None) -> str:
        try:
            # Build messages array
            messages = [{"role": "system", "content": SYSTEM_PROMPT}]
            
            if history:
                for msg in history:
                    messages.append({
                        "role": msg.role,
                        "content": msg.content
                    })
            
            # Add the current message
            messages.append({"role": "user", "content": message})

            # Call Groq API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=2048,
            )
            
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error in ChatService: {e}")
            return f"I apologize, but I encountered an error processing your request. Please try again. (Error: {str(e)})"
