from PySide6.QtWidgets import (
    QCheckBox,
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

from dfg_kursverwaltung.core.models import CourseType


class LehrgangstypDialog(QDialog):
    def __init__(
        self,
        course_type: CourseType | None = None,
        parent: QWidget | None = None,
    ):
        super().__init__(parent)

        self.course_type = course_type

        self.setModal(True)
        self.resize(500, 360)

        self._create_ui()

        if self.course_type is not None:
            self._load_course_type()

    def _create_ui(self):
        if self.course_type is None:
            self.setWindowTitle(
                self.tr("Neuer Lehrgangstyp")
            )
        else:
            self.setWindowTitle(
                self.tr("Lehrgangstyp bearbeiten")
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

        self.name_edit = QLineEdit()

        self.name_edit.setPlaceholderText(
            self.tr(
                "Bezeichnung des Lehrgangstyps"
            )
        )

        self.active_checkbox = QCheckBox(
            self.tr("Aktiv")
        )

        self.active_checkbox.setChecked(
            True
        )

        self.notes_edit = QTextEdit()

        self.notes_edit.setMinimumHeight(
            120
        )

        form.addRow(
            self.tr("Bezeichnung:"),
            self.name_edit,
        )

        form.addRow(
            self.tr("Status:"),
            self.active_checkbox,
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

    def _load_course_type(self):
        if self.course_type is None:
            return

        self.name_edit.setText(
            self.course_type.bezeichnung
        )

        self.active_checkbox.setChecked(
            self.course_type.aktiv
        )

        self.notes_edit.setPlainText(
            self.course_type.bemerkungen or ""
        )

    def _validate_and_accept(self):
        name = self.name_edit.text().strip()

        if not name:
            QMessageBox.warning(
                self,
                self.tr("Eingabe fehlt"),
                self.tr(
                    "Bitte geben Sie eine "
                    "Bezeichnung ein."
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
            "aktiv": (
                self.active_checkbox.isChecked()
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
