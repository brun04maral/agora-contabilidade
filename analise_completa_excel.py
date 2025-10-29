#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ANÁLISE COMPLETA E RÁPIDA DO EXCEL NOVO
"""
import pandas as pd
from decimal import Decimal
from datetime import date

excel_path = 'CONTABILIDADE_FINAL_20251029.xlsx'
xl = pd.ExcelFile(excel_path)

print("=" * 80)
print("🔍 ANÁLISE COMPLETA - EXCEL ATUALIZADO")
print("=" * 80)

# ============================================================================
# 1. VERIFICAR #P0001
# ============================================================================
print("\n1️⃣ VERIFICANDO #P0001...")

df_proj = pd.read_excel(xl, sheet_name='PROJETOS', header=3)
df_proj_dados = df_proj[df_proj.iloc[:, 0].astype(str).str.startswith('#P', na=False)]

p0001 = df_proj_dados[df_proj_dados.iloc[:, 0] == '#P0001']
if len(p0001) > 0:
    print(f"✅ #P0001 EXISTE!")
    row = p0001.iloc[0]
    print(f"   Cliente: {row.iloc[1]}")
    print(f"   Descrição: {row.iloc[4]}")
    print(f"   Valor s/IVA: €{float(row.iloc[5]):,.2f}")
    print(f"   Data recebimento: {row.iloc[8]}")
else:
    print("❌ #P0001 NÃO ENCONTRADO")

# Contar projetos
print(f"\nTotal projetos no Excel: {len(df_proj_dados)}")
print(f"Primeiro: {df_proj_dados.iloc[0, 0]}")
print(f"Último: {df_proj_dados.iloc[-1, 0]}")

# ============================================================================
# 2. ANÁLISE DE PRÉMIOS
# ============================================================================
print("\n" + "=" * 80)
print("2️⃣ ANÁLISE DE PRÉMIOS...")
print("=" * 80)

df_desp = pd.read_excel(xl, sheet_name='DESPESAS', header=5)
df_desp_dados = df_desp[df_desp.iloc[:, 0].astype(str).str.startswith('#D', na=False)]

# Prémios
premios = df_desp_dados[df_desp_dados.iloc[:, 6].astype(str).str.contains('prém', case=False, na=False)]

print(f"\nTotal prémios: {len(premios)}")

premios_bruno = Decimal('0')
premios_rafael = Decimal('0')

print("\nLista de prémios:")
for idx, row in premios.iterrows():
    numero = row.iloc[0]
    projeto = row.iloc[5]
    credor = row.iloc[4]
    valor = Decimal(str(row.iloc[16])) if pd.notna(row.iloc[16]) else Decimal(str(row.iloc[9]))

    if 'bruno' in str(credor).lower():
        premios_bruno += valor
        print(f"  {numero}: Bruno €{float(valor):,.2f} → {projeto}")
    elif 'rafael' in str(credor).lower():
        premios_rafael += valor
        print(f"  {numero}: Rafael €{float(valor):,.2f} → {projeto}")

print(f"\n💰 Total Bruno: €{float(premios_bruno):,.2f}")
print(f"💰 Total Rafael: €{float(premios_rafael):,.2f}")

# ============================================================================
# 3. DESPESAS FIXAS
# ============================================================================
print("\n" + "=" * 80)
print("3️⃣ ANÁLISE DE DESPESAS FIXAS...")
print("=" * 80)

# Despesas com periodicidade "Mensal" OU tipo "Ordenado"
fixas_mensais = df_desp_dados[
    (df_desp_dados.iloc[:, 8].astype(str).str.contains('mensal', case=False, na=False)) |
    (df_desp_dados.iloc[:, 6].astype(str).str.contains('ordenado', case=False, na=False))
]

print(f"\nTotal despesas fixas mensais: {len(fixas_mensais)}")

# Filtrar as que já venceram (até 29/10/2025)
hoje = date(2025, 10, 29)
total_fixas = Decimal('0')
count_pagas = 0

for idx, row in fixas_mensais.iterrows():
    ano = row.iloc[1]
    mes = row.iloc[2]
    dia = row.iloc[3]

    if pd.notna(ano) and pd.notna(mes) and pd.notna(dia):
        try:
            data_venc = date(int(ano), int(mes), int(dia))
            if data_venc <= hoje:
                valor = Decimal(str(row.iloc[16])) if pd.notna(row.iloc[16]) else Decimal(str(row.iloc[12]))
                total_fixas += valor
                count_pagas += 1
        except:
            pass

print(f"Despesas fixas PAGAS (até {hoje}): {count_pagas}")
print(f"💰 Total: €{float(total_fixas):,.2f}")
print(f"➗ Por sócio: €{float(total_fixas / 2):,.2f}")

# ============================================================================
# 4. DESPESAS PESSOAIS
# ============================================================================
print("\n" + "=" * 80)
print("4️⃣ ANÁLISE DE DESPESAS PESSOAIS...")
print("=" * 80)

# Procurar despesas pessoais (tipo contém "Pessoal" mas NÃO tem vírgula antes)
# ", Pessoal" = Boletim
# "Pessoal" sem vírgula = Despesa pessoal
despesas_pessoais = df_desp_dados[
    (df_desp_dados.iloc[:, 6].astype(str).str.contains('pessoal', case=False, na=False)) &
    (~df_desp_dados.iloc[:, 6].astype(str).str.contains(', pessoal', case=False, na=False))
]

print(f"\nTotal despesas pessoais: {len(despesas_pessoais)}")

if len(despesas_pessoais) > 0:
    print("\nListagem:")
    for idx, row in despesas_pessoais.iterrows():
        numero = row.iloc[0]
        credor = row.iloc[4]
        tipo = row.iloc[6]
        descricao = row.iloc[7]
        valor = row.iloc[16] if pd.notna(row.iloc[16]) else row.iloc[12]
        print(f"  {numero}: {credor} - {tipo} - €{float(valor):,.2f}")

# ============================================================================
# 5. RESUMO COMPARATIVO
# ============================================================================
print("\n" + "=" * 80)
print("📊 RESUMO COMPARATIVO")
print("=" * 80)

print("\n| Item | Excel Novo | BD Atual | Status |")
print("|------|------------|----------|--------|")
print(f"| Prémios Bruno | €{float(premios_bruno):,.2f} | €3,111.25 | {'✅' if abs(float(premios_bruno) - 3111.25) < 1 else '❌'} |")
print(f"| Prémios Rafael | €{float(premios_rafael):,.2f} | €6,140.17 | {'✅' if abs(float(premios_rafael) - 6140.17) < 1 else '❌'} |")
print(f"| Despesas fixas ÷2 | €{float(total_fixas/2):,.2f} | €12,571.00 | {'✅' if abs(float(total_fixas/2) - 12571) < 1 else '❌'} |")

print("\n" + "=" * 80)
