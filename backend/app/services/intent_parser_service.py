# ============================================
# Boussole - Intent Parser Service
# ============================================

"""
AI-powered intent parser that converts user business queries
into structured BusinessIntent objects. Uses the provider-agnostic
LLM adapter for flexibility across different AI providers.
"""

import json
from typing import Optional
from app.schemas.intent import BusinessIntent, BusinessObjective, GeographicScope, DataCategory
from app.services.llm_adapter import get_llm_adapter, BaseLLMAdapter
from app.models.intent import StaticIntent, SystemPrompt, IntentLog
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import time


# ---- Wilaya Code Mapping (for post-LLM enrichment) ----

WILAYA_NAME_TO_CODE = {
    "adrar": "01", "chlef": "02", "laghouat": "03", "oum el bouaghi": "04",
    "batna": "05", "bejaia": "06", "béjaïa": "06", "biskra": "07",
    "bechar": "08", "béchar": "08", "blida": "09", "bouira": "10",
    "tamanrasset": "11", "tebessa": "12", "tébessa": "12", "tlemcen": "13",
    "tiaret": "14", "tizi ouzou": "15", "algiers": "16", "alger": "16",
    "djelfa": "17", "jijel": "18", "setif": "19", "sétif": "19",
    "saida": "20", "saïda": "20", "skikda": "21", "sidi bel abbes": "22",
    "annaba": "23", "guelma": "24", "constantine": "25", "medea": "26",
    "médéa": "26", "mostaganem": "27", "msila": "28", "m'sila": "28",
    "mascara": "29", "ouargla": "30", "oran": "31", "el bayadh": "32",
    "illizi": "33", "bordj bou arreridj": "34", "boumerdes": "35",
    "boumerdès": "35", "el tarf": "36", "tindouf": "37", "tissemsilt": "38",
    "el oued": "39", "khenchela": "40", "souk ahras": "41",
    "tipaza": "42", "mila": "43", "ain defla": "44", "aïn defla": "44",
    "naama": "45", "naâma": "45", "ain temouchent": "46",
    "ghardaia": "47", "ghardaïa": "47", "relizane": "48",
    "el mghair": "49", "el menia": "50", "ouled djellal": "51",
    "bordj badji mokhtar": "52", "beni abbes": "53", "timimoun": "54",
    "touggourt": "55", "djanet": "56", "in salah": "57", "in guezzam": "58",
}

WILAYA_CODE_TO_NAME = {v: k.title() for k, v in WILAYA_NAME_TO_CODE.items()}


# ---- System Prompt ----

INTENT_SYSTEM_PROMPT = """You are Boussole's AI Intent Parser for an Algerian business analytics platform.

Your job is to analyze a user's business query and extract structured intent data.
Respond ONLY with valid JSON matching this exact schema:

{
    "sector": "string (agriculture, energy, manufacturing, services, tourism, innovation, consulting, housing, education, health, transport, telecom, finance, retail, or general)",
    "subsector": "string or null (e.g. greenhouses, solar_panels, bakeries)",
    "location": "string or null (Wilaya code 01-58)",
    "location_name": "string or null (Wilaya name in English)",
    "geographic_scope": "national | regional | local",
    "objective": "market_analysis | feasibility | competition | investment | trend_tracking | comparison | general",
    "data_categories": ["market_demand", "competition", "finance", "infrastructure", "demographics", "labor", "regulation", "trade"],
    "confidence": 0.0 to 1.0,
    "time_range": "string or null (last_year, 5_years, current)"
}

Rules:
1. Map Algerian wilaya names to codes: Algiers→16, Oran→31, Constantine→25, Setif→19, Batna→05, Annaba→23, Tlemcen→13, Blida→09, Tébessa→12, Biskra→07, Ouargla→30, Béjaïa→06.
2. data_categories MUST contain at least one item. Choose categories that are most relevant to the query.
3. If the query mentions prices, costs, or money → include "finance".
4. If the query mentions workers, employment, jobs → include "labor".
5. If the query mentions population, people, youth → include "demographics".
6. If the query mentions competitors, market share → include "competition".
7. If the query is vague, set confidence lower and objective to "general".
8. Respond ONLY with valid JSON. No markdown, no code blocks, no explanation."""


