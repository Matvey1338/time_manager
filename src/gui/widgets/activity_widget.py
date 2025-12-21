"""Виджет активности приложений с отображением продуктивности."""

from datetime import date
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QProgressBar, QFrame, QSizePolicy, QComboBox,
    QPushButton, QMenu
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction

from database.db_manager import DatabaseManager
from utils.config import Config
from utils.helpers import format_duration
from models.activity import ActivityType


class ProductivityCard(QFrame):
    """Карточка продуктивности."""

    def __init__(self, title: str, card_type: str, parent=None):
        super().__init__(parent)
        self.setObjectName(f"{card_type}Card")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setMinimumHeight(80)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(4)

        # Заголовок
        self._title = QLabel(title)
        self._title.setObjectName(f"{card_type}Label")
        layout.addWidget(self._title)

        # Время
        self._time_label = QLabel("0ч 0мин")
        self._time_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(self._time_label)

        # Процент
        self._percent_label = QLabel("0%")
        self._percent_label.setStyleSheet("font-size: 12px; color: #6B7280;")
        layout.addWidget(self._percent_label)

    def set_values(self, duration: int, total: int) -> None:
        """Установить значения."""
        self._time_label.setText(format_duration(duration))
        if total > 0:
            percent = int((duration / total) * 100)
            self._percent_label.setText(f"{percent}% от общего времени")
        else:
            self._percent_label.setText("0%")


