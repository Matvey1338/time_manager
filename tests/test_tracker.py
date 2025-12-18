"""Тесты для трекера времени."""

import unittest
from unittest.mock import Mock, MagicMock
from datetime import datetime

import sys

sys.path.insert(0, 'src')

from models.session import Session, SessionStatus


class TestSession(unittest.TestCase):
    """Тесты модели сессии."""

    def test_session_creation(self):
        """Тест создания сессии."""
        session = Session()

        self.assertIsNotNone(session.id)
        self.assertEqual(session.status, SessionStatus.ACTIVE)
        self.assertEqual(session.total_duration, 0)

    def test_session_pause(self):
        """Тест паузы сессии."""
        session = Session()
        session.pause()

        self.assertEqual(session.status, SessionStatus.PAUSED)
        self.assertTrue(session.is_paused)

    def test_session_resume(self):
        """Тест возобновления сессии."""
        session = Session()
        session.pause()
        session.resume()

        self.assertEqual(session.status, SessionStatus.ACTIVE)
        self.assertTrue(session.is_active)

    def test_session_complete(self):
        """Тест завершения сессии."""
        session = Session()
        session.complete()

        self.assertEqual(session.status, SessionStatus.COMPLETED)
        self.assertIsNotNone(session.end_time)

    def test_session_to_dict(self):
        """Тест сериализации сессии."""
        session = Session()
        data = session.to_dict()

        self.assertIn("id", data)
        self.assertIn("start_time", data)
        self.assertIn("status", data)

    def test_session_from_dict(self):
        """Тест десериализации сессии."""
        original = Session()
        original.total_duration = 3600
        data = original.to_dict()

        restored = Session.from_dict(data)

        self.assertEqual(restored.id, original.id)
        self.assertEqual(restored.total_duration, original.total_duration)


if __name__ == "__main__":
    unittest.main()
    