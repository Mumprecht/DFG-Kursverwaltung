from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QDialog,
    QFormLayout,
    QGroupBox,
    QHeaderView,
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
    Course,
    CourseDay,
    User,
)
from dfg_kursverwaltung.core.permissions import (
    Permission,
    has_permission,
)
from dfg_kursverwaltung.gui.kurstag_dialog import (
    KurstagDialog,
)
from dfg_kursverwaltung.gui.lehrgang_dialog import (
    LehrgangDialog,
)
from dfg_kursverwaltung.services.kurstage_service import (
    CourseDayService,
)
from dfg_kursverwaltung.services.lehrgaenge_service import (
    CourseService,
)
from dfg_kursverwaltung.services.lehrgangstypen_service import (
    CourseTypeService,
)
from dfg_kursverwaltung.services.standorte_service import (
    LocationService,
)


class LehrgaengeWidget(QWidget):
    def __init__(
        self,
        course_service: CourseService,
        course_type_service: CourseTypeService,
        course_day_service: CourseDayService,
        location_service: LocationService,
        authenticated_user: User,
        parent: QWidget | None = None,
    ):
        super().__init__(parent)

        self.course_service = course_service
        self.course_type_service = course_type_service
        self.course_day_service = course_day_service
        self.location_service = location_service
        self.authenticated_user = authenticated_user

        self.can_write_course = has_permission(
            authenticated_user,
            Permission.COURSE_WRITE,
        )

        self.can_write_course_day = has_permission(
            authenticated_user,
            Permission.COURSE_DAY_WRITE,
        )

        self.current_course_id: str | None = None
        self.current_course_day_id: str | None = None

        self._create_ui()
        self.load_courses()

    def _create_ui(self):
        main_layout = QVBoxLayout(self)

        title = QLabel(
            self.tr("Lehrgänge")
        )

        title.setStyleSheet(
            "font-size: 22px; "
            "font-weight: bold;"
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

        main_layout.addWidget(
            splitter,
            1,
        )

    def _create_list_area(
        self,
    ) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)

        self.search_edit = QLineEdit()

        self.search_edit.setPlaceholderText(
            self.tr("Lehrgang suchen...")
        )

        self.search_edit.setClearButtonEnabled(
            True
        )

        self.search_edit.textChanged.connect(
            self._search_changed
        )

        self.course_list = QListWidget()

        self.course_list.currentItemChanged.connect(
            self._course_selected
        )

        button_layout = QHBoxLayout()

        self.new_button = QPushButton(
            self.tr("Neu")
        )

        self.edit_button = QPushButton(
            self.tr("Bearbeiten")
        )

        self.delete_button = QPushButton(
            self.tr("Löschen")
        )

        self.new_button.setEnabled(
            self.can_write_course
        )

        self.new_button.clicked.connect(
            self._new_course
        )

        self.edit_button.clicked.connect(
            self._edit_course
        )

        self.delete_button.clicked.connect(
            self._delete_course
        )

        button_layout.addWidget(
            self.new_button
        )

        button_layout.addWidget(
            self.edit_button
        )

        button_layout.addWidget(
            self.delete_button
        )

        layout.addWidget(
            self.search_edit
        )

        layout.addWidget(
            self.course_list
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
            self.tr("Lehrgangsdetails")
        )

        self.detail_title.setStyleSheet(
            "font-size: 18px; "
            "font-weight: bold;"
        )

        layout.addWidget(
            self.detail_title
        )

        course_group = QGroupBox(
            self.tr("Lehrgang")
        )

        form = QFormLayout(
            course_group
        )

        self.type_value = QLabel("-")
        self.name_value = QLabel("-")

        self.description_value = QTextEdit()
        self.description_value.setReadOnly(
            True
        )
        self.description_value.setMaximumHeight(
            100
        )

        self.notes_value = QTextEdit()
        self.notes_value.setReadOnly(
            True
        )
        self.notes_value.setMaximumHeight(
            80
        )

        form.addRow(
            self.tr("Typ:"),
            self.type_value,
        )

        form.addRow(
            self.tr("Bezeichnung:"),
            self.name_value,
        )

        form.addRow(
            self.tr("Beschreibung:"),
            self.description_value,
        )

        form.addRow(
            self.tr("Bemerkungen:"),
            self.notes_value,
        )

        layout.addWidget(
            course_group
        )

        course_days_group = QGroupBox(
            self.tr("Kurstage")
        )

        course_days_layout = QVBoxLayout(
            course_days_group
        )

        self.course_days_list = QTableWidget()

        self.course_days_list.setColumnCount(
            4
        )

        self.course_days_list.setHorizontalHeaderLabels(
            [
                self.tr("Datum"),
                self.tr("Zeit"),
                self.tr("Bezeichnung"),
                self.tr("Ausführungsort"),
            ]
        )

        self.course_days_list.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )

        self.course_days_list.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )

        self.course_days_list.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )

        self.course_days_list.setAlternatingRowColors(
            True
        )

        self.course_days_list.verticalHeader().setVisible(
            False
        )

        self.course_days_list.setStyleSheet(
            """
            QTableWidget::item:selected {
                background-color: #B8DDF5;
                color: black;
            }
            """
        )

        header = (
            self.course_days_list.horizontalHeader()
        )

        for column in range(4):
            header.setSectionResizeMode(
                column,
                QHeaderView.ResizeMode.Interactive,
            )

        self.course_days_list.setColumnWidth(
            0,
            150,
        )

        self.course_days_list.setColumnWidth(
            1,
            170,
        )

        self.course_days_list.setColumnWidth(
            2,
            320,
        )

        self.course_days_list.setColumnWidth(
            3,
            260,
        )

        header.setStretchLastSection(
            True
        )

        self.course_days_list.itemSelectionChanged.connect(
            self._course_day_selected
        )

        self.course_days_list.itemDoubleClicked.connect(
            self._course_day_double_clicked
        )

        course_days_layout.addWidget(
            self.course_days_list
        )

        course_day_buttons = QHBoxLayout()

        self.new_course_day_button = QPushButton(
            self.tr("Kurstag hinzufügen")
        )

        self.edit_course_day_button = QPushButton(
            self.tr("Kurstag bearbeiten")
        )

        self.new_course_day_button.clicked.connect(
            self._new_course_day
        )

        self.edit_course_day_button.clicked.connect(
            self._edit_course_day
        )

        course_day_buttons.addWidget(
            self.new_course_day_button
        )

        course_day_buttons.addWidget(
            self.edit_course_day_button
        )

        course_day_buttons.addStretch()

        course_days_layout.addLayout(
            course_day_buttons
        )

        layout.addWidget(
            course_days_group,
            1,
        )

        self._clear_details()

        return widget

    def load_courses(
        self,
        *_args,
    ):
        search_text = (
            self.search_edit.text().strip()
        )

        if search_text:
            courses = (
                self.course_service.search_courses(
                    search_text
                )
            )
        else:
            courses = (
                self.course_service.list_courses()
            )

        selected_id = self.current_course_id

        self.course_list.blockSignals(True)
        self.course_list.clear()

        item_to_select = None

        for course in courses:
            item = QListWidgetItem(
                self._course_list_text(
                    course
                )
            )

            item.setData(
                Qt.ItemDataRole.UserRole,
                course.id,
            )

            self.course_list.addItem(item)

            if course.id == selected_id:
                item_to_select = item

        self.course_list.blockSignals(False)

        if item_to_select is not None:
            self.course_list.setCurrentItem(
                item_to_select
            )

        elif self.course_list.count() > 0:
            self.course_list.setCurrentRow(0)

        else:
            self.current_course_id = None
            self._clear_details()

    def select_course(
        self,
        course_id: str,
    ):
        course = (
            self.course_service.get_course(
                course_id
            )
        )

        if course is None:
            return

        self.current_course_id = course_id

        self.search_edit.blockSignals(True)
        self.search_edit.clear()
        self.search_edit.blockSignals(False)

        self.load_courses()

    def _search_changed(
        self,
        _text: str,
    ):
        self.load_courses()

    def _course_selected(
        self,
        current: QListWidgetItem | None,
        _previous: QListWidgetItem | None,
    ):
        if current is None:
            self.current_course_id = None
            self._clear_details()
            return

        course_id = current.data(
            Qt.ItemDataRole.UserRole
        )

        course = (
            self.course_service.get_course(
                course_id
            )
        )

        if course is None:
            self.current_course_id = None
            self._clear_details()
            return

        self.current_course_id = course.id
        self.current_course_day_id = None

        self._show_course(course)

    def _show_course(
        self,
        course: Course,
    ):
        self.type_value.setText(
            self._course_type_text(
                course.lehrgangstyp_id
            )
        )

        self.name_value.setText(
            course.bezeichnung
        )

        self.description_value.setPlainText(
            course.beschreibung or ""
        )

        self.notes_value.setPlainText(
            course.bemerkungen or ""
        )

        self.edit_button.setEnabled(
            self.can_write_course
        )

        self.delete_button.setEnabled(
            self.can_write_course
        )

        self.new_course_day_button.setEnabled(
            self.can_write_course_day
        )

        self._load_course_days()

    def _load_course_days(self):
        self.course_days_list.setRowCount(
            0
        )

        self.current_course_day_id = None

        self.edit_course_day_button.setEnabled(
            False
        )

        if self.current_course_id is None:
            return

        course_days = (
            self.course_day_service.list_course_days(
                self.current_course_id
            )
        )

        self.course_days_list.setRowCount(
            len(course_days)
        )

        for table_row, course_day in enumerate(
            course_days
        ):
            date_text = (
                course_day.datum.strftime(
                    "%d.%m.%Y"
                )
            )

            if (
                course_day.beginn
                and course_day.ende
            ):
                time_text = (
                    f"{course_day.beginn}"
                    f"–{course_day.ende}"
                )
            elif course_day.beginn:
                time_text = str(
                    course_day.beginn
                )
            else:
                time_text = ""

            name_text = (
                course_day.bezeichnung or ""
            )

            location_text = ""

            if course_day.standort_id:
                location = (
                    self.location_service.get_location(
                        course_day.standort_id
                    )
                )

                if location is not None:
                    location_text = (
                        location.bezeichnung
                    )

            values = [
                date_text,
                time_text,
                name_text,
                location_text,
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
                        course_day.id,
                    )

                self.course_days_list.setItem(
                    table_row,
                    column,
                    item,
                )

    def _course_day_selected(self):
        row = (
            self.course_days_list.currentRow()
        )

        if row < 0:
            self.current_course_day_id = None

            self.edit_course_day_button.setEnabled(
                False
            )

            return

        item = self.course_days_list.item(
            row,
            0,
        )

        if item is None:
            self.current_course_day_id = None

            self.edit_course_day_button.setEnabled(
                False
            )

            return

        course_day_id = item.data(
            Qt.ItemDataRole.UserRole
        )

        if not course_day_id:
            self.current_course_day_id = None

            self.edit_course_day_button.setEnabled(
                False
            )

            return

        self.current_course_day_id = (
            course_day_id
        )

        self.edit_course_day_button.setEnabled(
            self.can_write_course_day
        )

    def _course_day_double_clicked(
        self,
        item: QTableWidgetItem,
    ):
        row = item.row()

        id_item = self.course_days_list.item(
            row,
            0,
        )

        if id_item is None:
            return

        course_day_id = id_item.data(
            Qt.ItemDataRole.UserRole
        )

        if not course_day_id:
            return

        self.current_course_day_id = (
            course_day_id
        )

        self._edit_course_day()

    def _confirm_possible_course_duplicate(
        self,
        data: dict,
    ) -> bool:
        duplicate = (
            self.course_service
            .get_course_by_type_and_name(
                data["lehrgangstyp_id"],
                data["bezeichnung"],
            )
        )

        if duplicate is None:
            return True

        course_type_text = (
            self._course_type_text(
                duplicate.lehrgangstyp_id
            )
        )

        message = self.tr(
            "Es wurde möglicherweise bereits ein "
            "Lehrgang mit diesen Angaben gefunden."
        )

        message += (
            "\n\n"
            + self.tr(
                "Vorhandener Lehrgang:"
            )
            + "\n"
            + f"{duplicate.bezeichnung} "
            + f"({course_type_text})"
        )

        message += (
            "\n\n"
            + self.tr(
                "Möchten Sie den Lehrgang "
                "trotzdem neu erfassen?"
            )
        )

        answer = QMessageBox.question(
            self,
            self.tr(
                "Mögliche Dublette"
            ),
            message,
            QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        return (
            answer
            == QMessageBox.StandardButton.Yes
        )
    def _new_course(self):
        if not self.can_write_course:
            return

        dialog = LehrgangDialog(
            course_type_service=(
                self.course_type_service
            ),
            parent=self,
        )

        if (
            dialog.exec()
            != QDialog.DialogCode.Accepted
        ):
            return

        data = dialog.get_data()

        try:
            if not self._confirm_possible_course_duplicate(
                data
            ):
                return
            course = (
                self.course_service.create_course(
                    **data
                )
            )

        except Exception as exc:
            QMessageBox.critical(
                self,
                self.tr("Fehler"),
                self.tr(
                    "Der Lehrgang konnte nicht "
                    "gespeichert werden."
                )
                + "\n\n"
                + str(exc),
            )
            return

        self.current_course_id = course.id

        self.search_edit.clear()
        self.load_courses()

    def _delete_course(self):
        if not self.can_write_course:
            return

        if self.current_course_id is None:
            return

        course = (
            self.course_service.get_course(
                self.current_course_id
            )
        )

        if course is None:
            return

        answer = QMessageBox.question(
            self,
            self.tr("Lehrgang löschen"),
            self.tr(
                "Möchten Sie den Lehrgang wirklich löschen?"
            )
            + "\n\n"
            + course.bezeichnung,
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
            self.course_service.delete_course(
                course.id
            )
        except ValueError:
            QMessageBox.warning(
                self,
                self.tr(
                    "Lehrgang kann nicht gelöscht werden"
                ),
                self.tr(
                    "Der Lehrgang kann nicht gelöscht werden, "
                    "weil bereits Kurstage vorhanden sind."
                ),
            )
            return
        except Exception as exc:
            QMessageBox.critical(
                self,
                self.tr("Fehler beim Löschen"),
                str(exc),
            )
            return

        self.current_course_id = None
        self.load_courses()

    def _edit_course(self):
        if not self.can_write_course:
            return

        if self.current_course_id is None:
            return

        course = (
            self.course_service.get_course(
                self.current_course_id
            )
        )

        if course is None:
            return

        dialog = LehrgangDialog(
            course_type_service=(
                self.course_type_service
            ),
            course=course,
            parent=self,
        )

        if (
            dialog.exec()
            != QDialog.DialogCode.Accepted
        ):
            return

        data = dialog.get_data()

        course.lehrgangstyp_id = data[
            "lehrgangstyp_id"
        ]
        course.bezeichnung = data[
            "bezeichnung"
        ]
        course.beschreibung = data[
            "beschreibung"
        ]
        course.bemerkungen = data[
            "bemerkungen"
        ]

        try:
            updated_course = (
                self.course_service.update_course(
                    course
                )
            )

        except Exception as exc:
            QMessageBox.critical(
                self,
                self.tr("Fehler"),
                self.tr(
                    "Die Änderungen konnten nicht "
                    "gespeichert werden."
                )
                + "\n\n"
                + str(exc),
            )
            return

        self.current_course_id = (
            updated_course.id
        )

        self.load_courses()

    def _new_course_day(self):
        if not self.can_write_course_day:
            return

        if self.current_course_id is None:
            return

        dialog = KurstagDialog(
            location_service=self.location_service,
            parent=self,
        )

        if (
            dialog.exec()
            != QDialog.DialogCode.Accepted
        ):
            return

        data = dialog.get_data()

        try:
            course_day = (
                self.course_day_service
                .create_course_day(
                    lehrgang_id=(
                        self.current_course_id
                    ),
                    **data,
                )
            )

        except Exception as exc:
            QMessageBox.critical(
                self,
                self.tr("Fehler"),
                self.tr(
                    "Der Kurstag konnte nicht "
                    "gespeichert werden."
                )
                + "\n\n"
                + str(exc),
            )
            return

        self.current_course_day_id = (
            course_day.id
        )

        self._load_course_days()

        self._select_course_day(
            course_day.id
        )

    def _edit_course_day(self):
        if not self.can_write_course_day:
            return

        if self.current_course_day_id is None:
            return

        course_day = (
            self.course_day_service
            .get_course_day(
                self.current_course_day_id
            )
        )

        if course_day is None:
            return

        dialog = KurstagDialog(
            location_service=self.location_service,
            course_day=course_day,
            parent=self,
        )

        if (
            dialog.exec()
            != QDialog.DialogCode.Accepted
        ):
            return

        data = dialog.get_data()

        course_day.datum = data["datum"]
        course_day.beginn = data["beginn"]
        course_day.ende = data["ende"]
        course_day.standort_id = data[
            "standort_id"
        ]
        course_day.bezeichnung = data[
            "bezeichnung"
        ]
        course_day.bemerkungen = data[
            "bemerkungen"
        ]

        try:
            updated_course_day = (
                self.course_day_service
                .update_course_day(
                    course_day
                )
            )

        except Exception as exc:
            QMessageBox.critical(
                self,
                self.tr("Fehler"),
                self.tr(
                    "Die Änderungen am Kurstag "
                    "konnten nicht gespeichert werden."
                )
                + "\n\n"
                + str(exc),
            )
            return

        self.current_course_day_id = (
            updated_course_day.id
        )

        self._load_course_days()

        self._select_course_day(
            updated_course_day.id
        )

    def _select_course_day(
        self,
        course_day_id: str,
    ):
        for row in range(
            self.course_days_list.rowCount()
        ):
            item = self.course_days_list.item(
                row,
                0,
            )

            if item is None:
                continue

            if (
                item.data(
                    Qt.ItemDataRole.UserRole
                )
                == course_day_id
            ):
                self.course_days_list.selectRow(
                    row
                )

                self.course_days_list.setCurrentCell(
                    row,
                    0,
                )

                return

    def _clear_details(self):
        self.type_value.setText("-")
        self.name_value.setText("-")

        self.description_value.clear()
        self.notes_value.clear()

        self.course_days_list.setRowCount(
            0
        )

        self.edit_button.setEnabled(False)
        self.delete_button.setEnabled(False)

        self.new_course_day_button.setEnabled(
            False
        )

        self.edit_course_day_button.setEnabled(
            False
        )

    def _course_type_text(
        self,
        course_type_id: str,
    ) -> str:
        course_type = (
            self.course_type_service.get_course_type(
                course_type_id
            )
        )

        if course_type is None:
            return self.tr(
                "Unbekannter Lehrgangstyp"
            )

        return course_type.bezeichnung

    def _course_list_text(
        self,
        course: Course,
    ) -> str:
        return (
            f"{course.bezeichnung} "
            f"({self._course_type_text(course.lehrgangstyp_id)})"
        )

    def _course_day_list_text(
        self,
        course_day: CourseDay,
    ) -> str:
        date_text = (
            course_day.datum.strftime(
                "%d.%m.%Y"
            )
        )

        if (
            course_day.beginn
            and course_day.ende
        ):
            time_text = (
                f"{course_day.beginn}"
                f"–{course_day.ende}"
            )

        elif course_day.beginn:
            time_text = (
                f"ab {course_day.beginn}"
            )

        else:
            time_text = ""

        location_text = ""

        if course_day.standort_id:
            location = (
                self.location_service
                .get_location(
                    course_day.standort_id
                )
            )

            if location is not None:
                location_text = (
                    location.bezeichnung
                )

        parts = [
            date_text,
            time_text,
            course_day.bezeichnung or "",
        ]

        text = "   ".join(
            part
            for part in parts
            if part
        )

        if location_text:
            text += (
                f"   |   {location_text}"
            )

        return text