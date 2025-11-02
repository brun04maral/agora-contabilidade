# -*- coding: utf-8 -*-
"""
Script para extrair prémios específicos do Excel
"""
import pandas as pd

try:
    print("=" * 80)
    print("EXTRAÇÃO DE PRÉMIOS DO EXCEL")
    print("=" * 80)

    # Ler sheet CONSULTA_PREMIOS
    df_premios = pd.read_excel('CONTABILIDADE_FINAL_20251102.xlsx', sheet_name='CONSULTA_PREMIOS')

    print("\n📋 SHEET: CONSULTA_PREMIOS")
    print(f"\nColunas: {list(df_premios.columns)}")
    print(f"\nShape: {df_premios.shape}")
    print(f"\nTodas as linhas:")
    print(df_premios.to_string())

    # Também vamos ver a sheet PROJETOS para encontrar os prémios
    print("\n\n" + "=" * 80)
    print("SHEET: PROJETOS (procurando prémios)")
    print("=" * 80)

    df_projetos = pd.read_excel('CONTABILIDADE_FINAL_20251102.xlsx', sheet_name='PROJETOS', header=None)
    print(f"\nShape: {df_projetos.shape}")

    # Procurar linhas que contenham "prémio" ou "premio"
    for idx, row in df_projetos.iterrows():
        row_str = ' '.join([str(x) for x in row if pd.notna(x)]).lower()
        if 'prémio' in row_str or 'premio' in row_str or 'prêmio' in row_str:
            print(f"\nLinha {idx}: {list(row[:15])}")

except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()
