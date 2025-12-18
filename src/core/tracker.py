"""Основной трекер времени."""

import logging
from datetime import datetime
from typing import Optional, Callable
from PyQt6.QtCore import QObject, QTimer, pyqtSignal

from models.session import Session, SessionStatus
from database.db_manager import DatabaseManager


class TimeTracker(QObject):
    """Класс для отслеживания рабочего времени."""

    # Сигналы
    time_updated = pyqtSignal(int)  # общее время в секундах
    session_started = pyqtSignal(Session)
    session_paused = pyqtSignal()
    session_resumed = pyqtSignal()
    session_stopped = pyqtSignal(Session)

    def __init__(self, db_manager: DatabaseManager, parent=None):
        super().__init__(parent)
        self._logger = logging.getLogger(__name__)
        self._db = db_manager

        self._current_session: Optional[Session] = None
        self._elapsed_seconds: int = 0
        self._is_running: bool = False

        # Таймер для обновления времени
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._on_tick)
        self._timer.setInterval(1000)  # 1 секунда

        # Восстановление активной сессии
        self._restore_session()

    @property
    def current_session(self) -> Optional[Session]:
        """Текущая сессия."""
        return self._current_session

    @property
    def elapsed_seconds(self) -> int:
        """Прошедшее время в секундах."""
        return self._elapsed_seconds

    @property
    def is_running(self) -> bool:
        """Работает ли трекер."""
        return self._is_running

    @property
    def is_paused(self) -> bool:
        """На паузе ли трекер."""
        return (self._current_session is not None and
                self._current_session.is_paused)

    def _restore_session(self) -> None:
        """Восстановить активную сессию из БД."""
        session = self._db.get_active_session()
        if session:
            self._current_session = session
            self._elapsed_seconds = session.total_duration

            if session.is_active:
                self._is_running = True
                self._timer.start()

            self._logger.info(f"Восстановлена сессия: {session.id}")

    def start(self) -> None:
        """Начать новую сессию или продолжить текущую."""
        if self._current_session is None:
            # Создаем новую сессию
            self._current_session = Session()
            self._elapsed_seconds = 0
            self._db.save_session(self._current_session)
            self.session_started.emit(self._current_session)
            self._logger.info(f"Начата новая сессия: {self._current_session.id}")
        elif self._current_session.is_paused:
            # Возобновляем сессию
            self._current_session.resume()
            self._db.save_session(self._current_session)
            self.session_resumed.emit()
            self._logger.info("Сессия возобновлена")

        self._is_running = True
        self._timer.start()

    def pause(self) -> None:
        """Поставить на паузу."""
        if self._current_session and self._is_running:
            self._is_running = False
            self._timer.stop()

            self._current_session.pause()
            self._current_session.breaks_count += 1
            self._db.save_session(self._current_session)

            self.session_paused.emit()
            self._logger.info("Сессия приостановлена")

    def stop(self) -> None:
        """Остановить и завершить сессию."""
        if self._current_session:
            self._is_running = False
            self._timer.stop()

            self._current_session.complete()
            self._db.save_session(self._current_session)

            completed_session = self._current_session
            self._current_session = None
            self._elapsed_seconds = 0

            self.session_stopped.emit(completed_session)
            self._logger.info(f"Сессия завершена: {completed_session.id}")

    def _on_tick(self) -> None:
        """Обработчик тика таймера (каждую секунду)."""
        self._elapsed_seconds += 1

        if self._current_session:
            self._current_session.total_duration = self._elapsed_seconds
            self._current_session.active_duration = self._elapsed_seconds

            # Сохраняем каждую минуту
            if self._elapsed_seconds % 60 == 0:
                self._db.save_session(self._current_session)

        self.time_updated.emit(self._elapsed_seconds)

    def get_today_total(self) -> int:
        """Получить общее время за сегодня."""
        from datetime import date
        stats = self._db.get_daily_stats(date.today())
        return stats["total_time"]
    