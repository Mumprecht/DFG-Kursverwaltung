import csv
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

from dfg_kursverwaltung.core.database import DatabaseManager
from dfg_kursverwaltung.core.models import (
    User,
    CourseAssignmentRole,
    CourseAssignmentStatus,
    PhoneNumberType,
)
from dfg_kursverwaltung.core.permissions import (
    Permission,
    require_permission,
)
from dfg_kursverwaltung.services.kurstage_service import (
    CourseDayService,
)
from dfg_kursverwaltung.services.kurszuordnungen_service import (
    CourseAssignmentService,
)
from dfg_kursverwaltung.services.lehrgaenge_service import (
    CourseService,
)
from dfg_kursverwaltung.services.lehrgangstypen_service import (
    CourseTypeService,
)
from dfg_kursverwaltung.services.personen_service import (
    PersonService,
)
from dfg_kursverwaltung.services.pruefungsergebnisse_service import (
    ExamResultService,
)
from dfg_kursverwaltung.services.standorte_service import (
    LocationService,
)
from dfg_kursverwaltung.services.telefonnummern_service import (
    PhoneNumberService,
)


@dataclass(slots=True)
class ImportIssue:
    row_number: int
    message: str


# ============================================================
# Personen
# ============================================================

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
    ist_teilnehmer: bool
    ist_instruktor: bool
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


# ============================================================
# Ausführungsorte
# ============================================================

@dataclass(slots=True)
class LocationImportRow:
    row_number: int
    location_id: str | None
    action: str

    bezeichnung: str
    strasse: str | None
    hausnummer: str | None
    plz: str | None
    ort: str | None

    kontakt_vorname: str | None
    kontakt_nachname: str | None

    telefon: str | None
    email: str | None
    webseite: str | None

    aktiv: bool
    bemerkungen: str | None


@dataclass(slots=True)
class LocationImportPreview:
    rows: list[LocationImportRow]
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


# ============================================================
# Lehrgänge
# ============================================================

@dataclass(slots=True)
class CourseImportRow:
    row_number: int
    course_id: str | None
    action: str

    lehrgangstyp_id: str
    lehrgangstyp_bezeichnung: str
    bezeichnung: str
    beschreibung: str | None
    bemerkungen: str | None


@dataclass(slots=True)
class CourseImportPreview:
    rows: list[CourseImportRow]
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


# ============================================================
# Kurstage
# ============================================================

@dataclass(slots=True)
class CourseDayImportRow:
    row_number: int
    course_day_id: str | None
    action: str

    course_id: str
    course_name: str | None
    datum: date
    beginn: str | None
    ende: str | None
    location_id: str | None
    location_name: str | None
    bezeichnung: str | None
    bemerkungen: str | None


@dataclass(slots=True)
class CourseDayImportPreview:
    rows: list[CourseDayImportRow]
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


# ============================================================
# Kurszuordnungen
# ============================================================

@dataclass(slots=True)
class CourseAssignmentImportRow:
    row_number: int
    assignment_id: str | None
    action: str

    person_id: str
    kurstag_id: str

    rolle: CourseAssignmentRole
    status: CourseAssignmentStatus

    bemerkungen: str | None


@dataclass(slots=True)
class CourseAssignmentImportPreview:
    rows: list[CourseAssignmentImportRow]
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


# ============================================================
# Prüfungsergebnisse
# ============================================================

@dataclass(slots=True)
class ExamResultImportRow:
    row_number: int
    exam_result_id: str | None
    action: str

    assignment_id: str

    bestanden: bool
    note: str | None
    bemerkungen: str | None


