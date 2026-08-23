from datetime import date

from PySide6.QtCore import QDate, QTime
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDateEdit,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QTimeEdit,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from dfg_kursverwaltung.core.models import (
    CourseDay,
    Location,
)
from dfg_kursverwaltung.services.standorte_service import (
    LocationService,
)


class KurstagDialog(QDialog):
    def __init__(
        self,
        location_service: LocationService,
        course_day: CourseDay | None = None,
        parent: QWidget | None = None,
    ):
        super().__init__(parent)

        self.location_service = location_service
        self.course_day = course_day

        self.setModal(True)
        self.resize(520, 550)

        self._create_ui()
        self._load_locations()

        if self.course_day is not None:
            self._load_course_day()

    def _create_ui(self):
        if self.course_day is None:
            self.setWindowTitle(
                self.tr("Neuer Kurstag")
            )
        else:
            self.setWindowTitle(
                self.tr("Kurstag bearbeiten")
            )

        main_layout = QVBoxLayout(self)

        title = QLabel(
            self.windowTitle()
        )

        title.setStyleSheet(
            "font-size: 20px; "
            "font-weight: bold;"
        )

        main_layout.addWidget(title)

        form = QFormLayout()

        self.date_edit = QDateEdit()

        self.date_edit.setCalendarPopup(
            True
        )

        self.date_edit.setDisplayFormat(
            "dd.MM.yyyy"
        )

        self.date_edit.setDate(
            QDate.currentDate()
        )

        self.start_time_edit = QTimeEdit()

        self.start_time_edit.setDisplayFormat(
            "HH:mm"
        )

        self.start_time_edit.setTime(
            QTime(8, 30)
        )

        self.end_time_edit = QTimeEdit()

        self.end_time_edit.setDisplayFormat(
            "HH:mm"
        )

        self.end_time_edit.setTime(
            QTime(17, 0)
        )

        self.use_times_checkbox = QCheckBox(
            self.tr("Beginn und Ende verwenden")
        )

        self.use_times_checkbox.setChecked(
            True
        )

        self.use_times_checkbox.toggled.connect(
            self._update_time_fields
        )

        self.location_combo = QComboBox()

        self.name_edit = QLineEdit()

        self.name_edit.setPlaceholderText(
            self.tr(
                "Optionale Bezeichnung des Kurstags"
            )
        )

        self.notes_edit = QTextEdit()

        self.notes_edit.setMinimumHeight(
            100
        )

        form.addRow(
            self.tr("Datum:"),
            self.date_edit,
        )

        form.addRow(
            "",
            self.use_times_checkbox,
        )

        form.addRow(
            self.tr("Beginn:"),
            self.start_time_edit,
        )

        form.addRow(
            self.tr("Ende:"),
            self.end_time_edit,
        )

        form.addRow(
            self.tr("Ausführungsort:"),
            self.location_combo,
        )

        form.addRow(
            self.tr("Bezeichnung:"),
            self.name_edit,
        )

        form.addRow(
            self.tr("Bemerkungen:"),
            self.notes_edit,
        )

        main_layout.addLayout(form)
        main_layout.addStretch()

        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save
            | QDialogButtonBox.StandardButton.Cancel
        )

        self.button_box.button(
            QDialogButtonBox.StandardButton.Save
        ).setText(
            self.tr("Speichern")
        )

        self.button_box.button(
            QDialogButtonBox.StandardButton.Cancel
        ).setText(
            self.tr("Abbrechen")
        )

        self.button_box.accepted.connect(
            self._validate_and_accept
        )

        self.button_box.rejected.connect(
            self.reject
        )

        main_layout.addWidget(
            self.button_box
        )

        self._update_time_fields(
            True
        )

    def _load_locations(self):
        self.location_combo.clear()

        self.location_combo.addItem(
            self.tr("Kein Ausführungsort"),
            None,
        )

        locations = (
            self.location_service
            .list_locations()
        )

        existing_location_id = None

        if self.course_day is not None:
            existing_location_id = (
                self.course_day.standort_id
            )

        existing_location_found = False

        for location in locations:
            self._add_location(
                location
            )

            if (
                location.id
                == existing_location_id
            ):
                existing_location_found = True

        # Ein bereits verwendeter Standort muss auch
        # dann sichtbar bleiben, wenn er inzwischen
        # deaktiviert wurde.
        if (
            existing_location_id
            and not existing_location_found
        ):
            location = (
                self.location_service
                .get_location(
                    existing_location_id
                )
            )

            if location is not None:
                self._add_location(
                    location,
                    inactive=True,
                )

    def _add_location(
        self,
        location: Location,
        inactive: bool = False,
    ):
        text = location.bezeichnung

        if location.ort:
            text += (
                f" ({location.ort})"
            )

        if inactive:
            text += (
                " "
                + self.tr("[deaktiviert]")
            )

        self.location_combo.addItem(
            text,
            location.id,
        )

    def _load_course_day(self):
        if self.course_day is None:
            return

        value = self.course_day.datum

        self.date_edit.setDate(
            QDate(
                value.year,
                value.month,
                value.day,
            )
        )

        has_times = (
            self.course_day.beginn is not None
            or self.course_day.ende is not None
        )

        self.use_times_checkbox.setChecked(
            has_times
        )

        if self.course_day.beginn:
            hour, minute = (
                self.course_day.beginn.split(":")
            )

            self.start_time_edit.setTime(
                QTime(
                    int(hour),
                    int(minute),
                )
            )

        if self.course_day.ende:
            hour, minute = (
                self.course_day.ende.split(":")
            )

            self.end_time_edit.setTime(
                QTime(
                    int(hour),
                    int(minute),
                )
            )

        if self.course_day.standort_id:
            index = (
                self.location_combo.findData(
                    self.course_day.standort_id
                )
            )

            if index >= 0:
                self.location_combo.setCurrentIndex(
                    index
                )

        self.name_edit.setText(
            self.course_day.bezeichnung or ""
        )

        self.notes_edit.setPlainText(
            self.course_day.bemerkungen or ""
        )

        self._update_time_fields(
            has_times
        )

    def _update_time_fields(
        self,
        enabled: bool,
    ):
        self.start_time_edit.setEnabled(
            enabled
        )

        self.end_time_edit.setEnabled(
            enabled
        )

    def _validate_and_accept(self):
        if self.use_times_checkbox.isChecked():
            start_time = (
                self.start_time_edit.time()
            )

            end_time = (
                self.end_time_edit.time()
            )

            if end_time <= start_time:
                QMessageBox.warning(
                    self,
                    self.tr(
                        "Ungültige Zeit"
                    ),
                    self.tr(
                        "Das Ende muss nach "
                        "dem Beginn liegen."
                    ),
                )
                return

        self.accept()

    def get_data(self) -> dict:
        qdate = self.date_edit.date()

        datum = date(
            qdate.year(),
            qdate.month(),
            qdate.day(),
        )

        if self.use_times_checkbox.isChecked():
            beginn = (
                self.start_time_edit
                .time()
                .toString("HH:mm")
            )

            ende = (
                self.end_time_edit
                .time()
                .toString("HH:mm")
            )
        else:
            beginn = None
            ende = None

        return {
            "datum": datum,
            "beginn": beginn,
            "ende": ende,
            "standort_id": (
                self.location_combo.currentData()
            ),
            "bezeichnung": (
                self._optional_text(
                    self.name_edit.text()
                )
            ),
            "bemerkungen": (
                self._optional_text(
                    self.notes_edit.toPlainText()
                )
            ),
        }

    @staticmethod
    def _optional_text(
        value: str,
    ) -> str | None:
        value = value.strip()

        return value or None