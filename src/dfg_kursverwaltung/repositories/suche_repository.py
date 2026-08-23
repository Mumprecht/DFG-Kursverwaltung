from dataclasses import dataclass

from dfg_kursverwaltung.core.database import (
    DatabaseManager,
)


@dataclass(slots=True)
class SearchResult:
    typ: str
    id: str
    titel: str
    details: str | None = None
    person_id: str | None = None


class SearchRepository:
    def __init__(
        self,
        database_manager: DatabaseManager,
    ):
        self.database_manager = database_manager

    def search(
        self,
        search_text: str,
    ) -> list[SearchResult]:
        search_text = search_text.strip()

        if not search_text:
            return []

        search_value = (
            f"%{search_text}%"
        )

        results: list[SearchResult] = []

        results.extend(
            self._search_persons(
                search_value
            )
        )

        results.extend(
            self._search_phone_numbers(
                search_value
            )
        )

        results.extend(
            self._search_drones(
                search_value
            )
        )

        results.extend(
            self._search_courses(
                search_value
            )
        )

        results.extend(
            self._search_locations(
                search_value
            )
        )

        return results

    def _search_persons(
        self,
        search_value: str,
    ) -> list[SearchResult]:
        with self.database_manager.connect() as connection:
            rows = connection.execute(
                """
                SELECT
                    id,
                    nachname,
                    vorname,
                    email,
                    organisation,
                    ort,
                    aktiv
                FROM personen
                WHERE
                    nachname LIKE ?
                    OR vorname LIKE ?
                    OR email LIKE ?
                    OR organisation LIKE ?
                    OR ort LIKE ?
                ORDER BY
                    nachname COLLATE NOCASE,
                    vorname COLLATE NOCASE;
                """,
                (
                    search_value,
                    search_value,
                    search_value,
                    search_value,
                    search_value,
                ),
            ).fetchall()

        results = []

        for row in rows:
            details = []

            if row["organisation"]:
                details.append(
                    row["organisation"]
                )

            if row["email"]:
                details.append(
                    row["email"]
                )

            if row["ort"]:
                details.append(
                    row["ort"]
                )

            if not row["aktiv"]:
                details.append(
                    "inaktiv"
                )

            results.append(
                SearchResult(
                    typ="person",
                    id=row["id"],
                    person_id=row["id"],
                    titel=(
                        f"{row['nachname']}, "
                        f"{row['vorname']}"
                    ),
                    details=(
                        " | ".join(details)
                        if details
                        else None
                    ),
                )
            )

        return results

    def _search_phone_numbers(
        self,
        search_value: str,
    ) -> list[SearchResult]:
        with self.database_manager.connect() as connection:
            rows = connection.execute(
                """
                SELECT
                    t.id,
                    t.person_id,
                    t.nummer_e164,
                    t.typ,
                    p.nachname,
                    p.vorname
                FROM telefonnummern AS t
                JOIN personen AS p
                    ON p.id = t.person_id
                WHERE
                    t.nummer_e164 LIKE ?
                    OR t.typ LIKE ?
                ORDER BY
                    p.nachname COLLATE NOCASE,
                    p.vorname COLLATE NOCASE;
                """,
                (
                    search_value,
                    search_value,
                ),
            ).fetchall()

        return [
            SearchResult(
                typ="telefon",
                id=row["id"],
                person_id=row["person_id"],
                titel=row["nummer_e164"],
                details=(
                    f"{row['vorname']} "
                    f"{row['nachname']}"
                ),
            )
            for row in rows
        ]

    def _search_drones(
        self,
        search_value: str,
    ) -> list[SearchResult]:
        with self.database_manager.connect() as connection:
            rows = connection.execute(
                """
                SELECT
                    d.id,
                    d.person_id,
                    d.hersteller,
                    d.modell,
                    d.seriennummer,
                    p.nachname,
                    p.vorname
                FROM drohnen AS d
                JOIN personen AS p
                    ON p.id = d.person_id
                WHERE
                    d.hersteller LIKE ?
                    OR d.modell LIKE ?
                    OR d.seriennummer LIKE ?
                ORDER BY
                    d.hersteller COLLATE NOCASE,
                    d.modell COLLATE NOCASE;
                """,
                (
                    search_value,
                    search_value,
                    search_value,
                ),
            ).fetchall()

        results = []

        for row in rows:
            drone_name = " ".join(
                value
                for value in (
                    row["hersteller"],
                    row["modell"],
                )
                if value
            )

            details = (
                f"{row['vorname']} "
                f"{row['nachname']}"
            )

            if row["seriennummer"]:
                details += (
                    f" | SN: "
                    f"{row['seriennummer']}"
                )

            results.append(
                SearchResult(
                    typ="drohne",
                    id=row["id"],
                    person_id=row["person_id"],
                    titel=drone_name,
                    details=details,
                )
            )

        return results

    def _search_courses(
        self,
        search_value: str,
    ) -> list[SearchResult]:
        with self.database_manager.connect() as connection:
            rows = connection.execute(
                """
                SELECT
                    id,
                    typ,
                    bezeichnung
                FROM lehrgaenge
                WHERE
                    bezeichnung LIKE ?
                    OR beschreibung LIKE ?
                    OR bemerkungen LIKE ?
                ORDER BY
                    bezeichnung COLLATE NOCASE;
                """,
                (
                    search_value,
                    search_value,
                    search_value,
                ),
            ).fetchall()

        return [
            SearchResult(
                typ="lehrgang",
                id=row["id"],
                titel=row["bezeichnung"],
                details=row["typ"],
            )
            for row in rows
        ]

    def _search_locations(
        self,
        search_value: str,
    ) -> list[SearchResult]:
        with self.database_manager.connect() as connection:
            rows = connection.execute(
                """
                SELECT
                    id,
                    bezeichnung,
                    plz,
                    ort,
                    kontakt_vorname,
                    kontakt_nachname
                FROM standorte
                WHERE
                    bezeichnung LIKE ?
                    OR strasse LIKE ?
                    OR plz LIKE ?
                    OR ort LIKE ?
                    OR kontakt_vorname LIKE ?
                    OR kontakt_nachname LIKE ?
                    OR telefon_e164 LIKE ?
                    OR email LIKE ?
                    OR webseite LIKE ?
                ORDER BY
                    bezeichnung COLLATE NOCASE;
                """,
                (
                    search_value,
                    search_value,
                    search_value,
                    search_value,
                    search_value,
                    search_value,
                    search_value,
                    search_value,
                    search_value,
                ),
            ).fetchall()

        results = []

        for row in rows:
            location = " ".join(
                value
                for value in (
                    row["plz"],
                    row["ort"],
                )
                if value
            )

            results.append(
                SearchResult(
                    typ="standort",
                    id=row["id"],
                    titel=row["bezeichnung"],
                    details=(
                        location
                        if location
                        else None
                    ),
                )
            )

        return results