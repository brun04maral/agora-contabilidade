# -*- coding: utf-8 -*-
"""
Sidebar component - Menu de navegação lateral
"""
import customtkinter as ctk
from typing import Callable, Optional
from PIL import Image
import os


class Sidebar(ctk.CTkFrame):
    """
    Sidebar com menu de navegação
    """

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

        # Logo/Title
        logo_frame = ctk.CTkFrame(self, fg_color="transparent")
        logo_frame.pack(fill="x", padx=20, pady=(30, 40))

        # Load logo image
        logo_path = os.path.join(os.path.dirname(__file__), "..", "..", "media", "a + agora media production@0.5x.png")
        if os.path.exists(logo_path):
            logo_image = Image.open(logo_path)
            logo_ctk = ctk.CTkImage(
                light_image=logo_image,
                dark_image=logo_image,
                size=(100, 60)  # Adjust size as needed
            )
            logo_label = ctk.CTkLabel(
                logo_frame,
                image=logo_ctk,
                text=""
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

        # Menu items
        menu_items = [
            ("dashboard", "📊 Dashboard"),
            ("saldos", "💰 Saldos Pessoais"),
            ("projetos", "📁 Projetos"),
            ("despesas", "💸 Despesas"),
            ("boletins", "📄 Boletins"),
            ("relatorios", "📑 Relatórios"),
            ("clientes", "👥 Clientes"),
            ("fornecedores", "🏢 Fornecedores"),
        ]

        for menu_id, menu_text in menu_items:
            btn = self.create_menu_button(menu_id, menu_text)
            self.menu_buttons[menu_id] = btn

        # Spacer
        spacer = ctk.CTkFrame(self, fg_color="transparent", height=20)
        spacer.pack(fill="both", expand=True)

        # Settings/Logout at bottom
        settings_btn = ctk.CTkButton(
            self,
            text="⚙️ Definições",
            command=lambda: self.select_menu("settings"),
            fg_color="transparent",
            hover_color=("#C0C0C0", "#2a2a2a"),
            anchor="w",
            height=40,
            font=ctk.CTkFont(size=13)
        )
        settings_btn.pack(fill="x", padx=10, pady=(5, 5))

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
        self.select_menu("saldos")

    def create_menu_button(self, menu_id: str, text: str) -> ctk.CTkButton:
        """
        Create a menu button

        Args:
            menu_id: Menu identifier
            text: Button text

        Returns:
            Button widget
        """
        btn = ctk.CTkButton(
            self,
            text=text,
            command=lambda: self.select_menu(menu_id),
            fg_color="transparent",
            hover_color=("#C0C0C0", "#2a2a2a"),
            anchor="w",
            height=45,
            font=ctk.CTkFont(size=14)
        )
        btn.pack(fill="x", padx=10, pady=2)
        return btn

    def select_menu(self, menu_id: str):
        """
        Select a menu item

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

        # Call callback
        if self.on_menu_select:
            self.on_menu_select(menu_id)
