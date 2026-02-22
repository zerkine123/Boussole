import random
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.wilaya import Wilaya
from app.models.sector import Sector
from app.models.metric import Metric

# Constants moved from seed_metrics.py
ALL_WILAYAS = [
    ("01", "Adrar", "Adrar", "أدرار"), ("02", "Chlef", "Chlef", "الشلف"), ("03", "Laghouat", "Laghouat", "الأغواط"),
    ("04", "Oum El Bouaghi", "Oum El Bouaghi", "أم البواقي"), ("05", "Batna", "Batna", "باتنة"), ("06", "Béjaïa", "Béjaïa", "بجاية"),
    ("07", "Biskra", "Biskra", "بسكرة"), ("08", "Béchar", "Béchar", "بشار"), ("09", "Blida", "Blida", "البليدة"),
    ("10", "Bouira", "Bouira", "البويرة"), ("11", "Tamanrasset", "Tamanrasset", "تمنراست"), ("12", "Tébessa", "Tébessa", "تبسة"),
    ("13", "Tlemcen", "Tlemcen", "تلمسان"), ("14", "Tiaret", "Tiaret", "تيارت"), ("15", "Tizi Ouzou", "Tizi Ouzou", "تيزي وزو"),
    ("16", "Algiers", "Alger", "الجزائر"), ("17", "Djelfa", "Djelfa", "الجلفة"), ("18", "Jijel", "Jijel", "جيجل"),
    ("19", "Sétif", "Sétif", "سطيف"), ("20", "Saïda", "Saïda", "سعيدة"), ("21", "Skikda", "Skikda", "سكيكدة"),
    ("22", "Sidi Bel Abbès", "Sidi Bel Abbès", "سيدي بلعباس"), ("23", "Annaba", "Annaba", "عنابة"), ("24", "Guelma", "Guelma", "قالمة"),
    ("25", "Constantine", "Constantine", "قسنطينة"), ("26", "Médéa", "Médéa", "المدية"), ("27", "Mostaganem", "Mostaganem", "مستغانم"),
    ("28", "M'Sila", "M'Sila", "المسيلة"), ("29", "Mascara", "Mascara", "معسكر"), ("30", "Ouargla", "Ouargla", "ورقلة"),
    ("31", "Oran", "Oran", "وهران"), ("32", "El Bayadh", "El Bayadh", "البيض"), ("33", "Illizi", "Illizi", "إليزي"),
    ("34", "Bordj Bou Arréridj", "Bordj Bou Arréridj", "برج بوعريريج"), ("35", "Boumerdès", "Boumerdès", "بومرداس"),
    ("36", "El Tarf", "El Tarf", "الطارف"), ("37", "Tindouf", "Tindouf", "تندوف"), ("38", "Tissemsilt", "Tissemsilt", "تيسمسيلت"),
    ("39", "El Oued", "El Oued", "الوادي"), ("40", "Khenchela", "Khenchela", "خنشلة"), ("41", "Souk Ahras", "Souk Ahras", "سوق أهراس"),
    ("42", "Tipaza", "Tipaza", "تيبازة"), ("43", "Mila", "Mila", "ميلة"), ("44", "Aïn Defla", "Aïn Defla", "عين الدفلى"),
    ("45", "Naâma", "Naâma", "النعامة"), ("46", "Aïn Témouchent", "Aïn Témouchent", "عين تموشنت"), ("47", "Ghardaïa", "Ghardaïa", "غرداية"),
    ("48", "Relizane", "Relizane", "غليزان"), ("49", "Timimoun", "Timimoun", "تيميمون"), ("50", "Bordj Badji Mokhtar", "Bordj Badji Mokhtar", "برج باجي مختار"),
    ("51", "Ouled Djellal", "Ouled Djellal", "أولاد جلال"), ("52", "Béni Abbès", "Béni Abbès", "بني عباس"), ("53", "In Salah", "In Salah", "عين صالح"),
    ("54", "In Guezzam", "In Guezzam", "عين قزام"), ("55", "Touggourt", "Touggourt", "تقرت"), ("56", "Djanet", "Djanet", "جانت"),
    ("57", "El M'Ghair", "El M'Ghair", "المغير"), ("58", "El Meniaa", "El Meniaa", "المنيعة"),
]

