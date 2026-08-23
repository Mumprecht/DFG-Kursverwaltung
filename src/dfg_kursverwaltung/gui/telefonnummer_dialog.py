from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLineEdit,
    QMessageBox,
    QTextEdit,
    QVBoxLayout,
)

from dfg_kursverwaltung.core.models import (
    PhoneNumber,
    PhoneNumberType,
)
from dfg_kursverwaltung.services.telefonnummern_service import (
    PhoneNumberService,
)


class PhoneNumberDialog(QDialog):
    def __init__(
        self,
        phone_number: PhoneNumber | None = None,
        parent=None,
    ):
        super().__init__(parent)

        self.phone_number = phone_number

        if phone_number is None:
            self.setWindowTitle(
                self.tr(
                    "Telefonnummer hinzufügen"
                )
            )
        else:
            self.setWindowTitle(
                self.tr(
                    "Telefonnummer bearbeiten"
                )
            )

        self.resize(
            450,
            300,
        )

        self._create_ui()

        if self.phone_number is not None:
            self._load_phone_number()

    def _create_ui(self):
        main_layout = QVBoxLayout(
            self
        )

        form_layout = QFormLayout()

        self.type_combo = QComboBox()

        self.type_combo.addItem(
            self.tr("Mobil"),
            PhoneNumberType.MOBILE.value,
        )

        self.type_combo.addItem(
            self.tr("Privat"),
            PhoneNumberType.PRIVATE.value,
        )

        self.type_combo.addItem(
            self.tr("Geschäft"),
            PhoneNumberType.BUSINESS.value,
        )

        self.type_combo.addItem(
            self.tr("Andere"),
            PhoneNumberType.OTHER.value,
        )

        self.number_edit = QLineEdit()

        self.number_edit.setPlaceholderText(
            self.tr(
                "z. B. 079 123 45 67"
            )
        )

        self.primary_checkbox = QCheckBox(
            self.tr(
                "Als Primärnummer verwenden"
            )
        )

        self.notes_edit = QTextEdit()

        self.notes_edit.setMaximumHeight(
            100
        )

        form_layout.addRow(
            self.tr("Typ:"),
            self.type_combo,
        )

        form_layout.addRow(
            self.tr("Telefonnummer:"),
            self.number_edit,
        )

        form_layout.addRow(
            "",
            self.primary_checkbox,
        )

        form_layout.addRow(
            self.tr("Bemerkungen:"),
            self.notes_edit,
        )

        main_layout.addLayout(
            form_layout
        )

        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
        )

        self.button_box.accepted.connect(
            self._accept
        )

        self.button_box.rejected.connect(
            self.reject
        )

        main_layout.addWidget(
            self.button_box
        )

    def _load_phone_number(self):
        if self.phone_number is None:
            return

        index = self.type_combo.findData(
            self.phone_number.typ.value
        )

        if index >= 0:
            self.type_combo.setCurrentIndex(
                index
            )

        self.number_edit.setText(
            PhoneNumberService.format_for_display(
                self.phone_number.nummer_e164
            )
        )

        self.primary_checkbox.setChecked(
            self.phone_number.ist_primaer
        )

        self.notes_edit.setPlainText(
            self.phone_number.bemerkungen or ""
        )

    def _accept(self):
        number = (
            self.number_edit.text().strip()
        )

        if not number:
            QMessageBox.warning(
                self,
                self.tr(
                    "Ungültige Eingabe"
                ),
                self.tr(
                    "Bitte geben Sie eine "
                    "Telefonnummer ein."
                ),
            )

            self.number_edit.setFocus()
            return

        try:
            PhoneNumberService.normalize_phone_number(
                number
            )

        except ValueError as exc:
            QMessageBox.warning(
                self,
                self.tr(
                    "Ungültige Telefonnummer"
                ),
                str(exc),
            )

            self.number_edit.setFocus()
            return

        self.accept()

    def get_data(
        self,
    ) -> dict:
        return {
            "typ": PhoneNumberType(
                self.type_combo.currentData()
            ),
            "nummer": (
                self.number_edit.text().strip()
            ),
            "ist_primaer": (
                self.primary_checkbox.isChecked()
            ),
            "bemerkungen": (
                self.notes_edit
                .toPlainText()
                .strip()
                or None
            ),
        }