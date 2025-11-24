# -*- coding: utf-8 -*-
"""
Tela de gestão de Projetos
"""
import customtkinter as ctk
import tkinter as tk
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
from utils.base_dialogs import BaseDialogLarge


class ProjetosScreen(ctk.CTkFrame):
    """
    Tela de gestão de Projetos (CRUD completo)
    """

    def __init__(self, parent, db_session: Session, filtro_estado=None, filtro_cliente_id=None, filtro_tipo=None, filtro_premio_socio=None, **kwargs):
        """
        Initialize projetos screen

        Args:
            parent: Parent widget
            db_session: SQLAlchemy database session
            filtro_estado: Optional initial estado filter
            filtro_cliente_id: Optional initial cliente filter (cliente ID)
            filtro_tipo: Optional initial tipo filter ("Pessoal BA", "Pessoal RR", "Empresa")
            filtro_premio_socio: Optional filter for projects with prizes ("BA" or "RR")
        """
        super().__init__(parent, **kwargs)

        self.db_session = db_session
        self.manager = ProjetosManager(db_session)
        self.clientes_manager = ClientesManager(db_session)
        self.projeto_editando = None
        self.filtro_inicial_estado = filtro_estado
        self.filtro_inicial_cliente_id = filtro_cliente_id
        self.filtro_inicial_tipo = filtro_tipo
        self.filtro_premio_socio = filtro_premio_socio  # "BA" or "RR"

        # Configure
        self.configure(fg_color="transparent")

        # Create widgets
        self.create_widgets()

        # Apply initial filter if provided
        if self.filtro_inicial_estado or self.filtro_inicial_cliente_id or self.filtro_inicial_tipo or self.filtro_premio_socio:
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
                # Add highlight marker to numero to indicate match
                numero = f"➤ {numero}"
            elif search_lower in descricao.lower():
                # Add highlight marker to numero to indicate match
                numero = f"➤ {numero}"

        data = {
            'id': projeto.id,
            'numero': numero,
            'tipo': self.tipo_to_label(projeto.tipo),
            'cliente_nome': cliente_nome,
            'descricao': descricao,  # DataTableV2 will truncate automatically with tooltip
            'valor_sem_iva': float(projeto.valor_sem_iva),
            'estado': self.estado_to_label(projeto.estado),
            '_bg_color': self.estado_to_color(projeto.estado),  # Color by estado
            '_projeto': projeto  # Keep reference
        }

        # Add strikethrough for cancelled projects (except 'estado' column)
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
        """Convert estado enum to pastel background color (light, dark) - Opção 3 Agora Inspired"""
        mapping = {
            EstadoProjeto.ATIVO: ("#FFF4CC", "#806020"),        # Pastel golden (em curso)
            EstadoProjeto.FINALIZADO: ("#FFE5D0", "#8B4513"),  # Pastel orange (aguardando)
            EstadoProjeto.PAGO: ("#E8F5E0", "#4A7028"),         # Pastel green (positivo)
            EstadoProjeto.ANULADO: ("#808080", "#505050")       # Dark gray
        }
        return mapping.get(estado, ("#f8f8f8", "#252525"))

    def on_search_change(self, *args):
        """
        Reactive search handler - called on every keystroke
        Filters projects dynamically as user types
        """
        search_text = self.search_var.get()

        # Get base projects from search
        if search_text and search_text.strip():
            # Use backend search method
            projetos = self.manager.filtrar_por_texto(search_text)
        else:
            # No search text, get all
            projetos = self.manager.listar_todos()

        # Apply existing filters on top of search results
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

        # Filter by prémios (if filtro_premio_socio is set)
        if self.filtro_premio_socio:
            if self.filtro_premio_socio == "BA":
                projetos = [p for p in projetos if p.premio_bruno and p.premio_bruno > 0]
            elif self.filtro_premio_socio == "RR":
                projetos = [p for p in projetos if p.premio_rafael and p.premio_rafael > 0]

        # Update table with highlighting (pass search_text for visual markers)
        search_term = search_text.strip() if search_text and search_text.strip() else None
        data = [self.projeto_to_dict(p, search_text=search_term) for p in projetos]
        self.table.set_data(data)

    def limpar_pesquisa(self):
        """Clear search field and refresh results"""
        self.search_var.set("")
        self.search_entry.focus()

    def aplicar_filtros(self, *args):
        """Apply filters (dropdown filters trigger this, search triggers on_search_change)"""
        # Trigger search which will also apply filters
        self.on_search_change()

    def after_save_callback(self):
        """Callback after saving project - reload data and clear selection"""
        self.carregar_projetos()
        self.table.clear_selection()

    def abrir_formulario(self, projeto=None):
        """Open form dialog for create/edit"""
        FormularioProjetoDialog(self, self.manager, projeto, self.after_save_callback)

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

    def show_context_menu(self, event, data: dict):
        """
        Mostra menu de contexto (right-click) para um projeto

        Args:
            event: Evento do clique (para posição)
            data: Dados da linha clicada
        """
        projeto = data.get('_projeto')
        if not projeto:
            return

        # Criar menu
        menu = tk.Menu(self, tearoff=0)

        # ✏️ Editar
        menu.add_command(
            label="✏️ Editar",
            command=lambda: self.editar_projeto(data)
        )

        # 📋 Duplicar
        menu.add_command(
            label="📋 Duplicar",
            command=lambda: self._duplicar_from_context(projeto)
        )

        menu.add_separator()

        # Ações dependem do estado atual
        if projeto.estado == EstadoProjeto.ATIVO:
            menu.add_command(
                label="✅ Marcar como Finalizado",
                command=lambda: self._marcar_finalizado_from_context(projeto)
            )
        elif projeto.estado == EstadoProjeto.FINALIZADO:
            menu.add_command(
                label="✅ Marcar como Pago",
                command=lambda: self._marcar_pago_from_context(projeto)
            )
            menu.add_command(
                label="⏪ Voltar a Ativo",
                command=lambda: self._marcar_ativo_from_context(projeto)
            )
        elif projeto.estado == EstadoProjeto.PAGO:
            menu.add_command(
                label="⏪ Voltar a Finalizado",
                command=lambda: self._marcar_finalizado_from_context(projeto)
            )

        # Anular (se não estiver já anulado)
        if projeto.estado != EstadoProjeto.ANULADO:
            menu.add_separator()
            menu.add_command(
                label="⛔ Anular Projeto",
                command=lambda: self._anular_from_context(projeto)
            )

        menu.add_separator()

        # 🗑️ Apagar
        menu.add_command(
            label="🗑️ Apagar",
            command=lambda: self._apagar_from_context(projeto)
        )

        # Mostrar menu na posição do cursor
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def _duplicar_from_context(self, projeto):
        """Duplica projeto a partir do menu de contexto"""
        try:
            # Confirmar duplicação
            resposta = messagebox.askyesno(
                "Duplicar Projeto",
                f"Duplicar projeto {projeto.numero}?\n\n"
                f"Cliente: {projeto.cliente.nome if projeto.cliente else '-'}\n"
                f"Descrição: {projeto.descricao[:50]}...\n\n"
                f"O novo projeto será criado com estado ATIVO\n"
                f"e datas resetadas."
            )

            if not resposta:
                return

            # Duplicar
            sucesso, novo_projeto, erro = self.manager.duplicar_projeto(projeto.id)

            if sucesso:
                # Recarregar lista
                self.carregar_projetos()
                self.table.clear_selection()

                # Abrir novo projeto para edição
                messagebox.showinfo(
                    "Sucesso",
                    f"Projeto duplicado como {novo_projeto.numero}\n\n"
                    f"Abrindo para edição..."
                )
                self.abrir_formulario(novo_projeto)

            else:
                messagebox.showerror("Erro", erro or "Erro ao duplicar projeto")

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao duplicar projeto: {str(e)}")

    def _marcar_finalizado_from_context(self, projeto):
        """Marca projeto como FINALIZADO a partir do menu de contexto"""
        try:
            # Confirmar ação
            resposta = messagebox.askyesno(
                "Marcar como Finalizado",
                f"Marcar projeto {projeto.numero} como finalizado?\n\n"
                f"O projeto passa para estado FINALIZADO."
            )

            if not resposta:
                return

            sucesso, erro = self.manager.mudar_estado(
                projeto.id,
                EstadoProjeto.FINALIZADO
            )

            if sucesso:
                self.carregar_projetos()
                self.table.clear_selection()
                messagebox.showinfo("Sucesso", f"Projeto {projeto.numero} marcado como finalizado")
            else:
                messagebox.showerror("Erro", erro or "Erro ao mudar estado")

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao marcar como finalizado: {str(e)}")

    def _marcar_pago_from_context(self, projeto):
        """Marca projeto como PAGO a partir do menu de contexto"""
        try:
            # Confirmar ação
            hoje = date.today()
            resposta = messagebox.askyesno(
                "Marcar como Pago",
                f"Marcar projeto {projeto.numero} como pago?\n\n"
                f"Data de pagamento será definida como hoje ({hoje.strftime('%d/%m/%Y')}).\n\n"
                f"⚠️ ATENÇÃO: Isto afeta os cálculos de Saldos Pessoais!"
            )

            if not resposta:
                return

            sucesso, erro = self.manager.mudar_estado(
                projeto.id,
                EstadoProjeto.PAGO,
                data_pagamento=hoje
            )

            if sucesso:
                self.carregar_projetos()
                self.table.clear_selection()
                messagebox.showinfo("Sucesso", f"Projeto {projeto.numero} marcado como pago")
            else:
                messagebox.showerror("Erro", erro or "Erro ao mudar estado")

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao marcar como pago: {str(e)}")

    def _marcar_ativo_from_context(self, projeto):
        """Marca projeto como ATIVO a partir do menu de contexto"""
        try:
            # Confirmar ação
            resposta = messagebox.askyesno(
                "Voltar a Ativo",
                f"Marcar projeto {projeto.numero} como ativo?\n\n"
                f"O projeto voltará ao estado ATIVO."
            )

            if not resposta:
                return

            sucesso, erro = self.manager.mudar_estado(
                projeto.id,
                EstadoProjeto.ATIVO
            )

            if sucesso:
                self.carregar_projetos()
                self.table.clear_selection()
                messagebox.showinfo("Sucesso", f"Projeto {projeto.numero} marcado como ativo")
            else:
                messagebox.showerror("Erro", erro or "Erro ao mudar estado")

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao marcar como ativo: {str(e)}")

    def _anular_from_context(self, projeto):
        """Anula projeto a partir do menu de contexto"""
        try:
            # Confirmar ação
            resposta = messagebox.askyesno(
                "Anular Projeto",
                f"Anular projeto {projeto.numero}?\n\n"
                f"⚠️ ATENÇÃO: Projetos anulados não entram nos cálculos\n"
                f"de Saldos Pessoais e aparecem riscados na lista.\n\n"
                f"Esta ação pode ser revertida voltando o projeto a ATIVO.",
                icon='warning'
            )

            if not resposta:
                return

            sucesso, erro = self.manager.mudar_estado(
                projeto.id,
                EstadoProjeto.ANULADO
            )

            if sucesso:
                self.carregar_projetos()
                self.table.clear_selection()
                messagebox.showinfo("Sucesso", f"Projeto {projeto.numero} anulado")
            else:
                messagebox.showerror("Erro", erro or "Erro ao anular projeto")

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao anular projeto: {str(e)}")

    def _apagar_from_context(self, projeto):
        """Apaga projeto a partir do menu de contexto"""
        try:
            # Confirmar exclusão
            resposta = messagebox.askyesno(
                "Confirmar Exclusão",
                f"Tem certeza que deseja apagar o projeto {projeto.numero}?\n\n"
                f"Cliente: {projeto.cliente.nome if projeto.cliente else '-'}\n"
                f"Descrição: {projeto.descricao[:50]}...\n\n"
                f"⚠️ ATENÇÃO: Esta ação não pode ser desfeita!\n"
                f"⚠️ Isto vai afetar os cálculos de Saldos Pessoais!",
                icon='warning'
            )

            if not resposta:
                return

            sucesso, erro = self.manager.apagar(projeto.id)

            if sucesso:
                self.carregar_projetos()
                self.table.clear_selection()
                messagebox.showinfo("Sucesso", f"Projeto {projeto.numero} apagado com sucesso")
            else:
                messagebox.showerror("Erro", erro or "Erro ao apagar projeto")

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao apagar projeto: {str(e)}")


