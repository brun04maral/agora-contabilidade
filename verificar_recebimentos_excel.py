# -*- coding: utf-8 -*-
"""
Script para verificar se projetos têm data de recebimento no Excel
"""
import pandas as pd

try:
    # Projetos que estão FATURADOS mas não RECEBIDOS na DB
    projetos_verificar = ['#P0038', '#P0049', '#P0051', '#P0054', '#P0055', '#P0056', '#P0063', '#P0065']

    df = pd.read_excel('CONTABILIDADE_FINAL_20251102.xlsx', sheet_name='PROJETOS', header=1)

    print("=" * 100)
    print("VERIFICAR RECEBIMENTOS NO EXCEL")
    print("=" * 100)

    print(f"\nProcurando projetos: {', '.join(projetos_verificar)}")
    print(f"\nColunas disponíveis: {list(df.columns[:15])}")

    # Procurar coluna de número de projeto
    num_col = None
    recibo_col = None

    for col in df.columns:
        if 'PROJETO' in str(col).upper() and 'Nº' in str(col):
            num_col = col
        if 'RECIBO' in str(col).upper():
            recibo_col = col

    print(f"\nColuna de número: {num_col}")
    print(f"Coluna de recibo: {recibo_col}")

    if num_col:
        print("\n" + "=" * 100)
        print("PROJETOS COM PRÉMIOS - ESTADO DE RECEBIMENTO")
        print("=" * 100)

        for proj_num in projetos_verificar:
            projeto = df[df[num_col] == proj_num]

            if not projeto.empty:
                if recibo_col and recibo_col in projeto.columns:
                    data_recibo = projeto[recibo_col].values[0]
                    tem_recibo = pd.notna(data_recibo)
                    print(f"\n{proj_num}: {'✅ TEM recibo' if tem_recibo else '❌ SEM recibo'} | {data_recibo if tem_recibo else 'N/A'}")
                else:
                    print(f"\n{proj_num}: ⚠️  Coluna de recibo não encontrada")

                # Mostrar algumas colunas relevantes
                print(f"  Colunas: {list(projeto.iloc[0][:10])}")

except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()
