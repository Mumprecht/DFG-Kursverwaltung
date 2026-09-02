from datetime import datetime, timezone
from uuid import uuid4

from dfg_kursverwaltung.core.models import (
    CourseAssignment,
    CourseAssignmentRole,
    CourseAssignmentStatus,
    ExamResult,
    User,
)
from dfg_kursverwaltung.core.permissions import (
    Permission,
    require_permission,
)
from dfg_kursverwaltung.repositories.kurszuordnungen_repository import (
    CourseAssignmentRepository,
)
from dfg_kursverwaltung.repositories.pruefungsergebnisse_repository import (
    ExamResultRepository,
)

class ExamResultService:
    def __init__(
        self,
        repository: ExamResultRepository,
        assignment_repository: CourseAssignmentRepository,
    ):
        self.repository = repository
        self.assignment_repository = assignment_repository

    def create_exam_result(
        self,
        *,
        actor: User,
        kurszuordnung_id: str,
        bestanden: bool,
        note: str | None = None,
        bemerkungen: str | None = None,
    ) -> ExamResult:
        kurszuordnung_id = (
            kurszuordnung_id.strip()
        )

        if not kurszuordnung_id:
            raise ValueError(
                "Die Kurszuordnung darf "
                "nicht leer sein."
            )

        assignment = self._validate_assignment_status(
            kurszuordnung_id
        )

        self._ensure_exam_result_write_access(
            actor,
            assignment,
        )

        existing = (
            self.repository
            .get_by_assignment_id(
                kurszuordnung_id
            )
        )

        if existing is not None:
            raise ValueError(
                "Für diese Kurszuordnung "
                "existiert bereits ein "
                "Prüfungsergebnis."
            )

        timestamp = datetime.now(
            timezone.utc
        )

        exam_result = ExamResult(
            id=str(uuid4()),
            kurszuordnung_id=kurszuordnung_id,
            bestanden=bestanden,
            note=self._clean_optional(
                note
            ),
            bemerkungen=self._clean_optional(
                bemerkungen
            ),
            created_at=timestamp,
            updated_at=timestamp,
        )

        return self.repository.create(
            exam_result
        )

    def get_exam_result(
        self,
        exam_result_id: str,
    ) -> ExamResult | None:
        return self.repository.get_by_id(
            exam_result_id
        )

    def get_exam_result_for_assignment(
        self,
        kurszuordnung_id: str,
    ) -> ExamResult | None:
        return (
            self.repository
            .get_by_assignment_id(
                kurszuordnung_id
            )
        )

    def list_exam_results(
        self,
    ) -> list[ExamResult]:
        return self.repository.list_all()

    def update_exam_result(
        self,
        actor: User,
        exam_result: ExamResult,
    ) -> ExamResult:
        original = self.repository.get_by_id(
            exam_result.id
        )

        if original is None:
            raise KeyError(
                "Prüfungsergebnis nicht gefunden: "
                f"{exam_result.id}"
            )

        exam_result.kurszuordnung_id = (
            exam_result.kurszuordnung_id.strip()
        )

        if not exam_result.kurszuordnung_id:
            raise ValueError(
                "Die Kurszuordnung darf "
                "nicht leer sein."
            )

        original_assignment = (
            self.assignment_repository.get_by_id(
                original.kurszuordnung_id
            )
        )

        if original_assignment is None:
            raise ValueError(
                "Die ursprüngliche Kurszuordnung "
                "existiert nicht."
            )

        self._ensure_exam_result_write_access(
            actor,
            original_assignment,
        )

        if (
            exam_result.kurszuordnung_id
            != original.kurszuordnung_id
        ):
            raise ValueError(
                "Die Kurszuordnung eines "
                "Prüfungsergebnisses kann nicht "
                "nachträglich geändert werden."
            )

        assignment = self._validate_assignment_status(
            exam_result.kurszuordnung_id
        )

        self._ensure_exam_result_write_access(
            actor,
            assignment,
        )

        existing = (
            self.repository
            .get_by_assignment_id(
                exam_result.kurszuordnung_id
            )
        )

        if (
            existing is not None
            and existing.id != exam_result.id
        ):
            raise ValueError(
                "Für diese Kurszuordnung "
                "existiert bereits ein "
                "Prüfungsergebnis."
            )

        exam_result.note = (
            self._clean_optional(
                exam_result.note
            )
        )

        exam_result.bemerkungen = (
            self._clean_optional(
                exam_result.bemerkungen
            )
        )

        exam_result.updated_at = datetime.now(
            timezone.utc
        )

        return self.repository.update(
            exam_result
        )

    def delete_exam_result(
        self,
        actor: User,
        exam_result_id: str,
    ) -> None:
        exam_result = self.repository.get_by_id(
            exam_result_id
        )

        if exam_result is None:
            raise KeyError(
                "Prüfungsergebnis nicht gefunden: "
                f"{exam_result_id}"
            )

        assignment = (
            self.assignment_repository.get_by_id(
                exam_result.kurszuordnung_id
            )
        )

        if assignment is None:
            raise ValueError(
                "Die zugehörige Kurszuordnung "
                "existiert nicht."
            )

        self._ensure_exam_result_write_access(
            actor,
            assignment,
        )

        self.repository.delete(
            exam_result_id
        )

    def _validate_assignment_status(
        self,
        kurszuordnung_id: str,
    ) -> CourseAssignment:
        assignment = (
            self.assignment_repository
            .get_by_id(
                kurszuordnung_id
            )
        )

        if assignment is None:
            raise ValueError(
                "Die zugehörige Kurszuordnung "
                "existiert nicht."
            )

        if (
            assignment.rolle
            != CourseAssignmentRole.PARTICIPANT
        ):
            raise ValueError(
                "Ein Prüfungsergebnis kann nur "
                "für eine Teilnehmer-Zuordnung "
                "erfasst oder geändert werden."
            )

        if (
            assignment.status
            != CourseAssignmentStatus.ATTENDED
        ):
            raise ValueError(
                "Ein Prüfungsergebnis kann nur "
                "für eine Kurszuordnung mit dem "
                "Status 'Teilgenommen' erfasst "
                "oder geändert werden."
            )

        return assignment

    def _ensure_exam_result_write_access(
        self,
        actor: User,
        assignment: CourseAssignment,
    ) -> None:
        require_permission(
            actor,
            Permission.EXAM_RESULT_WRITE,
        )


    @staticmethod
    def _clean_optional(
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        value = value.strip()

        return value or None
