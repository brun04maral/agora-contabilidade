# -*- coding: utf-8 -*-
"""
Tela de gestão de Projetos
"""
import customtkinter as ctk
from typing import Optional
from sqlalchemy.orm import Session
from datetime import date
from decimal import Decimal
import tkinter.messagebox as messagebox

from logic.projetos import ProjetosManager
from logic.clientes import ClientesManager
from database.models import TipoProjeto, EstadoProjeto
from ui.components.data_table_v2 import DataTableV2
from assets.resources import get_icon, PROJETOS


class ProjetosScreen(ctk.CTkFrame):
    """
    Tela de gestão de Projetos (CRUD completo)
    """

    def __init__(self, parent, db_session: Session, filtro_estado=None, filtro_cliente_id=None, **kwargs):
        """
        Initialize projetos screen

        Args:
            parent: Parent widget
            db_session: SQLAlchemy database session
            filtro_estado: Optional initial estado filter
            filtro_cliente_id: Optional initial cliente filter (cliente ID)
        """
        super().__init__(parent, **kwargs)

        self.db_session = db_session
        self.manager = ProjetosManager(db_session)
        self.clientes_manager = ClientesManager(db_session)
        self.projeto_editando = None
        self.filtro_inicial_estado = filtro_estado
        self.filtro_inicial_cliente_id = filtro_cliente_id

        # Configure
        self.configure(fg_color="transparent")

        # Create widgets
        self.create_widgets()

        # Apply initial filter if provided
        if self.filtro_inicial_estado or self.filtro_inicial_cliente_id:
            if self.filtro_inicial_estado:
                self.estado_filter.set(self.filtro_inicial_estado)
            if self.filtro_inicial_cliente_id:
                # Find cliente in list and set filter
                for cliente in self.clientes_list:
                    if cliente.id == self.filtro_inicial_cliente_id:
                        self.cliente_filter.set(cliente.nome)
                        break
            self.aplicar_filtros()
        else:
            # Load data
            self.carregar_projetos()

    def create_widgets(self):
        """Create screen widgets"""

        # Header
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=30, pady=(30, 20))

        # Title with PNG icon
        icon_pil = get_icon(PROJETOS, size=(28, 28))
        if icon_pil:
            icon_ctk = ctk.CTkImage(
                light_image=icon_pil,
                dark_image=icon_pil,
                size=(28, 28)
            )
            title_label = ctk.CTkLabel(
                header_frame,
                image=icon_ctk,
                text=" Projetos",
                compound="left",
                font=ctk.CTkFont(size=28, weight="bold")
            )
        else:
            title_label = ctk.CTkLabel(
                header_frame,
                text="📁 Projetos",
                font=ctk.CTkFont(size=28, weight="bold")
            )
        title_label.pack(side="left")

        # Buttons
        btn_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        btn_frame.pack(side="right")

        refresh_btn = ctk.CTkButton(
            btn_frame,
            text="🔄 Atualizar",
            command=self.carregar_projetos,
            width=120,
            height=35,
            font=ctk.CTkFont(size=13)
        )
        refresh_btn.pack(side="left", padx=5)

        novo_btn = ctk.CTkButton(
            btn_frame,
            text="➕ Novo Projeto",
            command=self.abrir_formulario,
            width=140,
            height=35,
            font=ctk.CTkFont(size=13),
            fg_color=("#4CAF50", "#388E3C"),
            hover_color=("#66BB6A", "#2E7D32")
        )
        novo_btn.pack(side="left", padx=5)

        # Filters
        filters_frame = ctk.CTkFrame(self, fg_color="transparent")
        filters_frame.pack(fill="x", padx=30, pady=(0, 20))

        # Cliente filter
        ctk.CTkLabel(
            filters_frame,
            text="Cliente:",
            font=ctk.CTkFont(size=13)
        ).pack(side="left", padx=(0, 10))

        # Get all clients
        clientes = self.clientes_manager.listar_todos(order_by='nome')
        cliente_values = ["Todos"] + [c.nome for c in clientes]
        self.clientes_list = clientes  # Store for later lookup

        self.cliente_filter = ctk.CTkOptionMenu(
            filters_frame,
            values=cliente_values,
            command=self.aplicar_filtros,
            width=220
        )
        self.cliente_filter.pack(side="left", padx=(0, 20))

        # Tipo filter
        ctk.CTkLabel(
            filters_frame,
            text="Tipo:",
            font=ctk.CTkFont(size=13)
        ).pack(side="left", padx=(0, 10))

        self.tipo_filter = ctk.CTkOptionMenu(
            filters_frame,
            values=["Todos", "Empresa", "Pessoal BA", "Pessoal RR"],
            command=self.aplicar_filtros,
            width=180
        )
        self.tipo_filter.pack(side="left", padx=(0, 20))

        # Estado filter
        ctk.CTkLabel(
            filters_frame,
            text="Estado:",
            font=ctk.CTkFont(size=13)
        ).pack(side="left", padx=(0, 10))

        self.estado_filter = ctk.CTkOptionMenu(
            filters_frame,
            values=["Todos", "Não Faturado", "Faturado", "Recebido", "Anulado"],
            command=self.aplicar_filtros,
            width=150
        )
        self.estado_filter.pack(side="left")

        # Selection actions bar (created but NOT packed - will be shown on selection)
        self.selection_frame = ctk.CTkFrame(self, fg_color="transparent")

        # Clear selection button
        self.cancel_btn = ctk.CTkButton(
            self.selection_frame,
            text="🗑️ Limpar Seleção",
            command=self.cancelar_selecao,
            width=150,
            height=35,
            font=ctk.CTkFont(size=13),
            fg_color=("#757575", "#616161"),
            hover_color=("#9E9E9E", "#757575")
        )

        # Selection count label
        self.count_label = ctk.CTkLabel(
            self.selection_frame,
            text="0 selecionados",
            font=ctk.CTkFont(size=13)
        )

        # Report button
        self.report_btn = ctk.CTkButton(
            self.selection_frame,
            text="📊 Criar Relatório",
            command=self.criar_relatorio,
            width=160,
            height=35,
            font=ctk.CTkFont(size=13),
            fg_color=("#9C27B0", "#7B1FA2"),
            hover_color=("#AB47BC", "#6A1B9A")
        )

        # Total label
        self.total_label = ctk.CTkLabel(
            self.selection_frame,
            text="Total: €0,00",
            font=ctk.CTkFont(size=14, weight="bold")
        )

        # Table
        columns = [
            {'key': 'numero', 'label': 'ID', 'width': 80},
            {'key': 'tipo', 'label': 'Tipo', 'width': 140},
            {'key': 'cliente_nome', 'label': 'Cliente', 'width': 180},
            {'key': 'descricao', 'label': 'Descrição', 'width': 280, 'sortable': False},
            {'key': 'valor_sem_iva', 'label': 'Valor', 'width': 100,
             'formatter': lambda v: f"€{v:,.2f}" if v else "€0,00"},
            {'key': 'estado', 'label': 'Estado', 'width': 120},
        ]

        self.table = DataTableV2(
            self,
            columns=columns,
            height=400,
            on_row_double_click=self.editar_projeto,
            on_selection_change=self.on_selection_change
        )
        self.table.pack(fill="both", expand=True, padx=30, pady=(0, 30))

    def carregar_projetos(self):
        """Load and display projects (respecting active filters)"""
        # If we have active filters, apply them instead of loading all
        if self.cliente_filter.get() != "Todos" or self.tipo_filter.get() != "Todos" or self.estado_filter.get() != "Todos":
            self.aplicar_filtros()
        else:
            # No filters active, load all
            projetos = self.manager.listar_todos()
            data = [self.projeto_to_dict(p) for p in projetos]
            self.table.set_data(data)

    def projeto_to_dict(self, projeto) -> dict:
        """Convert project to dict for table"""
        return {
            'id': projeto.id,
            'numero': projeto.numero,
            'tipo': self.tipo_to_label(projeto.tipo),
            'cliente_nome': projeto.cliente.nome if projeto.cliente else '-',
            'descricao': projeto.descricao,  # DataTableV2 will truncate automatically with tooltip
            'valor_sem_iva': float(projeto.valor_sem_iva),
            'estado': self.estado_to_label(projeto.estado),
            '_bg_color': self.estado_to_color(projeto.estado),  # Color by estado
            '_projeto': projeto  # Keep reference
        }

    def tipo_to_label(self, tipo: TipoProjeto) -> str:
        """Convert tipo enum to label"""
        mapping = {
            TipoProjeto.EMPRESA: "Empresa",
            TipoProjeto.PESSOAL_BRUNO: "Pessoal BA",
            TipoProjeto.PESSOAL_RAFAEL: "Pessoal RR"
        }
        return mapping.get(tipo, str(tipo))

    def estado_to_label(self, estado: EstadoProjeto) -> str:
        """Convert estado enum to label"""
        mapping = {
            EstadoProjeto.NAO_FATURADO: "Não Faturado",
            EstadoProjeto.FATURADO: "Faturado",
            EstadoProjeto.RECEBIDO: "Recebido",
            EstadoProjeto.ANULADO: "Anulado"
        }
        return mapping.get(estado, str(estado))

    def estado_to_color(self, estado: EstadoProjeto) -> tuple:
        """Convert estado enum to pastel background color (light, dark)"""
        mapping = {
            EstadoProjeto.NAO_FATURADO: ("#FFB3BA", "#8B5A5E"),  # Pastel red
            EstadoProjeto.FATURADO: ("#FFFFBA", "#B8B85A"),     # Pastel yellow
            EstadoProjeto.RECEBIDO: ("#BAFFC9", "#5A8B63"),     # Pastel green
            EstadoProjeto.ANULADO: ("#808080", "#505050")       # Dark gray
        }
        return mapping.get(estado, ("#f8f8f8", "#252525"))

    def aplicar_filtros(self, *args):
        """Apply filters"""
        cliente = self.cliente_filter.get()
        tipo = self.tipo_filter.get()
        estado = self.estado_filter.get()

        # Get all projects
        projetos = self.manager.listar_todos()

        # Filter by cliente
        if cliente != "Todos":
            # Find cliente by name
            cliente_obj = next((c for c in self.clientes_list if c.nome == cliente), None)
            if cliente_obj:
                projetos = [p for p in projetos if p.cliente_id == cliente_obj.id]

        # Filter by tipo
        if tipo != "Todos":
            tipo_map = {
                "Empresa": TipoProjeto.EMPRESA,
                "Pessoal BA": TipoProjeto.PESSOAL_BRUNO,
                "Pessoal RR": TipoProjeto.PESSOAL_RAFAEL
            }
            tipo_enum = tipo_map[tipo]
            projetos = [p for p in projetos if p.tipo == tipo_enum]

        # Filter by estado
        if estado != "Todos":
            estado_map = {
                "Não Faturado": EstadoProjeto.NAO_FATURADO,
                "Faturado": EstadoProjeto.FATURADO,
                "Recebido": EstadoProjeto.RECEBIDO,
                "Anulado": EstadoProjeto.ANULADO
            }
            estado_enum = estado_map[estado]
            projetos = [p for p in projetos if p.estado == estado_enum]

        # Update table
        data = [self.projeto_to_dict(p) for p in projetos]
        self.table.set_data(data)

    def abrir_formulario(self, projeto=None):
        """Open form dialog for create/edit"""
        FormularioProjetoDialog(self, self.manager, projeto, self.carregar_projetos)

    def editar_projeto(self, data: dict):
        """Edit project"""
        projeto = data.get('_projeto')
        if projeto:
            self.abrir_formulario(projeto)

    def apagar_projeto(self, data: dict):
        """Delete project"""
        projeto = data.get('_projeto')
        if not projeto:
            return

        # Confirm deletion
        resposta = messagebox.askyesno(
            "Confirmar",
            f"Tem certeza que deseja apagar o projeto {projeto.numero}?\n\n"
            f"⚠️ ATENÇÃO: Isto vai afetar os cálculos de Saldos Pessoais!",
            icon='warning'
        )

        if resposta:
            sucesso, erro = self.manager.apagar(projeto.id)
            if sucesso:
                messagebox.showinfo("Sucesso", "Projeto apagado com sucesso!")
                self.carregar_projetos()
            else:
                messagebox.showerror("Erro", f"Erro ao apagar projeto: {erro}")

    def on_selection_change(self, selected_data: list):
        """Handle selection change in table"""
        num_selected = len(selected_data)

        if num_selected > 0:
            # Show selection frame
            self.selection_frame.pack(fill="x", padx=30, pady=(0, 10))

            # Show selection bar
            self.cancel_btn.pack(side="left", padx=5)

            # Show count
            count_text = f"{num_selected} selecionado" if num_selected == 1 else f"{num_selected} selecionados"
            self.count_label.configure(text=count_text)
            self.count_label.pack(side="left", padx=15)

            self.report_btn.pack(side="left", padx=5)

            # Calculate and show total
            total = sum(item.get('valor_sem_iva', 0) for item in selected_data)
            self.total_label.configure(text=f"Total: €{total:,.2f}")
            self.total_label.pack(side="left", padx=20)
        else:
            # Hide entire selection frame when nothing is selected
            self.selection_frame.pack_forget()

    def cancelar_selecao(self):
        """Cancel selection"""
        self.table.clear_selection()

    def criar_relatorio(self):
        """Create report for selected projects and navigate to Relatorios tab"""
        selected_data = self.table.get_selected_data()
        if len(selected_data) > 0:
            # Extract project IDs from selected data
            projeto_ids = [item.get('id') for item in selected_data if item.get('id')]

            # Navigate to Relatorios tab
            # Hierarchy: self (ProjetosScreen) -> master (content_frame) -> master (MainWindow)
            main_window = self.master.master
            if hasattr(main_window, 'show_relatorios'):
                main_window.show_relatorios(projeto_ids=projeto_ids)
            else:
                messagebox.showerror(
                    "Erro",
                    "Não foi possível navegar para a aba de Relatórios"
                )


