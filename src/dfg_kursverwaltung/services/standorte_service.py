from datetime import datetime, timezone
from uuid import uuid4

import phonenumbers
from phonenumbers import PhoneNumberFormat

from dfg_kursverwaltung.core.models import Location
from dfg_kursverwaltung.repositories.standorte_repository import (
    LocationRepository,
)


class LocationService:
    DEFAULT_REGION = "CH"

    def __init__(
        self,
        repository: LocationRepository,
    ):
        self.repository = repository

    def create_location(
        self,
        *,
        bezeichnung: str,
        strasse: str | None = None,
        hausnummer: str | None = None,
        plz: str | None = None,
        ort: str | None = None,
        kontakt_vorname: str | None = None,
        kontakt_nachname: str | None = None,
        telefon: str | None = None,
        email: str | None = None,
        webseite: str | None = None,
        bemerkungen: str | None = None,
    ) -> Location:
        bezeichnung = (
            bezeichnung.strip()
        )

        if not bezeichnung:
            raise ValueError(
                "Die Bezeichnung darf nicht leer sein."
            )

        email = self._clean_optional(
            email
        )

        self.validate_email(
            email
        )

        webseite = self._clean_optional(
            webseite
        )

        telefon_e164 = None

        if telefon is not None:
            telefon = telefon.strip()

            if telefon:
                telefon_e164 = (
                    self.normalize_phone_number(
                        telefon
                    )
                )

        timestamp = datetime.now(
            timezone.utc
        )

        location = Location(
            id=str(uuid4()),
            bezeichnung=bezeichnung,
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
            kontakt_vorname=self._clean_optional(
                kontakt_vorname
            ),
            kontakt_nachname=self._clean_optional(
                kontakt_nachname
            ),
            telefon_e164=telefon_e164,
            email=email,
            webseite=webseite,
            bemerkungen=self._clean_optional(
                bemerkungen
            ),
            aktiv=True,
            created_at=timestamp,
            updated_at=timestamp,
        )

        return self.repository.create(
            location
        )

    def get_location(
        self,
        location_id: str,
    ) -> Location | None:
        return self.repository.get_by_id(
            location_id
        )

    def list_locations(
        self,
        include_inactive: bool = False,
    ) -> list[Location]:
        return self.repository.list_all(
            include_inactive=include_inactive
        )

    def search_locations(
        self,
        search_text: str,
        include_inactive: bool = False,
    ) -> list[Location]:
        search_text = search_text.strip()

        if not search_text:
            return self.list_locations(
                include_inactive=include_inactive
            )

        return self.repository.search(
            search_text,
            include_inactive=include_inactive,
        )

    def find_possible_duplicate(
        self,
        bezeichnung: str,
        ort: str | None,
    ) -> Location | None:
        return self.repository.find_possible_duplicate(
            bezeichnung,
            ort,
        )

    def update_location(
        self,
        location: Location,
        *,
        telefon: str | None = None,
    ) -> Location:
        location.bezeichnung = (
            location.bezeichnung.strip()
        )

        if not location.bezeichnung:
            raise ValueError(
                "Die Bezeichnung darf nicht leer sein."
            )

        location.strasse = self._clean_optional(
            location.strasse
        )

        location.hausnummer = self._clean_optional(
            location.hausnummer
        )

        location.plz = self._clean_optional(
            location.plz
        )

        location.ort = self._clean_optional(
            location.ort
        )

        location.kontakt_vorname = (
            self._clean_optional(
                location.kontakt_vorname
            )
        )

        location.kontakt_nachname = (
            self._clean_optional(
                location.kontakt_nachname
            )
        )

        location.email = self._clean_optional(
            location.email
        )

        self.validate_email(
            location.email
        )

        location.webseite = self._clean_optional(
            location.webseite
        )

        location.bemerkungen = (
            self._clean_optional(
                location.bemerkungen
            )
        )

        if telefon is not None:
            telefon = telefon.strip()

            if telefon:
                location.telefon_e164 = (
                    self.normalize_phone_number(
                        telefon
                    )
                )
            else:
                location.telefon_e164 = None

        location.updated_at = datetime.now(
            timezone.utc
        )

        return self.repository.update(
            location
        )

    def delete_location(
        self,
        location_id: str,
    ) -> None:
        location_id = location_id.strip()

        if not location_id:
            raise ValueError(
                "Die ID des Ausführungsortes darf nicht leer sein."
            )

        location = self.repository.get_by_id(
            location_id
        )

        if location is None:
            raise KeyError(
                "Ausführungsort nicht gefunden: "
                f"{location_id}"
            )

        if self.repository.has_course_days(
            location_id
        ):
            raise ValueError(
                "Der Ausführungsort kann nicht gelöscht werden, "
                "weil bereits Kurstage vorhanden sind."
            )

        self.repository.delete(
            location_id
        )

    def deactivate_location(
        self,
        location_id: str,
    ) -> None:
        self.repository.set_active_status(
            location_id,
            False,
            datetime.now(
                timezone.utc
            ),
        )

    def activate_location(
        self,
        location_id: str,
    ) -> None:
        self.repository.set_active_status(
            location_id,
            True,
            datetime.now(
                timezone.utc
            ),
        )

    @classmethod
    def normalize_phone_number(
        cls,
        nummer: str,
    ) -> str:
        try:
            parsed = phonenumbers.parse(
                nummer,
                cls.DEFAULT_REGION,
            )
        except phonenumbers.NumberParseException as exc:
            raise ValueError(
                "Die Telefonnummer konnte "
                "nicht erkannt werden."
            ) from exc

        if not phonenumbers.is_possible_number(
            parsed
        ):
            raise ValueError(
                "Die Telefonnummer ist nicht plausibel."
            )

        if not phonenumbers.is_valid_number(
            parsed
        ):
            raise ValueError(
                "Die Telefonnummer ist nicht gültig."
            )

        return phonenumbers.format_number(
            parsed,
            PhoneNumberFormat.E164,
        )

    @staticmethod
    def format_phone_for_display(
        nummer_e164: str | None,
    ) -> str:
        if not nummer_e164:
            return ""

        try:
            parsed = phonenumbers.parse(
                nummer_e164,
                None,
            )
        except phonenumbers.NumberParseException:
            return nummer_e164

        return phonenumbers.format_number(
            parsed,
            PhoneNumberFormat.INTERNATIONAL,
        )

    @staticmethod
    def validate_email(
        email: str | None,
    ) -> None:
        if not email:
            return

        if (
            "@" not in email
            or "." not in email.split("@")[-1]
        ):
            raise ValueError(
                "Die E-Mail-Adresse ist ungültig."
            )

    @staticmethod
    def _clean_optional(
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        value = value.strip()

        return value or None
