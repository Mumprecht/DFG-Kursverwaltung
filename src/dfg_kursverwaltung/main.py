import sys
from pathlib import Path

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QMessageBox,
)

from dfg_kursverwaltung.core.database import (
    DatabaseManager,
)
from dfg_kursverwaltung.core.i18n import (
    TranslationManager,
)
from dfg_kursverwaltung.gui.change_password_dialog import (
    ChangePasswordDialog,
)
from dfg_kursverwaltung.gui.login_dialog import (
    LoginDialog,
)
from dfg_kursverwaltung.gui.main_window import (
    MainWindow,
)
from dfg_kursverwaltung.gui.systemadmin_setup_dialog import (
    SystemAdminSetupDialog,
)
from dfg_kursverwaltung.repositories.drohnen_repository import (
    DroneRepository,
)
from dfg_kursverwaltung.repositories.kurstage_repository import (
    CourseDayRepository,
)
from dfg_kursverwaltung.repositories.kurszuordnungen_repository import (
    CourseAssignmentRepository,
)
from dfg_kursverwaltung.repositories.lehrgaenge_repository import (
    CourseRepository,
)
from dfg_kursverwaltung.repositories.lehrgangstypen_repository import (
    CourseTypeRepository,
)
from dfg_kursverwaltung.repositories.personen_repository import (
    PersonRepository,
)
from dfg_kursverwaltung.repositories.pruefungsergebnisse_repository import (
    ExamResultRepository,
)
from dfg_kursverwaltung.repositories.standorte_repository import (
    LocationRepository,
)
from dfg_kursverwaltung.repositories.suche_repository import (
    SearchRepository,
)
from dfg_kursverwaltung.repositories.telefonnummern_repository import (
    PhoneNumberRepository,
)
from dfg_kursverwaltung.repositories.benutzer_repository import (
    UserRepository,
)
from dfg_kursverwaltung.services.auth_service import (
    AuthenticationService,
)
from dfg_kursverwaltung.services.backup_service import (
    BackupService,
)
from dfg_kursverwaltung.services.benutzer_service import (
    UserService,
)
from dfg_kursverwaltung.services.bootstrap_service import (
    BootstrapService,
)
from dfg_kursverwaltung.services.drohnen_service import (
    DroneService,
)
from dfg_kursverwaltung.services.export_service import (
    ExportService,
)
from dfg_kursverwaltung.services.import_service import (
    ImportService,
)
from dfg_kursverwaltung.services.kurstage_service import (
    CourseDayService,
)
from dfg_kursverwaltung.services.kurszuordnungen_service import (
    CourseAssignmentService,
)
from dfg_kursverwaltung.services.lehrgaenge_service import (
    CourseService,
)
from dfg_kursverwaltung.services.lehrgangstypen_service import (
    CourseTypeService,
)
from dfg_kursverwaltung.services.personen_service import (
    PersonService,
)
from dfg_kursverwaltung.services.pruefungsergebnisse_service import (
    ExamResultService,
)
from dfg_kursverwaltung.services.standorte_service import (
    LocationService,
)
from dfg_kursverwaltung.services.suche_service import (
    SearchService,
)
from dfg_kursverwaltung.services.telefonnummern_service import (
    PhoneNumberService,
)


def get_icon_path() -> Path:
    return (
        Path(__file__).resolve().parent
        / "resources"
        / "icons"
        / "DFG-Kursverwaltung.png"
    )


