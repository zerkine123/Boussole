"use client";

import { useEffect, useState } from "react";
import { Card, CardHeader, CardContent, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { FunnelChart, Funnel, Tooltip, ResponsiveContainer, LabelList, Cell } from "recharts";
import api from "@/lib/api";
import { useDashboardFilters } from "@/lib/DashboardFilterContext";

const COLORS = ['#3b82f6', '#0ea5e9', '#06b6d4', '#14b8a6', '#10b981'];

export function DynamicFunnelChart({ metric_slugs, title, filters: widgetFilters }: any) {
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

                // We want national totals for each metric step in the funnel, no group_by needed unless filtering
                const response = await api.queryData(token, {
                    metric_slugs: activeMetrics,
                    filters: { ...widgetFilters, ...globalFilters }
                });

                if (response?.data) {
                    const aggregated: Record<string, number> = {};

                    // Aggregate totals per metric slug
                    response.data.forEach((row: any) => {
                        const key = row.slug || "Unknown";
                        if (!aggregated[key]) aggregated[key] = 0;
                        aggregated[key] += (row.value || 0);
                    });

                    // Order the funnel according to the original metric_slugs array order (important for pipelines!)
                    const chartData = activeMetrics.map(slug => ({
                        name: slug.split('_').map((w: string) => w.charAt(0).toUpperCase() + w.slice(1)).join(' '),
                        value: aggregated[slug] || 0
                    })).filter(item => item.value > 0);

                    // Ensure it is strictly descending for a proper funnel shape if it's a true conversion funnel
                    // chartData.sort((a, b) => b.value - a.value); // Optional: forces funnel shape even if steps are out of order

                    setData(chartData);
                }
            } catch (err) {
                console.error("Failed to fetch Funnel data:", err);
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
                <CardContent>
                    <Skeleton className="h-[250px] w-full" />
                </CardContent>
            </Card>
        );
    }

    return (
        <Card className="h-full">
            <CardHeader className="pb-2">
                <CardTitle className="text-lg font-semibold">{title || "Conversion Pipeline"}</CardTitle>
            </CardHeader>
            <CardContent>
                <div className="h-[250px] w-full mt-4">
                    {data.length === 0 ? (
                        <div className="h-full flex items-center justify-center text-sm text-center text-muted-foreground border border-dashed rounded-md bg-accent/30 px-4">
                            Pipeline chart needs an array of sequentially shrinking metrics.
                        </div>
                    ) : (
                        <ResponsiveContainer width="100%" height="100%">
                            <FunnelChart>
                                <Tooltip
                                    contentStyle={{ borderRadius: "8px", border: "none", boxShadow: "0 4px 6px -1px rgb(0 0 0 / 0.1)" }}
                                />
                                <Funnel
                                    dataKey="value"
                                    data={data}
                                    isAnimationActive
                                >
                                    <LabelList position="right" fill="#6b7280" stroke="none" dataKey="name" fontSize={12} />
                                    {data.map((entry, index) => (
                                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                    ))}
                                </Funnel>
                            </FunnelChart>
                        </ResponsiveContainer>
                    )}
                </div>
            </CardContent>
        </Card>
    );
}
