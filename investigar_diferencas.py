#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para investigar as diferenças nos valores
"""
import os
from decimal import Decimal
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

from database.models import (
    Projeto, Despesa,
    TipoProjeto, EstadoProjeto,
    TipoDespesa, EstadoDespesa
)

# Setup database
database_url = os.getenv("DATABASE_URL", "sqlite:///./agora_media.db")
engine = create_engine(database_url)
Session = sessionmaker(bind=engine)
session = Session()

print("=" * 80)
print("🔍 INVESTIGANDO DIFERENÇAS")
print("=" * 80)

# ============================================================================
# 1. Verificar projeto #P0001
# ============================================================================
print("\n" + "=" * 80)
print("1️⃣  PROJETO #P0001 (prémios faltantes)")
print("=" * 80)

projeto_p0001 = session.query(Projeto).filter(Projeto.numero == '#P0001').first()

if projeto_p0001:
    print(f"✅ Projeto #P0001 encontrado:")
    print(f"   Descrição: {projeto_p0001.descricao}")
    print(f"   Tipo: {projeto_p0001.tipo}")
    print(f"   Estado: {projeto_p0001.estado}")
    print(f"   Prémio Bruno: €{float(projeto_p0001.premio_bruno):,.2f}")
    print(f"   Prémio Rafael: €{float(projeto_p0001.premio_rafael):,.2f}")
else:
    print("❌ Projeto #P0001 NÃO encontrado na base de dados")
    print("   → Isso explica os €428.75 faltantes em cada sócio")

# ============================================================================
# 2. Analisar despesas fixas em detalhe
# ============================================================================
print("\n" + "=" * 80)
print("2️⃣  DESPESAS FIXAS PAGAS (análise detalhada)")
print("=" * 80)

despesas_fixas = session.query(Despesa).filter(
    Despesa.tipo == TipoDespesa.FIXA_MENSAL,
    Despesa.estado == EstadoDespesa.PAGO
).order_by(Despesa.numero).all()

print(f"\nTotal: {len(despesas_fixas)} despesas")

# Agrupar por descrição
from collections import defaultdict
por_descricao = defaultdict(lambda: {'count': 0, 'total': Decimal('0')})

for d in despesas_fixas:
    desc = (d.descricao or 'Sem descrição')[:40]
    valor = d.valor_com_iva or d.valor_sem_iva or Decimal('0')
    por_descricao[desc]['count'] += 1
    por_descricao[desc]['total'] += valor

print("\nAgrupadas por descrição:")
for desc, info in sorted(por_descricao.items(), key=lambda x: -x[1]['total']):
    print(f"   {info['count']:2}x €{float(info['total']):8,.2f} - {desc}")

total = sum(d.valor_com_iva or d.valor_sem_iva or Decimal('0') for d in despesas_fixas)
print(f"\n💰 Total: €{float(total):,.2f}")
print(f"➗ Por sócio: €{float(total/2):,.2f}")

# Esperado
print("\n📊 Esperado: €24,631.42 total (€12,315.71 por sócio)")
print(f"📊 Diferença: €{float(total - Decimal('24631.42')):,.2f}")

# ============================================================================
# 3. Analisar projetos pessoais Bruno
# ============================================================================
print("\n" + "=" * 80)
print("3️⃣  PROJETOS PESSOAIS BRUNO (análise detalhada)")
print("=" * 80)

projetos_bruno = session.query(Projeto).filter(
    Projeto.tipo == TipoProjeto.PESSOAL_BRUNO,
    Projeto.estado == EstadoProjeto.RECEBIDO
).order_by(Projeto.numero).all()

print(f"\nTotal: {len(projetos_bruno)} projetos RECEBIDOS")
print("\nListagem completa:")

total_bruno = Decimal('0')
for p in projetos_bruno:
    valor = p.valor_sem_iva or Decimal('0')
    total_bruno += valor
    print(f"   {p.numero}: €{float(valor):8,.2f} - {p.descricao[:50]}")

print(f"\n💰 Total: €{float(total_bruno):,.2f}")
print(f"📊 Esperado: €15,040.00")
print(f"📊 Diferença: €{float(Decimal('15040.00') - total_bruno):,.2f}")

# Verificar se há projetos FATURADOS (não RECEBIDOS)
projetos_bruno_faturados = session.query(Projeto).filter(
    Projeto.tipo == TipoProjeto.PESSOAL_BRUNO,
    Projeto.estado == EstadoProjeto.FATURADO
).all()

if projetos_bruno_faturados:
    print(f"\n⚠️  Projetos FATURADOS (não RECEBIDOS): {len(projetos_bruno_faturados)}")
    total_faturados = Decimal('0')
    for p in projetos_bruno_faturados:
        valor = p.valor_sem_iva or Decimal('0')
        total_faturados += valor
        print(f"   {p.numero}: €{float(valor):8,.2f} - {p.descricao[:50]}")
    print(f"   Total faturados: €{float(total_faturados):,.2f}")

# ============================================================================
# 4. Comparar com valores esperados
# ============================================================================
print("\n" + "=" * 80)
print("📊 COMPARAÇÃO COM VALORES ESPERADOS")
print("=" * 80)

print("\n👤 BRUNO:")
print(f"   Projetos pessoais:")
print(f"      Atual: €{float(total_bruno):,.2f}")
print(f"      Esperado: €15,040.00")
print(f"      Diferença: €{float(Decimal('15040.00') - total_bruno):,.2f}")

print(f"\n   Prémios:")
total_premios_bruno = sum(p.premio_bruno for p in session.query(Projeto).all())
print(f"      Atual: €{float(total_premios_bruno):,.2f}")
print(f"      Esperado: €3,111.25")
print(f"      Diferença: €{float(Decimal('3111.25') - total_premios_bruno):,.2f}")

print(f"\n   Despesas fixas (÷2):")
total_fixas = sum(d.valor_com_iva or d.valor_sem_iva or Decimal('0') for d in despesas_fixas)
print(f"      Atual: €{float(total_fixas / 2):,.2f}")
print(f"      Esperado: €12,315.71")
print(f"      Diferença: €{float(total_fixas / 2 - Decimal('12315.71')):,.2f}")

print("\n" + "=" * 80)

session.close()
