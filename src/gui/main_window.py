"""Главное окно приложения."""

import logging
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QSystemTrayIcon, QMenu, QMessageBox
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QAction, QCloseEvent

from database.db_manager import DatabaseManager
from utils.config import Config
from core.tracker import TimeTracker
from core.activity_monitor import ActivityMonitor
from core.break_manager import BreakManager

from .styles import MAIN_STYLESHEET
from .widgets.timer_widget import TimerWidget
from .widgets.stats_widget import StatsWidget
from .widgets.activity_widget import ActivityWidget
from .widgets.settings_widget import SettingsWidget


class MainWindow(QMainWindow):
    """Главное окно приложения."""

    def __init__(self, db_manager: DatabaseManager, config: Config):
        super().__init__()
        self._logger = logging.getLogger(__name__)

        self._db = db_manager
        self._config = config

        # Инициализация компонентов ядра
        self._tracker = TimeTracker(db_manager)
        self._activity_monitor = ActivityMonitor(db_manager)
        self._break_manager = BreakManager(config)

        self._setup_ui()
        self._setup_tray()
        self._connect_signals()

        # Автозапуск отслеживания
        if config.settings.auto_start_tracking:
            self._tracker.start()

    def _setup_ui(self) -> None:
        """Настройка интерфейса."""
        self.setWindowTitle("Work Chronometer - Хронометраж работы")
        self.setMinimumSize(700, 550)  # Минимальный размер окна
        self.resize(950, 700)

        # Применение стилей
        self.setStyleSheet(MAIN_STYLESHEET)

        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)

        # Виджет таймера (всегда виден сверху)
        self._timer_widget = TimerWidget(self._tracker)
        main_layout.addWidget(self._timer_widget)

        # Вкладки с дополнительной информацией
        self._tab_widget = QTabWidget()

        # Вкладка статистики
        self._stats_widget = StatsWidget(self._db)
        self._tab_widget.addTab(self._stats_widget, "📊 Статистика")

        # Вкладка активности
        self._activity_widget = ActivityWidget(self._db)
        self._tab_widget.addTab(self._activity_widget, "📱 Приложения")

        # Вкладка настроек
        self._settings_widget = SettingsWidget(self._config)
        self._tab_widget.addTab(self._settings_widget, "⚙️ Настройки")

        main_layout.addWidget(self._tab_widget, 1)

    def _setup_tray(self) -> None:
        """Настройка иконки в системном трее."""
        self._tray_icon = QSystemTrayIcon(self)

        # Меню трея
        tray_menu = QMenu()

        show_action = QAction("📱 Показать", self)
        show_action.triggered.connect(self.show)
        tray_menu.addAction(show_action)

        tray_menu.addSeparator()

        start_action = QAction("▶ Старт", self)
        start_action.triggered.connect(self._tracker.start)
        tray_menu.addAction(start_action)

        pause_action = QAction("⏸ Пауза", self)
        pause_action.triggered.connect(self._tracker.pause)
        tray_menu.addAction(pause_action)

        stop_action = QAction("⏹ Стоп", self)
        stop_action.triggered.connect(self._tracker.stop)
        tray_menu.addAction(stop_action)

        tray_menu.addSeparator()

        quit_action = QAction("❌ Выход", self)
        quit_action.triggered.connect(self._quit_app)
        tray_menu.addAction(quit_action)

        self._tray_icon.setContextMenu(tray_menu)
        self._tray_icon.activated.connect(self._on_tray_activated)

    def _connect_signals(self) -> None:
        """Подключение сигналов."""
        self._tracker.session_started.connect(self._on_session_started)
        self._tracker.session_stopped.connect(self._on_session_stopped)
        self._break_manager.break_reminder.connect(self._show_break_reminder)
        self._tab_widget.currentChanged.connect(self._on_tab_changed)

    def _on_session_started(self, session) -> None:
        """Обработка начала сессии."""
        self._activity_monitor.start_monitoring(session.id)
        self._break_manager.start()
        self._update_title()

    def _on_session_stopped(self, session) -> None:
        """Обработка окончания сессии."""
        self._activity_monitor.stop_monitoring()
        self._break_manager.stop()
        self._stats_widget.refresh()
        self._activity_widget.refresh()
        self._update_title()

    def _on_tab_changed(self, index: int) -> None:
        """Обработка смены вкладки."""
        if index == 0:
            self._stats_widget.refresh()
        elif index == 1:
            self._activity_widget.refresh()

    def _show_break_reminder(self, break_type: str, duration: int) -> None:
        """Показать напоминание о перерыве."""
        if not self._config.settings.notifications_enabled:
            return

        if break_type == "long":
            title = "☕ Время для длинного перерыва!"
            message = f"Вы работали уже долго.\nОтдохните {duration} минут."
        else:
            title = "🍃 Время для перерыва!"
            message = f"Сделайте короткий перерыв на {duration} минут."

        QMessageBox.information(self, title, message)

    def _on_tray_activated(self, reason) -> None:
        """Обработка клика по иконке в трее."""
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show()
            self.activateWindow()

    def _update_title(self) -> None:
        """Обновить заголовок окна."""
        if self._tracker.is_running:
            self.setWindowTitle("▶ Work Chronometer - Работа")
        elif self._tracker.is_paused:
            self.setWindowTitle("⏸ Work Chronometer - Пауза")
        else:
            self.setWindowTitle("Work Chronometer - Хронометраж работы")

    def _quit_app(self) -> None:
        """Выход из приложения."""
        if self._tracker.current_session:
            reply = QMessageBox.question(
                self,
                "Подтверждение выхода",
                "Сессия все еще активна.\nЗавершить её перед выходом?",
                QMessageBox.StandardButton.Yes |
                QMessageBox.StandardButton.No |
                QMessageBox.StandardButton.Cancel
            )

            if reply == QMessageBox.StandardButton.Yes:
                self._tracker.stop()
            elif reply == QMessageBox.StandardButton.Cancel:
                return

        from PyQt6.QtWidgets import QApplication
        QApplication.quit()

    def closeEvent(self, event: QCloseEvent) -> None:
        """Обработка закрытия окна."""
        if self._config.settings.start_minimized:
            event.ignore()
            self.hide()
        else:
            self._quit_app()
            event.accept()
