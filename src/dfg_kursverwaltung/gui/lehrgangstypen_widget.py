from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QSplitter,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from dfg_kursverwaltung.core.models import (
    CourseType,
    User,
)
from dfg_kursverwaltung.core.permissions import (
    Permission,
    has_permission,
)
from dfg_kursverwaltung.gui.lehrgangstyp_dialog import (
    LehrgangstypDialog,
)
from dfg_kursverwaltung.services.lehrgangstypen_service import (
    CourseTypeService,
)


class LehrgangstypenWidget(QWidget):
    def __init__(
        self,
        course_type_service: CourseTypeService,
        authenticated_user: User,
        parent: QWidget | None = None,
    ):
        super().__init__(parent)

        self.course_type_service = course_type_service
        self.authenticated_user = authenticated_user
        self.can_write = has_permission(
            authenticated_user,
            Permission.COURSE_TYPE_WRITE,
        )

        self.current_course_type_id: str | None = None

        self._create_ui()
        self.load_course_types()

    def _create_ui(self):
        main_layout = QVBoxLayout(self)

        title = QLabel(
            self.tr("Lehrgangstypen")
        )

        title.setStyleSheet(
            "font-size: 22px; "
            "font-weight: bold;"
        )

        main_layout.addWidget(
            title
        )

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
            self.tr(
                "Lehrgangstyp suchen..."
            )
        )

        self.search_edit.setClearButtonEnabled(
            True
        )

        self.search_edit.textChanged.connect(
            self._search_changed
        )

        self.include_inactive_checkbox = QCheckBox(
            self.tr(
                "Deaktivierte anzeigen"
            )
        )

        self.include_inactive_checkbox.toggled.connect(
            self.load_course_types
        )

        self.course_type_list = QListWidget()

        self.course_type_list.currentItemChanged.connect(
            self._course_type_selected
        )

        self.course_type_list.itemDoubleClicked.connect(
            self._course_type_double_clicked
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
            self.can_write
        )

        self.new_button.clicked.connect(
            self._new_course_type
        )

        self.edit_button.clicked.connect(
            self._edit_course_type
        )

        self.delete_button.clicked.connect(
            self._delete_course_type
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
            self.include_inactive_checkbox
        )

        layout.addWidget(
            self.course_type_list
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
            self.tr("Lehrgangstypdetails")
        )

        self.detail_title.setStyleSheet(
            "font-size: 18px; "
            "font-weight: bold;"
        )

        layout.addWidget(
            self.detail_title
        )

        group = QGroupBox(
            self.tr("Lehrgangstyp")
        )

        form = QFormLayout(
            group
        )

        self.name_value = QLabel("-")
        self.status_value = QLabel("-")

        form.addRow(
            self.tr("Bezeichnung:"),
            self.name_value,
        )

        form.addRow(
            self.tr("Status:"),
            self.status_value,
        )

        layout.addWidget(
            group
        )

        notes_group = QGroupBox(
            self.tr("Bemerkungen")
        )

        notes_group.setSizePolicy(
            QSizePolicy.Policy.Preferred,
            QSizePolicy.Policy.Maximum,
        )

        notes_layout = QVBoxLayout(
            notes_group
        )

        self.notes_value = QTextEdit()

        self.notes_value.setReadOnly(
            True
        )

        self.notes_value.setMaximumHeight(
            140
        )

        notes_layout.addWidget(
            self.notes_value
        )

        layout.addWidget(
            notes_group
        )

        action_layout = QHBoxLayout()

        self.status_button = QPushButton()

        self.status_button.clicked.connect(
            self._toggle_active_status
        )

        action_layout.addWidget(
            self.status_button
        )

        action_layout.addStretch()

        layout.addLayout(
            action_layout
        )

        layout.addStretch()

        self._clear_details()

        return widget

    def load_course_types(
        self,
        *_args,
    ):
        search_text = (
            self.search_edit.text().strip()
        )

        include_inactive = (
            self.include_inactive_checkbox
            .isChecked()
        )

        if search_text:
            course_types = (
                self.course_type_service
                .search_course_types(
                    search_text,
                    include_inactive=(
                        include_inactive
                    ),
                )
            )
        else:
            course_types = (
                self.course_type_service
                .list_course_types(
                    include_inactive=(
                        include_inactive
                    )
                )
            )

        selected_id = (
            self.current_course_type_id
        )

        self.course_type_list.blockSignals(
            True
        )

        self.course_type_list.clear()

        item_to_select = None

        for course_type in course_types:
            item = QListWidgetItem(
                course_type.bezeichnung
            )

            item.setData(
                Qt.ItemDataRole.UserRole,
                course_type.id,
            )

            if not course_type.aktiv:
                font = item.font()
                font.setStrikeOut(True)
                item.setFont(font)

            self.course_type_list.addItem(
                item
            )

            if course_type.id == selected_id:
                item_to_select = item

        self.course_type_list.blockSignals(
            False
        )

        if item_to_select is not None:
            self.course_type_list.setCurrentItem(
                item_to_select
            )

        elif self.course_type_list.count() > 0:
            self.course_type_list.setCurrentRow(
                0
            )

        else:
            self.current_course_type_id = None
            self._clear_details()

    def _search_changed(
        self,
        _text: str,
    ):
        self.load_course_types()

    def _course_type_selected(
        self,
        current: QListWidgetItem | None,
        _previous: QListWidgetItem | None,
    ):
        if current is None:
            self.current_course_type_id = None
            self._clear_details()
            return

        course_type_id = current.data(
            Qt.ItemDataRole.UserRole
        )

        course_type = (
            self.course_type_service
            .get_course_type(
                course_type_id
            )
        )

        if course_type is None:
            self.current_course_type_id = None
            self._clear_details()
            return

        self.current_course_type_id = (
            course_type.id
        )

        self._show_course_type(
            course_type
        )

    def _show_course_type(
        self,
        course_type: CourseType,
    ):
        self.name_value.setText(
            course_type.bezeichnung
        )

        self.notes_value.setPlainText(
            course_type.bemerkungen or ""
        )

        if course_type.aktiv:
            self.status_value.setText(
                self.tr("Aktiv")
            )

            self.status_button.setText(
                self.tr("Deaktivieren")
            )

        else:
            self.status_value.setText(
                self.tr("Deaktiviert")
            )

            self.status_button.setText(
                self.tr("Wieder aktivieren")
            )

        self.edit_button.setEnabled(
            self.can_write
        )

        self.delete_button.setEnabled(
            self.can_write
        )

        self.status_button.setEnabled(
            self.can_write
        )

    def _new_course_type(self):
        if not self.can_write:
            return

        dialog = LehrgangstypDialog(
            parent=self
        )

        if (
            dialog.exec()
            != QDialog.DialogCode.Accepted
        ):
            return

        data = dialog.get_data()

        requested_active = data.pop(
            "aktiv"
        )

        try:
            course_type = (
                self.course_type_service
                .create_course_type(
                    **data
                )
            )

            if not requested_active:
                self.course_type_service.deactivate_course_type(
                    course_type.id
                )

                course_type.aktiv = False

        except Exception as exc:
            QMessageBox.critical(
                self,
                self.tr("Fehler"),
                self.tr(
                    "Der Lehrgangstyp konnte "
                    "nicht gespeichert werden."
                )
                + "\n\n"
                + str(exc),
            )
            return

        self.current_course_type_id = (
            course_type.id
        )

        if (
            not course_type.aktiv
            and not self.include_inactive_checkbox
            .isChecked()
        ):
            self.include_inactive_checkbox.setChecked(
                True
            )

        self.search_edit.clear()

        self.load_course_types()

    def _delete_course_type(self):
        if not self.can_write:
            return

        if self.current_course_type_id is None:
            return

        course_type = (
            self.course_type_service
            .get_course_type(
                self.current_course_type_id
            )
        )

        if course_type is None:
            return

        answer = QMessageBox.question(
            self,
            self.tr("Lehrgangstyp löschen"),
            self.tr(
                "Möchten Sie den Lehrgangstyp wirklich löschen?"
            )
            + "\n\n"
            + course_type.bezeichnung,
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
            self.course_type_service.delete_course_type(
                course_type.id
            )
        except ValueError:
            QMessageBox.warning(
                self,
                self.tr(
                    "Lehrgangstyp kann nicht gelöscht werden"
                ),
                self.tr(
                    "Der Lehrgangstyp kann nicht gelöscht werden, "
                    "weil bereits Lehrgänge vorhanden sind."
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

        self.current_course_type_id = None
        self.load_course_types()
    def _edit_course_type(self):
        if not self.can_write:
            return

        if self.current_course_type_id is None:
            return

        course_type = (
            self.course_type_service
            .get_course_type(
                self.current_course_type_id
            )
        )

        if course_type is None:
            return

        dialog = LehrgangstypDialog(
            course_type=course_type,
            parent=self,
        )

        if (
            dialog.exec()
            != QDialog.DialogCode.Accepted
        ):
            return

        data = dialog.get_data()

        requested_active = data.pop(
            "aktiv"
        )

        course_type.bezeichnung = data[
            "bezeichnung"
        ]

        course_type.bemerkungen = data[
            "bemerkungen"
        ]

        try:
            course_type = (
                self.course_type_service
                .update_course_type(
                    course_type
                )
            )

            if requested_active != course_type.aktiv:
                if requested_active:
                    self.course_type_service.activate_course_type(
                        course_type.id
                    )
                else:
                    self.course_type_service.deactivate_course_type(
                        course_type.id
                    )

                course_type.aktiv = (
                    requested_active
                )

        except Exception as exc:
            QMessageBox.critical(
                self,
                self.tr("Fehler"),
                self.tr(
                    "Die Änderungen konnten "
                    "nicht gespeichert werden."
                )
                + "\n\n"
                + str(exc),
            )
            return

        self.current_course_type_id = (
            course_type.id
        )

        self.load_course_types()

    def _toggle_active_status(self):
        if not self.can_write:
            return

        if self.current_course_type_id is None:
            return

        course_type = (
            self.course_type_service
            .get_course_type(
                self.current_course_type_id
            )
        )

        if course_type is None:
            return

        try:
            if course_type.aktiv:
                self.course_type_service.deactivate_course_type(
                    course_type.id
                )
            else:
                self.course_type_service.activate_course_type(
                    course_type.id
                )

        except Exception as exc:
            QMessageBox.critical(
                self,
                self.tr("Fehler"),
                self.tr(
                    "Der Status konnte nicht "
                    "geändert werden."
                )
                + "\n\n"
                + str(exc),
            )
            return

        if (
            course_type.aktiv
            and not self.include_inactive_checkbox
            .isChecked()
        ):
            self.current_course_type_id = None
        else:
            self.current_course_type_id = (
                course_type.id
            )

        self.load_course_types()

    def _course_type_double_clicked(
        self,
        item: QListWidgetItem,
    ):
        course_type_id = item.data(
            Qt.ItemDataRole.UserRole
        )

        if not course_type_id:
            return

        self.current_course_type_id = (
            course_type_id
        )

        self._edit_course_type()

    def _clear_details(self):
        self.name_value.setText("-")
        self.status_value.setText("-")
        self.notes_value.clear()

        self.edit_button.setEnabled(
            False
        )

        self.delete_button.setEnabled(
            False
        )

        self.status_button.setEnabled(
            False
        )

        self.status_button.setText(
            self.tr("Deaktivieren")
        )
