#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verificar detalhes específicos do Excel
"""
import pandas as pd
from datetime import datetime, date

print("=" * 80)
print("🔍 VERIFICANDO DETALHES DO EXCEL")
print("=" * 80)

xl = pd.ExcelFile('CONTABILIDADE_FINAL.xlsx')

# ============================================================================
# 1. Verificar projeto #P0001
# ============================================================================
print("\n" + "=" * 80)
print("1️⃣  PROJETO #P0001")
print("=" * 80)

df_projetos = pd.read_excel(xl, sheet_name='PROJETOS', header=3)
df_projetos_dados = df_projetos[df_projetos.iloc[:, 0].astype(str).str.startswith('#P', na=False)]

projeto_p0001 = df_projetos_dados[df_projetos_dados.iloc[:, 0] == '#P0001']

if len(projeto_p0001) > 0:
    print("✅ Projeto #P0001 encontrado no Excel")
    row = projeto_p0001.iloc[0]
    print(f"\nDados completos:")
    for i, col in enumerate(df_projetos.columns):
        valor = row.iloc[i]
        if pd.notna(valor):
            print(f"   Col {i:2} ({col}): {valor}")
else:
    print("❌ Projeto #P0001 NÃO encontrado no Excel")

# ============================================================================
# 2. Verificar prémios #D000009 e #D000010
# ============================================================================
print("\n" + "=" * 80)
print("2️⃣  PRÉMIOS #D000009 e #D000010")
print("=" * 80)

df_despesas = pd.read_excel(xl, sheet_name='DESPESAS', header=5)
df_despesas_dados = df_despesas[df_despesas.iloc[:, 0].astype(str).str.startswith('#D', na=False)]

premios = df_despesas_dados[df_despesas_dados.iloc[:, 0].isin(['#D000009', '#D000010'])]

for idx, row in premios.iterrows():
    numero = row.iloc[0]
    print(f"\n{numero}:")
    print(f"   Projeto (col 5): {row.iloc[5]}")
    print(f"   Credor (col 4): {row.iloc[4]}")
    print(f"   Tipo (col 6): {row.iloc[6]}")
    print(f"   Descrição (col 7): {row.iloc[7]}")
    print(f"   Valor col 9: {row.iloc[9]}")
    print(f"   Valor col 16 (TOTAL c/IVA): {row.iloc[16] if len(row) > 16 else 'N/A'}")

# ============================================================================
# 3. Verificar projeto #P0061 (GS1 Copenhaga)
# ============================================================================
print("\n" + "=" * 80)
print("3️⃣  PROJETO #P0061 (GS1 Copenhaga)")
print("=" * 80)

projeto_p0061 = df_projetos_dados[df_projetos_dados.iloc[:, 0] == '#P0061']

if len(projeto_p0061) > 0:
    print("✅ Projeto #P0061 encontrado no Excel")
    row = projeto_p0061.iloc[0]
    print(f"\nDados relevantes:")
    print(f"   Número (col 0): {row.iloc[0]}")
    print(f"   Cliente (col 1): {row.iloc[1]}")
    print(f"   Descrição (col 4): {row.iloc[4]}")
    print(f"   Valor sem IVA (col 5): {row.iloc[5]}")
    print(f"   Data faturação (col 6): {row.iloc[6]}")
    print(f"   Data vencimento (col 7): {row.iloc[7]}")
    print(f"   Data recebimento (col 8): {row.iloc[8]}")
    print(f"   Estado/Tipo (col 14): {row.iloc[14] if len(row) > 14 else 'N/A'}")
    print(f"   Owner (col 15): {row.iloc[15] if len(row) > 15 else 'N/A'}")

    # Verificar se tem data de recebimento
    data_recebimento = row.iloc[8]
    if pd.notna(data_recebimento):
        print(f"\n✅ TEM data de recebimento: {data_recebimento}")
    else:
        print(f"\n❌ NÃO TEM data de recebimento (col 8 vazia)")

    # Verificar data de vencimento
    data_vencimento = row.iloc[7]
    if pd.notna(data_vencimento):
        print(f"✅ TEM data de vencimento: {data_vencimento}")

# ============================================================================
# 4. Listar primeiros 5 projetos para comparação
# ============================================================================
print("\n" + "=" * 80)
print("4️⃣  PRIMEIROS 5 PROJETOS (para comparação)")
print("=" * 80)

primeiros = df_projetos_dados.head(5)
for idx, row in primeiros.iterrows():
    numero = row.iloc[0]
    descricao = row.iloc[4]
    data_rec = row.iloc[8] if len(row) > 8 and pd.notna(row.iloc[8]) else "N/A"
    data_fat = row.iloc[6] if len(row) > 6 and pd.notna(row.iloc[6]) else "N/A"
    print(f"\n{numero}: {descricao}")
    print(f"   Data faturação: {data_fat}")
    print(f"   Data recebimento: {data_rec}")

print("\n" + "=" * 80)
