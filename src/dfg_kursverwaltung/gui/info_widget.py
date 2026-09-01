import platform
import sqlite3
import sys
from pathlib import Path

import PySide6
from PySide6.QtCore import Qt, qVersion
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import (
    QFormLayout,
    QGroupBox,
    QLabel,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from dfg_kursverwaltung.core.database import (
    DatabaseManager,
)


class InfoWidget(QWidget):
    def __init__(
        self,
        database_manager: DatabaseManager,
    ):
        super().__init__()

        self.database_manager = database_manager

        main_layout = QVBoxLayout(self)

        title = QLabel(
            self.tr("DFG-Kursverwaltung")
        )
        title.setStyleSheet(
            "font-size: 22px; "
            "font-weight: bold;"
        )
        main_layout.addWidget(title)

        description = QLabel(
            self.tr(
                "Adress-, Kurs- und Prüfungsverwaltung "
                "der DFG Pfannenstiel"
            )
        )
        description.setWordWrap(True)
        main_layout.addWidget(description)

        application_group = QGroupBox(
            self.tr("Anwendung")
        )
        application_layout = QFormLayout(
            application_group
        )

        application_layout.addRow(
            self.tr("Version:"),
            QLabel(self._application_version()),
        )
        application_layout.addRow(
            self.tr("Entwicklung:"),
            QLabel(
                "Gregor Bölli / Urs Mumprecht"
            ),
        )
        application_layout.addRow(
            self.tr("Organisation:"),
            QLabel(
                "gresita.ch / Mumprecht Software"
            ),
        )
        application_layout.addRow(
            self.tr("Copyright:"),
            QLabel("© 2026"),
        )

        main_layout.addWidget(application_group)

        license_group = QGroupBox(
            self.tr("Lizenz")
        )
        license_layout = QFormLayout(
            license_group
        )

        license_layout.addRow(
            self.tr("Lizenz:"),
            QLabel(
                "DFG-Kursverwaltung "
                "Non-Commercial License 1.0"
            ),
        )
        license_layout.addRow(
            self.tr("Rechteinhaber:"),
            QLabel(
                "Gregor Bölli und Urs Mumprecht"
            ),
        )
        license_layout.addRow(
            self.tr("Nutzung:"),
            QLabel(
                self.tr(
                    "Nicht-kommerzielle Nutzung "
                    "gestattet"
                )
            ),
        )

        license_note = QLabel(
            self.tr(
                "Massgebend ist die deutsche "
                "Fassung des Lizenztextes."
            )
        )
        license_note.setWordWrap(True)
        license_layout.addRow(
            self.tr("Hinweis:"),
            license_note,
        )

        self.license_button = QPushButton(
            self.tr("Lizenztext anzeigen")
        )
        self.license_button.clicked.connect(
            self._show_license
        )
        license_layout.addRow(
            self.license_button
        )

        main_layout.addWidget(license_group)

        system_group = QGroupBox(
            self.tr("Systeminformationen")
        )
        system_layout = QFormLayout(
            system_group
        )

        system_layout.addRow(
            self.tr("Python:"),
            QLabel(platform.python_version()),
        )
        system_layout.addRow(
            self.tr("PySide6:"),
            QLabel(PySide6.__version__),
        )
        system_layout.addRow(
            self.tr("Qt:"),
            QLabel(qVersion()),
        )
        system_layout.addRow(
            self.tr("SQLite:"),
            QLabel(sqlite3.sqlite_version),
        )
        system_layout.addRow(
            self.tr("Betriebssystem:"),
            QLabel(self._platform_text()),
        )

        schema_version = (
            self.database_manager.get_schema_version()
        )

        system_layout.addRow(
            self.tr("Datenbankschema:"),
            QLabel(
                "-"
                if schema_version is None
                else str(schema_version)
            ),
        )

        database_path = QLabel(
            str(
                self.database_manager
                .database_path
                .resolve()
            )
        )
        database_path.setWordWrap(True)
        database_path.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )

        system_layout.addRow(
            self.tr("Datenbank:"),
            database_path,
        )

        main_layout.addWidget(system_group)

        self.copy_button = QPushButton(
            self.tr(
                "Systeminformationen kopieren"
            )
        )
        self.copy_button.clicked.connect(
            self._copy_system_information
        )
        main_layout.addWidget(self.copy_button)

        main_layout.addStretch()

    @staticmethod
    def _application_version() -> str:
        version_path = (
            Path(__file__).resolve().parents[3]
            / "VERSION"
        )

        try:
            content = version_path.read_text(
                encoding="utf-8"
            ).strip()
        except OSError:
            return "-"

        if "=" not in content:
            return content or "-"

        key, value = content.split(
            "=",
            maxsplit=1,
        )

        if key.strip().lower() != "version":
            return "-"

        return value.strip() or "-"

    @staticmethod
    def _platform_text() -> str:
        return (
            f"{platform.system()} "
            f"{platform.release()} "
            f"({platform.machine()})"
        )

    @staticmethod
    def _license_path() -> Path:
        return (
            Path(__file__).resolve().parents[3]
            / "LICENSE"
        )

    def _show_license(self):
        license_path = self._license_path()

        try:
            license_text = license_path.read_text(
                encoding="utf-8"
            )
        except OSError:
            QMessageBox.warning(
                self,
                self.tr("Lizenz"),
                self.tr(
                    "Der Lizenztext konnte nicht "
                    "geladen werden."
                ),
            )
            return

        dialog = QMessageBox(self)
        dialog.setWindowTitle(
            self.tr("Lizenz")
        )
        dialog.setText(
            self.tr(
                "DFG-Kursverwaltung "
                "Non-Commercial License 1.0"
            )
        )

        text_edit = QPlainTextEdit()
        text_edit.setReadOnly(True)
        text_edit.setPlainText(license_text)
        text_edit.setMinimumSize(700, 500)

        dialog.layout().addWidget(
            text_edit,
            dialog.layout().rowCount(),
            0,
            1,
            dialog.layout().columnCount(),
        )

        dialog.exec()

    def _system_information(self) -> str:
        schema_version = (
            self.database_manager.get_schema_version()
        )

        return "\n".join(
            (
                "DFG-Kursverwaltung "
                f"{self._application_version()}",
                "",
                f"Python: {platform.python_version()}",
                f"PySide6: {PySide6.__version__}",
                f"Qt: {qVersion()}",
                f"SQLite: {sqlite3.sqlite_version}",
                (
                    "Betriebssystem: "
                    f"{self._platform_text()}"
                ),
                (
                    "Datenbankschema: "
                    f"{schema_version}"
                ),
                (
                    "Datenbank: "
                    f"{self.database_manager.database_path.resolve()}"
                ),
            )
        )

    def _copy_system_information(self):
        clipboard = QGuiApplication.clipboard()

        if clipboard is not None:
            clipboard.setText(
                self._system_information()
            )
