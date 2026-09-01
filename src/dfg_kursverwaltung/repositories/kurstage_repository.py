from datetime import date, datetime
import sqlite3

from dfg_kursverwaltung.core.database import DatabaseManager
from dfg_kursverwaltung.core.models import CourseDay


class CourseDayRepository:
    def __init__(
        self,
        database_manager: DatabaseManager,
    ):
        self.database_manager = database_manager

    def create(
        self,
        course_day: CourseDay,
    ) -> CourseDay:
        with self.database_manager.connect() as connection:
            connection.execute(
                """
                INSERT INTO kurstage (
                    id,
                    lehrgang_id,
                    standort_id,
                    datum,
                    beginn,
                    ende,
                    bezeichnung,
                    bemerkungen,
                    created_at,
                    updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    course_day.id,
                    course_day.lehrgang_id,
                    course_day.standort_id,
                    self._date_to_db(
                        course_day.datum
                    ),
                    course_day.beginn,
                    course_day.ende,
                    course_day.bezeichnung,
                    course_day.bemerkungen,
                    self._datetime_to_db(
                        course_day.created_at
                    ),
                    self._datetime_to_db(
                        course_day.updated_at
                    ),
                ),
            )

            connection.commit()

        return course_day

    def get_by_id(
        self,
        course_day_id: str,
    ) -> CourseDay | None:
        with self.database_manager.connect() as connection:
            row = connection.execute(
                """
                SELECT *
                FROM kurstage
                WHERE id = ?;
                """,
                (course_day_id,),
            ).fetchone()

        if row is None:
            return None

        return self._row_to_course_day(
            row
        )

    def get_by_identity(
        self,
        course_id: str,
        datum: date,
        beginn: str | None,
        ende: str | None,
        bezeichnung: str | None,
    ) -> CourseDay | None:
        with self.database_manager.connect() as connection:
            row = connection.execute(
                """
                SELECT *
                FROM kurstage
                WHERE
                    lehrgang_id = ?
                    AND datum = ?
                    AND COALESCE(beginn, '') =
                        COALESCE(?, '')
                    AND COALESCE(ende, '') =
                        COALESCE(?, '')
                    AND COALESCE(bezeichnung, '') =
                        COALESCE(?, '')
                LIMIT 1;
                """,
                (
                    course_id,
                    self._date_to_db(datum),
                    beginn,
                    ende,
                    bezeichnung,
                ),
            ).fetchone()

        if row is None:
            return None

        return self._row_to_course_day(
            row
        )

    def find_possible_duplicate(
        self,
        course_id: str,
        datum: date,
        beginn: str | None,
        ende: str | None,
    ) -> CourseDay | None:
        with self.database_manager.connect() as connection:
            row = connection.execute(
                """
                SELECT *
                FROM kurstage
                WHERE
                    lehrgang_id = ?
                    AND datum = ?
                    AND COALESCE(beginn, '') =
                        COALESCE(?, '')
                    AND COALESCE(ende, '') =
                        COALESCE(?, '')
                LIMIT 1;
                """,
                (
                    course_id,
                    self._date_to_db(datum),
                    beginn,
                    ende,
                ),
            ).fetchone()

        if row is None:
            return None

        return self._row_to_course_day(
            row
        )

    def list_all(
        self,
    ) -> list[CourseDay]:
        with self.database_manager.connect() as connection:
            rows = connection.execute(
                """
                SELECT *
                FROM kurstage
                ORDER BY
                    datum ASC,
                    beginn ASC,
                    lehrgang_id ASC;
                """
            ).fetchall()

        return [
            self._row_to_course_day(row)
            for row in rows
        ]

    def list_for_course(
        self,
        course_id: str,
    ) -> list[CourseDay]:
        with self.database_manager.connect() as connection:
            rows = connection.execute(
                """
                SELECT *
                FROM kurstage
                WHERE lehrgang_id = ?
                ORDER BY
                    datum ASC,
                    beginn ASC;
                """,
                (course_id,),
            ).fetchall()

        return [
            self._row_to_course_day(row)
            for row in rows
        ]

    def update(
        self,
        course_day: CourseDay,
    ) -> CourseDay:
        with self.database_manager.connect() as connection:
            cursor = connection.execute(
                """
                UPDATE kurstage
                SET
                    lehrgang_id = ?,
                    standort_id = ?,
                    datum = ?,
                    beginn = ?,
                    ende = ?,
                    bezeichnung = ?,
                    bemerkungen = ?,
                    updated_at = ?
                WHERE id = ?;
                """,
                (
                    course_day.lehrgang_id,
                    course_day.standort_id,
                    self._date_to_db(
                        course_day.datum
                    ),
                    course_day.beginn,
                    course_day.ende,
                    course_day.bezeichnung,
                    course_day.bemerkungen,
                    self._datetime_to_db(
                        course_day.updated_at
                    ),
                    course_day.id,
                ),
            )

            if cursor.rowcount == 0:
                raise KeyError(
                    "Kurstag nicht gefunden: "
                    f"{course_day.id}"
                )

            connection.commit()

        return course_day

    def has_assignments(
        self,
        course_day_id: str,
    ) -> bool:
        with self.database_manager.connect() as connection:
            row = connection.execute(
                """
                SELECT 1
                FROM kurszuordnungen
                WHERE kurstag_id = ?
                LIMIT 1;
                """,
                (course_day_id,),
            ).fetchone()

        return row is not None

    def delete(
        self,
        course_day_id: str,
    ) -> None:
        with self.database_manager.connect() as connection:
            cursor = connection.execute(
                """
                DELETE FROM kurstage
                WHERE id = ?;
                """,
                (course_day_id,),
            )

            if cursor.rowcount == 0:
                raise KeyError(
                    "Kurstag nicht gefunden: "
                    f"{course_day_id}"
                )

            connection.commit()

    @staticmethod
    def _row_to_course_day(
        row: sqlite3.Row,
    ) -> CourseDay:
        return CourseDay(
            id=row["id"],
            lehrgang_id=row["lehrgang_id"],
            standort_id=row["standort_id"],
            datum=date.fromisoformat(
                row["datum"]
            ),
            beginn=row["beginn"],
            ende=row["ende"],
            bezeichnung=row["bezeichnung"],
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
    def _date_to_db(
        value: date,
    ) -> str:
        return value.isoformat()

    @staticmethod
    def _datetime_to_db(
        value: datetime | None,
    ) -> str | None:
        if value is None:
            return None

        return value.isoformat()