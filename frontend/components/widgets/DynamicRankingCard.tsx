"use client";

import { useEffect, useState } from "react";
import { Card, CardHeader, CardContent, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Trophy, TrendingDown, Minus } from "lucide-react";
import api from "@/lib/api";
import { useDashboardFilters } from "@/lib/DashboardFilterContext";

export function DynamicRankingCard({ metric_slug, title, group_by = "wilaya", filter_type = "top", limit = 5, filters: widgetFilters }: any) {
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

                        if (!aggregated[key]) aggregated[key] = 0;
                        aggregated[key] += (row.value || 0);
                    });

                    let rankedData = Object.entries(aggregated).map(([name, value]) => ({ name, value }));

                    // Sort direction based on filter_type
                    if (filter_type === "bottom") {
                        rankedData.sort((a, b) => a.value - b.value);
                    } else {
                        // default to top
                        rankedData.sort((a, b) => b.value - a.value);
                    }

                    if (limit && limit > 0) {
                        rankedData = rankedData.slice(0, limit);
                    }

                    setData(rankedData);
                }
            } catch (err) {
                console.error("Failed to fetch Ranking data:", err);
            } finally {
                setLoading(false);
            }
        }
        fetchData();
    }, [metric_slug, group_by, filter_type, limit, widgetFilters, globalFilters]);

    if (loading) {
        return (
            <Card className="h-full">
                <CardHeader>
                    <Skeleton className="h-5 w-2/3" />
                </CardHeader>
                <CardContent className="space-y-4">
                    {[...Array(limit || 3)].map((_, i) => (
                        <Skeleton key={i} className="h-8 w-full" />
                    ))}
                </CardContent>
            </Card>
        );
    }

    const isTop = filter_type !== "bottom";

    return (
        <Card className="h-full">
            <CardHeader className="pb-2 flex flex-row items-center justify-between">
                <CardTitle className="text-sm font-semibold text-foreground">
                    {title || `${isTop ? 'Top' : 'Bottom'} ${limit} ${group_by.charAt(0).toUpperCase() + group_by.slice(1)}s`}
                </CardTitle>
                {isTop ? <Trophy className="h-4 w-4 text-amber-500" /> : <TrendingDown className="h-4 w-4 text-red-500" />}
            </CardHeader>
            <CardContent>
                {data.length === 0 ? (
                    <div className="text-sm text-muted-foreground py-4 text-center">No data available to rank</div>
                ) : (
                    <ul className="space-y-3 mt-2">
                        {data.map((item, index) => (
                            <li key={index} className="flex items-center justify-between group">
                                <div className="flex items-center gap-3">
                                    <div className={`flex items-center justify-center h-6 w-6 rounded-full text-xs font-bold 
                     ${index === 0 && isTop ? 'bg-amber-100 text-amber-700' :
                                            index === 1 && isTop ? 'bg-gray-100 text-gray-700' :
                                                index === 2 && isTop ? 'bg-orange-100 text-orange-800' : 'bg-primary/5 text-muted-foreground'}`}>
                                        {index + 1}
                                    </div>
                                    <span className="text-sm font-medium text-foreground group-hover:text-primary transition-colors line-clamp-1">{item.name}</span>
                                </div>
                                <span className="text-sm font-bold">{item.value.toLocaleString()}</span>
                            </li>
                        ))}
                    </ul>
                )}
            </CardContent>
        </Card>
    );
}
