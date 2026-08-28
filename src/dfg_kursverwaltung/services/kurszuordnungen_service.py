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
from dfg_kursverwaltung.repositories.personen_repository import (
    PersonRepository,
)
from dfg_kursverwaltung.repositories.pruefungsergebnisse_repository import (
    ExamResultRepository,
)


class CourseAssignmentService:
    def __init__(
        self,
        repository: CourseAssignmentRepository,
        person_repository: PersonRepository,
        exam_result_repository: ExamResultRepository,
    ):
        self.repository = repository
        self.person_repository = person_repository
        self.exam_result_repository = exam_result_repository

    def create_assignment(
        self,
        *,
        person_id: str,
        kurstag_id: str,
        rolle: CourseAssignmentRole | str,
        status: CourseAssignmentStatus | str = (
            CourseAssignmentStatus.REGISTERED
        ),
        bemerkungen: str | None = None,
    ) -> CourseAssignment:
        rolle = CourseAssignmentRole(
            rolle
        )

        status = CourseAssignmentStatus(
            status
        )

        self._validate_role_for_person(
            person_id,
            rolle,
        )

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

    def create_historical_assignment(
        self,
        *,
        person_id: str,
        kurstag_id: str,
        rolle: CourseAssignmentRole | str,
        status: CourseAssignmentStatus | str = (
            CourseAssignmentStatus.REGISTERED
        ),
        bemerkungen: str | None = None,
    ) -> CourseAssignment:
        rolle = CourseAssignmentRole(
            rolle
        )

        status = CourseAssignmentStatus(
            status
        )

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

        # Bei historischen Importen wird bewusst
        # nicht gegen die heutigen Personenrollen
        # validiert. Die Rolle gehört zur jeweiligen
        # historischen Kurszuordnung.
        person = self.person_repository.get_by_id(
            person_id
        )

        if person is None:
            raise ValueError(
                "Die ausgewählte Person "
                "existiert nicht."
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
        assignment.rolle = CourseAssignmentRole(
            assignment.rolle
        )

        assignment.status = CourseAssignmentStatus(
            assignment.status
        )

        original = self.repository.get_by_id(
            assignment.id
        )

        if original is None:
            raise KeyError(
                "Kurszuordnung nicht gefunden: "
                f"{assignment.id}"
            )

        # Wenn bereits ein Prüfungsergebnis existiert,
        # muss der Status "Teilgenommen" erhalten bleiben.
        # Das Ergebnis wird niemals stillschweigend gelöscht.
        if (
            assignment.status
            != CourseAssignmentStatus.ATTENDED
        ):
            exam_result = (
                self.exam_result_repository
                .get_by_assignment_id(
                    assignment.id
                )
            )

            if exam_result is not None:
                raise ValueError(
                    "Für diese Kurszuordnung existiert "
                    "ein Prüfungsergebnis. "
                    "Löschen Sie zuerst das "
                    "Prüfungsergebnis, bevor Sie den "
                    "Status ändern."
                )

        # Die historische Rolle bleibt gültig.
        # Nur wenn die Rolle tatsächlich geändert
        # wird, muss die neue Rolle bei der Person
        # aktuell freigegeben sein.
        if assignment.rolle != original.rolle:
            self._validate_role_for_person(
                assignment.person_id,
                assignment.rolle,
            )

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

    def _validate_role_for_person(
        self,
        person_id: str,
        role: CourseAssignmentRole,
    ) -> None:
        person = self.person_repository.get_by_id(
            person_id
        )

        if person is None:
            raise ValueError(
                "Die ausgewählte Person "
                "existiert nicht."
            )

        if not person.aktiv:
            raise ValueError(
                "Eine inaktive Person kann "
                "keinem neuen Kurstag "
                "zugeordnet werden."
            )

        if (
            role
            == CourseAssignmentRole.PARTICIPANT
            and not person.ist_teilnehmer
        ):
            raise ValueError(
                "Der Person ist die Rolle "
                "Teilnehmer nicht zugeordnet."
            )

        if (
            role
            == CourseAssignmentRole.INSTRUCTOR
            and not person.ist_instruktor
        ):
            raise ValueError(
                "Der Person ist die Rolle "
                "Instruktor nicht zugeordnet."
            )

    @staticmethod
    def _clean_optional(
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        value = value.strip()

        return value or None
