"use client";

import Badge, { statusBadgeVariant, statusLabel } from "@/components/ui/Badge";
import type { ZoneResponse } from "@/types/reklamasi";
import { clsx } from "clsx";

interface ZoneCardProps {
  zone: ZoneResponse;
  selected?: boolean;
  onClick?: () => void;
}

export default function ZoneCard({ zone, selected, onClick }: ZoneCardProps) {
  return (
    <button
      onClick={onClick}
      className={clsx(
        "w-full text-left rounded-xl border p-4 transition-all hover:shadow-md",
        selected
          ? "border-emerald-500 ring-2 ring-emerald-200 bg-emerald-50/50"
          : "border-gray-200 bg-white"
      )}
    >
      <div className="flex items-start justify-between gap-2">
        <div className="min-w-0">
          <p className="text-sm font-semibold text-gray-900 truncate">{zone.name}</p>
          <p className="text-xs text-gray-500 mt-0.5">{zone.area_ha.toFixed(1)} ha</p>
        </div>
        <Badge variant={statusBadgeVariant(zone.status)}>
          {statusLabel(zone.status)}
        </Badge>
      </div>

      <div className="mt-3 grid grid-cols-2 gap-2 text-xs">
        <div>
          <span className="text-gray-500">NDVI: </span>
          <span className="font-medium text-gray-800">{zone.ndvi_latest.toFixed(4)}</span>
        </div>
        <div>
          <span className="text-gray-500">Tutupan: </span>
          <span className="font-medium text-gray-800">{zone.vegetation_cover_pct.toFixed(1)}%</span>
        </div>
      </div>
    </button>
  );
}
