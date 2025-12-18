"""Стили и темы интерфейса."""

# Основные цвета
COLORS = {
    "primary": "#2196F3",
    "primary_dark": "#1976D2",
    "secondary": "#4CAF50",
    "accent": "#FF9800",
    "danger": "#f44336",
    "warning": "#FFC107",
    "background": "#F0F2F5",
    "surface": "#FFFFFF",
    "text_primary": "#1a1a2e",
    "text_secondary": "#555555",
    "border": "#D0D0D0",
}

# Основной стиль приложения
MAIN_STYLESHEET = """
/* === ОСНОВНЫЕ СТИЛИ === */
QMainWindow {
    background-color: #F0F2F5;
}

QWidget {
    font-family: 'Segoe UI', 'Arial', sans-serif;
    font-size: 13px;
    color: #1a1a2e;
}

/* === КНОПКИ === */
QPushButton {
    background-color: #2196F3;
    color: #FFFFFF;
    border: none;
    border-radius: 8px;
    padding: 12px 24px;
    font-weight: bold;
    font-size: 14px;
    min-width: 100px;
    min-height: 44px;
}

QPushButton:hover {
    background-color: #1976D2;
}

QPushButton:pressed {
    background-color: #1565C0;
}

QPushButton:disabled {
    background-color: #B0B0B0;
    color: #FFFFFF;
}

QPushButton#startButton {
    background-color: #4CAF50;
}

QPushButton#startButton:hover {
    background-color: #388E3C;
}

QPushButton#startButton:disabled {
    background-color: #A5D6A7;
}

QPushButton#pauseButton {
    background-color: #FF9800;
}

QPushButton#pauseButton:hover {
    background-color: #F57C00;
}

QPushButton#pauseButton:disabled {
    background-color: #FFCC80;
}

QPushButton#stopButton {
    background-color: #f44336;
}

QPushButton#stopButton:hover {
    background-color: #d32f2f;
}

QPushButton#stopButton:disabled {
    background-color: #EF9A9A;
}

/* === КАРТОЧКИ === */
QFrame#card {
    background-color: #FFFFFF;
    border: 1px solid #D0D0D0;
    border-radius: 12px;
    padding: 10px;
}

QFrame#timerCard {
    background-color: #FFFFFF;
    border: 2px solid #E0E0E0;
    border-radius: 16px;
}

QFrame#statCard {
    background-color: #FFFFFF;
    border: 1px solid #E0E0E0;
    border-radius: 10px;
    min-width: 150px;
}

/* === МЕТКИ === */
QLabel {
    color: #1a1a2e;
    background-color: transparent;
}

QLabel#timerLabel {
    font-size: 64px;
    font-weight: bold;
    color: #1a1a2e;
    padding: 10px;
}

QLabel#statusLabel {
    font-size: 16px;
    font-weight: 500;
    color: #555555;
    padding: 5px;
}

QLabel#todayLabel {
    font-size: 14px;
    color: #666666;
    padding: 5px;
}

QLabel#sectionTitle {
    font-size: 18px;
    font-weight: bold;
    color: #1a1a2e;
    padding: 5px 0px;
}

QLabel#cardTitle {
    font-size: 13px;
    font-weight: bold;
    color: #666666;
}

QLabel#cardValue {
    font-size: 22px;
    font-weight: bold;
    color: #1a1a2e;
}

/* === ТАБЛИЦЫ === */
QTableWidget {
    background-color: #FFFFFF;
    border: 1px solid #D0D0D0;
    border-radius: 8px;
    gridline-color: #E8E8E8;
    color: #1a1a2e;
    selection-background-color: #E3F2FD;
    selection-color: #1a1a2e;
}

QTableWidget::item {
    padding: 10px;
    color: #1a1a2e;
    border-bottom: 1px solid #F0F0F0;
}

QTableWidget::item:selected {
    background-color: #E3F2FD;
    color: #1a1a2e;
}

QHeaderView::section {
    background-color: #F5F5F5;
    color: #333333;
    border: none;
    border-bottom: 2px solid #E0E0E0;
    padding: 12px 8px;
    font-weight: bold;
    font-size: 13px;
}

QTableCornerButton::section {
    background-color: #F5F5F5;
    border: none;
}

/* === ВКЛАДКИ === */
QTabWidget::pane {
    border: 1px solid #D0D0D0;
    border-radius: 8px;
    background-color: #FFFFFF;
    top: -1px;
}

QTabBar::tab {
    background-color: #E8E8E8;
    color: #555555;
    border: 1px solid #D0D0D0;
    border-bottom: none;
    padding: 12px 24px;
    margin-right: 4px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    font-weight: 500;
}

QTabBar::tab:selected {
    background-color: #FFFFFF;
    color: #1a1a2e;
    border-bottom: 2px solid #2196F3;
    font-weight: bold;
}

QTabBar::tab:hover:!selected {
    background-color: #F0F0F0;
}

/* === ГРУППЫ === */
QGroupBox {
    font-weight: bold;
    font-size: 14px;
    color: #1a1a2e;
    border: 1px solid #D0D0D0;
    border-radius: 8px;
    margin-top: 16px;
    padding: 15px;
    padding-top: 25px;
    background-color: #FFFFFF;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 15px;
    padding: 0 8px;
    color: #1a1a2e;
    background-color: #FFFFFF;
}

/* === ПОЛЯ ВВОДА === */
QLineEdit, QSpinBox, QComboBox {
    border: 2px solid #D0D0D0;
    border-radius: 6px;
    padding: 10px;
    background-color: #FFFFFF;
    color: #1a1a2e;
    font-size: 14px;
    min-height: 20px;
}

QLineEdit:focus, QSpinBox:focus, QComboBox:focus {
    border-color: #2196F3;
}

QComboBox::drop-down {
    border: none;
    width: 30px;
}

QComboBox::down-arrow {
    width: 12px;
    height: 12px;
}

QComboBox QAbstractItemView {
    background-color: #FFFFFF;
    color: #1a1a2e;
    selection-background-color: #E3F2FD;
    selection-color: #1a1a2e;
    border: 1px solid #D0D0D0;
}

/* === ЧЕКБОКСЫ === */
QCheckBox {
    spacing: 10px;
    color: #1a1a2e;
    font-size: 14px;
}

QCheckBox::indicator {
    width: 22px;
    height: 22px;
    border-radius: 4px;
    border: 2px solid #888888;
    background-color: #FFFFFF;
}

QCheckBox::indicator:checked {
    background-color: #2196F3;
    border-color: #2196F3;
}

QCheckBox::indicator:hover {
    border-color: #2196F3;
}

/* === ПРОГРЕСС БАР === */
QProgressBar {
    border: none;
    border-radius: 6px;
    background-color: #E0E0E0;
    height: 12px;
    text-align: center;
    font-size: 11px;
    color: #333333;
}

QProgressBar::chunk {
    background-color: #4CAF50;
    border-radius: 6px;
}

/* === СКРОЛЛБАРЫ === */
QScrollBar:vertical {
    background-color: #F0F0F0;
    width: 12px;
    border-radius: 6px;
    margin: 2px;
}

QScrollBar::handle:vertical {
    background-color: #C0C0C0;
    border-radius: 5px;
    min-height: 40px;
}

QScrollBar::handle:vertical:hover {
    background-color: #A0A0A0;
}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    background-color: #F0F0F0;
    height: 12px;
    border-radius: 6px;
    margin: 2px;
}

QScrollBar::handle:horizontal {
    background-color: #C0C0C0;
    border-radius: 5px;
    min-width: 40px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #A0A0A0;
}

QScrollBar::add-line:horizontal,
QScrollBar::sub-line:horizontal {
    width: 0px;
}

/* === ТУЛТИПЫ === */
QToolTip {
    background-color: #333333;
    color: #FFFFFF;
    border: none;
    padding: 8px;
    border-radius: 4px;
    font-size: 12px;
}

/* === СООБЩЕНИЯ === */
QMessageBox {
    background-color: #FFFFFF;
}

QMessageBox QLabel {
    color: #1a1a2e;
    font-size: 14px;
}
"""
