#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para executar migration 008 - Atualizar nomenclatura de orçamentos
"""
import os
import sys
from sqlalchemy import create_engine
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database.migrations import migration_008_rename_orcamento_tipo as migration_008


def run_migration_008():
    """Executa migration 008"""
    print("=" * 80)
    print("🔄 EXECUTANDO MIGRATION 008")
    print("=" * 80)
    print()

    # Setup database
    database_url = os.getenv("DATABASE_URL", "sqlite:///./agora.db")
    engine = create_engine(database_url)

    try:
        # Run upgrade
        migration_008.upgrade(engine)
        print()
        print("=" * 80)
        print("✅ MIGRATION 008 CONCLUÍDA")
        print("=" * 80)
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True


if __name__ == '__main__':
    success = run_migration_008()
    sys.exit(0 if success else 1)
