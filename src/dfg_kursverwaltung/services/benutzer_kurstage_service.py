from dfg_kursverwaltung.core.models import User, UserRole
from dfg_kursverwaltung.repositories.benutzer_kurstage_repository import (
    UserCourseDayRepository,
)
from dfg_kursverwaltung.repositories.benutzer_repository import (
    UserRepository,
)
from dfg_kursverwaltung.repositories.kurstage_repository import (
    CourseDayRepository,
)


class UserCourseDayService:
    def __init__(
        self,
        repository: UserCourseDayRepository,
        user_repository: UserRepository,
        course_day_repository: CourseDayRepository,
    ):
        self.repository = repository
        self.user_repository = user_repository
        self.course_day_repository = (
            course_day_repository
        )

    def grant_access(
        self,
        actor: User,
        user_id: str,
        course_day_id: str,
    ) -> None:
        self._ensure_actor_can_manage(
            actor
        )

        user = self._get_required_user(
            user_id
        )

        if user.rolle != UserRole.INSTRUCTOR:
            raise ValueError(
                "Kurstag-Berechtigungen können "
                "nur Instruktor-Benutzern "
                "zugewiesen werden."
            )

        self._ensure_course_day_exists(
            course_day_id
        )

        if self.repository.has_access(
            user_id,
            course_day_id,
        ):
            raise ValueError(
                "Der Benutzer besitzt bereits "
                "eine Berechtigung für diesen "
                "Kurstag."
            )

        self.repository.grant(
            user_id,
            course_day_id,
        )

    def revoke_access(
        self,
        actor: User,
        user_id: str,
        course_day_id: str,
    ) -> None:
        self._ensure_actor_can_manage(
            actor
        )

        self._get_required_user(
            user_id
        )
        self._ensure_course_day_exists(
            course_day_id
        )

        if not self.repository.has_access(
            user_id,
            course_day_id,
        ):
            raise KeyError(
                "Der Benutzer besitzt keine "
                "Berechtigung für diesen "
                "Kurstag."
            )

        self.repository.revoke(
            user_id,
            course_day_id,
        )

    def has_access(
        self,
        user_id: str,
        course_day_id: str,
    ) -> bool:
        user = self.user_repository.get_by_id(
            user_id
        )

        if user is None:
            return False

        if user.rolle != UserRole.INSTRUCTOR:
            return False

        return self.repository.has_access(
            user_id,
            course_day_id,
        )

    def list_course_day_ids(
        self,
        user_id: str,
    ) -> list[str]:
        user = self._get_required_user(
            user_id
        )

        if user.rolle != UserRole.INSTRUCTOR:
            return []

        return self.repository.list_course_day_ids(
            user_id
        )

    def list_user_ids(
        self,
        course_day_id: str,
    ) -> list[str]:
        self._ensure_course_day_exists(
            course_day_id
        )

        return self.repository.list_user_ids(
            course_day_id
        )

    def _get_required_user(
        self,
        user_id: str,
    ) -> User:
        user = self.user_repository.get_by_id(
            user_id
        )

        if user is None:
            raise KeyError(
                "Benutzer nicht gefunden: "
                f"{user_id}"
            )

        return user

    def _ensure_course_day_exists(
        self,
        course_day_id: str,
    ) -> None:
        course_day = (
            self.course_day_repository
            .get_by_id(course_day_id)
        )

        if course_day is None:
            raise KeyError(
                "Kurstag nicht gefunden: "
                f"{course_day_id}"
            )

    @staticmethod
    def _ensure_actor_can_manage(
        actor: User,
    ) -> None:
        if actor.rolle not in {
            UserRole.ADMINISTRATOR,
            UserRole.COURSE_MANAGEMENT,
        }:
            raise PermissionError(
                "Dieser Benutzer darf keine "
                "Kurstag-Berechtigungen "
                "verwalten."
            )
