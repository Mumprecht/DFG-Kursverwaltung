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
    QSizePolicy,
    QSplitter,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from dfg_kursverwaltung.core.models import (
    Location,
    User,
)
from dfg_kursverwaltung.core.permissions import (
    Permission,
    has_permission,
)
from dfg_kursverwaltung.gui.standort_dialog import (
    StandortDialog,
)
from dfg_kursverwaltung.services.standorte_service import (
    LocationService,
)


class StandorteWidget(QWidget):
    def __init__(
        self,
        location_service: LocationService,
        authenticated_user: User,
        parent: QWidget | None = None,
    ):
        super().__init__(parent)

        self.location_service = location_service
        self.authenticated_user = authenticated_user
        self.can_write = has_permission(
            authenticated_user,
            Permission.LOCATION_WRITE,
        )

        self.current_location_id: str | None = None

        self._create_ui()
        self.load_locations()

    def _create_ui(self):
        main_layout = QVBoxLayout(self)

        title = QLabel(
            self.tr("Ausführungsorte")
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
                "Ausführungsort suchen..."
            )
        )

        self.search_edit.setClearButtonEnabled(
            True
        )

        self.search_edit.textChanged.connect(
            self._search_changed
        )

        self.include_inactive_checkbox = QCheckBox(
            self.tr(
                "Deaktivierte anzeigen"
            )
        )

        self.include_inactive_checkbox.toggled.connect(
            self.load_locations
        )

        self.location_list = QListWidget()

        self.location_list.setStyleSheet(
            """
            QListWidget::item:selected {
                background-color: #B8DDF5;
                color: black;
            }
            """
        )

        self.location_list.currentItemChanged.connect(
            self._location_selected
        )

        self.location_list.itemDoubleClicked.connect(
            self._location_double_clicked
        )

        button_layout = QHBoxLayout()

        self.new_button = QPushButton(
            self.tr("Neu")
        )

        self.edit_button = QPushButton(
            self.tr("Bearbeiten")
        )

        self.new_button.setEnabled(
            self.can_write
        )

        self.new_button.clicked.connect(
            self._new_location
        )

        self.edit_button.clicked.connect(
            self._edit_location
        )

        button_layout.addWidget(
            self.new_button
        )

        button_layout.addWidget(
            self.edit_button
        )

        layout.addWidget(
            self.search_edit
        )

        layout.addWidget(
            self.include_inactive_checkbox
        )

        layout.addWidget(
            self.location_list
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
            self.tr("Standortdetails")
        )

        self.detail_title.setStyleSheet(
            "font-size: 18px; "
            "font-weight: bold;"
        )

        layout.addWidget(
            self.detail_title
        )

        location_group = QGroupBox(
            self.tr("Standort")
        )

        location_group.setSizePolicy(
            QSizePolicy.Policy.Preferred,
            QSizePolicy.Policy.Maximum,
        )

        location_form = QFormLayout(
            location_group
        )

        self.name_value = QLabel("-")
        self.address_value = QLabel("-")
        self.status_value = QLabel("-")

        location_form.addRow(
            self.tr("Bezeichnung:"),
            self.name_value,
        )

        location_form.addRow(
            self.tr("Adresse:"),
            self.address_value,
        )

        location_form.addRow(
            self.tr("Status:"),
            self.status_value,
        )

        layout.addWidget(
            location_group
        )

        contact_group = QGroupBox(
            self.tr("Kontakt")
        )

        contact_group.setSizePolicy(
            QSizePolicy.Policy.Preferred,
            QSizePolicy.Policy.Maximum,
        )

        contact_form = QFormLayout(
            contact_group
        )

        self.contact_value = QLabel("-")
        self.phone_value = QLabel("-")
        self.email_value = QLabel("-")
        self.website_value = QLabel("-")

        contact_form.addRow(
            self.tr("Name:"),
            self.contact_value,
        )

        contact_form.addRow(
            self.tr("Telefon:"),
            self.phone_value,
        )

        contact_form.addRow(
            self.tr("E-Mail:"),
            self.email_value,
        )

        contact_form.addRow(
            self.tr("Webseite:"),
            self.website_value,
        )

        layout.addWidget(
            contact_group
        )

        notes_group = QGroupBox(
            self.tr("Bemerkungen")
        )

        notes_group.setSizePolicy(
            QSizePolicy.Policy.Preferred,
            QSizePolicy.Policy.Maximum,
        )

        notes_layout = QVBoxLayout(
            notes_group
        )

        self.notes_value = QTextEdit()
        self.notes_value.setReadOnly(
            True
        )
        self.notes_value.setMaximumHeight(
            120
        )

        notes_layout.addWidget(
            self.notes_value
        )

        layout.addWidget(
            notes_group
        )

        action_layout = QHBoxLayout()

        self.status_button = QPushButton()

        self.status_button.clicked.connect(
            self._toggle_active_status
        )

        action_layout.addWidget(
            self.status_button
        )

        action_layout.addStretch()

        layout.addLayout(
            action_layout
        )

        layout.addStretch()

        self._clear_details()

        return widget

    def load_locations(
        self,
        *_args,
    ):
        search_text = (
            self.search_edit.text().strip()
        )

        include_inactive = (
            self.include_inactive_checkbox
            .isChecked()
        )

        if search_text:
            locations = (
                self.location_service
                .search_locations(
                    search_text,
                    include_inactive=(
                        include_inactive
                    ),
                )
            )
        else:
            locations = (
                self.location_service
                .list_locations(
                    include_inactive=(
                        include_inactive
                    )
                )
            )

        selected_id = (
            self.current_location_id
        )

        self.location_list.blockSignals(
            True
        )

        self.location_list.clear()

        item_to_select = None

        for location in locations:
            item = QListWidgetItem(
                self._location_list_text(
                    location
                )
            )

            item.setData(
                Qt.ItemDataRole.UserRole,
                location.id,
            )

            if not location.aktiv:
                font = item.font()
                font.setStrikeOut(True)
                item.setFont(font)

            self.location_list.addItem(
                item
            )

            if location.id == selected_id:
                item_to_select = item

        self.location_list.blockSignals(
            False
        )

        if item_to_select is not None:
            self.location_list.setCurrentItem(
                item_to_select
            )

        elif self.location_list.count() > 0:
            self.location_list.setCurrentRow(
                0
            )

        else:
            self.current_location_id = None
            self._clear_details()

    def select_location(
        self,
        location_id: str,
    ):
        location = (
            self.location_service
            .get_location(
                location_id
            )
        )

        if location is None:
            return

        self.current_location_id = (
            location_id
        )

        self.search_edit.blockSignals(
            True
        )

        self.search_edit.clear()

        self.search_edit.blockSignals(
            False
        )

        if (
            not location.aktiv
            and not self.include_inactive_checkbox
            .isChecked()
        ):
            self.include_inactive_checkbox.blockSignals(
                True
            )

            self.include_inactive_checkbox.setChecked(
                True
            )

            self.include_inactive_checkbox.blockSignals(
                False
            )

        self.load_locations()

    def _search_changed(
        self,
        _text: str,
    ):
        self.load_locations()

    def _location_selected(
        self,
        current: QListWidgetItem | None,
        _previous: QListWidgetItem | None,
    ):
        if current is None:
            self.current_location_id = None
            self._clear_details()
            return

        location_id = current.data(
            Qt.ItemDataRole.UserRole
        )

        location = (
            self.location_service
            .get_location(
                location_id
            )
        )

        if location is None:
            self.current_location_id = None
            self._clear_details()
            return

        self.current_location_id = (
            location.id
        )

        self._show_location(
            location
        )

    def _show_location(
        self,
        location: Location,
    ):
        self.name_value.setText(
            location.bezeichnung
        )

        self.address_value.setText(
            location.adresse or "-"
        )

        self.contact_value.setText(
            location.kontakt_voller_name or "-"
        )

        self.phone_value.setText(
            self.location_service
            .format_phone_for_display(
                location.telefon_e164
            )
            or "-"
        )

        self.email_value.setText(
            location.email or "-"
        )

        self.website_value.setText(
            location.webseite or "-"
        )

        self.notes_value.setPlainText(
            location.bemerkungen or ""
        )

        if location.aktiv:
            self.status_value.setText(
                self.tr("Aktiv")
            )

            self.status_button.setText(
                self.tr("Deaktivieren")
            )

        else:
            self.status_value.setText(
                self.tr("Deaktiviert")
            )

            self.status_button.setText(
                self.tr("Wieder aktivieren")
            )

        self.edit_button.setEnabled(
            self.can_write
        )

        self.status_button.setEnabled(
            self.can_write
        )

    def _new_location(self):
        if not self.can_write:
            return

        dialog = StandortDialog(
            parent=self
        )

        if (
            dialog.exec()
            != QDialog.DialogCode.Accepted
        ):
            return

        data = dialog.get_data()

        active = data.pop(
            "aktiv"
        )

        try:
            location = (
                self.location_service
                .create_location(
                    **data
                )
            )

            if not active:
                self.location_service.deactivate_location(
                    location.id
                )
                location.aktiv = False

        except Exception as exc:
            QMessageBox.critical(
                self,
                self.tr("Fehler"),
                self.tr(
                    "Der Ausführungsort konnte "
                    "nicht gespeichert werden."
                )
                + "\n\n"
                + str(exc),
            )
            return

        self.current_location_id = (
            location.id
        )

        if (
            not location.aktiv
            and not self.include_inactive_checkbox
            .isChecked()
        ):
            self.include_inactive_checkbox.setChecked(
                True
            )

        self.search_edit.clear()

        self.load_locations()

    def _edit_location(self):
        if not self.can_write:
            return

        if self.current_location_id is None:
            return

        location = (
            self.location_service
            .get_location(
                self.current_location_id
            )
        )

        if location is None:
            return

        dialog = StandortDialog(
            location=location,
            parent=self,
        )

        if (
            dialog.exec()
            != QDialog.DialogCode.Accepted
        ):
            return

        data = dialog.get_data()

        requested_active = data.pop(
            "aktiv"
        )

        telefon = data.pop(
            "telefon"
        )

        location.bezeichnung = data[
            "bezeichnung"
        ]

        location.strasse = data[
            "strasse"
        ]

        location.hausnummer = data[
            "hausnummer"
        ]

        location.plz = data["plz"]
        location.ort = data["ort"]

        location.kontakt_vorname = data[
            "kontakt_vorname"
        ]

        location.kontakt_nachname = data[
            "kontakt_nachname"
        ]

        location.email = data["email"]

        location.webseite = data[
            "webseite"
        ]

        location.bemerkungen = data[
            "bemerkungen"
        ]

        try:
            location = (
                self.location_service
                .update_location(
                    location,
                    telefon=telefon,
                )
            )

            if requested_active != location.aktiv:
                if requested_active:
                    self.location_service.activate_location(
                        location.id
                    )
                else:
                    self.location_service.deactivate_location(
                        location.id
                    )

                location.aktiv = (
                    requested_active
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

        self.current_location_id = (
            location.id
        )

        self.load_locations()

    def _toggle_active_status(self):
        if not self.can_write:
            return

        if self.current_location_id is None:
            return

        location = (
            self.location_service
            .get_location(
                self.current_location_id
            )
        )

        if location is None:
            return

        try:
            if location.aktiv:
                self.location_service.deactivate_location(
                    location.id
                )
            else:
                self.location_service.activate_location(
                    location.id
                )

        except Exception as exc:
            QMessageBox.critical(
                self,
                self.tr("Fehler"),
                self.tr(
                    "Der Status konnte nicht "
                    "geändert werden."
                )
                + "\n\n"
                + str(exc),
            )
            return

        if (
            location.aktiv
            and not self.include_inactive_checkbox
            .isChecked()
        ):
            self.current_location_id = None

        else:
            self.current_location_id = (
                location.id
            )

        self.load_locations()

    def _location_double_clicked(
        self,
        item: QListWidgetItem,
    ):
        location_id = item.data(
            Qt.ItemDataRole.UserRole
        )

        if not location_id:
            return

        self.current_location_id = (
            location_id
        )

        self._edit_location()

    def _clear_details(self):
        self.name_value.setText("-")
        self.address_value.setText("-")
        self.status_value.setText("-")

        self.contact_value.setText("-")
        self.phone_value.setText("-")
        self.email_value.setText("-")
        self.website_value.setText("-")

        self.notes_value.clear()

        self.edit_button.setEnabled(
            False
        )

        self.status_button.setEnabled(
            False
        )

        self.status_button.setText(
            self.tr("Deaktivieren")
        )

    def _location_list_text(
        self,
        location: Location,
    ) -> str:
        if location.ort:
            return (
                f"{location.bezeichnung} "
                f"({location.ort})"
            )

        return location.bezeichnung