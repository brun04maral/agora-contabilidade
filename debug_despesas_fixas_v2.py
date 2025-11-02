#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
from datetime import datetime, date

xl_path = 'CONTABILIDADE_FINAL_20251029.xlsx'
df = pd.read_excel(xl_path, sheet_name='DESPESAS', header=4)

print("="*80)
print("🔍 DEBUG: Primeiras 20 despesas fixas do Excel (LÓGICA CORRETA)")
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

    print(f"\n{count+1}. {numero} - {descricao[:50]}")
    print(f"   Valor: €{valor:.2f}")
    print(f"   Periodicidade: {periodicidade}")
    print(f"   Data vencimento: ANO={ano}, MÊS={mes}, DIA={dia}")

    if data_vencimento:
        print(f"   Data construída: {data_vencimento}")
        print(f"   É <= hoje ({hoje})? {data_vencimento <= hoje} → {'PAGO' if data_vencimento <= hoje else 'PENDENTE'}")
    else:
        print(f"   Data construída: INVÁLIDA")

    count += 1
    if count >= 20:
        break

print(f"\n\nTotal despesas fixas analisadas: {count}")
