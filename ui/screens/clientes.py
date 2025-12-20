# -*- coding: utf-8 -*-
"""
Tela de Clientes - Gestão de clientes da Agora Media
"""
import customtkinter as ctk
import tkinter as tk
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from logic.clientes import ClientesManager
from ui.components.base_screen import BaseScreen
from tkinter import messagebox
import csv
from datetime import datetime
from assets.resources import get_icon, CLIENTES
from utils.base_dialogs import BaseDialogMedium


class ClientesScreen(BaseScreen):
    """
    Tela de gestão de Clientes
    """

    def __init__(self, parent, db_session: Session, main_window=None, **kwargs):
        """
        Initialize clientes screen

        Args:
            parent: Parent widget
            db_session: SQLAlchemy database session
            main_window: Reference to MainWindow for navigation
        """
        self.db_session = db_session
        self.manager = ClientesManager(db_session)
        self.main_window = main_window

        # Initialize filter widgets (created in toolbar_slot)
        self.search_entry = None
        self.order_var = None

        # Call parent __init__ (this will call abstract methods)
        super().__init__(parent, db_session, **kwargs)

    # ===== ABSTRACT METHODS FROM BaseScreen =====

    def get_screen_title(self) -> str:
        """Return screen title"""
        return "Clientes"

    def get_screen_icon(self):
        """Return screen icon (PIL Image or None)"""
        return get_icon(CLIENTES, size=(28, 28))

    def get_table_columns(self) -> List[Dict[str, Any]]:
        """Return table column definitions"""
        return [
            {"key": "numero", "label": "ID", "width": 100, 'sortable': True},
            {"key": "nome", "label": "Nome", "width": 300, 'sortable': True},
            {"key": "nif", "label": "NIF", "width": 150, 'sortable': True},
            {"key": "projetos_count", "label": "Projetos", "width": 100, 'sortable': True},
        ]

    def load_data(self) -> List[Any]:
        """Load clientes from database and return as list of objects"""
        try:
            # Get search filter (widget pode não existir em __init__)
            search = None
            if hasattr(self, 'search_entry') and self.search_entry:
                try:
                    search = self.search_entry.get().strip() or None
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
                clientes = self.manager.pesquisar(search)
            else:
                clientes = self.manager.listar_todos(order_by=order_by)

            return clientes  # NUNCA None, sempre lista

        except Exception as e:
            print(f"ERROR in load_data(): {e}")
            import traceback
            traceback.print_exc()
            return []  # SEMPRE retornar lista vazia em erro

    def item_to_dict(self, item: Any) -> Dict[str, Any]:
        """Convert cliente object to dict for table"""
        projetos_count = len(item.projetos) if hasattr(item, 'projetos') and item.projetos else 0

        return {
            'id': item.id,
            'numero': item.numero,
            'nome': item.nome,
            'nif': item.nif or '-',
            'projetos_count': projetos_count,  # Integer para sorting correto
            '_cliente': item,  # CRÍTICO: guardar objeto original
            '_has_projetos': projetos_count > 0
        }

    def get_context_menu_items(self, data: dict) -> List[Dict[str, Any]]:
        """Define ações do context menu e barra de ações"""

        # Para barra de ações (data vazio {} quando BaseScreen chama)
        if not data or '_cliente' not in data:
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
                    'label': '📁 Ver Projetos',
                    'command': self._ver_projetos_selecionado,
                    'min_selection': 1,
                    'max_selection': 1,  # ⚠️ Apenas 1 por vez
                    'fg_color': ('#2196F3', '#1565C0'),
                    'hover_color': ('#1976D2', '#0D47A1'),
                    'width': 130
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

        # Para context menu (ações contextuais)
        cliente = data.get('_cliente')
        if not cliente:
            return []

        return [
            {'label': '✏️ Editar', 'command': lambda: self._editar_from_context(cliente)},
            {'separator': True},
            {'label': '🗑️ Apagar', 'command': lambda: self._apagar_from_context(cliente)}
        ]

    # ===== OPTIONAL METHODS =====

    def toolbar_slot(self, parent):
        """Create custom toolbar with search and order by"""
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
            placeholder_text="Nome, NIF ou Email...",
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

        # Order by
        ctk.CTkLabel(
            toolbar_frame,
            text="Ordenar por:",
            font=ctk.CTkFont(size=13)
        ).pack(side="left", padx=(0, 10))

        self.order_var = ctk.StringVar(value="numero")
        order_menu = ctk.CTkOptionMenu(
            toolbar_frame,
            variable=self.order_var,
            values=["numero", "nome", "nif"],
            command=lambda x: self.refresh_data(),
            width=120,
            height=35
        )
        order_menu.pack(side="left")

    def on_add_click(self):
        """Handle add button click"""
        self.adicionar_cliente()

    def on_item_double_click(self, data: dict):
        """Handle table row double-click (editar)"""
        cliente_id = data.get('id')
        if cliente_id:
            self.editar_cliente(cliente_id)

    def calculate_selection_total(self, selected_data: List[Dict[str, Any]]) -> float:
        """Not applicable for Clientes - return 0"""
        return 0.0

    # ===== BULK OPERATION METHODS FOR ACTION BAR =====

    def _editar_selecionado(self):
        """Edita cliente selecionado"""
        selected = self.get_selected_data()
        if selected and len(selected) == 1:
            self.on_item_double_click(selected[0])

    def _ver_projetos_selecionado(self):
        """Navega para projetos filtrados por cliente (APENAS 1)"""
        selected = self.get_selected_data()
        if not selected or len(selected) != 1:
            return

        cliente_id = selected[0].get('id')

        # Navigate to projetos with cliente filter
        if self.main_window and cliente_id:
            self.main_window.show_projetos(filtro_cliente_id=cliente_id)

    def _exportar_selecionados(self):
        """Exporta clientes selecionados para CSV"""
        selected = self.get_selected_data()
        if not selected:
            return

        # Prepare filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"clientes_export_{timestamp}.csv"

        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['Número', 'Nome', 'NIF', 'País', 'Contacto', 'Email', 'Projetos']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                writer.writeheader()
                for item in selected:
                    cliente = item.get('_cliente')
                    if cliente:
                        writer.writerow({
                            'Número': cliente.numero,
                            'Nome': cliente.nome,
                            'NIF': cliente.nif or '',
                            'País': cliente.pais or '',
                            'Contacto': cliente.contacto or '',
                            'Email': cliente.email or '',
                            'Projetos': str(len(cliente.projetos))
                        })

            messagebox.showinfo("Sucesso", f"Exportados {len(selected)} cliente(s) para {filename}")

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao exportar: {str(e)}")

    def _apagar_selecionados(self):
        """Apaga clientes selecionados"""
        selected = self.get_selected_data()
        if not selected:
            return

        num = len(selected)

        # Confirmar
        resposta = messagebox.askyesno(
            "Confirmar Eliminação",
            f"Apagar {num} cliente(s)?\n\n"
            f"⚠️ Esta ação não pode ser desfeita!"
        )

        if not resposta:
            return

        sucessos = 0
        erros = []

        for data in selected:
            cliente = data.get('_cliente')
            if cliente:
                sucesso, erro = self.manager.apagar(cliente.id)
                if sucesso:
                    sucessos += 1
                else:
                    erros.append(f"{cliente.nome}: {erro}")

        if sucessos > 0:
            msg = f"✅ {sucessos} cliente(s) apagado(s)!"
            if erros:
                msg += f"\n\n⚠️ {len(erros)} erro(s)"
            messagebox.showinfo("Resultado", msg)
        else:
            messagebox.showerror("Erro", "\n".join(erros[:5]))

        self.refresh_data()

    # ===== HELPER METHODS (MANTER) =====

    def on_new_item(self):
        """Ação do botão 'Novo' - abre formulário para criar novo cliente"""
        self.adicionar_cliente()

    def adicionar_cliente(self):
        """Navigate to cliente_form screen for create"""
        main_window = self.master.master
        if hasattr(main_window, 'show_screen'):
            main_window.show_screen("cliente_form", cliente_id=None)
        else:
            messagebox.showerror("Erro", "Não foi possível abrir formulário")

    def editar_cliente(self, cliente_id: int):
        """Navigate to cliente_form screen for edit"""
        main_window = self.master.master
        if hasattr(main_window, 'show_screen'):
            main_window.show_screen("cliente_form", cliente_id=cliente_id)
        else:
            messagebox.showerror("Erro", "Não foi possível abrir formulário")

    def apagar_cliente(self, cliente_id: int):
        """Delete cliente"""
        cliente = self.manager.buscar_por_id(cliente_id)
        if not cliente:
            messagebox.showerror("Erro", "Cliente não encontrado")
            return

        # Confirm
        dialog = ConfirmDialog(
            self,
            title="Confirmar eliminação",
            message=f"Tem certeza que deseja eliminar o cliente '{cliente.nome}'?\n\nEsta ação não pode ser desfeita.",
            confirm_text="Eliminar",
            cancel_text="Cancelar"
        )
        dialog.wait_window()

        if not dialog.confirmed:
            return

        # Delete
        success, message = self.manager.apagar(cliente_id)

        if success:
            self.refresh_data()
        else:
            messagebox.showerror("Erro", message)

    # ===== CONTEXT MENU HELPERS =====

    def _editar_from_context(self, cliente):
        """Edita cliente a partir do menu de contexto"""
        self.editar_cliente(cliente.id)

    def _apagar_from_context(self, cliente):
        """Apaga cliente a partir do menu de contexto"""
        self.apagar_cliente(cliente.id)


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
