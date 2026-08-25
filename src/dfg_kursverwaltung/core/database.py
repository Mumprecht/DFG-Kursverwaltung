from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
import sqlite3


SCHEMA_VERSION = 4


class DatabaseManager:
    def __init__(
        self,
        database_path: str | Path | None = None,
    ):
        self.project_root = (
            Path(__file__).resolve().parents[3]
        )

        self.data_dir = (
            self.project_root
            / "data"
        )

        if database_path is None:
            self.database_path = (
                self.data_dir
                / "DFG-Kursverwaltung.db"
            )
        else:
            self.database_path = Path(
                database_path
            )

        self.schema_path = (
            Path(__file__).resolve().parent.parent
            / "database"
            / "schema.sql"
        )

    @contextmanager
    def connect(
        self,
    ) -> Iterator[sqlite3.Connection]:
        self.database_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        connection = sqlite3.connect(
            self.database_path
        )

        connection.row_factory = (
            sqlite3.Row
        )

        connection.execute(
            "PRAGMA foreign_keys = ON;"
        )

        try:
            yield connection

        except Exception:
            connection.rollback()
            raise

        finally:
            connection.close()

    def initialize_database(
        self,
    ) -> None:
        if not self.schema_path.exists():
            raise FileNotFoundError(
                "Schema-Datei nicht gefunden: "
                f"{self.schema_path}"
            )

        schema_sql = (
            self.schema_path.read_text(
                encoding="utf-8"
            )
        )

        database_exists = (
            self.database_path.exists()
        )

        with self.connect() as connection:
            # -------------------------------------------------
            # Neue Datenbank
            # -------------------------------------------------

            if not database_exists:
                connection.executescript(
                    schema_sql
                )

                connection.execute(
                    """
                    INSERT INTO schema_info (
                        version
                    )
                    VALUES (?);
                    """,
                    (
                        SCHEMA_VERSION,
                    ),
                )

                connection.commit()

                return

            # -------------------------------------------------
            # Bestehende Datenbank
            # -------------------------------------------------

            current_version = (
                self._get_schema_version(
                    connection
                )
            )

            if current_version is None:
                raise RuntimeError(
                    "Die bestehende Datenbank "
                    "enthält keine gültige "
                    "Schema-Version."
                )

            if (
                current_version
                > SCHEMA_VERSION
            ):
                raise RuntimeError(
                    "Die Datenbank verwendet "
                    "eine neuere Schema-Version "
                    "als diese Programmversion: "
                    f"{current_version}. "
                    "Unterstützt wird "
                    f"{SCHEMA_VERSION}."
                )

            # -------------------------------------------------
            # Migrationen zuerst ausführen
            # -------------------------------------------------

            current_version = (
                self._migrate_database(
                    connection,
                    current_version,
                )
            )

            if (
                current_version
                != SCHEMA_VERSION
            ):
                raise RuntimeError(
                    "Nicht unterstützte "
                    "Datenbankschema-Version: "
                    f"{current_version}. "
                    "Erwartet: "
                    f"{SCHEMA_VERSION}."
                )

            # -------------------------------------------------
            # Danach aktuelles Schema anwenden
            #
            # CREATE TABLE/INDEX IF NOT EXISTS sorgt dafür,
            # dass auch neue Indizes etc. ergänzt werden.
            # -------------------------------------------------

            connection.executescript(
                schema_sql
            )

            connection.commit()

    def _migrate_database(
        self,
        connection: sqlite3.Connection,
        current_version: int,
    ) -> int:
        if current_version == 3:
            self._migrate_3_to_4(
                connection
            )

            current_version = 4

        return current_version

    @staticmethod
    def _migrate_3_to_4(
        connection: sqlite3.Connection,
    ) -> None:
        columns = {
            row["name"]
            for row in connection.execute(
                """
                PRAGMA table_info(personen);
                """
            ).fetchall()
        }

        if (
            "ist_teilnehmer"
            not in columns
        ):
            connection.execute(
                """
                ALTER TABLE personen
                ADD COLUMN ist_teilnehmer
                    INTEGER NOT NULL
                    DEFAULT 0
                    CHECK (
                        ist_teilnehmer
                        IN (0, 1)
                    );
                """
            )

        if (
            "ist_instruktor"
            not in columns
        ):
            connection.execute(
                """
                ALTER TABLE personen
                ADD COLUMN ist_instruktor
                    INTEGER NOT NULL
                    DEFAULT 0
                    CHECK (
                        ist_instruktor
                        IN (0, 1)
                    );
                """
            )

        connection.execute(
            """
            UPDATE schema_info
            SET version = 4;
            """
        )

    @staticmethod
    def _get_schema_version(
        connection: sqlite3.Connection,
    ) -> int | None:
        table_exists = (
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

        if table_exists is None:
            return None

        row = (
            connection.execute(
                """
                SELECT version
                FROM schema_info
                LIMIT 1;
                """
            ).fetchone()
        )

        if row is None:
            return None

        return int(
            row["version"]
        )

    def get_schema_version(
        self,
    ) -> int | None:
        if not self.database_path.exists():
            return None

        with self.connect() as connection:
            return self._get_schema_version(
                connection
            )