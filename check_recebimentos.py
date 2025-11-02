# -*- coding: utf-8 -*-
import pandas as pd

df = pd.read_excel('CONTABILIDADE_FINAL_20251102.xlsx', sheet_name='PROJETOS', header=None)

# Encontrar linha com headers
header_idx = None
for idx, row in df.iterrows():
    if 'Nº PROJETO' in str(row[0]) or 'PROJETO' in str(row.values):
        header_idx = idx
        break

if header_idx is None:
    print("❌ Headers não encontrados")
    exit(1)

# Ler com o header correto
df_proj = pd.read_excel('CONTABILIDADE_FINAL_20251102.xlsx', sheet_name='PROJETOS', header=header_idx)

print("=" * 90)
print("RECEBIMENTOS NO EXCEL - PROJETOS COM PRÉMIOS FATURADOS")
print("=" * 90)

projetos = ['#P0038', '#P0049', '#P0051', '#P0054', '#P0055', '#P0056', '#P0063', '#P0065']

for p in projetos:
    proj_rows = df_proj[df_proj['Nº PROJETO'] == p]

    if not proj_rows.empty:
        try:
            recibo = proj_rows['DATA RECIBO'].values[0]
            tem_recibo = pd.notna(recibo)
            status = "✅ RECEBIDO" if tem_recibo else "❌ NÃO RECEBIDO"
            print(f"{p:<10} {status:<20} | Recibo: {recibo if tem_recibo else 'N/A'}")
        except KeyError:
            print(f"{p:<10} ⚠️  Coluna 'DATA RECIBO' não encontrada")
    else:
        print(f"{p:<10} ⚠️  Projeto não encontrado no Excel")

print("=" * 90)
