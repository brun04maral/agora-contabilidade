#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Análise COMPLETA do Excel para entender a lógica real
"""
import pandas as pd


def mostrar_aba(nome_aba, header_row, max_exemplos=10):
    """Mostra estrutura e exemplos de uma aba"""
    print("\n" + "=" * 80)
    print(f"📋 ABA: {nome_aba}")
    print("=" * 80)

    xl = pd.ExcelFile('CONTABILIDADE_FINAL.xlsx')

    try:
        df = pd.read_excel(xl, sheet_name=nome_aba, header=header_row)

        print(f"Total de linhas: {len(df)}")
        print(f"Total de colunas: {len(df.columns)}")
        print()

        print("📌 COLUNAS:")
        for i, col in enumerate(df.columns, 1):
            print(f"  {i:2}. {col}")
        print()

        # Filtrar apenas linhas que parecem ser dados reais
        # (começam com # na primeira coluna)
        primeira_col = str(df.columns[0])
        if primeira_col.startswith('#'):
            # Primeira linha já é dados
            dados_reais = df
        else:
            # Filtrar linhas que começam com #
            dados_reais = df[df.iloc[:, 0].astype(str).str.startswith('#', na=False)]

        print(f"📊 Linhas de dados reais: {len(dados_reais)}")
        print()

        if len(dados_reais) > 0:
            print(f"🔍 EXEMPLOS ({min(max_exemplos, len(dados_reais))} primeiros registos):")
            print()

            pd.set_option('display.max_columns', None)
            pd.set_option('display.width', 200)
            pd.set_option('display.max_colwidth', 60)

            for idx, (row_idx, row) in enumerate(dados_reais.head(max_exemplos).iterrows(), 1):
                print(f"--- Registo {idx} ---")
                for col_name, value in row.items():
                    if pd.notna(value) and str(value).strip():
                        print(f"  {col_name}: {value}")
                print()

        return df

    except Exception as e:
        print(f"❌ Erro ao ler aba: {e}")
        import traceback
        traceback.print_exc()
        return None


def analisar_tipos_projeto():
    """Analisa os diferentes tipos de projetos"""
    print("\n" + "=" * 80)
    print("🎬 ANÁLISE DE TIPOS DE PROJETO")
    print("=" * 80)

    xl = pd.ExcelFile('CONTABILIDADE_FINAL.xlsx')
    df = pd.read_excel(xl, sheet_name='PROJETOS', header=3)

    # Filtrar linhas de dados
    dados = df[df.iloc[:, 0].astype(str).str.startswith('#P', na=False)]

    # Coluna 14 parece ser o estado/tipo, coluna 15 é owner
    if len(dados.columns) > 14:
        col_estado = dados.columns[14]
        col_owner = dados.columns[15] if len(dados.columns) > 15 else None

        print(f"Coluna ESTADO/TIPO (14): {col_estado}")
        if col_owner:
            print(f"Coluna OWNER (15): {col_owner}")
        print()

        # Valores únicos
        valores_estado = dados.iloc[:, 14].dropna().unique()
        print(f"Valores únicos em ESTADO ({len(valores_estado)}):")
        for v in valores_estado[:20]:
            count = (dados.iloc[:, 14] == v).sum()
            print(f"  • {v}: {count} projetos")

        if col_owner:
            print()
            valores_owner = dados.iloc[:, 15].dropna().unique()
            print(f"Valores únicos em OWNER ({len(valores_owner)}):")
            for v in valores_owner[:20]:
                count = (dados.iloc[:, 15] == v).sum()
                print(f"  • {v}: {count} projetos")


def analisar_tipos_despesa():
    """Analisa os diferentes tipos de despesas"""
    print("\n" + "=" * 80)
    print("💸 ANÁLISE DE TIPOS DE DESPESA")
    print("=" * 80)

    xl = pd.ExcelFile('CONTABILIDADE_FINAL.xlsx')
    df = pd.read_excel(xl, sheet_name='DESPESAS', header=5)

    # Filtrar linhas de dados
    dados = df[df.iloc[:, 0].astype(str).str.startswith('#D', na=False)]

    # Coluna 6 é TIPO, coluna 8 é PERIODICIDADE
    col_tipo = dados.columns[6]
    col_period = dados.columns[8]

    print(f"Coluna TIPO (6): {col_tipo}")
    print(f"Coluna PERIODICIDADE (8): {col_period}")
    print()

    # Valores únicos de TIPO
    valores_tipo = dados.iloc[:, 6].dropna().unique()
    print(f"Valores únicos em TIPO ({len(valores_tipo)}):")
    for v in sorted(valores_tipo)[:30]:
        count = (dados.iloc[:, 6] == v).sum()
        print(f"  • {v}: {count} despesas")

    print()

    # Valores únicos de PERIODICIDADE
    valores_period = dados.iloc[:, 8].dropna().unique()
    print(f"Valores únicos em PERIODICIDADE ({len(valores_period)}):")
    for v in valores_period:
        count = (dados.iloc[:, 8] == v).sum()
        print(f"  • {v}: {count} despesas")


def analisar_cargos():
    """Analisa a aba CARGOS (provavelmente boletins/ordenados)"""
    print("\n" + "=" * 80)
    print("👤 ANÁLISE DA ABA CARGOS")
    print("=" * 80)

    xl = pd.ExcelFile('CONTABILIDADE_FINAL.xlsx')

    # Ler as primeiras linhas para entender a estrutura
    df_raw = pd.read_excel(xl, sheet_name='CARGOS', header=None)

    print("Estrutura bruta (primeiras 20 linhas):")
    print(df_raw.head(20).to_string())


def main():
    print("=" * 80)
    print("🔍 ANÁLISE COMPLETA DO EXCEL")
    print("=" * 80)

    # Analisar cada aba principal
    mostrar_aba('CLIENTES', header_row=1, max_exemplos=5)
    mostrar_aba('FORNECEDORES', header_row=1, max_exemplos=5)
    mostrar_aba('PROJETOS', header_row=3, max_exemplos=10)
    mostrar_aba('DESPESAS', header_row=5, max_exemplos=10)

    # Análises específicas
    analisar_tipos_projeto()
    analisar_tipos_despesa()
    analisar_cargos()

    print("\n" + "=" * 80)
    print("✅ ANÁLISE CONCLUÍDA")
    print("=" * 80)


if __name__ == '__main__':
    main()