ALL_SECTORS = [
    ("agriculture", "Agriculture", "Agriculture", "الزراعة", "leaf", "#22c55e"),
    ("energy", "Energy", "Énergie", "الطاقة", "zap", "#f59e0b"),
    ("manufacturing", "Manufacturing", "Industrie", "الصناعة", "factory", "#6366f1"),
    ("services", "Services", "Services", "الخدمات", "briefcase", "#0ea5e9"),
    ("tourism", "Tourism", "Tourisme", "السياحة", "map-pin", "#ec4899"),
    ("innovation", "Innovation", "Innovation", "الابتكار", "lightbulb", "#8b5cf6"),
    ("consulting", "Consulting", "Conseil", "الاستشارات", "users", "#14b8a6"),
    ("housing", "Housing", "Logement", "السكن", "home", "#f97316"),
    ("education", "Education", "Éducation", "التعليم", "graduation-cap", "#3b82f6"),
    ("health", "Health", "Santé", "الصحة", "heart-pulse", "#ef4444"),
    ("technology", "Technology", "Technologie", "التكنولوجيا", "cpu", "#a855f7"),
    ("construction", "Construction", "Construction", "البناء", "building", "#78716c"),
    ("transport", "Transport", "Transport", "النقل", "truck", "#64748b"),
    ("commerce", "Commerce", "Commerce", "التجارة", "shopping-cart", "#059669"),
]

METRIC_DEFS = {
    "total_companies": {"name_en": "Total Companies", "name_fr": "Total des entreprises", "name_ar": "إجمالي الشركات", "base_range": (80, 12000), "unit": "count", "growth": (0.02, 0.08)},
    "active_jobs": {"name_en": "Active Jobs", "name_fr": "Emplois actifs", "name_ar": "الوظائف النشطة", "base_range": (150, 8000), "unit": "count", "growth": (0.01, 0.06)},
    "total_investment": {"name_en": "Total Investment", "name_fr": "Investissement total", "name_ar": "إجمالي الاستثمار", "base_range": (500, 45000), "unit": "M DZD", "growth": (0.03, 0.12)},
    "active_projects": {"name_en": "Active Projects", "name_fr": "Projets actifs", "name_ar": "المشاريع النشطة", "base_range": (10, 1800), "unit": "count", "growth": (0.02, 0.10)},
    "jobs_created": {"name_en": "Jobs Created", "name_fr": "Emplois créés", "name_ar": "الوظائف المنشأة", "base_range": (30, 4500), "unit": "count", "growth": (0.01, 0.07)},
    "revenue": {"name_en": "Revenue", "name_fr": "Revenu", "name_ar": "الإيرادات", "base_range": (1000, 90000), "unit": "M DZD", "growth": (0.02, 0.09)},
    "exports": {"name_en": "Exports", "name_fr": "Exportations", "name_ar": "الصادرات", "base_range": (50, 25000), "unit": "M DZD", "growth": (0.01, 0.08)},
    "startups": {"name_en": "Startups", "name_fr": "Startups", "name_ar": "الشركات الناشئة", "base_range": (2, 400), "unit": "count", "growth": (0.05, 0.20)},
    "incubators": {"name_en": "Incubators", "name_fr": "Incubateurs", "name_ar": "حاضنات الأعمال", "base_range": (0, 25), "unit": "count", "growth": (0.02, 0.10)},
    "patents": {"name_en": "Patents Filed", "name_fr": "Brevets déposés", "name_ar": "براءات الاختراع", "base_range": (0, 40), "unit": "count", "growth": (0.03, 0.15)},
    "production": {"name_en": "Production Volume", "name_fr": "Volume de production", "name_ar": "حجم الإنتاج", "base_range": (500, 50000), "unit": "tonnes", "growth": (0.01, 0.06)},
    "market_share": {"name_en": "Market Share", "name_fr": "Part de marché", "name_ar": "حصة السوق", "base_range": (1, 22), "unit": "%", "growth": (-0.02, 0.04)},
    "employment_rate": {"name_en": "Employment Rate", "name_fr": "Taux d'emploi", "name_ar": "معدل التوظيف", "base_range": (20, 80), "unit": "%", "growth": (-0.01, 0.03)},
    "growth_rate": {"name_en": "Growth Rate", "name_fr": "Taux de croissance", "name_ar": "معدل النمو", "base_range": (-3, 22), "unit": "%", "growth": (-0.05, 0.05)},
    "population": {"name_en": "Population", "name_fr": "Population", "name_ar": "السكان", "base_range": (80000, 4500000), "unit": "people", "growth": (0.01, 0.025)},
}

