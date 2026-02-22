"use client";

import { useTranslations, useLocale } from "next-intl";
import { useState, useEffect, useRef } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { Card, CardContent } from "@/components/ui/card";
import {
  Search, Sparkles, Loader2, X, ArrowRight, FileDown,
  SlidersHorizontal, Calendar, Building2, MapPin, ChevronDown, RotateCcw
} from "lucide-react";

import DashboardLayout from "@/components/DashboardLayout";
import { WidgetRenderer } from "@/components/widgets/WidgetRegistry";
import { api } from "@/lib/api";
import { DashboardFilterProvider } from "@/lib/DashboardFilterContext";
import { generateExplorerPDF } from "@/components/ExplorerPDFExport";

const SECTORS = [
  "All Sectors", "Agriculture", "Energy", "Manufacturing", "Services",
  "Tourism", "Innovation", "Consulting", "Housing", "Education",
  "Health", "Technology", "Construction", "Transport", "Commerce",
];

const YEARS = ["All Years", "2024", "2023", "2022", "2021", "2020", "2019", "2018"];

const WILAYAS = [
  "All Wilayas", "Algiers", "Oran", "Constantine", "Annaba", "Sétif",
  "Batna", "Béjaïa", "Tizi Ouzou", "Blida", "Boumerdès",
];

const SUGGESTIONS = [
  "Compare Agriculture and Tech startups in Algiers vs Oran",
  "Show me the growth timeline of incubators across Algeria",
  "What is the pipeline conversion rate for manufacturing?",
  "Give me an executive snapshot of the renewable energy sector",
];

