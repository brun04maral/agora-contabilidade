#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para executar migration 010 - Refatorar orçamento para estrutura única
"""
import os
import sys
import importlib.util
from sqlalchemy import create_engine
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import migration module using importlib (files starting with numbers can't be imported normally)
migration_path = os.path.join(
    os.path.dirname(__file__),
    '..',
    'database',
    'migrations',
    '010_refactor_orcamento_unico.py'
)
spec = importlib.util.spec_from_file_location("migration_010", migration_path)
migration_010 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(migration_010)


def run_migration_010():
    """Executa migration 010"""
    print("=" * 80)
    print("🔄 EXECUTANDO MIGRATION 010")
    print("=" * 80)
    print()

    # Setup database
    database_url = os.getenv("DATABASE_URL", "sqlite:///./agora.db")
    engine = create_engine(database_url)

    try:
        # Run upgrade
        migration_010.upgrade(engine)
        print()
        print("=" * 80)
        print("✅ MIGRATION 010 CONCLUÍDA")
        print("=" * 80)
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True


if __name__ == '__main__':
    success = run_migration_010()
    sys.exit(0 if success else 1)