class FormularioProjetoDialog(ctk.CTkToplevel):
    """
    Dialog para criar/editar projetos
    """

    def __init__(self, parent, manager: ProjetosManager, projeto=None, callback=None):
        super().__init__(parent)

        self.manager = manager
        self.projeto = projeto
        self.callback = callback

        # Configure window
        self.title("Novo Projeto" if not projeto else f"Editar Projeto {projeto.numero}")
        self.geometry("600x700")

        # Make modal
        self.transient(parent)
        self.grab_set()

        # Create form
        self.create_form()

        # Load data if editing
        if projeto:
            self.carregar_dados()

    def create_form(self):
        """Create form fields"""

        # Scrollable container
        scroll = ctk.CTkScrollableFrame(self)
        scroll.pack(fill="both", expand=True, padx=25, pady=25)

        # Tipo
        ctk.CTkLabel(scroll, text="Tipo *", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", pady=(5, 8))
        self.tipo_var = ctk.StringVar(value="Empresa")
        tipo_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        tipo_frame.pack(fill="x", pady=(0, 18))

        ctk.CTkRadioButton(tipo_frame, text="Empresa", variable=self.tipo_var, value="EMPRESA").pack(side="left", padx=(0, 20))
        ctk.CTkRadioButton(tipo_frame, text="Pessoal BA", variable=self.tipo_var, value="PESSOAL_BRUNO").pack(side="left", padx=(0, 20))
        ctk.CTkRadioButton(tipo_frame, text="Pessoal RR", variable=self.tipo_var, value="PESSOAL_RAFAEL").pack(side="left")

        # Cliente
        ctk.CTkLabel(scroll, text="Cliente", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", pady=(5, 8))
        clientes = self.manager.obter_clientes()
        cliente_options = ["(Nenhum)"] + [f"{c.numero} - {c.nome}" for c in clientes]
        self.cliente_dropdown = ctk.CTkOptionMenu(scroll, values=cliente_options, width=400, height=35)
        self.cliente_dropdown.pack(anchor="w", pady=(0, 18))
        self.clientes_map = {f"{c.numero} - {c.nome}": c.id for c in clientes}

        # Descrição
        ctk.CTkLabel(scroll, text="Descrição *", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", pady=(5, 8))
        self.descricao_entry = ctk.CTkTextbox(scroll, height=90)
        self.descricao_entry.pack(fill="x", pady=(0, 18))

        # Valor
        ctk.CTkLabel(scroll, text="Valor sem IVA *", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", pady=(5, 8))
        self.valor_entry = ctk.CTkEntry(scroll, placeholder_text="0.00", height=35)
        self.valor_entry.pack(fill="x", pady=(0, 18))

        # Datas
        datas_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        datas_frame.pack(fill="x", pady=(5, 18))
        datas_frame.grid_columnconfigure((0, 1), weight=1)

        # Data início
        ctk.CTkLabel(datas_frame, text="Data Início", font=ctk.CTkFont(size=14, weight="bold")).grid(row=0, column=0, sticky="w", padx=(0, 12))
        self.data_inicio_entry = ctk.CTkEntry(datas_frame, placeholder_text="AAAA-MM-DD", height=35)
        self.data_inicio_entry.grid(row=1, column=0, sticky="ew", padx=(0, 12), pady=(8, 12))

        # Data fim
        ctk.CTkLabel(datas_frame, text="Data Fim", font=ctk.CTkFont(size=14, weight="bold")).grid(row=0, column=1, sticky="w")
        self.data_fim_entry = ctk.CTkEntry(datas_frame, placeholder_text="AAAA-MM-DD", height=35)
        self.data_fim_entry.grid(row=1, column=1, sticky="ew", pady=(8, 12))

        # Data faturação
        ctk.CTkLabel(datas_frame, text="Data Faturação", font=ctk.CTkFont(size=14, weight="bold")).grid(row=2, column=0, sticky="w", padx=(0, 12))
        self.data_faturacao_entry = ctk.CTkEntry(datas_frame, placeholder_text="AAAA-MM-DD", height=35)
        self.data_faturacao_entry.grid(row=3, column=0, sticky="ew", padx=(0, 12), pady=(8, 12))

        # Data vencimento
        ctk.CTkLabel(datas_frame, text="Data Vencimento", font=ctk.CTkFont(size=14, weight="bold")).grid(row=2, column=1, sticky="w")
        self.data_vencimento_entry = ctk.CTkEntry(datas_frame, placeholder_text="AAAA-MM-DD", height=35)
        self.data_vencimento_entry.grid(row=3, column=1, sticky="ew", pady=(8, 12))

        # Estado
        ctk.CTkLabel(scroll, text="Estado *", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", pady=(5, 8))
        self.estado_dropdown = ctk.CTkOptionMenu(scroll, values=["Não Faturado", "Faturado", "Recebido", "Anulado"], height=35)
        self.estado_dropdown.pack(anchor="w", pady=(0, 18))

        # Prémios (só para projetos EMPRESA)
        premios_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        premios_frame.pack(fill="x", pady=(5, 18))
        premios_frame.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(premios_frame, text="Prémio BA (€)", font=ctk.CTkFont(size=14, weight="bold")).grid(row=0, column=0, sticky="w", padx=(0, 12))
        self.premio_bruno_entry = ctk.CTkEntry(premios_frame, placeholder_text="0.00", height=35)
        self.premio_bruno_entry.grid(row=1, column=0, sticky="ew", padx=(0, 12), pady=(8, 0))

        ctk.CTkLabel(premios_frame, text="Prémio RR (€)", font=ctk.CTkFont(size=14, weight="bold")).grid(row=0, column=1, sticky="w")
        self.premio_rafael_entry = ctk.CTkEntry(premios_frame, placeholder_text="0.00", height=35)
        self.premio_rafael_entry.grid(row=1, column=1, sticky="ew", pady=(8, 0))

        # Nota
        ctk.CTkLabel(scroll, text="Nota", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", pady=(5, 8))
        self.nota_entry = ctk.CTkTextbox(scroll, height=70)
        self.nota_entry.pack(fill="x", pady=(0, 10))

        # Buttons
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=25, pady=(0, 25))

        cancel_btn = ctk.CTkButton(
            btn_frame,
            text="Cancelar",
            command=self.destroy,
            width=130,
            height=40,
            font=ctk.CTkFont(size=14),
            fg_color=("#757575", "#616161"),
            hover_color=("#616161", "#424242")
        )
        cancel_btn.pack(side="right", padx=5)

        save_btn = ctk.CTkButton(
            btn_frame,
            text="💾 Guardar",
            command=self.guardar,
            width=150,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=("#4CAF50", "#388E3C"),
            hover_color=("#66BB6A", "#2E7D32")
        )
        save_btn.pack(side="right", padx=5)

    def carregar_dados(self):
        """Load project data into form"""
        p = self.projeto

        # Tipo
        self.tipo_var.set(p.tipo.value)

        # Cliente
        if p.cliente:
            cliente_str = f"{p.cliente.numero} - {p.cliente.nome}"
            self.cliente_dropdown.set(cliente_str)

        # Descrição
        self.descricao_entry.insert("1.0", p.descricao)

        # Valor
        self.valor_entry.insert(0, str(p.valor_sem_iva))

        # Datas
        if p.data_inicio:
            self.data_inicio_entry.insert(0, p.data_inicio.strftime("%Y-%m-%d"))
        if p.data_fim:
            self.data_fim_entry.insert(0, p.data_fim.strftime("%Y-%m-%d"))
        if p.data_faturacao:
            self.data_faturacao_entry.insert(0, p.data_faturacao.strftime("%Y-%m-%d"))
        if p.data_vencimento:
            self.data_vencimento_entry.insert(0, p.data_vencimento.strftime("%Y-%m-%d"))

        # Estado
        estado_map = {
            EstadoProjeto.NAO_FATURADO: "Não Faturado",
            EstadoProjeto.FATURADO: "Faturado",
            EstadoProjeto.RECEBIDO: "Recebido",
            EstadoProjeto.ANULADO: "Anulado"
        }
        self.estado_dropdown.set(estado_map[p.estado])

        # Prémios
        if p.premio_bruno:
            self.premio_bruno_entry.insert(0, str(p.premio_bruno))
        if p.premio_rafael:
            self.premio_rafael_entry.insert(0, str(p.premio_rafael))

        # Nota
        if p.nota:
            self.nota_entry.insert("1.0", p.nota)

    def guardar(self):
        """Save project"""
        try:
            # Get values
            tipo_str = self.tipo_var.get()
            tipo = TipoProjeto[tipo_str]

            cliente_str = self.cliente_dropdown.get()
            cliente_id = self.clientes_map.get(cliente_str) if cliente_str != "(Nenhum)" else None

            descricao = self.descricao_entry.get("1.0", "end-1c").strip()
            if not descricao:
                messagebox.showerror("Erro", "Descrição é obrigatória")
                return

            valor_str = self.valor_entry.get().strip()
            if not valor_str:
                messagebox.showerror("Erro", "Valor é obrigatório")
                return
            valor = Decimal(valor_str.replace(',', '.'))

            # Datas
            data_inicio = None
            if self.data_inicio_entry.get():
                data_inicio = date.fromisoformat(self.data_inicio_entry.get())

            data_fim = None
            if self.data_fim_entry.get():
                data_fim = date.fromisoformat(self.data_fim_entry.get())

            data_faturacao = None
            if self.data_faturacao_entry.get():
                data_faturacao = date.fromisoformat(self.data_faturacao_entry.get())

            data_vencimento = None
            if self.data_vencimento_entry.get():
                data_vencimento = date.fromisoformat(self.data_vencimento_entry.get())

            # Estado
            estado_map = {
                "Não Faturado": EstadoProjeto.NAO_FATURADO,
                "Faturado": EstadoProjeto.FATURADO,
                "Recebido": EstadoProjeto.RECEBIDO,
                "Anulado": EstadoProjeto.ANULADO
            }
            estado = estado_map[self.estado_dropdown.get()]

            # Prémios
            premio_bruno = None
            if self.premio_bruno_entry.get():
                premio_bruno = Decimal(self.premio_bruno_entry.get().replace(',', '.'))

            premio_rafael = None
            if self.premio_rafael_entry.get():
                premio_rafael = Decimal(self.premio_rafael_entry.get().replace(',', '.'))

            # Nota
            nota = self.nota_entry.get("1.0", "end-1c").strip() or None

            # Create or update
            if self.projeto:
                # Update
                sucesso, erro = self.manager.atualizar(
                    self.projeto.id,
                    tipo=tipo,
                    cliente_id=cliente_id,
                    descricao=descricao,
                    valor_sem_iva=valor,
                    data_inicio=data_inicio,
                    data_fim=data_fim,
                    data_faturacao=data_faturacao,
                    data_vencimento=data_vencimento,
                    estado=estado,
                    premio_bruno=premio_bruno,
                    premio_rafael=premio_rafael,
                    nota=nota
                )
                msg = "Projeto atualizado com sucesso!"
            else:
                # Create
                sucesso, projeto, erro = self.manager.criar(
                    tipo=tipo,
                    cliente_id=cliente_id,
                    descricao=descricao,
                    valor_sem_iva=valor,
                    data_inicio=data_inicio,
                    data_fim=data_fim,
                    data_faturacao=data_faturacao,
                    data_vencimento=data_vencimento,
                    estado=estado,
                    premio_bruno=premio_bruno,
                    premio_rafael=premio_rafael,
                    nota=nota
                )
                msg = f"Projeto {projeto.numero} criado com sucesso!"

            if sucesso:
                messagebox.showinfo("Sucesso", msg)
                if self.callback:
                    self.callback()
                self.destroy()
            else:
                messagebox.showerror("Erro", f"Erro ao guardar: {erro}")

        except ValueError as e:
            messagebox.showerror("Erro", f"Erro nos dados: {e}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro inesperado: {e}")
