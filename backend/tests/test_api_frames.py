"""Integration tests for frames API endpoints"""
import pytest
from tests.helpers import blank_frame_bytes
from fastapi import status
from datetime import datetime, timezone
import json


class TestFramesEndpoints:
    """Test /api/frames endpoints"""

    @pytest.mark.skip(reason="POST /api/frames is not implemented (frames are ingested via scripts)")
    def test_create_frame_as_patient(self, client, auth_headers_patient, test_patient, sample_pressure_matrix):
        """Test patient can create frame for themselves"""
        response = client.post(
            "/api/frames",
            headers=auth_headers_patient,
            json={
                "user_id": test_patient.id,
                "data": json.dumps({
                    "matrix": sample_pressure_matrix,
                    "width": 32,
                    "height": 16
                }),
                "captured_at": datetime.now(timezone.utc).isoformat()
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["user_id"] == test_patient.id
        assert "id" in data

    @pytest.mark.skip(reason="POST /api/frames is not implemented (frames are ingested via scripts)")
    def test_create_frame_as_patient_for_other_user_forbidden(self, client, auth_headers_patient, test_admin, sample_pressure_matrix):
        """Test patient cannot create frame for another user"""
        response = client.post(
            "/api/frames",
            headers=auth_headers_patient,
            json={
                "user_id": test_admin.id,  # Different user
                "data": json.dumps({
                    "matrix": sample_pressure_matrix,
                    "width": 32,
                    "height": 16
                }),
                "captured_at": datetime.now(timezone.utc).isoformat()
            }
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_get_frames_as_patient(self, client, auth_headers_patient, test_frame, test_patient):
        """Test patient can get their own frames"""
        response = client.get("/api/frames", headers=auth_headers_patient)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        # All frames should belong to the patient
        for frame in data:
            assert frame["user_id"] == test_patient.id

    def test_get_frames_as_clinician_with_access(self, client, auth_headers_clinician, test_patient_in_group, test_group, db_session):
        """Test clinician can get frames for patients in their group"""
        # Create frame for patient in group
        from app.models.frame import Frame
        frame_data = {"matrix": [[0 for _ in range(32)] for _ in range(16)]}
        frame = Frame(
            user_id=test_patient_in_group.id,
            data=blank_frame_bytes(),
            captured_at=datetime.now(timezone.utc)
        )
        db_session.add(frame)
        db_session.commit()

        response = client.get(
            f"/api/frames?user_id={test_patient_in_group.id}",
            headers=auth_headers_clinician
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    def test_get_frames_as_clinician_without_access(self, client, auth_headers_clinician, test_patient):
        """Test clinician cannot get frames for patients not in their group"""
        response = client.get(
            f"/api/frames?user_id={test_patient.id}",
            headers=auth_headers_clinician
        )
        # Should return empty list or 403
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_403_FORBIDDEN]
        if response.status_code == status.HTTP_200_OK:
            data = response.json()
            assert len(data) == 0

    def test_get_frame_by_id_as_owner(self, client, auth_headers_patient, test_frame, test_patient):
        """Test patient can get their own frame by ID"""
        response = client.get(f"/api/frames/{test_frame.id}", headers=auth_headers_patient)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == test_frame.id
        assert data["user_id"] == test_patient.id

    def test_get_frame_by_id_as_other_patient_forbidden(self, client, db_session, test_patient, test_admin):
        """Test patient cannot get another patient's frame"""
        # Create frame for admin
        frame_data = {"matrix": [[0 for _ in range(32)] for _ in range(16)]}
        from app.models.frame import Frame
        admin_frame = Frame(
            user_id=test_admin.id,
            data=blank_frame_bytes(),
            captured_at=datetime.now(timezone.utc)
        )
        db_session.add(admin_frame)
        db_session.commit()
        db_session.refresh(admin_frame)

        # Login as patient
        response = client.post(
            "/api/auth/login",
            json={"email": "patient@test.com", "password": "password123"}
        )
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Try to access admin's frame
        response = client.get(f"/api/frames/{admin_frame.id}", headers=headers)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_get_frames_with_pagination(self, client, auth_headers_patient, test_patient, db_session):
        """Test frame pagination works correctly"""
        # Create multiple frames
        from app.models.frame import Frame
        for i in range(5):
            frame_data = {"matrix": [[i for _ in range(32)] for _ in range(16)]}
            frame = Frame(
                user_id=test_patient.id,
                data=blank_frame_bytes(),
                captured_at=datetime.now(timezone.utc)
            )
            db_session.add(frame)
        db_session.commit()

        # Test with limit
        response = client.get("/api/frames?limit=3", headers=auth_headers_patient)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) <= 3

    def test_get_frames_with_time_filter(self, client, auth_headers_patient, test_frame):
        """Test filtering frames by time range"""
        start_time = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        response = client.get(
            f"/api/frames?start_time={start_time}",
            headers=auth_headers_patient
        )
        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.skip(reason="POST /api/frames is not implemented (frames are ingested via scripts)")
    def test_create_frame_without_auth(self, client, test_patient, sample_pressure_matrix):
        """Test creating frame without authentication fails"""
        response = client.post(
            "/api/frames",
            json={
                "user_id": test_patient.id,
                "data": json.dumps({
                    "matrix": sample_pressure_matrix,
                    "width": 32,
                    "height": 16
                }),
                "captured_at": datetime.now(timezone.utc).isoformat()
            }
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_nonexistent_frame(self, client, auth_headers_admin):
        """Test getting nonexistent frame returns 404"""
        response = client.get("/api/frames/99999", headers=auth_headers_admin)
        assert response.status_code == status.HTTP_404_NOT_FOUND
