from typing import List, Optional
from app.schemas.chat import ChatMessage
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.llm_adapter import get_llm_adapter, BaseLLMAdapter
from app.models.intent import SystemPrompt
from sqlalchemy import select

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
    def __init__(self, db: Optional[AsyncSession] = None):
        self.db = db
        self.adapter: Optional[BaseLLMAdapter] = None

    async def get_completion(self, message: str, history: List[ChatMessage] = None) -> str:
        try:
            if not self.adapter:
                self.adapter = await get_llm_adapter(self.db)

            # Build user prompt with history
            user_prompt = ""
            if history:
                user_prompt += "Previous conversation context:\n"
                for msg in history:
                    user_prompt += f"{msg.role.capitalize()}: {msg.content}\n"
                user_prompt += "\n"
            user_prompt += f"User: {message}"

            # Get active System Prompt from DB if available
            active_prompt = SYSTEM_PROMPT
            if self.db:
                stmt = select(SystemPrompt).where(
                    SystemPrompt.name == "ai_assistant",
                    SystemPrompt.is_active == True
                )
                prompt_match = await self.db.execute(stmt)
                db_prompt = prompt_match.scalar_one_or_none()
                if db_prompt:
                    active_prompt = db_prompt.content

            # Call provider-agnostic API
            response = await self.adapter.complete(
                system_prompt=active_prompt,
                user_prompt=user_prompt,
                temperature=0.7,
                max_tokens=2048,
            )
            
            return response
        except Exception as e:
            print(f"Error in ChatService: {e}")
            return f"I apologize, but I encountered an error processing your request. Please try again. (Error: {str(e)})"
