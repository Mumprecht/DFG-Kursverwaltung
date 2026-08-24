from datetime import date

from PySide6.QtCore import QDate, Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDateEdit,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from dfg_kursverwaltung.core.models import CourseType
from dfg_kursverwaltung.services.kurstage_service import CourseDayService
from dfg_kursverwaltung.services.lehrgaenge_service import CourseService
from dfg_kursverwaltung.services.standorte_service import LocationService


class DateTableWidgetItem(QTableWidgetItem):
    def __init__(self, text: str, sort_value: date):
        super().__init__(text)
        self.sort_value = sort_value

    def __lt__(self, other: QTableWidgetItem) -> bool:
        if isinstance(other, DateTableWidgetItem):
            return self.sort_value < other.sort_value
        return super().__lt__(other)


class KurstageWidget(QWidget):
    course_requested = Signal(str)

    LOCATION_NONE = "__none__"

    def __init__(
        self,
        course_day_service: CourseDayService,
        course_service: CourseService,
        location_service: LocationService,
        parent: QWidget | None = None,
    ):
        super().__init__(parent)

        self.course_day_service = course_day_service
        self.course_service = course_service
        self.location_service = location_service

        self._all_rows: list[dict[str, object]] = []

        self._create_ui()
        self.load_course_days()

    def _create_ui(self):
        main_layout = QVBoxLayout(self)

        title = QLabel(self.tr("Kurstage"))
        title.setStyleSheet(
            "font-size: 22px; "
            "font-weight: bold;"
        )
        main_layout.addWidget(title)

        description = QLabel(
            self.tr(
                "Übersicht über alle Kurstage. "
                "Mit einem Doppelklick öffnen Sie "
                "den zugehörigen Lehrgang."
            )
        )
        description.setWordWrap(True)
        main_layout.addWidget(description)

        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel(self.tr("Suche:")))

        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText(
            self.tr(
                "Datum, Lehrgang, Typ, "
                "Ausführungsort oder Bezeichnung..."
            )
        )
        self.search_edit.setClearButtonEnabled(True)
        self.search_edit.textChanged.connect(
            self._apply_filter
        )
        search_layout.addWidget(self.search_edit, 1)

        main_layout.addLayout(search_layout)

        filter_layout = QHBoxLayout()

        filter_layout.addWidget(QLabel(self.tr("Typ:")))

        self.type_combo = QComboBox()
        self.type_combo.currentIndexChanged.connect(
            self._apply_filter
        )
        filter_layout.addWidget(self.type_combo)

        filter_layout.addWidget(
            QLabel(self.tr("Ausführungsort:"))
        )

        self.location_combo = QComboBox()
        self.location_combo.currentIndexChanged.connect(
            self._apply_filter
        )
        filter_layout.addWidget(self.location_combo)

        self.from_checkbox = QCheckBox(
            self.tr("Von:")
        )
        self.from_checkbox.toggled.connect(
            self._from_filter_toggled
        )
        filter_layout.addWidget(self.from_checkbox)

        self.from_date_edit = QDateEdit()
        self.from_date_edit.setCalendarPopup(True)
        self.from_date_edit.setDisplayFormat(
            "dd.MM.yyyy"
        )
        self.from_date_edit.setEnabled(False)
        self.from_date_edit.dateChanged.connect(
            self._apply_filter
        )
        filter_layout.addWidget(self.from_date_edit)

        self.to_checkbox = QCheckBox(
            self.tr("Bis:")
        )
        self.to_checkbox.toggled.connect(
            self._to_filter_toggled
        )
        filter_layout.addWidget(self.to_checkbox)

        self.to_date_edit = QDateEdit()
        self.to_date_edit.setCalendarPopup(True)
        self.to_date_edit.setDisplayFormat(
            "dd.MM.yyyy"
        )
        self.to_date_edit.setEnabled(False)
        self.to_date_edit.dateChanged.connect(
            self._apply_filter
        )
        filter_layout.addWidget(self.to_date_edit)

        self.reset_filter_button = QPushButton(
            self.tr("Filter zurücksetzen")
        )
        self.reset_filter_button.clicked.connect(
            self._reset_filters
        )
        filter_layout.addWidget(
            self.reset_filter_button
        )

        filter_layout.addStretch()

        main_layout.addLayout(filter_layout)

        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels(
            [
                self.tr("Datum"),
                self.tr("Beginn"),
                self.tr("Ende"),
                self.tr("Lehrgang"),
                self.tr("Typ"),
                self.tr("Ausführungsort"),
                self.tr("Bezeichnung"),
            ]
        )
        self.table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )
        self.table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self.table.setSelectionMode(
            QTableWidget.SelectionMode.SingleSelection
        )
        self.table.setSortingEnabled(True)
        self.table.horizontalHeader().setStretchLastSection(
            True
        )
        self.table.cellDoubleClicked.connect(
            self._row_double_clicked
        )

        main_layout.addWidget(self.table, 1)

        self.status_label = QLabel()
        main_layout.addWidget(self.status_label)

    def load_course_days(self, *_args):
        selected_type = (
            self.type_combo.currentData()
            if self.type_combo.count()
            else None
        )
        selected_location = (
            self.location_combo.currentData()
            if self.location_combo.count()
            else None
        )

        course_days = (
            self.course_day_service
            .list_all_course_days()
        )

        rows: list[dict[str, object]] = []
        location_values: dict[str, str] = {}

        for course_day in course_days:
            course = self.course_service.get_course(
                course_day.lehrgang_id
            )

            course_name = ""
            course_type_value = ""
            course_type_text = ""

            if course is not None:
                course_name = course.bezeichnung
                course_type_value = course.typ.value
                course_type_text = (
                    self._course_type_text(
                        course.typ
                    )
                )

            location_name = ""

            if course_day.standort_id:
                location = (
                    self.location_service
                    .get_location(
                        course_day.standort_id
                    )
                )

                if location is not None:
                    location_name = (
                        location.bezeichnung
                    )
                    location_values[
                        location.id
                    ] = location.bezeichnung

            rows.append(
                {
                    "course_day_id": course_day.id,
                    "course_id": (
                        course_day.lehrgang_id
                    ),
                    "date_value": course_day.datum,
                    "datum": (
                        course_day.datum.strftime(
                            "%d.%m.%Y"
                        )
                    ),
                    "beginn": (
                        course_day.beginn or ""
                    ),
                    "ende": course_day.ende or "",
                    "lehrgang": course_name,
                    "typ_value": (
                        course_type_value
                    ),
                    "typ": course_type_text,
                    "location_id": (
                        course_day.standort_id
                    ),
                    "standort": location_name,
                    "bezeichnung": (
                        course_day.bezeichnung or ""
                    ),
                }
            )

        self._all_rows = rows

        self._reload_type_filter(
            selected_type
        )
        self._reload_location_filter(
            location_values,
            selected_location,
        )
        self._set_date_filter_defaults()
        self._apply_filter()

    def _reload_type_filter(
        self,
        selected_type: str | None,
    ):
        self.type_combo.blockSignals(True)
        self.type_combo.clear()
        self.type_combo.addItem(
            self.tr("Alle"),
            None,
        )

        for course_type in CourseType:
            self.type_combo.addItem(
                self._course_type_text(
                    course_type
                ),
                course_type.value,
            )

        if selected_type is not None:
            index = self.type_combo.findData(
                selected_type
            )
            if index >= 0:
                self.type_combo.setCurrentIndex(
                    index
                )

        self.type_combo.blockSignals(False)

    def _reload_location_filter(
        self,
        location_values: dict[str, str],
        selected_location: str | None,
    ):
        self.location_combo.blockSignals(True)
        self.location_combo.clear()

        self.location_combo.addItem(
            self.tr("Alle"),
            None,
        )
        self.location_combo.addItem(
            self.tr("Ohne Ausführungsort"),
            self.LOCATION_NONE,
        )

        for location_id, location_name in sorted(
            location_values.items(),
            key=lambda item: item[1].casefold(),
        ):
            self.location_combo.addItem(
                location_name,
                location_id,
            )

        if selected_location is not None:
            index = (
                self.location_combo.findData(
                    selected_location
                )
            )
            if index >= 0:
                self.location_combo.setCurrentIndex(
                    index
                )

        self.location_combo.blockSignals(False)

    def _set_date_filter_defaults(self):
        if not self._all_rows:
            today = QDate.currentDate()
            self.from_date_edit.setDate(today)
            self.to_date_edit.setDate(today)
            return

        dates = [
            row["date_value"]
            for row in self._all_rows
        ]

        minimum_date = min(dates)
        maximum_date = max(dates)

        if not self.from_checkbox.isChecked():
            self.from_date_edit.setDate(
                QDate(
                    minimum_date.year,
                    minimum_date.month,
                    minimum_date.day,
                )
            )

        if not self.to_checkbox.isChecked():
            self.to_date_edit.setDate(
                QDate(
                    maximum_date.year,
                    maximum_date.month,
                    maximum_date.day,
                )
            )

    def _from_filter_toggled(
        self,
        checked: bool,
    ):
        self.from_date_edit.setEnabled(
            checked
        )
        self._apply_filter()

    def _to_filter_toggled(
        self,
        checked: bool,
    ):
        self.to_date_edit.setEnabled(
            checked
        )
        self._apply_filter()

    def _reset_filters(self):
        self.search_edit.clear()
        self.type_combo.setCurrentIndex(0)
        self.location_combo.setCurrentIndex(0)
        self.from_checkbox.setChecked(False)
        self.to_checkbox.setChecked(False)
        self._set_date_filter_defaults()
        self._apply_filter()

    def _apply_filter(self, *_args):
        search_text = (
            self.search_edit.text()
            .strip()
            .casefold()
        )

        type_filter = (
            self.type_combo.currentData()
        )
        location_filter = (
            self.location_combo.currentData()
        )

        from_date = None

        if self.from_checkbox.isChecked():
            qdate = self.from_date_edit.date()
            from_date = date(
                qdate.year(),
                qdate.month(),
                qdate.day(),
            )

        to_date = None

        if self.to_checkbox.isChecked():
            qdate = self.to_date_edit.date()
            to_date = date(
                qdate.year(),
                qdate.month(),
                qdate.day(),
            )

        rows = []

        for row in self._all_rows:
            if search_text:
                searchable_text = " ".join(
                    [
                        str(row["datum"]),
                        str(row["beginn"]),
                        str(row["ende"]),
                        str(row["lehrgang"]),
                        str(row["typ"]),
                        str(row["standort"]),
                        str(row["bezeichnung"]),
                    ]
                ).casefold()

                if (
                    search_text
                    not in searchable_text
                ):
                    continue

            if (
                type_filter is not None
                and row["typ_value"]
                != type_filter
            ):
                continue

            if (
                location_filter
                == self.LOCATION_NONE
            ):
                if row["location_id"]:
                    continue

            elif (
                location_filter is not None
                and row["location_id"]
                != location_filter
            ):
                continue

            row_date = row["date_value"]

            if (
                from_date is not None
                and row_date < from_date
            ):
                continue

            if (
                to_date is not None
                and row_date > to_date
            ):
                continue

            rows.append(row)

        self._show_rows(rows)

    def _show_rows(
        self,
        rows: list[dict[str, object]],
    ):
        self.table.setSortingEnabled(False)
        self.table.setRowCount(len(rows))

        for row_index, row in enumerate(rows):
            date_item = DateTableWidgetItem(
                str(row["datum"]),
                row["date_value"],
            )
            date_item.setData(
                Qt.ItemDataRole.UserRole,
                row["course_id"],
            )
            date_item.setData(
                Qt.ItemDataRole.UserRole + 1,
                row["course_day_id"],
            )

            values = [
                date_item,
                QTableWidgetItem(
                    str(row["beginn"])
                ),
                QTableWidgetItem(
                    str(row["ende"])
                ),
                QTableWidgetItem(
                    str(row["lehrgang"])
                ),
                QTableWidgetItem(
                    str(row["typ"])
                ),
                QTableWidgetItem(
                    str(row["standort"])
                ),
                QTableWidgetItem(
                    str(row["bezeichnung"])
                ),
            ]

            for column, item in enumerate(
                values
            ):
                self.table.setItem(
                    row_index,
                    column,
                    item,
                )

        self.table.resizeColumnsToContents()
        self.table.setSortingEnabled(True)
        self.table.sortItems(
            0,
            Qt.SortOrder.AscendingOrder,
        )

        self.status_label.setText(
            self.tr(
                "%1 von %2 Kurstagen angezeigt"
            ).replace(
                "%1",
                str(len(rows)),
            ).replace(
                "%2",
                str(len(self._all_rows)),
            )
        )

    def _row_double_clicked(
        self,
        row: int,
        _column: int,
    ):
        item = self.table.item(row, 0)

        if item is None:
            return

        course_id = item.data(
            Qt.ItemDataRole.UserRole
        )

        if not course_id:
            return

        self.course_requested.emit(course_id)

    def _course_type_text(
        self,
        course_type: CourseType,
    ) -> str:
        if (
            course_type
            == CourseType.INTRODUCTORY_DAY
        ):
            return self.tr("Einführungstag")

        if course_type == CourseType.COURSE:
            return self.tr("Kurs")

        if course_type == CourseType.EXAM:
            return self.tr("Prüfung")

        return course_type.value
