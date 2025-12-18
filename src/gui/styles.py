"""Стили и темы интерфейса."""

# Основные цвета
COLORS = {
    "primary": "#2196F3",
    "primary_dark": "#1976D2",
    "secondary": "#4CAF50",
    "accent": "#FF9800",
    "danger": "#f44336",
    "warning": "#FFC107",
    "background": "#FAFAFA",
    "surface": "#FFFFFF",
    "text_primary": "#212121",
    "text_secondary": "#757575",
    "border": "#E0E0E0",
}

# Основной стиль приложения
MAIN_STYLESHEET = """
QMainWindow {
    background-color: #FAFAFA;
}

QWidget {
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 14px;
}

/* Кнопки */
QPushButton {
    background-color: #2196F3;
    color: white;
    border: none;
    border-radius: 6px;
    padding: 10px 20px;
    font-weight: bold;
    min-height: 40px;
}

QPushButton:hover {
    background-color: #1976D2;
}

QPushButton:pressed {
    background-color: #1565C0;
}

QPushButton:disabled {
    background-color: #BDBDBD;
}

QPushButton#stopButton {
    background-color: #f44336;
}

QPushButton#stopButton:hover {
    background-color: #d32f2f;
}

QPushButton#pauseButton {
    background-color: #FF9800;
}

QPushButton#pauseButton:hover {
    background-color: #F57C00;
}

QPushButton#startButton {
    background-color: #4CAF50;
}

QPushButton#startButton:hover {
    background-color: #388E3C;
}

/* Карточки */
QFrame#card {
    background-color: white;
    border: 1px solid #E0E0E0;
    border-radius: 8px;
}

/* Метки */
QLabel#timerLabel {
    font-size: 72px;
    font-weight: bold;
    color: #212121;
}

QLabel#statusLabel {
    font-size: 16px;
    color: #757575;
}

QLabel#sectionTitle {
    font-size: 18px;
    font-weight: bold;
    color: #212121;
}

/* Таблицы */
QTableWidget {
    background-color: white;
    border: 1px solid #E0E0E0;
    border-radius: 4px;
    gridline-color: #E0E0E0;
}

QTableWidget::item {
    padding: 8px;
}

QHeaderView::section {
    background-color: #F5F5F5;
    border: none;
    border-bottom: 1px solid #E0E0E0;
    padding: 10px;
    font-weight: bold;
}

/* Вкладки */
QTabWidget::pane {
    border: 1px solid #E0E0E0;
    border-radius: 4px;
    background-color: white;
}

QTabBar::tab {
    background-color: #F5F5F5;
    border: 1px solid #E0E0E0;
    border-bottom: none;
    padding: 10px 20px;
    margin-right: 2px;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
}

QTabBar::tab:selected {
    background-color: white;
    border-bottom: 2px solid #2196F3;
}

/* Поля ввода */
QLineEdit, QSpinBox {
    border: 1px solid #E0E0E0;
    border-radius: 4px;
    padding: 8px;
    background-color: white;
}

QLineEdit:focus, QSpinBox:focus {
    border-color: #2196F3;
}

/* Чекбоксы */
QCheckBox {
    spacing: 8px;
}

QCheckBox::indicator {
    width: 20px;
    height: 20px;
    border-radius: 4px;
    border: 2px solid #757575;
}

QCheckBox::indicator:checked {
    background-color: #2196F3;
    border-color: #2196F3;
}

/* Прогресс бар */
QProgressBar {
    border: none;
    border-radius: 4px;
    background-color: #E0E0E0;
    height: 8px;
    text-align: center;
}

QProgressBar::chunk {
    background-color: #4CAF50;
    border-radius: 4px;
}

/* Скроллбары */
QScrollBar:vertical {
    background-color: #F5F5F5;
    width: 10px;
    border-radius: 5px;
}

QScrollBar::handle:vertical {
    background-color: #BDBDBD;
    border-radius: 5px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background-color: #9E9E9E;
}
"""
