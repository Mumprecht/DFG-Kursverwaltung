from datetime import datetime
from pathlib import Path

from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QGroupBox,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from dfg_kursverwaltung.core.models import User
from dfg_kursverwaltung.core.permissions import (
    Permission,
    has_permission,
)
from dfg_kursverwaltung.services.backup_service import (
    BackupService,
)


class SicherungWidget(QWidget):
    def __init__(
        self,
        backup_service: BackupService,
        authenticated_user: User,
        parent: QWidget | None = None,
    ):
        super().__init__(parent)

        self.backup_service = backup_service
        self.authenticated_user = authenticated_user

        self.can_backup = has_permission(
            authenticated_user,
            Permission.BACKUP,
        )
        self.can_restore = has_permission(
            authenticated_user,
            Permission.RESTORE,
        )
        self.can_reset_database = has_permission(
            authenticated_user,
            Permission.DATABASE_RESET,
        )

        self._create_ui()

    def _create_ui(self):
        main_layout = QVBoxLayout(self)

        title = QLabel(
            self.tr("Sicherung")
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
                "Erstellen und prüfen Sie vollständige "
                "Datenbanksicherungen oder stellen Sie "
                "einen früheren Datenbestand wieder her."
            )
        )

        description.setWordWrap(
            True
        )

        main_layout.addWidget(
            description
        )

        # -----------------------------------------------------
        # Backup
        # -----------------------------------------------------

        backup_group = QGroupBox(
            self.tr("Datensicherung")
        )

        backup_layout = QVBoxLayout(
            backup_group
        )

        backup_info = QLabel(
            self.tr(
                "Eine Datensicherung enthält die vollständige "
                "SQLite-Datenbank mit allen Tabellen und "
                "Verknüpfungen."
            )
        )

        backup_info.setWordWrap(
            True
        )

        backup_layout.addWidget(
            backup_info
        )

        self.create_backup_button = QPushButton(
            self.tr("Backup erstellen...")
        )

        self.create_backup_button.setEnabled(
            self.can_backup
        )

        self.create_backup_button.clicked.connect(
            self._create_backup
        )

        backup_layout.addWidget(
            self.create_backup_button
        )

        self.validate_backup_button = QPushButton(
            self.tr("Backup prüfen...")
        )

        self.validate_backup_button.clicked.connect(
            self._validate_backup
        )

        backup_layout.addWidget(
            self.validate_backup_button
        )

        main_layout.addWidget(
            backup_group
        )

        # -----------------------------------------------------
        # Restore
        # -----------------------------------------------------

        restore_group = QGroupBox(
            self.tr("Wiederherstellung")
        )

        restore_layout = QVBoxLayout(
            restore_group
        )

        restore_info = QLabel(
            self.tr(
                "Vor jeder Wiederherstellung wird automatisch "
                "eine Sicherheitskopie des aktuellen "
                "Datenbestands erstellt."
            )
        )

        restore_info.setWordWrap(
            True
        )

        restore_layout.addWidget(
            restore_info
        )

        self.restore_button = QPushButton(
            self.tr("Backup wiederherstellen...")
        )

        self.restore_button.setEnabled(
            self.can_restore
        )

        self.restore_button.clicked.connect(
            self._restore_backup
        )

        restore_layout.addWidget(
            self.restore_button
        )

        main_layout.addWidget(
            restore_group
        )

        # -----------------------------------------------------
        # Zurücksetzen
        # -----------------------------------------------------

        reset_group = QGroupBox(
            self.tr("Datenbank zurücksetzen")
        )

        reset_layout = QVBoxLayout(
            reset_group
        )

        reset_info = QLabel(
            self.tr(
                "Dabei werden alle Fachdaten gelöscht und eine "
                "neue leere Datenbank erzeugt. Vorher wird "
                "automatisch eine vollständige Sicherheitskopie "
                "erstellt."
            )
        )

        reset_info.setWordWrap(
            True
        )

        reset_layout.addWidget(
            reset_info
        )

        self.reset_button = QPushButton(
            self.tr("Datenbank vollständig zurücksetzen...")
        )

        self.reset_button.setEnabled(
            self.can_reset_database
        )

        self.reset_button.clicked.connect(
            self._reset_database
        )

        reset_layout.addWidget(
            self.reset_button
        )

        main_layout.addWidget(
            reset_group
        )

        main_layout.addStretch()

    def _default_backup_directory(
        self,
    ) -> Path:
        directory = (
            self.backup_service.database_manager.project_root
            / "Backup"
        )

        directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        return directory

    def _create_backup(self):
        if not self.can_backup:
            return

        timestamp = datetime.now().strftime(
            "%Y-%m-%d_%H%M%S"
        )

        default_path = (
            self._default_backup_directory()
            / (
                "DFG-Kursverwaltung_"
                f"Backup_{timestamp}.db"
            )
        )

        file_path, _selected_filter = (
            QFileDialog.getSaveFileName(
                self,
                self.tr("Backup erstellen"),
                str(default_path),
                self.tr(
                    "SQLite-Datenbank (*.db)"
                ),
            )
        )

        if not file_path:
            return

        if not file_path.lower().endswith(
            ".db"
        ):
            file_path += ".db"

        try:
            result = (
                self.backup_service
                .create_backup(
                    file_path
                )
            )

            schema_version = (
                self.backup_service
                .validate_backup(
                    result
                )
            )

        except Exception as exc:
            QMessageBox.critical(
                self,
                self.tr("Fehler"),
                self.tr(
                    "Das Backup konnte nicht "
                    "erstellt werden."
                )
                + "\n\n"
                + str(exc),
            )
            return

        QMessageBox.information(
            self,
            self.tr("Backup erstellt"),
            self.tr(
                "Das Backup wurde erfolgreich "
                "erstellt und geprüft."
            )
            + "\n\n"
            + self.tr(
                "Schema-Version: %1"
            ).replace(
                "%1",
                str(schema_version),
            )
            + "\n\n"
            + str(result),
        )

    def _validate_backup(self):
        file_path, _selected_filter = (
            QFileDialog.getOpenFileName(
                self,
                self.tr("Backup prüfen"),
                str(
                    self._default_backup_directory()
                ),
                self.tr(
                    "SQLite-Datenbank (*.db)"
                ),
            )
        )

        if not file_path:
            return

        try:
            schema_version = (
                self.backup_service
                .validate_backup(
                    file_path
                )
            )

        except Exception as exc:
            QMessageBox.critical(
                self,
                self.tr("Backup ungültig"),
                self.tr(
                    "Die Sicherungsdatei ist "
                    "nicht gültig."
                )
                + "\n\n"
                + str(exc),
            )
            return

        QMessageBox.information(
            self,
            self.tr("Backup gültig"),
            self.tr(
                "Die Sicherungsdatei ist "
                "konsistent und kann verwendet werden."
            )
            + "\n\n"
            + self.tr(
                "Schema-Version: %1"
            ).replace(
                "%1",
                str(schema_version),
            )
            + "\n\n"
            + file_path,
        )

    def _restore_backup(self):
        if not self.can_restore:
            return

        file_path, _selected_filter = (
            QFileDialog.getOpenFileName(
                self,
                self.tr(
                    "Backup wiederherstellen"
                ),
                str(
                    self._default_backup_directory()
                ),
                self.tr(
                    "SQLite-Datenbank (*.db)"
                ),
            )
        )

        if not file_path:
            return

        try:
            schema_version = (
                self.backup_service
                .validate_backup(
                    file_path
                )
            )

        except Exception as exc:
            QMessageBox.critical(
                self,
                self.tr("Backup ungültig"),
                self.tr(
                    "Die ausgewählte Sicherungsdatei "
                    "kann nicht wiederhergestellt werden."
                )
                + "\n\n"
                + str(exc),
            )
            return

        answer = QMessageBox.warning(
            self,
            self.tr(
                "Wiederherstellung bestätigen"
            ),
            self.tr(
                "Der aktuelle Datenbestand wird durch "
                "den Stand aus der ausgewählten Sicherung "
                "ersetzt.\n\n"
                "Vorher wird automatisch eine "
                "Sicherheitskopie des aktuellen Zustands "
                "erstellt.\n\n"
                "Schema-Version der Sicherung: %1\n\n"
                "Möchten Sie fortfahren?"
            ).replace(
                "%1",
                str(schema_version),
            ),
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
            safety_backup = (
                self.backup_service
                .restore_backup(
                    file_path
                )
            )

        except Exception as exc:
            QMessageBox.critical(
                self,
                self.tr("Fehler"),
                self.tr(
                    "Die Wiederherstellung ist "
                    "fehlgeschlagen."
                )
                + "\n\n"
                + str(exc),
            )
            return

        QMessageBox.information(
            self,
            self.tr(
                "Wiederherstellung abgeschlossen"
            ),
            self.tr(
                "Die Datenbank wurde erfolgreich "
                "wiederhergestellt."
            )
            + "\n\n"
            + self.tr(
                "Sicherheitskopie des vorherigen "
                "Zustands:"
            )
            + "\n"
            + str(safety_backup)
            + "\n\n"
            + self.tr(
                "Die Anwendung wird jetzt beendet. "
                "Bitte starten Sie sie anschließend "
                "neu."
            ),
        )

        self._quit_application()

    def _reset_database(self):
        if not self.can_reset_database:
            return

        first_answer = QMessageBox.warning(
            self,
            self.tr(
                "Datenbank zurücksetzen"
            ),
            self.tr(
                "ACHTUNG: Alle Personen, Telefonnummern, "
                "Drohnen, Ausführungsorte, Lehrgänge, "
                "Kurstage, Kurszuordnungen und "
                "Kursergebnisse werden gelöscht.\n\n"
                "Vorher wird automatisch eine vollständige "
                "Sicherheitskopie erstellt.\n\n"
                "Möchten Sie fortfahren?"
            ),
            QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if (
            first_answer
            != QMessageBox.StandardButton.Yes
        ):
            return

        second_answer = QMessageBox.warning(
            self,
            self.tr(
                "Letzte Bestätigung"
            ),
            self.tr(
                "Dies ist die letzte Sicherheitsabfrage.\n\n"
                "Die aktive Datenbank wird jetzt vollständig "
                "zurückgesetzt.\n\n"
                "Wirklich fortfahren?"
            ),
            QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if (
            second_answer
            != QMessageBox.StandardButton.Yes
        ):
            return

        try:
            safety_backup = (
                self.backup_service
                .reset_database()
            )

        except Exception as exc:
            QMessageBox.critical(
                self,
                self.tr("Fehler"),
                self.tr(
                    "Die Datenbank konnte nicht "
                    "zurückgesetzt werden."
                )
                + "\n\n"
                + str(exc),
            )
            return

        QMessageBox.information(
            self,
            self.tr(
                "Datenbank zurückgesetzt"
            ),
            self.tr(
                "Die Datenbank wurde erfolgreich "
                "zurückgesetzt."
            )
            + "\n\n"
            + self.tr(
                "Sicherheitskopie des vorherigen "
                "Zustands:"
            )
            + "\n"
            + str(safety_backup)
            + "\n\n"
            + self.tr(
                "Die Anwendung wird jetzt beendet. "
                "Bitte starten Sie sie anschließend "
                "neu."
            ),
        )

        self._quit_application()

    @staticmethod
    def _quit_application():
        application = QApplication.instance()

        if application is not None:
            application.quit()
