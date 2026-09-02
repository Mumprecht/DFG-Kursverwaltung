from datetime import date, datetime, timezone
from uuid import uuid4

from dfg_kursverwaltung.core.models import CourseDay
from dfg_kursverwaltung.repositories.kurstage_repository import (
    CourseDayRepository,
)
from dfg_kursverwaltung.repositories.lehrgaenge_repository import (
    CourseRepository,
)
from dfg_kursverwaltung.repositories.standorte_repository import (
    LocationRepository,
)


class CourseDayService:
    def __init__(
        self,
        repository: CourseDayRepository,
        course_repository: CourseRepository,
        location_repository: LocationRepository,
    ):
        self.repository = repository
        self.course_repository = course_repository
        self.location_repository = location_repository

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
        self._ensure_course_exists(
            lehrgang_id
        )
        self._ensure_location_exists(
            standort_id
        )

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

    def find_possible_duplicate(
        self,
        *,
        lehrgang_id: str,
        datum: date,
        beginn: str | None = None,
        ende: str | None = None,
    ) -> CourseDay | None:
        beginn = self._clean_optional(
            beginn
        )

        ende = self._clean_optional(
            ende
        )

        return self.repository.find_possible_duplicate(
            lehrgang_id,
            datum,
            beginn,
            ende,
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
        self._ensure_course_exists(
            course_day.lehrgang_id
        )
        self._ensure_location_exists(
            course_day.standort_id
        )

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

    def delete_course_day(
        self,
        course_day_id: str,
    ) -> None:
        course_day_id = course_day_id.strip()

        if not course_day_id:
            raise ValueError(
                "Die Kurstag-ID darf nicht leer sein."
            )

        course_day = self.repository.get_by_id(
            course_day_id
        )

        if course_day is None:
            raise KeyError(
                "Kurstag nicht gefunden: "
                f"{course_day_id}"
            )

        if self.repository.has_assignments(
            course_day_id
        ):
            raise ValueError(
                "Der Kurstag kann nicht gelöscht werden, "
                "weil bereits Kurszuordnungen vorhanden sind."
            )

        self.repository.delete(
            course_day_id
        )

    def _ensure_course_exists(
        self,
        course_id: str,
    ) -> None:
        if self.course_repository.get_by_id(
            course_id
        ) is None:
            raise KeyError(
                "Lehrgang nicht gefunden: "
                f"{course_id}"
            )

    def _ensure_location_exists(
        self,
        location_id: str | None,
    ) -> None:
        if location_id is None:
            return

        if self.location_repository.get_by_id(
            location_id
        ) is None:
            raise KeyError(
                "Standort nicht gefunden: "
                f"{location_id}"
            )

    @staticmethod
    def _validate_times(
        beginn: str | None,
        ende: str | None,
    ) -> None:
        if (beginn is None) != (ende is None):
            raise ValueError(
                "Beginn und Ende müssen entweder "
                "beide angegeben oder beide leer sein."
            )

        parsed_times = {}

        for name, value in (
            ("Beginn", beginn),
            ("Ende", ende),
        ):
            if value is None:
                continue

            try:
                parsed = datetime.strptime(
                    value,
                    "%H:%M",
                )
            except ValueError as exc:
                raise ValueError(
                    f"{name} muss im Format "
                    "HH:MM angegeben werden."
                ) from exc

            if parsed.strftime("%H:%M") != value:
                raise ValueError(
                    f"{name} muss im Format "
                    "HH:MM angegeben werden."
                )

            parsed_times[name] = parsed.time()

        if (
            beginn is not None
            and ende is not None
            and parsed_times["Ende"]
            <= parsed_times["Beginn"]
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