# -*- coding: utf-8 -*-
"""
BaseScreen - Template base para screens de listagem principal

Este módulo implementa um template reutilizável para screens de listagem
(Projetos, Orçamentos, Despesas, Boletins) com layout consistente e
funcionalidades comuns centralizadas.

ARQUITETURA DE TEMPLATES:
-------------------------
1. BaseScreen (este ficheiro) - Template para screens de listagem
2. BaseForm (futuro) - Template para forms de criação/edição

VISUAL REFINEMENTS (25/11/2025):
---------------------------------
- Header: apenas título + ícone
- Barra de pesquisa compacta (só ícone lupa)
- Filtros horizontais com seleção múltipla
- Barra topo tabela: chips (esquerda) + botões Atualizar/Novo (direita)
- Tabela expandida (ocupa máximo espaço)
- Barra de ações (fundo, sempre visível): ações contextuais baseadas em seleção
- Espaçamentos otimizados

COMO USAR:
----------
```python
from ui.components.base_screen import BaseScreen

class ProjectsScreen(BaseScreen):
    def __init__(self, parent, db_session, **kwargs):
        # Configuração antes do super().__init__
        self.screen_config = {
            'title': 'Projetos',
            'icon_key': PROJETOS,
            'icon_fallback': '📁',
            'new_button_text': 'Novo Projeto',
            'new_button_color': ('#4CAF50', '#388E3C'),
            'search_placeholder': 'Pesquisar por cliente ou descrição...',
        }

        super().__init__(parent, db_session, **kwargs)

    # Override métodos para personalizar
    def get_table_columns(self):
        return [
            {'key': 'numero', 'label': 'ID', 'width': 80},
            ...
        ]

    def get_filters_config(self):
        return [
            {'key': 'estado', 'label': 'Estado', 'values': ['Todos', 'Ativo', 'Pago']},
            ...
        ]

    def load_data(self):
        return self.manager.listar_todos()

    def item_to_dict(self, item):
        return {'id': item.id, 'numero': item.numero, ...}
```

MÉTODOS PARA OVERRIDE:
----------------------
- get_table_columns() - Definir colunas da tabela
- get_filters_config() - Definir filtros disponíveis
- get_header_buttons() - Adicionar botões custom (aparecem no topo da tabela)
- get_context_menu_items(item) - Definir ações (context menu + barra de ações)
- load_data() - Carregar dados da BD
- item_to_dict(item) - Converter objeto para dict da tabela
- on_item_double_click(data) - Ação ao duplo clique
- on_new_item() - Ação do botão "Novo"
- apply_filters(items) - Aplicar filtros aos dados

SLOTS DISPONÍVEIS:
------------------
- header_slot - Frame para conteúdo custom no header
- filters_slot - Frame para filtros adicionais
- footer_slot - Frame para conteúdo no footer

Autor: Agora Media Production
Data: 2025-11-24
"""

import customtkinter as ctk
import tkinter as tk
from typing import Optional, List, Dict, Any, Callable, Set
from sqlalchemy.orm import Session
from abc import abstractmethod

from ui.components.data_table_v2 import DataTableV2
from assets.resources import get_icon