class IntentParserService:
    """
    Parses natural language business queries into structured BusinessIntent objects.
    Uses the provider-agnostic LLM adapter.
    """

    def __init__(self, provider: Optional[str] = None, db: Optional[AsyncSession] = None):
        self.provider = provider
        self.db = db
        self.adapter: Optional[BaseLLMAdapter] = None

    async def parse(self, query: str, context: Optional[str] = None) -> BusinessIntent:
        """
        Parse a business query into a structured BusinessIntent.

        Args:
            query: The user's natural language query
            context: Optional context from previous interactions

        Returns:
            A validated BusinessIntent object
        """
        # 1. Check for Static Intent (Cache Bypass)
        if self.db:
            normalized_query = query.strip().lower()
            stmt = select(StaticIntent).where(
                StaticIntent.keyword == normalized_query,
                StaticIntent.is_active == True
            )
            static_match = await self.db.execute(stmt)
            static_intent = static_match.scalar_one_or_none()
            if static_intent:
                static_data = static_intent.mapped_intent
                static_data["raw_query"] = query
                return BusinessIntent(**static_data)

        # 2. Get active System Prompt from DB if available
        active_prompt = INTENT_SYSTEM_PROMPT
        if self.db:
            stmt = select(SystemPrompt).where(
                SystemPrompt.name == "intent_parser",
                SystemPrompt.is_active == True
            )
            prompt_match = await self.db.execute(stmt)
            db_prompt = prompt_match.scalar_one_or_none()
            if db_prompt:
                active_prompt = db_prompt.content

        user_prompt = f'User Query: "{query}"'
        if context:
            user_prompt += f"\nContext: {context}"

        # Ensure adapter is dynamically initialized with DB config
        if not self.adapter:
            self.adapter = await get_llm_adapter(self.db, self.provider)

        start_time = time.time()
        raw_response = ""
        try:
            raw_response = await self.adapter.complete(
                system_prompt=active_prompt,
                user_prompt=user_prompt,
                temperature=0.1,
                max_tokens=512,
            )

            # Clean response (LLMs sometimes wrap in markdown)
            text = raw_response.strip()
            if text.startswith("```json"):
                text = text[7:]
            if text.startswith("```"):
                text = text[3:]
            if text.endswith("```"):
                text = text[:-3]
            text = text.strip()

            data = json.loads(text)

            # Enrich: validate and fix location codes
            data = self._enrich_location(data)

            # Ensure raw_query is set
            data["raw_query"] = query

            # Validate data_categories
            if "data_categories" in data:
                valid_cats = [c.value for c in DataCategory]
                data["data_categories"] = [c for c in data["data_categories"] if c in valid_cats]
                if not data["data_categories"]:
                    data["data_categories"] = ["market_demand"]

            # Validate objective
            if "objective" in data:
                valid_objs = [o.value for o in BusinessObjective]
                if data["objective"] not in valid_objs:
                    data["objective"] = "general"

            # Validate geographic_scope
            if "geographic_scope" in data:
                valid_scopes = [s.value for s in GeographicScope]
                if data["geographic_scope"] not in valid_scopes:
                    data["geographic_scope"] = "national" if not data.get("location") else "local"

            latency = (time.time() - start_time) * 1000.0
            confidence = data.get("confidence", 0.0)

            # Log to DB
            if self.db:
                log_entry = IntentLog(
                    query=query,
                    provider=self.adapter.get_provider_name(),
                    model_name=self.adapter.get_model_name(),
                    latency_ms=latency,
                    confidence=confidence,
                    parsed_intent=data
                )
                self.db.add(log_entry)
                await self.db.commit()

            return BusinessIntent(**data)

        except json.JSONDecodeError as e:
            print(f"[IntentParser] JSON parse error: {e}, raw: {raw_response[:200]}")
            fallback = self._fallback_intent(query)
            if self.db:
                latency = (time.time() - start_time) * 1000.0
                log_entry = IntentLog(
                    query=query,
                    provider=self.adapter.get_provider_name(),
                    model_name=self.adapter.get_model_name(),
                    latency_ms=latency,
                    confidence=0.1,
                    parsed_intent=fallback.model_dump(),
                    feedback_notes="Parse Error"
                )
                self.db.add(log_entry)
                await self.db.commit()
            return fallback

        except Exception as e:
            print(f"[IntentParser] Error parsing intent: {e}")
            return self._fallback_intent(query)

    def _enrich_location(self, data: dict) -> dict:
        """Post-LLM validation: ensure location codes are correct."""
        location = data.get("location")
        location_name = data.get("location_name", "")

        # If location_name is given but code is wrong/missing, fix it
        if location_name and not location:
            normalized = location_name.lower().strip()
            code = WILAYA_NAME_TO_CODE.get(normalized)
            if code:
                data["location"] = code
                data["geographic_scope"] = "local"

        # If location code is given, ensure location_name is set
        if location and not location_name:
            data["location_name"] = WILAYA_CODE_TO_NAME.get(location, f"Wilaya {location}")

        # If location is set, ensure scope is local
        if data.get("location"):
            data["geographic_scope"] = "local"

        return data

    def _fallback_intent(self, query: str) -> BusinessIntent:
        """Return a safe fallback intent when parsing fails."""
        return BusinessIntent(
            sector="general",
            subsector=None,
            location=None,
            location_name=None,
            geographic_scope=GeographicScope.NATIONAL,
            objective=BusinessObjective.GENERAL,
            data_categories=[DataCategory.MARKET_DEMAND],
            confidence=0.1,
            raw_query=query,
            time_range=None,
        )

    def get_provider_name(self) -> str:
        return self.adapter.get_provider_name() if self.adapter else "unknown"

    def get_model_name(self) -> str:
        return self.adapter.get_model_name() if self.adapter else "unknown"
