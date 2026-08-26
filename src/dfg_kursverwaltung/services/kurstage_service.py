from datetime import date, datetime, timezone
from uuid import uuid4

from dfg_kursverwaltung.core.models import CourseDay
from dfg_kursverwaltung.repositories.kurstage_repository import (
    CourseDayRepository,
)


class CourseDayService:
    def __init__(
        self,
        repository: CourseDayRepository,
    ):
        self.repository = repository

    def create_course_day(
        self,
        *,
        lehrgang_id: str,
        datum: date,
        standort_id: str | None = None,
        beginn: str | None = None,
        ende: str | None = None,
        bezeichnung: str | None = None,
        bemerkungen: str | None = None,
    ) -> CourseDay:
        beginn = self._clean_optional(
            beginn
        )
        ende = self._clean_optional(
            ende
        )

        self._validate_times(
            beginn,
            ende,
        )

        timestamp = datetime.now(
            timezone.utc
        )

        course_day = CourseDay(
            id=str(uuid4()),
            lehrgang_id=lehrgang_id,
            standort_id=standort_id,
            datum=datum,
            beginn=beginn,
            ende=ende,
            bezeichnung=self._clean_optional(
                bezeichnung
            ),
            bemerkungen=self._clean_optional(
                bemerkungen
            ),
            created_at=timestamp,
            updated_at=timestamp,
        )

        return self.repository.create(
            course_day
        )

    def get_course_day(
        self,
        course_day_id: str,
    ) -> CourseDay | None:
        return self.repository.get_by_id(
            course_day_id
        )

    def get_course_day_by_identity(
        self,
        *,
        lehrgang_id: str,
        datum: date,
        beginn: str | None = None,
        ende: str | None = None,
        bezeichnung: str | None = None,
    ) -> CourseDay | None:
        beginn = self._clean_optional(
            beginn
        )

        ende = self._clean_optional(
            ende
        )

        bezeichnung = self._clean_optional(
            bezeichnung
        )

        return self.repository.get_by_identity(
            lehrgang_id,
            datum,
            beginn,
            ende,
            bezeichnung,
        )

    def list_all_course_days(
        self,
    ) -> list[CourseDay]:
        return self.repository.list_all()

    def list_course_days(
        self,
        course_id: str,
    ) -> list[CourseDay]:
        return self.repository.list_for_course(
            course_id
        )

    def update_course_day(
        self,
        course_day: CourseDay,
    ) -> CourseDay:
        course_day.beginn = (
            self._clean_optional(
                course_day.beginn
            )
        )

        course_day.ende = (
            self._clean_optional(
                course_day.ende
            )
        )

        self._validate_times(
            course_day.beginn,
            course_day.ende,
        )

        course_day.bezeichnung = (
            self._clean_optional(
                course_day.bezeichnung
            )
        )

        course_day.bemerkungen = (
            self._clean_optional(
                course_day.bemerkungen
            )
        )

        course_day.updated_at = datetime.now(
            timezone.utc
        )

        return self.repository.update(
            course_day
        )

    @staticmethod
    def _validate_times(
        beginn: str | None,
        ende: str | None,
    ) -> None:
        for name, value in (
            ("Beginn", beginn),
            ("Ende", ende),
        ):
            if value is None:
                continue

            try:
                datetime.strptime(
                    value,
                    "%H:%M",
                )
            except ValueError as exc:
                raise ValueError(
                    f"{name} muss im Format "
                    "HH:MM angegeben werden."
                ) from exc

        if (
            beginn is not None
            and ende is not None
            and ende <= beginn
        ):
            raise ValueError(
                "Das Ende muss nach dem "
                "Beginn liegen."
            )

    @staticmethod
    def _clean_optional(
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        value = value.strip()

        return value or None