#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Teste do filtro de projetos no relatório de Projetos
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

from logic.relatorios import RelatoriosManager
from database.models import TipoProjeto

load_dotenv()

# Create database session
database_url = os.getenv("DATABASE_URL", "sqlite:///./agora_media.db")
engine = create_engine(database_url)
Session = sessionmaker(bind=engine)
session = Session()

# Create manager
manager = RelatoriosManager(session)

print("=" * 80)
print("🧪 TESTE DE FILTRO NO RELATÓRIO DE PROJETOS")
print("=" * 80)

# Test 1: Todos os projetos
print("\n[TESTE 1] Filtro: TODOS")
print("-" * 80)
relatorio = manager.gerar_relatorio_projetos()
print(f"Total de projetos: {relatorio['total_projetos']}")
print(f"Valor total: {relatorio['total_valor_fmt']}")

# Test 2: Apenas Empresa
print("\n[TESTE 2] Filtro: APENAS EMPRESA")
print("-" * 80)
relatorio = manager.gerar_relatorio_projetos(tipo=TipoProjeto.EMPRESA)
print(f"Total de projetos: {relatorio['total_projetos']}")
print(f"Valor total: {relatorio['total_valor_fmt']}")
for proj in relatorio['projetos'][:5]:
    print(f"  - {proj['numero']}: {proj['tipo']} - {proj['cliente']}")

# Test 3: Apenas Pessoais Bruno
print("\n[TESTE 3] Filtro: APENAS PESSOAIS BRUNO")
print("-" * 80)
relatorio = manager.gerar_relatorio_projetos(tipo=TipoProjeto.PESSOAL_BRUNO)
print(f"Total de projetos: {relatorio['total_projetos']}")
print(f"Valor total: {relatorio['total_valor_fmt']}")
for proj in relatorio['projetos'][:5]:
    print(f"  - {proj['numero']}: {proj['tipo']} - {proj['cliente']}")

# Test 4: Apenas Pessoais Rafael
print("\n[TESTE 4] Filtro: APENAS PESSOAIS RAFAEL")
print("-" * 80)
relatorio = manager.gerar_relatorio_projetos(tipo=TipoProjeto.PESSOAL_RAFAEL)
print(f"Total de projetos: {relatorio['total_projetos']}")
print(f"Valor total: {relatorio['total_valor_fmt']}")
for proj in relatorio['projetos'][:5]:
    print(f"  - {proj['numero']}: {proj['tipo']} - {proj['cliente']}")

session.close()

print("\n" + "=" * 80)
print("✅ TESTE COMPLETO")
print("=" * 80)
