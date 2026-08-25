from datetime import datetime
import sqlite3

from dfg_kursverwaltung.core.database import DatabaseManager
from dfg_kursverwaltung.core.models import CourseType


class CourseTypeRepository:
    def __init__(
        self,
        database_manager: DatabaseManager,
    ):
        self.database_manager = database_manager

    def create(
        self,
        course_type: CourseType,
    ) -> CourseType:
        with self.database_manager.connect() as connection:
            connection.execute(
                """
                INSERT INTO lehrgangstypen (
                    id,
                    bezeichnung,
                    aktiv,
                    bemerkungen,
                    created_at,
                    updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?);
                """,
                (
                    course_type.id,
                    course_type.bezeichnung,
                    int(course_type.aktiv),
                    course_type.bemerkungen,
                    self._datetime_to_db(
                        course_type.created_at
                    ),
                    self._datetime_to_db(
                        course_type.updated_at
                    ),
                ),
            )

            connection.commit()

        return course_type

    def get_by_id(
        self,
        course_type_id: str,
    ) -> CourseType | None:
        with self.database_manager.connect() as connection:
            row = connection.execute(
                """
                SELECT *
                FROM lehrgangstypen
                WHERE id = ?;
                """,
                (course_type_id,),
            ).fetchone()

        if row is None:
            return None

        return self._row_to_course_type(
            row
        )

    def get_by_name(
        self,
        bezeichnung: str,
    ) -> CourseType | None:
        with self.database_manager.connect() as connection:
            row = connection.execute(
                """
                SELECT *
                FROM lehrgangstypen
                WHERE bezeichnung = ? COLLATE NOCASE;
                """,
                (bezeichnung,),
            ).fetchone()

        if row is None:
            return None

        return self._row_to_course_type(
            row
        )

    def list_all(
        self,
        include_inactive: bool = False,
    ) -> list[CourseType]:
        sql = """
            SELECT *
            FROM lehrgangstypen
        """

        parameters: tuple = ()

        if not include_inactive:
            sql += " WHERE aktiv = ?"
            parameters = (1,)

        sql += """
            ORDER BY
                bezeichnung COLLATE NOCASE;
        """

        with self.database_manager.connect() as connection:
            rows = connection.execute(
                sql,
                parameters,
            ).fetchall()

        return [
            self._row_to_course_type(row)
            for row in rows
        ]

    def search(
        self,
        search_text: str,
        include_inactive: bool = False,
    ) -> list[CourseType]:
        search_value = (
            f"%{search_text.strip()}%"
        )

        sql = """
            SELECT *
            FROM lehrgangstypen
            WHERE (
                bezeichnung LIKE ?
                OR bemerkungen LIKE ?
            )
        """

        parameters: list = [
            search_value,
            search_value,
        ]

        if not include_inactive:
            sql += " AND aktiv = ?"
            parameters.append(1)

        sql += """
            ORDER BY
                bezeichnung COLLATE NOCASE;
        """

        with self.database_manager.connect() as connection:
            rows = connection.execute(
                sql,
                tuple(parameters),
            ).fetchall()

        return [
            self._row_to_course_type(row)
            for row in rows
        ]

    def update(
        self,
        course_type: CourseType,
    ) -> CourseType:
        with self.database_manager.connect() as connection:
            cursor = connection.execute(
                """
                UPDATE lehrgangstypen
                SET
                    bezeichnung = ?,
                    aktiv = ?,
                    bemerkungen = ?,
                    updated_at = ?
                WHERE id = ?;
                """,
                (
                    course_type.bezeichnung,
                    int(course_type.aktiv),
                    course_type.bemerkungen,
                    self._datetime_to_db(
                        course_type.updated_at
                    ),
                    course_type.id,
                ),
            )

            if cursor.rowcount == 0:
                raise KeyError(
                    "Lehrgangstyp nicht gefunden: "
                    f"{course_type.id}"
                )

            connection.commit()

        return course_type

    def set_active_status(
        self,
        course_type_id: str,
        active: bool,
        updated_at: datetime,
    ) -> None:
        with self.database_manager.connect() as connection:
            cursor = connection.execute(
                """
                UPDATE lehrgangstypen
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
                    course_type_id,
                ),
            )

            if cursor.rowcount == 0:
                raise KeyError(
                    "Lehrgangstyp nicht gefunden: "
                    f"{course_type_id}"
                )

            connection.commit()

    @staticmethod
    def _row_to_course_type(
        row: sqlite3.Row,
    ) -> CourseType:
        return CourseType(
            id=row["id"],
            bezeichnung=row["bezeichnung"],
            aktiv=bool(
                row["aktiv"]
            ),
            bemerkungen=row["bemerkungen"],
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