# -*- coding: utf-8 -*-
"""
FiscalCalculator - Cálculos Fiscais para Agora Contabilidade

Calcula:
- IVA Trimestral (liquidado vs dedutível)
- IRS Retido Mensal (retenções na fonte)
- IRC Estimado Anual (imposto sobre lucros)

Baseado em FISCAL.md
"""
from decimal import Decimal
from datetime import date, datetime
from typing import Dict, List, Optional, Tuple
from django.db.models import Sum, Q
from core.models import Projeto, Despesa


class FiscalCalculator:
    """
    Calculator para obrigações fiscais da Agora Media
    """

    # ========================================================================
    # IVA TRIMESTRAL
    # ========================================================================

    @staticmethod
    def get_periodo_trimestre(ano: int, trimestre: int) -> Tuple[date, date]:
        """
        Retorna datas de início e fim de um trimestre

        Args:
            ano: Ano (ex: 2025)
            trimestre: 1, 2, 3 ou 4

        Returns:
            Tuple (data_inicio, data_fim)
        """
        if trimestre == 1:
            return date(ano, 1, 1), date(ano, 3, 31)
        elif trimestre == 2:
            return date(ano, 4, 1), date(ano, 6, 30)
        elif trimestre == 3:
            return date(ano, 7, 1), date(ano, 9, 30)
        elif trimestre == 4:
            return date(ano, 10, 1), date(ano, 12, 31)
        else:
            raise ValueError("Trimestre deve ser 1, 2, 3 ou 4")

    def calcular_iva_trimestral(
        self,
        ano: int,
        trimestre: int
    ) -> Dict:
        """
        Calcula IVA trimestral baseado em receitas (projetos PAGOS) e despesas PAGAS

        IVA a Pagar = IVA Liquidado (vendas) - IVA Dedutível (compras)

        Args:
            ano: Ano do trimestre
            trimestre: 1, 2, 3 ou 4

        Returns:
            Dict com estrutura:
            {
                'periodo': {'ano': 2025, 'trimestre': 1, 'inicio': date, 'fim': date},
                'iva_liquidado': {
                    'total': Decimal,
                    'projetos_count': int,
                    'projetos': [...]
                },
                'iva_dedutivel': {
                    'total': Decimal,
                    'despesas_count': int,
                    'despesas': [...]
                },
                'iva_a_pagar': Decimal,
                'prazo_declaracao': date,
                'prazo_pagamento': date
            }
        """
        inicio, fim = self.get_periodo_trimestre(ano, trimestre)

        # ======= IVA LIQUIDADO (Receitas/Projetos PAGOS) =======
        # Assumindo que projetos com estado=PAGO representam receitas recebidas
        # IVA = valor_sem_iva * 0.23 (taxa normal)

        projetos_pagos = Projeto.objects.filter(
            estado='PAGO',
            data_faturacao__gte=inicio,
            data_faturacao__lte=fim
        ).values('id', 'numero', 'descricao', 'valor_sem_iva', 'data_faturacao')

        iva_liquidado_total = Decimal('0')
        projetos_list = []

        for proj in projetos_pagos:
            valor_sem_iva = Decimal(str(proj['valor_sem_iva'] or 0))
            iva = valor_sem_iva * Decimal('0.23')
            iva_liquidado_total += iva

            projetos_list.append({
                'numero': proj['numero'],
                'descricao': proj['descricao'][:50],
                'valor_sem_iva': valor_sem_iva,
                'iva': iva,
                'data': proj['data_faturacao']
            })

        # ======= IVA DEDUTÍVEL (Despesas PAGAS) =======
        # IVA dedutível = valor_com_iva - valor_sem_iva

        despesas_pagas = Despesa.objects.filter(
            estado='PAGO',
            data_pagamento__gte=inicio,
            data_pagamento__lte=fim
        ).values('id', 'numero', 'descricao', 'valor_sem_iva', 'valor_com_iva', 'data_pagamento')

        iva_dedutivel_total = Decimal('0')
        despesas_list = []

        for desp in despesas_pagas:
            valor_sem_iva = Decimal(str(desp['valor_sem_iva'] or 0))
            valor_com_iva = Decimal(str(desp['valor_com_iva'] or 0))
            iva = valor_com_iva - valor_sem_iva

            if iva > 0:  # Só conta se tiver IVA
                iva_dedutivel_total += iva
                despesas_list.append({
                    'numero': desp['numero'],
                    'descricao': desp['descricao'][:50],
                    'valor_sem_iva': valor_sem_iva,
                    'iva': iva,
                    'data': desp['data_pagamento']
                })

        # ======= APURAMENTO =======
        iva_a_pagar = iva_liquidado_total - iva_dedutivel_total

        # ======= PRAZOS =======
        # Declaração: dia 20 do 2º mês seguinte
        # Pagamento: dia 25 do 2º mês seguinte
        if trimestre == 1:
            prazo_decl = date(ano, 5, 20)
            prazo_pag = date(ano, 5, 25)
        elif trimestre == 2:
            prazo_decl = date(ano, 8, 20)
            prazo_pag = date(ano, 8, 25)
        elif trimestre == 3:
            prazo_decl = date(ano, 11, 20)
            prazo_pag = date(ano, 11, 25)
        else:  # Q4
            prazo_decl = date(ano + 1, 2, 20)
            prazo_pag = date(ano + 1, 2, 25)

        return {
            'periodo': {
                'ano': ano,
                'trimestre': trimestre,
                'inicio': inicio,
                'fim': fim
            },
            'iva_liquidado': {
                'total': iva_liquidado_total,
                'projetos_count': len(projetos_list),
                'projetos': projetos_list
            },
            'iva_dedutivel': {
                'total': iva_dedutivel_total,
                'despesas_count': len(despesas_list),
                'despesas': despesas_list
            },
            'iva_a_pagar': iva_a_pagar,
            'prazo_declaracao': prazo_decl,
            'prazo_pagamento': prazo_pag
        }

    # ========================================================================
    # IRS RETIDO MENSAL
    # ========================================================================

    def calcular_irs_mensal(
        self,
        ano: int,
        mes: int
    ) -> Dict:
        """
        Calcula IRS retido na fonte em pagamentos a freelancers no mês

        Obrigação MENSAL:
        - Declaração: até dia 20 do mês seguinte
        - Pagamento: até dia 25 do mês seguinte

        Args:
            ano: Ano (ex: 2025)
            mes: Mês (1-12)

        Returns:
            Dict com estrutura:
            {
                'periodo': {'ano': 2025, 'mes': 3, 'mes_nome': 'Março'},
                'total_retido': Decimal,
                'despesas_count': int,
                'despesas': [...],
                'prazo_declaracao': date,
                'prazo_pagamento': date
            }
        """
        # Período do mês
        inicio = date(ano, mes, 1)
        if mes == 12:
            fim = date(ano, 12, 31)
        else:
            from calendar import monthrange
            _, ultimo_dia = monthrange(ano, mes)
            fim = date(ano, mes, ultimo_dia)

        # Buscar despesas PAGAS no mês com IRS retido
        despesas = Despesa.objects.filter(
            data_pagamento__gte=inicio,
            data_pagamento__lte=fim,
            estado='PAGO',
            irs_retido__gt=0
        ).select_related('credor').values(
            'id', 'numero', 'descricao', 'credor__nome',
            'valor_sem_iva', 'irs_retido', 'taxa_retencao_irs', 'data_pagamento'
        )

        total_retido = Decimal('0')
        despesas_list = []

        for desp in despesas:
            irs = Decimal(str(desp['irs_retido'] or 0))
            total_retido += irs

            despesas_list.append({
                'numero': desp['numero'],
                'fornecedor': desp['credor__nome'] or 'N/A',
                'descricao': desp['descricao'][:50],
                'valor_base': Decimal(str(desp['valor_sem_iva'] or 0)),
                'taxa': Decimal(str(desp['taxa_retencao_irs'] or 0)),
                'irs_retido': irs,
                'data': desp['data_pagamento']
            })

        # Prazos
        if mes == 12:
            prazo_decl = date(ano + 1, 1, 20)
            prazo_pag = date(ano + 1, 1, 25)
        else:
            prazo_decl = date(ano, mes + 1, 20)
            prazo_pag = date(ano, mes + 1, 25)

        meses_nome = [
            'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
            'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
        ]

        return {
            'periodo': {
                'ano': ano,
                'mes': mes,
                'mes_nome': meses_nome[mes - 1]
            },
            'total_retido': total_retido,
            'despesas_count': len(despesas_list),
            'despesas': despesas_list,
            'prazo_declaracao': prazo_decl,
            'prazo_pagamento': prazo_pag
        }

    # ========================================================================
    # IRC ESTIMADO ANUAL
    # ========================================================================

    def estimar_irc_anual(
        self,
        ano: int
    ) -> Dict:
        """
        Estima IRC anual baseado em receitas e despesas

        IRC = Lucro × Taxa
        Lucro = Receitas - Despesas

        Taxa PME:
        - 16% sobre primeiros €50.000
        - 20% sobre excedente

        Args:
            ano: Ano fiscal

        Returns:
            Dict com estrutura:
            {
                'ano': 2025,
                'receitas_total': Decimal,
                'despesas_total': Decimal,
                'lucro_tributavel': Decimal,
                'irc_16': Decimal (primeiros 50k),
                'irc_20': Decimal (excedente),
                'irc_total': Decimal,
                'prazo_declaracao': date,
                'prazo_pagamento': date
            }
        """
        inicio = date(ano, 1, 1)
        fim = date(ano, 12, 31)

        # Receitas = Projetos PAGOS no ano
        receitas_agg = Projeto.objects.filter(
            estado='PAGO',
            data_faturacao__gte=inicio,
            data_faturacao__lte=fim
        ).aggregate(total=Sum('valor_sem_iva'))

        receitas_total = Decimal(str(receitas_agg['total'] or 0))

        # Despesas = Despesas PAGAS no ano
        despesas_agg = Despesa.objects.filter(
            estado='PAGO',
            data_pagamento__gte=inicio,
            data_pagamento__lte=fim
        ).aggregate(total=Sum('valor_sem_iva'))

        despesas_total = Decimal(str(despesas_agg['total'] or 0))

        # Lucro tributável (simplificado - TOC faz correções fiscais)
        lucro = receitas_total - despesas_total

        # Cálculo IRC
        if lucro <= 0:
            irc_16 = Decimal('0')
            irc_20 = Decimal('0')
            irc_total = Decimal('0')
        elif lucro <= Decimal('50000'):
            irc_16 = lucro * Decimal('0.16')
            irc_20 = Decimal('0')
            irc_total = irc_16
        else:
            irc_16 = Decimal('50000') * Decimal('0.16')
            irc_20 = (lucro - Decimal('50000')) * Decimal('0.20')
            irc_total = irc_16 + irc_20

        return {
            'ano': ano,
            'receitas_total': receitas_total,
            'despesas_total': despesas_total,
            'lucro_tributavel': lucro,
            'irc_16': irc_16,
            'irc_20': irc_20,
            'irc_total': irc_total,
            'prazo_declaracao': date(ano + 1, 5, 31),
            'prazo_pagamento': date(ano + 1, 8, 31)
        }

    # ========================================================================
    # HELPER: Próximas Obrigações
    # ========================================================================

    def proximas_obrigacoes(self) -> List[Dict]:
        """
        Retorna lista de próximas obrigações fiscais ordenadas por data

        Returns:
            List[Dict] com estrutura:
            [
                {'tipo': 'IVA Q1', 'descricao': 'Declaração IVA', 'prazo': date, 'dias_restantes': int},
                ...
            ]
        """
        hoje = date.today()
        ano = hoje.year
        mes = hoje.month
        trimestre = (mes - 1) // 3 + 1

        obrigacoes = []

        # IVA Trimestre atual
        iva = self.calcular_iva_trimestral(ano, trimestre)
        obrigacoes.append({
            'tipo': f'IVA Q{trimestre}/{ano}',
            'descricao': 'Declaração Periódica IVA',
            'prazo': iva['prazo_declaracao'],
            'dias_restantes': (iva['prazo_declaracao'] - hoje).days
        })
        obrigacoes.append({
            'tipo': f'IVA Q{trimestre}/{ano}',
            'descricao': 'Pagamento IVA',
            'prazo': iva['prazo_pagamento'],
            'dias_restantes': (iva['prazo_pagamento'] - hoje).days
        })

        # IRS Mês atual
        irs = self.calcular_irs_mensal(ano, mes)
        if irs['total_retido'] > 0:
            obrigacoes.append({
                'tipo': f'IRS {irs["periodo"]["mes_nome"]}/{ano}',
                'descricao': 'Declaração IRS Retido',
                'prazo': irs['prazo_declaracao'],
                'dias_restantes': (irs['prazo_declaracao'] - hoje).days
            })
            obrigacoes.append({
                'tipo': f'IRS {irs["periodo"]["mes_nome"]}/{ano}',
                'descricao': 'Pagamento IRS Retido',
                'prazo': irs['prazo_pagamento'],
                'dias_restantes': (irs['prazo_pagamento'] - hoje).days
            })

        # IRC Anual
        irc = self.estimar_irc_anual(ano - 1)  # Ano anterior
        obrigacoes.append({
            'tipo': f'IRC {ano - 1}',
            'descricao': 'Declaração Modelo 22',
            'prazo': irc['prazo_declaracao'],
            'dias_restantes': (irc['prazo_declaracao'] - hoje).days
        })

        # Ordenar por prazo
        obrigacoes.sort(key=lambda x: x['prazo'])

        # Filtrar apenas futuras ou hoje
        return [o for o in obrigacoes if o['dias_restantes'] >= 0]
