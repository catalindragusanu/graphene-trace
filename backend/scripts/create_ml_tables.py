"""
Simple SQL migration script for ML tables.
Run this if you don't have Alembic set up.

Usage:
    python backend/scripts/create_ml_tables.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.database import engine
from sqlalchemy import text

def create_ml_tables():
    """Create ML-related tables"""
    
    sql_statements = [
        # Movement Events Table
        """
        CREATE TABLE IF NOT EXISTS movement_events (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            from_frame_id INTEGER NOT NULL REFERENCES frames(id) ON DELETE CASCADE,
            to_frame_id INTEGER NOT NULL REFERENCES frames(id) ON DELETE CASCADE,
            movement_type VARCHAR(10) NOT NULL,
            quality_score FLOAT NOT NULL,
            metrics JSONB,
            detected_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """,
        
        # Indexes for movement_events
        """
        CREATE INDEX IF NOT EXISTS ix_movement_events_user_id ON movement_events(user_id);
        """,
        """
        CREATE INDEX IF NOT EXISTS ix_movement_events_detected_at ON movement_events(detected_at);
        """,
        
        # Risk Scores Table
        """
        CREATE TABLE IF NOT EXISTS risk_scores (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            score INTEGER NOT NULL,
            factors JSONB,
            calculated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """,
        
        # Indexes for risk_scores
        """
        CREATE INDEX IF NOT EXISTS ix_risk_scores_user_id ON risk_scores(user_id);
        """,
        """
        CREATE INDEX IF NOT EXISTS ix_risk_scores_calculated_at ON risk_scores(calculated_at);
        """,
        
        # Posture Labels Table
        """
        CREATE TABLE IF NOT EXISTS posture_labels (
            id SERIAL PRIMARY KEY,
            frame_id INTEGER NOT NULL REFERENCES frames(id) ON DELETE CASCADE,
            posture VARCHAR(20) NOT NULL,
            labeled_by INTEGER NOT NULL REFERENCES users(id),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """,
        
        # Indexes for posture_labels
        """
        CREATE INDEX IF NOT EXISTS ix_posture_labels_frame_id ON posture_labels(frame_id);
        """,
    ]
    
    with engine.connect() as conn:
        for sql in sql_statements:
            try:
                conn.execute(text(sql))
                conn.commit()
            except Exception as e:
                print(f"Error executing SQL: {e}")
                print(f"SQL: {sql[:100]}...")
                conn.rollback()
    
    print("✓ ML tables created successfully!")
    print("\nCreated tables:")
    print("  - movement_events")
    print("  - risk_scores")
    print("  - posture_labels")

if __name__ == "__main__":
    print("Creating ML tables...")
    create_ml_tables()
