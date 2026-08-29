from datetime import datetime, timezone
import sqlite3

from dfg_kursverwaltung.core.database import DatabaseManager
from dfg_kursverwaltung.core.models import User, UserRole


class UserRepository:
    def __init__(
        self,
        database_manager: DatabaseManager,
    ):
        self.database_manager = database_manager

    def create(
        self,
        user: User,
    ) -> User:
        with self.database_manager.connect() as connection:
            connection.execute(
                """
                INSERT INTO benutzer (
                    id,
                    username,
                    nachname,
                    vorname,
                    email,
                    password_hash,
                    rolle,
                    ist_systemadmin,
                    passwort_aendern,
                    created_at,
                    updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    user.id,
                    user.username,
                    user.nachname,
                    user.vorname,
                    user.email,
                    user.password_hash,
                    user.rolle.value,
                    int(user.ist_systemadmin),
                    int(user.passwort_aendern),
                    self._datetime_to_db(
                        user.created_at
                    ),
                    self._datetime_to_db(
                        user.updated_at
                    ),
                ),
            )

            connection.commit()

        return user

    def get_by_id(
        self,
        user_id: str,
    ) -> User | None:
        with self.database_manager.connect() as connection:
            row = connection.execute(
                """
                SELECT *
                FROM benutzer
                WHERE id = ?;
                """,
                (user_id,),
            ).fetchone()

        if row is None:
            return None

        return self._row_to_user(row)

    def get_by_username(
        self,
        username: str,
    ) -> User | None:
        username = username.strip()

        if not username:
            return None

        with self.database_manager.connect() as connection:
            row = connection.execute(
                """
                SELECT *
                FROM benutzer
                WHERE username = ? COLLATE NOCASE
                LIMIT 1;
                """,
                (username,),
            ).fetchone()

        if row is None:
            return None

        return self._row_to_user(row)

    def get_by_email(
        self,
        email: str,
    ) -> User | None:
        email = email.strip()

        if not email:
            return None

        with self.database_manager.connect() as connection:
            row = connection.execute(
                """
                SELECT *
                FROM benutzer
                WHERE email = ? COLLATE NOCASE
                LIMIT 1;
                """,
                (email,),
            ).fetchone()

        if row is None:
            return None

        return self._row_to_user(row)

    def get_systemadmin(
        self,
    ) -> User | None:
        with self.database_manager.connect() as connection:
            row = connection.execute(
                """
                SELECT *
                FROM benutzer
                WHERE ist_systemadmin = 1
                LIMIT 1;
                """
            ).fetchone()

        if row is None:
            return None

        return self._row_to_user(row)

    def list_all(
        self,
        include_inactive: bool = True,
    ) -> list[User]:
        sql = """
            SELECT *
            FROM benutzer
        """

        parameters: tuple = ()

        if not include_inactive:
            sql += " WHERE rolle <> ?"
            parameters = (
                UserRole.INACTIVE.value,
            )

        sql += """
            ORDER BY
                nachname COLLATE NOCASE,
                vorname COLLATE NOCASE,
                username COLLATE NOCASE;
        """

        with self.database_manager.connect() as connection:
            rows = connection.execute(
                sql,
                parameters,
            ).fetchall()

        return [
            self._row_to_user(row)
            for row in rows
        ]

    def count(
        self,
    ) -> int:
        with self.database_manager.connect() as connection:
            row = connection.execute(
                """
                SELECT COUNT(*) AS anzahl
                FROM benutzer;
                """
            ).fetchone()

        return int(row["anzahl"])

    def update(
        self,
        user: User,
    ) -> User:
        user.updated_at = datetime.now(
            timezone.utc
        )

        with self.database_manager.connect() as connection:
            cursor = connection.execute(
                """
                UPDATE benutzer
                SET
                    username = ?,
                    nachname = ?,
                    vorname = ?,
                    email = ?,
                    password_hash = ?,
                    rolle = ?,
                    ist_systemadmin = ?,
                    passwort_aendern = ?,
                    updated_at = ?
                WHERE id = ?;
                """,
                (
                    user.username,
                    user.nachname,
                    user.vorname,
                    user.email,
                    user.password_hash,
                    user.rolle.value,
                    int(user.ist_systemadmin),
                    int(user.passwort_aendern),
                    self._datetime_to_db(
                        user.updated_at
                    ),
                    user.id,
                ),
            )

            if cursor.rowcount == 0:
                raise KeyError(
                    "Benutzer nicht gefunden: "
                    f"{user.id}"
                )

            connection.commit()

        return user

    def delete(
        self,
        user_id: str,
    ) -> None:
        with self.database_manager.connect() as connection:
            cursor = connection.execute(
                """
                DELETE FROM benutzer
                WHERE id = ?;
                """,
                (user_id,),
            )

            if cursor.rowcount == 0:
                raise KeyError(
                    "Benutzer nicht gefunden: "
                    f"{user_id}"
                )

            connection.commit()

    @staticmethod
    def _row_to_user(
        row: sqlite3.Row,
    ) -> User:
        return User(
            id=row["id"],
            username=row["username"],
            nachname=row["nachname"],
            vorname=row["vorname"],
            email=row["email"],
            password_hash=row["password_hash"],
            rolle=UserRole(
                row["rolle"]
            ),
            ist_systemadmin=bool(
                row["ist_systemadmin"]
            ),
            passwort_aendern=bool(
                row["passwort_aendern"]
            ),
            created_at=(
                UserRepository._datetime_from_db(
                    row["created_at"]
                )
            ),
            updated_at=(
                UserRepository._datetime_from_db(
                    row["updated_at"]
                )
            ),
        )

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
