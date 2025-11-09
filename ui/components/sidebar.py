# -*- coding: utf-8 -*-
"""
Sidebar component - Menu de navegação lateral
"""
import customtkinter as ctk
from typing import Callable, Optional
from assets.resources import (
    get_logo_with_fallback,
    get_icon,
    DASHBOARD,
    SALDOSPESSOAIS,
    PROJETOS,
    ORCAMENTOS,
    DESPESAS,
    BOLETINS,
    CLIENTES,
    FORNECEDORES,
    EQUIPAMENTO,
    RELATORIOS,
    INFO,
)


class Sidebar(ctk.CTkFrame):
    """
    Sidebar com menu de navegação
    """

    # Mapeamento de ícones para cada menu
    MENU_ICONS = {
        "dashboard": DASHBOARD,
        "saldos": SALDOSPESSOAIS,
        "projetos": PROJETOS,
        "orcamentos": ORCAMENTOS,
        "despesas": DESPESAS,
        "boletins": BOLETINS,
        "clientes": CLIENTES,
        "fornecedores": FORNECEDORES,
        "equipamento": EQUIPAMENTO,
        "relatorios": RELATORIOS,
    }

    def __init__(self, parent, on_menu_select: Callable, **kwargs):
        """
        Initialize sidebar

        Args:
            parent: Parent widget
            on_menu_select: Callback quando menu é selecionado
                           Signature: on_menu_select(menu_id: str)
        """
        super().__init__(parent, corner_radius=0, **kwargs)

        self.on_menu_select = on_menu_select
        self.current_menu = None
        self.menu_buttons = {}

        # Configure
        self.configure(fg_color=("#E0E0E0", "#1a1a1a"))

        # Create widgets
        self.create_widgets()

    def create_widgets(self):
        """Create sidebar widgets"""

        # Logo/Title (FIXED - stays at top)
        logo_frame = ctk.CTkFrame(self, fg_color="transparent")
        logo_frame.pack(fill="x", padx=20, pady=(30, 20))

        # Load logo (SVG ou PNG pré-gerado)
        logo_image = get_logo_with_fallback("logo", size=(100, 60), suffix="sidebar")
        if logo_image:
            logo_ctk = ctk.CTkImage(
                light_image=logo_image,
                dark_image=logo_image,
                size=(100, 60)
            )
            logo_label = ctk.CTkLabel(
                logo_frame,
                image=logo_ctk,
                text=""
            )
            logo_label.pack(pady=(0, 10))
        else:
            # Fallback se logo não carregar
            logo_label = ctk.CTkLabel(
                logo_frame,
                text="AGORA",
                font=ctk.CTkFont(size=18, weight="bold")
            )
            logo_label.pack(pady=(0, 10))

        # Subtitle
        version_label = ctk.CTkLabel(
            logo_frame,
            text="Contabilidade",
            font=ctk.CTkFont(size=10),
            text_color="gray"
        )
        version_label.pack()

        # SCROLLABLE Menu Container
        menu_scroll = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            scrollbar_button_color=("#C0C0C0", "#3a3a3a"),
            scrollbar_button_hover_color=("#A0A0A0", "#4a4a4a")
        )
        menu_scroll.pack(fill="both", expand=True, padx=0, pady=(10, 10))

        # Menu items
        # Dashboard (separado)
        btn = self.create_menu_button(menu_scroll, "dashboard", "Dashboard")
        self.menu_buttons["dashboard"] = btn

        # Spacer após Dashboard
        spacer0 = ctk.CTkFrame(menu_scroll, fg_color="transparent", height=15)
        spacer0.pack(fill="x", pady=5)

        # Grupo principal: Operações
        menu_items_main = [
            ("saldos", "Saldos Pessoais"),
            ("projetos", "Projetos"),
            ("orcamentos", "Orçamentos"),
            ("despesas", "Despesas"),
            ("boletins", "Boletins"),
        ]

        for menu_id, menu_text in menu_items_main:
            btn = self.create_menu_button(menu_scroll, menu_id, menu_text)
            self.menu_buttons[menu_id] = btn

        # Spacer entre grupos
        spacer1 = ctk.CTkFrame(menu_scroll, fg_color="transparent", height=15)
        spacer1.pack(fill="x", pady=5)

        # Grupo secundário: Cadastros
        menu_items_cadastros = [
            ("clientes", "Clientes"),
            ("fornecedores", "Fornecedores"),
            ("equipamento", "Equipamento"),
        ]

        for menu_id, menu_text in menu_items_cadastros:
            btn = self.create_menu_button(menu_scroll, menu_id, menu_text)
            self.menu_buttons[menu_id] = btn

        # Spacer entre grupos
        spacer2 = ctk.CTkFrame(menu_scroll, fg_color="transparent", height=15)
        spacer2.pack(fill="x", pady=5)

        # Grupo relatórios
        menu_items_relatorios = [
            ("relatorios", "Relatórios"),
        ]

        for menu_id, menu_text in menu_items_relatorios:
            btn = self.create_menu_button(menu_scroll, menu_id, menu_text)
            self.menu_buttons[menu_id] = btn

        # FIXED Bottom Section (Info & Logout - outside scroll)
        # Separator line
        separator = ctk.CTkFrame(self, fg_color=("#C0C0C0", "#3a3a3a"), height=1)
        separator.pack(fill="x", padx=10, pady=(5, 5))

        # Info button with icon
        info_icon_pil = get_icon(INFO, size=(20, 20))
        if info_icon_pil:
            info_icon_ctk = ctk.CTkImage(
                light_image=info_icon_pil,
                dark_image=info_icon_pil,
                size=(20, 20)
            )
            info_btn = ctk.CTkButton(
                self,
                text=" Info",
                image=info_icon_ctk,
                compound="left",
                command=lambda: self.select_menu("info"),
                fg_color="transparent",
                hover_color=("#C0C0C0", "#2a2a2a"),
                anchor="w",
                height=40,
                font=ctk.CTkFont(size=13)
            )
        else:
            info_btn = ctk.CTkButton(
                self,
                text="ℹ️ Info",
                command=lambda: self.select_menu("info"),
                fg_color="transparent",
                hover_color=("#C0C0C0", "#2a2a2a"),
                anchor="w",
                height=40,
                font=ctk.CTkFont(size=13)
            )
        info_btn.pack(fill="x", padx=10, pady=(5, 5))

        logout_btn = ctk.CTkButton(
            self,
            text="🚪 Sair",
            command=lambda: self.select_menu("logout"),
            fg_color="transparent",
            hover_color=("#C0C0C0", "#2a2a2a"),
            anchor="w",
            height=40,
            font=ctk.CTkFont(size=13)
        )
        logout_btn.pack(fill="x", padx=10, pady=(0, 20))

        # Select dashboard by default
        self.select_menu("dashboard")

    def create_menu_button(self, parent, menu_id: str, text: str) -> ctk.CTkButton:
        """
        Create a menu button with icon

        Args:
            parent: Parent widget (usually menu_scroll)
            menu_id: Menu identifier
            text: Button text

        Returns:
            Button widget
        """
        # Carregar ícone se disponível
        icon_image = None
        if menu_id in self.MENU_ICONS:
            icon_base64 = self.MENU_ICONS[menu_id]
            icon_pil = get_icon(icon_base64, size=(27, 27))
            if icon_pil:
                icon_image = ctk.CTkImage(
                    light_image=icon_pil,
                    dark_image=icon_pil,
                    size=(27, 27)
                )

        # Criar botão
        btn = ctk.CTkButton(
            parent,
            text=text,
            image=icon_image if icon_image else None,
            compound="left" if icon_image else "none",
            command=lambda: self.select_menu(menu_id),
            fg_color="transparent",
            hover_color=("#C0C0C0", "#2a2a2a"),
            anchor="w",
            height=45,
            font=ctk.CTkFont(size=14)
        )
        btn.pack(fill="x", padx=10, pady=2)
        return btn

    def update_selection(self, menu_id: str):
        """
        Update visual selection without triggering callback

        Args:
            menu_id: Menu identifier
        """
        # Update button colors
        for btn_id, btn in self.menu_buttons.items():
            if btn_id == menu_id:
                btn.configure(
                    fg_color=("#2196F3", "#1565C0"),
                    hover_color=("#1976D2", "#0D47A1")
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    hover_color=("#C0C0C0", "#2a2a2a")
                )

        self.current_menu = menu_id

    def select_menu(self, menu_id: str):
        """
        Select a menu item

        Args:
            menu_id: Menu identifier
        """
        # Update visual selection
        self.update_selection(menu_id)

        # Call callback
        if self.on_menu_select:
            self.on_menu_select(menu_id)
