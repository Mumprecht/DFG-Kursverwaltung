from datetime import datetime
from pathlib import Path

from PySide6.QtWidgets import (
    QCheckBox,
    QFileDialog,
    QGroupBox,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from dfg_kursverwaltung.services.export_service import (
    ExportService,
)


class ExportWidget(QWidget):
    def __init__(
        self,
        export_service: ExportService,
        parent: QWidget | None = None,
    ):
        super().__init__(parent)

        self.export_service = export_service

        self._create_ui()

    def _create_ui(self):
        main_layout = QVBoxLayout(self)

        title = QLabel(
            self.tr("Export")
        )

        title.setStyleSheet(
            "font-size: 22px; "
            "font-weight: bold;"
        )

        main_layout.addWidget(
            title
        )

        description = QLabel(
            self.tr(
                "Exportieren Sie Daten "
                "als CSV-Dateien."
            )
        )

        main_layout.addWidget(
            description
        )

        # -----------------------------------------------------
        # Personenexport
        # -----------------------------------------------------

        person_group = QGroupBox(
            self.tr("Personenexport")
        )

        person_group_layout = QVBoxLayout(
            person_group
        )

        self.include_inactive_persons_checkbox = (
            QCheckBox(
                self.tr(
                    "Inaktive Personen einschliessen"
                )
            )
        )

        self.include_inactive_persons_checkbox.setChecked(
            True
        )

        self.export_persons_button = QPushButton(
            self.tr(
                "Personen als CSV exportieren"
            )
        )

        self.export_persons_button.clicked.connect(
            self._export_persons
        )

        person_group_layout.addWidget(
            self.include_inactive_persons_checkbox
        )

        person_group_layout.addWidget(
            self.export_persons_button
        )

        main_layout.addWidget(
            person_group
        )

        # -----------------------------------------------------
        # Ausführungsorte
        # -----------------------------------------------------

        location_group = QGroupBox(
            self.tr(
                "Ausführungsorte-Export"
            )
        )

        location_group_layout = QVBoxLayout(
            location_group
        )

        self.include_inactive_locations_checkbox = (
            QCheckBox(
                self.tr(
                    "Deaktivierte Ausführungsorte "
                    "einschliessen"
                )
            )
        )

        self.include_inactive_locations_checkbox.setChecked(
            True
        )

        self.export_locations_button = QPushButton(
            self.tr(
                "Ausführungsorte als CSV exportieren"
            )
        )

        self.export_locations_button.clicked.connect(
            self._export_locations
        )

        location_group_layout.addWidget(
            self.include_inactive_locations_checkbox
        )

        location_group_layout.addWidget(
            self.export_locations_button
        )

        main_layout.addWidget(
            location_group
        )

        # -----------------------------------------------------
        # Lehrgänge
        # -----------------------------------------------------

        course_group = QGroupBox(
            self.tr(
                "Lehrgänge-Export"
            )
        )

        course_group_layout = QVBoxLayout(
            course_group
        )

        self.export_courses_button = QPushButton(
            self.tr(
                "Lehrgänge als CSV exportieren"
            )
        )

        self.export_courses_button.clicked.connect(
            self._export_courses
        )

        course_group_layout.addWidget(
            self.export_courses_button
        )

        main_layout.addWidget(
            course_group
        )

        # -----------------------------------------------------
        # Kurstage
        # -----------------------------------------------------

        course_day_group = QGroupBox(
            self.tr(
                "Kurstage-Export"
            )
        )

        course_day_group_layout = QVBoxLayout(
            course_day_group
        )

        self.export_course_days_button = QPushButton(
            self.tr(
                "Kurstage als CSV exportieren"
            )
        )

        self.export_course_days_button.clicked.connect(
            self._export_course_days
        )

        course_day_group_layout.addWidget(
            self.export_course_days_button
        )

        main_layout.addWidget(
            course_day_group
        )

        main_layout.addStretch()

    def _export_persons(self):
        timestamp = datetime.now().strftime(
            "%Y-%m-%d_%H%M"
        )

        default_name = (
            f"DFG-Personen_{timestamp}.csv"
        )

        file_path, _selected_filter = (
            QFileDialog.getSaveFileName(
                self,
                self.tr(
                    "Personendaten exportieren"
                ),
                str(
                    Path.home()
                    / "Downloads"
                    / default_name
                ),
                self.tr(
                    "CSV-Dateien (*.csv)"
                ),
            )
        )

        if not file_path:
            return

        if not file_path.lower().endswith(
            ".csv"
        ):
            file_path += ".csv"

        include_inactive = (
            self.include_inactive_persons_checkbox
            .isChecked()
        )

        try:
            count = (
                self.export_service
                .export_persons_csv(
                    file_path,
                    include_inactive=(
                        include_inactive
                    ),
                )
            )

        except Exception as exc:
            QMessageBox.critical(
                self,
                self.tr("Fehler"),
                self.tr(
                    "Der Personenexport konnte "
                    "nicht erstellt werden."
                )
                + "\n\n"
                + str(exc),
            )
            return

        QMessageBox.information(
            self,
            self.tr(
                "Export abgeschlossen"
            ),
            self.tr(
                "%1 Personen wurden "
                "erfolgreich exportiert."
            ).replace(
                "%1",
                str(count),
            )
            + "\n\n"
            + file_path,
        )

    def _export_locations(self):
        timestamp = datetime.now().strftime(
            "%Y-%m-%d_%H%M"
        )

        default_name = (
            f"DFG-Ausfuehrungsorte_{timestamp}.csv"
        )

        file_path, _selected_filter = (
            QFileDialog.getSaveFileName(
                self,
                self.tr(
                    "Ausführungsorte exportieren"
                ),
                str(
                    Path.home()
                    / "Downloads"
                    / default_name
                ),
                self.tr(
                    "CSV-Dateien (*.csv)"
                ),
            )
        )

        if not file_path:
            return

        if not file_path.lower().endswith(
            ".csv"
        ):
            file_path += ".csv"

        include_inactive = (
            self.include_inactive_locations_checkbox
            .isChecked()
        )

        try:
            count = (
                self.export_service
                .export_locations_csv(
                    file_path,
                    include_inactive=(
                        include_inactive
                    ),
                )
            )

        except Exception as exc:
            QMessageBox.critical(
                self,
                self.tr("Fehler"),
                self.tr(
                    "Der Export der "
                    "Ausführungsorte konnte "
                    "nicht erstellt werden."
                )
                + "\n\n"
                + str(exc),
            )
            return

        QMessageBox.information(
            self,
            self.tr(
                "Export abgeschlossen"
            ),
            self.tr(
                "%1 Ausführungsorte wurden "
                "erfolgreich exportiert."
            ).replace(
                "%1",
                str(count),
            )
            + "\n\n"
            + file_path,
        )

    def _export_courses(self):
        timestamp = datetime.now().strftime(
            "%Y-%m-%d_%H%M"
        )

        default_name = (
            f"DFG-Lehrgaenge_{timestamp}.csv"
        )

        file_path, _selected_filter = (
            QFileDialog.getSaveFileName(
                self,
                self.tr(
                    "Lehrgänge exportieren"
                ),
                str(
                    Path.home()
                    / "Downloads"
                    / default_name
                ),
                self.tr(
                    "CSV-Dateien (*.csv)"
                ),
            )
        )

        if not file_path:
            return

        if not file_path.lower().endswith(
            ".csv"
        ):
            file_path += ".csv"

        try:
            count = (
                self.export_service
                .export_courses_csv(
                    file_path
                )
            )

        except Exception as exc:
            QMessageBox.critical(
                self,
                self.tr("Fehler"),
                self.tr(
                    "Der Export der Lehrgänge "
                    "konnte nicht erstellt werden."
                )
                + "\n\n"
                + str(exc),
            )
            return

        QMessageBox.information(
            self,
            self.tr(
                "Export abgeschlossen"
            ),
            self.tr(
                "%1 Lehrgänge wurden "
                "erfolgreich exportiert."
            ).replace(
                "%1",
                str(count),
            )
            + "\n\n"
            + file_path,
        )

    def _export_course_days(self):
        timestamp = datetime.now().strftime(
            "%Y-%m-%d_%H%M"
        )

        default_name = (
            f"DFG-Kurstage_{timestamp}.csv"
        )

        file_path, _selected_filter = (
            QFileDialog.getSaveFileName(
                self,
                self.tr(
                    "Kurstage exportieren"
                ),
                str(
                    Path.home()
                    / "Downloads"
                    / default_name
                ),
                self.tr(
                    "CSV-Dateien (*.csv)"
                ),
            )
        )

        if not file_path:
            return

        if not file_path.lower().endswith(
            ".csv"
        ):
            file_path += ".csv"

        try:
            count = (
                self.export_service
                .export_course_days_csv(
                    file_path
                )
            )

        except Exception as exc:
            QMessageBox.critical(
                self,
                self.tr("Fehler"),
                self.tr(
                    "Der Export der Kurstage "
                    "konnte nicht erstellt werden."
                )
                + "\n\n"
                + str(exc),
            )
            return

        QMessageBox.information(
            self,
            self.tr(
                "Export abgeschlossen"
            ),
            self.tr(
                "%1 Kurstage wurden "
                "erfolgreich exportiert."
            ).replace(
                "%1",
                str(count),
            )
            + "\n\n"
            + file_path,
        )