export interface FleetUnitResponse {
  unit_id: string;
  model: string;
  status: "active" | "idle" | "maintenance";
  idle_ratio_avg: number;
  fuel_avg: number;
  total_hours: number;
  risk_score: number;
  alert_level: "low" | "medium" | "high";
}

export interface AnomalyPoint {
  shift: number;
  idle_ratio: number;
  fuel_consumption: number;
  anomaly_score: -1 | 1;
  anomaly_label: "anomaly" | "normal";
}

export interface AnomalyResponse {
  unit_id: string;
  shifts: AnomalyPoint[];
}

export interface AlertItem {
  unit_id: string;
  alert_level: string;
  risk_score: number;
  message: string;
  recommendation: string;
}

export interface AlertsResponse {
  alerts: AlertItem[];
  total_alerts: number;
  generated_at: string;
}
