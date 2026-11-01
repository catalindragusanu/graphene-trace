export interface FrameSummary {
  id: number;
  user_id: number;
  captured_at: string;
  has_metrics: boolean;
  has_alerts: boolean;
  average_pressure?: number;
  max_pressure?: number;
}

export interface Frame {
  id: number;
  user_id: number;
  captured_at: string;
  data: number[][];  // 32x32 matrix
  created_at: string;
}
