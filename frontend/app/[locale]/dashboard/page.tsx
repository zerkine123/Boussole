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

import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from "recharts";
import { useLocale } from "next-intl";
import { useRouter } from "next/navigation";
import {
  Briefcase,
  Smartphone,
  Building2,
  FileText,
  ArrowRight,
  Activity,
  DollarSign,
  TrendingUp,
  Search,
  X,
  Loader2,
} from "lucide-react";
import dynamic from "next/dynamic";
import "leaflet/dist/leaflet.css";
import DashboardLayout from "@/components/DashboardLayout";
import {
  classifySearchIntent,
  getSearchRoute,
  getIntentDisplay,
} from "@/lib/searchRouter";

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

  const handleSuggestionClick = (label: string) => {
    const classified = classifySearchIntent(label);
    const route = getSearchRoute(classified, locale);
    router.push(route);
  };

  const clearSearch = () => setSearchQuery("");

  const [preferredSector, setPreferredSector] = useState<AvailableSector | null>(null);
  const [filteredReports, setFilteredReports] = useState<any[]>([]);

  useEffect(() => {
    const fetchOnboardingData = async () => {
      try {
        const token = localStorage.getItem('access_token');
        if (!token) return;

        const response = await fetch('/api/v1/onboarding/data', {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });

        if (response.ok) {
          const data: OnboardingData = await response.json();

          // Determine preferred sector
          const prefs = data.current_preferences;
          if (prefs && prefs.sectors_of_interest && prefs.sectors_of_interest.length > 0) {
            const sectorId = prefs.sectors_of_interest[0];
            const sector = data.available_sectors.find(s => s.id === sectorId);
            if (sector) {
              setPreferredSector(sector);
            }
          }
        }
      } catch (error) {
        console.error("Failed to fetch onboarding data", error);
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

        {/* 1. Top-Level KPI Row */}
        <div>
          <h2 className="text-xl font-bold text-foreground mb-4 flex items-center gap-2">
            Dashboard Overview
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">
            {[
              { title: "Registered Businesses", value: "2.4M", sub: "Source: CNRC", icon: <Briefcase className="h-5 w-5 text-emerald-600" />, bg: "bg-emerald-50" },
              { title: "State Incubators", value: "92 of 4000", sub: "Based on public data", icon: <Building2 className="h-5 w-5 text-teal-600" />, bg: "bg-teal-50" },
              { title: "Mobile Phone Penetration", value: "82.7%", sub: "Based on public data", icon: <Smartphone className="h-5 w-5 text-blue-600" />, bg: "bg-blue-50" },
              { title: "Job Offers Posted", value: "228k+", sub: "Source: Emploitic", icon: <Briefcase className="h-5 w-5 text-amber-600" />, bg: "bg-amber-50" },
            ].map((kpi, i) => (
              <Card key={i} className="hover:shadow-md transition-all duration-300">
                <CardContent className="p-6">
                  <div className="flex items-start justify-between mb-4">
                    <div className={`h-10 w-10 rounded-xl flex items-center justify-center ${kpi.bg}`}>
                      {kpi.icon}
                    </div>
                  </div>
                  <div className="text-2xl font-bold text-foreground mb-1">{kpi.value}</div>
                  <div className="text-sm font-medium text-muted-foreground">{kpi.title}</div>
                  <div className="text-xs text-muted-foreground/70 mt-1">{kpi.sub}</div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>

        {/* 2. Key Stats & Chart Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left: 2x2 Key Stats Grid */}
          <div className="lg:col-span-1 space-y-6">
            <h3 className="text-lg font-semibold text-foreground">Key Stats {preferredSector ? `(${preferredSector.name_en})` : ""}</h3>
            <div className="grid grid-cols-2 gap-4">
              {/* 1. New Businesses */}
              <Card className="col-span-2 sm:col-span-1 border-emerald-100/50">
                <CardContent className="p-4">
                  <div className="h-8 w-8 rounded-lg bg-emerald-50 flex items-center justify-center mb-3">
                    <Briefcase className="h-4 w-4 text-emerald-600" />
                  </div>
                  <div className="text-xs text-muted-foreground">New Businesses</div>
                  <div className="text-lg font-bold text-foreground">
                    {preferredSector?.slug === "agriculture" ? "1,240" :
                      preferredSector?.slug === "energy" ? "450" :
                        "8,350"}
                  </div>
                  <div className="text-[10px] text-emerald-600 font-medium">+425 past 7 days</div>
                </CardContent>
              </Card>
              {/* 2. Trending Sectors */}
              <Card className="col-span-2 sm:col-span-1 border-blue-100/50">
                <CardContent className="p-4">
                  <div className="h-8 w-8 rounded-lg bg-blue-50 flex items-center justify-center mb-3">
                    <TrendingUp className="h-4 w-4 text-blue-600" />
                  </div>
                  <div className="text-xs text-muted-foreground">Trending Sector</div>
                  <div className="text-lg font-bold text-foreground">
                    {preferredSector ? preferredSector.name_en : "Agri-Tech"}
                  </div>
                </CardContent>
              </Card>
              {/* 3. Average Salary */}
              <Card className="col-span-2 sm:col-span-1 border-amber-100/50">
                <CardContent className="p-4">
                  <div className="h-8 w-8 rounded-lg bg-amber-50 flex items-center justify-center mb-3">
                    <DollarSign className="h-4 w-4 text-amber-600" />
                  </div>
                  <div className="text-xs text-muted-foreground">Average Salary</div>
                  <div className="text-lg font-bold text-foreground">
                    {preferredSector?.slug === "agriculture" ? "DZD 55,000" :
                      preferredSector?.slug === "energy" ? "DZD 95,000" :
                        "DZD 66,500"}
                  </div>
                  <div className="text-[10px] text-amber-600 font-medium">+2,440 today</div>
                </CardContent>
              </Card>
              {/* 4. Market Conditions */}
              <Card className="col-span-2 sm:col-span-1 border-purple-100/50">
                <CardContent className="p-4">
                  <div className="h-8 w-8 rounded-lg bg-purple-50 flex items-center justify-center mb-3">
                    <Activity className="h-4 w-4 text-purple-600" />
                  </div>
                  <div className="text-xs text-muted-foreground">Market Conditions</div>
                  <div className="text-lg font-bold text-foreground">Stable</div>
                  <div className="text-[10px] text-muted-foreground">2.3% inflation</div>
                </CardContent>
              </Card>
            </div>
          </div>

          {/* Right: Business Registrations Chart */}
          <div className="lg:col-span-2">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-foreground">
                Business Registrations {preferredSector ? `in ${preferredSector.name_en}` : ""}
              </h3>
              <div className="flex gap-2">
                <Button variant="outline" size="sm" className="h-8 text-xs rounded-lg">Last 6 Months</Button>
              </div>
            </div>
            <Card>
              <CardContent className="p-6">
                <div className="h-[250px] w-full">
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={registrationData}>
                      <defs>
                        <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#10b981" stopOpacity={0.2} />
                          <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                        </linearGradient>
                      </defs>
                      <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e5e7eb" />
                      <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: '#6b7280' }} />
                      <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: '#6b7280' }} />
                      <Tooltip />
                      <Area type="monotone" dataKey="value" stroke="#10b981" strokeWidth={2} fillOpacity={1} fill="url(#colorValue)" />
                    </AreaChart>
                  </ResponsiveContainer>
                </div>
                <div className="mt-4 flex flex-col sm:flex-row items-center justify-between gap-4">
                  <div>
                    <div className="text-sm text-muted-foreground">New Businesses</div>
                    <div className="text-2xl font-bold text-foreground">
                      {preferredSector?.slug === "agriculture" ? "1,240" : "11,000"}
                    </div>
                    <div className="text-xs text-muted-foreground">Total: 225,229</div>
                  </div>
                  <Button className="w-full sm:w-auto">View Analytics</Button>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>

        {/* 3. Recent Reports & Feasibility Insights */}
        <div>
          <h2 className="text-lg font-semibold text-foreground mb-4">
            Recent Reports & Feasibility Insights
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {filteredReports.map((report, i) => (
              <Card key={i} className="hover:bg-accent/50 transition-colors cursor-pointer group">
                <CardContent className="p-4 flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className={`h-12 w-12 rounded-xl flex items-center justify-center text-xl ${report.color}`}>
                      {report.icon}
                    </div>
                    <div>
                      <h3 className="font-semibold text-foreground group-hover:text-primary transition-colors">{report.title}</h3>
                      <p className="text-xs text-muted-foreground">{report.date}</p>
                    </div>
                  </div>
                  <ArrowRight className="h-5 w-5 text-muted-foreground/50 group-hover:text-primary transition-colors" />
                </CardContent>
              </Card>
            ))}
          </div>
        </div>

      </div>
    </DashboardLayout>
  );
}



