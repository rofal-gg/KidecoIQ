"use client";

import { useState, useEffect } from "react";
import { X, TrendingUp, TrendingDown, Minus, AlertTriangle, Loader2 } from "lucide-react";
import Badge, { statusBadgeVariant, statusLabel } from "@/components/ui/Badge";
import { fetchApi } from "@/lib/api";
import type { ZoneResponse, ZoneHistoryResponse, HistoryPoint } from "@/types/reklamasi";

interface ZoneDetailSheetProps {
  zone: ZoneResponse | null;
  onClose: () => void;
}

function TrendIcon({ current, previous }: { current: number; previous: number }) {
  const diff = current - previous;
  if (diff > 0.01) return <TrendingUp className="w-4 h-4 text-emerald-500" />;
  if (diff < -0.01) return <TrendingDown className="w-4 h-4 text-red-500" />;
  return <Minus className="w-4 h-4 text-gray-400" />;
}

export default function ZoneDetailSheet({ zone, onClose }: ZoneDetailSheetProps) {
  const [history, setHistory] = useState<ZoneHistoryResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!zone) {
      setHistory(null);
      return;
    }

    let cancelled = false;

    const fetchHistory = async () => {
      setLoading(true);
      setError(null);
      try {
        const data = await fetchApi<ZoneHistoryResponse>(
          `/reklamasi/zones/${zone.id}/history`,
        );
        if (!cancelled) setHistory(data);
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : "Gagal memuat riwayat");
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    };

    fetchHistory();

    return () => {
      cancelled = true;
    };
  }, [zone]);

  if (!zone) return null;

  const riskFlag = zone.status === "air" || zone.status === "lahan_kosong";

  return (
    <div className="fixed inset-0 z-50 flex justify-end">
      <div className="absolute inset-0 bg-black/20" onClick={onClose} />
      <div className="relative w-full max-w-md bg-white shadow-2xl h-full overflow-y-auto">
        <div className="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
          <h2 className="font-semibold text-gray-900 truncate">{zone.name}</h2>
          <button onClick={onClose} className="p-1 hover:bg-gray-100 rounded-lg">
            <X className="w-5 h-5 text-gray-500" />
          </button>
        </div>

        <div className="p-6 space-y-6">
          <div className="flex items-center gap-3">
            <Badge variant={statusBadgeVariant(zone.status)} className="text-sm px-3 py-1">
              {statusLabel(zone.status)}
            </Badge>
            {riskFlag && (
              <Badge variant="danger" className="text-sm px-3 py-1">
                <AlertTriangle className="w-3 h-3 mr-1" />
                Berisiko
              </Badge>
            )}
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="bg-gray-50 rounded-lg p-3">
              <p className="text-xs text-gray-500">NDVI Terkini</p>
              <p className="text-lg font-bold text-gray-900">{zone.ndvi_latest.toFixed(4)}</p>
            </div>
            <div className="bg-gray-50 rounded-lg p-3">
              <p className="text-xs text-gray-500">Tutupan Vegetasi</p>
              <p className="text-lg font-bold text-gray-900">{zone.vegetation_cover_pct.toFixed(1)}%</p>
            </div>
            <div className="bg-gray-50 rounded-lg p-3">
              <p className="text-xs text-gray-500">Luas Area</p>
              <p className="text-lg font-bold text-gray-900">{zone.area_ha.toFixed(1)} ha</p>
            </div>
            <div className="bg-gray-50 rounded-lg p-3">
              <p className="text-xs text-gray-500">Update Terakhir</p>
              <p className="text-sm font-bold text-gray-900">
                {new Date(zone.updated_at).toLocaleDateString("id-ID")}
              </p>
            </div>
          </div>

          <div>
            <h3 className="text-sm font-semibold text-gray-900 mb-3">Riwayat NDVI</h3>

            {loading && (
              <div className="flex items-center justify-center py-8 text-gray-400">
                <Loader2 className="w-5 h-5 animate-spin mr-2" />
                <span className="text-sm">Memuat riwayat...</span>
              </div>
            )}

            {error && (
              <div className="text-center py-4">
                <p className="text-xs text-red-500">{error}</p>
              </div>
            )}

            {!loading && !error && history && history.history.length > 0 && (
              <div className="space-y-2">
                <div className="grid grid-cols-[80px_1fr_auto] gap-2 text-xs font-medium text-gray-500 px-3">
                  <span>Tanggal</span>
                  <span>NDVI</span>
                  <span>Trend</span>
                </div>
                {history.history.map((point: HistoryPoint, i: number) => (
                  <div
                    key={point.image_date}
                    className="grid grid-cols-[80px_1fr_auto] gap-2 items-center bg-gray-50 rounded-lg px-3 py-2 text-sm"
                  >
                    <span className="text-gray-500">
                      {new Date(point.image_date).toLocaleDateString("id-ID", { day: "numeric", month: "short", year: "numeric" })}
                    </span>
                    <span className="font-medium text-gray-800">{point.ndvi_mean.toFixed(4)}</span>
                    {i > 0 && <TrendIcon current={point.ndvi_mean} previous={history.history[i - 1].ndvi_mean} />}
                    {i === 0 && <span className="text-gray-300 text-xs">base</span>}
                  </div>
                ))}
              </div>
            )}

            {!loading && !error && (!history || history.history.length === 0) && (
              <p className="text-sm text-gray-400 text-center py-4">Tidak ada data riwayat</p>
            )}
          </div>

          <div className="bg-amber-50 border border-amber-200 rounded-lg p-4">
            <div className="flex items-start gap-2">
              <AlertTriangle className="w-4 h-4 text-amber-600 mt-0.5 shrink-0" />
              <div>
                <p className="text-sm font-medium text-amber-800">
                  {riskFlag
                    ? "Zona ini memerlukan perhatian khusus."
                    : "Zona ini dalam kondisi baik."}
                </p>
                <p className="text-xs text-amber-700 mt-1">
                  {riskFlag
                    ? "Status lahan kosong/air atau tren NDVI menurun. Disarankan intervensi reklamasi."
                    : "Tren NDVI positif atau stabil. Lanjutkan pemantauan rutin."}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
