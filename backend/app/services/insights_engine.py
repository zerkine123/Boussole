# ============================================
# Boussole - Insights Engine Service
# ============================================

import json
from groq import Groq
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.core.config import settings
from app.models.insight import Insight
from app.models.sector import Sector
from app.models.indicator import Indicator
from app.services.analytics_service import AnalyticsService


SYSTEM_PROMPT = """You are the AI Insights Engine for the Boussole Data Analytics SaaS.
Your job is to analyze data points representing Algerian market/economic data and generate meaningful insights.

The data points will be provided in JSON format, containing trends, indicators, and sectors.
You must return a raw JSON object with no markdown formatting or extra text.
The JSON must follow this precise format:
{
    "insights": [
        {
            "type": "trend",         // Can be "trend", "anomaly", "summary", or "correlation"
            "title_en": "...",       // Catchy insight title in English
            "title_fr": "...",       // Same title translated to French
            "title_ar": "...",       // Same title translated to Arabic
            "content_en": "...",     // Comprehensive insight description (1-2 sentences) in English
            "content_fr": "...",     // Same description translated to French
            "content_ar": "...",     // Same description translated to Arabic
            "importance_score": 8.5  // Score from 0.0 to 10.0 indicating how impactful this is
        }
    ]
}

Focus on:
- Identifying major growth/decline trends.
- Spotting anomalies or outliers in data.
- Summarizing overall performance over given periods.
Use exact numbers where possible to give context. Make translations natural and professional.
"""

class InsightsEngineService:
    """Service for generating data insights using AI."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.analytics_service = AnalyticsService(db)
        
        api_key = settings.GROQ_API_KEY
        if not api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")
            
        self.client = Groq(api_key=api_key)
        self.model = "llama-3.3-70b-versatile"

    async def generate_insights_for_sector(self, sector_slug: str, period_start: Optional[str] = None, period_end: Optional[str] = None) -> List[Insight]:
        """Fetch trends for a sector, generate insights via LLM, and save them to the DB."""
        
        # 1. Fetch data
        sector_result = await self.db.execute(select(Sector).where(Sector.slug == sector_slug))
        sector = sector_result.scalar_one_or_none()
        
        if not sector:
            return []
            
        trends = await self.analytics_service.get_sector_trends(
            sector_slug=sector_slug, 
            period_start=period_start, 
            period_end=period_end
        )
        
        if not trends:
            return []

        # 2. Build Prompt Payload
        # We sample or summarize data to avoid hitting context limits on massive datasets.
        # For this MVP, we pass the trends directly since they are aggregated.
        prompt_data = {
            "sector": sector.name_en,
            "period_start": period_start,
            "period_end": period_end,
            "trends_data": trends[:50]  # Limit to 50 data points for context budget
        }

        # 3. Call Groq
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": f"Analyze this data and generate 2-3 key insights:\n{json.dumps(prompt_data)}"}
                ],
                temperature=0.3,
                max_tokens=2048,
                response_format={"type": "json_object"}
            )
            
            result_text = response.choices[0].message.content
            parsed = json.loads(result_text)
            insight_dicts = parsed.get("insights", [])
            
        except Exception as e:
            print(f"Error calling Groq for insights: {e}")
            return []

        # 4. Save to Database
        saved_insights = []
        for item in insight_dicts:
            # Match the indicator if possible based on trends data (MVP heuristic: use first indicator from trends or none)
            indicator_id = None
            if trends and trends[0].get("indicator"):
                indicator_id = trends[0]["indicator"]["id"]
                
            insight = Insight(
                sector_id=sector.id,
                indicator_id=indicator_id,
                type=item.get("type", "trend"),
                title_en=item.get("title_en", ""),
                title_fr=item.get("title_fr", ""),
                title_ar=item.get("title_ar", ""),
                content_en=item.get("content_en", ""),
                content_fr=item.get("content_fr", ""),
                content_ar=item.get("content_ar", ""),
                importance_score=item.get("importance_score", 5.0),
                period=period_end or "Latest"
            )
            self.db.add(insight)
            saved_insights.append(insight)
            
        await self.db.commit()
        
        # Refresh to get IDs
        for ins in saved_insights:
            await self.db.refresh(ins)
            
        return saved_insights

    async def get_latest_insights(self, limit: int = 10, sector_id: Optional[int] = None) -> List[Insight]:
        """Fetch the most recent, highly important insights from the DB."""
        query = select(Insight).where(Insight.is_active == True)
        
        if sector_id:
            query = query.where(Insight.sector_id == sector_id)
            
        query = query.order_by(Insight.importance_score.desc(), Insight.created_at.desc()).limit(limit)
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
