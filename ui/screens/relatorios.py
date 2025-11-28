# -*- coding: utf-8 -*-
"""
Tela de Relatórios - Visualização e exportação
"""
import customtkinter as ctk
from sqlalchemy.orm import Session
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
import tkinter.messagebox as messagebox
from tkinter import filedialog

from logic.relatorios import RelatoriosManager
from database.models import Socio
from assets.resources import get_icon, RELATORIOS


class RelatoriosScreen(ctk.CTkFrame):
    """
    Tela de relatórios com filtros e exportação
    """

    def __init__(self, parent, db_session: Session, projeto_ids=None, despesa_ids=None, boletim_ids=None, **kwargs):
        """
        Initialize relatorios screen

        Args:
            parent: Parent widget
            db_session: SQLAlchemy database session
            projeto_ids: Optional list of project IDs to pre-filter report
            despesa_ids: Optional list of despesa IDs to pre-filter report
            boletim_ids: Optional list of boletim IDs to pre-filter report
        """
        super().__init__(parent, **kwargs)

        self.db_session = db_session
        self.manager = RelatoriosManager(db_session)
        self.current_report_data = None
        self.projeto_ids_prefilter = projeto_ids
        self.despesa_ids_prefilter = despesa_ids
        self.boletim_ids_prefilter = boletim_ids

        self.configure(fg_color="transparent")
        self.create_widgets()

        # Auto-generate preview if project IDs provided
        if self.projeto_ids_prefilter:
            self.after(100, self.apply_project_prefilter)
        # Auto-generate preview if despesa IDs provided
        elif self.despesa_ids_prefilter:
            self.after(100, self.apply_despesa_prefilter)
        # Auto-generate preview if boletim IDs provided
        elif self.boletim_ids_prefilter:
            self.after(100, self.apply_boletim_prefilter)

    def create_widgets(self):
        """Create screen widgets"""

        # Header
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=30, pady=(30, 20))

        # Title with PNG icon
        icon_pil = get_icon(RELATORIOS, size=(28, 28))
        if icon_pil:
            icon_ctk = ctk.CTkImage(
                light_image=icon_pil,
                dark_image=icon_pil,
                size=(28, 28)
            )
            title_label = ctk.CTkLabel(
                header_frame,
                image=icon_ctk,
                text=" Relatórios",
                compound="left",
                font=ctk.CTkFont(size=28, weight="bold")
            )
        else:
            title_label = ctk.CTkLabel(
                header_frame,
                text="📊 Relatórios",
                font=ctk.CTkFont(size=28, weight="bold")
            )
        title_label.pack(side="left")

        # Main container
        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=30, pady=(0, 30))

        # Left side - Filters
        filters_frame = ctk.CTkFrame(main_container, width=300)
        filters_frame.pack(side="left", fill="y", padx=(0, 20))
        filters_frame.pack_propagate(False)

        self.create_filters(filters_frame)

        # Right side - Preview
        preview_frame = ctk.CTkFrame(main_container)
        preview_frame.pack(side="left", fill="both", expand=True)

        self.create_preview(preview_frame)

    def create_filters(self, parent):
        """Create filter panel"""

        # Title
        filter_title = ctk.CTkLabel(
            parent,
            text="⚙️ Filtros",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        filter_title.pack(pady=(20, 20))

        # Tipo de Relatório
        ctk.CTkLabel(
            parent,
            text="Tipo de Relatório",
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(anchor="w", padx=20, pady=(10, 5))

        self.tipo_relatorio = ctk.CTkOptionMenu(
            parent,
            values=["Saldos Pessoais", "Financeiro Mensal", "Projetos", "Despesas"],
            command=self.on_tipo_changed
        )
        self.tipo_relatorio.pack(fill="x", padx=20, pady=(0, 20))

        # Período
        ctk.CTkLabel(
            parent,
            text="Período",
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(anchor="w", padx=20, pady=(10, 5))

        self.periodo_var = ctk.StringVar(value="atual")
        periodo_options = [
            ("Atual", "atual"),
            ("Mês Atual", "mes_atual"),
            ("Último Mês", "mes_anterior"),
            ("Último Trimestre", "trimestre"),
            ("Último Ano", "ano"),
            ("Personalizado", "custom")
        ]

        for label, value in periodo_options:
            radio = ctk.CTkRadioButton(
                parent,
                text=label,
                variable=self.periodo_var,
                value=value,
                command=self.on_periodo_changed
            )
            radio.pack(anchor="w", padx=20, pady=2)

        # Datas personalizadas (inicialmente ocultas)
        self.custom_dates_frame = ctk.CTkFrame(parent, fg_color="transparent")
        self.custom_dates_frame.pack(fill="x", padx=20, pady=(10, 10))
        self.custom_dates_frame.pack_forget()  # Hide initially

        ctk.CTkLabel(
            self.custom_dates_frame,
            text="Data Início:",
            font=ctk.CTkFont(size=11)
        ).pack(anchor="w")
        self.data_inicio_entry = ctk.CTkEntry(self.custom_dates_frame, placeholder_text="AAAA-MM-DD")
        self.data_inicio_entry.pack(fill="x", pady=(2, 5))

        ctk.CTkLabel(
            self.custom_dates_frame,
            text="Data Fim:",
            font=ctk.CTkFont(size=11)
        ).pack(anchor="w")
        self.data_fim_entry = ctk.CTkEntry(self.custom_dates_frame, placeholder_text="AAAA-MM-DD")
        self.data_fim_entry.pack(fill="x", pady=(2, 10))

        # Sócio (para relatório de saldos)
        self.socio_frame = ctk.CTkFrame(parent, fg_color="transparent")
        self.socio_frame.pack(fill="x", padx=20, pady=(10, 20))

        ctk.CTkLabel(
            self.socio_frame,
            text="Sócio",
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(anchor="w", pady=(0, 5))

        self.socio_filter = ctk.CTkOptionMenu(
            self.socio_frame,
            values=["Ambos", "BA", "RR"]
        )
        self.socio_filter.pack(fill="x")

        # Tipo de Projeto (para relatório de saldos)
        self.tipo_projeto_frame = ctk.CTkFrame(parent, fg_color="transparent")
        self.tipo_projeto_frame.pack(fill="x", padx=20, pady=(10, 20))

        ctk.CTkLabel(
            self.tipo_projeto_frame,
            text="Filtrar Projetos",
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(anchor="w", pady=(0, 5))

        self.tipo_projeto_var = ctk.StringVar(value="todos")
        tipo_projeto_options = [
            ("Todos", "todos"),
            ("Empresa", "empresa"),
            ("Pessoais BA", "bruno"),
            ("Pessoais RR", "rafael")
        ]

        for label, value in tipo_projeto_options:
            radio = ctk.CTkRadioButton(
                self.tipo_projeto_frame,
                text=label,
                variable=self.tipo_projeto_var,
                value=value
            )
            radio.pack(anchor="w", pady=2)

        # Estado de Projeto (para relatório de projetos)
        self.estado_projeto_frame = ctk.CTkFrame(parent, fg_color="transparent")
        self.estado_projeto_frame.pack(fill="x", padx=20, pady=(10, 20))

        ctk.CTkLabel(
            self.estado_projeto_frame,
            text="Filtrar Estado",
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(anchor="w", pady=(0, 5))

        self.estado_projeto_var = ctk.StringVar(value="todos")
        estado_projeto_options = [
            ("Todos", "todos"),
            ("Ativo", "ativo"),
            ("Finalizado", "finalizado"),
            ("Pago", "pago")
        ]

        for label, value in estado_projeto_options:
            radio = ctk.CTkRadioButton(
                self.estado_projeto_frame,
                text=label,
                variable=self.estado_projeto_var,
                value=value
            )
            radio.pack(anchor="w", pady=2)

        # Initially hide filters that shouldn't be visible (default is Saldos Pessoais)
        self.tipo_projeto_frame.pack_forget()
        self.estado_projeto_frame.pack_forget()

        # Buttons
        btn_frame = ctk.CTkFrame(parent, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=(20, 20), side="bottom")

        # Gerar preview
        gerar_btn = ctk.CTkButton(
            btn_frame,
            text="🔍 Gerar Preview",
            command=self.gerar_preview,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=("#2196F3", "#1976D2"),
            hover_color=("#1976D2", "#1565C0")
        )
        gerar_btn.pack(fill="x", pady=(0, 10))

        # Exportar PDF
        pdf_btn = ctk.CTkButton(
            btn_frame,
            text="📄 Exportar PDF",
            command=self.exportar_pdf,
            height=35,
            fg_color=("#F44336", "#D32F2F"),
            hover_color=("#E53935", "#C62828")
        )
        pdf_btn.pack(fill="x", pady=(0, 10))

        # Exportar Excel
        excel_btn = ctk.CTkButton(
            btn_frame,
            text="📊 Exportar Excel",
            command=self.exportar_excel,
            height=35,
            fg_color=("#4CAF50", "#388E3C"),
            hover_color=("#66BB6A", "#2E7D32")
        )
        excel_btn.pack(fill="x")

    def create_preview(self, parent):
        """Create preview panel"""

        # Title
        preview_title = ctk.CTkLabel(
            parent,
            text="👁️ Preview do Relatório",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        preview_title.pack(pady=(20, 20))

        # Preview area (scrollable)
        self.preview_scroll = ctk.CTkScrollableFrame(parent)
        self.preview_scroll.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Placeholder
        self.placeholder_label = ctk.CTkLabel(
            self.preview_scroll,
            text="Selecione os filtros e clique em 'Gerar Preview'\npara visualizar o relatório",
            font=ctk.CTkFont(size=14),
            text_color="gray"
        )
        self.placeholder_label.pack(pady=100)

    def on_tipo_changed(self, value):
        """Handle report type change"""
        # Show/hide socio filter for Saldos Pessoais
        if value == "Saldos Pessoais":
            self.socio_frame.pack(fill="x", padx=20, pady=(10, 20))
            self.tipo_projeto_frame.pack_forget()
            self.estado_projeto_frame.pack_forget()
        # Show/hide tipo_projeto and estado_projeto filters for Projetos
        elif value == "Projetos":
            self.socio_frame.pack_forget()
            self.tipo_projeto_frame.pack(fill="x", padx=20, pady=(10, 20))
            self.estado_projeto_frame.pack(fill="x", padx=20, pady=(10, 20))
        else:
            self.socio_frame.pack_forget()
            self.tipo_projeto_frame.pack_forget()
            self.estado_projeto_frame.pack_forget()

    def on_periodo_changed(self):
        """Handle period change"""
        if self.periodo_var.get() == "custom":
            self.custom_dates_frame.pack(fill="x", padx=20, pady=(10, 10))
        else:
            self.custom_dates_frame.pack_forget()

    def get_date_range(self):
        """Get date range based on selected period"""
        periodo = self.periodo_var.get()
        hoje = date.today()

        if periodo == "atual":
            return None, None  # Sem filtro de data
        elif periodo == "mes_atual":
            inicio = date(hoje.year, hoje.month, 1)
            fim = hoje
            return inicio, fim
        elif periodo == "mes_anterior":
            primeiro_dia_mes_atual = date(hoje.year, hoje.month, 1)
            ultimo_dia_mes_anterior = primeiro_dia_mes_atual - relativedelta(days=1)
            inicio = date(ultimo_dia_mes_anterior.year, ultimo_dia_mes_anterior.month, 1)
            return inicio, ultimo_dia_mes_anterior
        elif periodo == "trimestre":
            inicio = hoje - relativedelta(months=3)
            return inicio, hoje
        elif periodo == "ano":
            inicio = hoje - relativedelta(years=1)
            return inicio, hoje
        elif periodo == "custom":
            try:
                inicio = date.fromisoformat(self.data_inicio_entry.get())
                fim = date.fromisoformat(self.data_fim_entry.get())
                return inicio, fim
            except:
                messagebox.showerror("Erro", "Datas inválidas! Use formato AAAA-MM-DD")
                return None, None

    def apply_project_prefilter(self):
        """Apply pre-filter for selected projects and auto-generate preview"""
        # Set report type to Projetos
        self.tipo_relatorio.set("Projetos")
        self.on_tipo_changed("Projetos")

        # Set period to "Atual" (no date filter)
        self.periodo_var.set("atual")
        self.on_periodo_changed()

        # Generate preview
        self.gerar_preview()

    def apply_despesa_prefilter(self):
        """Apply pre-filter for selected despesas and auto-generate preview"""
        # Set report type to Despesas
        self.tipo_relatorio.set("Despesas")
        self.on_tipo_changed("Despesas")

        # Set period to "Atual" (no date filter)
        self.periodo_var.set("atual")
        self.on_periodo_changed()

        # Generate preview
        self.gerar_preview()

    def apply_boletim_prefilter(self):
        """Apply pre-filter for selected boletins and auto-generate preview"""
        # Set report type to Boletins
        self.tipo_relatorio.set("Boletins")
        self.on_tipo_changed("Boletins")

        # Set period to "Atual" (no date filter)
        self.periodo_var.set("atual")
        self.on_periodo_changed()

        # Generate preview
        self.gerar_preview()

    def gerar_preview(self):
        """Generate report preview"""
        tipo = self.tipo_relatorio.get()
        data_inicio, data_fim = self.get_date_range()

        if self.periodo_var.get() == "custom" and (data_inicio is None or data_fim is None):
            return

        # Clear preview
        for widget in self.preview_scroll.winfo_children():
            widget.destroy()

        try:
            if tipo == "Saldos Pessoais":
                socio_str = self.socio_filter.get()
                socio = None
                if socio_str == "BA":
                    socio = Socio.BA
                elif socio_str == "RR":
                    socio = Socio.RR

                self.current_report_data = self.manager.gerar_relatorio_saldos(
                    socio=socio,
                    data_inicio=data_inicio,
                    data_fim=data_fim
                )
                self.render_saldos_preview(self.current_report_data)

            elif tipo == "Financeiro Mensal":
                self.current_report_data = self.manager.gerar_relatorio_financeiro_mensal(
                    data_inicio=data_inicio,
                    data_fim=data_fim
                )
                self.render_financeiro_preview(self.current_report_data)

            elif tipo == "Projetos":
                # Map filter to TipoProjeto enum
                from database.models import TipoProjeto, EstadoProjeto
                filtro_tipo_str = self.tipo_projeto_var.get()
                tipo_projeto = None
                if filtro_tipo_str == "empresa":
                    tipo_projeto = TipoProjeto.EMPRESA
                elif filtro_tipo_str == "bruno":
                    tipo_projeto = TipoProjeto.PESSOAL_BRUNO
                elif filtro_tipo_str == "rafael":
                    tipo_projeto = TipoProjeto.PESSOAL_RAFAEL
                # "todos" maps to None (no filter)

                # Map filter to EstadoProjeto enum
                filtro_estado_str = self.estado_projeto_var.get()
                estado_projeto = None
                if filtro_estado_str == "ativo":
                    estado_projeto = EstadoProjeto.ATIVO
                elif filtro_estado_str == "finalizado":
                    estado_projeto = EstadoProjeto.FINALIZADO
                elif filtro_estado_str == "pago":
                    estado_projeto = EstadoProjeto.PAGO
                # "todos" maps to None (no filter)

                self.current_report_data = self.manager.gerar_relatorio_projetos(
                    tipo=tipo_projeto,
                    estado=estado_projeto,
                    data_inicio=data_inicio,
                    data_fim=data_fim,
                    projeto_ids=self.projeto_ids_prefilter  # Pass pre-filter IDs if available
                )
                self.render_projetos_preview(self.current_report_data)

            elif tipo == "Despesas":
                # Despesas report doesn't have tipo/estado filters yet, just use pre-filter IDs
                self.current_report_data = self.manager.gerar_relatorio_despesas(
                    data_inicio=data_inicio,
                    data_fim=data_fim,
                    despesa_ids=self.despesa_ids_prefilter  # Pass pre-filter IDs if available
                )
                self.render_despesas_preview(self.current_report_data)

            elif tipo == "Boletins":
                # Boletins report doesn't have tipo/estado filters yet, just use pre-filter IDs
                self.current_report_data = self.manager.gerar_relatorio_boletins(
                    data_inicio=data_inicio,
                    data_fim=data_fim,
                    boletim_ids=self.boletim_ids_prefilter  # Pass pre-filter IDs if available
                )
                self.render_boletins_preview(self.current_report_data)

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao gerar relatório: {e}")

    def render_saldos_preview(self, data):
        """Render saldos report preview"""

        # Header
        header = ctk.CTkLabel(
            self.preview_scroll,
            text=data['titulo'],
            font=ctk.CTkFont(size=22, weight="bold")
        )
        header.pack(pady=(10, 5))

        # Período
        if data['periodo']:
            periodo_label = ctk.CTkLabel(
                self.preview_scroll,
                text=data['periodo'],
                font=ctk.CTkFont(size=12),
                text_color="gray"
            )
            periodo_label.pack(pady=(0, 20))

        # Data geração
        data_label = ctk.CTkLabel(
            self.preview_scroll,
            text=f"Gerado em: {data['data_geracao']}",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        data_label.pack(pady=(0, 20))

        # Render each socio
        for socio_data in data['socios']:
            self.render_socio_card(self.preview_scroll, socio_data)

    def render_socio_card(self, parent, socio_data):
        """Render a single socio card with detailed lists"""

        # Card container
        card = ctk.CTkFrame(parent, fg_color=socio_data['cor'], corner_radius=10)
        card.pack(fill="x", pady=(0, 20))

        # Nome
        nome_label = ctk.CTkLabel(
            card,
            text=socio_data['nome'],
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="white"
        )
        nome_label.pack(pady=(20, 10))

        # Saldo
        saldo_label = ctk.CTkLabel(
            card,
            text=socio_data['saldo'],
            font=ctk.CTkFont(size=36, weight="bold"),
            text_color="white"
        )
        saldo_label.pack(pady=(0, 20))

        # Separator
        separator = ctk.CTkFrame(card, height=1, fg_color="white")
        separator.pack(fill="x", padx=30, pady=10)

        # Breakdown with totals
        breakdown_frame = ctk.CTkFrame(card, fg_color="transparent")
        breakdown_frame.pack(pady=(0, 10), padx=40, fill="x")

        # INs Summary
        ins_frame = ctk.CTkFrame(breakdown_frame, fg_color="transparent")
        ins_frame.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
            ins_frame,
            text="💰 RECEITAS (INs)",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="white"
        ).pack(anchor="w")

        for item in socio_data['ins']:
            ctk.CTkLabel(
                ins_frame,
                text=f"  • {item['label']}: {item['valor']}",
                font=ctk.CTkFont(size=12),
                text_color="white"
            ).pack(anchor="w")

        ctk.CTkLabel(
            ins_frame,
            text=f"  TOTAL INs: {socio_data['total_ins']}",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="white"
        ).pack(anchor="w", pady=(5, 0))

        # OUTs Summary
        outs_frame = ctk.CTkFrame(breakdown_frame, fg_color="transparent")
        outs_frame.pack(fill="x")

        ctk.CTkLabel(
            outs_frame,
            text="💸 DESPESAS (OUTs)",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="white"
        ).pack(anchor="w")

        for item in socio_data['outs']:
            ctk.CTkLabel(
                outs_frame,
                text=f"  • {item['label']}: {item['valor']}",
                font=ctk.CTkFont(size=12),
                text_color="white"
            ).pack(anchor="w")

        ctk.CTkLabel(
            outs_frame,
            text=f"  TOTAL OUTs: {socio_data['total_outs']}",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="white"
        ).pack(anchor="w", pady=(5, 0))

        # Detailed Lists Container (outside colored card, in white/dark background)
        details_container = ctk.CTkFrame(parent, fg_color=("white", "#2B2B2B"), corner_radius=10)
        details_container.pack(fill="x", pady=(0, 30), padx=20)

        # Title
        ctk.CTkLabel(
            details_container,
            text=f"📋 Detalhes - {socio_data['nome']}",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(15, 10))

        # Projetos Pessoais List
        if socio_data.get('projetos_pessoais_list'):
            self._render_detail_section(
                details_container,
                "💼 Projetos Pessoais",
                socio_data['projetos_pessoais_list'],
                ['Nº', 'Cliente', 'Valor', 'Data'],
                lambda p: [p['numero'], p['cliente'][:25], p['valor_fmt'], p['data']]
            )

        # Prémios List
        if socio_data.get('premios_list'):
            self._render_detail_section(
                details_container,
                "🏆 Prémios",
                socio_data['premios_list'],
                ['Nº Projeto', 'Cliente', 'Prémio', 'Tipo'],
                lambda p: [p['numero'], p['cliente'][:25], p['premio_fmt'], p['tipo']]
            )

        # Despesas Fixas List
        if socio_data.get('despesas_fixas_list'):
            self._render_detail_section(
                details_container,
                "🏢 Despesas Fixas (50% cada sócio)",
                socio_data['despesas_fixas_list'][:10],  # Show first 10
                ['Nº', 'Fornecedor', 'Valor 50%', 'Data'],
                lambda d: [d['numero'], d['fornecedor'][:25], d['valor_50_fmt'], d['data']],
                show_more=len(socio_data['despesas_fixas_list']) > 10,
                total_count=len(socio_data['despesas_fixas_list'])
            )

        # Boletins List
        if socio_data.get('boletins_list'):
            self._render_detail_section(
                details_container,
                "📄 Boletins Pagos",
                socio_data['boletins_list'],
                ['Nº', 'Descrição', 'Valor', 'Data Pag.'],
                lambda b: [b['numero'], b['descricao'][:30], b['valor_fmt'], b['data_pagamento']]
            )

        # Despesas Pessoais List
        if socio_data.get('despesas_pessoais_list'):
            self._render_detail_section(
                details_container,
                "💳 Despesas Pessoais",
                socio_data['despesas_pessoais_list'],
                ['Nº', 'Fornecedor', 'Valor', 'Data'],
                lambda d: [d['numero'], d['fornecedor'][:25], d['valor_fmt'], d['data']]
            )

    def _render_detail_section(self, parent, title, items, headers, row_formatter, show_more=False, total_count=0):
        """Render a detailed list section"""

        section = ctk.CTkFrame(parent, fg_color="transparent")
        section.pack(fill="x", padx=20, pady=(0, 15))

        # Section title
        title_label = ctk.CTkLabel(
            section,
            text=f"{title} ({len(items)} items)",
            font=ctk.CTkFont(size=13, weight="bold")
        )
        title_label.pack(anchor="w", pady=(0, 5))

        # Table frame
        table_frame = ctk.CTkFrame(section, fg_color=("#E0E0E0", "#1E1E1E"), corner_radius=5)
        table_frame.pack(fill="x")

        # Headers
        header_row = ctk.CTkFrame(table_frame, fg_color=("#BDBDBD", "#424242"))
        header_row.pack(fill="x", padx=2, pady=(2, 0))

        for header in headers:
            ctk.CTkLabel(
                header_row,
                text=header,
                font=ctk.CTkFont(size=10, weight="bold"),
                anchor="w",
                width=120
            ).pack(side="left", padx=5, pady=5)

        # Data rows (limit to show)
        for idx, item in enumerate(items):
            row_color = ("#FFFFFF", "#2B2B2B") if idx % 2 == 0 else ("#F5F5F5", "#1E1E1E")
            row_frame = ctk.CTkFrame(table_frame, fg_color=row_color)
            row_frame.pack(fill="x", padx=2, pady=1)

            row_data = row_formatter(item)
            for value in row_data:
                ctk.CTkLabel(
                    row_frame,
                    text=str(value),
                    font=ctk.CTkFont(size=9),
                    anchor="w",
                    width=120
                ).pack(side="left", padx=5, pady=3)

        # Show more indicator
        if show_more:
            more_frame = ctk.CTkFrame(table_frame, fg_color=("#E0E0E0", "#1E1E1E"))
            more_frame.pack(fill="x", padx=2, pady=2)

            ctk.CTkLabel(
                more_frame,
                text=f"... e mais {total_count - len(items)} items (ver exportação completa)",
                font=ctk.CTkFont(size=9, slant="italic"),
                text_color="gray"
            ).pack(pady=5)

    def render_financeiro_preview(self, data):
        """Render financeiro mensal report preview"""

        # Header
        header = ctk.CTkLabel(
            self.preview_scroll,
            text=data['titulo'],
            font=ctk.CTkFont(size=22, weight="bold")
        )
        header.pack(pady=(10, 5))

        # Período
        if data['periodo']:
            periodo_label = ctk.CTkLabel(
                self.preview_scroll,
                text=data['periodo'],
                font=ctk.CTkFont(size=12),
                text_color="gray"
            )
            periodo_label.pack(pady=(0, 20))

        # Data geração
        data_label = ctk.CTkLabel(
            self.preview_scroll,
            text=f"Gerado em: {data['data_geracao']}",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        data_label.pack(pady=(0, 20))

        # Monthly table
        table_frame = ctk.CTkFrame(self.preview_scroll, fg_color=("#E0E0E0", "#2B2B2B"), corner_radius=10)
        table_frame.pack(fill="x", pady=(0, 20))

        # Table header
        header_row = ctk.CTkFrame(table_frame, fg_color=("#2196F3", "#1565C0"))
        header_row.pack(fill="x", padx=5, pady=(5, 0))

        headers = [
            ("Mês", 180),
            ("Faturação", 120),
            ("Despesas", 120),
            ("Resultado", 120)
        ]

        for header_text, width in headers:
            ctk.CTkLabel(
                header_row,
                text=header_text,
                font=ctk.CTkFont(size=13, weight="bold"),
                width=width,
                text_color="white"
            ).pack(side="left", padx=10, pady=10)

        # Data rows
        for idx, mes in enumerate(data['meses']):
            row_color = ("#FFFFFF", "#1E1E1E") if idx % 2 == 0 else ("#F5F5F5", "#2B2B2B")
            row_frame = ctk.CTkFrame(table_frame, fg_color=row_color)
            row_frame.pack(fill="x", padx=5, pady=1)

            # Mês
            ctk.CTkLabel(
                row_frame,
                text=f"{mes['mes_nome']} {mes['ano']}",
                font=ctk.CTkFont(size=12),
                width=180,
                anchor="w"
            ).pack(side="left", padx=10, pady=8)

            # Faturação
            ctk.CTkLabel(
                row_frame,
                text=mes['faturacao_fmt'],
                font=ctk.CTkFont(size=12),
                width=120,
                anchor="e"
            ).pack(side="left", padx=10, pady=8)

            # Despesas
            ctk.CTkLabel(
                row_frame,
                text=mes['despesas_fmt'],
                font=ctk.CTkFont(size=12),
                width=120,
                anchor="e"
            ).pack(side="left", padx=10, pady=8)

            # Resultado
            ctk.CTkLabel(
                row_frame,
                text=mes['resultado_fmt'],
                font=ctk.CTkFont(size=12, weight="bold"),
                width=120,
                anchor="e",
                text_color=mes['cor_resultado']
            ).pack(side="left", padx=10, pady=8)

        # Totals row
        totais = data['totais']
        totals_row = ctk.CTkFrame(table_frame, fg_color=("#E3F2FD", "#1565C0"))
        totals_row.pack(fill="x", padx=5, pady=(0, 5))

        ctk.CTkLabel(
            totals_row,
            text="TOTAL",
            font=ctk.CTkFont(size=13, weight="bold"),
            width=180,
            anchor="w"
        ).pack(side="left", padx=10, pady=12)

        ctk.CTkLabel(
            totals_row,
            text=totais['faturacao_fmt'],
            font=ctk.CTkFont(size=13, weight="bold"),
            width=120,
            anchor="e"
        ).pack(side="left", padx=10, pady=12)

        ctk.CTkLabel(
            totals_row,
            text=totais['despesas_fmt'],
            font=ctk.CTkFont(size=13, weight="bold"),
            width=120,
            anchor="e"
        ).pack(side="left", padx=10, pady=12)

        ctk.CTkLabel(
            totals_row,
            text=totais['resultado_fmt'],
            font=ctk.CTkFont(size=14, weight="bold"),
            width=120,
            anchor="e",
            text_color=totais['cor_resultado']
        ).pack(side="left", padx=10, pady=12)

    def render_projetos_preview(self, data):
        """Render projetos report preview"""

        # Header
        header = ctk.CTkLabel(
            self.preview_scroll,
            text=data['titulo'],
            font=ctk.CTkFont(size=22, weight="bold")
        )
        header.pack(pady=(10, 5))

        # Período
        if data['periodo']:
            periodo_label = ctk.CTkLabel(
                self.preview_scroll,
                text=data['periodo'],
                font=ctk.CTkFont(size=12),
                text_color="gray"
            )
            periodo_label.pack(pady=(0, 10))

        # Data geração
        data_label = ctk.CTkLabel(
            self.preview_scroll,
            text=f"Gerado em: {data['data_geracao']}",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        data_label.pack(pady=(0, 20))

        # Summary stats
        summary_frame = ctk.CTkFrame(self.preview_scroll, fg_color=("#E3F2FD", "#1565C0"), corner_radius=10)
        summary_frame.pack(fill="x", pady=(0, 20))

        # Build summary text based on whether to show premios
        mostrar_premios = data.get('mostrar_premios', False)
        if mostrar_premios:
            summary_text = f"📊 {data['total_projetos']} Projetos  |  💰 Valor Total: {data['total_valor_fmt']}  |  🏆 Prémios: BA {data['total_premios_bruno_fmt']} | RR {data['total_premios_rafael_fmt']}"
        else:
            summary_text = f"📊 {data['total_projetos']} Projetos  |  💰 Valor Total: {data['total_valor_fmt']}"

        ctk.CTkLabel(
            summary_frame,
            text=summary_text,
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=("#1976D2", "white")
        ).pack(pady=15, padx=20)

        # Projects table (limit to first 15 for preview)
        table_frame = ctk.CTkFrame(self.preview_scroll, fg_color=("#E0E0E0", "#2B2B2B"), corner_radius=10)
        table_frame.pack(fill="x", pady=(0, 20))

        # Table header
        header_row = ctk.CTkFrame(table_frame, fg_color=("#9C27B0", "#7B1FA2"))
        header_row.pack(fill="x", padx=5, pady=(5, 0))

        # Define headers based on whether to show premios
        mostrar_premios = data.get('mostrar_premios', False)

        if mostrar_premios:
            headers = [
                ("Nº", 80),
                ("Tipo", 120),
                ("Cliente", 140),
                ("Valor", 90),
                ("Prémio B", 90),
                ("Prémio R", 90),
                ("Estado", 110)
            ]
        else:
            headers = [
                ("Nº", 100),
                ("Tipo", 140),
                ("Cliente", 180),
                ("Valor", 110),
                ("Estado", 130)
            ]

        for header_text, width in headers:
            ctk.CTkLabel(
                header_row,
                text=header_text,
                font=ctk.CTkFont(size=13, weight="bold"),
                width=width,
                text_color="white"
            ).pack(side="left", padx=8, pady=10)

        # Data rows (show first 15)
        projetos_to_show = data['projetos'][:15]

        for idx, proj in enumerate(projetos_to_show):
            row_color = ("#FFFFFF", "#1E1E1E") if idx % 2 == 0 else ("#F5F5F5", "#2B2B2B")
            row_frame = ctk.CTkFrame(table_frame, fg_color=row_color)
            row_frame.pack(fill="x", padx=5, pady=1)

            # Número
            ctk.CTkLabel(
                row_frame,
                text=proj['numero'],
                font=ctk.CTkFont(size=11),
                width=80 if mostrar_premios else 100,
                anchor="w"
            ).pack(side="left", padx=8, pady=6)

            # Tipo
            ctk.CTkLabel(
                row_frame,
                text=proj['tipo'],
                font=ctk.CTkFont(size=11),
                width=120 if mostrar_premios else 140,
                anchor="w"
            ).pack(side="left", padx=8, pady=6)

            # Cliente
            cliente_len = 17 if mostrar_premios else 22
            ctk.CTkLabel(
                row_frame,
                text=proj['cliente'][:cliente_len] + '...' if len(proj['cliente']) > cliente_len else proj['cliente'],
                font=ctk.CTkFont(size=11),
                width=140 if mostrar_premios else 180,
                anchor="w"
            ).pack(side="left", padx=8, pady=6)

            # Valor
            ctk.CTkLabel(
                row_frame,
                text=proj['valor_fmt'],
                font=ctk.CTkFont(size=11),
                width=90 if mostrar_premios else 110,
                anchor="e"
            ).pack(side="left", padx=8, pady=6)

            # Prémios (apenas se mostrar_premios)
            if mostrar_premios:
                # Prémio BA
                ctk.CTkLabel(
                    row_frame,
                    text=proj['premio_bruno_fmt'],
                    font=ctk.CTkFont(size=11),
                    width=90,
                    anchor="e"
                ).pack(side="left", padx=8, pady=6)

                # Prémio RR
                ctk.CTkLabel(
                    row_frame,
                    text=proj['premio_rafael_fmt'],
                    font=ctk.CTkFont(size=11),
                    width=90,
                    anchor="e"
                ).pack(side="left", padx=8, pady=6)

            # Estado
            ctk.CTkLabel(
                row_frame,
                text=proj['estado'],
                font=ctk.CTkFont(size=11),
                width=110 if mostrar_premios else 130,
                anchor="center"
            ).pack(side="left", padx=8, pady=6)

        # Show count if more projects
        if len(data['projetos']) > 15:
            more_frame = ctk.CTkFrame(table_frame, fg_color=("#F5F5F5", "#2B2B2B"))
            more_frame.pack(fill="x", padx=5, pady=(0, 5))

            ctk.CTkLabel(
                more_frame,
                text=f"... e mais {len(data['projetos']) - 15} projetos (ver exportação completa)",
                font=ctk.CTkFont(size=11, slant="italic"),
                text_color="gray"
            ).pack(pady=10)

    def render_despesas_preview(self, data):
        """Render despesas report preview"""
        preview_frame = ctk.CTkFrame(self.preview_scroll, fg_color="transparent")
        preview_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Title
        ctk.CTkLabel(
            preview_frame,
            text=data['titulo'],
            font=ctk.CTkFont(size=24, weight="bold")
        ).pack(anchor="w", pady=(0, 5))

        # Period
        ctk.CTkLabel(
            preview_frame,
            text=f"Período: {data['periodo']}",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        ).pack(anchor="w", pady=(0, 10))

        # Filters
        filter_str = f"Filtros: {data['filtros']['tipo']}, {data['filtros']['estado']}"
        ctk.CTkLabel(
            preview_frame,
            text=filter_str,
            font=ctk.CTkFont(size=11),
            text_color="gray"
        ).pack(anchor="w", pady=(0, 20))

        # Summary stats
        stats_frame = ctk.CTkFrame(preview_frame, fg_color=("#E8F5E9", "#1B5E20"))
        stats_frame.pack(fill="x", pady=(0, 20))

        summary_grid = ctk.CTkFrame(stats_frame, fg_color="transparent")
        summary_grid.pack(padx=20, pady=15)

        # Total despesas
        ctk.CTkLabel(
            summary_grid,
            text=f"Total de Despesas: {data['total_despesas']}",
            font=ctk.CTkFont(size=14, weight="bold")
        ).grid(row=0, column=0, sticky="w", padx=10, pady=5)

        # Total valor sem IVA
        ctk.CTkLabel(
            summary_grid,
            text=f"Total sem IVA: {data['total_valor_sem_iva_fmt']}",
            font=ctk.CTkFont(size=14, weight="bold")
        ).grid(row=0, column=1, sticky="w", padx=10, pady=5)

        # Total valor com IVA
        ctk.CTkLabel(
            summary_grid,
            text=f"Total com IVA: {data['total_valor_com_iva_fmt']}",
            font=ctk.CTkFont(size=14, weight="bold")
        ).grid(row=0, column=2, sticky="w", padx=10, pady=5)

        # Stats by type
        stats_tipo_frame = ctk.CTkFrame(preview_frame, fg_color=("#F5F5F5", "#2B2B2B"))
        stats_tipo_frame.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
            stats_tipo_frame,
            text="Por Tipo",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", padx=15, pady=(10, 5))

        for stat in data['stats_por_tipo']:
            if stat['count'] > 0:  # Only show types with data
                stat_row = ctk.CTkFrame(stats_tipo_frame, fg_color="transparent")
                stat_row.pack(fill="x", padx=15, pady=2)

                ctk.CTkLabel(
                    stat_row,
                    text=f"{stat['tipo']}: {stat['count']} despesa(s) - {stat['valor_fmt']}",
                    font=ctk.CTkFont(size=12)
                ).pack(side="left")

        # Stats by estado
        stats_estado_frame = ctk.CTkFrame(preview_frame, fg_color=("#F5F5F5", "#2B2B2B"))
        stats_estado_frame.pack(fill="x", pady=(0, 20))

        ctk.CTkLabel(
            stats_estado_frame,
            text="Por Estado",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", padx=15, pady=(10, 5))

        for stat in data['stats_por_estado']:
            if stat['count'] > 0:  # Only show estados with data
                stat_row = ctk.CTkFrame(stats_estado_frame, fg_color="transparent")
                stat_row.pack(fill="x", padx=15, pady=2)

                ctk.CTkLabel(
                    stat_row,
                    text=f"{stat['estado']}: {stat['count']} despesa(s) - {stat['valor_fmt']}",
                    font=ctk.CTkFont(size=12)
                ).pack(side="left")

        # Despesas table
        ctk.CTkLabel(
            preview_frame,
            text="Detalhes das Despesas",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", pady=(0, 10))

        table_frame = ctk.CTkFrame(preview_frame, fg_color=("#F5F5F5", "#2B2B2B"))
        table_frame.pack(fill="x", pady=(0, 10))

        # Table header
        header_frame = ctk.CTkFrame(table_frame, fg_color=("#efd578", "#d4bb5e"))
        header_frame.pack(fill="x", padx=5, pady=5)

        ctk.CTkLabel(header_frame, text="Nº", font=ctk.CTkFont(size=11, weight="bold"), width=80).pack(side="left", padx=8, pady=6)
        ctk.CTkLabel(header_frame, text="Data", font=ctk.CTkFont(size=11, weight="bold"), width=90).pack(side="left", padx=8, pady=6)
        ctk.CTkLabel(header_frame, text="Tipo", font=ctk.CTkFont(size=11, weight="bold"), width=110).pack(side="left", padx=8, pady=6)
        ctk.CTkLabel(header_frame, text="Credor", font=ctk.CTkFont(size=11, weight="bold"), width=140).pack(side="left", padx=8, pady=6)
        ctk.CTkLabel(header_frame, text="Valor c/ IVA", font=ctk.CTkFont(size=11, weight="bold"), width=100, anchor="e").pack(side="left", padx=8, pady=6)
        ctk.CTkLabel(header_frame, text="Estado", font=ctk.CTkFont(size=11, weight="bold"), width=90, anchor="center").pack(side="left", padx=8, pady=6)

        # Show first 15 despesas
        for i, desp in enumerate(data['despesas'][:15]):
            is_even = i % 2 == 0
            row_frame = ctk.CTkFrame(
                table_frame,
                fg_color=("#FFFFFF", "#1E1E1E") if is_even else ("#F8F8F8", "#252525")
            )
            row_frame.pack(fill="x", padx=5, pady=2)

            # Numero
            ctk.CTkLabel(
                row_frame,
                text=desp['numero'],
                font=ctk.CTkFont(size=11),
                width=80,
                anchor="w"
            ).pack(side="left", padx=8, pady=6)

            # Data
            ctk.CTkLabel(
                row_frame,
                text=desp['data'],
                font=ctk.CTkFont(size=11),
                width=90,
                anchor="w"
            ).pack(side="left", padx=8, pady=6)

            # Tipo
            tipo_len = 13
            ctk.CTkLabel(
                row_frame,
                text=desp['tipo'][:tipo_len] + '...' if len(desp['tipo']) > tipo_len else desp['tipo'],
                font=ctk.CTkFont(size=11),
                width=110,
                anchor="w"
            ).pack(side="left", padx=8, pady=6)

            # Credor
            credor_len = 18
            ctk.CTkLabel(
                row_frame,
                text=desp['credor'][:credor_len] + '...' if len(desp['credor']) > credor_len else desp['credor'],
                font=ctk.CTkFont(size=11),
                width=140,
                anchor="w"
            ).pack(side="left", padx=8, pady=6)

            # Valor com IVA
            ctk.CTkLabel(
                row_frame,
                text=desp['valor_com_iva_fmt'],
                font=ctk.CTkFont(size=11),
                width=100,
                anchor="e"
            ).pack(side="left", padx=8, pady=6)

            # Estado
            ctk.CTkLabel(
                row_frame,
                text=desp['estado'],
                font=ctk.CTkFont(size=11),
                width=90,
                anchor="center"
            ).pack(side="left", padx=8, pady=6)

        # Show count if more despesas
        if len(data['despesas']) > 15:
            more_frame = ctk.CTkFrame(table_frame, fg_color=("#F5F5F5", "#2B2B2B"))
            more_frame.pack(fill="x", padx=5, pady=(0, 5))

            ctk.CTkLabel(
                more_frame,
                text=f"... e mais {len(data['despesas']) - 15} despesas (ver exportação completa)",
                font=ctk.CTkFont(size=11, slant="italic"),
                text_color="gray"
            ).pack(pady=10)

    def render_boletins_preview(self, data):
        """Render boletins report preview"""
        preview_frame = ctk.CTkFrame(self.preview_scroll, fg_color="transparent")
        preview_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Title
        ctk.CTkLabel(
            preview_frame,
            text=data['titulo'],
            font=ctk.CTkFont(size=24, weight="bold")
        ).pack(anchor="w", pady=(0, 5))

        # Period
        ctk.CTkLabel(
            preview_frame,
            text=f"Período: {data['periodo']}",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        ).pack(anchor="w", pady=(0, 10))

        # Filters
        filter_str = f"Filtros: {data['filtros']['socio']}, {data['filtros']['estado']}"
        ctk.CTkLabel(
            preview_frame,
            text=filter_str,
            font=ctk.CTkFont(size=11),
            text_color="gray"
        ).pack(anchor="w", pady=(0, 20))

        # Summary stats
        stats_frame = ctk.CTkFrame(preview_frame, fg_color=("#E8F5E9", "#1B5E20"))
        stats_frame.pack(fill="x", pady=(0, 20))

        summary_grid = ctk.CTkFrame(stats_frame, fg_color="transparent")
        summary_grid.pack(padx=20, pady=15)

        # Total boletins
        ctk.CTkLabel(
            summary_grid,
            text=f"Total de Boletins: {data['total_boletins']}",
            font=ctk.CTkFont(size=14, weight="bold")
        ).grid(row=0, column=0, sticky="w", padx=10, pady=5)

        # Total valor
        ctk.CTkLabel(
            summary_grid,
            text=f"Total: {data['total_valor_fmt']}",
            font=ctk.CTkFont(size=14, weight="bold")
        ).grid(row=0, column=1, sticky="w", padx=10, pady=5)

        # Stats by socio
        stats_socio_frame = ctk.CTkFrame(preview_frame, fg_color=("#F5F5F5", "#2B2B2B"))
        stats_socio_frame.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
            stats_socio_frame,
            text="Por Sócio",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", padx=15, pady=(10, 5))

        for stat in data['stats_por_socio']:
            if stat['count'] > 0:  # Only show socios with data
                stat_row = ctk.CTkFrame(stats_socio_frame, fg_color="transparent")
                stat_row.pack(fill="x", padx=15, pady=2)

                ctk.CTkLabel(
                    stat_row,
                    text=f"{stat['socio']}: {stat['count']} boletim(ns) - {stat['valor_fmt']}",
                    font=ctk.CTkFont(size=12)
                ).pack(side="left")

        # Stats by estado
        stats_estado_frame = ctk.CTkFrame(preview_frame, fg_color=("#F5F5F5", "#2B2B2B"))
        stats_estado_frame.pack(fill="x", pady=(0, 20))

        ctk.CTkLabel(
            stats_estado_frame,
            text="Por Estado",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", padx=15, pady=(10, 5))

        for stat in data['stats_por_estado']:
            if stat['count'] > 0:  # Only show estados with data
                stat_row = ctk.CTkFrame(stats_estado_frame, fg_color="transparent")
                stat_row.pack(fill="x", padx=15, pady=2)

                ctk.CTkLabel(
                    stat_row,
                    text=f"{stat['estado']}: {stat['count']} boletim(ns) - {stat['valor_fmt']}",
                    font=ctk.CTkFont(size=12)
                ).pack(side="left")

        # Boletins table
        ctk.CTkLabel(
            preview_frame,
            text="Detalhes dos Boletins",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", pady=(0, 10))

        table_frame = ctk.CTkFrame(preview_frame, fg_color=("#F5F5F5", "#2B2B2B"))
        table_frame.pack(fill="x", pady=(0, 10))

        # Table header
        header_frame = ctk.CTkFrame(table_frame, fg_color=("#efd578", "#d4bb5e"))
        header_frame.pack(fill="x", padx=5, pady=5)

        ctk.CTkLabel(header_frame, text="Nº", font=ctk.CTkFont(size=11, weight="bold"), width=80).pack(side="left", padx=8, pady=6)
        ctk.CTkLabel(header_frame, text="Sócio", font=ctk.CTkFont(size=11, weight="bold"), width=80).pack(side="left", padx=8, pady=6)
        ctk.CTkLabel(header_frame, text="Data Emissão", font=ctk.CTkFont(size=11, weight="bold"), width=110).pack(side="left", padx=8, pady=6)
        ctk.CTkLabel(header_frame, text="Valor", font=ctk.CTkFont(size=11, weight="bold"), width=100, anchor="e").pack(side="left", padx=8, pady=6)
        ctk.CTkLabel(header_frame, text="Estado", font=ctk.CTkFont(size=11, weight="bold"), width=90, anchor="center").pack(side="left", padx=8, pady=6)
        ctk.CTkLabel(header_frame, text="Data Pagamento", font=ctk.CTkFont(size=11, weight="bold"), width=120, anchor="center").pack(side="left", padx=8, pady=6)

        # Show first 15 boletins
        for i, bol in enumerate(data['boletins'][:15]):
            is_even = i % 2 == 0
            row_frame = ctk.CTkFrame(
                table_frame,
                fg_color=("#FFFFFF", "#1E1E1E") if is_even else ("#F8F8F8", "#252525")
            )
            row_frame.pack(fill="x", padx=5, pady=2)

            # Numero
            ctk.CTkLabel(
                row_frame,
                text=bol['numero'],
                font=ctk.CTkFont(size=11),
                width=80,
                anchor="w"
            ).pack(side="left", padx=8, pady=6)

            # Socio
            ctk.CTkLabel(
                row_frame,
                text=bol['socio'],
                font=ctk.CTkFont(size=11),
                width=80,
                anchor="w"
            ).pack(side="left", padx=8, pady=6)

            # Data Emissão
            ctk.CTkLabel(
                row_frame,
                text=bol['data_emissao'],
                font=ctk.CTkFont(size=11),
                width=110,
                anchor="w"
            ).pack(side="left", padx=8, pady=6)

            # Valor
            ctk.CTkLabel(
                row_frame,
                text=bol['valor_fmt'],
                font=ctk.CTkFont(size=11),
                width=100,
                anchor="e"
            ).pack(side="left", padx=8, pady=6)

            # Estado
            ctk.CTkLabel(
                row_frame,
                text=bol['estado'],
                font=ctk.CTkFont(size=11),
                width=90,
                anchor="center"
            ).pack(side="left", padx=8, pady=6)

            # Data Pagamento
            ctk.CTkLabel(
                row_frame,
                text=bol['data_pagamento'],
                font=ctk.CTkFont(size=11),
                width=120,
                anchor="center"
            ).pack(side="left", padx=8, pady=6)

        # Show count if more boletins
        if len(data['boletins']) > 15:
            more_frame = ctk.CTkFrame(table_frame, fg_color=("#F5F5F5", "#2B2B2B"))
            more_frame.pack(fill="x", padx=5, pady=(0, 5))

            ctk.CTkLabel(
                more_frame,
                text=f"... e mais {len(data['boletins']) - 15} boletins (ver exportação completa)",
                font=ctk.CTkFont(size=11, slant="italic"),
                text_color="gray"
            ).pack(pady=10)

    def _gerar_nome_ficheiro(self, extensao):
        """Generate dynamic filename based on report type and filters"""
        if not self.current_report_data:
            return f"relatorio_{date.today().strftime('%Y%m%d')}.{extensao}"

        tipo = self.current_report_data.get('tipo', 'relatorio')
        data_str = date.today().strftime('%Y%m%d')

        # Build filename components
        parts = []

        # Report type
        if tipo == 'saldos_pessoais':
            parts.append('Saldos')
            # Add socio filter
            socio_str = self.socio_filter.get()
            if socio_str == "BA":
                parts.append('BA')
            elif socio_str == "RR":
                parts.append('RR')
            else:
                parts.append('Ambos')
        elif tipo == 'financeiro_mensal':
            parts.append('FinanceiroMensal')
        elif tipo == 'projetos':
            parts.append('Projetos')
            # Add tipo projeto filter
            filtro_tipo = self.current_report_data.get('filtros', {}).get('tipo', 'Todos')
            if filtro_tipo != 'Todos':
                filtro_clean = filtro_tipo.replace(' ', '')
                parts.append(filtro_clean)
            # Add estado projeto filter
            filtro_estado = self.current_report_data.get('filtros', {}).get('estado', 'Todos')
            if filtro_estado != 'Todos':
                filtro_clean = filtro_estado.replace(' ', '')
                parts.append(filtro_clean)
        else:
            parts.append('Relatorio')

        # Add date
        parts.append(data_str)

        # Build final filename
        filename = '_'.join(parts) + '.' + extensao
        return filename

    def exportar_pdf(self):
        """Export report to PDF"""
        if not self.current_report_data:
            messagebox.showwarning("Aviso", "Gere o preview do relatório primeiro!")
            return

        # Generate dynamic filename
        default_filename = self._gerar_nome_ficheiro('pdf')

        # Ask for save location
        filename = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
            initialfile=default_filename
        )

        if filename:
            try:
                self.manager.exportar_pdf(self.current_report_data, filename)
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao exportar PDF: {e}")

    def exportar_excel(self):
        """Export report to Excel"""
        if not self.current_report_data:
            messagebox.showwarning("Aviso", "Gere o preview do relatório primeiro!")
            return

        # Generate dynamic filename
        default_filename = self._gerar_nome_ficheiro('xlsx')

        # Ask for save location
        filename = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
            initialfile=default_filename
        )

        if filename:
            try:
                self.manager.exportar_excel(self.current_report_data, filename)
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao exportar Excel: {e}")
