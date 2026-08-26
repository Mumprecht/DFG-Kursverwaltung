from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QCompleter,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QMessageBox,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from dfg_kursverwaltung.core.models import (
    CourseAssignment,
    CourseAssignmentRole,
    CourseAssignmentStatus,
    Person,
)


class KurszuordnungDialog(QDialog):
    def __init__(
        self,
        persons: list[Person],
        assignment: CourseAssignment | None = None,
        parent: QWidget | None = None,
    ):
        super().__init__(parent)

        self.persons = persons
        self.assignment = assignment

        self.setModal(True)
        self.resize(500, 400)

        self._create_ui()
        self._load_persons()

        if self.assignment is not None:
            self._load_assignment()

    def _create_ui(self):
        if self.assignment is None:
            self.setWindowTitle(
                self.tr("Person zuordnen")
            )
        else:
            self.setWindowTitle(
                self.tr("Kurszuordnung bearbeiten")
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

        form = QFormLayout()

        self.person_combo = QComboBox()

        self.person_combo.setEditable(
            True
        )

        self.person_combo.setInsertPolicy(
            QComboBox.InsertPolicy.NoInsert
        )

        completer = self.person_combo.completer()

        completer.setCompletionMode(
            QCompleter.CompletionMode.PopupCompletion
        )

        completer.setFilterMode(
            Qt.MatchFlag.MatchContains
        )

        completer.setCaseSensitivity(
            Qt.CaseSensitivity.CaseInsensitive
        )

        self.person_combo.currentIndexChanged.connect(
            self._person_changed
        )

        self.role_combo = QComboBox()

        self.status_combo = QComboBox()
        self.status_combo.addItem(
            self.tr("Angemeldet"),
            CourseAssignmentStatus.REGISTERED,
        )
        self.status_combo.addItem(
            self.tr("Teilgenommen"),
            CourseAssignmentStatus.ATTENDED,
        )
        self.status_combo.addItem(
            self.tr("Nicht erschienen"),
            CourseAssignmentStatus.ABSENT,
        )
        self.status_combo.addItem(
            self.tr("Abgemeldet"),
            CourseAssignmentStatus.CANCELLED,
        )

        self.notes_edit = QTextEdit()
        self.notes_edit.setMinimumHeight(100)

        form.addRow(
            self.tr("Person:"),
            self.person_combo,
        )
        form.addRow(
            self.tr("Rolle:"),
            self.role_combo,
        )
        form.addRow(
            self.tr("Status:"),
            self.status_combo,
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

    def _load_persons(self):
        self.person_combo.clear()

        sorted_persons = sorted(
            self.persons,
            key=lambda person: (
                person.nachname.casefold(),
                person.vorname.casefold(),
            ),
        )

        for person in sorted_persons:
            self.person_combo.addItem(
                f"{person.nachname} {person.vorname}",
                person.id,
            )

        self._update_roles()

    def _person_changed(
        self,
        _index: int,
    ):
        self._update_roles()

    def _update_roles(self):
        current_person_id = (
            self.person_combo.currentData()
        )

        previous_role = (
            self.role_combo.currentData()
        )

        self.role_combo.clear()

        if current_person_id is None:
            return

        person = next(
            (
                person
                for person in self.persons
                if person.id == current_person_id
            ),
            None,
        )

        if person is None:
            return

        if person.ist_teilnehmer:
            self.role_combo.addItem(
                self.tr("Teilnehmer"),
                CourseAssignmentRole.PARTICIPANT,
            )

        if person.ist_instruktor:
            self.role_combo.addItem(
                self.tr("Instruktor"),
                CourseAssignmentRole.INSTRUCTOR,
            )

        if previous_role is not None:
            role_index = (
                self.role_combo.findData(
                    previous_role
                )
            )

            if role_index >= 0:
                self.role_combo.setCurrentIndex(
                    role_index
                )

    def _load_assignment(self):
        if self.assignment is None:
            return

        person_index = (
            self.person_combo.findData(
                self.assignment.person_id
            )
        )

        if person_index >= 0:
            self.person_combo.setCurrentIndex(
                person_index
            )

        self._update_roles()

        # Beim Bearbeiten wird die Person nicht
        # gewechselt. Damit verhindern wir
        # versehentliche Umzuordnungen.
        self.person_combo.setEnabled(False)

        role_index = (
            self.role_combo.findData(
                self.assignment.rolle
            )
        )

        if role_index >= 0:
            self.role_combo.setCurrentIndex(
                role_index
            )

        status_index = (
            self.status_combo.findData(
                self.assignment.status
            )
        )

        if status_index >= 0:
            self.status_combo.setCurrentIndex(
                status_index
            )

        self.notes_edit.setPlainText(
            self.assignment.bemerkungen or ""
        )

    def _validate_and_accept(self):
        if self.person_combo.currentData() is None:
            QMessageBox.warning(
                self,
                self.tr("Keine Person"),
                self.tr(
                    "Bitte wählen Sie eine Person aus."
                ),
            )
            return

        if self.role_combo.currentData() is None:
            QMessageBox.warning(
                self,
                self.tr("Keine Rolle"),
                self.tr(
                    "Der ausgewählten Person ist "
                    "keine für Kurszuordnungen "
                    "zulässige Rolle zugeordnet."
                ),
            )
            return

        self.accept()

    def get_data(self) -> dict:
        return {
            "person_id": (
                self.person_combo.currentData()
            ),
            "rolle": (
                self.role_combo.currentData()
            ),
            "status": (
                self.status_combo.currentData()
            ),
            "bemerkungen": (
                self._optional_text(
                    self.notes_edit.toPlainText()
                )
            ),
        }

    @staticmethod
    def _optional_text(
        value: str,
    ) -> str | None:
        value = value.strip()

        return value or None