"use client";

import { useTranslations } from "next-intl";
import { useState, useEffect, useMemo } from "react";
import { useSearchParams } from "next/navigation";
import {
  Card,
  CardContent,
  CardHeader,
  CardDescription,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Checkbox } from "@/components/ui/checkbox";
import { Label } from "@/components/ui/label";
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from "recharts";
import { useLocale } from "next-intl";
import {
  Download,
  Filter,
  RefreshCw,
  ChevronDown,
  ChevronUp,
  Search,
  FileText,
  Database,
  Calendar,
  MapPin,
} from "lucide-react";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import DashboardLayout from "@/components/DashboardLayout";
import DynamicDataView from "@/components/DynamicDataView";
import { Sparkles } from "lucide-react";

// Algeria Wilayas
const WILAYAS = [
  { code: "01", name: "Algiers", name_fr: "Alger", name_ar: "الجزائر" },
  { code: "02", name: "Oran", name_fr: "Oran", name_ar: "وهران" },
  { code: "03", name: "Constantine", name_fr: "Constantine", name_ar: "قسنطينة" },
  { code: "04", name: "Setif", name_fr: "Sétif", name_ar: "سطيف" },
  { code: "05", name: "Batna", name_fr: "Batna", name_ar: "باتنة" },
  { code: "06", name: "Annaba", name_fr: "Annaba", name_ar: "عنابة" },
  { code: "07", name: "Skikda", name_fr: "Skikda", name_ar: "سكيكدة" },
  { code: "08", name: "Tlemcen", name_fr: "Tlemcen", name_ar: "تلمسان" },
  { code: "09", name: "Tizi Ouzou", name_fr: "Tizi Ouzou", name_ar: "تيزي وزو" },
  { code: "10", name: "Béjaïa", name_fr: "Béjaïa", name_ar: "بجاية" },
  { code: "11", name: "Biskra", name_fr: "Biskra", name_ar: "بسكرة" },
  { code: "12", name: "Boumerdès", name_fr: "Boumerdès", name_ar: "بومرداس" },
  { code: "13", name: "Tebessa", name_fr: "Tébessa", name_ar: "تبسة" },
  { code: "14", name: "Ouargla", name_fr: "Ouargla", name_ar: "ورقلة" },
];

const SECTORS = [
  { id: "agriculture", name: "Agriculture", name_fr: "Agriculture", name_ar: "الزراعة" },
  { id: "energy", name: "Energy", name_fr: "Énergie", name_ar: "الطاقة" },
  { id: "manufacturing", name: "Manufacturing", name_fr: "Industrie", name_ar: "الصناعة" },
  { id: "services", name: "Services", name_fr: "Services", name_ar: "الخدمات" },
  { id: "tourism", name: "Tourism", name_fr: "Tourisme", name_ar: "السياحة" },
  { id: "innovation", name: "Innovation", name_fr: "Innovation", name_ar: "الابتكار" },
  { id: "consulting", name: "Consulting", name_fr: "Conseil", name_ar: "الاستشارات" },
];

const METRICS = [
  { id: "gdp", name: "GDP", name_fr: "PIB", name_ar: "الناتج المحلي الإجمالي" },
  { id: "population", name: "Population", name_fr: "Population", name_ar: "السكان" },
  { id: "employment", name: "Employment", name_fr: "Emploi", name_ar: "التشغيل" },
  { id: "investment", name: "Investment", name_fr: "Investissement", name_ar: "الاستثمار" },
  { id: "production", name: "Production", name_fr: "Production", name_ar: "الإنتاج" },
  { id: "entities", name: "Registered Entities", name_fr: "Entités immatriculées", name_ar: "الكيانات المسجلة" },
  { id: "incubators", name: "Incubators", name_fr: "Incubateurs", name_ar: "حاضنات الأعمال" },
  { id: "projects", name: "Startup Projects", name_fr: "Projets Startup", name_ar: "مشاريع ناشئة" },
];

interface DataPoint {
  id: string;
  wilaya: string;
  wilayaName: string;
  sector: string;
  sectorName: string;
  metric: string;
  metricName: string;
  year: number;
  value: number;
  unit: string;
}

