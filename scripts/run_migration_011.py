#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para executar migration 011
- Migration 011: Criar tabelas proposta_secoes e proposta_itens
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


def import_migration(migration_file):
    """Import migration module using importlib"""
    migration_path = os.path.join(
        os.path.dirname(__file__),
        '..',
        'database',
        'migrations',
        migration_file
    )
    module_name = "migration_{}".format(migration_file)
    spec = importlib.util.spec_from_file_location(module_name, migration_path)
    migration = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(migration)
    return migration


def run_migration_011():
    """Executa migration 011"""
    print("=" * 80)
    print("🔄 EXECUTANDO MIGRATION 011")
    print("=" * 80)
    print()

    # Setup database
    database_url = os.getenv("DATABASE_URL", "sqlite:///./agora.db")
    engine = create_engine(database_url)

    try:
        # Run migration 011
        print("📋 Migration 011: Criar tabelas proposta_secoes e proposta_itens")
        print("-" * 80)
        migration_011 = import_migration('011_create_proposta_tables.py')
        migration_011.upgrade(engine)
        print()

        print("=" * 80)
        print("✅ MIGRATION CONCLUÍDA COM SUCESSO")
        print("=" * 80)
    except Exception as e:
        print("❌ Erro: {}".format(e))
        import traceback
        traceback.print_exc()
        return False

    return True


if __name__ == '__main__':
    success = run_migration_011()
    sys.exit(0 if success else 1)
