"use client";

import { useTranslations } from "next-intl";
import { useState, useEffect, useMemo } from "react";
import {
  Card,
  CardContent,
  CardHeader,
  CardDescription,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useLocale } from "next-intl";
import { useRouter } from "next/navigation";

import {
  Search,
  X,
  Loader2,
} from "lucide-react";
import dynamic from "next/dynamic";
import "leaflet/dist/leaflet.css";
import DashboardLayout from "@/components/DashboardLayout";
import { WidgetRenderer } from "@/components/widgets/WidgetRegistry";
import {
  classifySearchIntent,
  getSearchRoute,
  getIntentDisplay,
} from "@/lib/searchRouter";
import { api } from "@/lib/api";
import { DashboardFilterProvider } from "@/lib/DashboardFilterContext";

const Map = dynamic(() => import("@/components/Map"), {
  ssr: false,
  loading: () => (
    <div className="h-[500px] w-full rounded-xl border border-gray-200/80 bg-white flex items-center justify-center">
      <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
    </div>
  ),
});

// Algeria Wilaya codes and coordinates
const WILAYA_COORDINATES: Record<
  string,
  { lat: number; lng: number; name: string }
> = {
  "01": { lat: 36.753, lng: 3.04197, name: "Algiers" },
  "02": { lat: 35.6911, lng: -0.6417, name: "Oran" },
  "03": { lat: 36.7747, lng: 3.3897, name: "Constantine" },
  "04": { lat: 36.765, lng: 5.081, name: "Setif" },
  "05": { lat: 36.75, lng: 7.6167, name: "Batna" },
  "06": { lat: 36.7583, lng: 5.0581, name: "Annaba" },
  "07": { lat: 36.7667, lng: 6.6142, name: "Skikda" },
  "08": { lat: 36.7569, lng: 5.3819, name: "Tlemcen" },
  "09": { lat: 36.7667, lng: 5.5214, name: "Tizi Ouzou" },
  "10": { lat: 35.9219, lng: 5.5475, name: "Béjaïa" },
  "11": { lat: 36.7183, lng: 3.8047, name: "Biskra" },
  "12": { lat: 36.7683, lng: 5.0417, name: "Boumerdès" },
};

interface AvailableSector {
  id: number;
  slug: string;
  name_en: string;
  name_fr: string;
  name_ar: string;
  icon?: string;
  color?: string;
}

interface AvailableWilaya {
  id: number;
  code: string;
  name_en: string;
  name_fr: string;
  name_ar: string;
  name_arabic: string;
  region?: string;
}

interface OnboardingPreferences {
  user_id: number;
  email: string;
  full_name: string;
  organization?: string;
  preferred_language: string;
  onboarding_completed: boolean;
  sectors_of_interest: number[];
  wilayas_of_interest: number[];
  use_case?: string;
}

interface OnboardingData {
  available_wilayas: AvailableWilaya[];
  available_sectors: AvailableSector[];
  current_preferences?: OnboardingPreferences;
}

