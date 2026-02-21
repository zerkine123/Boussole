"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
    BarChart,
    Bar,
    LineChart,
    Line,
    PieChart,
    Pie,
    RadarChart,
    Radar,
    PolarGrid,
    PolarAngleAxis,
    PolarRadiusAxis,
    XAxis,
    YAxis,
    Tooltip,
    ResponsiveContainer,
    CartesianGrid,
    Legend,
    Cell,
} from "recharts";
import {
    TrendingUp,
    TrendingDown,
    Minus,
    Lightbulb,
    ArrowLeft,
    Sparkles,
    Download,
    MapPin,
    Gauge,
    Trophy,
    Table2,
} from "lucide-react";
import { generateReportPdf } from "@/lib/generateReportPdf";
import { api } from "@/lib/api";
import dynamic from "next/dynamic";

const CompetitorMapWidget = dynamic(
    () => import("./widgets/CompetitorMapWidget"),
    { ssr: false, loading: () => <p className="h-[400px] flex items-center justify-center text-muted-foreground">Loading Map...</p> }
);

const FinancialSimulatorWidget = dynamic(
    () => import("./widgets/FinancialSimulatorWidget").then(mod => mod.FinancialSimulatorWidget),
    { ssr: false, loading: () => <p className="h-[400px] flex items-center justify-center text-muted-foreground">Loading Simulator...</p> }
);

// Color palette for charts
const CHART_COLORS = [
    "#059669",
    "#0ea5e9",
    "#8b5cf6",
    "#f59e0b",
    "#ef4444",
    "#ec4899",
    "#14b8a6",
    "#6366f1",
];

const PIE_COLORS = ["#059669", "#0ea5e9", "#8b5cf6", "#f59e0b", "#ef4444", "#ec4899", "#14b8a6", "#6366f1"];

// ========================
// Widget Components
// ========================