def main():
    app = QApplication(
        sys.argv
    )

    icon_path = get_icon_path()

    if icon_path.exists():
        app.setWindowIcon(
            QIcon(
                str(icon_path)
            )
        )

    # ---------------------------------------------------------
    # Datenbank
    # ---------------------------------------------------------

    database_manager = DatabaseManager()

    database_manager.initialize_database()

    # ---------------------------------------------------------
    # Repositories
    # ---------------------------------------------------------

    person_repository = PersonRepository(
        database_manager
    )

    phone_number_repository = PhoneNumberRepository(
        database_manager
    )

    drone_repository = DroneRepository(
        database_manager
    )

    course_type_repository = CourseTypeRepository(
        database_manager
    )

    course_repository = CourseRepository(
        database_manager
    )

    course_day_repository = CourseDayRepository(
        database_manager
    )

    location_repository = LocationRepository(
        database_manager
    )

    assignment_repository = CourseAssignmentRepository(
        database_manager
    )

    exam_result_repository = ExamResultRepository(
        database_manager
    )

    search_repository = SearchRepository(
        database_manager
    )

    user_repository = UserRepository(
        database_manager
    )

    # ---------------------------------------------------------
    # Services
    # ---------------------------------------------------------

    person_service = PersonService(
        person_repository
    )

    phone_number_service = PhoneNumberService(
        phone_number_repository
    )

    drone_service = DroneService(
        drone_repository
    )

    course_type_service = CourseTypeService(
        course_type_repository
    )

    course_service = CourseService(
        course_repository,
        course_type_repository,
    )

    course_day_service = CourseDayService(
        course_day_repository
    )

    location_service = LocationService(
        location_repository
    )

    assignment_service = CourseAssignmentService(
        assignment_repository,
        person_repository,
        exam_result_repository,
    )

    exam_result_service = ExamResultService(
        exam_result_repository,
        assignment_repository,
    )

    search_service = SearchService(
        search_repository
    )

    export_service = ExportService(
        person_service,
        phone_number_service,
        location_service,
        course_service,
        course_type_service,
        course_day_service,
        assignment_service,
        exam_result_service,
    )

    import_service = ImportService(
        person_service,
        phone_number_service,
        location_service,
        course_service,
        course_type_service,
        course_day_service,
        assignment_service,
        exam_result_service,
    )

    backup_service = BackupService(
        database_manager
    )

    user_service = UserService(
        user_repository
    )

    bootstrap_service = BootstrapService(
        user_service
    )

    authentication_service = AuthenticationService(
        user_repository
    )

    # ---------------------------------------------------------
    # Übersetzungen
    # ---------------------------------------------------------

    translation_manager = TranslationManager(
        app
    )

    language = (
        translation_manager
        .get_saved_language()
    )

    translation_manager.load_language(
        language
    )

    # ---------------------------------------------------------
    # Ersteinrichtung
    # ---------------------------------------------------------

    while (
        bootstrap_service
        .requires_systemadmin_setup()
    ):
        dialog = SystemAdminSetupDialog(
            translation_manager
        )

        if icon_path.exists():
            dialog.setWindowIcon(
                QIcon(
                    str(icon_path)
                )
            )

        result = dialog.exec()

        if (
            result
            == SystemAdminSetupDialog.LANGUAGE_CHANGED
        ):
            continue

        if result != QDialog.DialogCode.Accepted:
            return 0

        data = dialog.get_data()

        try:
            user_service.create_systemadmin(
                **data
            )
        except (ValueError, TypeError) as error:
            QMessageBox.warning(
                None,
                QApplication.translate(
                    "main",
                    "Systemadministrator",
                ),
                str(error),
            )
            continue

    # ---------------------------------------------------------
    # Anmeldung
    # ---------------------------------------------------------

    authenticated_user = None

    while authenticated_user is None:
        dialog = LoginDialog()

        if icon_path.exists():
            dialog.setWindowIcon(
                QIcon(
                    str(icon_path)
                )
            )

        result = dialog.exec()

        if result != QDialog.DialogCode.Accepted:
            return 0

        username, password = (
            dialog.get_credentials()
        )

        authenticated_user = (
            authentication_service.authenticate(
                username,
                password,
            )
        )

        del password

        if authenticated_user is None:
            QMessageBox.warning(
                None,
                QApplication.translate(
                    "main",
                    "Anmeldung fehlgeschlagen",
                ),
                QApplication.translate(
                    "main",
                    "Benutzername oder Passwort ist ungültig.",
                ),
            )
            continue

        # -----------------------------------------------------
        # Erzwungener Passwortwechsel
        # -----------------------------------------------------

        if authenticated_user.passwort_aendern:
            password_changed = False

            while not password_changed:
                password_dialog = (
                    ChangePasswordDialog()
                )

                if icon_path.exists():
                    password_dialog.setWindowIcon(
                        QIcon(
                            str(icon_path)
                        )
                    )

                result = password_dialog.exec()

                if (
                    result
                    != QDialog.DialogCode.Accepted
                ):
                    authenticated_user = None
                    break

                (
                    current_password,
                    new_password,
                ) = password_dialog.get_passwords()

                try:
                    user_service.change_own_password(
                        authenticated_user.id,
                        current_password,
                        new_password,
                    )
                except (ValueError, TypeError) as error:
                    QMessageBox.warning(
                        None,
                        QApplication.translate(
                            "main",
                            "Passwort konnte nicht geändert werden",
                        ),
                        str(error),
                    )
                    continue
                finally:
                    del current_password
                    del new_password

                authenticated_user = (
                    user_service.get_user(
                        authenticated_user.id
                    )
                )

                if authenticated_user is None:
                    raise RuntimeError(
                        "Benutzer konnte nach dem "
                        "Passwortwechsel nicht erneut "
                        "geladen werden."
                    )

                password_changed = True

            if authenticated_user is None:
                continue

    # ---------------------------------------------------------
    # Hauptfenster
    # ---------------------------------------------------------

    window = MainWindow(
        translation_manager,
        person_service,
        phone_number_service,
        drone_service,
        course_service,
        course_type_service,
        course_day_service,
        location_service,
        assignment_service,
        exam_result_service,
        search_service,
        import_service,
        export_service,
        backup_service,
        user_service,
        authenticated_user,
    )

    if icon_path.exists():
        window.setWindowIcon(
            QIcon(
                str(icon_path)
            )
        )

    window.show()

    return app.exec()


if __name__ == "__main__":
    sys.exit(
        main()
    )
