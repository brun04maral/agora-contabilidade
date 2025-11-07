#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para executar migrations
"""
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment
load_dotenv()


def run_migrations():
    """Executa todas as migrations"""
    print("=" * 80)
    print("🔄 EXECUTANDO MIGRATIONS")
    print("=" * 80)
    print()

    # Setup database
    database_url = os.getenv("DATABASE_URL", "sqlite:///./agora_media.db")
    engine = create_engine(database_url)

    # Import migrations
    import importlib

    migrations = [
        '003_add_pais_to_fornecedor',
        '004_add_anulado_estado',
    ]

    with engine.connect() as connection:
        for migration_name in migrations:
            print(f"Executando: {migration_name}")
            try:
                # Importar módulo dinamicamente
                module = importlib.import_module(f'database.migrations.{migration_name}')

                # Executar upgrade
                module.upgrade(connection)
                connection.commit()
                print(f"  ✅ {migration_name} completado")
            except Exception as e:
                print(f"  ⚠️  {migration_name} - {e}")
                # Pode ser que a coluna já exista
                if 'duplicate column' in str(e).lower() or 'already exists' in str(e).lower():
                    print(f"     (coluna já existe, continuando...)")
                else:
                    connection.rollback()
                    raise
            print()

    print("=" * 80)
    print("✅ MIGRATIONS CONCLUÍDAS")
    print("=" * 80)


if __name__ == '__main__':
    run_migrations()
