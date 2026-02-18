// ==============================================
// Universal Search Router
// ==============================================
// Keyword-based intent classification for the
// dashboard search box. Routes queries to the
// appropriate page based on detected intent.

export type SearchIntent = "market" | "data" | "sector" | "ai" | "fallback";

interface ClassifiedSearch {
    intent: SearchIntent;
    query: string;
    matchedSector?: string;
    location?: string; // Wilaya code
}

// Keyword dictionaries for each intent
const MARKET_KEYWORDS = [
    // English
    "price", "buy", "sell", "shop", "store", "cheap", "expensive", "occasion", "used",
    "ouedkniss", "marketplace", "product", "phone", "laptop", "car", "voiture",
    "samsung", "iphone", "xiaomi", "oppo", "realme", "huawei",
    // French
    "prix", "acheter", "vendre", "magasin", "boutique", "marché", "téléphone",
    "ordinateur", "portable", "immobilier", "appartement", "villa", "terrain",
    "moto", "camion", "electroménager",
    // Arabic
    "سعر", "شراء", "بيع", "هاتف", "سيارة", "شقة", "أرض", "محل",
];

const DATA_KEYWORDS = [
    // English
    "gdp", "population", "employment", "unemployment", "investment", "production",
    "statistics", "stat", "data", "trend", "growth", "rate", "export", "import",
    "trade", "inflation", "revenue", "budget", "forecast", "comparison", "compare",
    "learning bank", "greenhouses",
    // French
    "pib", "chômage", "emploi", "investissement", "statistiques", "données",
    "tendance", "croissance", "taux", "exportation", "importation", "commerce",
    "inflation", "revenu", "prévision", "serre",
    // Arabic
    "ناتج", "سكان", "بطالة", "استثمار", "إنتاج", "إحصائيات", "بيانات",
    "نمو", "تجارة", "تضخم", "دفيئة",
];

const SECTOR_MAP: Record<string, string[]> = {
    agriculture: [
        "agriculture", "farming", "crop", "wheat", "cereal", "date", "olive", "greenhouse",
        "agricole", "récolte", "blé", "céréale", "serre",
        "زراعة", "قمح", "محاصيل", "بيوت بلاستيكية",
    ],
    energy: [
        "energy", "oil", "gas", "solar", "wind", "renewable", "petroleum", "fuel",
        "énergie", "pétrole", "gaz", "solaire", "éolien", "carburant",
        "طاقة", "نفط", "غاز", "شمسية",
    ],
    tourism: [
        "tourism", "travel", "hotel", "sahara", "heritage", "cultural",
        "tourisme", "voyage", "hôtel", "patrimoine",
        "سياحة", "سفر", "فندق", "صحراء",
    ],
    manufacturing: [
        "manufacturing", "industry", "factory", "industrial", "production",
        "industrie", "usine", "industriel", "fabrication",
        "صناعة", "مصنع",
    ],
    services: [
        "services", "finance", "banking", "telecom", "it", "digital", "tech", "learning bank",
        "services", "banque", "télécommunication", "numérique",
        "خدمات", "بنك", "اتصالات",
    ],
    innovation: [
        "startup", "incubator", "tech", "innovation", "ai",
        "startup", "incubateur", "technologie", "innovation", "ia",
        "شركة ناشئة", "حاضنة", "تكنولوجيا", "ابتكار", "ذكاء اصطناعي",
    ]
};

const AI_QUESTION_STARTERS = [
    "what", "why", "how", "who", "when", "where", "explain", "tell me",
    "compare", "forecast", "predict", "analyze", "analyse",
    "quoi", "pourquoi", "comment", "qui", "quand", "expliquer",
    "ما", "لماذا", "كيف", "من", "متى", "أين", "اشرح", "قارن",
];

// Mapping of names/keywords to internal Wilaya codes
// Note: Using internal codes consistent with data/page.tsx (not official ISO codes)
// 01: Algiers, 02: Oran, ..., 12: Boumerdes, 13: Tebessa (New)
const WILAYA_CODE_MAP: Record<string, string> = {
    // 01 Algiers
    "algiers": "01", "alger": "01", "الجزائر": "01",
    // 02 Oran
    "oran": "02", "wahran": "02", "وهران": "02",
    // 03 Constantine
    "constantine": "03", "qasantina": "03", "قسنطينة": "03",
    // 04 Setif
    "setif": "04", "sétif": "04", "سطيف": "04",
    // 05 Batna
    "batna": "05", "باتنة": "05",
    // 06 Annaba
    "annaba": "06", "عنابة": "06",
    // 07 Skikda
    "skikda": "07", "سكيكدة": "07",
    // 08 Tlemcen
    "tlemcen": "08", "تلمسان": "08",
    // 09 Tizi Ouzou
    "tizi ouzou": "09", "tizi": "09", "تيزي وزو": "09",
    // 10 Bejaia
    "bejaia": "10", "béjaïa": "10", "bgayet": "10", "بجاية": "10",
    // 11 Biskra
    "biskra": "11", "بسكرة": "11",
    // 12 Boumerdes
    "boumerdes": "12", "boumerdès": "12", "بومرداس": "12",
    // 13 Tebessa (Added per request)
    "tebessa": "13", "tébessa": "13", "تبسة": "13",
    // 14 Ouargla (Mapped to 30 in some logic, but let's define a code)
    "ouargla": "14", "ورقلة": "14",
    // Generic
    "wilaya": "all", "state": "all", "province": "all", "ولاية": "all"
};

