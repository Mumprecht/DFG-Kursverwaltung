from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QGroupBox,
    QLabel,
    QLineEdit,
    QMessageBox,
    QVBoxLayout,
    QWidget,
)

from dfg_kursverwaltung.core.models import (
    User,
    UserRole,
)


class BenutzerDialog(QDialog):
    def __init__(
        self,
        user: User | None = None,
        parent: QWidget | None = None,
    ):
        super().__init__(parent)

        self.user = user

        self.setModal(True)
        self.resize(560, 520)

        self._create_ui()

        if self.user is not None:
            self._load_user()

    def _create_ui(self):
        if self.user is None:
            self.setWindowTitle(
                self.tr("Neuer Benutzer")
            )
        else:
            self.setWindowTitle(
                self.tr("Benutzer bearbeiten")
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

        # Benutzerdaten
        user_group = QGroupBox(
            self.tr("Benutzerdaten")
        )
        user_form = QFormLayout(
            user_group
        )

        self.username_edit = QLineEdit()
        self.last_name_edit = QLineEdit()
        self.first_name_edit = QLineEdit()
        self.email_edit = QLineEdit()

        self.email_edit.setPlaceholderText(
            self.tr(
                "name@example.ch"
            )
        )

        user_form.addRow(
            self.tr("Benutzername:"),
            self.username_edit,
        )
        user_form.addRow(
            self.tr("Nachname:"),
            self.last_name_edit,
        )
        user_form.addRow(
            self.tr("Vorname:"),
            self.first_name_edit,
        )
        user_form.addRow(
            self.tr("E-Mail:"),
            self.email_edit,
        )

        main_layout.addWidget(
            user_group
        )

        # Berechtigung
        permission_group = QGroupBox(
            self.tr("Berechtigung")
        )
        permission_form = QFormLayout(
            permission_group
        )

        self.role_combo = QComboBox()

        self.role_combo.addItem(
            self.tr("Administrator"),
            UserRole.ADMINISTRATOR,
        )
        self.role_combo.addItem(
            self.tr("Kursverwaltung"),
            UserRole.COURSE_MANAGEMENT,
        )
        self.role_combo.addItem(
            self.tr("Instruktor"),
            UserRole.INSTRUCTOR,
        )
        self.role_combo.addItem(
            self.tr("Leser"),
            UserRole.READER,
        )
        if self.user is not None:
            self.role_combo.addItem(
                self.tr("Inaktiv"),
                UserRole.INACTIVE,
            )

        permission_form.addRow(
            self.tr("Rolle:"),
            self.role_combo,
        )

        main_layout.addWidget(
            permission_group
        )

        # Passwort nur bei Neuanlage
        self.password_group = QGroupBox(
            self.tr("Passwort")
        )
        password_form = QFormLayout(
            self.password_group
        )

        self.password_edit = QLineEdit()
        self.password_repeat_edit = QLineEdit()

        self.password_edit.setEchoMode(
            QLineEdit.EchoMode.Password
        )
        self.password_repeat_edit.setEchoMode(
            QLineEdit.EchoMode.Password
        )

        self.require_password_change_checkbox = QCheckBox(
            self.tr(
                "Passwort muss beim nächsten "
                "Anmelden geändert werden"
            )
        )
        self.require_password_change_checkbox.setChecked(
            True
        )

        password_form.addRow(
            self.tr("Passwort:"),
            self.password_edit,
        )
        password_form.addRow(
            self.tr("Passwort wiederholen:"),
            self.password_repeat_edit,
        )
        password_form.addRow(
            "",
            self.require_password_change_checkbox,
        )

        main_layout.addWidget(
            self.password_group
        )

        if self.user is not None:
            self.password_group.setVisible(
                False
            )

        self.systemadmin_info = QLabel(
            self.tr(
                "Der geschützte Systemadministrator "
                "muss Administrator bleiben."
            )
        )
        self.systemadmin_info.setWordWrap(
            True
        )
        self.systemadmin_info.setVisible(
            False
        )

        main_layout.addWidget(
            self.systemadmin_info
        )

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

    def _load_user(self):
        if self.user is None:
            return

        self.username_edit.setText(
            self.user.username
        )
        self.last_name_edit.setText(
            self.user.nachname
        )
        self.first_name_edit.setText(
            self.user.vorname
        )
        self.email_edit.setText(
            self.user.email
        )

        role_index = self.role_combo.findData(
            self.user.rolle
        )

        if role_index >= 0:
            self.role_combo.setCurrentIndex(
                role_index
            )

        if self.user.ist_systemadmin:
            self.role_combo.setEnabled(
                False
            )
            self.systemadmin_info.setVisible(
                True
            )

    def _validate_and_accept(self):
        if not self.username_edit.text().strip():
            QMessageBox.warning(
                self,
                self.tr(
                    "Fehlender Benutzername"
                ),
                self.tr(
                    "Bitte geben Sie einen "
                    "Benutzernamen ein."
                ),
            )
            self.username_edit.setFocus()
            return

        if not self.last_name_edit.text().strip():
            QMessageBox.warning(
                self,
                self.tr(
                    "Fehlender Nachname"
                ),
                self.tr(
                    "Bitte geben Sie einen "
                    "Nachnamen ein."
                ),
            )
            self.last_name_edit.setFocus()
            return

        if not self.first_name_edit.text().strip():
            QMessageBox.warning(
                self,
                self.tr(
                    "Fehlender Vorname"
                ),
                self.tr(
                    "Bitte geben Sie einen "
                    "Vornamen ein."
                ),
            )
            self.first_name_edit.setFocus()
            return

        if not self.email_edit.text().strip():
            QMessageBox.warning(
                self,
                self.tr(
                    "Fehlende E-Mail-Adresse"
                ),
                self.tr(
                    "Bitte geben Sie eine "
                    "E-Mail-Adresse ein."
                ),
            )
            self.email_edit.setFocus()
            return

        if self.user is None:
            if not self.password_edit.text():
                QMessageBox.warning(
                    self,
                    self.tr(
                        "Fehlendes Passwort"
                    ),
                    self.tr(
                        "Bitte geben Sie ein "
                        "Passwort ein."
                    ),
                )
                self.password_edit.setFocus()
                return

            if not self.password_repeat_edit.text():
                QMessageBox.warning(
                    self,
                    self.tr(
                        "Fehlende Passwortbestätigung"
                    ),
                    self.tr(
                        "Bitte wiederholen Sie "
                        "das Passwort."
                    ),
                )
                self.password_repeat_edit.setFocus()
                return

            if (
                self.password_edit.text()
                != self.password_repeat_edit.text()
            ):
                QMessageBox.warning(
                    self,
                    self.tr(
                        "Passwörter stimmen nicht überein"
                    ),
                    self.tr(
                        "Das Passwort und seine "
                        "Bestätigung stimmen nicht "
                        "überein."
                    ),
                )
                self.password_repeat_edit.setFocus()
                return

        self.accept()

    def get_data(self) -> dict:
        data = {
            "username": (
                self.username_edit.text().strip()
            ),
            "nachname": (
                self.last_name_edit.text().strip()
            ),
            "vorname": (
                self.first_name_edit.text().strip()
            ),
            "email": (
                self.email_edit.text().strip()
            ),
            "rolle": (
                self.role_combo.currentData()
            ),
        }

        if self.user is None:
            data["password"] = (
                self.password_edit.text()
            )
            data["passwort_aendern"] = (
                self.require_password_change_checkbox.isChecked()
            )

        return data
