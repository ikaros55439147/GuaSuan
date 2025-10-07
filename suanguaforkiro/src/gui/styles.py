"""
Styles configuration for the GUI.

This module defines colors, fonts, and size constants for consistent UI styling.
"""

import sys
from typing import Tuple


class Theme:
    """Base theme class."""
    
    # Primary colors
    PRIMARY_COLOR = "#2C3E50"
    SECONDARY_COLOR = "#34495E"
    ACCENT_COLOR = "#F39C12"
    BACKGROUND_COLOR = "#ECF0F1"
    
    # Text colors
    TEXT_COLOR = "#2C3E50"
    LIGHT_TEXT = "#7F8C8D"
    WHITE_TEXT = "#FFFFFF"
    
    # Changing yao color
    CHANGING_YAO_COLOR = "#E74C3C"
    
    # Button colors
    BUTTON_BG = "#3498DB"
    BUTTON_HOVER = "#2980B9"
    BUTTON_ACTIVE = "#21618C"
    
    # Status colors
    SUCCESS_COLOR = "#27AE60"
    WARNING_COLOR = "#F39C12"
    ERROR_COLOR = "#E74C3C"
    INFO_COLOR = "#3498DB"


class LightTheme(Theme):
    """Light theme (default)."""
    
    PRIMARY_COLOR = "#2C3E50"
    SECONDARY_COLOR = "#34495E"
    ACCENT_COLOR = "#F39C12"
    BACKGROUND_COLOR = "#ECF0F1"
    
    TEXT_COLOR = "#2C3E50"
    LIGHT_TEXT = "#7F8C8D"
    WHITE_TEXT = "#FFFFFF"
    
    CHANGING_YAO_COLOR = "#E74C3C"
    
    BUTTON_BG = "#3498DB"
    BUTTON_HOVER = "#2980B9"
    BUTTON_ACTIVE = "#21618C"
    
    SUCCESS_COLOR = "#27AE60"
    WARNING_COLOR = "#F39C12"
    ERROR_COLOR = "#E74C3C"
    INFO_COLOR = "#3498DB"


class DarkTheme(Theme):
    """Dark theme."""
    
    PRIMARY_COLOR = "#ECF0F1"
    SECONDARY_COLOR = "#BDC3C7"
    ACCENT_COLOR = "#F39C12"
    BACKGROUND_COLOR = "#1C2833"
    
    TEXT_COLOR = "#ECF0F1"
    LIGHT_TEXT = "#95A5A6"
    WHITE_TEXT = "#FFFFFF"
    
    CHANGING_YAO_COLOR = "#E74C3C"
    
    BUTTON_BG = "#2980B9"
    BUTTON_HOVER = "#3498DB"
    BUTTON_ACTIVE = "#5DADE2"
    
    SUCCESS_COLOR = "#27AE60"
    WARNING_COLOR = "#F39C12"
    ERROR_COLOR = "#E74C3C"
    INFO_COLOR = "#3498DB"


class ElegantTheme(Theme):
    """Elegant purple theme."""
    
    PRIMARY_COLOR = "#6C3483"
    SECONDARY_COLOR = "#884EA0"
    ACCENT_COLOR = "#D4AF37"
    BACKGROUND_COLOR = "#F4ECF7"
    
    TEXT_COLOR = "#4A235A"
    LIGHT_TEXT = "#A569BD"
    WHITE_TEXT = "#FFFFFF"
    
    CHANGING_YAO_COLOR = "#C0392B"
    
    BUTTON_BG = "#8E44AD"
    BUTTON_HOVER = "#9B59B6"
    BUTTON_ACTIVE = "#BB8FCE"
    
    SUCCESS_COLOR = "#27AE60"
    WARNING_COLOR = "#F39C12"
    ERROR_COLOR = "#E74C3C"
    INFO_COLOR = "#8E44AD"


class TraditionalTheme(Theme):
    """Traditional Chinese theme with red and gold."""
    
    PRIMARY_COLOR = "#8B0000"
    SECONDARY_COLOR = "#A52A2A"
    ACCENT_COLOR = "#FFD700"
    BACKGROUND_COLOR = "#FFF8DC"
    
    TEXT_COLOR = "#2C1810"
    LIGHT_TEXT = "#8B7355"
    WHITE_TEXT = "#FFFFFF"
    
    CHANGING_YAO_COLOR = "#DC143C"
    
    BUTTON_BG = "#B22222"
    BUTTON_HOVER = "#CD5C5C"
    BUTTON_ACTIVE = "#F08080"
    
    SUCCESS_COLOR = "#228B22"
    WARNING_COLOR = "#FF8C00"
    ERROR_COLOR = "#DC143C"
    INFO_COLOR = "#B22222"


