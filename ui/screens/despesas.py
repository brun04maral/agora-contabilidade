# -*- coding: utf-8 -*-
"""
Tela de gestão de Despesas
"""
import customtkinter as ctk
import tkinter as tk
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from datetime import date
import tkinter.messagebox as messagebox

from logic.despesas import DespesasManager
from database.models import TipoDespesa, EstadoDespesa
from ui.components.base_screen import BaseScreen
from assets.resources import get_icon, DESPESAS


class DespesasScreen(BaseScreen):
    """
    Tela de gestão de Despesas (CRUD completo)
    """

    def __init__(self, parent, db_session: Session, filtro_estado=None, filtro_tipo=None, **kwargs):
        self.db_session = db_session
        self.manager = DespesasManager(db_session)
        self.filtro_inicial_estado = filtro_estado
        self.filtro_inicial_tipo = filtro_tipo

        # Initialize filter widgets (created in toolbar_slot)
        self.search_entry = None
        self.tipo_filter = None
        self.estado_filter = None

        # Call parent __init__ (this will call abstract methods)
        super().__init__(parent, db_session, **kwargs)

    # ===== ABSTRACT METHODS FROM BaseScreen =====

    def get_screen_title(self) -> str:
        """Return screen title"""
        return "Despesas"

    def get_screen_icon(self):
        """Return screen icon (PIL Image or None)"""
        return get_icon(DESPESAS, size=(28, 28))

    def get_table_columns(self) -> List[Dict[str, Any]]:
        """Return table column definitions"""
        return [
            {'key': 'numero', 'label': 'ID', 'width': 100, 'sortable': True},
            {'key': 'data', 'label': 'Data', 'width': 120, 'sortable': True},
            {'key': 'tipo', 'label': 'Tipo', 'width': 140, 'sortable': False},
            {'key': 'credor_nome', 'label': 'Credor', 'width': 160, 'sortable': True},
            {'key': 'descricao', 'label': 'Descrição', 'width': 280, 'sortable': False},
            {'key': 'valor_com_iva_fmt', 'label': 'Valor c/ IVA', 'width': 120, 'sortable': True},
            {'key': 'estado', 'label': 'Estado', 'width': 110, 'sortable': True},
        ]

    def load_data(self) -> List[Any]:
        """Load despesas from database and return as list of objects"""
        try:
            # Get search filter (widget pode não existir em __init__)
            search = None
            if hasattr(self, 'search_entry') and self.search_entry:
                try:
                    search = self.search_entry.get().strip() or None
                except Exception:
                    pass

            # Get dropdown filters
            tipo = "Todos"
            if hasattr(self, 'tipo_filter') and self.tipo_filter:
                try:
                    tipo = self.tipo_filter.get()
                except Exception:
                    pass

            estado = "Todos"
            if hasattr(self, 'estado_filter') and self.estado_filter:
                try:
                    estado = self.estado_filter.get()
                except Exception:
                    pass

            # Apply search
            if search:
                despesas = self.manager.filtrar_por_texto(search)
            else:
                despesas = self.manager.listar_todas()

            # Apply tipo filter
            if tipo != "Todos":
                tipo_map = {
                    "Fixa Mensal": TipoDespesa.FIXA_MENSAL,
                    "Pessoal BA": TipoDespesa.PESSOAL_BRUNO,
                    "Pessoal RR": TipoDespesa.PESSOAL_RAFAEL,
                    "Equipamento": TipoDespesa.EQUIPAMENTO,
                    "Projeto": TipoDespesa.PROJETO
                }
                tipo_enum = tipo_map.get(tipo)
                if tipo_enum:
                    despesas = [d for d in despesas if d.tipo == tipo_enum]

            # Apply estado filter
            if estado != "Todos":
                estado_map = {
                    "Pendente": EstadoDespesa.PENDENTE,
                    "Vencido": EstadoDespesa.VENCIDO,
                    "Pago": EstadoDespesa.PAGO
                }
                estado_enum = estado_map.get(estado)
                if estado_enum:
                    despesas = [d for d in despesas if d.estado == estado_enum]

            return despesas  # NUNCA None, sempre lista

        except Exception as e:
            print(f"ERROR in load_data(): {e}")
            import traceback
            traceback.print_exc()
            return []  # SEMPRE retornar lista vazia em erro

    def item_to_dict(self, item: Any) -> Dict[str, Any]:
        """Convert despesa object to dict for table"""
        # Reusar lógica de despesa_to_dict() existente mas sem search_text
        tipo_label = self.tipo_to_label(item.tipo)
        if item.despesa_template_id:
            tipo_label += "*"

        credor_nome = item.credor.nome if item.credor else '-'

        return {
            'id': item.id,
            'numero': item.numero,
            'data': item.data.strftime("%Y-%m-%d") if item.data else '-',
            'tipo': tipo_label,
            'credor_nome': credor_nome,
            'descricao': item.descricao or '',
            'valor_com_iva': float(item.valor_com_iva),
            'valor_com_iva_fmt': f"€{float(item.valor_com_iva):,.2f}",
            'estado': self.estado_to_label(item.estado),
            '_bg_color': self.get_estado_color(item.estado),
            '_despesa': item  # CRÍTICO: guardar objeto original
        }

    def get_context_menu_items(self, data: dict) -> List[Dict[str, Any]]:
        """Define ações do context menu e barra de ações"""

        # Para barra de ações (data vazio {} quando BaseScreen chama)
        if not data or '_despesa' not in data:
            return [
                {
                    'label': '✏️ Editar',
                    'command': self._editar_selecionada,
                    'min_selection': 1,
                    'max_selection': 1,
                    'fg_color': ('#2196F3', '#1976D2'),
                    'hover_color': ('#1976D2', '#1565C0'),
                    'width': 100
                },
                {
                    'label': '📋 Duplicar',
                    'command': self._duplicar_selecionadas,
                    'min_selection': 1,
                    'max_selection': None,
                    'fg_color': ('#9C27B0', '#7B1FA2'),
                    'hover_color': ('#7B1FA2', '#6A1B9A'),
                    'width': 110
                },
                {
                    'label': '✅ Marcar Pago',
                    'command': self._pagar_selecionadas,
                    'min_selection': 1,
                    'max_selection': None,
                    'fg_color': ('#4CAF50', '#388E3C'),
                    'hover_color': ('#388E3C', '#2E7D32'),
                    'width': 130
                },
                {
                    'label': '📊 Relatório',
                    'command': self.criar_relatorio,
                    'min_selection': 1,
                    'max_selection': None,
                    'fg_color': ('#607D8B', '#455A64'),
                    'hover_color': ('#455A64', '#37474F'),
                    'width': 110
                },
                {
                    'label': '🗑️ Apagar',
                    'command': self._apagar_selecionadas,
                    'min_selection': 1,
                    'max_selection': None,
                    'fg_color': ('#F44336', '#C62828'),
                    'hover_color': ('#D32F2F', '#B71C1C'),
                    'width': 100
                }
            ]

        # Para context menu (ações contextuais baseadas em estado)
        despesa = data.get('_despesa')
        if not despesa:
            return []

        items = [
            {'label': '✏️ Editar', 'command': lambda: self.editar_despesa(data)},
            {'label': '📋 Duplicar', 'command': lambda: self._duplicar_from_context(despesa)},
            {'separator': True},
        ]

        # Ações baseadas no estado
        if despesa.estado == EstadoDespesa.PENDENTE:
            items.append({'label': '✅ Marcar como Pago', 'command': lambda: self._marcar_pago_from_context(despesa)})
        elif despesa.estado == EstadoDespesa.VENCIDO:
            items.append({'label': '✅ Marcar como Pago', 'command': lambda: self._marcar_pago_from_context(despesa)})
            items.append({'label': '⏪ Voltar a Pendente', 'command': lambda: self._marcar_pendente_from_context(despesa)})
        elif despesa.estado == EstadoDespesa.PAGO:
            items.append({'label': '⏪ Voltar a Pendente', 'command': lambda: self._marcar_pendente_from_context(despesa)})

        items.append({'separator': True})
        items.append({'label': '🗑️ Apagar', 'command': lambda: self._apagar_from_context(despesa)})

        return items

    # ===== OPTIONAL METHODS =====

    def toolbar_slot(self, parent):
        """Create custom toolbar with search and filters"""
        # Frame principal
        toolbar_frame = ctk.CTkFrame(parent, fg_color="transparent")
        toolbar_frame.pack(fill="x", padx=0, pady=(0, 10))

        # Row 1: Search + botões especiais
        search_frame = ctk.CTkFrame(toolbar_frame, fg_color="transparent")
        search_frame.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
            search_frame,
            text="🔍 Pesquisar:",
            font=ctk.CTkFont(size=13)
        ).pack(side="left", padx=(0, 10))

        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Digite para pesquisar por fornecedor ou descrição...",
            width=400,
            height=35
        )
        self.search_entry.pack(side="left", padx=(0, 10))
        self.search_entry.bind("<KeyRelease>", lambda e: self.refresh_data())

        # Botão limpar search
        clear_btn = ctk.CTkButton(
            search_frame,
            text="✖",
            command=lambda: (self.search_entry.delete(0, 'end'), self.refresh_data()),
            width=35,
            height=35
        )
        clear_btn.pack(side="left", padx=(0, 20))

        # Botões especiais (Gerar Recorrentes + Editar Templates)
        gerar_btn = ctk.CTkButton(
            search_frame,
            text="🔁 Gerar Recorrentes",
            command=self.gerar_despesas_recorrentes,
            width=170,
            height=35,
            fg_color=("#2196F3", "#1976D2"),
            hover_color=("#64B5F6", "#1565C0")
        )
        gerar_btn.pack(side="left", padx=5)

        templates_btn = ctk.CTkButton(
            search_frame,
            text="📝 Editar Recorrentes",
            command=self.abrir_templates,
            width=170,
            height=35,
            fg_color=("#9C27B0", "#7B1FA2"),
            hover_color=("#BA68C8", "#6A1B9A")
        )
        templates_btn.pack(side="left", padx=5)

        # Row 2: Filters
        filters_frame = ctk.CTkFrame(toolbar_frame, fg_color="transparent")
        filters_frame.pack(fill="x")

        ctk.CTkLabel(
            filters_frame,
            text="Tipo:",
            font=ctk.CTkFont(size=13)
        ).pack(side="left", padx=(0, 10))

        self.tipo_filter = ctk.CTkOptionMenu(
            filters_frame,
            values=["Todos", "Fixa Mensal", "Pessoal BA", "Pessoal RR", "Equipamento", "Projeto"],
            command=lambda _: self.refresh_data(),
            width=180
        )
        self.tipo_filter.set(self.filtro_inicial_tipo or "Todos")
        self.tipo_filter.pack(side="left", padx=(0, 20))

        ctk.CTkLabel(
            filters_frame,
            text="Estado:",
            font=ctk.CTkFont(size=13)
        ).pack(side="left", padx=(0, 10))

        self.estado_filter = ctk.CTkOptionMenu(
            filters_frame,
            values=["Todos", "Pendente", "Vencido", "Pago"],
            command=lambda _: self.refresh_data(),
            width=120
        )
        self.estado_filter.set(self.filtro_inicial_estado or "Todos")
        self.estado_filter.pack(side="left")

    def on_add_click(self):
        """Handle add button click"""
        self.abrir_formulario(despesa=None)

    def on_item_double_click(self, data: dict):
        """Handle table row double-click (editar)"""
        despesa = data.get('_despesa')
        if despesa:
            self.abrir_formulario(despesa)

    def calculate_selection_total(self, selected_data: List[Dict[str, Any]]) -> float:
        """Calculate total value of selected despesas"""
        return sum(item.get('valor_com_iva', 0) for item in selected_data)

    # ===== BULK OPERATION METHODS FOR ACTION BAR =====

    def _editar_selecionada(self):
        """Edita despesa selecionada"""
        selected = self.get_selected_data()
        if selected and len(selected) == 1:
            self.on_item_double_click(selected[0])

    def _duplicar_selecionadas(self):
        """Duplica despesas selecionadas"""
        selected = self.get_selected_data()
        if not selected:
            return

        num = len(selected)
        msg = f"Duplicar {num} despesa(s)?"
        if not messagebox.askyesno("Confirmar", msg):
            return

        sucessos = 0
        erros = []

        for data in selected:
            despesa = data.get('_despesa')
            if despesa:
                sucesso, nova, erro = self.manager.duplicar_despesa(despesa.id)
                if sucesso:
                    sucessos += 1
                else:
                    erros.append(f"{despesa.numero}: {erro}")

        if sucessos > 0:
            self.refresh_data()
            if not erros:
                messagebox.showinfo("Sucesso", f"{sucessos} despesa(s) duplicada(s)")
            else:
                messagebox.showwarning("Parcial", f"{sucessos} sucesso(s), {len(erros)} erro(s):\n" + "\n".join(erros[:5]))
        elif erros:
            messagebox.showerror("Erro", "\n".join(erros[:5]))

    def _pagar_selecionadas(self):
        """Marca despesas selecionadas como pagas"""
        selected = self.get_selected_data()
        if not selected:
            return

        # Filtrar apenas não pagas
        unpaid = [d.get('_despesa') for d in selected
                  if d.get('_despesa') and d.get('_despesa').estado != EstadoDespesa.PAGO]

        if not unpaid:
            messagebox.showinfo("Info", "Todas já estão pagas.")
            return

        if not messagebox.askyesno("Confirmar", f"Marcar {len(unpaid)} como pagas?"):
            return

        hoje = date.today()
        erros = []

        for despesa in unpaid:
            sucesso, erro = self.manager.atualizar(
                despesa.id,
                estado=EstadoDespesa.PAGO,
                data_pagamento=hoje
            )
            if not sucesso:
                erros.append(f"{despesa.numero}: {erro}")

        if not erros:
            self.refresh_data()
            messagebox.showinfo("Sucesso", f"{len(unpaid)} despesa(s) marcada(s) como paga(s)")
        else:
            messagebox.showerror("Erro", "\n".join(erros))
            self.refresh_data()

    def _apagar_selecionadas(self):
        """Apaga despesas selecionadas"""
        selected = self.get_selected_data()
        if not selected:
            return

        num = len(selected)
        geradas_template = sum(1 for d in selected
                              if d.get('_despesa') and d.get('_despesa').despesa_template_id)

        msg = f"Apagar {num} despesa(s)?"
        if geradas_template > 0:
            msg += f"\n\n⚠️ {geradas_template} foram geradas de templates."

        if not messagebox.askyesno("Confirmar", msg):
            return

        sucessos = 0
        erros = []

        for data in selected:
            despesa = data.get('_despesa')
            if despesa:
                sucesso, erro = self.manager.apagar(despesa.id)
                if sucesso:
                    sucessos += 1
                else:
                    erros.append(f"{despesa.numero}: {erro}")

        if sucessos > 0:
            msg_result = f"✅ {sucessos} despesa(s) apagada(s)!"
            if erros:
                msg_result += f"\n\n⚠️ {len(erros)} erro(s)"
            messagebox.showinfo("Resultado", msg_result)
        else:
            messagebox.showerror("Erro", "\n".join(erros[:5]))

        self.refresh_data()

    # ===== HELPER METHODS (MANTER) =====

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

    def get_estado_color(self, estado: EstadoDespesa) -> tuple:
        """Get color for estado (returns tuple: light, dark mode) - Opção 3 Agora Inspired"""
        color_map = {
            EstadoDespesa.PAGO: ("#E8F5E0", "#4A7028"),        # Verde pastel - positivo
            EstadoDespesa.PENDENTE: ("#FFF4CC", "#806020"),    # Dourado pastel - harmoniza com BA
            EstadoDespesa.VENCIDO: ("#FFE5D0", "#8B4513")      # Laranja pastel - atenção urgente
        }
        return color_map.get(estado, ("#E0E0E0", "#4A4A4A"))

    def abrir_formulario(self, despesa=None):
        """Navigate to despesa_form screen for create/edit"""
        main_window = self.master.master
        if hasattr(main_window, 'show_screen'):
            if despesa:
                main_window.show_screen("despesa_form", despesa_id=despesa.id)
            else:
                main_window.show_screen("despesa_form", despesa_id=None)
        else:
            messagebox.showerror("Erro", "Não foi possível abrir formulário")

    def editar_despesa(self, data: dict):
        """Edit despesa (triggered by double-click or context menu)"""
        despesa = data.get('_despesa')
        if despesa:
            self.abrir_formulario(despesa)

    def gerar_despesas_recorrentes(self):
        """Gera despesas recorrentes para o mês atual"""
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
            self.refresh_data()  # Recarregar lista
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
            self.refresh_data()

        dialog.protocol("WM_DELETE_WINDOW", on_close)

    def criar_relatorio(self):
        """Create report for selected despesas and navigate to Relatorios tab"""
        selected_data = self.get_selected_data()
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

    # ===== CONTEXT MENU HELPERS =====

    def _duplicar_from_context(self, despesa):
        """Duplica despesa a partir do menu de contexto"""
        try:
            # Confirmar duplicação
            resposta = messagebox.askyesno(
                "Duplicar Despesa",
                f"Duplicar despesa {despesa.numero}?\n\n"
                f"Fornecedor: {despesa.credor.nome if despesa.credor else '-'}\n"
                f"Descrição: {despesa.descricao[:50] if despesa.descricao else '-'}...\n\n"
                f"A nova despesa será criada com estado PENDENTE\n"
                f"e data de hoje."
            )

            if not resposta:
                return

            # Duplicar
            sucesso, nova_despesa, erro = self.manager.duplicar_despesa(despesa.id)

            if sucesso:
                # Recarregar lista
                self.refresh_data()

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
                self.refresh_data()
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
                self.refresh_data()
                messagebox.showinfo("Sucesso", f"Despesa {despesa.numero} marcada como pendente")
            else:
                messagebox.showerror("Erro", erro or "Erro ao mudar estado")

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao marcar como pendente: {str(e)}")

    def _apagar_from_context(self, despesa):
        """Apaga despesa a partir do menu de contexto"""
        try:
            # Confirmar exclusão
            descricao_preview = despesa.descricao[:50] if despesa.descricao else '-'
            resposta = messagebox.askyesno(
                "Confirmar Exclusão",
                f"Tem certeza que deseja apagar a despesa {despesa.numero}?\n\n"
                f"Fornecedor: {despesa.credor.nome if despesa.credor else '-'}\n"
                f"Descrição: {descricao_preview}...\n\n"
                f"⚠️ ATENÇÃO: Esta ação não pode ser desfeita!\n"
                f"⚠️ Isto vai afetar os cálculos de Saldos Pessoais!",
                icon='warning'
            )

            if not resposta:
                return

            sucesso, erro = self.manager.apagar(despesa.id)

            if sucesso:
                self.refresh_data()
                messagebox.showinfo("Sucesso", f"Despesa {despesa.numero} apagada com sucesso")
            else:
                messagebox.showerror("Erro", erro or "Erro ao apagar despesa")

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao apagar despesa: {str(e)}")
