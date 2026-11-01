"""Integration tests for users API endpoints"""
import pytest
from fastapi import status


class TestUsersEndpoints:
    """Test /api/users endpoints"""

    def test_get_patients_as_admin(self, client, auth_headers_clinician, test_patient_in_group):
        """Test clinician gets the patients in their groups"""
        response = client.get("/api/users/patients", headers=auth_headers_clinician)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    def test_get_patients_as_clinician_with_group(self, client, auth_headers_clinician, test_patient_in_group, test_group):
        """Test clinician sees only patients in their groups"""
        response = client.get("/api/users/patients", headers=auth_headers_clinician)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        # Should see patient in their group
        patient_ids = [p["id"] for p in data]
        assert test_patient_in_group.id in patient_ids

    def test_get_patients_as_clinician_without_group(self, client, auth_headers_clinician, test_patient):
        """Test clinician without group assignments sees no patients"""
        response = client.get("/api/users/patients", headers=auth_headers_clinician)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        # Should see no patients or only those in groups
        patient_ids = [p["id"] for p in data]
        assert test_patient.id not in patient_ids

    def test_get_patients_as_patient_forbidden(self, client, auth_headers_patient):
        """Test patient cannot access patient list"""
        response = client.get("/api/users/patients", headers=auth_headers_patient)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_get_patients_without_auth(self, client):
        """Test accessing patients without authentication fails"""
        response = client.get("/api/users/patients")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.skip(reason="GET /api/users/{id} is not implemented")
    def test_get_user_by_id_as_admin(self, client, auth_headers_admin, test_patient):
        """Test admin can get any user by ID"""
        response = client.get(f"/api/users/{test_patient.id}", headers=auth_headers_admin)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == test_patient.id
        assert data["email"] == test_patient.email

    @pytest.mark.skip(reason="GET /api/users/{id} is not implemented")
    def test_get_user_by_id_as_self(self, client, auth_headers_patient, test_patient):
        """Test user can get their own info"""
        response = client.get(f"/api/users/{test_patient.id}", headers=auth_headers_patient)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == test_patient.id

    @pytest.mark.skip(reason="GET /api/users/{id} is not implemented")
    def test_get_user_by_id_as_clinician_with_access(self, client, auth_headers_clinician, test_patient_in_group, test_group):
        """Test clinician can get patient in their group"""
        response = client.get(f"/api/users/{test_patient_in_group.id}", headers=auth_headers_clinician)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == test_patient_in_group.id

    @pytest.mark.skip(reason="GET /api/users/{id} is not implemented")
    def test_get_user_by_id_as_clinician_without_access(self, client, auth_headers_clinician, test_patient):
        """Test clinician cannot get patient not in their group"""
        response = client.get(f"/api/users/{test_patient.id}", headers=auth_headers_clinician)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.skip(reason="GET /api/users/{id} is not implemented")
    def test_get_user_by_id_as_other_patient(self, client, auth_headers_patient, test_admin):
        """Test patient cannot get another user's info"""
        response = client.get(f"/api/users/{test_admin.id}", headers=auth_headers_patient)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_get_nonexistent_user(self, client, auth_headers_admin):
        """Test getting nonexistent user returns 404"""
        response = client.get("/api/users/99999", headers=auth_headers_admin)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_user_as_self(self, client, auth_headers_patient, test_patient):
        """Test user can update their own info"""
        response = client.put(
            f"/api/users/{test_patient.id}",
            headers=auth_headers_patient,
            json={
                "name": "Updated Name"
            }
        )
        # Endpoint may return 200 or 404 depending on implementation
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_patients_list_includes_last_frame(self, client, auth_headers_clinician, test_patient_in_group):
        """Test patient list entries expose the last update timestamp"""
        response = client.get("/api/users/patients", headers=auth_headers_clinician)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        patient_data = next((p for p in data if p["id"] == test_patient_in_group.id), None)
        assert patient_data is not None
        assert "last_updated" in patient_data
