"""Add ML tables (movement_events, risk_scores, posture_labels)

Moved from the unused migrations/ directory so that `alembic upgrade head`
actually creates these tables. Table creation is skipped when a table already
exists, so databases that got them via the old script are unaffected.

Revision ID: d4a7c9e1b2f3
Revises: c148f82b9ccf
Create Date: 2026-01-08 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import context, op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'd4a7c9e1b2f3'
down_revision: Union[str, None] = 'c148f82b9ccf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _existing_tables() -> set:
    # Offline (--sql) mode has no live connection to inspect
    if context.is_offline_mode():
        return set()
    return set(sa.inspect(op.get_bind()).get_table_names())


def upgrade() -> None:
    existing = _existing_tables()

    if 'movement_events' not in existing:
        op.create_table(
            'movement_events',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('user_id', sa.Integer(), nullable=False),
            sa.Column('from_frame_id', sa.Integer(), nullable=False),
            sa.Column('to_frame_id', sa.Integer(), nullable=False),
            sa.Column('movement_type', sa.String(length=10), nullable=False),
            sa.Column('quality_score', sa.Float(), nullable=False),
            sa.Column('metrics', postgresql.JSON(astext_type=sa.Text()), nullable=True),
            sa.Column('detected_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
            sa.ForeignKeyConstraint(['from_frame_id'], ['frames.id']),
            sa.ForeignKeyConstraint(['to_frame_id'], ['frames.id']),
            sa.ForeignKeyConstraint(['user_id'], ['users.id']),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_movement_events_id'), 'movement_events', ['id'], unique=False)
        op.create_index(op.f('ix_movement_events_user_id'), 'movement_events', ['user_id'], unique=False)

    if 'risk_scores' not in existing:
        op.create_table(
            'risk_scores',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('user_id', sa.Integer(), nullable=False),
            sa.Column('score', sa.Integer(), nullable=False),
            sa.Column('factors', postgresql.JSON(astext_type=sa.Text()), nullable=True),
            sa.Column('calculated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
            sa.ForeignKeyConstraint(['user_id'], ['users.id']),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_risk_scores_id'), 'risk_scores', ['id'], unique=False)
        op.create_index(op.f('ix_risk_scores_user_id'), 'risk_scores', ['user_id'], unique=False)
        op.create_index(op.f('ix_risk_scores_calculated_at'), 'risk_scores', ['calculated_at'], unique=False)

    if 'posture_labels' not in existing:
        op.create_table(
            'posture_labels',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('frame_id', sa.Integer(), nullable=False),
            sa.Column('posture', sa.String(length=20), nullable=False),
            sa.Column('labeled_by', sa.Integer(), nullable=False),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
            sa.ForeignKeyConstraint(['frame_id'], ['frames.id']),
            sa.ForeignKeyConstraint(['labeled_by'], ['users.id']),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_posture_labels_id'), 'posture_labels', ['id'], unique=False)
        op.create_index(op.f('ix_posture_labels_frame_id'), 'posture_labels', ['frame_id'], unique=False)


def downgrade() -> None:
    op.drop_table('posture_labels')
    op.drop_table('risk_scores')
    op.drop_table('movement_events')
