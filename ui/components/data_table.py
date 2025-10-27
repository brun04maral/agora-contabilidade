# -*- coding: utf-8 -*-
"""
Componente de Tabela reutilizável para listagens
"""
import customtkinter as ctk
from typing import List, Dict, Callable, Optional


class DataTable(ctk.CTkScrollableFrame):
    """
    Tabela de dados reutilizável com suporte a ações
    """

    def __init__(
        self,
        parent,
        columns: List[Dict],  # [{'key': 'nome', 'label': 'Nome', 'width': 200}]
        on_edit: Optional[Callable] = None,
        on_delete: Optional[Callable] = None,
        **kwargs
    ):
        """
        Initialize data table

        Args:
            parent: Parent widget
            columns: List of column definitions
            on_edit: Callback for edit action (receives row data)
            on_delete: Callback for delete action (receives row data)
        """
        super().__init__(parent, **kwargs)

        self.columns = columns
        self.on_edit = on_edit
        self.on_delete = on_delete
        self.rows = []

        # Configure
        self.configure(fg_color="transparent")

        # Create header
        self.create_header()

    def create_header(self):
        """Create table header"""
        header_frame = ctk.CTkFrame(self, fg_color=("#E0E0E0", "#2a2a2a"))
        header_frame.pack(fill="x", padx=5, pady=(5, 0))

        # Configure columns
        total_width = sum(col.get('width', 100) for col in self.columns)
        if self.on_edit or self.on_delete:
            total_width += 120  # Actions column

        col_index = 0
        for col in self.columns:
            label = ctk.CTkLabel(
                header_frame,
                text=col['label'],
                font=ctk.CTkFont(size=12, weight="bold"),
                width=col.get('width', 100),
                anchor="w"
            )
            label.grid(row=0, column=col_index, padx=10, pady=10, sticky="w")
            col_index += 1

        # Actions column
        if self.on_edit or self.on_delete:
            label = ctk.CTkLabel(
                header_frame,
                text="Ações",
                font=ctk.CTkFont(size=12, weight="bold"),
                width=120,
                anchor="center"
            )
            label.grid(row=0, column=col_index, padx=10, pady=10)

    def set_data(self, data: List[Dict]):
        """
        Set table data

        Args:
            data: List of row dictionaries
        """
        # Clear existing rows
        for row in self.rows:
            row.destroy()
        self.rows = []

        # Create new rows
        for item in data:
            self.add_row(item)

    def add_row(self, data: Dict):
        """
        Add a single row

        Args:
            data: Row data dictionary
        """
        row_frame = ctk.CTkFrame(
            self,
            fg_color=("white", "#1e1e1e"),
            corner_radius=5
        )
        row_frame.pack(fill="x", padx=5, pady=2)

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
        if self.on_edit or self.on_delete:
            actions_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
            actions_frame.grid(row=0, column=col_index, padx=10, pady=5)

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

        self.rows.append(row_frame)

    def clear(self):
        """Clear all rows"""
        for row in self.rows:
            row.destroy()
        self.rows = []
