from datetime import datetime
import sqlite3

from dfg_kursverwaltung.core.database import DatabaseManager
from dfg_kursverwaltung.core.models import Course


class CourseRepository:
    def __init__(
        self,
        database_manager: DatabaseManager,
    ):
        self.database_manager = database_manager

    def create(
        self,
        course: Course,
    ) -> Course:
        with self.database_manager.connect() as connection:
            connection.execute(
                """
                INSERT INTO lehrgaenge (
                    id,
                    lehrgangstyp_id,
                    bezeichnung,
                    beschreibung,
                    bemerkungen,
                    created_at,
                    updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    course.id,
                    course.lehrgangstyp_id,
                    course.bezeichnung,
                    course.beschreibung,
                    course.bemerkungen,
                    self._datetime_to_db(course.created_at),
                    self._datetime_to_db(course.updated_at),
                ),
            )
            connection.commit()
        return course

    def get_by_id(
        self,
        course_id: str,
    ) -> Course | None:
        with self.database_manager.connect() as connection:
            row = connection.execute(
                """
                SELECT *
                FROM lehrgaenge
                WHERE id = ?;
                """,
                (course_id,),
            ).fetchone()

        if row is None:
            return None

        return self._row_to_course(row)

    def list_all(
        self,
    ) -> list[Course]:
        with self.database_manager.connect() as connection:
            rows = connection.execute(
                """
                SELECT l.*
                FROM lehrgaenge AS l
                JOIN lehrgangstypen AS t
                    ON t.id = l.lehrgangstyp_id
                ORDER BY
                    t.bezeichnung COLLATE NOCASE,
                    l.bezeichnung COLLATE NOCASE;
                """
            ).fetchall()

        return [self._row_to_course(row) for row in rows]

    def search(
        self,
        search_text: str,
    ) -> list[Course]:
        search_value = f"%{search_text.strip()}%"

        with self.database_manager.connect() as connection:
            rows = connection.execute(
                """
                SELECT l.*
                FROM lehrgaenge AS l
                JOIN lehrgangstypen AS t
                    ON t.id = l.lehrgangstyp_id
                WHERE
                    l.bezeichnung LIKE ?
                    OR l.beschreibung LIKE ?
                    OR l.bemerkungen LIKE ?
                    OR t.bezeichnung LIKE ?
                ORDER BY
                    t.bezeichnung COLLATE NOCASE,
                    l.bezeichnung COLLATE NOCASE;
                """,
                (
                    search_value,
                    search_value,
                    search_value,
                    search_value,
                ),
            ).fetchall()

        return [self._row_to_course(row) for row in rows]

    def update(
        self,
        course: Course,
    ) -> Course:
        with self.database_manager.connect() as connection:
            cursor = connection.execute(
                """
                UPDATE lehrgaenge
                SET
                    lehrgangstyp_id = ?,
                    bezeichnung = ?,
                    beschreibung = ?,
                    bemerkungen = ?,
                    updated_at = ?
                WHERE id = ?;
                """,
                (
                    course.lehrgangstyp_id,
                    course.bezeichnung,
                    course.beschreibung,
                    course.bemerkungen,
                    self._datetime_to_db(course.updated_at),
                    course.id,
                ),
            )

            if cursor.rowcount == 0:
                raise KeyError(
                    "Lehrgang nicht gefunden: "
                    f"{course.id}"
                )

            connection.commit()

        return course

    @staticmethod
    def _row_to_course(
        row: sqlite3.Row,
    ) -> Course:
        return Course(
            id=row["id"],
            lehrgangstyp_id=row["lehrgangstyp_id"],
            bezeichnung=row["bezeichnung"],
            beschreibung=row["beschreibung"],
            bemerkungen=row["bemerkungen"],
            created_at=(
                datetime.fromisoformat(row["created_at"])
                if row["created_at"]
                else None
            ),
            updated_at=(
                datetime.fromisoformat(row["updated_at"])
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
