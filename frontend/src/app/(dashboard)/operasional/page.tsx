"use client";

import { useState, useEffect, useCallback } from "react";
import { BarChart3, Truck, AlertTriangle, Fuel, Gauge, AlertCircle, RefreshCw } from "lucide-react";
import Badge from "@/components/ui/Badge";
import { fetchApi } from "@/lib/api";
import type { FleetUnitResponse, AlertsResponse } from "@/types/operasional";

function LoadingSkeleton() {
  return (
    <div className="h-screen flex flex-col animate-pulse">
      <div className="shrink-0 border-b border-gray-200 bg-white px-6 py-4">
        <div className="h-6 w-32 bg-gray-200 rounded" />
        <div className="h-4 w-64 bg-gray-100 rounded mt-2" />
      </div>
      <div className="flex-1 p-6">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="h-96 bg-gray-100 rounded-xl" />
          <div className="space-y-4">
            <div className="h-64 bg-gray-100 rounded-xl" />
            <div className="h-32 bg-gray-100 rounded-xl" />
          </div>
        </div>
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

export default function OperasionalPage() {
  const [fleet, setFleet] = useState<FleetUnitResponse[]>([]);
  const [alerts, setAlerts] = useState<AlertsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [fleetResult, alertsResult] = await Promise.all([
        fetchApi<FleetUnitResponse[]>("/operasional/fleet"),
        fetchApi<AlertsResponse>("/operasional/alerts"),
      ]);
      setFleet(fleetResult);
      setAlerts(alertsResult);
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

  const statusVariant = (s: string) => {
    switch (s) {
      case "active": return "success" as const;
      case "idle": return "warning" as const;
      case "maintenance": return "danger" as const;
      default: return "default" as const;
    }
  };

  const alertVariant = (l: string) => {
    switch (l) {
      case "high": return "danger" as const;
      case "medium": return "warning" as const;
      default: return "default" as const;
    }
  };

  if (loading) return <LoadingSkeleton />;
  if (error) return <ErrorBanner message={error} onRetry={fetchData} />;

  return (
    <div className="h-screen flex flex-col">
      <header className="shrink-0 border-b border-gray-200 bg-white px-6 py-4">
        <div className="flex items-center gap-2">
          <Truck className="w-5 h-5 text-emerald-600" />
          <h1 className="text-lg font-semibold text-gray-900">Operasional</h1>
        </div>
        <p className="text-sm text-gray-500 mt-0.5">
          Monitoring efisiensi fleet alat berat dan peringatan dini maintenance
        </p>
      </header>

      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-white rounded-xl border border-gray-200 p-4">
            <div className="flex items-center gap-2 mb-4">
              <BarChart3 className="w-4 h-4 text-emerald-600" />
              <h2 className="text-sm font-semibold text-gray-900">Status Fleet</h2>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-gray-100">
                    <th className="text-left py-2 pr-4 text-xs font-medium text-gray-400">Unit</th>
                    <th className="text-left py-2 pr-4 text-xs font-medium text-gray-400">Model</th>
                    <th className="text-center py-2 pr-4 text-xs font-medium text-gray-400">Status</th>
                    <th className="text-right py-2 pr-4 text-xs font-medium text-gray-400">Idle %</th>
                    <th className="text-right py-2 pr-4 text-xs font-medium text-gray-400">BBM (L)</th>
                    <th className="text-right py-2 pr-4 text-xs font-medium text-gray-400">Jam</th>
                    <th className="text-right py-2 text-xs font-medium text-gray-400">Risiko</th>
                  </tr>
                </thead>
                <tbody>
                  {fleet.map((unit) => (
                    <tr key={unit.unit_id} className="border-b border-gray-50 hover:bg-gray-50">
                      <td className="py-2 pr-4 font-medium text-gray-900">{unit.unit_id}</td>
                      <td className="py-2 pr-4 text-gray-500 text-xs">{unit.model}</td>
                      <td className="py-2 pr-4 text-center">
                        <Badge variant={statusVariant(unit.status)}>
                          {unit.status}
                        </Badge>
                      </td>
                      <td className="py-2 pr-4 text-right text-gray-800">{unit.idle_ratio_avg.toFixed(1)}</td>
                      <td className="py-2 pr-4 text-right text-gray-800">{unit.fuel_avg.toFixed(1)}</td>
                      <td className="py-2 pr-4 text-right text-gray-800">{unit.total_hours.toFixed(0)}</td>
                      <td className="py-2 text-right">
                        <span className={`inline-flex items-center gap-1 text-xs font-medium ${
                          unit.risk_score >= 70 ? "text-red-600" :
                          unit.risk_score >= 40 ? "text-amber-600" :
                          "text-gray-600"
                        }`}>
                          <Gauge className="w-3 h-3" />
                          {unit.risk_score.toFixed(0)}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          <div className="space-y-4">
            <div className="bg-white rounded-xl border border-gray-200 p-4">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2">
                  <AlertTriangle className="w-4 h-4 text-amber-600" />
                  <h2 className="text-sm font-semibold text-gray-900">Peringatan Dini</h2>
                </div>
                {alerts && (
                  <Badge variant="danger">{alerts.total_alerts} aktif</Badge>
                )}
              </div>

              <div className="space-y-3">
                {alerts && alerts.alerts.length > 0 ? (
                  alerts.alerts.map((alert) => (
                    <div key={alert.unit_id} className="bg-gray-50 rounded-lg p-3">
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-sm font-semibold text-gray-900">{alert.unit_id}</span>
                        <Badge variant={alertVariant(alert.alert_level)}>
                          {alert.alert_level}
                        </Badge>
                      </div>
                      <p className="text-xs text-gray-600 mb-1">{alert.message}</p>
                      <p className="text-xs text-gray-400 italic">{alert.recommendation}</p>
                    </div>
                  ))
                ) : (
                  <p className="text-sm text-gray-400 text-center py-4">Tidak ada peringatan aktif</p>
                )}
              </div>
            </div>

            <div className="bg-white rounded-xl border border-gray-200 p-4">
              <div className="flex items-center gap-2 mb-3">
                <Fuel className="w-4 h-4 text-emerald-600" />
                <h2 className="text-sm font-semibold text-gray-900">Ringkasan Fleet</h2>
              </div>
              <div className="grid grid-cols-3 gap-3 text-center">
                <div className="bg-emerald-50 rounded-lg p-3">
                  <p className="text-xs text-gray-500">Aktif</p>
                  <p className="text-xl font-bold text-emerald-700">
                    {fleet.filter((u) => u.status === "active").length}
                  </p>
                </div>
                <div className="bg-amber-50 rounded-lg p-3">
                  <p className="text-xs text-gray-500">Idle</p>
                  <p className="text-xl font-bold text-amber-700">
                    {fleet.filter((u) => u.status === "idle").length}
                  </p>
                </div>
                <div className="bg-red-50 rounded-lg p-3">
                  <p className="text-xs text-gray-500">Maintenance</p>
                  <p className="text-xl font-bold text-red-700">
                    {fleet.filter((u) => u.status === "maintenance").length}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
