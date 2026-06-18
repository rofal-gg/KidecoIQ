"use client";

import { useState, useEffect, useCallback } from "react";
import dynamic from "next/dynamic";
import StatsGrid from "@/components/reklamasi/StatsGrid";
import ZoneCard from "@/components/reklamasi/ZoneCard";
import ZoneDetailSheet from "@/components/reklamasi/ZoneDetailSheet";
import { Layers, Map as MapIcon, AlertCircle, RefreshCw } from "lucide-react";
import { fetchApi } from "@/lib/api";
import type { ZoneResponse, ReportResponse } from "@/types/reklamasi";

const ZoneMap = dynamic(() => import("@/components/reklamasi/ZoneMap"), {
  ssr: false,
  loading: () => (
    <div className="w-full h-full flex items-center justify-center bg-gray-100 rounded-xl">
      <div className="flex items-center gap-2 text-gray-400">
        <MapIcon className="w-5 h-5 animate-pulse" />
        <span className="text-sm">Memuat peta...</span>
      </div>
    </div>
  ),
});

function LoadingSkeleton() {
  return (
    <div className="h-screen flex flex-col animate-pulse">
      <div className="shrink-0 border-b border-gray-200 bg-white px-6 py-4">
        <div className="h-6 w-32 bg-gray-200 rounded" />
        <div className="h-4 w-64 bg-gray-100 rounded mt-2" />
      </div>
      <div className="flex-1 p-6 space-y-4">
        <div className="grid grid-cols-4 gap-4">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="h-20 bg-gray-100 rounded-xl" />
          ))}
        </div>
        <div className="flex-1 bg-gray-100 rounded-xl" />
      </div>
    </div>
  );
}

function ErrorBanner({ message, onRetry }: { message: string; onRetry: () => void }) {
  return (
    <div className="h-screen flex flex-col items-center justify-center p-6">
      <div className="bg-red-50 border border-red-200 rounded-xl p-6 max-w-md text-center">
        <AlertCircle className="w-10 h-10 text-red-400 mx-auto mb-3" />
        <h2 className="text-lg font-semibold text-red-800 mb-2">Gagal Memuat Data</h2>
        <p className="text-sm text-red-600 mb-4">{message}</p>
        <button
          onClick={onRetry}
          className="inline-flex items-center gap-2 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 text-sm font-medium transition-colors"
        >
          <RefreshCw className="w-4 h-4" />
          Coba Lagi
        </button>
      </div>
    </div>
  );
}

export default function ReklamasiPage() {
  const [zones, setZones] = useState<ZoneResponse[]>([]);
  const [report, setReport] = useState<ReportResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedZone, setSelectedZone] = useState<ZoneResponse | null>(null);
  const [showDetail, setShowDetail] = useState(false);

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [zonesResult, reportResult] = await Promise.all([
        fetchApi<ZoneResponse[]>("/reklamasi/zones"),
        fetchApi<ReportResponse>("/reklamasi/report"),
      ]);
      setZones(zonesResult);
      setReport(reportResult);
    } catch (err) {
      const message = err instanceof Error ? err.message : "Terjadi kesalahan";
      setError(message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handleSelectZone = (zone: ZoneResponse) => {
    setSelectedZone(zone);
    setShowDetail(true);
  };

  if (loading) return <LoadingSkeleton />;
  if (error) return <ErrorBanner message={error} onRetry={fetchData} />;
  if (!report) return null;

  return (
    <div className="h-screen flex flex-col">
      <header className="shrink-0 border-b border-gray-200 bg-white px-6 py-4">
        <div className="flex items-center gap-2">
          <Layers className="w-5 h-5 text-emerald-600" />
          <h1 className="text-lg font-semibold text-gray-900">Reklamasi</h1>
        </div>
        <p className="text-sm text-gray-500 mt-0.5">
          Monitoring progres reklamasi lahan pascatambang — Area Roto Samurangau
        </p>
      </header>

      <div className="flex-1 flex overflow-hidden">
        <div className="flex-1 flex flex-col">
          <div className="shrink-0 px-6 pt-4 pb-2">
            <StatsGrid report={report} />
          </div>

          <div className="flex-1 px-6 pb-4">
            <div className="w-full h-full rounded-xl overflow-hidden border border-gray-200 shadow-sm">
              <ZoneMap
                zones={zones}
                selectedId={selectedZone?.id ?? null}
                onSelectZone={handleSelectZone}
              />
            </div>
          </div>
        </div>

        <aside className="w-80 shrink-0 border-l border-gray-200 bg-white overflow-y-auto">
          <div className="px-4 py-3 border-b border-gray-100">
            <h2 className="text-sm font-semibold text-gray-900">Zona Reklamasi</h2>
            <p className="text-xs text-gray-400">{zones.length} zona dipantau</p>
          </div>
          <div className="p-3 space-y-2">
            {zones.map((zone) => (
              <ZoneCard
                key={zone.id}
                zone={zone}
                selected={selectedZone?.id === zone.id}
                onClick={() => handleSelectZone(zone)}
              />
            ))}
          </div>
        </aside>
      </div>

      {showDetail && selectedZone && (
        <ZoneDetailSheet
          zone={selectedZone}
          onClose={() => {
            setShowDetail(false);
            setSelectedZone(null);
          }}
        />
      )}
    </div>
  );
}
