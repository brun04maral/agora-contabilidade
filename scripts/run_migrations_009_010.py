#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para executar migrations 009 e 010 em sequência
- Migration 009: Criar tabela equipamento_alugueres
- Migration 010: Refatorar orçamento para estrutura única
"""
from __future__ import print_function
import os
import sys
import imp
from sqlalchemy import create_engine
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def import_migration(migration_file):
    """Import migration module using imp"""
    migration_path = os.path.join(
        os.path.dirname(__file__),
        '..',
        'database',
        'migrations',
        migration_file
    )
    module_name = "migration_{}".format(migration_file.replace('.py', '').replace('-', '_'))
    return imp.load_source(module_name, migration_path)


def run_migrations():
    """Executa migrations 009 e 010"""
    print("=" * 80)
    print("🔄 EXECUTANDO MIGRATIONS 009 e 010")
    print("=" * 80)
    print()

    # Setup database
    database_url = os.getenv("DATABASE_URL", "sqlite:///./agora.db")
    engine = create_engine(database_url)

    try:
        # Run migration 009
        print("📋 Migration 009: Criar tabela equipamento_alugueres")
        print("-" * 80)
        migration_009 = import_migration('009_create_equipamento_aluguer.py')
        migration_009.upgrade(engine)
        print()

        # Run migration 010
        print("📋 Migration 010: Refatorar orçamento para estrutura única")
        print("-" * 80)
        migration_010 = import_migration('010_refactor_orcamento_unico.py')
        migration_010.upgrade(engine)
        print()

        print("=" * 80)
        print("✅ TODAS AS MIGRATIONS CONCLUÍDAS COM SUCESSO")
        print("=" * 80)
    except Exception as e:
        print("❌ Erro: {}".format(e))
        import traceback
        traceback.print_exc()
        return False

    return True


if __name__ == '__main__':
    success = run_migrations()
    sys.exit(0 if success else 1)
