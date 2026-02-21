"use client";

import { useEffect, useState } from "react";
import { Card, CardHeader, CardContent, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { History } from "lucide-react";
import api from "@/lib/api";
import { useDashboardFilters } from "@/lib/DashboardFilterContext";

export function DynamicSentimentTimeline({ metric_slug, title, limit = 5, filters: widgetFilters }: any) {
    const [data, setData] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const { filters: globalFilters } = useDashboardFilters();

    useEffect(() => {
        if (!metric_slug) return;

        async function fetchData() {
            try {
                setLoading(true);
                const token = localStorage.getItem("access_token");

                // We want to see how a specific metric evolved over time (grouped by year)
                const response = await api.queryData(token, {
                    metric_slugs: [metric_slug],
                    group_by: "year",
                    filters: { ...widgetFilters, ...globalFilters }
                });

                if (response?.data) {
                    const aggregated: Record<string, number> = {};

                    response.data.forEach((row: any) => {
                        const year = row.year ? row.year.toString() : "Unknown";
                        if (!aggregated[year]) aggregated[year] = 0;
                        aggregated[year] += (row.value || 0);
                    });

                    // Format as timeline events
                    let chartData = Object.entries(aggregated).map(([year, value]) => ({
                        year: year === 'null' ? 'Historical' : year,
                        value,
                        yoy: 0 // Will calculate below
                    }));

                    // Sort chronologically ascending to calculate YoY, then reverse for timeline display (newest first)
                    chartData.sort((a, b) => {
                        const yrA = parseInt(a.year) || 0;
                        const yrB = parseInt(b.year) || 0;
                        return yrA - yrB;
                    });

                    // Calculate Year over Year
                    for (let i = 1; i < chartData.length; i++) {
                        const prev = chartData[i - 1].value;
                        const curr = chartData[i].value;
                        if (prev > 0) {
                            chartData[i].yoy = ((curr - prev) / prev) * 100;
                        }
                    }

                    // Reverse to show newest at the top
                    chartData.reverse();

                    if (limit && limit > 0) {
                        chartData = chartData.slice(0, limit);
                    }

                    setData(chartData);
                }
            } catch (err) {
                console.error("Failed to fetch Timeline data:", err);
            } finally {
                setLoading(false);
            }
        }
        fetchData();
    }, [metric_slug, limit, widgetFilters, globalFilters]);

    if (loading) {
        return (
            <Card className="h-full">
                <CardHeader>
                    <Skeleton className="h-5 w-1/3" />
                </CardHeader>
                <CardContent className="space-y-6 pt-4">
                    <div className="flex gap-4"><Skeleton className="h-4 w-4 rounded-full" /><Skeleton className="h-12 w-full" /></div>
                    <div className="flex gap-4"><Skeleton className="h-4 w-4 rounded-full" /><Skeleton className="h-12 w-full" /></div>
                    <div className="flex gap-4"><Skeleton className="h-4 w-4 rounded-full" /><Skeleton className="h-12 w-full" /></div>
                </CardContent>
            </Card>
        );
    }

    return (
        <Card className="h-full border-t-4 border-slate-700/50">
            <CardHeader className="pb-2 flex flex-row items-center justify-between">
                <CardTitle className="text-sm font-semibold text-foreground">
                    {title || "Historical Timeline"}
                </CardTitle>
                <History className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent className="pt-4">
                {data.length === 0 ? (
                    <div className="text-sm text-center text-muted-foreground mt-4 border border-dashed rounded p-4 bg-accent/30">
                        Insufficient historical data for a timeline.
                    </div>
                ) : (
                    <div className="relative border-l border-muted-foreground/20 ml-3 pl-6 space-y-6">
                        {data.map((item, index) => {
                            const isPositive = item.yoy > 0;
                            const isNegative = item.yoy < 0;
                            const isNeutral = item.yoy === 0;

                            const dotColor = isPositive
                                ? "bg-emerald-500 border-emerald-200 dark:border-emerald-900"
                                : isNegative
                                    ? "bg-red-500 border-red-200 dark:border-red-900"
                                    : "bg-blue-500 border-blue-200 dark:border-blue-900";

                            return (
                                <div key={index} className="relative">
                                    <div className={`absolute -left-[31px] w-4 h-4 rounded-full border-4 bg-background z-10 ${dotColor}`} />
                                    <div className="flex flex-col">
                                        <span className="text-xs font-bold text-muted-foreground uppercase tracking-wider mb-1">
                                            {item.year}
                                        </span>
                                        <div className="bg-accent/40 rounded-md p-3 border">
                                            <p className="font-semibold text-sm">
                                                Recorded {item.value.toLocaleString()} units
                                            </p>

                                            {index < data.length - 1 && item.yoy !== 0 && (
                                                <p className={`text-xs mt-1 font-medium ${isPositive ? 'text-emerald-600' : 'text-red-600'}`}>
                                                    {isPositive ? "↑ Increased" : "↓ Decreased"} by {Math.abs(item.yoy).toFixed(1)}% vs previous
                                                </p>
                                            )}
                                            {index === data.length - 1 && (
                                                <p className="text-xs mt-1 font-medium text-muted-foreground">
                                                    Baseline established
                                                </p>
                                            )}
                                        </div>
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                )}
            </CardContent>
        </Card>
    );
}
