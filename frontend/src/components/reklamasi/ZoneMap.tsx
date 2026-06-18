"use client";

import { useEffect, useMemo } from "react";
import { MapContainer, TileLayer, Rectangle, Tooltip, useMap } from "react-leaflet";
import L from "leaflet";
import type { ZoneResponse } from "@/types/reklamasi";

interface ZoneMapProps {
  zones: ZoneResponse[];
  selectedId: string | null;
  onSelectZone: (zone: ZoneResponse) => void;
}

const ZONE_BOUNDS: Record<string, L.LatLngBoundsExpression> = {
  "11111111-1111-1111-1111-111111111111": [
    [-1.08, 116.68],
    [-1.06, 116.71],
  ],
  "22222222-2222-2222-2222-222222222222": [
    [-1.08, 116.71],
    [-1.06, 116.74],
  ],
  "33333333-3333-3333-3333-333333333333": [
    [-1.11, 116.68],
    [-1.08, 116.71],
  ],
  "44444444-4444-4444-4444-444444444444": [
    [-1.11, 116.71],
    [-1.08, 116.74],
  ],
  "55555555-5555-5555-5555-555555555555": [
    [-1.10, 116.69],
    [-1.07, 116.73],
  ],
};

const STATUS_COLORS: Record<string, string> = {
  vegetasi_sehat: "#22c55e",
  vegetasi_stres: "#eab308",
  lahan_kosong: "#b45309",
  air: "#3b82f6",
};

function MapController({ selectedId }: { selectedId: string | null }) {
  const map = useMap();

  useEffect(() => {
    if (selectedId) {
      const bounds = ZONE_BOUNDS[selectedId];
      if (bounds) {
        map.fitBounds(bounds, { padding: [50, 50], maxZoom: 16 });
      }
    } else {
      map.setView([-1.09, 116.71], 13);
    }
  }, [selectedId, map]);

  return null;
}

export default function ZoneMap({ zones, selectedId, onSelectZone }: ZoneMapProps) {
  const center: L.LatLngExpression = useMemo(() => [-1.09, 116.71], []);

  return (
    <MapContainer
      center={center}
      zoom={13}
      className="w-full h-full min-h-[400px]"
      zoomControl={true}
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />

      <MapController selectedId={selectedId} />

      {zones.map((zone) => {
        const bounds = ZONE_BOUNDS[zone.id];
        if (!bounds) return null;

        const color = STATUS_COLORS[zone.status] || "#6b7280";
        const isSelected = selectedId === zone.id;

        return (
          <Rectangle
            key={zone.id}
            bounds={bounds}
            pathOptions={{
              color,
              weight: isSelected ? 3 : 2,
              fillColor: color,
              fillOpacity: isSelected ? 0.35 : 0.2,
            }}
            eventHandlers={{
              click: () => onSelectZone(zone),
            }}
          >
            <Tooltip direction="center" permanent={false}>
              <div className="text-xs font-medium">{zone.name}</div>
              <div className="text-xs text-gray-500">NDVI: {zone.ndvi_latest.toFixed(3)}</div>
            </Tooltip>
          </Rectangle>
        );
      })}
    </MapContainer>
  );
}
