"""Модуль конфигурации приложения."""

import json
import logging
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Optional, Dict, List


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

    # Поведение
    auto_start_tracking: bool = False  # НЕ запускать автоматически!
    minimize_to_tray: bool = False

    # Отслеживание простоя
    idle_detection_enabled: bool = True
    idle_timeout: int = 300  # секунды бездействия для автопаузы

    # Категории приложений для продуктивности
    productive_apps: List[str] = None
    distracting_apps: List[str] = None

    def __post_init__(self):
        if self.productive_apps is None:
            self.productive_apps = [
                "code", "pycharm", "webstorm", "idea", "visual studio",
                "sublime", "atom", "vim", "nvim", "emacs",
                "word", "excel", "powerpoint", "outlook",
                "terminal", "cmd", "powershell", "iterm",
                "figma", "photoshop", "illustrator", "notion"
            ]
        if self.distracting_apps is None:
            self.distracting_apps = [
                "youtube", "netflix", "twitch", "discord",
                "telegram", "whatsapp", "facebook", "twitter",
                "instagram", "tiktok", "reddit", "vk"
            ]


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
                with open(self._config_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    # Фильтруем только известные поля
                    valid_fields = {f.name for f in AppSettings.__dataclass_fields__.values()}
                    filtered_data = {k: v for k, v in data.items() if k in valid_fields}
                    return AppSettings(**filtered_data)
            except (json.JSONDecodeError, TypeError) as e:
                self._logger.warning(f"Ошибка загрузки конфигурации: {e}")

        return AppSettings()

    def save_settings(self) -> None:
        """Сохранить настройки в файл."""
        self._config_path.parent.mkdir(parents=True, exist_ok=True)

        with open(self._config_path, "w", encoding="utf-8") as f:
            json.dump(asdict(self._settings), f, indent=2, ensure_ascii=False)

        self._logger.info("Настройки сохранены")

    def update_settings(self, **kwargs) -> None:
        """Обновить настройки."""
        for key, value in kwargs.items():
            if hasattr(self._settings, key):
                setattr(self._settings, key, value)

        self.save_settings()

    def add_productive_app(self, app_name: str) -> None:
        """Добавить приложение в продуктивные."""
        app_lower = app_name.lower()
        if app_lower not in self._settings.productive_apps:
            self._settings.productive_apps.append(app_lower)
            # Удаляем из отвлекающих если было там
            if app_lower in self._settings.distracting_apps:
                self._settings.distracting_apps.remove(app_lower)
            self.save_settings()

    def add_distracting_app(self, app_name: str) -> None:
        """Добавить приложение в отвлекающие."""
        app_lower = app_name.lower()
        if app_lower not in self._settings.distracting_apps:
            self._settings.distracting_apps.append(app_lower)
            # Удаляем из продуктивных если было там
            if app_lower in self._settings.productive_apps:
                self._settings.productive_apps.remove(app_lower)
            self.save_settings()