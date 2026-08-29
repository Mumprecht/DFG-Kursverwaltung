from dfg_kursverwaltung.core.models import User
from dfg_kursverwaltung.services.benutzer_service import (
    UserService,
)


class BootstrapService:
    def __init__(
        self,
        user_service: UserService,
    ):
        self.user_service = user_service

    def requires_systemadmin_setup(
        self,
    ) -> bool:
        return (
            self.user_service.get_systemadmin()
            is None
        )

    def get_systemadmin(
        self,
    ) -> User | None:
        return self.user_service.get_systemadmin()
