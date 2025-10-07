"""
Divination frame for the GUI application.

This module provides the DivinationFrame class which handles the divination
interface, including question input, divination execution, and result display.
"""

import tkinter as tk
from tkinter import scrolledtext
from typing import Optional, Callable

from .styles import Styles
from .utils import (
    show_error, show_success, show_warning, show_info,
    validate_not_empty, handle_exception, clear_frame
)
from .hexagram_display import HexagramDisplay
from .animations import DivinationAnimation, AnimationManager
from ..services.divination_service import DivinationService, DivinationResult
from ..services.history_manager import HistoryManager
from ..data.hexagram_database import HexagramDatabase
from src.exceptions import DivinationError, InvalidInputError


class DivinationFrame:
    """
    Divination interface frame.
    
    This class handles the complete divination workflow:
    1. Question input stage
    2. Divination execution
    3. Result display
    4. Save to history
    """
    
    def __init__(self, parent: tk.Frame, 
                 divination_service: DivinationService,
                 history_manager: HistoryManager,
                 database: HexagramDatabase,
                 on_return: Callable[[], None]):
        """
        Initialize the divination frame.
        
        Args:
            parent: Parent frame widget
            divination_service: DivinationService instance
            history_manager: HistoryManager instance
            database: HexagramDatabase instance
            on_return: Callback function to return to main menu
        """
        self.parent = parent
        self.divination_service = divination_service
        self.history_manager = history_manager
        self.database = database
        self.on_return = on_return
        
        # Current divination result
        self.current_result: Optional[DivinationResult] = None
        
        # Create the frame with grid layout
        self.frame = tk.Frame(
            parent,
            bg=Styles.colors.BACKGROUND_COLOR
        )
        self.frame.pack(fill=tk.BOTH, expand=True)
        
        # Configure grid weights for responsive layout
        self.frame.grid_rowconfigure(0, weight=0)  # Top bar
        self.frame.grid_rowconfigure(1, weight=0)  # Separator
        self.frame.grid_rowconfigure(2, weight=1)  # Content
        self.frame.grid_columnconfigure(0, weight=1)
        
        # Show input stage
        self.show_input_stage()
    
    def show_input_stage(self) -> None:
        """
        Display the question input stage.
        
        Shows:
        - Back button
        - Question input label
        - Text entry field
        - Start divination button
        """
        clear_frame(self.frame)
        
        # Top bar with back button
        top_bar = tk.Frame(
            self.frame,
            bg=Styles.colors.BACKGROUND_COLOR
        )
        top_bar.pack(fill=tk.X, padx=Styles.sizes.PADDING, pady=Styles.sizes.PADDING)
        
        # Back button
        back_btn = tk.Button(
            top_bar,
            text="← 返回",
            font=Styles.fonts.button_font(),
            bg=Styles.colors.SECONDARY_COLOR,
            fg=Styles.colors.WHITE_TEXT,
            command=self._on_back,
            cursor="hand2",
            relief=tk.RAISED,
            bd=2
        )
        back_btn.pack(side=tk.LEFT)
        
        # Separator line
        separator = tk.Frame(
            self.frame,
            bg=Styles.colors.LIGHT_TEXT,
            height=2
        )
        separator.pack(fill=tk.X, padx=Styles.sizes.LARGE_PADDING)
        
        # Content frame for centering
        content_frame = tk.Frame(
            self.frame,
            bg=Styles.colors.BACKGROUND_COLOR
        )
        content_frame.pack(expand=True, fill=tk.BOTH, padx=Styles.sizes.LARGE_PADDING)
        
        # Configure grid for centering
        content_frame.grid_rowconfigure(0, weight=1)
        content_frame.grid_rowconfigure(1, weight=0)
        content_frame.grid_rowconfigure(2, weight=0)
        content_frame.grid_rowconfigure(3, weight=0)
        content_frame.grid_rowconfigure(4, weight=1)
        content_frame.grid_columnconfigure(0, weight=1)
        
        # Question label
        question_label = tk.Label(
            content_frame,
            text="請輸入您的問題：",
            font=Styles.fonts.heading_font(),
            bg=Styles.colors.BACKGROUND_COLOR,
            fg=Styles.colors.TEXT_COLOR
        )
        question_label.grid(row=1, column=0, pady=(0, Styles.sizes.PADDING))
        
        # Question input field (Text widget for multi-line support)
        input_frame = tk.Frame(
            content_frame,
            bg=Styles.colors.BACKGROUND_COLOR
        )
        input_frame.grid(row=2, column=0, pady=Styles.sizes.PADDING)
        
        self.question_text = tk.Text(
            input_frame,
            font=Styles.fonts.body_font(),
            width=50,
            height=4,
            wrap=tk.WORD,
            relief=tk.SOLID,
            bd=1,
            padx=Styles.sizes.SMALL_PADDING,
            pady=Styles.sizes.SMALL_PADDING
        )
        self.question_text.pack()
        
        # Focus on the text field
        self.question_text.focus_set()
        
        # Hint text
        hint_label = tk.Label(
            content_frame,
            text="（請輸入您想要占卜的問題，例如：今年事業運勢如何？）",
            font=Styles.fonts.small_font(),
            bg=Styles.colors.BACKGROUND_COLOR,
            fg=Styles.colors.LIGHT_TEXT
        )
        hint_label.grid(row=3, column=0, pady=(0, Styles.sizes.LARGE_PADDING))
        
        # Start divination button
        start_btn = tk.Button(
            content_frame,
            text="開始占卜 🎲",
            font=Styles.fonts.button_font(),
            bg=Styles.colors.BUTTON_BG,
            fg=Styles.colors.WHITE_TEXT,
            activebackground=Styles.colors.BUTTON_HOVER,
            width=Styles.sizes.BUTTON_WIDTH,
            height=Styles.sizes.BUTTON_HEIGHT,
            cursor="hand2",
            relief=tk.RAISED,
            bd=2,
            command=self._on_start_divination
        )
        start_btn.grid(row=4, column=0, pady=Styles.sizes.LARGE_PADDING)
        
        # Add hover effect
        self._add_button_hover_effect(start_btn)
        
        # Bind Enter key to start divination (Ctrl+Enter for multi-line text)
        self.question_text.bind('<Control-Return>', lambda e: self._on_start_divination())
    
    @handle_exception
    def _on_start_divination(self) -> None:
        """
        Handle start divination button click.
        
        Validates input and performs divination if valid.
        """
        # Get question text
        question = self.question_text.get("1.0", tk.END).strip()
        
        # Validate input
        is_valid, error_message = validate_not_empty(question, "問題")
        if not is_valid:
            show_warning("輸入錯誤", error_message, self.frame)
            return
        
        # Additional length validation
        if len(question) > 500:
            show_warning(
                "輸入錯誤",
                "問題過長，請限制在 500 字以內",
                self.frame
            )
            return
        
        # Perform divination with animation
        try:
            def do_divination():
                try:
                    self.perform_divination(question)
                except InvalidInputError as e:
                    show_error("輸入錯誤", str(e), self.frame)
                except DivinationError as e:
                    show_error("卜卦錯誤", f"卜卦過程中發生錯誤：{str(e)}", self.frame)
                except Exception as e:
                    show_error("未知錯誤", f"發生未預期的錯誤：{str(e)}", self.frame)
            
            # Show animation before divination
            DivinationAnimation.show_divination_progress(self.frame, do_divination)
            
        except Exception as e:
            show_error("未知錯誤", f"發生未預期的錯誤：{str(e)}", self.frame)
    
    def perform_divination(self, question: str) -> None:
        """
        Perform divination with the given question.
        
        Calls the DivinationService to perform the divination and then
        displays the result using display_result().
        
        Args:
            question: The user's question
        """
        # Perform the divination
        result = self.divination_service.perform_divination(question)
        self.current_result = result
        
        # Display the result
        self.display_result(result)
    
    def display_result(self, result: DivinationResult) -> None:
        """
        Display the divination result.
        
        Shows:
        - Question
        - Original hexagram and changed hexagram (if any)
        - Hexagram descriptions and yao texts
        - Highlighted changing yao texts
        - Save and back buttons
        
        Args:
            result: DivinationResult object
        """
        clear_frame(self.frame)
        
        # Top bar with back button and save button
        top_bar = tk.Frame(
            self.frame,
            bg=Styles.colors.BACKGROUND_COLOR
        )
        top_bar.pack(fill=tk.X, padx=Styles.sizes.PADDING, pady=Styles.sizes.PADDING)
        
        # Back button
        back_btn = tk.Button(
            top_bar,
            text="← 返回",
            font=Styles.fonts.button_font(),
            bg=Styles.colors.SECONDARY_COLOR,
            fg=Styles.colors.WHITE_TEXT,
            command=self.clear_and_return,
            cursor="hand2",
            relief=tk.RAISED,
            bd=2
        )
        back_btn.pack(side=tk.LEFT)
        
        # Save button
        save_btn = tk.Button(
            top_bar,
            text="儲存記錄 💾",
            font=Styles.fonts.button_font(),
            bg=Styles.colors.ACCENT_COLOR,
            fg=Styles.colors.WHITE_TEXT,
            command=self.save_to_history,
            cursor="hand2",
            relief=tk.RAISED,
            bd=2
        )
        save_btn.pack(side=tk.RIGHT, padx=Styles.sizes.SMALL_PADDING)
        
        # Copy button
        copy_btn = tk.Button(
            top_bar,
            text="複製結果 📋",
            font=Styles.fonts.button_font(),
            bg=Styles.colors.INFO_COLOR,
            fg=Styles.colors.WHITE_TEXT,
            command=self.copy_to_clipboard,
            cursor="hand2",
            relief=tk.RAISED,
            bd=2
        )
        copy_btn.pack(side=tk.RIGHT, padx=Styles.sizes.SMALL_PADDING)
        
        # Interpretation help button
        help_btn = tk.Button(
            top_bar,
            text="解卦提示 💡",
            font=Styles.fonts.button_font(),
            bg=Styles.colors.SUCCESS_COLOR,
            fg=Styles.colors.WHITE_TEXT,
            command=self.show_interpretation_help,
            cursor="hand2",
            relief=tk.RAISED,
            bd=2
        )
        help_btn.pack(side=tk.RIGHT)
        
        # Add hover effects
        self._add_button_hover_effect(back_btn)
        self._add_button_hover_effect(save_btn)
        self._add_button_hover_effect(copy_btn)
        self._add_button_hover_effect(help_btn)
        
        # Separator line
        separator = tk.Frame(
            self.frame,
            bg=Styles.colors.LIGHT_TEXT,
            height=2
        )
        separator.pack(fill=tk.X, padx=Styles.sizes.LARGE_PADDING)
        
        # Create scrollable content area
        from .utils import create_scrollable_frame, bind_mousewheel
        
        # Main container for scrollable content
        scroll_container = tk.Frame(
            self.frame,
            bg=Styles.colors.BACKGROUND_COLOR
        )
        scroll_container.pack(fill=tk.BOTH, expand=True, padx=Styles.sizes.PADDING)
        
        # Create scrollable frame
        scrollable_frame, canvas, scrollbar = create_scrollable_frame(scroll_container)
        scrollable_frame.config(bg=Styles.colors.BACKGROUND_COLOR)
        canvas.config(bg=Styles.colors.BACKGROUND_COLOR)
        
        # Pack canvas and scrollbar
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind mousewheel
        bind_mousewheel(canvas, canvas)
        
        # Question display
        question_label = tk.Label(
            scrollable_frame,
            text=f"問題：{result.question}",
            font=Styles.fonts.heading_font(),
            bg=Styles.colors.BACKGROUND_COLOR,
            fg=Styles.colors.TEXT_COLOR,
            wraplength=700,
            justify=tk.LEFT
        )
        question_label.pack(pady=(Styles.sizes.PADDING, Styles.sizes.LARGE_PADDING))
        
        # Hexagram display area with grid layout for better responsiveness
        hexagram_frame = tk.Frame(
            scrollable_frame,
            bg=Styles.colors.BACKGROUND_COLOR
        )
        hexagram_frame.pack(pady=Styles.sizes.PADDING, fill=tk.X)
        
        # Configure grid for centering hexagrams
        hexagram_frame.grid_columnconfigure(0, weight=1)
        hexagram_frame.grid_columnconfigure(1, weight=0)
        hexagram_frame.grid_columnconfigure(2, weight=0)
        hexagram_frame.grid_columnconfigure(3, weight=1)
        
        # Original hexagram
        original_container = tk.Frame(
            hexagram_frame,
            bg=Styles.colors.BACKGROUND_COLOR
        )
        original_container.grid(row=0, column=1, padx=Styles.sizes.LARGE_PADDING)
        
        original_title = tk.Label(
            original_container,
            text="本卦",
            font=Styles.fonts.heading_font(),
            bg=Styles.colors.BACKGROUND_COLOR,
            fg=Styles.colors.TEXT_COLOR
        )
        original_title.pack(pady=(0, Styles.sizes.SMALL_PADDING))
        
        original_display = HexagramDisplay(original_container, width=150, height=200)
        original_display.pack()
        original_display.draw_hexagram(result.original_hexagram, show_changing=True)
        
        # Changed hexagram (if exists)
        if result.changed_hexagram:
            changed_container = tk.Frame(
                hexagram_frame,
                bg=Styles.colors.BACKGROUND_COLOR
            )
            changed_container.grid(row=0, column=2, padx=Styles.sizes.LARGE_PADDING)
            
            changed_title = tk.Label(
                changed_container,
                text="之卦",
                font=Styles.fonts.heading_font(),
                bg=Styles.colors.BACKGROUND_COLOR,
                fg=Styles.colors.TEXT_COLOR
            )
            changed_title.pack(pady=(0, Styles.sizes.SMALL_PADDING))
            
            changed_display = HexagramDisplay(changed_container, width=150, height=200)
            changed_display.pack()
            changed_display.draw_hexagram(result.changed_hexagram, show_changing=False)
        
        # Text display area
        text_frame = tk.Frame(
            scrollable_frame,
            bg=Styles.colors.BACKGROUND_COLOR
        )
        text_frame.pack(fill=tk.BOTH, expand=True, pady=Styles.sizes.PADDING, padx=Styles.sizes.LARGE_PADDING)
        
        # Description label
        desc_label = tk.Label(
            text_frame,
            text="卦辭與爻辭：",
            font=Styles.fonts.heading_font(),
            bg=Styles.colors.BACKGROUND_COLOR,
            fg=Styles.colors.TEXT_COLOR,
            anchor=tk.W
        )
        desc_label.pack(fill=tk.X, pady=(0, Styles.sizes.SMALL_PADDING))
        
        # Scrolled text widget for descriptions
        text_widget = scrolledtext.ScrolledText(
            text_frame,
            font=Styles.fonts.body_font(),
            wrap=tk.WORD,
            width=70,
            height=15,
            relief=tk.SOLID,
            bd=1,
            padx=Styles.sizes.PADDING,
            pady=Styles.sizes.PADDING
        )
        text_widget.pack(fill=tk.BOTH, expand=True)
        
        # Configure text tags for highlighting
        text_widget.tag_config("heading", font=Styles.fonts.heading_font(), foreground=Styles.colors.PRIMARY_COLOR)
        text_widget.tag_config("changing", font=Styles.fonts.body_font(), foreground=Styles.colors.CHANGING_YAO_COLOR, background="#FFF3CD")
        text_widget.tag_config("normal", font=Styles.fonts.body_font())
        
        # Build the text content
        self._populate_text_widget(text_widget, result)
        
        # Make text widget read-only
        text_widget.config(state=tk.DISABLED)
    
    def _populate_text_widget(self, text_widget: scrolledtext.ScrolledText, 
                              result: DivinationResult) -> None:
        """
        Populate the text widget with hexagram descriptions and yao texts.
        
        Args:
            text_widget: ScrolledText widget to populate
            result: DivinationResult object
        """
        text_widget.config(state=tk.NORMAL)
        
        # Original hexagram description
        text_widget.insert(tk.END, "【本卦】\n", "heading")
        text_widget.insert(tk.END, f"{result.original_hexagram.name}\n", "heading")
        text_widget.insert(tk.END, f"第 {result.original_hexagram.number} 卦 · ", "normal")
        text_widget.insert(tk.END, f"上卦 {result.original_hexagram.upper_trigram}，下卦 {result.original_hexagram.lower_trigram}\n\n", "normal")
        
        text_widget.insert(tk.END, "卦辭：\n", "normal")
        text_widget.insert(tk.END, f"{result.original_hexagram.description}\n\n", "normal")
        
        # Changing yaos information
        if result.has_changes():
            text_widget.insert(tk.END, "【變爻】\n", "heading")
            
            # Get yao names
            yao_names = ["初", "二", "三", "四", "五", "上"]
            
            for yao in result.changing_yaos:
                position = yao.position - 1  # Convert to 0-based index
                yao_name = yao_names[position]
                
                # Determine if it's yang or yin
                if yao.is_yang():
                    full_name = f"{yao_name}九"
                else:
                    full_name = f"{yao_name}六"
                
                # Get yao text
                yao_text = result.original_hexagram.yao_texts[position]
                
                # Insert with highlighting
                text_widget.insert(tk.END, f"{full_name}：", "changing")
                text_widget.insert(tk.END, f"{yao_text}\n", "changing")
            
            text_widget.insert(tk.END, "\n")
            
            # Changed hexagram information
            if result.changed_hexagram:
                text_widget.insert(tk.END, "【之卦】\n", "heading")
                text_widget.insert(tk.END, f"{result.changed_hexagram.name}\n", "heading")
                text_widget.insert(tk.END, f"第 {result.changed_hexagram.number} 卦 · ", "normal")
                text_widget.insert(tk.END, f"上卦 {result.changed_hexagram.upper_trigram}，下卦 {result.changed_hexagram.lower_trigram}\n\n", "normal")
                
                text_widget.insert(tk.END, "卦辭：\n", "normal")
                text_widget.insert(tk.END, f"{result.changed_hexagram.description}\n", "normal")
        else:
            text_widget.insert(tk.END, "【無變爻】\n", "heading")
            text_widget.insert(tk.END, "本次卜卦沒有變爻，專注於本卦的卦辭即可。\n", "normal")
        
        text_widget.config(state=tk.DISABLED)
    
    @handle_exception
    def save_to_history(self) -> None:
        """
        Save the current divination result to history.
        
        Calls HistoryManager.save_record() to persist the result.
        Displays success or error messages based on the outcome.
        """
        # Check if there's a result to save
        if not self.current_result:
            show_warning("無法儲存", "沒有可儲存的卜卦結果", self.frame)
            return
        
        try:
            # Save the record using HistoryManager
            self.history_manager.save_record(self.current_result)
            
            # Show success message
            show_success(
                "儲存成功",
                "卜卦記錄已成功儲存到歷史記錄中",
                self.frame
            )
            
        except PermissionError as e:
            # Handle permission errors (file access issues)
            show_error(
                "儲存失敗",
                f"無法寫入歷史記錄檔案：權限不足\n{str(e)}",
                self.frame
            )
        except IOError as e:
            # Handle I/O errors (disk full, file locked, etc.)
            show_error(
                "儲存失敗",
                f"寫入歷史記錄時發生錯誤：{str(e)}",
                self.frame
            )
        except Exception as e:
            # Handle any other unexpected errors
            show_error(
                "儲存失敗",
                f"儲存記錄時發生未預期的錯誤：{str(e)}",
                self.frame
            )
    
    @handle_exception
    def copy_to_clipboard(self) -> None:
        """
        Copy the current divination result to clipboard.
        """
        if not self.current_result:
            show_warning("無法複製", "沒有可複製的卜卦結果", self.frame)
            return
        
        try:
            # Build text representation
            result = self.current_result
            text_parts = []
            
            # Header
            text_parts.append("=" * 50)
            text_parts.append("易經卜卦結果")
            text_parts.append("=" * 50)
            text_parts.append("")
            
            # Question
            text_parts.append(f"問題：{result.question}")
            text_parts.append("")
            
            # Original hexagram
            text_parts.append("【本卦】")
            text_parts.append(f"{result.original_hexagram.name}")
            text_parts.append(f"第 {result.original_hexagram.number} 卦")
            text_parts.append(f"上卦：{result.original_hexagram.upper_trigram}")
            text_parts.append(f"下卦：{result.original_hexagram.lower_trigram}")
            text_parts.append("")
            text_parts.append("卦辭：")
            text_parts.append(result.original_hexagram.description)
            text_parts.append("")
            
            # Changing yaos
            if result.has_changes():
                text_parts.append("【變爻】")
                yao_names = ["初", "二", "三", "四", "五", "上"]
                
                for yao in result.changing_yaos:
                    position = yao.position - 1
                    yao_name = yao_names[position]
                    full_name = f"{yao_name}九" if yao.is_yang() else f"{yao_name}六"
                    yao_text = result.original_hexagram.yao_texts[position]
                    text_parts.append(f"{full_name}：{yao_text}")
                
                text_parts.append("")
                
                # Changed hexagram
                if result.changed_hexagram:
                    text_parts.append("【之卦】")
                    text_parts.append(f"{result.changed_hexagram.name}")
                    text_parts.append(f"第 {result.changed_hexagram.number} 卦")
                    text_parts.append(f"上卦：{result.changed_hexagram.upper_trigram}")
                    text_parts.append(f"下卦：{result.changed_hexagram.lower_trigram}")
                    text_parts.append("")
                    text_parts.append("卦辭：")
                    text_parts.append(result.changed_hexagram.description)
            else:
                text_parts.append("【無變爻】")
                text_parts.append("本次卜卦沒有變爻，專注於本卦的卦辭即可。")
            
            text_parts.append("")
            text_parts.append("=" * 50)
            
            # Join all parts
            full_text = "\n".join(text_parts)
            
            # Copy to clipboard
            self.frame.clipboard_clear()
            self.frame.clipboard_append(full_text)
            self.frame.update()  # Required for clipboard to work
            
            # Show success message
            show_success(
                "複製成功",
                "卜卦結果已複製到剪貼簿",
                self.frame
            )
            
        except Exception as e:
            show_error(
                "複製失敗",
                f"複製到剪貼簿時發生錯誤：{str(e)}",
                self.frame
            )
    
    @handle_exception
    def _on_back(self) -> None:
        """Handle back button click."""
        self.clear_and_return()
    
    def clear_and_return(self) -> None:
        """
        Clear the frame and return to main menu.
        """
        # Clear current result
        self.current_result = None
        
        # Clear the question text if it exists
        if hasattr(self, 'question_text') and self.question_text.winfo_exists():
            self.question_text.delete("1.0", tk.END)
        
        # Call the return callback
        self.on_return()
    
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
    def show_interpretation_help(self) -> None:
        """
        Show interpretation help dialog with guidance on how to interpret the hexagram.
        """
        if not self.current_result:
            show_warning("無法顯示", "沒有可解讀的卜卦結果", self.frame)
            return
        
        # Create dialog window
        dialog = tk.Toplevel(self.frame)
        dialog.title("解卦提示")
        dialog.geometry("700x600")
        dialog.configure(bg=Styles.colors.BACKGROUND_COLOR)
        
        # Center the dialog
        dialog.transient(self.frame)
        dialog.grab_set()
        
        # Title
        title_label = tk.Label(
            dialog,
            text="💡 解卦提示與指引",
            font=Styles.fonts.title_font(),
            bg=Styles.colors.BACKGROUND_COLOR,
            fg=Styles.colors.PRIMARY_COLOR
        )
        title_label.pack(pady=Styles.sizes.PADDING)
        
        # Create scrolled text for content
        from tkinter import scrolledtext
        content_text = scrolledtext.ScrolledText(
            dialog,
            font=Styles.fonts.body_font(),
            wrap=tk.WORD,
            padx=Styles.sizes.PADDING,
            pady=Styles.sizes.PADDING
        )
        content_text.pack(fill=tk.BOTH, expand=True, padx=Styles.sizes.PADDING, pady=Styles.sizes.PADDING)
        
        # Configure tags
        content_text.tag_config("heading", font=Styles.fonts.heading_font(), foreground=Styles.colors.PRIMARY_COLOR)
        content_text.tag_config("subheading", font=Styles.fonts.body_font_bold(), foreground=Styles.colors.ACCENT_COLOR)
        content_text.tag_config("important", foreground=Styles.colors.CHANGING_YAO_COLOR, font=Styles.fonts.body_font_bold())
        content_text.tag_config("normal", font=Styles.fonts.body_font())
        
        # Build interpretation help content
        self._populate_interpretation_help(content_text, self.current_result)
        
        # Make read-only
        content_text.config(state=tk.DISABLED)
        
        # Close button
        close_btn = tk.Button(
            dialog,
            text="關閉",
            font=Styles.fonts.button_font(),
            bg=Styles.colors.SECONDARY_COLOR,
            fg=Styles.colors.WHITE_TEXT,
            command=dialog.destroy,
            cursor="hand2",
            width=15
        )
        close_btn.pack(pady=Styles.sizes.PADDING)
        
        # Center dialog on screen
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
    
    def _populate_interpretation_help(self, text_widget: scrolledtext.ScrolledText, 
                                     result: DivinationResult) -> None:
        """
        Populate the interpretation help text widget with guidance.
        
        Args:
            text_widget: ScrolledText widget to populate
            result: DivinationResult object
        """
        text_widget.config(state=tk.NORMAL)
        
        # Header
        text_widget.insert(tk.END, "📖 如何解讀這個卦象\n\n", "heading")
        
        # Situation analysis
        if result.has_changes():
            text_widget.insert(tk.END, "【您的情況】\n", "subheading")
            text_widget.insert(tk.END, f"本次卜卦有 ", "normal")
            text_widget.insert(tk.END, f"{len(result.changing_yaos)} 個變爻", "important")
            text_widget.insert(tk.END, "，表示事物處於變化狀態。\n\n", "normal")
            
            # Interpretation steps for changing yaos
            text_widget.insert(tk.END, "【解讀步驟】\n", "subheading")
            text_widget.insert(tk.END, "1️⃣ ", "normal")
            text_widget.insert(tk.END, "先看本卦卦辭", "important")
            text_widget.insert(tk.END, f" - 了解當前狀態\n", "normal")
            text_widget.insert(tk.END, f"   本卦：{result.original_hexagram.name}\n", "normal")
            text_widget.insert(tk.END, f"   這代表您目前的處境和狀態。\n\n", "normal")
            
            text_widget.insert(tk.END, "2️⃣ ", "normal")
            text_widget.insert(tk.END, "重點看變爻爻辭", "important")
            text_widget.insert(tk.END, " - 這是最關鍵的訊息\n", "normal")
            
            yao_names = ["初", "二", "三", "四", "五", "上"]
            for yao in result.changing_yaos:
                position = yao.position - 1
                yao_name = yao_names[position]
                full_name = f"{yao_name}九" if yao.is_yang() else f"{yao_name}六"
                text_widget.insert(tk.END, f"   • {full_name}：", "important")
                text_widget.insert(tk.END, "這個爻正在變化，特別注意其爻辭的含義。\n", "normal")
            text_widget.insert(tk.END, "\n")
            
            text_widget.insert(tk.END, "3️⃣ ", "normal")
            text_widget.insert(tk.END, "再看之卦卦辭", "important")
            text_widget.insert(tk.END, " - 了解未來趨勢\n", "normal")
            if result.changed_hexagram:
                text_widget.insert(tk.END, f"   之卦：{result.changed_hexagram.name}\n", "normal")
                text_widget.insert(tk.END, f"   這代表事物的發展方向和未來趨勢。\n\n", "normal")
            
            text_widget.insert(tk.END, "4️⃣ ", "normal")
            text_widget.insert(tk.END, "綜合三者", "important")
            text_widget.insert(tk.END, " - 得出完整解讀\n", "normal")
            text_widget.insert(tk.END, "   結合本卦、變爻、之卦，思考它們與您問題的關聯。\n\n", "normal")
            
        else:
            text_widget.insert(tk.END, "【您的情況】\n", "subheading")
            text_widget.insert(tk.END, "本次卜卦", "normal")
            text_widget.insert(tk.END, "沒有變爻", "important")
            text_widget.insert(tk.END, "，表示事物處於穩定狀態。\n\n", "normal")
            
            text_widget.insert(tk.END, "【解讀步驟】\n", "subheading")
            text_widget.insert(tk.END, "1️⃣ ", "normal")
            text_widget.insert(tk.END, "專注於本卦卦辭", "important")
            text_widget.insert(tk.END, "\n", "normal")
            text_widget.insert(tk.END, f"   本卦：{result.original_hexagram.name}\n", "normal")
            text_widget.insert(tk.END, "   仔細閱讀卦辭，理解其整體含義。\n\n", "normal")
            
            text_widget.insert(tk.END, "2️⃣ ", "normal")
            text_widget.insert(tk.END, "思考卦象的象徵意義", "important")
            text_widget.insert(tk.END, "\n", "normal")
            text_widget.insert(tk.END, f"   上卦：{result.original_hexagram.upper_trigram}\n", "normal")
            text_widget.insert(tk.END, f"   下卦：{result.original_hexagram.lower_trigram}\n", "normal")
            text_widget.insert(tk.END, "   思考這兩個卦象的組合代表什麼。\n\n", "normal")
        
        # Trigram meanings
        text_widget.insert(tk.END, "【八卦象徵意義】\n", "subheading")
        trigram_meanings = {
            "乾": "☰ 天 - 剛健、創造、領導、父親",
            "坤": "☷ 地 - 柔順、承載、包容、母親",
            "震": "☳ 雷 - 震動、行動、長子",
            "巽": "☴ 風 - 順從、進入、長女",
            "坎": "☵ 水 - 險難、智慧、中男",
            "離": "☲ 火 - 光明、美麗、中女",
            "艮": "☶ 山 - 止、穩定、少男",
            "兌": "☱ 澤 - 喜悅、口舌、少女"
        }
        
        upper = result.original_hexagram.upper_trigram
        lower = result.original_hexagram.lower_trigram
        
        if upper in trigram_meanings:
            text_widget.insert(tk.END, f"上卦 {upper}：{trigram_meanings[upper]}\n", "normal")
        if lower in trigram_meanings:
            text_widget.insert(tk.END, f"下卦 {lower}：{trigram_meanings[lower]}\n", "normal")
        text_widget.insert(tk.END, "\n")
        
        # Question type guidance
        text_widget.insert(tk.END, "【根據問題類型解讀】\n", "subheading")
        question = result.question.lower()
        
        if any(word in question for word in ["事業", "工作", "職業", "升遷"]):
            text_widget.insert(tk.END, "💼 事業運勢問題\n", "important")
            text_widget.insert(tk.END, "• 注意卦象中的「進」與「退」\n", "normal")
            text_widget.insert(tk.END, "• 剛健的卦象（如乾、震）利於開創\n", "normal")
            text_widget.insert(tk.END, "• 柔順的卦象（如坤、巽）利於配合\n\n", "normal")
            
        elif any(word in question for word in ["感情", "愛情", "婚姻", "戀愛"]):
            text_widget.insert(tk.END, "💕 感情問題\n", "important")
            text_widget.insert(tk.END, "• 注意卦象中的「合」與「離」\n", "normal")
            text_widget.insert(tk.END, "• 陰陽調和的卦象較為吉利\n", "normal")
            text_widget.insert(tk.END, "• 變爻多表示關係有變化\n\n", "normal")
            
        elif any(word in question for word in ["財運", "金錢", "投資", "理財"]):
            text_widget.insert(tk.END, "💰 財運問題\n", "important")
            text_widget.insert(tk.END, "• 注意卦象中的「得」與「失」\n", "normal")
            text_widget.insert(tk.END, "• 穩健的卦象（如坤、艮）利於守成\n", "normal")
            text_widget.insert(tk.END, "• 變動的卦象需謹慎投資\n\n", "normal")
            
        elif any(word in question for word in ["健康", "身體", "疾病"]):
            text_widget.insert(tk.END, "🏥 健康問題\n", "important")
            text_widget.insert(tk.END, "• 注意卦象中的「陰陽平衡」\n", "normal")
            text_widget.insert(tk.END, "• 坎卦（水）與健康關係密切\n", "normal")
            text_widget.insert(tk.END, "• 建議配合專業醫療意見\n\n", "normal")
            
        else:
            text_widget.insert(tk.END, "📝 一般問題\n", "important")
            text_widget.insert(tk.END, "• 從卦象的整體氛圍理解\n", "normal")
            text_widget.insert(tk.END, "• 注意卦辭中的關鍵字\n", "normal")
            text_widget.insert(tk.END, "• 結合您的實際情況思考\n\n", "normal")
        
        # General tips
        text_widget.insert(tk.END, "【解卦建議】\n", "subheading")
        text_widget.insert(tk.END, "✓ 保持開放心態，易經是啟發而非預言\n", "normal")
        text_widget.insert(tk.END, "✓ 結合實際情況，不要生搬硬套\n", "normal")
        text_widget.insert(tk.END, "✓ 注意卦辭中的象徵意義\n", "normal")
        text_widget.insert(tk.END, "✓ 可以使用「複製結果」功能保存下來慢慢研讀\n", "normal")
        text_widget.insert(tk.END, "✓ 定期回顧歷史記錄，對照實際發展\n\n", "normal")
        
        # Footer
        text_widget.insert(tk.END, "═" * 50 + "\n", "normal")
        text_widget.insert(tk.END, "願易經的智慧為您指引方向 ☯\n", "heading")
        
        text_widget.config(state=tk.DISABLED)
