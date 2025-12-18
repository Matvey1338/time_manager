"""Виджет активности приложений."""

from datetime import date
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QProgressBar, QFrame
)
from PyQt6.QtCore import Qt

from database.db_manager import DatabaseManager
from utils.helpers import format_duration


class ActivityWidget(QWidget):
    """Виджет отображения активности приложений."""

    def __init__(self, db_manager: DatabaseManager, parent=None):
        super().__init__(parent)
        self._db = db_manager
        self._setup_ui()
        self.refresh()

    def _setup_ui(self) -> None:
        """Настройка интерфейса."""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)

        # Заголовок
        title = QLabel("📱 Использование приложений за сегодня")
        title.setObjectName("sectionTitle")
        layout.addWidget(title)

        # Таблица приложений
        self._apps_table = QTableWidget()
        self._apps_table.setColumnCount(3)
        self._apps_table.setHorizontalHeaderLabels([
            "Приложение", "Время", "Доля"
        ])

        header = self._apps_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        header.resizeSection(1, 120)
        header.resizeSection(2, 200)

        self._apps_table.setAlternatingRowColors(True)
        self._apps_table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self._apps_table.verticalHeader().setVisible(False)

        layout.addWidget(self._apps_table, 1)

        # Сводка
        summary_frame = QFrame()
        summary_frame.setObjectName("card")
        summary_layout = QHBoxLayout(summary_frame)

        self._total_apps_label = QLabel("Всего приложений: 0")
        summary_layout.addWidget(self._total_apps_label)

        summary_layout.addStretch()

        self._productive_label = QLabel("Продуктивное время: 0%")
        self._productive_label.setStyleSheet("color: #4CAF50; font-weight: bold;")
        summary_layout.addWidget(self._productive_label)

        layout.addWidget(summary_frame)

    def refresh(self) -> None:
        """Обновить данные."""
        self._apps_table.setRowCount(0)

        app_stats = self._db.get_app_statistics(date.today())

        if not app_stats:
            return

        total_time = sum(app_stats.values())

        # Сортировка по времени
        sorted_apps = sorted(
            app_stats.items(),
            key = lambda x: x[1],
            reverse = True
        )

        for app_name, duration in sorted_apps:
            row = self._apps_table.rowCount()
            self._apps_table.insertRow(row)

            # Имя приложения
            name_item = QTableWidgetItem(app_name)
            self._apps_table.setItem(row, 0, name_item)

            # Время
            time_item = QTableWidgetItem(format_duration(duration))
            time_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self._apps_table.setItem(row, 1, time_item)

            # Прогресс бар
            progress = QProgressBar()
            progress.setMaximum(100)
            percentage = int((duration / total_time) * 100) if total_time > 0 else 0
            progress.setValue(percentage)
            progress.setFormat(f"{percentage}%")
            self._apps_table.setCellWidget(row, 2, progress)

        self._total_apps_label.setText(f"Всего приложений: {len(app_stats)}")
        