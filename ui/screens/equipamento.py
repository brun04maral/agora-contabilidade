# -*- coding: utf-8 -*-
"""
Tela de Equipamento - Gestão de equipamento da Agora Media
"""
import customtkinter as ctk
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from logic.equipamento import EquipamentoManager
from ui.components.base_screen import BaseScreen
from tkinter import messagebox
from assets.resources import get_icon, EQUIPAMENTO


class EquipamentoScreen(BaseScreen):
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
        self.db_session = db_session
        self.manager = EquipamentoManager(db_session)

        # Initialize filter widgets (created in toolbar_slot)
        self.search_entry = None
        self.tipo_var = None
        self.tipo_dropdown = None
        self.aluguer_var = None
        self.info_label = None  # Created in footer_slot

        # Call parent __init__ (this will call abstract methods)
        super().__init__(parent, db_session, **kwargs)

    # ===== ABSTRACT METHODS FROM BaseScreen =====

    def get_screen_title(self) -> str:
        """Return screen title"""
        return "Equipamento"

    def get_screen_icon(self):
        """Return screen icon (PIL Image or None)"""
        return get_icon(EQUIPAMENTO, size=(28, 28))

    def get_table_columns(self) -> List[Dict[str, Any]]:
        """Return table column definitions"""
        return [
            {"key": "numero", "label": "ID", "width": 100, 'sortable': True},
            {"key": "produto", "label": "Produto", "width": 250, 'sortable': True},
            {"key": "tipo", "label": "Tipo", "width": 120, 'sortable': True},
            {"key": "valor_compra", "label": "Valor Compra", "width": 130, 'sortable': True},
            {"key": "preco_aluguer", "label": "Preço Aluguer/dia", "width": 150, 'sortable': True},
            {"key": "quantidade", "label": "Qtd", "width": 80, 'sortable': True},
            {"key": "estado", "label": "Estado", "width": 120, 'sortable': True},
            {"key": "fornecedor", "label": "Fornecedor", "width": 150, 'sortable': True},
        ]

    def load_data(self) -> List[Any]:
        """Load equipamentos from database and return as list of objects"""
        try:
            # Get search filter (widget pode não existir em __init__)
            pesquisa = None
            if hasattr(self, 'search_entry') and self.search_entry:
                try:
                    pesquisa = self.search_entry.get().strip() or None
                except Exception:
                    pass

            # Get tipo filter
            filtro_tipo = None
            if hasattr(self, 'tipo_var') and self.tipo_var:
                try:
                    tipo_value = self.tipo_var.get()
                    if tipo_value != "Todos":
                        filtro_tipo = tipo_value
                except Exception:
                    pass

            # Get aluguer filter
            filtro_com_aluguer = False
            if hasattr(self, 'aluguer_var') and self.aluguer_var:
                try:
                    filtro_com_aluguer = self.aluguer_var.get()
                except Exception:
                    pass

            # Query
            equipamentos = self.manager.listar_equipamentos(
                filtro_tipo=filtro_tipo,
                filtro_com_aluguer=filtro_com_aluguer,
                pesquisa=pesquisa
            )

            # Update info label with statistics
            if hasattr(self, 'info_label') and self.info_label:
                try:
                    stats = self.manager.estatisticas()
                    self.info_label.configure(
                        text=f"Total: {len(equipamentos)} equipamentos | "
                             f"Investimento total: €{stats['valor_total_investido']:,.2f} | "
                             f"Com aluguer: {stats['com_preco_aluguer']}"
                    )
                except Exception:
                    pass

            return equipamentos  # NUNCA None, sempre lista

        except Exception as e:
            print(f"ERROR in load_data(): {e}")
            import traceback
            traceback.print_exc()
            return []  # SEMPRE retornar lista vazia em erro

    def item_to_dict(self, item: Any) -> Dict[str, Any]:
        """Convert equipamento object to dict for table"""
        return {
            'id': item.id,
            'numero': item.numero,
            'produto': item.produto or '-',
            'tipo': item.tipo or '-',
            'valor_compra': f"€{float(item.valor_compra or 0):,.2f}",
            'preco_aluguer': f"€{float(item.preco_aluguer or 0):,.2f}" if item.preco_aluguer else '-',
            'quantidade': str(item.quantidade or 1),
            'estado': item.estado or '-',
            'fornecedor': item.fornecedor or '-',
            '_equipamento': item  # CRÍTICO: guardar objeto original
        }

    def get_context_menu_items(self, data: dict) -> List[Dict[str, Any]]:
        """Define ações do context menu e barra de ações"""

        # Para barra de ações (data vazio {} quando BaseScreen chama)
        if not data or '_equipamento' not in data:
            return [
                {
                    'label': '✏️ Editar',
                    'command': self._editar_selecionado,
                    'min_selection': 1,
                    'max_selection': 1,
                    'fg_color': ('#2196F3', '#1976D2'),
                    'hover_color': ('#1976D2', '#1565C0'),
                    'width': 100
                },
                {
                    'label': '🗑️ Eliminar',
                    'command': self._eliminar_selecionados,
                    'min_selection': 1,
                    'max_selection': None,
                    'fg_color': ('#F44336', '#C62828'),
                    'hover_color': ('#D32F2F', '#B71C1C'),
                    'width': 120
                }
            ]

        # Para context menu (ações contextuais simples)
        equipamento = data.get('_equipamento')
        if not equipamento:
            return []

        return [
            {'label': '✏️ Editar', 'command': lambda: self._editar_from_context(equipamento)},
            {'separator': True},
            {'label': '🗑️ Eliminar', 'command': lambda: self._eliminar_from_context(equipamento)}
        ]

    # ===== OPTIONAL METHODS =====

    def toolbar_slot(self, parent):
        """Create custom toolbar with search, tipo filter, and aluguer checkbox"""
        # Frame principal
        toolbar_frame = ctk.CTkFrame(parent, fg_color="transparent")
        toolbar_frame.pack(fill="x", padx=0, pady=(0, 10))

        # Search box
        ctk.CTkLabel(
            toolbar_frame,
            text="Pesquisar:",
            font=ctk.CTkFont(size=13)
        ).pack(side="left", padx=(0, 10))

        self.search_entry = ctk.CTkEntry(
            toolbar_frame,
            placeholder_text="Produto, ID ou Descrição...",
            width=300,
            height=35
        )
        self.search_entry.pack(side="left", padx=(0, 20))
        self.search_entry.bind("<KeyRelease>", lambda e: self.refresh_data())

        # Tipo filter
        ctk.CTkLabel(
            toolbar_frame,
            text="Tipo:",
            font=ctk.CTkFont(size=13)
        ).pack(side="left", padx=(0, 10))

        self.tipo_var = ctk.StringVar(value="Todos")
        self.tipo_dropdown = ctk.CTkOptionMenu(
            toolbar_frame,
            variable=self.tipo_var,
            values=self.manager.obter_tipos(),
            command=lambda x: self.refresh_data(),
            width=150,
            height=35
        )
        self.tipo_dropdown.pack(side="left", padx=(0, 20))

        # Com aluguer checkbox
        self.aluguer_var = ctk.BooleanVar(value=False)
        aluguer_check = ctk.CTkCheckBox(
            toolbar_frame,
            text="Apenas com preço de aluguer",
            variable=self.aluguer_var,
            command=self.refresh_data,
            font=ctk.CTkFont(size=13)
        )
        aluguer_check.pack(side="left", padx=(0, 10))

    def footer_slot(self, parent):
        """Create custom footer with info label for statistics"""
        self.info_label = ctk.CTkLabel(
            parent,
            text="",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.info_label.pack(pady=(10, 0))

    def on_add_click(self):
        """Handle add button click"""
        self.adicionar_equipamento()

    def on_item_double_click(self, data: dict):
        """Handle table row double-click (editar)"""
        equipamento_id = data.get('id')
        if equipamento_id:
            self.editar_equipamento_by_id(equipamento_id)

    def calculate_selection_total(self, selected_data: List[Dict[str, Any]]) -> float:
        """Return total investment of selected equipamentos"""
        total = 0.0
        for item in selected_data:
            equipamento = item.get('_equipamento')
            if equipamento and equipamento.valor_compra:
                total += float(equipamento.valor_compra)
        return total

    # ===== BULK OPERATION METHODS FOR ACTION BAR =====

    def _editar_selecionado(self):
        """Edita equipamento selecionado"""
        selected = self.get_selected_data()
        if selected and len(selected) == 1:
            self.on_item_double_click(selected[0])

    def _eliminar_selecionados(self):
        """Elimina equipamentos selecionados"""
        selected = self.get_selected_data()
        if not selected:
            return

        num = len(selected)

        # Confirmar
        resposta = messagebox.askyesno(
            "Confirmar Eliminação",
            f"Tem certeza que deseja eliminar {num} equipamento(s)?\n\n"
            f"Esta ação não pode ser desfeita."
        )

        if not resposta:
            return

        sucessos = 0
        erros = []

        for data in selected:
            equipamento = data.get('_equipamento')
            if equipamento:
                sucesso, erro = self.manager.eliminar_equipamento(equipamento.id)
                if sucesso:
                    sucessos += 1
                else:
                    erros.append(f"{equipamento.numero}: {erro}")

        if sucessos > 0:
            msg = f"✅ {sucessos} equipamento(s) eliminado(s)!"
            if erros:
                msg += f"\n\n⚠️ {len(erros)} erro(s)"
            messagebox.showinfo("Resultado", msg)
        else:
            messagebox.showerror("Erro", "\n".join(erros[:5]))

        self.refresh_data()

    # ===== HELPER METHODS (MANTER) =====

    def on_new_item(self):
        """Ação do botão 'Novo' - abre formulário para criar novo equipamento"""
        self.adicionar_equipamento()

    def adicionar_equipamento(self):
        """Navigate to equipamento_form screen for create"""
        main_window = self.master.master
        if hasattr(main_window, 'show_screen'):
            main_window.show_screen("equipamento_form", equipamento_id=None)
        else:
            messagebox.showerror("Erro", "Não foi possível abrir formulário")

    def editar_equipamento_by_id(self, equipamento_id: int):
        """Navigate to equipamento_form screen for edit"""
        main_window = self.master.master
        if hasattr(main_window, 'show_screen'):
            main_window.show_screen("equipamento_form", equipamento_id=equipamento_id)
        else:
            messagebox.showerror("Erro", "Não foi possível abrir formulário")

    # ===== CONTEXT MENU HELPERS =====

    def _editar_from_context(self, equipamento):
        """Edita equipamento a partir do menu de contexto"""
        self.editar_equipamento_by_id(equipamento.id)

    def _eliminar_from_context(self, equipamento):
        """Elimina equipamento a partir do menu de contexto (individual)"""
        # Confirmar
        resposta = messagebox.askyesno(
            "Confirmar Eliminação",
            f"Tem certeza que deseja eliminar o equipamento '{equipamento.numero}'?\n\n"
            f"Esta ação não pode ser desfeita."
        )

        if not resposta:
            return

        # Delete
        sucesso, erro = self.manager.eliminar_equipamento(equipamento.id)

        if sucesso:
            messagebox.showinfo("Sucesso", f"Equipamento eliminado!")
            self.refresh_data()
        else:
            messagebox.showerror("Erro", f"Erro ao eliminar: {erro}")

