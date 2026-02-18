"use client";

import { MapContainer, TileLayer, CircleMarker, Popup } from "react-leaflet";
import "leaflet/dist/leaflet.css";

interface MapProps {
    center: [number, number];
    zoom: number;
    markers?: Record<string, { lat: number; lng: number; name: string }>;
    t: (key: string) => string;
}

const Map = ({ center, zoom, markers, t }: MapProps) => {
    return (
        <div className="h-[600px] w-full rounded-lg border border-gray-200 dark:border-gray-700 overflow-hidden">
            <MapContainer
                center={center}
                zoom={zoom}
                style={{ height: "100%", width: "100%" }}
            >
                <TileLayer
                    attribution='&copy; <a href="https://boussole.dz">Boussole</a>'
                    url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                />
                {markers &&
                    Object.entries(markers).map(([code, coords]) => (
                        <CircleMarker
                            key={code}
                            center={[coords.lat, coords.lng]}
                            radius={10}
                            pathOptions={{
                                color: "#3b82f6",
                                fillColor: "#3b82f6",
                                fillOpacity: 0.7,
                            }}
                        >
                            <Popup>
                                <div className="p-2">
                                    <strong>{coords.name}</strong>
                                    <div className="text-sm text-muted-foreground">
                                        {t("wilayaCode")}: {code}
                                    </div>
                                </div>
                            </Popup>
                        </CircleMarker>
                    ))}
            </MapContainer>
        </div>
    );
};

export default Map;
