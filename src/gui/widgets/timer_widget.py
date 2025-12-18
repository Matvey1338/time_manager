"""Виджет таймера."""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QSizePolicy
)
from PyQt6.QtCore import Qt

from core.tracker import TimeTracker
from utils.helpers import format_time


class TimerWidget(QWidget):
    """Виджет отображения и управления таймером."""

    def __init__(self, tracker: TimeTracker, parent=None):
        super().__init__(parent)
        self._tracker = tracker
        self._setup_ui()
        self._connect_signals()
        self._update_display()

    def _setup_ui(self) -> None:
        """Настройка интерфейса."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Карточка таймера
        card = QFrame()
        card.setObjectName("card")
        card.setMinimumHeight(200)
        card_layout = QVBoxLayout(card)
        card_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.setSpacing(20)

        # Статус
        self._status_label = QLabel("Готов к работе")
        self._status_label.setObjectName("statusLabel")
        self._status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(self._status_label)

        # Таймер
        self._timer_label = QLabel("00:00:00")
        self._timer_label.setObjectName("timerLabel")
        self._timer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(self._timer_label)

        # Информация о сегодняшнем дне
        self._today_label = QLabel("Сегодня: 0ч 0мин")
        self._today_label.setObjectName("statusLabel")
        self._today_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(self._today_label)

        # Кнопки управления
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(15)
        buttons_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._start_btn = QPushButton("▶ Старт")
        self._start_btn.setObjectName("startButton")
        self._start_btn.setMinimumWidth(120)
        self._start_btn.clicked.connect(self._on_start)
        buttons_layout.addWidget(self._start_btn)

        self._pause_btn = QPushButton("⏸ Пауза")
        self._pause_btn.setObjectName("pauseButton")
        self._pause_btn.setMinimumWidth(120)
        self._pause_btn.clicked.connect(self._on_pause)
        self._pause_btn.setEnabled(False)
        buttons_layout.addWidget(self._pause_btn)

        self._stop_btn = QPushButton("⏹ Стоп")
        self._stop_btn.setObjectName("stopButton")
        self._stop_btn.setMinimumWidth(120)
        self._stop_btn.clicked.connect(self._on_stop)
        self._stop_btn.setEnabled(False)
        buttons_layout.addWidget(self._stop_btn)

        card_layout.addLayout(buttons_layout)
        layout.addWidget(card)

    def _connect_signals(self) -> None:
        """Подключение сигналов."""
        self._tracker.time_updated.connect(self._on_time_updated)
        self._tracker.session_started.connect(self._on_session_started)
        self._tracker.session_paused.connect(self._on_session_paused)
        self._tracker.session_resumed.connect(self._on_session_resumed)
        self._tracker.session_stopped.connect(self._on_session_stopped)

    def _update_display(self) -> None:
        """Обновить отображение."""
        self._timer_label.setText(format_time(self._tracker.elapsed_seconds))
        self._update_today_label()
        self._update_buttons()

    def _update_buttons(self) -> None:
        """Обновить состояние кнопок."""
        is_running = self._tracker.is_running
        is_paused = self._tracker.is_paused
        has_session = self._tracker.current_session is not None

        self._start_btn.setEnabled(not is_running)
        self._pause_btn.setEnabled(is_running)
        self._stop_btn.setEnabled(has_session)

        if is_paused:
            self._start_btn.setText("▶ Продолжить")
        else:
            self._start_btn.setText("▶ Старт")

    def _update_today_label(self) -> None:
        """Обновить метку общего времени за сегодня."""
        total = self._tracker.get_today_total()
        hours, remainder = divmod(total, 3600)
        minutes = remainder // 60
        self._today_label.setText(f"Сегодня: {hours}ч {minutes}мин")

    def _on_start(self) -> None:
        """Обработка нажатия кнопки Старт."""
        self._tracker.start()

    def _on_pause(self) -> None:
        """Обработка нажатия кнопки Пауза."""
        self._tracker.pause()

    def _on_stop(self) -> None:
        """Обработка нажатия кнопки Стоп."""
        self._tracker.stop()

    def _on_time_updated(self, seconds: int) -> None:
        """Обновление времени."""
        self._timer_label.setText(format_time(seconds))

        # Обновляем общее время каждую минуту
        if seconds % 60 == 0:
            self._update_today_label()

    def _on_session_started(self, session) -> None:
        """Сессия началась."""
        self._status_label.setText("🟢 Работа идёт...")
        self._status_label.setStyleSheet("color: #4CAF50;")
        self._update_buttons()

    def _on_session_paused(self) -> None:
        """Сессия на паузе."""
        self._status_label.setText("🟡 Пауза")
        self._status_label.setStyleSheet("color: #FF9800;")
        self._update_buttons()

    def _on_session_resumed(self) -> None:
        """Сессия возобновлена."""
        self._status_label.setText("🟢 Работа идёт...")
        self._status_label.setStyleSheet("color: #4CAF50;")
        self._update_buttons()

    def _on_session_stopped(self, session) -> None:
        """Сессия завершена."""
        self._status_label.setText("Готов к работе")
        self._status_label.setStyleSheet("")
        self._timer_label.setText("00:00:00")
        self._update_buttons()
        self._update_today_label()
        