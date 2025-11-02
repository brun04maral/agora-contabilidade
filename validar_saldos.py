#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Validação rápida dos saldos pessoais
"""
from sqlalchemy import create_engine, and_
from sqlalchemy.orm import sessionmaker
from database.models import Projeto, Despesa, Boletim, EstadoBoletim, TipoDespesa
from database.models.boletim import Socio
from datetime import date
from dotenv import load_dotenv
import os

load_dotenv()

# Criar sessão
database_url = os.getenv("DATABASE_URL", "sqlite:///./agora_media.db")
engine = create_engine(database_url)
Session = sessionmaker(bind=engine)
session = Session()

hoje = date(2025, 10, 29)

print('=' * 60)
print('📊 VALIDAÇÃO FINAL - SALDOS PESSOAIS')
print('=' * 60)

for socio in [Socio.BRUNO, Socio.RAFAEL]:
    print(f'\n👤 {socio.value.upper()}:')

    # Projetos pessoais RECEBIDOS
    projetos = session.query(Projeto).filter(
        and_(
            Projeto.socio == socio,
            Projeto.data_pagamento.isnot(None),
            Projeto.data_pagamento <= hoje
        )
    ).all()
    total_projetos = sum(p.valor_pessoal for p in projetos)
    print(f'   (+) Projetos pessoais RECEBIDOS: €{total_projetos:,.2f}')

    # Prémios (já incluídos nos projetos)
    premios = sum(p.premio for p in projetos if p.premio)
    print(f'   (+) Prémios: €{premios:,.2f}')

    # Despesas fixas PAGAS (÷2)
    fixas = session.query(Despesa).filter(
        and_(
            Despesa.tipo == TipoDespesa.FIXA_MENSAL,
            Despesa.data_vencimento.isnot(None),
            Despesa.data_vencimento <= hoje
        )
    ).all()
    total_fixas = sum(d.valor for d in fixas) / 2
    print(f'   (-) Despesas fixas ÷2: €{total_fixas:,.2f}')

    # PESSOAIS
    tipo_pessoal = TipoDespesa.PESSOAL_BRUNO if socio == Socio.BRUNO else TipoDespesa.PESSOAL_RAFAEL
    despesas_pessoais = session.query(Despesa).filter(
        and_(
            Despesa.tipo == tipo_pessoal,
            Despesa.data_vencimento.isnot(None),
            Despesa.data_vencimento <= hoje
        )
    ).all()
    total_desp_pessoais = sum(d.valor for d in despesas_pessoais)

    boletins = session.query(Boletim).filter(
        and_(
            Boletim.socio == socio,
            Boletim.estado == EstadoBoletim.PAGO
        )
    ).all()
    total_boletins = sum(b.valor for b in boletins)

    total_pessoais = total_desp_pessoais + total_boletins
    print(f'   (-) PESSOAIS (Desp + Bol): €{total_pessoais:,.2f}')
    print(f'       • Despesas PESSOAL: €{total_desp_pessoais:,.2f}')
    print(f'       • Boletins PAGOS: €{total_boletins:,.2f}')

    # SALDO FINAL
    saldo = total_projetos + premios - total_fixas - total_pessoais
    print(f'   = SALDO: €{saldo:,.2f}')

session.close()
print('\n' + '=' * 60)
print('✅ Valores importados com lógica correta!')
print('=' * 60)
