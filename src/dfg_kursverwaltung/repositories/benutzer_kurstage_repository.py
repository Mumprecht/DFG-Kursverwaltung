from datetime import datetime, timezone

from dfg_kursverwaltung.core.database import DatabaseManager


class UserCourseDayRepository:
    def __init__(
        self,
        database_manager: DatabaseManager,
    ):
        self.database_manager = database_manager

    def grant(
        self,
        user_id: str,
        course_day_id: str,
    ) -> None:
        created_at = datetime.now(
            timezone.utc
        ).isoformat()

        with self.database_manager.connect() as connection:
            connection.execute(
                """
                INSERT INTO benutzer_kurstage (
                    benutzer_id,
                    kurstag_id,
                    created_at
                )
                VALUES (?, ?, ?);
                """,
                (
                    user_id,
                    course_day_id,
                    created_at,
                ),
            )

            connection.commit()

    def revoke(
        self,
        user_id: str,
        course_day_id: str,
    ) -> None:
        with self.database_manager.connect() as connection:
            cursor = connection.execute(
                """
                DELETE FROM benutzer_kurstage
                WHERE
                    benutzer_id = ?
                    AND kurstag_id = ?;
                """,
                (
                    user_id,
                    course_day_id,
                ),
            )

            if cursor.rowcount == 0:
                raise KeyError(
                    "Kurstag-Berechtigung "
                    "nicht gefunden."
                )

            connection.commit()

    def revoke_all_for_user(
        self,
        user_id: str,
    ) -> int:
        with self.database_manager.connect() as connection:
            cursor = connection.execute(
                """
                DELETE FROM benutzer_kurstage
                WHERE benutzer_id = ?;
                """,
                (user_id,),
            )

            connection.commit()

        return cursor.rowcount

    def has_access(
        self,
        user_id: str,
        course_day_id: str,
    ) -> bool:
        with self.database_manager.connect() as connection:
            row = connection.execute(
                """
                SELECT 1
                FROM benutzer_kurstage
                WHERE
                    benutzer_id = ?
                    AND kurstag_id = ?
                LIMIT 1;
                """,
                (
                    user_id,
                    course_day_id,
                ),
            ).fetchone()

        return row is not None

    def list_course_day_ids(
        self,
        user_id: str,
    ) -> list[str]:
        with self.database_manager.connect() as connection:
            rows = connection.execute(
                """
                SELECT kurstag_id
                FROM benutzer_kurstage
                WHERE benutzer_id = ?
                ORDER BY kurstag_id;
                """,
                (user_id,),
            ).fetchall()

        return [
            row["kurstag_id"]
            for row in rows
        ]

    def list_user_ids(
        self,
        course_day_id: str,
    ) -> list[str]:
        with self.database_manager.connect() as connection:
            rows = connection.execute(
                """
                SELECT benutzer_id
                FROM benutzer_kurstage
                WHERE kurstag_id = ?
                ORDER BY benutzer_id;
                """,
                (course_day_id,),
            ).fetchall()

        return [
            row["benutzer_id"]
            for row in rows
        ]
