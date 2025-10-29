#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Análise detalhada do Excel - encontra onde começam os dados reais
"""
import pandas as pd


def encontrar_linha_cabecalho(xl, nome_aba, palavra_chave="#"):
    """
    Encontra a linha onde está o cabeçalho real (procura por palavra_chave)
    """
    # Ler sem header para ver todas as linhas
    df_raw = pd.read_excel(xl, sheet_name=nome_aba, header=None)

    for idx, row in df_raw.iterrows():
        # Procurar por palavra chave na primeira coluna
        primeira_col = str(row[0])
        if palavra_chave in primeira_col:
            return idx

    return None


def analisar_aba_detalhada(xl, nome_aba, palavra_chave_header="#"):
    """Analisa aba encontrando o cabeçalho correto"""
    print("=" * 80)
    print(f"📋 ABA: {nome_aba}")
    print("=" * 80)

    try:
        # Encontrar linha do cabeçalho
        linha_header = encontrar_linha_cabecalho(xl, nome_aba, palavra_chave_header)

        if linha_header is None:
            print(f"⚠️  Não encontrei cabeçalho com '{palavra_chave_header}'")
            # Tentar ler normalmente
            df = pd.read_excel(xl, sheet_name=nome_aba)
        else:
            print(f"✅ Cabeçalho encontrado na linha {linha_header}")
            # Ler a partir da linha do cabeçalho
            df = pd.read_excel(xl, sheet_name=nome_aba, header=linha_header)

        print(f"Total de linhas de dados: {len(df)}")
        print(f"Total de colunas: {len(df.columns)}")
        print()

        print("Colunas:")
        for i, col in enumerate(df.columns, 1):
            print(f"  {i:2}. {col}")
        print()

        if len(df) > 0:
            print(f"Primeiros 5 registos:")
            # Mostrar sem truncar
            pd.set_option('display.max_columns', None)
            pd.set_option('display.width', None)
            pd.set_option('display.max_colwidth', 40)
            print(df.head(5).to_string(index=False))
        else:
            print("⚠️  Sem dados")

        print()
        return df

    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        print()
        return None


def analisar_premios(xl):
    """Análise específica da aba CONSULTA_PREMIOS"""
    print("=" * 80)
    print("🏆 ABA: CONSULTA_PREMIOS (Análise Especial)")
    print("=" * 80)

    # Ler sem header para ver estrutura
    df_raw = pd.read_excel(xl, sheet_name='CONSULTA_PREMIOS', header=None)

    print("Estrutura bruta (primeiras 10 linhas):")
    print(df_raw.head(10).to_string())
    print()

    # Procurar valores de prémios
    print("Procurando valores de prémios...")
    for idx, row in df_raw.iterrows():
        for col_idx, value in enumerate(row):
            if isinstance(value, (int, float)) and value > 1000 and value < 10000:
                print(f"  Linha {idx}, Coluna {col_idx}: {value}")

    print()


def main():
    print("=" * 80)
    print("🔍 ANÁLISE DETALHADA DO EXCEL")
    print("=" * 80)
    print()

    xl = pd.ExcelFile('CONTABILIDADE_FINAL.xlsx')

    # Analisar CLIENTES
    print("\n📌 CLIENTES:")
    df_clientes = analisar_aba_detalhada(xl, 'CLIENTES', palavra_chave_header="#C")

    # Analisar FORNECEDORES
    print("\n📌 FORNECEDORES:")
    df_fornecedores = analisar_aba_detalhada(xl, 'FORNECEDORES', palavra_chave_header="#F")

    # Analisar PROJETOS
    print("\n📌 PROJETOS:")
    df_projetos = analisar_aba_detalhada(xl, 'PROJETOS', palavra_chave_header="#P")

    # Analisar DESPESAS
    print("\n📌 DESPESAS:")
    df_despesas = analisar_aba_detalhada(xl, 'DESPESAS', palavra_chave_header="#D")

    # Análise especial de prémios
    print("\n📌 PRÉMIOS:")
    analisar_premios(xl)

    print("=" * 80)
    print("✅ ANÁLISE CONCLUÍDA")
    print("=" * 80)


if __name__ == '__main__':
    main()
