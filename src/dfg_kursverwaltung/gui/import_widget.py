from pathlib import Path

from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from dfg_kursverwaltung.services.import_service import (
    CourseDayImportPreview,
    CourseImportPreview,
    ImportPreview,
    ImportService,
    LocationImportPreview,
)


class ImportWidget(QWidget):
    IMPORT_PERSONS = "persons"
    IMPORT_LOCATIONS = "locations"
    IMPORT_COURSES = "courses"
    IMPORT_COURSE_DAYS = "course_days"

    def __init__(
        self,
        import_service: ImportService,
        parent: QWidget | None = None,
    ):
        super().__init__(parent)

        self.import_service = import_service

        self.current_file_path: str | None = None
        self.current_preview: (
            ImportPreview
            | LocationImportPreview
            | CourseImportPreview
            | CourseDayImportPreview
            | None
        ) = None

        self._create_ui()

    def _create_ui(self):
        main_layout = QVBoxLayout(self)

        title = QLabel(
            self.tr("Import")
        )

        title.setStyleSheet(
            "font-size: 22px; "
            "font-weight: bold;"
        )

        main_layout.addWidget(
            title
        )

        self.description_label = QLabel()
        self.description_label.setWordWrap(
            True
        )

        main_layout.addWidget(
            self.description_label
        )

        # -----------------------------------------------------
        # Importart
        # -----------------------------------------------------

        type_group = QGroupBox(
            self.tr("Importart")
        )

        type_layout = QHBoxLayout(
            type_group
        )

        type_layout.addWidget(
            QLabel(
                self.tr("Daten:")
            )
        )

        self.import_type_combo = QComboBox()

        self.import_type_combo.addItem(
            self.tr("Personen"),
            self.IMPORT_PERSONS,
        )

        self.import_type_combo.addItem(
            self.tr("Ausführungsorte"),
            self.IMPORT_LOCATIONS,
        )

        self.import_type_combo.addItem(
            self.tr("Lehrgänge"),
            self.IMPORT_COURSES,
        )

        self.import_type_combo.addItem(
            self.tr("Kurstage"),
            self.IMPORT_COURSE_DAYS,
        )

        self.import_type_combo.currentIndexChanged.connect(
            self._import_type_changed
        )

        type_layout.addWidget(
            self.import_type_combo,
            1,
        )

        main_layout.addWidget(
            type_group
        )

        # -----------------------------------------------------
        # Datei
        # -----------------------------------------------------

        file_group = QGroupBox(
            self.tr("Importdatei")
        )

        file_layout = QVBoxLayout(
            file_group
        )

        path_layout = QHBoxLayout()

        self.file_label = QLabel(
            self.tr(
                "Keine Datei ausgewählt."
            )
        )

        self.file_label.setWordWrap(
            True
        )

        self.select_file_button = QPushButton(
            self.tr(
                "CSV-Datei auswählen..."
            )
        )

        self.select_file_button.clicked.connect(
            self._select_file
        )

        path_layout.addWidget(
            self.file_label,
            1,
        )

        path_layout.addWidget(
            self.select_file_button
        )

        file_layout.addLayout(
            path_layout
        )

        main_layout.addWidget(
            file_group
        )

        # -----------------------------------------------------
        # Vorschau
        # -----------------------------------------------------

        preview_group = QGroupBox(
            self.tr("Import-Vorschau")
        )

        preview_layout = QVBoxLayout(
            preview_group
        )

        summary_layout = QHBoxLayout()

        self.new_label = QLabel(
            self.tr("Neu: 0")
        )

        self.update_label = QLabel(
            self.tr(
                "Aktualisieren: 0"
            )
        )

        self.error_label = QLabel(
            self.tr("Fehler: 0")
        )

        summary_layout.addWidget(
            self.new_label
        )

        summary_layout.addWidget(
            self.update_label
        )

        summary_layout.addWidget(
            self.error_label
        )

        summary_layout.addStretch()

        preview_layout.addLayout(
            summary_layout
        )

        # -----------------------------------------------------
        # Vorschau-Tabelle
        # -----------------------------------------------------

        self.preview_table = QTableWidget(
            0,
            5,
        )

        self.preview_table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )

        self.preview_table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )

        self.preview_table.horizontalHeader().setStretchLastSection(
            True
        )

        preview_layout.addWidget(
            self.preview_table
        )

        # -----------------------------------------------------
        # Fehler
        # -----------------------------------------------------

        preview_layout.addWidget(
            QLabel(
                self.tr(
                    "Fehlerhafte Datensätze:"
                )
            )
        )

        self.issues_table = QTableWidget(
            0,
            2,
        )

        self.issues_table.setHorizontalHeaderLabels(
            [
                self.tr("Zeile"),
                self.tr("Fehler"),
            ]
        )

        self.issues_table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )

        self.issues_table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )

        self.issues_table.horizontalHeader().setStretchLastSection(
            True
        )

        preview_layout.addWidget(
            self.issues_table
        )

        main_layout.addWidget(
            preview_group,
            1,
        )

        # -----------------------------------------------------
        # Import
        # -----------------------------------------------------

        action_layout = QHBoxLayout()
        action_layout.addStretch()

        self.import_button = QPushButton(
            self.tr("Importieren")
        )

        self.import_button.setEnabled(
            False
        )

        self.import_button.clicked.connect(
            self._import_data
        )

        action_layout.addWidget(
            self.import_button
        )

        main_layout.addLayout(
            action_layout
        )

        self._update_import_type_ui()

    # =========================================================
    # Importart
    # =========================================================

    def _current_import_type(
        self,
    ) -> str:
        return (
            self.import_type_combo
            .currentData()
        )

    def _import_type_changed(
        self,
        _index: int,
    ):
        self._reset_preview()
        self._update_import_type_ui()

    def _update_import_type_ui(self):
        import_type = (
            self._current_import_type()
        )

        if import_type == self.IMPORT_PERSONS:
            self.description_label.setText(
                self.tr(
                    "Importieren Sie Personendaten "
                    "aus einer DFG-CSV-Datei. "
                    "Vor dem Import werden die Daten "
                    "zuerst geprüft."
                )
            )

            headers = [
                self.tr("Zeile"),
                self.tr("Aktion"),
                self.tr("Vorname"),
                self.tr("Nachname"),
                self.tr("ID"),
            ]

        elif import_type == self.IMPORT_LOCATIONS:
            self.description_label.setText(
                self.tr(
                    "Importieren Sie Ausführungsorte "
                    "aus einer DFG-CSV-Datei. "
                    "Vor dem Import werden die Daten "
                    "zuerst geprüft."
                )
            )

            headers = [
                self.tr("Zeile"),
                self.tr("Aktion"),
                self.tr("Bezeichnung"),
                self.tr("Ort"),
                self.tr("ID"),
            ]

        elif import_type == self.IMPORT_COURSES:
            self.description_label.setText(
                self.tr(
                    "Importieren Sie Lehrgänge "
                    "aus einer DFG-CSV-Datei. "
                    "Vor dem Import werden die Daten "
                    "zuerst geprüft."
                )
            )

            headers = [
                self.tr("Zeile"),
                self.tr("Aktion"),
                self.tr("Typ"),
                self.tr("Bezeichnung"),
                self.tr("ID"),
            ]

        else:
            self.description_label.setText(
                self.tr(
                    "Importieren Sie Kurstage "
                    "aus einer DFG-CSV-Datei. "
                    "Vor dem Import werden die Daten "
                    "zuerst geprüft."
                )
            )

            headers = [
                self.tr("Zeile"),
                self.tr("Aktion"),
                self.tr("Datum"),
                self.tr("Lehrgang"),
                self.tr("ID"),
            ]

        self.preview_table.setHorizontalHeaderLabels(
            headers
        )

    # =========================================================
    # Datei auswählen / Vorschau
    # =========================================================

    def _select_file(self):
        # Für das aktuelle Projekt liegen die Test-Exporte
        # direkt im Projektverzeichnis. Der Dateidialog selbst
        # bleibt ansonsten vollständig frei navigierbar.
        default_directory = Path.cwd()

        import_type = (
            self._current_import_type()
        )

        if import_type == self.IMPORT_PERSONS:
            dialog_title = self.tr(
                "Personendaten importieren"
            )

        elif import_type == self.IMPORT_LOCATIONS:
            dialog_title = self.tr(
                "Ausführungsorte importieren"
            )

        elif import_type == self.IMPORT_COURSES:
            dialog_title = self.tr(
                "Lehrgänge importieren"
            )

        else:
            dialog_title = self.tr(
                "Kurstage importieren"
            )

        file_path, _selected_filter = (
            QFileDialog.getOpenFileName(
                self,
                dialog_title,
                str(default_directory),
                self.tr(
                    "CSV-Dateien (*.csv)"
                ),
            )
        )

        if not file_path:
            return

        self._load_preview(
            file_path
        )

    def _load_preview(
        self,
        file_path: str,
    ):
        self._reset_preview()

        import_type = (
            self._current_import_type()
        )

        try:
            if import_type == self.IMPORT_PERSONS:
                preview = (
                    self.import_service
                    .preview_person_import(
                        file_path
                    )
                )

            elif import_type == self.IMPORT_LOCATIONS:
                preview = (
                    self.import_service
                    .preview_location_import(
                        file_path
                    )
                )

            elif import_type == self.IMPORT_COURSES:
                preview = (
                    self.import_service
                    .preview_course_import(
                        file_path
                    )
                )

            else:
                preview = (
                    self.import_service
                    .preview_course_day_import(
                        file_path
                    )
                )

        except Exception as exc:
            QMessageBox.critical(
                self,
                self.tr("Fehler"),
                self.tr(
                    "Die Importdatei konnte "
                    "nicht geprüft werden."
                )
                + "\n\n"
                + str(exc),
            )
            return

        self.current_file_path = (
            file_path
        )

        self.current_preview = (
            preview
        )

        self.file_label.setText(
            file_path
        )

        self._show_preview(
            preview
        )

    # =========================================================
    # Vorschau anzeigen
    # =========================================================

    def _show_preview(
        self,
        preview: (
            ImportPreview
            | LocationImportPreview
            | CourseImportPreview
            | CourseDayImportPreview
        ),
    ):
        self.new_label.setText(
            self.tr("Neu: %1").replace(
                "%1",
                str(
                    preview.new_count
                ),
            )
        )

        self.update_label.setText(
            self.tr(
                "Aktualisieren: %1"
            ).replace(
                "%1",
                str(
                    preview.update_count
                ),
            )
        )

        self.error_label.setText(
            self.tr(
                "Fehler: %1"
            ).replace(
                "%1",
                str(
                    preview.error_count
                ),
            )
        )

        self.preview_table.setRowCount(
            len(
                preview.rows
            )
        )

        import_type = (
            self._current_import_type()
        )

        for table_row, row in enumerate(
            preview.rows
        ):
            if row.action == "create":
                action_text = self.tr(
                    "Neu"
                )
            else:
                action_text = self.tr(
                    "Aktualisieren"
                )

            if import_type == self.IMPORT_PERSONS:
                values = [
                    str(
                        row.row_number
                    ),
                    action_text,
                    row.vorname,
                    row.nachname,
                    row.person_id or "",
                ]

            elif import_type == self.IMPORT_LOCATIONS:
                values = [
                    str(
                        row.row_number
                    ),
                    action_text,
                    row.bezeichnung,
                    row.ort or "",
                    row.location_id or "",
                ]

            elif import_type == self.IMPORT_COURSES:
                values = [
                    str(
                        row.row_number
                    ),
                    action_text,
                    row.lehrgangstyp_bezeichnung,
                    row.bezeichnung,
                    row.course_id or "",
                ]

            else:
                values = [
                    str(
                        row.row_number
                    ),
                    action_text,
                    row.datum.isoformat(),
                    row.course_name or row.course_id,
                    row.course_day_id or "",
                ]

            for column, value in enumerate(
                values
            ):
                self.preview_table.setItem(
                    table_row,
                    column,
                    QTableWidgetItem(
                        value
                    ),
                )

        self.preview_table.resizeColumnsToContents()

        self.issues_table.setRowCount(
            len(
                preview.issues
            )
        )

        for table_row, issue in enumerate(
            preview.issues
        ):
            self.issues_table.setItem(
                table_row,
                0,
                QTableWidgetItem(
                    str(
                        issue.row_number
                    )
                ),
            )

            self.issues_table.setItem(
                table_row,
                1,
                QTableWidgetItem(
                    issue.message
                ),
            )

        self.issues_table.resizeColumnsToContents()

        self.import_button.setEnabled(
            bool(
                preview.rows
            )
        )

    # =========================================================
    # Import
    # =========================================================

    def _import_data(self):
        if self.current_preview is None:
            return

        preview = self.current_preview

        if not preview.rows:
            QMessageBox.information(
                self,
                self.tr("Import"),
                self.tr(
                    "Es sind keine gültigen "
                    "Datensätze zum Importieren "
                    "vorhanden."
                ),
            )
            return

        import_type = (
            self._current_import_type()
        )

        if import_type == self.IMPORT_PERSONS:
            object_name = self.tr(
                "Personen"
            )

        elif import_type == self.IMPORT_LOCATIONS:
            object_name = self.tr(
                "Ausführungsorte"
            )

        elif import_type == self.IMPORT_COURSES:
            object_name = self.tr(
                "Lehrgänge"
            )

        else:
            object_name = self.tr(
                "Kurstage"
            )

        message = (
            self.tr(
                "Der Import wird jetzt "
                "durchgeführt."
            )
            + "\n\n"
            + self.tr(
                "Datenart: %1"
            ).replace(
                "%1",
                object_name,
            )
            + "\n"
            + self.tr(
                "Neu: %1"
            ).replace(
                "%1",
                str(
                    preview.new_count
                ),
            )
            + "\n"
            + self.tr(
                "Zu aktualisieren: %1"
            ).replace(
                "%1",
                str(
                    preview.update_count
                ),
            )
        )

        if preview.error_count:
            message += (
                "\n"
                + self.tr(
                    "Fehlerhafte Datensätze "
                    "werden übersprungen: %1"
                ).replace(
                    "%1",
                    str(
                        preview.error_count
                    ),
                )
            )

        message += (
            "\n\n"
            + self.tr(
                "Möchten Sie fortfahren?"
            )
        )

        answer = QMessageBox.question(
            self,
            self.tr(
                "Import bestätigen"
            ),
            message,
            QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if (
            answer
            != QMessageBox.StandardButton.Yes
        ):
            return

        try:
            if import_type == self.IMPORT_PERSONS:
                (
                    created_count,
                    updated_count,
                ) = (
                    self.import_service
                    .import_persons(
                        preview
                    )
                )

            elif import_type == self.IMPORT_LOCATIONS:
                (
                    created_count,
                    updated_count,
                ) = (
                    self.import_service
                    .import_locations(
                        preview
                    )
                )

            elif import_type == self.IMPORT_COURSES:
                (
                    created_count,
                    updated_count,
                ) = (
                    self.import_service
                    .import_courses(
                        preview
                    )
                )

            else:
                (
                    created_count,
                    updated_count,
                ) = (
                    self.import_service
                    .import_course_days(
                        preview
                    )
                )

        except Exception as exc:
            QMessageBox.critical(
                self,
                self.tr("Fehler"),
                self.tr(
                    "Der Import konnte nicht "
                    "vollständig durchgeführt "
                    "werden."
                )
                + "\n\n"
                + str(exc),
            )
            return

        QMessageBox.information(
            self,
            self.tr(
                "Import abgeschlossen"
            ),
            self.tr(
                "Der Import wurde erfolgreich "
                "abgeschlossen."
            )
            + "\n\n"
            + self.tr(
                "Neu angelegt: %1"
            ).replace(
                "%1",
                str(
                    created_count
                ),
            )
            + "\n"
            + self.tr(
                "Aktualisiert: %1"
            ).replace(
                "%1",
                str(
                    updated_count
                ),
            ),
        )

        if self.current_file_path:
            self._load_preview(
                self.current_file_path
            )

    # =========================================================
    # Zurücksetzen
    # =========================================================

    def _reset_preview(self):
        self.current_file_path = None
        self.current_preview = None

        self.file_label.setText(
            self.tr(
                "Keine Datei ausgewählt."
            )
        )

        self.new_label.setText(
            self.tr("Neu: 0")
        )

        self.update_label.setText(
            self.tr(
                "Aktualisieren: 0"
            )
        )

        self.error_label.setText(
            self.tr("Fehler: 0")
        )

        self.preview_table.setRowCount(
            0
        )

        self.issues_table.setRowCount(
            0
        )

        self.import_button.setEnabled(
            False
        )