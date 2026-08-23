from datetime import datetime
import sqlite3

from dfg_kursverwaltung.core.database import DatabaseManager
from dfg_kursverwaltung.core.models import (
    PhoneNumber,
    PhoneNumberType,
)


class PhoneNumberRepository:
    def __init__(
        self,
        database_manager: DatabaseManager,
    ):
        self.database_manager = database_manager

    def create(
        self,
        phone_number: PhoneNumber,
    ) -> PhoneNumber:
        with self.database_manager.connect() as connection:
            connection.execute(
                """
                INSERT INTO telefonnummern (
                    id,
                    person_id,
                    typ,
                    nummer_e164,
                    ist_primaer,
                    bemerkungen,
                    created_at,
                    updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    phone_number.id,
                    phone_number.person_id,
                    phone_number.typ.value,
                    phone_number.nummer_e164,
                    int(phone_number.ist_primaer),
                    phone_number.bemerkungen,
                    self._datetime_to_db(
                        phone_number.created_at
                    ),
                    self._datetime_to_db(
                        phone_number.updated_at
                    ),
                ),
            )

            connection.commit()

        return phone_number

    def get_by_id(
        self,
        phone_number_id: str,
    ) -> PhoneNumber | None:
        with self.database_manager.connect() as connection:
            row = connection.execute(
                """
                SELECT *
                FROM telefonnummern
                WHERE id = ?;
                """,
                (phone_number_id,),
            ).fetchone()

        if row is None:
            return None

        return self._row_to_phone_number(
            row
        )

    def list_for_person(
        self,
        person_id: str,
    ) -> list[PhoneNumber]:
        with self.database_manager.connect() as connection:
            rows = connection.execute(
                """
                SELECT *
                FROM telefonnummern
                WHERE person_id = ?
                ORDER BY
                    ist_primaer DESC,
                    typ ASC,
                    nummer_e164 ASC;
                """,
                (person_id,),
            ).fetchall()

        return [
            self._row_to_phone_number(row)
            for row in rows
        ]

    def update(
        self,
        phone_number: PhoneNumber,
    ) -> PhoneNumber:
        with self.database_manager.connect() as connection:
            cursor = connection.execute(
                """
                UPDATE telefonnummern
                SET
                    typ = ?,
                    nummer_e164 = ?,
                    ist_primaer = ?,
                    bemerkungen = ?,
                    updated_at = ?
                WHERE id = ?;
                """,
                (
                    phone_number.typ.value,
                    phone_number.nummer_e164,
                    int(
                        phone_number.ist_primaer
                    ),
                    phone_number.bemerkungen,
                    self._datetime_to_db(
                        phone_number.updated_at
                    ),
                    phone_number.id,
                ),
            )

            if cursor.rowcount == 0:
                raise KeyError(
                    "Telefonnummer nicht gefunden: "
                    f"{phone_number.id}"
                )

            connection.commit()

        return phone_number

    def clear_primary(
        self,
        person_id: str,
        except_id: str | None = None,
    ) -> None:
        with self.database_manager.connect() as connection:
            if except_id is None:
                connection.execute(
                    """
                    UPDATE telefonnummern
                    SET ist_primaer = 0
                    WHERE person_id = ?;
                    """,
                    (person_id,),
                )

            else:
                connection.execute(
                    """
                    UPDATE telefonnummern
                    SET ist_primaer = 0
                    WHERE person_id = ?
                      AND id <> ?;
                    """,
                    (
                        person_id,
                        except_id,
                    ),
                )

            connection.commit()

    def delete(
        self,
        phone_number_id: str,
    ) -> None:
        with self.database_manager.connect() as connection:
            cursor = connection.execute(
                """
                DELETE FROM telefonnummern
                WHERE id = ?;
                """,
                (phone_number_id,),
            )

            if cursor.rowcount == 0:
                raise KeyError(
                    "Telefonnummer nicht gefunden: "
                    f"{phone_number_id}"
                )

            connection.commit()

    @staticmethod
    def _row_to_phone_number(
        row: sqlite3.Row,
    ) -> PhoneNumber:
        return PhoneNumber(
            id=row["id"],
            person_id=row["person_id"],
            typ=PhoneNumberType(
                row["typ"]
            ),
            nummer_e164=row["nummer_e164"],
            ist_primaer=bool(
                row["ist_primaer"]
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