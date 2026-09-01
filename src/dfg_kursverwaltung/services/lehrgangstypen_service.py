from datetime import datetime, timezone
from uuid import uuid4

from dfg_kursverwaltung.core.models import CourseType
from dfg_kursverwaltung.repositories.lehrgangstypen_repository import (
    CourseTypeRepository,
)


class CourseTypeService:
    def __init__(
        self,
        repository: CourseTypeRepository,
    ):
        self.repository = repository

    def create_course_type(
        self,
        *,
        bezeichnung: str,
        bemerkungen: str | None = None,
    ) -> CourseType:
        bezeichnung = bezeichnung.strip()

        if not bezeichnung:
            raise ValueError(
                "Die Bezeichnung darf nicht leer sein."
            )

        existing = self.repository.get_by_name(
            bezeichnung
        )

        if existing is not None:
            raise ValueError(
                "Ein Lehrgangstyp mit dieser "
                "Bezeichnung existiert bereits."
            )

        timestamp = datetime.now(
            timezone.utc
        )

        course_type = CourseType(
            id=str(uuid4()),
            bezeichnung=bezeichnung,
            aktiv=True,
            bemerkungen=self._clean_optional(
                bemerkungen
            ),
            created_at=timestamp,
            updated_at=timestamp,
        )

        return self.repository.create(
            course_type
        )

    def get_course_type(
        self,
        course_type_id: str,
    ) -> CourseType | None:
        return self.repository.get_by_id(
            course_type_id
        )

    def get_course_type_by_name(
        self,
        bezeichnung: str,
    ) -> CourseType | None:
        bezeichnung = bezeichnung.strip()

        if not bezeichnung:
            return None

        return self.repository.get_by_name(
            bezeichnung
        )

    def list_course_types(
        self,
        include_inactive: bool = False,
    ) -> list[CourseType]:
        return self.repository.list_all(
            include_inactive=include_inactive
        )

    def search_course_types(
        self,
        search_text: str,
        include_inactive: bool = False,
    ) -> list[CourseType]:
        search_text = search_text.strip()

        if not search_text:
            return self.list_course_types(
                include_inactive=include_inactive
            )

        return self.repository.search(
            search_text,
            include_inactive=include_inactive,
        )

    def update_course_type(
        self,
        course_type: CourseType,
    ) -> CourseType:
        course_type.bezeichnung = (
            course_type.bezeichnung.strip()
        )

        if not course_type.bezeichnung:
            raise ValueError(
                "Die Bezeichnung darf nicht leer sein."
            )

        existing = self.repository.get_by_name(
            course_type.bezeichnung
        )

        if (
            existing is not None
            and existing.id != course_type.id
        ):
            raise ValueError(
                "Ein Lehrgangstyp mit dieser "
                "Bezeichnung existiert bereits."
            )

        course_type.bemerkungen = (
            self._clean_optional(
                course_type.bemerkungen
            )
        )

        course_type.updated_at = datetime.now(
            timezone.utc
        )

        return self.repository.update(
            course_type
        )

    def deactivate_course_type(
        self,
        course_type_id: str,
    ) -> None:
        self.repository.set_active_status(
            course_type_id,
            False,
            datetime.now(
                timezone.utc
            ),
        )

    def activate_course_type(
        self,
        course_type_id: str,
    ) -> None:
        self.repository.set_active_status(
            course_type_id,
            True,
            datetime.now(
                timezone.utc
            ),
        )

    def delete_course_type(
        self,
        course_type_id: str,
    ) -> None:
        course_type_id = course_type_id.strip()

        if not course_type_id:
            raise ValueError(
                "Die Lehrgangstyp-ID darf nicht leer sein."
            )

        course_type = self.repository.get_by_id(
            course_type_id
        )

        if course_type is None:
            raise KeyError(
                "Lehrgangstyp nicht gefunden: "
                f"{course_type_id}"
            )

        if self.repository.has_courses(
            course_type_id
        ):
            raise ValueError(
                "Der Lehrgangstyp kann nicht gelöscht werden, "
                "weil bereits Lehrgänge vorhanden sind."
            )

        self.repository.delete(
            course_type_id
        )
    @staticmethod
    def _clean_optional(
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        value = value.strip()

        return value or None