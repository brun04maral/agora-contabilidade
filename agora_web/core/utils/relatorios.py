# -*- coding: utf-8 -*-
"""
Sistema de Geração de Relatórios para Agora Contabilidade

Suporta exportação de projetos, despesas, boletins e orçamentos
em formatos PDF e Excel com templates personalizáveis.

Autor: Agora Contabilidade
Data: 2026-01-12
"""
from io import BytesIO
from datetime import date, datetime
from decimal import Decimal
from typing import List, Dict, Any, Optional

from django.http import HttpResponse
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT

import xlsxwriter
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side


class RelatorioBase:
    """
    Classe base para geração de relatórios
    """

    # Informações da empresa
    EMPRESA_NOME = "Amaral & Reigota - Produção Audiovisual, Lda"
    EMPRESA_MARCA = "Agora Media Production"
    EMPRESA_NIPC = "518 351 190"
    EMPRESA_MORADA = "Portugal"  # Atualizar com morada real se necessário

    def __init__(self):
        self.today = date.today()

    def _format_currency(self, value) -> str:
        """Formata valor como moeda EUR"""
        if value is None:
            return "€0,00"
        return f"€{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    def _format_date(self, date_value) -> str:
        """Formata data para formato PT"""
        if date_value is None:
            return "-"
        if isinstance(date_value, str):
            return date_value
        return date_value.strftime("%d/%m/%Y")

    def _format_number(self, value) -> str:
        """Formata número com separadores PT"""
        if value is None:
            return "0"
        return f"{value:,.0f}".replace(",", ".")


