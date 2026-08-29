from PySide6.QtWidgets import (
    QComboBox,
    QGroupBox,
    QLabel,
    QMainWindow,
    QMessageBox,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from dfg_kursverwaltung.core.i18n import (
    SUPPORTED_LANGUAGES,
    TranslationManager,
)
from dfg_kursverwaltung.core.models import (
    User,
    UserRole,
)
from dfg_kursverwaltung.gui.benutzer_widget import (
    BenutzerWidget,
)
from dfg_kursverwaltung.gui.export_widget import (
    ExportWidget,
)
from dfg_kursverwaltung.gui.import_widget import (
    ImportWidget,
)
from dfg_kursverwaltung.gui.kurstage_widget import (
    KurstageWidget,
)
from dfg_kursverwaltung.gui.kurszuordnungen_widget import (
    KurszuordnungenWidget,
)
from dfg_kursverwaltung.gui.lehrgaenge_widget import (
    LehrgaengeWidget,
)
from dfg_kursverwaltung.gui.lehrgangstypen_widget import (
    LehrgangstypenWidget,
)
from dfg_kursverwaltung.gui.personen_widget import (
    PersonenWidget,
)
from dfg_kursverwaltung.gui.sicherung_widget import (
    SicherungWidget,
)
from dfg_kursverwaltung.gui.standorte_widget import (
    StandorteWidget,
)
from dfg_kursverwaltung.gui.suche_widget import (
    SucheWidget,
)
from dfg_kursverwaltung.services.backup_service import (
    BackupService,
)
from dfg_kursverwaltung.services.benutzer_service import (
    UserService,
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


class MainWindow(QMainWindow):
    def __init__(
        self,
        translation_manager: TranslationManager,
        person_service: PersonService,
        phone_number_service: PhoneNumberService,
        drone_service: DroneService,
        course_service: CourseService,
        course_type_service: CourseTypeService,
        course_day_service: CourseDayService,
        location_service: LocationService,
        assignment_service: CourseAssignmentService,
        exam_result_service: ExamResultService,
        search_service: SearchService,
        import_service: ImportService,
        export_service: ExportService,
        backup_service: BackupService,
        user_service: UserService,
        authenticated_user: User,
    ):
        super().__init__()

        self.translation_manager = translation_manager
        self.person_service = person_service
        self.phone_number_service = phone_number_service
        self.drone_service = drone_service
        self.course_service = course_service
        self.course_type_service = course_type_service
        self.course_day_service = course_day_service
        self.location_service = location_service
        self.assignment_service = assignment_service
        self.exam_result_service = exam_result_service
        self.search_service = search_service
        self.import_service = import_service
        self.export_service = export_service
        self.backup_service = backup_service
        self.user_service = user_service
        self.authenticated_user = authenticated_user

        self.setWindowTitle(
            self.tr(
                "DFG Pfannenstiel – Adress- und Kursverwaltung"
            )
        )

        self.resize(
            1200,
            800,
        )

        self.tabs = QTabWidget()

        self.setCentralWidget(
            self.tabs
        )

        self._create_tabs()

        self.tabs.currentChanged.connect(
            self._on_current_tab_changed
        )

    def _create_tabs(self):
        self.start_tab = (
            self._create_start_tab()
        )

        self.tabs.addTab(
            self.start_tab,
            self.tr("Start"),
        )

        self.people_tab = PersonenWidget(
            self.person_service,
            self.phone_number_service,
            self.drone_service,
            self.course_service,
            self.course_type_service,
            self.course_day_service,
            self.assignment_service,
            self.exam_result_service,
        )

        self.courses_tab = LehrgaengeWidget(
            self.course_service,
            self.course_type_service,
            self.course_day_service,
            self.location_service,
        )

        self.course_types_tab = LehrgangstypenWidget(
            self.course_type_service
        )

        self.course_days_tab = KurstageWidget(
            self.course_day_service,
            self.course_service,
            self.course_type_service,
            self.location_service,
        )

        self.course_days_tab.course_requested.connect(
            self._open_course_from_search
        )

        self.locations_tab = StandorteWidget(
            self.location_service
        )

        self.assignments_tab = KurszuordnungenWidget(
            self.person_service,
            self.course_service,
            self.course_day_service,
            self.assignment_service,
            self.exam_result_service,
            self.location_service,
        )

        self.search_tab = SucheWidget(
            self.search_service
        )

        self.search_tab.person_requested.connect(
            self._open_person_from_search
        )

        self.search_tab.course_requested.connect(
            self._open_course_from_search
        )

        self.search_tab.location_requested.connect(
            self._open_location_from_search
        )

        self.import_tab = ImportWidget(
            self.import_service
        )

        self.export_tab = ExportWidget(
            self.export_service
        )

        self.backup_tab = SicherungWidget(
            self.backup_service
        )

        self.users_tab = None

        if (
            self.authenticated_user.rolle
            == UserRole.ADMINISTRATOR
        ):
            self.users_tab = BenutzerWidget(
                self.user_service
            )

        self.tabs.addTab(
            self.people_tab,
            self.tr("Personen"),
        )

        self.tabs.addTab(
            self.courses_tab,
            self.tr(
                "Lehrgänge"
            ),
        )

        self.tabs.addTab(
            self.course_types_tab,
            self.tr("Lehrgangstypen"),
        )

        self.tabs.addTab(
            self.course_days_tab,
            self.tr("Kurstage"),
        )

        self.tabs.addTab(
            self.locations_tab,
            self.tr(
                "Ausführungsorte"
            ),
        )

        self.tabs.addTab(
            self.assignments_tab,
            self.tr(
                "Kurszuordnung"
            ),
        )

        self.tabs.addTab(
            self.search_tab,
            self.tr("Suche"),
        )

        self.tabs.addTab(
            self.import_tab,
            self.tr("Import"),
        )

        self.tabs.addTab(
            self.export_tab,
            self.tr("Export"),
        )

        self.tabs.addTab(
            self.backup_tab,
            self.tr("Sicherung"),
        )

        if self.users_tab is not None:
            self.tabs.addTab(
                self.users_tab,
                self.tr("Benutzer"),
            )

        self.settings_tab = (
            self._create_settings_tab()
        )

        self.tabs.addTab(
            self.settings_tab,
            self.tr("Einstellungen"),
        )

        self.info_tab = QWidget()

        self.tabs.addTab(
            self.info_tab,
            self.tr("Info"),
        )

    def _create_start_tab(self):
        widget = QWidget()

        layout = QVBoxLayout(
            widget
        )

        title = QLabel(
            self.tr(
                "DFG Pfannenstiel – Adress- und Kursverwaltung"
            )
        )

        title.setStyleSheet(
            "font-size: 22px; "
            "font-weight: bold;"
        )

        description = QLabel(
            self.tr(
                "Verwaltung von Teilnehmern, "
                "Instruktoren, Lehrgängen "
                "und Schulungsdaten."
            )
        )

        layout.addWidget(
            title
        )

        layout.addWidget(
            description
        )

        layout.addStretch()

        return widget

    def _create_settings_tab(self):
        widget = QWidget()

        layout = QVBoxLayout(
            widget
        )

        language_group = QGroupBox(
            self.tr("Sprache")
        )

        language_layout = QVBoxLayout(
            language_group
        )

        language_label = QLabel(
            self.tr(
                "Anzeigesprache der Anwendung:"
            )
        )

        self.language_combo = QComboBox()

        language_names = {
            "de": self.tr("Deutsch"),
            "en": self.tr("Englisch"),
            "fr": self.tr("Französisch"),
            "it": self.tr("Italienisch"),
            "rm": self.tr(
                "Rätoromanisch"
            ),
        }

        for language_code in SUPPORTED_LANGUAGES:
            self.language_combo.addItem(
                language_names[
                    language_code
                ],
                language_code,
            )

        current_language = (
            self.translation_manager
            .get_saved_language()
        )

        current_index = (
            self.language_combo
            .findData(
                current_language
            )
        )

        if current_index >= 0:
            self.language_combo.setCurrentIndex(
                current_index
            )

        self.language_combo.currentIndexChanged.connect(
            self._on_language_selection_changed
        )

        language_hint = QLabel(
            self.tr(
                "Die neue Sprache wird beim "
                "nächsten Programmstart "
                "verwendet."
            )
        )

        language_hint.setWordWrap(
            True
        )

        language_layout.addWidget(
            language_label
        )

        language_layout.addWidget(
            self.language_combo
        )

        language_layout.addWidget(
            language_hint
        )

        layout.addWidget(
            language_group
        )

        layout.addStretch()

        return widget

    def _on_language_selection_changed(
        self,
        index: int,
    ):
        language_code = (
            self.language_combo
            .itemData(
                index
            )
        )

        if language_code is None:
            return

        self._change_language(
            str(language_code)
        )

    def _open_person_from_search(
        self,
        person_id: str,
    ):
        self.tabs.setCurrentWidget(
            self.people_tab
        )

        self.people_tab.select_person(
            person_id
        )

    def _open_course_from_search(
        self,
        course_id: str,
    ):
        self.tabs.setCurrentWidget(
            self.courses_tab
        )

        self.courses_tab.select_course(
            course_id
        )

    def _open_location_from_search(
        self,
        location_id: str,
    ):
        self.tabs.setCurrentWidget(
            self.locations_tab
        )

        self.locations_tab.select_location(
            location_id
        )

    def _on_current_tab_changed(
        self,
        index: int,
    ):
        current_widget = self.tabs.widget(
            index
        )

        if current_widget is self.people_tab:
            self.people_tab.load_persons()

        elif current_widget is self.courses_tab:
            self.courses_tab.load_courses()

        elif current_widget is self.course_days_tab:
            self.course_days_tab.load_course_days()

        elif current_widget is self.locations_tab:
            self.locations_tab.load_locations()

        elif current_widget is self.assignments_tab:
            self.assignments_tab.load_data()

        elif current_widget is self.search_tab:
            self.search_tab.refresh()

        elif (
            self.users_tab is not None
            and current_widget is self.users_tab
        ):
            self.users_tab.load_users()

    def _change_language(
        self,
        language_code: str,
    ):
        saved_language = (
            self.translation_manager
            .get_saved_language()
        )

        if language_code == saved_language:
            return

        TranslationManager.save_language(
            language_code
        )

        QMessageBox.information(
            self,
            self.tr(
                "Sprache geändert"
            ),
            self.tr(
                "Die Spracheinstellung "
                "wurde gespeichert.\n\n"
                "Die neue Sprache wird "
                "beim nächsten "
                "Programmstart verwendet."
            ),
        )
