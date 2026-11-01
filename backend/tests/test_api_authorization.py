"""Authorization tests for resource endpoints scoped to a patient"""
from fastapi import status


class TestCommentAuthorization:
    """Comments must only be visible to the frame owner and their clinicians"""

    def test_owner_can_read_comments(self, client, auth_headers_patient, test_frame):
        response = client.get(f"/api/comments?frame_id={test_frame.id}", headers=auth_headers_patient)
        assert response.status_code == status.HTTP_200_OK

    def test_unassigned_clinician_cannot_read_comments(self, client, auth_headers_clinician, test_frame):
        response = client.get(f"/api/comments?frame_id={test_frame.id}", headers=auth_headers_clinician)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_unassigned_clinician_cannot_comment(self, client, auth_headers_clinician, test_frame):
        response = client.post(
            "/api/comments",
            headers=auth_headers_clinician,
            json={"frame_id": test_frame.id, "text": "Not my patient"},
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_unknown_frame_returns_404(self, client, auth_headers_patient):
        response = client.get("/api/comments?frame_id=999999", headers=auth_headers_patient)
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestTargetUserResolution:
    """Clinicians may only target patients in their groups"""

    def test_unassigned_clinician_cannot_read_risk(self, client, auth_headers_clinician, test_patient):
        response = client.get(f"/api/risk/current?user_id={test_patient.id}", headers=auth_headers_clinician)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_unassigned_clinician_cannot_read_movements(self, client, auth_headers_clinician, test_patient):
        response = client.get(f"/api/movements?user_id={test_patient.id}", headers=auth_headers_clinician)
        assert response.status_code == status.HTTP_403_FORBIDDEN

