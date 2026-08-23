import sys
from pathlib import Path

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from dfg_kursverwaltung.core.database import (
    DatabaseManager,
)
from dfg_kursverwaltung.core.i18n import (
    TranslationManager,
)
from dfg_kursverwaltung.gui.main_window import (
    MainWindow,
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
from dfg_kursverwaltung.repositories.personen_repository import (
    PersonRepository,
)
from dfg_kursverwaltung.repositories.standorte_repository import (
    LocationRepository,
)
from dfg_kursverwaltung.repositories.telefonnummern_repository import (
    PhoneNumberRepository,
)
from dfg_kursverwaltung.services.drohnen_service import (
    DroneService,
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
from dfg_kursverwaltung.services.personen_service import (
    PersonService,
)
from dfg_kursverwaltung.services.standorte_service import (
    LocationService,
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

    course_repository = CourseRepository(
        database_manager
    )

    course_day_repository = CourseDayRepository(
        database_manager
    )

    location_repository = LocationRepository(
        database_manager
    )

    assignment_repository = (
        CourseAssignmentRepository(
            database_manager
        )
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

    course_service = CourseService(
        course_repository
    )

    course_day_service = CourseDayService(
        course_day_repository
    )

    location_service = LocationService(
        location_repository
    )

    assignment_service = (
        CourseAssignmentService(
            assignment_repository
        )
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
    # Hauptfenster
    # ---------------------------------------------------------

    window = MainWindow(
        translation_manager,
        person_service,
        phone_number_service,
        drone_service,
        course_service,
        course_day_service,
        location_service,
        assignment_service,
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