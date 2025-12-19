#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Teste de exportação de relatório de Saldos com listas detalhadas
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
print("🧪 TESTE DE EXPORTAÇÃO DE RELATÓRIO DE SALDOS COM LISTAS DETALHADAS")
print("=" * 80)

# Generate report
print("\n[1] Gerando relatório de Saldos (ambos sócios)...")
relatorio = manager.gerar_relatorio_saldos()

print(f"\nRelatório gerado:")
print(f"  Tipo: {relatorio['tipo']}")
print(f"  Título: {relatorio['titulo']}")
print(f"  Sócios: {len(relatorio['socios'])}")

for socio_data in relatorio['socios']:
    print(f"\n  {socio_data['nome']}:")
    print(f"    Saldo: {socio_data['saldo']}")
    print(f"    Projetos Pessoais: {len(socio_data.get('projetos_pessoais_list', []))} items")
    print(f"    Prémios: {len(socio_data.get('premios_list', []))} items")
    print(f"    Despesas Fixas: {len(socio_data.get('despesas_fixas_list', []))} items")
    print(f"    Boletins: {len(socio_data.get('boletins_list', []))} items")
    print(f"    Despesas Pessoais: {len(socio_data.get('despesas_pessoais_list', []))} items")

# Test PDF export
print("\n[2] Exportando para PDF...")
pdf_filename = "/tmp/test_saldos_detalhado.pdf"
try:
    manager.exportar_pdf(relatorio, pdf_filename)
    file_size = os.path.getsize(pdf_filename)
    print(f"  ✅ PDF exportado: {pdf_filename} ({file_size:,} bytes)")

    # Check if file was created
    if os.path.exists(pdf_filename):
        print("  ✅ Ficheiro criado com sucesso")
    else:
        print("  ❌ Ficheiro não foi criado")
except Exception as e:
    print(f"  ❌ Erro ao exportar PDF: {e}")

# Test Excel export
print("\n[3] Exportando para Excel...")
xlsx_filename = "/tmp/test_saldos_detalhado.xlsx"
try:
    manager.exportar_excel(relatorio, xlsx_filename)
    file_size = os.path.getsize(xlsx_filename)
    print(f"  ✅ Excel exportado: {xlsx_filename} ({file_size:,} bytes)")

    # Check if file was created
    if os.path.exists(xlsx_filename):
        print("  ✅ Ficheiro criado com sucesso")
    else:
        print("  ❌ Ficheiro não foi criado")
except Exception as e:
    print(f"  ❌ Erro ao exportar Excel: {e}")

session.close()

print("\n" + "=" * 80)
print("✅ TESTE COMPLETO")
print("=" * 80)
print(f"\nFicheiros gerados:")
print(f"  - {pdf_filename}")
print(f"  - {xlsx_filename}")
print("\nAbra os ficheiros para verificar que as listas detalhadas estão presentes!")
