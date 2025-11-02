#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de diagnóstico - Verifica valores importados vs esperados
"""
import os
import sys
from pathlib import Path
from decimal import Decimal

from dotenv import load_dotenv
load_dotenv()

from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker

from database.models import (
    Cliente, Fornecedor, Projeto, Despesa, Boletim,
    TipoProjeto, EstadoProjeto, TipoDespesa, EstadoDespesa,
    Socio, EstadoBoletim
)

print("=" * 80)
print("🔍 DIAGNÓSTICO - Valores Importados")
print("=" * 80)

# Connect to database
database_url = os.getenv("DATABASE_URL", "sqlite:///./agora_media.db")
engine = create_engine(database_url)
Session = sessionmaker(bind=engine)
session = Session()

print("\n📊 CONTAGEM GERAL:")
print("=" * 80)

total_clientes = session.query(Cliente).count()
total_fornecedores = session.query(Fornecedor).count()
total_projetos = session.query(Projeto).count()
total_despesas = session.query(Despesa).count()
total_boletins = session.query(Boletim).count()

print(f"✅ Clientes: {total_clientes}")
print(f"✅ Fornecedores: {total_fornecedores}")
print(f"✅ Projetos: {total_projetos}")
print(f"✅ Despesas: {total_despesas}")
print(f"✅ Boletins: {total_boletins}")

# PROJETOS
print("\n🎬 PROJETOS POR TIPO:")
print("=" * 80)

projetos_por_tipo = session.query(
    Projeto.tipo,
    func.count(Projeto.id)
).group_by(Projeto.tipo).all()

for tipo, count in projetos_por_tipo:
    print(f"  {tipo.value}: {count}")

# PROJETOS PESSOAIS BRUNO
print("\n💰 PROJETOS PESSOAIS BRUNO:")
print("=" * 80)

projetos_bruno = session.query(Projeto).filter(
    Projeto.tipo == TipoProjeto.PESSOAL_BRUNO
).all()

print(f"Total: {len(projetos_bruno)} projetos")

total_bruno = Decimal("0")
total_bruno_recebido = Decimal("0")

for p in projetos_bruno:
    estado_emoji = "✅" if p.estado == EstadoProjeto.RECEBIDO else "⏳" if p.estado == EstadoProjeto.FATURADO else "❌"
    print(f"  {estado_emoji} {p.numero}: {p.descricao[:40]:40} €{float(p.valor_sem_iva):>10,.2f} ({p.estado.value})")
    total_bruno += p.valor_sem_iva
    if p.estado == EstadoProjeto.RECEBIDO:
        total_bruno_recebido += p.valor_sem_iva

print(f"\n  TOTAL: €{float(total_bruno):,.2f}")
print(f"  RECEBIDO (conta para saldo): €{float(total_bruno_recebido):,.2f}")
print(f"  ❗ ESPERADO: €15,040.00")

if float(total_bruno_recebido) != 15040.00:
    diff = 15040.00 - float(total_bruno_recebido)
    print(f"  ⚠️  DIFERENÇA: €{diff:,.2f}")

# PROJETOS PESSOAIS RAFAEL
print("\n💰 PROJETOS PESSOAIS RAFAEL:")
print("=" * 80)

projetos_rafael = session.query(Projeto).filter(
    Projeto.tipo == TipoProjeto.PESSOAL_RAFAEL
).all()

print(f"Total: {len(projetos_rafael)} projetos")

total_rafael = Decimal("0")
total_rafael_recebido = Decimal("0")

for p in projetos_rafael:
    estado_emoji = "✅" if p.estado == EstadoProjeto.RECEBIDO else "⏳" if p.estado == EstadoProjeto.FATURADO else "❌"
    print(f"  {estado_emoji} {p.numero}: {p.descricao[:40]:40} €{float(p.valor_sem_iva):>10,.2f} ({p.estado.value})")
    total_rafael += p.valor_sem_iva
    if p.estado == EstadoProjeto.RECEBIDO:
        total_rafael_recebido += p.valor_sem_iva

print(f"\n  TOTAL: €{float(total_rafael):,.2f}")
print(f"  RECEBIDO (conta para saldo): €{float(total_rafael_recebido):,.2f}")
print(f"  ❗ ESPERADO: €11,154.45")

if float(total_rafael_recebido) != 11154.45:
    diff = 11154.45 - float(total_rafael_recebido)
    print(f"  ⚠️  DIFERENÇA: €{diff:,.2f}")

# PRÉMIOS (projetos da EMPRESA com estado RECEBIDO)
print("\n🏆 PRÉMIOS (Projetos EMPRESA RECEBIDOS):")
print("=" * 80)

projetos_empresa_recebidos = session.query(Projeto).filter(
    Projeto.tipo == TipoProjeto.EMPRESA,
    Projeto.estado == EstadoProjeto.RECEBIDO
).all()

print(f"Total: {len(projetos_empresa_recebidos)} projetos da empresa recebidos")

total_premio_bruno = Decimal("0")
total_premio_rafael = Decimal("0")

for p in projetos_empresa_recebidos:
    premio_b = p.premio_bruno or Decimal("0")
    premio_r = p.premio_rafael or Decimal("0")

    if premio_b > 0 or premio_r > 0:
        print(f"  ✅ {p.numero}: {p.descricao[:30]:30} B:€{float(premio_b):>8,.2f} R:€{float(premio_r):>8,.2f}")
        total_premio_bruno += premio_b
        total_premio_rafael += premio_r

print(f"\n  TOTAL PRÉMIOS BRUNO: €{float(total_premio_bruno):,.2f}")
print(f"  ❗ ESPERADO: €3,111.25")

if float(total_premio_bruno) != 3111.25:
    diff = 3111.25 - float(total_premio_bruno)
    print(f"  ⚠️  DIFERENÇA: €{diff:,.2f}")

print(f"\n  TOTAL PRÉMIOS RAFAEL: €{float(total_premio_rafael):,.2f}")
print(f"  ❗ ESPERADO: €6,140.17")

if float(total_premio_rafael) != 6140.17:
    diff = 6140.17 - float(total_premio_rafael)
    print(f"  ⚠️  DIFERENÇA: €{diff:,.2f}")

# DESPESAS POR TIPO
print("\n💸 DESPESAS POR TIPO:")
print("=" * 80)

despesas_por_tipo = session.query(
    Despesa.tipo,
    func.count(Despesa.id)
).group_by(Despesa.tipo).all()

for tipo, count in despesas_por_tipo:
    print(f"  {tipo.value}: {count}")

# DESPESAS FIXAS MENSAIS
print("\n💸 DESPESAS FIXAS MENSAIS:")
print("=" * 80)

despesas_fixas = session.query(Despesa).filter(
    Despesa.tipo == TipoDespesa.FIXA_MENSAL
).all()

print(f"Total: {len(despesas_fixas)} despesas")

if len(despesas_fixas) == 0:
    print("  ❌ NENHUMA DESPESA FIXA MENSAL ENCONTRADA!")
    print("  ⚠️  Isto explica porque Dashboard mostra €0.00")
else:
    # Mostrar algumas
    print("\nPrimeiras 10 despesas fixas:")
    for d in despesas_fixas[:10]:
        estado_emoji = "✅" if d.estado == EstadoDespesa.PAGO else "⏳"
        print(f"  {estado_emoji} {d.numero}: {d.descricao[:40]:40} €{float(d.valor_sem_iva):>10,.2f} ({d.estado.value})")

    # Total das PAGAS (conta para saldo)
    total_fixas_pagas = session.query(
        func.sum(Despesa.valor_sem_iva)
    ).filter(
        Despesa.tipo == TipoDespesa.FIXA_MENSAL,
        Despesa.estado == EstadoDespesa.PAGO
    ).scalar() or Decimal("0")

    print(f"\n  TOTAL PAGAS: €{float(total_fixas_pagas):,.2f}")
    print(f"  POR SÓCIO (÷2): €{float(total_fixas_pagas / 2):,.2f}")
    print(f"  ❗ ESPERADO: €12,315.71 por sócio")

    if float(total_fixas_pagas / 2) != 12315.71:
        diff = 12315.71 - float(total_fixas_pagas / 2)
        print(f"  ⚠️  DIFERENÇA: €{diff:,.2f}")

# BOLETINS
print("\n📄 BOLETINS:")
print("=" * 80)

boletins_bruno = session.query(Boletim).filter(Boletim.socio == Socio.BRUNO).all()
boletins_rafael = session.query(Boletim).filter(Boletim.socio == Socio.RAFAEL).all()

print(f"Bruno: {len(boletins_bruno)} boletins")
print(f"Rafael: {len(boletins_rafael)} boletins")

total_boletins_bruno = sum([b.valor for b in boletins_bruno], Decimal("0"))
total_boletins_rafael = sum([b.valor for b in boletins_rafael], Decimal("0"))

print(f"\n  TOTAL BRUNO: €{float(total_boletins_bruno):,.2f}")
print(f"  ❗ ESPERADO: €5,215.36")

if float(total_boletins_bruno) != 5215.36:
    diff = 5215.36 - float(total_boletins_bruno)
    print(f"  ⚠️  DIFERENÇA: €{diff:,.2f}")

print(f"\n  TOTAL RAFAEL: €{float(total_boletins_rafael):,.2f}")
print(f"  ❗ ESPERADO: €4,649.69")

if float(total_boletins_rafael) != 4649.69:
    diff = 4649.69 - float(total_boletins_rafael)
    print(f"  ⚠️  DIFERENÇA: €{diff:,.2f}")

# RESUMO FINAL
print("\n" + "=" * 80)
print("📊 RESUMO DE PROBLEMAS:")
print("=" * 80)

problemas = []

if len(despesas_fixas) == 0:
    problemas.append("❌ Despesas fixas mensais: NENHUMA importada (esperado 88)")
elif float(total_fixas_pagas / 2) != 12315.71:
    problemas.append(f"⚠️  Despesas fixas: €{float(total_fixas_pagas / 2):,.2f} (esperado €12,315.71)")

if float(total_premio_bruno) != 3111.25:
    problemas.append(f"⚠️  Prémios Bruno: €{float(total_premio_bruno):,.2f} (esperado €3,111.25)")

if float(total_premio_rafael) != 6140.17:
    problemas.append(f"⚠️  Prémios Rafael: €{float(total_premio_rafael):,.2f} (esperado €6,140.17)")

if float(total_bruno_recebido) != 15040.00:
    problemas.append(f"⚠️  Projetos Bruno: €{float(total_bruno_recebido):,.2f} (esperado €15,040.00)")

if float(total_rafael_recebido) != 11154.45:
    problemas.append(f"⚠️  Projetos Rafael: €{float(total_rafael_recebido):,.2f} (esperado €11,154.45)")

if problemas:
    print("\n❌ PROBLEMAS ENCONTRADOS:\n")
    for p in problemas:
        print(f"  {p}")
else:
    print("\n✅ Nenhum problema encontrado! Todos os valores batem certo!")

print("\n" + "=" * 80)
print("💡 PRÓXIMOS PASSOS:")
print("=" * 80)

if len(despesas_fixas) == 0:
    print("\n1. ❌ Despesas fixas mensais não foram importadas!")
    print("   Causa provável: JSON ainda tem estrutura 'despesas_fixas_mensais' separada")
    print("   Solução: python3 fix_json_structure.py")

if float(total_premio_bruno) == 0 and float(total_premio_rafael) == 0:
    print("\n2. ❌ Prémios não foram importados!")
    print("   Causa provável: Projetos EMPRESA não têm premio_bruno/premio_rafael")
    print("   Solução: Verificar o JSON - campo 'premio_bruno' e 'premio_rafael'")

if float(total_bruno_recebido) < 15040.00:
    diff = 15040.00 - float(total_bruno_recebido)
    print(f"\n3. ⚠️  Falta €{diff:,.2f} nos projetos de Bruno")
    print("   Causa provável: Alguns projetos não têm estado 'RECEBIDO'")
    print("   Solução: Verificar estados dos projetos no JSON")

print("\n" + "=" * 80)

session.close()
