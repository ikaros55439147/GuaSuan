"""
Main window for the GUI application.

This module provides the MainWindow class which manages the application's
main window and navigation between different frames.
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional
import sys

from .styles import Styles
from .utils import center_window, show_error, handle_exception, clear_frame
from .divination_frame import DivinationFrame
from .history_frame import HistoryFrame
from ..services.divination_service import DivinationService
from ..services.history_manager import HistoryManager
from ..data.hexagram_database import HexagramDatabase


class MainWindow:
    """
    Main application window.
    
    This class manages the root window and handles navigation between
    different frames (home, divination, history, about).
    """
    
    def __init__(self, root: tk.Tk, database: HexagramDatabase,
                 divination_service: DivinationService,
                 history_manager: HistoryManager):
        """
        Initialize the main window.
        
        Args:
            root: The tkinter root window
            database: HexagramDatabase instance
            divination_service: DivinationService instance
            history_manager: HistoryManager instance
        """
        self.root = root
        self.database = database
        self.divination_service = divination_service
        self.history_manager = history_manager
        
        # Configure root window
        self._configure_window()
        
        # Create main container frame with grid layout
        self.main_container = tk.Frame(
            self.root,
            bg=Styles.colors.BACKGROUND_COLOR
        )
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        # Configure grid weights for responsive layout
        self.main_container.grid_rowconfigure(0, weight=1)
        self.main_container.grid_columnconfigure(0, weight=1)
        
        # Show home screen
        self.show_home()
    
    def _configure_window(self) -> None:
        """Configure the root window properties."""
        # Set window title
        self.root.title("易經卜卦系統")
        
        # Apply DPI scaling for high-resolution displays
        Styles.apply_dpi_scaling(self.root)
        
        # Set window size and center it
        center_window(
            self.root,
            Styles.sizes.WINDOW_WIDTH,
            Styles.sizes.WINDOW_HEIGHT
        )
        
        # Set minimum window size
        self.root.minsize(
            Styles.sizes.MIN_WINDOW_WIDTH,
            Styles.sizes.MIN_WINDOW_HEIGHT
        )
        
        # Set background color
        self.root.configure(bg=Styles.colors.BACKGROUND_COLOR)
        
        # Handle window close event
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        
        # Configure platform-specific settings
        self._configure_platform_specific()
    
    def _configure_platform_specific(self) -> None:
        """Configure platform-specific window settings."""
        try:
            if sys.platform == 'darwin':
                # macOS specific settings
                self.root.tk.call('tk', 'scaling', 1.5)
            elif sys.platform == 'win32':
                # Windows specific settings
                try:
                    self.root.state('zoomed')  # Maximize on Windows
                except:
                    pass
        except Exception:
            # Ignore platform-specific configuration errors
            pass
    
    @handle_exception
    def _on_closing(self) -> None:
        """Handle window close event."""
        self.root.quit()
        self.root.destroy()
    
    def _clear_container(self) -> None:
        """Clear all widgets from the main container."""
        clear_frame(self.main_container)
    
    @handle_exception
    def show_home(self) -> None:
        """
        Display the home screen with main menu buttons.
        
        Shows:
        - Welcome message
        - Start divination button
        - View history button
        - About button
        """
        self._clear_container()
        
        # Create home frame with responsive grid layout
        home_frame = tk.Frame(
            self.main_container,
            bg=Styles.colors.BACKGROUND_COLOR
        )
        home_frame.grid(row=0, column=0, sticky="nsew")
        
        # Configure grid weights for responsive centering
        home_frame.grid_rowconfigure(0, weight=1)  # Top spacer
        home_frame.grid_rowconfigure(1, weight=0)  # Title
        home_frame.grid_rowconfigure(2, weight=0)  # Buttons
        home_frame.grid_rowconfigure(3, weight=1)  # Bottom spacer
        home_frame.grid_columnconfigure(0, weight=1)  # Center column
        
        # Title with decorative symbols
        title_label = tk.Label(
            home_frame,
            text="☯ 易經卜卦系統 ☯",
            font=Styles.fonts.title_font(),
            bg=Styles.colors.BACKGROUND_COLOR,
            fg=Styles.colors.PRIMARY_COLOR
        )
        title_label.grid(row=1, column=0, pady=(0, Styles.sizes.LARGE_PADDING * 2), sticky="n")
        
        # Button frame for consistent button sizing
        button_frame = tk.Frame(
            home_frame,
            bg=Styles.colors.BACKGROUND_COLOR
        )
        button_frame.grid(row=2, column=0, sticky="n")
        
        # Start divination button
        divination_btn = tk.Button(
            button_frame,
            text="開始卜卦 🎲",
            font=Styles.fonts.button_font(),
            bg=Styles.colors.BUTTON_BG,
            fg=Styles.colors.WHITE_TEXT,
            activebackground=Styles.colors.BUTTON_HOVER,
            width=Styles.sizes.BUTTON_WIDTH,
            height=Styles.sizes.BUTTON_HEIGHT,
            cursor="hand2",
            relief=tk.RAISED,
            bd=2,
            command=self.show_divination,
            padx=Styles.sizes.PADDING,
            pady=Styles.sizes.SMALL_PADDING
        )
        divination_btn.pack(pady=Styles.sizes.PADDING)
        
        # View history button
        history_btn = tk.Button(
            button_frame,
            text="查看歷史 📚",
            font=Styles.fonts.button_font(),
            bg=Styles.colors.BUTTON_BG,
            fg=Styles.colors.WHITE_TEXT,
            activebackground=Styles.colors.BUTTON_HOVER,
            width=Styles.sizes.BUTTON_WIDTH,
            height=Styles.sizes.BUTTON_HEIGHT,
            cursor="hand2",
            relief=tk.RAISED,
            bd=2,
            command=self.show_history,
            padx=Styles.sizes.PADDING,
            pady=Styles.sizes.SMALL_PADDING
        )
        history_btn.pack(pady=Styles.sizes.PADDING)
        
        # About button
        about_btn = tk.Button(
            button_frame,
            text="關於本程式 ℹ️",
            font=Styles.fonts.button_font(),
            bg=Styles.colors.BUTTON_BG,
            fg=Styles.colors.WHITE_TEXT,
            activebackground=Styles.colors.BUTTON_HOVER,
            width=Styles.sizes.BUTTON_WIDTH,
            height=Styles.sizes.BUTTON_HEIGHT,
            cursor="hand2",
            relief=tk.RAISED,
            bd=2,
            command=self.show_about,
            padx=Styles.sizes.PADDING,
            pady=Styles.sizes.SMALL_PADDING
        )
        about_btn.pack(pady=Styles.sizes.PADDING)
        
        # Theme button
        theme_btn = tk.Button(
            button_frame,
            text="切換主題 🎨",
            font=Styles.fonts.button_font(),
            bg=Styles.colors.ACCENT_COLOR,
            fg=Styles.colors.WHITE_TEXT,
            activebackground=Styles.colors.WARNING_COLOR,
            width=Styles.sizes.BUTTON_WIDTH,
            height=Styles.sizes.BUTTON_HEIGHT,
            cursor="hand2",
            relief=tk.RAISED,
            bd=2,
            command=self.show_theme_selector,
            padx=Styles.sizes.PADDING,
            pady=Styles.sizes.SMALL_PADDING
        )
        theme_btn.pack(pady=Styles.sizes.PADDING)
        
        # Add hover effects
        self._add_button_hover_effect(divination_btn)
        self._add_button_hover_effect(history_btn)
        self._add_button_hover_effect(about_btn)
        self._add_button_hover_effect(theme_btn)
    
    def _add_button_hover_effect(self, button: tk.Button) -> None:
        """
        Add hover effect to a button.
        
        Args:
            button: Button widget to add hover effect to
        """
        original_bg = button.cget('bg')
        hover_bg = Styles.colors.BUTTON_HOVER
        
        def on_enter(e):
            button.config(bg=hover_bg)
        
        def on_leave(e):
            button.config(bg=original_bg)
        
        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)
    
    @handle_exception
    def show_divination(self) -> None:
        """
        Display the divination interface.
        """
        self._clear_container()
        
        # Create divination frame
        DivinationFrame(
            parent=self.main_container,
            divination_service=self.divination_service,
            history_manager=self.history_manager,
            database=self.database,
            on_return=self.show_home
        )
    
    @handle_exception
    def show_history(self) -> None:
        """
        Display the history interface.
        """
        self._clear_container()
        
        # Create history frame
        HistoryFrame(
            parent=self.main_container,
            history_manager=self.history_manager,
            database=self.database,
            on_return=self.show_home
        )
    
    @handle_exception
    def show_about(self) -> None:
        """
        Display the about dialog with application information.
        """
        self._clear_container()
        
        # Create about frame
        about_frame = tk.Frame(
            self.main_container,
            bg=Styles.colors.BACKGROUND_COLOR
        )
        about_frame.pack(fill=tk.BOTH, expand=True)
        
        # Back button
        back_btn = tk.Button(
            about_frame,
            text="← 返回",
            font=Styles.fonts.button_font(),
            bg=Styles.colors.SECONDARY_COLOR,
            fg=Styles.colors.WHITE_TEXT,
            command=self.show_home,
            cursor="hand2"
        )
        back_btn.pack(anchor=tk.NW, padx=Styles.sizes.PADDING, pady=Styles.sizes.PADDING)
        
        # Content frame for centering
        content_frame = tk.Frame(
            about_frame,
            bg=Styles.colors.BACKGROUND_COLOR
        )
        content_frame.pack(expand=True)
        
        # Title
        title_label = tk.Label(
            content_frame,
            text="易經卜卦系統",
            font=Styles.fonts.title_font(),
            bg=Styles.colors.BACKGROUND_COLOR,
            fg=Styles.colors.PRIMARY_COLOR
        )
        title_label.pack(pady=(0, Styles.sizes.LARGE_PADDING))
        
        # Version info
        version_label = tk.Label(
            content_frame,
            text="版本 1.0.0",
            font=Styles.fonts.body_font(),
            bg=Styles.colors.BACKGROUND_COLOR,
            fg=Styles.colors.TEXT_COLOR
        )
        version_label.pack(pady=Styles.sizes.SMALL_PADDING)
        
        # Description
        description_text = (
            "這是一個基於《易經》的卜卦系統，\n"
            "使用傳統的三枚銅錢法進行占卜。\n\n"
            "系統包含完整的六十四卦資料，\n"
            "支援變爻解讀和歷史記錄管理。\n\n"
            "願易經的智慧為您指引方向。"
        )
        description_label = tk.Label(
            content_frame,
            text=description_text,
            font=Styles.fonts.body_font(),
            bg=Styles.colors.BACKGROUND_COLOR,
            fg=Styles.colors.TEXT_COLOR,
            justify=tk.CENTER
        )
        description_label.pack(pady=Styles.sizes.LARGE_PADDING)
        
        # Copyright
        copyright_label = tk.Label(
            content_frame,
            text="© 2025 易經卜卦系統",
            font=Styles.fonts.small_font(),
            bg=Styles.colors.BACKGROUND_COLOR,
            fg=Styles.colors.LIGHT_TEXT
        )
        copyright_label.pack(pady=(Styles.sizes.LARGE_PADDING, 0))
        
        # System info
        system_info = f"Python {sys.version.split()[0]} | {sys.platform}"
        system_label = tk.Label(
            content_frame,
            text=system_info,
            font=Styles.fonts.small_font(),
            bg=Styles.colors.BACKGROUND_COLOR,
            fg=Styles.colors.LIGHT_TEXT
        )
        system_label.pack(pady=Styles.sizes.SMALL_PADDING)
    
    @handle_exception
    def show_theme_selector(self) -> None:
        """
        Display the theme selector dialog.
        """
        from tkinter import messagebox
        
        # Create a custom dialog for theme selection
        dialog = tk.Toplevel(self.root)
        dialog.title("選擇主題")
        dialog.geometry("400x350")
        dialog.resizable(False, False)
        dialog.configure(bg=Styles.colors.BACKGROUND_COLOR)
        
        # Center the dialog
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Title
        title_label = tk.Label(
            dialog,
            text="選擇您喜歡的主題",
            font=Styles.fonts.heading_font(),
            bg=Styles.colors.BACKGROUND_COLOR,
            fg=Styles.colors.TEXT_COLOR
        )
        title_label.pack(pady=Styles.sizes.LARGE_PADDING)
        
        # Current theme display
        current_theme_label = tk.Label(
            dialog,
            text=f"當前主題：{Styles.get_current_theme()}",
            font=Styles.fonts.body_font(),
            bg=Styles.colors.BACKGROUND_COLOR,
            fg=Styles.colors.LIGHT_TEXT
        )
        current_theme_label.pack(pady=Styles.sizes.SMALL_PADDING)
        
        # Theme buttons frame
        themes_frame = tk.Frame(
            dialog,
            bg=Styles.colors.BACKGROUND_COLOR
        )
        themes_frame.pack(pady=Styles.sizes.PADDING, fill=tk.BOTH, expand=True)
        
        # Theme descriptions
        theme_descriptions = {
            "Light": "明亮主題 - 清新淡雅，適合日間使用",
            "Dark": "暗黑主題 - 深色護眼，適合夜間使用",
            "Elegant": "優雅主題 - 紫色高貴，典雅大方",
            "Traditional": "傳統主題 - 中國紅金，古典莊重"
        }
        
        def apply_theme(theme_name):
            """Apply the selected theme and refresh the UI."""
            Styles.set_theme(theme_name)
            dialog.destroy()
            # Refresh the main window
            self.show_home()
            messagebox.showinfo("主題已更新", f"已切換到「{theme_name}」主題")
        
        # Create theme buttons
        for theme_name in Styles.get_available_themes():
            theme_frame = tk.Frame(
                themes_frame,
                bg=Styles.colors.BACKGROUND_COLOR,
                relief=tk.RAISED,
                bd=1
            )
            theme_frame.pack(pady=Styles.sizes.SMALL_PADDING, padx=Styles.sizes.LARGE_PADDING, fill=tk.X)
            
            theme_btn = tk.Button(
                theme_frame,
                text=theme_name,
                font=Styles.fonts.button_font(),
                bg=Styles.colors.BUTTON_BG,
                fg=Styles.colors.WHITE_TEXT,
                width=15,
                cursor="hand2",
                command=lambda t=theme_name: apply_theme(t)
            )
            theme_btn.pack(side=tk.LEFT, padx=Styles.sizes.PADDING, pady=Styles.sizes.SMALL_PADDING)
            
            desc_label = tk.Label(
                theme_frame,
                text=theme_descriptions.get(theme_name, ""),
                font=Styles.fonts.small_font(),
                bg=Styles.colors.BACKGROUND_COLOR,
                fg=Styles.colors.LIGHT_TEXT,
                anchor=tk.W
            )
            desc_label.pack(side=tk.LEFT, padx=Styles.sizes.SMALL_PADDING, fill=tk.X, expand=True)
        
        # Close button
        close_btn = tk.Button(
            dialog,
            text="關閉",
            font=Styles.fonts.button_font(),
            bg=Styles.colors.SECONDARY_COLOR,
            fg=Styles.colors.WHITE_TEXT,
            command=dialog.destroy,
            cursor="hand2"
        )
        close_btn.pack(pady=Styles.sizes.PADDING)
        
        # Center the dialog on screen
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
    
    def run(self) -> None:
        """Start the main event loop."""
        self.root.mainloop()
