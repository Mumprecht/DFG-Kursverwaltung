import csv
from pathlib import Path

from dfg_kursverwaltung.core.models import (
    PhoneNumberType,
)
from dfg_kursverwaltung.services.kurstage_service import (
    CourseDayService,
)
from dfg_kursverwaltung.services.lehrgaenge_service import (
    CourseService,
)
from dfg_kursverwaltung.services.personen_service import (
    PersonService,
)
from dfg_kursverwaltung.services.standorte_service import (
    LocationService,
)
from dfg_kursverwaltung.services.telefonnummern_service import (
    PhoneNumberService,
)


class ExportService:
    def __init__(
        self,
        person_service: PersonService,
        phone_number_service: PhoneNumberService,
        location_service: LocationService,
        course_service: CourseService,
        course_day_service: CourseDayService,
    ):
        self.person_service = person_service
        self.phone_number_service = phone_number_service
        self.location_service = location_service
        self.course_service = course_service
        self.course_day_service = course_day_service

    # =========================================================
    # Personen
    # =========================================================

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
                fieldnames=self._person_fieldnames(),
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
                        "Teilnehmer": (
                            "Ja"
                            if person.ist_teilnehmer
                            else "Nein"
                        ),
                        "Instruktor": (
                            "Ja"
                            if person.ist_instruktor
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

    # =========================================================
    # Ausführungsorte
    # =========================================================

    def export_locations_csv(
        self,
        file_path: str | Path,
        *,
        include_inactive: bool = True,
    ) -> int:
        path = Path(file_path)

        locations = (
            self.location_service.list_locations(
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
                fieldnames=self._location_fieldnames(),
                delimiter=";",
                quoting=csv.QUOTE_MINIMAL,
            )

            writer.writeheader()

            for location in locations:
                phone_display = (
                    self.location_service
                    .format_phone_for_display(
                        location.telefon_e164
                    )
                )

                writer.writerow(
                    {
                        "ID": location.id,
                        "Bezeichnung": (
                            location.bezeichnung
                        ),
                        "Strasse": (
                            location.strasse or ""
                        ),
                        "Hausnummer": (
                            location.hausnummer or ""
                        ),
                        "PLZ": (
                            location.plz or ""
                        ),
                        "Ort": (
                            location.ort or ""
                        ),
                        "Kontakt Vorname": (
                            location.kontakt_vorname
                            or ""
                        ),
                        "Kontakt Nachname": (
                            location.kontakt_nachname
                            or ""
                        ),
                        "Telefon": (
                            phone_display or ""
                        ),
                        "E-Mail": (
                            location.email or ""
                        ),
                        "Webseite": (
                            location.webseite or ""
                        ),
                        "Aktiv": (
                            "Ja"
                            if location.aktiv
                            else "Nein"
                        ),
                        "Bemerkungen": (
                            location.bemerkungen or ""
                        ),
                    }
                )

        return len(locations)

    # =========================================================
    # Lehrgänge
    # =========================================================

    def export_courses_csv(
        self,
        file_path: str | Path,
    ) -> int:
        path = Path(file_path)

        courses = (
            self.course_service.list_courses()
        )

        with path.open(
            "w",
            encoding="utf-8-sig",
            newline="",
        ) as csv_file:
            writer = csv.DictWriter(
                csv_file,
                fieldnames=self._course_fieldnames(),
                delimiter=";",
                quoting=csv.QUOTE_MINIMAL,
            )

            writer.writeheader()

            for course in courses:
                writer.writerow(
                    {
                        "ID": course.id,
                        "Typ": course.typ.value,
                        "Bezeichnung": (
                            course.bezeichnung
                        ),
                        "Beschreibung": (
                            course.beschreibung or ""
                        ),
                        "Bemerkungen": (
                            course.bemerkungen or ""
                        ),
                    }
                )

        return len(courses)

    # =========================================================
    # Kurstage
    # =========================================================

    def export_course_days_csv(
        self,
        file_path: str | Path,
    ) -> int:
        path = Path(file_path)

        courses = (
            self.course_service.list_courses()
        )

        rows: list[dict[str, str]] = []

        for course in courses:
            course_days = (
                self.course_day_service
                .list_course_days(
                    course.id
                )
            )

            for course_day in course_days:
                location_name = ""

                if course_day.standort_id:
                    location = (
                        self.location_service
                        .get_location(
                            course_day.standort_id
                        )
                    )

                    if location is not None:
                        location_name = (
                            location.bezeichnung
                        )

                rows.append(
                    {
                        "ID": course_day.id,
                        "Lehrgang ID": (
                            course.id
                        ),
                        "Lehrgang": (
                            course.bezeichnung
                        ),
                        "Datum": (
                            course_day.datum.isoformat()
                        ),
                        "Beginn": (
                            course_day.beginn or ""
                        ),
                        "Ende": (
                            course_day.ende or ""
                        ),
                        "Standort ID": (
                            course_day.standort_id or ""
                        ),
                        "Standort": (
                            location_name
                        ),
                        "Bezeichnung": (
                            course_day.bezeichnung or ""
                        ),
                        "Bemerkungen": (
                            course_day.bemerkungen or ""
                        ),
                    }
                )

        with path.open(
            "w",
            encoding="utf-8-sig",
            newline="",
        ) as csv_file:
            writer = csv.DictWriter(
                csv_file,
                fieldnames=self._course_day_fieldnames(),
                delimiter=";",
                quoting=csv.QUOTE_MINIMAL,
            )

            writer.writeheader()

            writer.writerows(
                rows
            )

        return len(rows)

    # =========================================================
    # Telefonnummern Personen
    # =========================================================

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

    # =========================================================
    # CSV-Spalten
    # =========================================================

    @staticmethod
    def _person_fieldnames() -> list[str]:
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
            "Teilnehmer",
            "Instruktor",
            "Aktiv",
            "Telefon Primär",
            "Telefon Mobil",
            "Telefon Privat",
            "Telefon Geschäft",
            "Telefon Andere",
            "Bemerkungen",
        ]

    @staticmethod
    def _location_fieldnames() -> list[str]:
        return [
            "ID",
            "Bezeichnung",
            "Strasse",
            "Hausnummer",
            "PLZ",
            "Ort",
            "Kontakt Vorname",
            "Kontakt Nachname",
            "Telefon",
            "E-Mail",
            "Webseite",
            "Aktiv",
            "Bemerkungen",
        ]

    @staticmethod
    def _course_fieldnames() -> list[str]:
        return [
            "ID",
            "Typ",
            "Bezeichnung",
            "Beschreibung",
            "Bemerkungen",
        ]

    @staticmethod
    def _course_day_fieldnames() -> list[str]:
        return [
            "ID",
            "Lehrgang ID",
            "Lehrgang",
            "Datum",
            "Beginn",
            "Ende",
            "Standort ID",
            "Standort",
            "Bezeichnung",
            "Bemerkungen",
        ]