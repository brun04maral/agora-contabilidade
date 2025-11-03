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


class RelatoriosScreen(ctk.CTkFrame):
    """
    Tela de relatórios com filtros e exportação
    """

    def __init__(self, parent, db_session: Session, **kwargs):
        super().__init__(parent, **kwargs)

        self.db_session = db_session
        self.manager = RelatoriosManager(db_session)
        self.current_report_data = None

        self.configure(fg_color="transparent")
        self.create_widgets()

    def create_widgets(self):
        """Create screen widgets"""

        # Header
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=30, pady=(30, 20))

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
            values=["Ambos", "Bruno", "Rafael"]
        )
        self.socio_filter.pack(fill="x")

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
        # Show/hide socio filter based on report type
        if value == "Saldos Pessoais":
            self.socio_frame.pack(fill="x", padx=20, pady=(10, 20))
        else:
            self.socio_frame.pack_forget()

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
                if socio_str == "Bruno":
                    socio = Socio.BRUNO
                elif socio_str == "Rafael":
                    socio = Socio.RAFAEL

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
                messagebox.showinfo("Em breve", "Relatório de Projetos em desenvolvimento")
            elif tipo == "Despesas":
                messagebox.showinfo("Em breve", "Relatório de Despesas em desenvolvimento")

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
        """Render a single socio card"""

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

        # Breakdown
        breakdown_frame = ctk.CTkFrame(card, fg_color="transparent")
        breakdown_frame.pack(pady=(0, 20), padx=40, fill="x")

        # INs
        ins_frame = ctk.CTkFrame(breakdown_frame, fg_color="transparent")
        ins_frame.pack(fill="x", pady=(0, 15))

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

        # OUTs
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

    def exportar_pdf(self):
        """Export report to PDF"""
        if not self.current_report_data:
            messagebox.showwarning("Aviso", "Gere o preview do relatório primeiro!")
            return

        # Ask for save location
        filename = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
            initialfile=f"relatorio_saldos_{date.today().strftime('%Y%m%d')}.pdf"
        )

        if filename:
            try:
                self.manager.exportar_pdf(self.current_report_data, filename)
                messagebox.showinfo("Sucesso", f"Relatório exportado para:\n{filename}")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao exportar PDF: {e}")

    def exportar_excel(self):
        """Export report to Excel"""
        if not self.current_report_data:
            messagebox.showwarning("Aviso", "Gere o preview do relatório primeiro!")
            return

        # Ask for save location
        filename = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
            initialfile=f"relatorio_saldos_{date.today().strftime('%Y%m%d')}.xlsx"
        )

        if filename:
            try:
                self.manager.exportar_excel(self.current_report_data, filename)
                messagebox.showinfo("Sucesso", f"Relatório exportado para:\n{filename}")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao exportar Excel: {e}")
