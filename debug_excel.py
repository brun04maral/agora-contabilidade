#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Análise detalhada para debugging - identificar problemas
"""
import pandas as pd
from decimal import Decimal


def analisar_premios():
    """Analisa prémios no Excel"""
    print("\n" + "=" * 80)
    print("🏆 ANÁLISE DE PRÉMIOS")
    print("=" * 80)

    xl = pd.ExcelFile('CONTABILIDADE_FINAL.xlsx')
    df = pd.read_excel(xl, sheet_name='DESPESAS', header=5)

    # Filtrar prémios
    df_dados = df[df.iloc[:, 0].astype(str).str.startswith('#D', na=False)]
    premios = df_dados[df_dados.iloc[:, 6].astype(str).str.contains('rém', case=False, na=True)]

    print(f"Total de prémios: {len(premios)}")
    print()

    total_bruno = Decimal('0')
    total_rafael = Decimal('0')

    print("Prémios detalhados:")
    for idx, row in premios.iterrows():
        numero = str(row.iloc[0])
        credor = str(row.iloc[4])
        projeto_num = str(row.iloc[5]) if pd.notna(row.iloc[5]) else 'N/A'
        tipo = str(row.iloc[6])
        descricao = str(row.iloc[7])
        valor = Decimal(str(row.iloc[9])) if pd.notna(row.iloc[9]) else Decimal('0')

        de_quem = "?"
        if 'bruno' in credor.lower():
            de_quem = "BRUNO"
            total_bruno += valor
        elif 'rafael' in credor.lower():
            de_quem = "RAFAEL"
            total_rafael += valor

        print(f"  {numero}: {de_quem:6} | Projeto: {projeto_num:7} | €{float(valor):8.2f} | {descricao[:40]}")

    print()
    print(f"TOTAL Bruno:  €{float(total_bruno):,.2f}")
    print(f"TOTAL Rafael: €{float(total_rafael):,.2f}")
    print()
    print("💡 IMPORTANTE: Prémios devem ser adicionados aos campos premio_bruno/premio_rafael")
    print("   dos PROJETOS correspondentes, NÃO criados como despesas!")


def analisar_boletins():
    """Procura boletins no Excel"""
    print("\n" + "=" * 80)
    print("📄 ANÁLISE DE BOLETINS")
    print("=" * 80)

    xl = pd.ExcelFile('CONTABILIDADE_FINAL.xlsx')

    # Verificar se há aba específica
    print(f"Abas disponíveis: {xl.sheet_names}")
    print()

    # Verificar despesas com tipo "Sub. Alimentação" que podem ser boletins
    df = pd.read_excel(xl, sheet_name='DESPESAS', header=5)
    df_dados = df[df.iloc[:, 0].astype(str).str.startswith('#D', na=False)]

    # Sub. Alimentação
    sub_alim = df_dados[df_dados.iloc[:, 6].astype(str).str.contains('Sub. Alimentação', case=False, na=True)]
    print(f"'Sub. Alimentação': {len(sub_alim)} registos")

    if len(sub_alim) > 0:
        print("\nExemplos:")
        for idx, row in sub_alim.head(5).iterrows():
            numero = str(row.iloc[0])
            credor = str(row.iloc[4])
            valor = row.iloc[9] if pd.notna(row.iloc[9]) else 0
            print(f"  {numero}: {credor:20} | €{float(valor):8.2f}")

    # Verificar "Ordenado"
    ordenados = df_dados[df_dados.iloc[:, 6].astype(str).str.contains('Ordenado', case=False, na=True)]
    print(f"\n'Ordenado': {len(ordenados)} registos")

    if len(ordenados) > 0:
        total_bruno_ord = Decimal('0')
        total_rafael_ord = Decimal('0')

        print("\nOrdenados por sócio:")
        for idx, row in ordenados.iterrows():
            credor = str(row.iloc[4])
            valor = Decimal(str(row.iloc[9])) if pd.notna(row.iloc[9]) else Decimal('0')

            if 'bruno' in credor.lower():
                total_bruno_ord += valor
            elif 'rafael' in credor.lower():
                total_rafael_ord += valor

        print(f"  Bruno:  €{float(total_bruno_ord):,.2f} ({len(ordenados[ordenados.iloc[:, 4].astype(str).str.contains('Bruno', case=False, na=True)])} ordenados)")
        print(f"  Rafael: €{float(total_rafael_ord):,.2f} ({len(ordenados[ordenados.iloc[:, 4].astype(str).str.contains('Rafael', case=False, na=True)])} ordenados)")


def calcular_totais_esperados():
    """Calcula totais esperados para validação"""
    print("\n" + "=" * 80)
    print("📊 TOTAIS ESPERADOS")
    print("=" * 80)

    xl = pd.ExcelFile('CONTABILIDADE_FINAL.xlsx')

    # Projetos
    df_proj = pd.read_excel(xl, sheet_name='PROJETOS', header=3)
    df_proj = df_proj[df_proj.iloc[:, 0].astype(str).str.startswith('#P', na=False)]

    # Contar por tipo
    pessoal_bruno = 0
    pessoal_rafael = 0
    empresa = 0
    total_bruno = Decimal('0')
    total_rafael = Decimal('0')
    total_empresa = Decimal('0')

    for idx, row in df_proj.iterrows():
        estado_str = str(row.iloc[14]) if pd.notna(row.iloc[14]) else ''
        owner_str = str(row.iloc[15]) if pd.notna(row.iloc[15]) else ''
        valor = Decimal(str(row.iloc[5])) if pd.notna(row.iloc[5]) else Decimal('0')
        data_recebimento = row.iloc[8]

        # Determinar tipo
        if 'pessoal' in estado_str.lower():
            if 'bruno' in owner_str.lower():
                pessoal_bruno += 1
                if pd.notna(data_recebimento):
                    total_bruno += valor
            elif 'rafael' in owner_str.lower():
                pessoal_rafael += 1
                if pd.notna(data_recebimento):
                    total_rafael += valor
        else:
            empresa += 1
            if pd.notna(data_recebimento):
                total_empresa += valor

    print(f"\nPROJETOS:")
    print(f"  PESSOAL_BRUNO:  {pessoal_bruno:2} projetos | RECEBIDOS: €{float(total_bruno):,.2f}")
    print(f"  PESSOAL_RAFAEL: {pessoal_rafael:2} projetos | RECEBIDOS: €{float(total_rafael):,.2f}")
    print(f"  EMPRESA:        {empresa:2} projetos | RECEBIDOS: €{float(total_empresa):,.2f}")

    # Despesas fixas mensais
    df_desp = pd.read_excel(xl, sheet_name='DESPESAS', header=5)
    df_desp = df_desp[df_desp.iloc[:, 0].astype(str).str.startswith('#D', na=False)]

    fixas = df_desp[df_desp.iloc[:, 8].astype(str).str.contains('Mensal', case=False, na=True)]
    total_fixas = sum(Decimal(str(row.iloc[9])) if pd.notna(row.iloc[9]) else Decimal('0')
                      for idx, row in fixas.iterrows())

    print(f"\nDESPESAS FIXAS MENSAIS:")
    print(f"  Total: {len(fixas)} despesas")
    print(f"  Valor total: €{float(total_fixas):,.2f}")
    print(f"  Por sócio (÷2): €{float(total_fixas / 2):,.2f}")


def main():
    print("=" * 80)
    print("🔍 ANÁLISE DETALHADA PARA DEBUGGING")
    print("=" * 80)

    analisar_premios()
    analisar_boletins()
    calcular_totais_esperados()

    print("\n" + "=" * 80)
    print("✅ ANÁLISE CONCLUÍDA")
    print("=" * 80)


if __name__ == '__main__':
    main()
