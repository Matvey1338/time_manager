"""Главное окно приложения."""

import logging
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout,
    QTabWidget, QSystemTrayIcon, QMenu, QMessageBox,
    QApplication
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QAction, QCloseEvent, QPixmap, QPainter, QColor, QFont

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


def create_tray_icon() -> QIcon:
    """Создать иконку для системного трея."""
    pixmap = QPixmap(64, 64)
    pixmap.fill(Qt.GlobalColor.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    # Фон - синий круг
    painter.setBrush(QColor("#3B82F6"))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawEllipse(4, 4, 56, 56)

    # Белый текст "W"
    painter.setPen(QColor("#FFFFFF"))
    font = QFont("Arial", 28, QFont.Weight.Bold)
    painter.setFont(font)
    painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "W")

    painter.end()

    return QIcon(pixmap)


class MainWindow(QMainWindow):
    """Главное окно приложения."""

    def __init__(self, db_manager: DatabaseManager, config: Config):
        super().__init__()
        self._logger = logging.getLogger(__name__)

        self._db = db_manager
        self._config = config

        # Инициализация компонентов ядра
        self._tracker = TimeTracker(db_manager)
        self._activity_monitor = ActivityMonitor(db_manager, config)
        self._break_manager = BreakManager(config)

        self._setup_ui()
        self._setup_tray()
        self._connect_signals()

        # Автозапуск только если включено в настройках
        if config.settings.auto_start_tracking:
            self._tracker.start()

    def _setup_ui(self) -> None:
        """Настройка интерфейса."""
        self.setWindowTitle("Work Chronometer")
        self.setMinimumSize(600, 480)
        self.resize(850, 620)

        self.setWindowIcon(create_tray_icon())
        self.setStyleSheet(MAIN_STYLESHEET)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(12)

        # Виджет таймера
        self._timer_widget = TimerWidget(self._tracker)
        main_layout.addWidget(self._timer_widget)

        # Вкладки
        self._tab_widget = QTabWidget()

        self._stats_widget = StatsWidget(self._db)
        self._tab_widget.addTab(self._stats_widget, "Статистика")

        self._activity_widget = ActivityWidget(self._db, self._config)
        self._tab_widget.addTab(self._activity_widget, "Продуктивность")

        self._settings_widget = SettingsWidget(self._config)
        self._tab_widget.addTab(self._settings_widget, "Настройки")

        main_layout.addWidget(self._tab_widget, 1)

    def _setup_tray(self) -> None:
        """Настройка иконки в системном трее."""
        self._tray_icon = QSystemTrayIcon(self)
        self._tray_icon.setIcon(create_tray_icon())
        self._tray_icon.setToolTip("Work Chronometer")

        tray_menu = QMenu()

        show_action = QAction("Показать", self)
        show_action.triggered.connect(self._show_window)
        tray_menu.addAction(show_action)

        tray_menu.addSeparator()

        start_action = QAction("Старт", self)
        start_action.triggered.connect(self._tracker.start)
        tray_menu.addAction(start_action)

        pause_action = QAction("Пауза", self)
        pause_action.triggered.connect(self._tracker.pause)
        tray_menu.addAction(pause_action)

        stop_action = QAction("Стоп", self)
        stop_action.triggered.connect(self._tracker.stop)
        tray_menu.addAction(stop_action)

        tray_menu.addSeparator()

        quit_action = QAction("Выход", self)
        quit_action.triggered.connect(self._quit_app)
        tray_menu.addAction(quit_action)

        self._tray_icon.setContextMenu(tray_menu)
        self._tray_icon.activated.connect(self._on_tray_activated)
        self._tray_icon.show()

    def _show_window(self) -> None:
        """Показать окно."""
        self.show()
        self.showNormal()
        self.activateWindow()
        self.raise_()

    def _connect_signals(self) -> None:
        """Подключение сигналов."""
        self._tracker.session_started.connect(self._on_session_started)
        self._tracker.session_stopped.connect(self._on_session_stopped)
        self._tracker.session_paused.connect(self._on_session_paused)
        self._tracker.state_changed.connect(self._update_tray_tooltip)

        self._break_manager.break_reminder.connect(self._show_break_reminder)

        # Сигналы мониторинга простоя
        self._activity_monitor.idle_detected.connect(self._on_idle_detected)
        self._activity_monitor.user_returned.connect(self._on_user_returned)

        self._tab_widget.currentChanged.connect(self._on_tab_changed)

    def _update_tray_tooltip(self) -> None:
        """Обновить tooltip иконки в трее."""
        if self._tracker.is_running:
            status = "Работа"
        elif self._tracker.is_paused:
            status = "Пауза"
        else:
            status = "Остановлен"

        from utils.helpers import format_time
        time_str = format_time(self._tracker.elapsed_seconds)
        self._tray_icon.setToolTip(f"Work Chronometer - {status}\n{time_str}")

    def _on_session_started(self, session) -> None:
        """Обработка начала сессии."""
        self._activity_monitor.start_monitoring(session.id)
        self._break_manager.start()
        self._update_title()
        self._update_tray_tooltip()

    def _on_session_paused(self) -> None:
        """Сессия на паузе."""
        self._break_manager.pause()
        self._update_title()
        self._update_tray_tooltip()

    def _on_session_stopped(self, session) -> None:
        """Обработка окончания сессии."""
        self._activity_monitor.stop_monitoring()
        self._break_manager.stop()
        self._stats_widget.refresh()
        self._activity_widget.refresh()
        self._update_title()
        self._update_tray_tooltip()

    def _on_idle_detected(self, idle_seconds: int) -> None:
        """Обнаружен простой - автопауза."""
        if self._tracker.is_running:
            self._tracker.pause()

            if self._config.settings.notifications_enabled:
                minutes = idle_seconds // 60
                self._tray_icon.showMessage(
                    "Автопауза",
                    f"Вы не активны уже {minutes} мин.\nТаймер поставлен на паузу.",
                    QSystemTrayIcon.MessageIcon.Information,
                    3000
                )

    def _on_user_returned(self) -> None:
        """Пользователь вернулся после простоя."""
        if self._tracker.is_paused:
            # Можно автоматически продолжить или показать уведомление
            if self._config.settings.notifications_enabled:
                self._tray_icon.showMessage(
                    "С возвращением!",
                    "Нажмите 'Продолжить' чтобы возобновить таймер.",
                    QSystemTrayIcon.MessageIcon.Information,
                    3000
                )

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
            title = "Время для длинного перерыва"
            message = f"Вы работали уже долго.\nОтдохните {duration} минут."
        else:
            title = "Время для перерыва"
            message = f"Сделайте короткий перерыв на {duration} минут."

        self._tray_icon.showMessage(
            title, message,
            QSystemTrayIcon.MessageIcon.Information,
            5000
        )

    def _on_tray_activated(self, reason) -> None:
        """Обработка клика по иконке в трее."""
        if reason in (QSystemTrayIcon.ActivationReason.DoubleClick,
                      QSystemTrayIcon.ActivationReason.Trigger):
            self._show_window()

    def _update_title(self) -> None:
        """Обновить заголовок окна."""
        if self._tracker.is_running:
            self.setWindowTitle("▶ Work Chronometer - Работа")
        elif self._tracker.is_paused:
            self.setWindowTitle("⏸ Work Chronometer - Пауза")
        else:
            self.setWindowTitle("Work Chronometer")

    def _quit_app(self) -> None:
        """Выход из приложения."""
        if self._tracker.has_active_session:
            reply = QMessageBox.question(
                self,
                "Подтверждение выхода",
                "Сессия активна. Завершить её перед выходом?",
                QMessageBox.StandardButton.Yes |
                QMessageBox.StandardButton.No |
                QMessageBox.StandardButton.Cancel
            )

            if reply == QMessageBox.StandardButton.Yes:
                self._tracker.stop()
            elif reply == QMessageBox.StandardButton.Cancel:
                return

        self._tray_icon.hide()
        QApplication.quit()

    def closeEvent(self, event: QCloseEvent) -> None:
        """Обработка закрытия окна."""
        if self._config.settings.minimize_to_tray:
            event.ignore()
            self.hide()
            self._tray_icon.showMessage(
                "Work Chronometer",
                "Приложение свёрнуто в трей",
                QSystemTrayIcon.MessageIcon.Information,
                2000
            )
        else:
            event.ignore()
            self._quit_app()