class RelatorioProjetos(RelatorioBase):
    """
    Gerador de relatórios para Projetos
    """

    def gerar_pdf(self, projetos, filtros: Optional[Dict[str, Any]] = None) -> HttpResponse:
        """
        Gera relatório PDF de projetos

        Args:
            projetos: QuerySet de projetos
            filtros: Dicionário com filtros aplicados (opcional)

        Returns:
            HttpResponse com PDF
        """
        buffer = BytesIO()

        # Configurar documento PDF em landscape para caber mais colunas
        doc = SimpleDocTemplate(
            buffer,
            pagesize=landscape(A4),
            rightMargin=1*cm,
            leftMargin=1*cm,
            topMargin=1.5*cm,
            bottomMargin=1.5*cm
        )

        # Container para elementos do PDF
        elements = []

        # Estilos
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            textColor=colors.HexColor('#1976d2'),
            spaceAfter=12,
            alignment=TA_CENTER
        )

        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Normal'],
            fontSize=9,
            textColor=colors.grey,
            spaceAfter=6,
            alignment=TA_CENTER
        )

        # Cabeçalho
        elements.append(Paragraph(self.EMPRESA_MARCA, title_style))
        elements.append(Paragraph(f"{self.EMPRESA_NOME} | NIPC: {self.EMPRESA_NIPC}", subtitle_style))
        elements.append(Spacer(1, 0.3*cm))

        # Título do relatório
        titulo = "Relatório de Projetos"
        if filtros:
            if filtros.get('tipo_relatorio'):
                titulo = f"Relatório de Projetos - {filtros['tipo_relatorio']}"

        elements.append(Paragraph(titulo, title_style))

        # Informações do relatório
        info_text = f"Gerado em: {self._format_date(self.today)}"
        if filtros:
            if filtros.get('data_inicio') and filtros.get('data_fim'):
                info_text += f" | Período: {self._format_date(filtros['data_inicio'])} - {self._format_date(filtros['data_fim'])}"
            if filtros.get('socio'):
                info_text += f" | Sócio: {filtros['socio']}"
            if filtros.get('estado'):
                info_text += f" | Estado: {filtros['estado']}"

        elements.append(Paragraph(info_text, subtitle_style))
        elements.append(Spacer(1, 0.5*cm))

        # Preparar dados da tabela
        data = [
            ['#', 'Tipo', 'Sócio', 'Cliente', 'Descrição', 'Valor s/ IVA', 'Prémio BA', 'Prémio RR', 'Estado', 'Data Fat.']
        ]

        total_valor = Decimal('0.00')
        total_premio_ba = Decimal('0.00')
        total_premio_rr = Decimal('0.00')

        for projeto in projetos:
            data.append([
                projeto.numero,
                projeto.get_tipo_display(),
                str(projeto.socio) if projeto.socio else '-',
                str(projeto.cliente) if projeto.cliente else '-',
                projeto.descricao[:40] + '...' if len(projeto.descricao) > 40 else projeto.descricao,
                self._format_currency(projeto.valor_sem_iva),
                self._format_currency(projeto.premio_bruno) if projeto.premio_bruno else '-',
                self._format_currency(projeto.premio_rafael) if projeto.premio_rafael else '-',
                projeto.get_estado_display(),
                self._format_date(projeto.data_faturacao)
            ])

            total_valor += projeto.valor_sem_iva or Decimal('0.00')
            total_premio_ba += projeto.premio_bruno or Decimal('0.00')
            total_premio_rr += projeto.premio_rafael or Decimal('0.00')

        # Linha de totais
        data.append([
            '', '', '', '', 'TOTAL:',
            self._format_currency(total_valor),
            self._format_currency(total_premio_ba),
            self._format_currency(total_premio_rr),
            '', ''
        ])

        # Criar tabela
        table = Table(data, colWidths=[
            2*cm,   # #
            2*cm,   # Tipo
            1.5*cm, # Sócio
            3*cm,   # Cliente
            6*cm,   # Descrição
            2.5*cm, # Valor
            2.2*cm, # Prémio BA
            2.2*cm, # Prémio RR
            2*cm,   # Estado
            2.2*cm  # Data
        ])

        # Estilo da tabela
        table.setStyle(TableStyle([
            # Cabeçalho
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1976d2')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),

            # Dados
            ('FONTNAME', (0, 1), (-1, -2), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -2), 8),
            ('ALIGN', (5, 1), (7, -1), 'RIGHT'),  # Valores alinhados à direita
            ('ALIGN', (0, 1), (0, -1), 'CENTER'),  # Número centralizado

            # Linha de totais
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#e3f2fd')),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, -1), (-1, -1), 9),

            # Bordas
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),

            # Cores alternadas nas linhas
            *[('BACKGROUND', (0, i), (-1, i), colors.HexColor('#f5f5f5'))
              for i in range(2, len(data)-1, 2)]
        ]))

        elements.append(table)

        # Resumo
        elements.append(Spacer(1, 0.5*cm))
        resumo_text = f"Total de projetos: {len(projetos)}"
        elements.append(Paragraph(resumo_text, subtitle_style))

        # Gerar PDF
        doc.build(elements)

        # Preparar response
        buffer.seek(0)
        filename = self._gerar_nome_arquivo(filtros, 'pdf')

        response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'

        return response

    def gerar_excel(self, projetos, filtros: Optional[Dict[str, Any]] = None) -> HttpResponse:
        """
        Gera relatório Excel de projetos

        Args:
            projetos: QuerySet de projetos
            filtros: Dicionário com filtros aplicados (opcional)

        Returns:
            HttpResponse com Excel
        """
        buffer = BytesIO()

        # Criar workbook
        workbook = xlsxwriter.Workbook(buffer, {'in_memory': True})
        worksheet = workbook.add_worksheet('Projetos')

        # Formatos
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#1976d2',
            'font_color': 'white',
            'align': 'center',
            'valign': 'vcenter',
            'border': 1
        })

        currency_format = workbook.add_format({
            'num_format': '€#,##0.00',
            'align': 'right'
        })

        date_format = workbook.add_format({
            'num_format': 'dd/mm/yyyy',
            'align': 'center'
        })

        total_format = workbook.add_format({
            'bold': True,
            'bg_color': '#e3f2fd',
            'num_format': '€#,##0.00',
            'align': 'right',
            'border': 1
        })

        text_format = workbook.add_format({
            'align': 'left',
            'valign': 'vcenter'
        })

        center_format = workbook.add_format({
            'align': 'center',
            'valign': 'vcenter'
        })

        # Informações do cabeçalho
        worksheet.write(0, 0, self.EMPRESA_MARCA, workbook.add_format({'bold': True, 'font_size': 14}))
        worksheet.write(1, 0, f"{self.EMPRESA_NOME} | NIPC: {self.EMPRESA_NIPC}", workbook.add_format({'font_size': 10}))

        titulo = "Relatório de Projetos"
        if filtros and filtros.get('tipo_relatorio'):
            titulo = f"Relatório de Projetos - {filtros['tipo_relatorio']}"
        worksheet.write(2, 0, titulo, workbook.add_format({'bold': True, 'font_size': 12}))

        info_text = f"Gerado em: {self.today.strftime('%d/%m/%Y')}"
        worksheet.write(3, 0, info_text, workbook.add_format({'font_size': 10}))

        # Cabeçalhos da tabela
        row = 5
        headers = ['Número', 'Tipo', 'Sócio', 'Cliente', 'Descrição', 'Valor s/ IVA',
                   'Prémio Bruno', 'Prémio Rafael', 'Estado', 'Data Faturação', 'Data Início', 'Data Fim']

        for col, header in enumerate(headers):
            worksheet.write(row, col, header, header_format)

        # Dados
        row += 1
        total_valor = Decimal('0.00')
        total_premio_ba = Decimal('0.00')
        total_premio_rr = Decimal('0.00')

        for projeto in projetos:
            worksheet.write(row, 0, projeto.numero, center_format)
            worksheet.write(row, 1, projeto.get_tipo_display(), center_format)
            worksheet.write(row, 2, str(projeto.socio) if projeto.socio else '-', center_format)
            worksheet.write(row, 3, str(projeto.cliente) if projeto.cliente else '-', text_format)
            worksheet.write(row, 4, projeto.descricao, text_format)
            worksheet.write(row, 5, float(projeto.valor_sem_iva or 0), currency_format)
            worksheet.write(row, 6, float(projeto.premio_bruno or 0), currency_format)
            worksheet.write(row, 7, float(projeto.premio_rafael or 0), currency_format)
            worksheet.write(row, 8, projeto.get_estado_display(), center_format)

            if projeto.data_faturacao:
                worksheet.write_datetime(row, 9, projeto.data_faturacao, date_format)
            else:
                worksheet.write(row, 9, '-', center_format)

            if projeto.data_inicio:
                worksheet.write_datetime(row, 10, projeto.data_inicio, date_format)
            else:
                worksheet.write(row, 10, '-', center_format)

            if projeto.data_fim:
                worksheet.write_datetime(row, 11, projeto.data_fim, date_format)
            else:
                worksheet.write(row, 11, '-', center_format)

            total_valor += projeto.valor_sem_iva or Decimal('0.00')
            total_premio_ba += projeto.premio_bruno or Decimal('0.00')
            total_premio_rr += projeto.premio_rafael or Decimal('0.00')

            row += 1

        # Linha de totais
        worksheet.write(row, 4, 'TOTAL:', total_format)
        worksheet.write(row, 5, float(total_valor), total_format)
        worksheet.write(row, 6, float(total_premio_ba), total_format)
        worksheet.write(row, 7, float(total_premio_rr), total_format)

        # Ajustar larguras das colunas
        worksheet.set_column(0, 0, 12)  # Número
        worksheet.set_column(1, 1, 12)  # Tipo
        worksheet.set_column(2, 2, 8)   # Sócio
        worksheet.set_column(3, 3, 20)  # Cliente
        worksheet.set_column(4, 4, 40)  # Descrição
        worksheet.set_column(5, 7, 15)  # Valores
        worksheet.set_column(8, 8, 12)  # Estado
        worksheet.set_column(9, 11, 14) # Datas

        # Freeze panes
        worksheet.freeze_panes(6, 0)  # Congela cabeçalhos

        workbook.close()

        # Preparar response
        buffer.seek(0)
        filename = self._gerar_nome_arquivo(filtros, 'xlsx')

        response = HttpResponse(
            buffer.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="{filename}"'

        return response

    def _gerar_nome_arquivo(self, filtros: Optional[Dict[str, Any]], extensao: str) -> str:
        """
        Gera nome de arquivo baseado nos filtros aplicados

        Args:
            filtros: Dicionário com filtros aplicados
            extensao: Extensão do arquivo (pdf ou xlsx)

        Returns:
            Nome do arquivo
        """
        partes = ['projetos']

        if filtros:
            if filtros.get('socio'):
                partes.append(filtros['socio'])

            if filtros.get('estado'):
                partes.append(filtros['estado'].lower())

            if filtros.get('data_inicio') and filtros.get('data_fim'):
                data_inicio = filtros['data_inicio']
                data_fim = filtros['data_fim']

                if isinstance(data_inicio, str):
                    partes.append(data_inicio)
                else:
                    partes.append(data_inicio.strftime('%Y-%m'))

                if isinstance(data_fim, str):
                    partes.append(data_fim)
                else:
                    partes.append(data_fim.strftime('%Y-%m'))

        # Adicionar timestamp
        timestamp = self.today.strftime('%Y%m%d')
        partes.append(timestamp)

        return f"{'_'.join(partes)}.{extensao}"


# Funções auxiliares para facilitar o uso
def gerar_relatorio_projetos_pdf(projetos, filtros: Optional[Dict[str, Any]] = None) -> HttpResponse:
    """Atalho para gerar relatório PDF de projetos"""
    relatorio = RelatorioProjetos()
    return relatorio.gerar_pdf(projetos, filtros)


def gerar_relatorio_projetos_excel(projetos, filtros: Optional[Dict[str, Any]] = None) -> HttpResponse:
    """Atalho para gerar relatório Excel de projetos"""
    relatorio = RelatorioProjetos()
    return relatorio.gerar_excel(projetos, filtros)
