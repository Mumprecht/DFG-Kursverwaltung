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

from dfg_kursverwaltung.core.models import (
    Course,
    CourseType,
)


class LehrgangDialog(QDialog):
    def __init__(
        self,
        course: Course | None = None,
        parent: QWidget | None = None,
    ):
        super().__init__(parent)

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

        self.type_combo.addItem(
            self.tr("Einführungstag"),
            CourseType.INTRODUCTORY_DAY.value,
        )

        self.type_combo.addItem(
            self.tr("Kurs"),
            CourseType.COURSE.value,
        )

        self.type_combo.addItem(
            self.tr("Prüfung"),
            CourseType.EXAM.value,
        )

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

    def _load_course(self):
        if self.course is None:
            return

        type_index = self.type_combo.findData(
            self.course.typ.value
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
        type_value = self.type_combo.currentData()

        return {
            "typ": CourseType(
                type_value
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