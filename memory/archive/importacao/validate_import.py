#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de validação da importação
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from logic.saldos import SaldosCalculator

load_dotenv()

# Setup database
database_url = os.getenv("DATABASE_URL", "sqlite:///./agora_media.db")
engine = create_engine(database_url)
Session = sessionmaker(bind=engine)
session = Session()

# Import models
from database.models import Cliente, Fornecedor, Projeto, Despesa, Boletim

print("=" * 80)
print("📊 VALIDAÇÃO DA IMPORTAÇÃO - Excel 20251108")
print("=" * 80)
print()

# Contar registos
print("📋 TOTAIS IMPORTADOS:")
print(f"  • Clientes:     {session.query(Cliente).count()}")
print(f"  • Fornecedores: {session.query(Fornecedor).count()}")
print(f"  • Projetos:     {session.query(Projeto).count()}")
print(f"  • Despesas:     {session.query(Despesa).count()}")
print(f"  • Boletins:     {session.query(Boletim).count()}")
print()

# Calcular saldos
print("💰 SALDOS PESSOAIS:")
calc = SaldosCalculator(session)

saldo_bruno = calc.calcular_saldo_bruno()
saldo_rafael = calc.calcular_saldo_rafael()

print(f"\n👤 BA:")
print(f"  INs (Entradas):")
print(f"    • Projetos pessoais: €{saldo_bruno['ins']['projetos_pessoais']:,.2f}")
print(f"    • Prémios:           €{saldo_bruno['ins']['premios']:,.2f}")
print(f"    • TOTAL INs:         €{saldo_bruno['ins']['total']:,.2f}")
print(f"  OUTs (Saídas):")
print(f"    • Despesas fixas ÷2: €{saldo_bruno['outs']['despesas_fixas']:,.2f}")
print(f"    • Boletins:          €{saldo_bruno['outs']['boletins']:,.2f}")
print(f"    • Despesas pessoais: €{saldo_bruno['outs']['despesas_pessoais']:,.2f}")
print(f"    • TOTAL OUTs:        €{saldo_bruno['outs']['total']:,.2f}")
print(f"  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
print(f"  💵 SALDO TOTAL:      €{saldo_bruno['saldo_total']:,.2f}")
print(f"  💡 Sugestão boletim: €{saldo_bruno['sugestao_boletim']:,.2f}")

print(f"\n👤 RR:")
print(f"  INs (Entradas):")
print(f"    • Projetos pessoais: €{saldo_rafael['ins']['projetos_pessoais']:,.2f}")
print(f"    • Prémios:           €{saldo_rafael['ins']['premios']:,.2f}")
print(f"    • TOTAL INs:         €{saldo_rafael['ins']['total']:,.2f}")
print(f"  OUTs (Saídas):")
print(f"    • Despesas fixas ÷2: €{saldo_rafael['outs']['despesas_fixas']:,.2f}")
print(f"    • Boletins:          €{saldo_rafael['outs']['boletins']:,.2f}")
print(f"    • Despesas pessoais: €{saldo_rafael['outs']['despesas_pessoais']:,.2f}")
print(f"    • TOTAL OUTs:        €{saldo_rafael['outs']['total']:,.2f}")
print(f"  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
print(f"  💵 SALDO TOTAL:      €{saldo_rafael['saldo_total']:,.2f}")
print(f"  💡 Sugestão boletim: €{saldo_rafael['sugestao_boletim']:,.2f}")

print()
print("=" * 80)
print("✅ VALIDAÇÃO CONCLUÍDA!")
print("=" * 80)

session.close()
