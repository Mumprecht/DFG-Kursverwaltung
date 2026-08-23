import re

from dfg_kursverwaltung.repositories.suche_repository import (
    SearchRepository,
    SearchResult,
)
from dfg_kursverwaltung.services.telefonnummern_service import (
    PhoneNumberService,
)


class SearchService:
    def __init__(
        self,
        repository: SearchRepository,
    ):
        self.repository = repository

    def search(
        self,
        search_text: str,
    ) -> list[SearchResult]:
        search_text = search_text.strip()

        if not search_text:
            return []

        results = self.repository.search(
            search_text
        )

        normalized_phone = (
            self._try_normalize_phone(
                search_text
            )
        )

        if (
            normalized_phone is not None
            and normalized_phone != search_text
        ):
            phone_results = self.repository.search(
                normalized_phone
            )

            existing_keys = {
                (
                    result.typ,
                    result.id,
                )
                for result in results
            }

            for result in phone_results:
                key = (
                    result.typ,
                    result.id,
                )

                if key not in existing_keys:
                    results.append(
                        result
                    )
                    existing_keys.add(
                        key
                    )

        return self._sort_results(
            results
        )

    def group_results(
        self,
        results: list[SearchResult],
    ) -> dict[str, list[SearchResult]]:
        groups = {
            "person": [],
            "telefon": [],
            "drohne": [],
            "lehrgang": [],
            "standort": [],
        }

        for result in results:
            if result.typ not in groups:
                groups[result.typ] = []

            groups[result.typ].append(
                result
            )

        return groups

    @staticmethod
    def _sort_results(
        results: list[SearchResult],
    ) -> list[SearchResult]:
        type_order = {
            "person": 0,
            "telefon": 1,
            "drohne": 2,
            "lehrgang": 3,
            "standort": 4,
        }

        return sorted(
            results,
            key=lambda result: (
                type_order.get(
                    result.typ,
                    99,
                ),
                result.titel.casefold(),
            ),
        )

    @staticmethod
    def _try_normalize_phone(
        search_text: str,
    ) -> str | None:
        # Nur versuchen zu normalisieren,
        # wenn der Suchtext wie eine
        # Telefonnummer aussieht.
        if not re.fullmatch(
            r"[+\d\s()./-]+",
            search_text,
        ):
            return None

        try:
            return (
                PhoneNumberService
                .normalize_phone_number(
                    search_text
                )
            )

        except ValueError:
            return None