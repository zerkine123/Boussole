"use client";

import { useEffect, useState } from "react";
import { Card, CardHeader, CardContent, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from "recharts";
import api from "@/lib/api";
import { useDashboardFilters } from "@/lib/DashboardFilterContext";

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#14b8a6', '#f97316'];

export function DynamicStackedAreaChart({ metric_slug, title, group_by = "year", stack_by = "sector", filters: widgetFilters }: any) {
    const [data, setData] = useState<any[]>([]);
    const [stackKeys, setStackKeys] = useState<string[]>([]);
    const [loading, setLoading] = useState(true);
    const { filters: globalFilters } = useDashboardFilters();

    useEffect(() => {
        async function fetchData() {
            try {
                setLoading(true);
                const token = localStorage.getItem("access_token");

                // Note: Stacked charts require robust grouping by both X-axis and Stack level
                // E.g. group_by = 'year', but fetching for all sectors
                const response = await api.queryData(token, {
                    metric_slugs: [metric_slug],
                    group_by: "year_and_sector", // Custom grouping logic handled client-side for MVP
                    filters: { ...widgetFilters, ...globalFilters }
                });

                if (response?.data) {
                    // Pivot data into format: { year: 2023, SectorA: 100, SectorB: 200 }
                    const aggregated: Record<string, any> = {};
                    const keys = new Set<string>();

                    response.data.forEach((row: any) => {
                        let xValue = 'Unknown';
                        let stackValue = 'Unknown';

                        if (group_by === 'year') xValue = row.year ? row.year.toString() : 'Unknown';
                        else if (group_by === 'wilaya') xValue = row.wilaya_name || 'Unknown';

                        if (stack_by === 'sector') stackValue = row.sector_name || 'Unknown';
                        else if (stack_by === 'wilaya') stackValue = row.wilaya_name || 'Unknown';

                        keys.add(stackValue);

                        if (!aggregated[xValue]) {
                            aggregated[xValue] = { [group_by]: xValue };
                        }

                        // Accumulate value for this (xValue, stackValue) coordinate
                        if (!aggregated[xValue][stackValue]) {
                            aggregated[xValue][stackValue] = 0;
                        }
                        aggregated[xValue][stackValue] += (row.value || 0);
                    });

                    const chartData = Object.values(aggregated).sort((a: any, b: any) => {
                        // Attempt numeric sort for 'year'
                        return parseFloat(a[group_by]) - parseFloat(b[group_by]);
                    });

                    setStackKeys(Array.from(keys));
                    setData(chartData);
                }
            } catch (err) {
                console.error("Failed to fetch StackedArea data:", err);
            } finally {
                setLoading(false);
            }
        }
        fetchData();
    }, [metric_slug, group_by, stack_by, widgetFilters, globalFilters]);

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
                <CardTitle className="text-lg font-semibold">{title}</CardTitle>
            </CardHeader>
            <CardContent>
                <div className="h-[250px] w-full mt-4">
                    {data.length === 0 ? (
                        <div className="h-full flex items-center justify-center text-sm text-muted-foreground border border-dashed rounded-md bg-accent/30">
                            No historical distribution data available.
                        </div>
                    ) : (
                        <ResponsiveContainer width="100%" height="100%">
                            <AreaChart data={data}>
                                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e5e7eb" />
                                <XAxis dataKey={group_by} axisLine={false} tickLine={false} tick={{ fontSize: 12 }} />
                                <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 12 }} />
                                <Tooltip
                                    contentStyle={{ borderRadius: "8px", border: "none", boxShadow: "0 4px 6px -1px rgb(0 0 0 / 0.1)" }}
                                />
                                {stackKeys.map((key, index) => (
                                    <Area
                                        key={key}
                                        type="monotone"
                                        dataKey={key}
                                        stackId="1"
                                        stroke={COLORS[index % COLORS.length]}
                                        fill={COLORS[index % COLORS.length]}
                                        fillOpacity={0.6}
                                    />
                                ))}
                                <Legend verticalAlign="bottom" height={36} iconType="circle" wrapperStyle={{ fontSize: '12px' }} />
                            </AreaChart>
                        </ResponsiveContainer>
                    )}
                </div>
            </CardContent>
        </Card>
    );
}
