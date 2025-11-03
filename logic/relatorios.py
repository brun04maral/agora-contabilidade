# -*- coding: utf-8 -*-
"""
Lógica de geração de relatórios
"""
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from datetime import date, datetime
from decimal import Decimal
from collections import defaultdict
from dateutil.relativedelta import relativedelta

from database.models import Socio, Projeto, EstadoProjeto, Despesa, EstadoDespesa
from logic.saldos import SaldosCalculator


class RelatoriosManager:
    """
    Gestor de relatórios - geração e exportação
    """

    def __init__(self, db_session: Session):
        """
        Initialize manager

        Args:
            db_session: SQLAlchemy database session
        """
        self.db_session = db_session
        self.saldos_calculator = SaldosCalculator(db_session)

    def gerar_relatorio_saldos(
        self,
        socio: Optional[Socio] = None,
        data_inicio: Optional[date] = None,
        data_fim: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Gera relatório de saldos pessoais

        Args:
            socio: Socio específico ou None para ambos
            data_inicio: Data de início do período (opcional)
            data_fim: Data de fim do período (opcional)

        Returns:
            Dicionário com dados do relatório
        """

        # Calcular saldos
        if socio == Socio.BRUNO:
            saldo_bruno = self.saldos_calculator.calcular_saldo_bruno()
            socios_data = [self._format_socio_data("Bruno Amaral", saldo_bruno, "#4CAF50")]
        elif socio == Socio.RAFAEL:
            saldo_rafael = self.saldos_calculator.calcular_saldo_rafael()
            socios_data = [self._format_socio_data("Rafael Reigota", saldo_rafael, "#2196F3")]
        else:
            # Ambos
            saldo_bruno = self.saldos_calculator.calcular_saldo_bruno()
            saldo_rafael = self.saldos_calculator.calcular_saldo_rafael()
            socios_data = [
                self._format_socio_data("Bruno Amaral", saldo_bruno, "#4CAF50"),
                self._format_socio_data("Rafael Reigota", saldo_rafael, "#2196F3")
            ]

        # Build report data
        periodo_str = self._format_periodo(data_inicio, data_fim)

        return {
            'tipo': 'saldos_pessoais',
            'titulo': 'Relatório de Saldos Pessoais',
            'periodo': periodo_str,
            'data_geracao': datetime.now().strftime('%d/%m/%Y %H:%M'),
            'data_inicio': data_inicio,
            'data_fim': data_fim,
            'socios': socios_data
        }

    def gerar_relatorio_financeiro_mensal(
        self,
        data_inicio: Optional[date] = None,
        data_fim: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Gera relatório financeiro mensal (faturação vs despesas)

        Args:
            data_inicio: Data de início do período
            data_fim: Data de fim do período

        Returns:
            Dicionário com dados do relatório
        """

        # Define período (último ano se não especificado)
        if not data_fim:
            data_fim = date.today()
        if not data_inicio:
            data_inicio = data_fim - relativedelta(years=1)

        # Buscar projetos recebidos no período
        projetos = self.db_session.query(Projeto).filter(
            Projeto.estado == EstadoProjeto.RECEBIDO,
            Projeto.data_faturacao.isnot(None),
            Projeto.data_faturacao >= data_inicio,
            Projeto.data_faturacao <= data_fim
        ).all()

        # Buscar despesas pagas no período
        despesas = self.db_session.query(Despesa).filter(
            Despesa.estado == EstadoDespesa.PAGO,
            Despesa.data_pagamento.isnot(None),
            Despesa.data_pagamento >= data_inicio,
            Despesa.data_pagamento <= data_fim
        ).all()

        # Agregar por mês
        meses_data = defaultdict(lambda: {
            'faturacao': Decimal('0'),
            'despesas': Decimal('0'),
            'resultado': Decimal('0')
        })

        # Agregar projetos
        for projeto in projetos:
            if projeto.data_faturacao:
                mes_key = projeto.data_faturacao.strftime('%Y-%m')
                meses_data[mes_key]['faturacao'] += projeto.valor_sem_iva

        # Agregar despesas
        for despesa in despesas:
            if despesa.data_pagamento:
                mes_key = despesa.data_pagamento.strftime('%Y-%m')
                meses_data[mes_key]['despesas'] += despesa.valor_com_iva

        # Calcular resultados
        for mes_key in meses_data:
            meses_data[mes_key]['resultado'] = (
                meses_data[mes_key]['faturacao'] -
                meses_data[mes_key]['despesas']
            )

        # Ordenar por mês e formatar
        meses_ordenados = sorted(meses_data.keys())
        meses_formatados = []

        total_faturacao = Decimal('0')
        total_despesas = Decimal('0')

        for mes_key in meses_ordenados:
            ano, mes = mes_key.split('-')
            mes_nome = self._get_month_name(int(mes))
            data = meses_data[mes_key]

            total_faturacao += data['faturacao']
            total_despesas += data['despesas']

            meses_formatados.append({
                'mes_key': mes_key,
                'mes_nome': mes_nome,
                'ano': ano,
                'faturacao': float(data['faturacao']),
                'faturacao_fmt': self._format_currency(float(data['faturacao'])),
                'despesas': float(data['despesas']),
                'despesas_fmt': self._format_currency(float(data['despesas'])),
                'resultado': float(data['resultado']),
                'resultado_fmt': self._format_currency(float(data['resultado'])),
                'cor_resultado': '#4CAF50' if data['resultado'] >= 0 else '#F44336'
            })

        periodo_str = self._format_periodo(data_inicio, data_fim)
        total_resultado = total_faturacao - total_despesas

        return {
            'tipo': 'financeiro_mensal',
            'titulo': 'Relatório Financeiro Mensal',
            'periodo': periodo_str,
            'data_geracao': datetime.now().strftime('%d/%m/%Y %H:%M'),
            'data_inicio': data_inicio,
            'data_fim': data_fim,
            'meses': meses_formatados,
            'totais': {
                'faturacao': float(total_faturacao),
                'faturacao_fmt': self._format_currency(float(total_faturacao)),
                'despesas': float(total_despesas),
                'despesas_fmt': self._format_currency(float(total_despesas)),
                'resultado': float(total_resultado),
                'resultado_fmt': self._format_currency(float(total_resultado)),
                'cor_resultado': '#4CAF50' if total_resultado >= 0 else '#F44336'
            }
        }

    def _get_month_name(self, mes: int) -> str:
        """Get month name in Portuguese"""
        meses = [
            'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
            'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
        ]
        return meses[mes - 1]

    def _format_socio_data(self, nome: str, saldo_data: dict, cor: str) -> Dict[str, Any]:
        """Format socio data for report"""

        ins = saldo_data['ins']
        outs = saldo_data['outs']

        return {
            'nome': nome,
            'saldo': self._format_currency(saldo_data['saldo_total']),
            'saldo_valor': saldo_data['saldo_total'],
            'cor': cor,
            'ins': [
                {'label': 'Projetos Pessoais', 'valor': self._format_currency(ins['projetos_pessoais'])},
                {'label': 'Prémios', 'valor': self._format_currency(ins['premios'])}
            ],
            'total_ins': self._format_currency(ins['total']),
            'total_ins_valor': ins['total'],
            'outs': [
                {'label': 'Despesas Fixas (50%)', 'valor': self._format_currency(outs['despesas_fixas'])},
                {'label': 'Boletins Pagos', 'valor': self._format_currency(outs['boletins'])},
                {'label': 'Despesas Pessoais', 'valor': self._format_currency(outs['despesas_pessoais'])}
            ],
            'total_outs': self._format_currency(outs['total']),
            'total_outs_valor': outs['total']
        }

    def _format_currency(self, valor: float) -> str:
        """Format value as currency"""
        return f"€{valor:,.2f}".replace(",", " ").replace(".", ",").replace(" ", ".")

    def _format_periodo(self, data_inicio: Optional[date], data_fim: Optional[date]) -> str:
        """Format period string"""
        if data_inicio and data_fim:
            return f"Período: {data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')}"
        elif data_inicio:
            return f"A partir de: {data_inicio.strftime('%d/%m/%Y')}"
        elif data_fim:
            return f"Até: {data_fim.strftime('%d/%m/%Y')}"
        else:
            return "Período: Acumulado (todo o histórico)"

    def exportar_pdf(self, report_data: Dict[str, Any], filename: str):
        """
        Exporta relatório para PDF

        Args:
            report_data: Dados do relatório
            filename: Nome do arquivo
        """
        tipo = report_data.get('tipo')

        if tipo == 'saldos_pessoais':
            self._exportar_pdf_saldos(report_data, filename)
        elif tipo == 'financeiro_mensal':
            self._exportar_pdf_financeiro(report_data, filename)
        else:
            raise ValueError(f"Tipo de relatório não suportado: {tipo}")

    def _exportar_pdf_saldos(self, report_data: Dict[str, Any], filename: str):
        """Export Saldos report to PDF"""
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.lib.units import cm
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.enums import TA_CENTER, TA_LEFT

        # Create PDF
        doc = SimpleDocTemplate(filename, pagesize=A4)
        elements = []
        styles = getSampleStyleSheet()

        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#2196F3'),
            alignment=TA_CENTER,
            spaceAfter=12
        )

        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Normal'],
            fontSize=12,
            textColor=colors.grey,
            alignment=TA_CENTER,
            spaceAfter=20
        )

        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#424242'),
            spaceAfter=10
        )

        # Title
        elements.append(Paragraph(report_data['titulo'], title_style))

        # Period and generation date
        if report_data['periodo']:
            elements.append(Paragraph(report_data['periodo'], subtitle_style))
        elements.append(Paragraph(f"Gerado em: {report_data['data_geracao']}", subtitle_style))
        elements.append(Spacer(1, 0.5*cm))

        # For each socio
        for socio_data in report_data['socios']:
            # Socio name
            elements.append(Paragraph(socio_data['nome'], heading_style))

            # Saldo
            saldo_data = [
                ['SALDO ATUAL', socio_data['saldo']]
            ]
            saldo_table = Table(saldo_data, colWidths=[8*cm, 6*cm])
            saldo_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#E3F2FD')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#1976D2')),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 18),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('TOPPADDING', (0, 0), (-1, -1), 12),
            ]))
            elements.append(saldo_table)
            elements.append(Spacer(1, 0.5*cm))

            # INs table
            ins_data = [
                ['RECEITAS (INs)', ''],
            ]
            for item in socio_data['ins']:
                ins_data.append([item['label'], item['valor']])
            ins_data.append(['TOTAL INs', socio_data['total_ins']])

            ins_table = Table(ins_data, colWidths=[10*cm, 5*cm])
            ins_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4CAF50')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#E8F5E9')),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ]))
            elements.append(ins_table)
            elements.append(Spacer(1, 0.3*cm))

            # OUTs table
            outs_data = [
                ['DESPESAS (OUTs)', ''],
            ]
            for item in socio_data['outs']:
                outs_data.append([item['label'], item['valor']])
            outs_data.append(['TOTAL OUTs', socio_data['total_outs']])

            outs_table = Table(outs_data, colWidths=[10*cm, 5*cm])
            outs_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F44336')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#FFEBEE')),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ]))
            elements.append(outs_table)
            elements.append(Spacer(1, 1*cm))

        # Build PDF
        doc.build(elements)

    def _exportar_pdf_financeiro(self, report_data: Dict[str, Any], filename: str):
        """Export Financeiro Mensal report to PDF"""
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.lib.units import cm
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.enums import TA_CENTER

        doc = SimpleDocTemplate(filename, pagesize=A4)
        elements = []
        styles = getSampleStyleSheet()

        # Styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#2196F3'),
            alignment=TA_CENTER,
            spaceAfter=12
        )

        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Normal'],
            fontSize=12,
            textColor=colors.grey,
            alignment=TA_CENTER,
            spaceAfter=20
        )

        # Title and metadata
        elements.append(Paragraph(report_data['titulo'], title_style))
        if report_data['periodo']:
            elements.append(Paragraph(report_data['periodo'], subtitle_style))
        elements.append(Paragraph(f"Gerado em: {report_data['data_geracao']}", subtitle_style))
        elements.append(Spacer(1, 0.5*cm))

        # Monthly data table
        table_data = [['Mês', 'Faturação', 'Despesas', 'Resultado']]

        for mes in report_data['meses']:
            table_data.append([
                f"{mes['mes_nome']} {mes['ano']}",
                mes['faturacao_fmt'],
                mes['despesas_fmt'],
                mes['resultado_fmt']
            ])

        # Totals row
        totais = report_data['totais']
        table_data.append([
            'TOTAL',
            totais['faturacao_fmt'],
            totais['despesas_fmt'],
            totais['resultado_fmt']
        ])

        table = Table(table_data, colWidths=[5*cm, 4*cm, 4*cm, 4*cm])

        # Base style
        table_style = [
            # Header
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2196F3')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TOPPADDING', (0, 0), (-1, 0), 12),

            # Data rows
            ('ALIGN', (0, 1), (0, -2), 'LEFT'),
            ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
            ('FONTSIZE', (0, 1), (-1, -2), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.HexColor('#F5F5F5')]),

            # Total row
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#E3F2FD')),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, -1), (-1, -1), 11),
            ('TOPPADDING', (0, -1), (-1, -1), 12),
            ('BOTTOMPADDING', (0, -1), (-1, -1), 12),
        ]

        # Color resultado column based on values
        for i, mes in enumerate(report_data['meses'], start=1):
            color = colors.HexColor('#4CAF50') if mes['resultado'] >= 0 else colors.HexColor('#F44336')
            table_style.append(('TEXTCOLOR', (3, i), (3, i), color))

        # Total resultado color
        total_color = colors.HexColor(totais['cor_resultado'])
        table_style.append(('TEXTCOLOR', (3, -1), (3, -1), total_color))

        table.setStyle(TableStyle(table_style))
        elements.append(table)

        doc.build(elements)

    def exportar_excel(self, report_data: Dict[str, Any], filename: str):
        """
        Exporta relatório para Excel

        Args:
            report_data: Dados do relatório
            filename: Nome do arquivo
        """
        tipo = report_data.get('tipo')

        if tipo == 'saldos_pessoais':
            self._exportar_excel_saldos(report_data, filename)
        elif tipo == 'financeiro_mensal':
            self._exportar_excel_financeiro(report_data, filename)
        else:
            raise ValueError(f"Tipo de relatório não suportado: {tipo}")

    def _exportar_excel_saldos(self, report_data: Dict[str, Any], filename: str):
        """Export Saldos report to Excel"""
        import openpyxl
        from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
        from openpyxl.utils import get_column_letter

        # Create workbook
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Saldos Pessoais"

        # Set column widths
        ws.column_dimensions['A'].width = 30
        ws.column_dimensions['B'].width = 18

        row = 1

        # Title
        ws.merge_cells(f'A{row}:B{row}')
        cell = ws[f'A{row}']
        cell.value = report_data['titulo']
        cell.font = Font(size=18, bold=True, color="2196F3")
        cell.alignment = Alignment(horizontal='center', vertical='center')
        row += 1

        # Period
        if report_data['periodo']:
            ws.merge_cells(f'A{row}:B{row}')
            cell = ws[f'A{row}']
            cell.value = report_data['periodo']
            cell.font = Font(size=11, color="666666")
            cell.alignment = Alignment(horizontal='center')
            row += 1

        # Generation date
        ws.merge_cells(f'A{row}:B{row}')
        cell = ws[f'A{row}']
        cell.value = f"Gerado em: {report_data['data_geracao']}"
        cell.font = Font(size=10, color="999999")
        cell.alignment = Alignment(horizontal='center')
        row += 2

        # For each socio
        for socio_data in report_data['socios']:
            # Socio name
            ws.merge_cells(f'A{row}:B{row}')
            cell = ws[f'A{row}']
            cell.value = socio_data['nome']
            cell.font = Font(size=14, bold=True)
            cell.alignment = Alignment(horizontal='center')
            cell.fill = PatternFill(start_color="E3F2FD", end_color="E3F2FD", fill_type="solid")
            row += 1

            # Saldo
            ws.merge_cells(f'A{row}:B{row}')
            cell = ws[f'A{row}']
            cell.value = f"SALDO ATUAL: {socio_data['saldo']}"
            cell.font = Font(size=16, bold=True, color="1976D2")
            cell.alignment = Alignment(horizontal='center', vertical='center')
            cell.fill = PatternFill(start_color="BBDEFB", end_color="BBDEFB", fill_type="solid")
            ws.row_dimensions[row].height = 30
            row += 2

            # INs header
            ws[f'A{row}'].value = "RECEITAS (INs)"
            ws[f'A{row}'].font = Font(bold=True, color="FFFFFF")
            ws[f'A{row}'].fill = PatternFill(start_color="4CAF50", end_color="4CAF50", fill_type="solid")
            ws[f'B{row}'].fill = PatternFill(start_color="4CAF50", end_color="4CAF50", fill_type="solid")
            row += 1

            # INs items
            for item in socio_data['ins']:
                ws[f'A{row}'].value = item['label']
                ws[f'B{row}'].value = item['valor']
                ws[f'B{row}'].alignment = Alignment(horizontal='right')
                row += 1

            # INs total
            ws[f'A{row}'].value = "TOTAL INs"
            ws[f'A{row}'].font = Font(bold=True)
            ws[f'B{row}'].value = socio_data['total_ins']
            ws[f'B{row}'].font = Font(bold=True)
            ws[f'B{row}'].alignment = Alignment(horizontal='right')
            ws[f'A{row}'].fill = PatternFill(start_color="E8F5E9", end_color="E8F5E9", fill_type="solid")
            ws[f'B{row}'].fill = PatternFill(start_color="E8F5E9", end_color="E8F5E9", fill_type="solid")
            row += 2

            # OUTs header
            ws[f'A{row}'].value = "DESPESAS (OUTs)"
            ws[f'A{row}'].font = Font(bold=True, color="FFFFFF")
            ws[f'A{row}'].fill = PatternFill(start_color="F44336", end_color="F44336", fill_type="solid")
            ws[f'B{row}'].fill = PatternFill(start_color="F44336", end_color="F44336", fill_type="solid")
            row += 1

            # OUTs items
            for item in socio_data['outs']:
                ws[f'A{row}'].value = item['label']
                ws[f'B{row}'].value = item['valor']
                ws[f'B{row}'].alignment = Alignment(horizontal='right')
                row += 1

            # OUTs total
            ws[f'A{row}'].value = "TOTAL OUTs"
            ws[f'A{row}'].font = Font(bold=True)
            ws[f'B{row}'].value = socio_data['total_outs']
            ws[f'B{row}'].font = Font(bold=True)
            ws[f'B{row}'].alignment = Alignment(horizontal='right')
            ws[f'A{row}'].fill = PatternFill(start_color="FFEBEE", end_color="FFEBEE", fill_type="solid")
            ws[f'B{row}'].fill = PatternFill(start_color="FFEBEE", end_color="FFEBEE", fill_type="solid")
            row += 3

        # Save
        wb.save(filename)

    def _exportar_excel_financeiro(self, report_data: Dict[str, Any], filename: str):
        """Export Financeiro Mensal report to Excel"""
        import openpyxl
        from openpyxl.styles import Font, Alignment, PatternFill

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Financeiro Mensal"

        # Column widths
        ws.column_dimensions['A'].width = 20
        ws.column_dimensions['B'].width = 15
        ws.column_dimensions['C'].width = 15
        ws.column_dimensions['D'].width = 15

        row = 1

        # Title
        ws.merge_cells(f'A{row}:D{row}')
        cell = ws[f'A{row}']
        cell.value = report_data['titulo']
        cell.font = Font(size=18, bold=True, color="2196F3")
        cell.alignment = Alignment(horizontal='center', vertical='center')
        row += 1

        # Period
        if report_data['periodo']:
            ws.merge_cells(f'A{row}:D{row}')
            cell = ws[f'A{row}']
            cell.value = report_data['periodo']
            cell.font = Font(size=11, color="666666")
            cell.alignment = Alignment(horizontal='center')
            row += 1

        # Generation date
        ws.merge_cells(f'A{row}:D{row}')
        cell = ws[f'A{row}']
        cell.value = f"Gerado em: {report_data['data_geracao']}"
        cell.font = Font(size=10, color="999999")
        cell.alignment = Alignment(horizontal='center')
        row += 2

        # Header
        headers = ['Mês', 'Faturação', 'Despesas', 'Resultado']
        for col_idx, header in enumerate(headers, start=1):
            cell = ws.cell(row=row, column=col_idx)
            cell.value = header
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = PatternFill(start_color="2196F3", end_color="2196F3", fill_type="solid")
            cell.alignment = Alignment(horizontal='center')
        row += 1

        # Data rows
        for mes in report_data['meses']:
            ws[f'A{row}'].value = f"{mes['mes_nome']} {mes['ano']}"
            ws[f'B{row}'].value = mes['faturacao_fmt']
            ws[f'B{row}'].alignment = Alignment(horizontal='right')
            ws[f'C{row}'].value = mes['despesas_fmt']
            ws[f'C{row}'].alignment = Alignment(horizontal='right')
            ws[f'D{row}'].value = mes['resultado_fmt']
            ws[f'D{row}'].alignment = Alignment(horizontal='right')

            # Color resultado
            color = "4CAF50" if mes['resultado'] >= 0 else "F44336"
            ws[f'D{row}'].font = Font(color=color)

            # Alternate row colors
            if row % 2 == 0:
                for col in ['A', 'B', 'C', 'D']:
                    ws[f'{col}{row}'].fill = PatternFill(start_color="F5F5F5", end_color="F5F5F5", fill_type="solid")

            row += 1

        # Totals row
        totais = report_data['totais']
        ws[f'A{row}'].value = "TOTAL"
        ws[f'A{row}'].font = Font(bold=True)
        ws[f'B{row}'].value = totais['faturacao_fmt']
        ws[f'B{row}'].font = Font(bold=True)
        ws[f'B{row}'].alignment = Alignment(horizontal='right')
        ws[f'C{row}'].value = totais['despesas_fmt']
        ws[f'C{row}'].font = Font(bold=True)
        ws[f'C{row}'].alignment = Alignment(horizontal='right')
        ws[f'D{row}'].value = totais['resultado_fmt']
        ws[f'D{row}'].font = Font(bold=True, color=totais['cor_resultado'].replace('#', ''))
        ws[f'D{row}'].alignment = Alignment(horizontal='right')

        for col in ['A', 'B', 'C', 'D']:
            ws[f'{col}{row}'].fill = PatternFill(start_color="E3F2FD", end_color="E3F2FD", fill_type="solid")

        wb.save(filename)
