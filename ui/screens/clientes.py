# -*- coding: utf-8 -*-
"""
Tela de Clientes - Gestão de clientes da Agora Media
"""
import customtkinter as ctk
import tkinter as tk
from typing import Dict
from sqlalchemy.orm import Session
from logic.clientes import ClientesManager
from ui.components.data_table_v2 import DataTableV2
from tkinter import messagebox
import csv
from datetime import datetime
from assets.resources import get_icon, CLIENTES
from utils.base_dialogs import BaseDialogMedium


class ClientesScreen(ctk.CTkFrame):
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
        super().__init__(parent, **kwargs)

        self.db_session = db_session
        self.manager = ClientesManager(db_session)
        self.main_window = main_window

        # Configure
        self.configure(fg_color="transparent")

        # Create widgets
        self.create_widgets()

        # Load data
        self.carregar_clientes()

    def create_widgets(self):
        """Create screen widgets"""

        # Header
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=30, pady=(30, 20))

        # Title with PNG icon
        icon_pil = get_icon(CLIENTES, size=(28, 28))
        if icon_pil:
            icon_ctk = ctk.CTkImage(
                light_image=icon_pil,
                dark_image=icon_pil,
                size=(28, 28)
            )
            title_label = ctk.CTkLabel(
                header_frame,
                image=icon_ctk,
                text=" Clientes",
                compound="left",
                font=ctk.CTkFont(size=28, weight="bold")
            )
        else:
            title_label = ctk.CTkLabel(
                header_frame,
                text="👥 Clientes",
                font=ctk.CTkFont(size=28, weight="bold")
            )
        title_label.pack(side="left")

        # Buttons
        button_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        button_frame.pack(side="right")

        refresh_btn = ctk.CTkButton(
            button_frame,
            text="🔄 Atualizar",
            command=self.carregar_clientes,
            width=120,
            height=35,
            font=ctk.CTkFont(size=13)
        )
        refresh_btn.pack(side="left", padx=(0, 10))

        add_btn = ctk.CTkButton(
            button_frame,
            text="➕ Novo Cliente",
            command=self.adicionar_cliente,
            width=140,
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
            placeholder_text="Nome, NIF ou Email...",
            width=300,
            height=35
        )
        self.search_entry.pack(side="left", padx=(0, 10))
        self.search_entry.bind("<KeyRelease>", lambda e: self.pesquisar())

        search_btn = ctk.CTkButton(
            filter_frame,
            text="🔍 Pesquisar",
            command=self.pesquisar,
            width=120,
            height=35
        )
        search_btn.pack(side="left", padx=(0, 10))

        clear_btn = ctk.CTkButton(
            filter_frame,
            text="✖️ Limpar",
            command=self.limpar_pesquisa,
            width=100,
            height=35,
            fg_color="gray",
            hover_color="darkgray"
        )
        clear_btn.pack(side="left")

        # Order by
        ctk.CTkLabel(
            filter_frame,
            text="Ordenar por:",
            font=ctk.CTkFont(size=13)
        ).pack(side="left", padx=(20, 10))

        self.order_var = ctk.StringVar(value="numero")
        order_menu = ctk.CTkOptionMenu(
            filter_frame,
            variable=self.order_var,
            values=["numero", "nome", "nif"],
            command=lambda x: self.carregar_clientes(),
            width=120,
            height=35
        )
        order_menu.pack(side="left")

        # Selection actions bar (created but NOT packed - will be shown on selection)
        self.selection_frame = ctk.CTkFrame(self, fg_color="transparent")

        # Clear selection button
        self.cancel_btn = ctk.CTkButton(
            self.selection_frame,
            text="🗑️ Limpar Seleção",
            command=self.cancelar_selecao,
            width=150, height=35
        )

        # Ver Projetos button (only shown when 1 cliente selected)
        self.ver_projetos_btn = ctk.CTkButton(
            self.selection_frame,
            text="📁 Ver Projetos",
            command=self.ver_projetos_selecionado,
            width=150, height=35,
            fg_color=("#2196F3", "#1565C0"),
            hover_color=("#1976D2", "#0D47A1")
        )

        # Export button
        self.export_btn = ctk.CTkButton(
            self.selection_frame,
            text="📊 Exportar CSV",
            command=self.exportar_selecionados,
            width=150, height=35,
            fg_color=("#4CAF50", "#388E3C"),
            hover_color=("#66BB6A", "#2E7D32")
        )

        # Selection count label
        self.count_label = ctk.CTkLabel(
            self.selection_frame,
            text="",
            font=ctk.CTkFont(size=13)
        )

        # Table container
        table_container = ctk.CTkFrame(self)
        table_container.pack(fill="both", expand=True, padx=30, pady=(0, 30))

        # Create table
        columns = [
            {"key": "numero", "label": "ID", "width": 100},
            {"key": "nome", "label": "Nome", "width": 300},
            {"key": "nif", "label": "NIF", "width": 150},
            {"key": "projetos_count", "label": "Projetos", "width": 100},
        ]

        self.table = DataTableV2(
            table_container,
            columns=columns,
            on_row_double_click=self.on_double_click,
            on_selection_change=self.on_selection_change,
            on_row_right_click=self.show_context_menu
        )
        self.table.pack(fill="both", expand=True)

    def carregar_clientes(self):
        """Load and display clientes"""
        order_by = self.order_var.get()
        clientes = self.manager.listar_todos(order_by=order_by)

        # Prepare data
        data = []
        for cliente in clientes:
            projetos_count = len(cliente.projetos)
            data.append({
                "id": cliente.id,
                "numero": cliente.numero,
                "nome": cliente.nome,
                "nif": cliente.nif or "-",
                "projetos_count": projetos_count,  # Keep as integer for proper sorting
                # Store full data for export
                "_cliente": cliente,
                "_has_projetos": projetos_count > 0
            })

        self.table.set_data(data)

    def pesquisar(self):
        """Search clientes"""
        termo = self.search_entry.get().strip()

        if not termo:
            self.carregar_clientes()
            return

        clientes = self.manager.pesquisar(termo)

        # Prepare data
        data = []
        for cliente in clientes:
            projetos_count = len(cliente.projetos)
            data.append({
                "id": cliente.id,
                "numero": cliente.numero,
                "nome": cliente.nome,
                "nif": cliente.nif or "-",
                "projetos_count": projetos_count,  # Keep as integer for proper sorting
                "_cliente": cliente,
                "_has_projetos": projetos_count > 0
            })

        self.table.set_data(data)

    def limpar_pesquisa(self):
        """Clear search"""
        self.search_entry.delete(0, "end")
        self.carregar_clientes()

    def on_selection_change(self, selected_data: list):
        """Handle selection change in table"""
        num_selected = len(selected_data)

        if num_selected > 0:
            # Show selection frame
            self.selection_frame.pack(fill="x", padx=30, pady=(0, 10))
            self.cancel_btn.pack(side="left", padx=(0, 10))

            # Show "Ver Projetos" button only when exactly 1 cliente is selected
            if num_selected == 1:
                self.ver_projetos_btn.pack(side="left", padx=(0, 10))
            else:
                self.ver_projetos_btn.pack_forget()

            self.export_btn.pack(side="left", padx=(0, 20))
            self.count_label.configure(text=f"{num_selected} cliente(s) selecionado(s)")
            self.count_label.pack(side="left")
        else:
            # Hide entire selection frame when nothing is selected
            self.selection_frame.pack_forget()

    def on_double_click(self, data: Dict):
        """Handle double click - open for edit"""
        cliente_id = data.get("id")
        if cliente_id:
            self.editar_cliente(cliente_id)

    def show_context_menu(self, event, data: dict):
        """
        Mostra menu de contexto (right-click) para um cliente

        Args:
            event: Evento do clique (para posição)
            data: Dados da linha clicada
        """
        cliente = data.get('_cliente')
        if not cliente:
            return

        # Criar menu
        menu = tk.Menu(self, tearoff=0)

        # ✏️ Editar
        menu.add_command(
            label="✏️ Editar",
            command=lambda: self._editar_from_context(cliente)
        )

        menu.add_separator()

        # 🗑️ Apagar
        menu.add_command(
            label="🗑️ Apagar",
            command=lambda: self._apagar_from_context(cliente)
        )

        # Mostrar menu na posição do cursor
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def _editar_from_context(self, cliente):
        """Edita cliente a partir do menu de contexto"""
        self.editar_cliente(cliente.id)

    def _apagar_from_context(self, cliente):
        """Apaga cliente a partir do menu de contexto"""
        self.apagar_cliente(cliente.id)

    def cancelar_selecao(self):
        """Clear selection"""
        self.table.clear_selection()

    def ver_projetos_selecionado(self):
        """Navigate to projetos screen filtered by selected cliente"""
        selected_data = self.table.get_selected_data()

        if len(selected_data) != 1:
            return

        cliente_id = selected_data[0].get("id")

        # Navigate to projetos with cliente filter
        if self.main_window and cliente_id:
            self.main_window.show_projetos(filtro_cliente_id=cliente_id)

    def exportar_selecionados(self):
        """Export selected clientes to CSV"""
        selected_data = self.table.get_selected_data()

        if not selected_data:
            messagebox.showwarning("Aviso", "Nenhum cliente selecionado")
            return

        # Prepare filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"clientes_export_{timestamp}.csv"

        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['Número', 'Nome', 'NIF', 'País', 'Contacto', 'Email', 'Projetos']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                writer.writeheader()
                for item in selected_data:
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

            messagebox.showinfo(
                "Sucesso",
                f"Exportados {len(selected_data)} cliente(s) para {filename}"
            )
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao exportar: {str(e)}")

    def ver_projetos_cliente(self, row_data: Dict):
        """
        Navigate to projetos screen filtered by this cliente

        Args:
            row_data: Row data containing cliente info
        """
        # Check if cliente has projects
        if not row_data.get("_has_projetos"):
            return  # No projects to show

        # Get cliente ID for filtering
        cliente_id = row_data.get("id")

        # Navigate to projetos with cliente filter
        if self.main_window and cliente_id:
            self.main_window.show_projetos(filtro_cliente_id=cliente_id)

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
            self.carregar_clientes()
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
