from datetime import datetime, timezone
from uuid import uuid4

import phonenumbers
from phonenumbers import PhoneNumberFormat

from dfg_kursverwaltung.core.models import (
    PhoneNumber,
    PhoneNumberType,
)
from dfg_kursverwaltung.repositories.telefonnummern_repository import (
    PhoneNumberRepository,
)


class PhoneNumberService:
    DEFAULT_REGION = "CH"

    def __init__(
        self,
        repository: PhoneNumberRepository,
    ):
        self.repository = repository

    def create_phone_number(
        self,
        *,
        person_id: str,
        typ: PhoneNumberType,
        nummer: str,
        ist_primaer: bool = False,
        bemerkungen: str | None = None,
    ) -> PhoneNumber:
        nummer_e164 = self.normalize_phone_number(
            nummer
        )

        existing_numbers = (
            self.repository.list_for_person(
                person_id
            )
        )

        for existing in existing_numbers:
            if existing.nummer_e164 == nummer_e164:
                raise ValueError(
                    "Diese Telefonnummer ist für "
                    "die Person bereits vorhanden."
                )

        # Die erste Telefonnummer wird automatisch primär.
        if not existing_numbers:
            ist_primaer = True

        if ist_primaer:
            self.repository.clear_primary(
                person_id
            )

        timestamp = datetime.now(
            timezone.utc
        )

        phone_number = PhoneNumber(
            id=str(uuid4()),
            person_id=person_id,
            typ=typ,
            nummer_e164=nummer_e164,
            ist_primaer=ist_primaer,
            bemerkungen=self._clean_optional(
                bemerkungen
            ),
            created_at=timestamp,
            updated_at=timestamp,
        )

        return self.repository.create(
            phone_number
        )

    def list_phone_numbers(
        self,
        person_id: str,
    ) -> list[PhoneNumber]:
        return self.repository.list_for_person(
            person_id
        )

    def delete_phone_number(
        self,
        phone_number_id: str,
    ) -> None:
        self.repository.delete(
            phone_number_id
        )

    @classmethod
    def normalize_phone_number(
        cls,
        nummer: str,
    ) -> str:
        nummer = nummer.strip()

        if not nummer:
            raise ValueError(
                "Telefonnummer darf nicht leer sein."
            )

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

        if not phonenumbers.is_possible_number(parsed):
            raise ValueError(
                "Die Telefonnummer ist nicht plausibel."
            )

        if not phonenumbers.is_valid_number(parsed):
            raise ValueError(
                "Die Telefonnummer ist nicht gültig."
            )

        return phonenumbers.format_number(
            parsed,
            PhoneNumberFormat.E164,
        )

    @staticmethod
    def format_for_display(
        nummer_e164: str,
    ) -> str:
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
    def _clean_optional(
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        value = value.strip()

        return value or None