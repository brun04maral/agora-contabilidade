# -*- coding: utf-8 -*-
"""
Script para analisar prémios no ficheiro Excel
"""
import pandas as pd
import sys

try:
    # Ler ficheiro Excel
    print("=" * 80)
    print("ANÁLISE DO FICHEIRO EXCEL - PRÉMIOS")
    print("=" * 80)

    # Ler todas as sheets
    xls = pd.ExcelFile('CONTABILIDADE_FINAL_20251102.xlsx')
    print(f"\n📋 Sheets disponíveis: {xls.sheet_names}\n")

    # Procurar sheet de projetos (pode ter nomes diferentes)
    possible_sheets = ['Projetos', 'PROJETOS', 'projetos', 'Faturação', 'FATURACAO']

    for sheet_name in xls.sheet_names:
        print(f"\n{'='*80}")
        print(f"SHEET: {sheet_name}")
        print(f"{'='*80}")

        df = pd.read_excel('CONTABILIDADE_FINAL_20251102.xlsx', sheet_name=sheet_name)
        print(f"\nColunas: {list(df.columns)}")
        print(f"\nPrimeiras 3 linhas:")
        print(df.head(3))

        # Procurar colunas relacionadas com prémios
        premio_cols = [col for col in df.columns if 'prémio' in str(col).lower() or 'premio' in str(col).lower() or 'bruno' in str(col).lower() or 'rafael' in str(col).lower()]

        if premio_cols:
            print(f"\n⭐ Colunas de prémios encontradas: {premio_cols}")
            print(f"\nDados dos prémios:")
            print(df[premio_cols])

except Exception as e:
    print(f"❌ Erro ao ler Excel: {e}")
    import traceback
    traceback.print_exc()
