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
        self._update_buttons_state()

    def _setup_ui(self) -> None:
        """Настройка интерфейса."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Карточка таймера
        card = QFrame()
        card.setObjectName("timerCard")
        card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 20, 20, 20)
        card_layout.setSpacing(12)

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
        self._today_label.setObjectName("todayLabel")
        self._today_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(self._today_label)

        # Кнопки управления
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)
        buttons_layout.setContentsMargins(0, 8, 0, 0)

        buttons_layout.addStretch(1)

        # Кнопка Старт
        self._start_btn = QPushButton("Старт")
        self._start_btn.setObjectName("startButton")
        self._start_btn.setMinimumWidth(90)
        self._start_btn.setMaximumWidth(120)
        self._start_btn.setFixedHeight(36)
        self._start_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._start_btn.clicked.connect(self._on_start)
        buttons_layout.addWidget(self._start_btn)

        # Кнопка Пауза
        self._pause_btn = QPushButton("Пауза")
        self._pause_btn.setObjectName("pauseButton")
        self._pause_btn.setMinimumWidth(90)
        self._pause_btn.setMaximumWidth(120)
        self._pause_btn.setFixedHeight(36)
        self._pause_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._pause_btn.clicked.connect(self._on_pause)
        buttons_layout.addWidget(self._pause_btn)

        # Кнопка Стоп
        self._stop_btn = QPushButton("Стоп")
        self._stop_btn.setObjectName("stopButton")
        self._stop_btn.setMinimumWidth(90)
        self._stop_btn.setMaximumWidth(120)
        self._stop_btn.setFixedHeight(36)
        self._stop_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._stop_btn.clicked.connect(self._on_stop)
        buttons_layout.addWidget(self._stop_btn)

        buttons_layout.addStretch(1)

        card_layout.addLayout(buttons_layout)
        main_layout.addWidget(card)

        # Начальное обновление
        self._update_display()

    def _connect_signals(self) -> None:
        """Подключение сигналов."""
        self._tracker.time_updated.connect(self._on_time_updated)
        self._tracker.session_started.connect(self._on_session_started)
        self._tracker.session_paused.connect(self._on_session_paused)
        self._tracker.session_resumed.connect(self._on_session_resumed)
        self._tracker.session_stopped.connect(self._on_session_stopped)
        self._tracker.state_changed.connect(self._update_buttons_state)

    def _update_display(self) -> None:
        """Обновить отображение."""
        self._timer_label.setText(format_time(self._tracker.elapsed_seconds))
        self._update_today_label()

    def _update_buttons_state(self) -> None:
        """Обновить состояние кнопок."""
        is_running = self._tracker.is_running
        is_paused = self._tracker.is_paused
        has_session = self._tracker.has_active_session

        # Старт: активен когда НЕ работает (либо пауза, либо нет сессии)
        self._start_btn.setEnabled(not is_running)

        # Пауза: активна только когда работает
        self._pause_btn.setEnabled(is_running)

        # Стоп: активен когда есть сессия (работает или на паузе)
        self._stop_btn.setEnabled(has_session)

        # Меняем текст кнопки Старт
        if is_paused:
            self._start_btn.setText("Продолжить")
        else:
            self._start_btn.setText("Старт")

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

        # Обновляем общее время каждые 30 секунд
        if seconds % 30 == 0:
            self._update_today_label()

    def _on_session_started(self, session) -> None:
        """Сессия началась."""
        self._status_label.setText("● Работа идёт")
        self._status_label.setStyleSheet("color: #16A34A; font-weight: bold;")
        self._update_buttons_state()

    def _on_session_paused(self) -> None:
        """Сессия на паузе."""
        self._status_label.setText("● Пауза")
        self._status_label.setStyleSheet("color: #D97706; font-weight: bold;")
        self._update_buttons_state()

    def _on_session_resumed(self) -> None:
        """Сессия возобновлена."""
        self._status_label.setText("● Работа идёт")
        self._status_label.setStyleSheet("color: #16A34A; font-weight: bold;")
        self._update_buttons_state()

    def _on_session_stopped(self, session) -> None:
        """Сессия завершена."""
        self._status_label.setText("Готов к работе")
        self._status_label.setStyleSheet("color: #4B5563;")
        self._timer_label.setText("00:00:00")
        self._update_buttons_state()
        self._update_today_label()
