"""Виджет статистики."""

from datetime import date, timedelta
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QFrame, QTableWidget, QTableWidgetItem,
    QHeaderView, QComboBox, QSizePolicy
)
from PyQt6.QtCore import Qt

from database.db_manager import DatabaseManager
from utils.helpers import format_duration, get_week_bounds


class StatCard(QFrame):
    """Карточка статистики."""

    def __init__(self, title: str, value: str, color: str, parent=None):
        super().__init__(parent)
        self.setObjectName("statCard")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setMinimumHeight(70)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(4)

        # Заголовок
        header = QLabel(title)
        header.setObjectName("cardTitle")
        header.setStyleSheet(f"color: {color}; font-weight: bold;")
        layout.addWidget(header)

        # Значение
        self._value_label = QLabel(value)
        self._value_label.setObjectName("cardValue")
        layout.addWidget(self._value_label)

    def set_value(self, value: str) -> None:
        """Установить значение."""
        self._value_label.setText(value)


class StatsWidget(QWidget):
    """Виджет отображения статистики."""

    def __init__(self, db_manager: DatabaseManager, parent=None):
        super().__init__(parent)
        self._db = db_manager
        self._setup_ui()
        self.refresh()

    def _setup_ui(self) -> None:
        """Настройка интерфейса."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(16)

        # Заголовок и выбор периода
        header_layout = QHBoxLayout()

        title = QLabel("Статистика")
        title.setObjectName("sectionTitle")
        header_layout.addWidget(title)

        header_layout.addStretch()

        self._period_combo = QComboBox()
        self._period_combo.addItems(["Сегодня", "Эта неделя", "Этот месяц"])
        self._period_combo.setMinimumWidth(130)
        self._period_combo.currentIndexChanged.connect(self.refresh)
        header_layout.addWidget(self._period_combo)

        layout.addLayout(header_layout)

        # Карточки со статистикой
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(10)

        self._total_card = StatCard("Общее время", "0ч 0мин", "#3B82F6")
        cards_layout.addWidget(self._total_card)

        self._sessions_card = StatCard("Сессий", "0", "#22C55E")
        cards_layout.addWidget(self._sessions_card)

        self._breaks_card = StatCard("Перерывов", "0", "#F59E0B")
        cards_layout.addWidget(self._breaks_card)

        self._avg_card = StatCard("Среднее", "0мин", "#8B5CF6")
        cards_layout.addWidget(self._avg_card)

        layout.addLayout(cards_layout)

        # Таблица
        table_label = QLabel("История сессий")
        table_label.setObjectName("sectionTitle")
        layout.addWidget(table_label)

        self._sessions_table = QTableWidget()
        self._sessions_table.setColumnCount(5)
        self._sessions_table.setHorizontalHeaderLabels([
            "Дата", "Начало", "Окончание", "Длительность", "Перерывы"
        ])

        # Отключаем чередование цветов
        self._sessions_table.setAlternatingRowColors(False)

        header = self._sessions_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        for i in range(1, 5):
            header.setSectionResizeMode(i, QHeaderView.ResizeMode.Fixed)
            header.resizeSection(i, 95)

        self._sessions_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._sessions_table.verticalHeader().setVisible(False)

        layout.addWidget(self._sessions_table, 1)

    def refresh(self) -> None:
        """Обновить данные."""
        period_index = self._period_combo.currentIndex()

        if period_index == 0:
            self._load_daily_stats(date.today())
        elif period_index == 1:
            start, end = get_week_bounds()
            self._load_period_stats(start, end)
        else:
            today = date.today()
            start = today.replace(day=1)
            self._load_period_stats(start, today)

    def _load_daily_stats(self, target_date: date) -> None:
        """Загрузить статистику за день."""
        stats = self._db.get_daily_stats(target_date)

        self._total_card.set_value(format_duration(stats["total_time"]))
        self._sessions_card.set_value(str(stats["sessions_count"]))
        self._breaks_card.set_value(str(stats["breaks_count"]))

        avg = (stats["total_time"] // stats["sessions_count"]
               if stats["sessions_count"] > 0 else 0)
        self._avg_card.set_value(format_duration(avg))

        self._load_sessions_table([target_date])

    def _load_period_stats(self, start_date: date, end_date: date) -> None:
        """Загрузить статистику за период."""
        weekly_stats = self._db.get_weekly_stats(start_date, end_date)

        total_time = sum(day.get("total_time", 0) for day in weekly_stats)
        sessions_count = sum(day.get("sessions_count", 0) for day in weekly_stats)

        self._total_card.set_value(format_duration(total_time))
        self._sessions_card.set_value(str(sessions_count))

        avg = total_time // sessions_count if sessions_count > 0 else 0
        self._avg_card.set_value(format_duration(avg))

        dates = []
        current = start_date
        while current <= end_date:
            dates.append(current)
            current += timedelta(days=1)

        self._load_sessions_table(dates)

    def _load_sessions_table(self, dates: list) -> None:
        """Загрузить таблицу сессий."""
        self._sessions_table.setRowCount(0)

        all_sessions = []
        for d in dates:
            sessions = self._db.get_sessions_by_date(d)
            all_sessions.extend(sessions)

        all_sessions.sort(key=lambda s: s.start_time, reverse=True)

        for session in all_sessions:
            row = self._sessions_table.rowCount()
            self._sessions_table.insertRow(row)

            items = [
                session.start_time.strftime("%d.%m.%Y"),
                session.start_time.strftime("%H:%M"),
                session.end_time.strftime("%H:%M") if session.end_time else "—",
                format_duration(session.total_duration),
                str(session.breaks_count)
            ]

            for col, text in enumerate(items):
                item = QTableWidgetItem(text)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self._sessions_table.setItem(row, col, item)