class ActivityWidget(QWidget):
    """Виджет отображения активности приложений."""

    def __init__(self, db_manager: DatabaseManager, config: Config = None, parent=None):
        super().__init__(parent)
        self._db = db_manager
        self._config = config
        self._setup_ui()
        self.refresh()

    def _setup_ui(self) -> None:
        """Настройка интерфейса."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(16)

        # Заголовок
        header_layout = QHBoxLayout()

        title = QLabel("Продуктивность")
        title.setObjectName("sectionTitle")
        header_layout.addWidget(title)

        header_layout.addStretch()

        # Фильтр по типу
        self._filter_combo = QComboBox()
        self._filter_combo.addItems(["Все", "Продуктивные", "Отвлекающие", "Нейтральные"])
        self._filter_combo.setMinimumWidth(130)
        self._filter_combo.currentIndexChanged.connect(self._apply_filter)
        header_layout.addWidget(self._filter_combo)

        layout.addLayout(header_layout)

        # Карточки продуктивности
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(10)

        self._productive_card = ProductivityCard("✓ Продуктивное", "productive")
        cards_layout.addWidget(self._productive_card)

        self._distracting_card = ProductivityCard("✗ Отвлекающее", "distracting")
        cards_layout.addWidget(self._distracting_card)

        self._neutral_card = ProductivityCard("○ Нейтральное", "neutral")
        cards_layout.addWidget(self._neutral_card)

        layout.addLayout(cards_layout)

        # Таблица приложений
        table_label = QLabel("Приложения")
        table_label.setObjectName("sectionTitle")
        layout.addWidget(table_label)

        self._apps_table = QTableWidget()
        self._apps_table.setColumnCount(4)
        self._apps_table.setHorizontalHeaderLabels(["Приложение", "Тип", "Время", "Доля"])
        self._apps_table.setAlternatingRowColors(False)
        self._apps_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self._apps_table.customContextMenuRequested.connect(self._show_context_menu)

        header = self._apps_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        header.resizeSection(1, 110)
        header.resizeSection(2, 90)
        header.resizeSection(3, 130)

        self._apps_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._apps_table.verticalHeader().setVisible(False)

        layout.addWidget(self._apps_table, 1)

        # Подсказка
        hint_label = QLabel("Совет: Правый клик по приложению, чтобы изменить его категорию")
        hint_label.setStyleSheet("color: #6B7280; font-size: 11px; font-style: italic;")
        layout.addWidget(hint_label)

    def refresh(self) -> None:
        """Обновить данные."""
        # Получаем статистику продуктивности
        productivity = self._db.get_productivity_stats(date.today())

        productive_time = productivity["productive"]["duration"]
        distracting_time = productivity["distracting"]["duration"]
        neutral_time = productivity["neutral"]["duration"]
        total_time = productive_time + distracting_time + neutral_time

        self._productive_card.set_values(productive_time, total_time)
        self._distracting_card.set_values(distracting_time, total_time)
        self._neutral_card.set_values(neutral_time, total_time)

        # Обновляем таблицу
        self._load_apps_table()

    def _load_apps_table(self) -> None:
        """Загрузить таблицу приложений."""
        self._apps_table.setRowCount(0)

        apps = self._db.get_app_with_type(date.today())

        if not apps:
            return

        total_time = sum(app["duration"] for app in apps)

        # Применяем фильтр
        filter_index = self._filter_combo.currentIndex()
        if filter_index == 1:
            apps = [a for a in apps if a["type"] == "productive"]
        elif filter_index == 2:
            apps = [a for a in apps if a["type"] == "distracting"]
        elif filter_index == 3:
            apps = [a for a in apps if a["type"] == "neutral"]

        for app in apps:
            row = self._apps_table.rowCount()
            self._apps_table.insertRow(row)

            # Имя приложения
            name_item = QTableWidgetItem(f"  {app['name']}")
            name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            name_item.setData(Qt.ItemDataRole.UserRole, app['name'])  # Сохраняем имя
            self._apps_table.setItem(row, 0, name_item)

            # Тип активности
            type_text, type_color = self._get_type_display(app["type"])
            type_item = QTableWidgetItem(type_text)
            type_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            type_item.setForeground(type_color)
            type_item.setFlags(type_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self._apps_table.setItem(row, 1, type_item)

            # Время
            time_item = QTableWidgetItem(format_duration(app["duration"]))
            time_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            time_item.setFlags(time_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self._apps_table.setItem(row, 2, time_item)

            # Прогресс бар
            progress = QProgressBar()
            progress.setMaximum(100)
            percentage = int((app["duration"] / total_time) * 100) if total_time > 0 else 0
            progress.setValue(percentage)
            progress.setFormat(f"{percentage}%")

            # Цвет прогресс-бара в зависимости от типа
            bar_style = self._get_progress_style(app["type"])
            progress.setStyleSheet(bar_style)

            self._apps_table.setCellWidget(row, 3, progress)

    def _get_type_display(self, activity_type: str) -> tuple:
        """Получить отображение типа активности."""
        from PyQt6.QtGui import QColor

        types = {
            "productive": ("Продуктивное", QColor("#166534")),
            "distracting": ("Отвлекающее", QColor("#991B1B")),
            "neutral": ("Нейтральное", QColor("#4B5563")),
            "unknown": ("Неизвестно", QColor("#6B7280"))
        }
        return types.get(activity_type, types["unknown"])

    def _get_progress_style(self, activity_type: str) -> str:
        """Получить стиль прогресс-бара."""
        colors = {
            "productive": "#22C55E",
            "distracting": "#EF4444",
            "neutral": "#6B7280",
            "unknown": "#9CA3AF"
        }
        color = colors.get(activity_type, colors["unknown"])

        return f"""
            QProgressBar {{
                border: none;
                border-radius: 4px;
                background-color: #E5E7EB;
                height: 16px;
                text-align: center;
                font-size: 11px;
                font-weight: bold;
                color: #374151;
            }}
            QProgressBar::chunk {{
                background-color: {color};
                border-radius: 4px;
            }}
        """

    def _apply_filter(self) -> None:
        """Применить фильтр."""
        self._load_apps_table()

    def _show_context_menu(self, position) -> None:
        """Показать контекстное меню."""
        item = self._apps_table.itemAt(position)
        if not item:
            return

        row = item.row()
        name_item = self._apps_table.item(row, 0)
        if not name_item:
            return

        app_name = name_item.data(Qt.ItemDataRole.UserRole)

        menu = QMenu(self)

        productive_action = QAction("Отметить как продуктивное", self)
        productive_action.triggered.connect(lambda: self._set_app_type(app_name, "productive"))
        menu.addAction(productive_action)

        distracting_action = QAction("Отметить как отвлекающее", self)
        distracting_action.triggered.connect(lambda: self._set_app_type(app_name, "distracting"))
        menu.addAction(distracting_action)

        neutral_action = QAction("Отметить как нейтральное", self)
        neutral_action.triggered.connect(lambda: self._set_app_type(app_name, "neutral"))
        menu.addAction(neutral_action)

        menu.exec(self._apps_table.viewport().mapToGlobal(position))

    def _set_app_type(self, app_name: str, app_type: str) -> None:
        """Изменить тип приложения в конфигурации."""
        if not self._config:
            return

        app_lower = app_name.lower().replace(".exe", "")

        # Удаляем из всех списков
        if app_lower in self._config.settings.productive_apps:
            self._config.settings.productive_apps.remove(app_lower)
        if app_lower in self._config.settings.distracting_apps:
            self._config.settings.distracting_apps.remove(app_lower)

        # Добавляем в нужный список
        if app_type == "productive":
            self._config.settings.productive_apps.append(app_lower)
        elif app_type == "distracting":
            self._config.settings.distracting_apps.append(app_lower)

        self._config.save_settings()

        # Обновляем таблицу (но тип в БД не меняется - это только для будущих записей)
        self.refresh()
