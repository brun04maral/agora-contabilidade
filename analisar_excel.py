#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para analisar a estrutura do Excel CONTABILIDADE_FINAL.xlsx
Mostra as colunas e primeiros registos de cada aba
"""
import pandas as pd


def analisar_aba(xl, nome_aba, max_rows=5):
    """Analisa uma aba do Excel"""
    print("=" * 80)
    print(f"📋 ABA: {nome_aba}")
    print("=" * 80)

    try:
        df = pd.read_excel(xl, sheet_name=nome_aba)

        print(f"Total de linhas: {len(df)}")
        print(f"Total de colunas: {len(df.columns)}")
        print()

        print("Colunas:")
        for i, col in enumerate(df.columns, 1):
            print(f"  {i:2}. {col}")
        print()

        if len(df) > 0:
            print(f"Primeiros {min(max_rows, len(df))} registos:")
            print(df.head(max_rows).to_string())
        else:
            print("⚠️  Aba vazia")

        print()

    except Exception as e:
        print(f"❌ Erro ao ler aba: {e}")
        print()


def main():
    print("=" * 80)
    print("🔍 ANÁLISE DO EXCEL: CONTABILIDADE_FINAL.xlsx")
    print("=" * 80)
    print()

    # Abrir Excel
    xl = pd.ExcelFile('CONTABILIDADE_FINAL.xlsx')

    print(f"Total de abas: {len(xl.sheet_names)}")
    print()

    # Abas principais para analisar (em ordem de importância)
    abas_principais = [
        'CLIENTES',
        'FORNECEDORES',
        'PROJETOS',
        'DESPESAS',
        'CONSULTA_PREMIOS',
        'CARGOS',
    ]

    print("🎯 Analisando abas principais:")
    print()

    for aba in abas_principais:
        if aba in xl.sheet_names:
            analisar_aba(xl, aba, max_rows=3)
        else:
            print(f"⚠️  Aba '{aba}' não encontrada")
            print()

    print("=" * 80)
    print("✅ ANÁLISE CONCLUÍDA")
    print("=" * 80)
    print()
    print("Outras abas disponíveis:")
    outras = [a for a in xl.sheet_names if a not in abas_principais]
    for aba in outras:
        print(f"  • {aba}")
    print()


if __name__ == '__main__':
    main()
