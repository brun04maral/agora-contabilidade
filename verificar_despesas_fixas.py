#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import pandas as pd
from decimal import Decimal
from datetime import datetime, date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

from database.models import Despesa, TipoDespesa, EstadoDespesa

# Setup database
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///agora_media.db')
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

# Ler Excel
print("="*80)
print("🔍 VERIFICAÇÃO DESPESAS FIXAS MENSAIS")
print("="*80)

xl_path = 'CONTABILIDADE_FINAL_20251029.xlsx'
df = pd.read_excel(xl_path, sheet_name='DESPESAS', header=4)

print(f"\n📄 Total de linhas no Excel (DESPESAS): {len(df)}")

# Filtrar despesas fixas mensais no Excel
# Critério: periodicidade (coluna 8) = "Mensal"
despesas_fixas_excel = []
hoje = date(2025, 10, 29)  # Data de referência (mesma que import_from_excel.py)

for idx, row in df.iterrows():
    # Coluna 8 = Periodicidade
    periodicidade = str(row.iloc[8]) if pd.notna(row.iloc[8]) else ''

    # Verificar se é despesa fixa (periodicidade "Mensal")
    if 'mensal' not in periodicidade.lower():
        continue

    # Verificar se não é ordenado/sub. alimentação (excluir pessoais)
    tipo_str = str(row.iloc[1]) if pd.notna(row.iloc[1]) else ''
    if any(x in tipo_str.lower() for x in ['ordenado', 'alimentação']):
        continue

    numero = str(row.iloc[0]) if pd.notna(row.iloc[0]) else ''
    descricao = str(row.iloc[2]) if pd.notna(row.iloc[2]) else ''

    # Coluna 16 = TOTAL c/IVA
    valor = float(row.iloc[16]) if pd.notna(row.iloc[16]) else 0.0

    # Coluna 13 = Data vencimento
    data_vencimento = row.iloc[13] if pd.notna(row.iloc[13]) else None

    # Coluna 14 = Data pagamento
    data_pagamento = row.iloc[14] if pd.notna(row.iloc[14]) else None

    # Converter data_vencimento para date se for datetime
    if data_vencimento:
        if isinstance(data_vencimento, datetime):
            data_vencimento = data_vencimento.date()
        elif not isinstance(data_vencimento, date):
            # Se não for datetime nem date, ignorar
            data_vencimento = None

    # Determinar estado: Se data_vencimento <= hoje → PAGO
    estado = 'PENDENTE'
    if data_vencimento and isinstance(data_vencimento, date) and data_vencimento <= hoje:
        estado = 'PAGO'

    despesas_fixas_excel.append({
        'numero': numero,
        'tipo': tipo_str,
        'periodicidade': periodicidade,
        'descricao': descricao,
        'valor': valor,
        'estado': estado,
        'data_vencimento': data_vencimento,
        'data_pagamento': data_pagamento
    })

print(f"\n📊 Despesas fixas encontradas no Excel: {len(despesas_fixas_excel)}")
print(f"    - Dessas, quantas estão PAGAS?")

pagas_excel = [d for d in despesas_fixas_excel if d['estado'] == 'PAGO']
vencidas_excel = [d for d in despesas_fixas_excel if d['estado'] == 'VENCIDO']
pendentes_excel = [d for d in despesas_fixas_excel if d['estado'] == 'PENDENTE']

print(f"      • PAGAS: {len(pagas_excel)}")
print(f"      • VENCIDAS: {len(vencidas_excel)}")
print(f"      • PENDENTES: {len(pendentes_excel)}")

total_pagas_excel = sum(d['valor'] for d in pagas_excel)
print(f"\n💰 Total despesas fixas PAGAS no Excel: €{total_pagas_excel:,.2f}")
print(f"➗ Dividido por 2: €{total_pagas_excel/2:,.2f}")

