from PySide6.QtWidgets import (
    QButtonGroup,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QRadioButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from dfg_kursverwaltung.core.models import ExamResult


class PruefungsergebnisDialog(QDialog):
    def __init__(
        self,
        exam_result: ExamResult | None = None,
        parent: QWidget | None = None,
    ):
        super().__init__(parent)

        self.exam_result = exam_result

        if exam_result is None:
            self.setWindowTitle(
                self.tr(
                    "Kursergebnis erfassen"
                )
            )
        else:
            self.setWindowTitle(
                self.tr(
                    "Kursergebnis bearbeiten"
                )
            )

        self._create_ui()
        self._load_data()

    def _create_ui(self):
        layout = QVBoxLayout(self)

        form = QFormLayout()

        # ----------------------------------------------------
        # Kursergebnis
        # ----------------------------------------------------

        result_widget = QWidget()
        result_layout = QHBoxLayout(
            result_widget
        )

        result_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        self.passed_radio = QRadioButton(
            self.tr("Bestanden")
        )

        self.failed_radio = QRadioButton(
            self.tr("Nicht bestanden")
        )

        self.result_group = QButtonGroup(
            self
        )

        self.result_group.setExclusive(
            True
        )

        self.result_group.addButton(
            self.passed_radio
        )

        self.result_group.addButton(
            self.failed_radio
        )

        self.clear_result_button = QPushButton(
            self.tr("Auswahl löschen")
        )

        self.clear_result_button.clicked.connect(
            self._clear_result
        )

        result_layout.addWidget(
            self.passed_radio
        )

        result_layout.addWidget(
            self.failed_radio
        )

        result_layout.addWidget(
            self.clear_result_button
        )

        result_layout.addStretch()

        # ----------------------------------------------------
        # Note und Bemerkungen
        # ----------------------------------------------------

        self.grade_edit = QLineEdit()

        self.grade_edit.setPlaceholderText(
            self.tr("optional")
        )

        self.notes_edit = QTextEdit()

        self.notes_edit.setMaximumHeight(
            120
        )

        form.addRow(
            self.tr("Ergebnis:"),
            result_widget,
        )

        form.addRow(
            self.tr("Note:"),
            self.grade_edit,
        )

        form.addRow(
            self.tr("Bemerkungen:"),
            self.notes_edit,
        )

        layout.addLayout(form)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
        )

        ok_button = buttons.button(
            QDialogButtonBox.StandardButton.Ok
        )
        cancel_button = buttons.button(
            QDialogButtonBox.StandardButton.Cancel
        )

        if ok_button is not None:
            ok_button.setText(
                self.tr("OK")
            )

        if cancel_button is not None:
            cancel_button.setText(
                self.tr("Abbrechen")
            )

        buttons.accepted.connect(
            self.accept
        )

        buttons.rejected.connect(
            self.reject
        )

        layout.addWidget(buttons)

        self.resize(
            540,
            300,
        )

    def _load_data(self):
        if self.exam_result is None:
            return

        if self.exam_result.bestanden:
            self.passed_radio.setChecked(
                True
            )
        else:
            self.failed_radio.setChecked(
                True
            )

        self.grade_edit.setText(
            self.exam_result.note or ""
        )

        self.notes_edit.setPlainText(
            self.exam_result.bemerkungen or ""
        )

    def _clear_result(self):
        self.result_group.setExclusive(
            False
        )

        self.passed_radio.setChecked(
            False
        )

        self.failed_radio.setChecked(
            False
        )

        self.result_group.setExclusive(
            True
        )

    def get_data(self) -> dict:
        if self.passed_radio.isChecked():
            bestanden = True

        elif self.failed_radio.isChecked():
            bestanden = False

        else:
            bestanden = None

        return {
            "bestanden": bestanden,
            "note": self._optional_text(
                self.grade_edit.text()
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
