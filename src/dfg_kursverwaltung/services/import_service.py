import csv
from dataclasses import dataclass, field
from datetime import date
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


@dataclass(slots=True)
class ImportIssue:
    row_number: int
    message: str


@dataclass(slots=True)
class PersonImportRow:
    row_number: int
    person_id: str | None
    action: str

    nachname: str
    vorname: str
    geburtsdatum: date | None

    email: str | None
    strasse: str | None
    hausnummer: str | None
    plz: str | None
    ort: str | None
    organisation: str | None

    mitglied: bool
    aktiv: bool

    bemerkungen: str | None

    telefon_primaer: str | None
    telefon_mobil: list[str] = field(
        default_factory=list
    )
    telefon_privat: list[str] = field(
        default_factory=list
    )
    telefon_geschaeft: list[str] = field(
        default_factory=list
    )
    telefon_andere: list[str] = field(
        default_factory=list
    )


@dataclass(slots=True)
class ImportPreview:
    rows: list[PersonImportRow]
    issues: list[ImportIssue]

    @property
    def new_count(self) -> int:
        return sum(
            1
            for row in self.rows
            if row.action == "create"
        )

    @property
    def update_count(self) -> int:
        return sum(
            1
            for row in self.rows
            if row.action == "update"
        )

    @property
    def error_count(self) -> int:
        return len(
            self.issues
        )


