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
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from dfg_kursverwaltung.core.models import (
    User,
    UserRole,
)
from dfg_kursverwaltung.gui.benutzer_dialog import (
    BenutzerDialog,
)
from dfg_kursverwaltung.gui.reset_password_dialog import (
    ResetPasswordDialog,
)
from dfg_kursverwaltung.services.benutzer_service import (
    UserService,
)


class BenutzerWidget(QWidget):
    def __init__(
        self,
        user_service: UserService,
        parent: QWidget | None = None,
    ):
        super().__init__(parent)

        self.user_service = user_service
        self.current_user_id: str | None = None

        self._create_ui()
        self.load_users()

    def _create_ui(self):
        main_layout = QVBoxLayout(self)

        title = QLabel(
            self.tr("Benutzerverwaltung")
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
            self.tr(
                "Benutzer suchen..."
            )
        )
        self.search_edit.setClearButtonEnabled(
            True
        )
        self.search_edit.textChanged.connect(
            self.load_users
        )

        self.include_inactive_checkbox = QCheckBox(
            self.tr(
                "Inaktive anzeigen"
            )
        )
        self.include_inactive_checkbox.toggled.connect(
            self.load_users
        )

        self.user_list = QListWidget()

        self.user_list.setStyleSheet(
            """
            QListWidget::item:selected {
                background-color: #B8DDF5;
                color: black;
            }
            """
        )

        self.user_list.currentItemChanged.connect(
            self._user_selected
        )
        self.user_list.itemDoubleClicked.connect(
            self._user_double_clicked
        )

        button_layout = QHBoxLayout()

        self.new_button = QPushButton(
            self.tr("Neu")
        )
        self.edit_button = QPushButton(
            self.tr("Bearbeiten")
        )
        self.deactivate_button = QPushButton(
            self.tr("Deaktivieren")
        )
        self.reset_password_button = QPushButton(
            self.tr("Passwort zurücksetzen")
        )
        self.delete_button = QPushButton(
            self.tr("Löschen")
        )

        self.new_button.clicked.connect(
            self._new_user
        )
        self.edit_button.clicked.connect(
            self._edit_user
        )
        self.deactivate_button.clicked.connect(
            self._deactivate_user
        )
        self.reset_password_button.clicked.connect(
            self._reset_password
        )
        self.delete_button.clicked.connect(
            self._delete_user
        )

        button_layout.addWidget(
            self.new_button
        )
        button_layout.addWidget(
            self.edit_button
        )
        button_layout.addWidget(
            self.deactivate_button
        )
        button_layout.addWidget(
            self.reset_password_button
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
            self.user_list
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
            self.tr("Benutzerdetails")
        )
        self.detail_title.setStyleSheet(
            "font-size: 18px; "
            "font-weight: bold;"
        )

        layout.addWidget(
            self.detail_title
        )

        user_group = QGroupBox(
            self.tr("Benutzerdaten")
        )
        user_form = QFormLayout(
            user_group
        )

        self.username_value = QLabel("-")
        self.name_value = QLabel("-")
        self.email_value = QLabel("-")

        user_form.addRow(
            self.tr("Benutzername:"),
            self.username_value,
        )
        user_form.addRow(
            self.tr("Name:"),
            self.name_value,
        )
        user_form.addRow(
            self.tr("E-Mail:"),
            self.email_value,
        )

        layout.addWidget(
            user_group
        )

        permission_group = QGroupBox(
            self.tr("Berechtigung")
        )
        permission_form = QFormLayout(
            permission_group
        )

        self.role_value = QLabel("-")
        self.status_value = QLabel("-")
        self.systemadmin_value = QLabel("-")
        self.password_change_value = QLabel("-")

        permission_form.addRow(
            self.tr("Rolle:"),
            self.role_value,
        )
        permission_form.addRow(
            self.tr("Status:"),
            self.status_value,
        )
        permission_form.addRow(
            self.tr("Systemadministrator:"),
            self.systemadmin_value,
        )
        permission_form.addRow(
            self.tr(
                "Passwortänderung erforderlich:"
            ),
            self.password_change_value,
        )

        layout.addWidget(
            permission_group
        )

        layout.addStretch()

        self._clear_details()

        return widget

    def load_users(
        self,
        *_args,
    ):
        include_inactive = (
            self.include_inactive_checkbox
            .isChecked()
        )

        users = self.user_service.list_users(
            include_inactive=include_inactive
        )

        search_text = (
            self.search_edit.text()
            .strip()
            .casefold()
        )

        if search_text:
            users = [
                user
                for user in users
                if self._matches_search(
                    user,
                    search_text,
                )
            ]

        selected_id = self.current_user_id

        self.user_list.blockSignals(
            True
        )
        self.user_list.clear()

        item_to_select = None

        for user in users:
            item = QListWidgetItem(
                self._user_list_text(
                    user
                )
            )

            item.setData(
                Qt.ItemDataRole.UserRole,
                user.id,
            )

            if (
                user.rolle
                == UserRole.INACTIVE
            ):
                font = item.font()
                font.setStrikeOut(True)
                item.setFont(font)

            self.user_list.addItem(
                item
            )

            if user.id == selected_id:
                item_to_select = item

        self.user_list.blockSignals(
            False
        )

        if item_to_select is not None:
            self.user_list.setCurrentItem(
                item_to_select
            )
        elif self.user_list.count() > 0:
            self.user_list.setCurrentRow(
                0
            )
        else:
            self.current_user_id = None
            self._clear_details()

    def _user_selected(
        self,
        current: QListWidgetItem | None,
        _previous: QListWidgetItem | None,
    ):
        if current is None:
            self.current_user_id = None
            self._clear_details()
            return

        user_id = current.data(
            Qt.ItemDataRole.UserRole
        )

        user = self.user_service.get_user(
            user_id
        )

        if user is None:
            self.current_user_id = None
            self._clear_details()
            return

        self.current_user_id = user.id

        self._show_user(
            user
        )

    def _show_user(
        self,
        user: User,
    ):
        self.username_value.setText(
            user.username
        )
        self.name_value.setText(
            user.voller_name or "-"
        )
        self.email_value.setText(
            user.email
        )

        self.role_value.setText(
            self._role_text(
                user.rolle
            )
        )

        if user.rolle == UserRole.INACTIVE:
            self.status_value.setText(
                self.tr("Inaktiv")
            )
        else:
            self.status_value.setText(
                self.tr("Aktiv")
            )

        self.systemadmin_value.setText(
            self.tr("Ja")
            if user.ist_systemadmin
            else self.tr("Nein")
        )

        self.password_change_value.setText(
            self.tr("Ja")
            if user.passwort_aendern
            else self.tr("Nein")
        )

        self.edit_button.setEnabled(
            True
        )

        self.deactivate_button.setEnabled(
            not user.ist_systemadmin
            and user.rolle != UserRole.INACTIVE
        )

        self.reset_password_button.setEnabled(
            user.rolle != UserRole.INACTIVE
        )

        self.delete_button.setEnabled(
            not user.ist_systemadmin
        )

    def _new_user(self):
        dialog = BenutzerDialog(
            parent=self
        )

        if (
            dialog.exec()
            != QDialog.DialogCode.Accepted
        ):
            return

        data = dialog.get_data()

        try:
            user = (
                self.user_service
                .create_user(
                    **data
                )
            )
        except Exception as exc:
            QMessageBox.critical(
                self,
                self.tr("Fehler"),
                self.tr(
                    "Der Benutzer konnte nicht "
                    "gespeichert werden."
                )
                + "\n\n"
                + str(exc),
            )
            return

        self.current_user_id = user.id

        self.search_edit.clear()

        self.load_users()

    def _edit_user(self):
        if self.current_user_id is None:
            return

        user = self.user_service.get_user(
            self.current_user_id
        )

        if user is None:
            return

        dialog = BenutzerDialog(
            user=user,
            parent=self,
        )

        if (
            dialog.exec()
            != QDialog.DialogCode.Accepted
        ):
            return

        data = dialog.get_data()

        user.username = data[
            "username"
        ]
        user.nachname = data[
            "nachname"
        ]
        user.vorname = data[
            "vorname"
        ]
        user.email = data[
            "email"
        ]
        user.rolle = data[
            "rolle"
        ]

        try:
            user = (
                self.user_service
                .update_user(
                    user
                )
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

        self.current_user_id = user.id

        if (
            user.rolle
            == UserRole.INACTIVE
            and not self.include_inactive_checkbox
            .isChecked()
        ):
            self.current_user_id = None
        else:
            self.current_user_id = user.id

        self.load_users()

    def _delete_user(self):
        if self.current_user_id is None:
            return

        user = self.user_service.get_user(
            self.current_user_id
        )

        if user is None:
            return

        if user.ist_systemadmin:
            return

        answer = QMessageBox.warning(
            self,
            self.tr("Benutzer löschen"),
            self.tr(
                "Soll der Benutzer wirklich "
                "dauerhaft gelöscht werden?"
            )
            + "\n\n"
            + user.voller_name
            + " ("
            + user.username
            + ")"
            + "\n\n"
            + self.tr(
                "Dieser Vorgang kann nicht "
                "rückgängig gemacht werden."
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
            self.user_service.delete_user(
                user.id
            )
        except Exception as exc:
            QMessageBox.critical(
                self,
                self.tr("Fehler"),
                self.tr(
                    "Der Benutzer konnte nicht "
                    "gelöscht werden."
                )
                + "\n\n"
                + str(exc),
            )
            return

        self.current_user_id = None
        self.load_users()

    def _reset_password(self):
        if self.current_user_id is None:
            return

        user = self.user_service.get_user(
            self.current_user_id
        )

        if user is None:
            return

        if user.rolle == UserRole.INACTIVE:
            return

        dialog = ResetPasswordDialog(
            username=user.username,
            parent=self,
        )

        if (
            dialog.exec()
            != QDialog.DialogCode.Accepted
        ):
            return

        data = dialog.get_data()

        try:
            user = (
                self.user_service
                .reset_password(
                    user.id,
                    data["new_password"],
                    require_change=data[
                        "require_change"
                    ],
                )
            )
        except Exception as exc:
            QMessageBox.critical(
                self,
                self.tr("Fehler"),
                self.tr(
                    "Das Passwort konnte nicht "
                    "zurückgesetzt werden."
                )
                + "\n\n"
                + str(exc),
            )
            return

        self.current_user_id = user.id
        self.load_users()

        QMessageBox.information(
            self,
            self.tr("Passwort zurückgesetzt"),
            self.tr(
                "Das Passwort wurde erfolgreich "
                "zurückgesetzt."
            ),
        )

    def _deactivate_user(self):
        if self.current_user_id is None:
            return

        user = self.user_service.get_user(
            self.current_user_id
        )

        if user is None:
            return

        if (
            user.ist_systemadmin
            or user.rolle == UserRole.INACTIVE
        ):
            return

        answer = QMessageBox.question(
            self,
            self.tr("Benutzer deaktivieren"),
            self.tr(
                "Soll der Benutzer wirklich "
                "deaktiviert werden?"
            )
            + "\n\n"
            + user.voller_name
            + " ("
            + user.username
            + ")",
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
            user = (
                self.user_service
                .deactivate_user(
                    user.id
                )
            )
        except Exception as exc:
            QMessageBox.critical(
                self,
                self.tr("Fehler"),
                self.tr(
                    "Der Benutzer konnte nicht "
                    "deaktiviert werden."
                )
                + "\n\n"
                + str(exc),
            )
            return

        if (
            self.include_inactive_checkbox
            .isChecked()
        ):
            self.current_user_id = user.id
        else:
            self.current_user_id = None

        self.load_users()

    def _user_double_clicked(
        self,
        item: QListWidgetItem,
    ):
        user_id = item.data(
            Qt.ItemDataRole.UserRole
        )

        if not user_id:
            return

        self.current_user_id = user_id

        self._edit_user()

    def _clear_details(self):
        self.username_value.setText("-")
        self.name_value.setText("-")
        self.email_value.setText("-")

        self.role_value.setText("-")
        self.status_value.setText("-")
        self.systemadmin_value.setText("-")
        self.password_change_value.setText("-")

        self.edit_button.setEnabled(
            False
        )
        self.deactivate_button.setEnabled(
            False
        )
        self.reset_password_button.setEnabled(
            False
        )
        self.delete_button.setEnabled(
            False
        )

    def _matches_search(
        self,
        user: User,
        search_text: str,
    ) -> bool:
        values = (
            user.username,
            user.nachname,
            user.vorname,
            user.email,
            user.voller_name,
            self._role_text(
                user.rolle
            ),
        )

        return any(
            search_text
            in (value or "").casefold()
            for value in values
        )

    def _user_list_text(
        self,
        user: User,
    ) -> str:
        return (
            f"{user.nachname}, "
            f"{user.vorname} "
            f"({user.username})"
        )

    def _role_text(
        self,
        role: UserRole,
    ) -> str:
        labels = {
            UserRole.ADMINISTRATOR: (
                self.tr("Administrator")
            ),
            UserRole.COURSE_MANAGEMENT: (
                self.tr("Kursverwaltung")
            ),
            UserRole.INSTRUCTOR: (
                self.tr("Instruktor")
            ),
            UserRole.READER: (
                self.tr("Leser")
            ),
            UserRole.INACTIVE: (
                self.tr("Inaktiv")
            ),
        }

        return labels[role]



