#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Teste de filtros combinados (Tipo + Estado) no Relatório de Projetos
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

from logic.relatorios import RelatoriosManager
from database.models import TipoProjeto, EstadoProjeto

load_dotenv()

# Create database session
database_url = os.getenv("DATABASE_URL", "sqlite:///./agora_media.db")
engine = create_engine(database_url)
Session = sessionmaker(bind=engine)
session = Session()

# Create manager
manager = RelatoriosManager(session)

print("=" * 80)
print("🧪 TESTE DE FILTROS COMBINADOS (TIPO + ESTADO) NO RELATÓRIO DE PROJETOS")
print("=" * 80)

# Test 1: Todos os projetos
print("\n[TESTE 1] SEM FILTROS (Tipo=Todos, Estado=Todos)")
print("-" * 80)
relatorio = manager.gerar_relatorio_projetos()
print(f"Total de projetos: {relatorio['total_projetos']}")
print(f"Valor total: {relatorio['total_valor_fmt']}")
print(f"Filtros: {relatorio['filtros']}")

# Test 2: Empresa + Recebidos
print("\n[TESTE 2] FILTRO: Empresa + Recebidos")
print("-" * 80)
relatorio = manager.gerar_relatorio_projetos(
    tipo=TipoProjeto.EMPRESA,
    estado=EstadoProjeto.RECEBIDO
)
print(f"Total de projetos: {relatorio['total_projetos']}")
print(f"Valor total: {relatorio['total_valor_fmt']}")
print(f"Filtros: {relatorio['filtros']}")
if relatorio['projetos']:
    print("\nPrimeiros 3 projetos:")
    for proj in relatorio['projetos'][:3]:
        print(f"  - {proj['numero']}: {proj['tipo']} / {proj['estado']} - {proj['cliente']} ({proj['valor_fmt']})")

# Test 3: Pessoais Bruno + Não Faturado
print("\n[TESTE 3] FILTRO: Pessoais Bruno + Não Faturado")
print("-" * 80)
relatorio = manager.gerar_relatorio_projetos(
    tipo=TipoProjeto.PESSOAL_BRUNO,
    estado=EstadoProjeto.NAO_FATURADO
)
print(f"Total de projetos: {relatorio['total_projetos']}")
print(f"Valor total: {relatorio['total_valor_fmt']}")
print(f"Filtros: {relatorio['filtros']}")
if relatorio['projetos']:
    print("\nTodos os projetos:")
    for proj in relatorio['projetos']:
        print(f"  - {proj['numero']}: {proj['tipo']} / {proj['estado']} - {proj['cliente']} ({proj['valor_fmt']})")

# Test 4: Pessoais Rafael + Faturado
print("\n[TESTE 4] FILTRO: Pessoais Rafael + Faturado")
print("-" * 80)
relatorio = manager.gerar_relatorio_projetos(
    tipo=TipoProjeto.PESSOAL_RAFAEL,
    estado=EstadoProjeto.FATURADO
)
print(f"Total de projetos: {relatorio['total_projetos']}")
print(f"Valor total: {relatorio['total_valor_fmt']}")
print(f"Filtros: {relatorio['filtros']}")
if relatorio['projetos']:
    print("\nTodos os projetos:")
    for proj in relatorio['projetos']:
        print(f"  - {proj['numero']}: {proj['tipo']} / {proj['estado']} - {proj['cliente']} ({proj['valor_fmt']})")

# Test 5: Só filtro de Estado (Não Faturado)
print("\n[TESTE 5] FILTRO: Apenas Estado = Não Faturado")
print("-" * 80)
relatorio = manager.gerar_relatorio_projetos(
    estado=EstadoProjeto.NAO_FATURADO
)
print(f"Total de projetos: {relatorio['total_projetos']}")
print(f"Valor total: {relatorio['total_valor_fmt']}")
print(f"Filtros: {relatorio['filtros']}")
print("\nBreakdown por tipo:")
for stat in relatorio['stats_por_tipo']:
    if stat['count'] > 0:
        print(f"  - {stat['tipo']}: {stat['count']} projetos ({stat['valor_fmt']})")

# Test 6: Só filtro de Tipo (Empresa)
print("\n[TESTE 6] FILTRO: Apenas Tipo = Empresa")
print("-" * 80)
relatorio = manager.gerar_relatorio_projetos(
    tipo=TipoProjeto.EMPRESA
)
print(f"Total de projetos: {relatorio['total_projetos']}")
print(f"Valor total: {relatorio['total_valor_fmt']}")
print(f"Filtros: {relatorio['filtros']}")
print("\nBreakdown por estado:")
for stat in relatorio['stats_por_estado']:
    if stat['count'] > 0:
        print(f"  - {stat['estado']}: {stat['count']} projetos ({stat['valor_fmt']})")

session.close()

print("\n" + "=" * 80)
print("✅ TESTE COMPLETO")
print("=" * 80)
