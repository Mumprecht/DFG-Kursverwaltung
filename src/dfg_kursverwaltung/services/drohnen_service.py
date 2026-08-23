from datetime import datetime, timezone
from uuid import uuid4

from dfg_kursverwaltung.core.models import Drone
from dfg_kursverwaltung.repositories.drohnen_repository import (
    DroneRepository,
)


class DroneService:
    def __init__(
        self,
        repository: DroneRepository,
    ):
        self.repository = repository

    def create_drone(
        self,
        *,
        person_id: str,
        modell: str,
        hersteller: str | None = None,
        seriennummer: str | None = None,
        bemerkungen: str | None = None,
    ) -> Drone:
        modell = modell.strip()

        if not modell:
            raise ValueError(
                "Das Drohnenmodell darf nicht leer sein."
            )

        hersteller = self._clean_optional(
            hersteller
        )

        seriennummer = self._clean_optional(
            seriennummer
        )

        if seriennummer is not None:
            seriennummer = seriennummer.upper()

            if self.repository.serial_number_exists(
                seriennummer
            ):
                raise ValueError(
                    "Diese Seriennummer ist bereits "
                    "einer Drohne zugeordnet."
                )

        timestamp = datetime.now(
            timezone.utc
        )

        drone = Drone(
            id=str(uuid4()),
            person_id=person_id,
            hersteller=hersteller,
            modell=modell,
            seriennummer=seriennummer,
            bemerkungen=self._clean_optional(
                bemerkungen
            ),
            created_at=timestamp,
            updated_at=timestamp,
        )

        return self.repository.create(
            drone
        )

    def get_drone(
        self,
        drone_id: str,
    ) -> Drone | None:
        return self.repository.get_by_id(
            drone_id
        )

    def list_drones(
        self,
        person_id: str,
    ) -> list[Drone]:
        return self.repository.list_for_person(
            person_id
        )

    def update_drone(
        self,
        drone: Drone,
    ) -> Drone:
        drone.modell = drone.modell.strip()

        if not drone.modell:
            raise ValueError(
                "Das Drohnenmodell darf nicht leer sein."
            )

        drone.hersteller = self._clean_optional(
            drone.hersteller
        )

        drone.seriennummer = self._clean_optional(
            drone.seriennummer
        )

        if drone.seriennummer is not None:
            drone.seriennummer = (
                drone.seriennummer.upper()
            )

            if self.repository.serial_number_exists(
                drone.seriennummer,
                exclude_drone_id=drone.id,
            ):
                raise ValueError(
                    "Diese Seriennummer ist bereits "
                    "einer anderen Drohne zugeordnet."
                )

        drone.bemerkungen = self._clean_optional(
            drone.bemerkungen
        )

        drone.updated_at = datetime.now(
            timezone.utc
        )

        return self.repository.update(
            drone
        )

    def delete_drone(
        self,
        drone_id: str,
    ) -> None:
        self.repository.delete(
            drone_id
        )

    @staticmethod
    def _clean_optional(
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        value = value.strip()

        return value or None