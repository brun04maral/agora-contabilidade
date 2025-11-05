# -*- coding: utf-8 -*-
"""
Componente de Tabela V2 usando CTkTable
Resolve problemas de scroll horizontal + vertical
"""
import customtkinter as ctk
from CTkTable import CTkTable
from typing import List, Dict, Callable, Optional


class DataTableV2(ctk.CTkFrame):
    """
    Tabela de dados usando CTkTable com scroll nativo
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
        self.data_rows = []  # Store original data
        self.table_widget = None

        # Configure
        self.configure(fg_color="transparent")

        # Create container for table + scrollbars
        self.table_container = ctk.CTkFrame(self, fg_color="transparent")
        self.table_container.pack(fill="both", expand=True)

        # Add actions column if needed
        self.has_actions = bool(on_view or on_edit or on_delete)

        # Initialize with empty table
        self.create_empty_table()

    def create_empty_table(self):
        """Create empty table with just headers"""
        # Create header row
        headers = [col['label'] for col in self.columns]
        if self.has_actions:
            headers.append("Ações")

        # Create table with just headers
        values = [headers]

        self.table_widget = CTkTable(
            self.table_container,
            values=values,
            header_color=("#efd578", "#d4bb5e"),
            hover_color=("#B0BEC5", "#4A4A4A"),
            corner_radius=8,
            colors=[("#f8f8f8", "#252525"), ("#ffffff", "#1e1e1e")]  # Alternating colors
        )
        self.table_widget.pack(fill="both", expand=True, padx=5, pady=5)

    def set_data(self, data: List[Dict]):
        """
        Set table data

        Args:
            data: List of row dictionaries
        """
        self.data_rows = data

        # Destroy old table
        if self.table_widget:
            self.table_widget.destroy()

        # If no data, show empty message
        if not data:
            self.create_empty_table()
            return

        # Build table values (header + rows)
        headers = [col['label'] for col in self.columns]
        if self.has_actions:
            headers.append("Ações")

        values = [headers]

        # Add data rows
        for row_index, item in enumerate(data):
            row = []

            # Add data columns
            for col in self.columns:
                value = item.get(col['key'], '')

                # Format value if formatter provided
                if 'formatter' in col:
                    value = col['formatter'](value)

                row.append(str(value))

            # Placeholder for actions (we'll add buttons separately)
            if self.has_actions:
                row.append("")

            values.append(row)

        # Create table
        self.table_widget = CTkTable(
            self.table_container,
            values=values,
            header_color=("#efd578", "#d4bb5e"),
            hover_color=("#B0BEC5", "#4A4A4A"),
            corner_radius=8,
            colors=[("#f8f8f8", "#252525"), ("#ffffff", "#1e1e1e")]
        )
        self.table_widget.pack(fill="both", expand=True, padx=5, pady=5)

        # Add action buttons if needed
        if self.has_actions:
            self.add_action_buttons()

    def add_action_buttons(self):
        """Add action buttons to each row"""
        # Get the actions column index (last column)
        actions_col = len(self.columns)

        # Add buttons for each data row (skip header row 0)
        for row_index, row_data in enumerate(self.data_rows):
            # row_index in data_rows, but row_index + 1 in table (because of header)
            table_row = row_index + 1

            # Create frame for buttons
            actions_frame = ctk.CTkFrame(
                self.table_widget.frame,  # Access internal frame
                fg_color="transparent"
            )

            # Position frame in the cell
            # We need to access the internal structure of CTkTable
            # CTkTable creates labels in a grid, we'll overlay our buttons

            # Get the cell widget and replace with our frame
            # This is a bit hacky but works with CTkTable 1.1
            cell_frame = actions_frame

            button_width = 40
            button_height = 28

            if self.on_view:
                view_btn = ctk.CTkButton(
                    cell_frame,
                    text="👁️",
                    command=lambda d=row_data: self.on_view(d),
                    width=button_width,
                    height=button_height,
                    font=ctk.CTkFont(size=12),
                    fg_color=("#2196F3", "#1565C0"),
                    hover_color=("#1976D2", "#0D47A1")
                )
                view_btn.pack(side="left", padx=2)

            if self.on_edit:
                edit_btn = ctk.CTkButton(
                    cell_frame,
                    text="✏️",
                    command=lambda d=row_data: self.on_edit(d),
                    width=button_width,
                    height=button_height,
                    font=ctk.CTkFont(size=12)
                )
                edit_btn.pack(side="left", padx=2)

            if self.on_delete:
                delete_btn = ctk.CTkButton(
                    cell_frame,
                    text="🗑️",
                    command=lambda d=row_data: self.on_delete(d),
                    width=button_width,
                    height=button_height,
                    font=ctk.CTkFont(size=12),
                    fg_color=("#F44336", "#C62828"),
                    hover_color=("#E53935", "#B71C1C")
                )
                delete_btn.pack(side="left", padx=2)

            # Replace the cell content with our frame
            # Access the label at position [table_row, actions_col]
            try:
                # CTkTable stores cells in a 2D structure
                old_widget = self.table_widget.frame.grid_slaves(row=table_row, column=actions_col)[0]
                old_widget.destroy()
                cell_frame.grid(row=table_row, column=actions_col, padx=5, pady=3)
            except (IndexError, AttributeError):
                # Fallback: just grid the frame
                cell_frame.grid(row=table_row, column=actions_col, padx=5, pady=3, sticky="nsew")

    def clear(self):
        """Clear all data"""
        self.data_rows = []
        if self.table_widget:
            self.table_widget.destroy()
        self.create_empty_table()
