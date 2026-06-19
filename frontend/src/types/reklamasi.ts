export type ZoneStatus = "air" | "lahan_kosong" | "vegetasi_stres" | "vegetasi_sehat";

export interface ZoneResponse {
  id: string;
  name: string;
  status: ZoneStatus;
  ndvi_latest: number;
  area_ha: number;
  vegetation_cover_pct: number;
  trend_prediction: string;
  updated_at: string;
  southwest_lat: number;
  southwest_lng: number;
  northeast_lat: number;
  northeast_lng: number;
}

export interface HistoryPoint {
  image_date: string;
  ndvi_mean: number;
  classification: string;
  vegetation_cover_pct: number;
}

export interface ZoneHistoryResponse {
  zone_id: string;
  zone_name: string;
  history: HistoryPoint[];
}

export interface StatusSummary {
  vegetasi_sehat: number;
  vegetasi_stres: number;
  lahan_kosong: number;
  air: number;
}

export interface ZoneReportItem {
  zone_id: string;
  name: string;
  status: string;
  ndvi_mean: number;
  area_ha: number;
  risk_flag: boolean;
}

export interface ReportResponse {
  generated_at: string;
  total_zones: number;
  status_summary: StatusSummary;
  overall_ndvi_mean: number;
  overall_vegetation_cover_pct: number;
  compliance_score: number;
  zones: ZoneReportItem[];
}
