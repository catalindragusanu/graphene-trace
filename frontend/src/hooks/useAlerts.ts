import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { alertService } from '../services/alertService';
import { AlertSeverity } from '../types/alert';

interface UseAlertsParams {
  severity?: AlertSeverity;
  acknowledged?: boolean;
  user_id?: number;
}

export const useAlerts = (params?: UseAlertsParams) => {
  return useQuery({
    queryKey: ['alerts', params],
    queryFn: () => alertService.getAlerts(params),
    staleTime: 30 * 1000, // 30 seconds
    refetchInterval: 60 * 1000, // Refetch every minute for new alerts
  });
};

export const useAlert = (id: number) => {
  return useQuery({
    queryKey: ['alert', id],
    queryFn: () => alertService.getAlert(id),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};

export const useAcknowledgeAlert = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (alertId: number) => alertService.acknowledgeAlert(alertId, true),
    onSuccess: () => {
      // Invalidate and refetch alerts
      queryClient.invalidateQueries({ queryKey: ['alerts'] });
      queryClient.invalidateQueries({ queryKey: ['alert'] });
    },
  });
};