// ---------- Table Widget ----------
function DataTableWidget({
    title,
    data,
    config,
}: {
    title: string;
    data: Array<Record<string, any>>;
    config?: Record<string, any>;
}) {
    if (!data || data.length === 0) return null;
    const columns = Object.keys(data[0]);
    return (
        <Card className="overflow-hidden">
            <CardHeader className="pb-3">
                <div className="flex items-center gap-2">
                    <Table2 className="h-4 w-4 text-primary" />
                    <h3 className="font-semibold text-sm">{title}</h3>
                </div>
            </CardHeader>
            <CardContent className="p-0">
                <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                        <thead>
                            <tr className="border-b bg-muted/50">
                                {columns.map((col) => (
                                    <th key={col} className="px-4 py-2.5 text-left font-medium text-muted-foreground capitalize">
                                        {col.replace(/_/g, " ")}
                                    </th>
                                ))}
                            </tr>
                        </thead>
                        <tbody>
                            {data.slice(0, config?.rows_per_page || 10).map((row, i) => (
                                <tr key={i} className="border-b last:border-0 hover:bg-muted/30 transition-colors">
                                    {columns.map((col) => (
                                        <td key={col} className="px-4 py-2.5">
                                            {typeof row[col] === "number"
                                                ? row[col].toLocaleString()
                                                : String(row[col] ?? "-")}
                                        </td>
                                    ))}
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </CardContent>
        </Card>
    );
}

// ---------- Pie Chart Widget ----------
function PieChartWidget({
    title,
    data,
}: {
    title: string;
    data: Array<{ name: string; value: number }>;
}) {
    if (!data || data.length === 0) return null;
    return (
        <Card>
            <CardHeader className="pb-2">
                <h3 className="font-semibold text-sm">{title}</h3>
            </CardHeader>
            <CardContent>
                <ResponsiveContainer width="100%" height={280}>
                    <PieChart>
                        <Pie
                            data={data}
                            dataKey="value"
                            nameKey="name"
                            cx="50%"
                            cy="50%"
                            outerRadius={100}
                            label={({ name, percent }) =>
                                `${name} ${(percent * 100).toFixed(0)}%`
                            }
                            labelLine={false}
                        >
                            {data.map((_, i) => (
                                <Cell key={i} fill={PIE_COLORS[i % PIE_COLORS.length]} />
                            ))}
                        </Pie>
                        <Tooltip
                            formatter={(v: number) => v.toLocaleString()}
                            contentStyle={{
                                borderRadius: "8px",
                                border: "1px solid #e5e7eb",
                                boxShadow: "0 2px 8px rgba(0,0,0,0.08)",
                            }}
                        />
                        <Legend />
                    </PieChart>
                </ResponsiveContainer>
            </CardContent>
        </Card>
    );
}

// ---------- Radar Chart Widget ----------
function RadarChartWidget({
    title,
    data,
}: {
    title: string;
    data: Array<{ subject: string; value: number; fullMark?: number }>;
}) {
    if (!data || data.length === 0) return null;
    return (
        <Card>
            <CardHeader className="pb-2">
                <h3 className="font-semibold text-sm">{title}</h3>
            </CardHeader>
            <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                    <RadarChart data={data}>
                        <PolarGrid strokeDasharray="3 3" />
                        <PolarAngleAxis dataKey="subject" tick={{ fontSize: 12 }} />
                        <PolarRadiusAxis angle={30} domain={[0, 100]} tick={{ fontSize: 10 }} />
                        <Radar
                            name="Score"
                            dataKey="value"
                            stroke="#059669"
                            fill="#059669"
                            fillOpacity={0.3}
                        />
                        <Tooltip />
                    </RadarChart>
                </ResponsiveContainer>
            </CardContent>
        </Card>
    );
}

// ---------- Gauge / Score Widget ----------
function GaugeScoreWidget({
    title,
    data,
}: {
    title: string;
    data: {
        score: number;
        label?: string;
        breakdown?: Array<{ name: string; value: number }>;
    };
}) {
    if (!data) return null;
    const score = data.score ?? 0;
    const color =
        score >= 75 ? "#22c55e" : score >= 50 ? "#f59e0b" : score >= 25 ? "#f97316" : "#ef4444";
    const circumference = 2 * Math.PI * 60;
    const offset = circumference - (score / 100) * circumference;

    return (
        <Card>
            <CardHeader className="pb-2">
                <div className="flex items-center gap-2">
                    <Gauge className="h-4 w-4 text-primary" />
                    <h3 className="font-semibold text-sm">{title}</h3>
                </div>
            </CardHeader>
            <CardContent className="flex flex-col items-center">
                <div className="relative w-36 h-36">
                    <svg className="w-full h-full -rotate-90" viewBox="0 0 140 140">
                        <circle cx="70" cy="70" r="60" stroke="#e5e7eb" strokeWidth="10" fill="none" />
                        <circle
                            cx="70" cy="70" r="60"
                            stroke={color} strokeWidth="10" fill="none"
                            strokeDasharray={circumference}
                            strokeDashoffset={offset}
                            strokeLinecap="round"
                            className="transition-all duration-1000 ease-out"
                        />
                    </svg>
                    <div className="absolute inset-0 flex flex-col items-center justify-center">
                        <span className="text-3xl font-bold" style={{ color }}>{score}</span>
                        <span className="text-xs text-muted-foreground">/100</span>
                    </div>
                </div>
                {data.label && (
                    <span className="mt-2 text-sm font-medium px-3 py-1 rounded-full" style={{ backgroundColor: color + "20", color }}>
                        {data.label}
                    </span>
                )}
                {data.breakdown && data.breakdown.length > 0 && (
                    <div className="w-full mt-4 space-y-2">
                        {data.breakdown.map((item, i) => (
                            <div key={i} className="flex items-center justify-between text-xs">
                                <span className="text-muted-foreground">{item.name}</span>
                                <div className="flex items-center gap-2">
                                    <div className="w-24 h-1.5 bg-gray-100 rounded-full overflow-hidden">
                                        <div
                                            className="h-full rounded-full transition-all duration-700"
                                            style={{ width: `${item.value}%`, backgroundColor: CHART_COLORS[i % CHART_COLORS.length] }}
                                        />
                                    </div>
                                    <span className="font-medium w-8 text-right">{item.value}</span>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </CardContent>
        </Card>
    );
}

// ---------- Map Placeholder Widget ----------
function MapPlaceholderWidget({
    title,
    data,
}: {
    title: string;
    data?: { lat?: number; lon?: number; label?: string; score?: number };
}) {
    return (
        <Card>
            <CardHeader className="pb-2">
                <div className="flex items-center gap-2">
                    <MapPin className="h-4 w-4 text-primary" />
                    <h3 className="font-semibold text-sm">{title}</h3>
                </div>
            </CardHeader>
            <CardContent>
                <div className="aspect-video bg-gradient-to-br from-emerald-50 to-sky-50 rounded-xl flex flex-col items-center justify-center gap-3 border border-dashed border-emerald-200">
                    <MapPin className="h-10 w-10 text-emerald-400" />
                    {data?.label && (
                        <span className="text-sm font-medium text-emerald-700">{data.label}</span>
                    )}
                    {data?.score !== undefined && (
                        <span className="px-3 py-1 rounded-full text-xs font-medium bg-emerald-100 text-emerald-700">
                            Activity Score: {data.score}/100
                        </span>
                    )}
                    {data?.lat && data?.lon && (
                        <span className="text-xs text-muted-foreground">
                            {data.lat.toFixed(3)}°N, {data.lon.toFixed(3)}°E
                        </span>
                    )}
                </div>
            </CardContent>
        </Card>
    );
}

function HeroWidget({
    title,
    subtitle,
}: {
    title: string;
    subtitle: string;
}) {
    return (
        <div className="bg-gradient-to-r from-primary via-emerald-700 to-teal-700 rounded-2xl p-6 sm:p-8 text-white relative overflow-hidden">
            <div className="absolute inset-0">
                <div className="absolute top-[10%] left-[5%] w-48 h-48 bg-white/5 rounded-full blur-3xl" />
                <div className="absolute bottom-[10%] right-[10%] w-36 h-36 bg-white/10 rounded-full blur-3xl" />
            </div>
            <div className="relative">
                <div className="flex items-center gap-2 mb-2">
                    <Sparkles className="h-5 w-5 text-emerald-300" />
                    <span className="text-xs font-medium text-emerald-200 uppercase tracking-wider">
                        AI-Generated Analysis
                    </span>
                </div>
                <h2 className="text-2xl sm:text-3xl font-bold mb-2">{title}</h2>
                <p className="text-white/70 text-sm sm:text-base max-w-2xl">
                    {subtitle}
                </p>
            </div>
        </div>
    );
}

function KPIGridWidget({
    data,
}: {
    data: Array<{
        label: string;
        value: string;
        trend: string;
        change: string;
    }>;
}) {
    const getTrendIcon = (trend: string) => {
        switch (trend) {
            case "up":
                return <TrendingUp className="h-4 w-4 text-emerald-500" />;
            case "down":
                return <TrendingDown className="h-4 w-4 text-red-500" />;
            default:
                return <Minus className="h-4 w-4 text-gray-400" />;
        }
    };

    const getTrendColor = (trend: string) => {
        switch (trend) {
            case "up":
                return "text-emerald-600 bg-emerald-50";
            case "down":
                return "text-red-600 bg-red-50";
            default:
                return "text-gray-600 bg-gray-50";
        }
    };

    return (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            {data.map((kpi, i) => (
                <Card
                    key={i}
                    className="hover:shadow-md transition-shadow border-l-4"
                    style={{ borderLeftColor: CHART_COLORS[i % CHART_COLORS.length] }}
                >
                    <CardContent className="p-4">
                        <p className="text-xs text-muted-foreground font-medium uppercase tracking-wide mb-1 truncate">
                            {kpi.label}
                        </p>
                        <p className="text-xl sm:text-2xl font-bold text-foreground mb-2">
                            {kpi.value}
                        </p>
                        <div className="flex items-center gap-1.5">
                            {getTrendIcon(kpi.trend)}
                            <span
                                className={`text-xs font-medium px-1.5 py-0.5 rounded ${getTrendColor(kpi.trend)}`}
                            >
                                {kpi.change}
                            </span>
                        </div>
                    </CardContent>
                </Card>
            ))}
        </div>
    );
}

function BarChartWidget({
    title,
    data,
}: {
    title: string;
    data: Array<{ name: string; value: number }>;
}) {
    return (
        <Card>
            <CardHeader className="pb-2">
                <h3 className="text-sm font-semibold text-foreground">{title}</h3>
            </CardHeader>
            <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={data} margin={{ top: 5, right: 20, left: 10, bottom: 60 }}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                        <XAxis
                            dataKey="name"
                            tick={{ fontSize: 11 }}
                            angle={-35}
                            textAnchor="end"
                            height={60}
                        />
                        <YAxis tick={{ fontSize: 11 }} />
                        <Tooltip
                            contentStyle={{
                                borderRadius: "8px",
                                border: "1px solid #e5e7eb",
                                boxShadow: "0 4px 6px -1px rgba(0,0,0,0.1)",
                            }}
                        />
                        <Bar dataKey="value" radius={[6, 6, 0, 0]}>
                            {data.map((_, i) => (
                                <Cell
                                    key={i}
                                    fill={CHART_COLORS[i % CHART_COLORS.length]}
                                />
                            ))}
                        </Bar>
                    </BarChart>
                </ResponsiveContainer>
            </CardContent>
        </Card>
    );
}

function LineChartWidget({
    title,
    data,
}: {
    title: string;
    data: Array<{ year: number; value: number }>;
}) {
    return (
        <Card>
            <CardHeader className="pb-2">
                <h3 className="text-sm font-semibold text-foreground">{title}</h3>
            </CardHeader>
            <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                    <LineChart data={data} margin={{ top: 5, right: 20, left: 10, bottom: 5 }}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                        <XAxis dataKey="year" tick={{ fontSize: 11 }} />
                        <YAxis tick={{ fontSize: 11 }} />
                        <Tooltip
                            contentStyle={{
                                borderRadius: "8px",
                                border: "1px solid #e5e7eb",
                                boxShadow: "0 4px 6px -1px rgba(0,0,0,0.1)",
                            }}
                        />
                        <Line
                            type="monotone"
                            dataKey="value"
                            stroke="#059669"
                            strokeWidth={2.5}
                            dot={{ r: 4, fill: "#059669" }}
                            activeDot={{ r: 7, fill: "#059669" }}
                        />
                    </LineChart>
                </ResponsiveContainer>
            </CardContent>
        </Card>
    );
}

function InsightCardWidget({
    title,
    data,
}: {
    title: string;
    data: string[];
}) {
    return (
        <Card className="bg-gradient-to-br from-amber-50 to-orange-50 border-amber-200/50">
            <CardHeader className="pb-2">
                <div className="flex items-center gap-2">
                    <Lightbulb className="h-5 w-5 text-amber-500" />
                    <h3 className="text-sm font-semibold text-amber-900">{title}</h3>
                </div>
            </CardHeader>
            <CardContent>
                <ul className="space-y-2.5">
                    {data.map((insight, i) => (
                        <li key={i} className="flex gap-2 text-sm text-amber-800">
                            <span className="flex-shrink-0 h-5 w-5 rounded-full bg-amber-200/60 text-amber-700 text-xs flex items-center justify-center font-medium">
                                {i + 1}
                            </span>
                            <span>{insight}</span>
                        </li>
                    ))}
                </ul>
            </CardContent>
        </Card>
    );
}

// ========================
// Main DynamicDataView
// ========================

interface DynamicLayoutData {
    query: string;
    title: string;
    subtitle: string;
    icon: string;
    topic?: string;
    subtopic?: string;
    location?: string;
    location_name?: string;
    widgets: Array<{
        type: string;
        title?: string;
        subtitle?: string;
        data?: any;
        config?: Record<string, any>;
    }>;
}

interface DynamicDataViewProps {
    query: string;
    onBack: () => void;
}

export default function DynamicDataView({ query, onBack }: DynamicDataViewProps) {
    const [layout, setLayout] = useState<DynamicLayoutData | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    // Fetch layout on mount or when query changes
    useEffect(() => {
        const fetchLayout = async () => {
            setIsLoading(true);
            setError(null);
            try {
                const data = await api.getDynamicLayout(query);
                setLayout(data);
            } catch (err: any) {
                console.error("Layout fetch error:", err);
                setError(err.message || "Failed to generate layout");
            } finally {
                setIsLoading(false);
            }
        };

        fetchLayout();
    }, [query]);

    // Loading state
    if (isLoading) {
        return (
            <div className="space-y-6 animate-pulse">
                {/* Hero skeleton */}
                <div className="bg-gradient-to-r from-primary/20 to-emerald-600/20 rounded-2xl p-8 h-32" />
                {/* KPI skeletons */}
                <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                    {[...Array(4)].map((_, i) => (
                        <div key={i} className="bg-gray-100 rounded-xl h-24" />
                    ))}
                </div>
                {/* Chart skeletons */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                    <div className="bg-gray-100 rounded-xl h-64" />
                    <div className="bg-gray-100 rounded-xl h-64" />
                </div>
                {/* Loading text */}
                <div className="flex items-center justify-center gap-3 py-8">
                    <div className="flex gap-1.5">
                        <div className="w-2 h-2 rounded-full bg-primary animate-bounce" style={{ animationDelay: "0ms" }} />
                        <div className="w-2 h-2 rounded-full bg-primary animate-bounce" style={{ animationDelay: "150ms" }} />
                        <div className="w-2 h-2 rounded-full bg-primary animate-bounce" style={{ animationDelay: "300ms" }} />
                    </div>
                    <p className="text-sm text-muted-foreground">
                        AI is analyzing &ldquo;{query}&rdquo; and generating your data view...
                    </p>
                </div>
            </div>
        );
    }

    // Error state
    if (error || !layout) {
        return (
            <Card className="p-8 text-center">
                <p className="text-red-500 mb-4">{error || "Failed to generate layout"}</p>
                <div className="flex gap-3 justify-center">
                    <Button variant="outline" onClick={onBack}>
                        <ArrowLeft className="h-4 w-4 mr-1.5" />
                        Back to Data Explorer
                    </Button>
                </div>
            </Card>
        );
    }

    // Render widget by type
    const renderWidget = (widget: DynamicLayoutData["widgets"][0], index: number) => {
        switch (widget.type) {
            case "hero":
                return (
                    <HeroWidget
                        key={index}
                        title={widget.title || ""}
                        subtitle={widget.subtitle || ""}
                    />
                );
            case "kpi_grid":
                return <KPIGridWidget key={index} data={widget.data || []} />;
            case "bar_chart":
                return (
                    <BarChartWidget
                        key={index}
                        title={widget.title || "Chart"}
                        data={widget.data || []}
                    />
                );
            case "line_chart":
                return (
                    <LineChartWidget
                        key={index}
                        title={widget.title || "Trend"}
                        data={widget.data || []}
                    />
                );
            case "insight_card":
                return (
                    <InsightCardWidget
                        key={index}
                        title={widget.title || "Insights"}
                        data={widget.data || []}
                    />
                );
            case "table":
                return (
                    <DataTableWidget
                        key={index}
                        title={widget.title || "Data"}
                        data={widget.data || []}
                        config={widget.config}
                    />
                );
            case "pie_chart":
                return (
                    <PieChartWidget
                        key={index}
                        title={widget.title || "Distribution"}
                        data={widget.data || []}
                    />
                );
            case "radar":
                return (
                    <RadarChartWidget
                        key={index}
                        title={widget.title || "Analysis"}
                        data={widget.data || []}
                    />
                );
            case "gauge":
                return (
                    <GaugeScoreWidget
                        key={index}
                        title={widget.title || "Score"}
                        data={widget.data || { score: 0 }}
                    />
                );
            case "map":
                return (
                    <MapPlaceholderWidget
                        key={index}
                        title={widget.title || "Location"}
                        data={widget.data}
                    />
                );
            case "competitor_map":
                return (
                    <CompetitorMapWidget
                        key={index}
                        title={widget.title || "Competitor Map"}
                        data={widget.data}
                    />
                );
            case "financial_simulator":
                return (
                    <FinancialSimulatorWidget key={index} />
                );
            default:
                return null;
        }
    };

    // Group charts side by side
    const chartTypes = ["bar_chart", "line_chart", "pie_chart", "radar"];
    const chartWidgets = layout.widgets.filter((w) => chartTypes.includes(w.type));
    const otherWidgets = layout.widgets.filter((w) => !chartTypes.includes(w.type));

    return (
        <div className="space-y-6">
            {/* Back button & Export */}
            <div className="flex items-center gap-3">
                <Button
                    variant="outline"
                    size="sm"
                    onClick={onBack}
                    className="rounded-lg"
                >
                    <ArrowLeft className="h-4 w-4 mr-1.5" />
                    Back to Explorer
                </Button>
                <Button
                    size="sm"
                    onClick={() => generateReportPdf(layout)}
                    className="rounded-lg bg-gradient-to-r from-primary to-emerald-600 text-white hover:from-primary/90 hover:to-emerald-600/90"
                >
                    <Download className="h-4 w-4 mr-1.5" />
                    Export PDF
                </Button>
                <span className="text-xs text-muted-foreground ml-auto">
                    Showing AI-generated view for: &ldquo;{query}&rdquo;
                </span>
            </div>

            {/* Non-chart widgets (hero, kpi, insights) */}
            {otherWidgets.map((widget, i) => renderWidget(widget, i))}

            {/* Charts in a grid */}
            {chartWidgets.length > 0 && (
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                    {chartWidgets.map((widget, i) =>
                        renderWidget(widget, 100 + i)
                    )}
                </div>
            )}
        </div>
    );
}
