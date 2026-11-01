"""Pytest configuration and fixtures for testing"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, JSON
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from datetime import datetime, timezone, timedelta
import json

# Patch JSONB to use JSON for SQLite compatibility
import sqlalchemy.dialects.postgresql as postgresql_dialects
postgresql_dialects.JSONB = JSON

from app.main import app
from app.database import Base, get_db
from app.models.user import User, UserRole
from app.models.group import UserGroup, group_membership
from app.models.frame import Frame
from app.models.metric import Metric
from app.models.alert import Alert, AlertSeverity
from app.models.comment import Comment
from app.models.movement_event import MovementEvent
from app.models.risk_score import RiskScore
from app.models.posture_label import PostureLabel
from app.services.auth_service import AuthService
from app.rate_limit import limiter
from app.utils.pressure_matrix import encode_matrix
import numpy as np

# Fixtures log in repeatedly; the 5/minute login limit would turn that into 429s
limiter.enabled = False


# Create in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Code that opens its own session (e.g. the cached metrics summary) must use the test DB
import app.database as app_database
app_database.SessionLocal = TestingSessionLocal


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test"""
    # Create tables
    Base.metadata.create_all(bind=engine)

    # Create session
    session = TestingSessionLocal()

    try:
        yield session
    finally:
        session.close()
        # Drop all tables after test
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with database session override"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def test_patient(db_session):
    """Create a test patient user"""
    patient = User(
        email="patient@test.com",
        password_hash=AuthService.hash_password("password123"),
        role=UserRole.patient,
        name="Test Patient"
    )
    db_session.add(patient)
    db_session.commit()
    db_session.refresh(patient)
    return patient


@pytest.fixture
def test_clinician(db_session):
    """Create a test clinician user"""
    clinician = User(
        email="clinician@test.com",
        password_hash=AuthService.hash_password("password123"),
        role=UserRole.clinician,
        name="Test Clinician"
    )
    db_session.add(clinician)
    db_session.commit()
    db_session.refresh(clinician)
    return clinician


@pytest.fixture
def test_admin(db_session):
    """Create a test admin user"""
    admin = User(
        email="admin@test.com",
        password_hash=AuthService.hash_password("password123"),
        role=UserRole.clinician,  # Use clinician role instead of admin
        name="Test Admin"
    )
    db_session.add(admin)
    db_session.commit()
    db_session.refresh(admin)
    return admin


@pytest.fixture
def test_group(db_session, test_clinician):
    """Create a test group with clinician"""
    group = UserGroup(
        name="Test Group",
        clinician_id=test_clinician.id
    )
    db_session.add(group)
    db_session.commit()
    db_session.refresh(group)
    return group


@pytest.fixture
def test_patient_in_group(db_session, test_group):
    """Create a patient assigned to test group"""
    patient = User(
        email="patient_in_group@test.com",
        password_hash=AuthService.hash_password("password123"),
        role=UserRole.patient,
        name="Patient In Group"
    )
    db_session.add(patient)
    db_session.commit()
    db_session.refresh(patient)

    # Add patient to group via group_membership
    from sqlalchemy import insert
    stmt = insert(group_membership).values(
        group_id=test_group.id,
        patient_id=patient.id
    )
    db_session.execute(stmt)
    db_session.commit()

    return patient


@pytest.fixture
def test_frame(db_session, test_patient):
    """Create a test frame for patient"""
    frame = Frame(
        user_id=test_patient.id,
        data=encode_matrix(np.zeros((32, 32), dtype=np.uint8)),
        captured_at=datetime.now(timezone.utc)
    )
    db_session.add(frame)
    db_session.commit()
    db_session.refresh(frame)
    return frame


@pytest.fixture
def test_metric(db_session, test_frame):
    """Create a test metric for frame"""
    metric = Metric(
        frame_id=test_frame.id,
        peak_pressure=150.5,
        contact_area_percent=45.2,
        high_pressure_region={"x1": 1, "y1": 1, "x2": 5, "y2": 5, "area": 25},
        alert_generated=False
    )
    db_session.add(metric)
    db_session.commit()
    db_session.refresh(metric)
    return metric


@pytest.fixture
def test_alert(db_session, test_frame):
    """Create a test alert"""
    alert = Alert(
        frame_id=test_frame.id,
        severity=AlertSeverity.MEDIUM,
        acknowledged=False
    )
    db_session.add(alert)
    db_session.commit()
    db_session.refresh(alert)
    return alert


@pytest.fixture
def auth_headers_patient(client, test_patient):
    """Get authentication headers for test patient"""
    response = client.post(
        "/api/auth/login",
        json={
            "email": "patient@test.com",
            "password": "password123"
        }
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def auth_headers_clinician(client, test_clinician):
    """Get authentication headers for test clinician"""
    response = client.post(
        "/api/auth/login",
        json={
            "email": "clinician@test.com",
            "password": "password123"
        }
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def auth_headers_admin(client, test_admin):
    """Get authentication headers for test admin"""
    response = client.post(
        "/api/auth/login",
        json={
            "email": "admin@test.com",
            "password": "password123"
        }
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def sample_pressure_matrix():
    """Generate a sample 16x32 pressure matrix"""
    return [[50 + (i * j) % 100 for j in range(32)] for i in range(16)]
