# -*- coding: utf-8 -*-
"""
Dashboard - Visão geral do sistema
"""
import customtkinter as ctk
from sqlalchemy.orm import Session
from sqlalchemy import func
from logic.saldos import SaldosCalculator
from database.models import (
    Socio, Projeto, TipoProjeto, EstadoProjeto
)
from assets.resources import (
    get_icon,
    DASHBOARD,
    SALDOSPESSOAIS,
    PROJETOS
)


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

    def create_section_title(self, parent, text: str, icon_constant) -> ctk.CTkLabel:
        """
        Create section title with icon

        Args:
            parent: Parent widget
            text: Section title text
            icon_constant: Icon constant from assets.resources

        Returns:
            Label widget
        """
        # Try to load PNG icon
        icon_pil = get_icon(icon_constant, size=(22, 22))

        if icon_pil:
            icon_ctk = ctk.CTkImage(
                light_image=icon_pil,
                dark_image=icon_pil,
                size=(22, 22)
            )
            title_label = ctk.CTkLabel(
                parent,
                image=icon_ctk,
                text=f" {text}",
                compound="left",
                font=ctk.CTkFont(size=22, weight="bold")
            )
        else:
            # Fallback to emoji (shouldn't happen, but just in case)
            title_label = ctk.CTkLabel(
                parent,
                text=text,
                font=ctk.CTkFont(size=22, weight="bold")
            )

        return title_label

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
        saldos_title = self.create_section_title(scroll_frame, "Saldos Pessoais", SALDOSPESSOAIS)
        saldos_title.pack(anchor="w", pady=(15, 15))

        saldos_container = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        saldos_container.pack(fill="x", pady=(0, 35))

        # BA card (clickable - navigates to Saldos)
        self.bruno_card = self.create_saldo_card(
            saldos_container,
            "BA",
            "#C9941F",  # Dourado muito escuro (Agora yellow - dark)
            on_click=lambda: self.navigate_to_saldos()
        )
        self.bruno_card.pack(side="left", fill="both", expand=True, padx=(0, 10))

        # RR card (clickable - navigates to Saldos)
        self.rafael_card = self.create_saldo_card(
            saldos_container,
            "RR",
            "#A67F1B",  # Âmbar profundo (Agora yellow - darker)
            on_click=lambda: self.navigate_to_saldos()
        )
        self.rafael_card.pack(side="left", fill="both", expand=True, padx=(10, 0))

        # === PROJETOS ===
        projetos_title = self.create_section_title(scroll_frame, "Projetos", PROJETOS)
        projetos_title.pack(anchor="w", pady=(15, 15))

        projetos_container = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        projetos_container.pack(fill="x", pady=(0, 35))

        # Stats cards (Opção 3 - Agora Inspired)
        self.total_projetos_card = self.create_stat_card(
            projetos_container, "Total", "0", "#6D4C41",  # Brown terra neutral
            on_click=lambda: self.navigate_to_projetos("Todos")
        )
        self.total_projetos_card.pack(side="left", fill="both", expand=True, padx=(0, 10))

        self.projetos_recebidos_card = self.create_stat_card(
            projetos_container, "Pagos", "0", "#7CB342",  # Light Green 600 - Positivo
            on_click=lambda: self.navigate_to_projetos("Pago")
        )
        self.projetos_recebidos_card.pack(side="left", fill="both", expand=True, padx=(10, 10))

        self.projetos_faturados_card = self.create_stat_card(
            projetos_container, "Finalizados", "0", "#C9941F",  # Dourado (match BA) - Ativo
            on_click=lambda: self.navigate_to_projetos("Finalizado")
        )
        self.projetos_faturados_card.pack(side="left", fill="both", expand=True, padx=(10, 10))

        self.projetos_nao_faturados_card = self.create_stat_card(
            projetos_container, "Ativos", "0", "#EF6C00",  # Orange 800 - Atenção
            on_click=lambda: self.navigate_to_projetos("Ativo")
        )
        self.projetos_nao_faturados_card.pack(side="left", fill="both", expand=True, padx=(10, 0))

    def create_saldo_card(self, parent, nome: str, color: str, on_click=None) -> ctk.CTkFrame:
        """
        Create saldo card

        Args:
            parent: Parent widget
            nome: Nome do sócio
            color: Card color
            on_click: Optional callback when card is clicked

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

        # Make clickable if callback provided
        if on_click:
            card.configure(cursor="hand2")

            # Bind click events to card and all children
            def handle_click(event):
                on_click()

            card.bind("<Button-1>", handle_click)
            name_label.bind("<Button-1>", handle_click)
            value_label.bind("<Button-1>", handle_click)

            # Add hover effects
            original_border = card.cget("border_color")

            def on_enter(event):
                card.configure(border_color=("#ffffff", "#ffffff"), border_width=3)

            def on_leave(event):
                card.configure(border_color=original_border, border_width=2)

            card.bind("<Enter>", on_enter)
            card.bind("<Leave>", on_leave)
            name_label.bind("<Enter>", on_enter)
            name_label.bind("<Leave>", on_leave)
            value_label.bind("<Enter>", on_enter)
            value_label.bind("<Leave>", on_leave)

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

    def navigate_to_saldos(self):
        """Navigate to saldos pessoais screen"""
        if self.main_window:
            self.main_window.show_saldos()

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
            Projeto.estado == EstadoProjeto.PAGO
        ).scalar() or 0
        projetos_faturados = self.db_session.query(func.count(Projeto.id)).filter(
            Projeto.estado == EstadoProjeto.FINALIZADO
        ).scalar() or 0
        projetos_nao_faturados = self.db_session.query(func.count(Projeto.id)).filter(
            Projeto.estado == EstadoProjeto.ATIVO
        ).scalar() or 0

        self.total_projetos_card.value_label.configure(text=str(total_projetos))
        self.projetos_recebidos_card.value_label.configure(text=str(projetos_recebidos))
        self.projetos_faturados_card.value_label.configure(text=str(projetos_faturados))
        self.projetos_nao_faturados_card.value_label.configure(text=str(projetos_nao_faturados))