export default function DataExplorerPage() {
  const t = useTranslations("dataExplorer");
  const locale = useLocale();
  const searchParams = useSearchParams();
  const router = useRouter();

  const [searchQuery, setSearchQuery] = useState("");
  const [activeQuery, setActiveQuery] = useState("");
  const [isGenerating, setIsGenerating] = useState(false);
  const [isExporting, setIsExporting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [layoutParams, setLayoutParams] = useState<any[]>([]);
  const chartContainerRef = useRef<HTMLDivElement>(null);

  // Customization filters
  const [selectedSector, setSelectedSector] = useState("All Sectors");
  const [selectedYear, setSelectedYear] = useState("All Years");
  const [selectedWilaya, setSelectedWilaya] = useState("All Wilayas");
  const [showFilters, setShowFilters] = useState(false);

  // Are we in results mode?
  const hasResults = !isGenerating && layoutParams.length > 0 && !!activeQuery;

  useEffect(() => {
    const q = searchParams.get("q");
    if (q && q !== activeQuery) {
      setSearchQuery(q);
      handleGenerateLayout(q);
    }
  }, [searchParams]);

  const handleSearchKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      e.preventDefault();
      handleGenerateLayout(searchQuery);
    }
  };

  const handleGenerateLayout = async (queryToRun: string) => {
    if (!queryToRun.trim()) return;
    setIsGenerating(true);
    setError(null);
    setActiveQuery(queryToRun);
    try {
      const token = localStorage.getItem("access_token");
      const response = await api.generateDashboardLayout(token, queryToRun);
      if (response && response.layout) {
        setLayoutParams(response.layout);
      } else {
        setLayoutParams([]);
        setError("Failed to construct a comprehensive layout from your query.");
      }
    } catch (err: any) {
      console.error("AI Layout Generation error:", err);
      if (err.statusCode === 401 || err.statusCode === 403) {
        setError("Please log in to use the Data Explorer.");
      } else {
        setError(err.message || "Failed to analyze data request. Please try again.");
      }
      setLayoutParams([]);
    } finally {
      setIsGenerating(false);
    }
  };

  const clearSearch = () => {
    setSearchQuery("");
    setActiveQuery("");
    setLayoutParams([]);
    setError(null);
    setSelectedSector("All Sectors");
    setSelectedYear("All Years");
    setSelectedWilaya("All Wilayas");
    router.replace(`/${locale}/data`, undefined);
  };

  const suggestQuery = (q: string) => {
    setSearchQuery(q);
    handleGenerateLayout(q);
  };

  return (
    <DashboardFilterProvider>
      <DashboardLayout>

        {/* ── HERO BANNER ─────────────────────────────────────────────────
            Two states:
            1. Idle  → tall, centered, decorative
            2. Active → compact toolbar strip
        ─────────────────────────────────────────────────────────────── */}
        <div
          className={`relative overflow-hidden transition-all duration-500 ease-in-out shadow-sm
            ${hasResults || isGenerating ? "bg-emerald-600" : "bg-emerald-500"}`}
        >
          {/* Decorative blobs */}
          <div
            className={`absolute inset-0 pointer-events-none transition-opacity duration-500
              ${hasResults || isGenerating ? "opacity-30" : "opacity-100"}`}
          >
            <div className="absolute top-[20%] left-[10%] w-48 h-48 bg-white/20 rounded-full blur-3xl" />
            <div className="absolute top-[40%] right-[15%] w-36 h-36 bg-white/20 rounded-full blur-3xl" />
          </div>

          <div className="absolute inset-0 bg-gradient-to-br from-white/10 to-transparent pointer-events-none" />

          {/* ── IDLE STATE (full hero) ─────────────────────────── */}
          {!hasResults && !isGenerating && (
            <div className="relative px-4 sm:px-8 py-10 sm:py-16 text-center animate-in fade-in duration-300">
              <h1 className="text-3xl sm:text-4xl font-extrabold text-white mb-4 tracking-tight">
                Boussole <span className="text-accent">Data Explorer</span>
              </h1>
              <p className="max-w-xl mx-auto text-base sm:text-lg text-white/80 mb-8 leading-relaxed">
                Describe the insights you're looking for. Our AI synthesizes,
                aggregates, and renders the perfect real-time charts instantly.
              </p>

              {/* Big Search Bar */}
              <div className="max-w-2xl mx-auto relative group">
                <div className="absolute -inset-1 bg-gradient-to-r from-accent/20 via-white/20 to-accent/20 rounded-2xl blur-md opacity-0 group-focus-within:opacity-100 transition-opacity duration-500" />
                <div className="relative flex items-center bg-white/10 backdrop-blur-md border border-white/30 rounded-2xl overflow-hidden shadow-2xl group-focus-within:border-white/50 group-focus-within:bg-white/15 transition-all duration-300">
                  <Sparkles className="h-5 w-5 text-accent ml-5 shrink-0" />
                  <input
                    type="text"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    onKeyDown={handleSearchKeyDown}
                    placeholder="E.g. Compare total companies in Oran vs Setif..."
                    className="flex-1 h-14 sm:h-16 px-4 text-base sm:text-lg bg-transparent text-white placeholder:text-white/60 focus:outline-none"
                  />
                  <button
                    onClick={() => handleGenerateLayout(searchQuery)}
                    disabled={!searchQuery.trim()}
                    className="h-10 sm:h-12 px-5 sm:px-6 mr-2 rounded-xl bg-white text-primary text-sm sm:text-base font-bold hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-md shrink-0 flex items-center gap-2"
                  >
                    Explore
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* ── GENERATING STATE (compact, spinner) ───────────── */}
          {isGenerating && (
            <div className="relative px-4 sm:px-8 py-5 flex items-center gap-4 animate-in fade-in duration-200">
              <Loader2 className="w-5 h-5 text-accent animate-spin shrink-0" />
              <div className="flex-1 relative group">
                <div className="flex items-center bg-white/10 backdrop-blur-md border border-white/30 rounded-xl overflow-hidden px-4 h-11">
                  <Sparkles className="h-4 w-4 text-accent mr-3 shrink-0" />
                  <span className="text-white/80 text-sm truncate">{searchQuery}</span>
                </div>
              </div>
              <span className="text-white/70 text-sm shrink-0">Synthesizing...</span>
            </div>
          )}

          {/* ── RESULTS STATE (compact toolbar) ───────────────── */}
          {hasResults && (
            <div className="relative animate-in fade-in slide-in-from-top-2 duration-300">
              {/* Top row: search bar + actions */}
              <div className="px-4 sm:px-6 py-3 flex items-center gap-3">
                {/* Compact search input */}
                <div className="flex-1 flex items-center bg-white/10 backdrop-blur-md border border-white/25 rounded-xl overflow-hidden h-11 group focus-within:border-white/50 transition-all">
                  <Sparkles className="h-4 w-4 text-accent ml-4 shrink-0" />
                  <input
                    type="text"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    onKeyDown={handleSearchKeyDown}
                    placeholder="Refine your query..."
                    className="flex-1 px-3 h-full bg-transparent text-white text-sm placeholder:text-white/50 focus:outline-none"
                  />
                  {searchQuery && (
                    <button onClick={clearSearch} className="p-2 text-white/60 hover:text-white transition-colors">
                      <X className="h-4 w-4" />
                    </button>
                  )}
                  <button
                    onClick={() => handleGenerateLayout(searchQuery)}
                    disabled={!searchQuery.trim()}
                    className="h-full px-4 bg-white/15 hover:bg-white/25 text-white text-sm font-semibold border-l border-white/20 transition-all disabled:opacity-40 shrink-0 flex items-center gap-1.5"
                  >
                    <Search className="h-3.5 w-3.5" />
                    Search
                  </button>
                </div>

                {/* Filter toggle */}
                <button
                  onClick={() => setShowFilters(f => !f)}
                  className={`flex items-center gap-2 px-3.5 h-11 rounded-xl text-sm font-medium border transition-all shrink-0
                    ${showFilters
                      ? "bg-white text-primary border-white"
                      : "bg-white/10 text-white border-white/25 hover:bg-white/20"
                    }`}
                >
                  <SlidersHorizontal className="h-4 w-4" />
                  <span className="hidden sm:inline">Filters</span>
                  {(selectedSector !== "All Sectors" || selectedYear !== "All Years" || selectedWilaya !== "All Wilayas") && (
                    <span className="w-2 h-2 bg-accent rounded-full" />
                  )}
                </button>

                {/* PDF Export */}
                <button
                  onClick={async () => {
                    setIsExporting(true);
                    try {
                      await generateExplorerPDF({ query: activeQuery, layoutWidgets: layoutParams, chartContainerRef });
                    } catch (err) {
                      console.error("PDF export failed:", err);
                    } finally {
                      setIsExporting(false);
                    }
                  }}
                  disabled={isExporting}
                  className="flex items-center gap-2 px-3.5 h-11 rounded-xl bg-accent text-primary text-sm font-bold hover:bg-accent/90 disabled:opacity-50 transition-all shadow-md shrink-0"
                >
                  {isExporting ? <Loader2 className="w-4 h-4 animate-spin" /> : <FileDown className="w-4 h-4" />}
                  <span className="hidden sm:inline">{isExporting ? "Exporting..." : "Report"}</span>
                </button>

                {/* Reset */}
                <button
                  onClick={clearSearch}
                  title="Clear results"
                  className="flex items-center justify-center w-11 h-11 rounded-xl bg-white/10 text-white/70 hover:text-white hover:bg-white/20 border border-white/20 transition-all shrink-0"
                >
                  <RotateCcw className="h-4 w-4" />
                </button>
              </div>

              {/* Expandable filter row */}
              <div
                className={`overflow-hidden transition-all duration-300 ease-in-out
                  ${showFilters ? "max-h-24 opacity-100" : "max-h-0 opacity-0"}`}
              >
                <div className="px-4 sm:px-6 pb-3 pt-1 flex flex-wrap items-center gap-2 border-t border-white/10">
                  {/* Sector picker */}
                  <div className="relative">
                    <Building2 className="absolute left-2.5 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-white/50 pointer-events-none" />
                    <select
                      value={selectedSector}
                      onChange={(e) => setSelectedSector(e.target.value)}
                      className="h-9 pl-7 pr-7 rounded-lg bg-white/10 border border-white/20 text-white text-xs font-medium focus:outline-none focus:border-white/50 appearance-none cursor-pointer hover:bg-white/15 transition-all"
                    >
                      {SECTORS.map(s => <option key={s} value={s} className="bg-primary text-white">{s}</option>)}
                    </select>
                    <ChevronDown className="absolute right-2 top-1/2 -translate-y-1/2 h-3 w-3 text-white/50 pointer-events-none" />
                  </div>

                  {/* Wilaya picker */}
                  <div className="relative">
                    <MapPin className="absolute left-2.5 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-white/50 pointer-events-none" />
                    <select
                      value={selectedWilaya}
                      onChange={(e) => setSelectedWilaya(e.target.value)}
                      className="h-9 pl-7 pr-7 rounded-lg bg-white/10 border border-white/20 text-white text-xs font-medium focus:outline-none focus:border-white/50 appearance-none cursor-pointer hover:bg-white/15 transition-all"
                    >
                      {WILAYAS.map(w => <option key={w} value={w} className="bg-primary text-white">{w}</option>)}
                    </select>
                    <ChevronDown className="absolute right-2 top-1/2 -translate-y-1/2 h-3 w-3 text-white/50 pointer-events-none" />
                  </div>

                  {/* Year picker */}
                  <div className="relative">
                    <Calendar className="absolute left-2.5 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-white/50 pointer-events-none" />
                    <select
                      value={selectedYear}
                      onChange={(e) => setSelectedYear(e.target.value)}
                      className="h-9 pl-7 pr-7 rounded-lg bg-white/10 border border-white/20 text-white text-xs font-medium focus:outline-none focus:border-white/50 appearance-none cursor-pointer hover:bg-white/15 transition-all"
                    >
                      {YEARS.map(y => <option key={y} value={y} className="bg-primary text-white">{y}</option>)}
                    </select>
                    <ChevronDown className="absolute right-2 top-1/2 -translate-y-1/2 h-3 w-3 text-white/50 pointer-events-none" />
                  </div>

                  {/* Active query badge */}
                  <div className="ml-auto flex items-center gap-2 text-white/60 text-xs">
                    <span>Query:</span>
                    <span className="px-2 py-0.5 bg-white/10 rounded-full text-white/80 max-w-[200px] truncate">
                      "{activeQuery}"
                    </span>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* ── CONTENT AREA ───────────────────────────────────── */}
        <div className="px-4 sm:px-8 py-8 min-h-[500px]">

          {/* State 1: Empty / Instructions */}
          {!activeQuery && !isGenerating && layoutParams.length === 0 && (
            <div className="max-w-4xl mx-auto mt-6 animate-in fade-in duration-300">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <Card className="border-dashed bg-accent/5 hover:bg-accent/10 transition-colors">
                  <CardContent className="p-6">
                    <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center mb-4">
                      <Sparkles className="w-5 h-5 text-primary" />
                    </div>
                    <h3 className="text-lg font-bold mb-2">How it Works</h3>
                    <p className="text-muted-foreground text-sm leading-relaxed">
                      Tell Boussole what you want to know. The AI engine translates your intent
                      across 21 dynamic visualization modules—from head-to-head comparisons to
                      dense metric grids—and fetches live data instantly.
                    </p>
                  </CardContent>
                </Card>

                <div className="flex flex-col gap-3 justify-center">
                  <h4 className="text-sm font-semibold text-muted-foreground uppercase tracking-wider ml-1">
                    Example Prompts
                  </h4>
                  {SUGGESTIONS.map((suggestion, i) => (
                    <button
                      key={i}
                      onClick={() => suggestQuery(suggestion)}
                      className="text-left px-4 py-3 bg-card border rounded-lg hover:border-primary/50 hover:shadow-sm transition-all text-sm font-medium flex items-center justify-between group"
                    >
                      <span className="truncate pr-4">{suggestion}</span>
                      <ArrowRight className="w-4 h-4 text-muted-foreground group-hover:text-primary transition-colors shrink-0" />
                    </button>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* State 2: Error */}
          {error && !isGenerating && (
            <div className="max-w-2xl mx-auto p-4 bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 rounded-lg text-center border border-red-200 dark:border-red-800 animate-in fade-in duration-300">
              <p className="font-semibold">{error}</p>
            </div>
          )}

          {/* State 3: Loading */}
          {isGenerating && (
            <div className="flex flex-col items-center justify-center py-24 gap-6">
              <div className="relative">
                <div className="absolute inset-0 bg-primary/20 blur-xl rounded-full" />
                <Loader2 className="w-12 h-12 text-primary animate-spin relative z-10" />
              </div>
              <p className="text-lg font-medium text-muted-foreground text-center">
                Querying the database and structuring visualizations...
              </p>
            </div>
          )}

          {/* State 4: Results */}
          {hasResults && (
            <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-700">
              <div ref={chartContainerRef} className="grid grid-cols-1 lg:grid-cols-12 gap-6">
                {[...layoutParams]
                  .sort((a, b) => (a.component === 'executive_snapshot' ? -1 : (b.component === 'executive_snapshot' ? 1 : 0)))
                  .map((widgetConf, index) => {
                    const component = widgetConf.component;
                    let colSpan = "col-span-1 lg:col-span-12";
                    if (['kpi_card', 'growth_indicator', 'gauge_card'].includes(component)) {
                      colSpan = "col-span-1 md:col-span-6 lg:col-span-3";
                    } else if (['pie_chart', 'radar_chart', 'comparison_card', 'insight_panel'].includes(component)) {
                      colSpan = "col-span-1 lg:col-span-6";
                    } else if (['line_chart', 'bar_chart', 'composed_chart', 'scatter_plot', 'treemap', 'funnel_chart', 'choropleth_map', 'data_table', 'executive_snapshot', 'stacked_area_chart', 'metric_grid', 'sentiment_timeline'].includes(component)) {
                      colSpan = "col-span-1 lg:col-span-12";
                    }
                    return (
                      <div key={`${component}-${index}`} className={colSpan}>
                        <WidgetRenderer widget={widgetConf} />
                      </div>
                    );
                  })}
              </div>
            </div>
          )}

        </div>
      </DashboardLayout>
    </DashboardFilterProvider>
  );
}
