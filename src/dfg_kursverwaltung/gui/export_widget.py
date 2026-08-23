from datetime import datetime
from pathlib import Path

from PySide6.QtWidgets import (
    QCheckBox,
    QFileDialog,
    QGroupBox,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from dfg_kursverwaltung.services.export_service import (
    ExportService,
)


class ExportWidget(QWidget):
    def __init__(
        self,
        export_service: ExportService,
        parent: QWidget | None = None,
    ):
        super().__init__(parent)

        self.export_service = export_service

        self._create_ui()

    def _create_ui(self):
        main_layout = QVBoxLayout(self)

        title = QLabel(
            self.tr("Export")
        )

        title.setStyleSheet(
            "font-size: 22px; "
            "font-weight: bold;"
        )

        main_layout.addWidget(
            title
        )

        description = QLabel(
            self.tr(
                "Exportieren Sie Personendaten "
                "als CSV-Datei."
            )
        )

        main_layout.addWidget(
            description
        )

        group = QGroupBox(
            self.tr("Personenexport")
        )

        group_layout = QVBoxLayout(
            group
        )

        self.include_inactive_checkbox = (
            QCheckBox(
                self.tr(
                    "Inaktive Personen einschliessen"
                )
            )
        )

        self.include_inactive_checkbox.setChecked(
            True
        )

        self.export_button = QPushButton(
            self.tr(
                "Personen als CSV exportieren"
            )
        )

        self.export_button.clicked.connect(
            self._export_persons
        )

        group_layout.addWidget(
            self.include_inactive_checkbox
        )

        group_layout.addWidget(
            self.export_button
        )

        main_layout.addWidget(
            group
        )

        main_layout.addStretch()

    def _export_persons(self):
        timestamp = datetime.now().strftime(
            "%Y-%m-%d_%H%M"
        )

        default_name = (
            f"DFG-Personen_{timestamp}.csv"
        )

        file_path, _selected_filter = (
            QFileDialog.getSaveFileName(
                self,
                self.tr(
                    "Personendaten exportieren"
                ),
                str(
                    Path.home()
                    / "Downloads"
                    / default_name
                ),
                self.tr(
                    "CSV-Dateien (*.csv)"
                ),
            )
        )

        if not file_path:
            return

        if not file_path.lower().endswith(
            ".csv"
        ):
            file_path += ".csv"

        include_inactive = (
            self.include_inactive_checkbox
            .isChecked()
        )

        try:
            count = (
                self.export_service
                .export_persons_csv(
                    file_path,
                    include_inactive=(
                        include_inactive
                    ),
                )
            )

        except Exception as exc:
            QMessageBox.critical(
                self,
                self.tr("Fehler"),
                self.tr(
                    "Der Export konnte nicht "
                    "erstellt werden."
                )
                + "\n\n"
                + str(exc),
            )
            return

        QMessageBox.information(
            self,
            self.tr(
                "Export abgeschlossen"
            ),
            self.tr(
                "%1 Personen wurden "
                "erfolgreich exportiert."
            ).replace(
                "%1",
                str(count),
            )
            + "\n\n"
            + file_path,
        )