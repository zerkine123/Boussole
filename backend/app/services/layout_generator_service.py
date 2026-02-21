"""
Layout Generator Service
Generates dynamic dashboard layouts using LLM (lean prompt)
then enriches with real demand / geo data from backend services.
"""
import asyncio
import json
import logging
# from groq import Groq (Removed, using adapter)
from app.schemas.dynamic_layout import DynamicLayoutResponse, WidgetConfig
from app.core.config import settings
from app.services.demand_intelligence_service import DemandIntelligenceService
from app.models.intent import IntentLog
import time

logger = logging.getLogger(__name__)

# DEBUG
DEBUG_FILE = "debug_layout.log"
def debug_log(msg):
    try:
        with open(DEBUG_FILE, "a", encoding="utf-8") as f:
            import datetime
            ts = datetime.datetime.now().isoformat()
            f.write(f"[{ts}] {msg}\n")
    except Exception:
        pass

# Wilaya lookup
# Wilaya lookup (1-58)
WILAYAS = {
    "01": "Adrar", "02": "Chlef", "03": "Laghouat", "04": "Oum El Bouaghi",
    "05": "Batna", "06": "Béjaïa", "07": "Biskra", "08": "Béchar",
    "09": "Blida", "10": "Bouira", "11": "Tamanrasset", "12": "Tébessa",
    "13": "Tlemcen", "14": "Tiaret", "15": "Tizi Ouzou", "16": "Algiers",
    "17": "Djelfa", "18": "Jijel", "19": "Sétif", "20": "Saïda",
    "21": "Skikda", "22": "Sidi Bel Abbès", "23": "Annaba", "24": "Guelma",
    "25": "Constantine", "26": "Médéa", "27": "Mostaganem", "28": "M'Sila",
    "29": "Mascara", "30": "Ouargla", "31": "Oran", "32": "El Bayadh",
    "33": "Illizi", "34": "Bordj Bou Arréridj", "35": "Boumerdès", "36": "El Tarf",
    "37": "Tindouf", "38": "Tissemsilt", "39": "El Oued", "40": "Khenchela",
    "41": "Souk Ahras", "42": "Tipaza", "43": "Mila", "44": "Aïn Defla",
    "45": "Naâma", "46": "Aïn Témouchent", "47": "Ghardaïa", "48": "Relizane",
    "49": "Timimoun", "50": "Bordj Badji Mokhtar", "51": "Ouled Djellal",
    "52": "Béni Abbès", "53": "In Salah", "54": "In Guezzam", "55": "Touggourt",
    "56": "Djanet", "57": "El M'Ghair", "58": "El Meniaa"
}

# ── Lean LLM prompt (proven, fast) ──────────────────────────────
ANALYSIS_PROMPT = """You are an AI that analyzes search queries for an Algerian Data Analytics Platform.
Given the user query, extract structured data. Respond ONLY with valid JSON.

User Query: "{query}"

Output format:
{{
    "title": "A descriptive dashboard title (e.g. 'Greenhouses in Algiers')",
    "subtitle": "A brief analytical subtitle (e.g. 'Agricultural infrastructure analysis for Wilaya 01')",
    "topic": "main sector slug (agriculture, energy, manufacturing, services, tourism, innovation, consulting, housing, education, health, technology, construction, transport, commerce)",
    "subtopic": "specific focus area (e.g. greenhouses, solar panels, startups)",
    "location": "Wilaya code 01-58 or null if not specified",
    "icon": "a single relevant emoji",
    "kpis": [
        {{"label": "KPI name", "value": "formatted number with unit", "trend": "up or down or stable", "change": "+X% or -X%"}},
        {{"label": "KPI name", "value": "formatted number with unit", "trend": "up or down or stable", "change": "+X% or -X%"}},
        {{"label": "KPI name", "value": "formatted number with unit", "trend": "up or down or stable", "change": "+X% or -X%"}},
        {{"label": "KPI name", "value": "formatted number with unit", "trend": "up or down or stable", "change": "+X% or -X%"}}
    ],
    "bar_chart": {{
        "title": "chart title",
        "data": [{{"name": "Category A", "value": 1234}}, {{"name": "Category B", "value": 5678}}]
    }},
    "financial_simulator": {{
        "title": "Financial Feasibility Simulator",
        "subtitle": "Interactive ROI and Break-even Analysis"
    }},
    "line_chart": {{
        "title": "chart title (trend over years)",
        "data": [{{"year": 2018, "value": 100}}, {{"year": 2019, "value": 120}}, {{"year": 2020, "value": 115}}, {{"year": 2021, "value": 140}}, {{"year": 2022, "value": 160}}, {{"year": 2023, "value": 185}}, {{"year": 2024, "value": 210}}]
    }},
    "demand_analysis_config": {{
        "gauge_title": "Custom title for demand score (e.g. 'Investment Rating for Solar')",
        "radar_title": "Custom title for radar (e.g. 'Feasibility Analysis')",
        "table_title": "Custom title for opportunities (e.g. 'Top 5 Sectors in Algiers')",
        "pie_title": "Custom title for distribution (e.g. 'Market Share Breakdown')"
    }},
    "insights": [
        "Key insight about the data 1",
        "Key insight about the data 2",
        "Key insight about the data 3"
    ]
}}

Rules:
- Map wilaya names to codes (Cheat Sheet):
  - Adrar->01, Algiers->16, Oran->31, Constantine->25, Setif->19, Batna->05
  - Annaba->23, Ouargla->30, Blida->09, Tlemcen->13, Bejaia->06, Tizi Ouzou->15
- Generate REALISTIC data based on Algeria's actual economy
- KPI values should be plausible numbers with proper units (DZD, tonnes, hectares, etc.)
- Bar chart should have 4-6 categories relevant to the subtopic
- Line chart should show a realistic trend over 7 years
- Insights should be specific and data-driven
- demand_analysis_config titles should be highly relevant to the specific topic and location
"""


