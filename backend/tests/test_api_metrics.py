"""Integration tests for metrics API endpoints"""
import pytest
from tests.helpers import blank_frame_bytes
from fastapi import status
from datetime import datetime, timezone


class TestMetricsEndpoints:
    """Test /api/metrics endpoints"""

    def test_get_metrics_as_patient(self, client, auth_headers_patient, test_metric, test_patient):
        """Test patient can get their own metrics"""
        response = client.get("/api/metrics", headers=auth_headers_patient)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        # All metrics should belong to patient's frames
        for metric in data:
            assert metric["user_id"] == test_patient.id

    def test_get_metrics_as_clinician_with_access(self, client, auth_headers_clinician, test_patient_in_group, test_group, db_session):
        """Test clinician can get metrics for patients in their group"""
        # Create frame and metric for patient in group
        from app.models.frame import Frame
        from app.models.metric import Metric
        import json

        frame_data = {"matrix": [[0 for _ in range(32)] for _ in range(16)]}
        frame = Frame(
            user_id=test_patient_in_group.id,
            data=blank_frame_bytes(),
            captured_at=datetime.now(timezone.utc)
        )
        db_session.add(frame)
        db_session.commit()
        db_session.refresh(frame)

        metric = Metric(
            frame_id=frame.id,
            peak_pressure=120.5,
            contact_area_percent=40.0,
            high_pressure_region={"x1": 1, "y1": 1, "x2": 5, "y2": 5, "area": 25},
            alert_generated=False
        )
        db_session.add(metric)
        db_session.commit()

        response = client.get(
            f"/api/metrics?user_id={test_patient_in_group.id}",
            headers=auth_headers_clinician
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) >= 1

    def test_get_metrics_as_admin(self, client, auth_headers_admin, test_metric):
        """Test admin can get all metrics"""
        response = client.get("/api/metrics", headers=auth_headers_admin)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)

    def test_get_metrics_summary_as_patient(self, client, auth_headers_patient, test_metric):
        """Test patient can get their own metrics summary"""
        response = client.get("/api/metrics/summary", headers=auth_headers_patient)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "avg_peak_pressure" in data
        assert "max_peak_pressure" in data
        assert "avg_contact_area" in data
        assert "total_alerts" in data
        assert "frames_analyzed" in data

    def test_get_metrics_summary_as_clinician_with_access(self, client, auth_headers_clinician, test_patient_in_group, test_group, db_session):
        """Test clinician can get summary for patients in their group"""
        # Create frame and metric for patient in group
        from app.models.frame import Frame
        from app.models.metric import Metric
        import json

        frame_data = {"matrix": [[0 for _ in range(32)] for _ in range(16)]}
        frame = Frame(
            user_id=test_patient_in_group.id,
            data=blank_frame_bytes(),
            captured_at=datetime.now(timezone.utc)
        )
        db_session.add(frame)
        db_session.commit()
        db_session.refresh(frame)

        metric = Metric(
            frame_id=frame.id,
            peak_pressure=150.0,
            contact_area_percent=50.0,
            high_pressure_region="heel",
            alert_generated=True
        )
        db_session.add(metric)
        db_session.commit()

        response = client.get(
            f"/api/metrics/summary?user_id={test_patient_in_group.id}",
            headers=auth_headers_clinician
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["frames_analyzed"] >= 1

    def test_get_metrics_summary_as_clinician_without_access(self, client, auth_headers_clinician, test_patient):
        """Test clinician cannot get summary for patients not in their group"""
        response = client.get(
            f"/api/metrics/summary?user_id={test_patient.id}",
            headers=auth_headers_clinician
        )
        # Should return empty summary (0 frames)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["frames_analyzed"] == 0

    def test_get_metrics_with_time_filter(self, client, auth_headers_patient, test_metric):
        """Test filtering metrics by time range"""
        start_time = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        response = client.get(
            f"/api/metrics?start_time={start_time}",
            headers=auth_headers_patient
        )
        assert response.status_code == status.HTTP_200_OK

    def test_get_metrics_with_pagination(self, client, auth_headers_patient, test_patient, db_session):
        """Test metrics pagination"""
        # Create multiple frames and metrics
        from app.models.frame import Frame
        from app.models.metric import Metric
        import json

        for i in range(5):
            frame_data = {"matrix": [[0 for _ in range(32)] for _ in range(16)]}
            frame = Frame(
                user_id=test_patient.id,
                data=blank_frame_bytes(),
                captured_at=datetime.now(timezone.utc)
            )
            db_session.add(frame)
            db_session.commit()
            db_session.refresh(frame)

            metric = Metric(
                frame_id=frame.id,
                peak_pressure=100.0 + i,
                contact_area_percent=40.0 + i,
                high_pressure_region={"x1": 1, "y1": 1, "x2": 5, "y2": 5, "area": 25},
                alert_generated=False
            )
            db_session.add(metric)
        db_session.commit()

        response = client.get("/api/metrics?limit=3", headers=auth_headers_patient)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) <= 3

    def test_get_metrics_without_auth(self, client):
        """Test getting metrics without authentication fails"""
        response = client.get("/api/metrics")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_metrics_include_frame_timestamp(self, client, auth_headers_patient, test_metric):
        """Test that metrics include frame timestamp"""
        response = client.get("/api/metrics", headers=auth_headers_patient)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        if len(data) > 0:
            assert "frame_captured_at" in data[0]

    def test_metrics_summary_values_correct(self, client, auth_headers_patient, test_metric):
        """Test that metrics summary calculates correctly"""
        response = client.get("/api/metrics/summary", headers=auth_headers_patient)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Check that values are numeric and sensible
        assert isinstance(data["avg_peak_pressure"], (int, float))
        assert isinstance(data["max_peak_pressure"], (int, float))
        assert isinstance(data["total_alerts"], int)
        assert data["max_peak_pressure"] >= data["avg_peak_pressure"]
        assert data["frames_analyzed"] >= 0
