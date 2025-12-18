"""Вспомогательные функции."""

from datetime import datetime, date, timedelta
from typing import Tuple


def format_time(seconds: int) -> str:
    """
    Форматирование времени в человекочитаемый вид.

    Args:
        seconds: Количество секунд

    Returns:
        Строка в формате "HH:MM:SS"
    """
    hours, remainder = divmod(seconds, 3600)
    minutes, secs = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def format_duration(seconds: int) -> str:
    """
    Форматирование длительности в читаемый вид.

    Args:
        seconds: Количество секунд

    Returns:
        Строка вида "2ч 30мин" или "45мин"
    """
    hours, remainder = divmod(seconds, 3600)
    minutes, _ = divmod(remainder, 60)

    if hours > 0:
        return f"{hours}ч {minutes}мин"
    return f"{minutes}мин"


def get_today_date() -> date:
    """Получить текущую дату."""
    return date.today()


def get_week_bounds(target_date: date = None) -> Tuple[date, date]:
    """
    Получить границы недели для указанной даты.

    Args:
        target_date: Дата, для которой нужно найти границы недели

    Returns:
        Кортеж (начало_недели, конец_недели)
    """
    if target_date is None:
        target_date = date.today()

    start = target_date - timedelta(days = target_date.weekday())
    end = start + timedelta(days = 6)

    return start, end


def seconds_to_hms(seconds: int) -> Tuple[int, int, int]:
    """
    Конвертация секунд в часы, минуты, секунды.

    Args:
        seconds: Количество секунд

    Returns:
        Кортеж (часы, минуты, секунды)
    """
    hours, remainder = divmod(seconds, 3600)
    minutes, secs = divmod(remainder, 60)
    return hours, minutes, secs
