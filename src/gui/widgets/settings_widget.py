"""Виджет настроек."""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QSpinBox, QCheckBox, QGroupBox, QFormLayout,
    QPushButton, QComboBox, QMessageBox, QScrollArea,
    QFrame, QSizePolicy
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
        # Основной layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)

        # Заголовок
        title = QLabel("⚙️ Настройки")
        title.setObjectName("sectionTitle")
        main_layout.addWidget(title)

        # Scroll area для настроек
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("QScrollArea { background: transparent; }")

        # Контейнер для групп настроек
        content = QWidget()
        content.setStyleSheet("background: transparent;")
        content_layout = QVBoxLayout(content)
        content_layout.setSpacing(20)

        # === Группа настроек перерывов ===
        breaks_group = QGroupBox("☕ Перерывы")
        breaks_layout = QFormLayout(breaks_group)
        breaks_layout.setSpacing(15)
        breaks_layout.setContentsMargins(20, 25, 20, 20)

        self._short_break_interval = QSpinBox()
        self._short_break_interval.setRange(5, 120)
        self._short_break_interval.setSuffix(" мин")
        self._short_break_interval.setMinimumWidth(120)
        breaks_layout.addRow("Интервал коротких перерывов:", self._short_break_interval)

        self._short_break_duration = QSpinBox()
        self._short_break_duration.setRange(1, 30)
        self._short_break_duration.setSuffix(" мин")
        self._short_break_duration.setMinimumWidth(120)
        breaks_layout.addRow("Длительность короткого перерыва:", self._short_break_duration)

        self._long_break_interval = QSpinBox()
        self._long_break_interval.setRange(30, 240)
        self._long_break_interval.setSuffix(" мин")
        self._long_break_interval.setMinimumWidth(120)
        breaks_layout.addRow("Интервал длинных перерывов:", self._long_break_interval)

        self._long_break_duration = QSpinBox()
        self._long_break_duration.setRange(5, 60)
        self._long_break_duration.setSuffix(" мин")
        self._long_break_duration.setMinimumWidth(120)
        breaks_layout.addRow("Длительность длинного перерыва:", self._long_break_duration)

        content_layout.addWidget(breaks_group)

        # === Группа уведомлений ===
        notifications_group = QGroupBox("🔔 Уведомления")
        notifications_layout = QVBoxLayout(notifications_group)
        notifications_layout.setSpacing(12)
        notifications_layout.setContentsMargins(20, 25, 20, 20)

        self._notifications_enabled = QCheckBox("Включить уведомления о перерывах")
        notifications_layout.addWidget(self._notifications_enabled)

        self._sound_enabled = QCheckBox("Звуковые уведомления")
        notifications_layout.addWidget(self._sound_enabled)

        content_layout.addWidget(notifications_group)

        # === Группа поведения ===
        behavior_group = QGroupBox("🖥️ Поведение")
        behavior_layout = QVBoxLayout(behavior_group)
        behavior_layout.setSpacing(12)
        behavior_layout.setContentsMargins(20, 25, 20, 20)

        self._auto_start = QCheckBox("Автоматически начинать отслеживание при запуске")
        behavior_layout.addWidget(self._auto_start)

        self._minimize_to_tray = QCheckBox("Сворачивать в системный трей при закрытии")
        behavior_layout.addWidget(self._minimize_to_tray)

        self._track_apps = QCheckBox("Отслеживать использование приложений")
        behavior_layout.addWidget(self._track_apps)

        # Таймаут простоя
        idle_widget = QWidget()
        idle_layout = QHBoxLayout(idle_widget)
        idle_layout.setContentsMargins(0, 10, 0, 0)
        idle_layout.setSpacing(10)

        idle_label = QLabel("Таймаут простоя:")
        idle_layout.addWidget(idle_label)

        self._idle_timeout = QSpinBox()
        self._idle_timeout.setRange(60, 1800)
        self._idle_timeout.setSuffix(" сек")
        self._idle_timeout.setMinimumWidth(120)
        idle_layout.addWidget(self._idle_timeout)

        idle_layout.addStretch()
        behavior_layout.addWidget(idle_widget)

        content_layout.addWidget(behavior_group)

        # Растяжка
        content_layout.addStretch()

        scroll.setWidget(content)
        main_layout.addWidget(scroll, 1)

        # === Кнопки ===
        buttons_frame = QFrame()
        buttons_frame.setObjectName("card")
        buttons_frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        buttons_layout = QHBoxLayout(buttons_frame)
        buttons_layout.setContentsMargins(15, 10, 15, 10)
        buttons_layout.setSpacing(15)

        buttons_layout.addStretch()

        reset_btn = QPushButton("🔄 Сбросить")
        reset_btn.setFixedSize(130, 45)
        reset_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        reset_btn.setStyleSheet("""
            QPushButton {
                background-color: #757575;
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #616161;
            }
        """)
        reset_btn.clicked.connect(self._reset_settings)
        buttons_layout.addWidget(reset_btn)

        save_btn = QPushButton("💾 Сохранить")
        save_btn.setObjectName("startButton")
        save_btn.setFixedSize(130, 45)
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        save_btn.clicked.connect(self._save_settings)
        buttons_layout.addWidget(save_btn)

        main_layout.addWidget(buttons_frame)

    def _load_settings(self) -> None:
        """Загрузить текущие настройки в форму."""
        settings = self._config.settings

        self._short_break_interval.setValue(settings.short_break_interval)
        self._short_break_duration.setValue(settings.short_break_duration)
        self._long_break_interval.setValue(settings.long_break_interval)
        self._long_break_duration.setValue(settings.long_break_duration)

        self._notifications_enabled.setChecked(settings.notifications_enabled)
        self._sound_enabled.setChecked(settings.sound_enabled)

        self._auto_start.setChecked(settings.auto_start_tracking)
        self._minimize_to_tray.setChecked(settings.start_minimized)
        self._track_apps.setChecked(settings.track_applications)
        self._idle_timeout.setValue(settings.idle_timeout)

    def _save_settings(self) -> None:
        """Сохранить настройки."""
        self._config.update_settings(
            short_break_interval=self._short_break_interval.value(),
            short_break_duration=self._short_break_duration.value(),
            long_break_interval=self._long_break_interval.value(),
            long_break_duration=self._long_break_duration.value(),
            notifications_enabled=self._notifications_enabled.isChecked(),
            sound_enabled=self._sound_enabled.isChecked(),
            auto_start_tracking=self._auto_start.isChecked(),
            start_minimized=self._minimize_to_tray.isChecked(),
            track_applications=self._track_apps.isChecked(),
            idle_timeout=self._idle_timeout.value()
        )

        QMessageBox.information(
            self,
            "✅ Настройки",
            "Настройки успешно сохранены!"
        )

    def _reset_settings(self) -> None:
        """Сбросить настройки по умолчанию."""
        reply = QMessageBox.question(
            self,
            "Подтверждение",
            "Вы уверены, что хотите сбросить все настройки на значения по умолчанию?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            from utils.config import AppSettings
            default = AppSettings()

            self._short_break_interval.setValue(default.short_break_interval)
            self._short_break_duration.setValue(default.short_break_duration)
            self._long_break_interval.setValue(default.long_break_interval)
            self._long_break_duration.setValue(default.long_break_duration)
            self._notifications_enabled.setChecked(default.notifications_enabled)
            self._sound_enabled.setChecked(default.sound_enabled)
            self._auto_start.setChecked(default.auto_start_tracking)
            self._minimize_to_tray.setChecked(default.start_minimized)
            self._track_apps.setChecked(default.track_applications)
            self._idle_timeout.setValue(default.idle_timeout)

            QMessageBox.information(self, "✅ Сброс", "Настройки сброшены на значения по умолчанию.")
