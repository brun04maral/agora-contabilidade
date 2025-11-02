#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
from datetime import datetime, date

xl_path = 'CONTABILIDADE_FINAL_20251029.xlsx'
df = pd.read_excel(xl_path, sheet_name='DESPESAS', header=4)

print("="*80)
print("🔍 DEBUG: Primeiras 20 despesas fixas do Excel")
print("="*80)

hoje = date(2025, 10, 29)
print(f"\nData de referência (hoje): {hoje}\n")

count = 0
for idx, row in df.iterrows():
    # Coluna 8 = Periodicidade
    periodicidade = str(row.iloc[8]) if pd.notna(row.iloc[8]) else ''

    # Verificar se é despesa fixa (periodicidade "Mensal")
    if 'mensal' not in periodicidade.lower():
        continue

    # Verificar se não é ordenado/sub. alimentação
    tipo_str = str(row.iloc[1]) if pd.notna(row.iloc[1]) else ''
    if any(x in tipo_str.lower() for x in ['ordenado', 'alimentação']):
        continue

    numero = str(row.iloc[0]) if pd.notna(row.iloc[0]) else ''
    descricao = str(row.iloc[2]) if pd.notna(row.iloc[2]) else ''
    valor = float(row.iloc[16]) if pd.notna(row.iloc[16]) else 0.0

    # Coluna 13 = Data vencimento
    data_vencimento = row.iloc[13] if pd.notna(row.iloc[13]) else None
    data_vencimento_raw = row.iloc[13]

    print(f"\n{count+1}. {numero} - {descricao[:50]}")
    print(f"   Valor: €{valor:.2f}")
    print(f"   Periodicidade: {periodicidade}")
    print(f"   Data vencimento (raw): {data_vencimento_raw} (tipo: {type(data_vencimento_raw).__name__})")

    if data_vencimento:
        if isinstance(data_vencimento, datetime):
            data_vencimento_date = data_vencimento.date()
            print(f"   Data vencimento (date): {data_vencimento_date}")
            print(f"   É <= hoje? {data_vencimento_date <= hoje}")
        elif isinstance(data_vencimento, date):
            print(f"   Data vencimento (date): {data_vencimento}")
            print(f"   É <= hoje? {data_vencimento <= hoje}")
        else:
            print(f"   Data vencimento: TIPO INVÁLIDO ({type(data_vencimento).__name__})")
    else:
        print(f"   Data vencimento: NULO/VAZIO")

    count += 1
    if count >= 20:
        break

print(f"\n\nTotal despesas fixas encontradas: {count}")
