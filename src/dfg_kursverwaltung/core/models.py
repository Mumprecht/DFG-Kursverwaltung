from dataclasses import dataclass
from datetime import date, datetime
from enum import StrEnum


class PhoneNumberType(StrEnum):
    MOBILE = "mobile"
    PRIVATE = "private"
    BUSINESS = "business"
    OTHER = "other"


class CourseType(StrEnum):
    INTRODUCTORY_DAY = "introductory_day"
    COURSE = "course"
    EXAM = "exam"


class CourseAssignmentRole(StrEnum):
    PARTICIPANT = "participant"
    INSTRUCTOR = "instructor"


class CourseAssignmentStatus(StrEnum):
    REGISTERED = "registered"
    ATTENDED = "attended"
    ABSENT = "absent"
    CANCELLED = "cancelled"


@dataclass(slots=True)
class Person:
    id: str

    nachname: str
    vorname: str

    geburtsdatum: date | None = None
    email: str | None = None

    strasse: str | None = None
    hausnummer: str | None = None
    plz: str | None = None
    ort: str | None = None

    organisation: str | None = None

    mitglied: bool = False
    ist_teilnehmer: bool = False
    ist_instruktor: bool = False
    aktiv: bool = True

    bemerkungen: str | None = None

    created_at: datetime | None = None
    updated_at: datetime | None = None

    @property
    def voller_name(self) -> str:
        return (
            f"{self.vorname} {self.nachname}"
        ).strip()


@dataclass(slots=True)
class PhoneNumber:
    id: str
    person_id: str

    typ: PhoneNumberType
    nummer_e164: str

    ist_primaer: bool = False
    bemerkungen: str | None = None

    created_at: datetime | None = None
    updated_at: datetime | None = None


@dataclass(slots=True)
class Drone:
    id: str
    person_id: str

    hersteller: str | None
    modell: str

    seriennummer: str | None = None
    bemerkungen: str | None = None

    created_at: datetime | None = None
    updated_at: datetime | None = None

    @property
    def bezeichnung(self) -> str:
        if self.hersteller:
            return (
                f"{self.hersteller} "
                f"{self.modell}"
            ).strip()

        return self.modell


@dataclass(slots=True)
class Course:
    id: str

    typ: CourseType
    bezeichnung: str

    beschreibung: str | None = None
    bemerkungen: str | None = None

    created_at: datetime | None = None
    updated_at: datetime | None = None


@dataclass(slots=True)
class CourseDay:
    id: str

    lehrgang_id: str
    datum: date

    standort_id: str | None = None

    beginn: str | None = None
    ende: str | None = None

    bezeichnung: str | None = None
    bemerkungen: str | None = None

    created_at: datetime | None = None
    updated_at: datetime | None = None


@dataclass(slots=True)
class Location:
    id: str

    bezeichnung: str

    strasse: str | None = None
    hausnummer: str | None = None
    plz: str | None = None
    ort: str | None = None

    kontakt_vorname: str | None = None
    kontakt_nachname: str | None = None

    telefon_e164: str | None = None
    email: str | None = None
    webseite: str | None = None

    bemerkungen: str | None = None

    aktiv: bool = True

    created_at: datetime | None = None
    updated_at: datetime | None = None

    @property
    def kontakt_voller_name(self) -> str:
        return " ".join(
            value
            for value in (
                self.kontakt_vorname,
                self.kontakt_nachname,
            )
            if value
        )

    @property
    def adresse(self) -> str:
        line_1 = " ".join(
            value
            for value in (
                self.strasse,
                self.hausnummer,
            )
            if value
        )

        line_2 = " ".join(
            value
            for value in (
                self.plz,
                self.ort,
            )
            if value
        )

        return ", ".join(
            value
            for value in (
                line_1,
                line_2,
            )
            if value
        )


@dataclass(slots=True)
class CourseAssignment:
    id: str

    person_id: str
    kurstag_id: str

    rolle: CourseAssignmentRole
    status: CourseAssignmentStatus

    bemerkungen: str | None = None

    created_at: datetime | None = None
    updated_at: datetime | None = None