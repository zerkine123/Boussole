"use client";

import { useEffect, useState } from "react";
import { Card, CardHeader, CardContent, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ZAxis } from "recharts";
import api from "@/lib/api";
import { useDashboardFilters } from "@/lib/DashboardFilterContext";

export function DynamicScatterPlot({ metric_slugs, title, group_by = "wilaya", filters: widgetFilters }: any) {
    const [data, setData] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const { filters: globalFilters } = useDashboardFilters();

    const activeMetrics = Array.isArray(metric_slugs) ? metric_slugs : (metric_slugs ? [metric_slugs] : []);

    useEffect(() => {
        if (activeMetrics.length < 2) return;

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
                    // Output format: { name: 'Algiers', metricX: 100, metricY: 500, metricZ: (optional) }
                    const aggregated: Record<string, any> = {};

                    response.data.forEach((row: any) => {
                        let key = 'Unknown';
                        if (group_by === 'sector') key = row.sector_name || 'Unknown';
                        else if (group_by === 'wilaya') key = row.wilaya_name || 'Unknown';
                        else if (group_by === 'year') key = row.year ? row.year.toString() : 'Unknown';

                        if (!aggregated[key]) aggregated[key] = { name: key };

                        const metricKey = row.slug || "Value";
                        if (!aggregated[key][metricKey]) aggregated[key][metricKey] = 0;
                        aggregated[key][metricKey] += (row.value || 0);
                    });

                    // Only keep data points that have BOTH X and Y
                    const metricX = activeMetrics[0];
                    const metricY = activeMetrics[1];
                    const metricZ = activeMetrics[2]; // Optional 3rd metric for bubble size

                    let chartData = Object.values(aggregated).filter(item =>
                        item[metricX] !== undefined && item[metricY] !== undefined
                    );

                    setData(chartData);
                }
            } catch (err) {
                console.error("Failed to fetch ScatterPlot data:", err);
            } finally {
                setLoading(false);
            }
        }
        fetchData();
    }, [JSON.stringify(activeMetrics), group_by, widgetFilters, globalFilters]);

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

    const metricX = activeMetrics[0];
    const metricY = activeMetrics[1];
    const metricZ = activeMetrics[2];

    return (
        <Card className="h-full">
            <CardHeader className="pb-2">
                <CardTitle className="text-lg font-semibold">{title || "Correlation Analysis"}</CardTitle>
            </CardHeader>
            <CardContent>
                <div className="h-[250px] w-full mt-4">
                    {data.length === 0 || activeMetrics.length < 2 ? (
                        <div className="h-full flex items-center justify-center text-sm text-center text-muted-foreground border border-dashed rounded-md bg-accent/30 px-4">
                            Scatter plots require at least 2 metrics to find correlations (e.g. GDP vs Population).
                        </div>
                    ) : (
                        <ResponsiveContainer width="100%" height="100%">
                            <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />

                                <XAxis type="number" dataKey={metricX} name={metricX} tick={{ fontSize: 12, fill: "#6b7280" }} axisLine={false} tickLine={false} />
                                <YAxis type="number" dataKey={metricY} name={metricY} tick={{ fontSize: 12, fill: "#6b7280" }} axisLine={false} tickLine={false} />

                                {metricZ && (
                                    <ZAxis type="number" dataKey={metricZ} name={metricZ} range={[50, 400]} />
                                )}

                                <Tooltip
                                    cursor={{ strokeDasharray: '3 3' }}
                                    contentStyle={{ borderRadius: "8px", border: "none", boxShadow: "0 4px 6px -1px rgb(0 0 0 / 0.1)" }}
                                />

                                <Scatter name={title || "Distribution"} data={data} fill="#ec4899" fillOpacity={0.6} />
                            </ScatterChart>
                        </ResponsiveContainer>
                    )}
                </div>
            </CardContent>
        </Card>
    );
}