from app.services.competitor_service import CompetitorMappingService
from app.services.geo_intelligence_service import GeoIntelligenceService
from app.services.geo_cache_service import GeoCacheService
from app.db.session import redis_client
from app.models.wilaya import Wilaya
from sqlalchemy import select
from app.services.llm_adapter import get_llm_adapter


class LayoutGeneratorService:
    def __init__(self, db):
        self.db = db
        self.adapter = None
        
        # Initialize Geo Services
        # We assume redis_client is already initialized by main.py startup event
        self.geo_cache = GeoCacheService(redis_client)
        self.geo_service = GeoIntelligenceService(self.geo_cache)
        
        # Initialize Domain Services
        self.demand_service = DemandIntelligenceService(db=db, geo_service=self.geo_service)
        self.competitor_service = CompetitorMappingService(db=db, geo_service=self.geo_service)

    async def _enrich_with_demand(self, widgets: list, topic: str | None, location: str | None, config: dict = None) -> None:
        """Inject demand gauge, radar, pie, table, and competitor map widgets."""
        try:
            if not location:
                return

            wilaya = WILAYAS.get(location)
            if not wilaya:
                logger.warning(f"Could not map location code {location} to Wilaya name")
                return

            # Parallel fetching would be better, but sequential for safety first
            # 1. Demand Score → Gauge Widget
            score_result = await self.demand_service.compute_demand_score(topic, location)
            
            widgets.append(WidgetConfig(
                type="gauge",
                title=f"Investment Rating for {topic.title()} in {wilaya}",
                data={
                    "score": score_result.score,
                    "label": score_result.label,
                    "breakdown": [
                        {"name": s.name, "value": s.score} for s in score_result.signals
                    ]
                }
            ))

            # 2. Demand Signals → Radar Widget
            widgets.append(WidgetConfig(
                type="radar",
                title=f"Feasibility Analysis for {topic.title()}",
                data=[
                    {"subject": s.name, "value": s.score} for s in score_result.signals
                ]
            ))

            # 3. Opportunities → Table widget
            opportunities = await self.demand_service.get_sector_opportunities(location, limit=5)
            if opportunities:
                widgets.append(WidgetConfig(
                    type="table",
                    title=f"Top Sector Opportunities in {wilaya}",
                    data=[
                        {
                            "Rank": f"#{o.rank}",
                            "Sector": o.sector_name,
                            "Score": o.score,
                            "Top Signal": o.key_signals[0] if o.key_signals else "N/A"
                        } for o in opportunities
                    ]
                ))

            # 4. Market Distribution → Pie Chart
            # Mock distribution based on sector profile for now
            widgets.append(WidgetConfig(
                type="pie_chart",
                title="Sector Demand Distribution",
                data=[
                    {"name": "Residential", "value": 45},
                    {"name": "Commercial", "value": 30},
                    {"name": "Industrial", "value": 15},
                    {"name": "Govt/Public", "value": 10},
                ]
            ))

            # 5. Competitor Map → CompetitorMap Widget
            # Fetch real competitor data using the new service
            # We need lat/lon of the Wilaya first. GeoIntelligenceService can help if we had a geocoder,
            # but for now we rely on the implementation in DemandService or hardcoded center.
            # Wilaya model has lat/lon. We can query it via DB or just let CompetitorService handle it?
            # CompetitorMappingService expects lat/lon.
            # Let's look up the Wilaya object from DB to get lat/lon.
            # Since we don't have easy access to Wilaya model here (it's in DemandService), 
            # we'll assume DemandService or CompetitorService can look it up.
            # Actually, CompetitorService.get_competitors takes lat/lon.
            # We need to resolve Wilaya Code -> Lat/Lon.
            
            # Quick fix: We can add a helper in CompetitorService "get_competitors_by_wilaya" 
            # or just look it up here using the DB session.
            # Since self.competitor_service has DB, let's add `get_competitors_for_wilaya` to it?
            # Or just query DB here.
            
            # I will query DB here for simplicity if I import Wilaya and select.
            
            w_stmt = select(Wilaya).where(Wilaya.code == location)
            w_res = await self.competitor_service.db.execute(w_stmt)
            w_obj = w_res.scalar_one_or_none()
            
            if w_obj and w_obj.latitude and w_obj.longitude:
                comp_data = await self.competitor_service.get_competitors(
                    w_obj.latitude, w_obj.longitude, topic
                )
                
                widgets.append(WidgetConfig(
                    type="competitor_map",
                    title=f"Competitor Map: {topic.title()} in {wilaya}",
                    data={
                        "center": {"lat": w_obj.latitude, "lon": w_obj.longitude},
                        "competitors": comp_data["competitors"],
                        "saturation_index": comp_data["saturation_index"],
                        "label": comp_data["saturation_label"]
                    }
                ))

        except Exception as e:
            logger.error(f"Demand enrichment failed: {e}")
            import traceback
            tb = traceback.format_exc()
            widgets.append(WidgetConfig(
                type="insight_card",
                title="Demand Error (Debug)",
                data=[str(e)] + [l.strip() for l in tb.split('\n') if l.strip()][:3]
            ))

    def _extract_intent_fallback(self, query: str) -> tuple[str | None, str | None]:
        """Simple keyword matching fallback if AI fails."""
        query_lower = query.lower()
        
        # 1. Detect location (Wilaya name or code)
        location = None
        for code, name in WILAYAS.items():
            if code in query_lower or name.lower() in query_lower:
                location = code
                break
        
        # 2. Detect sector
        # Basic list of known sectors
        known_sectors = [
            "agriculture", "energy", "manufacturing", "services", "tourism", 
            "innovation", "consulting", "health", "education", "transport", 
            "commerce", "technology", "construction"
        ]
        topic = "services" # Default
        for sector in known_sectors:
            if sector in query_lower:
                topic = sector
                break
                
        return topic, location

    async def generate_layout(self, query: str) -> DynamicLayoutResponse:
        debug_log(f"Starting generate_layout for: {query}")
        ai_data = {}
        error_msg = None
        
        # 1. Try AI Generation
        try:
            if not self.adapter:
                self.adapter = await get_llm_adapter(self.db)
                
            debug_log("Calling AI (Provider Agnostic)...")
            
            # Prepare prompts
            # ANALYSIS_PROMPT contains "{query}" placeholder, but we should separate system/user for better adapter support
            # We will treat ANALYSIS_PROMPT as system prompt (removing the format argument for now if possible, or just formatting it)
            # Actually, the existing prompt has "User Query: {query}" embedded. 
            # We will format it and pass as User Prompt, with a generic System Prompt.
            
            system_instruction = "You are an AI that analyzes search queries for an Algerian Data Analytics Platform. Respond ONLY with valid JSON."
            formatted_prompt = ANALYSIS_PROMPT.format(query=query)
            
            start_time = time.time()
            response = await asyncio.wait_for(
                self.adapter.complete(
                    system_prompt=system_instruction,
                    user_prompt=formatted_prompt,
                    temperature=0.3,
                    max_tokens=1500
                ),
                timeout=25.0,
            )
            latency_ms = (time.time() - start_time) * 1000.0
            
            text = response.strip()
            if text.startswith("```json"): text = text[7:]
            if text.startswith("```"): text = text[3:]
            if text.endswith("```"): text = text[:-3]
            ai_data = json.loads(text.strip())
            debug_log("AI generation successful")
            
            # Log the search intent to the Audit logs
            if self.db:
                log_entry = IntentLog(
                    query=query,
                    provider=self.adapter.get_provider_name() if self.adapter else "unknown",
                    model_name=self.adapter.get_model_name() if self.adapter else "unknown",
                    latency_ms=latency_ms,
                    confidence=0.85, # Layout AI doesn't yield confidence, so assume high on success
                    parsed_intent=ai_data
                )
                self.db.add(log_entry)
                await self.db.commit()
                
        except Exception as e:
            logger.error(f"AI generation failed: {e}")
            debug_log(f"AI generation failed: {e}")
            error_msg = str(e)
            # Continue to fallback...

        # 2. Determine Scope (AI or Fallback)
        if ai_data:
            topic = ai_data.get("topic")
            location_code = ai_data.get("location")
            subtopic = ai_data.get("subtopic")
            title = ai_data.get("title", query)
            subtitle = ai_data.get("subtitle", "AI-generated data analysis")
            demand_config = ai_data.get("demand_analysis_config")
        else:
            # Fallback extraction
            topic, location_code = self._extract_intent_fallback(query)
            subtopic = topic
            location_name = WILAYAS.get(str(location_code), "") if location_code else ""
            title = f"Analysis: {topic.title()}" + (f" in {location_name}" if location_name else "")
            subtitle = "Automated market analysis (AI unavailable)"
            demand_config = None

        # 3. Build Widgets
        widgets = []

        # Hero (Always present)
        widgets.append(WidgetConfig(
            type="hero",
            title=title,
            subtitle=subtitle,
        ))

        # Core AI Widgets (only if AI succeeded)
        if ai_data:
            kpis = ai_data.get("kpis", [])
            if kpis:
                widgets.append(WidgetConfig(type="kpi_grid", title="Key Metrics", data=kpis))
            
            bar_data = ai_data.get("bar_chart")
            if bar_data:
                widgets.append(WidgetConfig(type="bar_chart", title=bar_data.get("title", "Distribution"), data=bar_data.get("data", [])))
            
            line_data = ai_data.get("line_chart")
            if line_data:
                widgets.append(WidgetConfig(type="line_chart", title=line_data.get("title", "Trend"), data=line_data.get("data", [])))

        # 4. Enrich will real backend data (Demand/Geo) - ALWAYS RUN
        # This ensures we get value even if AI fails
        try:
            debug_log("Starting enrichment...")
            # Add strict timeout to backend enrichment to prevent hanging
            await asyncio.wait_for(
                self._enrich_with_demand(widgets, topic, location_code, config=demand_config),
                timeout=12.0
            )
        except asyncio.TimeoutError:
            logger.error("Demand enrichment timed out (12s limit)")
            widgets.append(WidgetConfig(
                type="insight_card",
                title="System Alert",
                data=["Real-time data fetch timed out. Showing AI estimates only."]
            ))
        except Exception as e:
            import traceback
            tb = traceback.format_exc()
            logger.error(f"Critical error in demand enrichment: {tb}")
            # Inject error widget for debugging
            widgets.append(WidgetConfig(
                type="insight_card",
                title="System Error (Debug)",
                data=[f"Error: {str(e)}"] + [l.strip() for l in tb.split('\n') if l.strip()][:5]
            ))

        # Insights (AI or Default)
        insights = ai_data.get("insights", [])
        if not insights and error_msg:
            insights = ["AI analysis temporarily unavailable (Quota/Error) - showing real-time market data only."]
            
        # Ensure Financial Simulator is present (even if AI failed)
        # Check if already added by AI (it might not be if AI failed)
        has_simulator = any(w.type == "financial_simulator" for w in widgets)
        if not has_simulator:
            widgets.append(WidgetConfig(
                type="financial_simulator",
                title="Financial Feasibility Simulator",
                subtitle="Estimate ROI and Break-even point (Manual Mode)"
            ))

        if insights:
            widgets.append(WidgetConfig(
                type="insight_card",
                title="Insights",
                data=insights,
            ))

        location_name = WILAYAS.get(str(location_code), None) if location_code else None

        result = DynamicLayoutResponse(
            query=query,
            title=title,
            subtitle=subtitle,
            icon=ai_data.get("icon", "📊"),
            topic=topic,
            subtopic=subtopic,
            location=location_code,
            location_name=location_name,
            widgets=widgets,
        )
        debug_log("Finished generate_layout")
        return result
