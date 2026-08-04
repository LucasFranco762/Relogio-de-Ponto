"""Tema visual escuro da aplicação."""

THEME = """
QWidget { background: #121826; color: #e6edf7; font-family: Segoe UI; font-size: 10pt; }
QFrame#sidebar { background: #0d1320; }
QListWidget { font-size: 11pt; }
QLabel#brand { color: #55b7ff; font-size: 18pt; font-weight: 700; }
QPushButton { background: #1b2638; border: 0; border-radius: 6px; padding: 10px; text-align: left; }
QPushButton:hover, QPushButton:checked { background: #1769aa; }
QLineEdit, QSpinBox, QTimeEdit, QComboBox, QTableWidget { background: #1a2433; border: 1px solid #2b3a50; border-radius: 5px; padding: 7px; }
QTabWidget::pane { border: 1px solid #45617f; border-radius: 6px; background: #121826; }
QTabBar::tab { background: #223149; color: #dbeafe; border: 1px solid #45617f; border-bottom: 0; border-top-left-radius: 5px; border-top-right-radius: 5px; padding: 9px 18px; margin-right: 2px; }
QTabBar::tab:hover { background: #2d4966; color: #ffffff; }
QTabBar::tab:selected { background: #1769aa; color: #ffffff; border-color: #55b7ff; }
QHeaderView::section { background: #223149; padding: 7px; border: 0; }
QTableWidget { gridline-color: #29384d; }
QTableWidget::item:selected { background: #1769aa; color: #ffffff; border: 1px solid #55b7ff; }
QRadioButton { background: #1b2638; border: 1px solid #2b3a50; border-radius: 8px; padding: 14px; }
QRadioButton:checked { background: #203b59; border: 1px solid #55b7ff; }
QLabel#card { background: #1b2638; border-radius: 8px; padding: 18px; font-size: 14pt; }
"""


LAYOUT_02 = """
QWidget { background: #f4f7fb; color: #203047; font-family: Segoe UI; font-size: 10pt; }
QFrame#sidebar { background: #17324d; }
QLabel#brand { color: #70e1c1; font-size: 18pt; font-weight: 700; }
QListWidget { background: #17324d; color: #dceaf4; font-size: 11pt; border: 0; }
QListWidget::item { padding: 8px; border-radius: 6px; }
QListWidget::item:hover, QListWidget::item:selected { background: #245879; }
QLabel#topbar { background: #ffffff; color: #203047; }
QPushButton { background: #dcefe9; color: #173d42; border: 0; border-radius: 6px; padding: 10px; text-align: left; }
QPushButton:hover, QPushButton:checked { background: #70d6bd; color: #123437; }
QLineEdit, QSpinBox, QTimeEdit, QComboBox, QTableWidget { background: #ffffff; color: #203047; border: 1px solid #c8d7e5; border-radius: 5px; padding: 7px; }
QTabWidget::pane { border: 1px solid #d7e2ec; border-radius: 6px; background: #f8fbfd; }
QTabBar::tab { background: #e4edf4; color: #49627a; padding: 9px 18px; margin-right: 2px; }
QTabBar::tab:selected { background: #ffffff; color: #157a72; border-bottom: 2px solid #28b6a4; }
QHeaderView::section { background: #e4edf4; color: #203047; padding: 7px; border: 0; }
QTableWidget { gridline-color: #d7e2ec; }
QTableWidget::item:selected { background: #28a994; color: #ffffff; border: 1px solid #14796e; }
QRadioButton { background: #ffffff; border: 1px solid #c8d7e5; border-radius: 8px; padding: 14px; }
QRadioButton:checked { background: #e3f5f0; border: 1px solid #28b6a4; }
QLabel#card { background: #ffffff; border-radius: 8px; padding: 18px; font-size: 14pt; }
QStatusBar { background: #e8f0f5; color: #49627a; }
"""


LAYOUT_03 = """
QWidget { background: #201b2d; color: #f5efff; font-family: Segoe UI; font-size: 10pt; }
QFrame#sidebar { background: #171322; }
QLabel#brand { color: #d6a4ff; font-size: 18pt; font-weight: 700; }
QListWidget { background: #171322; color: #e8dcf8; font-size: 11pt; border: 0; }
QListWidget::item { padding: 8px; border-radius: 6px; }
QListWidget::item:hover, QListWidget::item:selected { background: #4b326d; }
QLabel#topbar { background: #2a233b; color: #f5efff; }
QPushButton { background: #382b50; color: #f5efff; border: 0; border-radius: 6px; padding: 10px; text-align: left; }
QPushButton:hover, QPushButton:checked { background: #a66bea; color: #ffffff; }
QLineEdit, QSpinBox, QTimeEdit, QComboBox, QTableWidget { background: #2b243b; color: #f5efff; border: 1px solid #55436d; border-radius: 5px; padding: 7px; }
QTabWidget::pane { border: 1px solid #4b3a60; border-radius: 6px; background: #241e33; }
QTabBar::tab { background: #312743; color: #cbb8df; padding: 9px 18px; margin-right: 2px; }
QTabBar::tab:selected { background: #3a2d50; color: #e0b6ff; border-bottom: 2px solid #c184ff; }
QHeaderView::section { background: #382d4b; color: #f5efff; padding: 7px; border: 0; }
QTableWidget { gridline-color: #49395c; }
QTableWidget::item:selected { background: #8e55c7; color: #ffffff; border: 1px solid #d6a4ff; }
QRadioButton { background: #2b243b; border: 1px solid #55436d; border-radius: 8px; padding: 14px; }
QRadioButton:checked { background: #43325a; border: 1px solid #c184ff; }
QLabel#card { background: #2b243b; border-radius: 8px; padding: 18px; font-size: 14pt; }
QStatusBar { background: #171322; color: #cbb8df; }
"""


LAYOUT_THEMES = (THEME, LAYOUT_02, LAYOUT_03)