interface SearchIntent {
  intent: string;
  topic?: string;
  subtopic?: string;
  location?: string;
  filters?: Record<string, any>;
  confidence: number;
}

interface SearchAnalysisResponse {
  original_query: string;
  analysis: SearchIntent;
}

export default function DataExplorerPage() {
  const t = useTranslations("dataExplorer");
  const locale = useLocale();
  const searchParams = useSearchParams();

  const [data, setData] = useState<DataPoint[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const [selectedSectors, setSelectedSectors] = useState<string[]>([]);
  const [selectedWilayas, setSelectedWilayas] = useState<string[]>([]);
  const [selectedMetrics, setSelectedMetrics] = useState<string[]>([]);
  const [yearRange, setYearRange] = useState({ start: 2015, end: 2024 });
  const [showFilters, setShowFilters] = useState(false);
  const [sortColumn, setSortColumn] = useState<string>("");
  const [sortDirection, setSortDirection] = useState<"asc" | "desc">("asc");
  const [exportFormat, setExportFormat] = useState<"csv" | "excel" | "pdf">("csv");
  const [isExporting, setIsExporting] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [dynamicQuery, setDynamicQuery] = useState<string | null>(null);

  // Auto-fill from URL search params (universal search router)
  useEffect(() => {
    const q = searchParams.get("q");
    const sector = searchParams.get("sector");
    const location = searchParams.get("location");

    // If there's a search query, always trigger AI dynamic view
    if (q) {
      setDynamicQuery(q);
      return;
    }

    // Standard URL filters (if clicked from dashboard badges without query)
    if (sector && SECTORS.some((s) => s.id === sector)) {
      setSelectedSectors([sector]);
      setShowFilters(true);
    }
    if (location && WILAYAS.some((w) => w.code === location)) {
      setSelectedWilayas([location]);
      setShowFilters(true);
    }
  }, [searchParams]);

  const analyzeSearchQuery = async (query: string) => {
    try {
      // 1. Set text query immediately for feedback
      setSearchQuery(query);
      setIsLoading(true);

      // 2. Call Backend API
      const token = localStorage.getItem("access_token"); // Optional: if protected
      const response = await fetch("/api/v1/search/analyze", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...(token && { Authorization: `Bearer ${token}` }),
        },
        body: JSON.stringify({ query }),
      });

      if (response.ok) {
        const data: SearchAnalysisResponse = await response.json();
        const { topic, location, subtopic, intent } = data.analysis;

        // 3. Apply Filters based on AI Analysis
        if (topic) {
          // Map topic to sector ID
          const matchedSector = SECTORS.find(s => s.id === topic || s.name.toLowerCase().includes(topic));
          if (matchedSector) {
            setSelectedSectors(prev => [...new Set([...prev, matchedSector.id])]);
            setShowFilters(true);
          }
        }

        if (location) {
          const matchedWilaya = WILAYAS.find(w => w.code === location);
          if (matchedWilaya) {
            setSelectedWilayas(prev => [...new Set([...prev, matchedWilaya.code])]);
            setShowFilters(true);
          }
        }

        // If high confidence, maybe clear purely textual search to show all sector data?
        // For now, keep it, but maybe optimize user experience later.
      }
    } catch (error) {
      console.error("Smart Search failed:", error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setIsLoading(true);
    setError("");

    try {
      // Simulate network delay
      await new Promise((resolve) => setTimeout(resolve, 600));

      const mockData: DataPoint[] = [];
      const sectorsList = selectedSectors.length > 0 ? selectedSectors : SECTORS.map((s) => s.id);
      const wilayasList = selectedWilayas.length > 0 ? selectedWilayas : WILAYAS.map((w) => w.code);
      const metricsList = selectedMetrics.length > 0 ? selectedMetrics : METRICS.map((m) => m.id);

      let id = 1;

      // Generation logic based on Boussole Presentation Data
      // Total Businesses: ~2.4M (Entities)
      // Startups: ~8,000 (Projects)
      // Incubators: 192
      // Consulting: ~5,000

      // Multipliers for realistic distribution
      const wilayaWeights: Record<string, number> = {
        "01": 0.15, // Algiers (High)
        "02": 0.08, // Oran
        "03": 0.06, // Constantine
        "04": 0.05, // Setif
        "14": 0.04, // Ouargla (Energy)
        "13": 0.03, // Tebessa
        "07": 0.04, // Biskra (Agriculture)
      };

      for (const sector of sectorsList) {
        for (const wilaya of wilayasList) {
          const wObj = WILAYAS.find((w) => w.code === wilaya);
          if (!wObj) continue;

          const weight = wilayaWeights[wilaya] || 0.015; // Default weight for others
          const isMajorCity = ["01", "02", "03", "04"].includes(wilaya);

          for (const metric of metricsList) {
            for (let year = yearRange.start; year <= yearRange.end; year++) {
              let computedValue = 0;
              let unit = "units";

              // Logic per metric and sector
              if (metric === "entities") {
                // PDF: 2.4M total entities
                // ~2.1M Individuals + ~274k Companies
                const totalEntities = 2400000;
                computedValue = Math.round(totalEntities * weight * (1 + (year - 2020) * 0.03));
              }
              else if (metric === "incubators") {
                // PDF: 192 official incubators
                if (sector === "innovation") {
                  const totalIncubators = 192;
                  // Heavily skewed to major cities
                  const incubatorWeight = isMajorCity ? weight * 2 : weight * 0.5;
                  computedValue = Math.round(totalIncubators * incubatorWeight);
                  if (computedValue < 1 && isMajorCity) computedValue = 1;
                } else {
                  computedValue = 0;
                }
              }
              else if (metric === "projects" && sector === "innovation") {
                // PDF: ~8000 startups, ~2500 labeled
                const totalStartups = 8000;
                computedValue = Math.round(totalStartups * weight * (1 + (year - 2024) * 0.1)); // High growth
              }
              else if (sector === "consulting" && metric === "entities") {
                // PDF: ~5000 consulting agencies
                const totalConsulting = 5000;
                computedValue = Math.round(totalConsulting * weight);
              }
              else if (sector === "agriculture" && metric === "production") {
                // PDF: 12% growth in 2024
                const baseProd = 50000; // Arbitrary base for tonnes/units
                const growth = year >= 2024 ? 1.12 : 1.02;
                computedValue = Math.round(baseProd * weight * Math.pow(growth, year - 2015));
                unit = "tonnes";
              }
              else if (metric === "gdp") {
                computedValue = Math.round(5000 * weight * (year - 2000)); // Rough GDP proxy
                unit = "M DZD";
              }
              else {
                // Fallback random
                computedValue = Math.round(Math.random() * 10000);
              }

              // Ensure no duplicates or weird zeros
              if (computedValue < 0) computedValue = 0;

              const sectorObj = SECTORS.find((s) => s.id === sector);
              const metricObj = METRICS.find((m) => m.id === metric);

              mockData.push({
                id: String(id++),
                wilaya,
                wilayaName: wObj.name,
                sector,
                sectorName: sectorObj?.name || sector,
                metric,
                metricName: metricObj?.name || metric,
                year,
                value: computedValue,
                unit: metric === "gdp" || metric === "investment" ? "M DZD" : unit,
              });
            }
          }
        }
      }
      setData(mockData);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load data");
    } finally {
      setIsLoading(false);
    }
  };

  const filteredAndSortedData = useMemo(() => {
    let result = [...data];

    if (searchQuery) {
      const q = searchQuery.toLowerCase();
      result = result.filter(
        (d) =>
          d.wilayaName.toLowerCase().includes(q) ||
          d.sectorName.toLowerCase().includes(q) ||
          d.metricName.toLowerCase().includes(q)
      );
    }

    if (sortColumn) {
      result.sort((a, b) => {
        const aValue = a[sortColumn as keyof DataPoint];
        const bValue = b[sortColumn as keyof DataPoint];
        if (typeof aValue === "number" && typeof bValue === "number") {
          return sortDirection === "asc" ? aValue - bValue : bValue - aValue;
        }
        if (typeof aValue === "string" && typeof bValue === "string") {
          return sortDirection === "asc" ? aValue.localeCompare(bValue) : bValue.localeCompare(aValue);
        }
        return 0;
      });
    }
    return result;
  }, [data, sortColumn, sortDirection, searchQuery]);

  const handleSort = (columnId: string) => {
    if (sortColumn === columnId) {
      setSortDirection(sortDirection === "asc" ? "desc" : "asc");
    } else {
      setSortColumn(columnId);
      setSortDirection("asc");
    }
  };

  const handleExport = async () => {
    setIsExporting(true);
    try {
      await new Promise((resolve) => setTimeout(resolve, 1000));
      alert(`${t("export.success")}`);
    } catch (err) {
      alert(t("export.error"));
    } finally {
      setIsExporting(false);
    }
  };

  const toggleSector = (sectorId: string) => {
    setSelectedSectors((prev) => prev.includes(sectorId) ? prev.filter((id) => id !== sectorId) : [...prev, sectorId]);
  };

  const toggleWilaya = (wilayaCode: string) => {
    setSelectedWilayas((prev) => prev.includes(wilayaCode) ? prev.filter((c) => c !== wilayaCode) : [...prev, wilayaCode]);
  };

  const toggleMetric = (metricId: string) => {
    setSelectedMetrics((prev) => prev.includes(metricId) ? prev.filter((id) => id !== metricId) : [...prev, metricId]);
  };

  const clearFilters = () => {
    setSelectedSectors([]);
    setSelectedWilayas([]);
    setSelectedMetrics([]);
    setYearRange({ start: 2015, end: 2024 });
  };

  const getWilayaName = (wilaya: string) => {
    const obj = WILAYAS.find((w) => w.code === wilaya);
    if (locale === "fr") return obj?.name_fr || wilaya;
    if (locale === "ar") return obj?.name_ar || wilaya;
    return obj?.name || wilaya;
  };

  const getSectorName = (sector: string) => {
    const obj = SECTORS.find((s) => s.id === sector);
    if (locale === "fr") return obj?.name_fr || sector;
    if (locale === "ar") return obj?.name_ar || sector;
    return obj?.name || sector;
  };

  const getMetricName = (metric: string) => {
    const obj = METRICS.find((m) => m.id === metric);
    if (locale === "fr") return obj?.name_fr || metric;
    if (locale === "ar") return obj?.name_ar || metric;
    return obj?.name || metric;
  };

  return (
    <DashboardLayout>
      {/* Banner Header */}
      <div className="banner-gradient relative overflow-hidden">
        <div className="absolute inset-0">
          <div className="absolute top-[20%] left-[10%] w-48 h-48 bg-white/5 rounded-full blur-3xl" />
          <div className="absolute top-[40%] right-[15%] w-36 h-36 bg-white/8 rounded-full blur-3xl" />
        </div>
        <div className="relative px-8 py-8">
          <p className="text-sm text-white/70 mb-1">📊 Data / Overview</p>
          <h1 className="text-2xl font-bold text-white">
            {t("title")}{" "}
            <span className="text-white/60 font-normal text-lg">
              {filteredAndSortedData.length.toLocaleString()}
            </span>
          </h1>
        </div>
      </div>

      {/* Content */}
      <div className="px-8 py-8 space-y-6">
        {/* Search & Actions Bar */}
        <Card>
          <CardContent className="p-4">
            <div className="flex flex-wrap items-center gap-3">
              {/* Search */}
              <div className="relative flex-1 min-w-[200px] max-w-md">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <input
                  type="text"
                  placeholder={"AI Search: e.g. greenhouses in Algiers..."}
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter" && searchQuery.trim()) {
                      setDynamicQuery(searchQuery.trim());
                    }
                  }}
                  className="w-full h-9 pl-9 pr-4 text-sm bg-gray-50 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary/50 transition-all"
                />
              </div>

              <Button
                size="sm"
                onClick={() => {
                  if (searchQuery.trim()) setDynamicQuery(searchQuery.trim());
                }}
                disabled={!searchQuery.trim()}
                className="bg-gradient-to-r from-primary to-emerald-600 text-white hover:from-primary/90 hover:to-emerald-600/90"
              >
                <Sparkles className="h-4 w-4 mr-1.5" />
                AI Search
              </Button>

              <Button
                variant="outline"
                size="sm"
                onClick={() => setShowFilters(!showFilters)}
              >
                <Filter className="h-4 w-4 mr-1.5" />
                {t("filters.title")}
                {showFilters ? (
                  <ChevronUp className="h-3.5 w-3.5 ml-1" />
                ) : (
                  <ChevronDown className="h-3.5 w-3.5 ml-1" />
                )}
              </Button>

              <Button
                variant="outline"
                size="sm"
                onClick={fetchData}
                disabled={isLoading}
              >
                <RefreshCw className={`h-4 w-4 mr-1.5 ${isLoading ? "animate-spin" : ""}`} />
                {t("refresh")}
              </Button>

              <div className="ml-auto flex items-center gap-2">
                <Select value={exportFormat} onValueChange={(value: any) => setExportFormat(value)}>
                  <SelectTrigger className="w-28 h-8 text-xs bg-white rounded-lg">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="csv">CSV</SelectItem>
                    <SelectItem value="excel">Excel</SelectItem>
                    <SelectItem value="pdf">PDF</SelectItem>
                  </SelectContent>
                </Select>
                <Button
                  size="sm"
                  onClick={handleExport}
                  disabled={isExporting || filteredAndSortedData.length === 0}
                >
                  {isExporting ? (
                    <RefreshCw className="h-4 w-4 mr-1.5 animate-spin" />
                  ) : (
                    <Download className="h-4 w-4 mr-1.5" />
                  )}
                  {t("export.button")}
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Dynamic AI View - shown when AI search is active */}
        {dynamicQuery ? (
          <DynamicDataView
            query={dynamicQuery}
            onBack={() => {
              setDynamicQuery(null);
              setSearchQuery("");
            }}
          />
        ) : (
          <>
            {/* Filters Panel */}
            {showFilters && (
              <Card className="animate-fade-in">
                <CardHeader className="pb-4">
                  <h3 className="text-sm font-semibold text-foreground">{t("filters.title")}</h3>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                    {/* Sectors */}
                    <div>
                      <Label className="mb-2 block text-xs font-medium uppercase tracking-wider text-muted-foreground">
                        {t("filters.sectors")}
                      </Label>
                      <div className="space-y-2 max-h-40 overflow-y-auto">
                        {SECTORS.map((sector) => (
                          <div key={sector.id} className="flex items-center space-x-2">
                            <Checkbox
                              id={`sector-${sector.id}`}
                              checked={selectedSectors.includes(sector.id)}
                              onCheckedChange={() => toggleSector(sector.id)}
                            />
                            <Label htmlFor={`sector-${sector.id}`} className="text-sm cursor-pointer">
                              {getSectorName(sector.id)}
                            </Label>
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* Wilayas */}
                    <div>
                      <Label className="mb-2 block text-xs font-medium uppercase tracking-wider text-muted-foreground">
                        {t("filters.wilayas")}
                      </Label>
                      <div className="space-y-2 max-h-40 overflow-y-auto">
                        {WILAYAS.map((wilaya) => (
                          <div key={wilaya.code} className="flex items-center space-x-2">
                            <Checkbox
                              id={`wilaya-${wilaya.code}`}
                              checked={selectedWilayas.includes(wilaya.code)}
                              onCheckedChange={() => toggleWilaya(wilaya.code)}
                            />
                            <Label htmlFor={`wilaya-${wilaya.code}`} className="text-sm cursor-pointer">
                              {getWilayaName(wilaya.code)}
                            </Label>
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* Metrics */}
                    <div>
                      <Label className="mb-2 block text-xs font-medium uppercase tracking-wider text-muted-foreground">
                        {t("filters.metrics")}
                      </Label>
                      <div className="space-y-2">
                        {METRICS.map((metric) => (
                          <div key={metric.id} className="flex items-center space-x-2">
                            <Checkbox
                              id={`metric-${metric.id}`}
                              checked={selectedMetrics.includes(metric.id)}
                              onCheckedChange={() => toggleMetric(metric.id)}
                            />
                            <Label htmlFor={`metric-${metric.id}`} className="text-sm cursor-pointer">
                              {getMetricName(metric.id)}
                            </Label>
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* Year Range */}
                    <div>
                      <Label className="mb-2 block text-xs font-medium uppercase tracking-wider text-muted-foreground">
                        {t("filters.yearRange")}
                      </Label>
                      <div className="space-y-3">
                        <div>
                          <Label htmlFor="year-start" className="text-xs text-muted-foreground">{t("filters.from")}</Label>
                          <Select value={String(yearRange.start)} onValueChange={(v) => setYearRange((p) => ({ ...p, start: parseInt(v) }))}>
                            <SelectTrigger id="year-start" className="bg-white">
                              <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                              {Array.from({ length: 20 }, (_, i) => 2005 + i).map((year) => (
                                <SelectItem key={year} value={String(year)}>{year}</SelectItem>
                              ))}
                            </SelectContent>
                          </Select>
                        </div>
                        <div>
                          <Label htmlFor="year-end" className="text-xs text-muted-foreground">{t("filters.to")}</Label>
                          <Select value={String(yearRange.end)} onValueChange={(v) => setYearRange((p) => ({ ...p, end: parseInt(v) }))}>
                            <SelectTrigger id="year-end" className="bg-white">
                              <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                              {Array.from({ length: 20 }, (_, i) => 2005 + i).map((year) => (
                                <SelectItem key={year} value={String(year)}>{year}</SelectItem>
                              ))}
                            </SelectContent>
                          </Select>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="mt-5 flex justify-end gap-2">
                    <Button variant="outline" size="sm" onClick={clearFilters}>
                      {t("filters.clear")}
                    </Button>
                    <Button size="sm" onClick={fetchData} disabled={isLoading}>
                      {t("filters.apply")}
                    </Button>
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Stats Cards */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <StatCard
                icon={<FileText className="h-4 w-4 text-emerald-600" />}
                label={t("stats.totalRecords")}
                value={filteredAndSortedData.length.toLocaleString()}
              />
              <StatCard
                icon={<MapPin className="h-4 w-4 text-teal-600" />}
                label={t("stats.wilayas")}
                value={String(new Set(filteredAndSortedData.map((d) => d.wilaya)).size)}
              />
              <StatCard
                icon={<Database className="h-4 w-4 text-amber-600" />}
                label={t("stats.sectors")}
                value={String(new Set(filteredAndSortedData.map((d) => d.sector)).size)}
              />
              <StatCard
                icon={<Calendar className="h-4 w-4 text-blue-600" />}
                label={t("stats.years")}
                value={String(yearRange.end - yearRange.start + 1)}
              />
            </div>

            {/* Charts */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card>
                <CardHeader className="pb-2">
                  <h3 className="text-sm font-semibold text-foreground">{t("charts.sectorDistribution")}</h3>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={260}>
                    <BarChart
                      data={SECTORS.map((s) => ({
                        name: getSectorName(s.id),
                        value: filteredAndSortedData.filter((d) => d.sector === s.id).reduce((sum, d) => sum + d.value, 0),
                      }))}
                    >
                      <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" vertical={false} />
                      <XAxis dataKey="name" tick={{ fontSize: 11, fill: "#6b7280" }} axisLine={{ stroke: "#e5e7eb" }} />
                      <YAxis tick={{ fontSize: 11, fill: "#6b7280" }} axisLine={{ stroke: "#e5e7eb" }} />
                      <Tooltip contentStyle={{ borderRadius: "12px", border: "1px solid #e5e7eb", boxShadow: "0 4px 6px -1px rgba(0,0,0,0.1)" }} />
                      <Bar dataKey="value" fill="#059669" radius={[6, 6, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="pb-2">
                  <h3 className="text-sm font-semibold text-foreground">{t("charts.yearTrend")}</h3>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={260}>
                    <LineChart
                      data={Array.from({ length: yearRange.end - yearRange.start + 1 }, (_, i) => ({
                        year: yearRange.start + i,
                        value: filteredAndSortedData.filter((d) => d.year === yearRange.start + i).reduce((sum, d) => sum + d.value, 0),
                      }))}
                    >
                      <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" vertical={false} />
                      <XAxis dataKey="year" tick={{ fontSize: 11, fill: "#6b7280" }} axisLine={{ stroke: "#e5e7eb" }} />
                      <YAxis tick={{ fontSize: 11, fill: "#6b7280" }} axisLine={{ stroke: "#e5e7eb" }} />
                      <Tooltip contentStyle={{ borderRadius: "12px", border: "1px solid #e5e7eb", boxShadow: "0 4px 6px -1px rgba(0,0,0,0.1)" }} />
                      <Line type="monotone" dataKey="value" stroke="#059669" strokeWidth={2.5} dot={{ fill: "#059669", r: 3 }} />
                    </LineChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            </div>

            {/* Data Table */}
            <Card>
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-sm font-semibold text-foreground">{t("table.title")}</h3>
                    <CardDescription className="mt-0.5">
                      {filteredAndSortedData.length} {t("table.records")}
                    </CardDescription>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="p-0">
                {isLoading ? (
                  <div className="text-center py-12">
                    <RefreshCw className="h-6 w-6 animate-spin mx-auto mb-3 text-muted-foreground" />
                    <p className="text-sm text-muted-foreground">{t("loading")}</p>
                  </div>
                ) : error ? (
                  <div className="text-center py-12">
                    <p className="text-destructive mb-3 text-sm">{error}</p>
                    <Button size="sm" onClick={fetchData}>Retry</Button>
                  </div>
                ) : (
                  <div className="overflow-x-auto">
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead className="w-10">
                            <Checkbox />
                          </TableHead>
                          {[
                            { id: "wilayaName", label: t("columns.wilaya") },
                            { id: "sectorName", label: t("columns.sector") },
                            { id: "metricName", label: t("columns.metric") },
                            { id: "year", label: t("columns.year") },
                            { id: "value", label: t("columns.value") },
                            { id: "unit", label: t("columns.unit") },
                          ].map((col) => (
                            <TableHead
                              key={col.id}
                              className="cursor-pointer hover:text-foreground transition-colors"
                              onClick={() => handleSort(col.id)}
                            >
                              <div className="flex items-center gap-1">
                                {col.label}
                                {sortColumn === col.id && (
                                  <span className="text-primary">
                                    {sortDirection === "asc" ? "↑" : "↓"}
                                  </span>
                                )}
                              </div>
                            </TableHead>
                          ))}
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {filteredAndSortedData.slice(0, 50).map((row) => (
                          <TableRow key={row.id}>
                            <TableCell>
                              <Checkbox />
                            </TableCell>
                            <TableCell className="font-medium">{row.wilayaName}</TableCell>
                            <TableCell>{row.sectorName}</TableCell>
                            <TableCell>{row.metricName}</TableCell>
                            <TableCell>{row.year}</TableCell>
                            <TableCell className="font-medium tabular-nums">
                              {row.value.toLocaleString()}
                            </TableCell>
                            <TableCell>
                              <span className="badge-active">{row.unit}</span>
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                    {filteredAndSortedData.length > 50 && (
                      <div className="px-4 py-3 text-xs text-muted-foreground border-t border-gray-100 bg-gray-50/50">
                        Showing 50 of {filteredAndSortedData.length.toLocaleString()} records
                      </div>
                    )}
                  </div>
                )}
              </CardContent>
            </Card>
          </>
        )}
      </div>
    </DashboardLayout>
  );
}

function StatCard({
  icon,
  label,
  value,
}: {
  icon: React.ReactNode;
  label: string;
  value: string;
}) {
  return (
    <Card>
      <CardContent className="p-4">
        <div className="flex items-center gap-2 mb-1.5">
          {icon}
          <span className="text-xs text-muted-foreground">{label}</span>
        </div>
        <div className="text-xl font-bold text-foreground">{value}</div>
      </CardContent>
    </Card>
  );
}