class ImportService:
    REQUIRED_COLUMNS = {
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
    }

    def __init__(
        self,
        person_service: PersonService,
        phone_number_service: PhoneNumberService,
    ):
        self.person_service = person_service
        self.phone_number_service = phone_number_service

    def preview_person_import(
        self,
        file_path: str | Path,
    ) -> ImportPreview:
        path = Path(
            file_path
        )

        if not path.exists():
            raise FileNotFoundError(
                f"Datei nicht gefunden: {path}"
            )

        rows: list[PersonImportRow] = []
        issues: list[ImportIssue] = []

        with path.open(
            "r",
            encoding="utf-8-sig",
            newline="",
        ) as csv_file:
            reader = csv.DictReader(
                csv_file,
                delimiter=";",
            )

            if reader.fieldnames is None:
                raise ValueError(
                    "Die CSV-Datei enthält "
                    "keine Kopfzeile."
                )

            missing_columns = (
                self.REQUIRED_COLUMNS
                - set(reader.fieldnames)
            )

            if missing_columns:
                missing_text = ", ".join(
                    sorted(
                        missing_columns
                    )
                )

                raise ValueError(
                    "In der CSV-Datei fehlen "
                    "Spalten:\n"
                    + missing_text
                )

            for row_number, csv_row in enumerate(
                reader,
                start=2,
            ):
                try:
                    parsed_row = (
                        self._parse_person_row(
                            csv_row,
                            row_number,
                        )
                    )

                except ValueError as exc:
                    issues.append(
                        ImportIssue(
                            row_number=row_number,
                            message=str(exc),
                        )
                    )
                    continue

                rows.append(
                    parsed_row
                )

        return ImportPreview(
            rows=rows,
            issues=issues,
        )

    def import_persons(
        self,
        preview: ImportPreview,
    ) -> tuple[int, int]:
        created_count = 0
        updated_count = 0

        for row in preview.rows:
            if row.action == "create":
                person = (
                    self.person_service
                    .create_person(
                        nachname=row.nachname,
                        vorname=row.vorname,
                        geburtsdatum=(
                            row.geburtsdatum
                        ),
                        email=row.email,
                        strasse=row.strasse,
                        hausnummer=(
                            row.hausnummer
                        ),
                        plz=row.plz,
                        ort=row.ort,
                        organisation=(
                            row.organisation
                        ),
                        mitglied=row.mitglied,
                        bemerkungen=(
                            row.bemerkungen
                        ),
                    )
                )

                if not row.aktiv:
                    self.person_service.deactivate_person(
                        person.id
                    )

                self._replace_phone_numbers(
                    person.id,
                    row,
                )

                created_count += 1

            elif row.action == "update":
                if row.person_id is None:
                    raise ValueError(
                        "Bei einer Aktualisierung "
                        "fehlt die Personen-ID."
                    )

                person = (
                    self.person_service
                    .get_person(
                        row.person_id
                    )
                )

                if person is None:
                    raise ValueError(
                        "Person für Aktualisierung "
                        "nicht gefunden: "
                        f"{row.person_id}"
                    )

                person.nachname = row.nachname
                person.vorname = row.vorname
                person.geburtsdatum = (
                    row.geburtsdatum
                )
                person.email = row.email
                person.strasse = row.strasse
                person.hausnummer = (
                    row.hausnummer
                )
                person.plz = row.plz
                person.ort = row.ort
                person.organisation = (
                    row.organisation
                )
                person.mitglied = row.mitglied
                person.bemerkungen = (
                    row.bemerkungen
                )

                self.person_service.update_person(
                    person
                )

                if row.aktiv and not person.aktiv:
                    self.person_service.activate_person(
                        person.id
                    )

                elif (
                    not row.aktiv
                    and person.aktiv
                ):
                    self.person_service.deactivate_person(
                        person.id
                    )

                self._replace_phone_numbers(
                    person.id,
                    row,
                )

                updated_count += 1

        return (
            created_count,
            updated_count,
        )

    def _parse_person_row(
        self,
        csv_row: dict[str, str],
        row_number: int,
    ) -> PersonImportRow:
        nachname = self._required_text(
            csv_row.get(
                "Nachname"
            ),
            "Nachname",
        )

        vorname = self._required_text(
            csv_row.get(
                "Vorname"
            ),
            "Vorname",
        )

        person_id = self._clean_optional(
            csv_row.get(
                "ID"
            )
        )

        if person_id:
            existing = (
                self.person_service
                .get_person(
                    person_id
                )
            )

            action = (
                "update"
                if existing is not None
                else "create"
            )

        else:
            action = "create"

        geburtsdatum = self._parse_date(
            csv_row.get(
                "Geburtsdatum"
            )
        )

        mitglied = self._parse_bool(
            csv_row.get(
                "Mitglied"
            ),
            "Mitglied",
        )

        aktiv = self._parse_bool(
            csv_row.get(
                "Aktiv"
            ),
            "Aktiv",
        )

        telefon_primaer = (
            self._clean_optional(
                csv_row.get(
                    "Telefon Primär"
                )
            )
        )

        telefon_mobil = (
            self._parse_phone_list(
                csv_row.get(
                    "Telefon Mobil"
                )
            )
        )

        telefon_privat = (
            self._parse_phone_list(
                csv_row.get(
                    "Telefon Privat"
                )
            )
        )

        telefon_geschaeft = (
            self._parse_phone_list(
                csv_row.get(
                    "Telefon Geschäft"
                )
            )
        )

        telefon_andere = (
            self._parse_phone_list(
                csv_row.get(
                    "Telefon Andere"
                )
            )
        )

        self._validate_phone_numbers(
            telefon_primaer,
            telefon_mobil,
            telefon_privat,
            telefon_geschaeft,
            telefon_andere,
        )

        return PersonImportRow(
            row_number=row_number,
            person_id=person_id,
            action=action,
            nachname=nachname,
            vorname=vorname,
            geburtsdatum=geburtsdatum,
            email=self._clean_optional(
                csv_row.get(
                    "E-Mail"
                )
            ),
            strasse=self._clean_optional(
                csv_row.get(
                    "Strasse"
                )
            ),
            hausnummer=self._clean_optional(
                csv_row.get(
                    "Hausnummer"
                )
            ),
            plz=self._clean_optional(
                csv_row.get(
                    "PLZ"
                )
            ),
            ort=self._clean_optional(
                csv_row.get(
                    "Ort"
                )
            ),
            organisation=self._clean_optional(
                csv_row.get(
                    "Organisation"
                )
            ),
            mitglied=mitglied,
            aktiv=aktiv,
            bemerkungen=self._clean_optional(
                csv_row.get(
                    "Bemerkungen"
                )
            ),
            telefon_primaer=telefon_primaer,
            telefon_mobil=telefon_mobil,
            telefon_privat=telefon_privat,
            telefon_geschaeft=(
                telefon_geschaeft
            ),
            telefon_andere=telefon_andere,
        )

    def _replace_phone_numbers(
        self,
        person_id: str,
        row: PersonImportRow,
    ):
        existing_numbers = (
            self.phone_number_service
            .list_phone_numbers(
                person_id
            )
        )

        for phone_number in existing_numbers:
            self.phone_number_service.delete_phone_number(
                phone_number.id
            )

        entries: list[
            tuple[PhoneNumberType, str]
        ] = []

        entries.extend(
            (
                PhoneNumberType.MOBILE,
                number,
            )
            for number in row.telefon_mobil
        )

        entries.extend(
            (
                PhoneNumberType.PRIVATE,
                number,
            )
            for number in row.telefon_privat
        )

        entries.extend(
            (
                PhoneNumberType.BUSINESS,
                number,
            )
            for number in row.telefon_geschaeft
        )

        entries.extend(
            (
                PhoneNumberType.OTHER,
                number,
            )
            for number in row.telefon_andere
        )

        primary_normalized = None

        if row.telefon_primaer:
            primary_normalized = (
                self.phone_number_service
                .normalize_phone_number(
                    row.telefon_primaer
                )
            )

        for phone_type, number in entries:
            normalized = (
                self.phone_number_service
                .normalize_phone_number(
                    number
                )
            )

            is_primary = (
                primary_normalized is not None
                and normalized
                == primary_normalized
            )

            self.phone_number_service.create_phone_number(
                person_id=person_id,
                typ=phone_type,
                nummer=number,
                ist_primaer=is_primary,
            )

    def _validate_phone_numbers(
        self,
        primary: str | None,
        mobile: list[str],
        private: list[str],
        business: list[str],
        other: list[str],
    ):
        all_numbers = (
            mobile
            + private
            + business
            + other
        )

        normalized_numbers: set[str] = set()

        for number in all_numbers:
            normalized = (
                self.phone_number_service
                .normalize_phone_number(
                    number
                )
            )

            if normalized in normalized_numbers:
                raise ValueError(
                    "Eine Telefonnummer ist "
                    "mehrfach vorhanden: "
                    f"{number}"
                )

            normalized_numbers.add(
                normalized
            )

        if primary:
            primary_normalized = (
                self.phone_number_service
                .normalize_phone_number(
                    primary
                )
            )

            if (
                primary_normalized
                not in normalized_numbers
            ):
                raise ValueError(
                    "Die Primärnummer muss auch "
                    "in einer der Telefonspalten "
                    "enthalten sein."
                )

    @staticmethod
    def _parse_phone_list(
        value: str | None,
    ) -> list[str]:
        value = (
            value.strip()
            if value
            else ""
        )

        if not value:
            return []

        return [
            part.strip()
            for part in value.split(";")
            if part.strip()
        ]

    @staticmethod
    def _parse_date(
        value: str | None,
    ) -> date | None:
        value = (
            value.strip()
            if value
            else ""
        )

        if not value:
            return None

        try:
            return date.fromisoformat(
                value
            )

        except ValueError as exc:
            raise ValueError(
                "Ungültiges Geburtsdatum: "
                f"{value}. "
                "Erwartet wird JJJJ-MM-TT."
            ) from exc

    @staticmethod
    def _parse_bool(
        value: str | None,
        field_name: str,
    ) -> bool:
        value = (
            value.strip().casefold()
            if value
            else ""
        )

        if value in {
            "ja",
            "true",
            "1",
        }:
            return True

        if value in {
            "nein",
            "false",
            "0",
        }:
            return False

        raise ValueError(
            f'Ungültiger Wert in "{field_name}": '
            f'"{value}". Erwartet wird Ja oder Nein.'
        )

    @staticmethod
    def _required_text(
        value: str | None,
        field_name: str,
    ) -> str:
        value = (
            value.strip()
            if value
            else ""
        )

        if not value:
            raise ValueError(
                f'Das Feld "{field_name}" '
                "darf nicht leer sein."
            )

        return value

    @staticmethod
    def _clean_optional(
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        value = value.strip()

        return value or None