from datetime import date

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QDialog,
    QFormLayout,
    QHeaderView,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from dfg_kursverwaltung.core.models import (
    Drone,
    Person,
    PhoneNumber,
    PhoneNumberType,
    User,
)
from dfg_kursverwaltung.core.permissions import (
    Permission,
    has_permission,
)
from dfg_kursverwaltung.gui.drohne_dialog import (
    DroneDialog,
)
from dfg_kursverwaltung.gui.person_dialog import (
    PersonDialog,
)
from dfg_kursverwaltung.gui.telefonnummer_dialog import (
    PhoneNumberDialog,
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
from dfg_kursverwaltung.services.lehrgangstypen_service import (
    CourseTypeService,
)
from dfg_kursverwaltung.services.personen_service import (
    PersonService,
)
from dfg_kursverwaltung.services.pruefungsergebnisse_service import (
    ExamResultService,
)
from dfg_kursverwaltung.services.telefonnummern_service import (
    PhoneNumberService,
)


class PersonenWidget(QWidget):
    def __init__(
        self,
        person_service: PersonService,
        phone_number_service: PhoneNumberService,
        drone_service: DroneService,
        course_service: CourseService,
        course_type_service: CourseTypeService,
        course_day_service: CourseDayService,
        assignment_service: CourseAssignmentService,
        exam_result_service: ExamResultService,
        authenticated_user: User,
        parent: QWidget | None = None,
    ):
        super().__init__(parent)

        self.person_service = person_service
        self.phone_number_service = phone_number_service
        self.drone_service = drone_service
        self.course_service = course_service
        self.course_type_service = course_type_service
        self.course_day_service = course_day_service
        self.assignment_service = assignment_service
        self.exam_result_service = exam_result_service
        self.authenticated_user = authenticated_user
        self.can_write = has_permission(
            authenticated_user,
            Permission.PERSON_WRITE,
        )

        self.current_person_id: str | None = None
        self.current_phone_number_id: str | None = None
        self.current_drone_id: str | None = None

        self._create_ui()
        self.load_persons()

    def _create_ui(self):
        main_layout = QVBoxLayout(self)

        title = QLabel(
            self.tr("Personen")
        )

        title.setStyleSheet(
            "font-size: 22px; font-weight: bold;"
        )

        main_layout.addWidget(title)

        splitter = QSplitter(
            Qt.Orientation.Horizontal
        )

        splitter.addWidget(
            self._create_list_area()
        )

        splitter.addWidget(
            self._create_detail_area()
        )

        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 3)

        main_layout.addWidget(splitter)

    def _create_list_area(
        self,
    ) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)

        self.search_edit = QLineEdit()

        self.search_edit.setPlaceholderText(
            self.tr("Person suchen...")
        )

        self.search_edit.setClearButtonEnabled(
            True
        )

        self.search_edit.textChanged.connect(
            self._search_changed
        )

        self.member_filter_checkbox = QCheckBox(
            self.tr("DFG-Mitglied")
        )

        self.participant_filter_checkbox = QCheckBox(
            self.tr("Teilnehmer")
        )

        self.instructor_filter_checkbox = QCheckBox(
            self.tr("Instruktor")
        )

        self.member_filter_checkbox.toggled.connect(
            self.load_persons
        )

        self.participant_filter_checkbox.toggled.connect(
            self.load_persons
        )

        self.instructor_filter_checkbox.toggled.connect(
            self.load_persons
        )

        self.person_list = QListWidget()

        self.person_list.currentItemChanged.connect(
            self._person_selected
        )

        self.show_inactive_checkbox = QCheckBox(
            self.tr(
                "Inaktive Personen anzeigen"
            )
        )

        self.show_inactive_checkbox.toggled.connect(
            self.load_persons
        )

        button_layout = QHBoxLayout()

        self.new_button = QPushButton(
            self.tr("Neu")
        )

        self.edit_button = QPushButton(
            self.tr("Bearbeiten")
        )

        self.active_button = QPushButton(
            self.tr("Deaktivieren")
        )

        self.new_button.setEnabled(
            self.can_write
        )

        self.new_button.clicked.connect(
            self._new_person
        )

        self.edit_button.clicked.connect(
            self._edit_person
        )

        self.active_button.clicked.connect(
            self._toggle_active_status
        )

        button_layout.addWidget(
            self.new_button
        )

        button_layout.addWidget(
            self.edit_button
        )

        button_layout.addWidget(
            self.active_button
        )

        layout.addWidget(
            self.search_edit
        )

        filter_label = QLabel(
            self.tr("Filter:")
        )

        layout.addWidget(
            filter_label
        )

        filter_layout = QHBoxLayout()

        filter_layout.addWidget(
            self.member_filter_checkbox
        )

        filter_layout.addWidget(
            self.participant_filter_checkbox
        )

        filter_layout.addWidget(
            self.instructor_filter_checkbox
        )

        filter_layout.addStretch()

        layout.addLayout(
            filter_layout
        )

        layout.addWidget(
            self.person_list
        )

        layout.addWidget(
            self.show_inactive_checkbox
        )

        layout.addLayout(
            button_layout
        )

        return widget

    def _create_detail_area(
        self,
    ) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)

        self.detail_title = QLabel(
            self.tr("Personendetails")
        )

        self.detail_title.setStyleSheet(
            "font-size: 18px; "
            "font-weight: bold;"
        )

        layout.addWidget(
            self.detail_title
        )

        master_data_group = QGroupBox(
            self.tr("Stammdaten")
        )

        form = QFormLayout(
            master_data_group
        )

        self.name_value = QLabel("-")
        self.birthdate_value = QLabel("-")
        self.email_value = QLabel("-")
        self.address_value = QLabel("-")
        self.location_value = QLabel("-")
        self.organisation_value = QLabel("-")
        self.member_value = QLabel("-")
        self.participant_value = QLabel("-")
        self.instructor_value = QLabel("-")
        self.active_value = QLabel("-")

        form.addRow(
            self.tr("Name:"),
            self.name_value,
        )

        form.addRow(
            self.tr("Geburtsdatum:"),
            self.birthdate_value,
        )

        form.addRow(
            self.tr("E-Mail:"),
            self.email_value,
        )

        form.addRow(
            self.tr("Adresse:"),
            self.address_value,
        )

        form.addRow(
            self.tr("PLZ / Ort:"),
            self.location_value,
        )

        form.addRow(
            self.tr(
                "Organisation / Firma:"
            ),
            self.organisation_value,
        )

        form.addRow(
            self.tr("DFG-Mitglied:"),
            self.member_value,
        )

        form.addRow(
            self.tr("Teilnehmer:"),
            self.participant_value,
        )

        form.addRow(
            self.tr("Instruktor:"),
            self.instructor_value,
        )

        form.addRow(
            self.tr("Aktiv:"),
            self.active_value,
        )

        layout.addWidget(
            master_data_group
        )

        notes_group = QGroupBox(
            self.tr("Bemerkungen")
        )

        notes_layout = QVBoxLayout(
            notes_group
        )

        self.notes_value = QTextEdit()
        self.notes_value.setReadOnly(True)
        self.notes_value.setMaximumHeight(90)

        notes_layout.addWidget(
            self.notes_value
        )

        layout.addWidget(
            notes_group
        )

        course_group = QGroupBox(
            self.tr("Kursteilnahmen")
        )

        course_layout = QVBoxLayout(
            course_group
        )

        self.course_participation_list = (
            QTableWidget()
        )

        self.course_participation_list.setColumnCount(
            7
        )

        self.course_participation_list.setHorizontalHeaderLabels(
            [
                self.tr("Datum"),
                self.tr("Lehrgang"),
                self.tr("Typ"),
                self.tr("Rolle"),
                self.tr("Status"),
                self.tr("Ergebnis"),
                self.tr("Note"),
            ]
        )

        self.course_participation_list.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )

        self.course_participation_list.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )

        self.course_participation_list.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )

        self.course_participation_list.setAlternatingRowColors(
            True
        )

        self.course_participation_list.verticalHeader().setVisible(
            False
        )

        self.course_participation_list.setStyleSheet(
            """
            QTableWidget::item:selected {
                background-color: #B8DDF5;
                color: black;
            }
            """
        )

        header = (
            self.course_participation_list.horizontalHeader()
        )

        for column in range(7):
            header.setSectionResizeMode(
                column,
                QHeaderView.ResizeMode.Interactive,
            )

        self.course_participation_list.setColumnWidth(
            0,
            110,
        )
        self.course_participation_list.setColumnWidth(
            1,
            220,
        )
        self.course_participation_list.setColumnWidth(
            2,
            150,
        )
        self.course_participation_list.setColumnWidth(
            3,
            120,
        )
        self.course_participation_list.setColumnWidth(
            4,
            140,
        )
        self.course_participation_list.setColumnWidth(
            5,
            150,
        )
        self.course_participation_list.setColumnWidth(
            6,
            70,
        )

        header.setStretchLastSection(
            True
        )

        self.course_participation_list.setMinimumHeight(
            180
        )

        self.course_participation_list.setMaximumHeight(
            240
        )

        course_layout.addWidget(
            self.course_participation_list
        )

        layout.addWidget(
            course_group
        )

        phone_group = QGroupBox(
            self.tr("Telefonnummern")
        )

        phone_layout = QVBoxLayout(
            phone_group
        )

        self.phone_list = QListWidget()

        self.phone_list.setMaximumHeight(
            130
        )

        self.phone_list.currentItemChanged.connect(
            self._phone_number_selected
        )

        self.phone_list.itemDoubleClicked.connect(
            self._phone_number_double_clicked
        )

        phone_layout.addWidget(
            self.phone_list
        )

        phone_button_layout = QHBoxLayout()

        self.phone_add_button = QPushButton(
            self.tr("Hinzufügen")
        )

        self.phone_edit_button = QPushButton(
            self.tr("Bearbeiten")
        )

        self.phone_delete_button = QPushButton(
            self.tr("Löschen")
        )

        self.phone_add_button.clicked.connect(
            self._add_phone_number
        )

        self.phone_edit_button.clicked.connect(
            self._edit_phone_number
        )

        self.phone_delete_button.clicked.connect(
            self._delete_phone_number
        )

        phone_button_layout.addWidget(
            self.phone_add_button
        )

        phone_button_layout.addWidget(
            self.phone_edit_button
        )

        phone_button_layout.addWidget(
            self.phone_delete_button
        )

        phone_button_layout.addStretch()

        phone_layout.addLayout(
            phone_button_layout
        )

        layout.addWidget(
            phone_group
        )

        drone_group = QGroupBox(
            self.tr("Drohnen")
        )

        drone_layout = QVBoxLayout(
            drone_group
        )

        self.drone_list = QListWidget()

        self.drone_list.setMaximumHeight(
            130
        )

        self.drone_list.currentItemChanged.connect(
            self._drone_selected
        )

        self.drone_list.itemDoubleClicked.connect(
            self._drone_double_clicked
        )

        drone_layout.addWidget(
            self.drone_list
        )

        drone_button_layout = QHBoxLayout()

        self.drone_add_button = QPushButton(
            self.tr("Hinzufügen")
        )

        self.drone_edit_button = QPushButton(
            self.tr("Bearbeiten")
        )

        self.drone_delete_button = QPushButton(
            self.tr("Löschen")
        )

        self.drone_add_button.clicked.connect(
            self._add_drone
        )

        self.drone_edit_button.clicked.connect(
            self._edit_drone
        )

        self.drone_delete_button.clicked.connect(
            self._delete_drone
        )

        drone_button_layout.addWidget(
            self.drone_add_button
        )

        drone_button_layout.addWidget(
            self.drone_edit_button
        )

        drone_button_layout.addWidget(
            self.drone_delete_button
        )

        drone_button_layout.addStretch()

        drone_layout.addLayout(
            drone_button_layout
        )

        layout.addWidget(
            drone_group
        )

        layout.addStretch()

        self._clear_details()

        return widget

    def load_persons(
        self,
        *_args,
    ):
        search_text = (
            self.search_edit.text().strip()
        )

        include_inactive = (
            self.show_inactive_checkbox.isChecked()
        )

        if search_text:
            persons = (
                self.person_service.search_persons(
                    search_text,
                    include_inactive=include_inactive,
                )
            )
        else:
            persons = (
                self.person_service.list_persons(
                    include_inactive=include_inactive,
                )
            )

        if self.member_filter_checkbox.isChecked():
            persons = [
                person
                for person in persons
                if person.mitglied
            ]

        if self.participant_filter_checkbox.isChecked():
            persons = [
                person
                for person in persons
                if person.ist_teilnehmer
            ]

        if self.instructor_filter_checkbox.isChecked():
            persons = [
                person
                for person in persons
                if person.ist_instruktor
            ]

        selected_id = self.current_person_id

        self.person_list.blockSignals(True)
        self.person_list.clear()

        item_to_select = None

        for person in persons:
            item = QListWidgetItem(
                self._person_list_text(
                    person
                )
            )

            item.setData(
                Qt.ItemDataRole.UserRole,
                person.id,
            )

            if not person.aktiv:
                font = item.font()
                font.setItalic(True)
                item.setFont(font)

            self.person_list.addItem(
                item
            )

            if person.id == selected_id:
                item_to_select = item

        self.person_list.blockSignals(False)

        if item_to_select is not None:
            self.person_list.setCurrentItem(
                item_to_select
            )

        elif self.person_list.count() > 0:
            self.person_list.setCurrentRow(0)

        else:
            self.current_person_id = None
            self._clear_details()

    def select_person(
        self,
        person_id: str,
    ):
        person = self.person_service.get_person(
            person_id
        )

        if person is None:
            return

        self.current_person_id = person_id

        # Eine bestehende Suche kann verhindern,
        # dass die gewünschte Person sichtbar ist.
        self.search_edit.blockSignals(True)
        self.search_edit.clear()
        self.search_edit.blockSignals(False)

        # Bei einer direkten Navigation muss auch
        # eine inaktive Person sichtbar gemacht werden.
        if (
            not person.aktiv
            and not self.show_inactive_checkbox.isChecked()
        ):
            self.show_inactive_checkbox.blockSignals(
                True
            )

            self.show_inactive_checkbox.setChecked(
                True
            )

            self.show_inactive_checkbox.blockSignals(
                False
            )

        self.load_persons()

    def _search_changed(
        self,
        _text: str,
    ):
        self.load_persons()

    def _person_selected(
        self,
        current: QListWidgetItem | None,
        _previous: QListWidgetItem | None,
    ):
        if current is None:
            self.current_person_id = None
            self._clear_details()
            return

        person_id = current.data(
            Qt.ItemDataRole.UserRole
        )

        person = self.person_service.get_person(
            person_id
        )

        if person is None:
            self.current_person_id = None
            self._clear_details()
            return

        self.current_person_id = person.id
        self.current_phone_number_id = None
        self.current_drone_id = None

        self._show_person(
            person
        )

    def _show_person(
        self,
        person: Person,
    ):
        self.name_value.setText(
            person.voller_name
        )

        self.birthdate_value.setText(
            self._format_date(
                person.geburtsdatum
            )
        )

        self.email_value.setText(
            person.email or "-"
        )

        address_parts = [
            value
            for value in (
                person.strasse,
                person.hausnummer,
            )
            if value
        ]

        self.address_value.setText(
            " ".join(address_parts)
            if address_parts
            else "-"
        )

        location_parts = [
            value
            for value in (
                person.plz,
                person.ort,
            )
            if value
        ]

        self.location_value.setText(
            " ".join(location_parts)
            if location_parts
            else "-"
        )

        self.organisation_value.setText(
            person.organisation or "-"
        )

        self.member_value.setText(
            self.tr("Ja")
            if person.mitglied
            else self.tr("Nein")
        )

        self.participant_value.setText(
            self.tr("Ja")
            if person.ist_teilnehmer
            else self.tr("Nein")
        )

        self.instructor_value.setText(
            self.tr("Ja")
            if person.ist_instruktor
            else self.tr("Nein")
        )

        self.active_value.setText(
            self.tr("Ja")
            if person.aktiv
            else self.tr("Nein")
        )

        self.notes_value.setPlainText(
            person.bemerkungen or ""
        )

        self.edit_button.setEnabled(
            self.can_write
        )
        self.active_button.setEnabled(
            self.can_write
        )
        self.phone_add_button.setEnabled(
            self.can_write
        )
        self.drone_add_button.setEnabled(
            self.can_write
        )

        if person.aktiv:
            self.active_button.setText(
                self.tr("Deaktivieren")
            )
        else:
            self.active_button.setText(
                self.tr("Aktivieren")
            )

        self._load_course_participations()
        self._load_phone_numbers()
        self._load_drones()

    def _load_course_participations(self):
        self.course_participation_list.setRowCount(
            0
        )

        if self.current_person_id is None:
            return

        assignments = (
            self.assignment_service
            .list_assignments_for_person(
                self.current_person_id
            )
        )

        entries = []

        for assignment in assignments:
            course_day = (
                self.course_day_service
                .get_course_day(
                    assignment.kurstag_id
                )
            )

            if course_day is None:
                continue

            course = (
                self.course_service.get_course(
                    course_day.lehrgang_id
                )
            )

            if course is None:
                course_name = self.tr(
                    "Unbekannter Lehrgang"
                )
                course_type_name = ""
            else:
                course_name = course.bezeichnung

                course_type = (
                    self.course_type_service
                    .get_course_type(
                        course.lehrgangstyp_id
                    )
                )

                if course_type is None:
                    course_type_name = ""
                else:
                    course_type_name = (
                        course_type.bezeichnung
                    )

            exam_result = (
                self.exam_result_service
                .get_exam_result_for_assignment(
                    assignment.id
                )
            )

            result_text = ""
            note_text = ""

            if exam_result is not None:
                if exam_result.bestanden:
                    result_text = self.tr(
                        "Bestanden"
                    )
                else:
                    result_text = self.tr(
                        "Nicht bestanden"
                    )

                note_text = (
                    exam_result.note or ""
                )

            entries.append(
                (
                    course_day.datum,
                    course_name,
                    course_type_name,
                    assignment,
                    result_text,
                    note_text,
                )
            )

        entries.sort(
            key=lambda entry: entry[0],
            reverse=True,
        )

        self.course_participation_list.setRowCount(
            len(entries)
        )

        for table_row, entry in enumerate(
            entries
        ):
            (
                course_date,
                course_name,
                course_type_name,
                assignment,
                result_text,
                note_text,
            ) = entry

            role_text = (
                self._assignment_role_text(
                    assignment.rolle.value
                )
            )

            status_text = (
                self._assignment_status_text(
                    assignment.status.value
                )
            )

            values = [
                course_date.strftime(
                    "%d.%m.%Y"
                ),
                course_name,
                course_type_name,
                role_text,
                status_text,
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

                self.course_participation_list.setItem(
                    table_row,
                    column,
                    item,
                )

    def _load_phone_numbers(self):
        self.phone_list.clear()
        self.current_phone_number_id = None

        self.phone_edit_button.setEnabled(
            False
        )

        self.phone_delete_button.setEnabled(
            False
        )

        if self.current_person_id is None:
            return

        phone_numbers = (
            self.phone_number_service
            .list_phone_numbers(
                self.current_person_id
            )
        )

        if not phone_numbers:
            item = QListWidgetItem(
                self.tr(
                    "Noch keine Telefonnummern vorhanden."
                )
            )

            item.setFlags(
                item.flags()
                & ~Qt.ItemFlag.ItemIsSelectable
            )

            self.phone_list.addItem(
                item
            )

            return

        for phone_number in phone_numbers:
            item = QListWidgetItem(
                self._phone_number_text(
                    phone_number
                )
            )

            item.setData(
                Qt.ItemDataRole.UserRole,
                phone_number.id,
            )

            self.phone_list.addItem(
                item
            )

    def _phone_number_selected(
        self,
        current: QListWidgetItem | None,
        _previous: QListWidgetItem | None,
    ):
        phone_number_id = (
            current.data(
                Qt.ItemDataRole.UserRole
            )
            if current is not None
            else None
        )

        self.current_phone_number_id = (
            phone_number_id
        )

        enabled = (
            self.can_write
            and bool(phone_number_id)
        )

        self.phone_edit_button.setEnabled(
            enabled
        )

        self.phone_delete_button.setEnabled(
            enabled
        )

    def _phone_number_double_clicked(
        self,
        item: QListWidgetItem,
    ):
        phone_number_id = item.data(
            Qt.ItemDataRole.UserRole
        )

        if not phone_number_id:
            return

        self.current_phone_number_id = (
            phone_number_id
        )

        self._edit_phone_number()

    def _add_phone_number(self):
        if not self.can_write:
            return

        if self.current_person_id is None:
            return

        dialog = PhoneNumberDialog(
            parent=self
        )

        if (
            dialog.exec()
            != QDialog.DialogCode.Accepted
        ):
            return

        data = dialog.get_data()

        try:
            phone_number = (
                self.phone_number_service
                .create_phone_number(
                    person_id=self.current_person_id,
                    **data,
                )
            )

        except Exception as exc:
            QMessageBox.critical(
                self,
                self.tr("Fehler"),
                self.tr(
                    "Die Telefonnummer konnte "
                    "nicht gespeichert werden."
                )
                + "\n\n"
                + str(exc),
            )
            return

        self._load_phone_numbers()

        self._select_phone_number(
            phone_number.id
        )

    def _edit_phone_number(self):
        if not self.can_write:
            return

        if self.current_phone_number_id is None:
            return

        phone_number = (
            self.phone_number_service
            .get_phone_number(
                self.current_phone_number_id
            )
        )

        if phone_number is None:
            return

        dialog = PhoneNumberDialog(
            phone_number=phone_number,
            parent=self,
        )

        if (
            dialog.exec()
            != QDialog.DialogCode.Accepted
        ):
            return

        data = dialog.get_data()

        try:
            updated = (
                self.phone_number_service
                .update_phone_number(
                    phone_number,
                    typ=data["typ"],
                    nummer=data["nummer"],
                    ist_primaer=data[
                        "ist_primaer"
                    ],
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
                    "Die Telefonnummer konnte "
                    "nicht geändert werden."
                )
                + "\n\n"
                + str(exc),
            )
            return

        self._load_phone_numbers()

        self._select_phone_number(
            updated.id
        )

    def _delete_phone_number(self):
        if not self.can_write:
            return

        if self.current_phone_number_id is None:
            return

        phone_number = (
            self.phone_number_service
            .get_phone_number(
                self.current_phone_number_id
            )
        )

        if phone_number is None:
            return

        number_text = (
            self.phone_number_service
            .format_for_display(
                phone_number.nummer_e164
            )
        )

        answer = QMessageBox.question(
            self,
            self.tr(
                "Telefonnummer löschen"
            ),
            self.tr(
                "Soll die Telefonnummer "
            )
            + number_text
            + self.tr(
                " wirklich gelöscht werden?"
            ),
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
            self.phone_number_service.delete_phone_number(
                phone_number.id
            )

        except Exception as exc:
            QMessageBox.critical(
                self,
                self.tr("Fehler"),
                str(exc),
            )
            return

        self._load_phone_numbers()

    def _select_phone_number(
        self,
        phone_number_id: str,
    ):
        for row in range(
            self.phone_list.count()
        ):
            item = self.phone_list.item(
                row
            )

            if (
                item.data(
                    Qt.ItemDataRole.UserRole
                )
                == phone_number_id
            ):
                self.phone_list.setCurrentItem(
                    item
                )
                return

    def _load_drones(self):
        self.drone_list.clear()
        self.current_drone_id = None

        self.drone_edit_button.setEnabled(
            False
        )

        self.drone_delete_button.setEnabled(
            False
        )

        if self.current_person_id is None:
            return

        drones = (
            self.drone_service.list_drones(
                self.current_person_id
            )
        )

        if not drones:
            item = QListWidgetItem(
                self.tr(
                    "Noch keine Drohnen vorhanden."
                )
            )

            item.setFlags(
                item.flags()
                & ~Qt.ItemFlag.ItemIsSelectable
            )

            self.drone_list.addItem(
                item
            )

            return

        for drone in drones:
            item = QListWidgetItem(
                self._drone_text(
                    drone
                )
            )

            item.setData(
                Qt.ItemDataRole.UserRole,
                drone.id,
            )

            self.drone_list.addItem(
                item
            )

    def _drone_selected(
        self,
        current: QListWidgetItem | None,
        _previous: QListWidgetItem | None,
    ):
        drone_id = (
            current.data(
                Qt.ItemDataRole.UserRole
            )
            if current is not None
            else None
        )

        self.current_drone_id = drone_id

        enabled = (
            self.can_write
            and bool(drone_id)
        )

        self.drone_edit_button.setEnabled(
            enabled
        )

        self.drone_delete_button.setEnabled(
            enabled
        )

    def _drone_double_clicked(
        self,
        item: QListWidgetItem,
    ):
        drone_id = item.data(
            Qt.ItemDataRole.UserRole
        )

        if not drone_id:
            return

        self.current_drone_id = drone_id

        self._edit_drone()

    def _add_drone(self):
        if not self.can_write:
            return

        if self.current_person_id is None:
            return

        dialog = DroneDialog(
            parent=self
        )

        if (
            dialog.exec()
            != QDialog.DialogCode.Accepted
        ):
            return

        data = dialog.get_data()

        try:
            drone = (
                self.drone_service.create_drone(
                    person_id=self.current_person_id,
                    **data,
                )
            )

        except Exception as exc:
            QMessageBox.critical(
                self,
                self.tr("Fehler"),
                self.tr(
                    "Die Drohne konnte nicht "
                    "gespeichert werden."
                )
                + "\n\n"
                + str(exc),
            )
            return

        self._load_drones()

        self._select_drone(
            drone.id
        )

    def _edit_drone(self):
        if not self.can_write:
            return

        if self.current_drone_id is None:
            return

        drone = self.drone_service.get_drone(
            self.current_drone_id
        )

        if drone is None:
            return

        dialog = DroneDialog(
            drone=drone,
            parent=self,
        )

        if (
            dialog.exec()
            != QDialog.DialogCode.Accepted
        ):
            return

        data = dialog.get_data()

        drone.hersteller = data[
            "hersteller"
        ]

        drone.modell = data[
            "modell"
        ]

        drone.seriennummer = data[
            "seriennummer"
        ]

        drone.bemerkungen = data[
            "bemerkungen"
        ]

        try:
            updated = (
                self.drone_service.update_drone(
                    drone
                )
            )

        except Exception as exc:
            QMessageBox.critical(
                self,
                self.tr("Fehler"),
                self.tr(
                    "Die Drohne konnte nicht "
                    "geändert werden."
                )
                + "\n\n"
                + str(exc),
            )
            return

        self._load_drones()

        self._select_drone(
            updated.id
        )

    def _delete_drone(self):
        if not self.can_write:
            return

        if self.current_drone_id is None:
            return

        drone = self.drone_service.get_drone(
            self.current_drone_id
        )

        if drone is None:
            return

        answer = QMessageBox.question(
            self,
            self.tr("Drohne löschen"),
            self.tr(
                'Soll die Drohne "%1" wirklich '
                "gelöscht werden?"
            ).replace(
                "%1",
                self._drone_name(
                    drone
                ),
            ),
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
            self.drone_service.delete_drone(
                drone.id
            )

        except Exception as exc:
            QMessageBox.critical(
                self,
                self.tr("Fehler"),
                self.tr(
                    "Die Drohne konnte nicht "
                    "gelöscht werden."
                )
                + "\n\n"
                + str(exc),
            )
            return

        self._load_drones()

    def _select_drone(
        self,
        drone_id: str,
    ):
        for row in range(
            self.drone_list.count()
        ):
            item = self.drone_list.item(
                row
            )

            if (
                item.data(
                    Qt.ItemDataRole.UserRole
                )
                == drone_id
            ):
                self.drone_list.setCurrentItem(
                    item
                )
                return

    def _clear_details(self):
        self.name_value.setText("-")
        self.birthdate_value.setText("-")
        self.email_value.setText("-")
        self.address_value.setText("-")
        self.location_value.setText("-")
        self.organisation_value.setText("-")
        self.member_value.setText("-")
        self.participant_value.setText("-")
        self.instructor_value.setText("-")
        self.active_value.setText("-")

        self.notes_value.clear()

        self.course_participation_list.setRowCount(
            0
        )
        self.phone_list.clear()
        self.drone_list.clear()

        self.current_phone_number_id = None
        self.current_drone_id = None

        self.edit_button.setEnabled(
            False
        )

        self.active_button.setEnabled(
            False
        )

        self.phone_add_button.setEnabled(
            False
        )

        self.phone_edit_button.setEnabled(
            False
        )

        self.phone_delete_button.setEnabled(
            False
        )

        self.drone_add_button.setEnabled(
            False
        )

        self.drone_edit_button.setEnabled(
            False
        )

        self.drone_delete_button.setEnabled(
            False
        )

        self.active_button.setText(
            self.tr("Deaktivieren")
        )

    def _new_person(self):
        if not self.can_write:
            return

        dialog = PersonDialog(
            parent=self
        )

        if (
            dialog.exec()
            != QDialog.DialogCode.Accepted
        ):
            return

        data = dialog.get_data()

        try:
            person = (
                self.person_service.create_person(
                    **data
                )
            )

        except Exception as exc:
            QMessageBox.critical(
                self,
                self.tr("Fehler"),
                self.tr(
                    "Die Person konnte nicht "
                    "gespeichert werden."
                )
                + "\n\n"
                + str(exc),
            )
            return

        self.current_person_id = person.id

        self.search_edit.clear()

        self.load_persons()

    def _edit_person(self):
        if not self.can_write:
            return

        if self.current_person_id is None:
            return

        person = (
            self.person_service.get_person(
                self.current_person_id
            )
        )

        if person is None:
            return

        dialog = PersonDialog(
            person=person,
            parent=self,
        )

        if (
            dialog.exec()
            != QDialog.DialogCode.Accepted
        ):
            return

        data = dialog.get_data()

        person.vorname = data["vorname"]
        person.nachname = data["nachname"]
        person.geburtsdatum = data[
            "geburtsdatum"
        ]
        person.email = data["email"]
        person.strasse = data["strasse"]
        person.hausnummer = data[
            "hausnummer"
        ]
        person.plz = data["plz"]
        person.ort = data["ort"]
        person.organisation = data[
            "organisation"
        ]
        person.mitglied = data["mitglied"]
        person.ist_teilnehmer = data[
            "ist_teilnehmer"
        ]
        person.ist_instruktor = data[
            "ist_instruktor"
        ]
        person.bemerkungen = data[
            "bemerkungen"
        ]

        try:
            updated_person = (
                self.person_service.update_person(
                    person
                )
            )

        except Exception as exc:
            QMessageBox.critical(
                self,
                self.tr("Fehler"),
                str(exc),
            )
            return

        self.current_person_id = (
            updated_person.id
        )

        self.load_persons()

    def _toggle_active_status(self):
        if not self.can_write:
            return

        if self.current_person_id is None:
            return

        person = (
            self.person_service.get_person(
                self.current_person_id
            )
        )

        if person is None:
            return

        if person.aktiv:
            title = self.tr(
                "Person deaktivieren"
            )

            text = self.tr(
                'Soll die Person "%1" wirklich '
                "deaktiviert werden?\n\n"
                "Historische Kursdaten bleiben erhalten."
            ).replace(
                "%1",
                person.voller_name,
            )

        else:
            title = self.tr(
                "Person aktivieren"
            )

            text = self.tr(
                'Soll die Person "%1" wieder '
                "aktiviert werden?"
            ).replace(
                "%1",
                person.voller_name,
            )

        answer = QMessageBox.question(
            self,
            title,
            text,
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
            if person.aktiv:
                self.person_service.deactivate_person(
                    person.id
                )
            else:
                self.person_service.activate_person(
                    person.id
                )

        except Exception as exc:
            QMessageBox.critical(
                self,
                self.tr("Fehler"),
                str(exc),
            )
            return

        if (
            person.aktiv
            and not self.show_inactive_checkbox.isChecked()
        ):
            self.current_person_id = None

        self.load_persons()

    def _phone_number_text(
        self,
        phone_number: PhoneNumber,
    ) -> str:
        primary_text = (
            "★ "
            if phone_number.ist_primaer
            else ""
        )

        type_text = self._phone_type_text(
            phone_number.typ
        )

        number_text = (
            self.phone_number_service
            .format_for_display(
                phone_number.nummer_e164
            )
        )

        return (
            f"{primary_text}"
            f"{type_text}"
            f"   {number_text}"
        )

    def _phone_type_text(
        self,
        phone_type: PhoneNumberType,
    ) -> str:
        if phone_type == PhoneNumberType.MOBILE:
            return self.tr("Mobil")

        if phone_type == PhoneNumberType.PRIVATE:
            return self.tr("Privat")

        if phone_type == PhoneNumberType.BUSINESS:
            return self.tr("Geschäft")

        if phone_type == PhoneNumberType.OTHER:
            return self.tr("Andere")

        return phone_type.value

    def _assignment_role_text(
        self,
        role_value: str,
    ) -> str:
        if role_value == "participant":
            return self.tr(
                "Teilnehmer"
            )

        if role_value == "instructor":
            return self.tr(
                "Instruktor"
            )

        return role_value

    def _assignment_status_text(
        self,
        status_value: str,
    ) -> str:
        status_names = {
            "registered": self.tr(
                "Angemeldet"
            ),
            "attended": self.tr(
                "Teilgenommen"
            ),
            "absent": self.tr(
                "Nicht erschienen"
            ),
            "cancelled": self.tr(
                "Abgemeldet"
            ),
        }

        return status_names.get(
            status_value,
            status_value,
        )

    def _drone_text(
        self,
        drone: Drone,
    ) -> str:
        text = self._drone_name(
            drone
        )

        if drone.seriennummer:
            text += (
                f"   |   SN: "
                f"{drone.seriennummer}"
            )

        return text

    @staticmethod
    def _drone_name(
        drone: Drone,
    ) -> str:
        parts = [
            value
            for value in (
                drone.hersteller,
                drone.modell,
            )
            if value
        ]

        return " ".join(
            parts
        )

    @staticmethod
    def _person_list_text(
        person: Person,
    ) -> str:
        text = (
            f"{person.nachname}, "
            f"{person.vorname}"
        )

        if person.organisation:
            text += (
                f" – {person.organisation}"
            )

        return text

    @staticmethod
    def _format_date(
        value: date | None,
    ) -> str:
        if value is None:
            return "-"

        return value.strftime(
            "%d.%m.%Y"
        )