#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Teste de correção dos bugs de relatórios
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
print("🧪 TESTE DE CORREÇÃO DOS BUGS DE RELATÓRIOS")
print("=" * 80)

# Test 1: Bug 2 - Export completo de Projetos
print("\n[TESTE 1] Bug 2 - Export PDF de Projetos (todos os projetos)")
print("-" * 80)

# Generate report with all projects
relatorio = manager.gerar_relatorio_projetos()
total_projetos = relatorio['total_projetos']
print(f"Total de projetos no relatório: {total_projetos}")

# Export to PDF
pdf_filename = "/tmp/test_projetos_completo.pdf"
try:
    manager.exportar_pdf(relatorio, pdf_filename)
    file_size = os.path.getsize(pdf_filename)
    print(f"✅ PDF exportado: {pdf_filename} ({file_size:,} bytes)")
    print(f"   Esperado: {total_projetos} projetos no PDF (não apenas 20)")
    print(f"   Verificar manualmente que não aparece '(+ X projetos)' no PDF")
except Exception as e:
    print(f"❌ Erro ao exportar PDF: {e}")

# Export to Excel
xlsx_filename = "/tmp/test_projetos_completo.xlsx"
try:
    manager.exportar_excel(relatorio, xlsx_filename)
    file_size = os.path.getsize(xlsx_filename)
    print(f"✅ Excel exportado: {xlsx_filename} ({file_size:,} bytes)")
    print(f"   Esperado: {total_projetos} projetos no Excel")
except Exception as e:
    print(f"❌ Erro ao exportar Excel: {e}")

# Test with filtered report (fewer projects to verify)
print("\n[TESTE 2] Bug 2 - Export PDF com filtro (Empresa + Recebido)")
print("-" * 80)

relatorio_filtrado = manager.gerar_relatorio_projetos(
    tipo=TipoProjeto.EMPRESA,
    estado=EstadoProjeto.RECEBIDO
)
total_filtrado = relatorio_filtrado['total_projetos']
print(f"Total de projetos filtrados: {total_filtrado}")

pdf_filtrado = "/tmp/test_projetos_filtrado.pdf"
try:
    manager.exportar_pdf(relatorio_filtrado, pdf_filtrado)
    file_size = os.path.getsize(pdf_filtrado)
    print(f"✅ PDF filtrado exportado: {pdf_filtrado} ({file_size:,} bytes)")
    print(f"   Esperado: {total_filtrado} projetos no PDF")
    print(f"   Verificar manualmente que TODOS aparecem listados")
except Exception as e:
    print(f"❌ Erro ao exportar PDF filtrado: {e}")

session.close()

print("\n" + "=" * 80)
print("✅ TESTE COMPLETO")
print("=" * 80)
print("\nNOTA sobre Bug 1 (filtros aparecem logo):")
print("  - Bug 1 foi corrigido no código da UI")
print("  - Ao abrir a aba Relatórios, só deve aparecer o filtro 'Sócio'")
print("  - Filtros 'Filtrar Projetos' e 'Filtrar Estado' só aparecem ao escolher 'Projetos'")
print("  - Testar manualmente na aplicação!")
print("\nFicheiros gerados para verificação:")
print(f"  - {pdf_filename}")
print(f"  - {xlsx_filename}")
print(f"  - {pdf_filtrado}")
