"""Стили и темы интерфейса."""

MAIN_STYLESHEET = """
/* === ОСНОВНЫЕ СТИЛИ === */
QMainWindow {
    background-color: #EAECF0;
}

QWidget {
    font-family: 'Segoe UI', 'Arial', sans-serif;
    font-size: 13px;
    color: #1C1C1C;
}

/* === КНОПКИ === */
QPushButton {
    background-color: #3B82F6;
    color: #FFFFFF;
    border: none;
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: bold;
    font-size: 13px;
}

QPushButton:hover {
    background-color: #2563EB;
}

QPushButton:pressed {
    background-color: #1D4ED8;
}

QPushButton:disabled {
    background-color: #9CA3AF;
    color: #E5E7EB;
}

QPushButton#startButton {
    background-color: #22C55E;
}

QPushButton#startButton:hover {
    background-color: #16A34A;
}

QPushButton#startButton:disabled {
    background-color: #86EFAC;
    color: #FFFFFF;
}

QPushButton#pauseButton {
    background-color: #F59E0B;
}

QPushButton#pauseButton:hover {
    background-color: #D97706;
}

QPushButton#pauseButton:disabled {
    background-color: #FCD34D;
    color: #FFFFFF;
}

QPushButton#stopButton {
    background-color: #EF4444;
}

QPushButton#stopButton:hover {
    background-color: #DC2626;
}

QPushButton#stopButton:disabled {
    background-color: #FCA5A5;
    color: #FFFFFF;
}

/* === КАРТОЧКИ === */
QFrame#timerCard {
    background-color: #FFFFFF;
    border: 1px solid #D1D5DB;
    border-radius: 12px;
}

QFrame#card, QFrame#statCard {
    background-color: #FFFFFF;
    border: 1px solid #D1D5DB;
    border-radius: 8px;
}

/* === МЕТКИ === */
QLabel {
    color: #1C1C1C;
    background: transparent;
}

QLabel#timerLabel {
    font-size: 56px;
    font-weight: bold;
    color: #111827;
}

QLabel#statusLabel {
    font-size: 15px;
    font-weight: 500;
    color: #4B5563;
}

QLabel#todayLabel {
    font-size: 13px;
    color: #6B7280;
}

QLabel#sectionTitle {
    font-size: 16px;
    font-weight: bold;
    color: #111827;
}

QLabel#cardTitle {
    font-size: 12px;
    font-weight: bold;
    color: #6B7280;
}

QLabel#cardValue {
    font-size: 20px;
    font-weight: bold;
    color: #111827;
}

/* === ТАБЛИЦЫ === */
QTableWidget {
    background-color: #FFFFFF;
    border: 1px solid #D1D5DB;
    border-radius: 6px;
    gridline-color: #E5E7EB;
    color: #1C1C1C;
    selection-background-color: #DBEAFE;
    selection-color: #1C1C1C;
    alternate-background-color: #F9FAFB;
}

QTableWidget::item {
    padding: 8px;
    color: #1C1C1C;
    background-color: #FFFFFF;
}

QTableWidget::item:alternate {
    background-color: #F9FAFB;
    color: #1C1C1C;
}

QTableWidget::item:selected {
    background-color: #DBEAFE;
    color: #1C1C1C;
}

QHeaderView::section {
    background-color: #F3F4F6;
    color: #374151;
    border: none;
    border-bottom: 1px solid #D1D5DB;
    border-right: 1px solid #E5E7EB;
    padding: 10px 8px;
    font-weight: bold;
    font-size: 12px;
}

QHeaderView::section:last {
    border-right: none;
}

QTableCornerButton::section {
    background-color: #F3F4F6;
    border: none;
}

/* === ВКЛАДКИ === */
QTabWidget::pane {
    border: 1px solid #D1D5DB;
    border-radius: 6px;
    background-color: #FFFFFF;
    top: -1px;
}

QTabBar::tab {
    background-color: #E5E7EB;
    color: #4B5563;
    border: 1px solid #D1D5DB;
    border-bottom: none;
    padding: 10px 20px;
    margin-right: 2px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    font-weight: 500;
}

QTabBar::tab:selected {
    background-color: #FFFFFF;
    color: #111827;
    font-weight: bold;
}

QTabBar::tab:hover:!selected {
    background-color: #F3F4F6;
}

/* === ГРУППЫ === */
QGroupBox {
    font-weight: bold;
    font-size: 13px;
    color: #111827;
    border: 1px solid #D1D5DB;
    border-radius: 8px;
    margin-top: 12px;
    padding-top: 20px;
    background-color: #FFFFFF;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 12px;
    padding: 0 6px;
    color: #111827;
    background-color: #FFFFFF;
}

/* === ПОЛЯ ВВОДА === */
QLineEdit {
    border: 1px solid #D1D5DB;
    border-radius: 4px;
    padding: 8px;
    background-color: #FFFFFF;
    color: #1C1C1C;
    font-size: 13px;
}

QLineEdit:focus {
    border-color: #3B82F6;
}

/* === SPINBOX === */
QSpinBox {
    border: 1px solid #D1D5DB;
    border-radius: 4px;
    padding: 6px 8px;
    background-color: #FFFFFF;
    color: #1C1C1C;
    font-size: 13px;
    padding-right: 20px;
}

QSpinBox:focus {
    border-color: #3B82F6;
}

QSpinBox::up-button {
    subcontrol-origin: border;
    subcontrol-position: top right;
    width: 20px;
    border-left: 1px solid #D1D5DB;
    border-bottom: 1px solid #D1D5DB;
    border-top-right-radius: 4px;
    background-color: #F3F4F6;
}

QSpinBox::up-button:hover {
    background-color: #E5E7EB;
}

QSpinBox::up-arrow {
    width: 0;
    height: 0;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-bottom: 5px solid #374151;
}

QSpinBox::down-button {
    subcontrol-origin: border;
    subcontrol-position: bottom right;
    width: 20px;
    border-left: 1px solid #D1D5DB;
    border-bottom-right-radius: 4px;
    background-color: #F3F4F6;
}

QSpinBox::down-button:hover {
    background-color: #E5E7EB;
}

QSpinBox::down-arrow {
    width: 0;
    height: 0;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 5px solid #374151;
}

/* === COMBOBOX === */
QComboBox {
    border: 1px solid #D1D5DB;
    border-radius: 4px;
    padding: 6px 10px;
    background-color: #FFFFFF;
    color: #1C1C1C;
    font-size: 13px;
    min-width: 100px;
}

QComboBox:focus {
    border-color: #3B82F6;
}

QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 24px;
    border-left: 1px solid #D1D5DB;
    border-top-right-radius: 4px;
    border-bottom-right-radius: 4px;
    background-color: #F3F4F6;
}

QComboBox::down-arrow {
    width: 0;
    height: 0;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 6px solid #374151;
}

QComboBox QAbstractItemView {
    background-color: #FFFFFF;
    color: #1C1C1C;
    selection-background-color: #DBEAFE;
    selection-color: #1C1C1C;
    border: 1px solid #D1D5DB;
    outline: none;
}

QComboBox QAbstractItemView::item {
    padding: 6px 10px;
    color: #1C1C1C;
}

QComboBox QAbstractItemView::item:hover {
    background-color: #F3F4F6;
}

/* === ЧЕКБОКСЫ === */
QCheckBox {
    spacing: 8px;
    color: #1C1C1C;
    font-size: 13px;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border-radius: 4px;
    border: 2px solid #9CA3AF;
    background-color: #FFFFFF;
}

QCheckBox::indicator:checked {
    background-color: #3B82F6;
    border-color: #3B82F6;
    image: none;
}

QCheckBox::indicator:hover {
    border-color: #3B82F6;
}

/* === ПРОГРЕСС БАР === */
QProgressBar {
    border: none;
    border-radius: 4px;
    background-color: #E5E7EB;
    height: 16px;
    text-align: center;
    font-size: 11px;
    font-weight: bold;
    color: #374151;
}

QProgressBar::chunk {
    background-color: #22C55E;
    border-radius: 4px;
}

/* === СКРОЛЛБАРЫ === */
QScrollBar:vertical {
    background-color: #F3F4F6;
    width: 10px;
    border-radius: 5px;
    margin: 0;
}

QScrollBar::handle:vertical {
    background-color: #9CA3AF;
    border-radius: 5px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background-color: #6B7280;
}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical,
QScrollBar::add-page:vertical,
QScrollBar::sub-page:vertical {
    height: 0;
    background: none;
}

QScrollBar:horizontal {
    background-color: #F3F4F6;
    height: 10px;
    border-radius: 5px;
    margin: 0;
}

QScrollBar::handle:horizontal {
    background-color: #9CA3AF;
    border-radius: 5px;
    min-width: 30px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #6B7280;
}

QScrollBar::add-line:horizontal,
QScrollBar::sub-line:horizontal,
QScrollBar::add-page:horizontal,
QScrollBar::sub-page:horizontal {
    width: 0;
    background: none;
}

/* === SCROLL AREA === */
QScrollArea {
    background: transparent;
    border: none;
}

QScrollArea > QWidget > QWidget {
    background: transparent;
}

/* === СООБЩЕНИЯ === */
QMessageBox {
    background-color: #FFFFFF;
}

QMessageBox QLabel {
    color: #1C1C1C;
    font-size: 13px;
}
"""
