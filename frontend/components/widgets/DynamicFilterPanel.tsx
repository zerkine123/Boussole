"use client";

import { Card, CardHeader, CardContent, CardTitle } from "@/components/ui/card";
import { SlidersHorizontal } from "lucide-react";
import { useDashboardFilters } from "@/lib/DashboardFilterContext";

export function DynamicFilterPanel({ title, available_filters = [] }: any) {
    const { filters, setFilter, availableSectors, availableWilayas } = useDashboardFilters();

    const currentYear = new Date().getFullYear();
    const years = Array.from({ length: 5 }, (_, i) => (currentYear - i).toString());

    return (
        <Card className="h-full bg-slate-50 border-slate-200">
            <CardHeader className="pb-2 flex flex-row items-center justify-between">
                <CardTitle className="text-sm font-semibold text-slate-700 flex items-center gap-2">
                    <SlidersHorizontal className="h-4 w-4" />
                    {title || "Dashboard Filters"}
                </CardTitle>
            </CardHeader>
            <CardContent>
                <div className="flex flex-wrap gap-3 mt-2">
                    {available_filters.length > 0 ? (
                        available_filters.map((f: string, i: number) => {
                            if (f === "sector") {
                                return (
                                    <div key={i} className="flex flex-col gap-1 w-[140px]">
                                        <label className="text-xs font-medium text-slate-500 capitalize">{f}</label>
                                        <select
                                            className="w-full text-sm border-slate-200 rounded-md bg-white p-1.5 text-slate-700"
                                            value={filters.sector_slug || "all"}
                                            onChange={(e) => setFilter("sector_slug", e.target.value)}
                                        >
                                            <option value="all">All Sectors</option>
                                            {availableSectors.map((s: any) => (
                                                <option key={s.id} value={s.slug}>{s.name_en}</option>
                                            ))}
                                        </select>
                                    </div>
                                );
                            } else if (f === "wilaya") {
                                return (
                                    <div key={i} className="flex flex-col gap-1 w-[140px]">
                                        <label className="text-xs font-medium text-slate-500 capitalize">{f}</label>
                                        <select
                                            className="w-full text-sm border-slate-200 rounded-md bg-white p-1.5 text-slate-700"
                                            value={filters.wilaya_code || "all"}
                                            onChange={(e) => setFilter("wilaya_code", e.target.value)}
                                        >
                                            <option value="all">All Wilayas</option>
                                            {availableWilayas.map((w: any) => (
                                                <option key={w.id} value={w.code}>{w.code} - {w.name_en}</option>
                                            ))}
                                        </select>
                                    </div>
                                );
                            } else if (f === "year") {
                                return (
                                    <div key={i} className="flex flex-col gap-1 w-[140px]">
                                        <label className="text-xs font-medium text-slate-500 capitalize">{f}</label>
                                        <select
                                            className="w-full text-sm border-slate-200 rounded-md bg-white p-1.5 text-slate-700"
                                            value={filters.year || "all"}
                                            onChange={(e) => setFilter("year", e.target.value)}
                                        >
                                            <option value="all">All Years</option>
                                            {years.map(y => (
                                                <option key={y} value={y}>{y}</option>
                                            ))}
                                        </select>
                                    </div>
                                );
                            }
                            return null;
                        })
                    ) : (
                        <p className="text-xs text-slate-400 italic">No dynamic filters configured for this view.</p>
                    )}
                </div>
            </CardContent>
        </Card>
    );
}
