#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Teste dos filtros do relatório de saldos
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

from logic.relatorios import RelatoriosManager
from database.models import Socio

load_dotenv()

# Create database session
database_url = os.getenv("DATABASE_URL", "sqlite:///./agora_media.db")
engine = create_engine(database_url)
Session = sessionmaker(bind=engine)
session = Session()

# Create manager
manager = RelatoriosManager(session)

print("=" * 80)
print("🧪 TESTE DE FILTROS DO RELATÓRIO DE SALDOS")
print("=" * 80)

# Test 1: Filtro "Todos"
print("\n[TESTE 1] Filtro: TODOS (ambos os sócios)")
print("-" * 80)
relatorio = manager.gerar_relatorio_saldos(filtro_tipo_projeto="todos")
for socio_data in relatorio['socios']:
    print(f"\n{socio_data['nome']}:")
    print(f"  Projetos Pessoais: {len(socio_data.get('projetos_pessoais_list', []))} items")
    print(f"  Prémios: {len(socio_data.get('premios_list', []))} items")
    print(f"  Despesas Fixas: {len(socio_data.get('despesas_fixas_list', []))} items")
    print(f"  Boletins: {len(socio_data.get('boletins_list', []))} items")

# Test 2: Filtro "Empresa"
print("\n\n[TESTE 2] Filtro: EMPRESA (só prémios, sem pessoais)")
print("-" * 80)
relatorio = manager.gerar_relatorio_saldos(filtro_tipo_projeto="empresa")
for socio_data in relatorio['socios']:
    print(f"\n{socio_data['nome']}:")
    print(f"  Projetos Pessoais: {len(socio_data.get('projetos_pessoais_list', []))} items (deve ser 0)")
    print(f"  Prémios: {len(socio_data.get('premios_list', []))} items (deve ter valores)")

# Test 3: Filtro "BA"
print("\n\n[TESTE 3] Filtro: PESSOAIS BRUNO (só pessoais BA, sem prémios)")
print("-" * 80)
relatorio = manager.gerar_relatorio_saldos(filtro_tipo_projeto="bruno")
for socio_data in relatorio['socios']:
    print(f"\n{socio_data['nome']}:")
    print(f"  Projetos Pessoais: {len(socio_data.get('projetos_pessoais_list', []))} items")
    if "BA" in socio_data['nome']:
        print(f"    (deve ter valores para BA)")
    else:
        print(f"    (deve ser 0 para RR)")
    print(f"  Prémios: {len(socio_data.get('premios_list', []))} items (deve ser 0 para ambos)")

# Test 4: Filtro "RR"
print("\n\n[TESTE 4] Filtro: PESSOAIS RAFAEL (só pessoais RR, sem prémios)")
print("-" * 80)
relatorio = manager.gerar_relatorio_saldos(filtro_tipo_projeto="rafael")
for socio_data in relatorio['socios']:
    print(f"\n{socio_data['nome']}:")
    print(f"  Projetos Pessoais: {len(socio_data.get('projetos_pessoais_list', []))} items")
    if "RR" in socio_data['nome']:
        print(f"    (deve ter valores para RR)")
    else:
        print(f"    (deve ser 0 para BA)")
    print(f"  Prémios: {len(socio_data.get('premios_list', []))} items (deve ser 0 para ambos)")

# Test 5: Filtro apenas para BA
print("\n\n[TESTE 5] Filtro: EMPRESA + Sócio BRUNO")
print("-" * 80)
relatorio = manager.gerar_relatorio_saldos(socio=Socio.BRUNO, filtro_tipo_projeto="empresa")
for socio_data in relatorio['socios']:
    print(f"\n{socio_data['nome']}:")
    print(f"  Projetos Pessoais: {len(socio_data.get('projetos_pessoais_list', []))} items (deve ser 0)")
    print(f"  Prémios: {len(socio_data.get('premios_list', []))} items (deve ter valores)")

session.close()

print("\n" + "=" * 80)
print("✅ TESTE COMPLETO")
print("=" * 80)