/**
 * Classify a search query into an intent category.
 */
export function classifySearchIntent(query: string): ClassifiedSearch {
    let q = query.toLowerCase().trim();
    let location: string | undefined;

    if (!q) {
        return { intent: "fallback", query };
    }

    // 0. Extract Location (Wilaya)
    // Check if any word in the query matches a known Wilaya
    const words = q.split(/\s+/);
    for (const word of words) {
        // Simple check for single words first
        if (WILAYA_CODE_MAP[word]) {
            location = WILAYA_CODE_MAP[word];
            // Optional: Remove location from query string?
            // q = q.replace(word, "").trim(); 
            // For now, keep it to ensure context is preserved unless it hampers strict text search
            break;
        }
    }
    // Also check for composite names like "Tizi Ouzou"
    if (!location) {
        for (const [name, code] of Object.entries(WILAYA_CODE_MAP)) {
            if (q.includes(name)) {
                location = code;
                break;
            }
        }
    }

    // 1. Check for AI question patterns
    if (q.endsWith("?")) {
        return { intent: "ai", query: q, location };
    }
    for (const starter of AI_QUESTION_STARTERS) {
        if (q.startsWith(starter + " ") || q.startsWith(starter + "'")) {
            return { intent: "ai", query: q, location };
        }
    }

    // 2. Check for Market intent
    for (const keyword of MARKET_KEYWORDS) {
        if (q.includes(keyword)) {
            return { intent: "market", query: q, location };
        }
    }

    // 3. Check for specific "Learning Bank" keyword -> Data/Sector
    if (q.includes("learning bank")) {
        return { intent: "data", query: q, location, matchedSector: "services" };
    }

    // 4. Check for Sector intent
    for (const [sectorId, keywords] of Object.entries(SECTOR_MAP)) {
        for (const keyword of keywords) {
            if (q.includes(keyword)) {
                return { intent: "sector", query: q, matchedSector: sectorId, location };
            }
        }
    }

    // 5. Check for Data intent (fallback for keywords)
    for (const keyword of DATA_KEYWORDS) {
        if (q.includes(keyword)) {
            return { intent: "data", query: q, location };
        }
    }

    // 6. If Location detected but no other intent, default to Data
    if (location) {
        return { intent: "data", query: q, location };
    }

    // 7. Fallback
    return { intent: "fallback", query: q, location };
}

/**
 * Get the URL route for a classified search intent.
 */
export function getSearchRoute(
    classified: ClassifiedSearch,
    locale: string
): string {
    const encodedQuery = encodeURIComponent(classified.query);
    const locationParam = classified.location && classified.location !== "all"
        ? `&location=${classified.location}`
        : "";

    switch (classified.intent) {
        case "market":
            return `/${locale}/dashboard/market?q=${encodedQuery}${locationParam}`;

        case "sector":
            return `/${locale}/data?q=${encodedQuery}&sector=${classified.matchedSector}${locationParam}`;

        case "data":
            return `/${locale}/data?q=${encodedQuery}${locationParam}`;

        case "ai":
            return `/${locale}/data?q=${encodedQuery}${locationParam}`;

        case "fallback":
        default:
            return `/${locale}/data?q=${encodedQuery}${locationParam}`;
    }
}

/**
 * Get display info for an intent (icon + label key).
 */
export function getIntentDisplay(intent: SearchIntent) {
    const map: Record<SearchIntent, { icon: string; labelKey: string; color: string }> = {
        market: { icon: "🛒", labelKey: "intentMarket", color: "bg-orange-500/20 text-orange-300" },
        data: { icon: "📊", labelKey: "intentData", color: "bg-blue-500/20 text-blue-300" },
        sector: { icon: "🏭", labelKey: "intentSector", color: "bg-emerald-500/20 text-emerald-300" },
        ai: { icon: "🤖", labelKey: "intentAI", color: "bg-violet-500/20 text-violet-300" },
        fallback: { icon: "🔍", labelKey: "intentData", color: "bg-blue-500/20 text-blue-300" },
    };
    return map[intent];
}
