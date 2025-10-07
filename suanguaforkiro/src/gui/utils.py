"""
Utility functions for the GUI.

This module provides common GUI utility functions such as dialog boxes,
validation helpers, and other shared functionality.
"""

import tkinter as tk
from tkinter import messagebox
from typing import Optional, Callable
import traceback


def show_error(title: str, message: str, parent: Optional[tk.Tk] = None) -> None:
    """
    Display an error dialog box.
    
    Args:
        title: Dialog title
        message: Error message to display
        parent: Parent window (optional)
    """
    messagebox.showerror(title, message, parent=parent)


def show_warning(title: str, message: str, parent: Optional[tk.Tk] = None) -> None:
    """
    Display a warning dialog box.
    
    Args:
        title: Dialog title
        message: Warning message to display
        parent: Parent window (optional)
    """
    messagebox.showwarning(title, message, parent=parent)


def show_info(title: str, message: str, parent: Optional[tk.Tk] = None) -> None:
    """
    Display an information dialog box.
    
    Args:
        title: Dialog title
        message: Information message to display
        parent: Parent window (optional)
    """
    messagebox.showinfo(title, message, parent=parent)


def show_success(title: str, message: str, parent: Optional[tk.Tk] = None) -> None:
    """
    Display a success message dialog.
    
    Args:
        title: Dialog title
        message: Success message to display
        parent: Parent window (optional)
    """
    messagebox.showinfo(title, message, parent=parent)


def ask_yes_no(title: str, message: str, parent: Optional[tk.Tk] = None) -> bool:
    """
    Display a yes/no confirmation dialog.
    
    Args:
        title: Dialog title
        message: Question to ask
        parent: Parent window (optional)
    
    Returns:
        bool: True if user clicked Yes, False otherwise
    """
    return messagebox.askyesno(title, message, parent=parent)


def ask_ok_cancel(title: str, message: str, parent: Optional[tk.Tk] = None) -> bool:
    """
    Display an OK/Cancel confirmation dialog.
    
    Args:
        title: Dialog title
        message: Question to ask
        parent: Parent window (optional)
    
    Returns:
        bool: True if user clicked OK, False otherwise
    """
    return messagebox.askokcancel(title, message, parent=parent)


def validate_not_empty(text: str, field_name: str = "輸入") -> tuple[bool, str]:
    """
    Validate that a text field is not empty.
    
    Args:
        text: Text to validate
        field_name: Name of the field for error message
    
    Returns:
        tuple: (is_valid, error_message)
    """
    text = text.strip()
    if not text:
        return False, f"{field_name}不能為空"
    return True, ""


def validate_length(text: str, min_length: int = 0, max_length: int = 1000,
                   field_name: str = "輸入") -> tuple[bool, str]:
    """
    Validate text length.
    
    Args:
        text: Text to validate
        min_length: Minimum allowed length
        max_length: Maximum allowed length
        field_name: Name of the field for error message
    
    Returns:
        tuple: (is_valid, error_message)
    """
    text_length = len(text.strip())
    
    if text_length < min_length:
        return False, f"{field_name}長度不能少於 {min_length} 個字元"
    
    if text_length > max_length:
        return False, f"{field_name}長度不能超過 {max_length} 個字元"
    
    return True, ""


def center_window(window: tk.Tk, width: int, height: int) -> None:
    """
    Center a window on the screen.
    
    Args:
        window: Window to center
        width: Window width
        height: Window height
    """
    # Get screen dimensions
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    
    # Calculate position
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    
    # Set window geometry
    window.geometry(f"{width}x{height}+{x}+{y}")