class Colors:
    """Color scheme for the application (dynamic based on current theme)."""
    
    _current_theme = LightTheme
    
    @classmethod
    def set_theme(cls, theme_class):
        """Set the current theme."""
        cls._current_theme = theme_class
    
    @classmethod
    def get_theme_name(cls) -> str:
        """Get the current theme name."""
        return cls._current_theme.__name__.replace('Theme', '')
    
    # Dynamic properties that reference the current theme
    @property
    def PRIMARY_COLOR(self):
        return self._current_theme.PRIMARY_COLOR
    
    @property
    def SECONDARY_COLOR(self):
        return self._current_theme.SECONDARY_COLOR
    
    @property
    def ACCENT_COLOR(self):
        return self._current_theme.ACCENT_COLOR
    
    @property
    def BACKGROUND_COLOR(self):
        return self._current_theme.BACKGROUND_COLOR
    
    @property
    def TEXT_COLOR(self):
        return self._current_theme.TEXT_COLOR
    
    @property
    def LIGHT_TEXT(self):
        return self._current_theme.LIGHT_TEXT
    
    @property
    def WHITE_TEXT(self):
        return self._current_theme.WHITE_TEXT
    
    @property
    def CHANGING_YAO_COLOR(self):
        return self._current_theme.CHANGING_YAO_COLOR
    
    @property
    def BUTTON_BG(self):
        return self._current_theme.BUTTON_BG
    
    @property
    def BUTTON_HOVER(self):
        return self._current_theme.BUTTON_HOVER
    
    @property
    def BUTTON_ACTIVE(self):
        return self._current_theme.BUTTON_ACTIVE
    
    @property
    def SUCCESS_COLOR(self):
        return self._current_theme.SUCCESS_COLOR
    
    @property
    def WARNING_COLOR(self):
        return self._current_theme.WARNING_COLOR
    
    @property
    def ERROR_COLOR(self):
        return self._current_theme.ERROR_COLOR
    
    @property
    def INFO_COLOR(self):
        return self._current_theme.INFO_COLOR


# Create a singleton instance
colors_instance = Colors()


# Available themes
THEMES = {
    "Light": LightTheme,
    "Dark": DarkTheme,
    "Elegant": ElegantTheme,
    "Traditional": TraditionalTheme
}


class Fonts:
    """Font configuration for different platforms."""
    
    # Font sizes
    TITLE_SIZE = 20
    HEADING_SIZE = 14
    BODY_SIZE = 11
    BUTTON_SIZE = 12
    SMALL_SIZE = 9
    
    # Font weights
    BOLD = "bold"
    NORMAL = "normal"
    
    @staticmethod
    def get_default_font_family() -> str:
        """
        Get the default font family based on the platform.
        
        Returns:
            str: Font family name suitable for the current platform
        """
        if sys.platform == 'win32':
            return "Microsoft YaHei UI"
        elif sys.platform == 'darwin':
            return "PingFang TC"
        else:
            # Linux and other platforms
            return "Noto Sans CJK TC"
    
    @staticmethod
    def get_fallback_fonts() -> Tuple[str, ...]:
        """
        Get fallback font families for cross-platform compatibility.
        
        Returns:
            Tuple of font family names
        """
        return (
            "Microsoft YaHei UI",
            "PingFang TC",
            "Noto Sans CJK TC",
            "SimHei",
            "Arial Unicode MS",
            "sans-serif"
        )
    
    @classmethod
    def title_font(cls) -> Tuple[str, int, str]:
        """Get title font configuration."""
        return (cls.get_default_font_family(), cls.TITLE_SIZE, cls.BOLD)
    
    @classmethod
    def heading_font(cls) -> Tuple[str, int, str]:
        """Get heading font configuration."""
        return (cls.get_default_font_family(), cls.HEADING_SIZE, cls.BOLD)
    
    @classmethod
    def body_font(cls) -> Tuple[str, int]:
        """Get body text font configuration."""
        return (cls.get_default_font_family(), cls.BODY_SIZE)
    
    @classmethod
    def body_font_bold(cls) -> Tuple[str, int, str]:
        """Get bold body text font configuration."""
        return (cls.get_default_font_family(), cls.BODY_SIZE, cls.BOLD)
    
    @classmethod
    def button_font(cls) -> Tuple[str, int]:
        """Get button font configuration."""
        return (cls.get_default_font_family(), cls.BUTTON_SIZE)
    
    @classmethod
    def small_font(cls) -> Tuple[str, int]:
        """Get small text font configuration."""
        return (cls.get_default_font_family(), cls.SMALL_SIZE)


