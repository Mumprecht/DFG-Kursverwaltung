from collections.abc import Iterator
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
import sqlite3


class _TransactionConnectionProxy:
    def __init__(
        self,
        connection: sqlite3.Connection,
    ):
        self._connection = connection

    def __getattr__(
        self,
        name: str,
    ):
        return getattr(
            self._connection,
            name,
        )

    def commit(
        self,
    ) -> None:
        # Innerhalb einer übergeordneten Transaktion
        # darf ein Repository nicht selbst committen.
        pass

    def rollback(
        self,
    ) -> None:
        # Das Rollback wird vom äußeren
        # Transaktionskontext gesteuert.
        pass


SCHEMA_VERSION = 8


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

        self._transaction_connection = None
        self._transaction_depth = 0

    @contextmanager
    def connect(
        self,
    ) -> Iterator[sqlite3.Connection]:
        if self._transaction_connection is not None:
            yield _TransactionConnectionProxy(
                self._transaction_connection
            )
            return

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

    @contextmanager
    def transaction(
        self,
    ) -> Iterator[sqlite3.Connection]:
        if self._transaction_connection is not None:
            self._transaction_depth += 1

            try:
                yield self._transaction_connection

            finally:
                self._transaction_depth -= 1

            return

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

        connection.execute(
            "BEGIN IMMEDIATE;"
        )

        self._transaction_connection = connection
        self._transaction_depth = 1

        try:
            yield connection

        except Exception:
            connection.rollback()
            raise

        else:
            connection.commit()

        finally:
            self._transaction_connection = None
            self._transaction_depth = 0
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

        if not database_exists:
            with self.connect() as connection:
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

        with self.connect() as connection:
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

        if current_version > SCHEMA_VERSION:
            raise RuntimeError(
                "Die Datenbank verwendet "
                "eine neuere Schema-Version "
                "als diese Programmversion: "
                f"{current_version}. "
                "Unterstützt wird "
                f"{SCHEMA_VERSION}."
            )

        if current_version == 3:
            with self.connect() as connection:
                self._migrate_3_to_4(
                    connection
                )
                connection.commit()

            current_version = 4

        if current_version == 4:
            self._migrate_4_to_5()
            current_version = 5

        if current_version == 5:
            self._migrate_5_to_6()
            current_version = 6

        if current_version == 6:
            self._migrate_6_to_7()
            current_version = 7

        if current_version == 7:
            self._migrate_7_to_8()
            current_version = 8

        if current_version != SCHEMA_VERSION:
            raise RuntimeError(
                "Nicht unterstützte "
                "Datenbankschema-Version: "
                f"{current_version}. "
                "Erwartet: "
                f"{SCHEMA_VERSION}."
            )

        with self.connect() as connection:
            connection.executescript(
                schema_sql
            )

            connection.commit()

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

        if "ist_teilnehmer" not in columns:
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

        if "ist_instruktor" not in columns:
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

    def _migrate_4_to_5(
        self,
    ) -> None:
        connection = sqlite3.connect(
            self.database_path
        )

        connection.row_factory = (
            sqlite3.Row
        )

        try:
            connection.execute(
                "PRAGMA foreign_keys = OFF;"
            )

            connection.execute(
                "BEGIN IMMEDIATE;"
            )

            timestamp = datetime.now(
                timezone.utc
            ).isoformat()

            connection.execute(
                """
                CREATE TABLE lehrgangstypen (
                    id TEXT PRIMARY KEY,

                    bezeichnung TEXT NOT NULL
                        COLLATE NOCASE UNIQUE,

                    aktiv INTEGER NOT NULL DEFAULT 1,

                    bemerkungen TEXT,

                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,

                    CHECK (
                        aktiv IN (0, 1)
                    )
                );
                """
            )

            default_types = [
                (
                    "course-type-introductory-day",
                    "Einführungstag",
                ),
                (
                    "course-type-course",
                    "Kurs",
                ),
                (
                    "course-type-exam",
                    "Prüfung",
                ),
            ]

            for type_id, name in default_types:
                connection.execute(
                    """
                    INSERT INTO lehrgangstypen (
                        id,
                        bezeichnung,
                        aktiv,
                        bemerkungen,
                        created_at,
                        updated_at
                    )
                    VALUES (
                        ?, ?, 1, NULL, ?, ?
                    );
                    """,
                    (
                        type_id,
                        name,
                        timestamp,
                        timestamp,
                    ),
                )

            old_count = connection.execute(
                """
                SELECT COUNT(*)
                FROM lehrgaenge;
                """
            ).fetchone()[0]

            unresolved = connection.execute(
                """
                SELECT COUNT(*)
                FROM lehrgaenge
                WHERE typ NOT IN (
                    'introductory_day',
                    'course',
                    'exam'
                );
                """
            ).fetchone()[0]

            if unresolved != 0:
                raise RuntimeError(
                    "Nicht alle bestehenden "
                    "Lehrgänge besitzen einen "
                    "unterstützten alten Typ. "
                    f"Offene Datensätze: "
                    f"{unresolved}"
                )

            connection.execute(
                """
                CREATE TABLE lehrgaenge_neu (
                    id TEXT PRIMARY KEY,

                    lehrgangstyp_id TEXT NOT NULL,

                    bezeichnung TEXT NOT NULL,
                    beschreibung TEXT,

                    bemerkungen TEXT,

                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,

                    FOREIGN KEY (
                        lehrgangstyp_id
                    )
                        REFERENCES
                            lehrgangstypen(id)
                        ON DELETE RESTRICT
                );
                """
            )

            connection.execute(
                """
                INSERT INTO lehrgaenge_neu (
                    id,
                    lehrgangstyp_id,
                    bezeichnung,
                    beschreibung,
                    bemerkungen,
                    created_at,
                    updated_at
                )
                SELECT
                    id,
                    CASE typ
                        WHEN 'introductory_day'
                            THEN
                            'course-type-introductory-day'
                        WHEN 'course'
                            THEN
                            'course-type-course'
                        WHEN 'exam'
                            THEN
                            'course-type-exam'
                    END,
                    bezeichnung,
                    beschreibung,
                    bemerkungen,
                    created_at,
                    updated_at
                FROM lehrgaenge;
                """
            )

            new_count = connection.execute(
                """
                SELECT COUNT(*)
                FROM lehrgaenge_neu;
                """
            ).fetchone()[0]

            if old_count != new_count:
                raise RuntimeError(
                    "Bei der Migration der "
                    "Lehrgänge ist ein "
                    "Datenverlust aufgetreten. "
                    f"Vorher: {old_count}, "
                    f"nachher: {new_count}."
                )

            null_types = connection.execute(
                """
                SELECT COUNT(*)
                FROM lehrgaenge_neu
                WHERE lehrgangstyp_id IS NULL;
                """
            ).fetchone()[0]

            if null_types != 0:
                raise RuntimeError(
                    "Mindestens ein Lehrgang "
                    "konnte keinem Lehrgangstyp "
                    "zugeordnet werden."
                )

            connection.execute(
                """
                DROP TABLE lehrgaenge;
                """
            )

            connection.execute(
                """
                ALTER TABLE lehrgaenge_neu
                RENAME TO lehrgaenge;
                """
            )

            connection.execute(
                """
                CREATE INDEX
                    idx_lehrgaenge_lehrgangstyp
                ON lehrgaenge(
                    lehrgangstyp_id
                );
                """
            )

            connection.execute(
                """
                CREATE INDEX
                    idx_lehrgangstypen_aktiv
                ON lehrgangstypen(
                    aktiv
                );
                """
            )

            connection.execute(
                """
                UPDATE schema_info
                SET version = 5;
                """
            )

            connection.commit()

            connection.execute(
                "PRAGMA foreign_keys = ON;"
            )

            foreign_key_errors = (
                connection.execute(
                    """
                    PRAGMA foreign_key_check;
                    """
                ).fetchall()
            )

            if foreign_key_errors:
                raise RuntimeError(
                    "Nach der Migration wurden "
                    "Foreign-Key-Fehler gefunden: "
                    f"{len(foreign_key_errors)}"
                )

            integrity = connection.execute(
                """
                PRAGMA integrity_check;
                """
            ).fetchone()[0]

            if integrity != "ok":
                raise RuntimeError(
                    "Integritätsprüfung nach "
                    "Migration fehlgeschlagen: "
                    f"{integrity}"
                )

        except Exception:
            if connection.in_transaction:
                connection.rollback()

            raise

        finally:
            connection.close()

    def _migrate_5_to_6(
        self,
    ) -> None:
        connection = sqlite3.connect(
            self.database_path
        )

        connection.row_factory = (
            sqlite3.Row
        )

        try:
            connection.execute(
                "PRAGMA foreign_keys = OFF;"
            )

            connection.execute(
                "BEGIN IMMEDIATE;"
            )

            old_count = connection.execute(
                """
                SELECT COUNT(*)
                FROM pruefungsergebnisse;
                """
            ).fetchone()[0]

            # Schema 5 kann Kursergebnisse nur
            # über Person + Lehrgang identifizieren.
            # Eine automatische Zuordnung zu einer
            # konkreten Kurszuordnung wäre daher
            # nicht eindeutig und könnte Daten
            # verfälschen.
            if old_count != 0:
                raise RuntimeError(
                    "Die Migration von Schema 5 "
                    "auf Schema 6 kann nicht "
                    "automatisch durchgeführt "
                    "werden, weil bereits "
                    "Kursergebnisse vorhanden "
                    "sind. Anzahl: "
                    f"{old_count}"
                )

            connection.execute(
                """
                CREATE TABLE
                    pruefungsergebnisse_neu (
                    id TEXT PRIMARY KEY,

                    kurszuordnung_id TEXT NOT NULL,

                    bestanden INTEGER NOT NULL,

                    note TEXT,
                    bemerkungen TEXT,

                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,

                    FOREIGN KEY (
                        kurszuordnung_id
                    )
                        REFERENCES
                            kurszuordnungen(id)
                        ON DELETE RESTRICT,

                    CHECK (
                        bestanden IN (0, 1)
                    ),

                    UNIQUE (
                        kurszuordnung_id
                    )
                );
                """
            )

            connection.execute(
                """
                DROP TABLE pruefungsergebnisse;
                """
            )

            connection.execute(
                """
                ALTER TABLE
                    pruefungsergebnisse_neu
                RENAME TO pruefungsergebnisse;
                """
            )

            connection.execute(
                """
                CREATE INDEX
                    idx_pruefungsergebnisse_kurszuordnung
                ON pruefungsergebnisse(
                    kurszuordnung_id
                );
                """
            )

            new_count = connection.execute(
                """
                SELECT COUNT(*)
                FROM pruefungsergebnisse;
                """
            ).fetchone()[0]

            if new_count != old_count:
                raise RuntimeError(
                    "Bei der Migration der "
                    "Kursergebnisse ist ein "
                    "Datenverlust aufgetreten. "
                    f"Vorher: {old_count}, "
                    f"nachher: {new_count}."
                )

            columns = {
                row["name"]
                for row in connection.execute(
                    """
                    PRAGMA table_info(
                        pruefungsergebnisse
                    );
                    """
                ).fetchall()
            }

            expected_columns = {
                "id",
                "kurszuordnung_id",
                "bestanden",
                "note",
                "bemerkungen",
                "created_at",
                "updated_at",
            }

            if columns != expected_columns:
                raise RuntimeError(
                    "Die Tabelle "
                    "pruefungsergebnisse besitzt "
                    "nach der Migration nicht die "
                    "erwartete Struktur."
                )

            foreign_key_errors = (
                connection.execute(
                    """
                    PRAGMA foreign_key_check;
                    """
                ).fetchall()
            )

            if foreign_key_errors:
                raise RuntimeError(
                    "Nach der Migration wurden "
                    "Foreign-Key-Fehler gefunden: "
                    f"{len(foreign_key_errors)}"
                )

            integrity = connection.execute(
                """
                PRAGMA integrity_check;
                """
            ).fetchone()[0]

            if integrity != "ok":
                raise RuntimeError(
                    "Integritätsprüfung nach "
                    "Migration fehlgeschlagen: "
                    f"{integrity}"
                )

            connection.execute(
                """
                UPDATE schema_info
                SET version = 6;
                """
            )

            connection.commit()

            connection.execute(
                "PRAGMA foreign_keys = ON;"
            )

        except Exception:
            if connection.in_transaction:
                connection.rollback()

            raise

        finally:
            connection.close()

    def _migrate_6_to_7(
        self,
    ) -> None:
        connection = sqlite3.connect(
            self.database_path
        )

        connection.row_factory = (
            sqlite3.Row
        )

        try:
            connection.execute(
                "PRAGMA foreign_keys = ON;"
            )

            connection.execute(
                "BEGIN IMMEDIATE;"
            )

            existing_table = (
                connection.execute(
                    """
                    SELECT name
                    FROM sqlite_master
                    WHERE
                        type = 'table'
                        AND name = 'benutzer';
                    """
                ).fetchone()
            )

            if existing_table is not None:
                raise RuntimeError(
                    "Die Tabelle 'benutzer' "
                    "existiert bereits, obwohl "
                    "die Datenbank noch "
                    "Schema-Version 6 meldet."
                )

            connection.execute(
                """
                CREATE TABLE benutzer (
                    id TEXT PRIMARY KEY,

                    username TEXT NOT NULL
                        COLLATE NOCASE UNIQUE,

                    nachname TEXT NOT NULL,
                    vorname TEXT NOT NULL,

                    email TEXT NOT NULL
                        COLLATE NOCASE UNIQUE,

                    password_hash TEXT NOT NULL,

                    rolle TEXT NOT NULL,

                    ist_systemadmin INTEGER
                        NOT NULL DEFAULT 0,

                    passwort_aendern INTEGER
                        NOT NULL DEFAULT 0,

                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,

                    CHECK (
                        rolle IN (
                            'administrator',
                            'kursverwaltung',
                            'instruktor',
                            'leser',
                            'inaktiv'
                        )
                    ),

                    CHECK (
                        ist_systemadmin IN (0, 1)
                    ),

                    CHECK (
                        passwort_aendern IN (0, 1)
                    ),

                    CHECK (
                        ist_systemadmin = 0
                        OR rolle = 'administrator'
                    )
                );
                """
            )

            connection.execute(
                """
                CREATE INDEX
                    idx_benutzer_namen
                ON benutzer(
                    nachname,
                    vorname
                );
                """
            )

            connection.execute(
                """
                CREATE INDEX
                    idx_benutzer_rolle
                ON benutzer(
                    rolle
                );
                """
            )

            connection.execute(
                """
                CREATE UNIQUE INDEX
                    idx_benutzer_systemadmin
                ON benutzer(
                    ist_systemadmin
                )
                WHERE ist_systemadmin = 1;
                """
            )

            columns = {
                row["name"]
                for row in connection.execute(
                    """
                    PRAGMA table_info(
                        benutzer
                    );
                    """
                ).fetchall()
            }

            expected_columns = {
                "id",
                "username",
                "nachname",
                "vorname",
                "email",
                "password_hash",
                "rolle",
                "ist_systemadmin",
                "passwort_aendern",
                "created_at",
                "updated_at",
            }

            if columns != expected_columns:
                raise RuntimeError(
                    "Die Tabelle 'benutzer' "
                    "besitzt nach der Migration "
                    "nicht die erwartete "
                    "Struktur."
                )

            indexes = {
                row["name"]
                for row in connection.execute(
                    """
                    SELECT name
                    FROM sqlite_master
                    WHERE
                        type = 'index'
                        AND tbl_name = 'benutzer';
                    """
                ).fetchall()
                if row["name"] is not None
            }

            expected_indexes = {
                "idx_benutzer_namen",
                "idx_benutzer_rolle",
                "idx_benutzer_systemadmin",
            }

            if not expected_indexes.issubset(
                indexes
            ):
                missing_indexes = (
                    expected_indexes - indexes
                )

                raise RuntimeError(
                    "Nach der Migration fehlen "
                    "Benutzer-Indizes: "
                    + ", ".join(
                        sorted(missing_indexes)
                    )
                )

            user_count = connection.execute(
                """
                SELECT COUNT(*)
                FROM benutzer;
                """
            ).fetchone()[0]

            if user_count != 0:
                raise RuntimeError(
                    "Die neu angelegte Tabelle "
                    "'benutzer' ist unerwartet "
                    "nicht leer."
                )

            foreign_key_errors = (
                connection.execute(
                    """
                    PRAGMA foreign_key_check;
                    """
                ).fetchall()
            )

            if foreign_key_errors:
                raise RuntimeError(
                    "Nach der Migration wurden "
                    "Foreign-Key-Fehler gefunden: "
                    f"{len(foreign_key_errors)}"
                )

            integrity = connection.execute(
                """
                PRAGMA integrity_check;
                """
            ).fetchone()[0]

            if integrity != "ok":
                raise RuntimeError(
                    "Integritätsprüfung nach "
                    "Migration fehlgeschlagen: "
                    f"{integrity}"
                )

            connection.execute(
                """
                UPDATE schema_info
                SET version = 7;
                """
            )

            connection.commit()

        except Exception:
            if connection.in_transaction:
                connection.rollback()

            raise

        finally:
            connection.close()

    def _migrate_7_to_8(
        self,
    ) -> None:
        connection = sqlite3.connect(
            self.database_path
        )

        connection.row_factory = (
            sqlite3.Row
        )

        try:
            connection.execute(
                "PRAGMA foreign_keys = ON;"
            )

            connection.execute(
                "BEGIN IMMEDIATE;"
            )

            existing_table = (
                connection.execute(
                    """
                    SELECT name
                    FROM sqlite_master
                    WHERE
                        type = 'table'
                        AND name = 'benutzer_kurstage';
                    """
                ).fetchone()
            )

            if existing_table is not None:
                raise RuntimeError(
                    "Die Tabelle "
                    "'benutzer_kurstage' "
                    "existiert bereits, obwohl "
                    "die Datenbank noch "
                    "Schema-Version 7 meldet."
                )

            connection.execute(
                """
                CREATE TABLE benutzer_kurstage (
                    benutzer_id TEXT NOT NULL,
                    kurstag_id TEXT NOT NULL,

                    created_at TEXT NOT NULL,

                    PRIMARY KEY (
                        benutzer_id,
                        kurstag_id
                    ),

                    FOREIGN KEY (benutzer_id)
                        REFERENCES benutzer(id)
                        ON DELETE CASCADE,

                    FOREIGN KEY (kurstag_id)
                        REFERENCES kurstage(id)
                        ON DELETE CASCADE
                );
                """
            )

            connection.execute(
                """
                CREATE INDEX
                    idx_benutzer_kurstage_kurstag
                ON benutzer_kurstage(
                    kurstag_id
                );
                """
            )

            columns = {
                row["name"]
                for row in connection.execute(
                    """
                    PRAGMA table_info(
                        benutzer_kurstage
                    );
                    """
                ).fetchall()
            }

            expected_columns = {
                "benutzer_id",
                "kurstag_id",
                "created_at",
            }

            if columns != expected_columns:
                raise RuntimeError(
                    "Die Tabelle "
                    "'benutzer_kurstage' "
                    "besitzt nicht die "
                    "erwartete Struktur."
                )

            index_row = connection.execute(
                """
                SELECT name
                FROM sqlite_master
                WHERE
                    type = 'index'
                    AND name =
                        'idx_benutzer_kurstage_kurstag';
                """
            ).fetchone()

            if index_row is None:
                raise RuntimeError(
                    "Der Index für "
                    "'benutzer_kurstage' "
                    "wurde nicht angelegt."
                )

            assignment_count = (
                connection.execute(
                    """
                    SELECT COUNT(*)
                    FROM benutzer_kurstage;
                    """
                ).fetchone()[0]
            )

            if assignment_count != 0:
                raise RuntimeError(
                    "Die neue Tabelle "
                    "'benutzer_kurstage' ist "
                    "unerwartet nicht leer."
                )

            foreign_key_errors = (
                connection.execute(
                    """
                    PRAGMA foreign_key_check;
                    """
                ).fetchall()
            )

            if foreign_key_errors:
                raise RuntimeError(
                    "Nach der Migration wurden "
                    "Foreign-Key-Fehler gefunden: "
                    f"{len(foreign_key_errors)}"
                )

            integrity = connection.execute(
                """
                PRAGMA integrity_check;
                """
            ).fetchone()[0]

            if integrity != "ok":
                raise RuntimeError(
                    "Integritätsprüfung nach "
                    "Migration fehlgeschlagen: "
                    f"{integrity}"
                )

            connection.execute(
                """
                UPDATE schema_info
                SET version = 8;
                """
            )

            connection.commit()

        except Exception:
            if connection.in_transaction:
                connection.rollback()

            raise

        finally:
            connection.close()

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

        row = connection.execute(
            """
            SELECT version
            FROM schema_info
            LIMIT 1;
            """
        ).fetchone()

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

