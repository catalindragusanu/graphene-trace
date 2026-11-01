import { useQuery } from '@tanstack/react-query';
import { frameService } from '../services/frameService';

export const useFrames = (params?: {
  start_time?: string;
  end_time?: string;
  user_id?: number;
  limit?: number;
}) => {
  return useQuery({
    queryKey: ['frames', params],
    queryFn: () => frameService.getFrames(params),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};

export const useFrame = (id: number) => {
  return useQuery({
    queryKey: ['frame', id],
    queryFn: () => frameService.getFrame(id),
    enabled: !!id,
    staleTime: 10 * 60 * 1000, // 10 minutes - frames don't change
  });
};