def handle_exception(func: Callable) -> Callable:
    """
    Decorator to handle exceptions in GUI callbacks.
    
    Args:
        func: Function to wrap
    
    Returns:
        Wrapped function with exception handling
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            error_msg = f"發生錯誤：{str(e)}\n\n詳細資訊：\n{traceback.format_exc()}"
            show_error("錯誤", error_msg)
            print(f"Exception in {func.__name__}: {e}")
            traceback.print_exc()
    
    return wrapper


def create_scrollable_frame(parent: tk.Widget) -> tuple[tk.Frame, tk.Canvas, tk.Scrollbar]:
    """
    Create a scrollable frame widget.
    
    Args:
        parent: Parent widget
    
    Returns:
        tuple: (scrollable_frame, canvas, scrollbar)
    """
    # Create canvas and scrollbar
    canvas = tk.Canvas(parent, highlightthickness=0)
    scrollbar = tk.Scrollbar(parent, orient="vertical", command=canvas.yview)
    
    # Create frame inside canvas
    scrollable_frame = tk.Frame(canvas)
    
    # Configure canvas
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    
    return scrollable_frame, canvas, scrollbar


def bind_mousewheel(widget: tk.Widget, canvas: tk.Canvas) -> None:
    """
    Bind mousewheel scrolling to a canvas.
    
    Args:
        widget: Widget to bind to
        canvas: Canvas to scroll
    """
    def on_mousewheel(event):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    
    def on_enter(event):
        widget.bind_all("<MouseWheel>", on_mousewheel)
    
    def on_leave(event):
        widget.unbind_all("<MouseWheel>")
    
    widget.bind("<Enter>", on_enter)
    widget.bind("<Leave>", on_leave)


def clear_frame(frame: tk.Frame) -> None:
    """
    Clear all widgets from a frame.
    
    Args:
        frame: Frame to clear
    """
    for widget in frame.winfo_children():
        widget.destroy()


def format_timestamp(timestamp: str) -> str:
    """
    Format a timestamp string for display.
    
    Args:
        timestamp: ISO format timestamp string
    
    Returns:
        str: Formatted timestamp
    """
    try:
        from datetime import datetime
        dt = datetime.fromisoformat(timestamp)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return timestamp


def truncate_text(text: str, max_length: int = 50, suffix: str = "...") -> str:
    """
    Truncate text to a maximum length.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated
    
    Returns:
        str: Truncated text
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


class LoadingIndicator:
    """
    A simple loading indicator widget.
    
    Displays a message with an animated indicator to show
    that a long-running operation is in progress.
    """
    
    def __init__(self, parent: tk.Widget, message: str = "載入中..."):
        """
        Initialize the loading indicator.
        
        Args:
            parent: Parent widget
            message: Message to display
        """
        self.parent = parent
        self.message = message
        self.window = None
        self.label = None
        self.animation_id = None
        self.dots = 0
    
    def show(self) -> None:
        """Show the loading indicator."""
        # Create a toplevel window
        self.window = tk.Toplevel(self.parent)
        self.window.title("請稍候")
        self.window.geometry("300x100")
        
        # Center the window
        self.window.transient(self.parent)
        self.window.grab_set()
        
        # Remove window decorations
        self.window.overrideredirect(True)
        
        # Create label
        self.label = tk.Label(
            self.window,
            text=self.message,
            font=("Microsoft YaHei UI", 12),
            pady=30
        )
        self.label.pack(expand=True)
        
        # Start animation
        self._animate()
        
        # Update the window
        self.window.update()
    
    def _animate(self) -> None:
        """Animate the loading indicator."""
        if self.window and self.label:
            self.dots = (self.dots + 1) % 4
            dots_str = "." * self.dots
            self.label.config(text=f"{self.message}{dots_str}")
            self.animation_id = self.window.after(500, self._animate)
    
    def hide(self) -> None:
        """Hide the loading indicator."""
        if self.animation_id:
            self.window.after_cancel(self.animation_id)
            self.animation_id = None
        
        if self.window:
            self.window.grab_release()
            self.window.destroy()
            self.window = None
            self.label = None


def with_loading_indicator(message: str = "處理中..."):
    """
    Decorator to show a loading indicator during function execution.
    
    Args:
        message: Message to display in the loading indicator
    
    Returns:
        Decorated function
    """
    def decorator(func: Callable) -> Callable:
        def wrapper(self, *args, **kwargs):
            # Try to get the parent widget
            parent = None
            if hasattr(self, 'frame'):
                parent = self.frame
            elif hasattr(self, 'parent'):
                parent = self.parent
            
            if parent:
                indicator = LoadingIndicator(parent, message)
                try:
                    indicator.show()
                    result = func(self, *args, **kwargs)
                    return result
                finally:
                    indicator.hide()
            else:
                # No parent found, just execute the function
                return func(self, *args, **kwargs)
        
        return wrapper
    return decorator
