from datetime import datetime
import sqlite3

from dfg_kursverwaltung.core.database import DatabaseManager
from dfg_kursverwaltung.core.models import Location


class LocationRepository:
    def __init__(
        self,
        database_manager: DatabaseManager,
    ):
        self.database_manager = database_manager

    def create(
        self,
        location: Location,
    ) -> Location:
        with self.database_manager.connect() as connection:
            connection.execute(
                """
                INSERT INTO standorte (
                    id,
                    bezeichnung,
                    strasse,
                    hausnummer,
                    plz,
                    ort,
                    kontakt_vorname,
                    kontakt_nachname,
                    telefon_e164,
                    email,
                    webseite,
                    bemerkungen,
                    aktiv,
                    created_at,
                    updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    location.id,
                    location.bezeichnung,
                    location.strasse,
                    location.hausnummer,
                    location.plz,
                    location.ort,
                    location.kontakt_vorname,
                    location.kontakt_nachname,
                    location.telefon_e164,
                    location.email,
                    location.webseite,
                    location.bemerkungen,
                    int(location.aktiv),
                    self._datetime_to_db(
                        location.created_at
                    ),
                    self._datetime_to_db(
                        location.updated_at
                    ),
                ),
            )

            connection.commit()

        return location

    def get_by_id(
        self,
        location_id: str,
    ) -> Location | None:
        with self.database_manager.connect() as connection:
            row = connection.execute(
                """
                SELECT *
                FROM standorte
                WHERE id = ?;
                """,
                (location_id,),
            ).fetchone()

        if row is None:
            return None

        return self._row_to_location(
            row
        )

    def list_all(
        self,
        include_inactive: bool = False,
    ) -> list[Location]:
        sql = """
            SELECT *
            FROM standorte
        """

        parameters: tuple = ()

        if not include_inactive:
            sql += " WHERE aktiv = ?"
            parameters = (1,)

        sql += """
            ORDER BY
                bezeichnung COLLATE NOCASE,
                ort COLLATE NOCASE;
        """

        with self.database_manager.connect() as connection:
            rows = connection.execute(
                sql,
                parameters,
            ).fetchall()

        return [
            self._row_to_location(row)
            for row in rows
        ]

    def search(
        self,
        search_text: str,
        include_inactive: bool = False,
    ) -> list[Location]:
        search_value = (
            f"%{search_text.strip()}%"
        )

        sql = """
            SELECT *
            FROM standorte
            WHERE (
                bezeichnung LIKE ?
                OR strasse LIKE ?
                OR plz LIKE ?
                OR ort LIKE ?
                OR kontakt_vorname LIKE ?
                OR kontakt_nachname LIKE ?
                OR email LIKE ?
                OR webseite LIKE ?
            )
        """

        parameters: list = [
            search_value,
            search_value,
            search_value,
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
                bezeichnung COLLATE NOCASE,
                ort COLLATE NOCASE;
        """

        with self.database_manager.connect() as connection:
            rows = connection.execute(
                sql,
                tuple(parameters),
            ).fetchall()

        return [
            self._row_to_location(row)
            for row in rows
        ]

    def update(
        self,
        location: Location,
    ) -> Location:
        with self.database_manager.connect() as connection:
            cursor = connection.execute(
                """
                UPDATE standorte
                SET
                    bezeichnung = ?,
                    strasse = ?,
                    hausnummer = ?,
                    plz = ?,
                    ort = ?,
                    kontakt_vorname = ?,
                    kontakt_nachname = ?,
                    telefon_e164 = ?,
                    email = ?,
                    webseite = ?,
                    bemerkungen = ?,
                    aktiv = ?,
                    updated_at = ?
                WHERE id = ?;
                """,
                (
                    location.bezeichnung,
                    location.strasse,
                    location.hausnummer,
                    location.plz,
                    location.ort,
                    location.kontakt_vorname,
                    location.kontakt_nachname,
                    location.telefon_e164,
                    location.email,
                    location.webseite,
                    location.bemerkungen,
                    int(location.aktiv),
                    self._datetime_to_db(
                        location.updated_at
                    ),
                    location.id,
                ),
            )

            if cursor.rowcount == 0:
                raise KeyError(
                    "Standort nicht gefunden: "
                    f"{location.id}"
                )

            connection.commit()

        return location

    def set_active_status(
        self,
        location_id: str,
        active: bool,
        updated_at: datetime,
    ) -> None:
        with self.database_manager.connect() as connection:
            cursor = connection.execute(
                """
                UPDATE standorte
                SET
                    aktiv = ?,
                    updated_at = ?
                WHERE id = ?;
                """,
                (
                    int(active),
                    self._datetime_to_db(
                        updated_at
                    ),
                    location_id,
                ),
            )

            if cursor.rowcount == 0:
                raise KeyError(
                    "Standort nicht gefunden: "
                    f"{location_id}"
                )

            connection.commit()

    @staticmethod
    def _row_to_location(
        row: sqlite3.Row,
    ) -> Location:
        return Location(
            id=row["id"],
            bezeichnung=row["bezeichnung"],
            strasse=row["strasse"],
            hausnummer=row["hausnummer"],
            plz=row["plz"],
            ort=row["ort"],
            kontakt_vorname=row[
                "kontakt_vorname"
            ],
            kontakt_nachname=row[
                "kontakt_nachname"
            ],
            telefon_e164=row[
                "telefon_e164"
            ],
            email=row["email"],
            webseite=row["webseite"],
            bemerkungen=row["bemerkungen"],
            aktiv=bool(
                row["aktiv"]
            ),
            created_at=(
                datetime.fromisoformat(
                    row["created_at"]
                )
                if row["created_at"]
                else None
            ),
            updated_at=(
                datetime.fromisoformat(
                    row["updated_at"]
                )
                if row["updated_at"]
                else None
            ),
        )

    @staticmethod
    def _datetime_to_db(
        value: datetime | None,
    ) -> str | None:
        if value is None:
            return None

        return value.isoformat()