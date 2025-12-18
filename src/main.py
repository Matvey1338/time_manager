"""Главный модуль приложения."""

import sys
import logging
from pathlib import Path

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

from gui.main_window import MainWindow
from database.db_manager import DatabaseManager
from utils.config import Config


def setup_logging() -> None:
    """Настройка системы логирования."""
    log_dir = Path(__file__).parent.parent / "data" / "logs"
    log_dir.mkdir(parents = True, exist_ok = True)

    logging.basicConfig(
        level = logging.INFO,
        format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers = [
            logging.FileHandler(log_dir / "app.log", encoding = "utf-8"),
            logging.StreamHandler()
        ]
    )


def main() -> int:
    """Главная функция запуска приложения."""
    setup_logging()
    logger = logging.getLogger(__name__)

    logger.info("Запуск приложения Work Chronometer")

    # Инициализация конфигурации
    config = Config()

    # Инициализация базы данных
    db_manager = DatabaseManager()
    db_manager.initialize()

    # Создание Qt приложения
    app = QApplication(sys.argv)
    app.setApplicationName("Work Chronometer")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("WorkChronometer")

    # Создание и отображение главного окна
    window = MainWindow(db_manager, config)
    window.show()

    logger.info("Приложение успешно запущено")

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
    