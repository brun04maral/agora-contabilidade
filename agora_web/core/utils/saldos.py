# -*- coding: utf-8 -*-
"""
Lógica de cálculo de Saldos Pessoais - MÓDULO CORE DO SISTEMA (Django ORM)

Este é o módulo mais importante da aplicação!
Calcula os saldos pessoais de cada sócio com base em:

INs (Entradas - empresa DEVE ao sócio):
  - Projetos pessoais faturados pela empresa
  - Prémios recebidos de projetos da empresa (cachets + comissões)
  - Investimento inicial (histórico)

OUTs (Saídas - empresa PAGA ao sócio):
  - Despesas fixas mensais ÷ 2 (cada sócio paga metade)
  - Boletins emitidos (ajudas de custo)
  - Despesas pessoais excecionais

Saldo = INs - OUTs
"""
from decimal import Decimal
from typing import Dict, List, Optional
from datetime import date, timedelta
from django.db.models import Sum, Q

from core.models import (
    Projeto, TipoProjeto, EstadoProjeto,
    Despesa, TipoDespesa, EstadoDespesa,
    Boletim, Socio, EstadoBoletim
)


class SaldosCalculator:
    """
    Calcula os saldos pessoais dos sócios usando Django ORM
    """

    # Investimento inicial de cada sócio (referência histórica)
    INVESTIMENTO_INICIAL_BRUNO = Decimal("5200.00")
    INVESTIMENTO_INICIAL_RAFAEL = Decimal("5200.00")

    def calcular_saldo_bruno(
        self,
        incluir_investimento: bool = False,
        data_inicio: Optional[date] = None,
        data_fim: Optional[date] = None
    ) -> Dict:
        """
        Calcula o saldo pessoal do Bruno

        Args:
            incluir_investimento: Se deve incluir o investimento inicial nos INs
            data_inicio: Data de início para filtrar (opcional)
            data_fim: Data de fim para filtrar (opcional)

        Returns:
            Dict com breakdown completo do saldo
        """
        return self._calcular_saldo(
            Socio.BA,
            incluir_investimento,
            data_inicio,
            data_fim
        )

    def calcular_saldo_rafael(
        self,
        incluir_investimento: bool = False,
        data_inicio: Optional[date] = None,
        data_fim: Optional[date] = None
    ) -> Dict:
        """
        Calcula o saldo pessoal do Rafael

        Args:
            incluir_investimento: Se deve incluir o investimento inicial nos INs
            data_inicio: Data de início para filtrar (opcional)
            data_fim: Data de fim para filtrar (opcional)

        Returns:
            Dict com breakdown completo do saldo
        """
        return self._calcular_saldo(
            Socio.RR,
            incluir_investimento,
            data_inicio,
            data_fim
        )

    def _calcular_saldo(
        self,
        socio: str,  # 'BA' ou 'RR'
        incluir_investimento: bool = False,
        data_inicio: Optional[date] = None,
        data_fim: Optional[date] = None
    ) -> Dict:
        """
        Calcula o saldo pessoal de um sócio

        Args:
            socio: Sócio ('BA' ou 'RR')
            incluir_investimento: Se deve incluir o investimento inicial
            data_inicio: Data de início para filtrar
            data_fim: Data de fim para filtrar

        Returns:
            Dict com breakdown completo do saldo
        """
        # Determinar owner e tipo de despesa pessoal
        owner = socio
        tipo_despesa = TipoDespesa.PESSOAL_BA if socio == Socio.BA else TipoDespesa.PESSOAL_RR

        # === CALCULAR INs (Entradas) ===

        # 1. Projetos pessoais (apenas PAGOS)
        query_projetos_pessoais = Projeto.objects.filter(
            tipo=TipoProjeto.PESSOAL,
            owner=owner,
            estado=EstadoProjeto.PAGO
        )

        if data_inicio:
            query_projetos_pessoais = query_projetos_pessoais.filter(
                data_faturacao__gte=data_inicio
            )
        if data_fim:
            query_projetos_pessoais = query_projetos_pessoais.filter(
                data_faturacao__lte=data_fim
            )

        projetos_pessoais = query_projetos_pessoais.aggregate(
            total=Sum('valor_sem_iva')
        )['total'] or Decimal("0.00")

        # 2. Prémios de projetos da empresa (apenas PAGOS)
        if socio == Socio.BA:
            query_premios = Projeto.objects.filter(
                premio_bruno__gt=0,
                estado=EstadoProjeto.PAGO
            )
            campo_premio = 'premio_bruno'
        else:
            query_premios = Projeto.objects.filter(
                premio_rafael__gt=0,
                estado=EstadoProjeto.PAGO
            )
            campo_premio = 'premio_rafael'

        if data_inicio:
            query_premios = query_premios.filter(
                data_faturacao__gte=data_inicio
            )
        if data_fim:
            query_premios = query_premios.filter(
                data_faturacao__lte=data_fim
            )

        premios = query_premios.aggregate(
            total=Sum(campo_premio)
        )['total'] or Decimal("0.00")

        # 3. Investimento inicial (se solicitado)
        investimento = Decimal("0.00")
        if incluir_investimento:
            investimento = (
                self.INVESTIMENTO_INICIAL_BRUNO if socio == Socio.BA
                else self.INVESTIMENTO_INICIAL_RAFAEL
            )

        total_ins = projetos_pessoais + premios + investimento

        # === CALCULAR OUTs (Saídas) ===

        # 1. Despesas fixas mensais (divididas por 2)
        query_despesas_fixas = Despesa.objects.filter(
            tipo=TipoDespesa.FIXA_MENSAL,
            estado=EstadoDespesa.PAGO
        )

        if data_inicio:
            query_despesas_fixas = query_despesas_fixas.filter(
                data__gte=data_inicio
            )
        if data_fim:
            query_despesas_fixas = query_despesas_fixas.filter(
                data__lte=data_fim
            )

        despesas_fixas_total = query_despesas_fixas.aggregate(
            total=Sum('valor_sem_iva')
        )['total'] or Decimal("0.00")
        despesas_fixas = despesas_fixas_total / Decimal("2.00")  # Divide por 2

        # 2. Boletins PENDENTES (emitidos mas não pagos)
        query_boletins_pendentes = Boletim.objects.filter(
            socio=socio,
            estado=EstadoBoletim.PENDENTE
        )

        if data_inicio:
            query_boletins_pendentes = query_boletins_pendentes.filter(
                data_emissao__gte=data_inicio
            )
        if data_fim:
            query_boletins_pendentes = query_boletins_pendentes.filter(
                data_emissao__lte=data_fim
            )

        # Usar valor_total se existir, senão usar valor (compatibilidade)
        boletins_pendentes = Decimal("0.00")
        for b in query_boletins_pendentes:
            boletins_pendentes += b.valor_total if b.valor_total else (b.valor or Decimal("0.00"))

        # 3. Boletins PAGOS
        query_boletins_pagos = Boletim.objects.filter(
            socio=socio,
            estado=EstadoBoletim.PAGO
        )

        if data_inicio:
            query_boletins_pagos = query_boletins_pagos.filter(
                data_emissao__gte=data_inicio
            )
        if data_fim:
            query_boletins_pagos = query_boletins_pagos.filter(
                data_emissao__lte=data_fim
            )

        boletins_pagos = Decimal("0.00")
        for b in query_boletins_pagos:
            boletins_pagos += b.valor_total if b.valor_total else (b.valor or Decimal("0.00"))

        boletins_total = boletins_pendentes + boletins_pagos

        # 4. Despesas pessoais excecionais
        query_despesas_pessoais = Despesa.objects.filter(
            tipo=tipo_despesa,
            estado=EstadoDespesa.PAGO
        )

        if data_inicio:
            query_despesas_pessoais = query_despesas_pessoais.filter(
                data__gte=data_inicio
            )
        if data_fim:
            query_despesas_pessoais = query_despesas_pessoais.filter(
                data__lte=data_fim
            )

        despesas_pessoais = query_despesas_pessoais.aggregate(
            total=Sum('valor_sem_iva')
        )['total'] or Decimal("0.00")

        # IMPORTANTE: Apenas boletins PAGOS entram no cálculo do saldo!
        total_outs = despesas_fixas + boletins_pagos + despesas_pessoais

        # === CALCULAR SALDO FINAL ===
        saldo_total = total_ins - total_outs

        # === PRÉMIOS NÃO FATURADOS (Projetos FINALIZADOS) ===
        if socio == Socio.BA:
            query_premios_nao_faturados = Projeto.objects.filter(
                estado=EstadoProjeto.FINALIZADO,
                premio_bruno__gt=0
            )
            campo_premio_nf = 'premio_bruno'
        else:
            query_premios_nao_faturados = Projeto.objects.filter(
                estado=EstadoProjeto.FINALIZADO,
                premio_rafael__gt=0
            )
            campo_premio_nf = 'premio_rafael'

        if data_inicio:
            query_premios_nao_faturados = query_premios_nao_faturados.filter(
                data_faturacao__gte=data_inicio
            )
        if data_fim:
            query_premios_nao_faturados = query_premios_nao_faturados.filter(
                data_faturacao__lte=data_fim
            )

        premios_nao_faturados = query_premios_nao_faturados.aggregate(
            total=Sum(campo_premio_nf)
        )['total'] or Decimal("0.00")

        # === PROJETOS PESSOAIS NÃO FATURADOS ===
        query_pessoais_nao_faturados = Projeto.objects.filter(
            estado=EstadoProjeto.FINALIZADO,
            tipo=TipoProjeto.PESSOAL,
            owner=owner
        )

        if data_inicio:
            query_pessoais_nao_faturados = query_pessoais_nao_faturados.filter(
                data_faturacao__gte=data_inicio
            )
        if data_fim:
            query_pessoais_nao_faturados = query_pessoais_nao_faturados.filter(
                data_faturacao__lte=data_fim
            )

        pessoais_nao_faturados = query_pessoais_nao_faturados.aggregate(
            total=Sum('valor_sem_iva')
        )['total'] or Decimal("0.00")

        # Saldo projetado
        saldo_projetado = None
        total_nao_faturados = premios_nao_faturados + pessoais_nao_faturados
        if total_nao_faturados > 0:
            saldo_projetado = float(saldo_total + total_nao_faturados)

        # === CALCULAR SUGESTÃO DE BOLETIM ===
        hoje = date.today()
        mes_atual = hoje.month
        ano_atual = hoje.year

        # Meses que já têm boletim emitido
        meses_com_boletim = set(
            Boletim.objects.filter(
                socio=socio,
                ano=ano_atual
            ).values_list('mes', flat=True)
        )

        # Meses restantes sem boletim
        meses_restantes = [m for m in range(mes_atual, 13) if m not in meses_com_boletim]
        num_meses_sem_boletim = len(meses_restantes)

        # Calcular saldo projetado para sugestão
        total_ins_projetado = total_ins + premios_nao_faturados + pessoais_nao_faturados
        total_outs_projetado = total_outs + boletins_pendentes
        saldo_projetado_calc = total_ins_projetado - total_outs_projetado

        # Sugestão = saldo projetado / meses restantes
        if num_meses_sem_boletim > 0:
            sugestao_boletim = max(0, float(saldo_projetado_calc / num_meses_sem_boletim))
        else:
            sugestao_boletim = 0.0

        return {
            'socio': socio,
            'saldo_total': float(saldo_total),
            'saldo_projetado': saldo_projetado,
            'ins': {
                'projetos_pessoais': float(projetos_pessoais),
                'premios': float(premios),
                'premios_nao_faturados': float(premios_nao_faturados),
                'pessoais_nao_faturados': float(pessoais_nao_faturados),
                'investimento_inicial': float(investimento),
                'total': float(total_ins)
            },
            'outs': {
                'despesas_fixas': float(despesas_fixas),
                'boletins_pendentes': float(boletins_pendentes),
                'boletins_pagos': float(boletins_pagos),
                'boletins_total': float(boletins_total),
                'despesas_pessoais': float(despesas_pessoais),
                'total': float(total_outs)
            },
            'sugestao_boletim': sugestao_boletim
        }

    def obter_historico_mensal(
        self,
        socio: str,
        ano: int,
        incluir_investimento: bool = False
    ) -> List[Dict]:
        """
        Obtém histórico mensal de saldos para um ano específico

        Args:
            socio: Sócio ('BA' ou 'RR')
            ano: Ano para obter histórico
            incluir_investimento: Se deve incluir investimento inicial

        Returns:
            Lista de dicts com saldos mensais
        """
        meses = [
            'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
            'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
        ]

        historico = []
        for mes in range(1, 13):
            # Calcular até o fim do mês
            if mes == 12:
                data_fim = date(ano, 12, 31)
            else:
                data_fim = date(ano, mes + 1, 1) - timedelta(days=1)

            saldo_data = self._calcular_saldo(
                socio,
                incluir_investimento=incluir_investimento,
                data_fim=data_fim
            )

            historico.append({
                'mes': mes,
                'mes_nome': meses[mes - 1],
                'saldo': saldo_data['saldo_total']
            })

        return historico

    def obter_breakdown_detalhado(self, socio: str) -> Dict:
        """
        Obtém breakdown detalhado com listas de itens específicos

        Args:
            socio: Sócio ('BA' ou 'RR')

        Returns:
            Dict com listas detalhadas de projetos, despesas e boletins
        """
        owner = socio
        tipo_despesa = TipoDespesa.PESSOAL_BA if socio == Socio.BA else TipoDespesa.PESSOAL_RR

        # Projetos pessoais
        projetos_pessoais = Projeto.objects.filter(
            tipo=TipoProjeto.PESSOAL,
            owner=owner,
            estado=EstadoProjeto.PAGO
        )

        # Projetos com prémios (apenas PAGOS)
        if socio == Socio.BA:
            projetos_premios = Projeto.objects.filter(
                premio_bruno__gt=0,
                estado=EstadoProjeto.PAGO
            )
        else:
            projetos_premios = Projeto.objects.filter(
                premio_rafael__gt=0,
                estado=EstadoProjeto.PAGO
            )

        # Despesas fixas
        despesas_fixas = Despesa.objects.filter(
            tipo=TipoDespesa.FIXA_MENSAL,
            estado=EstadoDespesa.PAGO
        )

        # Despesas pessoais
        despesas_pessoais = Despesa.objects.filter(
            tipo=tipo_despesa,
            estado=EstadoDespesa.PAGO
        )

        # Boletins (apenas PAGOS)
        boletins = Boletim.objects.filter(
            socio=socio,
            estado=EstadoBoletim.PAGO
        )

        # Converter para dicts (similar ao to_dict() do SQLAlchemy)
        return {
            'projetos_pessoais': list(projetos_pessoais.values()),
            'projetos_premios': list(projetos_premios.values()),
            'despesas_fixas': list(despesas_fixas.values()),
            'despesas_pessoais': list(despesas_pessoais.values()),
            'boletins': list(boletins.values())
        }
