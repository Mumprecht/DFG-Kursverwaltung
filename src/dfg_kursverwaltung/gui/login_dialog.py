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


class LoginDialog(QDialog):
    def __init__(
        self,
        parent: QWidget | None = None,
    ):
        super().__init__(parent)

        self.setWindowTitle(
            self.tr("Anmeldung")
        )
        self.setModal(True)
        self.resize(420, 0)

        layout = QVBoxLayout(self)

        title_label = QLabel(
            self.tr("DFG-Kursverwaltung")
        )
        title_label.setStyleSheet(
            "font-size: 20px; font-weight: bold;"
        )
        layout.addWidget(title_label)

        info_label = QLabel(
            self.tr(
                "Bitte melden Sie sich mit Ihrem "
                "Benutzerkonto an."
            )
        )
        info_label.setWordWrap(True)
        layout.addWidget(info_label)

        form = QFormLayout()

        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText(
            self.tr("Benutzername")
        )

        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(
            QLineEdit.EchoMode.Password
        )
        self.password_edit.setPlaceholderText(
            self.tr("Passwort")
        )

        form.addRow(
            self.tr("Benutzername:"),
            self.username_edit,
        )
        form.addRow(
            self.tr("Passwort:"),
            self.password_edit,
        )

        layout.addLayout(form)

        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
        )

        ok_button = self.button_box.button(
            QDialogButtonBox.StandardButton.Ok
        )
        cancel_button = self.button_box.button(
            QDialogButtonBox.StandardButton.Cancel
        )

        if ok_button is not None:
            ok_button.setText(
                self.tr("Anmelden")
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

        self.password_edit.returnPressed.connect(
            self._validate_and_accept
        )

        self.username_edit.setFocus()

    def _validate_and_accept(
        self,
    ) -> None:
        username = (
            self.username_edit
            .text()
            .strip()
        )

        password = self.password_edit.text()

        if not username:
            QMessageBox.warning(
                self,
                self.tr("Eingabe fehlt"),
                self.tr(
                    "Bitte geben Sie einen "
                    "Benutzernamen ein."
                ),
            )
            self.username_edit.setFocus()
            return

        if not password:
            QMessageBox.warning(
                self,
                self.tr("Eingabe fehlt"),
                self.tr(
                    "Bitte geben Sie ein "
                    "Passwort ein."
                ),
            )
            self.password_edit.setFocus()
            return

        self.accept()

    def get_credentials(
        self,
    ) -> tuple[str, str]:
        return (
            self.username_edit.text().strip(),
            self.password_edit.text(),
        )
