import api from './api';
import { Comment, CommentCreate } from '../types/comment';

export const commentService = {
  async getComments(frameId: number): Promise<Comment[]> {
    const response = await api.get<Comment[]>('/api/comments', {
      params: { frame_id: frameId },
    });
    return response.data;
  },

  async createComment(comment: CommentCreate): Promise<Comment> {
    const response = await api.post<Comment>('/api/comments', comment);
    return response.data;
  },
};
