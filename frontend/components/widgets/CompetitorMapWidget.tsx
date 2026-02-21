"use client";

import { useEffect, useState } from "react";
import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import L from "leaflet";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

// Fix Leaflet default icon issue in Next.js
const iconUrl = "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png";
const iconRetinaUrl = "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png";
const shadowUrl = "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png";

const customIcon = L.icon({
    iconUrl: iconUrl,
    iconRetinaUrl: iconRetinaUrl,
    shadowUrl: shadowUrl,
    iconSize: [25, 41],
    iconAnchor: [12, 41],
    popupAnchor: [1, -34],
    shadowSize: [41, 41]
});

interface Competitor {
    name: string;
    lat: number;
    lon: number;
    rating?: number;
    user_ratings_total?: number;
    vicinity?: string;
    types?: string[];
}

interface CompetitorMapData {
    center: { lat: number; lon: number };
    competitors: Competitor[];
    saturation_index: number;
    label: string;
}

interface CompetitorMapWidgetProps {
    title: string;
    data: CompetitorMapData;
}

export default function CompetitorMapWidget({ title, data }: CompetitorMapWidgetProps) {
    const [isMounted, setIsMounted] = useState(false);

    useEffect(() => {
        setIsMounted(true);
    }, []);

    if (!isMounted) {
        return (
            <Card className="h-[400px] w-full flex items-center justify-center bg-muted/20">
                <p className="text-muted-foreground">Loading Map...</p>
            </Card>
        );
    }

    const { center, competitors, saturation_index, label } = data;

    // Saturation color
    const getBadgeColor = (val: number) => {
        if (val < 40) return "bg-green-500 hover:bg-green-600";
        if (val < 70) return "bg-yellow-500 hover:bg-yellow-600";
        return "bg-red-500 hover:bg-red-600";
    };

    return (
        <Card className="w-full h-full min-h-[400px] flex flex-col">
            <CardHeader className="pb-2">
                <div className="flex items-center justify-between">
                    <CardTitle className="text-lg font-medium">{title}</CardTitle>
                    <Badge className={`${getBadgeColor(saturation_index)} text-white`}>
                        {label} ({competitors.length} found)
                    </Badge>
                </div>
            </CardHeader>
            <CardContent className="flex-1 p-0 relative overflow-hidden rounded-b-lg">
                <MapContainer
                    center={[center.lat, center.lon]}
                    zoom={14}
                    style={{ height: "100%", width: "100%", minHeight: "350px" }}
                >
                    <TileLayer
                        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                    />

                    {/* Location Center Marker (Optional, different color) */}

                    {competitors.map((comp, idx) => (
                        <Marker
                            key={idx}
                            position={[comp.lat, comp.lon]}
                            icon={customIcon}
                        >
                            <Popup>
                                <div className="p-1">
                                    <h3 className="font-bold text-sm">{comp.name}</h3>
                                    <p className="text-xs text-gray-600">{comp.vicinity}</p>
                                    <div className="flex items-center gap-2 mt-1">
                                        {comp.rating && (
                                            <span className="text-xs font-medium bg-yellow-100 px-1 rounded text-yellow-800">
                                                ★ {comp.rating} ({comp.user_ratings_total})
                                            </span>
                                        )}
                                        <span className="text-xs text-gray-500 capitalize">
                                            {comp.types?.[0]?.replace('_', ' ')}
                                        </span>
                                    </div>
                                </div>
                            </Popup>
                        </Marker>
                    ))}
                </MapContainer>

                {/* Overlay Legend */}
                <div className="absolute bottom-4 right-4 bg-white/90 p-2 rounded shadow-md text-xs z-[1000]">
                    <div className="font-semibold mb-1">Saturation Index</div>
                    <div className="flex items-center gap-1 mb-1">
                        <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                        <span>Low (Opportunity)</span>
                    </div>
                    <div className="flex items-center gap-1 mb-1">
                        <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
                        <span>Moderate</span>
                    </div>
                    <div className="flex items-center gap-1">
                        <div className="w-3 h-3 bg-red-500 rounded-full"></div>
                        <span>High (Saturated)</span>
                    </div>
                </div>
            </CardContent>
        </Card>
    );
}
