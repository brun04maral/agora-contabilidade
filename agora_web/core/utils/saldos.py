# -*- coding: utf-8 -*-
"""
Lógica de cálculo de Saldos Pessoais - MÓDULO CORE DO SISTEMA (Django ORM)

Empresa: Amaral & Reigota - Produção Audiovisual, Lda (NIPC: 518 351 190)
Marca: Agora Media Production

Este é o módulo mais importante da aplicação!
Calcula os saldos pessoais de cada sócio com base em:

SALDO ATUAL (Real):
  INs (Entradas - empresa DEVE ao sócio):
    - Projetos pessoais com data_recibo (cliente JÁ PAGOU)
    - Prémios de projetos com data_fim < hoje (trabalho JÁ FEITO)

  OUTs (Saídas - empresa PAGOU ao sócio):
    - Despesas fixas mensais ÷ 2 (cada sócio paga metade)
    - Boletins com estado=PAGO (já foram pagos ao sócio)
    - Despesas pessoais pagas

SALDO PROJETADO (Futuro):
  INs:
    - Projetos pessoais com data_recibo (cliente JÁ PAGOU)
    - Prémios de TODOS os projetos (incluindo futuros agendados)

  OUTs:
    - Despesas fixas mensais ÷ 2
    - Boletins TODOS (PAGO + PENDENTE) - já foram declarados às finanças
    - Despesas pessoais todas

Saldo Atual = INs (trabalho feito) - OUTs (pagos)
Saldo Projetado = INs (incluindo futuros) - OUTs (incluindo pendentes)

Nota: Investimento inicial está documentado mas NÃO conta no cálculo do saldo.
      É apenas informação de referência histórica.
"""
from decimal import Decimal
from typing import Dict, List, Optional
from datetime import date, timedelta
from django.db.models import Sum, Q

from core.models import (
    Projeto, TipoProjeto, EstadoProjeto,
    Despesa, Boletim, Socio, EstadoBoletim
)


