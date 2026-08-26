from datetime import datetime, timezone
from uuid import uuid4

from dfg_kursverwaltung.core.models import Course
from dfg_kursverwaltung.repositories.lehrgaenge_repository import (
    CourseRepository,
)
from dfg_kursverwaltung.repositories.lehrgangstypen_repository import (
    CourseTypeRepository,
)


class CourseService:
    def __init__(
        self,
        repository: CourseRepository,
        course_type_repository: CourseTypeRepository,
    ):
        self.repository = repository
        self.course_type_repository = course_type_repository

    def create_course(
        self,
        *,
        lehrgangstyp_id: str,
        bezeichnung: str,
        beschreibung: str | None = None,
        bemerkungen: str | None = None,
    ) -> Course:
        bezeichnung = bezeichnung.strip()
        lehrgangstyp_id = lehrgangstyp_id.strip()

        if not bezeichnung:
            raise ValueError(
                "Die Bezeichnung darf nicht leer sein."
            )

        self._validate_course_type(
            lehrgangstyp_id
        )

        timestamp = datetime.now(
            timezone.utc
        )

        course = Course(
            id=str(uuid4()),
            lehrgangstyp_id=lehrgangstyp_id,
            bezeichnung=bezeichnung,
            beschreibung=self._clean_optional(
                beschreibung
            ),
            bemerkungen=self._clean_optional(
                bemerkungen
            ),
            created_at=timestamp,
            updated_at=timestamp,
        )

        return self.repository.create(
            course
        )

    def get_course(
        self,
        course_id: str,
    ) -> Course | None:
        return self.repository.get_by_id(
            course_id
        )

    def get_course_by_type_and_name(
        self,
        course_type_id: str,
        bezeichnung: str,
    ) -> Course | None:
        course_type_id = course_type_id.strip()
        bezeichnung = bezeichnung.strip()

        if (
            not course_type_id
            or not bezeichnung
        ):
            return None

        return (
            self.repository
            .get_by_type_and_name(
                course_type_id,
                bezeichnung,
            )
        )

    def list_courses(
        self,
    ) -> list[Course]:
        return self.repository.list_all()

    def search_courses(
        self,
        search_text: str,
    ) -> list[Course]:
        search_text = search_text.strip()

        if not search_text:
            return self.list_courses()

        return self.repository.search(
            search_text
        )

    def update_course(
        self,
        course: Course,
    ) -> Course:
        course.bezeichnung = course.bezeichnung.strip()
        course.lehrgangstyp_id = course.lehrgangstyp_id.strip()

        if not course.bezeichnung:
            raise ValueError(
                "Die Bezeichnung darf nicht leer sein."
            )

        self._validate_course_type(
            course.lehrgangstyp_id
        )

        course.beschreibung = self._clean_optional(
            course.beschreibung
        )

        course.bemerkungen = self._clean_optional(
            course.bemerkungen
        )

        course.updated_at = datetime.now(
            timezone.utc
        )

        return self.repository.update(
            course
        )

    def _validate_course_type(
        self,
        course_type_id: str,
    ) -> None:
        if not course_type_id:
            raise ValueError(
                "Es muss ein Lehrgangstyp ausgewählt werden."
            )

        course_type = self.course_type_repository.get_by_id(
            course_type_id
        )

        if course_type is None:
            raise ValueError(
                "Der ausgewählte Lehrgangstyp existiert nicht."
            )

        if not course_type.aktiv:
            raise ValueError(
                "Der ausgewählte Lehrgangstyp ist nicht aktiv."
            )

    @staticmethod
    def _clean_optional(
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        value = value.strip()

        return value or None
