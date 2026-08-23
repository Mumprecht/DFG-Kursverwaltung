from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
import sqlite3


SCHEMA_VERSION = 3


class DatabaseManager:
    def __init__(
        self,
        database_path: str | Path | None = None,
    ):
        self.project_root = (
            Path(__file__).resolve().parents[3]
        )

        self.data_dir = self.project_root / "data"

        if database_path is None:
            self.database_path = (
                self.data_dir / "DFG-Kursverwaltung.db"
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

        connection.row_factory = sqlite3.Row

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

    def initialize_database(self) -> None:
        if not self.schema_path.exists():
            raise FileNotFoundError(
                f"Schema-Datei nicht gefunden: "
                f"{self.schema_path}"
            )

        schema_sql = self.schema_path.read_text(
            encoding="utf-8"
        )

        with self.connect() as connection:
            connection.executescript(
                schema_sql
            )

            current_version = (
                self._get_schema_version(
                    connection
                )
            )

            if current_version is None:
                connection.execute(
                    """
                    INSERT INTO schema_info (version)
                    VALUES (?);
                    """,
                    (SCHEMA_VERSION,),
                )

            elif current_version != SCHEMA_VERSION:
                raise RuntimeError(
                    "Nicht unterstützte "
                    "Datenbankschema-Version: "
                    f"{current_version}. "
                    f"Erwartet: {SCHEMA_VERSION}."
                )

            connection.commit()

    @staticmethod
    def _get_schema_version(
        connection: sqlite3.Connection,
    ) -> int | None:
        cursor = connection.execute(
            """
            SELECT version
            FROM schema_info
            LIMIT 1;
            """
        )

        row = cursor.fetchone()

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