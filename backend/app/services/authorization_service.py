"""Authorization service for access control"""
from typing import List, Optional
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.user import User, UserRole
from app.models.group import UserGroup, group_membership


class AuthorizationService:
    """Service for checking user access permissions"""

    @staticmethod
    def check_patient_access(clinician: User, patient_id: int, db: Session) -> bool:
        """
        Verify that a clinician has access to a specific patient.

        Clinicians have access to patients if:
        1. The patient is in one of the clinician's groups

        Args:
            clinician: The clinician user
            patient_id: ID of the patient to check access for
            db: Database session

        Returns:
            bool: True if clinician has access, False otherwise
        """
        if clinician.role != UserRole.clinician:
            return False

        # Check if patient is in any of clinician's groups
        has_access = db.query(group_membership).join(
            UserGroup, UserGroup.id == group_membership.c.group_id
        ).filter(
            UserGroup.clinician_id == clinician.id,
            group_membership.c.patient_id == patient_id
        ).first() is not None

        return has_access

    @staticmethod
    def require_patient_access(user: User, patient_id: int, db: Session) -> None:
        """
        Raise 403 unless the user may access the given patient's data.

        Patients may only access their own data; clinicians need the patient
        to be in one of their groups.
        """
        if user.role == UserRole.patient and user.id == patient_id:
            return
        if user.role == UserRole.clinician and AuthorizationService.check_patient_access(
            user, patient_id, db
        ):
            return
        raise HTTPException(status_code=403, detail="Access denied")

    @staticmethod
    def resolve_target_user_id(
        user: User, requested_user_id: Optional[int], db: Session
    ) -> int:
        """
        Resolve which user's data a request operates on.

        Patients always operate on themselves. Clinicians may name a patient
        via ``requested_user_id``, which must be in one of their groups.
        """
        if user.role == UserRole.clinician and requested_user_id:
            AuthorizationService.require_patient_access(user, requested_user_id, db)
            return requested_user_id
        return user.id

    @staticmethod
    def get_accessible_patients(clinician: User, db: Session) -> List[int]:
        """
        Get list of patient IDs accessible to a clinician.

        Args:
            clinician: The clinician user
            db: Database session

        Returns:
            List[int]: List of patient IDs the clinician can access
        """
        if clinician.role != UserRole.clinician:
            return []

        # Get all patients from clinician's groups
        patient_ids = db.query(group_membership.c.patient_id).join(
            UserGroup, UserGroup.id == group_membership.c.group_id
        ).filter(
            UserGroup.clinician_id == clinician.id
        ).distinct().all()

        return [pid[0] for pid in patient_ids]

    @staticmethod
    def filter_by_access(
        current_user: User,
        query,
        user_id_column,
        requested_user_id: Optional[int],
        db: Session
    ):
        """
        Filter a query based on user access permissions.

        For patients: Only show their own data
        For clinicians: Show data for patients in their groups (or requested patient)

        Args:
            current_user: The current authenticated user
            query: SQLAlchemy query to filter
            user_id_column: Column to filter by (e.g., Frame.user_id)
            requested_user_id: Optional user_id requested in the API call
            db: Database session

        Returns:
            Filtered query
        """
        if current_user.role == UserRole.patient:
            # Patients can only see their own data
            return query.filter(user_id_column == current_user.id)

        elif current_user.role == UserRole.clinician:
            if requested_user_id:
                # Verify clinician has access to requested patient
                if not AuthorizationService.check_patient_access(
                    current_user, requested_user_id, db
                ):
                    # Return empty query if no access
                    return query.filter(user_id_column == -1)
                return query.filter(user_id_column == requested_user_id)
            else:
                # Show all accessible patients
                accessible_patients = AuthorizationService.get_accessible_patients(
                    current_user, db
                )
                if not accessible_patients:
                    # No patients accessible, return empty query
                    return query.filter(user_id_column == -1)
                return query.filter(user_id_column.in_(accessible_patients))

        # Unknown role, deny all access
        return query.filter(user_id_column == -1)
