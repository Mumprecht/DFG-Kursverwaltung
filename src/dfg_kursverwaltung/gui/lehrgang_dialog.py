from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from dfg_kursverwaltung.core.models import Course
from dfg_kursverwaltung.services.lehrgangstypen_service import (
    CourseTypeService,
)


class LehrgangDialog(QDialog):
    def __init__(
        self,
        course_type_service: CourseTypeService,
        course: Course | None = None,
        parent: QWidget | None = None,
    ):
        super().__init__(parent)

        self.course_type_service = course_type_service
        self.course = course

        self.setModal(True)
        self.resize(560, 520)

        self._create_ui()

        if self.course is not None:
            self._load_course()

    def _create_ui(self):
        if self.course is None:
            self.setWindowTitle(
                self.tr("Neuer Lehrgang")
            )
        else:
            self.setWindowTitle(
                self.tr("Lehrgang bearbeiten")
            )

        main_layout = QVBoxLayout(self)

        title = QLabel(
            self.windowTitle()
        )

        title.setStyleSheet(
            "font-size: 20px; "
            "font-weight: bold;"
        )

        main_layout.addWidget(
            title
        )

        form = QFormLayout()

        self.type_combo = QComboBox()

        self._load_course_types()

        self.name_edit = QLineEdit()

        self.description_edit = QTextEdit()
        self.description_edit.setMinimumHeight(
            120
        )

        self.notes_edit = QTextEdit()
        self.notes_edit.setMinimumHeight(
            100
        )

        self.name_edit.setPlaceholderText(
            self.tr("Bezeichnung des Lehrgangs")
        )

        form.addRow(
            self.tr("Typ:"),
            self.type_combo,
        )

        form.addRow(
            self.tr("Bezeichnung:"),
            self.name_edit,
        )

        form.addRow(
            self.tr("Beschreibung:"),
            self.description_edit,
        )

        form.addRow(
            self.tr("Bemerkungen:"),
            self.notes_edit,
        )

        main_layout.addLayout(
            form
        )

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

        self.name_edit.setFocus()

    def _load_course_types(self):
        self.type_combo.clear()

        course_types = (
            self.course_type_service.list_course_types(
                include_inactive=False
            )
        )

        for course_type in course_types:
            self.type_combo.addItem(
                course_type.bezeichnung,
                course_type.id,
            )

        # Beim Bearbeiten kann ein inzwischen deaktivierter
        # Lehrgangstyp weiterhin am bestehenden Lehrgang hängen.
        if self.course is not None:
            current_type = (
                self.course_type_service.get_course_type(
                    self.course.lehrgangstyp_id
                )
            )

            if (
                current_type is not None
                and self.type_combo.findData(
                    current_type.id
                ) < 0
            ):
                self.type_combo.addItem(
                    current_type.bezeichnung,
                    current_type.id,
                )

    def _load_course(self):
        if self.course is None:
            return

        type_index = self.type_combo.findData(
            self.course.lehrgangstyp_id
        )

        if type_index >= 0:
            self.type_combo.setCurrentIndex(
                type_index
            )

        self.name_edit.setText(
            self.course.bezeichnung
        )

        self.description_edit.setPlainText(
            self.course.beschreibung or ""
        )

        self.notes_edit.setPlainText(
            self.course.bemerkungen or ""
        )

    def _validate_and_accept(self):
        course_type_id = (
            self.type_combo.currentData()
        )

        if not course_type_id:
            QMessageBox.warning(
                self,
                self.tr("Eingabe fehlt"),
                self.tr(
                    "Bitte wählen Sie einen Lehrgangstyp aus."
                ),
            )

            self.type_combo.setFocus()
            return

        name = self.name_edit.text().strip()

        if not name:
            QMessageBox.warning(
                self,
                self.tr("Eingabe fehlt"),
                self.tr(
                    "Bitte geben Sie eine Bezeichnung ein."
                ),
            )

            self.name_edit.setFocus()
            return

        self.accept()

    def get_data(self) -> dict:
        return {
            "lehrgangstyp_id": (
                self.type_combo.currentData()
            ),
            "bezeichnung": (
                self.name_edit.text().strip()
            ),
            "beschreibung": (
                self._optional_text(
                    self.description_edit.toPlainText()
                )
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