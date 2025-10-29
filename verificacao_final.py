#!/usr/bin/env python3
"""VERIFICAÇÃO FINAL - TODOS OS VALORES"""
import os
from decimal import Decimal
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.models import Projeto, Despesa, Boletim, TipoProjeto, EstadoProjeto, TipoDespesa, EstadoDespesa, Socio

engine = create_engine('sqlite:///./agora_media.db')
Session = sessionmaker(bind=engine)
session = Session()

print("=" * 80)
print("✅ VERIFICAÇÃO FINAL - TODOS OS VALORES")
print("=" * 80)

# Calcular tudo
proj_bruno = session.query(Projeto).filter(Projeto.tipo == TipoProjeto.PESSOAL_BRUNO, Projeto.estado == EstadoProjeto.RECEBIDO).all()
proj_rafael = session.query(Projeto).filter(Projeto.tipo == TipoProjeto.PESSOAL_RAFAEL, Projeto.estado == EstadoProjeto.RECEBIDO).all()
total_proj_bruno = sum(p.valor_sem_iva or Decimal('0') for p in proj_bruno)
total_proj_rafael = sum(p.valor_sem_iva or Decimal('0') for p in proj_rafael)

premios_bruno = sum(p.premio_bruno for p in session.query(Projeto).all())
premios_rafael = sum(p.premio_rafael for p in session.query(Projeto).all())

fixas = session.query(Despesa).filter(Despesa.tipo == TipoDespesa.FIXA_MENSAL, Despesa.estado == EstadoDespesa.PAGO).all()
total_fixas = sum(d.valor_com_iva or d.valor_sem_iva or Decimal('0') for d in fixas)

desp_bruno = session.query(Despesa).filter(Despesa.tipo == TipoDespesa.PESSOAL_BRUNO, Despesa.estado == EstadoDespesa.PAGO).all()
desp_rafael = session.query(Despesa).filter(Despesa.tipo == TipoDespesa.PESSOAL_RAFAEL, Despesa.estado == EstadoDespesa.PAGO).all()
total_desp_bruno = sum(d.valor_com_iva or d.valor_sem_iva or Decimal('0') for d in desp_bruno)
total_desp_rafael = sum(d.valor_com_iva or d.valor_sem_iva or Decimal('0') for d in desp_rafael)

bol_bruno = session.query(Boletim).filter(Boletim.socio == Socio.BRUNO).all()
bol_rafael = session.query(Boletim).filter(Boletim.socio == Socio.RAFAEL).all()
total_bol_bruno = sum(b.valor for b in bol_bruno)
total_bol_rafael = sum(b.valor for b in bol_rafael)

saldo_bruno = total_proj_bruno + premios_bruno - (total_fixas / 2) - total_desp_bruno - total_bol_bruno
saldo_rafael = total_proj_rafael + premios_rafael - (total_fixas / 2) - total_desp_rafael - total_bol_rafael

print('\n👤 BRUNO:')
print(f'   (+) Projetos pessoais: €{float(total_proj_bruno):,.2f}')
print(f'   (+) Prémios: €{float(premios_bruno):,.2f}')
print(f'   (-) Despesas fixas ÷2: €{float(total_fixas / 2):,.2f}')
print(f'   (-) Despesas pessoais: €{float(total_desp_bruno):,.2f}')
print(f'   (-) Boletins: €{float(total_bol_bruno):,.2f}')
print(f'   = SALDO: €{float(saldo_bruno):,.2f}')

print(f'\n👤 RAFAEL:')
print(f'   (+) Projetos pessoais: €{float(total_proj_rafael):,.2f}')
print(f'   (+) Prémios: €{float(premios_rafael):,.2f}')
print(f'   (-) Despesas fixas ÷2: €{float(total_fixas / 2):,.2f}')
print(f'   (-) Despesas pessoais: €{float(total_desp_rafael):,.2f}')
print(f'   (-) Boletins: €{float(total_bol_rafael):,.2f}')
print(f'   = SALDO: €{float(saldo_rafael):,.2f}')

print('\n' + '=' * 80)
print('📊 COMPARAÇÃO COM EXCEL')
print('=' * 80)

checks = [
    ('Prémios Bruno', premios_bruno, Decimal('3111.25')),
    ('Prémios Rafael', premios_rafael, Decimal('6140.17')),
    ('Projetos Bruno', total_proj_bruno, Decimal('15040.00')),
    ('Despesas pessoais Bruno', total_desp_bruno, Decimal('8670.80')),
    ('Despesas pessoais Rafael', total_desp_rafael, Decimal('8658.00')),
    ('Boletins Bruno', total_bol_bruno, Decimal('5215.34')),
    ('Boletins Rafael', total_bol_rafael, Decimal('4649.70')),
]

for nome, valor, esperado in checks:
    diff = abs(float(valor) - float(esperado))
    status = '✅' if diff < 1 else f'❌ (diff: €{diff:.2f})'
    print(f'{nome:30} | €{float(valor):9,.2f} | €{float(esperado):9,.2f} | {status}')

print('\n' + '=' * 80)
print('🎯 RESULTADO:')

all_ok = all(abs(float(v) - float(e)) < 1 for _, v, e in checks)
if all_ok:
    print('✅ TODOS OS VALORES CORRETOS!')
else:
    print('⚠️ Alguns valores ainda precisam ajuste')

print('=' * 80)

session.close()
