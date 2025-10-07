"""
Animation effects for the GUI.

This module provides animation functions for enhancing the user experience.
"""

import tkinter as tk
from typing import Callable, Optional
import time


class AnimationManager:
    """Manager for GUI animations."""
    
    @staticmethod
    def fade_in(widget: tk.Widget, duration: int = 500, callback: Optional[Callable] = None) -> None:
        """
        Fade in a widget.
        
        Args:
            widget: Widget to fade in
            duration: Duration in milliseconds
            callback: Optional callback function to call after animation
        """
        try:
            steps = 20
            step_duration = duration // steps
            alpha_step = 1.0 / steps
            
            def animate(step=0):
                if step < steps:
                    alpha = alpha_step * step
                    try:
                        widget.attributes('-alpha', alpha)
                    except:
                        pass
                    widget.after(step_duration, lambda: animate(step + 1))
                else:
                    try:
                        widget.attributes('-alpha', 1.0)
                    except:
                        pass
                    if callback:
                        callback()
            
            animate()
        except:
            # If animation fails, just show the widget
            if callback:
                callback()
    
    @staticmethod
    def slide_in(widget: tk.Widget, direction: str = 'left', duration: int = 300) -> None:
        """
        Slide in a widget from a direction.
        
        Args:
            widget: Widget to slide in
            direction: Direction to slide from ('left', 'right', 'top', 'bottom')
            duration: Duration in milliseconds
        """
        # Simple implementation - just pack the widget
        # Full implementation would require more complex geometry management
        widget.pack()
    
    @staticmethod
    def coin_flip_animation(canvas: tk.Canvas, x: int, y: int, 
                           callback: Optional[Callable] = None) -> None:
        """
        Animate a coin flip.
        
        Args:
            canvas: Canvas to draw on
            x: X coordinate
            y: Y coordinate
            callback: Optional callback function to call after animation
        """
        coin_size = 30
        flip_count = 10
        flip_duration = 50  # milliseconds per flip
        
        def draw_coin(is_heads: bool):
            """Draw a coin face."""
            canvas.delete("coin")
            
            # Draw coin circle
            canvas.create_oval(
                x - coin_size, y - coin_size,
                x + coin_size, y + coin_size,
                fill="#FFD700",
                outline="#DAA520",
                width=2,
                tags="coin"
            )
            
            # Draw coin face (simplified)
            if is_heads:
                # Heads - draw a circle
                canvas.create_oval(
                    x - coin_size//2, y - coin_size//2,
                    x + coin_size//2, y + coin_size//2,
                    fill="#DAA520",
                    outline="#B8860B",
                    tags="coin"
                )
            else:
                # Tails - draw a square
                canvas.create_rectangle(
                    x - coin_size//2, y - coin_size//2,
                    x + coin_size//2, y + coin_size//2,
                    fill="#DAA520",
                    outline="#B8860B",
                    tags="coin"
                )
        
        def animate(flip=0):
            if flip < flip_count:
                is_heads = flip % 2 == 0
                draw_coin(is_heads)
                canvas.after(flip_duration, lambda: animate(flip + 1))
            else:
                canvas.delete("coin")
                if callback:
                    callback()
        
        animate()
    
    @staticmethod
    def yao_generation_animation(canvas: tk.Canvas, yao_positions: list,
                                 on_complete: Optional[Callable] = None) -> None:
        """
        Animate the generation of yaos one by one.
        
        Args:
            canvas: Canvas to draw on
            yao_positions: List of (x, y, is_yang, is_changing) tuples
            on_complete: Callback function to call when animation completes
        """
        delay = 200  # milliseconds between each yao
        
        def draw_next_yao(index=0):
            if index < len(yao_positions):
                # Draw the yao at this index
                # This would integrate with HexagramDisplay
                canvas.after(delay, lambda: draw_next_yao(index + 1))
            else:
                if on_complete:
                    on_complete()
        
        draw_next_yao()
    
    @staticmethod
    def pulse_effect(widget: tk.Widget, count: int = 3, duration: int = 200) -> None:
        """
        Create a pulse effect on a widget.
        
        Args:
            widget: Widget to pulse
            count: Number of pulses
            duration: Duration of each pulse in milliseconds
        """
        original_bg = widget.cget('bg')
        
        def pulse(iteration=0):
            if iteration < count * 2:
                if iteration % 2 == 0:
                    # Brighten
                    try:
                        widget.config(relief=tk.RAISED, bd=3)
                    except:
                        pass
                else:
                    # Restore
                    try:
                        widget.config(relief=tk.RAISED, bd=2)
                    except:
                        pass
                widget.after(duration, lambda: pulse(iteration + 1))
        
        pulse()
    
    @staticmethod
    def loading_dots(label: tk.Label, base_text: str, duration: int = 500, 
                    max_dots: int = 3, callback: Optional[Callable] = None) -> dict:
        """
        Animate loading dots on a label.
        
        Args:
            label: Label widget to animate
            base_text: Base text to display
            duration: Duration between dot updates in milliseconds
            max_dots: Maximum number of dots
            callback: Optional callback when animation should stop
            
        Returns:
            dict with 'stop' function to stop the animation
        """
        animation_state = {'running': True, 'dots': 0}
        
        def animate():
            if animation_state['running']:
                dots = '.' * (animation_state['dots'] % (max_dots + 1))
                try:
                    label.config(text=f"{base_text}{dots}")
                except:
                    animation_state['running'] = False
                    return
                
                animation_state['dots'] += 1
                label.after(duration, animate)
        
        def stop():
            animation_state['running'] = False
            try:
                label.config(text=base_text)
            except:
                pass
        
        animate()
        return {'stop': stop}
    
    @staticmethod
    def smooth_scroll_to(canvas: tk.Canvas, target_y: float, duration: int = 300) -> None:
        """
        Smoothly scroll a canvas to a target position.
        
        Args:
            canvas: Canvas to scroll
            target_y: Target Y position (0.0 to 1.0)
            duration: Duration in milliseconds
        """
        try:
            current_y = canvas.yview()[0]
            steps = 20
            step_duration = duration // steps
            y_step = (target_y - current_y) / steps
            
            def animate(step=0):
                if step < steps:
                    new_y = current_y + (y_step * step)
                    try:
                        canvas.yview_moveto(new_y)
                    except:
                        pass
                    canvas.after(step_duration, lambda: animate(step + 1))
                else:
                    try:
                        canvas.yview_moveto(target_y)
                    except:
                        pass
            
            animate()
        except:
            # If animation fails, just scroll directly
            try:
                canvas.yview_moveto(target_y)
            except:
                pass


