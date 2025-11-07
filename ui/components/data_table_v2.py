# -*- coding: utf-8 -*-
"""
Componente de Tabela V2 com scroll horizontal e vertical
Resolve problemas de overflow e scroll do DataTable original
"""
import customtkinter as ctk
import platform
import tkinter as tk
from typing import List, Dict, Callable, Optional


class ToolTip:
    """
    Tooltip para mostrar conteúdo completo ao passar o mouse
    """
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event=None):
        """Show tooltip if text is not empty"""
        if not self.text or self.text.strip() == "":
            return

        x, y, _, _ = self.widget.bbox("insert") if hasattr(self.widget, "bbox") else (0, 0, 0, 0)
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25

        self.tooltip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")

        label = tk.Label(
            tw,
            text=self.text,
            justify=tk.LEFT,
            background="#ffffe0",
            foreground="#000000",
            relief=tk.SOLID,
            borderwidth=1,
            font=("TkDefaultFont", 10),
            wraplength=400
        )
        label.pack(ipadx=5, ipady=3)

    def hide_tooltip(self, event=None):
        """Hide tooltip"""
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None


class DataTableV2(ctk.CTkFrame):
    """
    Tabela de dados com scroll horizontal + vertical nativo
    Colunas responsivas: expandem em fullscreen, scroll horizontal em janelas pequenas
    """

    def __init__(
        self,
        parent,
        columns: List[Dict],  # [{'key': 'nome', 'label': 'Nome', 'width': 200, 'truncate': True}]
        height: int = 400,
        on_row_double_click: Optional[Callable] = None,
        on_selection_change: Optional[Callable] = None,
        **kwargs
    ):
        """
        Initialize data table V2

        Args:
            parent: Parent widget
            columns: List of column definitions. Each column can have:
                - key: Data key
                - label: Column header
                - width: Minimum column width in pixels
                - truncate: If True, truncate text and show tooltip (default: True)
                - formatter: Optional function to format value
                - sortable: If False, column is not sortable (default: True)
            height: Table height in pixels
            on_row_double_click: Optional callback when row is double-clicked (receives row data)
            on_selection_change: Optional callback when selection changes (receives list of selected data)
        """
        super().__init__(parent, **kwargs)

        # Store base column widths (minimum widths)
        self.base_columns = columns
        self.columns = columns.copy()  # Will be updated with responsive widths

        self.data_rows = []
        self.original_data_rows = []  # Store original order
        self.row_widgets = []
        self.header_widgets = []
        self.is_mac = platform.system() == "Darwin"
        self.last_canvas_width = 0

        # Callbacks
        self.on_row_double_click = on_row_double_click
        self.on_selection_change = on_selection_change

        # Selection state
        self.selected_rows = set()  # Set of row indices
        self.row_data_map = {}  # Map row_frame widget -> (data, index)
        self.last_clicked_index = None  # For shift-click range selection

        # Sorting state
        self.sort_column = None  # Column key being sorted
        self.sort_direction = None  # 'asc', 'desc', or None

        # Configure
        self.configure(fg_color="transparent")

        # Calculate minimum width needed
        self.min_table_width = self._calculate_min_width()

        # Create main container with 2 rows: header (fixed) + data (scrollable)
        self.grid_rowconfigure(0, weight=0)  # Header row (fixed height)
        self.grid_rowconfigure(1, weight=1)  # Data row (expandable)
        self.grid_columnconfigure(0, weight=1)

        # Create header canvas (fixed height, scrolls horizontally with content)
        self.header_canvas = ctk.CTkCanvas(self, highlightthickness=0, height=50, bg="#3a3a3a")
        self.header_canvas.grid(row=0, column=0, sticky="ew")

        # Create header container inside canvas
        self.header_container = ctk.CTkFrame(self.header_canvas, fg_color="transparent")
        self.header_canvas_window = self.header_canvas.create_window((0, 0), window=self.header_container, anchor="nw")

        # Create header
        self.create_header()

        # Create canvas for scrolling data (below header)
        self.canvas = ctk.CTkCanvas(self, highlightthickness=0, bg="#3a3a3a")
        self.canvas.grid(row=1, column=0, sticky="nsew")

        # Create scrollbars
        self.v_scrollbar = ctk.CTkScrollbar(self, orientation="vertical", command=self.canvas.yview)
        self.v_scrollbar.grid(row=1, column=1, sticky="ns")

        self.h_scrollbar = ctk.CTkScrollbar(self, orientation="horizontal", command=self._on_h_scroll)
        self.h_scrollbar.grid(row=2, column=0, sticky="ew")

        # Configure canvas
        self.canvas.configure(
            yscrollcommand=self.v_scrollbar.set,
            xscrollcommand=self.h_scrollbar.set
        )

        # Configure header canvas to use same horizontal scrollbar
        self.header_canvas.configure(xscrollcommand=lambda *args: None)  # Ignore, we'll sync manually

        # Create inner frame for content (NO fixed width - will be responsive)
        self.inner_frame = ctk.CTkFrame(self.canvas, fg_color="transparent")
        self.canvas_window = self.canvas.create_window((0, 0), window=self.inner_frame, anchor="nw")

        # Bind events
        self.inner_frame.bind("<Configure>", self._on_frame_configure)
        self.header_container.bind("<Configure>", self._on_header_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)

        # Bind scroll events
        self._bind_scroll_events()

        # Setup keyboard shortcuts (after canvas creation)
        self._setup_keyboard_shortcuts()

        # Ensure canvas starts at top-left (delayed to ensure canvas is fully initialized)
        self.after(10, lambda: self.canvas.yview_moveto(0))
        self.after(10, lambda: self.canvas.xview_moveto(0))

    def _calculate_min_width(self) -> int:
        """Calculate minimum width needed for all columns"""
        # Data columns + their paddings (minimal)
        data_width = sum(col.get('width', 100) + 4 for col in self.base_columns)
        return data_width  # No extra outer margins

    def _update_responsive_widths(self, available_width: int):
        """
        Update column widths based on available space

        Args:
            available_width: Width available in canvas
        """
        # Use all available width
        usable_width = available_width

        # Calculate total minimum width for data columns (with their paddings)
        min_data_width = sum(col.get('width', 100) for col in self.base_columns)
        # Add padding per column (minimal)
        data_columns_total = min_data_width + (len(self.base_columns) * 4)

        # Total minimum width
        total_min_width = data_columns_total

        # If we have extra space, distribute it proportionally to columns
        if usable_width > total_min_width:
            extra_space = usable_width - total_min_width

            # Distribute extra space proportionally to column widths
            self.columns = []
            for col in self.base_columns:
                base_width = col.get('width', 100)
                proportion = base_width / min_data_width
                extra_for_col = int(extra_space * proportion)

                new_col = col.copy()
                new_col['width'] = base_width + extra_for_col
                self.columns.append(new_col)

            # Set inner frame width to fill canvas
            self.canvas.itemconfig(self.canvas_window, width=usable_width)
            # Hide horizontal scrollbar when not needed
            self.h_scrollbar.grid_remove()
        else:
            # Use minimum widths + enable horizontal scroll
            self.columns = [col.copy() for col in self.base_columns]

            # Set inner frame width to minimum
            self.canvas.itemconfig(self.canvas_window, width=total_min_width)
            # Show horizontal scrollbar when needed
            self.h_scrollbar.grid(row=2, column=0, sticky="ew")

    def _on_canvas_configure(self, event):
        """Update layout when canvas resizes"""
        new_width = event.width

        # Only update if width actually changed (avoid loops)
        if abs(new_width - self.last_canvas_width) > 5:
            self.last_canvas_width = new_width

            # Update responsive widths
            self._update_responsive_widths(new_width)

            # Rebuild table with new widths
            if self.data_rows:
                self._rebuild_table()

    def _rebuild_table(self):
        """Rebuild table with updated column widths"""
        # Store current data
        current_data = self.data_rows.copy()

        # Clear and rebuild header
        for widget in self.header_widgets:
            widget.destroy()
        self.header_widgets = []
        self.create_header()

        # Clear and rebuild rows
        for widget in self.row_widgets:
            widget.destroy()
        self.row_widgets = []

        # Recreate rows with new widths
        for index, item in enumerate(current_data):
            self.add_row(item, index)

        # Update scroll region
        self.inner_frame.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

        # Force another update to ensure scrollregion is applied
        self.canvas.update_idletasks()

        # Reset scroll to top-left (delayed to ensure canvas is fully updated)
        self.after(1, lambda: self.canvas.yview_moveto(0))
        self.after(1, lambda: self.canvas.xview_moveto(0))

    def _truncate_text(self, text: str, max_width: int, font_size: int = 12) -> str:
        """
        Truncate text to fit in max_width pixels

        Args:
            text: Text to truncate
            max_width: Maximum width in pixels
            font_size: Font size in points

        Returns:
            Truncated text with ellipsis if needed
        """
        if not text:
            return ""

        # Rough estimation: each character is ~6-8 pixels for size 12 font
        char_width = font_size * 0.6
        max_chars = int((max_width - 10) / char_width)  # -10 for padding

        if len(text) <= max_chars:
            return text

        return text[:max_chars - 3] + "..."

    def _bind_scroll_events(self):
        """Bind scroll events for all platforms"""
        # Bind to canvas itself
        self.canvas.bind("<Enter>", self._on_enter)
        self.canvas.bind("<Leave>", self._on_leave)

        # Also bind to the frame and all its children
        self.inner_frame.bind("<Enter>", self._on_enter)
        self.inner_frame.bind("<Leave>", self._on_leave)

    def _setup_keyboard_shortcuts(self):
        """Setup keyboard shortcuts for selection"""
        # Bind to multiple widgets to ensure shortcuts work when focused
        widgets_to_bind = [self, self.canvas, self.header_canvas]

        for widget in widgets_to_bind:
            self._bind_shortcuts_to_widget(widget)

    def _bind_shortcuts_to_widget(self, widget):
        """Bind keyboard shortcuts to a specific widget"""
        # Select all: Command-A on Mac, Control-A on others
        if self.is_mac:
            widget.bind("<Command-a>", self._select_all)
            widget.bind("<Command-z>", self._clear_selection_key)
        else:
            widget.bind("<Control-a>", self._select_all)
            widget.bind("<Control-z>", self._clear_selection_key)

        # Clear selection: Escape
        widget.bind("<Escape>", self._clear_selection_key)

    def _select_all(self, event=None):
        """Select all rows"""
        # Select all row indices
        self.selected_rows = set(range(len(self.row_widgets)))

        # Update colors for all rows
        for row_frame in self.row_widgets:
            if hasattr(row_frame, '_index'):
                is_hovered = getattr(row_frame, '_is_hovered', False)
                self._update_row_color(row_frame, True, is_hovered=is_hovered)

        # Update last clicked index to last row
        if self.row_widgets:
            self.last_clicked_index = len(self.row_widgets) - 1

        # Notify callback
        if self.on_selection_change:
            selected_data = self.get_selected_data()
            self.on_selection_change(selected_data)

        return "break"  # Prevent default behavior

    def _clear_selection_key(self, event=None):
        """Clear selection via keyboard"""
        self.clear_selection()
        return "break"  # Prevent default behavior

    def _on_enter(self, event):
        """When mouse enters the widget area"""
        # Give focus to canvas so keyboard shortcuts work
        self.canvas.focus_set()

        # Bind scroll events based on platform
        if self.is_mac:
            # macOS trackpad and mouse
            self.canvas.bind_all("<MouseWheel>", self._on_mousewheel_vertical)
            self.canvas.bind_all("<Shift-MouseWheel>", self._on_mousewheel_horizontal)
        elif platform.system() == "Linux":
            # Linux
            self.canvas.bind_all("<Button-4>", self._on_mousewheel_vertical)
            self.canvas.bind_all("<Button-5>", self._on_mousewheel_vertical)
        else:
            # Windows
            self.canvas.bind_all("<MouseWheel>", self._on_mousewheel_vertical)
            self.canvas.bind_all("<Shift-MouseWheel>", self._on_mousewheel_horizontal)

    def _on_leave(self, event):
        """When mouse leaves the widget area"""
        # Unbind scroll events
        if self.is_mac:
            self.canvas.unbind_all("<MouseWheel>")
            self.canvas.unbind_all("<Shift-MouseWheel>")
        elif platform.system() == "Linux":
            self.canvas.unbind_all("<Button-4>")
            self.canvas.unbind_all("<Button-5>")
        else:
            self.canvas.unbind_all("<MouseWheel>")
            self.canvas.unbind_all("<Shift-MouseWheel>")

    def _on_mousewheel_vertical(self, event):
        """Handle vertical scrolling"""
        if self.is_mac:
            # macOS: use delta directly
            self.canvas.yview_scroll(-1 * event.delta, "units")
        elif platform.system() == "Linux":
            # Linux: Button-4 is scroll up, Button-5 is scroll down
            if event.num == 4:
                self.canvas.yview_scroll(-1, "units")
            elif event.num == 5:
                self.canvas.yview_scroll(1, "units")
        else:
            # Windows
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _on_mousewheel_horizontal(self, event):
        """Handle horizontal scrolling (Shift + scroll)"""
        if self.is_mac:
            # macOS: use delta directly
            self.canvas.xview_scroll(-1 * event.delta, "units")
        else:
            # Windows
            self.canvas.xview_scroll(int(-1 * (event.delta / 120)), "units")

    def _on_frame_configure(self, event=None):
        """Update scroll region when frame changes"""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_header_configure(self, event=None):
        """Update header scroll region when header changes"""
        self.header_canvas.configure(scrollregion=self.header_canvas.bbox("all"))

    def _on_h_scroll(self, *args):
        """Sync horizontal scroll between header and content"""
        # Scroll both canvases horizontally
        self.canvas.xview(*args)
        self.header_canvas.xview(*args)

    def create_header(self):
        """Create fixed table header with sortable columns"""
        header_frame = ctk.CTkFrame(
            self.header_container,
            fg_color=("#efd578", "#d4bb5e"),
            corner_radius=0
        )
        header_frame.pack(fill="both", expand=True, padx=0, pady=0)
        self.header_widgets.append(header_frame)

        col_index = 0
        for col in self.columns:
            # Check if column is sortable (default True)
            is_sortable = col.get('sortable', True)

            # Get sort indicator
            sort_indicator = ""
            if is_sortable and self.sort_column == col['key']:
                sort_indicator = " ▲" if self.sort_direction == "asc" else " ▼"

            label = ctk.CTkLabel(
                header_frame,
                text=col['label'] + sort_indicator,
                font=ctk.CTkFont(size=13, weight="bold"),
                width=col.get('width', 100),
                anchor="w",
                text_color=("#1a1a1a", "#1a1a1a"),
                cursor="hand2" if is_sortable else "arrow"  # Show clickable cursor only if sortable
            )
            label.grid(row=0, column=col_index, padx=5, pady=6, sticky="w")

            # Make column header clickable for sorting (only if sortable)
            if is_sortable:
                label.bind("<Button-1>", lambda e, key=col['key']: self._on_header_click(key))

            self.header_widgets.append(label)
            col_index += 1

    def _on_header_click(self, column_key: str):
        """Handle column header click for sorting"""
        # Cycle through: None → asc → desc → None
        if self.sort_column == column_key:
            if self.sort_direction == "asc":
                self.sort_direction = "desc"
            elif self.sort_direction == "desc":
                # Reset to original order
                self.sort_column = None
                self.sort_direction = None
        else:
            # New column, start with ascending
            self.sort_column = column_key
            self.sort_direction = "asc"

        # Apply sort
        self._sort_and_refresh()

    def _sort_and_refresh(self):
        """Sort data and refresh table"""
        if self.sort_column is None or self.sort_direction is None:
            # No sorting, use original order
            self.data_rows = self.original_data_rows.copy()
        else:
            # Sort data
            reverse = (self.sort_direction == "desc")

            try:
                # Sort by the column key
                self.data_rows = sorted(
                    self.original_data_rows,
                    key=lambda row: row.get(self.sort_column, ""),
                    reverse=reverse
                )
            except TypeError:
                # Handle cases where values can't be compared directly (e.g., None vs string)
                self.data_rows = sorted(
                    self.original_data_rows,
                    key=lambda row: str(row.get(self.sort_column, "")),
                    reverse=reverse
                )

        # Rebuild table with sorted data
        self._rebuild_table()

    def set_data(self, data: List[Dict]):
        """
        Set table data

        Args:
            data: List of row dictionaries
        """
        # Store original data order
        self.original_data_rows = data.copy()
        self.data_rows = data

        # Reset sorting state when new data is loaded
        self.sort_column = None
        self.sort_direction = None

        # Clear existing rows
        for widget in self.row_widgets:
            widget.destroy()
        self.row_widgets = []

        # Create new rows
        for index, item in enumerate(data):
            self.add_row(item, index)

        # Update scroll region
        self.inner_frame.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

        # Force another update to ensure scrollregion is applied
        self.canvas.update_idletasks()

        # Reset scroll to top-left (delayed to ensure canvas is fully updated)
        self.after(1, lambda: self.canvas.yview_moveto(0))
        self.after(1, lambda: self.canvas.xview_moveto(0))

    def add_row(self, data: Dict, index: int = 0):
        """
        Add a single row

        Args:
            data: Row data dictionary (can include '_bg_color' for custom background)
            index: Row index for alternating colors
        """
        # Check for custom background color
        if '_bg_color' in data:
            bg_color = data['_bg_color']
        else:
            # Alternating row colors
            if index % 2 == 0:
                bg_color = ("#f8f8f8", "#252525")
            else:
                bg_color = ("#ffffff", "#1e1e1e")

        row_frame = ctk.CTkFrame(
            self.inner_frame,
            fg_color=bg_color,
            corner_radius=6
        )
        row_frame.pack(fill="x", padx=2, pady=1)

        # Store data and state in row frame
        row_frame._base_color = bg_color
        row_frame._index = index
        row_frame._is_hovered = False
        self.row_data_map[row_frame] = (data, index)

        # Propagate scroll events from row to canvas
        row_frame.bind("<Enter>", lambda e, rf=row_frame: self._on_row_enter(e, rf))
        row_frame.bind("<Leave>", lambda e, rf=row_frame: self._on_row_leave(e, rf))

        # Bind click for selection and double-click for edit
        row_frame.bind("<Button-1>", lambda e, rf=row_frame: self._on_row_click(e, rf))
        row_frame.bind("<Double-Button-1>", lambda e, d=data: self._on_row_double_click(d))

        # Bind keyboard shortcuts
        self._bind_shortcuts_to_widget(row_frame)

        col_index = 0
        for col in self.columns:
            value = data.get(col['key'], '')
            original_value = str(value)

            # Format value if formatter provided
            if 'formatter' in col:
                value = col['formatter'](value)
                original_value = str(value)

            # Truncate text if needed
            truncate = col.get('truncate', True)
            displayed_value = str(value)

            if truncate:
                displayed_value = self._truncate_text(
                    str(value),
                    col.get('width', 100)
                )

            label = ctk.CTkLabel(
                row_frame,
                text=displayed_value,
                font=ctk.CTkFont(size=12),
                width=col.get('width', 100),
                anchor="w"
            )
            label.grid(row=0, column=col_index, padx=5, pady=5, sticky="w")

            # Add tooltip if text was truncated
            if truncate and displayed_value != original_value:
                ToolTip(label, original_value)

            # Propagate scroll events and hover from labels to canvas/row
            label.bind("<Enter>", lambda e, rf=row_frame: self._on_row_enter(e, rf))
            label.bind("<Leave>", lambda e, rf=row_frame: self._on_row_leave(e, rf))

            # Bind click for selection and double-click for edit
            label.bind("<Button-1>", lambda e, rf=row_frame: self._on_row_click(e, rf))
            label.bind("<Double-Button-1>", lambda e, d=data: self._on_row_double_click(d))

            # Bind keyboard shortcuts
            self._bind_shortcuts_to_widget(label)

            col_index += 1

        self.row_widgets.append(row_frame)

    def clear(self):
        """Clear all data"""
        self.data_rows = []
        self.selected_rows.clear()
        self.row_data_map.clear()
        for widget in self.row_widgets:
            widget.destroy()
        self.row_widgets = []

    def _on_row_enter(self, event, row_frame):
        """Handle mouse enter on row - show hover state"""
        # Propagate scroll events
        self._on_enter(event)

        # Update hover state
        row_frame._is_hovered = True
        index = row_frame._index
        is_selected = index in self.selected_rows
        self._update_row_color(row_frame, is_selected, is_hovered=True)

    def _on_row_leave(self, event, row_frame):
        """Handle mouse leave on row - remove hover state"""
        # Propagate scroll events
        self._on_leave(event)

        # Update hover state
        row_frame._is_hovered = False
        index = row_frame._index
        is_selected = index in self.selected_rows
        self._update_row_color(row_frame, is_selected, is_hovered=False)

    def _on_row_click(self, event, row_frame):
        """Handle single click - toggle selection or range selection with shift"""
        # Give focus to canvas so keyboard shortcuts work
        self.canvas.focus_set()

        index = row_frame._index

        # Check if shift is held
        if event.state & 0x1:  # Shift key is held
            # Range selection
            if self.last_clicked_index is not None:
                # Select all rows between last clicked and current
                start = min(self.last_clicked_index, index)
                end = max(self.last_clicked_index, index)

                # Add all rows in range to selection
                for i in range(start, end + 1):
                    self.selected_rows.add(i)

                # Update colors for all affected rows
                for rf in self.row_widgets:
                    if hasattr(rf, '_index') and rf._index in self.selected_rows:
                        is_hovered = getattr(rf, '_is_hovered', False)
                        self._update_row_color(rf, True, is_hovered=is_hovered)
            else:
                # No previous click, just select this one
                self.selected_rows.add(index)
                is_selected = index in self.selected_rows
                self._update_row_color(row_frame, is_selected, is_hovered=row_frame._is_hovered)
        else:
            # Normal toggle selection
            if index in self.selected_rows:
                self.selected_rows.remove(index)
            else:
                self.selected_rows.add(index)

            # Update row color
            is_selected = index in self.selected_rows
            self._update_row_color(row_frame, is_selected, is_hovered=row_frame._is_hovered)

        # Update last clicked index
        self.last_clicked_index = index

        # Notify callback
        if self.on_selection_change:
            selected_data = self.get_selected_data()
            self.on_selection_change(selected_data)

    def _on_row_double_click(self, data: Dict):
        """Handle double click - open for edit"""
        if self.on_row_double_click:
            self.on_row_double_click(data)

    def _update_row_color(self, row_frame, is_selected: bool, is_hovered: bool = False):
        """Update row color based on selection and hover state"""
        base_color = row_frame._base_color

        if is_selected:
            # Saturate color significantly for selected state (more obvious)
            if isinstance(base_color, tuple):
                light_color = self._saturate_color(base_color[0])
                dark_color = self._saturate_color(base_color[1])
                row_frame.configure(fg_color=(light_color, dark_color))
            else:
                row_frame.configure(fg_color=self._saturate_color(base_color))
        elif is_hovered:
            # Darken slightly for hover state (clickable indication)
            if isinstance(base_color, tuple):
                light_color = self._darken_color(base_color[0])
                dark_color = self._darken_color(base_color[1])
                row_frame.configure(fg_color=(light_color, dark_color))
            else:
                row_frame.configure(fg_color=self._darken_color(base_color))
        else:
            # Restore base color
            row_frame.configure(fg_color=base_color)

    def _darken_color(self, hex_color: str, factor: float = 0.85) -> str:
        """Darken a hex color by a factor"""
        # Remove # if present
        hex_color = hex_color.lstrip('#')

        # Convert to RGB
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)

        # Darken
        r = int(r * factor)
        g = int(g * factor)
        b = int(b * factor)

        # Convert back to hex
        return f"#{r:02x}{g:02x}{b:02x}"

    def _saturate_color(self, hex_color: str) -> str:
        """Saturate a hex color to make it more vivid/obvious for selection"""
        # Remove # if present
        hex_color = hex_color.lstrip('#')

        # Convert to RGB
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)

        # Find the dominant color and boost it
        max_val = max(r, g, b)
        min_val = min(r, g, b)

        # If already saturated or neutral, slightly darken instead
        if max_val - min_val < 30:
            # Neutral color (gray-ish), just darken it more
            r = int(r * 0.7)
            g = int(g * 0.7)
            b = int(b * 0.7)
        else:
            # Boost saturation: push high values higher, low values lower
            # This makes the color more vivid
            factor = 1.3
            if r == max_val:
                r = min(255, int(r * factor))
                g = int(g * 0.8)
                b = int(b * 0.8)
            elif g == max_val:
                g = min(255, int(g * factor))
                r = int(r * 0.8)
                b = int(b * 0.8)
            else:  # b == max_val
                b = min(255, int(b * factor))
                r = int(r * 0.8)
                g = int(g * 0.8)

        # Convert back to hex
        return f"#{r:02x}{g:02x}{b:02x}"

    def get_selected_data(self) -> List[Dict]:
        """Get data for all selected rows"""
        selected_data = []
        for row_frame in self.row_widgets:
            if hasattr(row_frame, '_index') and row_frame._index in self.selected_rows:
                if row_frame in self.row_data_map:
                    data, _ = self.row_data_map[row_frame]
                    selected_data.append(data)
        return selected_data

    def clear_selection(self):
        """Clear all selected rows"""
        for row_frame in self.row_widgets:
            if hasattr(row_frame, '_index') and row_frame._index in self.selected_rows:
                is_hovered = getattr(row_frame, '_is_hovered', False)
                self._update_row_color(row_frame, False, is_hovered=is_hovered)
        self.selected_rows.clear()

        # Notify callback
        if self.on_selection_change:
            self.on_selection_change([])

    def destroy(self):
        """Clean up before destroying"""
        # Unbind all scroll events to avoid memory leaks
        self._on_leave(None)
        super().destroy()
