"""
History frame for displaying divination records.

This module provides the HistoryFrame class which displays a list of
historical divination records.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
from typing import Callable, List, Optional
from datetime import datetime

from .styles import Styles
from .utils import handle_exception, show_error
from .hexagram_display import HexagramDisplay
from ..services.history_manager import HistoryManager, DivinationRecord
from ..data.hexagram_database import HexagramDatabase
from ..models.hexagram import Hexagram
from ..models.yao import Yao, YaoType


class HistoryFrame:
    """
    History display frame.
    
    This class manages the history interface, displaying a list of
    divination records with date, question, and hexagram information.
    """
    
    def __init__(self, parent: tk.Frame, history_manager: HistoryManager,
                 database: HexagramDatabase, on_return: Callable[[], None]):
        """
        Initialize the history frame.
        
        Args:
            parent: Parent frame widget
            history_manager: HistoryManager instance
            database: HexagramDatabase instance for looking up hexagram details
            on_return: Callback function to return to main menu
        """
        self.parent = parent
        self.history_manager = history_manager
        self.database = database
        self.on_return = on_return
        self.records: List[DivinationRecord] = []
        self.filtered_records: List[DivinationRecord] = []
        
        # Detail view state
        self.detail_view_active = False
        self.current_record: Optional[DivinationRecord] = None
        
        # Search variable
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self._on_search_changed)
        
        # Create main frame
        self.frame = tk.Frame(
            parent,
            bg=Styles.colors.BACKGROUND_COLOR
        )
        self.frame.pack(fill=tk.BOTH, expand=True)
        
        # Build the UI
        self._build_ui()
        
        # Load records
        self.load_records()
    
    def _build_ui(self) -> None:
        """Build the user interface."""
        # Top bar with title and back button
        self._create_top_bar()
        
        # Main content area
        self._create_content_area()
    
    def _create_top_bar(self) -> None:
        """Create the top bar with title and back button."""
        top_bar = tk.Frame(
            self.frame,
            bg=Styles.colors.PRIMARY_COLOR,
            height=60
        )
        top_bar.pack(fill=tk.X, side=tk.TOP)
        top_bar.pack_propagate(False)
        
        # Back button
        back_btn = tk.Button(
            top_bar,
            text="← 返回",
            font=Styles.fonts.button_font(),
            bg=Styles.colors.SECONDARY_COLOR,
            fg=Styles.colors.WHITE_TEXT,
            activebackground=Styles.colors.BUTTON_HOVER,
            command=self.on_return,
            cursor="hand2",
            relief=tk.FLAT,
            padx=Styles.sizes.LARGE_PADDING,
            pady=Styles.sizes.PADDING
        )
        back_btn.pack(side=tk.LEFT, padx=Styles.sizes.PADDING, pady=Styles.sizes.PADDING)
        
        # Title
        title_label = tk.Label(
            top_bar,
            text="📚 歷史記錄",
            font=Styles.fonts.title_font(),
            bg=Styles.colors.PRIMARY_COLOR,
            fg=Styles.colors.WHITE_TEXT
        )
        title_label.pack(side=tk.LEFT, padx=Styles.sizes.LARGE_PADDING)
    
    def _create_search_area(self, parent: tk.Frame) -> None:
        """
        Create the search area with input box and clear button.
        
        Args:
            parent: Parent frame widget
        """
        search_frame = tk.Frame(
            parent,
            bg=Styles.colors.BACKGROUND_COLOR
        )
        search_frame.pack(fill=tk.X)
        
        # Configure grid for search frame
        search_frame.grid_columnconfigure(1, weight=1)
        
        # Search label
        search_label = tk.Label(
            search_frame,
            text="🔍 搜尋：",
            font=Styles.fonts.body_font(),
            bg=Styles.colors.BACKGROUND_COLOR,
            fg=Styles.colors.TEXT_COLOR
        )
        search_label.grid(row=0, column=0, padx=(0, Styles.sizes.SMALL_PADDING), sticky="w")
        
        # Search entry with responsive width
        self.search_entry = tk.Entry(
            search_frame,
            textvariable=self.search_var,
            font=Styles.fonts.body_font()
        )
        self.search_entry.grid(row=0, column=1, padx=(0, Styles.sizes.SMALL_PADDING), sticky="ew")
        
        # Clear button
        clear_btn = tk.Button(
            search_frame,
            text="✕ 清除",
            font=Styles.fonts.body_font(),
            bg=Styles.colors.SECONDARY_COLOR,
            fg=Styles.colors.WHITE_TEXT,
            activebackground=Styles.colors.BUTTON_HOVER,
            command=self.clear_search,
            cursor="hand2",
            relief=tk.FLAT,
            padx=Styles.sizes.PADDING,
            pady=Styles.sizes.SMALL_PADDING
        )
        clear_btn.grid(row=0, column=2, sticky="e")
    
    def _create_content_area(self) -> None:
        """Create the main content area with record list."""
        # Content frame with grid layout
        content_frame = tk.Frame(
            self.frame,
            bg=Styles.colors.BACKGROUND_COLOR
        )
        content_frame.pack(fill=tk.BOTH, expand=True, padx=Styles.sizes.LARGE_PADDING,
                          pady=Styles.sizes.LARGE_PADDING)
        
        # Configure grid weights for responsive layout
        content_frame.grid_rowconfigure(0, weight=0)  # Search area
        content_frame.grid_rowconfigure(1, weight=0)  # Info label
        content_frame.grid_rowconfigure(2, weight=1)  # Tree view
        content_frame.grid_columnconfigure(0, weight=1)
        
        # Search area
        search_container = tk.Frame(content_frame, bg=Styles.colors.BACKGROUND_COLOR)
        search_container.grid(row=0, column=0, sticky="ew", pady=(0, Styles.sizes.PADDING))
        self._create_search_area(search_container)
        
        # Info label
        info_label = tk.Label(
            content_frame,
            text="點擊記錄查看詳細內容",
            font=Styles.fonts.small_font(),
            bg=Styles.colors.BACKGROUND_COLOR,
            fg=Styles.colors.LIGHT_TEXT
        )
        info_label.grid(row=1, column=0, sticky="w", pady=(0, Styles.sizes.SMALL_PADDING))
        
        # Create frame for treeview and scrollbar with grid layout
        tree_frame = tk.Frame(
            content_frame,
            bg=Styles.colors.BACKGROUND_COLOR
        )
        tree_frame.grid(row=2, column=0, sticky="nsew")
        
        # Configure grid weights for tree frame
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        # Create treeview for displaying records
        self.tree = ttk.Treeview(
            tree_frame,
            columns=("date", "question", "hexagram"),
            show="headings",
            height=Styles.sizes.LISTBOX_HEIGHT
        )
        
        # Create scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Define column headings
        self.tree.heading("date", text="日期時間")
        self.tree.heading("question", text="問題")
        self.tree.heading("hexagram", text="卦象")
        
        # Configure column widths with stretch for responsiveness
        self.tree.column("date", width=150, minwidth=120, stretch=False)
        self.tree.column("question", width=300, minwidth=200, stretch=True)
        self.tree.column("hexagram", width=200, minwidth=150, stretch=False)
        
        # Grid layout for treeview and scrollbar
        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Configure treeview style
        style = ttk.Style()
        style.configure("Treeview",
                       font=Styles.fonts.body_font(),
                       rowheight=30)
        style.configure("Treeview.Heading",
                       font=Styles.fonts.heading_font())
        
        # Bind double-click event (for future detail view)
        self.tree.bind("<Double-Button-1>", self._on_record_double_click)
    
    @handle_exception
    def load_records(self) -> None:
        """
        Load records from HistoryManager and display them.
        
        This method retrieves all records from the history manager
        and populates the treeview with formatted data.
        """
        try:
            # Get all records
            self.records = self.history_manager.get_all_records()
            
            # Initialize filtered records to all records
            self.filtered_records = self.records.copy()
            
            # Display the records
            self._display_records(self.filtered_records)
        
        except FileNotFoundError as e:
            # History file doesn't exist yet - this is OK for first run
            show_warning(
                "歷史記錄",
                "尚未建立歷史記錄檔案。\n開始卜卦後儲存記錄即可建立。",
                self.parent
            )
            self.records = []
            self.filtered_records = []
            self._display_records([])
        
        except PermissionError as e:
            # Cannot read history file due to permissions
            show_error(
                "載入失敗",
                f"無法讀取歷史記錄檔案：權限不足\n\n{str(e)}\n\n請檢查檔案權限設定。",
                self.parent
            )
            self.records = []
            self.filtered_records = []
            self._display_records([])
        
        except Exception as e:
            # Other errors - show warning but allow continuing
            show_warning(
                "載入警告",
                f"載入歷史記錄時發生錯誤：\n\n{str(e)}\n\n您仍可以進行卜卦，但無法查看歷史記錄。",
                self.parent
            )
            self.records = []
            self.filtered_records = []
            self._display_records([])
    
    def _display_records(self, records: List[DivinationRecord]) -> None:
        """
        Display records in the treeview.
        
        Args:
            records: List of records to display
        """
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Check if there are no records
        if not records:
            # Insert a placeholder message
            message = "尚無歷史記錄" if not self.records else "沒有符合的記錄"
            self.tree.insert("", tk.END, values=(
                "",
                message,
                ""
            ))
            return
        
        # Populate treeview with records
        for record in records:
            # Format date
            date_str = self._format_date(record.timestamp)
            
            # Format question (truncate if too long)
            question_str = self._format_question(record.question)
            
            # Format hexagram info
            hexagram_str = self._format_hexagram(record)
            
            # Insert into treeview
            self.tree.insert("", tk.END, values=(
                date_str,
                question_str,
                hexagram_str
            ))
    
    def _format_date(self, timestamp_str: str) -> str:
        """
        Format timestamp for display.
        
        Args:
            timestamp_str: ISO format timestamp string
        
        Returns:
            Formatted date string
        """
        try:
            dt = datetime.fromisoformat(timestamp_str)
            return dt.strftime("%Y-%m-%d %H:%M")
        except Exception:
            return timestamp_str
    
    def _format_question(self, question: str, max_length: int = 40) -> str:
        """
        Format question text for display.
        
        Args:
            question: Question text
            max_length: Maximum length before truncation
        
        Returns:
            Formatted question string
        """
        if len(question) > max_length:
            return question[:max_length] + "..."
        return question
    
    def _format_hexagram(self, record: DivinationRecord) -> str:
        """
        Format hexagram information for display.
        
        Args:
            record: DivinationRecord object
        
        Returns:
            Formatted hexagram string
        """
        hexagram_str = f"{record.original_hexagram_number}. {record.original_hexagram_name}"
        
        if record.has_changes and record.changed_hexagram_name:
            hexagram_str += f" → {record.changed_hexagram_number}. {record.changed_hexagram_name}"
        
        return hexagram_str
    
    def search_records(self, keyword: str) -> None:
        """
        Search records by keyword.
        
        This method filters records based on the search keyword,
        matching against question text, hexagram names, and dates.
        
        Args:
            keyword: Search keyword (case-insensitive)
        """
        if not keyword or keyword.strip() == "":
            # If no keyword, show all records
            self.filtered_records = self.records.copy()
        else:
            # Convert keyword to lowercase for case-insensitive search
            keyword_lower = keyword.lower()
            
            # Filter records
            self.filtered_records = []
            for record in self.records:
                # Check if keyword matches question
                if keyword_lower in record.question.lower():
                    self.filtered_records.append(record)
                    continue
                
                # Check if keyword matches original hexagram name
                if keyword_lower in record.original_hexagram_name.lower():
                    self.filtered_records.append(record)
                    continue
                
                # Check if keyword matches changed hexagram name
                if record.changed_hexagram_name and keyword_lower in record.changed_hexagram_name.lower():
                    self.filtered_records.append(record)
                    continue
                
                # Check if keyword matches date
                date_str = self._format_date(record.timestamp)
                if keyword_lower in date_str.lower():
                    self.filtered_records.append(record)
                    continue
        
        # Update display
        self._display_records(self.filtered_records)
    
    def clear_search(self) -> None:
        """
        Clear the search input and show all records.
        """
        self.search_var.set("")
        self.search_entry.focus()
    
    def _on_search_changed(self, *args) -> None:
        """
        Callback for search variable changes.
        
        This method is called automatically when the search text changes,
        implementing real-time search filtering.
        
        Args:
            *args: Variable trace arguments (unused)
        """
        keyword = self.search_var.get()
        self.search_records(keyword)
    
    @handle_exception
    def show_record_detail(self, record: DivinationRecord) -> None:
        """
        Show detailed view of a divination record.
        
        This method displays the complete hexagram information, including
        the original hexagram, changing yaos, and changed hexagram if applicable.
        
        Args:
            record: DivinationRecord to display
        """
        try:
            # Store current record
            self.current_record = record
            self.detail_view_active = True
            
            # Hide the list view
            self.frame.pack_forget()
            
            # Create detail view frame
            self.detail_frame = tk.Frame(
                self.parent,
                bg=Styles.colors.BACKGROUND_COLOR
            )
            self.detail_frame.pack(fill=tk.BOTH, expand=True)
            
            # Build detail UI
            self._build_detail_ui()
            
        except KeyError as e:
            # Hexagram data not found in database
            show_error(
                "資料錯誤",
                f"找不到卦象資料：{str(e)}\n\n記錄可能已損壞。",
                self.parent
            )
            self._return_to_list()
        
        except Exception as e:
            show_error(
                "顯示失敗",
                f"無法顯示記錄詳情：\n\n{str(e)}",
                self.parent
            )
            self._return_to_list()
    
    def _build_detail_ui(self) -> None:
        """Build the detail view UI."""
        if not self.current_record:
            return
        
        # Top bar with back button
        top_bar = tk.Frame(
            self.detail_frame,
            bg=Styles.colors.PRIMARY_COLOR,
            height=60
        )
        top_bar.pack(fill=tk.X, side=tk.TOP)
        top_bar.pack_propagate(False)
        
        # Back to list button
        back_btn = tk.Button(
            top_bar,
            text="← 返回列表",
            font=Styles.fonts.button_font(),
            bg=Styles.colors.SECONDARY_COLOR,
            fg=Styles.colors.WHITE_TEXT,
            activebackground=Styles.colors.BUTTON_HOVER,
            command=self._return_to_list,
            cursor="hand2",
            relief=tk.FLAT,
            padx=Styles.sizes.LARGE_PADDING,
            pady=Styles.sizes.PADDING
        )
        back_btn.pack(side=tk.LEFT, padx=Styles.sizes.PADDING, pady=Styles.sizes.PADDING)
        
        # Title
        title_label = tk.Label(
            top_bar,
            text="📖 記錄詳情",
            font=Styles.fonts.title_font(),
            bg=Styles.colors.PRIMARY_COLOR,
            fg=Styles.colors.WHITE_TEXT
        )
        title_label.pack(side=tk.LEFT, padx=Styles.sizes.LARGE_PADDING)
        
        # Main content area with scrollbar
        content_frame = tk.Frame(
            self.detail_frame,
            bg=Styles.colors.BACKGROUND_COLOR
        )
        content_frame.pack(fill=tk.BOTH, expand=True, padx=Styles.sizes.LARGE_PADDING,
                          pady=Styles.sizes.LARGE_PADDING)
        
        # Create canvas for scrolling
        canvas = tk.Canvas(
            content_frame,
            bg=Styles.colors.BACKGROUND_COLOR,
            highlightthickness=0
        )
        scrollbar = ttk.Scrollbar(content_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=Styles.colors.BACKGROUND_COLOR)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack canvas and scrollbar
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Display record information
        self._display_record_info(scrollable_frame)
    
    def _display_record_info(self, parent: tk.Frame) -> None:
        """
        Display the complete record information.
        
        Args:
            parent: Parent frame for the content
        """
        if not self.current_record:
            return
        
        # Question and timestamp
        info_frame = tk.Frame(parent, bg=Styles.colors.BACKGROUND_COLOR)
        info_frame.pack(fill=tk.X, pady=(0, Styles.sizes.LARGE_PADDING))
        
        # Timestamp
        timestamp_label = tk.Label(
            info_frame,
            text=f"時間：{self._format_date(self.current_record.timestamp)}",
            font=Styles.fonts.body_font(),
            fg=Styles.colors.LIGHT_TEXT,
            bg=Styles.colors.BACKGROUND_COLOR,
            anchor=tk.W
        )
        timestamp_label.pack(fill=tk.X)
        
        # Question
        question_label = tk.Label(
            info_frame,
            text=f"問題：{self.current_record.question}",
            font=Styles.fonts.heading_font(),
            fg=Styles.colors.TEXT_COLOR,
            bg=Styles.colors.BACKGROUND_COLOR,
            anchor=tk.W,
            wraplength=700,
            justify=tk.LEFT
        )
        question_label.pack(fill=tk.X, pady=(Styles.sizes.SMALL_PADDING, 0))
        
        # Separator
        separator = tk.Frame(info_frame, height=2, bg=Styles.colors.LIGHT_TEXT)
        separator.pack(fill=tk.X, pady=Styles.sizes.PADDING)
        
        # Hexagram display area
        hexagram_frame = tk.Frame(parent, bg=Styles.colors.BACKGROUND_COLOR)
        hexagram_frame.pack(fill=tk.BOTH, expand=True)
        
        # Get hexagram data from database
        try:
            original_hex_data = self.database.get_by_number(self.current_record.original_hexagram_number)
            
            if not original_hex_data:
                show_error(
                    "資料錯誤",
                    f"找不到卦象資料（卦序 {self.current_record.original_hexagram_number}）",
                    self.parent
                )
                return
            
            # Create hexagram displays side by side with grid layout
            displays_frame = tk.Frame(hexagram_frame, bg=Styles.colors.BACKGROUND_COLOR)
            displays_frame.pack(pady=Styles.sizes.PADDING, fill=tk.X)
            
            # Configure grid for centering
            displays_frame.grid_columnconfigure(0, weight=1)
            displays_frame.grid_columnconfigure(1, weight=0)
            displays_frame.grid_columnconfigure(2, weight=0)
            displays_frame.grid_columnconfigure(3, weight=1)
            
            # Original hexagram display
            original_frame = tk.Frame(displays_frame, bg=Styles.colors.BACKGROUND_COLOR)
            original_frame.grid(row=0, column=1, padx=Styles.sizes.LARGE_PADDING)
            
            original_title = tk.Label(
                original_frame,
                text="本卦",
                font=Styles.fonts.heading_font(),
                fg=Styles.colors.TEXT_COLOR,
                bg=Styles.colors.BACKGROUND_COLOR
            )
            original_title.pack()
            
            # Create hexagram display
            original_display = HexagramDisplay(original_frame, width=150, height=200)
            original_display.pack()
            
            # Reconstruct hexagram from binary
            original_hexagram = self._reconstruct_hexagram(original_hex_data)
            original_display.draw_hexagram(original_hexagram, show_changing=False)
            
            # Changed hexagram display (if applicable)
            if self.current_record.has_changes and self.current_record.changed_hexagram_number:
                changed_hex_data = self.database.get_by_number(self.current_record.changed_hexagram_number)
                
                if changed_hex_data:
                    changed_frame = tk.Frame(displays_frame, bg=Styles.colors.BACKGROUND_COLOR)
                    changed_frame.grid(row=0, column=2, padx=Styles.sizes.LARGE_PADDING)
                    
                    changed_title = tk.Label(
                        changed_frame,
                        text="之卦",
                        font=Styles.fonts.heading_font(),
                        fg=Styles.colors.TEXT_COLOR,
                        bg=Styles.colors.BACKGROUND_COLOR
                    )
                    changed_title.pack()
                    
                    changed_display = HexagramDisplay(changed_frame, width=150, height=200)
                    changed_display.pack()
                    
                    changed_hexagram = self._reconstruct_hexagram(changed_hex_data)
                    changed_display.draw_hexagram(changed_hexagram, show_changing=False)
            
            # Text display area
            text_frame = tk.Frame(hexagram_frame, bg=Styles.colors.BACKGROUND_COLOR)
            text_frame.pack(fill=tk.BOTH, expand=True, pady=Styles.sizes.PADDING)
            
            # Description label
            desc_label = tk.Label(
                text_frame,
                text="卦辭與解釋：",
                font=Styles.fonts.heading_font(),
                fg=Styles.colors.TEXT_COLOR,
                bg=Styles.colors.BACKGROUND_COLOR,
                anchor=tk.W
            )
            desc_label.pack(fill=tk.X, pady=(0, Styles.sizes.SMALL_PADDING))
            
            # Scrolled text for descriptions
            text_display = scrolledtext.ScrolledText(
                text_frame,
                font=Styles.fonts.body_font(),
                wrap=tk.WORD,
                height=15,
                bg="white",
                fg=Styles.colors.TEXT_COLOR
            )
            text_display.pack(fill=tk.BOTH, expand=True)
            
            # Build text content
            self._build_text_content(text_display, original_hex_data, changed_hex_data if self.current_record.has_changes else None)
            
            # Make text read-only
            text_display.config(state=tk.DISABLED)
            
        except KeyError as e:
            show_error(
                "資料錯誤",
                f"卦象資料不完整：{str(e)}\n\n記錄可能已損壞。",
                self.parent
            )
        
        except Exception as e:
            show_error(
                "顯示錯誤",
                f"無法顯示卦象詳情：\n\n{str(e)}",
                self.parent
            )
    
    def _reconstruct_hexagram(self, hex_data) -> Hexagram:
        """
        Reconstruct a Hexagram object from database data.
        
        Args:
            hex_data: HexagramData from database
        
        Returns:
            Hexagram object
        """
        # Convert binary string to yaos
        yaos = []
        for i, bit in enumerate(hex_data.binary):
            # Determine yao type based on binary value
            # For historical records, we use non-changing yaos
            if bit == '1':
                yao_type = YaoType.YOUNG_YANG
            else:
                yao_type = YaoType.YOUNG_YIN
            
            yao = Yao(
                yao_type=yao_type,
                position=i + 1
            )
            yaos.append(yao)
        
        return Hexagram(
            yaos=yaos,
            name=hex_data.name,
            number=hex_data.number,
            upper_trigram=hex_data.upper_trigram,
            lower_trigram=hex_data.lower_trigram,
            description=hex_data.description,
            yao_texts=hex_data.yao_texts
        )
    
    def _build_text_content(self, text_widget: scrolledtext.ScrolledText, 
                           original_data, changed_data=None) -> None:
        """
        Build the text content for the description area.
        
        Args:
            text_widget: ScrolledText widget to populate
            original_data: Original hexagram data
            changed_data: Changed hexagram data (optional)
        """
        text_widget.config(state=tk.NORMAL)
        
        # Original hexagram description
        text_widget.insert(tk.END, "【本卦】\n", "heading")
        text_widget.insert(tk.END, f"{original_data.name}卦\n", "subheading")
        text_widget.insert(tk.END, f"第 {original_data.number} 卦\n")
        text_widget.insert(tk.END, f"上卦：{original_data.upper_trigram}  下卦：{original_data.lower_trigram}\n\n")
        text_widget.insert(tk.END, f"卦辭：{original_data.description}\n\n")
        
        # Yao texts
        text_widget.insert(tk.END, "爻辭：\n", "subheading")
        yao_names = ["初", "二", "三", "四", "五", "上"]
        for i, yao_text in enumerate(original_data.yao_texts):
            text_widget.insert(tk.END, f"{yao_names[i]}：{yao_text}\n")
        
        # Changed hexagram (if applicable)
        if changed_data:
            text_widget.insert(tk.END, "\n" + "="*50 + "\n\n")
            text_widget.insert(tk.END, "【之卦】\n", "heading")
            text_widget.insert(tk.END, f"{changed_data.name}卦\n", "subheading")
            text_widget.insert(tk.END, f"第 {changed_data.number} 卦\n")
            text_widget.insert(tk.END, f"上卦：{changed_data.upper_trigram}  下卦：{changed_data.lower_trigram}\n\n")
            text_widget.insert(tk.END, f"卦辭：{changed_data.description}\n")
        
        # Configure tags for formatting
        text_widget.tag_config("heading", font=Styles.fonts.heading_font(), 
                              foreground=Styles.colors.PRIMARY_COLOR)
        text_widget.tag_config("subheading", font=Styles.fonts.body_font_bold())
        
        text_widget.config(state=tk.DISABLED)
    
    def _return_to_list(self) -> None:
        """Return from detail view to list view."""
        if hasattr(self, 'detail_frame'):
            self.detail_frame.pack_forget()
            self.detail_frame.destroy()
        
        self.detail_view_active = False
        self.current_record = None
        
        # Show the list view again
        self.frame.pack(fill=tk.BOTH, expand=True)
    
    def _on_record_double_click(self, event) -> None:
        """
        Handle double-click on a record to show details.
        
        Args:
            event: Click event
        """
        # Get selected item
        selection = self.tree.selection()
        if not selection:
            return
        
        # Get the index of the selected item
        item = selection[0]
        item_index = self.tree.index(item)
        
        # Check if we have filtered records
        if not self.filtered_records or item_index >= len(self.filtered_records):
            return
        
        # Get the selected record
        selected_record = self.filtered_records[item_index]
        
        # Show record detail
        self.show_record_detail(selected_record)
