# -*- coding: utf-8 -*-
"""
Tela de gestão de Projetos - Lista com navegação para edição
"""
import customtkinter as ctk
import tkinter as tk
from typing import Optional
from sqlalchemy.orm import Session
from datetime import date
import tkinter.messagebox as messagebox

from logic.projetos import ProjetosManager
from logic.clientes import ClientesManager
from database.models import TipoProjeto, EstadoProjeto
from ui.components.data_table_v2 import DataTableV2
from assets.resources import get_icon, PROJETOS


class ProjetosScreen(ctk.CTkFrame):
    """
    Tela de gestão de Projetos (lista com navegação para edição)
    """

    def __init__(self, parent, db_session: Session, filtro_estado=None, filtro_cliente_id=None, filtro_tipo=None, filtro_premio_socio=None, filtro_owner=None, **kwargs):
        """
        Initialize projetos screen

        Args:
            parent: Parent widget
            db_session: SQLAlchemy database session
            filtro_estado: Optional initial estado filter
            filtro_cliente_id: Optional initial cliente filter (cliente ID)
            filtro_tipo: Optional initial tipo filter ("Pessoal BA", "Pessoal RR", "Empresa")
            filtro_premio_socio: Optional filter for projects with prizes ("BA" or "RR")
            filtro_owner: Optional owner filter ("BA" or "RR") for empresa projects
        """
        super().__init__(parent, **kwargs)

        self.db_session = db_session
        self.manager = ProjetosManager(db_session)
        self.clientes_manager = ClientesManager(db_session)
        self.filtro_inicial_estado = filtro_estado
        self.filtro_inicial_cliente_id = filtro_cliente_id
        self.filtro_inicial_tipo = filtro_tipo
        self.filtro_premio_socio = filtro_premio_socio  # "BA" or "RR"
        self.filtro_owner = filtro_owner  # "BA" or "RR" for empresa projects

        # Configure
        self.configure(fg_color="transparent")

        # Create widgets
        self.create_widgets()

        # Apply initial filter if provided
        if self.filtro_inicial_estado or self.filtro_inicial_cliente_id or self.filtro_inicial_tipo or self.filtro_premio_socio or self.filtro_owner:
            if self.filtro_inicial_estado:
                self.estado_filter.set(self.filtro_inicial_estado)
            if self.filtro_inicial_cliente_id:
                # Find cliente in list and set filter
                for cliente in self.clientes_list:
                    if cliente.id == self.filtro_inicial_cliente_id:
                        self.cliente_filter.set(cliente.nome)
                        break
            if self.filtro_inicial_tipo:
                self.tipo_filter.set(self.filtro_inicial_tipo)
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

        # Search bar (search-as-you-type)
        search_frame = ctk.CTkFrame(self, fg_color="transparent")
        search_frame.pack(fill="x", padx=30, pady=(0, 15))

        ctk.CTkLabel(
            search_frame,
            text="🔍 Pesquisar:",
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(side="left", padx=(0, 10))

        # Search entry with StringVar for reactive tracking
        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", self.on_search_change)

        self.search_entry = ctk.CTkEntry(
            search_frame,
            textvariable=self.search_var,
            placeholder_text="Digite para pesquisar por cliente ou descrição...",
            width=500,
            height=35,
            font=ctk.CTkFont(size=13)
        )
        self.search_entry.pack(side="left", padx=(0, 10))

        # Clear search button
        clear_search_btn = ctk.CTkButton(
            search_frame,
            text="✖",
            command=self.limpar_pesquisa,
            width=35,
            height=35,
            font=ctk.CTkFont(size=14),
            fg_color=("#E0E0E0", "#404040"),
            hover_color=("#BDBDBD", "#606060")
        )
        clear_search_btn.pack(side="left")

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
            values=["Todos", "Ativo", "Finalizado", "Pago", "Anulado"],
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
            on_selection_change=self.on_selection_change,
            on_row_right_click=self.show_context_menu
        )
        self.table.pack(fill="both", expand=True, padx=30, pady=(0, 30))

    def carregar_projetos(self):
        """Load and display projects (respecting active filters)"""
        # Atualizar estados automaticamente antes de carregar
        self.manager.atualizar_estados_projetos()

        # If we have active filters, apply them instead of loading all
        if self.cliente_filter.get() != "Todos" or self.tipo_filter.get() != "Todos" or self.estado_filter.get() != "Todos":
            self.aplicar_filtros()
        else:
            # No filters active, load all
            projetos = self.manager.listar_todos()
            data = [self.projeto_to_dict(p) for p in projetos]
            self.table.set_data(data)

    def projeto_to_dict(self, projeto, search_text: Optional[str] = None) -> dict:
        """
        Convert project to dict for table

        Args:
            projeto: Projeto object
            search_text: Optional search text to highlight in results

        Returns:
            Dictionary with project data for table display
        """
        cliente_nome = projeto.cliente.nome if projeto.cliente else '-'
        descricao = projeto.descricao or ''
        numero = projeto.numero

        # Apply visual highlighting if search text is provided
        if search_text and search_text.strip():
            search_lower = search_text.strip().lower()

            # Check if cliente_nome or descricao match
            if search_lower in cliente_nome.lower():
                numero = f"➤ {numero}"
            elif search_lower in descricao.lower():
                numero = f"➤ {numero}"

        data = {
            'id': projeto.id,
            'numero': numero,
            'tipo': self.tipo_to_label(projeto.tipo),
            'cliente_nome': cliente_nome,
            'descricao': descricao,
            'valor_sem_iva': float(projeto.valor_sem_iva),
            'estado': self.estado_to_label(projeto.estado),
            '_bg_color': self.estado_to_color(projeto.estado),
            '_projeto': projeto
        }

        # Add strikethrough for cancelled projects
        if projeto.estado == EstadoProjeto.ANULADO:
            data['_strikethrough_except'] = ['estado']

        return data

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
            EstadoProjeto.ATIVO: "Ativo",
            EstadoProjeto.FINALIZADO: "Finalizado",
            EstadoProjeto.PAGO: "Pago",
            EstadoProjeto.ANULADO: "Anulado"
        }
        return mapping.get(estado, str(estado))

    def estado_to_color(self, estado: EstadoProjeto) -> tuple:
        """Convert estado enum to pastel background color"""
        mapping = {
            EstadoProjeto.ATIVO: ("#FFF4CC", "#806020"),
            EstadoProjeto.FINALIZADO: ("#FFE5D0", "#8B4513"),
            EstadoProjeto.PAGO: ("#E8F5E0", "#4A7028"),
            EstadoProjeto.ANULADO: ("#808080", "#505050")
        }
        return mapping.get(estado, ("#f8f8f8", "#252525"))

    def on_search_change(self, *args):
        """Reactive search handler - filters projects as user types"""
        search_text = self.search_var.get()

        # Get base projects from search
        if search_text and search_text.strip():
            projetos = self.manager.filtrar_por_texto(search_text)
        else:
            projetos = self.manager.listar_todos()

        # Apply existing filters
        cliente = self.cliente_filter.get()
        tipo = self.tipo_filter.get()
        estado = self.estado_filter.get()

        # Filter by cliente
        if cliente != "Todos":
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
                "Ativo": EstadoProjeto.ATIVO,
                "Finalizado": EstadoProjeto.FINALIZADO,
                "Pago": EstadoProjeto.PAGO,
                "Anulado": EstadoProjeto.ANULADO
            }
            estado_enum = estado_map[estado]
            projetos = [p for p in projetos if p.estado == estado_enum]

        # Filter by prémios
        if self.filtro_premio_socio:
            if self.filtro_premio_socio == "BA":
                projetos = [p for p in projetos if p.premio_bruno and p.premio_bruno > 0]
            elif self.filtro_premio_socio == "RR":
                projetos = [p for p in projetos if p.premio_rafael and p.premio_rafael > 0]

        # Filter by owner (empresa projects only)
        if self.filtro_owner:
            projetos = [p for p in projetos if p.owner == self.filtro_owner and p.tipo == TipoProjeto.EMPRESA]

        # Update table
        search_term = search_text.strip() if search_text and search_text.strip() else None
        data = [self.projeto_to_dict(p, search_text=search_term) for p in projetos]
        self.table.set_data(data)

    def limpar_pesquisa(self):
        """Clear search field and refresh results"""
        self.search_var.set("")
        self.search_entry.focus()

    def aplicar_filtros(self, *args):
        """Apply filters"""
        self.on_search_change()

    def abrir_formulario(self, projeto=None):
        """Navigate to projeto_form screen for create/edit"""
        main_window = self.master.master
        if hasattr(main_window, 'show_screen'):
            if projeto:
                main_window.show_screen("projeto_form", projeto_id=projeto.id)
            else:
                main_window.show_screen("projeto_form", projeto_id=None)
        else:
            messagebox.showerror("Erro", "Não foi possível abrir formulário")

    def editar_projeto(self, data: dict):
        """Edit project - navigate to form"""
        projeto = data.get('_projeto')
        if projeto:
            self.abrir_formulario(projeto)

    def on_selection_change(self, selected_data: list):
        """Handle selection change in table"""
        num_selected = len(selected_data)

        if num_selected > 0:
            # Show selection frame
            self.selection_frame.pack(fill="x", padx=30, pady=(0, 10))
            self.cancel_btn.pack(side="left", padx=5)

            count_text = f"{num_selected} selecionado" if num_selected == 1 else f"{num_selected} selecionados"
            self.count_label.configure(text=count_text)
            self.count_label.pack(side="left", padx=15)

            self.report_btn.pack(side="left", padx=5)

            total = sum(item.get('valor_sem_iva', 0) for item in selected_data)
            self.total_label.configure(text=f"Total: €{total:,.2f}")
            self.total_label.pack(side="left", padx=20)
        else:
            self.selection_frame.pack_forget()

    def cancelar_selecao(self):
        """Cancel selection"""
        self.table.clear_selection()

    def criar_relatorio(self):
        """Create report for selected projects"""
        selected_data = self.table.get_selected_data()
        if len(selected_data) > 0:
            projeto_ids = [item.get('id') for item in selected_data if item.get('id')]
            main_window = self.master.master
            if hasattr(main_window, 'show_relatorios'):
                main_window.show_relatorios(projeto_ids=projeto_ids)
            else:
                messagebox.showerror("Erro", "Não foi possível navegar para Relatórios")

    def show_context_menu(self, event, data: dict):
        """Show context menu for a project"""
        projeto = data.get('_projeto')
        if not projeto:
            return

        menu = tk.Menu(self, tearoff=0)

        menu.add_command(label="✏️ Editar", command=lambda: self.editar_projeto(data))
        menu.add_command(label="📋 Duplicar", command=lambda: self._duplicar_from_context(projeto))

        menu.add_separator()

        # State actions
        if projeto.estado == EstadoProjeto.ATIVO:
            menu.add_command(label="✅ Marcar como Finalizado", command=lambda: self._marcar_finalizado_from_context(projeto))
        elif projeto.estado == EstadoProjeto.FINALIZADO:
            menu.add_command(label="✅ Marcar como Pago", command=lambda: self._marcar_pago_from_context(projeto))
            menu.add_command(label="⏪ Voltar a Ativo", command=lambda: self._marcar_ativo_from_context(projeto))
        elif projeto.estado == EstadoProjeto.PAGO:
            menu.add_command(label="⏪ Voltar a Finalizado", command=lambda: self._marcar_finalizado_from_context(projeto))

        if projeto.estado != EstadoProjeto.ANULADO:
            menu.add_separator()
            menu.add_command(label="⛔ Anular Projeto", command=lambda: self._anular_from_context(projeto))

        menu.add_separator()
        menu.add_command(label="🗑️ Apagar", command=lambda: self._apagar_from_context(projeto))

        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def _duplicar_from_context(self, projeto):
        """Duplicate project from context menu"""
        try:
            resposta = messagebox.askyesno(
                "Duplicar Projeto",
                f"Duplicar projeto {projeto.numero}?\n\n"
                f"Cliente: {projeto.cliente.nome if projeto.cliente else '-'}\n"
                f"O novo projeto será criado com estado ATIVO."
            )

            if not resposta:
                return

            sucesso, novo_projeto, erro = self.manager.duplicar_projeto(projeto.id)

            if sucesso:
                self.carregar_projetos()
                self.table.clear_selection()
                messagebox.showinfo("Sucesso", f"Projeto duplicado como {novo_projeto.numero}")
                self.abrir_formulario(novo_projeto)
            else:
                messagebox.showerror("Erro", erro or "Erro ao duplicar projeto")

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao duplicar projeto: {str(e)}")

    def _marcar_finalizado_from_context(self, projeto):
        """Mark project as FINALIZADO"""
        try:
            resposta = messagebox.askyesno(
                "Marcar como Finalizado",
                f"Marcar projeto {projeto.numero} como finalizado?"
            )

            if not resposta:
                return

            sucesso, erro = self.manager.mudar_estado(projeto.id, EstadoProjeto.FINALIZADO)

            if sucesso:
                self.carregar_projetos()
                self.table.clear_selection()
            else:
                messagebox.showerror("Erro", erro or "Erro ao mudar estado")

        except Exception as e:
            messagebox.showerror("Erro", f"Erro: {str(e)}")

    def _marcar_pago_from_context(self, projeto):
        """Mark project as PAGO"""
        try:
            hoje = date.today()
            resposta = messagebox.askyesno(
                "Marcar como Pago",
                f"Marcar projeto {projeto.numero} como pago?\n\n"
                f"Data de pagamento: {hoje.strftime('%d/%m/%Y')}"
            )

            if not resposta:
                return

            sucesso, erro = self.manager.mudar_estado(projeto.id, EstadoProjeto.PAGO, data_pagamento=hoje)

            if sucesso:
                self.carregar_projetos()
                self.table.clear_selection()
            else:
                messagebox.showerror("Erro", erro or "Erro ao mudar estado")

        except Exception as e:
            messagebox.showerror("Erro", f"Erro: {str(e)}")

    def _marcar_ativo_from_context(self, projeto):
        """Mark project as ATIVO"""
        try:
            resposta = messagebox.askyesno(
                "Voltar a Ativo",
                f"Marcar projeto {projeto.numero} como ativo?"
            )

            if not resposta:
                return

            sucesso, erro = self.manager.mudar_estado(projeto.id, EstadoProjeto.ATIVO)

            if sucesso:
                self.carregar_projetos()
                self.table.clear_selection()
            else:
                messagebox.showerror("Erro", erro or "Erro ao mudar estado")

        except Exception as e:
            messagebox.showerror("Erro", f"Erro: {str(e)}")

    def _anular_from_context(self, projeto):
        """Cancel project"""
        try:
            resposta = messagebox.askyesno(
                "Anular Projeto",
                f"Anular projeto {projeto.numero}?\n\n"
                f"⚠️ Projetos anulados não entram nos cálculos.",
                icon='warning'
            )

            if not resposta:
                return

            sucesso, erro = self.manager.mudar_estado(projeto.id, EstadoProjeto.ANULADO)

            if sucesso:
                self.carregar_projetos()
                self.table.clear_selection()
            else:
                messagebox.showerror("Erro", erro or "Erro ao anular projeto")

        except Exception as e:
            messagebox.showerror("Erro", f"Erro: {str(e)}")

    def _apagar_from_context(self, projeto):
        """Delete project"""
        try:
            resposta = messagebox.askyesno(
                "Confirmar Exclusão",
                f"Apagar projeto {projeto.numero}?\n\n"
                f"⚠️ Esta ação não pode ser desfeita!",
                icon='warning'
            )

            if not resposta:
                return

            sucesso, erro = self.manager.apagar(projeto.id)

            if sucesso:
                self.carregar_projetos()
                self.table.clear_selection()
            else:
                messagebox.showerror("Erro", erro or "Erro ao apagar projeto")

        except Exception as e:
            messagebox.showerror("Erro", f"Erro: {str(e)}")
