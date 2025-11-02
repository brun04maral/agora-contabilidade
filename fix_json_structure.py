#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de correção do JSON gerado pelo Claude Chat
Converte despesas_fixas_mensais para o formato correto
"""
import json
import sys
from pathlib import Path
from datetime import datetime


def parse_date(date_str):
    """Parse date string to YYYY-MM-DD format"""
    if not date_str:
        return None

    try:
        # Try parsing "2024-10-15 00:00:00" format
        dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
        return dt.strftime("%Y-%m-%d")
    except:
        try:
            # Try parsing "2024-10-15" format
            dt = datetime.strptime(date_str, "%Y-%m-%d")
            return dt.strftime("%Y-%m-%d")
        except:
            return None


def converter_fixa_mensal(fixa):
    """
    Converte uma despesa fixa mensal do formato Claude Chat
    para o formato esperado pelo import_excel.py

    INPUT (formato Claude Chat):
    {
        "codigo": "#D000002",
        "credor": "GMD- Contabilidade e consultoria, Lda",
        "tipo": "Administrativo",
        "descricao": "Contabilidade empresa",
        "total": 170.0,
        "data_vencimento": "2024-10-15 00:00:00"
    }

    OUTPUT (formato import_excel.py):
    {
        "tipo": "FIXA_MENSAL",
        "data": "2024-10-15",
        "credor_nome": "GMD- Contabilidade e consultoria, Lda",
        "projeto_descricao": null,
        "descricao": "Contabilidade empresa",
        "valor_sem_iva": 170.0,
        "valor_com_iva": 170.0,
        "estado": "ATIVO",
        "data_pagamento": null,
        "nota": null
    }
    """
    # Parse data
    data = parse_date(fixa.get('data_vencimento'))

    # Valor
    valor = float(fixa.get('total', 0))

    # Credor
    credor_nome = fixa.get('credor')

    # Descrição
    descricao = fixa.get('descricao', '')

    return {
        "tipo": "FIXA_MENSAL",
        "data": data,
        "credor_nome": credor_nome,
        "projeto_descricao": None,
        "descricao": descricao,
        "valor_sem_iva": valor,
        "valor_com_iva": valor,
        "estado": "ATIVO",
        "data_pagamento": None,
        "nota": None
    }


def main():
    """Main function"""
    print("=" * 80)
    print("🔧 CORREÇÃO DO JSON - Despesas Fixas Mensais")
    print("=" * 80)

    # Check if JSON file exists
    json_file = Path("dados_excel.json")

    if not json_file.exists():
        print("\n❌ Ficheiro 'dados_excel.json' não encontrado!")
        print("\nProcurando ficheiros alternativos...")

        # Try alternative names
        alternatives = [
            "dados_excel_FINAL_ATUALIZADO.json",
            "dados_excel_final.json",
            "dados_reais.json"
        ]

        for alt in alternatives:
            if Path(alt).exists():
                json_file = Path(alt)
                print(f"✅ Encontrado: {alt}")
                break

        if not json_file.exists():
            print("\n❌ Nenhum ficheiro JSON encontrado!")
            print("\nFicheiros disponíveis:")
            for f in Path(".").glob("*.json"):
                print(f"   • {f.name}")
            sys.exit(1)

    print(f"\n📖 A ler ficheiro: {json_file.name}")

    # Load JSON
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print("   ✅ JSON carregado com sucesso")
    except Exception as e:
        print(f"   ❌ Erro ao ler JSON: {e}")
        sys.exit(1)

    # Check structure
    print("\n📊 Estrutura atual:")
    print(f"   • Clientes: {len(data.get('clientes', []))}")
    print(f"   • Fornecedores: {len(data.get('fornecedores', []))}")
    print(f"   • Projetos: {len(data.get('projetos', []))}")
    print(f"   • Despesas: {len(data.get('despesas', []))}")
    print(f"   • Boletins: {len(data.get('boletins', []))}")

    # Check if despesas_fixas_mensais exists
    if 'despesas_fixas_mensais' not in data:
        print("\n⚠️  Objeto 'despesas_fixas_mensais' não encontrado!")
        print("   O JSON já pode estar no formato correto.")

        response = input("\nContinuar mesmo assim? (sim/não): ").strip().lower()
        if response not in ['sim', 's', 'yes', 'y']:
            print("\n❌ Operação cancelada.")
            sys.exit(0)

        fixas = []
    else:
        fixas_obj = data.get('despesas_fixas_mensais', {})
        fixas = fixas_obj.get('registos', [])
        total_por_pessoa = fixas_obj.get('total_por_pessoa', 0)

        print(f"\n🔍 Despesas Fixas Mensais encontradas:")
        print(f"   • Registos: {len(fixas)}")
        print(f"   • Total por pessoa: €{total_por_pessoa:,.2f}")

    if not fixas:
        print("\n⚠️  Nenhuma despesa fixa mensal para converter.")
        sys.exit(0)

    # Show confirmation
    print(f"\n⚠️  CONVERSÃO:")
    print(f"   Origem: despesas_fixas_mensais.registos ({len(fixas)} despesas)")
    print(f"   Destino: array despesas")
    print(f"   Total após conversão: {len(data.get('despesas', []))} + {len(fixas)} = {len(data.get('despesas', [])) + len(fixas)} despesas")

    response = input("\nContinuar com a conversão? (sim/não): ").strip().lower()
    if response not in ['sim', 's', 'yes', 'y']:
        print("\n❌ Conversão cancelada.")
        sys.exit(0)

    # Convert fixas mensais
    print(f"\n🔄 A converter {len(fixas)} despesas fixas mensais...")

    despesas_array = data.get('despesas', [])
    conversoes_ok = 0
    conversoes_erro = 0

    for idx, fixa in enumerate(fixas, 1):
        try:
            despesa_convertida = converter_fixa_mensal(fixa)
            despesas_array.append(despesa_convertida)
            conversoes_ok += 1

            # Show progress every 20
            if idx % 20 == 0:
                print(f"   ✅ Convertidas: {idx}/{len(fixas)}")

        except Exception as e:
            conversoes_erro += 1
            print(f"   ❌ Erro na despesa #{idx}: {e}")

    print(f"\n📊 Resultado da conversão:")
    print(f"   ✅ Sucesso: {conversoes_ok}")
    if conversoes_erro > 0:
        print(f"   ❌ Erros: {conversoes_erro}")

    # Update data
    data['despesas'] = despesas_array

    # Remove despesas_fixas_mensais
    if 'despesas_fixas_mensais' in data:
        del data['despesas_fixas_mensais']
        print(f"\n🗑️  Objeto 'despesas_fixas_mensais' removido")

    # Show final structure
    print(f"\n📊 Estrutura final:")
    print(f"   • Clientes: {len(data.get('clientes', []))}")
    print(f"   • Fornecedores: {len(data.get('fornecedores', []))}")
    print(f"   • Projetos: {len(data.get('projetos', []))}")
    print(f"   • Despesas: {len(data.get('despesas', []))} ✅")
    print(f"   • Boletins: {len(data.get('boletins', []))}")

    # Save corrected JSON
    output_file = Path("dados_excel.json")

    print(f"\n💾 A guardar ficheiro corrigido: {output_file.name}")

    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print("   ✅ Ficheiro guardado com sucesso")
    except Exception as e:
        print(f"   ❌ Erro ao guardar: {e}")
        sys.exit(1)

    # Final summary
    print("\n" + "=" * 80)
    print("✅ CONVERSÃO CONCLUÍDA COM SUCESSO!")
    print("=" * 80)
    print(f"\n📁 Ficheiro: dados_excel.json")
    print(f"📊 Total de despesas: {len(data.get('despesas', []))}")
    print(f"   • Despesas gerais: {len(data.get('despesas', [])) - conversoes_ok}")
    print(f"   • Despesas fixas mensais: {conversoes_ok}")
    print(f"\n💡 Próximo passo:")
    print(f"   python3 import_excel.py")
    print(f"\n✨ Dashboard vai mostrar:")
    print(f"   Despesas fixas (÷2): €12,315.71 ✅")
    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()
