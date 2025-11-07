# -*- coding: utf-8 -*-
"""
Componente de Tabela V2 com scroll horizontal e vertical
Resolve problemas de overflow e scroll do DataTable original
"""
import customtkinter as ctk
import platform
from typing import List, Dict, Callable, Optional


class DataTableV2(ctk.CTkFrame):
    """
    Tabela de dados com scroll horizontal + vertical nativo
    API compatível com DataTable original
    """

    def __init__(
        self,
        parent,
        columns: List[Dict],  # [{'key': 'nome', 'label': 'Nome', 'width': 200}]
        on_edit: Optional[Callable] = None,
        on_delete: Optional[Callable] = None,
        on_view: Optional[Callable] = None,
        height: int = 400,
        **kwargs
    ):
        """
        Initialize data table V2

        Args:
            parent: Parent widget
            columns: List of column definitions
            on_edit: Callback for edit action (receives row data)
            on_delete: Callback for delete action (receives row data)
            on_view: Callback for view action (receives row data)
            height: Table height in pixels
        """
        super().__init__(parent, **kwargs)

        self.columns = columns
        self.on_edit = on_edit
        self.on_delete = on_delete
        self.on_view = on_view
        self.data_rows = []
        self.row_widgets = []

        # Configure
        self.configure(fg_color="transparent")

        # Add actions column if needed
        self.has_actions = bool(on_view or on_edit or on_delete)

        # Calculate total width needed for horizontal scroll
        self.table_width = self._calculate_table_width()

        # Create main container
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Create canvas for scrolling
        self.canvas = ctk.CTkCanvas(self, highlightthickness=0)
        self.canvas.grid(row=0, column=0, sticky="nsew")

        # Create scrollbars
        self.v_scrollbar = ctk.CTkScrollbar(self, orientation="vertical", command=self.canvas.yview)
        self.v_scrollbar.grid(row=0, column=1, sticky="ns")

        self.h_scrollbar = ctk.CTkScrollbar(self, orientation="horizontal", command=self.canvas.xview)
        self.h_scrollbar.grid(row=1, column=0, sticky="ew")

        # Configure canvas
        self.canvas.configure(
            yscrollcommand=self.v_scrollbar.set,
            xscrollcommand=self.h_scrollbar.set
        )

        # Create inner frame for content with fixed width
        self.inner_frame = ctk.CTkFrame(self.canvas, fg_color="transparent", width=self.table_width)
        self.canvas_window = self.canvas.create_window((0, 0), window=self.inner_frame, anchor="nw")

        # Bind events
        self.inner_frame.bind("<Configure>", self._on_frame_configure)
        self.bind("<Enter>", self._bind_mouse_scroll)
        self.bind("<Leave>", self._unbind_mouse_scroll)

        # Create header
        self.create_header()

    def _calculate_table_width(self) -> int:
        """Calculate total width needed for all columns"""
        total = sum(col.get('width', 100) + 20 for col in self.columns)  # +20 for padding
        if self.has_actions:
            total += 180 if self.on_view else 120
        return total + 10  # +10 for margins

    def _bind_mouse_scroll(self, event):
        """Bind mouse scroll events when mouse enters widget"""
        # Detect OS for appropriate scroll binding
        system = platform.system()

        if system == "Darwin":  # macOS
            self.canvas.bind_all("<MouseWheel>", self._on_mousewheel_mac)
        elif system == "Linux":
            self.canvas.bind_all("<Button-4>", self._on_mousewheel_linux)
            self.canvas.bind_all("<Button-5>", self._on_mousewheel_linux)
        else:  # Windows
            self.canvas.bind_all("<MouseWheel>", self._on_mousewheel_windows)

    def _unbind_mouse_scroll(self, event):
        """Unbind mouse scroll events when mouse leaves widget"""
        system = platform.system()

        if system == "Darwin":
            self.canvas.unbind_all("<MouseWheel>")
        elif system == "Linux":
            self.canvas.unbind_all("<Button-4>")
            self.canvas.unbind_all("<Button-5>")
        else:
            self.canvas.unbind_all("<MouseWheel>")

    def _on_mousewheel_mac(self, event):
        """Handle mouse wheel scrolling on macOS"""
        self.canvas.yview_scroll(int(-1 * event.delta), "units")

    def _on_mousewheel_windows(self, event):
        """Handle mouse wheel scrolling on Windows"""
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _on_mousewheel_linux(self, event):
        """Handle mouse wheel scrolling on Linux"""
        if event.num == 4:
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5:
            self.canvas.yview_scroll(1, "units")

    def _on_frame_configure(self, event=None):
        """Update scroll region when frame changes"""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def create_header(self):
        """Create table header"""
        header_frame = ctk.CTkFrame(
            self.inner_frame,
            fg_color=("#efd578", "#d4bb5e"),
            corner_radius=8
        )
        header_frame.pack(fill="x", padx=5, pady=(5, 10))

        col_index = 0
        for col in self.columns:
            label = ctk.CTkLabel(
                header_frame,
                text=col['label'],
                font=ctk.CTkFont(size=13, weight="bold"),
                width=col.get('width', 100),
                anchor="w",
                text_color=("#1a1a1a", "#1a1a1a")
            )
            label.grid(row=0, column=col_index, padx=10, pady=12, sticky="w")
            col_index += 1

        # Actions column
        if self.has_actions:
            width = 180 if self.on_view else 120
            label = ctk.CTkLabel(
                header_frame,
                text="Ações",
                font=ctk.CTkFont(size=13, weight="bold"),
                width=width,
                anchor="center",
                text_color=("#1a1a1a", "#1a1a1a")
            )
            label.grid(row=0, column=col_index, padx=10, pady=12)

    def set_data(self, data: List[Dict]):
        """
        Set table data

        Args:
            data: List of row dictionaries
        """
        self.data_rows = data

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

    def add_row(self, data: Dict, index: int = 0):
        """
        Add a single row

        Args:
            data: Row data dictionary
            index: Row index for alternating colors
        """
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
        row_frame.pack(fill="x", padx=5, pady=3)

        col_index = 0
        for col in self.columns:
            value = data.get(col['key'], '')

            # Format value if formatter provided
            if 'formatter' in col:
                value = col['formatter'](value)

            label = ctk.CTkLabel(
                row_frame,
                text=str(value),
                font=ctk.CTkFont(size=12),
                width=col.get('width', 100),
                anchor="w"
            )
            label.grid(row=0, column=col_index, padx=10, pady=10, sticky="w")
            col_index += 1

        # Actions buttons
        if self.has_actions:
            actions_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
            actions_frame.grid(row=0, column=col_index, padx=10, pady=5)

            if self.on_view:
                view_btn = ctk.CTkButton(
                    actions_frame,
                    text="👁️",
                    command=lambda d=data: self.on_view(d),
                    width=50,
                    height=30,
                    font=ctk.CTkFont(size=14),
                    fg_color=("#2196F3", "#1565C0"),
                    hover_color=("#1976D2", "#0D47A1")
                )
                view_btn.pack(side="left", padx=2)

            if self.on_edit:
                edit_btn = ctk.CTkButton(
                    actions_frame,
                    text="✏️",
                    command=lambda d=data: self.on_edit(d),
                    width=50,
                    height=30,
                    font=ctk.CTkFont(size=14)
                )
                edit_btn.pack(side="left", padx=2)

            if self.on_delete:
                delete_btn = ctk.CTkButton(
                    actions_frame,
                    text="🗑️",
                    command=lambda d=data: self.on_delete(d),
                    width=50,
                    height=30,
                    font=ctk.CTkFont(size=14),
                    fg_color=("#F44336", "#C62828"),
                    hover_color=("#E53935", "#B71C1C")
                )
                delete_btn.pack(side="left", padx=2)

        self.row_widgets.append(row_frame)

    def clear(self):
        """Clear all data"""
        self.data_rows = []
        for widget in self.row_widgets:
            widget.destroy()
        self.row_widgets = []

    def destroy(self):
        """Clean up before destroying"""
        # Unbind mousewheel to avoid memory leaks
        self._unbind_mouse_scroll(None)
        super().destroy()
