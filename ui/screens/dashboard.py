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


class DashboardScreen(ctk.CTkFrame):
    """
    Dashboard com indicadores principais do sistema
    """

    def __init__(self, parent, db_session: Session, **kwargs):
        """
        Initialize dashboard screen

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
        self.carregar_dados()

    def create_widgets(self):
        """Create screen widgets"""

        # Header
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=30, pady=(30, 20))

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
            font=ctk.CTkFont(size=20, weight="bold")
        )
        saldos_title.pack(anchor="w", pady=(10, 10))

        saldos_container = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        saldos_container.pack(fill="x", pady=(0, 30))

        # Bruno card
        self.bruno_card = self.create_saldo_card(saldos_container, "Bruno Amaral", "#4CAF50")
        self.bruno_card.pack(side="left", fill="both", expand=True, padx=(0, 10))

        # Rafael card
        self.rafael_card = self.create_saldo_card(saldos_container, "Rafael Reigota", "#2196F3")
        self.rafael_card.pack(side="left", fill="both", expand=True, padx=(10, 0))

        # === PROJETOS ===
        projetos_title = ctk.CTkLabel(
            scroll_frame,
            text="🎬 Projetos",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        projetos_title.pack(anchor="w", pady=(10, 10))

        projetos_container = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        projetos_container.pack(fill="x", pady=(0, 30))

        # Stats cards
        self.total_projetos_card = self.create_stat_card(projetos_container, "Total", "0", "#9C27B0")
        self.total_projetos_card.pack(side="left", fill="both", expand=True, padx=(0, 10))

        self.projetos_recebidos_card = self.create_stat_card(projetos_container, "Recebidos", "0", "#4CAF50")
        self.projetos_recebidos_card.pack(side="left", fill="both", expand=True, padx=(10, 10))

        self.projetos_faturados_card = self.create_stat_card(projetos_container, "Faturados", "0", "#FF9800")
        self.projetos_faturados_card.pack(side="left", fill="both", expand=True, padx=(10, 10))

        self.projetos_nao_faturados_card = self.create_stat_card(projetos_container, "Não Faturados", "0", "#F44336")
        self.projetos_nao_faturados_card.pack(side="left", fill="both", expand=True, padx=(10, 0))

        # === DESPESAS ===
        despesas_title = ctk.CTkLabel(
            scroll_frame,
            text="💸 Despesas",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        despesas_title.pack(anchor="w", pady=(10, 10))

        despesas_container = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        despesas_container.pack(fill="x", pady=(0, 30))

        self.total_despesas_card = self.create_stat_card(despesas_container, "Total", "0", "#795548")
        self.total_despesas_card.pack(side="left", fill="both", expand=True, padx=(0, 10))

        self.despesas_pagas_card = self.create_stat_card(despesas_container, "Pagas", "0", "#4CAF50")
        self.despesas_pagas_card.pack(side="left", fill="both", expand=True, padx=(10, 10))

        self.despesas_pendentes_card = self.create_stat_card(despesas_container, "Pendentes", "0", "#FF9800")
        self.despesas_pendentes_card.pack(side="left", fill="both", expand=True, padx=(10, 0))

        # === BOLETINS ===
        boletins_title = ctk.CTkLabel(
            scroll_frame,
            text="📄 Boletins",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        boletins_title.pack(anchor="w", pady=(10, 10))

        boletins_container = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        boletins_container.pack(fill="x", pady=(0, 30))

        self.total_boletins_card = self.create_stat_card(boletins_container, "Total", "0", "#607D8B")
        self.total_boletins_card.pack(side="left", fill="both", expand=True, padx=(0, 10))

        self.boletins_pagos_card = self.create_stat_card(boletins_container, "Pagos", "0", "#4CAF50")
        self.boletins_pagos_card.pack(side="left", fill="both", expand=True, padx=(10, 10))

        self.boletins_pendentes_card = self.create_stat_card(boletins_container, "Pendentes", "0", "#FF9800")
        self.boletins_pendentes_card.pack(side="left", fill="both", expand=True, padx=(10, 0))

        # === CLIENTES & FORNECEDORES ===
        outros_title = ctk.CTkLabel(
            scroll_frame,
            text="📇 Clientes & Fornecedores",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        outros_title.pack(anchor="w", pady=(10, 10))

        outros_container = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        outros_container.pack(fill="x", pady=(0, 30))

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
        card = ctk.CTkFrame(parent, fg_color=color, corner_radius=10)

        # Nome
        name_label = ctk.CTkLabel(
            card,
            text=nome,
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="white"
        )
        name_label.pack(pady=(20, 10))

        # Valor
        value_label = ctk.CTkLabel(
            card,
            text="€ 0,00",
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color="white"
        )
        value_label.pack(pady=(0, 20))

        # Store reference to update later
        card.value_label = value_label

        return card

    def create_stat_card(self, parent, title: str, value: str, color: str) -> ctk.CTkFrame:
        """
        Create statistics card

        Args:
            parent: Parent widget
            title: Card title
            value: Card value
            color: Card color

        Returns:
            Card frame
        """
        card = ctk.CTkFrame(parent, fg_color=color, corner_radius=10)

        # Title
        title_label = ctk.CTkLabel(
            card,
            text=title,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="white"
        )
        title_label.pack(pady=(15, 5))

        # Value
        value_label = ctk.CTkLabel(
            card,
            text=value,
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="white"
        )
        value_label.pack(pady=(0, 15))

        # Store reference to update later
        card.value_label = value_label

        return card

    def carregar_dados(self):
        """Load and display all dashboard data"""

        # === SALDOS PESSOAIS ===
        saldo_bruno = self.calculator.calcular_saldo_bruno()
        saldo_rafael = self.calculator.calcular_saldo_rafael()

        self.bruno_card.value_label.configure(text=f"€ {saldo_bruno['saldo_final']:,.2f}".replace(",", " ").replace(".", ",").replace(" ", "."))
        self.rafael_card.value_label.configure(text=f"€ {saldo_rafael['saldo_final']:,.2f}".replace(",", " ").replace(".", ",").replace(" ", "."))

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
        despesas_pendentes = self.db_session.query(func.count(Despesa.id)).filter(
            Despesa.estado == EstadoDespesa.PENDENTE
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
