# -*- coding: utf-8 -*-
"""
Migration 024: Adicionar campo projeto_id à tabela orcamentos

Adiciona link bidirecional orçamento ↔ projeto para rastreabilidade
e prevenção de conversão dupla.
"""
from sqlalchemy import create_engine, text


def upgrade(connection):
    """
    Adiciona coluna projeto_id à tabela orcamentos
    """
    # Adicionar coluna projeto_id
    connection.execute(text("""
        ALTER TABLE orcamentos
        ADD COLUMN projeto_id INTEGER NULL
    """))

    # Criar índice para performance
    connection.execute(text("""
        CREATE INDEX IF NOT EXISTS idx_orcamentos_projeto
        ON orcamentos(projeto_id)
    """))

    # Nota: Foreign key constraint será gerenciada pelo SQLAlchemy no modelo
    # SQLite tem limitações com ALTER TABLE para adicionar FK constraints

    connection.commit()


def downgrade(connection):
    """
    Remove coluna projeto_id da tabela orcamentos

    Nota: SQLite não suporta DROP COLUMN diretamente.
    É necessário recriar a tabela sem o campo.
    """
    # 1. Criar tabela temporária sem projeto_id
    connection.execute(text("""
        CREATE TABLE orcamentos_temp AS
        SELECT
            id, codigo, owner, cliente_id,
            data_criacao, data_evento, local_evento,
            valor_total, status,
            created_at, updated_at
        FROM orcamentos
    """))

    # 2. Dropar tabela original
    connection.execute(text("DROP TABLE orcamentos"))

    # 3. Renomear tabela temporária
    connection.execute(text("ALTER TABLE orcamentos_temp RENAME TO orcamentos"))

    # 4. Recriar índices
    connection.execute(text("""
        CREATE INDEX IF NOT EXISTS idx_orcamentos_codigo
        ON orcamentos(codigo)
    """))

    connection.execute(text("""
        CREATE INDEX IF NOT EXISTS idx_orcamentos_cliente
        ON orcamentos(cliente_id)
    """))

    connection.execute(text("""
        CREATE INDEX IF NOT EXISTS idx_orcamentos_status
        ON orcamentos(status)
    """))

    connection.commit()


if __name__ == "__main__":
    """Executar migration standalone"""
    import os
    import sys

    # Adicionar path do projeto
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

    # Criar engine
    engine = create_engine('sqlite:///agora_media.db')

    with engine.connect() as conn:
        print("🔧 Executando migration 024: add projeto_id to orcamentos...")
        upgrade(conn)
        print("✅ Migration 024 aplicada com sucesso!")

        # Verificar estrutura
        result = conn.execute(text('PRAGMA table_info(orcamentos);'))
        print("\n📊 Estrutura da tabela orcamentos:")
        for row in result:
            print(f"  {row[1]}: {row[2]} {'NOT NULL' if row[3] == 1 else 'NULL'}")

        # Verificar se projeto_id existe
        print("\n🔍 Verificação do campo projeto_id:")
        result = conn.execute(text("PRAGMA table_info(orcamentos);"))
        projeto_id_exists = any(row[1] == 'projeto_id' for row in result)
        if projeto_id_exists:
            print("  ✅ Campo projeto_id criado com sucesso!")
        else:
            print("  ❌ Campo projeto_id NÃO foi criado!")
