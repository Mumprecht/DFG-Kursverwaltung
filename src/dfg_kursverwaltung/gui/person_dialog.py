from datetime import date

from PySide6.QtCore import QDate
from PySide6.QtWidgets import (
    QCheckBox,
    QDateEdit,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from dfg_kursverwaltung.core.models import Person


class PersonDialog(QDialog):
    def __init__(
        self,
        person: Person | None = None,
        parent: QWidget | None = None,
    ):
        super().__init__(parent)

        self.person = person

        self.setModal(True)
        self.resize(600, 680)

        self._create_ui()

        if self.person is not None:
            self._load_person()

    def _create_ui(self):
        if self.person is None:
            self.setWindowTitle(
                self.tr("Neue Person")
            )
        else:
            self.setWindowTitle(
                self.tr("Person bearbeiten")
            )

        main_layout = QVBoxLayout(self)

        title = QLabel()

        if self.person is None:
            title.setText(
                self.tr("Neue Person")
            )
        else:
            title.setText(
                self.tr("Person bearbeiten")
            )

        title.setStyleSheet(
            "font-size: 20px; "
            "font-weight: bold;"
        )

        main_layout.addWidget(title)

        form = QFormLayout()

        self.first_name_edit = QLineEdit()
        self.last_name_edit = QLineEdit()

        self.birthdate_edit = QDateEdit()
        self.birthdate_edit.setCalendarPopup(True)
        self.birthdate_edit.setDisplayFormat(
            "dd.MM.yyyy"
        )

        self.birthdate_edit.setMinimumDate(
            QDate(1900, 1, 1)
        )

        self.birthdate_edit.setMaximumDate(
            QDate.currentDate()
        )

        # Ein spezielles Mindestdatum verwenden wir
        # als Kennzeichnung für "kein Geburtsdatum".
        self.birthdate_edit.setSpecialValueText(
            self.tr("Nicht angegeben")
        )

        self.birthdate_edit.setDate(
            self.birthdate_edit.minimumDate()
        )

        self.email_edit = QLineEdit()

        self.street_edit = QLineEdit()
        self.house_number_edit = QLineEdit()

        address_widget = QWidget()
        address_layout = QHBoxLayout(
            address_widget
        )
        address_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        address_layout.addWidget(
            self.street_edit,
            4,
        )

        address_layout.addWidget(
            self.house_number_edit,
            1,
        )

        self.postal_code_edit = QLineEdit()
        self.city_edit = QLineEdit()

        location_widget = QWidget()
        location_layout = QHBoxLayout(
            location_widget
        )
        location_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        location_layout.addWidget(
            self.postal_code_edit,
            1,
        )

        location_layout.addWidget(
            self.city_edit,
            3,
        )

        self.organisation_edit = QLineEdit()

        # -----------------------------------------------------
        # Status / Funktion
        # -----------------------------------------------------

        self.member_checkbox = QCheckBox(
            self.tr(
                "Person ist Mitglied der DFG Pfannenstiel"
            )
        )

        self.participant_checkbox = QCheckBox(
            self.tr(
                "Person ist Teilnehmer"
            )
        )

        self.instructor_checkbox = QCheckBox(
            self.tr(
                "Person ist Instruktor"
            )
        )

        status_widget = QWidget()
        status_layout = QVBoxLayout(
            status_widget
        )
        status_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        status_layout.addWidget(
            self.member_checkbox
        )
        status_layout.addWidget(
            self.participant_checkbox
        )
        status_layout.addWidget(
            self.instructor_checkbox
        )

        self.notes_edit = QTextEdit()
        self.notes_edit.setMinimumHeight(130)

        self.first_name_edit.setPlaceholderText(
            self.tr("Vorname")
        )

        self.last_name_edit.setPlaceholderText(
            self.tr("Nachname")
        )

        self.email_edit.setPlaceholderText(
            self.tr("name@beispiel.ch")
        )

        self.street_edit.setPlaceholderText(
            self.tr("Strasse")
        )

        self.house_number_edit.setPlaceholderText(
            self.tr("Nr.")
        )

        self.postal_code_edit.setPlaceholderText(
            self.tr("PLZ")
        )

        self.city_edit.setPlaceholderText(
            self.tr("Ort")
        )

        self.organisation_edit.setPlaceholderText(
            self.tr("Organisation / Firma")
        )

        form.addRow(
            self.tr("Vorname:"),
            self.first_name_edit,
        )

        form.addRow(
            self.tr("Nachname:"),
            self.last_name_edit,
        )

        form.addRow(
            self.tr("Geburtsdatum:"),
            self.birthdate_edit,
        )

        form.addRow(
            self.tr("E-Mail:"),
            self.email_edit,
        )

        form.addRow(
            self.tr("Adresse:"),
            address_widget,
        )

        form.addRow(
            self.tr("PLZ / Ort:"),
            location_widget,
        )

        form.addRow(
            self.tr("Organisation / Firma:"),
            self.organisation_edit,
        )

        form.addRow(
            self.tr("Status / Funktion:"),
            status_widget,
        )

        form.addRow(
            self.tr("Bemerkungen:"),
            self.notes_edit,
        )

        main_layout.addLayout(form)

        main_layout.addStretch()

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

        self.first_name_edit.setFocus()

    def _load_person(self):
        if self.person is None:
            return

        self.first_name_edit.setText(
            self.person.vorname
        )

        self.last_name_edit.setText(
            self.person.nachname
        )

        if self.person.geburtsdatum is not None:
            self.birthdate_edit.setDate(
                QDate(
                    self.person.geburtsdatum.year,
                    self.person.geburtsdatum.month,
                    self.person.geburtsdatum.day,
                )
            )
        else:
            self.birthdate_edit.setDate(
                self.birthdate_edit.minimumDate()
            )

        self.email_edit.setText(
            self.person.email or ""
        )

        self.street_edit.setText(
            self.person.strasse or ""
        )

        self.house_number_edit.setText(
            self.person.hausnummer or ""
        )

        self.postal_code_edit.setText(
            self.person.plz or ""
        )

        self.city_edit.setText(
            self.person.ort or ""
        )

        self.organisation_edit.setText(
            self.person.organisation or ""
        )

        self.member_checkbox.setChecked(
            self.person.mitglied
        )

        self.participant_checkbox.setChecked(
            self.person.ist_teilnehmer
        )

        self.instructor_checkbox.setChecked(
            self.person.ist_instruktor
        )

        self.notes_edit.setPlainText(
            self.person.bemerkungen or ""
        )

    def _validate_and_accept(self):
        first_name = (
            self.first_name_edit.text().strip()
        )

        last_name = (
            self.last_name_edit.text().strip()
        )

        if not first_name:
            QMessageBox.warning(
                self,
                self.tr("Eingabe fehlt"),
                self.tr(
                    "Bitte geben Sie einen Vornamen ein."
                ),
            )

            self.first_name_edit.setFocus()
            return

        if not last_name:
            QMessageBox.warning(
                self,
                self.tr("Eingabe fehlt"),
                self.tr(
                    "Bitte geben Sie einen Nachnamen ein."
                ),
            )

            self.last_name_edit.setFocus()
            return

        email = self.email_edit.text().strip()

        if email and (
            "@" not in email
            or "." not in email.split("@")[-1]
        ):
            QMessageBox.warning(
                self,
                self.tr("Ungültige E-Mail-Adresse"),
                self.tr(
                    "Bitte geben Sie eine gültige "
                    "E-Mail-Adresse ein."
                ),
            )

            self.email_edit.setFocus()
            return

        self.accept()

    def get_data(self) -> dict:
        birthdate: date | None

        if (
            self.birthdate_edit.date()
            == self.birthdate_edit.minimumDate()
        ):
            birthdate = None
        else:
            qt_date = self.birthdate_edit.date()

            birthdate = date(
                qt_date.year(),
                qt_date.month(),
                qt_date.day(),
            )

        return {
            "vorname": (
                self.first_name_edit.text().strip()
            ),
            "nachname": (
                self.last_name_edit.text().strip()
            ),
            "geburtsdatum": birthdate,
            "email": self._optional_text(
                self.email_edit.text()
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
            "organisation": self._optional_text(
                self.organisation_edit.text()
            ),
            "mitglied": (
                self.member_checkbox.isChecked()
            ),
            "ist_teilnehmer": (
                self.participant_checkbox.isChecked()
            ),
            "ist_instruktor": (
                self.instructor_checkbox.isChecked()
            ),
            "bemerkungen": self._optional_text(
                self.notes_edit.toPlainText()
            ),
        }

    @staticmethod
    def _optional_text(
        value: str,
    ) -> str | None:
        value = value.strip()

        return value or None