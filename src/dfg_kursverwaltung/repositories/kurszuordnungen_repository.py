from datetime import datetime
import sqlite3

from dfg_kursverwaltung.core.database import DatabaseManager
from dfg_kursverwaltung.core.models import (
    CourseAssignment,
    CourseAssignmentRole,
    CourseAssignmentStatus,
)


class CourseAssignmentRepository:
    def __init__(
        self,
        database_manager: DatabaseManager,
    ):
        self.database_manager = database_manager

    def create(
        self,
        assignment: CourseAssignment,
    ) -> CourseAssignment:
        with self.database_manager.connect() as connection:
            connection.execute(
                """
                INSERT INTO kurszuordnungen (
                    id,
                    person_id,
                    kurstag_id,
                    rolle,
                    status,
                    bemerkungen,
                    created_at,
                    updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    assignment.id,
                    assignment.person_id,
                    assignment.kurstag_id,
                    assignment.rolle.value,
                    assignment.status.value,
                    assignment.bemerkungen,
                    self._datetime_to_db(
                        assignment.created_at
                    ),
                    self._datetime_to_db(
                        assignment.updated_at
                    ),
                ),
            )

            connection.commit()

        return assignment

    def get_by_id(
        self,
        assignment_id: str,
    ) -> CourseAssignment | None:
        with self.database_manager.connect() as connection:
            row = connection.execute(
                """
                SELECT *
                FROM kurszuordnungen
                WHERE id = ?;
                """,
                (assignment_id,),
            ).fetchone()

        if row is None:
            return None

        return self._row_to_assignment(
            row
        )

    def get_for_person_and_course_day(
        self,
        person_id: str,
        course_day_id: str,
    ) -> CourseAssignment | None:
        with self.database_manager.connect() as connection:
            row = connection.execute(
                """
                SELECT *
                FROM kurszuordnungen
                WHERE
                    person_id = ?
                    AND kurstag_id = ?;
                """,
                (
                    person_id,
                    course_day_id,
                ),
            ).fetchone()

        if row is None:
            return None

        return self._row_to_assignment(
            row
        )

    def list_for_course_day(
        self,
        course_day_id: str,
    ) -> list[CourseAssignment]:
        with self.database_manager.connect() as connection:
            rows = connection.execute(
                """
                SELECT *
                FROM kurszuordnungen
                WHERE kurstag_id = ?
                ORDER BY
                    rolle ASC,
                    created_at ASC;
                """,
                (course_day_id,),
            ).fetchall()

        return [
            self._row_to_assignment(row)
            for row in rows
        ]

    def list_for_person(
        self,
        person_id: str,
    ) -> list[CourseAssignment]:
        with self.database_manager.connect() as connection:
            rows = connection.execute(
                """
                SELECT *
                FROM kurszuordnungen
                WHERE person_id = ?
                ORDER BY
                    created_at ASC;
                """,
                (person_id,),
            ).fetchall()

        return [
            self._row_to_assignment(row)
            for row in rows
        ]

    def update(
        self,
        assignment: CourseAssignment,
    ) -> CourseAssignment:
        with self.database_manager.connect() as connection:
            cursor = connection.execute(
                """
                UPDATE kurszuordnungen
                SET
                    person_id = ?,
                    kurstag_id = ?,
                    rolle = ?,
                    status = ?,
                    bemerkungen = ?,
                    updated_at = ?
                WHERE id = ?;
                """,
                (
                    assignment.person_id,
                    assignment.kurstag_id,
                    assignment.rolle.value,
                    assignment.status.value,
                    assignment.bemerkungen,
                    self._datetime_to_db(
                        assignment.updated_at
                    ),
                    assignment.id,
                ),
            )

            if cursor.rowcount == 0:
                raise KeyError(
                    "Kurszuordnung nicht gefunden: "
                    f"{assignment.id}"
                )

            connection.commit()

        return assignment

    def delete(
        self,
        assignment_id: str,
    ) -> None:
        with self.database_manager.connect() as connection:
            cursor = connection.execute(
                """
                DELETE FROM kurszuordnungen
                WHERE id = ?;
                """,
                (assignment_id,),
            )

            if cursor.rowcount == 0:
                raise KeyError(
                    "Kurszuordnung nicht gefunden: "
                    f"{assignment_id}"
                )

            connection.commit()

    @staticmethod
    def _row_to_assignment(
        row: sqlite3.Row,
    ) -> CourseAssignment:
        return CourseAssignment(
            id=row["id"],
            person_id=row["person_id"],
            kurstag_id=row["kurstag_id"],
            rolle=CourseAssignmentRole(
                row["rolle"]
            ),
            status=CourseAssignmentStatus(
                row["status"]
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