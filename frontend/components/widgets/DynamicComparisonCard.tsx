"use client";

import { useEffect, useState } from "react";
import { Card, CardHeader, CardContent, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { ArrowUpRight, ArrowDownRight, Minus, Scale } from "lucide-react";
import api from "@/lib/api";
import { useDashboardFilters } from "@/lib/DashboardFilterContext";

export function DynamicComparisonCard({ metric_slug, title, compare_field = "wilaya", compare_entities, filters: widgetFilters }: any) {
    const [data, setData] = useState<{ entity1: any, entity2: any, diff: number, percentDiff: number } | null>(null);
    const [loading, setLoading] = useState(true);
    const { filters: globalFilters } = useDashboardFilters();

    // compare_entities should be an array of two IDs or names: e.g. ["16", "31"] (Algiers vs Oran)
    const entities = Array.isArray(compare_entities) ? compare_entities : [];

    useEffect(() => {
        if (entities.length !== 2) return;

        async function fetchData() {
            try {
                setLoading(true);
                const token = localStorage.getItem("access_token");

                // Fetch data grouped by the compare_field (e.g. wilaya or sector)
                const response = await api.queryData(token, {
                    metric_slugs: [metric_slug],
                    group_by: compare_field,
                    filters: { ...widgetFilters, ...globalFilters }
                });

                if (response?.data) {
                    const aggregated: Record<string, any> = {};

                    response.data.forEach((row: any) => {
                        let key = 'Unknown';
                        if (compare_field === 'sector') key = row.sector_code || row.sector_name || 'Unknown';
                        else if (compare_field === 'wilaya') key = row.wilaya_code?.padStart(2, '0') || row.wilaya_name || 'Unknown';

                        const displayLabel = compare_field === 'sector' ? row.sector_name : row.wilaya_name;

                        if (!aggregated[key]) {
                            aggregated[key] = { name: displayLabel || key, value: 0 };
                        }
                        aggregated[key].value += (row.value || 0);
                    });

                    // Search for the two entities in the aggregated results
                    // E.g. entities[0] = "16", entities[1] = "31"
                    const entity1Key = entities[0];
                    const entity2Key = entities[1];

                    const e1 = aggregated[entity1Key] || { name: entity1Key, value: 0 };
                    const e2 = aggregated[entity2Key] || { name: entity2Key, value: 0 };

                    let diff = e1.value - e2.value;
                    let percentDiff = 0;
                    if (e2.value > 0) {
                        percentDiff = (diff / e2.value) * 100;
                    } else if (e1.value > 0) {
                        percentDiff = 100;
                    }

                    setData({
                        entity1: e1,
                        entity2: e2,
                        diff,
                        percentDiff
                    });
                }
            } catch (err) {
                console.error("Failed to fetch Comparison data:", err);
            } finally {
                setLoading(false);
            }
        }
        fetchData();
    }, [metric_slug, compare_field, JSON.stringify(entities), widgetFilters, globalFilters]);

    if (loading) {
        return (
            <Card className="h-full">
                <CardHeader>
                    <Skeleton className="h-5 w-1/2" />
                </CardHeader>
                <CardContent>
                    <Skeleton className="h-16 w-full mb-4" />
                    <Skeleton className="h-16 w-full" />
                </CardContent>
            </Card>
        );
    }

    if (!data || entities.length !== 2) {
        return (
            <Card className="h-full">
                <CardHeader className="pb-2">
                    <CardTitle className="text-sm font-medium">{title || "Head-to-Head Comparison"}</CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="text-sm text-center text-muted-foreground mt-4 border border-dashed rounded p-4 bg-accent/30">
                        Invalid comparison parameters. Provide exactly two entities to compare.
                    </div>
                </CardContent>
            </Card>
        );
    }

    const isE1Winner = data.diff > 0;
    const isTie = data.diff === 0;

    return (
        <Card className="h-full border-t-4 border-primary/50 relative overflow-hidden">
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 opacity-5 pointer-events-none">
                <Scale className="w-48 h-48" />
            </div>

            <CardHeader className="pb-2 flex flex-row items-center justify-between">
                <CardTitle className="text-sm font-semibold text-foreground">
                    {title || `${data.entity1.name} vs ${data.entity2.name}`}
                </CardTitle>
            </CardHeader>
            <CardContent className="h-full flex flex-col justify-center gap-6 mt-2 relative z-10">

                {/* Entity 1 */}
                <div className="flex justify-between items-end border-b pb-3 border-gray-100 dark:border-gray-800">
                    <div>
                        <p className="text-sm font-medium text-muted-foreground mb-1">{data.entity1.name}</p>
                        <h3 className={`text-3xl font-bold ${isE1Winner ? 'text-primary' : 'text-foreground'}`}>
                            {data.entity1.value.toLocaleString()}
                        </h3>
                    </div>
                    {!isTie && isE1Winner && (
                        <div className="flex items-center text-emerald-600 bg-emerald-50 dark:bg-emerald-900/20 px-2 py-1 rounded text-xs font-bold">
                            <ArrowUpRight className="w-3 h-3 mr-1" />
                            +{data.percentDiff.toFixed(1)}% vs {data.entity2.name}
                        </div>
                    )}
                </div>

                {/* VS Badge */}
                <div className="absolute top-1/2 left-[calc(50%-1.1rem)] -translate-y-1/2 bg-accent text-accent-foreground text-xs font-bold w-9 h-9 rounded-full flex items-center justify-center border-4 border-background z-20 shadow-sm">
                    VS
                </div>

                {/* Entity 2 */}
                <div className="flex justify-between items-start pt-1">
                    <div>
                        <p className="text-sm font-medium text-muted-foreground mb-1">{data.entity2.name}</p>
                        <h3 className={`text-3xl font-bold ${!isE1Winner && !isTie ? 'text-primary' : 'text-foreground'}`}>
                            {data.entity2.value.toLocaleString()}
                        </h3>
                    </div>
                    {!isTie && !isE1Winner && (
                        <div className="flex items-center text-amber-600 bg-amber-50 dark:bg-amber-900/20 px-2 py-1 rounded text-xs font-bold">
                            <ArrowDownRight className="w-3 h-3 mr-1" />
                            {data.percentDiff.toFixed(1)}% vs {data.entity1.name}
                        </div>
                    )}
                    {isTie && (
                        <div className="flex items-center text-gray-500 bg-gray-100 dark:bg-gray-800 px-2 py-1 rounded text-xs font-bold">
                            <Minus className="w-3 h-3 mr-1" /> Equal
                        </div>
                    )}
                </div>

            </CardContent>
        </Card>
    );
}
