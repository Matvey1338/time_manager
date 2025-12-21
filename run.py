#!/usr/bin/env python3
"""Точка входа в приложение."""

import sys
import os


# Добавляем src в путь поиска модулей
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from main import main

if __name__ == "__main__":
    sys.exit(main())
    