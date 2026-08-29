from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QVBoxLayout,
    QWidget,
)


class ChangePasswordDialog(QDialog):
    def __init__(
        self,
        parent: QWidget | None = None,
    ):
        super().__init__(parent)

        self.setWindowTitle(
            self.tr("Passwort ändern")
        )
        self.setModal(True)
        self.resize(440, 0)

        layout = QVBoxLayout(self)

        title_label = QLabel(
            self.tr("Passwort ändern")
        )
        title_label.setStyleSheet(
            "font-size: 20px; font-weight: bold;"
        )
        layout.addWidget(title_label)

        info_label = QLabel(
            self.tr(
                "Geben Sie Ihr aktuelles Passwort "
                "und anschliessend das neue Passwort ein."
            )
        )
        info_label.setWordWrap(True)
        layout.addWidget(info_label)

        form = QFormLayout()

        self.current_password_edit = QLineEdit()
        self.current_password_edit.setEchoMode(
            QLineEdit.EchoMode.Password
        )

        self.new_password_edit = QLineEdit()
        self.new_password_edit.setEchoMode(
            QLineEdit.EchoMode.Password
        )

        self.repeat_password_edit = QLineEdit()
        self.repeat_password_edit.setEchoMode(
            QLineEdit.EchoMode.Password
        )

        form.addRow(
            self.tr("Aktuelles Passwort:"),
            self.current_password_edit,
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

        layout.addWidget(self.button_box)

        self.repeat_password_edit.returnPressed.connect(
            self._validate_and_accept
        )

        self.current_password_edit.setFocus()

    def _validate_and_accept(
        self,
    ) -> None:
        current_password = (
            self.current_password_edit.text()
        )
        new_password = (
            self.new_password_edit.text()
        )
        repeat_password = (
            self.repeat_password_edit.text()
        )

        if not current_password:
            QMessageBox.warning(
                self,
                self.tr("Eingabe fehlt"),
                self.tr(
                    "Bitte geben Sie Ihr aktuelles "
                    "Passwort ein."
                ),
            )
            self.current_password_edit.setFocus()
            return

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
                self.tr("Passwörter stimmen nicht überein"),
                self.tr(
                    "Das neue Passwort und die "
                    "Wiederholung stimmen nicht überein."
                ),
            )
            self.new_password_edit.selectAll()
            self.new_password_edit.setFocus()
            return

        self.accept()

    def get_passwords(
        self,
    ) -> tuple[str, str]:
        return (
            self.current_password_edit.text(),
            self.new_password_edit.text(),
        )
