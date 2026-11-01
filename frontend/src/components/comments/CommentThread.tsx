import React from 'react';
import { Comment } from '../../types/comment';
import '../../styles/CommentThread.css';

interface CommentThreadProps {
  comments: Comment[];
  onReply?: (parentId: number) => void;
}

export const CommentThread: React.FC<CommentThreadProps> = ({ comments, onReply }) => {
  const renderComment = (comment: Comment, depth: number = 0) => {
    const isPatient = comment.user_role === 'patient';
    const replies = comments.filter(reply => reply.parent_comment_id === comment.id);

    return (
      <div key={comment.id} className={`comment depth-${Math.min(depth, 3)}`}>
        <div className="comment-header">
          <div className="comment-author">
            <span className={`author-name ${isPatient ? 'patient' : 'clinician'}`}>
              {comment.user_name}
            </span>
            <span className={`role-badge ${isPatient ? 'badge-patient' : 'badge-clinician'}`}>
              {comment.user_role}
            </span>
          </div>
          <div className="comment-time">
            {formatRelativeTime(new Date(comment.created_at))}
          </div>
        </div>

        <div className="comment-text">
          {comment.text}
        </div>

        <div className="comment-actions">
          {onReply && (
            <button
              className="reply-btn"
              onClick={() => onReply(comment.id)}
            >
              Reply
            </button>
          )}
        </div>

        {replies && replies.length > 0 && (
          <div className="comment-replies">
            {replies.map(reply => renderComment(reply, depth + 1))}
          </div>
        )}
      </div>
    );
  };

  if (comments.length === 0) {
    return (
      <div className="comment-thread empty">
        <p>No comments yet</p>
      </div>
    );
  }

  return (
    <div className="comment-thread">
      {comments
        .filter(comment => comment.parent_comment_id === null ||
          !comments.some(parent => parent.id === comment.parent_comment_id))
        .map(comment => renderComment(comment))}
    </div>
  );
};

function formatRelativeTime(date: Date): string {
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffSec = Math.floor(diffMs / 1000);
  const diffMin = Math.floor(diffSec / 60);
  const diffHour = Math.floor(diffMin / 60);
  const diffDay = Math.floor(diffHour / 24);

  if (diffSec < 60) return 'just now';
  if (diffMin < 60) return `${diffMin}m ago`;
  if (diffHour < 24) return `${diffHour}h ago`;
  if (diffDay < 7) return `${diffDay}d ago`;

  return date.toLocaleDateString();
}
