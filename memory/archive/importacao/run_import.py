#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script automático para importar Excel 20251108
"""
import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Adicionar raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load environment
load_dotenv()

# Import the importer
from scripts.import_from_excel import ExcelImporter

def main():
    print("=" * 80)
    print("🚀 IMPORTAÇÃO AUTOMÁTICA DO EXCEL 20251108")
    print("=" * 80)
    print()

    # Setup database
    database_url = os.getenv("DATABASE_URL", "sqlite:///./agora_media.db")
    print(f"📊 Base de dados: {database_url}")
    print(f"📁 Excel: excel/CONTABILIDADE_FINAL_20251108.xlsx")
    print()

    engine = create_engine(database_url)
    Session = sessionmaker(bind=engine)
    session = Session()

    # Executar importação COM limpeza usando o novo Excel
    importer = ExcelImporter(session, excel_path='excel/CONTABILIDADE_FINAL_20251108.xlsx')
    success = importer.executar(limpar_tudo=True)

    session.close()

    if success:
        print("\n✅ IMPORTAÇÃO CONCLUÍDA COM SUCESSO!")
        sys.exit(0)
    else:
        print("\n❌ IMPORTAÇÃO FALHOU!")
        sys.exit(1)

if __name__ == '__main__':
    main()
