from datetime import datetime, timezone
from uuid import uuid4

from dfg_kursverwaltung.core.models import User, UserRole
from dfg_kursverwaltung.core.passwords import (
    hash_password,
    verify_password,
)
from dfg_kursverwaltung.repositories.benutzer_repository import (
    UserRepository,
)


class UserService:
    def __init__(
        self,
        repository: UserRepository,
    ):
        self.repository = repository

    def create_user(
        self,
        *,
        username: str,
        nachname: str,
        vorname: str,
        email: str,
        password: str,
        rolle: UserRole | str,
        passwort_aendern: bool = False,
    ) -> User:
        username = self._clean_required(
            username,
            "Benutzername",
        )
        nachname = self._clean_required(
            nachname,
            "Nachname",
        )
        vorname = self._clean_required(
            vorname,
            "Vorname",
        )
        email = self._clean_required(
            email,
            "E-Mail",
        )

        rolle = UserRole(rolle)

        if rolle == UserRole.INACTIVE:
            raise ValueError(
                "Ein neuer Benutzer kann nicht "
                "direkt mit der Rolle Inaktiv "
                "erstellt werden."
            )

        self._ensure_username_available(
            username
        )
        self._ensure_email_available(
            email
        )

        timestamp = datetime.now(
            timezone.utc
        )

        user = User(
            id=str(uuid4()),
            username=username,
            nachname=nachname,
            vorname=vorname,
            email=email,
            password_hash=hash_password(
                password
            ),
            rolle=rolle,
            ist_systemadmin=False,
            passwort_aendern=bool(
                passwort_aendern
            ),
            created_at=timestamp,
            updated_at=timestamp,
        )

        return self.repository.create(
            user
        )

    def create_systemadmin(
        self,
        *,
        username: str,
        nachname: str,
        vorname: str,
        email: str,
        password: str,
    ) -> User:
        if (
            self.repository.get_systemadmin()
            is not None
        ):
            raise ValueError(
                "Der geschützte "
                "Systemadministrator existiert "
                "bereits."
            )

        username = self._clean_required(
            username,
            "Benutzername",
        )
        nachname = self._clean_required(
            nachname,
            "Nachname",
        )
        vorname = self._clean_required(
            vorname,
            "Vorname",
        )
        email = self._clean_required(
            email,
            "E-Mail",
        )

        self._ensure_username_available(
            username
        )
        self._ensure_email_available(
            email
        )

        timestamp = datetime.now(
            timezone.utc
        )

        user = User(
            id=str(uuid4()),
            username=username,
            nachname=nachname,
            vorname=vorname,
            email=email,
            password_hash=hash_password(
                password
            ),
            rolle=UserRole.ADMINISTRATOR,
            ist_systemadmin=True,
            passwort_aendern=False,
            created_at=timestamp,
            updated_at=timestamp,
        )

        return self.repository.create(
            user
        )

    def get_user(
        self,
        user_id: str,
    ) -> User | None:
        return self.repository.get_by_id(
            user_id
        )

    def get_user_by_username(
        self,
        username: str,
    ) -> User | None:
        return self.repository.get_by_username(
            username
        )

    def get_systemadmin(
        self,
    ) -> User | None:
        return self.repository.get_systemadmin()

    def list_users(
        self,
        include_inactive: bool = True,
    ) -> list[User]:
        return self.repository.list_all(
            include_inactive=include_inactive
        )

    def update_user(
        self,
        user: User,
    ) -> User:
        original = self.repository.get_by_id(
            user.id
        )

        if original is None:
            raise KeyError(
                "Benutzer nicht gefunden: "
                f"{user.id}"
            )

        user.username = self._clean_required(
            user.username,
            "Benutzername",
        )
        user.nachname = self._clean_required(
            user.nachname,
            "Nachname",
        )
        user.vorname = self._clean_required(
            user.vorname,
            "Vorname",
        )
        user.email = self._clean_required(
            user.email,
            "E-Mail",
        )
        user.rolle = UserRole(
            user.rolle
        )

        self._ensure_username_available(
            user.username,
            exclude_user_id=user.id,
        )
        self._ensure_email_available(
            user.email,
            exclude_user_id=user.id,
        )

        # Passwort-Hash und Systemadmin-Flag dürfen
        # über die normale Stammdatenänderung nicht
        # manipuliert werden.
        user.password_hash = (
            original.password_hash
        )
        user.ist_systemadmin = (
            original.ist_systemadmin
        )

        if original.ist_systemadmin:
            if (
                user.rolle
                != UserRole.ADMINISTRATOR
            ):
                raise ValueError(
                    "Die Rolle des geschützten "
                    "Systemadministrators kann "
                    "nicht geändert werden."
                )

            # Auch die Kennzeichnung für einen
            # erzwungenen Passwortwechsel wird beim
            # Systemadministrator nicht über die
            # Stammdatenpflege verändert.
            user.passwort_aendern = (
                original.passwort_aendern
            )

        user.updated_at = datetime.now(
            timezone.utc
        )

        updated_user = self.repository.update(
            user
        )

        return updated_user

    def deactivate_user(
        self,
        user_id: str,
    ) -> User:
        user = self._get_required_user(
            user_id
        )

        if user.ist_systemadmin:
            raise ValueError(
                "Der geschützte "
                "Systemadministrator kann "
                "nicht deaktiviert werden."
            )

        original_role = user.rolle

        user.rolle = UserRole.INACTIVE

        updated_user = self.repository.update(
            user
        )

        return updated_user

    def set_role(
        self,
        user_id: str,
        rolle: UserRole | str,
    ) -> User:
        user = self._get_required_user(
            user_id
        )

        rolle = UserRole(rolle)

        if user.ist_systemadmin:
            if rolle != UserRole.ADMINISTRATOR:
                raise ValueError(
                    "Die Rolle des geschützten "
                    "Systemadministrators kann "
                    "nicht geändert werden."
                )

            return user

        original_role = user.rolle

        user.rolle = rolle

        updated_user = self.repository.update(
            user
        )

        return updated_user

    def reset_password(
        self,
        user_id: str,
        new_password: str,
        *,
        require_change: bool = True,
    ) -> User:
        user = self._get_required_user(
            user_id
        )

        user.password_hash = hash_password(
            new_password
        )
        user.passwort_aendern = bool(
            require_change
        )
        user.updated_at = datetime.now(
            timezone.utc
        )

        return self.repository.update(
            user
        )

    def change_own_password(
        self,
        user_id: str,
        current_password: str,
        new_password: str,
    ) -> User:
        user = self._get_required_user(
            user_id
        )

        if not verify_password(
            current_password,
            user.password_hash,
        ):
            raise ValueError(
                "Das aktuelle Passwort ist "
                "nicht korrekt."
            )

        user.password_hash = hash_password(
            new_password
        )
        user.passwort_aendern = False
        user.updated_at = datetime.now(
            timezone.utc
        )

        return self.repository.update(
            user
        )

    def delete_user(
        self,
        user_id: str,
    ) -> None:
        user = self._get_required_user(
            user_id
        )

        if user.ist_systemadmin:
            raise ValueError(
                "Der geschützte "
                "Systemadministrator kann "
                "nicht gelöscht werden."
            )

        self.repository.delete(
            user_id
        )

    def _get_required_user(
        self,
        user_id: str,
    ) -> User:
        user = self.repository.get_by_id(
            user_id
        )

        if user is None:
            raise KeyError(
                "Benutzer nicht gefunden: "
                f"{user_id}"
            )

        return user

    def _ensure_username_available(
        self,
        username: str,
        *,
        exclude_user_id: str | None = None,
    ) -> None:
        existing = (
            self.repository
            .get_by_username(username)
        )

        if (
            existing is not None
            and existing.id
            != exclude_user_id
        ):
            raise ValueError(
                "Der Benutzername ist bereits "
                "vergeben."
            )

    def _ensure_email_available(
        self,
        email: str,
        *,
        exclude_user_id: str | None = None,
    ) -> None:
        existing = (
            self.repository
            .get_by_email(email)
        )

        if (
            existing is not None
            and existing.id
            != exclude_user_id
        ):
            raise ValueError(
                "Die E-Mail-Adresse ist bereits "
                "vergeben."
            )

    @staticmethod
    def _clean_required(
        value: str,
        field_name: str,
    ) -> str:
        if not isinstance(value, str):
            raise TypeError(
                f"{field_name} muss eine "
                "Zeichenkette sein."
            )

        value = value.strip()

        if not value:
            raise ValueError(
                f"{field_name} darf nicht "
                "leer sein."
            )

        return value
