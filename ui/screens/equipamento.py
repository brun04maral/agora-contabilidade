# -*- coding: utf-8 -*-
"""
Tela de Equipamento - Gestão de equipamento da Agora Media
"""
import customtkinter as ctk
from sqlalchemy.orm import Session
from logic.equipamento import EquipamentoManager
from ui.components.data_table_v2 import DataTableV2
from tkinter import messagebox
from assets.resources import get_icon, EQUIPAMENTO


class EquipamentoScreen(ctk.CTkFrame):
    """
    Tela de gestão de Equipamento
    """

    def __init__(self, parent, db_session: Session, **kwargs):
        """
        Initialize equipamento screen

        Args:
            parent: Parent widget
            db_session: SQLAlchemy database session
        """
        super().__init__(parent, **kwargs)

        self.db_session = db_session
        self.manager = EquipamentoManager(db_session)

        # Configure
        self.configure(fg_color="transparent")

        # Create widgets
        self.create_widgets()

        # Load data
        self.carregar_equipamentos()

    def create_widgets(self):
        """Create screen widgets"""

        # Header
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=30, pady=(30, 20))

        # Title with PNG icon
        icon_pil = get_icon(EQUIPAMENTO, size=(28, 28))
        if icon_pil:
            icon_ctk = ctk.CTkImage(
                light_image=icon_pil,
                dark_image=icon_pil,
                size=(28, 28)
            )
            title_label = ctk.CTkLabel(
                header_frame,
                image=icon_ctk,
                text=" Equipamento",
                compound="left",
                font=ctk.CTkFont(size=28, weight="bold")
            )
        else:
            title_label = ctk.CTkLabel(
                header_frame,
                text="💻 Equipamento",
                font=ctk.CTkFont(size=28, weight="bold")
            )
        title_label.pack(side="left")

        # Buttons
        button_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        button_frame.pack(side="right")

        refresh_btn = ctk.CTkButton(
            button_frame,
            text="🔄 Atualizar",
            command=self.carregar_equipamentos,
            width=120,
            height=35,
            font=ctk.CTkFont(size=13)
        )
        refresh_btn.pack(side="left", padx=(0, 10))

        add_btn = ctk.CTkButton(
            button_frame,
            text="➕ Novo Equipamento",
            command=self.adicionar_equipamento,
            width=160,
            height=35,
            font=ctk.CTkFont(size=13),
            fg_color=("#2196F3", "#1565C0"),
            hover_color=("#1976D2", "#0D47A1")
        )
        add_btn.pack(side="left")

        # Filters
        filter_frame = ctk.CTkFrame(self, fg_color="transparent")
        filter_frame.pack(fill="x", padx=30, pady=(0, 20))

        # Search box
        ctk.CTkLabel(
            filter_frame,
            text="Pesquisar:",
            font=ctk.CTkFont(size=13)
        ).pack(side="left", padx=(0, 10))

        self.search_entry = ctk.CTkEntry(
            filter_frame,
            placeholder_text="Produto, ID ou Descrição...",
            width=300,
            height=35
        )
        self.search_entry.pack(side="left", padx=(0, 20))
        self.search_entry.bind("<KeyRelease>", lambda e: self.carregar_equipamentos())

        # Tipo filter
        ctk.CTkLabel(
            filter_frame,
            text="Tipo:",
            font=ctk.CTkFont(size=13)
        ).pack(side="left", padx=(0, 10))

        self.tipo_var = ctk.StringVar(value="Todos")
        self.tipo_dropdown = ctk.CTkOptionMenu(
            filter_frame,
            variable=self.tipo_var,
            values=self.manager.obter_tipos(),
            command=lambda x: self.carregar_equipamentos(),
            width=150,
            height=35
        )
        self.tipo_dropdown.pack(side="left", padx=(0, 20))

        # Com aluguer checkbox
        self.aluguer_var = ctk.BooleanVar(value=False)
        aluguer_check = ctk.CTkCheckBox(
            filter_frame,
            text="Apenas com preço de aluguer",
            variable=self.aluguer_var,
            command=self.carregar_equipamentos,
            font=ctk.CTkFont(size=13)
        )
        aluguer_check.pack(side="left", padx=(0, 10))

        # Table container
        table_container = ctk.CTkFrame(self, fg_color="transparent")
        table_container.pack(fill="both", expand=True, padx=30, pady=(0, 30))

        # DataTable
        self.table = DataTableV2(
            table_container,
            columns=[
                {"key": "numero", "label": "ID", "width": 100},
                {"key": "produto", "label": "Produto", "width": 250},
                {"key": "tipo", "label": "Tipo", "width": 120},
                {"key": "valor_compra", "label": "Valor Compra", "width": 130},
                {"key": "preco_aluguer", "label": "Preço Aluguer/dia", "width": 150},
                {"key": "quantidade", "label": "Qtd", "width": 80},
                {"key": "estado", "label": "Estado", "width": 120},
                {"key": "fornecedor", "label": "Fornecedor", "width": 150},
            ],
            height=500,
            on_selection_change=self.on_selection_changed,
            on_row_double_click=self.editar_equipamento_duplo_clique
        )
        self.table.pack(fill="both", expand=True)

        # Action buttons
        action_frame = ctk.CTkFrame(self, fg_color="transparent")
        action_frame.pack(fill="x", padx=30, pady=(10, 30))

        self.edit_btn = ctk.CTkButton(
            action_frame,
            text="✏️ Editar",
            command=self.editar_equipamento,
            width=120,
            height=35,
            state="disabled"
        )
        self.edit_btn.pack(side="left", padx=(0, 10))

        self.delete_btn = ctk.CTkButton(
            action_frame,
            text="🗑️ Eliminar",
            command=self.eliminar_equipamento,
            width=120,
            height=35,
            state="disabled",
            fg_color=("#D32F2F", "#B71C1C"),
            hover_color=("#C62828", "#A31515")
        )
        self.delete_btn.pack(side="left")

        # Info label
        self.info_label = ctk.CTkLabel(
            action_frame,
            text="",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.info_label.pack(side="right", padx=20)

    def carregar_equipamentos(self):
        """Carrega equipamentos com filtros aplicados"""
        # Get filters
        pesquisa = self.search_entry.get().strip() or None
        filtro_tipo = self.tipo_var.get() if self.tipo_var.get() != "Todos" else None
        filtro_com_aluguer = self.aluguer_var.get()

        # Query
        equipamentos = self.manager.listar_equipamentos(
            filtro_tipo=filtro_tipo,
            filtro_com_aluguer=filtro_com_aluguer,
            pesquisa=pesquisa
        )

        # Format data
        data = []
        for eq in equipamentos:
            data.append({
                "id": eq.id,
                "numero": eq.numero,
                "produto": eq.produto or "-",
                "tipo": eq.tipo or "-",
                "valor_compra": f"€{float(eq.valor_compra or 0):,.2f}",
                "preco_aluguer": f"€{float(eq.preco_aluguer or 0):,.2f}" if eq.preco_aluguer else "-",
                "quantidade": str(eq.quantidade or 1),
                "estado": eq.estado or "-",
                "fornecedor": eq.fornecedor or "-",
            })

        # Update table
        self.table.set_data(data)

        # Update info
        stats = self.manager.estatisticas()
        self.info_label.configure(
            text=f"Total: {len(equipamentos)} equipamentos | "
                 f"Investimento total: €{stats['valor_total_investido']:,.2f} | "
                 f"Com aluguer: {stats['com_preco_aluguer']}"
        )

    def on_selection_changed(self, selected_rows):
        """Handle selection change"""
        has_selection = len(selected_rows) > 0
        single_selection = len(selected_rows) == 1

        self.edit_btn.configure(state="normal" if single_selection else "disabled")
        self.delete_btn.configure(state="normal" if has_selection else "disabled")

    def adicionar_equipamento(self):
        """Navigate to equipamento_form screen for create"""
        main_window = self.master.master
        if hasattr(main_window, 'show_screen'):
            main_window.show_screen("equipamento_form", equipamento_id=None)
        else:
            messagebox.showerror("Erro", "Não foi possível abrir formulário")

    def editar_equipamento_duplo_clique(self, row_data):
        """Navigate to equipamento_form screen for edit (double-click)"""
        equipamento_id = row_data["id"]
        main_window = self.master.master
        if hasattr(main_window, 'show_screen'):
            main_window.show_screen("equipamento_form", equipamento_id=equipamento_id)
        else:
            messagebox.showerror("Erro", "Não foi possível abrir formulário")

    def editar_equipamento(self):
        """Navigate to equipamento_form screen for edit (button)"""
        selected = self.table.get_selected_data()
        if len(selected) != 1:
            return

        self.editar_equipamento_duplo_clique(selected[0])

    def eliminar_equipamento(self):
        """Elimina equipamentos selecionados"""
        selected = self.table.get_selected_data()
        if not selected:
            return

        # Confirm
        response = messagebox.askyesno(
            "Confirmar",
            f"Tem certeza que deseja eliminar {len(selected)} equipamento(s)?\n\n"
            "Esta ação não pode ser desfeita."
        )

        if not response:
            return

        # Delete
        erros = 0
        for row in selected:
            sucesso, erro = self.manager.eliminar_equipamento(row["id"])
            if not sucesso:
                erros += 1

        if erros > 0:
            messagebox.showwarning(
                "Aviso",
                f"{len(selected) - erros} equipamento(s) eliminado(s)\n"
                f"{erros} erro(s)"
            )

        self.carregar_equipamentos()

