"""
Migration 003: Adicionar campo pais à tabela fornecedores

Adiciona o campo 'pais' para cálculo de IVA
"""
from sqlalchemy import text


def upgrade(connection):
    """Adiciona coluna pais à tabela fornecedores"""
    connection.execute(text("""
        ALTER TABLE fornecedores
        ADD COLUMN pais VARCHAR(100) DEFAULT 'Portugal'
    """))

    print("✅ Coluna 'pais' adicionada à tabela 'fornecedores'")


def downgrade(connection):
    """Remove coluna pais da tabela fornecedores"""
    connection.execute(text("""
        ALTER TABLE fornecedores
        DROP COLUMN pais
    """))

    print("✅ Coluna 'pais' removida da tabela 'fornecedores'")
