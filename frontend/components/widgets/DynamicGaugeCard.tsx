"use client";

import { useEffect, useState } from "react";
import { Card, CardHeader, CardContent, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Target } from "lucide-react";
import api from "@/lib/api";
import { useDashboardFilters } from "@/lib/DashboardFilterContext";

export function DynamicGaugeCard({ metric_slug, title, target_value = 100, filters: widgetFilters }: any) {
    const [data, setData] = useState<number | null>(null);
    const [loading, setLoading] = useState(true);
    const { filters: globalFilters } = useDashboardFilters();

    useEffect(() => {
        async function fetchData() {
            try {
                setLoading(true);
                const token = localStorage.getItem("access_token");

                const response = await api.queryData(token, {
                    metric_slugs: [metric_slug],
                    filters: { ...widgetFilters, ...globalFilters }
                });

                if (response?.data) {
                    // Aggregate total value
                    const total = response.data.reduce((sum: number, row: any) => sum + (row.value || 0), 0);
                    setData(total);
                }
            } catch (err) {
                console.error("Failed to fetch Gauge data:", err);
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
                    <Skeleton className="h-5 w-1/3" />
                </CardHeader>
                <CardContent className="flex justify-center items-center">
                    <Skeleton className="h-[200px] w-[200px] rounded-full" />
                </CardContent>
            </Card>
        );
    }

    if (data === null) {
        return (
            <Card className="h-full">
                <CardHeader className="pb-2">
                    <CardTitle className="text-sm font-medium">{title || "Performance to Target"}</CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="text-sm text-center text-muted-foreground mt-4 border border-dashed rounded p-4 bg-accent/30">
                        No metric data available to gauge against target.
                    </div>
                </CardContent>
            </Card>
        );
    }

    const percentage = target_value > 0 ? Math.min((data / target_value) * 100, 100) : 0;
    const overperformance = target_value > 0 && data > target_value ? ((data - target_value) / target_value) * 100 : 0;

    // SVG properties
    const radius = 80;
    const circumference = 2 * Math.PI * radius;
    // For a semi-circle gauge, circumference / 2
    // Let's do a full ring gauge to keep it simple and clean
    const strokeDashoffset = circumference - (percentage / 100) * circumference;

    return (
        <Card className="h-full flex flex-col justify-between overflow-hidden">
            <CardHeader className="pb-0 flex flex-row items-center justify-between z-10">
                <CardTitle className="text-sm font-semibold text-foreground">
                    {title || "Target Completion"}
                </CardTitle>
                <Target className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent className="flex flex-col items-center justify-center p-6 relative">

                <div className="relative flex items-center justify-center">
                    {/* Background Ring */}
                    <svg className="w-48 h-48 transform -rotate-90">
                        <circle
                            cx="96"
                            cy="96"
                            r={radius}
                            fill="transparent"
                            stroke="currentColor"
                            strokeWidth="16"
                            className="text-muted/20"
                        />
                        {/* Progress Ring */}
                        <circle
                            cx="96"
                            cy="96"
                            r={radius}
                            fill="transparent"
                            stroke={percentage >= 100 ? "#10b981" : "#3b82f6"} // Emerald if reached, Blue if in progress
                            strokeWidth="16"
                            strokeDasharray={circumference}
                            strokeDashoffset={strokeDashoffset}
                            strokeLinecap="round"
                            className="transition-all duration-1000 ease-in-out"
                        />
                    </svg>

                    {/* Inner Text */}
                    <div className="absolute flex flex-col items-center justify-center text-center">
                        <span className="text-4xl font-bold font-mono tracking-tighter">
                            {percentage.toFixed(0)}%
                        </span>
                        <span className="text-xs uppercase font-semibold text-muted-foreground tracking-wider mt-1">
                            Reached
                        </span>
                    </div>
                </div>

                <div className="w-full flex justify-between items-center mt-6 px-2 text-sm">
                    <div className="flex flex-col items-start">
                        <span className="text-muted-foreground font-medium">Current</span>
                        <span className="font-bold text-lg">{data.toLocaleString()}</span>
                    </div>
                    <div className="h-8 w-px bg-border mx-4"></div>
                    <div className="flex flex-col items-end">
                        <span className="text-muted-foreground font-medium">Target</span>
                        <span className="font-bold text-lg">{Number(target_value).toLocaleString()}</span>
                    </div>
                </div>

                {overperformance > 0 && (
                    <div className="w-full mt-4 bg-emerald-50 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400 py-2 px-3 rounded-md text-xs font-bold text-center border border-emerald-200 dark:border-emerald-800">
                        Goal Exceeded by {overperformance.toFixed(1)}% 🚀
                    </div>
                )}
            </CardContent>
        </Card>
    );
}
