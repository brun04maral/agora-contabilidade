#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para executar migration 025
- Migration 025: Criar tabelas freelancers, freelancer_trabalhos, fornecedor_compras
- Expandir tabela fornecedores (numero, categoria, iban)
"""
import os
import sys
import importlib.util
from sqlalchemy import create_engine, text
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


def run_migration_025():
    """Executa migration 025"""
    print("=" * 80)
    print("🔄 EXECUTANDO MIGRATION 025")
    print("=" * 80)
    print()

    # Setup database
    database_url = os.getenv("DATABASE_URL", "sqlite:///./agora_media.db")
    engine = create_engine(database_url)

    try:
        # Run migration 025
        print("📋 Migration 025: Freelancers, Fornecedores Expandidos e Históricos")
        print("-" * 80)
        print("  ✓ Criar tabela freelancers")
        print("  ✓ Criar tabela freelancer_trabalhos")
        print("  ✓ Criar tabela fornecedor_compras")
        print("  ✓ Expandir tabela fornecedores (numero, categoria, iban)")
        print()

        migration_025 = import_migration('025_freelancers_fornecedores.py')
        migration_025.upgrade(engine)

        print()
        print("🔍 Verificando estruturas criadas...")
        print("-" * 80)

        with engine.connect() as connection:
            # Verificar tabela freelancers
            result = connection.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='freelancers'"))
            if result.fetchone():
                print("  ✅ Tabela 'freelancers' criada")
            else:
                print("  ❌ Tabela 'freelancers' NÃO foi criada!")
                return False

            # Verificar tabela freelancer_trabalhos
            result = connection.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='freelancer_trabalhos'"))
            if result.fetchone():
                print("  ✅ Tabela 'freelancer_trabalhos' criada")
            else:
                print("  ❌ Tabela 'freelancer_trabalhos' NÃO foi criada!")
                return False

            # Verificar tabela fornecedor_compras
            result = connection.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='fornecedor_compras'"))
            if result.fetchone():
                print("  ✅ Tabela 'fornecedor_compras' criada")
            else:
                print("  ❌ Tabela 'fornecedor_compras' NÃO foi criada!")
                return False

            # Verificar campos adicionados em fornecedores
            result = connection.execute(text("PRAGMA table_info(fornecedores)"))
            columns = [row[1] for row in result.fetchall()]

            if 'numero' in columns:
                print("  ✅ Campo 'numero' adicionado em fornecedores")
            else:
                print("  ❌ Campo 'numero' NÃO foi adicionado!")
                return False

            if 'categoria' in columns:
                print("  ✅ Campo 'categoria' adicionado em fornecedores")
            else:
                print("  ❌ Campo 'categoria' NÃO foi adicionado!")
                return False

            if 'iban' in columns:
                print("  ✅ Campo 'iban' adicionado em fornecedores")
            else:
                print("  ❌ Campo 'iban' NÃO foi adicionado!")
                return False

            # Contar freelancers e fornecedores
            result = connection.execute(text("SELECT COUNT(*) FROM freelancers"))
            freelancers_count = result.scalar()

            result = connection.execute(text("SELECT COUNT(*) FROM fornecedores"))
            fornecedores_count = result.scalar()

            print()
            print("📊 Estatísticas:")
            print(f"  - {freelancers_count} freelancers na base de dados")
            print(f"  - {fornecedores_count} fornecedores na base de dados")

        print()
        print("=" * 80)
        print("✅ MIGRATION 025 CONCLUÍDA COM SUCESSO")
        print("=" * 80)
        print()
        print("📝 PRÓXIMOS PASSOS:")
        print("  1. Criar modelos: database/models/freelancer.py")
        print("  2. Criar modelos: database/models/freelancer_trabalho.py")
        print("  3. Criar modelos: database/models/fornecedor_compra.py")
        print("  4. Criar manager: logic/freelancers.py")
        print("  5. Expandir manager: logic/fornecedores.py")
        print("  6. Atualizar dialogs EMPRESA com beneficiários multi-entidade")
        print("  7. Testar sistema completo")
        print()

    except Exception as e:
        print("❌ Erro: {}".format(e))
        import traceback
        traceback.print_exc()
        return False

    return True


if __name__ == '__main__':
    success = run_migration_025()
    sys.exit(0 if success else 1)
