# -*- coding: utf-8 -*-
"""
Script para executar migration 013 - Adicionar recorrência a despesas
"""
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

def run_migration():
    """Executar migration 013"""
    load_dotenv()

    # Get database URL from environment or use default
    database_url = os.getenv("DATABASE_URL", "sqlite:///./agora_media.db")
    engine = create_engine(database_url)

    with engine.connect() as conn:
        try:
            # Add is_recorrente column
            conn.execute(text("ALTER TABLE despesas ADD COLUMN is_recorrente BOOLEAN NOT NULL DEFAULT 0"))
            print("✅ Coluna 'is_recorrente' adicionada")

            # Add dia_recorrencia column
            conn.execute(text("ALTER TABLE despesas ADD COLUMN dia_recorrencia INTEGER"))
            print("✅ Coluna 'dia_recorrencia' adicionada")

            # Add despesa_template_id column
            conn.execute(text("ALTER TABLE despesas ADD COLUMN despesa_template_id INTEGER"))
            print("✅ Coluna 'despesa_template_id' adicionada")

            # Note: SQLite doesn't enforce foreign keys by default in ALTER TABLE
            # The relationship will be handled by SQLAlchemy ORM

            conn.commit()
            print("✅ Migration 013 aplicada com sucesso!")
            print("   - Adicionado suporte para despesas recorrentes automáticas")
            print("   - Campos: is_recorrente, dia_recorrencia, despesa_template_id")

        except Exception as e:
            error_msg = str(e).lower()
            if "duplicate column name" in error_msg or "already exists" in error_msg:
                print("⚠️  Campos de recorrência já existem - migration já foi aplicada")
            else:
                print(f"❌ Erro ao aplicar migration: {e}")
                raise

if __name__ == "__main__":
    run_migration()
