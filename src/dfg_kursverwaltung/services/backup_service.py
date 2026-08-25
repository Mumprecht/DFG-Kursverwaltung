from datetime import datetime
from pathlib import Path
import sqlite3

from dfg_kursverwaltung.core.database import (
    DatabaseManager,
    SCHEMA_VERSION,
)


class BackupService:
    REQUIRED_TABLES = {
        "drohnen",
        "kurstage",
        "kurszuordnungen",
        "lehrgaenge",
        "lehrgangstypen",
        "personen",
        "pruefungsergebnisse",
        "schema_info",
        "standorte",
        "telefonnummern",
    }

    def __init__(
        self,
        database_manager: DatabaseManager,
    ):
        self.database_manager = database_manager

    def create_backup(
        self,
        backup_path: str | Path,
    ) -> Path:
        target_path = Path(
            backup_path
        )

        target_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        active_path = (
            self.database_manager.database_path
        )

        if not active_path.exists():
            raise FileNotFoundError(
                "Die Datenbankdatei wurde nicht "
                "gefunden: "
                f"{active_path}"
            )

        if (
            target_path.resolve()
            == active_path.resolve()
        ):
            raise ValueError(
                "Die Sicherungsdatei darf nicht "
                "identisch mit der aktiven "
                "Datenbankdatei sein."
            )

        with self.database_manager.connect() as source:
            destination = sqlite3.connect(
                target_path
            )

            try:
                source.backup(
                    destination
                )

                destination.commit()

            finally:
                destination.close()

        self.validate_backup(
            target_path
        )

        return target_path

    def restore_backup(
        self,
        backup_path: str | Path,
        *,
        safety_backup_dir: str | Path | None = None,
    ) -> Path:
        source_path = Path(
            backup_path
        )

        # Backup vor dem Restore vollständig prüfen.
        self.validate_backup(
            source_path
        )

        active_path = (
            self.database_manager.database_path
        )

        if (
            source_path.resolve()
            == active_path.resolve()
        ):
            raise ValueError(
                "Die Wiederherstellungsdatei darf "
                "nicht identisch mit der aktiven "
                "Datenbankdatei sein."
            )

        safety_dir = self._get_safety_backup_dir(
            safety_backup_dir
        )

        safety_backup_path = (
            self._create_timestamped_path(
                safety_dir,
                "Vor-Restore",
            )
        )

        # Vor jeder Wiederherstellung wird der
        # aktuelle Zustand automatisch gesichert.
        self.create_backup(
            safety_backup_path
        )

        source = sqlite3.connect(
            source_path
        )

        try:
            with self.database_manager.connect() as destination:
                source.backup(
                    destination
                )

                destination.commit()

        finally:
            source.close()

        # Die wiederhergestellte aktive Datenbank
        # nochmals vollständig prüfen.
        self.validate_backup(
            active_path
        )

        return safety_backup_path

    def reset_database(
        self,
        *,
        safety_backup_dir: str | Path | None = None,
    ) -> Path:
        active_path = (
            self.database_manager.database_path
        )

        if not active_path.exists():
            raise FileNotFoundError(
                "Die Datenbankdatei wurde nicht "
                "gefunden: "
                f"{active_path}"
            )

        safety_dir = self._get_safety_backup_dir(
            safety_backup_dir
        )

        safety_backup_path = (
            self._create_timestamped_path(
                safety_dir,
                "Vor-Zuruecksetzen",
            )
        )

        # Zwingende Sicherheitskopie vor dem
        # Zurücksetzen.
        self.create_backup(
            safety_backup_path
        )

        # Erst nach erfolgreicher Sicherung wird
        # die aktive Datenbank entfernt.
        active_path.unlink()

        try:
            self.database_manager.initialize_database()

            self.validate_backup(
                active_path
            )

            self._validate_empty_database(
                active_path
            )

        except Exception:
            # Falls die Neuerstellung fehlschlägt,
            # versuchen wir automatisch, den vorherigen
            # Zustand aus der Sicherheitskopie
            # wiederherzustellen.
            if active_path.exists():
                active_path.unlink()

            source = sqlite3.connect(
                safety_backup_path
            )

            try:
                destination = sqlite3.connect(
                    active_path
                )

                try:
                    source.backup(
                        destination
                    )

                    destination.commit()

                finally:
                    destination.close()

            finally:
                source.close()

            raise

        return safety_backup_path

    def validate_backup(
        self,
        backup_path: str | Path,
    ) -> int:
        path = Path(
            backup_path
        )

        if not path.exists():
            raise FileNotFoundError(
                "Die Sicherungsdatei wurde "
                "nicht gefunden: "
                f"{path}"
            )

        connection = sqlite3.connect(
            path
        )

        connection.row_factory = sqlite3.Row

        try:
            integrity_row = (
                connection.execute(
                    "PRAGMA integrity_check;"
                ).fetchone()
            )

            if (
                integrity_row is None
                or integrity_row[0] != "ok"
            ):
                result = (
                    integrity_row[0]
                    if integrity_row is not None
                    else "Keine Rückmeldung"
                )

                raise ValueError(
                    "Die SQLite-Integritätsprüfung "
                    "ist fehlgeschlagen: "
                    f"{result}"
                )

            schema_table = (
                connection.execute(
                    """
                    SELECT name
                    FROM sqlite_master
                    WHERE
                        type = 'table'
                        AND name = 'schema_info';
                    """
                ).fetchone()
            )

            if schema_table is None:
                raise ValueError(
                    "Die Sicherungsdatei enthält "
                    "keine Tabelle schema_info."
                )

            version_row = (
                connection.execute(
                    """
                    SELECT version
                    FROM schema_info
                    LIMIT 1;
                    """
                ).fetchone()
            )

            if version_row is None:
                raise ValueError(
                    "In der Sicherungsdatei ist "
                    "keine Schema-Version "
                    "gespeichert."
                )

            schema_version = int(
                version_row["version"]
            )

            if schema_version != SCHEMA_VERSION:
                raise ValueError(
                    "Nicht unterstützte "
                    "Schema-Version der Sicherung: "
                    f"{schema_version}. "
                    "Erwartet wird "
                    f"{SCHEMA_VERSION}."
                )

            self._validate_required_tables(
                connection
            )

            foreign_key_errors = (
                connection.execute(
                    "PRAGMA foreign_key_check;"
                ).fetchall()
            )

            if foreign_key_errors:
                error_text = "; ".join(
                    " | ".join(
                        str(value)
                        for value in row
                    )
                    for row in foreign_key_errors
                )

                raise ValueError(
                    "Die Fremdschlüsselprüfung "
                    "der Sicherungsdatei ist "
                    "fehlgeschlagen: "
                    f"{error_text}"
                )

            return schema_version

        finally:
            connection.close()

    def _get_safety_backup_dir(
        self,
        safety_backup_dir: str | Path | None,
    ) -> Path:
        if safety_backup_dir is None:
            path = (
                self.database_manager.project_root
                / "Backup"
            )
        else:
            path = Path(
                safety_backup_dir
            )

        path.mkdir(
            parents=True,
            exist_ok=True,
        )

        return path

    @staticmethod
    def _create_timestamped_path(
        directory: Path,
        operation: str,
    ) -> Path:
        timestamp = datetime.now().strftime(
            "%Y-%m-%d_%H%M%S"
        )

        return (
            directory
            / (
                "DFG-Kursverwaltung_"
                f"{operation}_{timestamp}.db"
            )
        )

    def _validate_required_tables(
        self,
        connection: sqlite3.Connection,
    ) -> None:
        rows = connection.execute(
            """
            SELECT name
            FROM sqlite_master
            WHERE type = 'table';
            """
        ).fetchall()

        existing_tables = {
            row["name"]
            for row in rows
        }

        missing_tables = (
            self.REQUIRED_TABLES
            - existing_tables
        )

        if missing_tables:
            missing_text = ", ".join(
                sorted(
                    missing_tables
                )
            )

            raise ValueError(
                "In der Sicherungsdatei fehlen "
                "erforderliche Tabellen: "
                f"{missing_text}"
            )

    def _validate_empty_database(
        self,
        database_path: str | Path,
    ) -> None:
        path = Path(
            database_path
        )

        connection = sqlite3.connect(
            path
        )

        try:
            tables_to_check = (
                self.REQUIRED_TABLES
                - {"schema_info"}
            )

            non_empty_tables = []

            for table_name in sorted(
                tables_to_check
            ):
                count = connection.execute(
                    f"SELECT COUNT(*) "
                    f"FROM {table_name};"
                ).fetchone()[0]

                if count != 0:
                    non_empty_tables.append(
                        f"{table_name}: {count}"
                    )

            if non_empty_tables:
                raise RuntimeError(
                    "Die neu erstellte Datenbank "
                    "ist nicht leer: "
                    + ", ".join(
                        non_empty_tables
                    )
                )

        finally:
            connection.close()