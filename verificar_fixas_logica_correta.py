#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import pandas as pd
from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

from database.models import Despesa, TipoDespesa, EstadoDespesa

# Setup database
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///agora_media.db')
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

print("="*80)
print("📊 VERIFICAÇÃO: Despesas Fixas com LÓGICA CORRETA")
print("="*80)

# Valor esperado na CAIXA
valor_esperado_caixa = 12315.705  # Da célula H3 (Bruno)
print(f"\n💰 Valor esperado na CAIXA (célula H3): €{valor_esperado_caixa:,.2f}")
print(f"   (Por sócio, já dividido por 2)")

# Ler Excel
xl_path = 'CONTABILIDADE_FINAL_20251029.xlsx'
df = pd.read_excel(xl_path, sheet_name='DESPESAS', header=4)

print(f"\n📄 Total de linhas no Excel (DESPESAS): {len(df)}")

# Lógica correta da fórmula CAIXA:
# =SUMIFS(DESPESAS!$P$6:$P1002,
#         DESPESAS!$I$6:$I1002, "Mensal",
#         DESPESAS!$T$6:$T1002, "<>"&"") / 2
#
# Coluna I (índice 8) = PERIODICIDADE
# Coluna P (índice 15 mas depois das fórmulas é 16) = TOTAL s/IVA
# Coluna Q (índice 16) = TOTAL c/IVA  ← ESTA é a coluna P no Excel (16+1=P na contagem Excel)
# Coluna T (índice 19) = DATA DE VENCIMENTO

print("\n🔍 Contando despesas fixas mensais no Excel:")
print("   Critério: Periodicidade='Mensal' AND Data_vencimento<>vazio")
print("-" * 80)

despesas_fixas_excel = []

for idx, row in df.iterrows():
    # Coluna 8 = Periodicidade
    periodicidade = str(row.iloc[8]) if pd.notna(row.iloc[8]) else ''

    # Verificar se é "Mensal"
    if 'mensal' not in periodicidade.lower():
        continue

    # Coluna 19 = DATA DE VENCIMENTO
    data_vencimento_col = row.iloc[19] if len(row) > 19 and pd.notna(row.iloc[19]) else None

    # Se data de vencimento está vazia, pular
    if not data_vencimento_col:
        continue

    numero = str(row.iloc[0]) if pd.notna(row.iloc[0]) else ''
    descricao = str(row.iloc[7]) if pd.notna(row.iloc[7]) else ''  # Coluna 7 = DESCRIÇÃO
    tipo_str = str(row.iloc[6]) if pd.notna(row.iloc[6]) else ''  # Coluna 6 = TIPO

    # A fórmula usa coluna P do Excel, que corresponde a coluna 16 em Python (TOTAL c/IVA)
    valor = float(row.iloc[16]) if pd.notna(row.iloc[16]) else 0.0

    despesas_fixas_excel.append({
        'numero': numero,
        'tipo': tipo_str,
        'descricao': descricao,
        'valor': valor,
        'periodicidade': periodicidade,
        'data_vencimento': data_vencimento_col
    })

total_excel = sum(d['valor'] for d in despesas_fixas_excel)
por_socio_excel = total_excel / 2

print(f"\n✅ Total despesas fixas mensais (com data vencimento): {len(despesas_fixas_excel)}")
print(f"   Valor total: €{total_excel:,.2f}")
print(f"   Por sócio (÷2): €{por_socio_excel:,.2f}")

# Comparar com CAIXA
diff_caixa = por_socio_excel - valor_esperado_caixa
print(f"\n📊 Comparação com CAIXA:")
print(f"   Esperado (CAIXA): €{valor_esperado_caixa:,.2f}")
print(f"   Calculado (Excel): €{por_socio_excel:,.2f}")
print(f"   Diferença: €{diff_caixa:+,.2f} {'✅' if abs(diff_caixa) < 0.01 else '⚠️'}")

# Verificar na base de dados
print("\n" + "="*80)
print("💾 VERIFICAÇÃO NA BASE DE DADOS")
print("="*80)

session = SessionLocal()

despesas_fixas_db = session.query(Despesa).filter(
    Despesa.tipo == TipoDespesa.FIXA_MENSAL,
    Despesa.estado == EstadoDespesa.PAGO
).all()

print(f"\n📊 Total despesas FIXA_MENSAL PAGO na DB: {len(despesas_fixas_db)}")

total_db = sum(float(d.valor_com_iva) for d in despesas_fixas_db)
por_socio_db = total_db / 2

print(f"   Valor total: €{total_db:,.2f}")
print(f"   Por sócio (÷2): €{por_socio_db:,.2f}")

# Comparação
print("\n" + "="*80)
print("📊 COMPARAÇÃO FINAL")
print("="*80)

diff_quantidade = len(despesas_fixas_excel) - len(despesas_fixas_db)
diff_valor = total_excel - total_db
diff_por_socio = por_socio_excel - por_socio_db

print(f"\nQuantidade:")
print(f"   Excel: {len(despesas_fixas_excel)}")
print(f"   DB:    {len(despesas_fixas_db)}")
print(f"   Diff:  {diff_quantidade:+d} {'✅' if diff_quantidade == 0 else '⚠️'}")

print(f"\nValor total:")
print(f"   Excel: €{total_excel:,.2f}")
print(f"   DB:    €{total_db:,.2f}")
print(f"   Diff:  €{diff_valor:+,.2f} {'✅' if abs(diff_valor) < 0.01 else '⚠️'}")

print(f"\nPor sócio (÷2):")
print(f"   Excel: €{por_socio_excel:,.2f}")
print(f"   DB:    €{por_socio_db:,.2f}")
print(f"   Diff:  €{diff_por_socio:+,.2f} {'✅' if abs(diff_por_socio) < 0.01 else '⚠️'}")

if abs(diff_quantidade) > 0:
    print("\n" + "="*80)
    print("🔍 ANÁLISE DE DIFERENÇAS")
    print("="*80)

    numeros_excel = set(d['numero'] for d in despesas_fixas_excel)
    numeros_db = set(d.numero for d in despesas_fixas_db)

    so_no_excel = numeros_excel - numeros_db
    so_na_db = numeros_db - numeros_excel

    if so_no_excel:
        print(f"\n⚠️  Despesas no Excel mas NÃO na DB ({len(so_no_excel)}):")
        for num in sorted(list(so_no_excel)[:10]):
            desp = next(d for d in despesas_fixas_excel if d['numero'] == num)
            print(f"   {num}: €{desp['valor']:>10.2f} | {desp['tipo'][:30]} | {desp['descricao'][:40]}")

    if so_na_db:
        print(f"\n⚠️  Despesas na DB mas NÃO no Excel ({len(so_na_db)}):")
        for num in sorted(list(so_na_db)[:10]):
            desp = next(d for d in despesas_fixas_db if d.numero == num)
            print(f"   {num}: €{float(desp.valor_com_iva):>10.2f} | {desp.descricao[:50]}")

# Mostrar primeiras despesas para confirmar tipos
print("\n" + "="*80)
print("📋 PRIMEIRAS 15 DESPESAS FIXAS DO EXCEL:")
print("="*80)

for i, desp in enumerate(despesas_fixas_excel[:15], 1):
    print(f"{i:2d}. {desp['numero']}: €{desp['valor']:>10.2f} | {desp['tipo'][:25]} | {desp['descricao'][:35]}")

session.close()

print("\n" + "="*80)
print("✅ VERIFICAÇÃO CONCLUÍDA")
print("="*80)
