from datetime import datetime
import sqlite3

from dfg_kursverwaltung.core.database import DatabaseManager
from dfg_kursverwaltung.core.models import Drone


class DroneRepository:
    def __init__(
        self,
        database_manager: DatabaseManager,
    ):
        self.database_manager = database_manager

    def create(
        self,
        drone: Drone,
    ) -> Drone:
        with self.database_manager.connect() as connection:
            connection.execute(
                """
                INSERT INTO drohnen (
                    id,
                    person_id,
                    hersteller,
                    modell,
                    seriennummer,
                    bemerkungen,
                    created_at,
                    updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    drone.id,
                    drone.person_id,
                    drone.hersteller,
                    drone.modell,
                    drone.seriennummer,
                    drone.bemerkungen,
                    self._datetime_to_db(
                        drone.created_at
                    ),
                    self._datetime_to_db(
                        drone.updated_at
                    ),
                ),
            )

            connection.commit()

        return drone

    def get_by_id(
        self,
        drone_id: str,
    ) -> Drone | None:
        with self.database_manager.connect() as connection:
            row = connection.execute(
                """
                SELECT *
                FROM drohnen
                WHERE id = ?;
                """,
                (drone_id,),
            ).fetchone()

        if row is None:
            return None

        return self._row_to_drone(row)

    def list_for_person(
        self,
        person_id: str,
    ) -> list[Drone]:
        with self.database_manager.connect() as connection:
            rows = connection.execute(
                """
                SELECT *
                FROM drohnen
                WHERE person_id = ?
                ORDER BY
                    hersteller COLLATE NOCASE,
                    modell COLLATE NOCASE;
                """,
                (person_id,),
            ).fetchall()

        return [
            self._row_to_drone(row)
            for row in rows
        ]

    def update(
        self,
        drone: Drone,
    ) -> Drone:
        with self.database_manager.connect() as connection:
            cursor = connection.execute(
                """
                UPDATE drohnen
                SET
                    hersteller = ?,
                    modell = ?,
                    seriennummer = ?,
                    bemerkungen = ?,
                    updated_at = ?
                WHERE id = ?;
                """,
                (
                    drone.hersteller,
                    drone.modell,
                    drone.seriennummer,
                    drone.bemerkungen,
                    self._datetime_to_db(
                        drone.updated_at
                    ),
                    drone.id,
                ),
            )

            if cursor.rowcount == 0:
                raise KeyError(
                    f"Drohne nicht gefunden: {drone.id}"
                )

            connection.commit()

        return drone

    def delete(
        self,
        drone_id: str,
    ) -> None:
        with self.database_manager.connect() as connection:
            cursor = connection.execute(
                """
                DELETE FROM drohnen
                WHERE id = ?;
                """,
                (drone_id,),
            )

            if cursor.rowcount == 0:
                raise KeyError(
                    f"Drohne nicht gefunden: {drone_id}"
                )

            connection.commit()

    def serial_number_exists(
        self,
        seriennummer: str,
        exclude_drone_id: str | None = None,
    ) -> bool:
        sql = """
            SELECT 1
            FROM drohnen
            WHERE seriennummer = ?
        """

        parameters: list[str] = [
            seriennummer
        ]

        if exclude_drone_id is not None:
            sql += " AND id <> ?"
            parameters.append(exclude_drone_id)

        sql += " LIMIT 1;"

        with self.database_manager.connect() as connection:
            row = connection.execute(
                sql,
                tuple(parameters),
            ).fetchone()

        return row is not None

    @staticmethod
    def _row_to_drone(
        row: sqlite3.Row,
    ) -> Drone:
        return Drone(
            id=row["id"],
            person_id=row["person_id"],
            hersteller=row["hersteller"],
            modell=row["modell"],
            seriennummer=row["seriennummer"],
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