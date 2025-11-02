# -*- coding: utf-8 -*-
"""
Script para buscar campos de prémios na sheet PROJETOS
"""
import pandas as pd

try:
    # Ler sheet PROJETOS - linha 1 tem os headers reais
    df = pd.read_excel('CONTABILIDADE_FINAL_20251102.xlsx', sheet_name='PROJETOS', header=1)

    print("=" * 100)
    print("TODAS AS COLUNAS DA SHEET PROJETOS")
    print("=" * 100)

    for idx, col in enumerate(df.columns):
        print(f"{idx:2d}. {col}")

    # Procurar colunas com "prémio", "bruno", "rafael"
    print("\n" + "=" * 100)
    print("COLUNAS RELACIONADAS COM PRÉMIOS")
    print("=" * 100)

    premio_related = []
    for idx, col in enumerate(df.columns):
        col_str = str(col).lower()
        if 'prémio' in col_str or 'premio' in col_str or 'prêmio' in col_str or 'bruno' in col_str or 'rafael' in col_str:
            premio_related.append((idx, col))
            print(f"✓ Coluna {idx}: {col}")

    if not premio_related:
        print("\n⚠️  Nenhuma coluna de prémios encontrada nos headers.")
        print("\nMostrando todas as colunas (30 primeiros caracteres):")
        for idx, col in enumerate(df.columns):
            print(f"  {idx:2d}. {str(col)[:50]}")

    # Verificar se há dados de prémios em alguma linha
    print("\n" + "=" * 100)
    print("PROCURANDO PALAVRA 'PRÉMIO' NAS PRIMEIRAS 20 LINHAS")
    print("=" * 100)

    for row_idx in range(min(20, len(df))):
        row = df.iloc[row_idx]
        for col_idx, val in enumerate(row):
            val_str = str(val).lower()
            if 'prémio' in val_str or 'premio' in val_str:
                print(f"Linha {row_idx}, Coluna {col_idx} ({df.columns[col_idx]}): {val}")

except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()
