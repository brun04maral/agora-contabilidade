# -*- coding: utf-8 -*-
"""
Tela de gestão de Despesas
"""
import customtkinter as ctk
import tkinter as tk
from typing import Optional
from sqlalchemy.orm import Session
from datetime import date
from decimal import Decimal
import tkinter.messagebox as messagebox

from logic.despesas import DespesasManager
from database.models import TipoDespesa, EstadoDespesa
from ui.components.data_table_v2 import DataTableV2
from assets.resources import get_icon, DESPESAS
from utils.base_dialogs import BaseDialogLarge


class DespesasScreen(ctk.CTkFrame):
    """
    Tela de gestão de Despesas (CRUD completo)
    """

    def __init__(self, parent, db_session: Session, filtro_estado=None, filtro_tipo=None, **kwargs):
        super().__init__(parent, **kwargs)

        self.db_session = db_session
        self.manager = DespesasManager(db_session)
        self.filtro_inicial_estado = filtro_estado
        self.filtro_inicial_tipo = filtro_tipo

        self.configure(fg_color="transparent")
        self.create_widgets()

        # Apply initial filter if provided
        if self.filtro_inicial_estado or self.filtro_inicial_tipo:
            if self.filtro_inicial_estado:
                self.estado_filter.set(self.filtro_inicial_estado)
            if self.filtro_inicial_tipo:
                self.tipo_filter.set(self.filtro_inicial_tipo)
            self.aplicar_filtros()
        else:
            self.carregar_despesas()

    def create_widgets(self):
        """Create screen widgets"""

        # Header
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=30, pady=(30, 20))

        # Title with PNG icon
        icon_pil = get_icon(DESPESAS, size=(28, 28))
        if icon_pil:
            icon_ctk = ctk.CTkImage(
                light_image=icon_pil,
                dark_image=icon_pil,
                size=(28, 28)
            )
            title_label = ctk.CTkLabel(
                header_frame,
                image=icon_ctk,
                text=" Despesas",
                compound="left",
                font=ctk.CTkFont(size=28, weight="bold")
            )
        else:
            title_label = ctk.CTkLabel(
                header_frame,
                text="💸 Despesas",
                font=ctk.CTkFont(size=28, weight="bold")
            )
        title_label.pack(side="left")

        # Buttons
        btn_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        btn_frame.pack(side="right")

        refresh_btn = ctk.CTkButton(
            btn_frame,
            text="🔄 Atualizar",
            command=self.carregar_despesas,
            width=120,
            height=35,
            font=ctk.CTkFont(size=13)
        )
        refresh_btn.pack(side="left", padx=5)

        gerar_recorrentes_btn = ctk.CTkButton(
            btn_frame,
            text="🔁 Gerar Recorrentes",
            command=self.gerar_despesas_recorrentes,
            width=170,
            height=35,
            font=ctk.CTkFont(size=13),
            fg_color=("#2196F3", "#1976D2"),
            hover_color=("#64B5F6", "#1565C0")
        )
        gerar_recorrentes_btn.pack(side="left", padx=5)

        editar_templates_btn = ctk.CTkButton(
            btn_frame,
            text="📝 Editar Recorrentes",
            command=self.abrir_templates,
            width=170,
            height=35,
            font=ctk.CTkFont(size=13),
            fg_color=("#9C27B0", "#7B1FA2"),
            hover_color=("#BA68C8", "#6A1B9A")
        )
        editar_templates_btn.pack(side="left", padx=5)

        nova_btn = ctk.CTkButton(
            btn_frame,
            text="➕ Nova Despesa",
            command=self.abrir_formulario,
            width=140,
            height=35,
            font=ctk.CTkFont(size=13),
            fg_color=("#F44336", "#C62828"),
            hover_color=("#E57373", "#B71C1C")
        )
        nova_btn.pack(side="left", padx=5)

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
            placeholder_text="Digite para pesquisar por fornecedor ou descrição...",
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

        # Tipo filter
        ctk.CTkLabel(
            filters_frame,
            text="Tipo:",
            font=ctk.CTkFont(size=13)
        ).pack(side="left", padx=(0, 10))

        self.tipo_filter = ctk.CTkOptionMenu(
            filters_frame,
            values=["Todos", "Fixa Mensal", "Pessoal BA", "Pessoal RR", "Equipamento", "Projeto"],
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
            values=["Todos", "Pendente", "Vencido", "Pago"],
            command=self.aplicar_filtros,
            width=120
        )
        self.estado_filter.pack(side="left")

        # Selection actions bar (created but NOT packed - will be shown on selection)
        self.selection_frame = ctk.CTkFrame(self, fg_color="transparent")

        # Clear selection button
        self.cancel_btn = ctk.CTkButton(
            self.selection_frame,
            text="🗑️ Limpar Seleção",
            command=self.cancelar_selecao,
            width=150, height=35
        )

        # Selection count label
        self.count_label = ctk.CTkLabel(
            self.selection_frame,
            text="0 selecionados",
            font=ctk.CTkFont(size=13)
        )

        # Mark as paid button
        self.marcar_pago_btn = ctk.CTkButton(
            self.selection_frame,
            text="✅ Marcar como Pago",
            command=self.marcar_como_pago,
            width=160, height=35,
            fg_color=("#4CAF50", "#388E3C"),
            hover_color=("#66BB6A", "#2E7D32")
        )

        # Report button
        self.report_btn = ctk.CTkButton(
            self.selection_frame,
            text="📊 Criar Relatório",
            command=self.criar_relatorio,
            width=160, height=35
        )

        # Delete button
        self.delete_btn = ctk.CTkButton(
            self.selection_frame,
            text="🗑️ Apagar Selecionadas",
            command=self.apagar_selecionadas,
            width=160, height=35,
            fg_color=("#F44336", "#C62828"),
            hover_color=("#E57373", "#B71C1C")
        )

        # Total label
        self.total_label = ctk.CTkLabel(
            self.selection_frame,
            text="Total: €0,00",
            font=ctk.CTkFont(size=14, weight="bold")
        )

        # Table
        columns = [
            {'key': 'numero', 'label': 'ID', 'width': 100, 'sortable': True},
            {'key': 'data', 'label': 'Data', 'width': 120, 'sortable': True},
            {'key': 'tipo', 'label': 'Tipo', 'width': 140, 'sortable': False},
            {'key': 'credor_nome', 'label': 'Credor', 'width': 160, 'sortable': True},
            {'key': 'descricao', 'label': 'Descrição', 'width': 280, 'sortable': False},
            {'key': 'valor_com_iva_fmt', 'label': 'Valor c/ IVA', 'width': 120, 'sortable': True},
            {'key': 'estado', 'label': 'Estado', 'width': 110, 'sortable': True},
        ]

        self.table = DataTableV2(
            self,
            columns=columns,
            on_row_double_click=self.editar_despesa,
            on_selection_change=self.on_selection_change,
            on_row_right_click=self.show_context_menu,
            height=400
        )
        self.table.pack(fill="both", expand=True, padx=30, pady=(0, 30))

    def carregar_despesas(self):
        """Load and display despesas"""
        despesas = self.manager.listar_todas()
        data = [self.despesa_to_dict(d) for d in despesas]
        self.table.set_data(data)

    def despesa_to_dict(self, despesa, search_text: Optional[str] = None) -> dict:
        """
        Convert despesa to dict for table

        Args:
            despesa: Despesa object
            search_text: Optional search text to highlight in results

        Returns:
            Dictionary with despesa data for table display
        """
        # Determine color based on estado
        color = self.get_estado_color(despesa.estado)

        # Add asterisk to tipo if generated from template
        tipo_label = self.tipo_to_label(despesa.tipo)
        if despesa.despesa_template_id:
            tipo_label += "*"

        credor_nome = despesa.credor.nome if despesa.credor else '-'
        descricao = despesa.descricao or ''
        numero = despesa.numero

        # Apply visual highlighting if search text is provided
        if search_text and search_text.strip():
            search_lower = search_text.strip().lower()

            # Check if credor_nome or descricao match
            if search_lower in credor_nome.lower():
                # Add highlight marker to numero to indicate match
                numero = f"➤ {numero}"
            elif search_lower in descricao.lower():
                # Add highlight marker to numero to indicate match
                numero = f"➤ {numero}"

        return {
            'id': despesa.id,
            'numero': numero,
            'data': despesa.data.strftime("%Y-%m-%d") if despesa.data else '-',
            'tipo': tipo_label,
            'credor_nome': credor_nome,
            'descricao': descricao,
            'valor_com_iva': float(despesa.valor_com_iva),
            'valor_com_iva_fmt': f"€{float(despesa.valor_com_iva):,.2f}",
            'estado': self.estado_to_label(despesa.estado),
            '_bg_color': color,
            '_despesa': despesa
        }

    def get_estado_color(self, estado: EstadoDespesa) -> tuple:
        """Get color for estado (returns tuple: light, dark mode) - Opção 3 Agora Inspired"""
        color_map = {
            EstadoDespesa.PAGO: ("#E8F5E0", "#4A7028"),        # Verde pastel - positivo
            EstadoDespesa.PENDENTE: ("#FFF4CC", "#806020"),    # Dourado pastel - harmoniza com BA
            EstadoDespesa.VENCIDO: ("#FFE5D0", "#8B4513")      # Laranja pastel - atenção urgente
        }
        return color_map.get(estado, ("#E0E0E0", "#4A4A4A"))

    def tipo_to_label(self, tipo: TipoDespesa) -> str:
        """Convert tipo enum to label"""
        mapping = {
            TipoDespesa.FIXA_MENSAL: "Fixa Mensal",
            TipoDespesa.PESSOAL_BRUNO: "Pessoal BA",
            TipoDespesa.PESSOAL_RAFAEL: "Pessoal RR",
            TipoDespesa.EQUIPAMENTO: "Equipamento",
            TipoDespesa.PROJETO: "Projeto"
        }
        return mapping.get(tipo, str(tipo))

    def estado_to_label(self, estado: EstadoDespesa) -> str:
        """Convert estado enum to label"""
        mapping = {
            EstadoDespesa.PENDENTE: "Pendente",
            EstadoDespesa.VENCIDO: "Vencido",
            EstadoDespesa.PAGO: "Pago"
        }
        return mapping.get(estado, str(estado))

    def aplicar_filtros(self, *args):
        """Apply filters (dropdown filters trigger this, search triggers on_search_change)"""
        # Trigger search which will also apply filters
        self.on_search_change()

    def after_save_callback(self):
        """Callback after saving - reload data and clear selection"""
        self.carregar_despesas()
        self.table.clear_selection()

    def abrir_formulario(self, despesa=None):
        """Open form dialog"""
        FormularioDespesaDialog(self, self.manager, despesa, self.after_save_callback)

    def gerar_despesas_recorrentes(self):
        """Gera despesas recorrentes para o mês atual"""
        from datetime import date
        hoje = date.today()
        mes_nome = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
                    "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"][hoje.month - 1]

        # Confirmar com o usuário
        resposta = messagebox.askyesno(
            "Gerar Despesas Recorrentes",
            f"Gerar despesas recorrentes para {mes_nome} de {hoje.year}?\n\n"
            f"Serão criadas automaticamente as despesas fixas mensais configuradas como recorrentes."
        )

        if not resposta:
            return

        # Gerar despesas
        geradas, erros = self.manager.verificar_e_gerar_recorrentes_pendentes()

        # Mostrar resultado
        if geradas > 0:
            self.carregar_despesas()  # Recarregar lista
            if erros:
                msg = f"⚠️ {len(erros)} erro(s) ao gerar despesas:\n" + "\n".join(erros[:3])
                if len(erros) > 3:
                    msg += f"\n... e mais {len(erros) - 3} erro(s)"
                messagebox.showwarning("Aviso", msg)
        elif erros:
            msg = f"❌ Nenhuma despesa gerada.\n\nErros:\n" + "\n".join(erros[:5])
            if len(erros) > 5:
                msg += f"\n... e mais {len(erros) - 5} erro(s)"
            messagebox.showerror("Erro", msg)
        else:
            messagebox.showinfo(
                "Sem Novas Despesas",
                f"Nenhuma despesa recorrente para gerar em {mes_nome}.\n\n"
                f"As despesas deste mês já foram geradas ou não há templates configurados."
            )

    def abrir_templates(self):
        """Abre janela de gestão de templates de despesas recorrentes"""
        from ui.screens.templates_despesas import TemplatesDespesasScreen

        # Criar janela modal
        dialog = ctk.CTkToplevel(self)
        dialog.title("Templates de Despesas Recorrentes")
        dialog.geometry("1000x700")
        dialog.transient(self)
        dialog.grab_set()

        # Adicionar screen de templates
        templates_screen = TemplatesDespesasScreen(dialog, self.db_session)
        templates_screen.pack(fill="both", expand=True)

        # Ao fechar, atualizar lista de despesas
        def on_close():
            dialog.destroy()
            self.carregar_despesas()

        dialog.protocol("WM_DELETE_WINDOW", on_close)

    def editar_despesa(self, data: dict):
        """Edit despesa (triggered by double-click)"""
        despesa = data.get('_despesa')
        if despesa:
            self.abrir_formulario(despesa)

    def apagar_despesa(self, data: dict):
        """Apagar despesa individual"""
        despesa = data.get('_despesa')
        if not despesa:
            return

        # Mostrar informação se foi gerada de template
        msg = f"Apagar despesa {despesa.numero}?"
        if despesa.despesa_template_id:
            msg += f"\n\n⚠️ Esta despesa foi gerada automaticamente do template {despesa.despesa_template.numero}."
            msg += "\nAo apagar, ela não será recriada automaticamente."

        resposta = messagebox.askyesno("Confirmar", msg)

        if resposta:
            sucesso, erro = self.manager.apagar(despesa.id)
            if sucesso:
                self.carregar_despesas()
            else:
                messagebox.showerror("Erro", f"Erro ao apagar: {erro}")

    def apagar_selecionadas(self):
        """Apagar despesas selecionadas"""
        selected_data = self.table.get_selected_data()
        if len(selected_data) == 0:
            return

        # Verificar quantas são geradas de templates
        geradas_template = sum(
            1 for item in selected_data
            if item.get('_despesa') and item.get('_despesa').despesa_template_id
        )

        # Confirmar ação
        msg = f"Apagar {len(selected_data)} despesa(s) selecionada(s)?"
        if geradas_template > 0:
            msg += f"\n\n⚠️ {geradas_template} despesa(s) foram geradas de templates."
            msg += "\nAo apagar, elas não serão recriadas automaticamente."

        resposta = messagebox.askyesno("Confirmar", msg)

        if resposta:
            sucesso_count = 0
            erros = []

            for item in selected_data:
                despesa = item.get('_despesa')
                if despesa:
                    sucesso, erro = self.manager.apagar(despesa.id)
                    if sucesso:
                        sucesso_count += 1
                    else:
                        erros.append(f"{despesa.numero}: {erro}")

            # Mostrar resultado
            if sucesso_count > 0:
                msg = f"✅ {sucesso_count} despesa(s) apagada(s) com sucesso!"
                if erros:
                    msg += f"\n\n⚠️ {len(erros)} erro(s):\n" + "\n".join(erros[:3])
                messagebox.showinfo("Resultado", msg)
            else:
                messagebox.showerror("Erro", "Nenhuma despesa foi apagada:\n" + "\n".join(erros[:5]))

            self.carregar_despesas()
            self.table.clear_selection()

    def on_selection_change(self, selected_data: list):
        """Handle selection change in table"""
        num_selected = len(selected_data)

        if num_selected > 0:
            # Show selection frame
            self.selection_frame.pack(fill="x", padx=30, pady=(0, 10))

            # Show selection bar
            self.cancel_btn.pack(side="left", padx=5)

            # Show count
            count_text = f"{num_selected} selecionada" if num_selected == 1 else f"{num_selected} selecionadas"
            self.count_label.configure(text=count_text)
            self.count_label.pack(side="left", padx=15)

            # Show "Marcar como Pago" only if there are unpaid despesas
            has_unpaid = any(
                item.get('_despesa') and item.get('_despesa').estado != EstadoDespesa.PAGO
                for item in selected_data
            )
            if has_unpaid:
                self.marcar_pago_btn.pack(side="left", padx=5)

            self.report_btn.pack(side="left", padx=5)
            self.delete_btn.pack(side="left", padx=5)

            # Calculate and show total
            total = sum(item.get('valor_com_iva', 0) for item in selected_data)
            self.total_label.configure(text=f"Total: €{total:,.2f}")
            self.total_label.pack(side="left", padx=20)
        else:
            # Hide entire selection frame when nothing is selected
            self.selection_frame.pack_forget()

    def cancelar_selecao(self):
        """Cancel selection"""
        self.table.clear_selection()

    def marcar_como_pago(self):
        """Mark selected despesas as paid"""
        selected_data = self.table.get_selected_data()
        if len(selected_data) == 0:
            return

        # Filter only unpaid despesas
        unpaid_despesas = [
            item.get('_despesa') for item in selected_data
            if item.get('_despesa') and item.get('_despesa').estado != EstadoDespesa.PAGO
        ]

        if len(unpaid_despesas) == 0:
            messagebox.showinfo("Info", "Todas as despesas selecionadas já estão pagas.")
            return

        # Confirm action
        resposta = messagebox.askyesno(
            "Confirmar",
            f"Marcar {len(unpaid_despesas)} despesa(s) como pagas?\n\n"
            f"Data de pagamento será definida como hoje ({date.today().strftime('%Y-%m-%d')})."
        )

        if resposta:
            hoje = date.today()
            erros = []

            for despesa in unpaid_despesas:
                sucesso, erro = self.manager.atualizar(
                    despesa.id,
                    estado=EstadoDespesa.PAGO,
                    data_pagamento=hoje
                )
                if not sucesso:
                    erros.append(f"{despesa.numero}: {erro}")

            if len(erros) == 0:
                self.carregar_despesas()
                self.table.clear_selection()
            else:
                messagebox.showerror("Erro", f"Erros ao marcar despesas:\n" + "\n".join(erros))
                self.carregar_despesas()

    def criar_relatorio(self):
        """Create report for selected despesas and navigate to Relatorios tab"""
        selected_data = self.table.get_selected_data()
        if len(selected_data) > 0:
            # Extract despesa IDs from selected data
            despesa_ids = [item.get('id') for item in selected_data if item.get('id')]

            # Navigate to Relatorios tab
            # Hierarchy: self (DespesasScreen) -> master (content_frame) -> master (MainWindow)
            main_window = self.master.master
            if hasattr(main_window, 'show_relatorios'):
                main_window.show_relatorios(despesa_ids=despesa_ids)
            else:
                messagebox.showerror(
                    "Erro",
                    "Não foi possível navegar para a aba de Relatórios"
                )

    def on_search_change(self, *args):
        """
        Reactive search handler - called on every keystroke
        Filters despesas dynamically as user types
        """
        search_text = self.search_var.get()

        # Get base despesas from search
        if search_text and search_text.strip():
            # Use backend search method
            despesas = self.manager.filtrar_por_texto(search_text)
        else:
            # No search text, get all
            despesas = self.manager.listar_todas()

        # Apply existing filters on top of search results
        tipo = self.tipo_filter.get()
        estado = self.estado_filter.get()

        # Filter by tipo
        if tipo != "Todos":
            tipo_map = {
                "Fixa Mensal": TipoDespesa.FIXA_MENSAL,
                "Pessoal BA": TipoDespesa.PESSOAL_BRUNO,
                "Pessoal RR": TipoDespesa.PESSOAL_RAFAEL,
                "Equipamento": TipoDespesa.EQUIPAMENTO,
                "Projeto": TipoDespesa.PROJETO
            }
            tipo_enum = tipo_map[tipo]
            despesas = [d for d in despesas if d.tipo == tipo_enum]

        # Filter by estado
        if estado != "Todos":
            estado_map = {
                "Pendente": EstadoDespesa.PENDENTE,
                "Vencido": EstadoDespesa.VENCIDO,
                "Pago": EstadoDespesa.PAGO
            }
            estado_enum = estado_map[estado]
            despesas = [d for d in despesas if d.estado == estado_enum]

        # Update table with highlighting (pass search_text for visual markers)
        search_term = search_text.strip() if search_text and search_text.strip() else None
        data = [self.despesa_to_dict(d, search_text=search_term) for d in despesas]
        self.table.set_data(data)

    def limpar_pesquisa(self):
        """Clear search field and refresh results"""
        self.search_var.set("")
        self.search_entry.focus()

    def show_context_menu(self, event, data: dict):
        """
        Mostra menu de contexto (right-click) para uma despesa

        Args:
            event: Evento do clique (para posição)
            data: Dados da linha clicada
        """
        despesa = data.get('_despesa')
        if not despesa:
            return

        # Criar menu
        menu = tk.Menu(self, tearoff=0)

        # ✏️ Editar
        menu.add_command(
            label="✏️ Editar",
            command=lambda: self.editar_despesa(data)
        )

        # 📋 Duplicar
        menu.add_command(
            label="📋 Duplicar",
            command=lambda: self._duplicar_from_context(despesa)
        )

        menu.add_separator()

        # Ações dependem do estado atual
        if despesa.estado == EstadoDespesa.PENDENTE:
            menu.add_command(
                label="✅ Marcar como Pago",
                command=lambda: self._marcar_pago_from_context(despesa)
            )
        elif despesa.estado == EstadoDespesa.VENCIDO:
            menu.add_command(
                label="✅ Marcar como Pago",
                command=lambda: self._marcar_pago_from_context(despesa)
            )
            menu.add_command(
                label="⏪ Voltar a Pendente",
                command=lambda: self._marcar_pendente_from_context(despesa)
            )
        elif despesa.estado == EstadoDespesa.PAGO:
            menu.add_command(
                label="⏪ Voltar a Pendente",
                command=lambda: self._marcar_pendente_from_context(despesa)
            )

        menu.add_separator()

        # 🗑️ Apagar
        menu.add_command(
            label="🗑️ Apagar",
            command=lambda: self._apagar_from_context(despesa)
        )

        # Mostrar menu na posição do cursor
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def _duplicar_from_context(self, despesa):
        """Duplica despesa a partir do menu de contexto"""
        try:
            # Confirmar duplicação
            resposta = messagebox.askyesno(
                "Duplicar Despesa",
                f"Duplicar despesa {despesa.numero}?\n\n"
                f"Fornecedor: {despesa.credor.nome if despesa.credor else '-'}\n"
                f"Descrição: {despesa.descricao[:50]}...\n\n"
                f"A nova despesa será criada com estado PENDENTE\n"
                f"e data de hoje."
            )

            if not resposta:
                return

            # Duplicar
            sucesso, nova_despesa, erro = self.manager.duplicar_despesa(despesa.id)

            if sucesso:
                # Recarregar lista
                self.carregar_despesas()
                self.table.clear_selection()

                # Abrir nova despesa para edição
                messagebox.showinfo(
                    "Sucesso",
                    f"Despesa duplicada como {nova_despesa.numero}\n\n"
                    f"Abrindo para edição..."
                )
                self.abrir_formulario(nova_despesa)

            else:
                messagebox.showerror("Erro", erro or "Erro ao duplicar despesa")

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao duplicar despesa: {str(e)}")

    def _marcar_pago_from_context(self, despesa):
        """Marca despesa como PAGO a partir do menu de contexto"""
        try:
            # Confirmar ação
            hoje = date.today()
            resposta = messagebox.askyesno(
                "Marcar como Pago",
                f"Marcar despesa {despesa.numero} como paga?\n\n"
                f"Data de pagamento será definida como hoje ({hoje.strftime('%d/%m/%Y')}).\n\n"
                f"⚠️ ATENÇÃO: Isto afeta os cálculos de Saldos Pessoais!"
            )

            if not resposta:
                return

            sucesso, erro = self.manager.mudar_estado(
                despesa.id,
                EstadoDespesa.PAGO,
                data_pagamento=hoje
            )

            if sucesso:
                self.carregar_despesas()
                self.table.clear_selection()
                messagebox.showinfo("Sucesso", f"Despesa {despesa.numero} marcada como paga")
            else:
                messagebox.showerror("Erro", erro or "Erro ao mudar estado")

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao marcar como pago: {str(e)}")

    def _marcar_pendente_from_context(self, despesa):
        """Marca despesa como PENDENTE a partir do menu de contexto"""
        try:
            # Confirmar ação
            resposta = messagebox.askyesno(
                "Voltar a Pendente",
                f"Marcar despesa {despesa.numero} como pendente?\n\n"
                f"Data de pagamento será removida."
            )

            if not resposta:
                return

            sucesso, erro = self.manager.mudar_estado(
                despesa.id,
                EstadoDespesa.PENDENTE
            )

            if sucesso:
                self.carregar_despesas()
                self.table.clear_selection()
                messagebox.showinfo("Sucesso", f"Despesa {despesa.numero} marcada como pendente")
            else:
                messagebox.showerror("Erro", erro or "Erro ao mudar estado")

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao marcar como pendente: {str(e)}")

    def _apagar_from_context(self, despesa):
        """Apaga despesa a partir do menu de contexto"""
        try:
            # Confirmar exclusão
            resposta = messagebox.askyesno(
                "Confirmar Exclusão",
                f"Tem certeza que deseja apagar a despesa {despesa.numero}?\n\n"
                f"Fornecedor: {despesa.credor.nome if despesa.credor else '-'}\n"
                f"Descrição: {despesa.descricao[:50]}...\n\n"
                f"⚠️ ATENÇÃO: Esta ação não pode ser desfeita!\n"
                f"⚠️ Isto vai afetar os cálculos de Saldos Pessoais!",
                icon='warning'
            )

            if not resposta:
                return

            sucesso, erro = self.manager.apagar(despesa.id)

            if sucesso:
                self.carregar_despesas()
                self.table.clear_selection()
                messagebox.showinfo("Sucesso", f"Despesa {despesa.numero} apagada com sucesso")
            else:
                messagebox.showerror("Erro", erro or "Erro ao apagar despesa")

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao apagar despesa: {str(e)}")


