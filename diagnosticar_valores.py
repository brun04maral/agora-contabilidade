#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de diagnóstico completo dos valores na base de dados
"""
import os
from decimal import Decimal
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

from database.models import (
    Projeto, Despesa, Boletim,
    TipoProjeto, EstadoProjeto,
    TipoDespesa, EstadoDespesa,
    Socio, EstadoBoletim
)

# Setup database
database_url = os.getenv("DATABASE_URL", "sqlite:///./agora_media.db")
engine = create_engine(database_url)
Session = sessionmaker(bind=engine)
session = Session()

print("=" * 80)
print("🔍 DIAGNÓSTICO COMPLETO DA BASE DE DADOS")
print("=" * 80)

# ============================================================================
# 1. PROJETOS PESSOAIS RECEBIDOS
# ============================================================================
print("\n" + "=" * 80)
print("1️⃣  PROJETOS PESSOAIS RECEBIDOS")
print("=" * 80)

projetos_bruno = session.query(Projeto).filter(
    Projeto.tipo == TipoProjeto.PESSOAL_BRUNO,
    Projeto.estado == EstadoProjeto.RECEBIDO
).all()

projetos_rafael = session.query(Projeto).filter(
    Projeto.tipo == TipoProjeto.PESSOAL_RAFAEL,
    Projeto.estado == EstadoProjeto.RECEBIDO
).all()

total_bruno_projetos = sum(p.valor_sem_iva or Decimal('0') for p in projetos_bruno)
total_rafael_projetos = sum(p.valor_sem_iva or Decimal('0') for p in projetos_rafael)

print(f"\n👤 BRUNO:")
print(f"   Quantidade: {len(projetos_bruno)} projetos")
print(f"   Total: €{float(total_bruno_projetos):,.2f}")
if len(projetos_bruno) <= 10:
    for p in projetos_bruno:
        print(f"      - {p.numero}: {p.descricao[:40]} → €{float(p.valor_sem_iva or 0):,.2f}")

print(f"\n👤 RAFAEL:")
print(f"   Quantidade: {len(projetos_rafael)} projetos")
print(f"   Total: €{float(total_rafael_projetos):,.2f}")
if len(projetos_rafael) <= 10:
    for p in projetos_rafael:
        print(f"      - {p.numero}: {p.descricao[:40]} → €{float(p.valor_sem_iva or 0):,.2f}")

# ============================================================================
# 2. PRÉMIOS (nos campos dos projetos)
# ============================================================================
print("\n" + "=" * 80)
print("2️⃣  PRÉMIOS (campos premio_bruno/premio_rafael dos projetos)")
print("=" * 80)

projetos_com_premios = session.query(Projeto).filter(
    (Projeto.premio_bruno > 0) | (Projeto.premio_rafael > 0)
).all()

total_premios_bruno = sum(p.premio_bruno for p in projetos_com_premios)
total_premios_rafael = sum(p.premio_rafael for p in projetos_com_premios)

print(f"\n🏆 Total prémios Bruno: €{float(total_premios_bruno):,.2f}")
print(f"🏆 Total prémios Rafael: €{float(total_premios_rafael):,.2f}")
print(f"\nProjetos com prémios ({len(projetos_com_premios)}):")

for p in projetos_com_premios:
    bruno_str = f"Bruno: €{float(p.premio_bruno):,.2f}" if p.premio_bruno > 0 else ""
    rafael_str = f"Rafael: €{float(p.premio_rafael):,.2f}" if p.premio_rafael > 0 else ""
    premios_str = " | ".join(filter(None, [bruno_str, rafael_str]))
    print(f"   {p.numero}: {premios_str} - {p.descricao[:40]}")

# ============================================================================
# 3. DESPESAS FIXAS PAGAS (÷2)
# ============================================================================
print("\n" + "=" * 80)
print("3️⃣  DESPESAS FIXAS MENSAIS PAGAS")
print("=" * 80)

despesas_fixas_pagas = session.query(Despesa).filter(
    Despesa.tipo == TipoDespesa.FIXA_MENSAL,
    Despesa.estado == EstadoDespesa.PAGO
).all()

total_fixas_pagas = sum(d.valor_com_iva or d.valor_sem_iva or Decimal('0') for d in despesas_fixas_pagas)
total_por_socio = total_fixas_pagas / 2

print(f"\n🔧 Total despesas fixas pagas: {len(despesas_fixas_pagas)}")
print(f"💰 Valor total: €{float(total_fixas_pagas):,.2f}")
print(f"➗ Dividido por 2: €{float(total_por_socio):,.2f}")

# Contar ordenados
ordenados = [d for d in despesas_fixas_pagas if 'ordenado' in (d.descricao or '').lower()]
print(f"💼 Ordenados: {len(ordenados)}")

# Mostrar primeiras 10
print("\nPrimeiras 10 despesas fixas pagas:")
for d in despesas_fixas_pagas[:10]:
    valor = d.valor_com_iva or d.valor_sem_iva or Decimal('0')
    print(f"   {d.numero}: €{float(valor):,.2f} - {d.descricao[:40]}")

# ============================================================================
# 4. BOLETINS
# ============================================================================
print("\n" + "=" * 80)
print("4️⃣  BOLETINS")
print("=" * 80)

boletins_bruno = session.query(Boletim).filter(Boletim.socio == Socio.BRUNO).all()
boletins_rafael = session.query(Boletim).filter(Boletim.socio == Socio.RAFAEL).all()

total_boletins_bruno = sum(b.valor for b in boletins_bruno)
total_boletins_rafael = sum(b.valor for b in boletins_rafael)

print(f"\n👤 BRUNO:")
print(f"   Quantidade: {len(boletins_bruno)} boletins")
print(f"   Total: €{float(total_boletins_bruno):,.2f}")

print(f"\n👤 RAFAEL:")
print(f"   Quantidade: {len(boletins_rafael)} boletins")
print(f"   Total: €{float(total_boletins_rafael):,.2f}")

# ============================================================================
# 5. DESPESAS PESSOAIS
# ============================================================================
print("\n" + "=" * 80)
print("5️⃣  DESPESAS PESSOAIS (tipo PESSOAL_BRUNO/PESSOAL_RAFAEL)")
print("=" * 80)

despesas_bruno = session.query(Despesa).filter(
    Despesa.tipo == TipoDespesa.PESSOAL_BRUNO,
    Despesa.estado == EstadoDespesa.PAGO
).all()

despesas_rafael = session.query(Despesa).filter(
    Despesa.tipo == TipoDespesa.PESSOAL_RAFAEL,
    Despesa.estado == EstadoDespesa.PAGO
).all()

total_despesas_bruno = sum(d.valor_com_iva or d.valor_sem_iva or Decimal('0') for d in despesas_bruno)
total_despesas_rafael = sum(d.valor_com_iva or d.valor_sem_iva or Decimal('0') for d in despesas_rafael)

print(f"\n👤 BRUNO:")
print(f"   Quantidade: {len(despesas_bruno)} despesas")
print(f"   Total: €{float(total_despesas_bruno):,.2f}")

print(f"\n👤 RAFAEL:")
print(f"   Quantidade: {len(despesas_rafael)} despesas")
print(f"   Total: €{float(total_despesas_rafael):,.2f}")

# ============================================================================
# 6. RESUMO FINAL
# ============================================================================
print("\n" + "=" * 80)
print("📊 RESUMO FINAL - SALDOS PESSOAIS")
print("=" * 80)

print("\n👤 BRUNO:")
print(f"   (+) Projetos pessoais recebidos: €{float(total_bruno_projetos):,.2f}")
print(f"   (+) Prémios empresa: €{float(total_premios_bruno):,.2f}")
print(f"   (-) Despesas fixas (÷2): €{float(total_por_socio):,.2f}")
print(f"   (-) Boletins: €{float(total_boletins_bruno):,.2f}")
print(f"   (-) Despesas pessoais: €{float(total_despesas_bruno):,.2f}")
saldo_bruno = total_bruno_projetos + total_premios_bruno - total_por_socio - total_boletins_bruno - total_despesas_bruno
print(f"   = SALDO: €{float(saldo_bruno):,.2f}")

print(f"\n👤 RAFAEL:")
print(f"   (+) Projetos pessoais recebidos: €{float(total_rafael_projetos):,.2f}")
print(f"   (+) Prémios empresa: €{float(total_premios_rafael):,.2f}")
print(f"   (-) Despesas fixas (÷2): €{float(total_por_socio):,.2f}")
print(f"   (-) Boletins: €{float(total_boletins_rafael):,.2f}")
print(f"   (-) Despesas pessoais: €{float(total_despesas_rafael):,.2f}")
saldo_rafael = total_rafael_projetos + total_premios_rafael - total_por_socio - total_boletins_rafael - total_despesas_rafael
print(f"   = SALDO: €{float(saldo_rafael):,.2f}")

print("\n" + "=" * 80)
print("✅ DIAGNÓSTICO CONCLUÍDO")
print("=" * 80)

session.close()