@dataclass(slots=True)
class ExamResultImportPreview:
    rows: list[ExamResultImportRow]
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
    PERSON_REQUIRED_COLUMNS = {
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
    }

    LOCATION_REQUIRED_COLUMNS = {
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
    }

    COURSE_REQUIRED_COLUMNS = {
        "ID",
        "Typ",
        "Bezeichnung",
        "Beschreibung",
        "Bemerkungen",
    }

    COURSE_DAY_REQUIRED_COLUMNS = {
        "ID",
        "Lehrgang ID",
        "Lehrgang",
        "Lehrgangstyp",
        "Datum",
        "Beginn",
        "Ende",
        "Standort ID",
        "Standort",
        "Bezeichnung",
        "Bemerkungen",
    }

    COURSE_ASSIGNMENT_REQUIRED_COLUMNS = {
        "ID",
        "Person ID",
        "Nachname",
        "Vorname",
        "Geburtsdatum",
        "E-Mail",
        "Kurstag ID",
        "Lehrgang",
        "Lehrgangstyp",
        "Datum",
        "Beginn",
        "Ende",
        "Kurstag Bezeichnung",
        "Rolle",
        "Status",
        "Bemerkungen",
    }

    EXAM_RESULT_REQUIRED_COLUMNS = {
        "ID",
        "Kurszuordnung ID",
        "Person ID",
        "Nachname",
        "Vorname",
        "Geburtsdatum",
        "E-Mail",
        "Kurstag ID",
        "Lehrgang",
        "Lehrgangstyp",
        "Datum",
        "Beginn",
        "Ende",
        "Kurstag Bezeichnung",
        "Rolle",
        "Bestanden",
        "Note",
        "Bemerkungen",
    }

    def __init__(
        self,
        database_manager: DatabaseManager,
        person_service: PersonService,
        phone_number_service: PhoneNumberService,
        location_service: LocationService,
        course_service: CourseService,
        course_type_service: CourseTypeService,
        course_day_service: CourseDayService,
        assignment_service: CourseAssignmentService,
        exam_result_service: ExamResultService,
    ):
        self.database_manager = database_manager
        self.person_service = person_service
        self.phone_number_service = phone_number_service
        self.location_service = location_service
        self.course_service = course_service
        self.course_type_service = course_type_service
        self.course_day_service = course_day_service
        self.assignment_service = assignment_service
        self.exam_result_service = exam_result_service

    # ========================================================
    # Personen – Vorschau
    # ========================================================

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

        seen_create_emails: dict[str, int] = {}
        seen_create_identity: dict[
            tuple[str, str, date],
            int,
        ] = {}
        seen_update_ids: dict[str, int] = {}

        with path.open(
            "r",
            encoding="utf-8-sig",
            newline="",
        ) as csv_file:
            reader = csv.DictReader(
                csv_file,
                delimiter=";",
            )

            self._validate_columns(
                reader.fieldnames,
                self.PERSON_REQUIRED_COLUMNS,
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

                duplicate_message = None

                if parsed_row.action == "create":
                    if parsed_row.email:
                        email_key = (
                            parsed_row.email
                            .strip()
                            .casefold()
                        )

                        first_row = (
                            seen_create_emails.get(
                                email_key
                            )
                        )

                        if first_row is not None:
                            duplicate_message = (
                                "Dublette innerhalb der "
                                "Importdatei: Die "
                                "E-Mail-Adresse stimmt "
                                f"mit Zeile {first_row} "
                                "überein."
                            )

                    if (
                        duplicate_message is None
                        and parsed_row.geburtsdatum
                        is not None
                    ):
                        identity_key = (
                            parsed_row.vorname
                            .strip()
                            .casefold(),
                            parsed_row.nachname
                            .strip()
                            .casefold(),
                            parsed_row.geburtsdatum,
                        )

                        first_row = (
                            seen_create_identity.get(
                                identity_key
                            )
                        )

                        if first_row is not None:
                            duplicate_message = (
                                "Dublette innerhalb der "
                                "Importdatei: Vorname, "
                                "Nachname und "
                                "Geburtsdatum stimmen "
                                f"mit Zeile {first_row} "
                                "überein."
                            )

                elif (
                    parsed_row.action == "update"
                    and parsed_row.person_id
                ):
                    first_row = (
                        seen_update_ids.get(
                            parsed_row.person_id
                        )
                    )

                    if first_row is not None:
                        duplicate_message = (
                            "Dieselbe bestehende Person "
                            "wird innerhalb der "
                            "Importdatei mehrfach "
                            "aktualisiert: "
                            f"Zeile {first_row}."
                        )

                if duplicate_message is not None:
                    issues.append(
                        ImportIssue(
                            row_number=row_number,
                            message=duplicate_message,
                        )
                    )
                    continue

                rows.append(
                    parsed_row
                )

                if parsed_row.action == "create":
                    if parsed_row.email:
                        seen_create_emails[
                            parsed_row.email
                            .strip()
                            .casefold()
                        ] = row_number

                    if (
                        parsed_row.geburtsdatum
                        is not None
                    ):
                        seen_create_identity[
                            (
                                parsed_row.vorname
                                .strip()
                                .casefold(),
                                parsed_row.nachname
                                .strip()
                                .casefold(),
                                parsed_row.geburtsdatum,
                            )
                        ] = row_number

                elif (
                    parsed_row.action == "update"
                    and parsed_row.person_id
                ):
                    seen_update_ids[
                        parsed_row.person_id
                    ] = row_number

        return ImportPreview(
            rows=rows,
            issues=issues,
        )

    # ========================================================
    # Personen – Import
    # ========================================================

    def import_persons(
        self,
        preview: ImportPreview,
    ) -> tuple[int, int]:
        with self.database_manager.transaction():
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
                            ist_teilnehmer=(
                                row.ist_teilnehmer
                            ),
                            ist_instruktor=(
                                row.ist_instruktor
                            ),
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
                    person.ist_teilnehmer = (
                        row.ist_teilnehmer
                    )
                    person.ist_instruktor = (
                        row.ist_instruktor
                    )
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

    # ========================================================
    # Ausführungsorte – Vorschau
    # ========================================================

    def preview_location_import(
        self,
        file_path: str | Path,
    ) -> LocationImportPreview:
        path = Path(
            file_path
        )

        if not path.exists():
            raise FileNotFoundError(
                f"Datei nicht gefunden: {path}"
            )

        rows: list[LocationImportRow] = []
        issues: list[ImportIssue] = []

        seen_create_any_name: dict[str, int] = {}
        seen_create_without_location: dict[str, int] = {}
        seen_create_with_location: dict[
            tuple[str, str],
            int,
        ] = {}
        seen_update_ids: dict[str, int] = {}

        with path.open(
            "r",
            encoding="utf-8-sig",
            newline="",
        ) as csv_file:
            reader = csv.DictReader(
                csv_file,
                delimiter=";",
            )

            self._validate_columns(
                reader.fieldnames,
                self.LOCATION_REQUIRED_COLUMNS,
            )

            for row_number, csv_row in enumerate(
                reader,
                start=2,
            ):
                try:
                    parsed_row = (
                        self._parse_location_row(
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

                duplicate_message = None

                if parsed_row.action == "create":
                    name_key = (
                        parsed_row.bezeichnung
                        .strip()
                        .casefold()
                    )

                    location_key = (
                        parsed_row.ort
                        .strip()
                        .casefold()
                        if parsed_row.ort
                        else None
                    )

                    if location_key is None:
                        first_row = (
                            seen_create_any_name.get(
                                name_key
                            )
                        )

                        if first_row is not None:
                            duplicate_message = (
                                "Dublette innerhalb der "
                                "Importdatei: Die "
                                "Bezeichnung stimmt mit "
                                f"Zeile {first_row} "
                                "überein; mindestens bei "
                                "einem der beiden "
                                "Ausführungsorte ist kein "
                                "Ort angegeben."
                            )

                    else:
                        first_row = (
                            seen_create_without_location
                            .get(
                                name_key
                            )
                        )

                        if first_row is not None:
                            duplicate_message = (
                                "Dublette innerhalb der "
                                "Importdatei: Die "
                                "Bezeichnung stimmt mit "
                                f"Zeile {first_row} "
                                "überein; mindestens bei "
                                "einem der beiden "
                                "Ausführungsorte ist kein "
                                "Ort angegeben."
                            )

                        else:
                            first_row = (
                                seen_create_with_location
                                .get(
                                    (
                                        name_key,
                                        location_key,
                                    )
                                )
                            )

                            if first_row is not None:
                                duplicate_message = (
                                    "Dublette innerhalb "
                                    "der Importdatei: "
                                    "Bezeichnung und Ort "
                                    "stimmen mit Zeile "
                                    f"{first_row} "
                                    "überein."
                                )

                elif (
                    parsed_row.action == "update"
                    and parsed_row.location_id
                ):
                    first_row = (
                        seen_update_ids.get(
                            parsed_row.location_id
                        )
                    )

                    if first_row is not None:
                        duplicate_message = (
                            "Derselbe bestehende "
                            "Ausführungsort wird "
                            "innerhalb der "
                            "Importdatei mehrfach "
                            "aktualisiert: "
                            f"Zeile {first_row}."
                        )

                if duplicate_message is not None:
                    issues.append(
                        ImportIssue(
                            row_number=row_number,
                            message=duplicate_message,
                        )
                    )
                    continue

                rows.append(
                    parsed_row
                )

                if parsed_row.action == "create":
                    name_key = (
                        parsed_row.bezeichnung
                        .strip()
                        .casefold()
                    )

                    location_key = (
                        parsed_row.ort
                        .strip()
                        .casefold()
                        if parsed_row.ort
                        else None
                    )

                    seen_create_any_name.setdefault(
                        name_key,
                        row_number,
                    )

                    if location_key is None:
                        seen_create_without_location[
                            name_key
                        ] = row_number

                    else:
                        seen_create_with_location[
                            (
                                name_key,
                                location_key,
                            )
                        ] = row_number

                elif (
                    parsed_row.action == "update"
                    and parsed_row.location_id
                ):
                    seen_update_ids[
                        parsed_row.location_id
                    ] = row_number

        return LocationImportPreview(
            rows=rows,
            issues=issues,
        )

    # ========================================================
    # Ausführungsorte – Import
    # ========================================================

    def import_locations(
        self,
        preview: LocationImportPreview,
    ) -> tuple[int, int]:
        with self.database_manager.transaction():
            created_count = 0
            updated_count = 0

            for row in preview.rows:
                if row.action == "create":
                    location = (
                        self.location_service
                        .create_location(
                            bezeichnung=(
                                row.bezeichnung
                            ),
                            strasse=row.strasse,
                            hausnummer=(
                                row.hausnummer
                            ),
                            plz=row.plz,
                            ort=row.ort,
                            kontakt_vorname=(
                                row.kontakt_vorname
                            ),
                            kontakt_nachname=(
                                row.kontakt_nachname
                            ),
                            telefon=row.telefon,
                            email=row.email,
                            webseite=row.webseite,
                            bemerkungen=(
                                row.bemerkungen
                            ),
                        )
                    )

                    if not row.aktiv:
                        self.location_service.deactivate_location(
                            location.id
                        )

                    created_count += 1

                elif row.action == "update":
                    if row.location_id is None:
                        raise ValueError(
                            "Bei einer Aktualisierung "
                            "fehlt die Standort-ID."
                        )

                    location = (
                        self.location_service
                        .get_location(
                            row.location_id
                        )
                    )

                    if location is None:
                        raise ValueError(
                            "Ausführungsort für "
                            "Aktualisierung nicht "
                            "gefunden: "
                            f"{row.location_id}"
                        )

                    location.bezeichnung = (
                        row.bezeichnung
                    )
                    location.strasse = row.strasse
                    location.hausnummer = (
                        row.hausnummer
                    )
                    location.plz = row.plz
                    location.ort = row.ort
                    location.kontakt_vorname = (
                        row.kontakt_vorname
                    )
                    location.kontakt_nachname = (
                        row.kontakt_nachname
                    )
                    location.email = row.email
                    location.webseite = row.webseite
                    location.bemerkungen = (
                        row.bemerkungen
                    )

                    self.location_service.update_location(
                        location,
                        telefon=(
                            row.telefon
                            if row.telefon is not None
                            else ""
                        ),
                    )

                    if row.aktiv and not location.aktiv:
                        self.location_service.activate_location(
                            location.id
                        )

                    elif (
                        not row.aktiv
                        and location.aktiv
                    ):
                        self.location_service.deactivate_location(
                            location.id
                        )

                    updated_count += 1

            return (
                created_count,
                updated_count,
            )

    # ========================================================
    # Lehrgänge – Vorschau
    # ========================================================

    def preview_course_import(
        self,
        file_path: str | Path,
    ) -> CourseImportPreview:
        path = Path(
            file_path
        )

        if not path.exists():
            raise FileNotFoundError(
                f"Datei nicht gefunden: {path}"
            )

        rows: list[CourseImportRow] = []
        issues: list[ImportIssue] = []

        seen_create_courses: dict[
            tuple[str, str],
            int,
        ] = {}
        seen_update_ids: dict[str, int] = {}

        with path.open(
            "r",
            encoding="utf-8-sig",
            newline="",
        ) as csv_file:
            reader = csv.DictReader(
                csv_file,
                delimiter=";",
            )

            self._validate_columns(
                reader.fieldnames,
                self.COURSE_REQUIRED_COLUMNS,
            )

            for row_number, csv_row in enumerate(
                reader,
                start=2,
            ):
                try:
                    parsed_row = (
                        self._parse_course_row(
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

                duplicate_message = None

                if parsed_row.action == "create":
                    duplicate_key = (
                        parsed_row.lehrgangstyp_id,
                        parsed_row.bezeichnung
                        .strip()
                        .casefold(),
                    )

                    first_row = (
                        seen_create_courses.get(
                            duplicate_key
                        )
                    )

                    if first_row is not None:
                        duplicate_message = (
                            "Dublette innerhalb der "
                            "Importdatei: "
                            "Lehrgangstyp und "
                            "Bezeichnung stimmen mit "
                            f"Zeile {first_row} "
                            "überein."
                        )

                elif (
                    parsed_row.action == "update"
                    and parsed_row.course_id
                ):
                    first_row = (
                        seen_update_ids.get(
                            parsed_row.course_id
                        )
                    )

                    if first_row is not None:
                        duplicate_message = (
                            "Derselbe bestehende "
                            "Lehrgang wird innerhalb "
                            "der Importdatei mehrfach "
                            "aktualisiert: "
                            f"Zeile {first_row}."
                        )

                if duplicate_message is not None:
                    issues.append(
                        ImportIssue(
                            row_number=row_number,
                            message=duplicate_message,
                        )
                    )
                    continue

                rows.append(
                    parsed_row
                )

                if parsed_row.action == "create":
                    duplicate_key = (
                        parsed_row.lehrgangstyp_id,
                        parsed_row.bezeichnung
                        .strip()
                        .casefold(),
                    )

                    seen_create_courses[
                        duplicate_key
                    ] = row_number

                elif (
                    parsed_row.action == "update"
                    and parsed_row.course_id
                ):
                    seen_update_ids[
                        parsed_row.course_id
                    ] = row_number

        return CourseImportPreview(
            rows=rows,
            issues=issues,
        )

    # ========================================================
    # Lehrgänge – Import
    # ========================================================

    def import_courses(
        self,
        preview: CourseImportPreview,
    ) -> tuple[int, int]:
        with self.database_manager.transaction():
            created_count = 0
            updated_count = 0

            for row in preview.rows:
                if row.action == "create":
                    self.course_service.create_course(
                        lehrgangstyp_id=(
                            row.lehrgangstyp_id
                        ),
                        bezeichnung=row.bezeichnung,
                        beschreibung=row.beschreibung,
                        bemerkungen=row.bemerkungen,
                    )

                    created_count += 1

                elif row.action == "update":
                    if row.course_id is None:
                        raise ValueError(
                            "Bei einer Aktualisierung "
                            "fehlt die Lehrgangs-ID."
                        )

                    course = (
                        self.course_service.get_course(
                            row.course_id
                        )
                    )

                    if course is None:
                        raise ValueError(
                            "Lehrgang für Aktualisierung "
                            "nicht gefunden: "
                            f"{row.course_id}"
                        )

                    course.lehrgangstyp_id = (
                        row.lehrgangstyp_id
                    )
                    course.bezeichnung = (
                        row.bezeichnung
                    )
                    course.beschreibung = (
                        row.beschreibung
                    )
                    course.bemerkungen = (
                        row.bemerkungen
                    )

                    self.course_service.update_course(
                        course
                    )

                    updated_count += 1

            return (
                created_count,
                updated_count,
            )

    # ========================================================
    # Kurstage – Vorschau
    # ========================================================

    def preview_course_day_import(
        self,
        file_path: str | Path,
    ) -> CourseDayImportPreview:
        path = Path(
            file_path
        )

        if not path.exists():
            raise FileNotFoundError(
                f"Datei nicht gefunden: {path}"
            )

        rows: list[CourseDayImportRow] = []
        issues: list[ImportIssue] = []

        seen_create_course_days: dict[
            tuple[
                str,
                date,
                str | None,
                str | None,
            ],
            int,
        ] = {}
        seen_update_ids: dict[str, int] = {}

        with path.open(
            "r",
            encoding="utf-8-sig",
            newline="",
        ) as csv_file:
            reader = csv.DictReader(
                csv_file,
                delimiter=";",
            )

            self._validate_columns(
                reader.fieldnames,
                self.COURSE_DAY_REQUIRED_COLUMNS,
            )

            for row_number, csv_row in enumerate(
                reader,
                start=2,
            ):
                try:
                    parsed_row = (
                        self._parse_course_day_row(
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

                duplicate_message = None

                if parsed_row.action == "create":
                    duplicate_key = (
                        parsed_row.course_id,
                        parsed_row.datum,
                        parsed_row.beginn,
                        parsed_row.ende,
                    )

                    first_row = (
                        seen_create_course_days.get(
                            duplicate_key
                        )
                    )

                    if first_row is not None:
                        duplicate_message = (
                            "Dublette innerhalb der "
                            "Importdatei: Lehrgang, "
                            "Datum, Beginn und Ende "
                            "stimmen mit "
                            f"Zeile {first_row} "
                            "überein."
                        )

                elif (
                    parsed_row.action == "update"
                    and parsed_row.course_day_id
                ):
                    first_row = (
                        seen_update_ids.get(
                            parsed_row.course_day_id
                        )
                    )

                    if first_row is not None:
                        duplicate_message = (
                            "Derselbe bestehende "
                            "Kurstag wird innerhalb "
                            "der Importdatei mehrfach "
                            "aktualisiert: "
                            f"Zeile {first_row}."
                        )

                if duplicate_message is not None:
                    issues.append(
                        ImportIssue(
                            row_number=row_number,
                            message=duplicate_message,
                        )
                    )
                    continue

                rows.append(
                    parsed_row
                )

                if parsed_row.action == "create":
                    duplicate_key = (
                        parsed_row.course_id,
                        parsed_row.datum,
                        parsed_row.beginn,
                        parsed_row.ende,
                    )

                    seen_create_course_days[
                        duplicate_key
                    ] = row_number

                elif (
                    parsed_row.action == "update"
                    and parsed_row.course_day_id
                ):
                    seen_update_ids[
                        parsed_row.course_day_id
                    ] = row_number

        return CourseDayImportPreview(
            rows=rows,
            issues=issues,
        )

    # ========================================================
    # Kurstage – Import
    # ========================================================

    def import_course_days(
        self,
        preview: CourseDayImportPreview,
    ) -> tuple[int, int]:
        with self.database_manager.transaction():
            created_count = 0
            updated_count = 0

            for row in preview.rows:
                if row.action == "create":
                    self.course_day_service.create_course_day(
                        lehrgang_id=row.course_id,
                        datum=row.datum,
                        standort_id=row.location_id,
                        beginn=row.beginn,
                        ende=row.ende,
                        bezeichnung=row.bezeichnung,
                        bemerkungen=row.bemerkungen,
                    )

                    created_count += 1

                elif row.action == "update":
                    if row.course_day_id is None:
                        raise ValueError(
                            "Bei einer Aktualisierung "
                            "fehlt die Kurstag-ID."
                        )

                    course_day = (
                        self.course_day_service
                        .get_course_day(
                            row.course_day_id
                        )
                    )

                    if course_day is None:
                        raise ValueError(
                            "Kurstag für Aktualisierung "
                            "nicht gefunden: "
                            f"{row.course_day_id}"
                        )

                    course_day.lehrgang_id = row.course_id
                    course_day.standort_id = row.location_id
                    course_day.datum = row.datum
                    course_day.beginn = row.beginn
                    course_day.ende = row.ende
                    course_day.bezeichnung = (
                        row.bezeichnung
                    )
                    course_day.bemerkungen = (
                        row.bemerkungen
                    )

                    self.course_day_service.update_course_day(
                        course_day
                    )

                    updated_count += 1

            return (
                created_count,
                updated_count,
            )

    # ========================================================
    # Kurszuordnungen – Vorschau
    # ========================================================

    # ========================================================
    # Prüfungsergebnisse – Vorschau
    # ========================================================

    def import_exam_results(
        self,
        actor: User,
        preview: ExamResultImportPreview,
    ) -> tuple[int, int]:
        with self.database_manager.transaction():
            require_permission(
                actor,
                Permission.IMPORT,
            )

            created_count = 0
            updated_count = 0

            for row in preview.rows:
                if row.action == "create":
                    self.exam_result_service.create_exam_result(
                        actor=actor,
                        kurszuordnung_id=row.assignment_id,
                        bestanden=row.bestanden,
                        note=row.note,
                        bemerkungen=row.bemerkungen,
                    )

                    created_count += 1

                elif row.action == "update":
                    if row.exam_result_id is None:
                        raise RuntimeError(
                            "Für ein Update fehlt die "
                            "Prüfungsergebnis-ID."
                        )

                    existing = (
                        self.exam_result_service
                        .get_exam_result(
                            row.exam_result_id
                        )
                    )

                    if existing is None:
                        raise RuntimeError(
                            "Das zu aktualisierende "
                            "Prüfungsergebnis wurde "
                            "nicht gefunden."
                        )

                    # Die historische Kurszuordnung
                    # bleibt bei einem Update bewusst
                    # unverändert.
                    existing.bestanden = row.bestanden
                    existing.note = row.note
                    existing.bemerkungen = (
                        row.bemerkungen
                    )

                    self.exam_result_service.update_exam_result(
                        actor,
                        existing,
                    )

                    updated_count += 1

                else:
                    raise RuntimeError(
                        "Unbekannte Importaktion: "
                        f"{row.action}"
                    )

            return (
                created_count,
                updated_count,
            )


    def preview_exam_result_import(
        self,
        file_path: str | Path,
    ) -> ExamResultImportPreview:
        path = Path(
            file_path
        )

        if not path.exists():
            raise FileNotFoundError(
                f"Datei nicht gefunden: {path}"
            )

        rows: list[ExamResultImportRow] = []
        issues: list[ImportIssue] = []

        seen_create_assignments: dict[str, int] = {}
        seen_update_ids: dict[str, int] = {}

        with path.open(
            "r",
            encoding="utf-8-sig",
            newline="",
        ) as csv_file:
            reader = csv.DictReader(
                csv_file,
                delimiter=";",
            )

            fieldnames = set(
                reader.fieldnames or []
            )

            missing_columns = (
                self.EXAM_RESULT_REQUIRED_COLUMNS
                - fieldnames
            )

            if missing_columns:
                missing_text = ", ".join(
                    sorted(missing_columns)
                )

                raise ValueError(
                    "Folgende Pflichtspalten fehlen: "
                    f"{missing_text}"
                )

            for row_number, csv_row in enumerate(
                reader,
                start=2,
            ):
                try:
                    parsed_row = (
                        self._parse_exam_result_row(
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

                duplicate_message = None

                if parsed_row.action == "create":
                    first_row = (
                        seen_create_assignments.get(
                            parsed_row.assignment_id
                        )
                    )

                    if first_row is not None:
                        duplicate_message = (
                            "Dublette innerhalb der "
                            "Importdatei: Für dieselbe "
                            "Kurszuordnung ist bereits "
                            "in Zeile "
                            f"{first_row} ein "
                            "Prüfungsergebnis enthalten."
                        )

                elif (
                    parsed_row.action == "update"
                    and parsed_row.exam_result_id
                ):
                    first_row = (
                        seen_update_ids.get(
                            parsed_row.exam_result_id
                        )
                    )

                    if first_row is not None:
                        duplicate_message = (
                            "Dasselbe bestehende "
                            "Prüfungsergebnis wird "
                            "innerhalb der Importdatei "
                            "mehrfach aktualisiert: "
                            f"Zeile {first_row}."
                        )

                if duplicate_message is not None:
                    issues.append(
                        ImportIssue(
                            row_number=row_number,
                            message=duplicate_message,
                        )
                    )
                    continue

                rows.append(
                    parsed_row
                )

                if parsed_row.action == "create":
                    seen_create_assignments[
                        parsed_row.assignment_id
                    ] = row_number

                elif (
                    parsed_row.action == "update"
                    and parsed_row.exam_result_id
                ):
                    seen_update_ids[
                        parsed_row.exam_result_id
                    ] = row_number

        return ExamResultImportPreview(
            rows=rows,
            issues=issues,
        )


    def preview_course_assignment_import(
        self,
        file_path: str | Path,
    ) -> CourseAssignmentImportPreview:
        path = Path(
            file_path
        )

        if not path.exists():
            raise FileNotFoundError(
                f"Datei nicht gefunden: {path}"
            )

        rows: list[CourseAssignmentImportRow] = []
        issues: list[ImportIssue] = []

        seen_create_assignments: dict[
            tuple[str, str],
            int,
        ] = {}
        seen_update_ids: dict[str, int] = {}

        with path.open(
            "r",
            encoding="utf-8-sig",
            newline="",
        ) as csv_file:
            reader = csv.DictReader(
                csv_file,
                delimiter=";",
            )

            self._validate_columns(
                reader.fieldnames,
                self.COURSE_ASSIGNMENT_REQUIRED_COLUMNS,
            )

            for row_number, csv_row in enumerate(
                reader,
                start=2,
            ):
                try:
                    parsed_row = (
                        self._parse_course_assignment_row(
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

                duplicate_message = None

                if parsed_row.action == "create":
                    duplicate_key = (
                        parsed_row.person_id,
                        parsed_row.kurstag_id,
                    )

                    first_row = (
                        seen_create_assignments.get(
                            duplicate_key
                        )
                    )

                    if first_row is not None:
                        duplicate_message = (
                            "Dublette innerhalb der "
                            "Importdatei: Dieselbe Person "
                            "ist bereits in Zeile "
                            f"{first_row} demselben "
                            "Kurstag zugeordnet."
                        )

                elif (
                    parsed_row.action == "update"
                    and parsed_row.assignment_id
                ):
                    first_row = (
                        seen_update_ids.get(
                            parsed_row.assignment_id
                        )
                    )

                    if first_row is not None:
                        duplicate_message = (
                            "Dieselbe bestehende "
                            "Kurszuordnung wird innerhalb "
                            "der Importdatei mehrfach "
                            "aktualisiert: "
                            f"Zeile {first_row}."
                        )

                if duplicate_message is not None:
                    issues.append(
                        ImportIssue(
                            row_number=row_number,
                            message=duplicate_message,
                        )
                    )
                    continue

                rows.append(
                    parsed_row
                )

                if parsed_row.action == "create":
                    seen_create_assignments[
                        (
                            parsed_row.person_id,
                            parsed_row.kurstag_id,
                        )
                    ] = row_number

                elif (
                    parsed_row.action == "update"
                    and parsed_row.assignment_id
                ):
                    seen_update_ids[
                        parsed_row.assignment_id
                    ] = row_number

        return CourseAssignmentImportPreview(
            rows=rows,
            issues=issues,
        )

    # ========================================================
    # Kurszuordnungen – Import
    # ========================================================

    def import_course_assignments(
        self,
        actor: User,
        preview: CourseAssignmentImportPreview,
    ) -> tuple[int, int]:
        with self.database_manager.transaction():
            require_permission(
                actor,
                Permission.IMPORT,
            )

            created_count = 0
            updated_count = 0

            for row in preview.rows:
                if row.action == "create":
                    self.assignment_service.create_historical_assignment(
                        actor=actor,
                        person_id=row.person_id,
                        kurstag_id=row.kurstag_id,
                        rolle=row.rolle,
                        status=row.status,
                        bemerkungen=row.bemerkungen,
                    )

                    created_count += 1

                elif row.action == "update":
                    if row.assignment_id is None:
                        raise ValueError(
                            "Bei einer Aktualisierung fehlt "
                            "die Kurszuordnungs-ID."
                        )

                    assignment = (
                        self.assignment_service
                        .get_assignment(
                            row.assignment_id
                        )
                    )

                    if assignment is None:
                        raise ValueError(
                            "Kurszuordnung für "
                            "Aktualisierung nicht gefunden: "
                            f"{row.assignment_id}"
                        )

                    # Die Person und der Kurstag bilden
                    # die historische Identität der
                    # Zuordnung und werden nicht ersetzt.
                    assignment.rolle = row.rolle
                    assignment.status = row.status
                    assignment.bemerkungen = (
                        row.bemerkungen
                    )

                    self.assignment_service.update_assignment(
                        actor,
                        assignment,
                    )

                    updated_count += 1

            return (
                created_count,
                updated_count,
            )

    # ========================================================
    # Personen – CSV-Zeile
    # ========================================================

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

        if (
            geburtsdatum is not None
            and geburtsdatum > date.today()
        ):
            raise ValueError(
                "Das Geburtsdatum darf nicht "
                "in der Zukunft liegen."
            )

        email = self._clean_optional(
            csv_row.get(
                "E-Mail"
            )
        )

        self.person_service.validate_email(
            email
        )

        mitglied = self._parse_bool(
            csv_row.get(
                "Mitglied"
            ),
            "Mitglied",
        )

        ist_teilnehmer = self._parse_bool(
            csv_row.get(
                "Teilnehmer"
            ),
            "Teilnehmer",
        )

        ist_instruktor = self._parse_bool(
            csv_row.get(
                "Instruktor"
            ),
            "Instruktor",
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
            email=email,
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
            ist_teilnehmer=ist_teilnehmer,
            ist_instruktor=ist_instruktor,
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

    # ========================================================
    # Ausführungsorte – CSV-Zeile
    # ========================================================

    def _parse_location_row(
        self,
        csv_row: dict[str, str],
        row_number: int,
    ) -> LocationImportRow:
        bezeichnung = self._required_text(
            csv_row.get(
                "Bezeichnung"
            ),
            "Bezeichnung",
        )

        location_id = self._clean_optional(
            csv_row.get(
                "ID"
            )
        )

        if location_id:
            existing = (
                self.location_service
                .get_location(
                    location_id
                )
            )

            action = (
                "update"
                if existing is not None
                else "create"
            )

        else:
            action = "create"

        telefon = self._clean_optional(
            csv_row.get(
                "Telefon"
            )
        )

        if telefon:
            self.location_service.normalize_phone_number(
                telefon
            )

        email = self._clean_optional(
            csv_row.get(
                "E-Mail"
            )
        )

        self.location_service.validate_email(
            email
        )

        aktiv = self._parse_bool(
            csv_row.get(
                "Aktiv"
            ),
            "Aktiv",
        )

        return LocationImportRow(
            row_number=row_number,
            location_id=location_id,
            action=action,
            bezeichnung=bezeichnung,
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
            kontakt_vorname=self._clean_optional(
                csv_row.get(
                    "Kontakt Vorname"
                )
            ),
            kontakt_nachname=self._clean_optional(
                csv_row.get(
                    "Kontakt Nachname"
                )
            ),
            telefon=telefon,
            email=email,
            webseite=self._clean_optional(
                csv_row.get(
                    "Webseite"
                )
            ),
            aktiv=aktiv,
            bemerkungen=self._clean_optional(
                csv_row.get(
                    "Bemerkungen"
                )
            ),
        )

    # ========================================================
    # Lehrgänge – CSV-Zeile
    # ========================================================

    def _parse_course_row(
        self,
        csv_row: dict[str, str],
        row_number: int,
    ) -> CourseImportRow:
        course_id = self._clean_optional(
            csv_row.get(
                "ID"
            )
        )

        type_text = self._required_text(
            csv_row.get(
                "Typ"
            ),
            "Typ",
        )

        course_type = (
            self.course_type_service
            .get_course_type_by_name(
                type_text
            )
        )

        if course_type is None:
            raise ValueError(
                "Unbekannter Lehrgangstyp: "
                f"{type_text}."
            )

        if not course_type.aktiv:
            raise ValueError(
                "Der Lehrgangstyp ist nicht aktiv: "
                f"{type_text}."
            )

        bezeichnung = self._required_text(
            csv_row.get(
                "Bezeichnung"
            ),
            "Bezeichnung",
        )

        existing = None

        if course_id:
            existing = (
                self.course_service
                .get_course(
                    course_id
                )
            )

        if existing is None:
            existing = (
                self.course_service
                .get_course_by_type_and_name(
                    course_type.id,
                    bezeichnung,
                )
            )

        if existing is not None:
            action = "update"
            resolved_course_id = existing.id

        else:
            action = "create"
            resolved_course_id = None

        return CourseImportRow(
            row_number=row_number,
            course_id=resolved_course_id,
            action=action,
            lehrgangstyp_id=course_type.id,
            lehrgangstyp_bezeichnung=(
                course_type.bezeichnung
            ),
            bezeichnung=bezeichnung,
            beschreibung=self._clean_optional(
                csv_row.get(
                    "Beschreibung"
                )
            ),
            bemerkungen=self._clean_optional(
                csv_row.get(
                    "Bemerkungen"
                )
            ),
        )

    # ========================================================
    # Kurstage – CSV-Zeile
    # ========================================================

    def _parse_course_day_row(
        self,
        csv_row: dict[str, str],
        row_number: int,
    ) -> CourseDayImportRow:
        course_day_id = self._clean_optional(
            csv_row.get(
                "ID"
            )
        )

        course_id = self._clean_optional(
            csv_row.get(
                "Lehrgang ID"
            )
        )

        course_name = self._required_text(
            csv_row.get(
                "Lehrgang"
            ),
            "Lehrgang",
        )

        course_type_name = self._required_text(
            csv_row.get(
                "Lehrgangstyp"
            ),
            "Lehrgangstyp",
        )

        course = None

        if course_id:
            course = (
                self.course_service.get_course(
                    course_id
                )
            )

        if course is None:
            course_type = (
                self.course_type_service
                .get_course_type_by_name(
                    course_type_name
                )
            )

            if course_type is None:
                raise ValueError(
                    "Unbekannter Lehrgangstyp: "
                    f"{course_type_name}."
                )

            course = (
                self.course_service
                .get_course_by_type_and_name(
                    course_type.id,
                    course_name,
                )
            )

        if course is None:
            raise ValueError(
                "Der Lehrgang konnte nicht "
                "aufgelöst werden: "
                f"{course_type_name} / "
                f"{course_name}"
            )

        course_id = course.id

        date_text = self._required_text(
            csv_row.get(
                "Datum"
            ),
            "Datum",
        )

        course_date = self._parse_course_day_date(
            date_text
        )

        beginn = self._clean_optional(
            csv_row.get(
                "Beginn"
            )
        )

        ende = self._clean_optional(
            csv_row.get(
                "Ende"
            )
        )

        self.course_day_service.validate_times(
            beginn,
            ende,
        )

        location_id = self._clean_optional(
            csv_row.get(
                "Standort ID"
            )
        )

        location_name = self._clean_optional(
            csv_row.get(
                "Standort"
            )
        )

        location = None

        if location_id:
            location = (
                self.location_service.get_location(
                    location_id
                )
            )

        if location is None and location_name:
            normalized_location_name = (
                location_name.strip().casefold()
            )

            matching_locations = [
                candidate
                for candidate
                in self.location_service.list_locations(
                    include_inactive=True
                )
                if (
                    candidate.bezeichnung
                    .strip()
                    .casefold()
                    == normalized_location_name
                )
            ]

            if len(matching_locations) > 1:
                raise ValueError(
                    "Der Standort kann nicht eindeutig "
                    "aufgelöst werden: "
                    f"{location_name}."
                )

            if len(matching_locations) == 1:
                location = matching_locations[0]

        if location is not None:
            location_id = location.id

        elif location_id:
            raise ValueError(
                "Die Standort ID ist unbekannt und "
                "der Standort konnte nicht über die "
                "Bezeichnung aufgelöst werden: "
                f"{location_id}"
            )

        elif location_name:
            raise ValueError(
                "Der Standort konnte nicht aufgelöst "
                "werden: "
                f"{location_name}."
            )

        existing = None

        if course_day_id:
            existing = (
                self.course_day_service
                .get_course_day(
                    course_day_id
                )
            )

        if existing is None:
            existing = (
                self.course_day_service
                .get_course_day_by_identity(
                    lehrgang_id=course_id,
                    datum=course_date,
                    beginn=beginn,
                    ende=ende,
                    bezeichnung=self._clean_optional(
                        csv_row.get(
                            "Bezeichnung"
                        )
                    ),
                )
            )

        if existing is not None:
            action = "update"
            resolved_course_day_id = (
                existing.id
            )

        else:
            action = "create"
            resolved_course_day_id = None

        return CourseDayImportRow(
            row_number=row_number,
            course_day_id=(
                resolved_course_day_id
            ),
            action=action,
            course_id=course_id,
            course_name=self._clean_optional(
                csv_row.get(
                    "Lehrgang"
                )
            ),
            datum=course_date,
            beginn=beginn,
            ende=ende,
            location_id=location_id,
            location_name=self._clean_optional(
                csv_row.get(
                    "Standort"
                )
            ),
            bezeichnung=self._clean_optional(
                csv_row.get(
                    "Bezeichnung"
                )
            ),
            bemerkungen=self._clean_optional(
                csv_row.get(
                    "Bemerkungen"
                )
            ),
        )

    # ========================================================
    # Kurszuordnungen – CSV-Zeile
    # ========================================================

    # ========================================================
    # Prüfungsergebnisse – CSV-Zeile
    # ========================================================

    def _parse_exam_result_row(
        self,
        csv_row: dict[str, str],
        row_number: int,
    ) -> ExamResultImportRow:
        exam_result_id = self._clean_optional(
            csv_row.get("ID")
        )

        # ----------------------------------------------------
        # Kurszuordnung auflösen
        # ----------------------------------------------------

        assignment_id = self._clean_optional(
            csv_row.get("Kurszuordnung ID")
        )

        assignment = None

        if assignment_id:
            assignment = (
                self.assignment_service
                .get_assignment(
                    assignment_id
                )
            )

        # Bei einer fremden oder fehlenden
        # Kurszuordnungs-ID verwenden wir dieselbe
        # fachliche Auflösung wie beim bereits getesteten
        # Kurszuordnungs-Import.
        if assignment is None:
            # Die Prüfungsergebnis-CSV enthält keinen
            # Zuordnungsstatus. Für die fachliche Auflösung
            # einer bereits bestehenden Kurszuordnung wird
            # dieser jedoch nicht benötigt.
            #
            # _parse_course_assignment_row() erwartet das
            # Feld aus Validierungsgründen trotzdem. Deshalb
            # arbeiten wir mit einer Kopie und ergänzen nur
            # für die Auflösung einen neutralen Status.
            assignment_csv_row = dict(
                csv_row
            )

            assignment_csv_row.setdefault(
                "Status",
                "registered",
            )

            assignment_row = (
                self._parse_course_assignment_row(
                    assignment_csv_row,
                    row_number,
                )
            )

            if assignment_row.assignment_id:
                assignment = (
                    self.assignment_service
                    .get_assignment(
                        assignment_row.assignment_id
                    )
                )

            if assignment is None:
                assignment = (
                    self.assignment_service
                    .get_assignment_for_person_and_course_day(
                        assignment_row.person_id,
                        assignment_row.kurstag_id,
                    )
                )

        if assignment is None:
            raise ValueError(
                "Die Kurszuordnung für das "
                "Prüfungsergebnis konnte nicht "
                "aufgelöst werden."
            )

        assignment_id = assignment.id

        # ----------------------------------------------------
        # Prüfungsergebnis auflösen
        # ----------------------------------------------------

        existing = None

        if exam_result_id:
            existing = (
                self.exam_result_service
                .get_exam_result(
                    exam_result_id
                )
            )

        # Fremde Prüfungsergebnis-ID:
        # Ein Prüfungsergebnis ist fachlich eindeutig
        # über die Kurszuordnung identifizierbar.
        if existing is None:
            existing = (
                self.exam_result_service
                .get_exam_result_for_assignment(
                    assignment_id
                )
            )

        if existing is not None:
            action = "update"
            resolved_exam_result_id = (
                existing.id
            )

        else:
            action = "create"
            resolved_exam_result_id = None

        # ----------------------------------------------------
        # Ergebnisdaten
        # ----------------------------------------------------

        bestanden = self._parse_bool(
            csv_row.get("Bestanden"),
            "Bestanden",
        )

        note = self._clean_optional(
            csv_row.get("Note")
        )

        bemerkungen = self._clean_optional(
            csv_row.get("Bemerkungen")
        )

        return ExamResultImportRow(
            row_number=row_number,
            exam_result_id=(
                resolved_exam_result_id
            ),
            action=action,
            assignment_id=assignment_id,
            bestanden=bestanden,
            note=note,
            bemerkungen=bemerkungen,
        )


    def _parse_course_assignment_row(
        self,
        csv_row: dict[str, str],
        row_number: int,
    ) -> CourseAssignmentImportRow:
        assignment_id = self._clean_optional(
            csv_row.get("ID")
        )

        # ----------------------------------------------------
        # Person auflösen
        # ----------------------------------------------------

        person_id = self._clean_optional(
            csv_row.get("Person ID")
        )

        nachname = self._required_text(
            csv_row.get("Nachname"),
            "Nachname",
        )

        vorname = self._required_text(
            csv_row.get("Vorname"),
            "Vorname",
        )

        email = self._clean_optional(
            csv_row.get("E-Mail")
        )

        birthdate_text = self._clean_optional(
            csv_row.get("Geburtsdatum")
        )

        birthdate = None

        if birthdate_text:
            birthdate = self._parse_date(
                birthdate_text
            )

        person = None

        if person_id:
            person = self.person_service.get_person(
                person_id
            )

        if person is None and email:
            person = (
                self.person_service
                .get_person_by_email(
                    email
                )
            )

            if (
                person is not None
                and birthdate is not None
                and person.geburtsdatum != birthdate
            ):
                raise ValueError(
                    "E-Mail-Adresse und Geburtsdatum "
                    "verweisen nicht auf dieselbe Person."
                )

        if (
            person is None
            and birthdate is not None
        ):
            person = (
                self.person_service
                .get_person_by_name_and_birthdate(
                    nachname,
                    vorname,
                    birthdate,
                )
            )

        if person is None:
            if not email and birthdate is None:
                raise ValueError(
                    "Die Person kann nicht eindeutig "
                    "identifiziert werden. Es wird "
                    "zusätzlich zur Person-ID entweder "
                    "eine E-Mail-Adresse oder ein "
                    "Geburtsdatum benötigt."
                )

            raise ValueError(
                "Die Person konnte nicht aufgelöst "
                "werden: "
                f"{nachname} {vorname}."
            )

        person_id = person.id

        # ----------------------------------------------------
        # Lehrgang auflösen
        # ----------------------------------------------------

        course_name = self._required_text(
            csv_row.get("Lehrgang"),
            "Lehrgang",
        )

        course_type_name = self._required_text(
            csv_row.get("Lehrgangstyp"),
            "Lehrgangstyp",
        )

        course_type = (
            self.course_type_service
            .get_course_type_by_name(
                course_type_name
            )
        )

        if course_type is None:
            raise ValueError(
                "Unbekannter Lehrgangstyp: "
                f"{course_type_name}."
            )

        course = (
            self.course_service
            .get_course_by_type_and_name(
                course_type.id,
                course_name,
            )
        )

        if course is None:
            raise ValueError(
                "Der Lehrgang konnte nicht "
                "aufgelöst werden: "
                f"{course_type_name} / "
                f"{course_name}"
            )

        # ----------------------------------------------------
        # Kurstag auflösen
        # ----------------------------------------------------

        course_day_id = self._clean_optional(
            csv_row.get("Kurstag ID")
        )

        course_day = None

        if course_day_id:
            course_day = (
                self.course_day_service
                .get_course_day(
                    course_day_id
                )
            )

        date_text = self._required_text(
            csv_row.get("Datum"),
            "Datum",
        )

        course_date = (
            self._parse_course_day_date(
                date_text
            )
        )

        beginn = self._clean_optional(
            csv_row.get("Beginn")
        )

        ende = self._clean_optional(
            csv_row.get("Ende")
        )

        day_name = self._clean_optional(
            csv_row.get(
                "Kurstag Bezeichnung"
            )
        )

        if course_day is None:
            course_day = (
                self.course_day_service
                .get_course_day_by_identity(
                    lehrgang_id=course.id,
                    datum=course_date,
                    beginn=beginn,
                    ende=ende,
                    bezeichnung=day_name,
                )
            )

        if course_day is None:
            raise ValueError(
                "Der Kurstag konnte nicht "
                "aufgelöst werden: "
                f"{course_name}, "
                f"{course_date.isoformat()}."
            )

        course_day_id = course_day.id

        # ----------------------------------------------------
        # Rolle und Status
        # ----------------------------------------------------

        role_text = self._required_text(
            csv_row.get("Rolle"),
            "Rolle",
        )

        status_text = self._required_text(
            csv_row.get("Status"),
            "Status",
        )

        try:
            role = CourseAssignmentRole(
                role_text
            )
        except ValueError as exc:
            raise ValueError(
                "Unbekannte Rolle: "
                f"{role_text}."
            ) from exc

        try:
            status = CourseAssignmentStatus(
                status_text
            )
        except ValueError as exc:
            raise ValueError(
                "Unbekannter Status: "
                f"{status_text}."
            ) from exc

        # ----------------------------------------------------
        # Bestehende Zuordnung finden
        # ----------------------------------------------------

        existing = (
            self.assignment_service
            .get_assignment_for_person_and_course_day(
                person_id,
                course_day_id,
            )
        )

        if existing is not None:
            action = "update"
            resolved_assignment_id = (
                existing.id
            )

        else:
            action = "create"
            resolved_assignment_id = None

        return CourseAssignmentImportRow(
            row_number=row_number,
            assignment_id=(
                resolved_assignment_id
            ),
            action=action,
            person_id=person_id,
            kurstag_id=course_day_id,
            rolle=role,
            status=status,
            bemerkungen=self._clean_optional(
                csv_row.get("Bemerkungen")
            ),
        )

    # ========================================================
    # Telefonnummern Personen
    # ========================================================

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

    # ========================================================
    # Hilfsmethoden
    # ========================================================

    @staticmethod
    def _validate_columns(
        fieldnames: list[str] | None,
        required_columns: set[str],
    ) -> None:
        if fieldnames is None:
            raise ValueError(
                "Die CSV-Datei enthält "
                "keine Kopfzeile."
            )

        missing_columns = (
            required_columns
            - set(fieldnames)
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
    def _parse_course_day_date(
        value: str,
    ) -> date:
        value = value.strip()

        try:
            return date.fromisoformat(
                value
            )
        except ValueError:
            pass

        try:
            day, month, year = value.split(".")

            return date(
                int(year),
                int(month),
                int(day),
            )
        except (
            ValueError,
            TypeError,
        ) as exc:
            raise ValueError(
                "Ungültiges Datum: "
                f"{value}. "
                "Erwartet wird JJJJ-MM-TT "
                "oder TT.MM.JJJJ."
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
