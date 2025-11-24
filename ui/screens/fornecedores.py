# -*- coding: utf-8 -*-
"""
Tela de Fornecedores - Gestão de fornecedores/credores
"""
import customtkinter as ctk
from sqlalchemy.orm import Session
from logic.fornecedores import FornecedoresManager
from ui.components.data_table_v2 import DataTableV2
from database.models import EstatutoFornecedor
from datetime import datetime
from tkinter import messagebox
import csv
from assets.resources import get_icon, FORNECEDORES
from utils.base_dialogs import BaseDialogMedium


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
            self.carregar_fornecedores()
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
