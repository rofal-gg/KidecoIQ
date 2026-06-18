"use client";

import { clsx } from "clsx";
import type { ReportResponse } from "@/types/reklamasi";

interface StatsGridProps {
  report: ReportResponse;
}

const statCards = [
  {
    key: "total_zones",
    label: "Total Zona",
    getValue: (r: ReportResponse) => r.total_zones,
    unit: "",
    color: "bg-blue-50 text-blue-700 border-blue-200",
  },
  {
    key: "ndvi",
    label: "Rata-rata NDVI",
    getValue: (r: ReportResponse) => r.overall_ndvi_mean.toFixed(3),
    unit: "",
    color: "bg-emerald-50 text-emerald-700 border-emerald-200",
  },
  {
    key: "vegetation",
    label: "Tutupan Vegetasi",
    getValue: (r: ReportResponse) => r.overall_vegetation_cover_pct.toFixed(1),
    unit: "%",
    color: "bg-green-50 text-green-700 border-green-200",
  },
  {
    key: "compliance",
    label: "Skor Kepatuhan",
    getValue: (r: ReportResponse) => r.compliance_score.toFixed(1),
    unit: "%",
    color: (r: ReportResponse) =>
      r.compliance_score >= 70
        ? "bg-emerald-50 text-emerald-700 border-emerald-200"
        : r.compliance_score >= 40
          ? "bg-amber-50 text-amber-700 border-amber-200"
          : "bg-red-50 text-red-700 border-red-200",
  },
];

export default function StatsGrid({ report }: StatsGridProps) {
  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
      {statCards.map((card) => {
        const color = typeof card.color === "function" ? card.color(report) : card.color;
        return (
          <div key={card.key} className={clsx("rounded-xl border p-4", color)}>
            <p className="text-xs font-medium opacity-75">{card.label}</p>
            <p className="text-2xl font-bold mt-1">
              {card.getValue(report)}
              {card.unit && <span className="text-sm font-normal ml-0.5">{card.unit}</span>}
            </p>
          </div>
        );
      })}
    </div>
  );
}
