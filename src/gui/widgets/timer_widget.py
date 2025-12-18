"""Виджет таймера."""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QSizePolicy, QSpacerItem
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
        # Главный layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Карточка таймера
        card = QFrame()
        card.setObjectName("timerCard")
        card.setMinimumHeight(220)
        card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(30, 25, 30, 25)
        card_layout.setSpacing(15)

        # Статус
        self._status_label = QLabel("⏸ Готов к работе")
        self._status_label.setObjectName("statusLabel")
        self._status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(self._status_label)

        # Таймер
        self._timer_label = QLabel("00:00:00")
        self._timer_label.setObjectName("timerLabel")
        self._timer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._timer_label.setMinimumHeight(80)
        card_layout.addWidget(self._timer_label)

        # Информация о сегодняшнем дне
        self._today_label = QLabel("📅 Сегодня: 0ч 0мин")
        self._today_label.setObjectName("todayLabel")
        self._today_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(self._today_label)

        # Контейнер для кнопок (чтобы кнопки не растягивались)
        buttons_container = QWidget()
        buttons_layout = QHBoxLayout(buttons_container)
        buttons_layout.setContentsMargins(0, 10, 0, 0)
        buttons_layout.setSpacing(15)

        # Спейсер слева
        buttons_layout.addSpacerItem(
            QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        )

        # Кнопка Старт
        self._start_btn = QPushButton("▶  Старт")
        self._start_btn.setObjectName("startButton")
        self._start_btn.setFixedSize(130, 50)
        self._start_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._start_btn.clicked.connect(self._on_start)
        buttons_layout.addWidget(self._start_btn)

        # Кнопка Пауза
        self._pause_btn = QPushButton("⏸  Пауза")
        self._pause_btn.setObjectName("pauseButton")
        self._pause_btn.setFixedSize(130, 50)
        self._pause_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._pause_btn.clicked.connect(self._on_pause)
        self._pause_btn.setEnabled(False)
        buttons_layout.addWidget(self._pause_btn)

        # Кнопка Стоп
        self._stop_btn = QPushButton("⏹  Стоп")
        self._stop_btn.setObjectName("stopButton")
        self._stop_btn.setFixedSize(130, 50)
        self._stop_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._stop_btn.clicked.connect(self._on_stop)
        self._stop_btn.setEnabled(False)
        buttons_layout.addWidget(self._stop_btn)

        # Спейсер справа
        buttons_layout.addSpacerItem(
            QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        )

        card_layout.addWidget(buttons_container)
        main_layout.addWidget(card)

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
            self._start_btn.setText("▶  Продолжить")
        else:
            self._start_btn.setText("▶  Старт")

    def _update_today_label(self) -> None:
        """Обновить метку общего времени за сегодня."""
        total = self._tracker.get_today_total()
        hours, remainder = divmod(total, 3600)
        minutes = remainder // 60
        self._today_label.setText(f"📅 Сегодня: {hours}ч {minutes}мин")

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
        self._status_label.setStyleSheet("color: #2E7D32; font-weight: bold;")
        self._update_buttons()

    def _on_session_paused(self) -> None:
        """Сессия на паузе."""
        self._status_label.setText("🟡 Пауза")
        self._status_label.setStyleSheet("color: #F57C00; font-weight: bold;")
        self._update_buttons()

    def _on_session_resumed(self) -> None:
        """Сессия возобновлена."""
        self._status_label.setText("🟢 Работа идёт...")
        self._status_label.setStyleSheet("color: #2E7D32; font-weight: bold;")
        self._update_buttons()

    def _on_session_stopped(self, session) -> None:
        """Сессия завершена."""
        self._status_label.setText("⏸ Готов к работе")
        self._status_label.setStyleSheet("color: #555555;")
        self._timer_label.setText("00:00:00")
        self._update_buttons()
        self._update_today_label()
