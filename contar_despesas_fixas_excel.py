#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
from datetime import date

xl_path = 'CONTABILIDADE_FINAL_20251029.xlsx'
df = pd.read_excel(xl_path, sheet_name='DESPESAS', header=4)

print("="*80)
print("📊 CONTAGEM COMPLETA: Despesas Fixas Mensais no Excel")
print("="*80)

hoje = date(2025, 10, 29)
print(f"\nData de referência (hoje): {hoje}\n")

despesas_fixas_pagas = []
despesas_fixas_pendentes = []

for idx, row in df.iterrows():
    # Coluna 8 = Periodicidade
    periodicidade = str(row.iloc[8]) if pd.notna(row.iloc[8]) else ''

    # Verificar se é despesa fixa (periodicidade "Mensal")
    if 'mensal' not in periodicidade.lower():
        continue

    # Verificar se não é ordenado/sub. alimentação (essas são PESSOAL_*)
    tipo_str = str(row.iloc[6]) if pd.notna(row.iloc[6]) else ''  # Coluna 6 = TIPO
    if any(x in tipo_str.lower() for x in ['ordenado', 'alimentação']):
        continue

    numero = str(row.iloc[0]) if pd.notna(row.iloc[0]) else ''
    descricao = str(row.iloc[7]) if pd.notna(row.iloc[7]) else ''  # Coluna 7 = DESCRIÇÃO
    valor = float(row.iloc[16]) if pd.notna(row.iloc[16]) else 0.0

    # Construir data_vencimento usando colunas 1, 2, 3 (ANO, MÊS, DIA)
    ano = int(row.iloc[1]) if pd.notna(row.iloc[1]) else None
    mes = int(row.iloc[2]) if pd.notna(row.iloc[2]) else None
    dia = int(row.iloc[3]) if pd.notna(row.iloc[3]) else None

    data_vencimento = None
    if ano and mes and dia:
        try:
            data_vencimento = date(ano, mes, dia)
        except:
            data_vencimento = None

    if data_vencimento and data_vencimento <= hoje:
        despesas_fixas_pagas.append({
            'numero': numero,
            'descricao': descricao,
            'valor': valor,
            'data_vencimento': data_vencimento
        })
    else:
        despesas_fixas_pendentes.append({
            'numero': numero,
            'descricao': descricao,
            'valor': valor,
            'data_vencimento': data_vencimento
        })

print(f"Total despesas fixas mensais (periodicidade=Mensal, excluindo ordenados):")
print(f"   PAGAS:     {len(despesas_fixas_pagas)}")
print(f"   PENDENTES: {len(despesas_fixas_pendentes)}")
print(f"   TOTAL:     {len(despesas_fixas_pagas) + len(despesas_fixas_pendentes)}")

total_pagas = sum(d['valor'] for d in despesas_fixas_pagas)
total_pendentes = sum(d['valor'] for d in despesas_fixas_pendentes)

print(f"\nValor total:")
print(f"   PAGAS:     €{total_pagas:,.2f}")
print(f"   PENDENTES: €{total_pendentes:,.2f}")
print(f"   TOTAL:     €{total_pagas + total_pendentes:,.2f}")

print(f"\nPara saldos pessoais (PAGAS ÷ 2):")
print(f"   Cada sócio: €{total_pagas / 2:,.2f}")

print("\n" + "="*80)
print("COMPARAÇÃO COM BASE DE DADOS")
print("="*80)

print(f"\nNa DB:")
print(f"   Despesas FIXA_MENSAL PAGAS: 40")
print(f"   Valor total: €7,939.66")
print(f"   Cada sócio: €3,969.83")

print(f"\nDiferença:")
print(f"   Quantidade: {len(despesas_fixas_pagas) - 40:+d}")
print(f"   Valor: €{total_pagas - 7939.66:+,.2f}")

if len(despesas_fixas_pagas) != 40:
    print("\n" + "="*80)
    print("⚠️  ANÁLISE: Por que há diferença?")
    print("="*80)

    print(f"\nPrimeiras 10 despesas fixas PAGAS no Excel:")
    for i, desp in enumerate(despesas_fixas_pagas[:10], 1):
        print(f"   {i:2d}. {desp['numero']}: €{desp['valor']:>10.2f} - {desp['data_vencimento']} - {desp['descricao'][:40]}")

    if len(despesas_fixas_pendentes) > 0:
        print(f"\nPrimeiras 10 despesas fixas PENDENTES no Excel:")
        for i, desp in enumerate(despesas_fixas_pendentes[:10], 1):
            print(f"   {i:2d}. {desp['numero']}: €{desp['valor']:>10.2f} - {desp['data_vencimento']} - {desp['descricao'][:40]}")

print("\n" + "="*80)
