# -*- coding: utf-8 -*-
"""
Dashboard - Visão geral do sistema
"""
import customtkinter as ctk
from sqlalchemy.orm import Session
from sqlalchemy import func
from logic.saldos import SaldosCalculator
from database.models import (
    Socio, Projeto, TipoProjeto, EstadoProjeto,
    Despesa, TipoDespesa, EstadoDespesa,
    Boletim, EstadoBoletim,
    Cliente, Fornecedor
)
from assets.resources import get_icon, DASHBOARD


class DashboardScreen(ctk.CTkFrame):
    """
    Dashboard com indicadores principais do sistema
    """

    def __init__(self, parent, db_session: Session, main_window=None, **kwargs):
        """
        Initialize dashboard screen

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
        self.carregar_dados()

    def create_widgets(self):
        """Create screen widgets"""

        # Header
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=30, pady=(30, 20))

        # Title with PNG icon
        icon_pil = get_icon(DASHBOARD, size=(28, 28))
        if icon_pil:
            icon_ctk = ctk.CTkImage(
                light_image=icon_pil,
                dark_image=icon_pil,
                size=(28, 28)
            )
            title_label = ctk.CTkLabel(
                header_frame,
                image=icon_ctk,
                text=" Dashboard",
                compound="left",
                font=ctk.CTkFont(size=28, weight="bold")
            )
        else:
            title_label = ctk.CTkLabel(
                header_frame,
                text="📊 Dashboard",
                font=ctk.CTkFont(size=28, weight="bold")
            )
        title_label.pack(side="left")

        # Refresh button
        refresh_btn = ctk.CTkButton(
            header_frame,
            text="🔄 Atualizar",
            command=self.carregar_dados,
            width=120,
            height=35,
            font=ctk.CTkFont(size=13)
        )
        refresh_btn.pack(side="right")

        # Scrollable container
        scroll_frame = ctk.CTkScrollableFrame(self)
        scroll_frame.pack(fill="both", expand=True, padx=30, pady=(0, 30))

        # === SALDOS PESSOAIS ===
        saldos_title = ctk.CTkLabel(
            scroll_frame,
            text="💰 Saldos Pessoais",
            font=ctk.CTkFont(size=22, weight="bold")
        )
        saldos_title.pack(anchor="w", pady=(15, 15))

        saldos_container = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        saldos_container.pack(fill="x", pady=(0, 35))

        # BA card
        self.bruno_card = self.create_saldo_card(saldos_container, "BA", "#4CAF50")
        self.bruno_card.pack(side="left", fill="both", expand=True, padx=(0, 10))

        # RR card
        self.rafael_card = self.create_saldo_card(saldos_container, "RR", "#2196F3")
        self.rafael_card.pack(side="left", fill="both", expand=True, padx=(10, 0))

        # === PROJETOS ===
        projetos_title = ctk.CTkLabel(
            scroll_frame,
            text="🎬 Projetos",
            font=ctk.CTkFont(size=22, weight="bold")
        )
        projetos_title.pack(anchor="w", pady=(15, 15))

        projetos_container = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        projetos_container.pack(fill="x", pady=(0, 35))

        # Stats cards
        self.total_projetos_card = self.create_stat_card(
            projetos_container, "Total", "0", "#9C27B0",
            on_click=lambda: self.navigate_to_projetos("Todos")
        )
        self.total_projetos_card.pack(side="left", fill="both", expand=True, padx=(0, 10))

        self.projetos_recebidos_card = self.create_stat_card(
            projetos_container, "Recebidos", "0", "#4CAF50",
            on_click=lambda: self.navigate_to_projetos("Recebido")
        )
        self.projetos_recebidos_card.pack(side="left", fill="both", expand=True, padx=(10, 10))

        self.projetos_faturados_card = self.create_stat_card(
            projetos_container, "Faturados", "0", "#FF9800",
            on_click=lambda: self.navigate_to_projetos("Faturado")
        )
        self.projetos_faturados_card.pack(side="left", fill="both", expand=True, padx=(10, 10))

        self.projetos_nao_faturados_card = self.create_stat_card(
            projetos_container, "Não Faturados", "0", "#F44336",
            on_click=lambda: self.navigate_to_projetos("Não Faturado")
        )
        self.projetos_nao_faturados_card.pack(side="left", fill="both", expand=True, padx=(10, 0))

        # === DESPESAS ===
        despesas_title = ctk.CTkLabel(
            scroll_frame,
            text="💸 Despesas",
            font=ctk.CTkFont(size=22, weight="bold")
        )
        despesas_title.pack(anchor="w", pady=(15, 15))

        despesas_container = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        despesas_container.pack(fill="x", pady=(0, 35))

        self.total_despesas_card = self.create_stat_card(
            despesas_container, "Total", "0", "#795548",
            on_click=lambda: self.navigate_to_despesas("Todos")
        )
        self.total_despesas_card.pack(side="left", fill="both", expand=True, padx=(0, 10))

        self.despesas_pagas_card = self.create_stat_card(
            despesas_container, "Pagas", "0", "#4CAF50",
            on_click=lambda: self.navigate_to_despesas("Pago")
        )
        self.despesas_pagas_card.pack(side="left", fill="both", expand=True, padx=(10, 10))

        self.despesas_pendentes_card = self.create_stat_card(
            despesas_container, "Pendentes", "0", "#FF9800",
            on_click=lambda: self.navigate_to_despesas("Ativo")
        )
        self.despesas_pendentes_card.pack(side="left", fill="both", expand=True, padx=(10, 0))

        # === BOLETINS ===
        boletins_title = ctk.CTkLabel(
            scroll_frame,
            text="📄 Boletins",
            font=ctk.CTkFont(size=22, weight="bold")
        )
        boletins_title.pack(anchor="w", pady=(15, 15))

        boletins_container = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        boletins_container.pack(fill="x", pady=(0, 35))

        self.total_boletins_card = self.create_stat_card(
            boletins_container, "Total", "0", "#607D8B",
            on_click=lambda: self.navigate_to_boletins("Todos")
        )
        self.total_boletins_card.pack(side="left", fill="both", expand=True, padx=(0, 10))

        self.boletins_pagos_card = self.create_stat_card(
            boletins_container, "Pagos", "0", "#4CAF50",
            on_click=lambda: self.navigate_to_boletins("Pago")
        )
        self.boletins_pagos_card.pack(side="left", fill="both", expand=True, padx=(10, 10))

        self.boletins_pendentes_card = self.create_stat_card(
            boletins_container, "Pendentes", "0", "#FF9800",
            on_click=lambda: self.navigate_to_boletins("Pendente")
        )
        self.boletins_pendentes_card.pack(side="left", fill="both", expand=True, padx=(10, 0))

        # === CLIENTES & FORNECEDORES ===
        outros_title = ctk.CTkLabel(
            scroll_frame,
            text="📇 Clientes & Fornecedores",
            font=ctk.CTkFont(size=22, weight="bold")
        )
        outros_title.pack(anchor="w", pady=(15, 15))

        outros_container = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        outros_container.pack(fill="x", pady=(0, 35))

        self.total_clientes_card = self.create_stat_card(outros_container, "Clientes", "0", "#3F51B5")
        self.total_clientes_card.pack(side="left", fill="both", expand=True, padx=(0, 10))

        self.total_fornecedores_card = self.create_stat_card(outros_container, "Fornecedores", "0", "#009688")
        self.total_fornecedores_card.pack(side="left", fill="both", expand=True, padx=(10, 0))

    def create_saldo_card(self, parent, nome: str, color: str) -> ctk.CTkFrame:
        """
        Create saldo card

        Args:
            parent: Parent widget
            nome: Nome do sócio
            color: Card color

        Returns:
            Card frame
        """
        card = ctk.CTkFrame(
            parent,
            fg_color=color,
            corner_radius=15,
            border_width=2,
            border_color=("#e0e0e0", "#3a3a3a")
        )

        # Nome
        name_label = ctk.CTkLabel(
            card,
            text=nome,
            font=ctk.CTkFont(size=19, weight="bold"),
            text_color="white"
        )
        name_label.pack(pady=(25, 10))

        # Valor
        value_label = ctk.CTkLabel(
            card,
            text="€ 0,00",
            font=ctk.CTkFont(size=36, weight="bold"),
            text_color="white"
        )
        value_label.pack(pady=(5, 25))

        # Store reference to update later
        card.value_label = value_label

        return card

    def create_stat_card(self, parent, title: str, value: str, color: str, on_click=None) -> ctk.CTkFrame:
        """
        Create statistics card

        Args:
            parent: Parent widget
            title: Card title
            value: Card value
            color: Card color
            on_click: Optional callback when card is clicked

        Returns:
            Card frame
        """
        card = ctk.CTkFrame(
            parent,
            fg_color=color,
            corner_radius=12,
            border_width=2,
            border_color=("#e0e0e0", "#3a3a3a")
        )

        # Title
        title_label = ctk.CTkLabel(
            card,
            text=title,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="white"
        )
        title_label.pack(pady=(18, 8))

        # Value
        value_label = ctk.CTkLabel(
            card,
            text=value,
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color="white"
        )
        value_label.pack(pady=(0, 18))

        # Store reference to update later
        card.value_label = value_label

        # Make clickable if callback provided
        if on_click:
            card.configure(cursor="hand2")

            # Bind click events to card and all children
            def handle_click(event):
                on_click()

            card.bind("<Button-1>", handle_click)
            title_label.bind("<Button-1>", handle_click)
            value_label.bind("<Button-1>", handle_click)

            # Add hover effects
            original_border = card.cget("border_color")

            def on_enter(event):
                card.configure(border_color=("#ffffff", "#ffffff"), border_width=3)

            def on_leave(event):
                card.configure(border_color=original_border, border_width=2)

            card.bind("<Enter>", on_enter)
            card.bind("<Leave>", on_leave)
            title_label.bind("<Enter>", on_enter)
            title_label.bind("<Leave>", on_leave)
            value_label.bind("<Enter>", on_enter)
            value_label.bind("<Leave>", on_leave)

        return card

    def navigate_to_projetos(self, estado):
        """
        Navigate to projetos screen with filter

        Args:
            estado: Estado filter to apply
        """
        if self.main_window:
            self.main_window.show_projetos(filtro_estado=estado)

    def navigate_to_despesas(self, estado):
        """
        Navigate to despesas screen with filter

        Args:
            estado: Estado filter to apply
        """
        if self.main_window:
            self.main_window.show_despesas(filtro_estado=estado)

    def navigate_to_boletins(self, estado):
        """
        Navigate to boletins screen with filter

        Args:
            estado: Estado filter to apply
        """
        if self.main_window:
            self.main_window.show_boletins(filtro_estado=estado)

    def carregar_dados(self):
        """Load and display all dashboard data"""

        # === SALDOS PESSOAIS ===
        saldo_bruno = self.calculator.calcular_saldo_bruno()
        saldo_rafael = self.calculator.calcular_saldo_rafael()

        self.bruno_card.value_label.configure(text=f"€ {saldo_bruno['saldo_total']:,.2f}".replace(",", " ").replace(".", ",").replace(" ", "."))
        self.rafael_card.value_label.configure(text=f"€ {saldo_rafael['saldo_total']:,.2f}".replace(",", " ").replace(".", ",").replace(" ", "."))

        # === PROJETOS ===
        total_projetos = self.db_session.query(func.count(Projeto.id)).scalar() or 0
        projetos_recebidos = self.db_session.query(func.count(Projeto.id)).filter(
            Projeto.estado == EstadoProjeto.RECEBIDO
        ).scalar() or 0
        projetos_faturados = self.db_session.query(func.count(Projeto.id)).filter(
            Projeto.estado == EstadoProjeto.FATURADO
        ).scalar() or 0
        projetos_nao_faturados = self.db_session.query(func.count(Projeto.id)).filter(
            Projeto.estado == EstadoProjeto.NAO_FATURADO
        ).scalar() or 0

        self.total_projetos_card.value_label.configure(text=str(total_projetos))
        self.projetos_recebidos_card.value_label.configure(text=str(projetos_recebidos))
        self.projetos_faturados_card.value_label.configure(text=str(projetos_faturados))
        self.projetos_nao_faturados_card.value_label.configure(text=str(projetos_nao_faturados))

        # === DESPESAS ===
        total_despesas = self.db_session.query(func.count(Despesa.id)).scalar() or 0
        despesas_pagas = self.db_session.query(func.count(Despesa.id)).filter(
            Despesa.estado == EstadoDespesa.PAGO
        ).scalar() or 0
        # Despesas pendentes = PENDENTE + VENCIDO (tudo que não foi pago)
        despesas_pendentes = self.db_session.query(func.count(Despesa.id)).filter(
            (Despesa.estado == EstadoDespesa.PENDENTE) | (Despesa.estado == EstadoDespesa.VENCIDO)
        ).scalar() or 0

        self.total_despesas_card.value_label.configure(text=str(total_despesas))
        self.despesas_pagas_card.value_label.configure(text=str(despesas_pagas))
        self.despesas_pendentes_card.value_label.configure(text=str(despesas_pendentes))

        # === BOLETINS ===
        total_boletins = self.db_session.query(func.count(Boletim.id)).scalar() or 0
        boletins_pagos = self.db_session.query(func.count(Boletim.id)).filter(
            Boletim.estado == EstadoBoletim.PAGO
        ).scalar() or 0
        boletins_pendentes = self.db_session.query(func.count(Boletim.id)).filter(
            Boletim.estado == EstadoBoletim.PENDENTE
        ).scalar() or 0

        self.total_boletins_card.value_label.configure(text=str(total_boletins))
        self.boletins_pagos_card.value_label.configure(text=str(boletins_pagos))
        self.boletins_pendentes_card.value_label.configure(text=str(boletins_pendentes))

        # === CLIENTES & FORNECEDORES ===
        total_clientes = self.db_session.query(func.count(Cliente.id)).scalar() or 0
        total_fornecedores = self.db_session.query(func.count(Fornecedor.id)).scalar() or 0

        self.total_clientes_card.value_label.configure(text=str(total_clientes))
        self.total_fornecedores_card.value_label.configure(text=str(total_fornecedores))
