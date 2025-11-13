#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para executar migration 012 - Adicionar website a fornecedores
"""
from sqlalchemy import text
from database.models.base import engine

def run_migration():
    """Executar migration 012"""
    with engine.connect() as conn:
        try:
            # Add website column
            conn.execute(text("ALTER TABLE fornecedores ADD COLUMN website VARCHAR(255)"))
            conn.commit()
            print("✅ Migration 012 aplicada com sucesso!")
            print("   - Adicionada coluna 'website' à tabela fornecedores")
        except Exception as e:
            if "duplicate column name" in str(e).lower():
                print("⚠️  Coluna 'website' já existe - migration já foi aplicada")
            else:
                print(f"❌ Erro ao aplicar migration: {e}")
                raise

if __name__ == "__main__":
    run_migration()
