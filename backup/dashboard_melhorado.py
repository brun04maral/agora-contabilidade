# -*- coding: utf-8 -*-
"""
Dashboard Melhorado - Visão geral completa do negócio
"""
import customtkinter as ctk
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from logic.saldos import SaldosCalculator
from database.models import (
    Socio, Projeto, TipoProjeto, EstadoProjeto,
    Despesa, TipoDespesa, EstadoDespesa,
    Boletim, EstadoBoletim,
    Cliente, Fornecedor
)
from datetime import date, timedelta
from decimal import Decimal


class DashboardMelhorado(ctk.CTkFrame):
    """
    Dashboard melhorado com indicadores financeiros e gráficos
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

        # === RESUMO FINANCEIRO (NOVO) ===
        self.criar_resumo_financeiro(scroll_frame)

        # === SALDOS PESSOAIS ===
        self.criar_saldos_pessoais(scroll_frame)

        # === ALERTAS (NOVO) ===
        self.criar_alertas(scroll_frame)

        # === ESTATÍSTICAS RÁPIDAS ===
        self.criar_estatisticas(scroll_frame)

    def criar_resumo_financeiro(self, parent):
        """Cria seção de resumo financeiro"""

        titulo = ctk.CTkLabel(
            parent,
            text="💰 Resumo Financeiro",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        titulo.pack(anchor="w", pady=(10, 10))

        container = ctk.CTkFrame(parent, fg_color="transparent")
        container.pack(fill="x", pady=(0, 30))

        # Faturação Total
        self.faturacao_card = self.create_metric_card(
            container,
            "Faturação Total",
            "€0,00",
            "#4CAF50",
            "Projetos recebidos"
        )
        self.faturacao_card.pack(side="left", fill="both", expand=True, padx=(0, 10))

        # Despesas Totais
        self.despesas_totais_card = self.create_metric_card(
            container,
            "Despesas Totais",
            "€0,00",
            "#F44336",
            "Despesas pagas"
        )
        self.despesas_totais_card.pack(side="left", fill="both", expand=True, padx=(10, 10))

        # Lucro/Prejuízo
        self.lucro_card = self.create_metric_card(
            container,
            "Resultado",
            "€0,00",
            "#2196F3",
            "Faturação - Despesas"
        )
        self.lucro_card.pack(side="left", fill="both", expand=True, padx=(10, 0))

    def criar_saldos_pessoais(self, parent):
        """Cria seção de saldos pessoais"""

        titulo = ctk.CTkLabel(
            parent,
            text="👥 Saldos Pessoais",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        titulo.pack(anchor="w", pady=(10, 10))

        container = ctk.CTkFrame(parent, fg_color="transparent")
        container.pack(fill="x", pady=(0, 30))

        # Bruno card
        self.bruno_card = self.create_saldo_detalhado_card(container, "Bruno Amaral", "#4CAF50")
        self.bruno_card.pack(side="left", fill="both", expand=True, padx=(0, 10))

        # Rafael card
        self.rafael_card = self.create_saldo_detalhado_card(container, "Rafael Reigota", "#2196F3")
        self.rafael_card.pack(side="left", fill="both", expand=True, padx=(10, 0))

    def criar_alertas(self, parent):
        """Cria seção de alertas"""

        titulo = ctk.CTkLabel(
            parent,
            text="⚠️ Ações Necessárias",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        titulo.pack(anchor="w", pady=(10, 10))

        # Container de alertas
        self.alertas_container = ctk.CTkFrame(parent, fg_color=("#E0E0E0", "#2B2B2B"), corner_radius=10)
        self.alertas_container.pack(fill="x", pady=(0, 30))

        # Label placeholder (será atualizado em carregar_dados)
        self.alertas_label = ctk.CTkLabel(
            self.alertas_container,
            text="Carregando alertas...",
            font=ctk.CTkFont(size=14),
            justify="left",
            anchor="w"
        )
        self.alertas_label.pack(padx=20, pady=15, fill="x")

    def criar_estatisticas(self, parent):
        """Cria estatísticas rápidas"""

        # === PROJETOS ===
        projetos_title = ctk.CTkLabel(
            parent,
            text="🎬 Projetos",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        projetos_title.pack(anchor="w", pady=(10, 10))

        projetos_container = ctk.CTkFrame(parent, fg_color="transparent")
        projetos_container.pack(fill="x", pady=(0, 30))

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
            parent,
            text="💸 Despesas",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        despesas_title.pack(anchor="w", pady=(10, 10))

        despesas_container = ctk.CTkFrame(parent, fg_color="transparent")
        despesas_container.pack(fill="x", pady=(0, 30))

        self.total_despesas_card = self.create_stat_card(despesas_container, "Total", "0", "#795548")
        self.total_despesas_card.pack(side="left", fill="both", expand=True, padx=(0, 10))

        self.despesas_pagas_card = self.create_stat_card(despesas_container, "Pagas", "0", "#4CAF50")
        self.despesas_pagas_card.pack(side="left", fill="both", expand=True, padx=(10, 10))

        self.despesas_pendentes_card = self.create_stat_card(despesas_container, "Pendentes", "0", "#FF9800")
        self.despesas_pendentes_card.pack(side="left", fill="both", expand=True, padx=(10, 0))

        # === BOLETINS ===
        boletins_title = ctk.CTkLabel(
            parent,
            text="📄 Boletins",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        boletins_title.pack(anchor="w", pady=(10, 10))

        boletins_container = ctk.CTkFrame(parent, fg_color="transparent")
        boletins_container.pack(fill="x", pady=(0, 30))

        self.total_boletins_card = self.create_stat_card(boletins_container, "Total", "0", "#607D8B")
        self.total_boletins_card.pack(side="left", fill="both", expand=True, padx=(0, 10))

        self.boletins_pagos_card = self.create_stat_card(boletins_container, "Pagos", "0", "#4CAF50")
        self.boletins_pagos_card.pack(side="left", fill="both", expand=True, padx=(10, 10))

        self.boletins_pendentes_card = self.create_stat_card(boletins_container, "Pendentes", "0", "#FF9800")
        self.boletins_pendentes_card.pack(side="left", fill="both", expand=True, padx=(10, 0))

    def create_metric_card(self, parent, title: str, value: str, color: str, subtitle: str = "") -> ctk.CTkFrame:
        """
        Create financial metric card

        Args:
            parent: Parent widget
            title: Card title
            value: Card value
            color: Card color
            subtitle: Card subtitle

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
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color="white"
        )
        value_label.pack(pady=(0, 5))

        # Subtitle
        if subtitle:
            subtitle_label = ctk.CTkLabel(
                card,
                text=subtitle,
                font=ctk.CTkFont(size=11),
                text_color=("gray90", "gray70")  # Cor mais suave para simular opacidade
            )
            subtitle_label.pack(pady=(0, 15))

        # Store reference
        card.value_label = value_label

        return card

    def create_saldo_detalhado_card(self, parent, nome: str, color: str) -> ctk.CTkFrame:
        """
        Create detailed saldo card with breakdown

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

        # Valor principal
        value_label = ctk.CTkLabel(
            card,
            text="€ 0,00",
            font=ctk.CTkFont(size=36, weight="bold"),
            text_color="white"
        )
        value_label.pack(pady=(0, 10))

        # Separador
        separator = ctk.CTkFrame(card, height=1, fg_color="white")
        separator.pack(fill="x", padx=30, pady=10)

        # Breakdown (INs e OUTs)
        breakdown_frame = ctk.CTkFrame(card, fg_color="transparent")
        breakdown_frame.pack(pady=(0, 20), padx=20, fill="x")

        # INs
        ins_label = ctk.CTkLabel(
            breakdown_frame,
            text="↑ INs: €0,00",
            font=ctk.CTkFont(size=12),
            text_color="white"
        )
        ins_label.pack(anchor="w")

        # OUTs
        outs_label = ctk.CTkLabel(
            breakdown_frame,
            text="↓ OUTs: €0,00",
            font=ctk.CTkFont(size=12),
            text_color="white"
        )
        outs_label.pack(anchor="w")

        # Store references
        card.value_label = value_label
        card.ins_label = ins_label
        card.outs_label = outs_label

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

        # Store reference
        card.value_label = value_label

        return card

    def formatar_moeda(self, valor: float) -> str:
        """Formata valor como moeda portuguesa"""
        return f"€{valor:,.2f}".replace(",", " ").replace(".", ",").replace(" ", ".")

    def carregar_dados(self):
        """Load and display all dashboard data"""

        # === RESUMO FINANCEIRO ===
        # Faturação total (projetos recebidos)
        faturacao = self.db_session.query(func.sum(Projeto.valor_sem_iva)).filter(
            Projeto.estado == EstadoProjeto.RECEBIDO
        ).scalar() or Decimal("0")

        # Despesas totais (pagas)
        despesas_total = self.db_session.query(func.sum(Despesa.valor_com_iva)).filter(
            Despesa.estado == EstadoDespesa.PAGO
        ).scalar() or Decimal("0")

        # Lucro/Prejuízo
        resultado = faturacao - despesas_total

        self.faturacao_card.value_label.configure(text=self.formatar_moeda(float(faturacao)))
        self.despesas_totais_card.value_label.configure(text=self.formatar_moeda(float(despesas_total)))

        # Mudar cor do card de resultado baseado no valor
        if resultado >= 0:
            self.lucro_card.configure(fg_color="#4CAF50")  # Verde para lucro
        else:
            self.lucro_card.configure(fg_color="#F44336")  # Vermelho para prejuízo
        self.lucro_card.value_label.configure(text=self.formatar_moeda(float(resultado)))

        # === SALDOS PESSOAIS ===
        saldo_bruno = self.calculator.calcular_saldo_bruno()
        saldo_rafael = self.calculator.calcular_saldo_rafael()

        # Bruno
        self.bruno_card.value_label.configure(text=self.formatar_moeda(saldo_bruno['saldo_total']))
        self.bruno_card.ins_label.configure(text=f"↑ INs: {self.formatar_moeda(saldo_bruno['ins']['total'])}")
        self.bruno_card.outs_label.configure(text=f"↓ OUTs: {self.formatar_moeda(saldo_bruno['outs']['total'])}")

        # Rafael
        self.rafael_card.value_label.configure(text=self.formatar_moeda(saldo_rafael['saldo_total']))
        self.rafael_card.ins_label.configure(text=f"↑ INs: {self.formatar_moeda(saldo_rafael['ins']['total'])}")
        self.rafael_card.outs_label.configure(text=f"↓ OUTs: {self.formatar_moeda(saldo_rafael['outs']['total'])}")

        # === ALERTAS ===
        alertas = []

        # Projetos não faturados
        projetos_nao_faturados = self.db_session.query(func.count(Projeto.id)).filter(
            Projeto.estado == EstadoProjeto.NAO_FATURADO
        ).scalar() or 0

        if projetos_nao_faturados > 0:
            alertas.append(f"• {projetos_nao_faturados} projeto(s) por faturar")

        # Boletins pendentes há mais de 30 dias
        data_limite = date.today() - timedelta(days=30)
        boletins_antigos = self.db_session.query(func.count(Boletim.id)).filter(
            Boletim.estado == EstadoBoletim.PENDENTE,
            Boletim.data_emissao <= data_limite
        ).scalar() or 0

        if boletins_antigos > 0:
            alertas.append(f"• {boletins_antigos} boletim(s) pendente(s) há mais de 30 dias")

        # Despesas vencidas
        despesas_vencidas = self.db_session.query(func.count(Despesa.id)).filter(
            Despesa.estado == EstadoDespesa.VENCIDO
        ).scalar() or 0

        if despesas_vencidas > 0:
            alertas.append(f"• {despesas_vencidas} despesa(s) vencida(s)")

        if alertas:
            self.alertas_label.configure(text="\n".join(alertas), text_color=("#D32F2F", "#FF5252"))
        else:
            self.alertas_label.configure(text="✅ Tudo em ordem! Não há ações pendentes.", text_color=("#388E3C", "#66BB6A"))

        # === PROJETOS ===
        total_projetos = self.db_session.query(func.count(Projeto.id)).scalar() or 0
        projetos_recebidos = self.db_session.query(func.count(Projeto.id)).filter(
            Projeto.estado == EstadoProjeto.RECEBIDO
        ).scalar() or 0
        projetos_faturados = self.db_session.query(func.count(Projeto.id)).filter(
            Projeto.estado == EstadoProjeto.FATURADO
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
            (Despesa.estado == EstadoDespesa.ATIVO) | (Despesa.estado == EstadoDespesa.VENCIDO)
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
