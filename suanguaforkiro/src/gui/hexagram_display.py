"""
Hexagram display component for visualizing I Ching hexagrams.

This module provides a widget for drawing hexagrams with proper yao representation,
changing yao markers, and hexagram information display.
"""

import tkinter as tk
from typing import Optional
from ..models.hexagram import Hexagram
from ..models.yao import Yao
from .styles import Styles


class HexagramDisplay(tk.Frame):
    """
    A widget for displaying I Ching hexagrams visually.
    
    This component draws hexagrams using Canvas, showing:
    - Yang yaos as solid lines (━━━━━━)
    - Yin yaos as broken lines (━━  ━━)
    - Changing yaos with special markers
    - Hexagram name and basic information
    """
    
    def __init__(self, parent: tk.Widget, width: int = 150, height: int = 200):
        """
        Initialize the hexagram display widget.
        
        Args:
            parent: Parent tkinter widget
            width: Canvas width in pixels
            height: Canvas height in pixels
        """
        super().__init__(parent, bg=Styles.colors.BACKGROUND_COLOR)
        
        self.width = width
        self.height = height
        
        # Create canvas for drawing hexagram
        self.canvas = tk.Canvas(
            self,
            width=width,
            height=height,
            bg=Styles.colors.BACKGROUND_COLOR,
            highlightthickness=0
        )
        self.canvas.pack(pady=Styles.sizes.SMALL_PADDING)
        
        # Label for hexagram name
        self.name_label = tk.Label(
            self,
            text="",
            font=Styles.fonts.heading_font(),
            fg=Styles.colors.TEXT_COLOR,
            bg=Styles.colors.BACKGROUND_COLOR
        )
        self.name_label.pack()
        
        # Label for hexagram number and trigrams
        self.info_label = tk.Label(
            self,
            text="",
            font=Styles.fonts.small_font(),
            fg=Styles.colors.LIGHT_TEXT,
            bg=Styles.colors.BACKGROUND_COLOR
        )
        self.info_label.pack()
    
    def draw_hexagram(self, hexagram: Hexagram, show_changing: bool = True) -> None:
        """
        Draw a hexagram on the canvas.
        
        Args:
            hexagram: The Hexagram object to draw
            show_changing: Whether to mark changing yaos with special color/symbol
        """
        self.clear()
        
        # Calculate starting position (draw from bottom to top)
        yao_height = Styles.sizes.YAO_HEIGHT
        yao_spacing = Styles.sizes.YAO_SPACING
        total_height = 6 * yao_height + 5 * yao_spacing
        start_y = (self.height - total_height) // 2 + total_height - yao_height
        
        # Draw each yao from bottom (position 1) to top (position 6)
        for i, yao in enumerate(hexagram.yaos):
            y_position = start_y - i * (yao_height + yao_spacing)
            self.draw_yao(yao, y_position, show_changing)
        
        # Display hexagram information
        self._display_info(hexagram)
    
    def draw_yao(self, yao: Yao, y_position: int, show_changing: bool = True) -> None:
        """
        Draw a single yao (line) on the canvas.
        
        Args:
            yao: The Yao object to draw
            y_position: Y coordinate for the yao
            show_changing: Whether to use special color for changing yaos
        """
        yao_width = Styles.sizes.YAO_WIDTH
        yao_height = Styles.sizes.YAO_HEIGHT
        yao_gap = Styles.sizes.YAO_GAP
        
        # Calculate center position
        center_x = self.width // 2
        
        # Determine color based on whether it's a changing yao
        if show_changing and yao.is_changing:
            color = Styles.colors.CHANGING_YAO_COLOR
        else:
            color = Styles.colors.PRIMARY_COLOR
        
        if yao.is_yang():
            # Draw solid line for yang yao (━━━━━━)
            x1 = center_x - yao_width // 2
            x2 = center_x + yao_width // 2
            y1 = y_position
            y2 = y_position + yao_height
            
            self.canvas.create_rectangle(
                x1, y1, x2, y2,
                fill=color,
                outline=color
            )
        else:
            # Draw broken line for yin yao (━━  ━━)
            segment_width = (yao_width - yao_gap) // 2
            
            # Left segment
            x1_left = center_x - yao_width // 2
            x2_left = x1_left + segment_width
            y1 = y_position
            y2 = y_position + yao_height
            
            self.canvas.create_rectangle(
                x1_left, y1, x2_left, y2,
                fill=color,
                outline=color
            )
            
            # Right segment
            x1_right = center_x + yao_gap // 2
            x2_right = x1_right + segment_width
            
            self.canvas.create_rectangle(
                x1_right, y1, x2_right, y2,
                fill=color,
                outline=color
            )
        
        # Add changing marker if applicable
        if show_changing and yao.is_changing:
            marker_x = center_x + yao_width // 2 + 15
            marker_y = y_position + yao_height // 2
            
            self.canvas.create_text(
                marker_x, marker_y,
                text="⚡",
                font=Styles.fonts.small_font(),
                fill=Styles.colors.CHANGING_YAO_COLOR
            )
    
    def _display_info(self, hexagram: Hexagram) -> None:
        """
        Display hexagram name and basic information.
        
        Args:
            hexagram: The Hexagram object
        """
        # Display hexagram name
        if hexagram.name:
            self.name_label.config(text=hexagram.name)
        
        # Display hexagram number and trigrams
        info_parts = []
        if hexagram.number:
            info_parts.append(f"第 {hexagram.number} 卦")
        if hexagram.upper_trigram and hexagram.lower_trigram:
            info_parts.append(f"{hexagram.upper_trigram}/{hexagram.lower_trigram}")
        
        if info_parts:
            self.info_label.config(text=" · ".join(info_parts))
    
    def clear(self) -> None:
        """Clear the canvas and reset labels."""
        self.canvas.delete("all")
        self.name_label.config(text="")
        self.info_label.config(text="")

