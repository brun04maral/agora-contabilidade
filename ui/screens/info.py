# -*- coding: utf-8 -*-
"""
Info Screen - Informações sobre a aplicação
"""
import customtkinter as ctk
from assets.resources import get_icon, INFO


class InfoScreen(ctk.CTkFrame):
    """
    Tela com informações sobre a aplicação
    """

    def __init__(self, parent, **kwargs):
        """
        Initialize info screen

        Args:
            parent: Parent widget
        """
        super().__init__(parent, **kwargs)

        # Configure
        self.configure(fg_color="transparent")

        # Create widgets
        self.create_widgets()

    def create_widgets(self):
        """Create screen widgets"""

        # Container centralizado
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.place(relx=0.5, rely=0.5, anchor="center")

        # Ícone grande
        icon_pil = get_icon(INFO, size=(80, 80))
        if icon_pil:
            icon_ctk = ctk.CTkImage(
                light_image=icon_pil,
                dark_image=icon_pil,
                size=(80, 80)
            )
            icon_label = ctk.CTkLabel(
                container,
                image=icon_ctk,
                text=""
            )
            icon_label.pack(pady=(0, 30))

        # Título
        title_label = ctk.CTkLabel(
            container,
            text="Agora Contabilidade",
            font=ctk.CTkFont(size=32, weight="bold")
        )
        title_label.pack(pady=(0, 10))

        # Versão
        version_label = ctk.CTkLabel(
            container,
            text="Versão v0.0.1",
            font=ctk.CTkFont(size=16),
            text_color="gray"
        )
        version_label.pack(pady=(0, 40))

        # Separador
        separator = ctk.CTkFrame(
            container,
            fg_color=("#C0C0C0", "#3a3a3a"),
            height=1,
            width=400
        )
        separator.pack(pady=(0, 30))

        # Informação de desenvolvimento
        dev_title = ctk.CTkLabel(
            container,
            text="Desenvolvido por",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        dev_title.pack(pady=(0, 10))

        dev_name = ctk.CTkLabel(
            container,
            text="Bruno Amaral",
            font=ctk.CTkFont(size=16)
        )
        dev_name.pack(pady=(0, 5))

        dev_company = ctk.CTkLabel(
            container,
            text="para Agora Media Production",
            font=ctk.CTkFont(size=14),
            text_color="gray"
        )
        dev_company.pack(pady=(0, 40))

        # Nota de futuro (comentado visualmente)
        # future_note = ctk.CTkLabel(
        #     container,
        #     text="💡 Futuro: Botão de atualização aqui",
        #     font=ctk.CTkFont(size=12),
        #     text_color=("gray", "darkgray")
        # )
        # future_note.pack(pady=(20, 0))
