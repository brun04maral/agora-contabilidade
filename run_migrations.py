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
    from database.migrations import (
        add_pais_to_fornecedor
    )

    migrations = [
        ('003_add_pais_to_fornecedor', add_pais_to_fornecedor),
    ]

    with engine.connect() as connection:
        for name, migration_module in migrations:
            print(f"Executando: {name}")
            try:
                migration_module.upgrade(connection)
                connection.commit()
                print(f"  ✅ {name} completado")
            except Exception as e:
                print(f"  ⚠️  {name} - {e}")
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
