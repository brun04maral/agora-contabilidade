# -*- coding: utf-8 -*-
"""
Tela de Fornecedores - Gestão de fornecedores/credores
"""
import customtkinter as ctk
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from logic.fornecedores import FornecedoresManager
from ui.components.base_screen import BaseScreen
from database.models import EstatutoFornecedor
from datetime import datetime
from tkinter import messagebox
import csv
from assets.resources import get_icon, FORNECEDORES
from utils.base_dialogs import BaseDialogMedium


class FornecedoresScreen(BaseScreen):
    """
    Tela de gestão de Fornecedores
    """

    def __init__(self, parent, db_session: Session, **kwargs):
        """
        Initialize fornecedores screen

        Args:
            parent: Parent widget
            db_session: SQLAlchemy database session
        """
        self.db_session = db_session
        self.manager = FornecedoresManager(db_session)

        # Initialize filter widgets (created in toolbar_slot)
        self.search_entry = None
        self.estatuto_var = None
        self.order_var = None

        # Call parent __init__ (this will call abstract methods)
        super().__init__(parent, db_session, **kwargs)

    # ===== ABSTRACT METHODS FROM BaseScreen =====

    def get_screen_title(self) -> str:
        """Return screen title"""
        return "Fornecedores"

    def get_screen_icon(self):
        """Return screen icon (PIL Image or None)"""
        return get_icon(FORNECEDORES, size=(28, 28))

    def get_table_columns(self) -> List[Dict[str, Any]]:
        """Return table column definitions"""
        return [
            {"key": "numero", "label": "ID", "width": 100, 'sortable': True},
            {"key": "nome", "label": "Nome", "width": 250, 'sortable': True},
            {"key": "estatuto", "label": "Estatuto", "width": 120, 'sortable': True},
            {"key": "area", "label": "Área", "width": 150, 'sortable': True},
            {"key": "funcao", "label": "Função", "width": 150, 'sortable': True},
            {"key": "classificacao", "label": "★", "width": 80, 'sortable': True},
            {"key": "despesas_count", "label": "Despesas", "width": 100, 'sortable': True},
        ]

    def load_data(self) -> List[Any]:
        """Load fornecedores from database and return as list of objects"""
        try:
            # Get search filter (widget pode não existir em __init__)
            search = None
            if hasattr(self, 'search_entry') and self.search_entry:
                try:
                    search = self.search_entry.get().strip() or None
                except Exception:
                    pass

            # Get estatuto filter
            estatuto = None
            if hasattr(self, 'estatuto_var') and self.estatuto_var:
                try:
                    estatuto_str = self.estatuto_var.get()
                    if estatuto_str != "TODOS":
                        estatuto = EstatutoFornecedor[estatuto_str]
                except Exception:
                    pass

            # Get order by filter
            order_by = "numero"  # default
            if hasattr(self, 'order_var') and self.order_var:
                try:
                    order_by = self.order_var.get()
                except Exception:
                    pass

            # Apply search or load all
            if search:
                fornecedores = self.manager.pesquisar(search)
            else:
                fornecedores = self.manager.listar_todos(estatuto=estatuto, order_by=order_by)

            return fornecedores  # NUNCA None, sempre lista

        except Exception as e:
            print(f"ERROR in load_data(): {e}")
            import traceback
            traceback.print_exc()
            return []  # SEMPRE retornar lista vazia em erro

    def item_to_dict(self, item: Any) -> Dict[str, Any]:
        """Convert fornecedor object to dict for table"""
        color = self.get_estatuto_color(item.estatuto) if item.estatuto else ("#E0E0E0", "#4A4A4A")
        despesas_count = len(item.despesas) if hasattr(item, 'despesas') and item.despesas else 0

        return {
            'id': item.id,
            'numero': item.numero,
            'nome': item.nome,
            'estatuto': item.estatuto.value if item.estatuto else '-',
            'area': item.area or '-',
            'funcao': item.funcao or '-',
            'classificacao': '★' * item.classificacao if item.classificacao else '-',
            'despesas_count': despesas_count,  # Integer para sorting correto
            '_bg_color': color,
            '_fornecedor': item  # CRÍTICO: guardar objeto original
        }

    def get_context_menu_items(self, data: dict) -> List[Dict[str, Any]]:
        """Define ações do context menu e barra de ações"""

        # Para barra de ações (data vazio {} quando BaseScreen chama)
        if not data or '_fornecedor' not in data:
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
                    'label': '📊 Exportar CSV',
                    'command': self._exportar_selecionados,
                    'min_selection': 1,
                    'max_selection': None,
                    'fg_color': ('#4CAF50', '#388E3C'),
                    'hover_color': ('#66BB6A', '#2E7D32'),
                    'width': 140
                },
                {
                    'label': '🗑️ Apagar',
                    'command': self._apagar_selecionados,
                    'min_selection': 1,
                    'max_selection': None,
                    'fg_color': ('#F44336', '#C62828'),
                    'hover_color': ('#D32F2F', '#B71C1C'),
                    'width': 100
                }
            ]

        # Para context menu (ações contextuais simples)
        fornecedor = data.get('_fornecedor')
        if not fornecedor:
            return []

        return [
            {'label': '✏️ Editar', 'command': lambda: self.editar_fornecedor(fornecedor.id)},
            {'separator': True},
            {'label': '🗑️ Apagar', 'command': lambda: self.apagar_fornecedor(fornecedor.id)}
        ]

    # ===== OPTIONAL METHODS =====

    def toolbar_slot(self, parent):
        """Create custom toolbar with search, estatuto and order by filters"""
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
            placeholder_text="Nome, NIF, Área, Função...",
            width=300,
            height=35
        )
        self.search_entry.pack(side="left", padx=(0, 10))
        self.search_entry.bind("<KeyRelease>", lambda e: self.refresh_data())

        # Botão Pesquisar (opcional, search é reativo)
        search_btn = ctk.CTkButton(
            toolbar_frame,
            text="🔍",
            command=self.refresh_data,
            width=35,
            height=35
        )
        search_btn.pack(side="left", padx=(0, 10))

        # Botão Limpar
        clear_btn = ctk.CTkButton(
            toolbar_frame,
            text="✖️",
            command=lambda: (self.search_entry.delete(0, 'end'), self.refresh_data()),
            width=35,
            height=35,
            fg_color="gray",
            hover_color="darkgray"
        )
        clear_btn.pack(side="left", padx=(0, 20))

        # Estatuto filter
        ctk.CTkLabel(
            toolbar_frame,
            text="Estatuto:",
            font=ctk.CTkFont(size=13)
        ).pack(side="left", padx=(0, 10))

        self.estatuto_var = ctk.StringVar(value="TODOS")
        estatuto_menu = ctk.CTkOptionMenu(
            toolbar_frame,
            variable=self.estatuto_var,
            values=["TODOS", "EMPRESA", "FREELANCER", "ESTADO"],
            command=lambda x: self.refresh_data(),
            width=130,
            height=35
        )
        estatuto_menu.pack(side="left", padx=(0, 20))

        # Order by
        ctk.CTkLabel(
            toolbar_frame,
            text="Ordenar:",
            font=ctk.CTkFont(size=13)
        ).pack(side="left", padx=(0, 10))

        self.order_var = ctk.StringVar(value="numero")
        order_menu = ctk.CTkOptionMenu(
            toolbar_frame,
            variable=self.order_var,
            values=["numero", "nome", "estatuto", "area"],
            command=lambda x: self.refresh_data(),
            width=120,
            height=35
        )
        order_menu.pack(side="left")

    def on_add_click(self):
        """Handle add button click"""
        self.adicionar_fornecedor()

    def on_item_double_click(self, data: dict):
        """Handle table row double-click (editar)"""
        fornecedor_id = data.get('id')
        if fornecedor_id:
            self.editar_fornecedor(fornecedor_id)

    def calculate_selection_total(self, selected_data: List[Dict[str, Any]]) -> float:
        """Not applicable for Fornecedores - return 0"""
        return 0.0

    # ===== BULK OPERATION METHODS FOR ACTION BAR =====

    def _editar_selecionado(self):
        """Edita fornecedor selecionado"""
        selected = self.get_selected_data()
        if selected and len(selected) == 1:
            self.on_item_double_click(selected[0])

    def _exportar_selecionados(self):
        """Exporta fornecedores selecionados para CSV"""
        selected = self.get_selected_data()
        if not selected:
            return

        # Prepare filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"fornecedores_export_{timestamp}.csv"

        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['Número', 'Nome', 'Estatuto', 'Área', 'Função', 'Classificação', 'NIF', 'Contacto', 'Email', 'Despesas']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                writer.writeheader()
                for item in selected:
                    fornecedor = item.get('_fornecedor')
                    if fornecedor:
                        writer.writerow({
                            'Número': fornecedor.numero,
                            'Nome': fornecedor.nome,
                            'Estatuto': fornecedor.estatuto.value if fornecedor.estatuto else '',
                            'Área': fornecedor.area or '',
                            'Função': fornecedor.funcao or '',
                            'Classificação': str(fornecedor.classificacao) if fornecedor.classificacao else '',
                            'NIF': fornecedor.nif or '',
                            'Contacto': fornecedor.contacto or '',
                            'Email': fornecedor.email or '',
                            'Despesas': str(len(fornecedor.despesas))
                        })

            messagebox.showinfo("Sucesso", f"Exportados {len(selected)} fornecedor(es) para {filename}")

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao exportar: {str(e)}")

    def _apagar_selecionados(self):
        """Apaga fornecedores selecionados"""
        selected = self.get_selected_data()
        if not selected:
            return

        num = len(selected)

        # Confirmar
        resposta = messagebox.askyesno(
            "Confirmar Eliminação",
            f"Apagar {num} fornecedor(es)?\n\n"
            f"⚠️ Esta ação não pode ser desfeita!"
        )

        if not resposta:
            return

        sucessos = 0
        erros = []

        for data in selected:
            fornecedor = data.get('_fornecedor')
            if fornecedor:
                sucesso, erro = self.manager.apagar(fornecedor.id)
                if sucesso:
                    sucessos += 1
                else:
                    erros.append(f"{fornecedor.nome}: {erro}")

        if sucessos > 0:
            msg = f"✅ {sucessos} fornecedor(es) apagado(s)!"
            if erros:
                msg += f"\n\n⚠️ {len(erros)} erro(s)"
            messagebox.showinfo("Resultado", msg)
        else:
            messagebox.showerror("Erro", "\n".join(erros[:5]))

        self.refresh_data()

    # ===== HELPER METHODS (MANTER) =====

    def get_estatuto_color(self, estatuto: EstatutoFornecedor) -> tuple:
        """Get color for estatuto (tonalidades diferentes da mesma cor)"""
        color_map = {
            EstatutoFornecedor.EMPRESA: ("#B3D9FF", "#5A8BB8"),      # Azul claro
            EstatutoFornecedor.FREELANCER: ("#99CCFF", "#4D7A99"),  # Azul médio
            EstatutoFornecedor.ESTADO: ("#80BFFF", "#406B8B")        # Azul escuro
        }
        return color_map.get(estatuto, ("#E0E0E0", "#4A4A4A"))

    def adicionar_fornecedor(self):
        """Navigate to fornecedor_form screen for create"""
        main_window = self.master.master
        if hasattr(main_window, 'show_screen'):
            main_window.show_screen("fornecedor_form", fornecedor_id=None)
        else:
            messagebox.showerror("Erro", "Não foi possível abrir formulário")

    def editar_fornecedor(self, fornecedor_id: int):
        """Navigate to fornecedor_form screen for edit"""
        main_window = self.master.master
        if hasattr(main_window, 'show_screen'):
            main_window.show_screen("fornecedor_form", fornecedor_id=fornecedor_id)
        else:
            messagebox.showerror("Erro", "Não foi possível abrir formulário")

    def apagar_fornecedor(self, fornecedor_id: int):
        """Delete fornecedor"""
        fornecedor = self.manager.buscar_por_id(fornecedor_id)
        if not fornecedor:
            messagebox.showerror("Erro", "Fornecedor não encontrado")
            return

        # Confirm
        dialog = ConfirmDialog(
            self,
            title="Confirmar eliminação",
            message=f"Tem certeza que deseja eliminar o fornecedor '{fornecedor.nome}'?\n\nEsta ação não pode ser desfeita.",
            confirm_text="Eliminar",
            cancel_text="Cancelar"
        )
        dialog.wait_window()

        if not dialog.confirmed:
            return

        # Delete
        success, message = self.manager.apagar(fornecedor_id)

        if success:
            self.refresh_data()
        else:
            messagebox.showerror("Erro", message)


