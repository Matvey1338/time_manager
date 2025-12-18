"""Монитор активности приложений."""

import logging
import sys
from datetime import datetime
from typing import Optional, Tuple
from PyQt6.QtCore import QObject, QTimer, pyqtSignal

from models.activity import Activity, ActivityType
from database.db_manager import DatabaseManager


class ActivityMonitor(QObject):
    """Мониторинг активных приложений."""

    # Сигналы
    activity_changed = pyqtSignal(str, str)  # app_name, window_title
    idle_detected = pyqtSignal(int)  # seconds of idle

    def __init__(self, db_manager: DatabaseManager, parent=None):
        super().__init__(parent)
        self._logger = logging.getLogger(__name__)
        self._db = db_manager

        self._current_activity: Optional[Activity] = None
        self._session_id: str = ""
        self._is_monitoring: bool = False

        # Таймер для проверки активного окна
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._check_active_window)
        self._timer.setInterval(2000)  # проверка каждые 2 секунды

        # Кэш последнего приложения
        self._last_app: str = ""
        self._last_title: str = ""

    def start_monitoring(self, session_id: str) -> None:
        """Начать мониторинг."""
        self._session_id = session_id
        self._is_monitoring = True
        self._timer.start()
        self._logger.info("Мониторинг активности запущен")

    def stop_monitoring(self) -> None:
        """Остановить мониторинг."""
        self._is_monitoring = False
        self._timer.stop()
        self._finish_current_activity()
        self._logger.info("Мониторинг активности остановлен")

    def _check_active_window(self) -> None:
        """Проверить текущее активное окно."""
        try:
            app_name, window_title = self._get_active_window_info()

            if app_name != self._last_app:
                self._finish_current_activity()
                self._start_new_activity(app_name, window_title)

                self._last_app = app_name
                self._last_title = window_title

                self.activity_changed.emit(app_name, window_title)
        except Exception as e:
            self._logger.debug(f"Ошибка получения активного окна: {e}")

    def _get_active_window_info(self) -> Tuple[str, str]:
        """Получить информацию об активном окне."""
        app_name = "Unknown"
        window_title = ""

        if sys.platform == "win32":
            try:
                import win32gui
                import win32process
                import psutil

                hwnd = win32gui.GetForegroundWindow()
                window_title = win32gui.GetWindowText(hwnd)

                _, pid = win32process.GetWindowThreadProcessId(hwnd)
                process = psutil.Process(pid)
                app_name = process.name()
            except ImportError:
                # Если win32gui недоступен, используем заглушку
                pass
            except Exception:
                pass

        elif sys.platform == "darwin":
            try:
                from AppKit import NSWorkspace
                active_app = NSWorkspace.sharedWorkspace().activeApplication()
                app_name = active_app.get("NSApplicationName", "Unknown")
            except ImportError:
                pass
            except Exception:
                pass

        else:  # Linux
            try:
                import subprocess
                result = subprocess.run(
                    ["xdotool", "getactivewindow", "getwindowname"],
                    capture_output = True, text = True
                )
                window_title = result.stdout.strip()

                result = subprocess.run(
                    ["xdotool", "getactivewindow", "getwindowpid"],
                    capture_output = True, text = True
                )
                pid = int(result.stdout.strip())

                import psutil
                process = psutil.Process(pid)
                app_name = process.name()
            except Exception:
                pass

        return app_name, window_title

    def _start_new_activity(self, app_name: str, window_title: str) -> None:
        """Начать запись новой активности."""
        self._current_activity = Activity(
            session_id = self._session_id,
            application_name = app_name,
            window_title = window_title,
            activity_type = self._classify_activity(app_name)
        )
        self._db.save_activity(self._current_activity)

    def _finish_current_activity(self) -> None:
        """Завершить текущую активность."""
        if self._current_activity:
            self._current_activity.stop()
            self._db.save_activity(self._current_activity)
            self._current_activity = None

    def _classify_activity(self, app_name: str) -> ActivityType:
        """Классификация активности по имени приложения."""
        app_lower = app_name.lower()

        productive_apps = {
            "code", "pycharm", "webstorm", "idea", "visual studio",
            "sublime", "atom", "vim", "nvim", "emacs",
            "word", "excel", "powerpoint", "outlook",
            "terminal", "cmd", "powershell", "iterm",
            "figma", "photoshop", "illustrator"
        }

        distracting_apps = {
            "youtube", "netflix", "twitch", "discord",
            "telegram", "whatsapp", "facebook", "twitter",
            "instagram", "tiktok", "reddit"
        }

        for app in productive_apps:
            if app in app_lower:
                return ActivityType.PRODUCTIVE

        for app in distracting_apps:
            if app in app_lower:
                return ActivityType.DISTRACTING

        return ActivityType.NEUTRAL
    