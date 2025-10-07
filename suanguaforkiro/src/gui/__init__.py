"""
GUI module for the I Ching divination system.

This module provides a graphical user interface using tkinter.
"""

from .main_window import MainWindow
from .divination_frame import DivinationFrame
from .history_frame import HistoryFrame
from .hexagram_display import HexagramDisplay
from .styles import Styles
from .utils import (
    show_error, show_warning, show_info, show_success,
    ask_yes_no, ask_ok_cancel, validate_not_empty
)

__version__ = "1.0.0"

__all__ = [
    'MainWindow',
    'DivinationFrame',
    'HistoryFrame',
    'HexagramDisplay',
    'Styles',
    'show_error',
    'show_warning',
    'show_info',
    'show_success',
    'ask_yes_no',
    'ask_ok_cancel',
    'validate_not_empty',
]
