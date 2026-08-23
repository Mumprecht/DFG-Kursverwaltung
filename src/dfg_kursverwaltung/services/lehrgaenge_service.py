from datetime import datetime, timezone
from uuid import uuid4

from dfg_kursverwaltung.core.models import (
    Course,
    CourseType,
)
from dfg_kursverwaltung.repositories.lehrgaenge_repository import (
    CourseRepository,
)


class CourseService:
    def __init__(
        self,
        repository: CourseRepository,
    ):
        self.repository = repository

    def create_course(
        self,
        *,
        typ: CourseType,
        bezeichnung: str,
        beschreibung: str | None = None,
        bemerkungen: str | None = None,
    ) -> Course:
        bezeichnung = bezeichnung.strip()

        if not bezeichnung:
            raise ValueError(
                "Die Bezeichnung darf nicht leer sein."
            )

        timestamp = datetime.now(
            timezone.utc
        )

        course = Course(
            id=str(uuid4()),
            typ=typ,
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
        course.bezeichnung = (
            course.bezeichnung.strip()
        )

        if not course.bezeichnung:
            raise ValueError(
                "Die Bezeichnung darf nicht leer sein."
            )

        course.beschreibung = (
            self._clean_optional(
                course.beschreibung
            )
        )

        course.bemerkungen = (
            self._clean_optional(
                course.bemerkungen
            )
        )

        course.updated_at = datetime.now(
            timezone.utc
        )

        return self.repository.update(
            course
        )

    @staticmethod
    def _clean_optional(
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        value = value.strip()

        return value or None