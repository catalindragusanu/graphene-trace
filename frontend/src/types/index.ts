// User types
export interface User {
  id: number;
  email: string;
  name: string;
  role: 'patient' | 'clinician';
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  user_id: number;
  email: string;
  name: string;
  role: 'patient' | 'clinician';
}

// Frame types
export interface FrameSummary {
  id: number;
  user_id: number;
  captured_at: string;
  has_alert: boolean;
  has_metrics: boolean;
}

export interface Frame {
  id: number;
  user_id: number;
  captured_at: string;
  data: number[][]; // 32x32 matrix
}

// Metric types
export interface HighPressureRegion {
  x1: number;
  y1: number;
  x2: number;
  y2: number;
  area: number;
}

export interface Metric {
  id: number;
  frame_id: number;
  peak_pressure: number;
  contact_area_percent: number;
  high_pressure_region: HighPressureRegion | null;
  alert_generated: boolean;
  created_at: string;
  frame: {
    captured_at: string;
    user_id: number;
  };
}

export interface MetricsSummary {
  total_frames: number;
  avg_peak_pressure: number;
  max_peak_pressure: number;
  avg_contact_area: number;
  alert_count: number;
  period_start: string;
  period_end: string;
}

// Alert types
export type AlertSeverity = 'low' | 'medium' | 'high';

export interface Alert {
  id: number;
  frame_id: number;
  severity: AlertSeverity;
  region: HighPressureRegion;
  acknowledged: boolean;
  acknowledged_by: number | null;
  acknowledged_at: string | null;
  created_at: string;
  frame: {
    captured_at: string;
    user_id: number;
  };
}

// Comment types
export interface Comment {
  id: number;
  frame_id: number;
  user_id: number;
  text: string;
  parent_comment_id: number | null;
  created_at: string;
  user: {
    name: string;
    role: 'patient' | 'clinician';
  };
  replies?: Comment[];
}

export interface CreateCommentRequest {
  frame_id: number;
  text: string;
  parent_comment_id?: number;
}

// Group types
export interface Group {
  id: number;
  name: string;
  clinician_id: number;
  created_at: string;
}

export interface GroupMember {
  user_id: number;
  group_id: number;
  added_at: string;
  user: User;
}

export interface CreateGroupRequest {
  name: string;
}

export interface AddGroupMemberRequest {
  user_id: number;
}
