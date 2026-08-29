from datetime import datetime, timezone

from dfg_kursverwaltung.core.models import User, UserRole
from dfg_kursverwaltung.core.passwords import (
    hash_password,
    needs_rehash,
    verify_password,
)
from dfg_kursverwaltung.repositories.benutzer_repository import (
    UserRepository,
)


class AuthenticationService:
    def __init__(
        self,
        repository: UserRepository,
    ):
        self.repository = repository

        # Dummy-Hash für nicht vorhandene Benutzer.
        # Dadurch wird auch in diesem Fall eine
        # scrypt-Prüfung durchgeführt.
        self._dummy_hash = hash_password(
            "DFG-Kursverwaltung-Dummy-Passwort"
        )

    def authenticate(
        self,
        username: str,
        password: str,
    ) -> User | None:
        if not isinstance(username, str):
            self._verify_dummy(password)
            return None

        username = username.strip()

        if not username:
            self._verify_dummy(password)
            return None

        user = self.repository.get_by_username(
            username
        )

        if user is None:
            self._verify_dummy(password)
            return None

        password_valid = verify_password(
            password,
            user.password_hash,
        )

        if not password_valid:
            return None

        # Ein inaktiver Benutzer wird trotz
        # korrektem Passwort niemals angemeldet.
        if user.rolle == UserRole.INACTIVE:
            return None

        # Erfolgreiche Anmeldung bietet einen
        # sicheren Zeitpunkt, um einen älteren
        # Passwort-Hash transparent auf die
        # aktuellen Parameter zu aktualisieren.
        if needs_rehash(
            user.password_hash
        ):
            user.password_hash = hash_password(
                password
            )
            user.updated_at = datetime.now(
                timezone.utc
            )

            user = self.repository.update(
                user
            )

        return user

    def _verify_dummy(
        self,
        password: str,
    ) -> None:
        # Das Ergebnis wird bewusst ignoriert.
        verify_password(
            password,
            self._dummy_hash,
        )
