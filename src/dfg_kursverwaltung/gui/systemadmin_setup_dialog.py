from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QVBoxLayout,
    QWidget,
)

from dfg_kursverwaltung.core.i18n import (
    SUPPORTED_LANGUAGES,
    TranslationManager,
)


class SystemAdminSetupDialog(QDialog):
    LANGUAGE_CHANGED = 2

    def __init__(
        self,
        translation_manager: TranslationManager,
        parent: QWidget | None = None,
    ):
        super().__init__(parent)

        self.translation_manager = translation_manager

        self.setModal(True)
        self.resize(520, 0)

        self._create_ui()

    def _create_ui(self):
        self.setWindowTitle(
            self.tr(
                "Ersteinrichtung"
            )
        )

        main_layout = QVBoxLayout(self)

        title = QLabel(
            self.tr(
                "Systemadministrator einrichten"
            )
        )

        title.setStyleSheet(
            "font-size: 20px; "
            "font-weight: bold;"
        )

        main_layout.addWidget(
            title
        )

        information = QLabel(
            self.tr(
                "Für die DFG-Kursverwaltung muss "
                "zuerst ein geschützter "
                "Systemadministrator eingerichtet "
                "werden."
            )
        )

        information.setWordWrap(
            True
        )

        main_layout.addWidget(
            information
        )

        form = QFormLayout()

        self.language_combo = QComboBox()

        for code, name in SUPPORTED_LANGUAGES.items():
            self.language_combo.addItem(
                name,
                code,
            )

        current_language = (
            self.translation_manager.current_language
        )

        current_index = (
            self.language_combo.findData(
                current_language
            )
        )

        if current_index >= 0:
            self.language_combo.setCurrentIndex(
                current_index
            )

        self.language_combo.currentIndexChanged.connect(
            self._on_language_changed
        )

        form.addRow(
            self.tr("Sprache:"),
            self.language_combo,
        )

        self.username_edit = QLineEdit()
        self.last_name_edit = QLineEdit()
        self.first_name_edit = QLineEdit()
        self.email_edit = QLineEdit()

        self.password_edit = QLineEdit()
        self.password_repeat_edit = QLineEdit()

        self.password_edit.setEchoMode(
            QLineEdit.EchoMode.Password
        )

        self.password_repeat_edit.setEchoMode(
            QLineEdit.EchoMode.Password
        )

        self.username_edit.setPlaceholderText(
            self.tr("Benutzername")
        )

        self.last_name_edit.setPlaceholderText(
            self.tr("Nachname")
        )

        self.first_name_edit.setPlaceholderText(
            self.tr("Vorname")
        )

        self.email_edit.setPlaceholderText(
            self.tr("name@beispiel.ch")
        )

        form.addRow(
            self.tr("Benutzername:"),
            self.username_edit,
        )

        form.addRow(
            self.tr("Nachname:"),
            self.last_name_edit,
        )

        form.addRow(
            self.tr("Vorname:"),
            self.first_name_edit,
        )

        form.addRow(
            self.tr("E-Mail:"),
            self.email_edit,
        )

        form.addRow(
            self.tr("Passwort:"),
            self.password_edit,
        )

        form.addRow(
            self.tr("Passwort wiederholen:"),
            self.password_repeat_edit,
        )

        main_layout.addLayout(
            form
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

        save_button.setText(
            self.tr("Speichern")
        )

        cancel_button.setText(
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

        self.username_edit.setFocus()

    def _on_language_changed(
        self,
        index: int,
    ):
        language_code = (
            self.language_combo.itemData(index)
        )

        if (
            not language_code
            or language_code
            == self.translation_manager.current_language
        ):
            return

        if not self.translation_manager.change_language(
            language_code
        ):
            QMessageBox.warning(
                self,
                self.tr("Sprachwechsel nicht möglich"),
                self.tr(
                    "Die ausgewählte Sprache konnte "
                    "nicht geladen werden."
                ),
            )

            current_index = (
                self.language_combo.findData(
                    self.translation_manager.current_language
                )
            )

            if current_index >= 0:
                self.language_combo.blockSignals(True)
                self.language_combo.setCurrentIndex(
                    current_index
                )
                self.language_combo.blockSignals(False)

            return

        self.done(
            self.LANGUAGE_CHANGED
        )

    def _validate_and_accept(self):
        username = (
            self.username_edit.text().strip()
        )

        last_name = (
            self.last_name_edit.text().strip()
        )

        first_name = (
            self.first_name_edit.text().strip()
        )

        email = (
            self.email_edit.text().strip()
        )

        password = (
            self.password_edit.text()
        )

        password_repeat = (
            self.password_repeat_edit.text()
        )

        if not username:
            self._show_required(
                self.tr(
                    "Bitte geben Sie einen "
                    "Benutzernamen ein."
                ),
                self.username_edit,
            )
            return

        if not last_name:
            self._show_required(
                self.tr(
                    "Bitte geben Sie einen "
                    "Nachnamen ein."
                ),
                self.last_name_edit,
            )
            return

        if not first_name:
            self._show_required(
                self.tr(
                    "Bitte geben Sie einen "
                    "Vornamen ein."
                ),
                self.first_name_edit,
            )
            return

        if not email:
            self._show_required(
                self.tr(
                    "Bitte geben Sie eine "
                    "E-Mail-Adresse ein."
                ),
                self.email_edit,
            )
            return

        if (
            "@" not in email
            or "." not in email.split("@")[-1]
        ):
            QMessageBox.warning(
                self,
                self.tr(
                    "Ungültige E-Mail-Adresse"
                ),
                self.tr(
                    "Bitte geben Sie eine gültige "
                    "E-Mail-Adresse ein."
                ),
            )

            self.email_edit.setFocus()
            return

        if not password:
            self._show_required(
                self.tr(
                    "Bitte geben Sie ein "
                    "Passwort ein."
                ),
                self.password_edit,
            )
            return

        if password != password_repeat:
            QMessageBox.warning(
                self,
                self.tr(
                    "Passwörter stimmen nicht überein"
                ),
                self.tr(
                    "Die beiden eingegebenen "
                    "Passwörter stimmen nicht "
                    "überein."
                ),
            )

            self.password_repeat_edit.clear()
            self.password_repeat_edit.setFocus()
            return

        self.accept()

    def _show_required(
        self,
        message: str,
        widget: QLineEdit,
    ):
        QMessageBox.warning(
            self,
            self.tr("Eingabe fehlt"),
            message,
        )

        widget.setFocus()

    def get_data(self) -> dict:
        return {
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
            "password": (
                self.password_edit.text()
            ),
        }
