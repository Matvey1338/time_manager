"""Модель рабочей сессии."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional
import uuid


class SessionStatus(Enum):
    """Статус сессии."""
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    IDLE = "idle"


@dataclass
class Session:
    """Модель рабочей сессии."""

    id: str = field(default_factory = lambda: str(uuid.uuid4()))
    start_time: datetime = field(default_factory = datetime.now)
    end_time: Optional[datetime] = None
    status: SessionStatus = SessionStatus.ACTIVE
    total_duration: int = 0  # в секундах
    active_duration: int = 0  # активное время в секундах
    idle_duration: int = 0  # время простоя в секундах
    breaks_count: int = 0
    notes: str = ""

    @property
    def is_active(self) -> bool:
        """Проверка, активна ли сессия."""
        return self.status == SessionStatus.ACTIVE

    @property
    def is_paused(self) -> bool:
        """Проверка, на паузе ли сессия."""
        return self.status == SessionStatus.PAUSED

    def pause(self) -> None:
        """Поставить сессию на паузу."""
        if self.status == SessionStatus.ACTIVE:
            self.status = SessionStatus.PAUSED

    def resume(self) -> None:
        """Возобновить сессию."""
        if self.status == SessionStatus.PAUSED:
            self.status = SessionStatus.ACTIVE

    def complete(self) -> None:
        """Завершить сессию."""
        self.status = SessionStatus.COMPLETED
        self.end_time = datetime.now()

    def to_dict(self) -> dict:
        """Преобразовать в словарь для сохранения."""
        return {
            "id": self.id,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "status": self.status.value,
            "total_duration": self.total_duration,
            "active_duration": self.active_duration,
            "idle_duration": self.idle_duration,
            "breaks_count": self.breaks_count,
            "notes": self.notes
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Session":
        """Создать объект из словаря."""
        return cls(
            id = data["id"],
            start_time = datetime.fromisoformat(data["start_time"]),
            end_time = datetime.fromisoformat(data["end_time"]) if data["end_time"] else None,
            status = SessionStatus(data["status"]),
            total_duration = data["total_duration"],
            active_duration = data["active_duration"],
            idle_duration = data["idle_duration"],
            breaks_count = data["breaks_count"],
            notes = data.get("notes", "")
        )
    