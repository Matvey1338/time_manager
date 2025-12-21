"""Монитор активности приложений и определение простоя."""

import logging
import sys
import time
from datetime import datetime
from typing import Optional, Tuple
from PyQt6.QtCore import QObject, QTimer, pyqtSignal

from models.activity import Activity, ActivityType
from database.db_manager import DatabaseManager
from utils.config import Config


class ActivityMonitor(QObject):
    """Мониторинг активных приложений и простоя пользователя."""

    # Сигналы
    activity_changed = pyqtSignal(str, str)  # app_name, window_title
    idle_detected = pyqtSignal(int)  # seconds of idle
    user_returned = pyqtSignal()  # пользователь вернулся после простоя

    def __init__(self, db_manager: DatabaseManager, config: Config = None, parent=None):
        super().__init__(parent)
        self._logger = logging.getLogger(__name__)
        self._db = db_manager
        self._config = config

        self._current_activity: Optional[Activity] = None
        self._session_id: str = ""
        self._is_monitoring: bool = False

        # Отслеживание простоя
        self._last_input_time: float = time.time()
        self._is_idle: bool = False
        self._idle_seconds: int = 0

        # Таймер для проверки активного окна
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._check_activity)
        self._timer.setInterval(2000)  # проверка каждые 2 секунды

        # Кэш последнего приложения
        self._last_app: str = ""
        self._last_title: str = ""

    def start_monitoring(self, session_id: str) -> None:
        """Начать мониторинг."""
        self._session_id = session_id
        self._is_monitoring = True
        self._last_input_time = time.time()
        self._is_idle = False
        self._idle_seconds = 0
        self._timer.start()
        self._logger.info("Мониторинг активности запущен")

    def stop_monitoring(self) -> None:
        """Остановить мониторинг."""
        self._is_monitoring = False
        self._timer.stop()
        self._finish_current_activity()
        self._logger.info("Мониторинг активности остановлен")

    def _check_activity(self) -> None:
        """Проверить активность пользователя."""
        # Проверяем простой
        self._check_idle()

        # Проверяем активное окно
        if not self._is_idle:
            self._check_active_window()

    def _check_idle(self) -> None:
        """Проверить время простоя."""
        idle_time = self._get_idle_time()

        idle_timeout = 300  # по умолчанию 5 минут
        idle_enabled = True

        if self._config:
            idle_timeout = self._config.settings.idle_timeout
            idle_enabled = self._config.settings.idle_detection_enabled

        if not idle_enabled:
            return

        if idle_time >= idle_timeout:
            if not self._is_idle:
                self._is_idle = True
                self._idle_seconds = idle_time
                self._logger.info(f"Обнаружен простой: {idle_time} сек")
                self.idle_detected.emit(idle_time)
        else:
            if self._is_idle:
                self._is_idle = False
                self._logger.info("Пользователь вернулся")
                self.user_returned.emit()

    def _get_idle_time(self) -> int:
        """Получить время простоя в секундах."""
        if sys.platform == "win32":
            try:
                import ctypes

                class LASTINPUTINFO(ctypes.Structure):
                    _fields_ = [
                        ('cbSize', ctypes.c_uint),
                        ('dwTime', ctypes.c_uint),
                    ]

                lii = LASTINPUTINFO()
                lii.cbSize = ctypes.sizeof(LASTINPUTINFO)

                if ctypes.windll.user32.GetLastInputInfo(ctypes.byref(lii)):
                    millis = ctypes.windll.kernel32.GetTickCount() - lii.dwTime
                    return millis // 1000
            except Exception as e:
                self._logger.debug(f"Ошибка получения времени простоя: {e}")

        elif sys.platform == "darwin":
            try:
                import subprocess
                result = subprocess.run(
                    ["ioreg", "-c", "IOHIDSystem"],
                    capture_output=True, text=True
                )
                # Парсинг вывода для получения HIDIdleTime
                for line in result.stdout.split('\n'):
                    if 'HIDIdleTime' in line:
                        # Значение в наносекундах
                        idle_ns = int(line.split('=')[1].strip())
                        return idle_ns // 1_000_000_000
            except Exception as e:
                self._logger.debug(f"Ошибка получения времени простоя: {e}")

        else:  # Linux
            try:
                import subprocess
                result = subprocess.run(
                    ["xprintidle"],
                    capture_output=True, text=True
                )
                return int(result.stdout.strip()) // 1000
            except Exception:
                pass

        return 0

    def _check_active_window(self) -> None:
        """Проверить текущее активное окно."""
        try:
            app_name, window_title = self._get_active_window_info()

            if app_name and app_name != self._last_app:
                self._finish_current_activity()
                self._start_new_activity(app_name, window_title)

                self._last_app = app_name
                self._last_title = window_title

                self.activity_changed.emit(app_name, window_title)
        except Exception as e:
            self._logger.debug(f"Ошибка получения активного окна: {e}")

    def _get_active_window_info(self) -> Tuple[str, str]:
        """Получить информацию об активном окне."""
        app_name = ""
        window_title = ""

        if sys.platform == "win32":
            try:
                import ctypes
                from ctypes import wintypes

                user32 = ctypes.windll.user32

                # Получаем handle активного окна
                hwnd = user32.GetForegroundWindow()
                if not hwnd:
                    return "", ""

                # Получаем заголовок окна
                length = user32.GetWindowTextLengthW(hwnd) + 1
                buffer = ctypes.create_unicode_buffer(length)
                user32.GetWindowTextW(hwnd, buffer, length)
                window_title = buffer.value

                # Получаем PID процесса
                pid = wintypes.DWORD()
                user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))

                # Получаем имя процесса
                import psutil
                try:
                    process = psutil.Process(pid.value)
                    app_name = process.name()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    app_name = "Unknown"

            except Exception as e:
                self._logger.debug(f"Windows API error: {e}")

        elif sys.platform == "darwin":
            try:
                import subprocess
                script = '''
                tell application "System Events"
                    set frontApp to first application process whose frontmost is true
                    set appName to name of frontApp
                end tell
                return appName
                '''
                result = subprocess.run(
                    ["osascript", "-e", script],
                    capture_output=True, text=True
                )
                app_name = result.stdout.strip()
            except Exception:
                pass

        else:  # Linux
            try:
                import subprocess

                # Получаем ID активного окна
                result = subprocess.run(
                    ["xdotool", "getactivewindow"],
                    capture_output=True, text=True
                )
                window_id = result.stdout.strip()

                if window_id:
                    # Получаем заголовок
                    result = subprocess.run(
                        ["xdotool", "getwindowname", window_id],
                        capture_output=True, text=True
                    )
                    window_title = result.stdout.strip()

                    # Получаем PID
                    result = subprocess.run(
                        ["xdotool", "getwindowpid", window_id],
                        capture_output=True, text=True
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
        activity_type = self._classify_activity(app_name)

        self._current_activity = Activity(
            session_id=self._session_id,
            application_name=app_name,
            window_title=window_title,
            activity_type=activity_type
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

        # Получаем списки из конфига
        productive_apps = []
        distracting_apps = []

        if self._config:
            productive_apps = self._config.settings.productive_apps
            distracting_apps = self._config.settings.distracting_apps
        else:
            productive_apps = [
                "code", "pycharm", "webstorm", "idea", "visual studio",
                "sublime", "atom", "vim", "nvim", "emacs",
                "word", "excel", "powerpoint", "outlook",
                "terminal", "cmd", "powershell", "iterm",
                "figma", "photoshop", "illustrator"
            ]
            distracting_apps = [
                "youtube", "netflix", "twitch", "discord",
                "telegram", "whatsapp", "facebook", "twitter",
                "instagram", "tiktok", "reddit"
            ]

        for app in productive_apps:
            if app in app_lower:
                return ActivityType.PRODUCTIVE

        for app in distracting_apps:
            if app in app_lower:
                return ActivityType.DISTRACTING

        return ActivityType.NEUTRAL
