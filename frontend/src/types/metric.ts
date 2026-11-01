export interface Metric {
  id: number;
  frame_id: number;
  peak_pressure: number;
  contact_area_percent: number;
  high_pressure_region: HighPressureRegion | null;
  alert_generated: boolean;
  created_at: string;
}

export interface MetricWithFrame extends Metric {
  frame_captured_at: string;
  user_id: number;
}

export interface HighPressureRegion {
  x1: number;
  y1: number;
  x2: number;
  y2: number;
  area: number;
}

export interface MetricsSummary {
  avg_peak_pressure: number;
  max_peak_pressure: number;
  min_peak_pressure: number;
  avg_contact_area: number;
  total_alerts: number;
  frames_analyzed: number;
}