# Mostrar primeiras 15
print(f"\n📋 Primeiras 15 despesas fixas PAGAS no Excel:")
for i, desp in enumerate(pagas_excel[:15], 1):
    print(f"   {i:2d}. {desp['numero']}: €{desp['valor']:>10.2f} - {desp['descricao'][:60]}")

# Verificar na base de dados
print("\n" + "="*80)
print("💾 VERIFICAÇÃO NA BASE DE DADOS")
print("="*80)

session = SessionLocal()

despesas_fixas_db = session.query(Despesa).filter(
    Despesa.tipo == TipoDespesa.FIXA_MENSAL
).all()

print(f"\n📊 Total despesas FIXA_MENSAL na DB: {len(despesas_fixas_db)}")

despesas_fixas_pagas_db = [d for d in despesas_fixas_db if d.estado == EstadoDespesa.PAGO]
print(f"    - Dessas, quantas estão PAGAS: {len(despesas_fixas_pagas_db)}")

total_pagas_db = sum(float(d.valor_com_iva) for d in despesas_fixas_pagas_db)
print(f"\n💰 Total despesas fixas PAGAS na DB: €{total_pagas_db:,.2f}")
print(f"➗ Dividido por 2: €{total_pagas_db/2:,.2f}")

print(f"\n📋 Primeiras 15 despesas fixas PAGAS na DB:")
for i, desp in enumerate(despesas_fixas_pagas_db[:15], 1):
    print(f"   {i:2d}. {desp.numero}: €{float(desp.valor_com_iva):>10.2f} - {desp.descricao[:60]}")

# Comparação
print("\n" + "="*80)
print("📊 COMPARAÇÃO")
print("="*80)

diff_quantidade = len(pagas_excel) - len(despesas_fixas_pagas_db)
diff_valor = total_pagas_excel - float(total_pagas_db)

print(f"\nQuantidade de despesas fixas PAGAS:")
print(f"   Excel: {len(pagas_excel)}")
print(f"   DB:    {len(despesas_fixas_pagas_db)}")
print(f"   Diff:  {diff_quantidade:+d} {'✅' if diff_quantidade == 0 else '⚠️'}")

print(f"\nValor total despesas fixas PAGAS:")
print(f"   Excel: €{total_pagas_excel:,.2f}")
print(f"   DB:    €{float(total_pagas_db):,.2f}")
print(f"   Diff:  €{diff_valor:+,.2f} {'✅' if abs(diff_valor) < 0.01 else '⚠️'}")

print(f"\nValor dividido por 2 (para cada sócio):")
print(f"   Excel: €{total_pagas_excel/2:,.2f}")
print(f"   DB:    €{float(total_pagas_db)/2:,.2f}")

# Encontrar despesas que estão no Excel mas não na DB
print("\n" + "="*80)
print("🔍 ANÁLISE DETALHADA")
print("="*80)

numeros_excel = set(d['numero'] for d in pagas_excel)
numeros_db = set(d.numero for d in despesas_fixas_pagas_db)

so_no_excel = numeros_excel - numeros_db
so_na_db = numeros_db - numeros_excel

if so_no_excel:
    print(f"\n⚠️  Despesas que estão no Excel (PAGAS) mas NÃO na DB ({len(so_no_excel)}):")
    for num in sorted(so_no_excel):
        desp = next(d for d in pagas_excel if d['numero'] == num)
        print(f"   {num}: €{desp['valor']:>10.2f} - {desp['descricao'][:60]}")

if so_na_db:
    print(f"\n⚠️  Despesas que estão na DB (PAGAS) mas NÃO no Excel ({len(so_na_db)}):")
    for num in sorted(so_na_db):
        desp = next(d for d in despesas_fixas_pagas_db if d.numero == num)
        print(f"   {num}: €{float(desp.valor_com_iva):>10.2f} - {desp.descricao[:60]}")

session.close()

print("\n" + "="*80)
print("✅ VERIFICAÇÃO CONCLUÍDA")
print("="*80)
