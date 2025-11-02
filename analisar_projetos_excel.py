# -*- coding: utf-8 -*-
"""
Script para analisar a estrutura da sheet PROJETOS
"""
import pandas as pd
import numpy as np

try:
    print("=" * 100)
    print("ANÁLISE DETALHADA DA SHEET PROJETOS")
    print("=" * 100)

    # Ler sheet PROJETOS sem header automático
    df = pd.read_excel('CONTABILIDADE_FINAL_20251102.xlsx', sheet_name='PROJETOS', header=None)

    # Procurar a linha com os headers (normalmente contém "Nº PROJETO")
    header_row = None
    for idx, row in df.iterrows():
        if any('Nº PROJETO' in str(cell) or 'PROJETO' in str(cell) for cell in row if pd.notna(cell)):
            header_row = idx
            print(f"\n✓ Header encontrado na linha {idx}")
            print(f"Headers: {list(row[:20])}")
            break

    if header_row is not None:
        # Usar essa linha como header e ler as linhas seguintes como dados
        df_projetos = pd.read_excel('CONTABILIDADE_FINAL_20251102.xlsx', sheet_name='PROJETOS', header=header_row)
        print(f"\n\n📊 DataFrame com headers corretos:")
        print(f"Colunas: {list(df_projetos.columns)}")
        print(f"\nShape: {df_projetos.shape}")

        # Procurar colunas relacionadas com prémios
        premio_cols = [col for col in df_projetos.columns if pd.notna(col) and ('prémio' in str(col).lower() or 'premio' in str(col).lower() or 'bruno' in str(col).lower() or 'rafael' in str(col).lower())]

        if premio_cols:
            print(f"\n⭐ Colunas de prémios encontradas: {premio_cols}")

        # Mostrar primeiros projetos com todas as colunas relevantes
        relevant_cols = [col for col in df_projetos.columns if pd.notna(col)][:15]
        print(f"\n\nPrimeiros 10 projetos:")
        print(df_projetos[relevant_cols].head(10).to_string())

        # Se houver colunas de prémios, mostrar só essas
        if premio_cols:
            print(f"\n\nDados dos prémios (todas as linhas):")
            num_project_col = [col for col in df_projetos.columns if 'Nº PROJETO' in str(col) or 'PROJETO' == str(col)]
            if num_project_col:
                print(df_projetos[num_project_col + premio_cols].dropna(how='all').to_string())

except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()
