from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QVBoxLayout,
    QWidget,
)


class ResetPasswordDialog(QDialog):
    def __init__(
        self,
        username: str,
        parent: QWidget | None = None,
    ):
        super().__init__(parent)

        self.username = username

        self.setWindowTitle(
            self.tr("Passwort zurücksetzen")
        )
        self.setModal(True)
        self.resize(460, 0)

        layout = QVBoxLayout(self)

        title_label = QLabel(
            self.tr("Passwort zurücksetzen")
        )
        title_label.setStyleSheet(
            "font-size: 20px; font-weight: bold;"
        )
        layout.addWidget(title_label)

        info_label = QLabel(
            self.tr(
                "Legen Sie ein neues Passwort für "
                "den ausgewählten Benutzer fest."
            )
        )
        info_label.setWordWrap(True)
        layout.addWidget(info_label)

        user_form = QFormLayout()

        username_value = QLabel(
            self.username
        )

        user_form.addRow(
            self.tr("Benutzername:"),
            username_value,
        )

        layout.addLayout(user_form)

        form = QFormLayout()

        self.new_password_edit = QLineEdit()
        self.new_password_edit.setEchoMode(
            QLineEdit.EchoMode.Password
        )

        self.repeat_password_edit = QLineEdit()
        self.repeat_password_edit.setEchoMode(
            QLineEdit.EchoMode.Password
        )

        form.addRow(
            self.tr("Neues Passwort:"),
            self.new_password_edit,
        )
        form.addRow(
            self.tr("Neues Passwort wiederholen:"),
            self.repeat_password_edit,
        )

        layout.addLayout(form)

        self.require_change_checkbox = QCheckBox(
            self.tr(
                "Passwort muss beim nächsten "
                "Anmelden geändert werden"
            )
        )
        self.require_change_checkbox.setChecked(
            True
        )

        layout.addWidget(
            self.require_change_checkbox
        )

        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save
            | QDialogButtonBox.StandardButton.Cancel
        )

        save_button = self.button_box.button(
            QDialogButtonBox.StandardButton.Save
        )
        cancel_button = self.button_box.button(
            QDialogButtonBox.StandardButton.Cancel
        )

        if save_button is not None:
            save_button.setText(
                self.tr("Speichern")
            )

        if cancel_button is not None:
            cancel_button.setText(
                self.tr("Abbrechen")
            )

        self.button_box.accepted.connect(
            self._validate_and_accept
        )
        self.button_box.rejected.connect(
            self.reject
        )

        layout.addWidget(
            self.button_box
        )

        self.repeat_password_edit.returnPressed.connect(
            self._validate_and_accept
        )

        self.new_password_edit.setFocus()

    def _validate_and_accept(
        self,
    ) -> None:
        new_password = (
            self.new_password_edit.text()
        )
        repeat_password = (
            self.repeat_password_edit.text()
        )

        if not new_password:
            QMessageBox.warning(
                self,
                self.tr("Eingabe fehlt"),
                self.tr(
                    "Bitte geben Sie ein neues "
                    "Passwort ein."
                ),
            )
            self.new_password_edit.setFocus()
            return

        if not repeat_password:
            QMessageBox.warning(
                self,
                self.tr("Eingabe fehlt"),
                self.tr(
                    "Bitte wiederholen Sie das "
                    "neue Passwort."
                ),
            )
            self.repeat_password_edit.setFocus()
            return

        if new_password != repeat_password:
            QMessageBox.warning(
                self,
                self.tr(
                    "Passwörter stimmen nicht überein"
                ),
                self.tr(
                    "Das neue Passwort und die "
                    "Wiederholung stimmen nicht überein."
                ),
            )
            self.new_password_edit.selectAll()
            self.new_password_edit.setFocus()
            return

        self.accept()

    def get_data(
        self,
    ) -> dict:
        return {
            "new_password": (
                self.new_password_edit.text()
            ),
            "require_change": (
                self.require_change_checkbox
                .isChecked()
            ),
        }