class BaseScreen(ctk.CTkFrame):
    """
    Template base para screens de listagem principal.

    Fornece layout consistente com:
    - Header (título + ícone)
    - Barra de pesquisa compacta + filtros horizontais
    - Barra topo tabela (chips à esquerda, botões Atualizar/Novo à direita)
    - DataTableV2 expandida
    - Barra de ações (fundo, sempre visível, ações contextuais)
    - Context menu

    Subclasses devem implementar os métodos abstratos e podem
    override métodos opcionais para personalização.
    """

    def __init__(
        self,
        parent,
        db_session: Session,
        initial_filters: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        """
        Inicializa o BaseScreen.

        Args:
            parent: Widget pai
            db_session: Sessão SQLAlchemy
            initial_filters: Filtros iniciais {key: value}
            **kwargs: Argumentos adicionais para CTkFrame
        """
        super().__init__(parent, **kwargs)

        self.db_session = db_session
        self.initial_filters = initial_filters or {}

        # Configuração padrão (subclasse deve definir screen_config antes de super().__init__)
        self.config = getattr(self, 'screen_config', {})

        # Estado interno
        self._filter_widgets = {}
        self._filter_selections = {}  # {key: Set[value]}
        self._filter_chips = {}  # {key: {value: chip_widget}}
        self._search_chip = None  # Chip da pesquisa ativa
        self._action_buttons = {}  # {label: {button, min_selection, max_selection}}

        # Configure frame
        self.configure(fg_color="transparent")

        # Criar widgets
        self._create_layout()

        # Aplicar filtros iniciais e carregar dados
        self._apply_initial_filters()
        self.refresh_data()

    def _create_layout(self):
        """Cria o layout base do screen."""
        # Header (apenas título)
        self._create_header()

        # Search + Filters toolbar (compacto)
        if self.config.get('show_search', True) or self.get_filters_config():
            self._create_toolbar()

        # Barra topo tabela: chips (esquerda) + botões (direita)
        self._create_table_header_bar()

        # Table (expandida)
        self._create_table()

        # Barra de ações (fundo, sempre visível)
        self._create_action_bar()

    def _create_header(self):
        """Cria o header com título (apenas)."""
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=30, pady=(20, 20))

        # Título com ícone
        title = self.config.get('title', 'Screen')
        icon_key = self.config.get('icon_key')
        icon_fallback = self.config.get('icon_fallback', '')

        if icon_key:
            icon_pil = get_icon(icon_key, size=(28, 28))
            if icon_pil:
                icon_ctk = ctk.CTkImage(
                    light_image=icon_pil,
                    dark_image=icon_pil,
                    size=(28, 28)
                )
                title_label = ctk.CTkLabel(
                    header_frame,
                    image=icon_ctk,
                    text=f" {title}",
                    compound="left",
                    font=ctk.CTkFont(size=28, weight="bold")
                )
                # Keep reference to prevent garbage collection
                title_label._icon_image = icon_ctk
            else:
                title_label = ctk.CTkLabel(
                    header_frame,
                    text=f"{icon_fallback} {title}",
                    font=ctk.CTkFont(size=28, weight="bold")
                )
        else:
            title_label = ctk.CTkLabel(
                header_frame,
                text=title,
                font=ctk.CTkFont(size=28, weight="bold")
            )
        title_label.pack(side="left")

    def _create_toolbar(self):
        """Cria toolbar compacto com pesquisa e filtros horizontais."""
        toolbar = ctk.CTkFrame(self, fg_color="transparent", height=40)
        toolbar.pack(fill="x", padx=30, pady=(0, 10))  # ZERO top, 10px bottom (como DespesasScreen)
        toolbar.pack_propagate(False)  # NÃO expande automaticamente

        # Search (compacta, só ícone lupa)
        if self.config.get('show_search', True):
            # Ícone lupa
            search_icon = ctk.CTkLabel(
                toolbar,
                text="🔍",
                font=ctk.CTkFont(size=16)
            )
            search_icon.pack(side="left", padx=(0, 8))

            # Search entry (compacto)
            self.search_var = ctk.StringVar()
            self.search_var.trace_add("write", self._on_search_change)

            placeholder = self.config.get('search_placeholder', 'Digite para pesquisar...')
            self.search_entry = ctk.CTkEntry(
                toolbar,
                textvariable=self.search_var,
                placeholder_text=placeholder,
                width=320,
                height=32,
                font=ctk.CTkFont(size=12)
            )
            self.search_entry.pack(side="left", padx=(0, 5))

            # Botão limpar (só ícone)
            clear_btn = ctk.CTkButton(
                toolbar,
                text="✖",
                command=self._clear_search,
                width=32,
                height=32,
                font=ctk.CTkFont(size=12),
                fg_color="transparent",
                hover_color=("#E0E0E0", "#404040"),
                border_width=0
            )
            clear_btn.pack(side="left", padx=(0, 20))

        # Filtros (horizontais, à direita)
        filters_config = self.get_filters_config()
        if filters_config:
            for filter_cfg in filters_config:
                key = filter_cfg['key']
                label = filter_cfg.get('label', key.capitalize())
                values = filter_cfg.get('values', ['Todos'])
                width = filter_cfg.get('width', 120)

                # Dropdown simples
                option_menu = ctk.CTkOptionMenu(
                    toolbar,
                    values=values,
                    command=lambda v, k=key: self._on_filter_select(k, v),
                    width=width,
                    height=32,
                    font=ctk.CTkFont(size=12),
                    dropdown_font=ctk.CTkFont(size=11),
                    fg_color=("#E0E0E0", "#404040"),
                    button_color=("#E0E0E0", "#404040"),
                    button_hover_color=("#BDBDBD", "#505050"),
                    text_color=("#000000", "#FFFFFF")
                )
                option_menu.set(label)
                option_menu.pack(side="left", padx=5)

                self._filter_widgets[key] = option_menu
                self._filter_selections[key] = set()

        # Slot para filtros adicionais
        self.filters_slot = ctk.CTkFrame(toolbar, fg_color="transparent")
        self.filters_slot.pack(side="left", padx=10)

    def _create_table_header_bar(self):
        """Cria barra topo tabela: chips (esquerda) + botões (direita)."""
        # Container sempre visível com height fixo
        table_header = ctk.CTkFrame(self, fg_color="transparent", height=50)
        table_header.pack(fill="x", padx=30, pady=(0, 10))
        table_header.pack_propagate(False)

        # Frame esquerdo para chips
        self.chips_frame = ctk.CTkFrame(table_header, fg_color="transparent")
        self.chips_frame.pack(side="left", fill="both", expand=True)

        # Frame direito para botões
        buttons_frame = ctk.CTkFrame(table_header, fg_color="transparent")
        buttons_frame.pack(side="right")

        # Botão Atualizar
        refresh_btn = ctk.CTkButton(
            buttons_frame,
            text="🔄 Atualizar",
            command=self.refresh_data,
            width=120,
            height=36,
            font=ctk.CTkFont(size=12)
        )
        refresh_btn.pack(side="left", padx=5)

        # Botões custom do header
        for btn_config in self.get_header_buttons():
            btn = ctk.CTkButton(
                buttons_frame,
                text=btn_config.get('text', ''),
                command=btn_config.get('command'),
                width=btn_config.get('width', 140),
                height=36,
                font=ctk.CTkFont(size=12),
                fg_color=btn_config.get('fg_color'),
                hover_color=btn_config.get('hover_color')
            )
            btn.pack(side="left", padx=5)

        # Botão Novo
        new_text = self.config.get('new_button_text', 'Novo')
        new_color = self.config.get('new_button_color', ('#4CAF50', '#388E3C'))
        new_hover = self.config.get('new_button_hover', ('#66BB6A', '#2E7D32'))

        new_btn = ctk.CTkButton(
            buttons_frame,
            text=f"➕ {new_text}",
            command=self.on_new_item,
            width=140,
            height=36,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=new_color,
            hover_color=new_hover
        )
        new_btn.pack(side="left", padx=5)

    def _add_filter_chip(self, filter_key: str, value: str):
        """Adiciona chip para filtro ativo."""
        if filter_key not in self._filter_chips:
            self._filter_chips[filter_key] = {}

        if value in self._filter_chips[filter_key]:
            return  # Already exists

        # Create chip
        chip = ctk.CTkFrame(
            self.chips_frame,
            fg_color=("#E3F2FD", "#1E3A5F"),
            corner_radius=16,
            height=28
        )
        chip.pack(side="left", padx=3, pady=2)

        # Chip label
        chip_label = ctk.CTkLabel(
            chip,
            text=value,
            font=ctk.CTkFont(size=11),
            text_color=("#1976D2", "#90CAF9")
        )
        chip_label.pack(side="left", padx=(10, 5))

        # Remove button
        remove_btn = ctk.CTkButton(
            chip,
            text="✕",
            width=20,
            height=20,
            font=ctk.CTkFont(size=10),
            fg_color="transparent",
            hover_color=("#BBDEFB", "#2C5282"),
            command=lambda: self._remove_filter_chip(filter_key, value)
        )
        remove_btn.pack(side="left", padx=(0, 5))

        self._filter_chips[filter_key][value] = chip

        # Destacar filtro quando tem seleções ativas
        self._update_filter_appearance(filter_key)

    def _remove_filter_chip(self, filter_key: str, value: str):
        """Remove chip de filtro ativo."""
        if filter_key in self._filter_chips and value in self._filter_chips[filter_key]:
            chip = self._filter_chips[filter_key][value]
            chip.destroy()
            del self._filter_chips[filter_key][value]

            # Remove from selections
            if filter_key in self._filter_selections:
                self._filter_selections[filter_key].discard(value)

            # Atualizar aparência do filtro
            self._update_filter_appearance(filter_key)

            # Refresh data
            self.refresh_data()

    def _update_filter_appearance(self, filter_key: str):
        """Atualiza aparência do filtro baseado em seleções ativas."""
        if filter_key not in self._filter_widgets:
            return

        widget = self._filter_widgets[filter_key]
        has_selections = filter_key in self._filter_selections and len(self._filter_selections[filter_key]) > 0

        # Obter label do filtro
        filter_cfg = next((f for f in self.get_filters_config() if f['key'] == filter_key), None)
        label = filter_cfg.get('label', filter_key.capitalize()) if filter_cfg else filter_key.capitalize()

        if has_selections:
            # Mostrar primeira seleção em AZUL
            selections = list(self._filter_selections[filter_key])
            first_selection = selections[0] if len(selections) == 1 else f"{selections[0]} (+{len(selections)-1})"
            widget.set(first_selection)
            widget.configure(text_color=("#2196F3", "#1976D2"))
        else:
            # Mostrar label em preto/branco
            widget.set(label)
            widget.configure(text_color=("#000000", "#FFFFFF"))

    def _add_search_chip(self, search_text: str):
        """Adiciona chip para pesquisa ativa."""
        if self._search_chip:
            return  # Already exists

        # Create chip
        chip = ctk.CTkFrame(
            self.chips_frame,
            fg_color=("#E8F5E9", "#1B5E20"),
            corner_radius=16,
            height=28
        )
        chip.pack(side="left", padx=3, pady=2)

        # Chip label
        chip_label = ctk.CTkLabel(
            chip,
            text=f"🔍 {search_text}",
            font=ctk.CTkFont(size=11),
            text_color=("#2E7D32", "#81C784")
        )
        chip_label.pack(side="left", padx=(10, 5))

        # Remove button
        remove_btn = ctk.CTkButton(
            chip,
            text="✕",
            width=20,
            height=20,
            font=ctk.CTkFont(size=10),
            fg_color="transparent",
            hover_color=("#C8E6C9", "#2E7D32"),
            command=self._remove_search_chip
        )
        remove_btn.pack(side="left", padx=(0, 5))

        self._search_chip = chip

    def _remove_search_chip(self):
        """Remove chip de pesquisa ativa."""
        if self._search_chip:
            self._search_chip.destroy()
            self._search_chip = None

            # Clear search and refresh
            self.search_var.set("")
            self.refresh_data()

    def _clear_all_chips(self):
        """Limpa todos os chips de filtros."""
        # Remove search chip
        if self._search_chip:
            self._remove_search_chip()

        # Remove filter chips
        for filter_key in list(self._filter_chips.keys()):
            for value in list(self._filter_chips[filter_key].keys()):
                self._remove_filter_chip(filter_key, value)

    def _create_action_bar(self):
        """Cria a barra de ações no fundo (sempre visível)."""
        # Container sempre visível com height fixo
        action_container = ctk.CTkFrame(
            self,
            fg_color=("#F5F5F5", "#2B2B2B"),
            corner_radius=8,
            border_width=1,
            border_color=("#E0E0E0", "#404040"),
            height=60
        )
        action_container.pack(fill="x", padx=30, pady=(10, 20))
        action_container.pack_propagate(False)

        # Frame esquerdo para botões de ação
        self.action_buttons_frame = ctk.CTkFrame(action_container, fg_color="transparent")
        self.action_buttons_frame.pack(side="left", fill="y", padx=10)

        # Criar botões de ação (inicialmente escondidos)
        self._action_buttons = {}
        for item in self.get_context_menu_items({}):
            if item.get('separator'):
                continue

            btn = ctk.CTkButton(
                self.action_buttons_frame,
                text=item.get('label', ''),
                command=item.get('command'),
                width=item.get('width', 100),
                height=36,
                font=ctk.CTkFont(size=11),
                fg_color=item.get('fg_color', ("#2196F3", "#1976D2")),
                hover_color=item.get('hover_color', ("#1976D2", "#1565C0"))
            )

            # Armazenar referência com config
            self._action_buttons[item.get('label', '')] = {
                'button': btn,
                'min_selection': item.get('min_selection', 1),
                'max_selection': item.get('max_selection', None)
            }

        # Frame direito para info
        info_frame = ctk.CTkFrame(action_container, fg_color="transparent")
        info_frame.pack(side="right", fill="y", padx=10)

        # Label status (sem seleção ou com seleção)
        self.status_label = ctk.CTkLabel(
            info_frame,
            text="Nenhum item selecionado",
            font=ctk.CTkFont(size=12)
        )
        self.status_label.pack(side="left", padx=10)

        # Label total (aparece quando há seleção com valor)
        self.total_label = ctk.CTkLabel(
            info_frame,
            text="Total: €0,00",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        # Inicialmente escondido

    def _create_table(self):
        """Cria a tabela de dados (expandida)."""
        columns = self.get_table_columns()

        self.table = DataTableV2(
            self,
            columns=columns,
            height=100,  # Mínimo, vai expandir
            on_row_double_click=self._on_row_double_click,
            on_selection_change=self._on_selection_change,
            on_row_right_click=self._on_row_right_click
        )
        # Expandir tabela para ocupar MÁXIMO espaço disponível
        self.table.pack(fill="both", expand=True, padx=30, pady=0)

    # ========== Event Handlers ==========

    def _on_search_change(self, *args):
        """Handler para mudança na pesquisa."""
        search_text = self.search_var.get().strip()

        if search_text:
            # Adicionar chip de pesquisa
            if not self._search_chip:
                self._add_search_chip(search_text)
            else:
                # Atualizar texto do chip existente
                for widget in self._search_chip.winfo_children():
                    if isinstance(widget, ctk.CTkLabel):
                        widget.configure(text=f"🔍 {search_text}")
                        break
        else:
            # Remover chip se pesquisa foi limpa
            if self._search_chip:
                self._search_chip.destroy()
                self._search_chip = None

        self.refresh_data()

    def _clear_search(self):
        """Limpa o campo de pesquisa."""
        self.search_var.set("")
        self.search_entry.focus()

    def _on_filter_select(self, key: str, value: str):
        """Handler para seleção em filtro."""
        # Ignorar se é "Todos" ou é o próprio label do filtro
        filter_cfg = next((f for f in self.get_filters_config() if f['key'] == key), None)
        if not filter_cfg:
            return

        label = filter_cfg.get('label', key.capitalize())

        if value == "Todos" or value == label:
            return

        # Adicionar à seleção
        if key not in self._filter_selections:
            self._filter_selections[key] = set()

        self._filter_selections[key].add(value)

        # Adicionar chip
        self._add_filter_chip(key, value)

        # Atualizar aparência do dropdown
        self._update_filter_appearance(key)

        # Refresh data
        self.refresh_data()

    def _on_filter_change(self, key: str, value: str):
        """Handler para mudança em filtro (backward compatibility)."""
        self._on_filter_select(key, value)

    def _apply_initial_filters(self):
        """Aplica filtros iniciais."""
        for key, value in self.initial_filters.items():
            if key in self._filter_widgets:
                self._filter_widgets[key].set(value)

    def _on_selection_change(self, selected_data: list):
        """Handler para mudança de seleção na tabela."""
        num_selected = len(selected_data)

        if num_selected > 0:
            # Atualizar status
            count_text = f"{num_selected} selecionado" if num_selected == 1 else f"{num_selected} selecionados"
            self.status_label.configure(text=count_text)

            # Mostrar/esconder botões baseado em min/max selection
            for label, config in self._action_buttons.items():
                btn = config['button']
                min_sel = config['min_selection']
                max_sel = config['max_selection']

                # Verificar se botão deve aparecer
                should_show = num_selected >= min_sel
                if max_sel is not None:
                    should_show = should_show and num_selected <= max_sel

                if should_show:
                    if not btn.winfo_manager():
                        btn.pack(side="left", padx=4)
                else:
                    btn.pack_forget()

            # Calcular e mostrar total
            total = self.calculate_selection_total(selected_data)
            if total > 0:
                self.total_label.configure(text=f"Total: €{total:,.2f}")
                if not self.total_label.winfo_manager():
                    self.total_label.pack(side="left", padx=12)
            else:
                self.total_label.pack_forget()
        else:
            # Sem seleção
            self.status_label.configure(text="Nenhum item selecionado")

            # Esconder todos os botões
            for config in self._action_buttons.values():
                config['button'].pack_forget()

            # Esconder total
            self.total_label.pack_forget()

    def _on_row_double_click(self, data: dict):
        """Handler para duplo clique na linha."""
        self.on_item_double_click(data)

    def _on_row_right_click(self, event, data: dict):
        """Handler para clique direito na linha."""
        menu_items = self.get_context_menu_items(data)
        if not menu_items:
            return

        menu = tk.Menu(self, tearoff=0)

        for item in menu_items:
            if item.get('separator'):
                menu.add_separator()
            else:
                menu.add_command(
                    label=item.get('label', ''),
                    command=item.get('command')
                )

        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    # ========== Public Methods ==========

    def refresh_data(self):
        """Recarrega os dados da tabela aplicando filtros."""
        # Carregar dados
        items = self.load_data()

        # Aplicar pesquisa
        search_text = getattr(self, 'search_var', None)
        if search_text:
            search_text = search_text.get().strip().lower()
            if search_text:
                items = self.filter_by_search(items, search_text)

        # Aplicar filtros de chips
        filters = self.get_current_filters()
        items = self.apply_filters(items, filters)

        # Converter para dict e atualizar tabela
        data = [self.item_to_dict(item) for item in items]
        self.table.set_data(data)

    def get_current_filters(self) -> Dict[str, List[str]]:
        """Retorna filtros ativos (multi-seleção)."""
        return {
            key: list(selections)
            for key, selections in self._filter_selections.items()
            if len(selections) > 0
        }

    def get_selected_data(self) -> list:
        """Retorna dados das linhas selecionadas."""
        return self.table.get_selected_data()

    # ========== Abstract Methods (Obrigatórios) ==========

    @abstractmethod
    def get_table_columns(self) -> List[Dict[str, Any]]:
        """
        Define as colunas da tabela.

        Returns:
            Lista de dicts com configuração das colunas:
            [{'key': 'id', 'label': 'ID', 'width': 80, 'sortable': True}, ...]
        """
        pass

    @abstractmethod
    def load_data(self) -> list:
        """
        Carrega dados da base de dados.

        Returns:
            Lista de objetos (models) para exibir na tabela
        """
        pass

    @abstractmethod
    def item_to_dict(self, item) -> dict:
        """
        Converte um objeto para dict da tabela.

        Args:
            item: Objeto model

        Returns:
            Dict com dados para a tabela (incluir 'id' e '_item' para referência)
        """
        pass

    # ========== Optional Override Methods ==========

    def get_filters_config(self) -> List[Dict[str, Any]]:
        """
        Define os filtros disponíveis.

        Returns:
            Lista de dicts com configuração dos filtros:
            [{'key': 'estado', 'label': 'Estado', 'values': ['Todos', 'Ativo'], 'width': 150}, ...]
        """
        return []

    def get_header_buttons(self) -> List[Dict[str, Any]]:
        """
        Define botões adicionais no header.

        Returns:
            Lista de dicts com configuração dos botões:
            [{'text': '🔁 Gerar', 'command': self.gerar, 'fg_color': '#2196F3', 'width': 140}, ...]
        """
        return []

    def get_context_menu_items(self, data: dict) -> List[Dict[str, Any]]:
        """
        Define itens do context menu e da barra de ações.

        Args:
            data: Dict com dados da linha (pode estar vazio {} ao criar barra de ações)

        Returns:
            Lista de dicts com itens do menu:
            [{
                'label': '✏️ Editar',
                'command': lambda: self.editar(data),
                'min_selection': 1,  # Mínimo de itens selecionados (default: 1)
                'max_selection': 1,  # Máximo de itens selecionados (default: None = sem limite)
                'fg_color': '#2196F3',  # Cor do botão (opcional)
                'hover_color': '#1976D2',  # Cor hover (opcional)
                'width': 100  # Largura do botão (opcional)
            }, ...]

        Exemplos:
            - Editar: min=1, max=1 (só 1 item)
            - Apagar: min=1, max=None (1 ou mais)
            - Exportar: min=1, max=None (1 ou mais)
        """
        return []

    def filter_by_search(self, items: list, search_text: str) -> list:
        """
        Filtra items pelo texto de pesquisa.

        Args:
            items: Lista de objetos
            search_text: Texto de pesquisa (lowercase)

        Returns:
            Lista filtrada
        """
        return items

    def apply_filters(self, items: list, filters: Dict[str, List[str]]) -> list:
        """
        Aplica filtros aos items.

        Args:
            items: Lista de objetos
            filters: Dict com listas de valores {key: [value1, value2, ...]}

        Returns:
            Lista filtrada
        """
        return items

    def calculate_selection_total(self, selected_data: list) -> float:
        """
        Calcula o total dos items selecionados.

        Args:
            selected_data: Lista de dicts das linhas selecionadas

        Returns:
            Valor total
        """
        return 0.0

    def on_item_double_click(self, data: dict):
        """
        Ação ao duplo clique numa linha.

        Args:
            data: Dict com dados da linha
        """
        pass

    def on_new_item(self):
        """Ação do botão 'Novo'."""
        pass
