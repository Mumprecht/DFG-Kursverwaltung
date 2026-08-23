from datetime import date, datetime, timezone
import sqlite3

from dfg_kursverwaltung.core.database import DatabaseManager
from dfg_kursverwaltung.core.models import Person


class PersonRepository:
    def __init__(
        self,
        database_manager: DatabaseManager,
    ):
        self.database_manager = database_manager

    def create(
        self,
        person: Person,
    ) -> Person:
        with self.database_manager.connect() as connection:
            connection.execute(
                """
                INSERT INTO personen (
                    id,
                    nachname,
                    vorname,
                    geburtsdatum,
                    email,
                    strasse,
                    hausnummer,
                    plz,
                    ort,
                    organisation,
                    mitglied,
                    aktiv,
                    bemerkungen,
                    created_at,
                    updated_at
                )
                VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                );
                """,
                (
                    person.id,
                    person.nachname,
                    person.vorname,
                    self._date_to_db(
                        person.geburtsdatum
                    ),
                    person.email,
                    person.strasse,
                    person.hausnummer,
                    person.plz,
                    person.ort,
                    person.organisation,
                    int(person.mitglied),
                    int(person.aktiv),
                    person.bemerkungen,
                    self._datetime_to_db(
                        person.created_at
                    ),
                    self._datetime_to_db(
                        person.updated_at
                    ),
                ),
            )

            connection.commit()

        return person

    def get_by_id(
        self,
        person_id: str,
    ) -> Person | None:
        with self.database_manager.connect() as connection:
            row = connection.execute(
                """
                SELECT *
                FROM personen
                WHERE id = ?;
                """,
                (person_id,),
            ).fetchone()

        if row is None:
            return None

        return self._row_to_person(
            row
        )

    def list_all(
        self,
        include_inactive: bool = False,
    ) -> list[Person]:
        sql = """
            SELECT *
            FROM personen
        """

        parameters: tuple = ()

        if not include_inactive:
            sql += " WHERE aktiv = ?"
            parameters = (1,)

        sql += """
            ORDER BY
                nachname COLLATE NOCASE,
                vorname COLLATE NOCASE;
        """

        with self.database_manager.connect() as connection:
            rows = connection.execute(
                sql,
                parameters,
            ).fetchall()

        return [
            self._row_to_person(row)
            for row in rows
        ]

    def search(
        self,
        search_text: str,
        include_inactive: bool = False,
    ) -> list[Person]:
        search_value = (
            f"%{search_text.strip()}%"
        )

        sql = """
            SELECT *
            FROM personen
            WHERE (
                nachname LIKE ?
                OR vorname LIKE ?
                OR email LIKE ?
                OR organisation LIKE ?
                OR ort LIKE ?
            )
        """

        parameters: list = [
            search_value,
            search_value,
            search_value,
            search_value,
            search_value,
        ]

        if not include_inactive:
            sql += " AND aktiv = ?"
            parameters.append(1)

        sql += """
            ORDER BY
                nachname COLLATE NOCASE,
                vorname COLLATE NOCASE;
        """

        with self.database_manager.connect() as connection:
            rows = connection.execute(
                sql,
                tuple(parameters),
            ).fetchall()

        return [
            self._row_to_person(row)
            for row in rows
        ]

    def update(
        self,
        person: Person,
    ) -> Person:
        person.updated_at = datetime.now(
            timezone.utc
        )

        with self.database_manager.connect() as connection:
            cursor = connection.execute(
                """
                UPDATE personen
                SET
                    nachname = ?,
                    vorname = ?,
                    geburtsdatum = ?,
                    email = ?,
                    strasse = ?,
                    hausnummer = ?,
                    plz = ?,
                    ort = ?,
                    organisation = ?,
                    mitglied = ?,
                    aktiv = ?,
                    bemerkungen = ?,
                    updated_at = ?
                WHERE id = ?;
                """,
                (
                    person.nachname,
                    person.vorname,
                    self._date_to_db(
                        person.geburtsdatum
                    ),
                    person.email,
                    person.strasse,
                    person.hausnummer,
                    person.plz,
                    person.ort,
                    person.organisation,
                    int(person.mitglied),
                    int(person.aktiv),
                    person.bemerkungen,
                    self._datetime_to_db(
                        person.updated_at
                    ),
                    person.id,
                ),
            )

            if cursor.rowcount == 0:
                raise KeyError(
                    f"Person nicht gefunden: {person.id}"
                )

            connection.commit()

        return person

    def set_active_status(
        self,
        person_id: str,
        active: bool,
    ) -> None:
        timestamp = datetime.now(
            timezone.utc
        )

        with self.database_manager.connect() as connection:
            cursor = connection.execute(
                """
                UPDATE personen
                SET
                    aktiv = ?,
                    updated_at = ?
                WHERE id = ?;
                """,
                (
                    int(active),
                    self._datetime_to_db(
                        timestamp
                    ),
                    person_id,
                ),
            )

            if cursor.rowcount == 0:
                raise KeyError(
                    f"Person nicht gefunden: {person_id}"
                )

            connection.commit()

    def deactivate(
        self,
        person_id: str,
    ) -> None:
        self.set_active_status(
            person_id,
            False,
        )

    def activate(
        self,
        person_id: str,
    ) -> None:
        self.set_active_status(
            person_id,
            True,
        )

    @staticmethod
    def _row_to_person(
        row: sqlite3.Row,
    ) -> Person:
        return Person(
            id=row["id"],
            nachname=row["nachname"],
            vorname=row["vorname"],
            geburtsdatum=(
                date.fromisoformat(
                    row["geburtsdatum"]
                )
                if row["geburtsdatum"]
                else None
            ),
            email=row["email"],
            strasse=row["strasse"],
            hausnummer=row["hausnummer"],
            plz=row["plz"],
            ort=row["ort"],
            organisation=row["organisation"],
            mitglied=bool(
                row["mitglied"]
            ),
            aktiv=bool(
                row["aktiv"]
            ),
            bemerkungen=row["bemerkungen"],
            created_at=(
                PersonRepository._datetime_from_db(
                    row["created_at"]
                )
            ),
            updated_at=(
                PersonRepository._datetime_from_db(
                    row["updated_at"]
                )
            ),
        )

    @staticmethod
    def _date_to_db(
        value: date | None,
    ) -> str | None:
        if value is None:
            return None

        return value.isoformat()

    @staticmethod
    def _datetime_to_db(
        value: datetime | None,
    ) -> str | None:
        if value is None:
            return None

        return value.isoformat()

    @staticmethod
    def _datetime_from_db(
        value: str | None,
    ) -> datetime | None:
        if value is None:
            return None

        return datetime.fromisoformat(
            value
        )