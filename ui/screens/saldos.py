# -*- coding: utf-8 -*-
"""
Tela de Saldos Pessoais - CORE DO SISTEMA
"""
import customtkinter as ctk
from typing import Callable, Optional
from sqlalchemy.orm import Session
from logic.saldos import SaldosCalculator
from database.models import Socio


class SaldosScreen(ctk.CTkFrame):
    """
    Tela de visualização de Saldos Pessoais dos sócios
    """

    def __init__(self, parent, db_session: Session, **kwargs):
        """
        Initialize saldos screen

        Args:
            parent: Parent widget
            db_session: SQLAlchemy database session
        """
        super().__init__(parent, **kwargs)

        self.db_session = db_session
        self.calculator = SaldosCalculator(db_session)

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

        # Header
        header = ctk.CTkFrame(card, fg_color=("#2196F3", "#1565C0"), corner_radius=10)
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

    def create_saldo_item(self, parent, label: str, value: float, is_total: bool = False):
        """
        Create a saldo line item

        Args:
            parent: Parent frame
            label: Item label
            value: Item value
            is_total: If this is a total line (bold)
        """
        item_frame = ctk.CTkFrame(parent, fg_color="transparent")
        item_frame.pack(fill="x", pady=3)

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
            saldo_bruno['ins']['projetos_pessoais']
        )
        self.create_saldo_item(
            self.bruno_ins_frame,
            "Prémios",
            saldo_bruno['ins']['premios']
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
            saldo_bruno['outs']['despesas_fixas']
        )
        self.create_saldo_item(
            self.bruno_outs_frame,
            "Boletins emitidos",
            saldo_bruno['outs']['boletins']
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
            saldo_rafael['ins']['projetos_pessoais']
        )
        self.create_saldo_item(
            self.rafael_ins_frame,
            "Prémios",
            saldo_rafael['ins']['premios']
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
            saldo_rafael['outs']['despesas_fixas']
        )
        self.create_saldo_item(
            self.rafael_outs_frame,
            "Boletins emitidos",
            saldo_rafael['outs']['boletins']
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
