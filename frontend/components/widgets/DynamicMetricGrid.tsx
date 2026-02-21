"use client";

import { useEffect, useState } from "react";
import { Card, CardHeader, CardContent, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Activity, LayoutGrid } from "lucide-react";
import api from "@/lib/api";
import { useDashboardFilters } from "@/lib/DashboardFilterContext";

export function DynamicMetricGrid({ metric_slugs, title, filters: widgetFilters }: any) {
    const [data, setData] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const { filters: globalFilters } = useDashboardFilters();

    const activeMetrics = Array.isArray(metric_slugs) ? metric_slugs : (metric_slugs ? [metric_slugs] : []);

    useEffect(() => {
        if (activeMetrics.length === 0) return;

        async function fetchData() {
            try {
                setLoading(true);
                const token = localStorage.getItem("access_token");

                // Get national totals for each metric slug requested (e.g. ['startups', 'incubators', 'revenue', 'jobs'])
                const response = await api.queryData(token, {
                    metric_slugs: activeMetrics,
                    filters: { ...widgetFilters, ...globalFilters }
                });

                if (response?.data) {
                    const aggregated: Record<string, number> = {};

                    response.data.forEach((row: any) => {
                        const key = row.slug || "Unknown";
                        if (!aggregated[key]) aggregated[key] = 0;
                        aggregated[key] += (row.value || 0);
                    });

                    // Format it as an array of KPIs
                    const chartData = activeMetrics.map(slug => ({
                        name: slug.split('_').map((w: string) => w.charAt(0).toUpperCase() + w.slice(1)).join(' '),
                        value: aggregated[slug] || 0
                    }));

                    setData(chartData);
                }
            } catch (err) {
                console.error("Failed to fetch Metric Grid data:", err);
            } finally {
                setLoading(false);
            }
        }
        fetchData();
    }, [JSON.stringify(activeMetrics), widgetFilters, globalFilters]);

    if (loading) {
        return (
            <Card className="h-full">
                <CardHeader>
                    <Skeleton className="h-5 w-1/3" />
                </CardHeader>
                <CardContent className="grid grid-cols-2 gap-4">
                    <Skeleton className="h-20 w-full" />
                    <Skeleton className="h-20 w-full" />
                    <Skeleton className="h-20 w-full" />
                    <Skeleton className="h-20 w-full" />
                </CardContent>
            </Card>
        );
    }

    return (
        <Card className="h-full">
            <CardHeader className="pb-2 flex flex-row items-center justify-between">
                <CardTitle className="text-sm font-semibold text-foreground">
                    {title || "KPI Snapshot Grid"}
                </CardTitle>
                <LayoutGrid className="w-4 h-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
                {data.length === 0 ? (
                    <div className="text-sm text-center text-muted-foreground mt-4 border border-dashed rounded p-4 bg-accent/30">
                        Provide a list of metrics to populate the grid.
                    </div>
                ) : (
                    <div className="grid grid-cols-2 gap-3 mt-2">
                        {data.map((item, index) => (
                            <div key={index} className="flex flex-col bg-accent/30 dark:bg-accent/10 border p-3 rounded-lg hover:bg-accent/50 transition-colors">
                                <span className="text-xs font-medium text-muted-foreground mb-1 line-clamp-1" title={item.name}>
                                    {item.name}
                                </span>
                                <span className="text-xl font-bold text-foreground">
                                    {item.value.toLocaleString()}
                                </span>
                            </div>
                        ))}
                    </div>
                )}
            </CardContent>
        </Card>
    );
}
