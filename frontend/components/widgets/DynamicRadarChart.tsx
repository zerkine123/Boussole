"use client";

import { useEffect, useState } from "react";
import { Card, CardHeader, CardContent, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer, Tooltip } from "recharts";
import api from "@/lib/api";
import { useDashboardFilters } from "@/lib/DashboardFilterContext";

export function DynamicRadarChart({ metric_slug, title, group_by = "sector", limit = 6, filters: widgetFilters }: any) {
    const [data, setData] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const { filters: globalFilters } = useDashboardFilters();

    useEffect(() => {
        async function fetchData() {
            try {
                setLoading(true);
                const token = localStorage.getItem("access_token");

                const response = await api.queryData(token, {
                    metric_slugs: [metric_slug],
                    group_by,
                    filters: { ...widgetFilters, ...globalFilters }
                });

                if (response?.data) {
                    const aggregated: Record<string, number> = {};

                    response.data.forEach((row: any) => {
                        let key = 'Unknown';
                        if (group_by === 'sector') key = row.sector_name || 'Unknown';
                        else if (group_by === 'wilaya') key = row.wilaya_name || 'Unknown';
                        else if (group_by === 'year') key = row.year ? row.year.toString() : 'Unknown';

                        if (!aggregated[key]) aggregated[key] = 0;
                        aggregated[key] += (row.value || 0);
                    });

                    let chartData = Object.entries(aggregated).map(([name, value]) => ({ subject: name, value }));

                    // Sort descending and apply limit. Radar looks best with <= 8 points.
                    chartData.sort((a, b) => b.value - a.value);
                    if (limit && limit > 0) {
                        chartData = chartData.slice(0, limit > 8 ? 8 : limit);
                    }

                    setData(chartData);
                }
            } catch (err) {
                console.error("Failed to fetch RadarChart data:", err);
            } finally {
                setLoading(false);
            }
        }
        fetchData();
    }, [metric_slug, group_by, limit, widgetFilters, globalFilters]);

    if (loading) {
        return (
            <Card className="h-full">
                <CardHeader>
                    <Skeleton className="h-5 w-1/3" />
                </CardHeader>
                <CardContent>
                    <Skeleton className="h-[250px] w-full rounded-full" />
                </CardContent>
            </Card>
        );
    }

    return (
        <Card className="h-full">
            <CardHeader className="pb-2">
                <CardTitle className="text-lg font-semibold">{title || "Performance Profile"}</CardTitle>
            </CardHeader>
            <CardContent>
                <div className="h-[250px] w-full mt-4">
                    {data.length < 3 ? (
                        <div className="h-full flex items-center justify-center text-sm text-muted-foreground border border-dashed rounded-md bg-accent/30 text-center px-4">
                            Radar charts require at least 3 distinct data points to render. Try grouping by Sector or Wilaya.
                        </div>
                    ) : (
                        <ResponsiveContainer width="100%" height="100%">
                            <RadarChart cx="50%" cy="50%" outerRadius="70%" data={data}>
                                <PolarGrid stroke="#e5e7eb" />
                                <PolarAngleAxis dataKey="subject" tick={{ fontSize: 11, fill: '#6b7280' }} />
                                <PolarRadiusAxis angle={30} domain={[0, 'dataMax']} tick={false} axisLine={false} />
                                <Radar
                                    name={title || "Value"}
                                    dataKey="value"
                                    stroke="#8b5cf6"
                                    fill="#8b5cf6"
                                    fillOpacity={0.5}
                                />
                                <Tooltip
                                    contentStyle={{ borderRadius: "8px", border: "none", boxShadow: "0 4px 6px -1px rgb(0 0 0 / 0.1)" }}
                                />
                            </RadarChart>
                        </ResponsiveContainer>
                    )}
                </div>
            </CardContent>
        </Card>
    );
}