class DivinationAnimation:
    """Specialized animations for divination process."""
    
    @staticmethod
    def show_divination_progress(parent: tk.Frame, on_complete: Callable) -> None:
        """
        Show an animated divination progress dialog.
        
        Args:
            parent: Parent frame
            on_complete: Callback function when animation completes
        """
        from .styles import Styles
        
        # Create overlay
        overlay = tk.Frame(
            parent,
            bg=Styles.colors.BACKGROUND_COLOR
        )
        overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
        
        # Center frame
        center_frame = tk.Frame(
            overlay,
            bg=Styles.colors.BACKGROUND_COLOR
        )
        center_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        # Title
        title_label = tk.Label(
            center_frame,
            text="正在卜卦...",
            font=Styles.fonts.heading_font(),
            bg=Styles.colors.BACKGROUND_COLOR,
            fg=Styles.colors.TEXT_COLOR
        )
        title_label.pack(pady=Styles.sizes.PADDING)
        
        # Progress label
        progress_label = tk.Label(
            center_frame,
            text="擲銅錢中",
            font=Styles.fonts.body_font(),
            bg=Styles.colors.BACKGROUND_COLOR,
            fg=Styles.colors.LIGHT_TEXT
        )
        progress_label.pack(pady=Styles.sizes.SMALL_PADDING)
        
        # Start loading animation
        animation = AnimationManager.loading_dots(progress_label, "擲銅錢中")
        
        # Simulate divination process
        def complete():
            animation['stop']()
            overlay.destroy()
            on_complete()
        
        # Complete after a short delay
        overlay.after(1500, complete)
