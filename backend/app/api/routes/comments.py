"""Comments API routes"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.frame import Frame
from app.models.comment import Comment
from app.schemas.comment import CommentCreate, CommentResponse
from app.services.authorization_service import AuthorizationService

router = APIRouter()


@router.post("", response_model=CommentResponse)
def create_comment(
    request: CommentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new comment on a frame.

    Args:
        request: Comment data
        current_user: Current user
        db: Database session

    Returns:
        CommentResponse: Created comment
    """
    # Verify frame exists
    frame = db.query(Frame).filter(Frame.id == request.frame_id).first()
    if not frame:
        raise HTTPException(status_code=404, detail="Frame not found")

    AuthorizationService.require_patient_access(current_user, frame.user_id, db)

    # A reply must belong to the same frame
    if request.parent_comment_id is not None:
        parent = db.query(Comment).filter(
            Comment.id == request.parent_comment_id,
            Comment.frame_id == request.frame_id
        ).first()
        if not parent:
            raise HTTPException(status_code=404, detail="Parent comment not found on this frame")

    # Create comment
    comment = Comment(
        frame_id=request.frame_id,
        user_id=current_user.id,
        text=request.text,
        parent_comment_id=request.parent_comment_id
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)

    return CommentResponse(
        id=comment.id,
        frame_id=comment.frame_id,
        text=comment.text,
        parent_comment_id=comment.parent_comment_id,
        user_id=comment.user_id,
        user_name=current_user.name,
        user_role=current_user.role.value,
        created_at=comment.created_at,
        updated_at=comment.updated_at
    )


@router.get("", response_model=List[CommentResponse])
def get_comments(
    frame_id: int = Query(..., description="Frame ID to get comments for"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all comments for a frame.

    Args:
        frame_id: Frame ID
        current_user: Current user
        db: Database session

    Returns:
        List[CommentResponse]: List of comments
    """
    frame = db.query(Frame).filter(Frame.id == frame_id).first()
    if not frame:
        raise HTTPException(status_code=404, detail="Frame not found")

    AuthorizationService.require_patient_access(current_user, frame.user_id, db)

    comments = db.query(Comment, User).join(User, Comment.user_id == User.id).filter(
        Comment.frame_id == frame_id
    ).order_by(Comment.created_at).all()

    return [
        CommentResponse(
            id=comment.id,
            frame_id=comment.frame_id,
            text=comment.text,
            parent_comment_id=comment.parent_comment_id,
            user_id=comment.user_id,
            user_name=user.name,
            user_role=user.role.value,
            created_at=comment.created_at,
            updated_at=comment.updated_at
        )
        for comment, user in comments
    ]