class ConfirmDialog(BaseDialogMedium):
    """Confirmation dialog"""

    def __init__(self, parent, title: str, message: str, confirm_text: str = "Confirmar", cancel_text: str = "Cancelar"):
        self.confirmed = False
        self._message = message
        self._confirm_text = confirm_text
        self._cancel_text = cancel_text

        super().__init__(parent, title=title, height=280)

        self.create_layout()

    def create_layout(self):
        """Create dialog layout"""
        # Icon
        icon_label = ctk.CTkLabel(
            self.main_frame,
            text="⚠️",
            font=ctk.CTkFont(size=40)
        )
        icon_label.pack(pady=(20, 10))

        # Message
        message_label = ctk.CTkLabel(
            self.main_frame,
            text=self._message,
            font=ctk.CTkFont(size=14),
            wraplength=400
        )
        message_label.pack(pady=(0, 20))

        # Buttons
        button_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        button_frame.pack(fill="x")

        cancel_btn = ctk.CTkButton(
            button_frame,
            text=self._cancel_text,
            command=self.cancel,
            width=140,
            height=35,
            fg_color="gray",
            hover_color="darkgray"
        )
        cancel_btn.pack(side="left", expand=True, padx=5)

        confirm_btn = ctk.CTkButton(
            button_frame,
            text=self._confirm_text,
            command=self.confirm,
            width=140,
            height=35,
            fg_color=("#F44336", "#D32F2F"),
            hover_color=("#E53935", "#C62828")
        )
        confirm_btn.pack(side="right", expand=True, padx=5)

    def confirm(self):
        """Confirm action"""
        self.confirmed = True
        self.destroy()

    def cancel(self):
        """Cancel action"""
        self.confirmed = False
        self.destroy()
