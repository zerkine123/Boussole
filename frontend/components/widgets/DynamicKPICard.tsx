"use client";

import { useEffect, useState } from "react";
import { useLocale } from "next-intl";
import { Card, CardHeader, CardContent, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { ArrowUpRight, ArrowDownRight, Minus, Activity } from "lucide-react";
import api from "@/lib/api";
import { useDashboardFilters } from "@/lib/DashboardFilterContext";

interface KPICardProps {
    metric_slug: string;
    title: string;
    trend_type?: "up" | "down" | "neutral" | "none";
    filters?: any;
}

export function DynamicKPICard({ metric_slug, title, trend_type = "none", filters: widgetFilters }: KPICardProps) {
    const [data, setData] = useState<any>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(false);
    const locale = useLocale();
    const { filters: globalFilters } = useDashboardFilters();

    useEffect(() => {
        async function fetchData() {
            try {
                setLoading(true);
                // We do not require token for public dashboard demo
                const token = localStorage.getItem("access_token");

                const response = await api.queryData(token, {
                    metric_slugs: [metric_slug],
                    filters: { ...widgetFilters, ...globalFilters }
                });

                if (response?.data && response.data.length > 0) {
                    setData(response.data[0]);
                } else {
                    setData(null);
                }
            } catch (err) {
                console.error("Failed to fetch KPI data:", err);
                setError(true);
            } finally {
                setLoading(false);
            }
        }
        fetchData();
    }, [metric_slug, widgetFilters, globalFilters]);

    if (loading) {
        return (
            <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <Skeleton className="h-4 w-1/2" />
                    <Skeleton className="h-4 w-4 rounded-full" />
                </CardHeader>
                <CardContent>
                    <Skeleton className="h-8 w-[100px] mb-2" />
                    <Skeleton className="h-3 w-1/3" />
                </CardContent>
            </Card>
        );
    }

    if (error || !data) {
        return (
            <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">{title}</CardTitle>
                    <Activity className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                    <div className="text-2xl font-bold text-muted-foreground">--</div>
                    <p className="text-xs text-muted-foreground">Data unavailable</p>
                </CardContent>
            </Card>
        );
    }

    // Formatting value intelligently
    let formattedValue = data.value.toString();
    if (data.value >= 1000000) {
        formattedValue = (data.value / 1000000).toFixed(1) + "M";
    } else if (data.value >= 1000) {
        formattedValue = (data.value / 1000).toFixed(1) + "K";
    }

    // Render trend arrow
    const renderTrend = () => {
        if (trend_type === "none") return null;

        // Use the fetched change_percent if available, otherwise fallback to trend_type direction
        const pct = data.change_percent ? `${data.change_percent >= 0 ? '+' : ''}${data.change_percent}%` : '';

        if (trend_type === "up" || data.trend === "up") {
            return (
                <p className="text-xs text-emerald-600 flex items-center font-medium">
                    <ArrowUpRight className="h-3 w-3 mr-1" />
                    {pct || "Trending up"}
                </p>
            );
        }
        if (trend_type === "down" || data.trend === "down") {
            return (
                <p className="text-xs text-red-600 flex items-center font-medium">
                    <ArrowDownRight className="h-3 w-3 mr-1" />
                    {pct || "Trending down"}
                </p>
            );
        }
        return (
            <p className="text-xs text-muted-foreground flex items-center font-medium">
                <Minus className="h-3 w-3 mr-1" />
                {pct || "Stable"}
            </p>
        );
    };

    return (
        <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">{title}</CardTitle>
                <Activity className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
                <div className="flex items-baseline space-x-2">
                    <div className="text-2xl font-bold">{formattedValue}</div>
                    {data.unit && <span className="text-sm font-medium text-muted-foreground">{data.unit}</span>}
                </div>
                {renderTrend()}
                <p className="text-[10px] text-muted-foreground uppercase mt-2 tracking-wider">
                    {data.year ? `DATA FROM ${data.year}` : 'LATEST DATA'} • {data.sector_name}
                </p>
            </CardContent>
        </Card>
    );
}
