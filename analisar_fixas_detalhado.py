# -*- coding: utf-8 -*-
"""
Analisar despesas fixas usando índices de coluna das fórmulas
"""
import pandas as pd

try:
    print("=" * 100)
    print("DESPESAS FIXAS MENSAIS - ANÁLISE DETALHADA")
    print("=" * 100)

    # Ler sheet DESPESAS
    # Pela fórmula: Coluna P (16) = valor s/IVA, Coluna I (9) = periodicidade, Coluna T (20) = data pagamento
    df = pd.read_excel('CONTABILIDADE_FINAL_20251102.xlsx', sheet_name='DESPESAS', header=5)

    print(f"\nTotal de linhas: {len(df)}")
    print(f"Colunas disponíveis: {len(df.columns)}")

    # Usar índices de coluna (0-indexed, então P=15, I=8, T=19)
    # Mas o header está na linha 5, então preciso ajustar

    # Vou ler sem header e processar manualmente
    df_raw = pd.read_excel('CONTABILIDADE_FINAL_20251102.xlsx', sheet_name='DESPESAS', header=None)

    print(f"\n📋 Headers (linha 6):")
    headers_row = 5  # 0-indexed
    for idx, val in enumerate(df_raw.iloc[headers_row][:25]):
        if pd.notna(val):
            print(f"  Col {idx} ({chr(65+idx) if idx < 26 else 'AA+'}): {val}")

    # Pegar dados a partir da linha 7 (índice 6)
    df_data = df_raw.iloc[6:].copy()
    df_data.columns = df_raw.iloc[5]  # Usar linha 6 como header

    # Identificar colunas
    # P = coluna 15 (0-indexed)
    # I = coluna 8
    # T = coluna 19

    valor_col_idx = 15  # P
    periodicidade_col_idx = 8  # I
    data_pago_col_idx = 19  # T
    numero_col_idx = 0  # A

    # Filtrar despesas fixas mensais PAGAS
    print("\n\n" + "=" * 100)
    print("FILTRAR DESPESAS FIXAS MENSAIS PAGAS")
    print("=" * 100)

    # Filtro 1: Periodicidade = "Mensal"
    mask_mensal = df_data.iloc[:, periodicidade_col_idx].astype(str).str.contains('Mensal', case=False, na=False)

    # Filtro 2: Data de pagamento não vazia
    mask_pago = df_data.iloc[:, data_pago_col_idx].notna()

    # Combinar filtros
    fixas_pagas = df_data[mask_mensal & mask_pago].copy()

    print(f"\nTotal de despesas fixas mensais PAGAS: {len(fixas_pagas)}")

    # Somar valores
    valores = fixas_pagas.iloc[:, valor_col_idx]
    total = valores.sum()

    print(f"\n💰 TOTAL (s/IVA): €{total:,.2f}")
    print(f"   Por sócio (÷2): €{total/2:,.2f}")

    # Comparar com Excel
    excel_por_socio = 12315.70
    print(f"\n📊 COMPARAÇÃO:")
    print(f"   Excel mostra: €{excel_por_socio:,.2f} por sócio")
    print(f"   DB tem: €9,426.70 por sócio")
    print(f"   Calculado agora: €{total/2:,.2f} por sócio")

    diferenca = excel_por_socio - (total/2)
    print(f"\n   Diferença Excel vs Calculado: €{diferenca:,.2f}")

    # Mostrar algumas despesas
    print(f"\n\nPrimeiras 30 despesas fixas mensais PAGAS:")
    print("-" * 100)
    for idx, row in fixas_pagas.head(30).iterrows():
        numero = row.iloc[numero_col_idx]
        valor = row.iloc[valor_col_idx]
        desc = row.iloc[4] if len(row) > 4 else ''  # Coluna E geralmente é descrição
        print(f"  {numero} | €{valor:>8,.2f} | {str(desc)[:60]}")

    print("\n" + "=" * 100)

except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()
