import api from './api';
import { Frame, FrameSummary } from '../types/frame';

export const frameService = {
  async getFrames(params?: {
    start_time?: string;
    end_time?: string;
    user_id?: number;
    limit?: number;
    offset?: number;
  }): Promise<FrameSummary[]> {
    const response = await api.get<FrameSummary[]>('/api/frames', { params });
    return response.data;
  },

  async getFrame(id: number): Promise<Frame> {
    const response = await api.get<Frame>(`/api/frames/${id}`);
    return response.data;
  },
};
