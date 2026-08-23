from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLineEdit,
    QMessageBox,
    QTextEdit,
    QVBoxLayout,
)

from dfg_kursverwaltung.core.models import (
    Drone,
)


class DroneDialog(QDialog):
    def __init__(
        self,
        drone: Drone | None = None,
        parent=None,
    ):
        super().__init__(parent)

        self.drone = drone

        if drone is None:
            self.setWindowTitle(
                self.tr("Drohne hinzufügen")
            )
        else:
            self.setWindowTitle(
                self.tr("Drohne bearbeiten")
            )

        self.resize(
            500,
            300,
        )

        self._create_ui()

        if self.drone is not None:
            self._load_drone()

    def _create_ui(self):
        main_layout = QVBoxLayout(
            self
        )

        form_layout = QFormLayout()

        self.manufacturer_edit = QLineEdit()

        self.manufacturer_edit.setPlaceholderText(
            self.tr(
                "z. B. DJI"
            )
        )

        self.model_edit = QLineEdit()

        self.model_edit.setPlaceholderText(
            self.tr(
                "z. B. Mini 4 Pro"
            )
        )

        self.serial_number_edit = QLineEdit()

        self.serial_number_edit.setPlaceholderText(
            self.tr(
                "Seriennummer"
            )
        )

        self.notes_edit = QTextEdit()

        self.notes_edit.setMaximumHeight(
            100
        )

        form_layout.addRow(
            self.tr("Hersteller:"),
            self.manufacturer_edit,
        )

        form_layout.addRow(
            self.tr("Modell:"),
            self.model_edit,
        )

        form_layout.addRow(
            self.tr("Seriennummer:"),
            self.serial_number_edit,
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

    def _load_drone(self):
        if self.drone is None:
            return

        self.manufacturer_edit.setText(
            self.drone.hersteller or ""
        )

        self.model_edit.setText(
            self.drone.modell
        )

        self.serial_number_edit.setText(
            self.drone.seriennummer or ""
        )

        self.notes_edit.setPlainText(
            self.drone.bemerkungen or ""
        )

    def _accept(self):
        model = (
            self.model_edit.text().strip()
        )

        if not model:
            QMessageBox.warning(
                self,
                self.tr(
                    "Ungültige Eingabe"
                ),
                self.tr(
                    "Bitte geben Sie das "
                    "Drohnenmodell ein."
                ),
            )

            self.model_edit.setFocus()
            return

        self.accept()

    def get_data(
        self,
    ) -> dict:
        return {
            "hersteller": (
                self.manufacturer_edit
                .text()
                .strip()
                or None
            ),
            "modell": (
                self.model_edit
                .text()
                .strip()
            ),
            "seriennummer": (
                self.serial_number_edit
                .text()
                .strip()
                or None
            ),
            "bemerkungen": (
                self.notes_edit
                .toPlainText()
                .strip()
                or None
            ),
        }