class SaldosCalculator:
    """
    Calcula os saldos pessoais dos sócios usando Django ORM

    Retorna sempre dois valores:
    - saldo_atual: Baseado apenas em trabalho feito e pagamentos efetuados
    - saldo_projetado: Incluindo trabalho futuro e obrigações fiscais pendentes
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
            'BA',
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
            'RR',
            incluir_investimento,
            data_inicio,
            data_fim
        )

    def _calcular_saldo(
        self,
        socio_codigo: str,  # 'BA' ou 'RR'
        incluir_investimento: bool = False,
        data_inicio: Optional[date] = None,
        data_fim_param: Optional[date] = None
    ) -> Dict:
        """
        Calcula o saldo pessoal de um sócio

        Args:
            socio_codigo: Sócio ('BA' ou 'RR')
            incluir_investimento: Se deve incluir o investimento inicial
            data_inicio: Data de início para filtrar
            data_fim_param: Data de fim para filtrar

        Returns:
            Dict com breakdown completo do saldo
        """
        hoje = date.today()

        # === CALCULAR INs SALDO ATUAL (trabalho feito) ===

        # 1. Projetos pessoais PAGOS (cliente já pagou)
        query_projetos_pagos = Projeto.objects.filter(
            tipo=TipoProjeto.PESSOAL,
            socio__codigo=socio_codigo,
            data_recibo__isnull=False  # Cliente já pagou
        )

        if data_inicio:
            query_projetos_pagos = query_projetos_pagos.filter(
                data_recibo__gte=data_inicio
            )
        if data_fim_param:
            query_projetos_pagos = query_projetos_pagos.filter(
                data_recibo__lte=data_fim_param
            )

        projetos_pessoais_pagos = query_projetos_pagos.aggregate(
            total=Sum('valor_sem_iva')
        )['total'] or Decimal("0.00")

        # 2. Prémios de projetos FINALIZADOS (data_fim < hoje, trabalho feito)
        campo_premio = 'premio_bruno' if socio_codigo == 'BA' else 'premio_rafael'

        query_premios_feitos = Projeto.objects.filter(
            **{f'{campo_premio}__gt': 0},
            data_fim__lt=hoje  # Trabalho já aconteceu
        )

        if data_inicio:
            query_premios_feitos = query_premios_feitos.filter(
                data_fim__gte=data_inicio
            )
        if data_fim_param:
            query_premios_feitos = query_premios_feitos.filter(
                data_fim__lte=data_fim_param
            )

        premios_feitos = query_premios_feitos.aggregate(
            total=Sum(campo_premio)
        )['total'] or Decimal("0.00")

        # 3. Investimento inicial (se solicitado)
        investimento = Decimal("0.00")
        if incluir_investimento:
            investimento = (
                self.INVESTIMENTO_INICIAL_BRUNO if socio_codigo == 'BA'
                else self.INVESTIMENTO_INICIAL_RAFAEL
            )

        total_ins_atual = projetos_pessoais_pagos + premios_feitos + investimento

        # === CALCULAR INs SALDO PROJETADO (incluindo futuros) ===

        # 4. Prémios de TODOS os projetos (incluindo futuros)
        query_premios_todos = Projeto.objects.filter(
            **{f'{campo_premio}__gt': 0}
        )

        if data_inicio:
            query_premios_todos = query_premios_todos.filter(
                data_fim__gte=data_inicio
            )
        if data_fim_param:
            query_premios_todos = query_premios_todos.filter(
                data_fim__lte=data_fim_param
            )

        premios_todos = query_premios_todos.aggregate(
            total=Sum(campo_premio)
        )['total'] or Decimal("0.00")

        total_ins_projetado = projetos_pessoais_pagos + premios_todos + investimento

        # === CALCULAR OUTs SALDO ATUAL (apenas pagos) ===

        # 5. Despesas fixas mensais (divididas por 2) - só as com tag ADMINISTRATIVO, ORDENADO, SUB_ALIMENTACAO
        from core.models import TagDespesa

        query_despesas_fixas = Despesa.objects.filter(
            tags__codigo__in=['ADMINISTRATIVO', 'ORDENADO', 'SUB_ALIMENTACAO']
        ).distinct()

        if data_inicio:
            query_despesas_fixas = query_despesas_fixas.filter(
                ano__gte=data_inicio.year
            )
        if data_fim_param:
            query_despesas_fixas = query_despesas_fixas.filter(
                ano__lte=data_fim_param.year
            )

        despesas_fixas_total = query_despesas_fixas.aggregate(
            total=Sum('valor_sem_iva')
        )['total'] or Decimal("0.00")
        despesas_fixas = despesas_fixas_total / Decimal("2.00")  # Divide por 2

        # 6. Boletins PAGOS
        query_boletins_pagos = Boletim.objects.filter(
            socio__codigo=socio_codigo,
            estado=EstadoBoletim.PAGO
        )

        if data_inicio:
            query_boletins_pagos = query_boletins_pagos.filter(
                data_emissao__gte=data_inicio
            )
        if data_fim_param:
            query_boletins_pagos = query_boletins_pagos.filter(
                data_emissao__lte=data_fim_param
            )

        boletins_pagos = query_boletins_pagos.aggregate(
            total=Sum('valor_total')
        )['total'] or Decimal("0.00")

        # 7. Despesas pessoais - só as com tag PESSOAL do sócio
        query_despesas_pessoais = Despesa.objects.filter(
            tags__codigo='PESSOAL'
        ).distinct()

        # Filtrar por credor (nome do sócio)
        socio_obj = Socio.objects.get(codigo=socio_codigo)
        query_despesas_pessoais = query_despesas_pessoais.filter(
            credor__nome__icontains=socio_obj.nome_completo.split()[0]  # "Bruno" ou "Rafael"
        )

        if data_inicio:
            query_despesas_pessoais = query_despesas_pessoais.filter(
                ano__gte=data_inicio.year
            )
        if data_fim_param:
            query_despesas_pessoais = query_despesas_pessoais.filter(
                ano__lte=data_fim_param.year
            )

        despesas_pessoais = query_despesas_pessoais.aggregate(
            total=Sum('valor_sem_iva')
        )['total'] or Decimal("0.00")

        total_outs_atual = despesas_fixas + boletins_pagos + despesas_pessoais

        # === CALCULAR OUTs SALDO PROJETADO (incluindo pendentes) ===

        # 8. Boletins TODOS (PAGO + PENDENTE) - já foram declarados
        query_boletins_todos = Boletim.objects.filter(
            socio__codigo=socio_codigo
        )

        if data_inicio:
            query_boletins_todos = query_boletins_todos.filter(
                data_emissao__gte=data_inicio
            )
        if data_fim_param:
            query_boletins_todos = query_boletins_todos.filter(
                data_emissao__lte=data_fim_param
            )

        boletins_todos = query_boletins_todos.aggregate(
            total=Sum('valor_total')
        )['total'] or Decimal("0.00")

        boletins_pendentes = boletins_todos - boletins_pagos

        total_outs_projetado = despesas_fixas + boletins_todos + despesas_pessoais

        # === CALCULAR SALDOS FINAIS ===
        saldo_atual = total_ins_atual - total_outs_atual
        saldo_projetado = total_ins_projetado - total_outs_projetado

        # === CALCULAR SUGESTÃO DE BOLETIM (baseada no saldo projetado) ===
        mes_atual = hoje.month
        ano_atual = hoje.year

        # Meses que já têm boletim emitido
        meses_com_boletim = set(
            Boletim.objects.filter(
                socio__codigo=socio_codigo,
                ano=ano_atual
            ).values_list('mes', flat=True)
        )

        # Meses restantes sem boletim
        meses_restantes = [m for m in range(mes_atual, 13) if m not in meses_com_boletim]
        num_meses_sem_boletim = len(meses_restantes)

        # Sugestão = saldo projetado / meses restantes
        if num_meses_sem_boletim > 0:
            sugestao_boletim = max(0, float(saldo_projetado / num_meses_sem_boletim))
        else:
            sugestao_boletim = 0.0

        # Breakdown detalhado de prémios
        premios_futuros = premios_todos - premios_feitos

        return {
            'socio': socio_codigo,
            'saldo_atual': float(saldo_atual),
            'saldo_projetado': float(saldo_projetado),
            'ins': {
                'projetos_pessoais_pagos': float(projetos_pessoais_pagos),
                'premios_trabalho_feito': float(premios_feitos),
                'premios_trabalho_futuro': float(premios_futuros),
                'premios_total': float(premios_todos),
                'investimento_inicial': float(investimento),
                'total_atual': float(total_ins_atual),
                'total_projetado': float(total_ins_projetado)
            },
            'outs': {
                'despesas_fixas': float(despesas_fixas),
                'boletins_pagos': float(boletins_pagos),
                'boletins_pendentes': float(boletins_pendentes),
                'boletins_total': float(boletins_todos),
                'despesas_pessoais': float(despesas_pessoais),
                'total_atual': float(total_outs_atual),
                'total_projetado': float(total_outs_projetado)
            },
            'sugestao_boletim': sugestao_boletim
        }

    def obter_breakdown_detalhado(self, socio_codigo: str) -> Dict:
        """
        Obtém breakdown detalhado com listas de itens específicos

        Args:
            socio_codigo: Sócio ('BA' ou 'RR')

        Returns:
            Dict com listas detalhadas de projetos, despesas e boletins
        """
        hoje = date.today()
        campo_premio = 'premio_bruno' if socio_codigo == 'BA' else 'premio_rafael'

        # Projetos pessoais pagos
        projetos_pessoais = Projeto.objects.filter(
            tipo=TipoProjeto.PESSOAL,
            socio__codigo=socio_codigo,
            data_recibo__isnull=False
        )

        # Projetos com prémios (trabalho feito)
        projetos_premios_feitos = Projeto.objects.filter(
            **{f'{campo_premio}__gt': 0},
            data_fim__lt=hoje
        )

        # Projetos com prémios futuros
        projetos_premios_futuros = Projeto.objects.filter(
            **{f'{campo_premio}__gt': 0},
            data_fim__gte=hoje
        )

        # Despesas fixas
        despesas_fixas = Despesa.objects.filter(
            tags__codigo__in=['ADMINISTRATIVO', 'ORDENADO', 'SUB_ALIMENTACAO']
        ).distinct()

        # Despesas pessoais
        socio_obj = Socio.objects.get(codigo=socio_codigo)
        despesas_pessoais = Despesa.objects.filter(
            tags__codigo='PESSOAL',
            credor__nome__icontains=socio_obj.nome_completo.split()[0]
        ).distinct()

        # Boletins pagos
        boletins_pagos = Boletim.objects.filter(
            socio__codigo=socio_codigo,
            estado=EstadoBoletim.PAGO
        )

        # Boletins pendentes
        boletins_pendentes = Boletim.objects.filter(
            socio__codigo=socio_codigo,
            estado=EstadoBoletim.PENDENTE
        )

        return {
            'projetos_pessoais': list(projetos_pessoais.values()),
            'projetos_premios_feitos': list(projetos_premios_feitos.values()),
            'projetos_premios_futuros': list(projetos_premios_futuros.values()),
            'despesas_fixas': list(despesas_fixas.values()),
            'despesas_pessoais': list(despesas_pessoais.values()),
            'boletins_pagos': list(boletins_pagos.values()),
            'boletins_pendentes': list(boletins_pendentes.values())
        }
