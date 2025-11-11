# -*- coding: utf-8 -*-
"""
Lógica de cálculo de Saldos Pessoais - MÓDULO CORE DO SISTEMA

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
from typing import Dict, List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from datetime import date, datetime

from database.models import (
    Projeto, TipoProjeto, EstadoProjeto,
    Despesa, TipoDespesa, EstadoDespesa,
    Boletim, Socio, EstadoBoletim
)


class SaldosCalculator:
    """
    Calcula os saldos pessoais dos sócios
    """

    # Investimento inicial de cada sócio (referência histórica)
    INVESTIMENTO_INICIAL_BRUNO = Decimal("5200.00")
    INVESTIMENTO_INICIAL_RAFAEL = Decimal("5200.00")

    def __init__(self, db_session: Session):
        """
        Initialize calculator

        Args:
            db_session: SQLAlchemy database session
        """
        self.db_session = db_session

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
            Socio.BRUNO,
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
            Socio.RAFAEL,
            incluir_investimento,
            data_inicio,
            data_fim
        )

    def _calcular_saldo(
        self,
        socio: Socio,
        incluir_investimento: bool = False,
        data_inicio: Optional[date] = None,
        data_fim: Optional[date] = None
    ) -> Dict:
        """
        Calcula o saldo pessoal de um sócio

        Args:
            socio: Sócio (BRUNO ou RAFAEL)
            incluir_investimento: Se deve incluir o investimento inicial
            data_inicio: Data de início para filtrar
            data_fim: Data de fim para filtrar

        Returns:
            Dict com breakdown completo:
            {
                'socio': 'BRUNO',
                'saldo_total': 11766.55,
                'ins': {
                    'projetos_pessoais': 15040.00,
                    'premios': 3086.25,
                    'investimento_inicial': 5200.00,  # se incluir_investimento=True
                    'total': 18126.25
                },
                'outs': {
                    'despesas_fixas': 11559.71,
                    'boletins': 5215.36,
                    'despesas_pessoais': 0.00,
                    'total': 16775.07
                },
                'sugestao_boletim': 11766.55  # valor para zerar o saldo
            }
        """
        # Determinar tipo de projeto pessoal
        tipo_projeto = TipoProjeto.PESSOAL_BRUNO if socio == Socio.BRUNO else TipoProjeto.PESSOAL_RAFAEL
        tipo_despesa = TipoDespesa.PESSOAL_BRUNO if socio == Socio.BRUNO else TipoDespesa.PESSOAL_RAFAEL

        # === CALCULAR INs (Entradas) ===

        # 1. Projetos pessoais (apenas RECEBIDOS)
        query_projetos_pessoais = self.db_session.query(
            func.sum(Projeto.valor_sem_iva)
        ).filter(
            Projeto.tipo == tipo_projeto,
            Projeto.estado == EstadoProjeto.RECEBIDO
        )

        if data_inicio:
            query_projetos_pessoais = query_projetos_pessoais.filter(
                Projeto.data_faturacao >= data_inicio
            )
        if data_fim:
            query_projetos_pessoais = query_projetos_pessoais.filter(
                Projeto.data_faturacao <= data_fim
            )

        projetos_pessoais = query_projetos_pessoais.scalar() or Decimal("0.00")

        # 2. Prémios de projetos da empresa (TODOS, independentemente do estado!)
        # ✅ CORREÇÃO: Prémios contam no saldo mesmo antes do projeto ser recebido (saldo virtual)
        if socio == Socio.BRUNO:
            query_premios = self.db_session.query(
                func.sum(Projeto.premio_bruno)
            ).filter(
                Projeto.premio_bruno > 0
            )
        else:
            query_premios = self.db_session.query(
                func.sum(Projeto.premio_rafael)
            ).filter(
                Projeto.premio_rafael > 0
            )

        if data_inicio:
            query_premios = query_premios.filter(
                Projeto.data_faturacao >= data_inicio
            )
        if data_fim:
            query_premios = query_premios.filter(
                Projeto.data_faturacao <= data_fim
            )

        premios = query_premios.scalar() or Decimal("0.00")

        # 3. Investimento inicial (se solicitado)
        investimento = Decimal("0.00")
        if incluir_investimento:
            investimento = (
                self.INVESTIMENTO_INICIAL_BRUNO if socio == Socio.BRUNO
                else self.INVESTIMENTO_INICIAL_RAFAEL
            )

        total_ins = projetos_pessoais + premios + investimento

        # === CALCULAR OUTs (Saídas) ===

        # 1. Despesas fixas mensais (divididas por 2)
        # ✅ CORREÇÃO: Usar valor_sem_iva (coluna P do Excel)
        query_despesas_fixas = self.db_session.query(
            func.sum(Despesa.valor_sem_iva)
        ).filter(
            Despesa.tipo == TipoDespesa.FIXA_MENSAL,
            Despesa.estado == EstadoDespesa.PAGO
        )

        if data_inicio:
            query_despesas_fixas = query_despesas_fixas.filter(
                Despesa.data >= data_inicio
            )
        if data_fim:
            query_despesas_fixas = query_despesas_fixas.filter(
                Despesa.data <= data_fim
            )

        despesas_fixas_total = query_despesas_fixas.scalar() or Decimal("0.00")
        despesas_fixas = despesas_fixas_total / Decimal("2.00")  # Divide por 2

        # 2. Boletins PENDENTES (emitidos mas não pagos)
        query_boletins_pendentes = self.db_session.query(
            func.sum(Boletim.valor)
        ).filter(
            Boletim.socio == socio,
            Boletim.estado == EstadoBoletim.PENDENTE
        )

        if data_inicio:
            query_boletins_pendentes = query_boletins_pendentes.filter(
                Boletim.data_emissao >= data_inicio
            )
        if data_fim:
            query_boletins_pendentes = query_boletins_pendentes.filter(
                Boletim.data_emissao <= data_fim
            )

        boletins_pendentes = query_boletins_pendentes.scalar() or Decimal("0.00")

        # 3. Boletins PAGOS
        query_boletins_pagos = self.db_session.query(
            func.sum(Boletim.valor)
        ).filter(
            Boletim.socio == socio,
            Boletim.estado == EstadoBoletim.PAGO
        )

        if data_inicio:
            query_boletins_pagos = query_boletins_pagos.filter(
                Boletim.data_emissao >= data_inicio
            )
        if data_fim:
            query_boletins_pagos = query_boletins_pagos.filter(
                Boletim.data_emissao <= data_fim
            )

        boletins_pagos = query_boletins_pagos.scalar() or Decimal("0.00")
        boletins_total = boletins_pendentes + boletins_pagos

        # 3. Despesas pessoais excecionais
        # ✅ CORREÇÃO: Usar valor_sem_iva (coluna P do Excel)
        query_despesas_pessoais = self.db_session.query(
            func.sum(Despesa.valor_sem_iva)
        ).filter(
            Despesa.tipo == tipo_despesa,
            Despesa.estado == EstadoDespesa.PAGO
        )

        if data_inicio:
            query_despesas_pessoais = query_despesas_pessoais.filter(
                Despesa.data >= data_inicio
            )
        if data_fim:
            query_despesas_pessoais = query_despesas_pessoais.filter(
                Despesa.data <= data_fim
            )

        despesas_pessoais = query_despesas_pessoais.scalar() or Decimal("0.00")

        total_outs = despesas_fixas + boletins_total + despesas_pessoais

        # === CALCULAR SALDO FINAL ===
        saldo_total = total_ins - total_outs

        return {
            'socio': socio.value,
            'saldo_total': float(saldo_total),
            'ins': {
                'projetos_pessoais': float(projetos_pessoais),
                'premios': float(premios),
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
            'sugestao_boletim': max(0, float(saldo_total))  # Nunca negativo
        }

    def obter_historico_mensal(
        self,
        socio: Socio,
        ano: int,
        incluir_investimento: bool = False
    ) -> List[Dict]:
        """
        Obtém histórico mensal de saldos para um ano específico

        Args:
            socio: Sócio (BRUNO ou RAFAEL)
            ano: Ano para obter histórico
            incluir_investimento: Se deve incluir investimento inicial

        Returns:
            Lista de dicts com saldos mensais:
            [
                {'mes': 1, 'mes_nome': 'Janeiro', 'saldo': 1234.56},
                {'mes': 2, 'mes_nome': 'Fevereiro', 'saldo': 2345.67},
                ...
            ]
        """
        meses = [
            'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
            'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
        ]

        historico = []
        for mes in range(1, 13):
            # Calcular até o fim do mês
            data_fim = date(ano, mes, 1)
            # Último dia do mês
            if mes == 12:
                data_fim = date(ano, 12, 31)
            else:
                data_fim = date(ano, mes + 1, 1)
                # Voltar 1 dia para ficar no último dia do mês anterior
                from datetime import timedelta
                data_fim = data_fim - timedelta(days=1)

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

    def obter_breakdown_detalhado(self, socio: Socio) -> Dict:
        """
        Obtém breakdown detalhado com listas de itens específicos

        Args:
            socio: Sócio (BRUNO ou RAFAEL)

        Returns:
            Dict com listas detalhadas de projetos, despesas e boletins
        """
        tipo_projeto = TipoProjeto.PESSOAL_BRUNO if socio == Socio.BRUNO else TipoProjeto.PESSOAL_RAFAEL
        tipo_despesa = TipoDespesa.PESSOAL_BRUNO if socio == Socio.BRUNO else TipoDespesa.PESSOAL_RAFAEL

        # Projetos pessoais
        projetos_pessoais = self.db_session.query(Projeto).filter(
            Projeto.tipo == tipo_projeto,
            Projeto.estado == EstadoProjeto.RECEBIDO
        ).all()

        # Projetos com prémios (TODOS, não só recebidos!)
        # ✅ CORREÇÃO: Prémios contam no saldo independentemente do estado
        if socio == Socio.BRUNO:
            projetos_premios = self.db_session.query(Projeto).filter(
                Projeto.premio_bruno > 0
            ).all()
        else:
            projetos_premios = self.db_session.query(Projeto).filter(
                Projeto.premio_rafael > 0
            ).all()

        # Despesas fixas
        despesas_fixas = self.db_session.query(Despesa).filter(
            Despesa.tipo == TipoDespesa.FIXA_MENSAL,
            Despesa.estado == EstadoDespesa.PAGO
        ).all()

        # Despesas pessoais
        despesas_pessoais = self.db_session.query(Despesa).filter(
            Despesa.tipo == tipo_despesa,
            Despesa.estado == EstadoDespesa.PAGO
        ).all()

        # Boletins (apenas PAGOS)
        boletins = self.db_session.query(Boletim).filter(
            Boletim.socio == socio,
            Boletim.estado == EstadoBoletim.PAGO
        ).all()

        return {
            'projetos_pessoais': [p.to_dict() for p in projetos_pessoais],
            'projetos_premios': [p.to_dict() for p in projetos_premios],
            'despesas_fixas': [d.to_dict() for d in despesas_fixas],
            'despesas_pessoais': [d.to_dict() for d in despesas_pessoais],
            'boletins': [b.to_dict() for b in boletins]
        }
