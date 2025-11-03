#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Teste da funcionalidade de mostrar/ocultar prémios no relatório de Projetos
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
print("🧪 TESTE DE MOSTRAR/OCULTAR PRÉMIOS NO RELATÓRIO DE PROJETOS")
print("=" * 80)

# Test 1: Todos - deve mostrar prémios
print("\n[TESTE 1] Filtro: TODOS (deve mostrar prémios: True)")
print("-" * 80)
relatorio = manager.gerar_relatorio_projetos()
print(f"mostrar_premios: {relatorio['mostrar_premios']}")
print(f"Total de projetos: {relatorio['total_projetos']}")
print(f"Prémios Bruno: {relatorio['total_premios_bruno_fmt']}")
print(f"Prémios Rafael: {relatorio['total_premios_rafael_fmt']}")
print("\nPrimeiro projeto:")
proj = relatorio['projetos'][0]
print(f"  {proj['numero']}: {proj['tipo']} - {proj['cliente']}")
print(f"  Valor: {proj['valor_fmt']}")
print(f"  Prémio Bruno: {proj['premio_bruno_fmt']}")
print(f"  Prémio Rafael: {proj['premio_rafael_fmt']}")

# Test 2: Empresa - deve mostrar prémios
print("\n\n[TESTE 2] Filtro: EMPRESA (deve mostrar prémios: True)")
print("-" * 80)
relatorio = manager.gerar_relatorio_projetos(tipo=TipoProjeto.EMPRESA)
print(f"mostrar_premios: {relatorio['mostrar_premios']}")
print(f"Total de projetos: {relatorio['total_projetos']}")
print(f"Prémios Bruno: {relatorio['total_premios_bruno_fmt']}")
print(f"Prémios Rafael: {relatorio['total_premios_rafael_fmt']}")
print("\nPrimeiro projeto:")
proj = relatorio['projetos'][0]
print(f"  {proj['numero']}: {proj['tipo']} - {proj['cliente']}")
print(f"  Valor: {proj['valor_fmt']}")
print(f"  Prémio Bruno: {proj['premio_bruno_fmt']}")
print(f"  Prémio Rafael: {proj['premio_rafael_fmt']}")

# Test 3: Pessoais Bruno - NÃO deve mostrar prémios
print("\n\n[TESTE 3] Filtro: PESSOAIS BRUNO (deve mostrar prémios: False)")
print("-" * 80)
relatorio = manager.gerar_relatorio_projetos(tipo=TipoProjeto.PESSOAL_BRUNO)
print(f"mostrar_premios: {relatorio['mostrar_premios']}")
print(f"Total de projetos: {relatorio['total_projetos']}")
print(f"Valor Total: {relatorio['total_valor_fmt']}")
print("\nPrimeiro projeto:")
proj = relatorio['projetos'][0]
print(f"  {proj['numero']}: {proj['tipo']} - {proj['cliente']}")
print(f"  Valor: {proj['valor_fmt']}")
print(f"  (Prémios não devem aparecer na UI)")

# Test 4: Pessoais Rafael - NÃO deve mostrar prémios
print("\n\n[TESTE 4] Filtro: PESSOAIS RAFAEL (deve mostrar prémios: False)")
print("-" * 80)
relatorio = manager.gerar_relatorio_projetos(tipo=TipoProjeto.PESSOAL_RAFAEL)
print(f"mostrar_premios: {relatorio['mostrar_premios']}")
print(f"Total de projetos: {relatorio['total_projetos']}")
print(f"Valor Total: {relatorio['total_valor_fmt']}")
print("\nPrimeiro projeto:")
proj = relatorio['projetos'][0]
print(f"  {proj['numero']}: {proj['tipo']} - {proj['cliente']}")
print(f"  Valor: {proj['valor_fmt']}")
print(f"  (Prémios não devem aparecer na UI)")

session.close()

print("\n" + "=" * 80)
print("✅ TESTE COMPLETO")
print("=" * 80)
