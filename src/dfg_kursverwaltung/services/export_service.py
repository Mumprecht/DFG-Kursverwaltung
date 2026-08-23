import csv
from pathlib import Path

from dfg_kursverwaltung.core.models import (
    PhoneNumberType,
)
from dfg_kursverwaltung.services.personen_service import (
    PersonService,
)
from dfg_kursverwaltung.services.telefonnummern_service import (
    PhoneNumberService,
)


class ExportService:
    def __init__(
        self,
        person_service: PersonService,
        phone_number_service: PhoneNumberService,
    ):
        self.person_service = person_service
        self.phone_number_service = phone_number_service

    def export_persons_csv(
        self,
        file_path: str | Path,
        *,
        include_inactive: bool = True,
    ) -> int:
        path = Path(file_path)

        persons = (
            self.person_service.list_persons(
                include_inactive=include_inactive
            )
        )

        with path.open(
            "w",
            encoding="utf-8-sig",
            newline="",
        ) as csv_file:
            writer = csv.DictWriter(
                csv_file,
                fieldnames=self._fieldnames(),
                delimiter=";",
                quoting=csv.QUOTE_MINIMAL,
            )

            writer.writeheader()

            for person in persons:
                phone_numbers = (
                    self.phone_number_service
                    .list_phone_numbers(
                        person.id
                    )
                )

                phone_data = (
                    self._prepare_phone_numbers(
                        phone_numbers
                    )
                )

                writer.writerow(
                    {
                        "ID": person.id,
                        "Nachname": person.nachname,
                        "Vorname": person.vorname,
                        "Geburtsdatum": (
                            person.geburtsdatum.isoformat()
                            if person.geburtsdatum
                            else ""
                        ),
                        "E-Mail": person.email or "",
                        "Strasse": person.strasse or "",
                        "Hausnummer": (
                            person.hausnummer or ""
                        ),
                        "PLZ": person.plz or "",
                        "Ort": person.ort or "",
                        "Organisation": (
                            person.organisation or ""
                        ),
                        "Mitglied": (
                            "Ja"
                            if person.mitglied
                            else "Nein"
                        ),
                        "Aktiv": (
                            "Ja"
                            if person.aktiv
                            else "Nein"
                        ),
                        "Telefon Primär": (
                            phone_data["primary"]
                        ),
                        "Telefon Mobil": (
                            phone_data["mobile"]
                        ),
                        "Telefon Privat": (
                            phone_data["private"]
                        ),
                        "Telefon Geschäft": (
                            phone_data["business"]
                        ),
                        "Telefon Andere": (
                            phone_data["other"]
                        ),
                        "Bemerkungen": (
                            person.bemerkungen or ""
                        ),
                    }
                )

        return len(persons)

    def _prepare_phone_numbers(
        self,
        phone_numbers,
    ) -> dict[str, str]:
        grouped = {
            "mobile": [],
            "private": [],
            "business": [],
            "other": [],
        }

        primary = ""

        for phone_number in phone_numbers:
            display_number = (
                self.phone_number_service
                .format_for_display(
                    phone_number.nummer_e164
                )
            )

            if phone_number.ist_primaer:
                primary = display_number

            if (
                phone_number.typ
                == PhoneNumberType.MOBILE
            ):
                grouped["mobile"].append(
                    display_number
                )

            elif (
                phone_number.typ
                == PhoneNumberType.PRIVATE
            ):
                grouped["private"].append(
                    display_number
                )

            elif (
                phone_number.typ
                == PhoneNumberType.BUSINESS
            ):
                grouped["business"].append(
                    display_number
                )

            elif (
                phone_number.typ
                == PhoneNumberType.OTHER
            ):
                grouped["other"].append(
                    display_number
                )

        return {
            "primary": primary,
            "mobile": "; ".join(
                grouped["mobile"]
            ),
            "private": "; ".join(
                grouped["private"]
            ),
            "business": "; ".join(
                grouped["business"]
            ),
            "other": "; ".join(
                grouped["other"]
            ),
        }

    @staticmethod
    def _fieldnames() -> list[str]:
        return [
            "ID",
            "Nachname",
            "Vorname",
            "Geburtsdatum",
            "E-Mail",
            "Strasse",
            "Hausnummer",
            "PLZ",
            "Ort",
            "Organisation",
            "Mitglied",
            "Aktiv",
            "Telefon Primär",
            "Telefon Mobil",
            "Telefon Privat",
            "Telefon Geschäft",
            "Telefon Andere",
            "Bemerkungen",
        ]