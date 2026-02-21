"use client";

import { useEffect, useState } from "react";
import { Card, CardHeader, CardContent, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { TrendingUp, TrendingDown, Minus, Activity } from "lucide-react";
import api from "@/lib/api";
import { useDashboardFilters } from "@/lib/DashboardFilterContext";

export function DynamicGrowthIndicator({ metric_slug, title, filters: widgetFilters }: any) {
    const [data, setData] = useState<any>(null);
    const [loading, setLoading] = useState(true);
    const { filters: globalFilters } = useDashboardFilters();

    useEffect(() => {
        async function fetchData() {
            try {
                setLoading(true);
                const token = localStorage.getItem("access_token");

                const response = await api.queryData(token, {
                    metric_slugs: [metric_slug],
                    group_by: "year",
                    filters: { ...widgetFilters, ...globalFilters }
                });

                if (response?.data && response.data.length >= 2) {
                    // Calculate growth between the newest and oldest year (or previous year)
                    // Sort by year ascending
                    const sorted = response.data.sort((a: any, b: any) => a.year - b.year);
                    const current = sorted[sorted.length - 1];
                    const previous = sorted[sorted.length - 2];

                    let cagr = 0;
                    if (sorted.length > 2) {
                        const first = sorted[0];
                        const years = current.year - first.year;
                        if (years > 0 && first.value > 0) {
                            cagr = (Math.pow(current.value / first.value, 1 / years) - 1) * 100;
                        }
                    }

                    let yoy = 0;
                    if (previous.value > 0) {
                        yoy = ((current.value - previous.value) / previous.value) * 100;
                    }

                    setData({
                        currentValue: current.value,
                        previousValue: previous.value,
                        currentYear: current.year,
                        previousYear: previous.year,
                        yoy,
                        cagr: sorted.length > 2 ? cagr : null,
                        trend: current.trend || (yoy > 0 ? "up" : yoy < 0 ? "down" : "none")
                    });
                }
            } catch (err) {
                console.error("Failed to fetch Growth Indicator data:", err);
            } finally {
                setLoading(false);
            }
        }
        fetchData();
    }, [metric_slug, widgetFilters, globalFilters]);

    if (loading) {
        return (
            <Card className="h-full">
                <CardHeader>
                    <Skeleton className="h-5 w-1/2" />
                </CardHeader>
                <CardContent>
                    <Skeleton className="h-12 w-32 mb-4" />
                    <Skeleton className="h-4 w-full" />
                    <Skeleton className="h-4 w-3/4 mt-2" />
                </CardContent>
            </Card>
        );
    }

    if (!data) {
        return (
            <Card className="h-full">
                <CardHeader className="pb-2">
                    <CardTitle className="text-sm font-medium">{title || "Growth Indicator"}</CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="text-sm text-muted-foreground mt-4">Not enough historical data to calculate growth.</div>
                </CardContent>
            </Card>
        );
    }

    return (
        <Card className="h-full border-t-4 border-t-primary/50 relative overflow-hidden">
            <div className="absolute -right-4 -bottom-4 opacity-5 pointer-events-none">
                <Activity className="w-32 h-32" />
            </div>
            <CardHeader className="pb-2 flex flex-row items-center justify-between">
                <CardTitle className="text-sm font-semibold text-foreground">
                    {title || "Growth Indicator"}
                </CardTitle>
                <div className={`p-1.5 rounded-full ${data.yoy > 0 ? 'bg-emerald-100' : data.yoy < 0 ? 'bg-red-100' : 'bg-gray-100'}`}>
                    {data.yoy > 0 ? <TrendingUp className="h-4 w-4 text-emerald-600" /> :
                        data.yoy < 0 ? <TrendingDown className="h-4 w-4 text-red-600" /> :
                            <Minus className="h-4 w-4 text-gray-600" />}
                </div>
            </CardHeader>
            <CardContent>
                <div className="flex flex-col mt-2">
                    <div className="flex items-baseline gap-2">
                        <span className={`text-4xl font-bold tracking-tighter ${data.yoy > 0 ? 'text-emerald-600' : data.yoy < 0 ? 'text-red-600' : 'text-foreground'}`}>
                            {data.yoy > 0 ? '+' : ''}{data.yoy.toFixed(1)}%
                        </span>
                        <span className="text-sm font-medium text-muted-foreground">YoY</span>
                    </div>

                    <div className="mt-6 space-y-2">
                        <div className="flex justify-between items-center text-sm border-b pb-1 border-dashed">
                            <span className="text-muted-foreground">{data.previousYear}</span>
                            <span className="font-semibold">{data.previousValue.toLocaleString()}</span>
                        </div>
                        <div className="flex justify-between items-center text-sm border-b pb-1 border-dashed">
                            <span className="text-muted-foreground font-medium text-primary">{data.currentYear}</span>
                            <span className="font-bold text-foreground">{data.currentValue.toLocaleString()}</span>
                        </div>
                        {data.cagr !== null && (
                            <div className="flex justify-between items-center text-sm pt-2">
                                <span className="text-muted-foreground">Historical CAGR</span>
                                <span className="font-bold">{data.cagr > 0 ? '+' : ''}{data.cagr.toFixed(1)}%</span>
                            </div>
                        )}
                    </div>
                </div>
            </CardContent>
        </Card>
    );
}
