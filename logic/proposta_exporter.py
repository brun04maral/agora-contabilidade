# -*- coding: utf-8 -*-
"""
PropostaExporter - Exporta propostas (versão cliente) para PDF
"""
import os
from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Session
from database.models.orcamento import Orcamento, PropostaSecao, PropostaItem
from database.models.cliente import Cliente


class PropostaExporter:
    """
    Exportador de propostas para PDF
    """

    def __init__(self, db_session: Session):
        """
        Initialize exporter

        Args:
            db_session: SQLAlchemy database session
        """
        self.db = db_session

    def exportar_pdf(self, orcamento_id: int, filename: str):
        """
        Exporta proposta para PDF

        Args:
            orcamento_id: ID do orçamento
            filename: Nome do arquivo de saída
        """
        # Obter orçamento
        orcamento = self.db.query(Orcamento).filter(
            Orcamento.id == orcamento_id
        ).first()

        if not orcamento:
            raise ValueError(f"Orçamento com ID {orcamento_id} não encontrado")

        if not orcamento.tem_versao_cliente:
            raise ValueError("Este orçamento não tem versão para cliente")

        # Obter secções e itens da proposta
        proposta_secoes = self.db.query(PropostaSecao).filter(
            PropostaSecao.orcamento_id == orcamento_id
        ).order_by(PropostaSecao.ordem).all()

        if not proposta_secoes:
            raise ValueError("Nenhum item de proposta encontrado")

        # Gerar PDF
        self._gerar_pdf(orcamento, proposta_secoes, filename)

    def _gerar_pdf(self, orcamento: Orcamento, proposta_secoes: list, filename: str):
        """
        Gera PDF da proposta

        Args:
            orcamento: Orçamento
            proposta_secoes: Lista de secções da proposta
            filename: Nome do arquivo
        """
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.lib.units import cm
        from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.platypus import (
            SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
            PageBreak, Image
        )
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont

        # Create PDF
        doc = SimpleDocTemplate(
            filename,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )

        # Styles
        styles = getSampleStyleSheet()

        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1F6AA5'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )

        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#333333'),
            spaceAfter=12,
            alignment=TA_LEFT,
            fontName='Helvetica-Bold'
        )

        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontSize=11,
            textColor=colors.HexColor('#333333'),
            alignment=TA_JUSTIFY,
            spaceAfter=12
        )

        # Build document
        elements = []

        # Header with logo
        logo_path = os.path.join(os.path.dirname(__file__), "..", "media", "AGORA media production@0.5x.png")

        if os.path.exists(logo_path):
            logo_img = Image(logo_path, width=8*cm, height=2*cm, kind='proportional')
            elements.append(logo_img)
            elements.append(Spacer(1, 0.5*cm))
        else:
            # Fallback text logo
            company_name = Paragraph(
                "<font size='20' color='#1F6AA5'><b>AGORA</b></font> "
                "<font size='16'>media production</font>",
                normal_style
            )
            elements.append(company_name)
            elements.append(Spacer(1, 0.5*cm))

        # Linha separadora azul
        line_data = [['', '']]
        line_table = Table(line_data, colWidths=[17*cm])
        line_table.setStyle(TableStyle([
            ('LINEABOVE', (0, 0), (-1, 0), 2, colors.HexColor('#1F6AA5')),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ]))
        elements.append(line_table)
        elements.append(Spacer(1, 1*cm))

        # Título da proposta
        titulo = orcamento.titulo_cliente or "Proposta Comercial"
        elements.append(Paragraph(titulo, title_style))
        elements.append(Spacer(1, 0.5*cm))

        # Informações do cliente
        if orcamento.cliente:
            cliente_info = f"""
            <b>Cliente:</b> {orcamento.cliente.nome}<br/>
            <b>Código do Orçamento:</b> {orcamento.codigo}<br/>
            <b>Data:</b> {orcamento.data_criacao.strftime('%d/%m/%Y') if orcamento.data_criacao else 'N/A'}
            """

            if orcamento.data_evento:
                cliente_info += f"<br/><b>Data do Evento:</b> {orcamento.data_evento}"

            if orcamento.local_evento:
                cliente_info += f"<br/><b>Local:</b> {orcamento.local_evento}"

            elements.append(Paragraph(cliente_info, normal_style))
            elements.append(Spacer(1, 0.5*cm))

        # Descrição da proposta
        if orcamento.descricao_cliente:
            elements.append(Paragraph("<b>Descrição:</b>", subtitle_style))
            elements.append(Paragraph(orcamento.descricao_cliente, normal_style))
            elements.append(Spacer(1, 0.5*cm))

        # Itens por secção
        elements.append(Paragraph("<b>Itens da Proposta:</b>", subtitle_style))
        elements.append(Spacer(1, 0.3*cm))

        total_geral = 0

        for secao in proposta_secoes:
            # Header da secção
            secao_title = Paragraph(
                f"<b>{secao.nome}</b>",
                ParagraphStyle(
                    'SectionTitle',
                    parent=normal_style,
                    fontSize=12,
                    textColor=colors.HexColor('#1F6AA5'),
                    fontName='Helvetica-Bold'
                )
            )
            elements.append(secao_title)
            elements.append(Spacer(1, 0.2*cm))

            # Obter itens da secção
            itens = self.db.query(PropostaItem).filter(
                PropostaItem.secao_id == secao.id
            ).order_by(PropostaItem.ordem).all()

            if itens:
                # Tabela de itens
                table_data = [
                    ['Descrição', 'Qtd', 'Dias', 'Preço Unit.', 'Desconto', 'Total']
                ]

                for item in itens:
                    descricao = Paragraph(item.descricao, normal_style)
                    quantidade = str(item.quantidade)
                    dias = str(item.dias)
                    preco_unit = f"{float(item.preco_unitario):.2f}€"
                    desconto = f"{float(item.desconto)*100:.0f}%" if item.desconto > 0 else "-"
                    total = f"{float(item.total):.2f}€"

                    table_data.append([
                        descricao,
                        quantidade,
                        dias,
                        preco_unit,
                        desconto,
                        total
                    ])

                    total_geral += float(item.total)

                # Criar tabela
                col_widths = [7*cm, 1.5*cm, 1.5*cm, 2*cm, 2*cm, 3*cm]
                items_table = Table(table_data, colWidths=col_widths)

                items_table.setStyle(TableStyle([
                    # Header
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1F6AA5')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                    ('TOPPADDING', (0, 0), (-1, 0), 8),

                    # Body
                    ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                    ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                    ('ALIGN', (1, 1), (1, -1), 'CENTER'),  # Qtd
                    ('ALIGN', (2, 1), (2, -1), 'CENTER'),  # Dias
                    ('ALIGN', (3, 1), (3, -1), 'RIGHT'),   # Preço
                    ('ALIGN', (4, 1), (4, -1), 'CENTER'),  # Desconto
                    ('ALIGN', (5, 1), (5, -1), 'RIGHT'),   # Total
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 1), (-1, -1), 9),
                    ('VALIGN', (0, 1), (-1, -1), 'MIDDLE'),
                    ('LEFTPADDING', (0, 1), (-1, -1), 6),
                    ('RIGHTPADDING', (0, 1), (-1, -1), 6),
                    ('TOPPADDING', (0, 1), (-1, -1), 6),
                    ('BOTTOMPADDING', (0, 1), (-1, -1), 6),

                    # Grid
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')])
                ]))

                elements.append(items_table)
                elements.append(Spacer(1, 0.3*cm))

                # Subtotal da secção (se houver)
                if secao.subtotal:
                    subtotal_text = Paragraph(
                        f"<b>Subtotal {secao.nome}:</b> {float(secao.subtotal):.2f}€",
                        ParagraphStyle(
                            'Subtotal',
                            parent=normal_style,
                            fontSize=11,
                            alignment=TA_RIGHT,
                            textColor=colors.HexColor('#1F6AA5')
                        )
                    )
                    elements.append(subtotal_text)
                    elements.append(Spacer(1, 0.5*cm))

        # Total geral
        elements.append(Spacer(1, 0.5*cm))

        total_data = [
            ['TOTAL GERAL:', f"{total_geral:.2f}€"]
        ]
        total_table = Table(total_data, colWidths=[14*cm, 3*cm])
        total_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#4CAF50')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.whitesmoke),
            ('ALIGN', (0, 0), (0, 0), 'RIGHT'),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 14),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
            ('RIGHTPADDING', (0, 0), (-1, -1), 12),
        ]))
        elements.append(total_table)
        elements.append(Spacer(1, 1*cm))

        # Notas contratuais
        if orcamento.notas_contratuais:
            elements.append(Paragraph("<b>Notas:</b>", subtitle_style))
            elements.append(Paragraph(orcamento.notas_contratuais, normal_style))
            elements.append(Spacer(1, 0.5*cm))

        # Footer
        elements.append(Spacer(1, 1*cm))
        footer_text = f"""
        <para alignment="center">
        <font size="9" color="gray">
        Documento gerado em {datetime.now().strftime('%d/%m/%Y às %H:%M')}<br/>
        AGORA media production • www.agoramedia.pt
        </font>
        </para>
        """
        elements.append(Paragraph(footer_text, normal_style))

        # Build PDF
        doc.build(elements)
