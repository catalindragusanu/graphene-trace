import api from './api';
import { LoginRequest, TokenResponse, User } from '../types/auth';

export const authService = {
  async login(credentials: LoginRequest): Promise<TokenResponse> {
    const response = await api.post<TokenResponse>('/api/auth/login', credentials);
    const data = response.data;

    // Store token and user info
    localStorage.setItem('access_token', data.access_token);
    localStorage.setItem('user', JSON.stringify({
      id: data.user_id,
      email: credentials.email,
      role: data.role,
      name: data.name,
      date_of_birth: data.date_of_birth,
      medical_condition: data.medical_condition,
      photo_url: data.photo_url,
    }));

    return data;
  },

  logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
  },

  getCurrentUser(): User | null {
    const userStr = localStorage.getItem('user');
    if (!userStr) return null;

    try {
      return JSON.parse(userStr);
    } catch {
      return null;
    }
  },

  isAuthenticated(): boolean {
    return !!localStorage.getItem('access_token');
  },
};
