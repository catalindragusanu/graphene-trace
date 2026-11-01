export interface LoginRequest {
  email: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  user_id: number;
  role: string;
  name: string;
  date_of_birth?: string;
  medical_condition?: string;
  photo_url?: string;
}

export interface User {
  id: number;
  email: string;
  role: 'patient' | 'clinician';
  name: string;
  date_of_birth?: string;
  medical_condition?: string;
  photo_url?: string;
}