class FormularioDespesaDialog(BaseDialogLarge):
    """
    Dialog para criar/editar despesas
    """

    def __init__(self, parent, manager: DespesasManager, despesa=None, callback=None):
        self.manager = manager
        self.despesa = despesa
        self.callback = callback
        self.parent_ref = parent

        title = "Nova Despesa" if not despesa else f"Editar Despesa {despesa.numero}"
        super().__init__(parent, title=title)

        # Create form
        self.create_form()

        if despesa:
            self.carregar_dados()

        # Handle window close to clear selection
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def create_form(self):
        """Create form fields"""

        # Use main_frame (already scrollable from BaseDialogLarge)
        scroll = self.main_frame

        # Tipo
        ctk.CTkLabel(scroll, text="Tipo *", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", pady=(10, 5))
        self.tipo_var = ctk.StringVar(value="FIXA_MENSAL")
        tipo_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        tipo_frame.pack(fill="x", pady=(0, 10))

        tipos = [
            ("Fixa Mensal", "FIXA_MENSAL"),
            ("Pessoal BA", "PESSOAL_BRUNO"),
            ("Pessoal RR", "PESSOAL_RAFAEL"),
            ("Equipamento", "EQUIPAMENTO"),
            ("Projeto", "PROJETO")
        ]

        for i, (label, value) in enumerate(tipos):
            ctk.CTkRadioButton(
                tipo_frame,
                text=label,
                variable=self.tipo_var,
                value=value
            ).pack(side="left", padx=(0, 15))

        # Data
        ctk.CTkLabel(scroll, text="Data *", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", pady=(10, 5))
        from ui.components.date_picker_dropdown import DatePickerDropdown
        self.data_picker = DatePickerDropdown(scroll, placeholder="Selecionar data...")
        self.data_picker.pack(fill="x", pady=(0, 10))

        # Credor/Fornecedor
        ctk.CTkLabel(scroll, text="Credor/Fornecedor", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", pady=(10, 5))
        fornecedores = self.manager.obter_fornecedores()
        fornecedor_options = ["(Nenhum)"] + [f"{f.numero} - {f.nome}" for f in fornecedores]
        self.credor_dropdown = ctk.CTkOptionMenu(scroll, values=fornecedor_options, width=400)
        self.credor_dropdown.pack(anchor="w", pady=(0, 10))
        self.fornecedores_map = {f"{f.numero} - {f.nome}": f.id for f in fornecedores}

        # Projeto associado
        ctk.CTkLabel(scroll, text="Projeto Associado", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", pady=(10, 5))
        projetos = self.manager.obter_projetos()
        projeto_options = ["(Nenhum)"] + [f"{p.numero} - {p.descricao[:30]}" for p in projetos]
        self.projeto_dropdown = ctk.CTkOptionMenu(scroll, values=projeto_options, width=400)
        self.projeto_dropdown.pack(anchor="w", pady=(0, 10))
        self.projetos_map = {f"{p.numero} - {p.descricao[:30]}": p.id for p in projetos}

        # Descrição
        ctk.CTkLabel(scroll, text="Descrição *", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", pady=(10, 5))
        self.descricao_entry = ctk.CTkTextbox(scroll, height=80)
        self.descricao_entry.pack(fill="x", pady=(0, 10))

        # Valores
        valores_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        valores_frame.pack(fill="x", pady=(10, 10))
        valores_frame.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(valores_frame, text="Valor sem IVA *", font=ctk.CTkFont(size=13, weight="bold")).grid(row=0, column=0, sticky="w", padx=(0, 10))
        self.valor_sem_iva_entry = ctk.CTkEntry(valores_frame, placeholder_text="0.00")
        self.valor_sem_iva_entry.grid(row=1, column=0, sticky="ew", padx=(0, 10), pady=(5, 10))

        ctk.CTkLabel(valores_frame, text="Valor com IVA *", font=ctk.CTkFont(size=13, weight="bold")).grid(row=0, column=1, sticky="w")
        self.valor_com_iva_entry = ctk.CTkEntry(valores_frame, placeholder_text="0.00")
        self.valor_com_iva_entry.grid(row=1, column=1, sticky="ew", pady=(5, 10))

        # Estado
        ctk.CTkLabel(scroll, text="Estado *", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", pady=(10, 5))
        self.estado_dropdown = ctk.CTkOptionMenu(scroll, values=["Pendente", "Vencido", "Pago"])
        self.estado_dropdown.pack(anchor="w", pady=(0, 10))

        # Data pagamento
        ctk.CTkLabel(scroll, text="Data Pagamento (se pago)", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", pady=(10, 5))
        self.data_pagamento_picker = DatePickerDropdown(scroll, placeholder="Selecionar data de pagamento...")
        self.data_pagamento_picker.pack(fill="x", pady=(0, 10))

        # Nota
        ctk.CTkLabel(scroll, text="Nota", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", pady=(10, 5))
        self.nota_entry = ctk.CTkTextbox(scroll, height=60)
        self.nota_entry.pack(fill="x", pady=(0, 10))

        # Buttons
        btn_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(20, 0))

        cancel_btn = ctk.CTkButton(
            btn_frame,
            text="Cancelar",
            command=self._on_close,
            width=120,
            fg_color="gray",
            hover_color="darkgray"
        )
        cancel_btn.pack(side="right", padx=5)

        save_btn = ctk.CTkButton(
            btn_frame,
            text="Guardar",
            command=self.guardar,
            width=120,
            fg_color=("#F44336", "#C62828"),
            hover_color=("#E57373", "#B71C1C")
        )
        save_btn.pack(side="right", padx=5)

    def carregar_dados(self):
        """Load despesa data into form"""
        d = self.despesa

        self.tipo_var.set(d.tipo.value)

        if d.data:
            self.data_picker.set_date(d.data)

        if d.credor:
            credor_str = f"{d.credor.numero} - {d.credor.nome}"
            self.credor_dropdown.set(credor_str)

        if d.projeto:
            projeto_str = f"{d.projeto.numero} - {d.projeto.descricao[:30]}"
            self.projeto_dropdown.set(projeto_str)

        self.descricao_entry.insert("1.0", d.descricao)

        self.valor_sem_iva_entry.insert(0, str(d.valor_sem_iva))
        self.valor_com_iva_entry.insert(0, str(d.valor_com_iva))

        estado_map = {
            EstadoDespesa.PENDENTE: "Pendente",
            EstadoDespesa.VENCIDO: "Vencido",
            EstadoDespesa.PAGO: "Pago"
        }
        self.estado_dropdown.set(estado_map[d.estado])

        if d.data_pagamento:
            self.data_pagamento_picker.set_date(d.data_pagamento)

        if d.nota:
            self.nota_entry.insert("1.0", d.nota)

    def guardar(self):
        """Save despesa"""
        try:
            # Get values
            tipo_str = self.tipo_var.get()
            tipo = TipoDespesa[tipo_str]

            if not self.data_picker.get():
                messagebox.showerror("Erro", "Data é obrigatória")
                return
            data_despesa = self.data_picker.get_date()

            credor_str = self.credor_dropdown.get()
            credor_id = self.fornecedores_map.get(credor_str) if credor_str != "(Nenhum)" else None

            projeto_str = self.projeto_dropdown.get()
            projeto_id = self.projetos_map.get(projeto_str) if projeto_str != "(Nenhum)" else None

            descricao = self.descricao_entry.get("1.0", "end-1c").strip()
            if not descricao:
                messagebox.showerror("Erro", "Descrição é obrigatória")
                return

            valor_sem_iva_str = self.valor_sem_iva_entry.get().strip()
            if not valor_sem_iva_str:
                messagebox.showerror("Erro", "Valor sem IVA é obrigatório")
                return
            valor_sem_iva = Decimal(valor_sem_iva_str.replace(',', '.'))

            valor_com_iva_str = self.valor_com_iva_entry.get().strip()
            if not valor_com_iva_str:
                messagebox.showerror("Erro", "Valor com IVA é obrigatório")
                return
            valor_com_iva = Decimal(valor_com_iva_str.replace(',', '.'))

            estado_map = {
                "Pendente": EstadoDespesa.PENDENTE,
                "Vencido": EstadoDespesa.VENCIDO,
                "Pago": EstadoDespesa.PAGO
            }
            estado = estado_map[self.estado_dropdown.get()]

            data_pagamento = None
            if self.data_pagamento_picker.get():
                data_pagamento = self.data_pagamento_picker.get_date()

            nota = self.nota_entry.get("1.0", "end-1c").strip() or None

            # Create or update
            if self.despesa:
                sucesso, erro = self.manager.atualizar(
                    self.despesa.id,
                    tipo=tipo,
                    data=data_despesa,
                    descricao=descricao,
                    valor_sem_iva=valor_sem_iva,
                    valor_com_iva=valor_com_iva,
                    credor_id=credor_id,
                    projeto_id=projeto_id,
                    estado=estado,
                    data_pagamento=data_pagamento,
                    nota=nota
                )
                msg = "Despesa atualizada com sucesso!"
            else:
                sucesso, despesa, erro = self.manager.criar(
                    tipo=tipo,
                    data=data_despesa,
                    descricao=descricao,
                    valor_sem_iva=valor_sem_iva,
                    valor_com_iva=valor_com_iva,
                    credor_id=credor_id,
                    projeto_id=projeto_id,
                    estado=estado,
                    data_pagamento=data_pagamento,
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

    def _setup_scroll_capture(self):
        """Capture scroll events on this dialog and redirect only to internal scrollable frame"""
        # Get the internal canvas from CTkScrollableFrame
        if hasattr(self.scroll, '_parent_canvas'):
            canvas = self.scroll._parent_canvas

            def handle_scroll(event):
                """Handle scroll event - redirect to internal canvas and stop propagation"""
                # Scroll the internal canvas
                if event.num == 4 or event.delta > 0:
                    # Scroll up
                    canvas.yview_scroll(-1, "units")
                elif event.num == 5 or event.delta < 0:
                    # Scroll down
                    canvas.yview_scroll(1, "units")

                # Return "break" to stop event propagation
                return "break"

            # Bind with add=True to not remove existing bindings
            # Windows and MacOS
            self.bind_all("<MouseWheel>", handle_scroll, add=True)
            # Linux
            self.bind_all("<Button-4>", handle_scroll, add=True)
            self.bind_all("<Button-5>", handle_scroll, add=True)

    def _on_close(self):
        """Handle window close - clear selection"""
        # No need to unbind - tkinter cleans up when dialog destroys
        if hasattr(self.parent_ref, 'table'):
            self.parent_ref.table.clear_selection()
        self.destroy()
