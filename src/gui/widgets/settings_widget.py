"""Виджет настроек."""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QSpinBox, QCheckBox, QGroupBox, QFormLayout,
    QPushButton, QMessageBox, QScrollArea, QFrame
)
from PyQt6.QtCore import Qt

from utils.config import Config


class SettingsWidget(QWidget):
    """Виджет настроек приложения."""

    def __init__(self, config: Config, parent=None):
        super().__init__(parent)
        self._config = config
        self._setup_ui()
        self._load_settings()

    def _setup_ui(self) -> None:
        """Настройка интерфейса."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(12)

        # Заголовок
        title = QLabel("Настройки")
        title.setObjectName("sectionTitle")
        main_layout.addWidget(title)

        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setSpacing(16)
        content_layout.setContentsMargins(0, 0, 8, 0)

        # === Группа перерывов ===
        breaks_group = QGroupBox("Напоминания о перерывах")
        breaks_layout = QFormLayout(breaks_group)
        breaks_layout.setSpacing(12)
        breaks_layout.setContentsMargins(15, 20, 15, 15)

        self._short_break_interval = QSpinBox()
        self._short_break_interval.setRange(5, 120)
        self._short_break_interval.setSuffix(" мин")
        self._short_break_interval.setMinimumWidth(100)
        self._short_break_interval.setToolTip("Как часто напоминать о коротком перерыве")
        breaks_layout.addRow("Короткий перерыв каждые:", self._short_break_interval)

        self._short_break_duration = QSpinBox()
        self._short_break_duration.setRange(1, 30)
        self._short_break_duration.setSuffix(" мин")
        self._short_break_duration.setMinimumWidth(100)
        self._short_break_duration.setToolTip("Рекомендуемая длительность короткого перерыва")
        breaks_layout.addRow("Длительность короткого:", self._short_break_duration)

        self._long_break_interval = QSpinBox()
        self._long_break_interval.setRange(30, 240)
        self._long_break_interval.setSuffix(" мин")
        self._long_break_interval.setMinimumWidth(100)
        self._long_break_interval.setToolTip("Как часто напоминать о длинном перерыве")
        breaks_layout.addRow("Длинный перерыв каждые:", self._long_break_interval)

        self._long_break_duration = QSpinBox()
        self._long_break_duration.setRange(5, 60)
        self._long_break_duration.setSuffix(" мин")
        self._long_break_duration.setMinimumWidth(100)
        self._long_break_duration.setToolTip("Рекомендуемая длительность длинного перерыва")
        breaks_layout.addRow("Длительность длинного:", self._long_break_duration)

        content_layout.addWidget(breaks_group)

        # === Группа уведомлений ===
        notifications_group = QGroupBox("Уведомления")
        notifications_layout = QVBoxLayout(notifications_group)
        notifications_layout.setSpacing(10)
        notifications_layout.setContentsMargins(15, 20, 15, 15)

        self._notifications_enabled = QCheckBox("Показывать уведомления о перерывах")
        self._notifications_enabled.setToolTip("Всплывающие уведомления когда пора отдохнуть")
        notifications_layout.addWidget(self._notifications_enabled)

        self._sound_enabled = QCheckBox("Звуковой сигнал при уведомлениях")
        self._sound_enabled.setToolTip("Воспроизводить звук вместе с уведомлением")
        notifications_layout.addWidget(self._sound_enabled)

        content_layout.addWidget(notifications_group)

        # === Группа отслеживания простоя ===
        idle_group = QGroupBox("Определение простоя")
        idle_layout = QVBoxLayout(idle_group)
        idle_layout.setSpacing(10)
        idle_layout.setContentsMargins(15, 20, 15, 15)

        self._idle_enabled = QCheckBox("Автоматически ставить на паузу при простое")
        self._idle_enabled.setToolTip(
            "Если вы не используете мышь и клавиатуру указанное время,\n"
            "таймер автоматически встанет на паузу"
        )
        idle_layout.addWidget(self._idle_enabled)

        idle_time_layout = QHBoxLayout()
        idle_time_layout.addWidget(QLabel("Считать простоем после:"))
        self._idle_timeout = QSpinBox()
        self._idle_timeout.setRange(60, 1800)
        self._idle_timeout.setSuffix(" сек")
        self._idle_timeout.setMinimumWidth(100)
        self._idle_timeout.setToolTip(
            "Время бездействия (нет движения мыши, нажатий клавиш),\n"
            "после которого таймер встанет на паузу.\n"
            "300 сек = 5 минут"
        )
        idle_time_layout.addWidget(self._idle_timeout)
        idle_time_layout.addStretch()
        idle_layout.addLayout(idle_time_layout)

        # Подсказка
        idle_hint = QLabel("Например: 300 сек = 5 мин, 600 сек = 10 мин")
        idle_hint.setStyleSheet("color: #6B7280; font-size: 11px;")
        idle_layout.addWidget(idle_hint)

        content_layout.addWidget(idle_group)

        # === Группа запуска ===
        startup_group = QGroupBox("При запуске")
        startup_layout = QVBoxLayout(startup_group)
        startup_layout.setSpacing(10)
        startup_layout.setContentsMargins(15, 20, 15, 15)

        self._auto_start = QCheckBox("Автоматически начинать отсчёт времени")
        self._auto_start.setToolTip("Таймер запустится сразу при открытии программы")
        startup_layout.addWidget(self._auto_start)

        self._minimize_to_tray = QCheckBox("Сворачивать в трей вместо закрытия")
        self._minimize_to_tray.setToolTip(
            "При нажатии на X окно свернётся в системный трей,\n"
            "а не закроется. Таймер продолжит работать."
        )
        startup_layout.addWidget(self._minimize_to_tray)

        content_layout.addWidget(startup_group)

        content_layout.addStretch()

        scroll.setWidget(content)
        main_layout.addWidget(scroll, 1)

        # === Кнопки ===
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)
        buttons_layout.addStretch()

        reset_btn = QPushButton("Сбросить")
        reset_btn.setMinimumWidth(100)
        reset_btn.setFixedHeight(34)
        reset_btn.clicked.connect(self._reset_settings)
        buttons_layout.addWidget(reset_btn)

        save_btn = QPushButton("Сохранить")
        save_btn.setObjectName("startButton")
        save_btn.setMinimumWidth(100)
        save_btn.setFixedHeight(34)
        save_btn.clicked.connect(self._save_settings)
        buttons_layout.addWidget(save_btn)

        main_layout.addLayout(buttons_layout)

    def _load_settings(self) -> None:
        """Загрузить настройки."""
        s = self._config.settings

        self._short_break_interval.setValue(s.short_break_interval)
        self._short_break_duration.setValue(s.short_break_duration)
        self._long_break_interval.setValue(s.long_break_interval)
        self._long_break_duration.setValue(s.long_break_duration)

        self._notifications_enabled.setChecked(s.notifications_enabled)
        self._sound_enabled.setChecked(s.sound_enabled)

        self._idle_enabled.setChecked(s.idle_detection_enabled)
        self._idle_timeout.setValue(s.idle_timeout)

        self._auto_start.setChecked(s.auto_start_tracking)
        self._minimize_to_tray.setChecked(s.minimize_to_tray)

    def _save_settings(self) -> None:
        """Сохранить настройки."""
        self._config.update_settings(
            short_break_interval=self._short_break_interval.value(),
            short_break_duration=self._short_break_duration.value(),
            long_break_interval=self._long_break_interval.value(),
            long_break_duration=self._long_break_duration.value(),
            notifications_enabled=self._notifications_enabled.isChecked(),
            sound_enabled=self._sound_enabled.isChecked(),
            idle_detection_enabled=self._idle_enabled.isChecked(),
            idle_timeout=self._idle_timeout.value(),
            auto_start_tracking=self._auto_start.isChecked(),
            minimize_to_tray=self._minimize_to_tray.isChecked()
        )

        QMessageBox.information(self, "Готово", "Настройки сохранены!")

    def _reset_settings(self) -> None:
        """Сбросить настройки."""
        reply = QMessageBox.question(
            self, "Подтверждение",
            "Сбросить все настройки на значения по умолчанию?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            from utils.config import AppSettings
            d = AppSettings()

            self._short_break_interval.setValue(d.short_break_interval)
            self._short_break_duration.setValue(d.short_break_duration)
            self._long_break_interval.setValue(d.long_break_interval)
            self._long_break_duration.setValue(d.long_break_duration)
            self._notifications_enabled.setChecked(d.notifications_enabled)
            self._sound_enabled.setChecked(d.sound_enabled)
            self._idle_enabled.setChecked(d.idle_detection_enabled)
            self._idle_timeout.setValue(d.idle_timeout)
            self._auto_start.setChecked(d.auto_start_tracking)
            self._minimize_to_tray.setChecked(d.minimize_to_tray)
