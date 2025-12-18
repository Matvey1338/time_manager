"""Менеджер базы данных SQLite."""

import sqlite3
import logging
from pathlib import Path
from datetime import date, datetime
from typing import List, Optional, Dict, Any
from contextlib import contextmanager

from models.session import Session, SessionStatus
from models.activity import Activity, ActivityType


class DatabaseManager:
    """Класс для управления базой данных."""

    def __init__(self, db_path: Optional[Path] = None):
        self._logger = logging.getLogger(__name__)

        if db_path is None:
            self._db_path = Path(__file__).parent.parent.parent / "data" / "chronometer.db"
        else:
            self._db_path = db_path

        self._db_path.parent.mkdir(parents = True, exist_ok = True)

    @contextmanager
    def _get_connection(self):
        """Контекстный менеджер для подключения к БД."""
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            self._logger.error(f"Ошибка базы данных: {e}")
            raise
        finally:
            conn.close()

    def initialize(self) -> None:
        """Инициализация базы данных."""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Таблица сессий
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id TEXT PRIMARY KEY,
                    start_time TEXT NOT NULL,
                    end_time TEXT,
                    status TEXT NOT NULL,
                    total_duration INTEGER DEFAULT 0,
                    active_duration INTEGER DEFAULT 0,
                    idle_duration INTEGER DEFAULT 0,
                    breaks_count INTEGER DEFAULT 0,
                    notes TEXT DEFAULT ''
                )
            """)

            # Таблица активностей
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS activities (
                    id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    application_name TEXT NOT NULL,
                    window_title TEXT,
                    start_time TEXT NOT NULL,
                    end_time TEXT,
                    duration INTEGER DEFAULT 0,
                    activity_type TEXT DEFAULT 'unknown',
                    FOREIGN KEY (session_id) REFERENCES sessions(id)
                )
            """)

            # Таблица ежедневной статистики
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS daily_stats (
                    date TEXT PRIMARY KEY,
                    total_time INTEGER DEFAULT 0,
                    active_time INTEGER DEFAULT 0,
                    breaks_count INTEGER DEFAULT 0,
                    sessions_count INTEGER DEFAULT 0
                )
            """)

            # Индексы
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_sessions_date 
                ON sessions(start_time)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_activities_session 
                ON activities(session_id)
            """)

            self._logger.info("База данных инициализирована")

    # === Методы для работы с сессиями ===

    def save_session(self, session: Session) -> None:
        """Сохранить сессию."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO sessions 
                (id, start_time, end_time, status, total_duration, 
                 active_duration, idle_duration, breaks_count, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                session.id,
                session.start_time.isoformat(),
                session.end_time.isoformat() if session.end_time else None,
                session.status.value,
                session.total_duration,
                session.active_duration,
                session.idle_duration,
                session.breaks_count,
                session.notes
            ))

    def get_session(self, session_id: str) -> Optional[Session]:
        """Получить сессию по ID."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM sessions WHERE id = ?", (session_id,))
            row = cursor.fetchone()

            if row:
                return self._row_to_session(row)
        return None

    def get_sessions_by_date(self, target_date: date) -> List[Session]:
        """Получить все сессии за указанную дату."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            date_str = target_date.isoformat()
            cursor.execute("""
                SELECT * FROM sessions 
                WHERE date(start_time) = ?
                ORDER BY start_time DESC
            """, (date_str,))

            return [self._row_to_session(row) for row in cursor.fetchall()]

    def get_active_session(self) -> Optional[Session]:
        """Получить текущую активную сессию."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM sessions 
                WHERE status IN ('active', 'paused')
                ORDER BY start_time DESC
                LIMIT 1
            """)
            row = cursor.fetchone()

            if row:
                return self._row_to_session(row)
        return None

    def _row_to_session(self, row: sqlite3.Row) -> Session:
        """Преобразовать строку БД в объект Session."""
        return Session(
            id = row["id"],
            start_time = datetime.fromisoformat(row["start_time"]),
            end_time = datetime.fromisoformat(row["end_time"]) if row["end_time"] else None,
            status = SessionStatus(row["status"]),
            total_duration = row["total_duration"],
            active_duration = row["active_duration"],
            idle_duration = row["idle_duration"],
            breaks_count = row["breaks_count"],
            notes = row["notes"] or ""
        )

    # === Методы для работы с активностями ===

    def save_activity(self, activity: Activity) -> None:
        """Сохранить активность."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO activities 
                (id, session_id, application_name, window_title, 
                 start_time, end_time, duration, activity_type)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                activity.id,
                activity.session_id,
                activity.application_name,
                activity.window_title,
                activity.start_time.isoformat(),
                activity.end_time.isoformat() if activity.end_time else None,
                activity.duration,
                activity.activity_type.value
            ))

    def get_activities_by_session(self, session_id: str) -> List[Activity]:
        """Получить все активности для сессии."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM activities 
                WHERE session_id = ?
                ORDER BY start_time DESC
            """, (session_id,))

            return [self._row_to_activity(row) for row in cursor.fetchall()]

    def get_app_statistics(self, target_date: date) -> Dict[str, int]:
        """Получить статистику по приложениям за день."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            date_str = target_date.isoformat()
            cursor.execute("""
                SELECT application_name, SUM(duration) as total_duration
                FROM activities
                WHERE date(start_time) = ?
                GROUP BY application_name
                ORDER BY total_duration DESC
            """, (date_str,))

            return {row["application_name"]: row["total_duration"]
                    for row in cursor.fetchall()}

    def _row_to_activity(self, row: sqlite3.Row) -> Activity:
        """Преобразовать строку БД в объект Activity."""
        return Activity(
            id = row["id"],
            session_id = row["session_id"],
            application_name = row["application_name"],
            window_title = row["window_title"] or "",
            start_time = datetime.fromisoformat(row["start_time"]),
            end_time = datetime.fromisoformat(row["end_time"]) if row["end_time"] else None,
            duration = row["duration"],
            activity_type = ActivityType(row["activity_type"])
        )

    # === Методы для статистики ===

    def get_daily_stats(self, target_date: date) -> Dict[str, Any]:
        """Получить статистику за день."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            date_str = target_date.isoformat()

            cursor.execute("""
                SELECT 
                    COUNT(*) as sessions_count,
                    COALESCE(SUM(total_duration), 0) as total_time,
                    COALESCE(SUM(active_duration), 0) as active_time,
                    COALESCE(SUM(breaks_count), 0) as breaks_count
                FROM sessions
                WHERE date(start_time) = ?
            """, (date_str,))

            row = cursor.fetchone()
            return {
                "date": target_date,
                "sessions_count": row["sessions_count"],
                "total_time": row["total_time"],
                "active_time": row["active_time"],
                "breaks_count": row["breaks_count"]
            }

    def get_weekly_stats(self, start_date: date, end_date: date) -> List[Dict[str, Any]]:
        """Получить статистику за период."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    date(start_time) as date,
                    COUNT(*) as sessions_count,
                    COALESCE(SUM(total_duration), 0) as total_time,
                    COALESCE(SUM(active_duration), 0) as active_time
                FROM sessions
                WHERE date(start_time) BETWEEN ? AND ?
                GROUP BY date(start_time)
                ORDER BY date(start_time)
            """, (start_date.isoformat(), end_date.isoformat()))

            return [dict(row) for row in cursor.fetchall()]
        