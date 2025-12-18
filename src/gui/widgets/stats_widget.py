"""Виджет статистики."""

from datetime import date, timedelta
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QFrame, QGridLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QComboBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

from database.db_manager import DatabaseManager
from utils.helpers import format_duration, get_week_bounds


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
        layout.setSpacing(20)

        # Заголовок и выбор периода
        header_layout = QHBoxLayout()

        title = QLabel("📊 Статистика")
        title.setObjectName("sectionTitle")
        header_layout.addWidget(title)

        header_layout.addStretch()

        self._period_combo = QComboBox()
        self._period_combo.addItems(["Сегодня", "Эта неделя", "Этот месяц"])
        self._period_combo.currentIndexChanged.connect(self.refresh)
        header_layout.addWidget(self._period_combo)

        layout.addLayout(header_layout)

        # Карточки с основной статистикой
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(15)

        # Общее время
        self._total_card = self._create_stat_card("⏱️ Общее время", "0ч 0мин", "#2196F3")
        cards_layout.addWidget(self._total_card)

        # Количество сессий
        self._sessions_card = self._create_stat_card("📝 Сессий", "0", "#4CAF50")
        cards_layout.addWidget(self._sessions_card)

        # Перерывов
        self._breaks_card = self._create_stat_card("☕ Перерывов", "0", "#FF9800")
        cards_layout.addWidget(self._breaks_card)

        # Среднее время сессии
        self._avg_card = self._create_stat_card("📊 Среднее", "0мин", "#9C27B0")
        cards_layout.addWidget(self._avg_card)

        layout.addLayout(cards_layout)

        # Таблица с историей сессий
        sessions_title = QLabel("История сессий")
        sessions_title.setObjectName("sectionTitle")
        layout.addWidget(sessions_title)

        self._sessions_table = QTableWidget()
        self._sessions_table.setColumnCount(5)
        self._sessions_table.setHorizontalHeaderLabels([
            "Дата", "Начало", "Окончание", "Длительность", "Перерывы"
        ])

        header = self._sessions_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        self._sessions_table.setAlternatingRowColors(True)
        self._sessions_table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )

        layout.addWidget(self._sessions_table, 1)

    def _create_stat_card(self, title: str, value: str, color: str) -> QFrame:
        """Создать карточку статистики."""
        card = QFrame()
        card.setObjectName("card")
        card.setMinimumHeight(100)

        layout = QVBoxLayout(card)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title_label = QLabel(title)
        title_label.setStyleSheet(f"color: {color}; font-weight: bold;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        value_label = QLabel(value)
        value_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        value_label.setObjectName("value")
        layout.addWidget(value_label)

        return card

    def _update_card_value(self, card: QFrame, value: str) -> None:
        """Обновить значение в карточке."""
        value_label = card.findChild(QLabel, "value")
        if value_label:
            value_label.setText(value)

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
            start = today.replace(day = 1)
            self._load_period_stats(start, today)

    def _load_daily_stats(self, target_date: date) -> None:
        """Загрузить статистику за день."""
        stats = self._db.get_daily_stats(target_date)

        self._update_card_value(
            self._total_card,
            format_duration(stats["total_time"])
        )
        self._update_card_value(
            self._sessions_card,
            str(stats["sessions_count"])
        )
        self._update_card_value(
            self._breaks_card,
            str(stats["breaks_count"])
        )

        avg = (stats["total_time"] // stats["sessions_count"]
               if stats["sessions_count"] > 0 else 0)
        self._update_card_value(self._avg_card, format_duration(avg))

        # Загрузка сессий
        self._load_sessions_table([target_date])

    def _load_period_stats(self, start_date: date, end_date: date) -> None:
        """Загрузить статистику за период."""
        weekly_stats = self._db.get_weekly_stats(start_date, end_date)

        total_time = sum(day.get("total_time", 0) for day in weekly_stats)
        sessions_count = sum(day.get("sessions_count", 0) for day in weekly_stats)

        self._update_card_value(self._total_card, format_duration(total_time))
        self._update_card_value(self._sessions_card, str(sessions_count))

        avg = total_time // sessions_count if sessions_count > 0 else 0
        self._update_card_value(self._avg_card, format_duration(avg))

        # Загрузка сессий за период
        dates = []
        current = start_date
        while current <= end_date:
            dates.append(current)
            current += timedelta(days = 1)

        self._load_sessions_table(dates)

    def _load_sessions_table(self, dates: list) -> None:
        """Загрузить таблицу сессий."""
        self._sessions_table.setRowCount(0)

        all_sessions = []
        for d in dates:
            sessions = self._db.get_sessions_by_date(d)
            all_sessions.extend(sessions)

        # Сортировка по времени начала (новые сверху)
        all_sessions.sort(key = lambda s: s.start_time, reverse = True)

        for session in all_sessions:
            row = self._sessions_table.rowCount()
            self._sessions_table.insertRow(row)

            # Дата
            date_item = QTableWidgetItem(
                session.start_time.strftime("%d.%m.%Y")
            )
            date_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self._sessions_table.setItem(row, 0, date_item)

            # Начало
            start_item = QTableWidgetItem(
                session.start_time.strftime("%H:%M")
            )
            start_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self._sessions_table.setItem(row, 1, start_item)

            # Окончание
            end_str = (session.end_time.strftime("%H:%M")
                       if session.end_time else "—")
            end_item = QTableWidgetItem(end_str)
            end_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self._sessions_table.setItem(row, 2, end_item)

            # Длительность
            duration_item = QTableWidgetItem(
                format_duration(session.total_duration)
            )
            duration_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self._sessions_table.setItem(row, 3, duration_item)

            # Перерывы
            breaks_item = QTableWidgetItem(str(session.breaks_count))
            breaks_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self._sessions_table.setItem(row, 4, breaks_item)
            