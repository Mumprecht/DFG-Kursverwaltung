from datetime import datetime
import sqlite3

from dfg_kursverwaltung.core.database import DatabaseManager
from dfg_kursverwaltung.core.models import ExamResult


class ExamResultRepository:
    def __init__(
        self,
        database_manager: DatabaseManager,
    ):
        self.database_manager = database_manager

    def create(
        self,
        exam_result: ExamResult,
    ) -> ExamResult:
        with self.database_manager.connect() as connection:
            connection.execute(
                """
                INSERT INTO pruefungsergebnisse (
                    id,
                    kurszuordnung_id,
                    bestanden,
                    note,
                    bemerkungen,
                    created_at,
                    updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    exam_result.id,
                    exam_result.kurszuordnung_id,
                    int(exam_result.bestanden),
                    exam_result.note,
                    exam_result.bemerkungen,
                    self._datetime_to_db(
                        exam_result.created_at
                    ),
                    self._datetime_to_db(
                        exam_result.updated_at
                    ),
                ),
            )

            connection.commit()

        return exam_result

    def get_by_id(
        self,
        exam_result_id: str,
    ) -> ExamResult | None:
        with self.database_manager.connect() as connection:
            row = connection.execute(
                """
                SELECT *
                FROM pruefungsergebnisse
                WHERE id = ?;
                """,
                (exam_result_id,),
            ).fetchone()

        if row is None:
            return None

        return self._row_to_exam_result(
            row
        )

    def get_by_assignment_id(
        self,
        assignment_id: str,
    ) -> ExamResult | None:
        with self.database_manager.connect() as connection:
            row = connection.execute(
                """
                SELECT *
                FROM pruefungsergebnisse
                WHERE kurszuordnung_id = ?;
                """,
                (assignment_id,),
            ).fetchone()

        if row is None:
            return None

        return self._row_to_exam_result(
            row
        )

    def list_all(
        self,
    ) -> list[ExamResult]:
        with self.database_manager.connect() as connection:
            rows = connection.execute(
                """
                SELECT *
                FROM pruefungsergebnisse
                ORDER BY created_at;
                """
            ).fetchall()

        return [
            self._row_to_exam_result(row)
            for row in rows
        ]

    def update(
        self,
        exam_result: ExamResult,
    ) -> ExamResult:
        with self.database_manager.connect() as connection:
            cursor = connection.execute(
                """
                UPDATE pruefungsergebnisse
                SET
                    kurszuordnung_id = ?,
                    bestanden = ?,
                    note = ?,
                    bemerkungen = ?,
                    updated_at = ?
                WHERE id = ?;
                """,
                (
                    exam_result.kurszuordnung_id,
                    int(exam_result.bestanden),
                    exam_result.note,
                    exam_result.bemerkungen,
                    self._datetime_to_db(
                        exam_result.updated_at
                    ),
                    exam_result.id,
                ),
            )

            if cursor.rowcount == 0:
                raise KeyError(
                    "Prüfungsergebnis nicht gefunden: "
                    f"{exam_result.id}"
                )

            connection.commit()

        return exam_result

    def delete(
        self,
        exam_result_id: str,
    ) -> None:
        with self.database_manager.connect() as connection:
            cursor = connection.execute(
                """
                DELETE FROM pruefungsergebnisse
                WHERE id = ?;
                """,
                (exam_result_id,),
            )

            if cursor.rowcount == 0:
                raise KeyError(
                    "Prüfungsergebnis nicht gefunden: "
                    f"{exam_result_id}"
                )

            connection.commit()

    @staticmethod
    def _row_to_exam_result(
        row: sqlite3.Row,
    ) -> ExamResult:
        return ExamResult(
            id=row["id"],
            kurszuordnung_id=row[
                "kurszuordnung_id"
            ],
            bestanden=bool(
                row["bestanden"]
            ),
            note=row["note"],
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
