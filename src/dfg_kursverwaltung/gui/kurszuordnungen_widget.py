from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from dfg_kursverwaltung.core.models import (
    CourseAssignment,
    CourseAssignmentRole,
    CourseAssignmentStatus,
    CourseDay,
)
from dfg_kursverwaltung.gui.kurszuordnung_dialog import (
    KurszuordnungDialog,
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


class KurszuordnungenWidget(QWidget):
    def __init__(
        self,
        person_service: PersonService,
        course_service: CourseService,
        course_day_service: CourseDayService,
        assignment_service: CourseAssignmentService,
        location_service: LocationService,
        parent: QWidget | None = None,
    ):
        super().__init__(parent)

        self.person_service = person_service
        self.course_service = course_service
        self.course_day_service = course_day_service
        self.assignment_service = assignment_service
        self.location_service = location_service

        self.current_assignment_id: str | None = None

        self._create_ui()
        self.load_data()

    def _create_ui(self):
        main_layout = QVBoxLayout(self)

        title = QLabel(
            self.tr("Kurszuordnung")
        )
        title.setStyleSheet(
            "font-size: 22px; "
            "font-weight: bold;"
        )

        main_layout.addWidget(title)

        selection_layout = QHBoxLayout()

        selection_layout.addWidget(
            QLabel(self.tr("Lehrgang:"))
        )

        self.course_combo = QComboBox()
        self.course_combo.currentIndexChanged.connect(
            self._course_changed
        )

        selection_layout.addWidget(
            self.course_combo,
            1,
        )

        selection_layout.addWidget(
            QLabel(self.tr("Kurstag:"))
        )

        self.course_day_combo = QComboBox()
        self.course_day_combo.currentIndexChanged.connect(
            self._course_day_changed
        )

        selection_layout.addWidget(
            self.course_day_combo,
            2,
        )

        main_layout.addLayout(
            selection_layout
        )

        self.course_day_info = QLabel("-")
        self.course_day_info.setWordWrap(True)

        main_layout.addWidget(
            self.course_day_info
        )

        assignments_title = QLabel(
            self.tr("Zugeordnete Personen")
        )
        assignments_title.setStyleSheet(
            "font-size: 17px; "
            "font-weight: bold;"
        )

        main_layout.addWidget(
            assignments_title
        )

        self.assignment_list = QListWidget()
        self.assignment_list.currentItemChanged.connect(
            self._assignment_selected
        )
        self.assignment_list.itemDoubleClicked.connect(
            self._assignment_double_clicked
        )

        main_layout.addWidget(
            self.assignment_list
        )

        button_layout = QHBoxLayout()

        self.add_button = QPushButton(
            self.tr("Hinzufügen")
        )
        self.edit_button = QPushButton(
            self.tr("Bearbeiten")
        )
        self.remove_button = QPushButton(
            self.tr("Entfernen")
        )

        self.add_button.clicked.connect(
            self._add_assignment
        )
        self.edit_button.clicked.connect(
            self._edit_assignment
        )
        self.remove_button.clicked.connect(
            self._remove_assignment
        )

        button_layout.addWidget(
            self.add_button
        )
        button_layout.addWidget(
            self.edit_button
        )
        button_layout.addWidget(
            self.remove_button
        )
        button_layout.addStretch()

        main_layout.addLayout(
            button_layout
        )

        notes_title = QLabel(
            self.tr("Bemerkungen zur Zuordnung")
        )

        main_layout.addWidget(
            notes_title
        )

        self.notes_value = QTextEdit()
        self.notes_value.setReadOnly(True)
        self.notes_value.setMaximumHeight(100)

        main_layout.addWidget(
            self.notes_value
        )

        self._update_buttons()

    def load_data(
        self,
        *_args,
    ):
        selected_course_id = (
            self.course_combo.currentData()
        )

        self.course_combo.blockSignals(True)
        self.course_combo.clear()

        courses = self.course_service.list_courses()

        selected_index = -1

        for course in courses:
            self.course_combo.addItem(
                course.bezeichnung,
                course.id,
            )

            if course.id == selected_course_id:
                selected_index = (
                    self.course_combo.count() - 1
                )

        self.course_combo.blockSignals(False)

        if self.course_combo.count() == 0:
            self.course_day_combo.clear()
            self._load_assignments()
            return

        if selected_index >= 0:
            self.course_combo.setCurrentIndex(
                selected_index
            )
        else:
            self.course_combo.setCurrentIndex(0)

        self._load_course_days()

    def _course_changed(
        self,
        _index: int,
    ):
        self._load_course_days()

    def _load_course_days(self):
        course_id = (
            self.course_combo.currentData()
        )

        self.course_day_combo.blockSignals(True)
        self.course_day_combo.clear()

        if course_id:
            course_days = (
                self.course_day_service
                .list_course_days(
                    course_id
                )
            )

            for course_day in course_days:
                self.course_day_combo.addItem(
                    self._course_day_text(
                        course_day
                    ),
                    course_day.id,
                )

        self.course_day_combo.blockSignals(False)

        if self.course_day_combo.count() > 0:
            self.course_day_combo.setCurrentIndex(0)

        self._course_day_changed(
            self.course_day_combo.currentIndex()
        )

    def _course_day_changed(
        self,
        _index: int,
    ):
        self.current_assignment_id = None

        self._show_course_day_info()
        self._load_assignments()

    def _show_course_day_info(self):
        course_day_id = (
            self.course_day_combo.currentData()
        )

        if not course_day_id:
            self.course_day_info.setText(
                self.tr(
                    "Für diesen Lehrgang sind "
                    "keine Kurstage vorhanden."
                )
            )
            return

        course_day = (
            self.course_day_service.get_course_day(
                course_day_id
            )
        )

        if course_day is None:
            self.course_day_info.setText("-")
            return

        parts = [
            course_day.datum.strftime(
                "%d.%m.%Y"
            )
        ]

        if (
            course_day.beginn
            and course_day.ende
        ):
            parts.append(
                f"{course_day.beginn}"
                f"–{course_day.ende}"
            )

        if course_day.bezeichnung:
            parts.append(
                course_day.bezeichnung
            )

        if course_day.standort_id:
            location = (
                self.location_service.get_location(
                    course_day.standort_id
                )
            )

            if location is not None:
                parts.append(
                    location.bezeichnung
                )

        self.course_day_info.setText(
            " | ".join(parts)
        )

    def _load_assignments(self):
        self.assignment_list.clear()
        self.notes_value.clear()

        self.current_assignment_id = None

        course_day_id = (
            self.course_day_combo.currentData()
        )

        if not course_day_id:
            self._update_buttons()
            return

        assignments = (
            self.assignment_service
            .list_assignments_for_course_day(
                course_day_id
            )
        )

        for assignment in assignments:
            person = (
                self.person_service.get_person(
                    assignment.person_id
                )
            )

            if person is None:
                person_text = self.tr(
                    "Unbekannte Person"
                )
            else:
                person_text = person.voller_name

            item = QListWidgetItem(
                f"{person_text}   |   "
                f"{self._role_text(assignment.rolle)}"
                f"   |   "
                f"{self._status_text(assignment.status)}"
            )

            item.setData(
                Qt.ItemDataRole.UserRole,
                assignment.id,
            )

            self.assignment_list.addItem(
                item
            )

        self._update_buttons()

    def _assignment_selected(
        self,
        current: QListWidgetItem | None,
        _previous: QListWidgetItem | None,
    ):
        if current is None:
            self.current_assignment_id = None
            self.notes_value.clear()
            self._update_buttons()
            return

        assignment_id = current.data(
            Qt.ItemDataRole.UserRole
        )

        if not assignment_id:
            self.current_assignment_id = None
            self.notes_value.clear()
            self._update_buttons()
            return

        self.current_assignment_id = (
            assignment_id
        )

        assignment = (
            self.assignment_service.get_assignment(
                assignment_id
            )
        )

        if assignment is None:
            self.notes_value.clear()
        else:
            self.notes_value.setPlainText(
                assignment.bemerkungen or ""
            )

        self._update_buttons()

    def _assignment_double_clicked(
        self,
        item: QListWidgetItem,
    ):
        assignment_id = item.data(
            Qt.ItemDataRole.UserRole
        )

        if not assignment_id:
            return

        self.current_assignment_id = (
            assignment_id
        )

        self._edit_assignment()

    def _add_assignment(self):
        course_day_id = (
            self.course_day_combo.currentData()
        )

        if not course_day_id:
            return

        persons = (
            self._available_persons(
                course_day_id
            )
        )

        if not persons:
            QMessageBox.information(
                self,
                self.tr(
                    "Keine Person verfügbar"
                ),
                self.tr(
                    "Alle aktiven Personen sind "
                    "diesem Kurstag bereits "
                    "zugeordnet."
                ),
            )
            return

        dialog = KurszuordnungDialog(
            persons=persons,
            parent=self,
        )

        if (
            dialog.exec()
            != QDialog.DialogCode.Accepted
        ):
            return

        data = dialog.get_data()

        try:
            assignment = (
                self.assignment_service
                .create_assignment(
                    person_id=data[
                        "person_id"
                    ],
                    kurstag_id=course_day_id,
                    rolle=data["rolle"],
                    status=data["status"],
                    bemerkungen=data[
                        "bemerkungen"
                    ],
                )
            )

        except Exception as exc:
            QMessageBox.critical(
                self,
                self.tr("Fehler"),
                self.tr(
                    "Die Kurszuordnung konnte "
                    "nicht gespeichert werden."
                )
                + "\n\n"
                + str(exc),
            )
            return

        self.current_assignment_id = (
            assignment.id
        )

        self._load_assignments()
        self._select_assignment(
            assignment.id
        )

    def _edit_assignment(self):
        if self.current_assignment_id is None:
            return

        assignment = (
            self.assignment_service.get_assignment(
                self.current_assignment_id
            )
        )

        if assignment is None:
            return

        person = self.person_service.get_person(
            assignment.person_id
        )

        if person is None:
            QMessageBox.warning(
                self,
                self.tr("Person nicht gefunden"),
                self.tr(
                    "Die zugeordnete Person konnte "
                    "nicht gefunden werden."
                ),
            )
            return

        dialog = KurszuordnungDialog(
            persons=[person],
            assignment=assignment,
            parent=self,
        )

        if (
            dialog.exec()
            != QDialog.DialogCode.Accepted
        ):
            return

        data = dialog.get_data()

        assignment.rolle = data["rolle"]
        assignment.status = data["status"]
        assignment.bemerkungen = data[
            "bemerkungen"
        ]

        try:
            updated_assignment = (
                self.assignment_service
                .update_assignment(
                    assignment
                )
            )

        except Exception as exc:
            QMessageBox.critical(
                self,
                self.tr("Fehler"),
                self.tr(
                    "Die Kurszuordnung konnte "
                    "nicht geändert werden."
                )
                + "\n\n"
                + str(exc),
            )
            return

        self.current_assignment_id = (
            updated_assignment.id
        )

        self._load_assignments()
        self._select_assignment(
            updated_assignment.id
        )

    def _remove_assignment(self):
        if self.current_assignment_id is None:
            return

        assignment = (
            self.assignment_service.get_assignment(
                self.current_assignment_id
            )
        )

        if assignment is None:
            return

        person = self.person_service.get_person(
            assignment.person_id
        )

        person_name = (
            person.voller_name
            if person is not None
            else self.tr("diese Person")
        )

        answer = QMessageBox.question(
            self,
            self.tr("Zuordnung entfernen"),
            self.tr(
                "Soll die Kurszuordnung von "
            )
            + person_name
            + self.tr(
                " wirklich entfernt werden?"
            ),
            QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if answer != QMessageBox.StandardButton.Yes:
            return

        try:
            self.assignment_service.delete_assignment(
                assignment.id
            )

        except Exception as exc:
            QMessageBox.critical(
                self,
                self.tr("Fehler"),
                self.tr(
                    "Die Kurszuordnung konnte "
                    "nicht entfernt werden."
                )
                + "\n\n"
                + str(exc),
            )
            return

        self.current_assignment_id = None
        self._load_assignments()

    def _available_persons(
        self,
        course_day_id: str,
    ):
        persons = (
            self.person_service.list_persons()
        )

        assignments = (
            self.assignment_service
            .list_assignments_for_course_day(
                course_day_id
            )
        )

        assigned_person_ids = {
            assignment.person_id
            for assignment in assignments
        }

        return [
            person
            for person in persons
            if person.id not in assigned_person_ids
        ]

    def _select_assignment(
        self,
        assignment_id: str,
    ):
        for row in range(
            self.assignment_list.count()
        ):
            item = self.assignment_list.item(
                row
            )

            if (
                item.data(
                    Qt.ItemDataRole.UserRole
                )
                == assignment_id
            ):
                self.assignment_list.setCurrentItem(
                    item
                )
                return

    def _update_buttons(self):
        has_course_day = (
            self.course_day_combo.currentData()
            is not None
        )

        has_assignment = (
            self.current_assignment_id
            is not None
        )

        self.add_button.setEnabled(
            has_course_day
        )
        self.edit_button.setEnabled(
            has_assignment
        )
        self.remove_button.setEnabled(
            has_assignment
        )

    def _course_day_text(
        self,
        course_day: CourseDay,
    ) -> str:
        text = course_day.datum.strftime(
            "%d.%m.%Y"
        )

        if (
            course_day.beginn
            and course_day.ende
        ):
            text += (
                f"  {course_day.beginn}"
                f"–{course_day.ende}"
            )

        if course_day.bezeichnung:
            text += (
                f"  |  {course_day.bezeichnung}"
            )

        return text

    def _role_text(
        self,
        role: CourseAssignmentRole,
    ) -> str:
        if role == CourseAssignmentRole.PARTICIPANT:
            return self.tr("Teilnehmer")

        if role == CourseAssignmentRole.INSTRUCTOR:
            return self.tr("Instruktor")

        return role.value

    def _status_text(
        self,
        status: CourseAssignmentStatus,
    ) -> str:
        if status == CourseAssignmentStatus.REGISTERED:
            return self.tr("Angemeldet")

        if status == CourseAssignmentStatus.ATTENDED:
            return self.tr("Teilgenommen")

        if status == CourseAssignmentStatus.ABSENT:
            return self.tr(
                "Nicht erschienen"
            )

        if status == CourseAssignmentStatus.CANCELLED:
            return self.tr("Abgemeldet")

        return status.value