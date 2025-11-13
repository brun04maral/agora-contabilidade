# -*- coding: utf-8 -*-
"""
Tela de Fornecedores - Gestão de fornecedores/credores
"""
import customtkinter as ctk
from typing import Optional
from sqlalchemy.orm import Session
from logic.fornecedores import FornecedoresManager
from ui.components.data_table_v2 import DataTableV2
from database.models import Fornecedor, EstatutoFornecedor
from datetime import datetime
from tkinter import messagebox
import csv
from assets.resources import get_icon, FORNECEDORES


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

        # Title with PNG icon
        icon_pil = get_icon(FORNECEDORES, size=(28, 28))
        if icon_pil:
            icon_ctk = ctk.CTkImage(
                light_image=icon_pil,
                dark_image=icon_pil,
                size=(28, 28)
            )
            title_label = ctk.CTkLabel(
                header_frame,
                image=icon_ctk,
                text=" Fornecedores",
                compound="left",
                font=ctk.CTkFont(size=28, weight="bold")
            )
        else:
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

        # Selection actions bar (created but NOT packed - will be shown on selection)
        self.selection_frame = ctk.CTkFrame(self, fg_color="transparent")

        # Clear selection button
        self.cancel_btn = ctk.CTkButton(
            self.selection_frame,
            text="🗑️ Limpar Seleção",
            command=self.cancelar_selecao,
            width=150, height=35
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
            {"key": "nome", "label": "Nome", "width": 250},
            {"key": "estatuto", "label": "Estatuto", "width": 120},
            {"key": "area", "label": "Área", "width": 150},
            {"key": "funcao", "label": "Função", "width": 150},
            {"key": "classificacao", "label": "★", "width": 80},
            {"key": "despesas_count", "label": "Despesas", "width": 100},
        ]

        self.table = DataTableV2(
            table_container,
            columns=columns,
            on_row_double_click=self.on_double_click,
            on_selection_change=self.on_selection_change
        )
        self.table.pack(fill="both", expand=True)

    def get_estatuto_color(self, estatuto: EstatutoFornecedor) -> tuple:
        """Get color for estatuto (tonalidades diferentes da mesma cor)"""
        color_map = {
            EstatutoFornecedor.EMPRESA: ("#B3D9FF", "#5A8BB8"),      # Azul claro
            EstatutoFornecedor.FREELANCER: ("#99CCFF", "#4D7A99"),  # Azul médio
            EstatutoFornecedor.ESTADO: ("#80BFFF", "#406B8B")        # Azul escuro
        }
        return color_map.get(estatuto, ("#E0E0E0", "#4A4A4A"))

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
            color = self.get_estatuto_color(fornecedor.estatuto) if fornecedor.estatuto else ("#E0E0E0", "#4A4A4A")
            data.append({
                "id": fornecedor.id,
                "numero": fornecedor.numero,
                "nome": fornecedor.nome,
                "estatuto": fornecedor.estatuto.value if fornecedor.estatuto else "-",
                "area": fornecedor.area or "-",
                "funcao": fornecedor.funcao or "-",
                "classificacao": "★" * fornecedor.classificacao if fornecedor.classificacao else "-",
                "despesas_count": len(fornecedor.despesas),  # Keep as integer for proper sorting
                "_bg_color": color,
                "_fornecedor": fornecedor
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
            color = self.get_estatuto_color(fornecedor.estatuto) if fornecedor.estatuto else ("#E0E0E0", "#4A4A4A")
            data.append({
                "id": fornecedor.id,
                "numero": fornecedor.numero,
                "nome": fornecedor.nome,
                "estatuto": fornecedor.estatuto.value if fornecedor.estatuto else "-",
                "area": fornecedor.area or "-",
                "funcao": fornecedor.funcao or "-",
                "classificacao": "★" * fornecedor.classificacao if fornecedor.classificacao else "-",
                "despesas_count": len(fornecedor.despesas),  # Keep as integer for proper sorting
                "_bg_color": color,
                "_fornecedor": fornecedor
            })

        self.table.set_data(data)

    def limpar_pesquisa(self):
        """Clear search"""
        self.search_entry.delete(0, "end")
        self.carregar_fornecedores()

    def on_selection_change(self, selected_data: list):
        """Handle selection change in table"""
        num_selected = len(selected_data)

        if num_selected > 0:
            # Show selection frame
            self.selection_frame.pack(fill="x", padx=30, pady=(0, 10))
            self.cancel_btn.pack(side="left", padx=(0, 10))
            self.export_btn.pack(side="left", padx=(0, 20))
            self.count_label.configure(text=f"{num_selected} fornecedor(es) selecionado(s)")
            self.count_label.pack(side="left")
        else:
            # Hide entire selection frame when nothing is selected
            self.selection_frame.pack_forget()

    def on_double_click(self, data: dict):
        """Handle double click - open for edit"""
        fornecedor_id = data.get("id")
        if fornecedor_id:
            self.editar_fornecedor(fornecedor_id)

    def cancelar_selecao(self):
        """Clear selection"""
        self.table.clear_selection()

    def exportar_selecionados(self):
        """Export selected fornecedores to CSV"""
        selected_data = self.table.get_selected_data()

        if not selected_data:
            messagebox.showwarning("Aviso", "Nenhum fornecedor selecionado")
            return

        # Prepare filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"fornecedores_export_{timestamp}.csv"

        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['Número', 'Nome', 'Estatuto', 'Área', 'Função', 'Classificação', 'NIF', 'Contacto', 'Email', 'Despesas']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                writer.writeheader()
                for item in selected_data:
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

            messagebox.showinfo(
                "Sucesso",
                f"Exportados {len(selected_data)} fornecedor(es) para {filename}"
            )
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao exportar: {str(e)}")

    def adicionar_fornecedor(self):
        """Show dialog to add new fornecedor"""
        dialog = FormularioFornecedorDialog(self, self.db_session)
        dialog.wait_window()

        # Reload if fornecedor was created
        if dialog.fornecedor_criado:
            self.carregar_fornecedores()
            self.table.clear_selection()

    def editar_fornecedor(self, fornecedor_id: int):
        """Show dialog to edit fornecedor"""
        fornecedor = self.manager.buscar_por_id(fornecedor_id)
        if not fornecedor:
            self.show_error("Fornecedor não encontrado")
            return

        dialog = FormularioFornecedorDialog(self, self.db_session, fornecedor=fornecedor)
        dialog.wait_window()

        # Clear selection after closing dialog (whether updated or cancelled)
        self.table.clear_selection()

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

        from ui.components.date_picker_dropdown import DatePickerDropdown
        self.seguro_picker = DatePickerDropdown(
            form_frame,
            placeholder="Selecionar data de validade do seguro..."
        )
        self.seguro_picker.pack(fill="x", pady=(0, 15))

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
            # validade_seguro_trabalho é datetime, converter para date
            if hasattr(self.fornecedor.validade_seguro_trabalho, 'date'):
                self.seguro_picker.set_date(self.fornecedor.validade_seguro_trabalho.date())
            else:
                self.seguro_picker.set_date(self.fornecedor.validade_seguro_trabalho)

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
        if self.seguro_picker.get():
            # Converter date para datetime (BD espera datetime)
            seguro_date = self.seguro_picker.get_date()
            validade_seguro = datetime.combine(seguro_date, datetime.min.time())

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
