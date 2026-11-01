import api from './api';
import { MetricWithFrame, MetricsSummary } from '../types/metric';

export const metricsService = {
  async getMetrics(params?: {
    start_time?: string;
    end_time?: string;
    user_id?: number;
    limit?: number;
    offset?: number;
  }): Promise<MetricWithFrame[]> {
    const response = await api.get<MetricWithFrame[]>('/api/metrics', { params });
    return response.data;
  },

  async getSummary(params?: {
    start_time?: string;
    end_time?: string;
    user_id?: number;
  }): Promise<MetricsSummary> {
    const response = await api.get<MetricsSummary>('/api/metrics/summary', { params });
    return response.data;
  },

  async getMetricsSummary(params?: {
    start_time?: string;
    end_time?: string;
    user_id?: number;
  }): Promise<MetricsSummary> {
    return this.getSummary(params);
  },
};
