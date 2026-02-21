"use client";

import { useEffect, useState } from "react";
import { Card, CardHeader, CardContent, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from "@/components/ui/table";
import api from "@/lib/api";
import { useDashboardFilters } from "@/lib/DashboardFilterContext";

export function DynamicDataTable({ metric_slugs, metric_slug, title, group_by = "sector", limit = 10, filters: widgetFilters }: any) {
    const [data, setData] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const { filters: globalFilters } = useDashboardFilters();

    // Accept both metric_slugs (array from AI schema) and metric_slug (single string fallback)
    const resolvedSlugs: string[] = Array.isArray(metric_slugs)
        ? metric_slugs.filter(Boolean)
        : metric_slug
            ? [metric_slug]
            : [];

    useEffect(() => {
        async function fetchData() {
            if (resolvedSlugs.length === 0) { setLoading(false); return; }
            try {
                setLoading(true);
                const token = localStorage.getItem("access_token");

                const response = await api.queryData(token, {
                    metric_slugs: resolvedSlugs,
                    group_by,
                    filters: { ...widgetFilters, ...globalFilters }
                });

                if (response?.data) {
                    const aggregated: Record<string, any> = {};

                    response.data.forEach((row: any) => {
                        let key = 'Unknown';
                        if (group_by === 'sector') key = row.sector_name || 'Unknown';
                        else if (group_by === 'wilaya') key = row.wilaya_name || 'Unknown';
                        else if (group_by === 'year') key = row.year ? row.year.toString() : 'Unknown';

                        if (!aggregated[key]) {
                            aggregated[key] = {
                                label: key,
                                value: 0,
                                trend: row.trend || 'none',
                                change_percent: row.change_percent || 0
                            };
                        }
                        aggregated[key].value += (row.value || 0);
                    });

                    let tableData = Object.values(aggregated) as any[];

                    // Sort descending
                    tableData.sort((a, b) => b.value - a.value);
                    if (limit && limit > 0) {
                        tableData = tableData.slice(0, limit);
                    }

                    setData(tableData);
                }
            } catch (err) {
                console.error("Failed to fetch DataTable data:", err);
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
                <CardTitle className="text-lg font-semibold">{title}</CardTitle>
            </CardHeader>
            <CardContent>
                {data.length === 0 ? (
                    <div className="h-[200px] flex items-center justify-center text-sm text-muted-foreground border border-dashed rounded-md bg-accent/30 mt-4">
                        No tabular data available.
                    </div>
                ) : (
                    <div className="overflow-auto mt-4 max-h-[300px]">
                        <Table>
                            <TableHeader>
                                <TableRow>
                                    <TableHead className="w-[50%]">{group_by.charAt(0).toUpperCase() + group_by.slice(1)}</TableHead>
                                    <TableHead className="text-right">Value</TableHead>
                                    <TableHead className="text-right">% Change</TableHead>
                                </TableRow>
                            </TableHeader>
                            <TableBody>
                                {data.map((row, i) => (
                                    <TableRow key={i}>
                                        <TableCell className="font-medium">{row.label}</TableCell>
                                        <TableCell className="text-right">{row.value.toLocaleString()}</TableCell>
                                        <TableCell className={`text-right ${row.change_percent > 0 ? "text-emerald-600" : row.change_percent < 0 ? "text-red-600" : "text-muted-foreground"}`}>
                                            {row.change_percent > 0 ? '+' : ''}{row.change_percent}%
                                        </TableCell>
                                    </TableRow>
                                ))}
                            </TableBody>
                        </Table>
                    </div>
                )}
            </CardContent>
        </Card>
    );
}
