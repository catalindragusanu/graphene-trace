import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { commentService } from '../services/commentService';
import { CommentCreate } from '../types/comment';

export const useComments = (frameId: number) => {
  return useQuery({
    queryKey: ['comments', frameId],
    queryFn: () => commentService.getComments(frameId),
    staleTime: 2 * 60 * 1000, // 2 minutes
    enabled: !!frameId,
  });
};

export const useCreateComment = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (request: CommentCreate) => commentService.createComment(request),
    onSuccess: (_, variables) => {
      // Invalidate comments for the specific frame
      queryClient.invalidateQueries({ queryKey: ['comments', variables.frame_id] });
    },
  });
};
