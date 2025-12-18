"""Виджет статистики."""

from datetime import date, timedelta
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QFrame, QGridLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QComboBox, QSizePolicy, QScrollArea
)
from PyQt6.QtCore import Qt

from database.db_manager import DatabaseManager
from utils.helpers import format_duration, get_week_bounds


class StatCard(QFrame):
    """Карточка статистики."""

    def __init__(self, icon: str, title: str, value: str, color: str, parent=None):
        super().__init__(parent)
        self.setObjectName("statCard")
        self.setMinimumSize(140, 90)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 12, 15, 12)
        layout.setSpacing(5)

        # Иконка + заголовок
        header = QLabel(f"{icon} {title}")
        header.setObjectName("cardTitle")
        header.setStyleSheet(f"color: {color};")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)

        # Значение
        self._value_label = QLabel(value)
        self._value_label.setObjectName("cardValue")
        self._value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
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
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(20)

        # Заголовок и выбор периода
        header_layout = QHBoxLayout()
        header_layout.setSpacing(15)

        title = QLabel("📊 Статистика")
        title.setObjectName("sectionTitle")
        header_layout.addWidget(title)

        header_layout.addStretch()

        period_label = QLabel("Период:")
        period_label.setStyleSheet("color: #555555;")
        header_layout.addWidget(period_label)

        self._period_combo = QComboBox()
        self._period_combo.addItems(["Сегодня", "Эта неделя", "Этот месяц"])
        self._period_combo.setMinimumWidth(150)
        self._period_combo.currentIndexChanged.connect(self.refresh)
        header_layout.addWidget(self._period_combo)

        layout.addLayout(header_layout)

        # Карточки со статистикой
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(15)

        self._total_card = StatCard("⏱️", "Общее время", "0ч 0мин", "#2196F3")
        cards_layout.addWidget(self._total_card)

        self._sessions_card = StatCard("📝", "Сессий", "0", "#4CAF50")
        cards_layout.addWidget(self._sessions_card)

        self._breaks_card = StatCard("☕", "Перерывов", "0", "#FF9800")
        cards_layout.addWidget(self._breaks_card)

        self._avg_card = StatCard("📊", "Среднее", "0мин", "#9C27B0")
        cards_layout.addWidget(self._avg_card)

        layout.addLayout(cards_layout)

        # Заголовок таблицы
        table_header = QLabel("📋 История сессий")
        table_header.setObjectName("sectionTitle")
        layout.addWidget(table_header)

        # Таблица
        self._sessions_table = QTableWidget()
        self._sessions_table.setColumnCount(5)
        self._sessions_table.setHorizontalHeaderLabels([
            "Дата", "Начало", "Окончание", "Длительность", "Перерывы"
        ])

        # Настройка заголовков
        header = self._sessions_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        header.resizeSection(1, 90)
        header.resizeSection(2, 100)
        header.resizeSection(3, 120)
        header.resizeSection(4, 90)

        self._sessions_table.setAlternatingRowColors(True)
        self._sessions_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._sessions_table.verticalHeader().setVisible(False)
        self._sessions_table.setMinimumHeight(200)

        layout.addWidget(self._sessions_table, 1)

    def refresh(self) -> None:
        """Обновить данные статистики."""
        period_index = self._period_combo.currentIndex()

        if period_index == 0:  # Сегодня
            self._load_daily_stats(date.today())
        elif period_index == 1:  # Неделя
            start, end = get_week_bounds()
            self._load_period_stats(start, end)
        else:  # Месяц
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

        # Загрузка сессий за период
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

        # Сортировка по времени начала (новые сверху)
        all_sessions.sort(key=lambda s: s.start_time, reverse=True)

        for session in all_sessions:
            row = self._sessions_table.rowCount()
            self._sessions_table.insertRow(row)

            # Дата
            date_item = QTableWidgetItem(session.start_time.strftime("%d.%m.%Y"))
            date_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self._sessions_table.setItem(row, 0, date_item)

            # Начало
            start_item = QTableWidgetItem(session.start_time.strftime("%H:%M"))
            start_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self._sessions_table.setItem(row, 1, start_item)

            # Окончание
            end_str = session.end_time.strftime("%H:%M") if session.end_time else "—"
            end_item = QTableWidgetItem(end_str)
            end_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self._sessions_table.setItem(row, 2, end_item)

            # Длительность
            duration_item = QTableWidgetItem(format_duration(session.total_duration))
            duration_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self._sessions_table.setItem(row, 3, duration_item)

            # Перерывы
            breaks_item = QTableWidgetItem(str(session.breaks_count))
            breaks_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self._sessions_table.setItem(row, 4, breaks_item)
