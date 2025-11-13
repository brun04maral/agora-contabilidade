#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para executar migration 012 - Adicionar website a fornecedores
"""
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

def run_migration():
    """Executar migration 012"""
    load_dotenv()

    # Get database URL from environment or use default
    database_url = os.getenv("DATABASE_URL", "sqlite:///./agora_media.db")
    engine = create_engine(database_url)

    with engine.connect() as conn:
        try:
            # Add website column
            conn.execute(text("ALTER TABLE fornecedores ADD COLUMN website VARCHAR(255)"))
            conn.commit()
            print("✅ Migration 012 aplicada com sucesso!")
            print("   - Adicionada coluna 'website' à tabela fornecedores")
        except Exception as e:
            error_msg = str(e).lower()
            if "duplicate column name" in error_msg or "already exists" in error_msg:
                print("⚠️  Coluna 'website' já existe - migration já foi aplicada")
            else:
                print(f"❌ Erro ao aplicar migration: {e}")
                raise

if __name__ == "__main__":
    run_migration()
