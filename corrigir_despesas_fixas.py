#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para corrigir despesas fixas mensais no JSON

Lógica de correção:
- Para cada despesa com tipo "FIXA_MENSAL"
- Se data (vencimento) <= hoje (2025-10-29)
- Então: estado "ATIVO" → "PAGO" + data_pagamento = data

Isto faz sentido porque despesas fixas mensais são recorrentes e se já
venceram, foram pagas automaticamente (ordenados, contabilidade, etc.)
"""
import json
from datetime import datetime, date
from decimal import Decimal


def parse_date(date_str):
    """Converte string de data para objeto date"""
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        try:
            return datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S").date()
        except ValueError:
            return None


def main():
    print("=" * 80)
    print("🔧 CORREÇÃO DE DESPESAS FIXAS MENSAIS")
    print("=" * 80)
    print()

    # Data de referência (hoje)
    hoje = date(2025, 10, 29)
    print(f"📅 Data de referência: {hoje}")
    print()

    # Ler JSON
    print("📖 A ler: dados_excel.json")
    try:
        with open("dados_excel.json", 'r', encoding='utf-8') as f:
            data = json.load(f)
        print("   ✅ JSON carregado")
    except FileNotFoundError:
        print("   ❌ Ficheiro 'dados_excel.json' não encontrado!")
        return
    except json.JSONDecodeError as e:
        print(f"   ❌ Erro ao parsear JSON: {e}")
        return

    print()
    print("=" * 80)
    print("🔍 ANALISANDO DESPESAS FIXAS MENSAIS")
    print("=" * 80)

    despesas = data.get('despesas', [])

    # Contar despesas fixas mensais
    fixas = [d for d in despesas if d.get('tipo') == 'FIXA_MENSAL']
    print(f"Total de despesas FIXA_MENSAL: {len(fixas)}")
    print()

    # Separar por estado atual
    fixas_ativo = [d for d in fixas if d.get('estado') == 'ATIVO']
    fixas_pago = [d for d in fixas if d.get('estado') == 'PAGO']
    fixas_vencido = [d for d in fixas if d.get('estado') == 'VENCIDO']

    print(f"  ATIVO: {len(fixas_ativo)}")
    print(f"  PAGO: {len(fixas_pago)}")
    print(f"  VENCIDO: {len(fixas_vencido)}")
    print()

    # Analisar despesas ATIVO que devem ser marcadas como PAGO
    to_update = []
    futuras = []

    for despesa in fixas_ativo:
        data_vencimento = parse_date(despesa.get('data'))

        if data_vencimento:
            if data_vencimento <= hoje:
                to_update.append((despesa, data_vencimento))
            else:
                futuras.append((despesa, data_vencimento))
        else:
            print(f"⚠️  Despesa sem data válida: {despesa.get('descricao', 'N/A')}")

    print("=" * 80)
    print(f"📊 RESULTADO DA ANÁLISE:")
    print("=" * 80)
    print(f"✅ Despesas já vencidas (marcar como PAGO): {len(to_update)}")
    print(f"⏳ Despesas futuras (manter ATIVO): {len(futuras)}")
    print()

    if len(to_update) == 0:
        print("✅ Nenhuma correção necessária!")
        return

    # Mostrar algumas despesas que serão corrigidas
    print("Exemplos de despesas que serão marcadas como PAGO:")
    for despesa, data_venc in to_update[:5]:
        print(f"  • {despesa.get('descricao', 'N/A')[:50]:50} | Vencimento: {data_venc} | €{despesa.get('valor_sem_iva', 0):,.2f}")

    if len(to_update) > 5:
        print(f"  ... e mais {len(to_update) - 5} despesas")
    print()

    # Calcular total que será marcado como PAGO
    total_a_marcar = sum(Decimal(str(d[0].get('valor_sem_iva', 0))) for d in to_update)
    print(f"💰 Valor total a marcar como PAGO: €{float(total_a_marcar):,.2f}")
    print(f"   Por sócio (÷2): €{float(total_a_marcar / 2):,.2f}")
    print()

    # Confirmar
    resposta = input("🔧 Aplicar correções? (sim/não): ").strip().lower()
    if resposta not in ['sim', 's', 'yes', 'y']:
        print("❌ Operação cancelada!")
        return

    print()
    print("=" * 80)
    print("🔧 APLICANDO CORREÇÕES")
    print("=" * 80)

    # Aplicar correções
    corrigidas = 0
    for despesa, data_venc in to_update:
        despesa['estado'] = 'PAGO'
        despesa['data_pagamento'] = data_venc.strftime("%Y-%m-%d")
        corrigidas += 1

    print(f"✅ {corrigidas} despesas corrigidas")
    print()

    # Salvar JSON corrigido
    print("💾 A guardar: dados_excel.json")
    try:
        with open("dados_excel.json", 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print("   ✅ JSON guardado com sucesso!")
    except Exception as e:
        print(f"   ❌ Erro ao guardar: {e}")
        return

    print()
    print("=" * 80)
    print("✅ CORREÇÃO CONCLUÍDA")
    print("=" * 80)
    print()
    print("Resumo:")
    print(f"  • {corrigidas} despesas fixas marcadas como PAGO")
    print(f"  • Valor total: €{float(total_a_marcar):,.2f}")
    print(f"  • Por sócio: €{float(total_a_marcar / 2):,.2f}")
    print()
    print("Próximo passo:")
    print("  → Resolver o problema dos prémios")
    print("  → Verificar estado do projeto GS1 Copenhaga")
    print("  → Executar: python3 import_excel.py")
    print()


if __name__ == '__main__':
    main()
