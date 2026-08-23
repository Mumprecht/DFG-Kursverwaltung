from datetime import date, datetime, timezone
from uuid import uuid4

from dfg_kursverwaltung.core.models import Person
from dfg_kursverwaltung.repositories.personen_repository import (
    PersonRepository,
)


class PersonService:
    def __init__(
        self,
        repository: PersonRepository,
    ):
        self.repository = repository

    def create_person(
        self,
        *,
        nachname: str,
        vorname: str,
        geburtsdatum: date | None = None,
        email: str | None = None,
        strasse: str | None = None,
        hausnummer: str | None = None,
        plz: str | None = None,
        ort: str | None = None,
        organisation: str | None = None,
        mitglied: bool = False,
        bemerkungen: str | None = None,
    ) -> Person:
        nachname = nachname.strip()
        vorname = vorname.strip()

        if not nachname:
            raise ValueError(
                "Nachname darf nicht leer sein."
            )

        if not vorname:
            raise ValueError(
                "Vorname darf nicht leer sein."
            )

        if (
            geburtsdatum is not None
            and geburtsdatum > date.today()
        ):
            raise ValueError(
                "Das Geburtsdatum darf nicht "
                "in der Zukunft liegen."
            )

        timestamp = datetime.now(
            timezone.utc
        )

        person = Person(
            id=str(uuid4()),
            nachname=nachname,
            vorname=vorname,
            geburtsdatum=geburtsdatum,
            email=self._clean_optional(
                email
            ),
            strasse=self._clean_optional(
                strasse
            ),
            hausnummer=self._clean_optional(
                hausnummer
            ),
            plz=self._clean_optional(
                plz
            ),
            ort=self._clean_optional(
                ort
            ),
            organisation=self._clean_optional(
                organisation
            ),
            mitglied=mitglied,
            aktiv=True,
            bemerkungen=self._clean_optional(
                bemerkungen
            ),
            created_at=timestamp,
            updated_at=timestamp,
        )

        return self.repository.create(
            person
        )

    def get_person(
        self,
        person_id: str,
    ) -> Person | None:
        return self.repository.get_by_id(
            person_id
        )

    def list_persons(
        self,
        include_inactive: bool = False,
    ) -> list[Person]:
        return self.repository.list_all(
            include_inactive=include_inactive
        )

    def search_persons(
        self,
        search_text: str,
        include_inactive: bool = False,
    ) -> list[Person]:
        search_text = search_text.strip()

        if not search_text:
            return self.list_persons(
                include_inactive=include_inactive
            )

        return self.repository.search(
            search_text,
            include_inactive=include_inactive,
        )

    def update_person(
        self,
        person: Person,
    ) -> Person:
        person.nachname = person.nachname.strip()
        person.vorname = person.vorname.strip()

        if not person.nachname:
            raise ValueError(
                "Nachname darf nicht leer sein."
            )

        if not person.vorname:
            raise ValueError(
                "Vorname darf nicht leer sein."
            )

        if (
            person.geburtsdatum is not None
            and person.geburtsdatum > date.today()
        ):
            raise ValueError(
                "Das Geburtsdatum darf nicht "
                "in der Zukunft liegen."
            )

        person.email = self._clean_optional(
            person.email
        )

        person.strasse = self._clean_optional(
            person.strasse
        )

        person.hausnummer = self._clean_optional(
            person.hausnummer
        )

        person.plz = self._clean_optional(
            person.plz
        )

        person.ort = self._clean_optional(
            person.ort
        )

        person.organisation = self._clean_optional(
            person.organisation
        )

        person.bemerkungen = self._clean_optional(
            person.bemerkungen
        )

        person.updated_at = datetime.now(
            timezone.utc
        )

        return self.repository.update(
            person
        )

    def deactivate_person(
        self,
        person_id: str,
    ) -> None:
        self.repository.deactivate(
            person_id
        )

    def activate_person(
        self,
        person_id: str,
    ) -> None:
        self.repository.activate(
            person_id
        )

    @staticmethod
    def _clean_optional(
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        value = value.strip()

        return value or None