class Sizes:
    """Size constants for UI elements."""
    
    # Window dimensions
    WINDOW_WIDTH = 800
    WINDOW_HEIGHT = 600
    MIN_WINDOW_WIDTH = 600
    MIN_WINDOW_HEIGHT = 400
    
    # Button dimensions
    BUTTON_WIDTH = 20
    BUTTON_HEIGHT = 2
    SMALL_BUTTON_WIDTH = 15
    
    # Padding and spacing
    PADDING = 10
    LARGE_PADDING = 20
    SMALL_PADDING = 5
    
    # Hexagram display
    YAO_WIDTH = 100
    YAO_HEIGHT = 10
    YAO_GAP = 20  # Gap in the middle of yin yao
    YAO_SPACING = 15  # Vertical spacing between yaos
    
    # Text areas
    TEXT_AREA_HEIGHT = 15
    TEXT_AREA_WIDTH = 60
    
    # Entry fields
    ENTRY_WIDTH = 40
    
    # List box
    LISTBOX_HEIGHT = 15


class Styles:
    """
    Main styles class that combines all style configurations.
    
    This class provides easy access to all styling constants.
    """
    
    colors = colors_instance
    fonts = Fonts
    sizes = Sizes
    
    @classmethod
    def set_theme(cls, theme_name: str) -> None:
        """
        Set the application theme.
        
        Args:
            theme_name: Name of the theme ('Light', 'Dark', 'Elegant', 'Traditional')
        """
        if theme_name in THEMES:
            Colors.set_theme(THEMES[theme_name])
    
    @classmethod
    def get_current_theme(cls) -> str:
        """Get the name of the current theme."""
        return Colors.get_theme_name()
    
    @classmethod
    def get_available_themes(cls) -> list:
        """Get list of available theme names."""
        return list(THEMES.keys())
    
    @staticmethod
    def configure_platform_specific() -> dict:
        """
        Get platform-specific tkinter configuration.
        
        Returns:
            dict: Configuration options for tkinter
        """
        config = {}
        
        if sys.platform == 'darwin':
            # macOS specific settings
            config['theme'] = 'aqua'
            config['platform'] = 'macOS'
        elif sys.platform == 'win32':
            # Windows specific settings
            config['theme'] = 'vista'
            config['platform'] = 'Windows'
        else:
            # Linux specific settings
            config['theme'] = 'clam'
            config['platform'] = 'Linux'
        
        return config
    
    @staticmethod
    def get_platform_name() -> str:
        """
        Get the current platform name.
        
        Returns:
            str: Platform name (Windows, macOS, or Linux)
        """
        if sys.platform == 'darwin':
            return 'macOS'
        elif sys.platform == 'win32':
            return 'Windows'
        else:
            return 'Linux'
    
    @staticmethod
    def apply_dpi_scaling(root) -> None:
        """
        Apply DPI scaling for high-resolution displays.
        
        Args:
            root: The tkinter root window
        """
        try:
            # Try to enable DPI awareness on Windows
            if sys.platform == 'win32':
                try:
                    from ctypes import windll
                    windll.shcore.SetProcessDpiAwareness(1)
                except:
                    pass
            
            # Get DPI scaling factor
            dpi = root.winfo_fpixels('1i')
            scaling_factor = dpi / 96.0  # 96 DPI is the standard
            
            if scaling_factor > 1.0:
                # Apply scaling to fonts if needed
                # This is handled automatically by tkinter in most cases
                pass
                
        except Exception as e:
            # Silently fail if DPI detection doesn't work
            pass
