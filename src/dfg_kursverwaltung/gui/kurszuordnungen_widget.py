from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QHBoxLayout,
    QLabel,
    QAbstractItemView,
    QHeaderView,
    QTableWidget,
    QTableWidgetItem,
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
    User,
)
from dfg_kursverwaltung.core.permissions import (
    Permission,
    has_permission,
)
from dfg_kursverwaltung.gui.kurszuordnung_dialog import (
    KurszuordnungDialog,
)
from dfg_kursverwaltung.gui.pruefungsergebnis_dialog import (
    PruefungsergebnisDialog,
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
from dfg_kursverwaltung.services.pruefungsergebnisse_service import (
    ExamResultService,
)
from dfg_kursverwaltung.services.standorte_service import (
    LocationService,
)


class KurszuordnungenWidget(QWidget):
    EXAM_COURSE_TYPE_ID = "course-type-exam"

    def __init__(
        self,
        person_service: PersonService,
        course_service: CourseService,
        course_day_service: CourseDayService,
        assignment_service: CourseAssignmentService,
        exam_result_service: ExamResultService,
        location_service: LocationService,
        authenticated_user: User,
        parent: QWidget | None = None,
    ):
        super().__init__(parent)

        self.person_service = person_service
        self.course_service = course_service
        self.course_day_service = course_day_service
        self.assignment_service = assignment_service
        self.exam_result_service = exam_result_service
        self.location_service = location_service
        self.authenticated_user = authenticated_user

        self.can_write_assignment = has_permission(
            authenticated_user,
            Permission.ASSIGNMENT_WRITE,
        )

        self.can_write_exam_result = has_permission(
            authenticated_user,
            Permission.EXAM_RESULT_WRITE,
        )

        self.current_assignment_id: str | None = None

        self._create_ui()
        self.load_data()

    def _can_modify_assignment(
        self,
        assignment: CourseAssignment,
    ) -> bool:
        if not self.can_write_assignment:
            return False

        return True

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

        self.exam_summary = QLabel()
        self.exam_summary.setWordWrap(
            True
        )
        self.exam_summary.setStyleSheet(
            "padding: 6px; "
            "font-weight: bold; "
            "background-color: #EAF4FB; "
            "border: 1px solid #B8DDF5;"
        )
        self.exam_summary.setVisible(
            False
        )

        main_layout.addWidget(
            self.exam_summary
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

        self.assignment_list = QTableWidget()

        self.assignment_list.setColumnCount(
            5
        )

        self.assignment_list.setHorizontalHeaderLabels(
            [
                self.tr("Name Vorname"),
                self.tr("Rolle"),
                self.tr("Status"),
                self.tr("Ergebnis"),
                self.tr("Note"),
            ]
        )

        self.assignment_list.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )

        self.assignment_list.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )

        self.assignment_list.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )

        self.assignment_list.setAlternatingRowColors(
            True
        )

        self.assignment_list.setStyleSheet(
            """
            QTableWidget::item:selected {
                background-color: #B8DDF5;
                color: black;
            }
            """
        )

        self.assignment_list.verticalHeader().setVisible(
            False
        )

        header = (
            self.assignment_list.horizontalHeader()
        )

        for column in range(5):
            header.setSectionResizeMode(
                column,
                QHeaderView.ResizeMode.Interactive,
            )

        self.assignment_list.setColumnWidth(
            0,
            360,
        )

        self.assignment_list.setColumnWidth(
            1,
            140,
        )

        self.assignment_list.setColumnWidth(
            2,
            180,
        )

        self.assignment_list.setColumnWidth(
            3,
            180,
        )

        self.assignment_list.setColumnWidth(
            4,
            90,
        )

        header.setStretchLastSection(
            True
        )

        self.assignment_list.itemSelectionChanged.connect(
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

        self.exam_result_button = QPushButton(
            self.tr("Prüfungsergebnis")
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

        self.exam_result_button.clicked.connect(
            self._edit_exam_result
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
        button_layout.addWidget(
            self.exam_result_button
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
        self.assignment_list.setRowCount(
            0
        )

        self.exam_summary.clear()
        self.exam_summary.setVisible(
            False
        )

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

        course_id = (
            self.course_combo.currentData()
        )

        course = None

        if course_id:
            course = (
                self.course_service.get_course(
                    course_id
                )
            )

        is_exam = (
            course is not None
            and course.lehrgangstyp_id
            == self.EXAM_COURSE_TYPE_ID
        )

        rows = []

        participant_count = 0
        registered_count = 0
        attended_count = 0
        absent_count = 0
        cancelled_count = 0

        passed_count = 0
        failed_count = 0
        without_result_count = 0

        for assignment in assignments:
            person = (
                self.person_service.get_person(
                    assignment.person_id
                )
            )

            if person is None:
                name_text = self.tr(
                    "Unbekannte Person"
                )

                sort_key = (
                    "\uffff",
                    "\uffff",
                )

            else:
                name_text = (
                    f"{person.nachname} "
                    f"{person.vorname}"
                )

                sort_key = (
                    person.nachname.casefold(),
                    person.vorname.casefold(),
                )

            result_text = ""
            note_text = ""

            if (
                assignment.rolle
                == CourseAssignmentRole.PARTICIPANT
            ):
                participant_count += 1

                if (
                    assignment.status
                    == CourseAssignmentStatus.REGISTERED
                ):
                    registered_count += 1

                elif (
                    assignment.status
                    == CourseAssignmentStatus.ATTENDED
                ):
                    attended_count += 1

                elif (
                    assignment.status
                    == CourseAssignmentStatus.ABSENT
                ):
                    absent_count += 1

                elif (
                    assignment.status
                    == CourseAssignmentStatus.CANCELLED
                ):
                    cancelled_count += 1

            if (
                is_exam
                and assignment.rolle
                == CourseAssignmentRole.PARTICIPANT
            ):
                exam_result = (
                    self.exam_result_service
                    .get_exam_result_for_assignment(
                        assignment.id
                    )
                )

                if exam_result is None:
                    without_result_count += 1

                else:
                    if exam_result.bestanden:
                        result_text = self.tr(
                            "Bestanden"
                        )
                        passed_count += 1

                    else:
                        result_text = self.tr(
                            "Nicht bestanden"
                        )
                        failed_count += 1

                    note_text = (
                        exam_result.note or ""
                    )

            rows.append(
                (
                    sort_key,
                    assignment,
                    name_text,
                    result_text,
                    note_text,
                )
            )

        rows.sort(
            key=lambda row: row[0]
        )

        if is_exam:
            summary_parts = [
                (
                    f"{self.tr('Teilnehmer')}: "
                    f"{participant_count}"
                ),
                (
                    f"{self.tr('Angemeldet')}: "
                    f"{registered_count}"
                ),
                (
                    f"{self.tr('Teilgenommen')}: "
                    f"{attended_count}"
                ),
                (
                    f"{self.tr('Nicht erschienen')}: "
                    f"{absent_count}"
                ),
                (
                    f"{self.tr('Abgemeldet')}: "
                    f"{cancelled_count}"
                ),
                (
                    f"{self.tr('Bestanden')}: "
                    f"{passed_count}"
                ),
                (
                    f"{self.tr('Nicht bestanden')}: "
                    f"{failed_count}"
                ),
                (
                    f"{self.tr('Ohne Ergebnis')}: "
                    f"{without_result_count}"
                ),
            ]

            self.exam_summary.setText(
                "   |   ".join(
                    summary_parts
                )
            )

            self.exam_summary.setVisible(
                True
            )

        self.assignment_list.setRowCount(
            len(rows)
        )

        for table_row, row_data in enumerate(
            rows
        ):
            (
                _sort_key,
                assignment,
                name_text,
                result_text,
                note_text,
            ) = row_data

            values = [
                name_text,
                self._role_text(
                    assignment.rolle
                ),
                self._status_text(
                    assignment.status
                ),
                result_text,
                note_text,
            ]

            for column, value in enumerate(
                values
            ):
                item = QTableWidgetItem(
                    value
                )

                if column == 0:
                    item.setData(
                        Qt.ItemDataRole.UserRole,
                        assignment.id,
                    )

                self.assignment_list.setItem(
                    table_row,
                    column,
                    item,
                )

        self._update_buttons()

    def _assignment_selected(self):
        row = (
            self.assignment_list.currentRow()
        )

        if row < 0:
            self.current_assignment_id = None
            self.notes_value.clear()
            self._update_buttons()
            return

        item = self.assignment_list.item(
            row,
            0,
        )

        if item is None:
            self.current_assignment_id = None
            self.notes_value.clear()
            self._update_buttons()
            return

        assignment_id = item.data(
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
        item: QTableWidgetItem,
    ):
        row = item.row()

        id_item = self.assignment_list.item(
            row,
            0,
        )

        if id_item is None:
            return

        assignment_id = id_item.data(
            Qt.ItemDataRole.UserRole
        )

        if not assignment_id:
            return

        self.current_assignment_id = (
            assignment_id
        )

        self._edit_assignment()

    def _add_assignment(self):
        if not self.can_write_assignment:
            return

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
                    actor=self.authenticated_user,
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
        if not self.can_write_assignment:
            return

        if self.current_assignment_id is None:
            return

        assignment = (
            self.assignment_service.get_assignment(
                self.current_assignment_id
            )
        )

        if assignment is None:
            return


        if not self._can_modify_assignment(
            assignment
        ):
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
                    self.authenticated_user,
                    assignment,
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
        if not self.can_write_assignment:
            return

        if self.current_assignment_id is None:
            return

        assignment = (
            self.assignment_service.get_assignment(
                self.current_assignment_id
            )
        )

        if assignment is None:
            return


        if not self._can_modify_assignment(
            assignment
        ):
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
                self.authenticated_user,
                assignment.id,
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
            self.assignment_list.rowCount()
        ):
            item = self.assignment_list.item(
                row,
                0,
            )

            if item is None:
                continue

            if (
                item.data(
                    Qt.ItemDataRole.UserRole
                )
                == assignment_id
            ):
                self.assignment_list.selectRow(
                    row
                )

                self.assignment_list.setCurrentCell(
                    row,
                    0,
                )

                return

    def _edit_exam_result(self):
        if not self.can_write_exam_result:
            return

        if self.current_assignment_id is None:
            return

        assignment = (
            self.assignment_service.get_assignment(
                self.current_assignment_id
            )
        )

        if assignment is None:
            return


        if (
            assignment.rolle
            != CourseAssignmentRole.PARTICIPANT
        ):
            QMessageBox.information(
                self,
                self.tr(
                    "Kein Prüfungsergebnis"
                ),
                self.tr(
                    "Ein Prüfungsergebnis kann "
                    "nur für Teilnehmer erfasst "
                    "werden."
                ),
            )
            return

        course_id = (
            self.course_combo.currentData()
        )

        if not course_id:
            return

        course = (
            self.course_service.get_course(
                course_id
            )
        )

        if (
            course is None
            or course.lehrgangstyp_id
            != self.EXAM_COURSE_TYPE_ID
        ):
            QMessageBox.information(
                self,
                self.tr(
                    "Kein Prüfungstermin"
                ),
                self.tr(
                    "Für diesen Lehrgang kann "
                    "kein Prüfungsergebnis "
                    "erfasst werden."
                ),
            )
            return

        exam_result = (
            self.exam_result_service
            .get_exam_result_for_assignment(
                assignment.id
            )
        )

        dialog = PruefungsergebnisDialog(
            exam_result=exam_result,
            parent=self,
        )

        if (
            dialog.exec()
            != QDialog.DialogCode.Accepted
        ):
            return

        data = dialog.get_data()

        try:
            if data["bestanden"] is None:
                if exam_result is not None:
                    self.exam_result_service.delete_exam_result(
                        self.authenticated_user,
                        exam_result.id,
                    )

            elif exam_result is None:
                self.exam_result_service.create_exam_result(
                    actor=self.authenticated_user,
                    kurszuordnung_id=assignment.id,
                    bestanden=data["bestanden"],
                    note=data["note"],
                    bemerkungen=data["bemerkungen"],
                )

            else:
                exam_result.bestanden = data[
                    "bestanden"
                ]
                exam_result.note = data[
                    "note"
                ]
                exam_result.bemerkungen = data[
                    "bemerkungen"
                ]

                self.exam_result_service.update_exam_result(
                    self.authenticated_user,
                    exam_result,
                )

        except Exception as exc:
            QMessageBox.critical(
                self,
                self.tr("Fehler"),
                self.tr(
                    "Das Prüfungsergebnis konnte "
                    "nicht gespeichert werden."
                )
                + "\n\n"
                + str(exc),
            )
            return

        self._load_assignments()

    def _update_buttons(self):
        course_day_id = (
            self.course_day_combo.currentData()
        )

        has_course_day = (
            course_day_id is not None
        )

        has_assignment = (
            self.current_assignment_id
            is not None
        )

        assignment = None

        if has_assignment:
            assignment = (
                self.assignment_service
                .get_assignment(
                    self.current_assignment_id
                )
            )

        can_add_assignment = (
            self.can_write_assignment
            and has_course_day
        )

        can_edit_assignment = (
            self.can_write_assignment
            and assignment is not None
        )

        self.add_button.setEnabled(
            can_add_assignment
        )
        self.edit_button.setEnabled(
            can_edit_assignment
        )
        self.remove_button.setEnabled(
            can_edit_assignment
        )

        can_edit_exam_result = False

        if assignment is not None:
            course_id = (
                self.course_combo.currentData()
            )

            course = None

            if course_id:
                course = (
                    self.course_service
                    .get_course(
                        course_id
                    )
                )

            can_edit_exam_result = (
                self.can_write_exam_result
                and assignment.rolle
                == CourseAssignmentRole.PARTICIPANT
                and assignment.status
                == CourseAssignmentStatus.ATTENDED
                and course is not None
                and course.lehrgangstyp_id
                == self.EXAM_COURSE_TYPE_ID
            )

        self.exam_result_button.setEnabled(
            can_edit_exam_result
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
