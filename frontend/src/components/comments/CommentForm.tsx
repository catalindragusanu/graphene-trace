import React, { useState } from 'react';
import { useCreateComment } from '../../hooks/useComments';
import '../../styles/CommentForm.css';

interface CommentFormProps {
  frameId: number;
  parentCommentId?: number;
  onSuccess?: () => void;
  onCancel?: () => void;
}

export const CommentForm: React.FC<CommentFormProps> = ({
  frameId,
  parentCommentId,
  onSuccess,
  onCancel
}) => {
  const [text, setText] = useState('');
  const createComment = useCreateComment();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!text.trim()) {
      return;
    }

    try {
      await createComment.mutateAsync({
        frame_id: frameId,
        text: text.trim(),
        parent_comment_id: parentCommentId,
      });

      setText('');
      if (onSuccess) {
        onSuccess();
      }
    } catch (error) {
      console.error('Failed to create comment:', error);
    }
  };

  return (
    <form className="comment-form" onSubmit={handleSubmit}>
      <div className="form-header">
        <h3>{parentCommentId ? 'Reply to comment' : 'Add a comment'}</h3>
      </div>

      <textarea
        className="comment-input"
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder={parentCommentId ? 'Write a reply...' : 'Write a comment...'}
        rows={4}
        maxLength={1000}
        disabled={createComment.isPending}
      />

      <div className="form-footer">
        <div className="char-count">
          {text.length}/1000
        </div>
        <div className="form-actions">
          {onCancel && (
            <button
              type="button"
              className="cancel-btn"
              onClick={onCancel}
              disabled={createComment.isPending}
            >
              Cancel
            </button>
          )}
          <button
            type="submit"
            className="submit-btn"
            disabled={!text.trim() || createComment.isPending}
          >
            {createComment.isPending ? 'Posting...' : parentCommentId ? 'Post Reply' : 'Post Comment'}
          </button>
        </div>
      </div>

      {createComment.isError && (
        <div className="error-message">
          Failed to post comment. Please try again.
        </div>
      )}
    </form>
  );
};
