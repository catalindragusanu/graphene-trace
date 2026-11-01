import api from './api';
import { AlertWithFrame } from '../types/alert';

export const alertService = {
  async getAlerts(params?: {
    severity?: string;
    acknowledged?: boolean;
    user_id?: number;
    limit?: number;
    offset?: number;
  }): Promise<AlertWithFrame[]> {
    const response = await api.get<AlertWithFrame[]>('/api/alerts', { params });
    return response.data;
  },

  // The backend exposes a paginated list, but no single-alert GET route.
  async getAlert(id: number): Promise<AlertWithFrame> {
    const limit = 1000;
    for (let offset = 0; ; offset += limit) {
      const alerts = await alertService.getAlerts({ limit, offset });
      const alert = alerts.find(alert => alert.id === id);
      if (alert) return alert;
      if (alerts.length < limit) throw new Error('Alert not found');
    }
  },

  async acknowledgeAlert(id: number, acknowledged: boolean): Promise<void> {
    await api.patch(`/api/alerts/${id}/acknowledge`, { acknowledged });
  },
};