export default function DashboardPage() {
  const t = useTranslations("dashboard");
  const locale = useLocale();
  const router = useRouter();

  const [isLoading, setIsLoading] = useState(false);

  // Universal search state
  const [searchQuery, setSearchQuery] = useState("");

  // Live intent classification as the user types
  const detectedIntent = useMemo(
    () => classifySearchIntent(searchQuery),
    [searchQuery]
  );
  const intentDisplay = useMemo(
    () => getIntentDisplay(detectedIntent.intent),
    [detectedIntent.intent]
  );

  const handleSearch = () => {
    if (!searchQuery.trim()) return;
    const route = getSearchRoute(detectedIntent, locale);
    router.push(route);
  };

  const handleSearchKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") handleSearch();
  };

  const clearSearch = () => setSearchQuery("");

  const [preferredSector, setPreferredSector] = useState<AvailableSector | null>(null);
  const [filteredReports, setFilteredReports] = useState<any[]>([]);

  // The AI now returns structured schema definitions
  const [dashboardLayout, setDashboardLayout] = useState<any[]>([]);

  useEffect(() => {
    const fetchOnboardingData = async () => {
      try {
        const token = localStorage.getItem('access_token');
        if (!token) return;

        const data: OnboardingData = await api.getOnboardingData(token);

        // Determine preferred sector
        const prefs = data.current_preferences;
        if (prefs && prefs.sectors_of_interest && prefs.sectors_of_interest.length > 0) {
          const sectorId = prefs.sectors_of_interest[0];
          const sector = data.available_sectors.find(s => s.id === sectorId);
          if (sector) {
            setPreferredSector(sector);
          }
        }

        // Fetch AI-driven dynamic layout
        try {
          const layoutRes = await api.getDashboardLayout(token);
          if (layoutRes && layoutRes.layout && layoutRes.layout.length > 0) {
            setDashboardLayout(layoutRes.layout);
          }
        } catch (layoutError) {
          console.error("Failed to fetch dashboard layout:", layoutError);
        }

      } catch (error: any) {
        if (error.statusCode === 401) {
          // Token expired or invalid
          localStorage.removeItem('access_token');
          router.push(`/${locale}/login`);
        } else {
          console.error("Failed to fetch onboarding data:", error.message || error);
        }
      }
    };

    fetchOnboardingData();
  }, []);

  // Update reports based on preferred sector
  useEffect(() => {
    const allReports = [
      { title: "2024 Startup Ecosystem Report", date: "April 2024", icon: "💡", color: "bg-orange-100 text-orange-600", tag: "business" },
      { title: "Agriculture Market Analysis", date: "Feasibility Study · March 2024", icon: "📊", color: "bg-emerald-100 text-emerald-600", tag: "agriculture" },
      { title: "Top Opportunities in Manufacturing", date: "Feasibility Study · February 2024", icon: "🏭", color: "bg-green-100 text-green-600", tag: "manufacturing" },
      { title: "E-Commerce Growth Trends", date: "Sector Analysis · January 2024", icon: "🛒", color: "bg-red-100 text-red-600", tag: "services" },
      { title: "Renewable Energy Roadmap", date: "Strategic Plan · Dec 2023", icon: "⚡", color: "bg-yellow-100 text-yellow-600", tag: "energy" }
    ];

    if (preferredSector) {
      // Prioritize reports matching the sector
      const relevant = allReports.filter(r => r.tag === preferredSector.slug);
      const others = allReports.filter(r => r.tag !== preferredSector.slug);
      setFilteredReports([...relevant, ...others].slice(0, 4));
    } else {
      setFilteredReports(allReports.slice(0, 4));
    }
  }, [preferredSector]);

  const registrationData = [
    { name: "Oct 2023", value: 2000 },
    { name: "Nov 2023", value: 3500 },
    { name: "Dec 2023", value: 4800 },
    { name: "Jan 2024", value: 4200 },
    { name: "Feb 2024", value: 6800 },
    { name: "Mar 2024", value: 8500 },
    { name: "Apr 2024", value: 11000 },
  ];

  return (
    <DashboardFilterProvider>
      <DashboardLayout>
        {/* Search Hero */}
        <div className="bg-primary relative overflow-hidden shadow-sm">
          <div className="absolute inset-0">
            <div className="absolute top-[10%] left-[5%] w-72 h-72 bg-white/10 rounded-full blur-3xl" />
            <div className="absolute top-[20%] right-[10%] w-56 h-56 bg-accent/20 rounded-full blur-3xl" />
          </div>
          <div className="relative px-4 sm:px-8 py-10 sm:py-14">
            <div className="max-w-2xl mx-auto text-center">
              <h1 className="text-2xl sm:text-3xl font-bold text-white mb-2 shadow-sm">
                {t("title")}
              </h1>
              <p className="text-sm sm:text-base text-white/80 mb-6">
                {t("welcome")}
              </p>

              {/* Search Input */}
              <div className="relative group">
                <div className="absolute -inset-1 bg-gradient-to-r from-accent/20 via-white/20 to-accent/20 rounded-2xl blur-sm opacity-0 group-focus-within:opacity-100 transition-opacity duration-500" />
                <div className="relative flex items-center bg-white/10 backdrop-blur-md border border-white/30 rounded-2xl overflow-hidden shadow-lg group-focus-within:border-white/50 group-focus-within:bg-white/15 transition-all duration-300">
                  <Search className="h-5 w-5 text-white/70 ml-4 shrink-0" />
                  <input
                    type="text"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    onKeyDown={handleSearchKeyDown}
                    placeholder={t("searchPlaceholder")}
                    className="flex-1 h-12 sm:h-14 px-3 text-sm sm:text-base bg-transparent text-white placeholder:text-white/60 focus:outline-none"
                  />
                  {searchQuery && (
                    <button
                      onClick={clearSearch}
                      className="p-1.5 mr-1 rounded-full text-white/70 hover:text-white hover:bg-white/10 transition-all shrink-0"
                    >
                      <X className="h-4 w-4" />
                    </button>
                  )}
                  <button
                    onClick={handleSearch}
                    disabled={!searchQuery.trim()}
                    className="h-9 sm:h-10 px-4 sm:px-5 mr-1.5 sm:mr-2 rounded-full bg-white text-primary text-sm font-semibold hover:bg-white/90 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-sm shrink-0 flex items-center gap-2"
                  >
                    {t("searchButton")}
                  </button>
                </div>
              </div>

              {/* Live Intent Hint */}
              {searchQuery.trim() && (
                <div className="flex items-center justify-center gap-2 mt-3 animate-fade-in-up">
                  <span
                    className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium ${intentDisplay.color} transition-all duration-200`}
                  >
                    <span>{intentDisplay.icon}</span>
                    <span>{t(intentDisplay.labelKey)}</span>
                  </span>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Content */}
        <div className="px-4 sm:px-8 py-8 space-y-8">

          {/* Customization Badge */}
          {preferredSector && (
            <div className="flex items-center gap-2 px-4 py-2 bg-primary/10 text-primary rounded-full w-fit animate-fade-in">
              <div className="h-2 w-2 rounded-full bg-primary animate-pulse" />
              <span className="text-sm font-medium">
                Customized for <span className="font-bold">{preferredSector.name_en}</span>
              </span>
            </div>
          )}

          {/* Executive Snapshot - Always visible at the top */}
          <div className="animate-in fade-in duration-700">
            <WidgetRenderer widget={{
              component: "executive_snapshot",
              title: "Algeria Market Pulse",
              summary_text: "Our AI orchestrated a real-time summary of the current economic climate in Algeria. Market activity remains robust with a focus on startup growth and digital transformation.",
              key_metrics: [
                { label: "Active Entities", value: "2.4M+", trend: "up" },
                { label: "Market Growth", value: "4.2%", trend: "up" },
                { label: "New Startups", value: "1,240", trend: "down" },
                { label: "Investor Index", value: "84/100", trend: "up" }
              ]
            }} />
          </div>

          {/* Dynamic AI Layout Integration */}
          {dashboardLayout.length > 0 && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 animate-in fade-in slide-in-from-bottom-4 duration-500 delay-100">
              {dashboardLayout
                .filter(w => w.component !== 'executive_snapshot') // Prevent duplication
                .map((widgetConf, index) => {
                  const component = widgetConf.component;
                  let colSpanInfo = 'col-span-1 md:col-span-2 lg:col-span-1';

                  // Standardizing column spans
                  if (component === 'choropleth_map' || component === 'data_table') {
                    colSpanInfo = 'col-span-1 md:col-span-2 lg:col-span-4';
                  } else if (['line_chart', 'bar_chart', 'pie_chart', 'stacked_area_chart', 'composed_chart'].includes(component)) {
                    colSpanInfo = 'col-span-1 md:col-span-2 lg:col-span-2';
                  } else if (['kpi_card', 'growth_indicator', 'gauge_card'].includes(component)) {
                    colSpanInfo = 'col-span-1 md:col-span-1 lg:col-span-1';
                  }

                  return (
                    <div key={index} className={colSpanInfo}>
                      <WidgetRenderer widget={widgetConf} />
                    </div>
                  );
                })}
            </div>
          )}

          {/* Loading placeholders if no dynamic layout yet */}
          {dashboardLayout.length === 0 && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <div className="col-span-1 md:col-span-2 lg:col-span-2">
                <div className="flex justify-center items-center py-20 flex-col gap-4 border border-dashed rounded-xl bg-gray-50/50">
                  <Loader2 className="h-8 w-8 animate-spin text-primary/40" />
                  <p className="text-muted-foreground animate-pulse text-xs">Analyzing regional trends...</p>
                </div>
              </div>
              <div className="col-span-1 md:col-span-2 lg:col-span-2">
                <div className="flex justify-center items-center py-20 flex-col gap-4 border border-dashed rounded-xl bg-gray-50/50">
                  <Loader2 className="h-8 w-8 animate-spin text-primary/40" />
                  <p className="text-muted-foreground animate-pulse text-xs">Synthesizing live data...</p>
                </div>
              </div>
            </div>
          )}

        </div>
      </DashboardLayout>
    </DashboardFilterProvider>
  );
}
