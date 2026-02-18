# ============================================
# Boussole - LLM Module
# ============================================

"""
LLM integration using LangChain with Groq and OpenAI.

This module provides functions for:
- Initializing LLM clients
- Generating responses from queries and context
- Managing LLM configuration
"""

import logging
from typing import List, Optional, Dict, Any
from langchain.schema import HumanMessage, SystemMessage, AIMessage

from app.core.config import settings

logger = logging.getLogger(__name__)


class LLMProvider:
    """
    Enum-like class for LLM providers.
    """
    GROQ = "groq"
    OPENAI = "openai"


class LLMClient:
    """
    Wrapper class for LLM clients.
    """
    
    _instance = None
    _client = None
    _provider = None
    
    def __new__(cls, provider: Optional[str] = None):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._provider = provider or settings.LLM_PROVIDER
            cls._instance._load_client()
        return cls._instance
    
    def _load_client(self):
        """
        Load the LLM client based on provider.
        """
        try:
            if self._provider == LLMProvider.GROQ:
                from langchain_groq import ChatGroq
                self._client = ChatGroq(
                    model=settings.GROQ_MODEL,
                    api_key=settings.GROQ_API_KEY,
                    temperature=0.7,
                )
                logger.info(f"Loaded Groq LLM: {settings.GROQ_MODEL}")
            
            elif self._provider == LLMProvider.OPENAI:
                from langchain_openai import ChatOpenAI
                self._client = ChatOpenAI(
                    model=settings.OPENAI_MODEL,
                    api_key=settings.OPENAI_API_KEY,
                    temperature=0.7,
                )
                logger.info(f"Loaded OpenAI LLM: {settings.OPENAI_MODEL}")
            
            else:
                raise ValueError(f"Unsupported LLM provider: {self._provider}")
        
        except Exception as e:
            logger.error(f"Failed to load LLM client: {e}", exc_info=True)
            raise
    
    def generate_response(
        self,
        query: str,
        context: Optional[str] = None,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None
    ) -> str:
        """
        Generate a response from the LLM.
        
        Args:
            query: User query/question
            context: Optional context information (e.g., retrieved documents)
            system_prompt: Optional system prompt
            temperature: Optional temperature override
        
        Returns:
            Generated response text
        """
        if self._client is None:
            self._load_client()
        
        try:
            # Build messages
            messages = []
            
            # Add system prompt if provided
            if system_prompt:
                messages.append(SystemMessage(content=system_prompt))
            else:
                # Default system prompt
                messages.append(SystemMessage(content="""
                    You are a helpful assistant for Boussole, an Algerian data analytics platform.
                    Provide accurate, informative answers based on the given context.
                    If the context doesn't contain enough information, acknowledge this limitation.
                    Respond in the same language as the user's query.
                    """))
            
            # Add context if provided
            if context:
                messages.append(SystemMessage(content=f"Context: {context}"))
            
            # Add user query
            messages.append(HumanMessage(content=query))
            
            # Generate response
            if temperature is not None:
                response = self._client.invoke(messages, temperature=temperature)
            else:
                response = self._client.invoke(messages)
            
            return response.content
        
        except Exception as e:
            logger.error(f"Failed to generate LLM response: {e}", exc_info=True)
            return "I apologize, but I encountered an error while generating a response. Please try again."


# Global LLM client instance
llm_client = LLMClient()


def generate_rag_response(
    query: str,
    retrieved_docs: List[Dict[str, Any]],
    language: str = "en"
) -> Dict[str, Any]:
    """
    Generate a RAG response using retrieved documents.
    
    Args:
        query: User query/question
        retrieved_docs: List of retrieved document chunks
        language: Response language (en, fr, ar)
    
    Returns:
        Dictionary with response and metadata
    
    Example:
        >>> query = "What is Algeria's GDP?"
        >>> docs = await similarity_search(db, query)
        >>> response = generate_rag_response(query, docs, "en")
        >>> print(response["answer"])
    """
    try:
        # Build context from retrieved documents
        context_parts = []
        sources = []
        
        for i, doc in enumerate(retrieved_docs, 1):
            context_parts.append(f"[Document {i}] {doc['chunk_text']}")
            sources.append({
                "id": doc["id"],
                "document_id": doc["document_id"],
                "title": doc["title"],
                "source": doc["source"],
                "similarity": doc["similarity"],
            })
        
        context = "\n\n".join(context_parts)
        
        # Language-specific system prompt
        system_prompts = {
            "en": "You are a helpful assistant for Boussole, an Algerian data analytics platform. Answer the question based on the provided context.",
            "fr": "Vous êtes un assistant utile pour Boussole, une plateforme algérienne d'analyse de données. Répondez à la question en vous basant sur le contexte fourni.",
            "ar": "أنت مساعد مفيد لبوصلة، منصة تحليل البيانات الجزائرية. أجب على السؤال بناءً على السياق المقدم.",
        }
        
        system_prompt = system_prompts.get(language, system_prompts["en"])
        
        # Generate response
        answer = llm_client.generate_response(
            query=query,
            context=context,
            system_prompt=system_prompt
        )
        
        return {
            "answer": answer,
            "sources": sources,
            "language": language,
            "context_used": len(retrieved_docs),
        }
    
    except Exception as e:
        logger.error(f"Failed to generate RAG response: {e}", exc_info=True)
        return {
            "answer": "I apologize, but I encountered an error while generating a response. Please try again.",
            "sources": [],
            "language": language,
            "error": str(e),
        }


def generate_summary(
    text: str,
    max_length: int = 200,
    language: str = "en"
) -> str:
    """
    Generate a summary of the given text.
    
    Args:
        text: Text to summarize
        max_length: Maximum length of summary (approximate)
        language: Summary language (en, fr, ar)
    
    Returns:
        Generated summary
    
    Example:
        >>> summary = generate_summary("Long document text...", max_length=100)
        >>> print(summary)
    """
    try:
        # Language-specific prompt
        prompts = {
            "en": f"Summarize the following text in about {max_length} characters:\n\n{text}",
            "fr": f"Résumez le texte suivant en environ {max_length} caractères:\n\n{text}",
            "ar": f"لخص النص التالي في حوالي {max_length} حرف:\n\n{text}",
        }
        
        prompt = prompts.get(language, prompts["en"])
        
        summary = llm_client.generate_response(query=prompt)
        return summary
    
    except Exception as e:
        logger.error(f"Failed to generate summary: {e}", exc_info=True)
        return text[:max_length]


def generate_data_insight(
    data: Dict[str, Any],
    language: str = "en"
) -> str:
    """
    Generate an insight from data.
    
    Args:
        data: Data dictionary with statistics
        language: Insight language (en, fr, ar)
    
    Returns:
        Generated insight
    
    Example:
        >>> data = {"sector": "Agriculture", "value": 1234.56, "change": 5.2}
        >>> insight = generate_data_insight(data, "en")
        >>> print(insight)
    """
    try:
        # Build prompt
        data_str = json.dumps(data, indent=2)
        
        prompts = {
            "en": f"Analyze the following data and provide a brief insight:\n\n{data_str}",
            "fr": f"Analysez les données suivantes et fournissez un bref aperçu:\n\n{data_str}",
            "ar": f"حلل البيانات التالية وقدم رؤية موجزة:\n\n{data_str}",
        }
        
        prompt = prompts.get(language, prompts["en"])
        
        insight = llm_client.generate_response(query=prompt)
        return insight
    
    except Exception as e:
        logger.error(f"Failed to generate data insight: {e}", exc_info=True)
        return "Unable to generate insight at this time."
