#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para executar migration 024
- Migration 024: Adicionar campo projeto_id à tabela orcamentos
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
    module_name = "migration_{}".format(migration_file.replace('.py', '').replace('-', '_'))
    spec = importlib.util.spec_from_file_location(module_name, migration_path)
    migration = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(migration)
    return migration


def run_migration_024():
    """Executa migration 024"""
    print("=" * 80)
    print("🔄 EXECUTANDO MIGRATION 024")
    print("=" * 80)
    print()

    # Setup database
    database_url = os.getenv("DATABASE_URL", "sqlite:///./agora_media.db")
    engine = create_engine(database_url)

    try:
        # Run migration 024
        print("📋 Migration 024: Adicionar campo projeto_id à tabela orcamentos")
        print("-" * 80)

        with engine.connect() as connection:
            migration_024 = import_migration('024_add_projeto_id_to_orcamento.py')
            migration_024.upgrade(connection)

        print()
        print("✅ Campo projeto_id adicionado com sucesso!")
        print()

        # Verificar se campo foi criado
        print("🔍 Verificando estrutura da tabela orcamentos...")
        print("-" * 80)

        with engine.connect() as connection:
            from sqlalchemy import text
            result = connection.execute(text('PRAGMA table_info(orcamentos);'))

            projeto_id_exists = False
            for row in result:
                if row[1] == 'projeto_id':
                    projeto_id_exists = True
                    print(f"  ✅ projeto_id: {row[2]} {'NOT NULL' if row[3] == 1 else 'NULL'}")
                    break

            if not projeto_id_exists:
                print("  ❌ Campo projeto_id NÃO foi criado!")
                return False

        print()
        print("=" * 80)
        print("✅ MIGRATION CONCLUÍDA COM SUCESSO")
        print("=" * 80)
        print()
        print("📝 PRÓXIMOS PASSOS:")
        print("  1. Reiniciar aplicação para carregar novo modelo")
        print("  2. Testar conversão de orçamento em projeto")
        print("  3. Verificar link bidirecional orçamento ↔ projeto")
        print()

    except Exception as e:
        print("❌ Erro: {}".format(e))
        import traceback
        traceback.print_exc()
        return False

    return True


if __name__ == '__main__':
    success = run_migration_024()
    sys.exit(0 if success else 1)
