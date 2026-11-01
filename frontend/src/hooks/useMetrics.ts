import { useQuery } from '@tanstack/react-query';
import { metricsService } from '../services/metricsService';

interface UseMetricsParams {
  start_time?: string;
  end_time?: string;
  user_id?: number;
  limit?: number;
  offset?: number;
}

export const useMetrics = (params?: UseMetricsParams) => {
  return useQuery({
    queryKey: ['metrics', params],
    queryFn: () => metricsService.getMetrics(params),
    staleTime: 5 * 60 * 1000, // 5 minutes
    refetchOnWindowFocus: false,
  });
};

export const useMetricsSummary = (params?: { start_time?: string; end_time?: string; user_id?: number }) => {
  return useQuery({
    queryKey: ['metrics-summary', params],
    queryFn: () => metricsService.getMetricsSummary(params),
    staleTime: 5 * 60 * 1000, // 5 minutes
    refetchOnWindowFocus: false,
  });
};
