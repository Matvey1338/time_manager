"""Модель активности приложений."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional
import uuid


class ActivityType(Enum):
    """Тип активности."""
    PRODUCTIVE = "productive"
    NEUTRAL = "neutral"
    DISTRACTING = "distracting"
    UNKNOWN = "unknown"


@dataclass
class Activity:
    """Модель активности (использование приложения)."""

    id: str = field(default_factory = lambda: str(uuid.uuid4()))
    session_id: str = ""
    application_name: str = ""
    window_title: str = ""
    start_time: datetime = field(default_factory = datetime.now)
    end_time: Optional[datetime] = None
    duration: int = 0  # в секундах
    activity_type: ActivityType = ActivityType.UNKNOWN

    @property
    def is_active(self) -> bool:
        """Проверка, активна ли запись."""
        return self.end_time is None

    def stop(self) -> None:
        """Остановить запись активности."""
        self.end_time = datetime.now()
        if self.start_time:
            self.duration = int((self.end_time - self.start_time).total_seconds())

    def to_dict(self) -> dict:
        """Преобразовать в словарь."""
        return {
            "id": self.id,
            "session_id": self.session_id,
            "application_name": self.application_name,
            "window_title": self.window_title,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration": self.duration,
            "activity_type": self.activity_type.value
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Activity":
        """Создать объект из словаря."""
        return cls(
            id = data["id"],
            session_id = data["session_id"],
            application_name = data["application_name"],
            window_title = data["window_title"],
            start_time = datetime.fromisoformat(data["start_time"]),
            end_time = datetime.fromisoformat(data["end_time"]) if data["end_time"] else None,
            duration = data["duration"],
            activity_type = ActivityType(data["activity_type"])
        )
