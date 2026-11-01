"""Unit tests for AuthorizationService"""
import pytest
from tests.helpers import blank_frame_bytes
from app.services.authorization_service import AuthorizationService
from app.models.user import User, UserRole
from app.models.group import UserGroup, group_membership
from app.models.frame import Frame


class TestAuthorizationService:
    """Test authorization service methods"""

    def test_check_patient_access_with_group_membership(self, db_session, test_clinician, test_patient_in_group, test_group):
        """Test clinician can access patient in their group"""
        has_access = AuthorizationService.check_patient_access(
            clinician=test_clinician,
            patient_id=test_patient_in_group.id,
            db=db_session
        )
        assert has_access is True

    def test_check_patient_access_without_group_membership(self, db_session, test_clinician, test_patient):
        """Test clinician cannot access patient not in their group"""
        has_access = AuthorizationService.check_patient_access(
            clinician=test_clinician,
            patient_id=test_patient.id,
            db=db_session
        )
        assert has_access is False

    def test_get_accessible_patients_for_clinician(self, db_session, test_clinician, test_patient_in_group, test_patient, test_group):
        """Test getting list of accessible patients for clinician"""
        accessible_patients = AuthorizationService.get_accessible_patients(
            clinician=test_clinician,
            db=db_session
        )
        assert test_patient_in_group.id in accessible_patients
        assert test_patient.id not in accessible_patients

    def test_get_accessible_patients_for_admin(self, db_session, test_admin, test_patient, test_patient_in_group):
        """Test admin can access all patients"""
        accessible_patients = AuthorizationService.get_accessible_patients(
            clinician=test_admin,
            db=db_session
        )
        # Admin should see all patients (returns empty list meaning no filtering)
        assert accessible_patients == []

    def test_filter_by_access_patient_sees_own_data(self, db_session, test_patient, test_frame):
        """Test patient can only see their own frames"""
        query = db_session.query(Frame)
        filtered_query = AuthorizationService.filter_by_access(
            current_user=test_patient,
            query=query,
            user_id_column=Frame.user_id,
            requested_user_id=None,
            db=db_session
        )
        frames = filtered_query.all()
        assert len(frames) == 1
        assert frames[0].user_id == test_patient.id

    def test_filter_by_access_patient_cannot_request_other_user(self, db_session, test_patient):
        """Test a patient's requested user_id never widens access beyond themselves"""
        query = db_session.query(Frame)
        filtered_query = AuthorizationService.filter_by_access(
            current_user=test_patient,
            query=query,
            user_id_column=Frame.user_id,
            requested_user_id=999,  # Different user
            db=db_session
        )
        assert filtered_query.all() == []

    def test_filter_by_access_clinician_sees_group_patients(self, db_session, test_clinician, test_patient_in_group, test_group):
        """Test clinician sees only patients in their groups"""
        from datetime import datetime, timezone
        import json

        # Create frame for patient in group
        frame_data = {"matrix": [[0 for _ in range(32)] for _ in range(16)]}
        frame = Frame(
            user_id=test_patient_in_group.id,
            data=blank_frame_bytes(),
            captured_at=datetime.now(timezone.utc)
        )
        db_session.add(frame)
        db_session.commit()

        query = db_session.query(Frame)
        filtered_query = AuthorizationService.filter_by_access(
            current_user=test_clinician,
            query=query,
            user_id_column=Frame.user_id,
            requested_user_id=None,
            db=db_session
        )
        frames = filtered_query.all()
        assert len(frames) == 1
        assert frames[0].user_id == test_patient_in_group.id

    def test_filter_by_access_clinician_cannot_see_unassigned_patients(self, db_session, test_clinician, test_patient, test_frame):
        """Test clinician cannot see patients not in their groups"""
        query = db_session.query(Frame)
        filtered_query = AuthorizationService.filter_by_access(
            current_user=test_clinician,
            query=query,
            user_id_column=Frame.user_id,
            requested_user_id=None,
            db=db_session
        )
        frames = filtered_query.all()
        assert len(frames) == 0

    def test_filter_by_access_clinician_without_groups_sees_nothing(self, db_session, test_admin, test_frame):
        """Test a clinician with no groups sees no frames (there is no admin role)"""
        query = db_session.query(Frame)
        filtered_query = AuthorizationService.filter_by_access(
            current_user=test_admin,
            query=query,
            user_id_column=Frame.user_id,
            requested_user_id=None,
            db=db_session
        )
        assert filtered_query.all() == []

    def test_filter_by_access_with_specific_patient_request(self, db_session, test_clinician, test_patient_in_group, test_group):
        """Test clinician can request specific patient they have access to"""
        from datetime import datetime, timezone
        import json

        # Create frame for patient in group
        frame_data = {"matrix": [[0 for _ in range(32)] for _ in range(16)]}
        frame = Frame(
            user_id=test_patient_in_group.id,
            data=blank_frame_bytes(),
            captured_at=datetime.now(timezone.utc)
        )
        db_session.add(frame)
        db_session.commit()

        query = db_session.query(Frame)
        filtered_query = AuthorizationService.filter_by_access(
            current_user=test_clinician,
            query=query,
            user_id_column=Frame.user_id,
            requested_user_id=test_patient_in_group.id,
            db=db_session
        )
        frames = filtered_query.all()
        assert len(frames) == 1
        assert frames[0].user_id == test_patient_in_group.id

    def test_filter_by_access_clinician_denied_for_unauthorized_patient(self, db_session, test_clinician, test_patient):
        """Test clinician gets no data for a patient not in their group"""
        query = db_session.query(Frame)
        filtered_query = AuthorizationService.filter_by_access(
            current_user=test_clinician,
            query=query,
            user_id_column=Frame.user_id,
            requested_user_id=test_patient.id,
            db=db_session
        )
        assert filtered_query.all() == []