WILAYA_WEIGHTS = {"16": 3.5, "31": 2.5, "25": 2.0, "19": 1.8, "09": 1.6, "23": 1.5, "06": 1.4, "05": 1.3, "15": 1.3, "35": 1.2, "42": 1.2}
SECTOR_BOOSTS = {
    "energy": {"exports": 3.0, "total_investment": 2.5, "revenue": 2.0, "production": 2.5},
    "agriculture": {"production": 3.0, "exports": 1.5, "employment_rate": 1.3},
    "innovation": {"startups": 5.0, "incubators": 4.0, "patents": 4.0, "active_projects": 2.0},
    "technology": {"startups": 3.0, "patents": 3.0, "growth_rate": 1.5},
    "manufacturing": {"production": 2.5, "exports": 2.0, "jobs_created": 1.5},
    "commerce": {"revenue": 2.0, "total_companies": 2.0, "market_share": 1.5},
    "construction": {"active_projects": 2.5, "jobs_created": 2.0, "total_investment": 1.8},
    "health": {"employment_rate": 1.3, "active_projects": 1.5},
    "education": {"employment_rate": 1.2},
    "tourism": {"revenue": 1.5, "active_jobs": 1.3},
}

YEARS = [2018, 2019, 2020, 2021, 2022, 2023, 2024]

async def seed_metrics(db: AsyncSession):
    """
    Seeds the database with comprehensive metrics data.
    """
    # ── 1. Ensure Wilayas exist ──────────────
    result = await db.execute(select(Wilaya))
    existing_wilayas = {w.code: w for w in result.scalars().all()}
    for code, n_en, n_fr, n_ar in ALL_WILAYAS:
        if code not in existing_wilayas:
            db.add(Wilaya(code=code, name_en=n_en, name_fr=n_fr, name_ar=n_ar, name_arabic=n_ar))
    await db.commit()
    
    result = await db.execute(select(Wilaya))
    wilayas = result.scalars().all()

    # ── 2. Ensure Sectors exist ──────────────
    result = await db.execute(select(Sector))
    existing_sectors = {s.slug: s for s in result.scalars().all()}
    for slug, n_en, n_fr, n_ar, icon, color in ALL_SECTORS:
        if slug not in existing_sectors:
            db.add(Sector(slug=slug, name_en=n_en, name_fr=n_fr, name_ar=n_ar, icon=icon, color=color))
    await db.commit()
    
    result = await db.execute(select(Sector))
    sectors = result.scalars().all()

    # ── 3. Clear metrics ──────────────
    await db.execute(delete(Metric))
    await db.commit()

    # ── 4. Seed metrics ──────────────
    total_rows = 0
    batch = []
    BATCH_SIZE = 1000
    
    for w in wilayas:
        w_weight = WILAYA_WEIGHTS.get(w.code, 1.0)
        for s in sectors:
            s_boosts = SECTOR_BOOSTS.get(s.slug, {})
            for slug, meta in METRIC_DEFS.items():
                base_lo, base_hi = meta["base_range"]
                g_lo, g_hi = meta["growth"]
                boost = s_boosts.get(slug, 1.0)
                base_val = random.uniform(base_lo, base_hi) * w_weight * boost
                prev_val = None
                for y in YEARS:
                    growth = random.uniform(g_lo, g_hi)
                    if y == 2020: growth -= random.uniform(0.03, 0.08)
                    if y == 2021: growth += random.uniform(0.02, 0.05)
                    val = base_val * (1 + growth)
                    base_val = val
                    if meta["unit"] == "%": val = max(0, min(100, val))
                    else: val = max(0, val)
                    if meta["unit"] in ("count", "people"): val = round(val)
                    else: val = round(val, 1)
                    
                    change = 0
                    trend = "stable"
                    if prev_val and prev_val > 0:
                        change = round(((val - prev_val) / prev_val) * 100, 1)
                        trend = "up" if change > 1 else ("down" if change < -1 else "stable")
                    
                    batch.append(Metric(
                        wilaya_id=w.id,
                        sector_id=s.id,
                        slug=slug,
                        name_en=meta["name_en"],
                        name_fr=meta["name_fr"],
                        name_ar=meta["name_ar"],
                        value=val,
                        unit=meta["unit"],
                        year=y,
                        period=str(y),
                        trend=trend,
                        change_percent=change,
                        is_verified=True,
                        source="Boussole AI Seed"
                    ))
                    total_rows += 1
                    prev_val = val
                    
                    if len(batch) >= BATCH_SIZE:
                        db.add_all(batch)
                        await db.flush()
                        batch = []
    
    if batch:
        db.add_all(batch)
    
    await db.commit()
    return total_rows
