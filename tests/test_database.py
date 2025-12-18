"""Тесты для базы данных."""

import unittest
import tempfile
from pathlib import Path
from datetime import date

import sys

sys.path.insert(0, 'src')

from database.db_manager import DatabaseManager
from models.session import Session


class TestDatabaseManager(unittest.TestCase):
    """Тесты менеджера базы данных."""

    def setUp(self):
        """Подготовка к тестам."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / "test.db"
        self.db = DatabaseManager(self.db_path)
        self.db.initialize()

    def test_save_and_get_session(self):
        """Тест сохранения и получения сессии."""
        session = Session()
        session.total_duration = 3600

        self.db.save_session(session)

        retrieved = self.db.get_session(session.id)

        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.id, session.id)
        self.assertEqual(retrieved.total_duration, 3600)

    def test_get_sessions_by_date(self):
        """Тест получения сессий по дате."""
        session = Session()
        self.db.save_session(session)

        sessions = self.db.get_sessions_by_date(date.today())

        self.assertEqual(len(sessions), 1)
        self.assertEqual(sessions[0].id, session.id)

    def test_get_daily_stats(self):
        """Тест получения дневной статистики."""
        session1 = Session()
        session1.total_duration = 1800
        self.db.save_session(session1)

        session2 = Session()
        session2.total_duration = 1800
        self.db.save_session(session2)

        stats = self.db.get_daily_stats(date.today())

        self.assertEqual(stats["sessions_count"], 2)
        self.assertEqual(stats["total_time"], 3600)


if __name__ == "__main__":
    unittest.main()
