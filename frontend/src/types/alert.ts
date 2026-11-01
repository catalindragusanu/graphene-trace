export type AlertSeverity = 'low' | 'medium' | 'high';

export interface Alert {
  id: number;
  frame_id: number;
  severity: AlertSeverity;
  region: {
    x1: number;
    y1: number;
    x2: number;
    y2: number;
    area: number;
  } | null;
  acknowledged: boolean;
  acknowledged_by: number | null;
  acknowledged_at: string | null;
  created_at: string;
}

export interface AlertWithFrame extends Alert {
  frame_captured_at: string;
  user_id: number;
  user_name: string;
}
