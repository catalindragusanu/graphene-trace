export interface Comment {
  id: number;
  frame_id: number;
  user_id: number;
  user_name: string;
  user_role: string;
  text: string;
  parent_comment_id: number | null;
  created_at: string;
  updated_at: string | null;
}

export interface CommentCreate {
  frame_id: number;
  text: string;
  parent_comment_id?: number | null;
}
