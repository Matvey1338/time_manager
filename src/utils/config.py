"""Модуль конфигурации приложения."""

import json
import logging
from pathlib import Path
from dataclasses import dataclass, asdict, field
from typing import Optional


@dataclass
class AppSettings:
    """Настройки приложения."""
    # Интервалы перерывов (в минутах)
    short_break_interval: int = 25
    short_break_duration: int = 5
    long_break_interval: int = 100
    long_break_duration: int = 15

    # Уведомления
    notifications_enabled: bool = True
    sound_enabled: bool = True

    # Автозапуск
    start_minimized: bool = False
    auto_start_tracking: bool = True

    # Отслеживание активности
    track_applications: bool = True
    idle_timeout: int = 300  # секунды бездействия для паузы

    # Интерфейс
    theme: str = "light"
    language: str = "ru"


class Config:
    """Класс управления конфигурацией."""

    def __init__(self, config_path: Optional[Path] = None):
        self._logger = logging.getLogger(__name__)

        if config_path is None:
            self._config_path = Path(__file__).parent.parent.parent / "data" / "config.json"
        else:
            self._config_path = config_path

        self._settings = self._load_settings()

    @property
    def settings(self) -> AppSettings:
        """Получить текущие настройки."""
        return self._settings

    def _load_settings(self) -> AppSettings:
        """Загрузить настройки из файла."""
        if self._config_path.exists():
            try:
                with open(self._config_path, "r", encoding = "utf-8") as f:
                    data = json.load(f)
                    return AppSettings(**data)
            except (json.JSONDecodeError, TypeError) as e:
                self._logger.warning(f"Ошибка загрузки конфигурации: {e}")

        return AppSettings()

    def save_settings(self) -> None:
        """Сохранить настройки в файл."""
        self._config_path.parent.mkdir(parents = True, exist_ok = True)

        with open(self._config_path, "w", encoding = "utf-8") as f:
            json.dump(asdict(self._settings), f, indent = 2, ensure_ascii = False)

        self._logger.info("Настройки сохранены")

    def update_settings(self, **kwargs) -> None:
        """Обновить настройки."""
        for key, value in kwargs.items():
            if hasattr(self._settings, key):
                setattr(self._settings, key, value)

        self.save_settings()
