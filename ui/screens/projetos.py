# -*- coding: utf-8 -*-
"""
Tela de gestão de Projetos - Usa BaseScreen template

Migrado para BaseScreen em 2025-11-24.
"""
import tkinter.messagebox as messagebox
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from datetime import date

from logic.projetos import ProjetosManager
from logic.clientes import ClientesManager
from database.models import TipoProjeto, EstadoProjeto
from ui.components.base_screen import BaseScreen
from assets.resources import PROJETOS


class ProjetosScreen(BaseScreen):
    """
    Tela de gestão de Projetos (lista com navegação para edição)
    Herda de BaseScreen para layout consistente.
    """

    def __init__(
        self,
        parent,
        db_session: Session,
        filtro_estado=None,
        filtro_cliente_id=None,
        filtro_tipo=None,
        filtro_premio_socio=None,
        filtro_owner=None,
        **kwargs
    ):
        # Managers
        self.manager = ProjetosManager(db_session)
        self.clientes_manager = ClientesManager(db_session)

        # Carregar clientes para filtro
        self.clientes_list = self.clientes_manager.listar_todos(order_by='nome')

        # Filtros especiais (não são OptionMenu padrão)
        self.filtro_premio_socio = filtro_premio_socio
        self.filtro_owner = filtro_owner
        self._filtro_cliente_id = filtro_cliente_id

        # Configuração do screen
        self.screen_config = {
            'title': 'Projetos',
            'icon_key': PROJETOS,
            'icon_fallback': '📁',
            'new_button_text': 'Novo Projeto',
            'new_button_color': ('#4CAF50', '#388E3C'),
            'new_button_hover': ('#66BB6A', '#2E7D32'),
            'search_placeholder': 'Digite para pesquisar por cliente ou descrição...',
            'table_height': 400,
        }

        # Filtros iniciais (só para dropdowns)
        initial_filters = {}
        if filtro_estado:
            initial_filters['estado'] = filtro_estado
        if filtro_tipo:
            initial_filters['tipo'] = filtro_tipo

        super().__init__(parent, db_session, initial_filters=initial_filters, **kwargs)

    # ========== Implementação dos métodos obrigatórios ==========

    def get_table_columns(self) -> List[Dict[str, Any]]:
        return [
            {'key': 'numero', 'label': 'ID', 'width': 80},
            {'key': 'tipo', 'label': 'Tipo', 'width': 140},
            {'key': 'cliente_nome', 'label': 'Cliente', 'width': 180},
            {'key': 'descricao', 'label': 'Descrição', 'width': 280, 'sortable': False},
            {'key': 'valor_sem_iva', 'label': 'Valor', 'width': 100,
             'formatter': lambda v: f"€{v:,.2f}" if v else "€0,00"},
            {'key': 'estado', 'label': 'Estado', 'width': 120},
        ]

    def load_data(self) -> list:
        # Atualizar estados automaticamente antes de carregar
        self.manager.atualizar_estados_projetos()
        return self.manager.listar_todos()

    def item_to_dict(self, projeto) -> dict:
        cliente_nome = projeto.cliente.nome if projeto.cliente else '-'
        descricao = projeto.descricao or ''

        data = {
            'id': projeto.id,
            'numero': projeto.numero,
            'tipo': self._tipo_to_label(projeto),
            'cliente_nome': cliente_nome,
            'descricao': descricao,
            'valor_sem_iva': float(projeto.valor_sem_iva),
            'estado': self._estado_to_label(projeto.estado),
            '_bg_color': self._estado_to_color(projeto.estado),
            '_projeto': projeto
        }

        # Strikethrough para projetos anulados
        if projeto.estado == EstadoProjeto.ANULADO:
            data['_strikethrough_except'] = ['estado']

        return data

    # ========== Métodos opcionais override ==========

    def get_filters_config(self) -> List[Dict[str, Any]]:
        return [
            {
                'key': 'tipo',
                'label': 'Tipo:',
                'values': ["Todos", "Empresa BA", "Empresa RR", "Pessoal BA", "Pessoal RR"],
                'width': 180
            },
            {
                'key': 'estado',
                'label': 'Estado:',
                'values': ["Todos", "Ativo", "Finalizado", "Pago", "Anulado"],
                'width': 150
            },
        ]

    def get_selection_actions(self) -> List[Dict[str, Any]]:
        return [
            {
                'text': '📊 Criar Relatório',
                'command': self._criar_relatorio,
                'fg_color': ('#9C27B0', '#7B1FA2'),
                'hover_color': ('#AB47BC', '#6A1B9A'),
                'width': 160
            }
        ]

    def get_context_menu_items(self, data: dict) -> List[Dict[str, Any]]:
        """
        Define ações do context menu e barra de ações.

        Args:
            data: Dict com dados da linha (vazio {} quando criar barra de ações)
        """
        # Para barra de ações (data vazio): retorna TODAS as ações possíveis
        if not data or '_projeto' not in data:
            return [
                {
                    'label': '✏️ Editar',
                    'command': self._editar_selecionado,
                    'min_selection': 1,
                    'max_selection': 1,
                    'fg_color': ('#2196F3', '#1976D2'),
                    'hover_color': ('#1976D2', '#1565C0'),
                    'width': 100
                },
                {
                    'label': '📋 Duplicar',
                    'command': self._duplicar_selecionado,
                    'min_selection': 1,
                    'max_selection': 1,
                    'fg_color': ('#9C27B0', '#7B1FA2'),
                    'hover_color': ('#7B1FA2', '#6A1B9A'),
                    'width': 110
                },
                {
                    'label': '✅ Finalizar',
                    'command': self._finalizar_selecionados,
                    'min_selection': 1,
                    'max_selection': None,
                    'fg_color': ('#4CAF50', '#388E3C'),
                    'hover_color': ('#388E3C', '#2E7D32'),
                    'width': 100
                },
                {
                    'label': '💰 Marcar Pago',
                    'command': self._pagar_selecionados,
                    'min_selection': 1,
                    'max_selection': None,
                    'fg_color': ('#4CAF50', '#388E3C'),
                    'hover_color': ('#388E3C', '#2E7D32'),
                    'width': 130
                },
                {
                    'label': '⛔ Anular',
                    'command': self._anular_selecionados,
                    'min_selection': 1,
                    'max_selection': None,
                    'fg_color': ('#FF9800', '#F57C00'),
                    'hover_color': ('#F57C00', '#EF6C00'),
                    'width': 100
                },
                {
                    'label': '🗑️ Apagar',
                    'command': self._apagar_selecionados,
                    'min_selection': 1,
                    'max_selection': None,
                    'fg_color': ('#F44336', '#D32F2F'),
                    'hover_color': ('#D32F2F', '#C62828'),
                    'width': 100
                }
            ]

        # Para context menu (data com projeto específico): ações contextuais
        projeto = data.get('_projeto')
        if not projeto:
            return []

        items = [
            {'label': '✏️ Editar', 'command': lambda: self.on_item_double_click(data)},
            {'label': '📋 Duplicar', 'command': lambda: self._duplicar(projeto)},
            {'separator': True},
        ]

        # Ações de estado
        if projeto.estado == EstadoProjeto.ATIVO:
            items.append({'label': '✅ Marcar como Finalizado', 'command': lambda: self._marcar_finalizado(projeto)})
        elif projeto.estado == EstadoProjeto.FINALIZADO:
            items.append({'label': '✅ Marcar como Pago', 'command': lambda: self._marcar_pago(projeto)})
            items.append({'label': '⏪ Voltar a Ativo', 'command': lambda: self._marcar_ativo(projeto)})
        elif projeto.estado == EstadoProjeto.PAGO:
            items.append({'label': '⏪ Voltar a Finalizado', 'command': lambda: self._marcar_finalizado(projeto)})

        if projeto.estado != EstadoProjeto.ANULADO:
            items.append({'separator': True})
            items.append({'label': '⛔ Anular Projeto', 'command': lambda: self._anular(projeto)})

        items.append({'separator': True})
        items.append({'label': '🗑️ Apagar', 'command': lambda: self._apagar(projeto)})

        return items

    def filter_by_search(self, items: list, search_text: str) -> list:
        return self.manager.filtrar_por_texto(search_text)

    def apply_filters(self, items: list, filters: Dict[str, List[str]]) -> list:
        projetos = items

        # Filtrar por tipo (multi-seleção)
        tipos_selecionados = filters.get('tipo', [])
        if tipos_selecionados:
            tipo_matches = []
            for tipo in tipos_selecionados:
                if tipo == "Empresa BA":
                    tipo_matches.extend([p for p in projetos if p.tipo == TipoProjeto.EMPRESA and p.owner == 'BA'])
                elif tipo == "Empresa RR":
                    tipo_matches.extend([p for p in projetos if p.tipo == TipoProjeto.EMPRESA and p.owner == 'RR'])
                elif tipo == "Pessoal BA":
                    tipo_matches.extend([p for p in projetos if p.tipo == TipoProjeto.PESSOAL and p.owner == 'BA'])
                elif tipo == "Pessoal RR":
                    tipo_matches.extend([p for p in projetos if p.tipo == TipoProjeto.PESSOAL and p.owner == 'RR'])

            # Remove duplicates preserving order
            seen = set()
            projetos = [p for p in tipo_matches if not (p.id in seen or seen.add(p.id))]

        # Filtrar por estado (multi-seleção)
        estados_selecionados = filters.get('estado', [])
        if estados_selecionados:
            estado_map = {
                "Ativo": EstadoProjeto.ATIVO,
                "Finalizado": EstadoProjeto.FINALIZADO,
                "Pago": EstadoProjeto.PAGO,
                "Anulado": EstadoProjeto.ANULADO
            }
            estado_enums = [estado_map[e] for e in estados_selecionados if e in estado_map]
            if estado_enums:
                projetos = [p for p in projetos if p.estado in estado_enums]

        # Filtros especiais (passados no constructor)
        if self._filtro_cliente_id:
            projetos = [p for p in projetos if p.cliente_id == self._filtro_cliente_id]

        if self.filtro_premio_socio:
            if self.filtro_premio_socio == "BA":
                projetos = [p for p in projetos if p.premio_bruno and p.premio_bruno > 0]
            elif self.filtro_premio_socio == "RR":
                projetos = [p for p in projetos if p.premio_rafael and p.premio_rafael > 0]

        if self.filtro_owner:
            projetos = [p for p in projetos if p.owner == self.filtro_owner and p.tipo == TipoProjeto.EMPRESA]

        return projetos

    def calculate_selection_total(self, selected_data: list) -> float:
        return sum(item.get('valor_sem_iva', 0) for item in selected_data)

    def on_item_double_click(self, data: dict):
        projeto = data.get('_projeto')
        if projeto:
            self._abrir_formulario(projeto)

    def on_new_item(self):
        self._abrir_formulario(None)

    # ========== Métodos privados ==========

    def _tipo_to_label(self, projeto) -> str:
        if projeto.tipo == TipoProjeto.EMPRESA:
            return f"Empresa {projeto.owner}"
        elif projeto.tipo == TipoProjeto.PESSOAL:
            return f"Pessoal {projeto.owner}"
        return str(projeto.tipo)

    def _estado_to_label(self, estado: EstadoProjeto) -> str:
        mapping = {
            EstadoProjeto.ATIVO: "Ativo",
            EstadoProjeto.FINALIZADO: "Finalizado",
            EstadoProjeto.PAGO: "Pago",
            EstadoProjeto.ANULADO: "Anulado"
        }
        return mapping.get(estado, str(estado))

    def _estado_to_color(self, estado: EstadoProjeto) -> tuple:
        mapping = {
            EstadoProjeto.ATIVO: ("#FFF4CC", "#806020"),
            EstadoProjeto.FINALIZADO: ("#FFE5D0", "#8B4513"),
            EstadoProjeto.PAGO: ("#E8F5E0", "#4A7028"),
            EstadoProjeto.ANULADO: ("#808080", "#505050")
        }
        return mapping.get(estado, ("#f8f8f8", "#252525"))

    def _abrir_formulario(self, projeto=None):
        main_window = self.master.master
        if hasattr(main_window, 'show_screen'):
            if projeto:
                main_window.show_screen("projeto_form", projeto_id=projeto.id)
            else:
                main_window.show_screen("projeto_form", projeto_id=None)
        else:
            messagebox.showerror("Erro", "Não foi possível abrir formulário")

    def _criar_relatorio(self):
        selected_data = self.get_selected_data()
        if len(selected_data) > 0:
            projeto_ids = [item.get('id') for item in selected_data if item.get('id')]
            main_window = self.master.master
            if hasattr(main_window, 'show_relatorios'):
                main_window.show_relatorios(projeto_ids=projeto_ids)
            else:
                messagebox.showerror("Erro", "Não foi possível navegar para Relatórios")

    def _duplicar(self, projeto):
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
                self.refresh_data()
                self._clear_selection()
                messagebox.showinfo("Sucesso", f"Projeto duplicado como {novo_projeto.numero}")
                self._abrir_formulario(novo_projeto)
            else:
                messagebox.showerror("Erro", erro or "Erro ao duplicar projeto")

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao duplicar projeto: {str(e)}")

    def _marcar_finalizado(self, projeto):
        try:
            resposta = messagebox.askyesno(
                "Marcar como Finalizado",
                f"Marcar projeto {projeto.numero} como finalizado?"
            )

            if not resposta:
                return

            sucesso, erro = self.manager.mudar_estado(projeto.id, EstadoProjeto.FINALIZADO)

            if sucesso:
                self.refresh_data()
                self._clear_selection()
            else:
                messagebox.showerror("Erro", erro or "Erro ao mudar estado")

        except Exception as e:
            messagebox.showerror("Erro", f"Erro: {str(e)}")

    def _marcar_pago(self, projeto):
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
                self.refresh_data()
                self._clear_selection()
            else:
                messagebox.showerror("Erro", erro or "Erro ao mudar estado")

        except Exception as e:
            messagebox.showerror("Erro", f"Erro: {str(e)}")

    def _marcar_ativo(self, projeto):
        try:
            resposta = messagebox.askyesno(
                "Voltar a Ativo",
                f"Marcar projeto {projeto.numero} como ativo?"
            )

            if not resposta:
                return

            sucesso, erro = self.manager.mudar_estado(projeto.id, EstadoProjeto.ATIVO)

            if sucesso:
                self.refresh_data()
                self._clear_selection()
            else:
                messagebox.showerror("Erro", erro or "Erro ao mudar estado")

        except Exception as e:
            messagebox.showerror("Erro", f"Erro: {str(e)}")

    def _anular(self, projeto):
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
                self.refresh_data()
                self._clear_selection()
            else:
                messagebox.showerror("Erro", erro or "Erro ao anular projeto")

        except Exception as e:
            messagebox.showerror("Erro", f"Erro: {str(e)}")

    def _apagar(self, projeto):
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
                self.refresh_data()
                self._clear_selection()
            else:
                messagebox.showerror("Erro", erro or "Erro ao apagar projeto")

        except Exception as e:
            messagebox.showerror("Erro", f"Erro: {str(e)}")

    # ========== Métodos para Barra de Ações (trabalham com seleção) ==========

    def _editar_selecionado(self):
        """Edita o único projeto selecionado."""
        selected = self.get_selected_data()
        if len(selected) == 1:
            self.on_item_double_click(selected[0])

    def _duplicar_selecionado(self):
        """Duplica o único projeto selecionado."""
        selected = self.get_selected_data()
        if len(selected) == 1:
            projeto = selected[0].get('_projeto')
            if projeto:
                self._duplicar(projeto)

    def _finalizar_selecionados(self):
        """Marca projetos selecionados como finalizados."""
        selected = self.get_selected_data()
        if not selected:
            return

        num = len(selected)
        resposta = messagebox.askyesno(
            "Marcar como Finalizados",
            f"Marcar {num} projeto(s) como finalizado(s)?"
        )

        if not resposta:
            return

        sucessos = 0
        erros = []

        for data in selected:
            projeto = data.get('_projeto')
            if projeto:
                sucesso, erro = self.manager.mudar_estado(projeto.id, EstadoProjeto.FINALIZADO)
                if sucesso:
                    sucessos += 1
                else:
                    erros.append(f"{projeto.numero}: {erro}")

        # Mostrar resultado
        if sucessos > 0:
            self.refresh_data()
            if len(erros) == 0:
                messagebox.showinfo("Sucesso", f"{sucessos} projeto(s) marcado(s) como finalizado(s)")
            else:
                messagebox.showwarning(
                    "Parcialmente Concluído",
                    f"{sucessos} sucesso(s), {len(erros)} erro(s):\n" + "\n".join(erros[:5])
                )
        elif erros:
            messagebox.showerror("Erro", "Erros:\n" + "\n".join(erros[:5]))

    def _pagar_selecionados(self):
        """Marca projetos selecionados como pagos."""
        selected = self.get_selected_data()
        if not selected:
            return

        num = len(selected)
        resposta = messagebox.askyesno(
            "Marcar como Pagos",
            f"Marcar {num} projeto(s) como pago(s)?"
        )

        if not resposta:
            return

        sucessos = 0
        erros = []

        for data in selected:
            projeto = data.get('_projeto')
            if projeto:
                sucesso, erro = self.manager.mudar_estado(projeto.id, EstadoProjeto.PAGO)
                if sucesso:
                    sucessos += 1
                else:
                    erros.append(f"{projeto.numero}: {erro}")

        # Mostrar resultado
        if sucessos > 0:
            self.refresh_data()
            if len(erros) == 0:
                messagebox.showinfo("Sucesso", f"{sucessos} projeto(s) marcado(s) como pago(s)")
            else:
                messagebox.showwarning(
                    "Parcialmente Concluído",
                    f"{sucessos} sucesso(s), {len(erros)} erro(s):\n" + "\n".join(erros[:5])
                )
        elif erros:
            messagebox.showerror("Erro", "Erros:\n" + "\n".join(erros[:5]))

    def _anular_selecionados(self):
        """Anula projetos selecionados."""
        selected = self.get_selected_data()
        if not selected:
            return

        num = len(selected)
        resposta = messagebox.askyesno(
            "Anular Projetos",
            f"Anular {num} projeto(s)?\n\n"
            f"⚠️ Projetos anulados não entram nos cálculos.",
            icon='warning'
        )

        if not resposta:
            return

        sucessos = 0
        erros = []

        for data in selected:
            projeto = data.get('_projeto')
            if projeto:
                sucesso, erro = self.manager.mudar_estado(projeto.id, EstadoProjeto.ANULADO)
                if sucesso:
                    sucessos += 1
                else:
                    erros.append(f"{projeto.numero}: {erro}")

        # Mostrar resultado
        if sucessos > 0:
            self.refresh_data()
            if len(erros) == 0:
                messagebox.showinfo("Sucesso", f"{sucessos} projeto(s) anulado(s)")
            else:
                messagebox.showwarning(
                    "Parcialmente Concluído",
                    f"{sucessos} sucesso(s), {len(erros)} erro(s):\n" + "\n".join(erros[:5])
                )
        elif erros:
            messagebox.showerror("Erro", "Erros:\n" + "\n".join(erros[:5]))

    def _apagar_selecionados(self):
        """Apaga projetos selecionados."""
        selected = self.get_selected_data()
        if not selected:
            return

        num = len(selected)
        resposta = messagebox.askyesno(
            "Confirmar Exclusão",
            f"Apagar {num} projeto(s)?\n\n"
            f"⚠️ Esta ação não pode ser desfeita!",
            icon='warning'
        )

        if not resposta:
            return

        sucessos = 0
        erros = []

        for data in selected:
            projeto = data.get('_projeto')
            if projeto:
                sucesso, erro = self.manager.apagar(projeto.id)
                if sucesso:
                    sucessos += 1
                else:
                    erros.append(f"{projeto.numero}: {erro}")

        # Mostrar resultado
        if sucessos > 0:
            self.refresh_data()
            if len(erros) == 0:
                messagebox.showinfo("Sucesso", f"{sucessos} projeto(s) apagado(s)")
            else:
                messagebox.showwarning(
                    "Parcialmente Concluído",
                    f"{sucessos} sucesso(s), {len(erros)} erro(s):\n" + "\n".join(erros[:5])
                )
        elif erros:
            messagebox.showerror("Erro", "Erros:\n" + "\n".join(erros[:5]))
