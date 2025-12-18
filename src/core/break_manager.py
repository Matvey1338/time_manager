"""Менеджер перерывов."""

import logging
from PyQt6.QtCore import QObject, QTimer, pyqtSignal

from utils.config import Config


class BreakManager(QObject):
    """Управление перерывами."""

    # Сигналы
    short_break_due = pyqtSignal()
    long_break_due = pyqtSignal()
    break_reminder = pyqtSignal(str, int)  # тип перерыва, длительность в минутах

    def __init__(self, config: Config, parent=None):
        super().__init__(parent)
        self._logger = logging.getLogger(__name__)
        self._config = config

        self._work_seconds: int = 0
        self._is_active: bool = False

        # Таймер для отсчета рабочего времени
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._on_tick)
        self._timer.setInterval(1000)

    def start(self) -> None:
        """Начать отслеживание перерывов."""
        self._is_active = True
        self._timer.start()
        self._logger.info("Менеджер перерывов запущен")

    def stop(self) -> None:
        """Остановить отслеживание."""
        self._is_active = False
        self._timer.stop()
        self._logger.info("Менеджер перерывов остановлен")

    def pause(self) -> None:
        """Приостановить (перерыв начался)."""
        self._timer.stop()

    def resume(self) -> None:
        """Продолжить после перерыва."""
        if self._is_active:
            self._timer.start()

    def reset(self) -> None:
        """Сбросить счетчик (после перерыва)."""
        self._work_seconds = 0

    def _on_tick(self) -> None:
        """Обработчик тика (каждую секунду)."""
        self._work_seconds += 1
        settings = self._config.settings

        work_minutes = self._work_seconds // 60

        # Проверка на длинный перерыв
        if work_minutes > 0 and work_minutes % settings.long_break_interval == 0:
            if self._work_seconds % 60 == 0:  # только в начале минуты
                self.long_break_due.emit()
                self.break_reminder.emit("long", settings.long_break_duration)
                self._logger.info("Пора сделать длинный перерыв!")

        # Проверка на короткий перерыв
        elif work_minutes > 0 and work_minutes % settings.short_break_interval == 0:
            if self._work_seconds % 60 == 0:
                self.short_break_due.emit()
                self.break_reminder.emit("short", settings.short_break_duration)
                self._logger.info("Пора сделать короткий перерыв!")
