# ============================================
# Boussole - LLM Adapter (Provider-Agnostic)
# ============================================

"""
Provider-agnostic LLM adapter supporting Groq, OpenAI, Google Gemini,
Azure/Microsoft Foundry, and Anthropic. Can be dynamically configured via the DB or fallbacks to env var.
"""

import json
from abc import ABC, abstractmethod
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import settings
from app.models.ai_config import AIProviderConfig


class BaseLLMAdapter(ABC):
    """Abstract base for LLM providers."""
    
    def __init__(self, api_key: str, model_name: str, api_base_url: Optional[str] = None):
        self.api_key = api_key
        self.model_name = model_name
        self.api_base_url = api_base_url

    @abstractmethod
    async def complete(self, system_prompt: str, user_prompt: str, temperature: float = 0.1, max_tokens: int = 512) -> str:
        """Send a completion request and return the raw text response."""
        ...

    @abstractmethod
    def get_provider_name(self) -> str:
        ...

    def get_model_name(self) -> str:
        return self.model_name


class GroqAdapter(BaseLLMAdapter):
    """Adapter for Groq (Llama, Mixtral, etc.)."""

    def __init__(self, api_key: str, model_name: str, api_base_url: Optional[str] = None):
        super().__init__(api_key, model_name, api_base_url)
        from groq import AsyncGroq
        self.client = AsyncGroq(api_key=self.api_key)

    async def complete(self, system_prompt: str, user_prompt: str, temperature: float = 0.1, max_tokens: int = 512) -> str:
        response = await self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content.strip()

    def get_provider_name(self) -> str:
        return "groq"


class OpenAIAdapter(BaseLLMAdapter):
    """Adapter for OpenAI (GPT-4, GPT-4o, etc.)."""

    def __init__(self, api_key: str, model_name: str, api_base_url: Optional[str] = None):
        super().__init__(api_key, model_name, api_base_url)
        from openai import AsyncOpenAI
        self.client = AsyncOpenAI(api_key=self.api_key)

    async def complete(self, system_prompt: str, user_prompt: str, temperature: float = 0.1, max_tokens: int = 512) -> str:
        response = await self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content.strip()

    def get_provider_name(self) -> str:
        return "openai"


class AzureOpenAIAdapter(BaseLLMAdapter):
    """Adapter for Microsoft Foundry / Azure OpenAI."""

    def __init__(self, api_key: str, model_name: str, api_base_url: Optional[str] = None):
        super().__init__(api_key, model_name, api_base_url)
        from openai import AsyncAzureOpenAI
        
        if not self.api_base_url:
            raise ValueError("api_base_url is required for AzureOpenAI / Microsoft Foundry")
            
        # The 'model_name' here maps to the Azure deployment name
        self.client = AsyncAzureOpenAI(
            api_key=self.api_key,
            api_version="2023-05-15", # Standard default version, should ideally be configurable
            azure_endpoint=self.api_base_url
        )

    async def complete(self, system_prompt: str, user_prompt: str, temperature: float = 0.1, max_tokens: int = 512) -> str:
        response = await self.client.chat.completions.create(
            model=self.model_name, # Azure deployment name
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content.strip()

    def get_provider_name(self) -> str:
        return "azure"


class GeminiAdapter(BaseLLMAdapter):
    """Adapter for Google Gemini."""

    def __init__(self, api_key: str, model_name: str, api_base_url: Optional[str] = None):
        super().__init__(api_key, model_name, api_base_url)
        import google.generativeai as genai
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(
            self.model_name,
            generation_config={"response_mime_type": "application/json"},
        )

    async def complete(self, system_prompt: str, user_prompt: str, temperature: float = 0.1, max_tokens: int = 512) -> str:
        full_prompt = f"{system_prompt}\n\n{user_prompt}"
        response = await self.model.generate_content_async(full_prompt)
        return response.text.strip()

    def get_provider_name(self) -> str:
        return "gemini"


class AnthropicAdapter(BaseLLMAdapter):
    """Adapter for Anthropic Claude."""

    def __init__(self, api_key: str, model_name: str, api_base_url: Optional[str] = None):
        super().__init__(api_key, model_name, api_base_url)
        import anthropic
        self.client = anthropic.AsyncAnthropic(api_key=self.api_key)

    async def complete(self, system_prompt: str, user_prompt: str, temperature: float = 0.1, max_tokens: int = 512) -> str:
        response = await self.client.messages.create(
            model=self.model_name,
            max_tokens=max_tokens,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        )
        return response.content[0].text.strip()

    def get_provider_name(self) -> str:
        return "anthropic"


# ---- Factory ----

_PROVIDERS = {
    "groq": GroqAdapter,
    "openai": OpenAIAdapter,
    "azure": AzureOpenAIAdapter,
    "gemini": GeminiAdapter,
    "anthropic": AnthropicAdapter,
}

async def get_llm_adapter(db: Optional[AsyncSession] = None, provider_override: Optional[str] = None) -> BaseLLMAdapter:
    """
    Factory to retrieve the active LLM Adapter.
    If a DB session is provided, it attempts to load from AIProviderConfig.
    Otherwise, it falls back to environment variables.
    """
    provider = provider_override
    api_key = None
    model_name = None
    api_base_url = None

    # Step 1: Check Database Configuration
    if db:
        if provider:
            # Look for specific provider
            stmt = select(AIProviderConfig).where(AIProviderConfig.provider_name == provider)
        else:
            # Look for active provider
            stmt = select(AIProviderConfig).where(AIProviderConfig.is_active == True)
            
        result = await db.execute(stmt)
        config = result.scalar_one_or_none()
        
        if config:
            provider = config.provider_name
            api_key = config.api_key
            model_name = config.model_name
            api_base_url = config.api_base_url


    # Step 2: Fallback to Environment Variables (.env variables remain as the default fallback)
    if not provider:
        provider = settings.LLM_PROVIDER.lower()

    if not api_key:
        if provider == "groq":
            api_key = settings.GROQ_API_KEY
            model_name = model_name or settings.GROQ_MODEL
        elif provider == "openai":
            api_key = settings.OPENAI_API_KEY
            model_name = model_name or settings.OPENAI_MODEL
        elif provider == "gemini":
            api_key = settings.GOOGLE_API_KEY
            model_name = model_name or "gemini-2.0-flash"
        elif provider == "anthropic":
            api_key = getattr(settings, "ANTHROPIC_API_KEY", None)
            model_name = model_name or "claude-sonnet-4-20250514"
        elif provider == "azure":
            # Just an example, maybe they add these to .env later
            api_key = getattr(settings, "AZURE_API_KEY", None)
            model_name = model_name or "gpt-4"
            api_base_url = getattr(settings, "AZURE_ENDPOINT", None)

    # Step 3: Instantiate Adapter
    if not api_key:
        raise ValueError(f"No API key configured for Provider: '{provider}' via Database or Settings.")

    adapter_cls = _PROVIDERS.get(provider.lower())
    if not adapter_cls:
        raise ValueError(f"Unknown LLM provider: '{provider}'. Available: {list(_PROVIDERS.keys())}")
        
    return adapter_cls(api_key=api_key, model_name=model_name, api_base_url=api_base_url)
