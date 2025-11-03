#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Teste do logo nos PDFs
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

from logic.relatorios import RelatoriosManager

load_dotenv()

# Create database session
database_url = os.getenv("DATABASE_URL", "sqlite:///./agora_media.db")
engine = create_engine(database_url)
Session = sessionmaker(bind=engine)
session = Session()

# Create manager
manager = RelatoriosManager(session)

print("=" * 80)
print("🧪 TESTE DO LOGO NOS PDFs")
print("=" * 80)

# Test 1: Saldos PDF
print("\n[TESTE 1] PDF de Saldos com logo")
print("-" * 80)
relatorio_saldos = manager.gerar_relatorio_saldos()
pdf_saldos = "/tmp/test_saldos_com_logo.pdf"
try:
    manager.exportar_pdf(relatorio_saldos, pdf_saldos)
    file_size = os.path.getsize(pdf_saldos)
    print(f"✅ PDF exportado: {pdf_saldos} ({file_size:,} bytes)")
    print(f"   Abrir e verificar se o logo 'a' + 'Agora Media Production' aparece no topo")
except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()

# Test 2: Financeiro PDF
print("\n[TESTE 2] PDF Financeiro com logo")
print("-" * 80)
relatorio_fin = manager.gerar_relatorio_financeiro_mensal()
pdf_fin = "/tmp/test_financeiro_com_logo.pdf"
try:
    manager.exportar_pdf(relatorio_fin, pdf_fin)
    file_size = os.path.getsize(pdf_fin)
    print(f"✅ PDF exportado: {pdf_fin} ({file_size:,} bytes)")
except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()

# Test 3: Projetos PDF
print("\n[TESTE 3] PDF Projetos com logo")
print("-" * 80)
relatorio_proj = manager.gerar_relatorio_projetos()
pdf_proj = "/tmp/test_projetos_com_logo.pdf"
try:
    manager.exportar_pdf(relatorio_proj, pdf_proj)
    file_size = os.path.getsize(pdf_proj)
    print(f"✅ PDF exportado: {pdf_proj} ({file_size:,} bytes)")
except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()

session.close()

print("\n" + "=" * 80)
print("✅ TESTE COMPLETO")
print("=" * 80)
print("\nFicheiros gerados:")
print(f"  - {pdf_saldos}")
print(f"  - {pdf_fin}")
print(f"  - {pdf_proj}")
print("\nAbrir e verificar:")
print("  - Logo 'a' azul no topo esquerdo")
print("  - 'Agora Media' + 'Production' (azul)")
print("  - Linha azul separadora")
