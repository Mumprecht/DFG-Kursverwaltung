from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QGroupBox,
    QLabel,
    QLineEdit,
    QMessageBox,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from dfg_kursverwaltung.core.models import Location
from dfg_kursverwaltung.services.standorte_service import (
    LocationService,
)


class StandortDialog(QDialog):
    def __init__(
        self,
        location: Location | None = None,
        parent: QWidget | None = None,
    ):
        super().__init__(parent)

        self.location = location

        self.setModal(True)
        self.resize(560, 650)

        self._create_ui()

        if self.location is not None:
            self._load_location()

    def _create_ui(self):
        if self.location is None:
            self.setWindowTitle(
                self.tr("Neuer Ausführungsort")
            )
        else:
            self.setWindowTitle(
                self.tr("Ausführungsort bearbeiten")
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

        # Standort
        location_group = QGroupBox(
            self.tr("Standort")
        )
        location_form = QFormLayout(
            location_group
        )

        self.name_edit = QLineEdit()
        self.street_edit = QLineEdit()
        self.house_number_edit = QLineEdit()
        self.postal_code_edit = QLineEdit()
        self.city_edit = QLineEdit()

        location_form.addRow(
            self.tr("Bezeichnung:"),
            self.name_edit,
        )
        location_form.addRow(
            self.tr("Strasse:"),
            self.street_edit,
        )
        location_form.addRow(
            self.tr("Hausnummer:"),
            self.house_number_edit,
        )
        location_form.addRow(
            self.tr("PLZ:"),
            self.postal_code_edit,
        )
        location_form.addRow(
            self.tr("Ort:"),
            self.city_edit,
        )

        main_layout.addWidget(
            location_group
        )

        # Kontakt
        contact_group = QGroupBox(
            self.tr("Kontakt")
        )
        contact_form = QFormLayout(
            contact_group
        )

        self.first_name_edit = QLineEdit()
        self.last_name_edit = QLineEdit()
        self.phone_edit = QLineEdit()
        self.email_edit = QLineEdit()
        self.website_edit = QLineEdit()

        self.phone_edit.setPlaceholderText(
            self.tr(
                "z. B. +41 79 123 45 67"
            )
        )

        self.email_edit.setPlaceholderText(
            self.tr(
                "name@example.ch"
            )
        )

        self.website_edit.setPlaceholderText(
            self.tr(
                "https://www.example.ch"
            )
        )

        contact_form.addRow(
            self.tr("Vorname:"),
            self.first_name_edit,
        )
        contact_form.addRow(
            self.tr("Nachname:"),
            self.last_name_edit,
        )
        contact_form.addRow(
            self.tr("Telefon:"),
            self.phone_edit,
        )
        contact_form.addRow(
            self.tr("E-Mail:"),
            self.email_edit,
        )
        contact_form.addRow(
            self.tr("Webseite:"),
            self.website_edit,
        )

        main_layout.addWidget(
            contact_group
        )

        # Weitere Angaben
        other_group = QGroupBox(
            self.tr("Weitere Angaben")
        )
        other_form = QFormLayout(
            other_group
        )

        self.notes_edit = QTextEdit()
        self.notes_edit.setMinimumHeight(
            90
        )

        self.active_checkbox = QCheckBox(
            self.tr("Standort ist aktiv")
        )
        self.active_checkbox.setChecked(
            True
        )

        other_form.addRow(
            self.tr("Bemerkungen:"),
            self.notes_edit,
        )
        other_form.addRow(
            "",
            self.active_checkbox,
        )

        main_layout.addWidget(
            other_group
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

    def _load_location(self):
        if self.location is None:
            return

        self.name_edit.setText(
            self.location.bezeichnung
        )
        self.street_edit.setText(
            self.location.strasse or ""
        )
        self.house_number_edit.setText(
            self.location.hausnummer or ""
        )
        self.postal_code_edit.setText(
            self.location.plz or ""
        )
        self.city_edit.setText(
            self.location.ort or ""
        )

        self.first_name_edit.setText(
            self.location.kontakt_vorname or ""
        )
        self.last_name_edit.setText(
            self.location.kontakt_nachname or ""
        )

        self.phone_edit.setText(
            LocationService.format_phone_for_display(
                self.location.telefon_e164
            )
        )

        self.email_edit.setText(
            self.location.email or ""
        )
        self.website_edit.setText(
            self.location.webseite or ""
        )
        self.notes_edit.setPlainText(
            self.location.bemerkungen or ""
        )
        self.active_checkbox.setChecked(
            self.location.aktiv
        )

    def _validate_and_accept(self):
        if not self.name_edit.text().strip():
            QMessageBox.warning(
                self,
                self.tr(
                    "Fehlende Bezeichnung"
                ),
                self.tr(
                    "Bitte geben Sie eine "
                    "Bezeichnung für den "
                    "Ausführungsort ein."
                ),
            )
            self.name_edit.setFocus()
            return

        self.accept()

    def get_data(self) -> dict:
        return {
            "bezeichnung": (
                self.name_edit.text().strip()
            ),
            "strasse": self._optional_text(
                self.street_edit.text()
            ),
            "hausnummer": self._optional_text(
                self.house_number_edit.text()
            ),
            "plz": self._optional_text(
                self.postal_code_edit.text()
            ),
            "ort": self._optional_text(
                self.city_edit.text()
            ),
            "kontakt_vorname": (
                self._optional_text(
                    self.first_name_edit.text()
                )
            ),
            "kontakt_nachname": (
                self._optional_text(
                    self.last_name_edit.text()
                )
            ),
            "telefon": self._optional_text(
                self.phone_edit.text()
            ),
            "email": self._optional_text(
                self.email_edit.text()
            ),
            "webseite": self._optional_text(
                self.website_edit.text()
            ),
            "bemerkungen": (
                self._optional_text(
                    self.notes_edit.toPlainText()
                )
            ),
            "aktiv": (
                self.active_checkbox.isChecked()
            ),
        }

    @staticmethod
    def _optional_text(
        value: str,
    ) -> str | None:
        value = value.strip()
        return value or None