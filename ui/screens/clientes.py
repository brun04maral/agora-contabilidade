# -*- coding: utf-8 -*-
"""
Tela de Clientes - Gestão de clientes da Agora Media
"""
import customtkinter as ctk
from typing import Callable, Optional, Dict
from sqlalchemy.orm import Session
from logic.clientes import ClientesManager
from ui.components.data_table_v2 import DataTableV2
from database.models import Cliente
from tkinter import messagebox
import csv
from datetime import datetime


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
            {"key": "numero", "label": "Número", "width": 100},
            {"key": "nome", "label": "Nome", "width": 300},
            {"key": "nif", "label": "NIF", "width": 150},
            {"key": "projetos_count", "label": "Projetos", "width": 100},
        ]

        self.table = DataTableV2(
            table_container,
            columns=columns,
            on_row_double_click=self.on_double_click,
            on_selection_change=self.on_selection_change
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
                "projetos_count": str(projetos_count) if projetos_count > 0 else "0",
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
                "projetos_count": str(projetos_count) if projetos_count > 0 else "0",
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
        """Show dialog to add new cliente"""
        dialog = FormularioClienteDialog(self, self.db_session)
        dialog.wait_window()

        # Reload if cliente was created
        if dialog.cliente_criado:
            self.carregar_clientes()

    def editar_cliente(self, cliente_id: int):
        """Show dialog to edit cliente"""
        cliente = self.manager.buscar_por_id(cliente_id)
        if not cliente:
            self.show_error("Cliente não encontrado")
            return

        dialog = FormularioClienteDialog(self, self.db_session, cliente=cliente)
        dialog.wait_window()

        # Reload if cliente was updated
        if dialog.cliente_atualizado:
            self.carregar_clientes()

    def apagar_cliente(self, cliente_id: int):
        """Delete cliente"""
        cliente = self.manager.buscar_por_id(cliente_id)
        if not cliente:
            self.show_error("Cliente não encontrado")
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
            self.show_success(message)
            self.carregar_clientes()
        else:
            self.show_error(message)

    def show_success(self, message: str):
        """Show success message"""
        dialog = MessageDialog(self, title="Sucesso", message=message, type="success")
        dialog.wait_window()

    def show_error(self, message: str):
        """Show error message"""
        dialog = MessageDialog(self, title="Erro", message=message, type="error")
        dialog.wait_window()


class FormularioClienteDialog(ctk.CTkToplevel):
    """
    Dialog for creating/editing cliente
    """

    def __init__(self, parent, db_session: Session, cliente: Optional[Cliente] = None):
        super().__init__(parent)

        self.db_session = db_session
        self.manager = ClientesManager(db_session)
        self.cliente = cliente
        self.cliente_criado = False
        self.cliente_atualizado = False

        # Configure window
        self.title("Editar Cliente" if cliente else "Novo Cliente")
        self.geometry("600x700")
        self.resizable(False, False)

        # Make modal
        self.transient(parent)
        self.grab_set()

        # Center window
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (600 // 2)
        y = (self.winfo_screenheight() // 2) - (700 // 2)
        self.geometry(f"600x700+{x}+{y}")

        # Create widgets
        self.create_widgets()

        # Load data if editing
        if self.cliente:
            self.load_cliente_data()

    def create_widgets(self):
        """Create dialog widgets"""

        # Main container
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Title
        title = ctk.CTkLabel(
            main_frame,
            text="✏️ Editar Cliente" if self.cliente else "➕ Novo Cliente",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title.pack(pady=(0, 20))

        # Scrollable form
        form_frame = ctk.CTkScrollableFrame(main_frame)
        form_frame.pack(fill="both", expand=True)

        # Nome (required)
        ctk.CTkLabel(
            form_frame,
            text="Nome *",
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(anchor="w", pady=(10, 5))

        self.nome_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="Nome do cliente...",
            height=35
        )
        self.nome_entry.pack(fill="x", pady=(0, 15))

        # NIF
        ctk.CTkLabel(
            form_frame,
            text="NIF / Tax ID",
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(anchor="w", pady=(0, 5))

        self.nif_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="Número de identificação fiscal...",
            height=35
        )
        self.nif_entry.pack(fill="x", pady=(0, 15))

        # País
        ctk.CTkLabel(
            form_frame,
            text="País",
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(anchor="w", pady=(0, 5))

        self.pais_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="Portugal",
            height=35
        )
        self.pais_entry.pack(fill="x", pady=(0, 15))

        # Morada
        ctk.CTkLabel(
            form_frame,
            text="Morada",
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(anchor="w", pady=(0, 5))

        self.morada_entry = ctk.CTkTextbox(
            form_frame,
            height=60
        )
        self.morada_entry.pack(fill="x", pady=(0, 15))

        # Contacto
        ctk.CTkLabel(
            form_frame,
            text="Contacto",
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(anchor="w", pady=(0, 5))

        self.contacto_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="Telefone...",
            height=35
        )
        self.contacto_entry.pack(fill="x", pady=(0, 15))

        # Email
        ctk.CTkLabel(
            form_frame,
            text="Email",
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(anchor="w", pady=(0, 5))

        self.email_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="email@exemplo.pt",
            height=35
        )
        self.email_entry.pack(fill="x", pady=(0, 15))

        # Angariação
        ctk.CTkLabel(
            form_frame,
            text="Angariação",
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(anchor="w", pady=(0, 5))

        self.angariacao_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="Como foi angariado este cliente...",
            height=35
        )
        self.angariacao_entry.pack(fill="x", pady=(0, 15))

        # Nota
        ctk.CTkLabel(
            form_frame,
            text="Nota",
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(anchor="w", pady=(0, 5))

        self.nota_entry = ctk.CTkTextbox(
            form_frame,
            height=80
        )
        self.nota_entry.pack(fill="x", pady=(0, 15))

        # Buttons
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=(20, 0))

        cancel_btn = ctk.CTkButton(
            button_frame,
            text="Cancelar",
            command=self.destroy,
            width=140,
            height=40,
            fg_color="gray",
            hover_color="darkgray"
        )
        cancel_btn.pack(side="left", padx=(0, 10))

        save_btn = ctk.CTkButton(
            button_frame,
            text="Guardar",
            command=self.guardar,
            width=140,
            height=40,
            fg_color=("#2196F3", "#1565C0"),
            hover_color=("#1976D2", "#0D47A1")
        )
        save_btn.pack(side="right")

    def load_cliente_data(self):
        """Load cliente data into form"""
        if not self.cliente:
            return

        self.nome_entry.insert(0, self.cliente.nome)

        if self.cliente.nif:
            self.nif_entry.insert(0, self.cliente.nif)

        if self.cliente.pais:
            self.pais_entry.insert(0, self.cliente.pais)

        if self.cliente.morada:
            self.morada_entry.insert("1.0", self.cliente.morada)

        if self.cliente.contacto:
            self.contacto_entry.insert(0, self.cliente.contacto)

        if self.cliente.email:
            self.email_entry.insert(0, self.cliente.email)

        if self.cliente.angariacao:
            self.angariacao_entry.insert(0, self.cliente.angariacao)

        if self.cliente.nota:
            self.nota_entry.insert("1.0", self.cliente.nota)

    def guardar(self):
        """Save cliente"""
        # Get values
        nome = self.nome_entry.get().strip()
        nif = self.nif_entry.get().strip()
        pais = self.pais_entry.get().strip() or "Portugal"
        morada = self.morada_entry.get("1.0", "end").strip()
        contacto = self.contacto_entry.get().strip()
        email = self.email_entry.get().strip()
        angariacao = self.angariacao_entry.get().strip()
        nota = self.nota_entry.get("1.0", "end").strip()

        # Validate
        if not nome:
            self.show_error("Nome é obrigatório")
            return

        # Create or update
        if self.cliente:
            # Update
            success, cliente, message = self.manager.atualizar(
                self.cliente.id,
                nome=nome,
                nif=nif if nif else None,
                pais=pais,
                morada=morada if morada else None,
                contacto=contacto if contacto else None,
                email=email if email else None,
                angariacao=angariacao if angariacao else None,
                nota=nota if nota else None
            )

            if success:
                self.cliente_atualizado = True
                self.show_success(message)
                self.destroy()
            else:
                self.show_error(message)
        else:
            # Create
            success, cliente, message = self.manager.criar(
                nome=nome,
                nif=nif if nif else None,
                pais=pais,
                morada=morada if morada else None,
                contacto=contacto if contacto else None,
                email=email if email else None,
                angariacao=angariacao if angariacao else None,
                nota=nota if nota else None
            )

            if success:
                self.cliente_criado = True
                self.show_success(message)
                self.destroy()
            else:
                self.show_error(message)

    def show_success(self, message: str):
        """Show success message"""
        dialog = MessageDialog(self, title="Sucesso", message=message, type="success")
        dialog.wait_window()

    def show_error(self, message: str):
        """Show error message"""
        dialog = MessageDialog(self, title="Erro", message=message, type="error")
        dialog.wait_window()


class MessageDialog(ctk.CTkToplevel):
    """Simple message dialog"""

    def __init__(self, parent, title: str, message: str, type: str = "info"):
        super().__init__(parent)

        self.title(title)
        self.geometry("400x200")
        self.resizable(False, False)

        # Make modal
        self.transient(parent)
        self.grab_set()

        # Center
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (400 // 2)
        y = (self.winfo_screenheight() // 2) - (200 // 2)
        self.geometry(f"400x200+{x}+{y}")

        # Icon
        icon = "✅" if type == "success" else "❌" if type == "error" else "ℹ️"

        # Content
        frame = ctk.CTkFrame(self)
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        icon_label = ctk.CTkLabel(
            frame,
            text=icon,
            font=ctk.CTkFont(size=40)
        )
        icon_label.pack(pady=(20, 10))

        message_label = ctk.CTkLabel(
            frame,
            text=message,
            font=ctk.CTkFont(size=14),
            wraplength=350
        )
        message_label.pack(pady=(0, 20))

        ok_btn = ctk.CTkButton(
            frame,
            text="OK",
            command=self.destroy,
            width=120,
            height=35
        )
        ok_btn.pack()


class ConfirmDialog(ctk.CTkToplevel):
    """Confirmation dialog"""

    def __init__(self, parent, title: str, message: str, confirm_text: str = "Confirmar", cancel_text: str = "Cancelar"):
        super().__init__(parent)

        self.confirmed = False

        self.title(title)
        self.geometry("450x220")
        self.resizable(False, False)

        # Make modal
        self.transient(parent)
        self.grab_set()

        # Center
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (450 // 2)
        y = (self.winfo_screenheight() // 2) - (220 // 2)
        self.geometry(f"450x220+{x}+{y}")

        # Content
        frame = ctk.CTkFrame(self)
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        icon_label = ctk.CTkLabel(
            frame,
            text="⚠️",
            font=ctk.CTkFont(size=40)
        )
        icon_label.pack(pady=(20, 10))

        message_label = ctk.CTkLabel(
            frame,
            text=message,
            font=ctk.CTkFont(size=14),
            wraplength=400
        )
        message_label.pack(pady=(0, 20))

        # Buttons
        button_frame = ctk.CTkFrame(frame, fg_color="transparent")
        button_frame.pack(fill="x")

        cancel_btn = ctk.CTkButton(
            button_frame,
            text=cancel_text,
            command=self.cancel,
            width=140,
            height=35,
            fg_color="gray",
            hover_color="darkgray"
        )
        cancel_btn.pack(side="left", expand=True, padx=5)

        confirm_btn = ctk.CTkButton(
            button_frame,
            text=confirm_text,
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
