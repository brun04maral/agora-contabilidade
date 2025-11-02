#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar o JSON ANTES de importar
"""
import json
import sys
from pathlib import Path
from decimal import Decimal

print("=" * 80)
print("📋 VERIFICAÇÃO DO JSON - Antes de Importar")
print("=" * 80)

# Find JSON file
json_file = Path("dados_excel.json")

if not json_file.exists():
    print("\n❌ Ficheiro 'dados_excel.json' não encontrado!")
    alternatives = [f for f in Path(".").glob("*dados*.json")]
    if alternatives:
        print("\nFicheiros encontrados:")
        for f in alternatives:
            print(f"  • {f.name}")
    sys.exit(1)

print(f"\n📖 A ler: {json_file.name}")

# Load JSON
try:
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    print("   ✅ JSON carregado")
except Exception as e:
    print(f"   ❌ Erro: {e}")
    sys.exit(1)

# Estrutura geral
print("\n📊 ESTRUTURA:")
print("=" * 80)
print(f"✅ Clientes: {len(data.get('clientes', []))}")
print(f"✅ Fornecedores: {len(data.get('fornecedores', []))}")
print(f"✅ Projetos: {len(data.get('projetos', []))}")
print(f"✅ Despesas: {len(data.get('despesas', []))}")
print(f"✅ Boletins: {len(data.get('boletins', []))}")

# Verificar se ainda tem despesas_fixas_mensais separadas
if 'despesas_fixas_mensais' in data:
    fixas = data['despesas_fixas_mensais']
    print(f"\n⚠️  ATENÇÃO: Objeto 'despesas_fixas_mensais' ainda existe!")
    print(f"   Registos: {len(fixas.get('registos', []))}")
    print(f"   Total por pessoa: €{fixas.get('total_por_pessoa', 0):,.2f}")
    print(f"\n❌ PROBLEMA: Estas despesas NÃO serão importadas!")
    print(f"   Solução: python3 fix_json_structure.py")

# Verificar despesas por tipo
print("\n💸 DESPESAS POR TIPO (no JSON):")
print("=" * 80)

despesas = data.get('despesas', [])
tipos_count = {}

for d in despesas:
    tipo = d.get('tipo', 'UNKNOWN')
    tipos_count[tipo] = tipos_count.get(tipo, 0) + 1

for tipo, count in sorted(tipos_count.items()):
    print(f"  {tipo}: {count}")

if 'FIXA_MENSAL' not in tipos_count:
    print(f"\n❌ PROBLEMA: Nenhuma despesa tipo 'FIXA_MENSAL' encontrada!")
    print(f"   Esperado: 88 despesas")
    if 'despesas_fixas_mensais' in data:
        print(f"   Causa: Ainda tem objeto 'despesas_fixas_mensais' separado")
        print(f"   Solução: python3 fix_json_structure.py")
else:
    print(f"\n✅ Despesas fixas mensais: {tipos_count['FIXA_MENSAL']}")

# Verificar projetos por tipo
print("\n🎬 PROJETOS POR TIPO (no JSON):")
print("=" * 80)

projetos = data.get('projetos', [])
tipos_proj = {}

for p in projetos:
    tipo = p.get('tipo', 'UNKNOWN')
    tipos_proj[tipo] = tipos_proj.get(tipo, 0) + 1

for tipo, count in sorted(tipos_proj.items()):
    print(f"  {tipo}: {count}")

# Verificar projetos pessoais BRUNO
print("\n💰 PROJETOS PESSOAIS BRUNO (no JSON):")
print("=" * 80)

projetos_bruno = [p for p in projetos if p.get('tipo') == 'PESSOAL_BRUNO']
print(f"Total: {len(projetos_bruno)}")

total_bruno = Decimal("0")
total_bruno_recebido = Decimal("0")

for p in projetos_bruno:
    valor = Decimal(str(p.get('valor_sem_iva', 0)))
    estado = p.get('estado', 'UNKNOWN')

    estado_emoji = "✅" if estado == "RECEBIDO" else "⏳" if estado == "FATURADO" else "❌"
    print(f"  {estado_emoji} {p.get('descricao', '')[:40]:40} €{float(valor):>10,.2f} ({estado})")

    total_bruno += valor
    if estado == 'RECEBIDO':
        total_bruno_recebido += valor

print(f"\n  TOTAL: €{float(total_bruno):,.2f}")
print(f"  RECEBIDO: €{float(total_bruno_recebido):,.2f}")
print(f"  ❗ ESPERADO: €15,040.00")

if float(total_bruno_recebido) != 15040.00:
    diff = 15040.00 - float(total_bruno_recebido)
    print(f"  ⚠️  DIFERENÇA: €{diff:,.2f}")

    # Mostrar quais NÃO estão RECEBIDOS
    nao_recebidos = [p for p in projetos_bruno if p.get('estado') != 'RECEBIDO']
    if nao_recebidos:
        print(f"\n  ⚠️  Projetos NÃO RECEBIDOS ({len(nao_recebidos)}):")
        for p in nao_recebidos:
            valor = Decimal(str(p.get('valor_sem_iva', 0)))
            print(f"     • {p.get('descricao', '')[:40]:40} €{float(valor):>10,.2f} ({p.get('estado')})")

# Verificar prémios em projetos EMPRESA
print("\n🏆 PRÉMIOS (Projetos EMPRESA no JSON):")
print("=" * 80)

projetos_empresa = [p for p in projetos if p.get('tipo') == 'EMPRESA']
print(f"Total projetos EMPRESA: {len(projetos_empresa)}")

projetos_com_premio = [p for p in projetos_empresa
                       if (p.get('premio_bruno', 0) > 0 or p.get('premio_rafael', 0) > 0)]

print(f"Com prémios: {len(projetos_com_premio)}")

total_premio_bruno = Decimal("0")
total_premio_rafael = Decimal("0")

for p in projetos_com_premio:
    premio_b = Decimal(str(p.get('premio_bruno', 0)))
    premio_r = Decimal(str(p.get('premio_rafael', 0)))

    print(f"  {p.get('descricao', '')[:30]:30} B:€{float(premio_b):>8,.2f} R:€{float(premio_r):>8,.2f} ({p.get('estado')})")

    total_premio_bruno += premio_b
    total_premio_rafael += premio_r

print(f"\n  TOTAL BRUNO: €{float(total_premio_bruno):,.2f}")
print(f"  ❗ ESPERADO: €3,111.25")

if float(total_premio_bruno) != 3111.25:
    diff = 3111.25 - float(total_premio_bruno)
    print(f"  ⚠️  DIFERENÇA: €{diff:,.2f}")

print(f"\n  TOTAL RAFAEL: €{float(total_premio_rafael):,.2f}")
print(f"  ❗ ESPERADO: €6,140.17")

if float(total_premio_rafael) != 6140.17:
    diff = 6140.17 - float(total_premio_rafael)
    print(f"  ⚠️  DIFERENÇA: €{diff:,.2f}")

# Verificar boletins
print("\n📄 BOLETINS (no JSON):")
print("=" * 80)

boletins = data.get('boletins', [])
boletins_bruno = [b for b in boletins if b.get('socio') == 'BRUNO']
boletins_rafael = [b for b in boletins if b.get('socio') == 'RAFAEL']

print(f"Bruno: {len(boletins_bruno)}")
print(f"Rafael: {len(boletins_rafael)}")

total_bruno_boletins = sum([Decimal(str(b.get('valor', 0))) for b in boletins_bruno], Decimal("0"))
total_rafael_boletins = sum([Decimal(str(b.get('valor', 0))) for b in boletins_rafael], Decimal("0"))

print(f"\n  TOTAL BRUNO: €{float(total_bruno_boletins):,.2f}")
print(f"  ❗ ESPERADO: €5,215.36")

print(f"\n  TOTAL RAFAEL: €{float(total_rafael_boletins):,.2f}")
print(f"  ❗ ESPERADO: €4,649.69")

# RESUMO
print("\n" + "=" * 80)
print("📊 RESUMO:")
print("=" * 80)

problemas = []

if 'despesas_fixas_mensais' in data:
    problemas.append("❌ Objeto 'despesas_fixas_mensais' ainda existe (não será importado)")

if 'FIXA_MENSAL' not in tipos_count:
    problemas.append("❌ Nenhuma despesa FIXA_MENSAL no array despesas")

if float(total_premio_bruno) == 0:
    problemas.append("⚠️  Prémios Bruno = €0.00 (esperado €3,111.25)")

if float(total_bruno_recebido) != 15040.00:
    problemas.append(f"⚠️  Projetos Bruno = €{float(total_bruno_recebido):,.2f} (esperado €15,040.00)")

if problemas:
    print("\n❌ PROBLEMAS NO JSON:\n")
    for p in problemas:
        print(f"  {p}")

    print("\n💡 AÇÕES NECESSÁRIAS:")
    if 'despesas_fixas_mensais' in data or 'FIXA_MENSAL' not in tipos_count:
        print("  1. python3 fix_json_structure.py  (corrige estrutura)")
    if float(total_premio_bruno) == 0:
        print("  2. Verificar campos premio_bruno/premio_rafael no JSON")
    if float(total_bruno_recebido) != 15040.00:
        print("  3. Verificar estados dos projetos (devem ser 'RECEBIDO')")

    print("\n⚠️  NÃO IMPORTAR AINDA! Corrige primeiro os problemas acima.")
else:
    print("\n✅ JSON parece correto! Pode importar:")
    print("   python3 import_excel.py")

print("\n" + "=" * 80)
