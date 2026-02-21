"use client";

import { useEffect, useState } from "react";
import { Card, CardHeader, CardContent, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Treemap, ResponsiveContainer, Tooltip } from "recharts";
import api from "@/lib/api";
import { useDashboardFilters } from "@/lib/DashboardFilterContext";

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#14b8a6', '#f97316'];

const CustomizedContent = (props: any) => {
    const { root, depth, x, y, width, height, index, name, value, colors } = props;

    return (
        <g>
            <rect
                x={x}
                y={y}
                width={width}
                height={height}
                style={{
                    fill: depth < 2 ? colors[index % colors.length] : "none",
                    stroke: "#fff",
                    strokeWidth: 2 / (depth + 1e-10),
                    strokeOpacity: 1 / (depth + 1e-10),
                }}
            />
            {width > 50 && height > 30 && (
                <text x={x + 6} y={y + 18} fill="#fff" fontSize={12} fontWeight="bold" className="truncate">
                    {name}
                </text>
            )}
            {width > 50 && height > 45 && (
                <text x={x + 6} y={y + 34} fill="#fff" fontSize={10} opacity={0.8}>
                    {value?.toLocaleString()}
                </text>
            )}
        </g>
    );
};

export function DynamicTreemap({ metric_slug, title, group_by = "sector", limit = 15, filters: widgetFilters }: any) {
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

                    let chartData = Object.entries(aggregated).map(([name, value]) => ({ name, size: value }));

                    chartData.sort((a, b) => b.size - a.size);
                    if (limit && limit > 0) {
                        chartData = chartData.slice(0, limit);
                    }

                    // Treemap expects a root node
                    setData([{ name: "Total", children: chartData }]);
                }
            } catch (err) {
                console.error("Failed to fetch Treemap data:", err);
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
                    <Skeleton className="h-[250px] w-full" />
                </CardContent>
            </Card>
        );
    }

    return (
        <Card className="h-full">
            <CardHeader className="pb-2">
                <CardTitle className="text-lg font-semibold">{title || "Market Hierarchy"}</CardTitle>
            </CardHeader>
            <CardContent>
                <div className="h-[250px] w-full mt-4">
                    {data.length === 0 || !data[0]?.children?.length ? (
                        <div className="h-full flex items-center justify-center text-sm text-muted-foreground border border-dashed rounded-md bg-accent/30">
                            No hierarchical data available.
                        </div>
                    ) : (
                        <ResponsiveContainer width="100%" height="100%">
                            <Treemap
                                data={data}
                                dataKey="size"
                                stroke="#fff"
                                fill="#8884d8"
                                content={<CustomizedContent colors={COLORS} />}
                            >
                                <Tooltip
                                    formatter={(value: any) => [value.toLocaleString(), group_by]}
                                    contentStyle={{ borderRadius: "8px", border: "none", boxShadow: "0 4px 6px -1px rgb(0 0 0 / 0.1)" }}
                                />
                            </Treemap>
                        </ResponsiveContainer>
                    )}
                </div>
            </CardContent>
        </Card>
    );
}
