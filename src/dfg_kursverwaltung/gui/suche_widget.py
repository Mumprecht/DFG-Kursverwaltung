from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QVBoxLayout,
    QWidget,
)

from dfg_kursverwaltung.repositories.suche_repository import (
    SearchResult,
)
from dfg_kursverwaltung.services.suche_service import (
    SearchService,
)


class SucheWidget(QWidget):
    person_requested = Signal(str)
    course_requested = Signal(str)
    location_requested = Signal(str)

    def __init__(
        self,
        search_service: SearchService,
        parent: QWidget | None = None,
    ):
        super().__init__(parent)

        self.search_service = search_service

        self._create_ui()

    def _create_ui(self):
        main_layout = QVBoxLayout(self)

        title = QLabel(
            self.tr("Suche")
        )

        title.setStyleSheet(
            "font-size: 22px; "
            "font-weight: bold;"
        )

        main_layout.addWidget(
            title
        )

        search_layout = QHBoxLayout()

        search_label = QLabel(
            self.tr("Suchbegriff:")
        )

        self.search_edit = QLineEdit()

        self.search_edit.setPlaceholderText(
            self.tr(
                "Name, Telefonnummer, Drohne, "
                "Lehrgang oder Standort suchen..."
            )
        )

        self.search_edit.setClearButtonEnabled(
            True
        )

        self.search_edit.textChanged.connect(
            self._search
        )

        search_layout.addWidget(
            search_label
        )

        search_layout.addWidget(
            self.search_edit,
            1,
        )

        main_layout.addLayout(
            search_layout
        )

        self.info_label = QLabel(
            self.tr(
                "Bitte geben Sie einen Suchbegriff ein."
            )
        )

        main_layout.addWidget(
            self.info_label
        )

        # -----------------------------------------------------
        # Personen
        # -----------------------------------------------------

        (
            self.person_group,
            self.person_list,
        ) = self._create_result_group(
            self.tr("Personen")
        )

        self.person_list.itemDoubleClicked.connect(
            self._person_result_double_clicked
        )

        main_layout.addWidget(
            self.person_group
        )

        # -----------------------------------------------------
        # Telefonnummern
        # -----------------------------------------------------

        (
            self.phone_group,
            self.phone_list,
        ) = self._create_result_group(
            self.tr("Telefonnummern")
        )

        self.phone_list.itemDoubleClicked.connect(
            self._person_result_double_clicked
        )

        main_layout.addWidget(
            self.phone_group
        )

        # -----------------------------------------------------
        # Drohnen
        # -----------------------------------------------------

        (
            self.drone_group,
            self.drone_list,
        ) = self._create_result_group(
            self.tr("Drohnen")
        )

        self.drone_list.itemDoubleClicked.connect(
            self._person_result_double_clicked
        )

        main_layout.addWidget(
            self.drone_group
        )

        # -----------------------------------------------------
        # Lehrgänge
        # -----------------------------------------------------

        (
            self.course_group,
            self.course_list,
        ) = self._create_result_group(
            self.tr("Lehrgänge")
        )

        self.course_list.itemDoubleClicked.connect(
            self._course_result_double_clicked
        )

        main_layout.addWidget(
            self.course_group
        )

        # -----------------------------------------------------
        # Ausführungsorte
        # -----------------------------------------------------

        (
            self.location_group,
            self.location_list,
        ) = self._create_result_group(
            self.tr("Ausführungsorte")
        )

        self.location_list.itemDoubleClicked.connect(
            self._location_result_double_clicked
        )

        main_layout.addWidget(
            self.location_group
        )

        main_layout.addStretch()

        self._clear_results()

    def _create_result_group(
        self,
        title: str,
    ) -> tuple[QGroupBox, QListWidget]:
        group = QGroupBox(
            title
        )

        layout = QVBoxLayout(
            group
        )

        result_list = QListWidget()

        result_list.setMaximumHeight(
            120
        )

        layout.addWidget(
            result_list
        )

        return (
            group,
            result_list,
        )

    def _search(
        self,
        text: str,
    ):
        search_text = text.strip()

        if not search_text:
            self._clear_results()

            self.info_label.setText(
                self.tr(
                    "Bitte geben Sie einen "
                    "Suchbegriff ein."
                )
            )

            return

        results = self.search_service.search(
            search_text
        )

        groups = self.search_service.group_results(
            results
        )

        self._fill_list(
            self.person_list,
            groups.get(
                "person",
                [],
            ),
        )

        self._fill_list(
            self.phone_list,
            groups.get(
                "telefon",
                [],
            ),
        )

        self._fill_list(
            self.drone_list,
            groups.get(
                "drohne",
                [],
            ),
        )

        self._fill_list(
            self.course_list,
            groups.get(
                "lehrgang",
                [],
            ),
        )

        self._fill_list(
            self.location_list,
            groups.get(
                "standort",
                [],
            ),
        )

        self._update_group_visibility()

        count = len(results)

        if count == 0:
            self.info_label.setText(
                self.tr(
                    "Keine Treffer gefunden."
                )
            )

        elif count == 1:
            self.info_label.setText(
                self.tr(
                    "1 Treffer gefunden."
                )
            )

        else:
            self.info_label.setText(
                self.tr(
                    "%1 Treffer gefunden."
                ).replace(
                    "%1",
                    str(count),
                )
            )

    def _fill_list(
        self,
        widget: QListWidget,
        results: list[SearchResult],
    ):
        widget.clear()

        for result in results:
            text = result.titel

            if result.details:
                text += (
                    "   |   "
                    + result.details
                )

            item = QListWidgetItem(
                text
            )

            item.setData(
                Qt.ItemDataRole.UserRole,
                result,
            )

            widget.addItem(
                item
            )

    def _person_result_double_clicked(
        self,
        item: QListWidgetItem,
    ):
        result = item.data(
            Qt.ItemDataRole.UserRole
        )

        if not isinstance(
            result,
            SearchResult,
        ):
            return

        person_id = result.person_id

        if not person_id:
            return

        self.person_requested.emit(
            person_id
        )

    def _course_result_double_clicked(
        self,
        item: QListWidgetItem,
    ):
        result = item.data(
            Qt.ItemDataRole.UserRole
        )

        if not isinstance(
            result,
            SearchResult,
        ):
            return

        if not result.id:
            return

        self.course_requested.emit(
            result.id
        )

    def _location_result_double_clicked(
        self,
        item: QListWidgetItem,
    ):
        result = item.data(
            Qt.ItemDataRole.UserRole
        )

        if not isinstance(
            result,
            SearchResult,
        ):
            return

        if not result.id:
            return

        self.location_requested.emit(
            result.id
        )

    def _clear_results(self):
        self.person_list.clear()
        self.phone_list.clear()
        self.drone_list.clear()
        self.course_list.clear()
        self.location_list.clear()

        self.person_group.setVisible(
            False
        )

        self.phone_group.setVisible(
            False
        )

        self.drone_group.setVisible(
            False
        )

        self.course_group.setVisible(
            False
        )

        self.location_group.setVisible(
            False
        )

    def _update_group_visibility(self):
        self.person_group.setVisible(
            self.person_list.count() > 0
        )

        self.phone_group.setVisible(
            self.phone_list.count() > 0
        )

        self.drone_group.setVisible(
            self.drone_list.count() > 0
        )

        self.course_group.setVisible(
            self.course_list.count() > 0
        )

        self.location_group.setVisible(
            self.location_list.count() > 0
        )

    def clear_search(self):
        self.search_edit.clear()

    def refresh(
        self,
    ):
        self._search(
            self.search_edit.text()
        )