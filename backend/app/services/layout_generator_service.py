import json
import random
from typing import Optional
from groq import Groq
from app.core.config import settings
from app.schemas.dynamic_layout import DynamicLayoutResponse, WidgetConfig

# Wilaya lookup
WILAYAS = {
    "01": "Algiers", "02": "Oran", "03": "Constantine", "04": "Setif",
    "05": "Batna", "06": "Annaba", "07": "Skikda", "08": "Tlemcen",
    "09": "Tizi Ouzou", "10": "Béjaïa", "11": "Biskra", "12": "Boumerdès",
    "13": "Tebessa", "14": "Ouargla", "15": "Blida", "16": "Djelfa",
    "17": "Bordj Bou Arréridj", "18": "Bouira", "19": "Médéa",
    "20": "M'Sila", "21": "Mostaganem", "22": "Mascara", "23": "Chlef",
    "24": "Saïda", "25": "Sidi Bel Abbès", "26": "Guelma", "27": "Jijel",
    "28": "Relizane", "29": "Tiaret", "30": "Aïn Defla",
    "31": "Naâma", "32": "Aïn Témouchent", "33": "Ghardaïa",
    "34": "El Oued", "35": "Mila", "36": "Souk Ahras",
    "37": "Tipaza", "38": "Tissemsilt", "39": "El Bayadh",
    "40": "Khenchela", "41": "Tamanrasset", "42": "Illizi",
    "43": "Laghouat", "44": "Adrar", "45": "Béchar",
    "46": "El Tarf", "47": "Tindouf", "48": "El M'Ghair",
    "49": "El Menia", "50": "Touggourt", "51": "Djanet",
    "52": "In Salah", "53": "In Guezzam", "54": "Bordj Badji Mokhtar",
    "55": "Béni Abbès", "56": "Timimoun", "57": "Ouled Djellal", "58": "Ain Salah"
}

SECTOR_ICONS = {
    "agriculture": "🌾", "energy": "⚡", "manufacturing": "🏭",
    "services": "💼", "tourism": "🏖️", "innovation": "🚀",
    "consulting": "📋", "housing": "🏠", "education": "📚",
    "health": "🏥", "technology": "💻", "electronics": "📱",
    "construction": "🏗️", "transport": "🚚", "commerce": "🛒",
}

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
    "line_chart": {{
        "title": "chart title (trend over years)",
        "data": [{{"year": 2018, "value": 100}}, {{"year": 2019, "value": 120}}, {{"year": 2020, "value": 115}}, {{"year": 2021, "value": 140}}, {{"year": 2022, "value": 160}}, {{"year": 2023, "value": 185}}, {{"year": 2024, "value": 210}}]
    }},
    "insights": [
        "Key insight about the data 1",
        "Key insight about the data 2",
        "Key insight about the data 3"
    ]
}}

Rules:
- Map wilaya names to codes: Algiers->01, Oran->02, Constantine->03, Setif->04, Batna->05, Annaba->06, Biskra->11, Ouargla->14, Blida->15
- Generate REALISTIC data based on Algeria's actual economy
- KPI values should be plausible numbers with proper units (DZD, tonnes, hectares, etc.)
- Bar chart should have 4-6 categories relevant to the subtopic
- Line chart should show a realistic trend over 7 years
- Insights should be specific and data-driven
"""


class LayoutGeneratorService:
    def __init__(self):
        api_key = settings.GROQ_API_KEY
        if not api_key:
            raise ValueError("GROQ_API_KEY not found")
        self.client = Groq(api_key=api_key)
        self.model = "llama-3.3-70b-versatile"

    async def generate_layout(self, query: str) -> DynamicLayoutResponse:
        try:
            prompt = ANALYSIS_PROMPT.format(query=query)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=1500,
            )
            
            text = response.choices[0].message.content.strip()
            if text.startswith("```json"):
                text = text[7:]
            if text.startswith("```"):
                text = text[3:]
            if text.endswith("```"):
                text = text[:-3]
            
            ai_data = json.loads(text.strip())
            
            # Build widgets from AI response
            widgets = []
            
            # 1. Hero Banner
            widgets.append(WidgetConfig(
                type="hero",
                title=ai_data.get("title", query),
                subtitle=ai_data.get("subtitle", "AI-generated data analysis"),
            ))
            
            # 2. KPI Grid
            kpis = ai_data.get("kpis", [])
            if kpis:
                widgets.append(WidgetConfig(
                    type="kpi_grid",
                    title="Key Metrics",
                    data=kpis,
                ))
            
            # 3. Bar Chart
            bar_data = ai_data.get("bar_chart")
            if bar_data:
                widgets.append(WidgetConfig(
                    type="bar_chart",
                    title=bar_data.get("title", "Distribution"),
                    data=bar_data.get("data", []),
                ))
            
            # 4. Line Chart
            line_data = ai_data.get("line_chart")
            if line_data:
                widgets.append(WidgetConfig(
                    type="line_chart",
                    title=line_data.get("title", "Trend Over Time"),
                    data=line_data.get("data", []),
                ))
            
            # 5. Insights
            insights = ai_data.get("insights", [])
            if insights:
                widgets.append(WidgetConfig(
                    type="insight_card",
                    title="AI Insights",
                    data=insights,
                ))
            
            location_code = ai_data.get("location")
            location_name = WILAYAS.get(str(location_code), None) if location_code else None
            
            return DynamicLayoutResponse(
                query=query,
                title=ai_data.get("title", query),
                subtitle=ai_data.get("subtitle", ""),
                icon=ai_data.get("icon", "📊"),
                topic=ai_data.get("topic"),
                subtopic=ai_data.get("subtopic"),
                location=location_code,
                location_name=location_name,
                widgets=widgets,
            )
            
        except Exception as e:
            print(f"Error generating layout: {e}")
            # Fallback layout
            return DynamicLayoutResponse(
                query=query,
                title=f"Results for: {query}",
                subtitle="Could not generate AI layout, showing default view",
                icon="📊",
                widgets=[
                    WidgetConfig(
                        type="hero",
                        title=f"Results for: {query}",
                        subtitle="Default data view",
                    ),
                    WidgetConfig(
                        type="insight_card",
                        title="Notice",
                        data=[f"AI layout generation failed: {str(e)}. Showing default view."],
                    ),
                ],
            )
