"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
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
} from "lucide-react";
import { generateReportPdf } from "@/lib/generateReportPdf";
import { api } from "@/lib/api";

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

// ========================
// Widget Components
// ========================

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
            default:
                return null;
        }
    };

    // Group charts side by side
    const chartWidgets = layout.widgets.filter(
        (w) => w.type === "bar_chart" || w.type === "line_chart"
    );
    const otherWidgets = layout.widgets.filter(
        (w) => w.type !== "bar_chart" && w.type !== "line_chart"
    );

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