class FormularioProjetoDialog(BaseDialogLarge):
    """
    Dialog para criar/editar projetos
    """

    def __init__(self, parent, manager: ProjetosManager, projeto=None, callback=None):
        self.manager = manager
        self.projeto = projeto
        self.callback = callback
        self.parent_ref = parent

        title = "Novo Projeto" if not projeto else f"Editar Projeto {projeto.numero}"
        super().__init__(parent, title=title)

        # Create form
        self.create_form()

        # Load data if editing
        if projeto:
            self.carregar_dados()

        # Focus on the dialog
        self.focus_set()

        # After window is mapped, configure it to stay on top and grab focus
        self.after(10, lambda: self.lift())

        # Handle window close
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def create_form(self):
        """Create form fields"""

        # Use main_frame (already scrollable from BaseDialogLarge)
        scroll = self.main_frame

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

        # Período do projeto (Data início - Data fim)
        ctk.CTkLabel(datas_frame, text="Período do Projeto", font=ctk.CTkFont(size=14, weight="bold")).grid(row=0, column=0, sticky="w", columnspan=2)
        from ui.components.date_range_picker_dropdown import DateRangePickerDropdown
        self.periodo_picker = DateRangePickerDropdown(datas_frame, placeholder="Selecionar período...")
        self.periodo_picker.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(8, 12))

        # Data faturação
        ctk.CTkLabel(datas_frame, text="Data Faturação", font=ctk.CTkFont(size=14, weight="bold")).grid(row=2, column=0, sticky="w", padx=(0, 12))
        from ui.components.date_picker_dropdown import DatePickerDropdown
        self.data_faturacao_picker = DatePickerDropdown(datas_frame, placeholder="Selecionar data faturação...")
        self.data_faturacao_picker.grid(row=3, column=0, sticky="ew", padx=(0, 12), pady=(8, 12))

        # Data vencimento
        ctk.CTkLabel(datas_frame, text="Data Vencimento", font=ctk.CTkFont(size=14, weight="bold")).grid(row=2, column=1, sticky="w")
        self.data_vencimento_picker = DatePickerDropdown(datas_frame, placeholder="Selecionar data vencimento...")
        self.data_vencimento_picker.grid(row=3, column=1, sticky="ew", pady=(8, 12))

        # Estado
        ctk.CTkLabel(scroll, text="Estado *", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", pady=(5, 8))
        self.estado_dropdown = ctk.CTkOptionMenu(scroll, values=["Ativo", "Finalizado", "Pago", "Anulado"], height=35)
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
        btn_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(20, 0))

        cancel_btn = ctk.CTkButton(
            btn_frame,
            text="Cancelar",
            command=self._on_close,
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
            self.periodo_picker.set_range(p.data_inicio, p.data_fim)
        if p.data_faturacao:
            self.data_faturacao_picker.set_date(p.data_faturacao)
        if p.data_vencimento:
            self.data_vencimento_picker.set_date(p.data_vencimento)

        # Estado
        estado_map = {
            EstadoProjeto.ATIVO: "Ativo",
            EstadoProjeto.FINALIZADO: "Finalizado",
            EstadoProjeto.PAGO: "Pago",
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
            data_inicio = self.periodo_picker.start_date if self.periodo_picker.get() else None
            data_fim = self.periodo_picker.end_date if self.periodo_picker.get() else None
            data_faturacao = self.data_faturacao_picker.get_date() if self.data_faturacao_picker.get() else None
            data_vencimento = self.data_vencimento_picker.get_date() if self.data_vencimento_picker.get() else None

            # Estado
            estado_map = {
                "Ativo": EstadoProjeto.ATIVO,
                "Finalizado": EstadoProjeto.FINALIZADO,
                "Pago": EstadoProjeto.PAGO,
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

            if sucesso:
                if self.callback:
                    self.callback()
                self.destroy()
            else:
                messagebox.showerror("Erro", f"Erro ao guardar: {erro}")

        except ValueError as e:
            messagebox.showerror("Erro", f"Erro nos dados: {e}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro inesperado: {e}")

    def _on_close(self):
        """Handle window close"""
        # Clear selection when closing (cancel or X button)
        if hasattr(self.parent_ref, 'table'):
            self.parent_ref.table.clear_selection()

        self.destroy()
