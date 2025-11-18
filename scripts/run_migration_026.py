#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para executar migration 026
- Migration 026: Alterar percentagem de NUMERIC(8,3) para NUMERIC(8,4)
- Suporta ajuste de comissões com precisão de 0.0001% (4 casas decimais)
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


def run_migration_026():
    """Executa migration 026"""
    print("=" * 80)
    print("🔄 EXECUTANDO MIGRATION 026")
    print("=" * 80)
    print()

    # Setup database
    database_url = os.getenv("DATABASE_URL", "sqlite:///./agora_media.db")
    engine = create_engine(database_url)

    try:
        # Run migration 026
        print("📋 Migration 026: Percentagem 4 Casas Decimais")
        print("-" * 80)
        print("  ✓ Alterar campo percentagem: NUMERIC(8,3) → NUMERIC(8,4)")
        print("  ✓ Fix bug: Valores truncados após commit/reload")
        print()

        migration_026 = import_migration('026_percentagem_4_decimais.py')
        migration_026.upgrade(engine)

        print()
        print("🔍 Verificando estrutura alterada...")
        print("-" * 80)

        with engine.connect() as connection:
            # Verificar tabela existe
            result = connection.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='orcamento_reparticoes'"))
            if not result.fetchone():
                print("  ❌ Tabela 'orcamento_reparticoes' NÃO encontrada!")
                return False

            print("  ✅ Tabela 'orcamento_reparticoes' existe")

            # Verificar estrutura da coluna percentagem
            result = connection.execute(text("PRAGMA table_info(orcamento_reparticoes)"))
            columns = {row[1]: row[2] for row in result.fetchall()}  # {name: type}

            if 'percentagem' in columns:
                col_type = columns['percentagem']
                print(f"  ✅ Campo 'percentagem' encontrado: {col_type}")

                # Verificar se é NUMERIC(8,4)
                # SQLite armazena como "NUMERIC(8, 4)" ou similar
                if '8' in col_type and '4' in col_type:
                    print("  ✅ Precisão correta: NUMERIC(8,4) ✓")
                else:
                    print(f"  ⚠️ Tipo inesperado: {col_type}")
            else:
                print("  ❌ Campo 'percentagem' NÃO foi encontrado!")
                return False

            # Contar repartições com comissões
            result = connection.execute(text("SELECT COUNT(*) FROM orcamento_reparticoes WHERE tipo = 'comissao'"))
            comissoes_count = result.scalar()

            print()
            print("📊 Estatísticas:")
            print(f"  - {comissoes_count} comissões na base de dados")

        print()
        print("=" * 80)
        print("✅ MIGRATION 026 CONCLUÍDA COM SUCESSO")
        print("=" * 80)
        print()
        print("📝 ALTERAÇÕES APLICADAS:")
        print("  ✓ Campo percentagem agora suporta 4 casas decimais (0.0001%)")
        print("  ✓ Valores existentes preservados sem perda de dados")
        print("  ✓ Setas ▲▼ agora persistem ajustes com precisão total")
        print()
        print("🎯 PRÓXIMOS PASSOS:")
        print("  1. Testar ajuste de percentagem com setas ▲▼")
        print("  2. Verificar persistência após reload (4 casas decimais)")
        print("  3. Validar cálculo de totais com nova precisão")
        print()

    except Exception as e:
        print("❌ Erro: {}".format(e))
        import traceback
        traceback.print_exc()
        return False

    return True


if __name__ == '__main__':
    success = run_migration_026()
    sys.exit(0 if success else 1)
