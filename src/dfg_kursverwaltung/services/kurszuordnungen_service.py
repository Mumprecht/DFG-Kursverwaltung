from datetime import datetime, timezone
from uuid import uuid4

from dfg_kursverwaltung.core.models import (
    CourseAssignment,
    CourseAssignmentRole,
    CourseAssignmentStatus,
)
from dfg_kursverwaltung.repositories.kurszuordnungen_repository import (
    CourseAssignmentRepository,
)


class CourseAssignmentService:
    def __init__(
        self,
        repository: CourseAssignmentRepository,
    ):
        self.repository = repository

    def create_assignment(
        self,
        *,
        person_id: str,
        kurstag_id: str,
        rolle: CourseAssignmentRole,
        status: CourseAssignmentStatus = (
            CourseAssignmentStatus.REGISTERED
        ),
        bemerkungen: str | None = None,
    ) -> CourseAssignment:
        existing = (
            self.repository
            .get_for_person_and_course_day(
                person_id,
                kurstag_id,
            )
        )

        if existing is not None:
            raise ValueError(
                "Diese Person ist diesem Kurstag "
                "bereits zugeordnet."
            )

        timestamp = datetime.now(
            timezone.utc
        )

        assignment = CourseAssignment(
            id=str(uuid4()),
            person_id=person_id,
            kurstag_id=kurstag_id,
            rolle=rolle,
            status=status,
            bemerkungen=self._clean_optional(
                bemerkungen
            ),
            created_at=timestamp,
            updated_at=timestamp,
        )

        return self.repository.create(
            assignment
        )

    def get_assignment(
        self,
        assignment_id: str,
    ) -> CourseAssignment | None:
        return self.repository.get_by_id(
            assignment_id
        )

    def get_assignment_for_person_and_course_day(
        self,
        person_id: str,
        kurstag_id: str,
    ) -> CourseAssignment | None:
        return (
            self.repository
            .get_for_person_and_course_day(
                person_id,
                kurstag_id,
            )
        )

    def list_assignments_for_course_day(
        self,
        kurstag_id: str,
    ) -> list[CourseAssignment]:
        return self.repository.list_for_course_day(
            kurstag_id
        )

    def list_assignments_for_person(
        self,
        person_id: str,
    ) -> list[CourseAssignment]:
        return self.repository.list_for_person(
            person_id
        )

    def update_assignment(
        self,
        assignment: CourseAssignment,
    ) -> CourseAssignment:
        existing = (
            self.repository
            .get_for_person_and_course_day(
                assignment.person_id,
                assignment.kurstag_id,
            )
        )

        if (
            existing is not None
            and existing.id != assignment.id
        ):
            raise ValueError(
                "Diese Person ist diesem Kurstag "
                "bereits zugeordnet."
            )

        assignment.bemerkungen = (
            self._clean_optional(
                assignment.bemerkungen
            )
        )

        assignment.updated_at = datetime.now(
            timezone.utc
        )

        return self.repository.update(
            assignment
        )

    def delete_assignment(
        self,
        assignment_id: str,
    ) -> None:
        self.repository.delete(
            assignment_id
        )

    @staticmethod
    def _clean_optional(
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        value = value.strip()

        return value or None