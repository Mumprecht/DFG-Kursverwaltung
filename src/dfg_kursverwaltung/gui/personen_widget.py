from datetime import date

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
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from dfg_kursverwaltung.core.models import Person
from dfg_kursverwaltung.gui.person_dialog import (
    PersonDialog,
)
from dfg_kursverwaltung.services.personen_service import (
    PersonService,
)


class PersonenWidget(QWidget):
    def __init__(
        self,
        person_service: PersonService,
        parent: QWidget | None = None,
    ):
        super().__init__(parent)

        self.person_service = person_service
        self.current_person_id: str | None = None

        self._create_ui()
        self.load_persons()

    def _create_ui(self):
        main_layout = QVBoxLayout(self)

        title = QLabel(
            self.tr("Personen")
        )

        title.setStyleSheet(
            "font-size: 22px; font-weight: bold;"
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

        main_layout.addWidget(splitter)

    def _create_list_area(
        self,
    ) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)

        self.search_edit = QLineEdit()

        self.search_edit.setPlaceholderText(
            self.tr("Person suchen...")
        )

        self.search_edit.setClearButtonEnabled(
            True
        )

        self.search_edit.textChanged.connect(
            self._search_changed
        )

        self.person_list = QListWidget()

        self.person_list.currentItemChanged.connect(
            self._person_selected
        )

        self.show_inactive_checkbox = QCheckBox(
            self.tr(
                "Inaktive Personen anzeigen"
            )
        )

        self.show_inactive_checkbox.toggled.connect(
            self.load_persons
        )

        button_layout = QHBoxLayout()

        self.new_button = QPushButton(
            self.tr("Neu")
        )

        self.edit_button = QPushButton(
            self.tr("Bearbeiten")
        )

        self.active_button = QPushButton(
            self.tr("Deaktivieren")
        )

        self.new_button.clicked.connect(
            self._new_person
        )

        self.edit_button.clicked.connect(
            self._edit_person
        )

        self.active_button.clicked.connect(
            self._toggle_active_status
        )

        button_layout.addWidget(
            self.new_button
        )

        button_layout.addWidget(
            self.edit_button
        )

        button_layout.addWidget(
            self.active_button
        )

        layout.addWidget(
            self.search_edit
        )

        layout.addWidget(
            self.person_list
        )

        layout.addWidget(
            self.show_inactive_checkbox
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
            self.tr("Personendetails")
        )

        self.detail_title.setStyleSheet(
            "font-size: 18px; "
            "font-weight: bold;"
        )

        layout.addWidget(
            self.detail_title
        )

        master_data_group = QGroupBox(
            self.tr("Stammdaten")
        )

        form = QFormLayout(
            master_data_group
        )

        self.name_value = QLabel("-")
        self.birthdate_value = QLabel("-")
        self.email_value = QLabel("-")
        self.address_value = QLabel("-")
        self.location_value = QLabel("-")
        self.organisation_value = QLabel("-")
        self.member_value = QLabel("-")
        self.active_value = QLabel("-")

        form.addRow(
            self.tr("Name:"),
            self.name_value,
        )

        form.addRow(
            self.tr("Geburtsdatum:"),
            self.birthdate_value,
        )

        form.addRow(
            self.tr("E-Mail:"),
            self.email_value,
        )

        form.addRow(
            self.tr("Adresse:"),
            self.address_value,
        )

        form.addRow(
            self.tr("PLZ / Ort:"),
            self.location_value,
        )

        form.addRow(
            self.tr(
                "Organisation / Firma:"
            ),
            self.organisation_value,
        )

        form.addRow(
            self.tr("DFG-Mitglied:"),
            self.member_value,
        )

        form.addRow(
            self.tr("Aktiv:"),
            self.active_value,
        )

        layout.addWidget(
            master_data_group
        )

        notes_group = QGroupBox(
            self.tr("Bemerkungen")
        )

        notes_layout = QVBoxLayout(
            notes_group
        )

        self.notes_value = QTextEdit()
        self.notes_value.setReadOnly(True)
        self.notes_value.setMaximumHeight(90)

        notes_layout.addWidget(
            self.notes_value
        )

        layout.addWidget(
            notes_group
        )

        course_group = QGroupBox(
            self.tr("Kursteilnahmen")
        )

        course_layout = QVBoxLayout(
            course_group
        )

        self.course_participation_list = (
            QListWidget()
        )

        self.course_participation_list.setMaximumHeight(
            140
        )

        self.course_participation_placeholder = (
            QListWidgetItem(
                self.tr(
                    "Noch keine Kursteilnahmen vorhanden."
                )
            )
        )

        self.course_participation_list.addItem(
            self.course_participation_placeholder
        )

        course_layout.addWidget(
            self.course_participation_list
        )

        layout.addWidget(
            course_group
        )

        phone_group = QGroupBox(
            self.tr("Telefonnummern")
        )

        phone_layout = QVBoxLayout(
            phone_group
        )

        self.phone_placeholder = QLabel(
            self.tr(
                "Die Telefonnummern werden "
                "im nächsten Ausbauschritt eingebunden."
            )
        )

        phone_layout.addWidget(
            self.phone_placeholder
        )

        layout.addWidget(
            phone_group
        )

        drone_group = QGroupBox(
            self.tr("Drohnen")
        )

        drone_layout = QVBoxLayout(
            drone_group
        )

        self.drone_placeholder = QLabel(
            self.tr(
                "Die Drohnen werden "
                "im nächsten Ausbauschritt eingebunden."
            )
        )

        drone_layout.addWidget(
            self.drone_placeholder
        )

        layout.addWidget(
            drone_group
        )

        layout.addStretch()

        self._clear_details()

        return widget

    def load_persons(
        self,
        *_args,
    ):
        search_text = (
            self.search_edit.text().strip()
        )

        include_inactive = (
            self.show_inactive_checkbox.isChecked()
        )

        if search_text:
            persons = (
                self.person_service.search_persons(
                    search_text,
                    include_inactive=include_inactive,
                )
            )
        else:
            persons = (
                self.person_service.list_persons(
                    include_inactive=include_inactive,
                )
            )

        selected_id = self.current_person_id

        self.person_list.blockSignals(True)
        self.person_list.clear()

        item_to_select = None

        for person in persons:
            item = QListWidgetItem(
                self._person_list_text(
                    person
                )
            )

            item.setData(
                Qt.ItemDataRole.UserRole,
                person.id,
            )

            if not person.aktiv:
                font = item.font()
                font.setItalic(True)
                item.setFont(font)

            self.person_list.addItem(
                item
            )

            if person.id == selected_id:
                item_to_select = item

        self.person_list.blockSignals(False)

        if item_to_select is not None:
            self.person_list.setCurrentItem(
                item_to_select
            )

        elif self.person_list.count() > 0:
            self.person_list.setCurrentRow(0)

        else:
            self.current_person_id = None
            self._clear_details()

    def _search_changed(
        self,
        _text: str,
    ):
        self.load_persons()

    def _person_selected(
        self,
        current: QListWidgetItem | None,
        _previous: QListWidgetItem | None,
    ):
        if current is None:
            self.current_person_id = None
            self._clear_details()
            return

        person_id = current.data(
            Qt.ItemDataRole.UserRole
        )

        person = self.person_service.get_person(
            person_id
        )

        if person is None:
            self.current_person_id = None
            self._clear_details()
            return

        self.current_person_id = person.id

        self._show_person(
            person
        )

    def _show_person(
        self,
        person: Person,
    ):
        self.name_value.setText(
            person.voller_name
        )

        self.birthdate_value.setText(
            self._format_date(
                person.geburtsdatum
            )
        )

        self.email_value.setText(
            person.email or "-"
        )

        address_parts = [
            value
            for value in (
                person.strasse,
                person.hausnummer,
            )
            if value
        ]

        self.address_value.setText(
            " ".join(address_parts)
            if address_parts
            else "-"
        )

        location_parts = [
            value
            for value in (
                person.plz,
                person.ort,
            )
            if value
        ]

        self.location_value.setText(
            " ".join(location_parts)
            if location_parts
            else "-"
        )

        self.organisation_value.setText(
            person.organisation or "-"
        )

        self.member_value.setText(
            self.tr("Ja")
            if person.mitglied
            else self.tr("Nein")
        )

        self.active_value.setText(
            self.tr("Ja")
            if person.aktiv
            else self.tr("Nein")
        )

        self.notes_value.setPlainText(
            person.bemerkungen or ""
        )

        self.edit_button.setEnabled(True)
        self.active_button.setEnabled(True)

        if person.aktiv:
            self.active_button.setText(
                self.tr("Deaktivieren")
            )
        else:
            self.active_button.setText(
                self.tr("Aktivieren")
            )

        self._load_course_participations()

    def _load_course_participations(self):
        self.course_participation_list.clear()

        item = QListWidgetItem(
            self.tr(
                "Noch keine Kursteilnahmen vorhanden."
            )
        )

        self.course_participation_list.addItem(
            item
        )

    def _clear_details(self):
        self.name_value.setText("-")
        self.birthdate_value.setText("-")
        self.email_value.setText("-")
        self.address_value.setText("-")
        self.location_value.setText("-")
        self.organisation_value.setText("-")
        self.member_value.setText("-")
        self.active_value.setText("-")

        self.notes_value.clear()

        self.course_participation_list.clear()

        self.edit_button.setEnabled(False)
        self.active_button.setEnabled(False)

        self.active_button.setText(
            self.tr("Deaktivieren")
        )

    def _new_person(self):
        dialog = PersonDialog(
            parent=self
        )

        if (
            dialog.exec()
            != QDialog.DialogCode.Accepted
        ):
            return

        data = dialog.get_data()

        try:
            person = (
                self.person_service.create_person(
                    **data
                )
            )

        except Exception as exc:
            QMessageBox.critical(
                self,
                self.tr("Fehler"),
                self.tr(
                    "Die Person konnte nicht "
                    "gespeichert werden."
                )
                + "\n\n"
                + str(exc),
            )
            return

        self.current_person_id = person.id

        self.search_edit.clear()

        self.load_persons()

    def _edit_person(self):
        if self.current_person_id is None:
            return

        person = (
            self.person_service.get_person(
                self.current_person_id
            )
        )

        if person is None:
            return

        dialog = PersonDialog(
            person=person,
            parent=self,
        )

        if (
            dialog.exec()
            != QDialog.DialogCode.Accepted
        ):
            return

        data = dialog.get_data()

        person.vorname = data["vorname"]
        person.nachname = data["nachname"]
        person.geburtsdatum = data[
            "geburtsdatum"
        ]
        person.email = data["email"]
        person.strasse = data["strasse"]
        person.hausnummer = data[
            "hausnummer"
        ]
        person.plz = data["plz"]
        person.ort = data["ort"]
        person.organisation = data[
            "organisation"
        ]
        person.mitglied = data["mitglied"]
        person.bemerkungen = data[
            "bemerkungen"
        ]

        try:
            updated_person = (
                self.person_service.update_person(
                    person
                )
            )

        except Exception as exc:
            QMessageBox.critical(
                self,
                self.tr("Fehler"),
                str(exc),
            )
            return

        self.current_person_id = (
            updated_person.id
        )

        self.load_persons()

    def _toggle_active_status(self):
        if self.current_person_id is None:
            return

        person = (
            self.person_service.get_person(
                self.current_person_id
            )
        )

        if person is None:
            return

        if person.aktiv:
            title = self.tr(
                "Person deaktivieren"
            )

            text = self.tr(
                'Soll die Person "%1" wirklich '
                "deaktiviert werden?\n\n"
                "Historische Kursdaten bleiben erhalten."
            ).replace(
                "%1",
                person.voller_name,
            )

        else:
            title = self.tr(
                "Person aktivieren"
            )

            text = self.tr(
                'Soll die Person "%1" wieder '
                "aktiviert werden?"
            ).replace(
                "%1",
                person.voller_name,
            )

        answer = QMessageBox.question(
            self,
            title,
            text,
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
            if person.aktiv:
                self.person_service.deactivate_person(
                    person.id
                )
            else:
                self.person_service.activate_person(
                    person.id
                )

        except Exception as exc:
            QMessageBox.critical(
                self,
                self.tr("Fehler"),
                str(exc),
            )
            return

        if (
            person.aktiv
            and not self.show_inactive_checkbox.isChecked()
        ):
            self.current_person_id = None

        self.load_persons()

    @staticmethod
    def _person_list_text(
        person: Person,
    ) -> str:
        text = (
            f"{person.nachname}, "
            f"{person.vorname}"
        )

        if person.organisation:
            text += (
                f" – {person.organisation}"
            )

        return text

    @staticmethod
    def _format_date(
        value: date | None,
    ) -> str:
        if value is None:
            return "-"

        return value.strftime(
            "%d.%m.%Y"
        )