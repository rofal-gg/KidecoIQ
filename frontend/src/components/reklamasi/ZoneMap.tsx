"use client";

import { useEffect, useMemo, useCallback } from "react";
import { MapContainer, TileLayer, Rectangle, Tooltip, useMap } from "react-leaflet";
import L from "leaflet";
import type { ZoneResponse } from "@/types/reklamasi";

interface ZoneMapProps {
  zones: ZoneResponse[];
  selectedId: string | null;
  onSelectZone: (zone: ZoneResponse) => void;
}

const STATUS_COLORS: Record<string, string> = {
  vegetasi_sehat: "#22c55e",
  vegetasi_stres: "#eab308",
  lahan_kosong: "#b45309",
  air: "#3b82f6",
};

function getBounds(zone: ZoneResponse): L.LatLngBoundsExpression {
  return [
    [zone.southwest_lat, zone.southwest_lng],
    [zone.northeast_lat, zone.northeast_lng],
  ];
}

function MapController({ zones, selectedId }: { zones: ZoneResponse[]; selectedId: string | null }) {
  const map = useMap();

  useEffect(() => {
    if (selectedId) {
      const zone = zones.find((z) => z.id === selectedId);
      if (zone) {
        map.fitBounds(getBounds(zone), { padding: [50, 50], maxZoom: 16 });
        return;
      }
    }
    map.setView([-1.09, 116.71], 13);
  }, [selectedId, zones, map]);

  return null;
}

export default function ZoneMap({ zones, selectedId, onSelectZone }: ZoneMapProps) {
  const center: L.LatLngExpression = useMemo(() => [-1.09, 116.71], []);

  const handleClick = useCallback(
    (zone: ZoneResponse) => {
      onSelectZone(zone);
    },
    [onSelectZone],
  );

  return (
    <MapContainer
      center={center}
      zoom={13}
      className="w-full h-full min-h-[400px]"
      zoomControl={true}
    >
      <TileLayer
        attribution='&copy; <a href="https://www.esri.com/">Esri</a>, Maxar, Earthstar Geographics, and the GIS User Community'
        url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
      />

      <MapController zones={zones} selectedId={selectedId} />

      {zones.map((zone) => {
        const bounds = getBounds(zone);
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
              click: () => handleClick(zone),
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
