# -*- coding: utf-8 -*-
"""
Tela de Fornecedores - Gestão de fornecedores/credores
"""
import customtkinter as ctk
from typing import Optional
from sqlalchemy.orm import Session
from logic.fornecedores import FornecedoresManager
from ui.components.data_table import DataTable
from database.models import Fornecedor, EstatutoFornecedor
from datetime import datetime


class FornecedoresScreen(ctk.CTkFrame):
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
        super().__init__(parent, **kwargs)

        self.db_session = db_session
        self.manager = FornecedoresManager(db_session)

        # Configure
        self.configure(fg_color="transparent")

        # Create widgets
        self.create_widgets()

        # Load data
        self.carregar_fornecedores()

    def create_widgets(self):
        """Create screen widgets"""

        # Header
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=30, pady=(30, 20))

        title_label = ctk.CTkLabel(
            header_frame,
            text="🏢 Fornecedores",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        title_label.pack(side="left")

        # Buttons
        button_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        button_frame.pack(side="right")

        refresh_btn = ctk.CTkButton(
            button_frame,
            text="🔄 Atualizar",
            command=self.carregar_fornecedores,
            width=120,
            height=35,
            font=ctk.CTkFont(size=13)
        )
        refresh_btn.pack(side="left", padx=(0, 10))

        add_btn = ctk.CTkButton(
            button_frame,
            text="➕ Novo Fornecedor",
            command=self.adicionar_fornecedor,
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
            placeholder_text="Nome, NIF, Área, Função...",
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

        # Estatuto filter
        ctk.CTkLabel(
            filter_frame,
            text="Estatuto:",
            font=ctk.CTkFont(size=13)
        ).pack(side="left", padx=(20, 10))

        self.estatuto_var = ctk.StringVar(value="TODOS")
        estatuto_menu = ctk.CTkOptionMenu(
            filter_frame,
            variable=self.estatuto_var,
            values=["TODOS", "EMPRESA", "FREELANCER", "ESTADO"],
            command=lambda x: self.carregar_fornecedores(),
            width=130,
            height=35
        )
        estatuto_menu.pack(side="left", padx=(0, 20))

        # Order by
        ctk.CTkLabel(
            filter_frame,
            text="Ordenar:",
            font=ctk.CTkFont(size=13)
        ).pack(side="left", padx=(0, 10))

        self.order_var = ctk.StringVar(value="numero")
        order_menu = ctk.CTkOptionMenu(
            filter_frame,
            variable=self.order_var,
            values=["numero", "nome", "estatuto", "area"],
            command=lambda x: self.carregar_fornecedores(),
            width=120,
            height=35
        )
        order_menu.pack(side="left")

        # Table container
        table_container = ctk.CTkFrame(self)
        table_container.pack(fill="both", expand=True, padx=30, pady=(0, 30))

        # Create table
        columns = [
            {"key": "numero", "label": "Número", "width": 100},
            {"key": "nome", "label": "Nome", "width": 200},
            {"key": "estatuto", "label": "Estatuto", "width": 120},
            {"key": "area", "label": "Área", "width": 150},
            {"key": "funcao", "label": "Função", "width": 150},
            {"key": "classificacao", "label": "★", "width": 60},
            {"key": "contacto", "label": "Contacto", "width": 120},
            {"key": "despesas_count", "label": "Despesas", "width": 80},
        ]

        self.table = DataTable(
            table_container,
            columns=columns,
            on_edit=self.editar_fornecedor,
            on_delete=self.apagar_fornecedor
        )
        self.table.pack(fill="both", expand=True)

    def carregar_fornecedores(self):
        """Load and display fornecedores"""
        # Get filters
        estatuto_str = self.estatuto_var.get()
        estatuto = None if estatuto_str == "TODOS" else EstatutoFornecedor[estatuto_str]
        order_by = self.order_var.get()

        fornecedores = self.manager.listar_todos(estatuto=estatuto, order_by=order_by)

        # Prepare data
        data = []
        for fornecedor in fornecedores:
            data.append({
                "id": fornecedor.id,
                "numero": fornecedor.numero,
                "nome": fornecedor.nome,
                "estatuto": fornecedor.estatuto.value if fornecedor.estatuto else "-",
                "area": fornecedor.area or "-",
                "funcao": fornecedor.funcao or "-",
                "classificacao": "★" * fornecedor.classificacao if fornecedor.classificacao else "-",
                "contacto": fornecedor.contacto or "-",
                "despesas_count": str(len(fornecedor.despesas))
            })

        self.table.set_data(data)

    def pesquisar(self):
        """Search fornecedores"""
        termo = self.search_entry.get().strip()

        if not termo:
            self.carregar_fornecedores()
            return

        fornecedores = self.manager.pesquisar(termo)

        # Prepare data
        data = []
        for fornecedor in fornecedores:
            data.append({
                "id": fornecedor.id,
                "numero": fornecedor.numero,
                "nome": fornecedor.nome,
                "estatuto": fornecedor.estatuto.value if fornecedor.estatuto else "-",
                "area": fornecedor.area or "-",
                "funcao": fornecedor.funcao or "-",
                "classificacao": "★" * fornecedor.classificacao if fornecedor.classificacao else "-",
                "contacto": fornecedor.contacto or "-",
                "despesas_count": str(len(fornecedor.despesas))
            })

        self.table.set_data(data)

    def limpar_pesquisa(self):
        """Clear search"""
        self.search_entry.delete(0, "end")
        self.carregar_fornecedores()

    def adicionar_fornecedor(self):
        """Show dialog to add new fornecedor"""
        dialog = FormularioFornecedorDialog(self, self.db_session)
        dialog.wait_window()

        # Reload if fornecedor was created
        if dialog.fornecedor_criado:
            self.carregar_fornecedores()

    def editar_fornecedor(self, fornecedor_id: int):
        """Show dialog to edit fornecedor"""
        fornecedor = self.manager.buscar_por_id(fornecedor_id)
        if not fornecedor:
            self.show_error("Fornecedor não encontrado")
            return

        dialog = FormularioFornecedorDialog(self, self.db_session, fornecedor=fornecedor)
        dialog.wait_window()

        # Reload if fornecedor was updated
        if dialog.fornecedor_atualizado:
            self.carregar_fornecedores()

    def apagar_fornecedor(self, fornecedor_id: int):
        """Delete fornecedor"""
        fornecedor = self.manager.buscar_por_id(fornecedor_id)
        if not fornecedor:
            self.show_error("Fornecedor não encontrado")
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
            self.show_success(message)
            self.carregar_fornecedores()
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


class FormularioFornecedorDialog(ctk.CTkToplevel):
    """
    Dialog for creating/editing fornecedor
    """

    def __init__(self, parent, db_session: Session, fornecedor: Optional[Fornecedor] = None):
        super().__init__(parent)

        self.db_session = db_session
        self.manager = FornecedoresManager(db_session)
        self.fornecedor = fornecedor
        self.fornecedor_criado = False
        self.fornecedor_atualizado = False

        # Configure window
        self.title("Editar Fornecedor" if fornecedor else "Novo Fornecedor")
        self.geometry("600x800")
        self.resizable(False, False)

        # Make modal
        self.transient(parent)
        self.grab_set()

        # Center window
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (600 // 2)
        y = (self.winfo_screenheight() // 2) - (800 // 2)
        self.geometry(f"600x800+{x}+{y}")

        # Create widgets
        self.create_widgets()

        # Load data if editing
        if self.fornecedor:
            self.load_fornecedor_data()

    def create_widgets(self):
        """Create dialog widgets"""

        # Main container
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Title
        title = ctk.CTkLabel(
            main_frame,
            text="✏️ Editar Fornecedor" if self.fornecedor else "➕ Novo Fornecedor",
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
            placeholder_text="Nome do fornecedor...",
            height=35
        )
        self.nome_entry.pack(fill="x", pady=(0, 15))

        # Estatuto (required)
        ctk.CTkLabel(
            form_frame,
            text="Estatuto *",
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(anchor="w", pady=(0, 5))

        self.estatuto_var = ctk.StringVar(value="FREELANCER")
        estatuto_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        estatuto_frame.pack(fill="x", pady=(0, 15))

        for estatuto in ["EMPRESA", "FREELANCER", "ESTADO"]:
            ctk.CTkRadioButton(
                estatuto_frame,
                text=estatuto,
                variable=self.estatuto_var,
                value=estatuto
            ).pack(side="left", padx=(0, 20))

        # Área
        ctk.CTkLabel(
            form_frame,
            text="Área",
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(anchor="w", pady=(0, 5))

        self.area_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="Ex: Produção, Pós-produção, Som...",
            height=35
        )
        self.area_entry.pack(fill="x", pady=(0, 15))

        # Função
        ctk.CTkLabel(
            form_frame,
            text="Função",
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(anchor="w", pady=(0, 5))

        self.funcao_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="Ex: Técnico de som, Editor, Realizador...",
            height=35
        )
        self.funcao_entry.pack(fill="x", pady=(0, 15))

        # Classificação
        ctk.CTkLabel(
            form_frame,
            text="Classificação (1-5 estrelas)",
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(anchor="w", pady=(0, 5))

        self.classificacao_var = ctk.StringVar(value="0")
        class_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        class_frame.pack(fill="x", pady=(0, 15))

        for i in range(6):
            text = "Nenhuma" if i == 0 else "★" * i
            ctk.CTkRadioButton(
                class_frame,
                text=text,
                variable=self.classificacao_var,
                value=str(i)
            ).pack(side="left", padx=(0, 15))

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

        # IBAN
        ctk.CTkLabel(
            form_frame,
            text="IBAN",
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(anchor="w", pady=(0, 5))

        self.iban_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="PT50...",
            height=35
        )
        self.iban_entry.pack(fill="x", pady=(0, 15))

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

        # Validade Seguro Trabalho
        ctk.CTkLabel(
            form_frame,
            text="Validade Seguro Trabalho",
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(anchor="w", pady=(0, 5))

        self.seguro_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="AAAA-MM-DD",
            height=35
        )
        self.seguro_entry.pack(fill="x", pady=(0, 15))

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

    def load_fornecedor_data(self):
        """Load fornecedor data into form"""
        if not self.fornecedor:
            return

        self.nome_entry.insert(0, self.fornecedor.nome)

        if self.fornecedor.estatuto:
            self.estatuto_var.set(self.fornecedor.estatuto.value)

        if self.fornecedor.area:
            self.area_entry.insert(0, self.fornecedor.area)

        if self.fornecedor.funcao:
            self.funcao_entry.insert(0, self.fornecedor.funcao)

        if self.fornecedor.classificacao:
            self.classificacao_var.set(str(self.fornecedor.classificacao))

        if self.fornecedor.nif:
            self.nif_entry.insert(0, self.fornecedor.nif)

        if self.fornecedor.iban:
            self.iban_entry.insert(0, self.fornecedor.iban)

        if self.fornecedor.morada:
            self.morada_entry.insert("1.0", self.fornecedor.morada)

        if self.fornecedor.contacto:
            self.contacto_entry.insert(0, self.fornecedor.contacto)

        if self.fornecedor.email:
            self.email_entry.insert(0, self.fornecedor.email)

        if self.fornecedor.validade_seguro_trabalho:
            self.seguro_entry.insert(0, self.fornecedor.validade_seguro_trabalho.strftime("%Y-%m-%d"))

        if self.fornecedor.nota:
            self.nota_entry.insert("1.0", self.fornecedor.nota)

    def guardar(self):
        """Save fornecedor"""
        # Get values
        nome = self.nome_entry.get().strip()
        estatuto_str = self.estatuto_var.get()
        area = self.area_entry.get().strip()
        funcao = self.funcao_entry.get().strip()
        classificacao = int(self.classificacao_var.get())
        nif = self.nif_entry.get().strip()
        iban = self.iban_entry.get().strip()
        morada = self.morada_entry.get("1.0", "end").strip()
        contacto = self.contacto_entry.get().strip()
        email = self.email_entry.get().strip()
        seguro_str = self.seguro_entry.get().strip()
        nota = self.nota_entry.get("1.0", "end").strip()

        # Validate
        if not nome:
            self.show_error("Nome é obrigatório")
            return

        # Parse estatuto
        try:
            estatuto = EstatutoFornecedor[estatuto_str]
        except:
            self.show_error("Estatuto inválido")
            return

        # Parse seguro date
        validade_seguro = None
        if seguro_str:
            try:
                validade_seguro = datetime.strptime(seguro_str, "%Y-%m-%d")
            except:
                self.show_error("Data de validade do seguro inválida (use AAAA-MM-DD)")
                return

        # Create or update
        if self.fornecedor:
            # Update
            success, fornecedor, message = self.manager.atualizar(
                self.fornecedor.id,
                nome=nome,
                estatuto=estatuto,
                area=area if area else None,
                funcao=funcao if funcao else None,
                classificacao=classificacao if classificacao > 0 else None,
                nif=nif if nif else None,
                iban=iban if iban else None,
                morada=morada if morada else None,
                contacto=contacto if contacto else None,
                email=email if email else None,
                validade_seguro_trabalho=validade_seguro,
                nota=nota if nota else None
            )

            if success:
                self.fornecedor_atualizado = True
                self.show_success(message)
                self.destroy()
            else:
                self.show_error(message)
        else:
            # Create
            success, fornecedor, message = self.manager.criar(
                nome=nome,
                estatuto=estatuto,
                area=area if area else None,
                funcao=funcao if funcao else None,
                classificacao=classificacao if classificacao > 0 else None,
                nif=nif if nif else None,
                iban=iban if iban else None,
                morada=morada if morada else None,
                contacto=contacto if contacto else None,
                email=email if email else None,
                validade_seguro_trabalho=validade_seguro,
                nota=nota if nota else None
            )

            if success:
                self.fornecedor_criado = True
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
