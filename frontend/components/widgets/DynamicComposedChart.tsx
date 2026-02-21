"use client";

import { useEffect, useState } from "react";
import { Card, CardHeader, CardContent, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { ComposedChart, Line, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts";
import api from "@/lib/api";
import { useDashboardFilters } from "@/lib/DashboardFilterContext";

export function DynamicComposedChart({ metric_slugs, title, group_by = "year", limit = 10, filters: widgetFilters }: any) {
    const [data, setData] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const { filters: globalFilters } = useDashboardFilters();

    // The Composed Chart expects an array of metric slugs (usually 2 for Bar and Line)
    const activeMetrics = Array.isArray(metric_slugs) ? metric_slugs : (metric_slugs ? [metric_slugs] : []);

    useEffect(() => {
        if (activeMetrics.length === 0) return;

        async function fetchData() {
            try {
                setLoading(true);
                const token = localStorage.getItem("access_token");

                const response = await api.queryData(token, {
                    metric_slugs: activeMetrics,
                    group_by,
                    filters: { ...widgetFilters, ...globalFilters }
                });

                if (response?.data) {
                    // Pivot data around the group_by axis
                    // Output format: { name: '2023', metric1: 100, metric2: 500 }
                    const aggregated: Record<string, any> = {};

                    response.data.forEach((row: any) => {
                        let key = 'Unknown';
                        if (group_by === 'sector') key = row.sector_name || 'Unknown';
                        else if (group_by === 'wilaya') key = row.wilaya_name || 'Unknown';
                        else if (group_by === 'year') key = row.year ? row.year.toString() : 'Unknown';

                        if (!aggregated[key]) aggregated[key] = { name: key };

                        // Add the metric value to this row. Assuming the API returns `slug` or `metric_slug` or we match by `name_en`
                        // Ensure your API returns 'slug' per row when querying multiple metrics
                        const metricKey = row.slug || "Value";
                        if (!aggregated[key][metricKey]) aggregated[key][metricKey] = 0;
                        aggregated[key][metricKey] += (row.value || 0);
                    });

                    let chartData = Object.values(aggregated);

                    // Sort
                    if (group_by === 'year') {
                        chartData.sort((a: any, b: any) => parseFloat(a.name) - parseFloat(b.name));
                    } else {
                        // Sort by the first metric descending
                        const primaryMetric = activeMetrics[0] || "Value";
                        chartData.sort((a: any, b: any) => (b[primaryMetric] || 0) - (a[primaryMetric] || 0));
                    }

                    if (limit && limit > 0) {
                        chartData = chartData.slice(0, limit);
                    }

                    setData(chartData);
                }
            } catch (err) {
                console.error("Failed to fetch ComposedChart data:", err);
            } finally {
                setLoading(false);
            }
        }
        fetchData();
    }, [JSON.stringify(activeMetrics), group_by, limit, widgetFilters, globalFilters]);

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

    const primaryMetric = activeMetrics[0];
    const secondaryMetric = activeMetrics[1];

    return (
        <Card className="h-full">
            <CardHeader className="pb-2">
                <CardTitle className="text-lg font-semibold">{title || "Comparative Analysis"}</CardTitle>
            </CardHeader>
            <CardContent>
                <div className="h-[250px] w-full mt-4">
                    {data.length === 0 || activeMetrics.length < 2 ? (
                        <div className="h-full flex items-center justify-center text-sm text-center text-muted-foreground border border-dashed rounded-md bg-accent/30 px-4">
                            Composed charts require at least 2 metric slugs to compare (e.g. Volume vs. Value).
                        </div>
                    ) : (
                        <ResponsiveContainer width="100%" height="100%">
                            <ComposedChart data={data}>
                                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e5e7eb" />
                                <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: "#6b7280" }} />

                                {/* Left Y-Axis for Primary Metric (Bar) */}
                                <YAxis yAxisId="left" axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: "#6b7280" }} />

                                {/* Right Y-Axis for Secondary Metric (Line) */}
                                <YAxis yAxisId="right" orientation="right" axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: "#6b7280" }} />

                                <Tooltip
                                    cursor={{ fill: "transparent" }}
                                    contentStyle={{ borderRadius: "8px", border: "none", boxShadow: "0 4px 6px -1px rgb(0 0 0 / 0.1)" }}
                                />
                                <Legend verticalAlign="bottom" height={36} wrapperStyle={{ fontSize: '12px' }} />

                                <Bar yAxisId="left" name={primaryMetric} dataKey={primaryMetric} fill="#3b82f6" radius={[4, 4, 0, 0]} barSize={32} />
                                <Line yAxisId="right" name={secondaryMetric} type="monotone" dataKey={secondaryMetric} stroke="#f59e0b" strokeWidth={3} dot={{ r: 4, fill: "#f59e0b" }} activeDot={{ r: 6 }} />
                            </ComposedChart>
                        </ResponsiveContainer>
                    )}
                </div>
            </CardContent>
        </Card>
    );
}
