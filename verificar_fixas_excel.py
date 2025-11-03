# -*- coding: utf-8 -*-
"""
Verificar despesas fixas mensais no Excel
"""
import pandas as pd

try:
    # Ler despesas do Excel
    df = pd.read_excel('CONTABILIDADE_FINAL_20251102.xlsx', sheet_name='DESPESAS', header=None)

    # Encontrar linha com headers
    header_idx = None
    for idx, row in df.iterrows():
        if 'Nº DESPESA' in str(row.values) or 'DESPESA' in str(row.values):
            header_idx = idx
            break

    if header_idx is None:
        print("❌ Headers não encontrados")
        exit(1)

    # Ler com header correto
    df_desp = pd.read_excel('CONTABILIDADE_FINAL_20251102.xlsx', sheet_name='DESPESAS', header=header_idx)

    print("=" * 100)
    print("DESPESAS FIXAS MENSAIS NO EXCEL")
    print("=" * 100)

    # Procurar coluna de tipo
    tipo_col = None
    num_col = None
    valor_col = None
    pago_col = None

    for col in df_desp.columns:
        if 'TIPO' in str(col).upper() or 'PERIODICIDADE' in str(col).upper():
            tipo_col = col
        if 'Nº DESPESA' in str(col) or 'DESPESA' in str(col):
            num_col = col
        if 'TOTAL' in str(col).upper() and 'IVA' in str(col).upper() and 's/' in str(col):
            valor_col = col
        if 'DATA' in str(col).upper() and ('PAGO' in str(col).upper() or 'PAGAMENTO' in str(col).upper()):
            pago_col = col

    print(f"\nColunas encontradas:")
    print(f"  Número: {num_col}")
    print(f"  Tipo: {tipo_col}")
    print(f"  Valor: {valor_col}")
    print(f"  Data pagamento: {pago_col}")

    if tipo_col and num_col and valor_col:
        # Filtrar despesas fixas mensais
        fixas = df_desp[df_desp[tipo_col].astype(str).str.contains('Mensal', case=False, na=False)]

        print(f"\n\nTotal de despesas fixas mensais: {len(fixas)}")

        # Filtrar pagas (têm data de pagamento)
        if pago_col:
            pagas = fixas[fixas[pago_col].notna()]
            print(f"Despesas fixas mensais PAGAS: {len(pagas)}")

            total = pagas[valor_col].sum()
            print(f"\nTotal PAGO (s/IVA): €{total:,.2f}")
            print(f"Por sócio (÷2): €{total/2:,.2f}")

            # Mostrar algumas
            print(f"\nPrimeiras 20 despesas fixas PAGAS:")
            for idx, row in pagas.head(20).iterrows():
                num = row[num_col] if num_col else '?'
                valor = row[valor_col] if pd.notna(row[valor_col]) else 0
                desc = row[df_desp.columns[4]] if len(df_desp.columns) > 4 else ''
                print(f"  {num} | €{valor:>8,.2f} | {str(desc)[:50]}")
        else:
            total = fixas[valor_col].sum()
            print(f"\nTotal (todas): €{total:,.2f}")
            print(f"Por sócio (÷2): €{total/2:,.2f}")

    print("\n" + "=" * 100)

except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()
