# -*- coding: utf-8 -*-
"""
Tela de Saldos Pessoais - CORE DO SISTEMA
"""
import customtkinter as ctk
from typing import Callable, Optional
from sqlalchemy.orm import Session
from logic.saldos import SaldosCalculator
from database.models import Socio
from assets.resources import get_icon, SALDOSPESSOAIS


class SaldosScreen(ctk.CTkFrame):
    """
    Tela de visualização de Saldos Pessoais dos sócios
    """

    def __init__(self, parent, db_session: Session, main_window=None, **kwargs):
        """
        Initialize saldos screen

        Args:
            parent: Parent widget
            db_session: SQLAlchemy database session
            main_window: Reference to MainWindow for navigation
        """
        super().__init__(parent, **kwargs)

        self.db_session = db_session
        self.calculator = SaldosCalculator(db_session)
        self.main_window = main_window

        # Configure
        self.configure(fg_color="transparent")

        # Create widgets
        self.create_widgets()

        # Load data
        self.carregar_saldos()

    def create_widgets(self):
        """Create screen widgets"""

        # Header
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=30, pady=(30, 20))

        # Title with PNG icon
        icon_pil = get_icon(SALDOSPESSOAIS, size=(28, 28))
        if icon_pil:
            icon_ctk = ctk.CTkImage(
                light_image=icon_pil,
                dark_image=icon_pil,
                size=(28, 28)
            )
            title_label = ctk.CTkLabel(
                header_frame,
                image=icon_ctk,
                text=" Saldos Pessoais",
                compound="left",
                font=ctk.CTkFont(size=28, weight="bold")
            )
        else:
            title_label = ctk.CTkLabel(
                header_frame,
                text="💰 Saldos Pessoais",
                font=ctk.CTkFont(size=28, weight="bold")
            )
        title_label.pack(side="left")

        # Refresh button
        refresh_btn = ctk.CTkButton(
            header_frame,
            text="🔄 Atualizar",
            command=self.carregar_saldos,
            width=120,
            height=35,
            font=ctk.CTkFont(size=13)
        )
        refresh_btn.pack(side="right")

        # Scrollable container
        scroll_frame = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent"
        )
        scroll_frame.pack(fill="both", expand=True, padx=30, pady=(0, 30))

        # Container for both saldos side by side
        saldos_container = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        saldos_container.pack(fill="both", expand=True)
        saldos_container.grid_columnconfigure(0, weight=1)
        saldos_container.grid_columnconfigure(1, weight=1)

        # BA's saldo
        self.bruno_frame = self.create_saldo_card(saldos_container, "BA", Socio.BRUNO)
        self.bruno_frame.grid(row=0, column=0, padx=(0, 10), sticky="nsew")

        # RR's saldo
        self.rafael_frame = self.create_saldo_card(saldos_container, "RR", Socio.RAFAEL)
        self.rafael_frame.grid(row=0, column=1, padx=(10, 0), sticky="nsew")

    def create_saldo_card(self, parent, nome: str, socio: Socio) -> ctk.CTkFrame:
        """
        Create a saldo card for a socio

        Args:
            parent: Parent widget
            nome: Nome do sócio
            socio: Socio enum

        Returns:
            Frame with saldo card
        """
        card = ctk.CTkFrame(parent)
        card.grid_columnconfigure(0, weight=1)

        # Header with Agora colors (matching dashboard)
        header_color = "#C9941F" if socio == Socio.BRUNO else "#A67F1B"  # Agora yellow colors
        header = ctk.CTkFrame(card, fg_color=header_color, corner_radius=10)
        header.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 0))

        header_label = ctk.CTkLabel(
            header,
            text=nome,
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="white"
        )
        header_label.pack(pady=15)

        # Saldo total (will be filled later)
        saldo_frame = ctk.CTkFrame(card, fg_color="transparent")
        saldo_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=20)

        saldo_label = ctk.CTkLabel(
            saldo_frame,
            text="Saldo Atual:",
            font=ctk.CTkFont(size=14),
            text_color="gray"
        )
        saldo_label.pack()

        saldo_value = ctk.CTkLabel(
            saldo_frame,
            text="€0.00",
            font=ctk.CTkFont(size=36, weight="bold")
        )
        saldo_value.pack(pady=(5, 0))

        # Store reference to update later
        if socio == Socio.BRUNO:
            self.bruno_saldo_label = saldo_value
        else:
            self.rafael_saldo_label = saldo_value

        # Separator
        sep1 = ctk.CTkFrame(card, height=1, fg_color="gray")
        sep1.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 20))

        # INs section
        ins_frame = ctk.CTkFrame(card, fg_color="transparent")
        ins_frame.grid(row=3, column=0, sticky="ew", padx=20, pady=(0, 15))

        ins_title = ctk.CTkLabel(
            ins_frame,
            text="📈 INs (Entradas)",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        ins_title.pack(anchor="w")

        # INs items (will be filled later)
        ins_items_frame = ctk.CTkFrame(ins_frame, fg_color="transparent")
        ins_items_frame.pack(fill="x", pady=(10, 0))

        if socio == Socio.BRUNO:
            self.bruno_ins_frame = ins_items_frame
        else:
            self.rafael_ins_frame = ins_items_frame

        # Separator
        sep2 = ctk.CTkFrame(card, height=1, fg_color="gray")
        sep2.grid(row=4, column=0, sticky="ew", padx=20, pady=(15, 20))

        # OUTs section
        outs_frame = ctk.CTkFrame(card, fg_color="transparent")
        outs_frame.grid(row=5, column=0, sticky="ew", padx=20, pady=(0, 15))

        outs_title = ctk.CTkLabel(
            outs_frame,
            text="📉 OUTs (Saídas)",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        outs_title.pack(anchor="w")

        # OUTs items (will be filled later)
        outs_items_frame = ctk.CTkFrame(outs_frame, fg_color="transparent")
        outs_items_frame.pack(fill="x", pady=(10, 0))

        if socio == Socio.BRUNO:
            self.bruno_outs_frame = outs_items_frame
        else:
            self.rafael_outs_frame = outs_items_frame

        # Separator
        sep3 = ctk.CTkFrame(card, height=1, fg_color="gray")
        sep3.grid(row=6, column=0, sticky="ew", padx=20, pady=(15, 20))

        # Sugestão
        sugestao_frame = ctk.CTkFrame(card, fg_color=("#FFF3E0", "#3E2723"), corner_radius=10)
        sugestao_frame.grid(row=7, column=0, sticky="ew", padx=20, pady=(0, 20))

        sugestao_label = ctk.CTkLabel(
            sugestao_frame,
            text="💡 Sugestão:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        sugestao_label.pack(anchor="w", padx=15, pady=(15, 5))

        sugestao_text = ctk.CTkLabel(
            sugestao_frame,
            text="Emitir boletim de €0.00 para zerar saldo",
            font=ctk.CTkFont(size=13),
            wraplength=300
        )
        sugestao_text.pack(anchor="w", padx=15, pady=(0, 15))

        if socio == Socio.BRUNO:
            self.bruno_sugestao_label = sugestao_text
        else:
            self.rafael_sugestao_label = sugestao_text

        return card

    def create_saldo_item(self, parent, label: str, value: float, is_total: bool = False, clickable: bool = False, on_click: Optional[Callable] = None, button_color: str = None):
        """
        Create a saldo line item

        Args:
            parent: Parent frame
            label: Item label
            value: Item value
            is_total: If this is a total line (bold)
            clickable: If true, makes the item clickable with hover effects
            on_click: Callback function when item is clicked
            button_color: Background color for clickable button (when clickable=True)
        """
        item_frame = ctk.CTkFrame(parent, fg_color="transparent")
        item_frame.pack(fill="x", pady=5)

        # Use button if clickable, otherwise label
        if clickable and on_click:
            # Determine colors based on button_color
            if button_color:
                # Extract light/dark from tuple or use as single color
                bg_light, bg_dark = button_color if isinstance(button_color, tuple) else (button_color, button_color)
                # Set border color (golden/amber tones)
                border_color = ("#C9941F", "#FFD54F")  # Golden border
            else:
                bg_light, bg_dark = "#E8F5E9", "#1B5E20"
                border_color = ("#66BB6A", "#2E7D32")

            # Create a proper button-like card (clickable frame)
            button_card = ctk.CTkFrame(
                item_frame,
                fg_color=(bg_light, bg_dark),
                corner_radius=10,
                border_width=2,
                border_color=border_color,
                cursor="hand2"
            )
            button_card.pack(fill="x", pady=2)

            # Label on the left (white text)
            item_label = ctk.CTkLabel(
                button_card,
                text=f"{label}",
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color="white",
                anchor="w"
            )
            item_label.pack(side="left", padx=15, pady=12)

            # Value label on the right (white text)
            value_label = ctk.CTkLabel(
                button_card,
                text=f"€{value:,.2f}",
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color="white",
                anchor="e"
            )
            value_label.pack(side="right", padx=15, pady=12)

            # Store original colors for hover effect
            original_border = border_color
            original_bg = (bg_light, bg_dark)

            # Make entire card clickable
            def handle_click(event):
                on_click()

            button_card.bind("<Button-1>", handle_click)
            item_label.bind("<Button-1>", handle_click)
            value_label.bind("<Button-1>", handle_click)

            # Hover effects
            def on_enter(event):
                button_card.configure(
                    border_width=3,
                    border_color=("#FFFFFF", "#FFFFFF")
                )

            def on_leave(event):
                button_card.configure(
                    border_width=2,
                    border_color=original_border
                )

            button_card.bind("<Enter>", on_enter)
            button_card.bind("<Leave>", on_leave)
            item_label.bind("<Enter>", on_enter)
            item_label.bind("<Leave>", on_leave)
            value_label.bind("<Enter>", on_enter)
            value_label.bind("<Leave>", on_leave)
        else:
            item_label = ctk.CTkLabel(
                item_frame,
                text=f"{'  ' if not is_total else ''}• {label}:",
                font=ctk.CTkFont(size=14 if not is_total else 15, weight="bold" if is_total else "normal"),
                anchor="w"
            )
            item_label.pack(side="left")

            item_value = ctk.CTkLabel(
                item_frame,
                text=f"€{value:,.2f}",
                font=ctk.CTkFont(size=14 if not is_total else 15, weight="bold" if is_total else "normal"),
                anchor="e"
            )
            item_value.pack(side="right")

    def navegar_projetos_bruno(self):
        """Navigate to Projetos screen with Bruno's personal projects filter"""
        if self.main_window:
            self.main_window.show_projetos(filtro_tipo="Pessoal BA")

    def navegar_projetos_rafael(self):
        """Navigate to Projetos screen with Rafael's personal projects filter"""
        if self.main_window:
            self.main_window.show_projetos(filtro_tipo="Pessoal RR")

    def navegar_premios_bruno(self):
        """Navigate to Projetos screen with Bruno's prizes filter"""
        if self.main_window:
            self.main_window.show_projetos(filtro_premio_socio="BA")

    def navegar_premios_rafael(self):
        """Navigate to Projetos screen with Rafael's prizes filter"""
        if self.main_window:
            self.main_window.show_projetos(filtro_premio_socio="RR")

    def navegar_despesas_fixas(self):
        """Navigate to Despesas screen with Fixa Mensal filter"""
        if self.main_window:
            self.main_window.show_despesas(filtro_tipo="Fixa Mensal")

    def navegar_boletins_pendentes_bruno(self):
        """Navigate to Boletins screen with Bruno's pending boletins"""
        if self.main_window:
            self.main_window.show_boletins(filtro_estado="Pendente", filtro_socio="BA")

    def navegar_boletins_pendentes_rafael(self):
        """Navigate to Boletins screen with Rafael's pending boletins"""
        if self.main_window:
            self.main_window.show_boletins(filtro_estado="Pendente", filtro_socio="RR")

    def navegar_boletins_pagos_bruno(self):
        """Navigate to Boletins screen with Bruno's paid boletins"""
        if self.main_window:
            self.main_window.show_boletins(filtro_estado="Pago", filtro_socio="BA")

    def navegar_boletins_pagos_rafael(self):
        """Navigate to Boletins screen with Rafael's paid boletins"""
        if self.main_window:
            self.main_window.show_boletins(filtro_estado="Pago", filtro_socio="RR")

    def carregar_saldos(self):
        """Load and display saldos"""

        # Calculate saldos
        saldo_bruno = self.calculator.calcular_saldo_bruno()
        saldo_rafael = self.calculator.calcular_saldo_rafael()

        # Update BA
        self.bruno_saldo_label.configure(
            text=f"€{saldo_bruno['saldo_total']:,.2f}",
            text_color=("#4CAF50", "#66BB6A") if saldo_bruno['saldo_total'] >= 0 else ("#F44336", "#E57373")
        )

        # Clear and populate INs
        for widget in self.bruno_ins_frame.winfo_children():
            widget.destroy()

        self.create_saldo_item(
            self.bruno_ins_frame,
            "Projetos pessoais",
            saldo_bruno['ins']['projetos_pessoais'],
            clickable=True,
            on_click=self.navegar_projetos_bruno,
            button_color=("#FFF8E1", "#4A3C0F")  # Light yellow/golden (BA color)
        )
        self.create_saldo_item(
            self.bruno_ins_frame,
            "Prémios",
            saldo_bruno['ins']['premios'],
            clickable=True,
            on_click=self.navegar_premios_bruno,
            button_color=("#FFF8E1", "#4A3C0F")  # Light yellow/golden (BA color)
        )

        # Separator line
        sep = ctk.CTkFrame(self.bruno_ins_frame, height=1, fg_color="gray")
        sep.pack(fill="x", pady=8)

        self.create_saldo_item(
            self.bruno_ins_frame,
            "TOTAL INs",
            saldo_bruno['ins']['total'],
            is_total=True
        )

        # Clear and populate OUTs
        for widget in self.bruno_outs_frame.winfo_children():
            widget.destroy()

        self.create_saldo_item(
            self.bruno_outs_frame,
            "Despesas fixas (÷2)",
            saldo_bruno['outs']['despesas_fixas'],
            clickable=True,
            on_click=self.navegar_despesas_fixas,
            button_color=("#FFF8E1", "#4A3C0F")  # Light yellow/golden (matching BA)
        )
        self.create_saldo_item(
            self.bruno_outs_frame,
            "Boletins pendentes",
            saldo_bruno['outs']['boletins_pendentes'],
            clickable=True,
            on_click=self.navegar_boletins_pendentes_bruno,
            button_color=("#FFF8E1", "#4A3C0F")  # Light yellow/golden (matching BA)
        )
        self.create_saldo_item(
            self.bruno_outs_frame,
            "Boletins pagos",
            saldo_bruno['outs']['boletins_pagos'],
            clickable=True,
            on_click=self.navegar_boletins_pagos_bruno,
            button_color=("#FFF8E1", "#4A3C0F")  # Light yellow/golden (matching BA)
        )
        self.create_saldo_item(
            self.bruno_outs_frame,
            "Despesas pessoais",
            saldo_bruno['outs']['despesas_pessoais']
        )

        # Separator line
        sep = ctk.CTkFrame(self.bruno_outs_frame, height=1, fg_color="gray")
        sep.pack(fill="x", pady=8)

        self.create_saldo_item(
            self.bruno_outs_frame,
            "TOTAL OUTs",
            saldo_bruno['outs']['total'],
            is_total=True
        )

        # Update sugestão
        self.bruno_sugestao_label.configure(
            text=f"Emitir boletim de €{saldo_bruno['sugestao_boletim']:,.2f} para zerar saldo"
        )

        # Update RR (same logic)
        self.rafael_saldo_label.configure(
            text=f"€{saldo_rafael['saldo_total']:,.2f}",
            text_color=("#4CAF50", "#66BB6A") if saldo_rafael['saldo_total'] >= 0 else ("#F44336", "#E57373")
        )

        # Clear and populate INs
        for widget in self.rafael_ins_frame.winfo_children():
            widget.destroy()

        self.create_saldo_item(
            self.rafael_ins_frame,
            "Projetos pessoais",
            saldo_rafael['ins']['projetos_pessoais'],
            clickable=True,
            on_click=self.navegar_projetos_rafael,
            button_color=("#FFF3E0", "#3E2A0D")  # Light amber/orange (RR color)
        )
        self.create_saldo_item(
            self.rafael_ins_frame,
            "Prémios",
            saldo_rafael['ins']['premios'],
            clickable=True,
            on_click=self.navegar_premios_rafael,
            button_color=("#FFF3E0", "#3E2A0D")  # Light amber/orange (RR color)
        )

        sep = ctk.CTkFrame(self.rafael_ins_frame, height=1, fg_color="gray")
        sep.pack(fill="x", pady=8)

        self.create_saldo_item(
            self.rafael_ins_frame,
            "TOTAL INs",
            saldo_rafael['ins']['total'],
            is_total=True
        )

        # Clear and populate OUTs
        for widget in self.rafael_outs_frame.winfo_children():
            widget.destroy()

        self.create_saldo_item(
            self.rafael_outs_frame,
            "Despesas fixas (÷2)",
            saldo_rafael['outs']['despesas_fixas'],
            clickable=True,
            on_click=self.navegar_despesas_fixas,
            button_color=("#FFF3E0", "#3E2A0D")  # Light amber/orange (matching RR)
        )
        self.create_saldo_item(
            self.rafael_outs_frame,
            "Boletins pendentes",
            saldo_rafael['outs']['boletins_pendentes'],
            clickable=True,
            on_click=self.navegar_boletins_pendentes_rafael,
            button_color=("#FFF3E0", "#3E2A0D")  # Light amber/orange (matching RR)
        )
        self.create_saldo_item(
            self.rafael_outs_frame,
            "Boletins pagos",
            saldo_rafael['outs']['boletins_pagos'],
            clickable=True,
            on_click=self.navegar_boletins_pagos_rafael,
            button_color=("#FFF3E0", "#3E2A0D")  # Light amber/orange (matching RR)
        )
        self.create_saldo_item(
            self.rafael_outs_frame,
            "Despesas pessoais",
            saldo_rafael['outs']['despesas_pessoais']
        )

        sep = ctk.CTkFrame(self.rafael_outs_frame, height=1, fg_color="gray")
        sep.pack(fill="x", pady=8)

        self.create_saldo_item(
            self.rafael_outs_frame,
            "TOTAL OUTs",
            saldo_rafael['outs']['total'],
            is_total=True
        )

        # Update sugestão
        self.rafael_sugestao_label.configure(
            text=f"Emitir boletim de €{saldo_rafael['sugestao_boletim']:,.2f} para zerar saldo"
        )
