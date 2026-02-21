"use client";

import { useEffect, useState } from "react";
import { Card, CardHeader, CardContent, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import dynamic from "next/dynamic";
import { Loader2 } from "lucide-react";
import { useTranslations } from "next-intl";
import api from "@/lib/api";
import { useDashboardFilters } from "@/lib/DashboardFilterContext";

const Map = dynamic(() => import("@/components/Map"), {
    ssr: false,
    loading: () => (
        <div className="h-[450px] w-full rounded-xl flex items-center justify-center bg-accent/30">
            <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
        </div>
    ),
});

// Helper for approximate coordinates per Wilaya (for MVP)
const WILAYA_COORDINATES: Record<string, { lat: number; lng: number; name: string }> = {
    "01": { lat: 36.753, lng: 3.04197, name: "Algiers" },
    "02": { lat: 35.6911, lng: -0.6417, name: "Oran" },
    "03": { lat: 36.7747, lng: 3.3897, name: "Constantine" },
    "04": { lat: 36.765, lng: 5.081, name: "Setif" },
    "05": { lat: 36.75, lng: 7.6167, name: "Batna" },
    "06": { lat: 36.7583, lng: 5.0581, name: "Annaba" },
    "07": { lat: 36.7667, lng: 6.6142, name: "Skikda" },
    "08": { lat: 36.7569, lng: 5.3819, name: "Tlemcen" },
    "09": { lat: 36.7667, lng: 5.5214, name: "Tizi Ouzou" },
    "10": { lat: 35.9219, lng: 5.5475, name: "Béjaïa" },
    "11": { lat: 36.7183, lng: 3.8047, name: "Biskra" },
    "12": { lat: 36.7683, lng: 5.0417, name: "Boumerdès" },
};

export function DynamicChoroplethMap({ metric_slug, title, filters: widgetFilters }: any) {
    const [data, setData] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const t = useTranslations("dashboard");
    const { filters: globalFilters } = useDashboardFilters();

    useEffect(() => {
        async function fetchData() {
            try {
                setLoading(true);
                const token = localStorage.getItem("access_token");

                const response = await api.queryData(token, {
                    metric_slugs: [metric_slug],
                    group_by: "wilaya",
                    filters: { ...widgetFilters, ...globalFilters }
                });

                if (response?.data) {
                    setData(response.data);
                }
            } catch (err) {
                console.error("Failed to fetch Map data:", err);
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
                <CardContent>
                    <Skeleton className="h-[450px] w-full" />
                </CardContent>
            </Card>
        );
    }

    // Enrich markers with values from API
    const mapMarkers: Record<string, { lat: number; lng: number; name: string; value?: number }> = { ...WILAYA_COORDINATES };

    data.forEach(item => {
        const code = item.wilaya_code?.padStart(2, '0');
        if (code && mapMarkers[code]) {
            mapMarkers[code].value = item.value;
        }
    });

    return (
        <Card className="h-full">
            <CardHeader className="pb-2">
                <CardTitle className="text-lg font-semibold">{title || "Regional Distribution"}</CardTitle>
            </CardHeader>
            <CardContent className="p-0 overflow-hidden rounded-b-xl border-t">
                <Map
                    center={[36.7538, 3.0588]}
                    zoom={5}
                    markers={mapMarkers}
                    t={t}
                />
            </CardContent>
        </Card>
    );
}
