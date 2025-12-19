# -*- coding: utf-8 -*-
"""
Migration 010: Refatorar orçamento para estrutura única
- Remover colunas tipo e versao (conceito descartado)
- Adicionar colunas para versão cliente (tem_versao_cliente, titulo_cliente, descricao_cliente)
"""

from sqlalchemy import text


def upgrade(engine):
    """
    Refatora estrutura de orçamentos para modelo único
    """
    print("Running migration 010: Refatorar orçamento único...")

    with engine.begin() as conn:
        # Adicionar novas colunas primeiro (para SQLite não perder dados)
        try:
            conn.execute(text("""
                ALTER TABLE orcamentos
                ADD COLUMN tem_versao_cliente BOOLEAN NOT NULL DEFAULT 0
            """))
        except Exception as e:
            if 'duplicate column' not in str(e).lower():
                raise

        try:
            conn.execute(text("""
                ALTER TABLE orcamentos
                ADD COLUMN titulo_cliente VARCHAR(255)
            """))
        except Exception as e:
            if 'duplicate column' not in str(e).lower():
                raise

        try:
            conn.execute(text("""
                ALTER TABLE orcamentos
                ADD COLUMN descricao_cliente TEXT
            """))
        except Exception as e:
            if 'duplicate column' not in str(e).lower():
                raise

        # SQLite não suporta DROP COLUMN diretamente
        # Precisamos criar nova tabela e migrar dados
        print("  - Criando nova estrutura de tabela...")

        conn.execute(text("""
            CREATE TABLE orcamentos_new (
                id INTEGER PRIMARY KEY,
                codigo VARCHAR(100) NOT NULL UNIQUE,
                cliente_id INTEGER,
                data_criacao DATE NOT NULL,
                data_evento VARCHAR(200),
                local_evento VARCHAR(200),
                descricao_proposta TEXT,
                valor_total DECIMAL(10, 2),
                total_parcial_1 DECIMAL(10, 2),
                total_parcial_2 DECIMAL(10, 2),
                notas_contratuais TEXT,
                status VARCHAR(20) NOT NULL DEFAULT 'rascunho',
                tem_versao_cliente BOOLEAN NOT NULL DEFAULT 0,
                titulo_cliente VARCHAR(255),
                descricao_cliente TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (cliente_id) REFERENCES clientes(id)
            )
        """))

        print("  - Migrando dados...")
        conn.execute(text("""
            INSERT INTO orcamentos_new (
                id, codigo, cliente_id, data_criacao, data_evento, local_evento,
                descricao_proposta, valor_total, total_parcial_1, total_parcial_2,
                notas_contratuais, status, tem_versao_cliente, titulo_cliente,
                descricao_cliente, created_at, updated_at
            )
            SELECT
                id, codigo, cliente_id, data_criacao, data_evento, local_evento,
                descricao_proposta, valor_total, total_parcial_1, total_parcial_2,
                notas_contratuais, status,
                COALESCE(tem_versao_cliente, 0),
                titulo_cliente,
                descricao_cliente,
                created_at, updated_at
            FROM orcamentos
        """))

        print("  - Substituindo tabela antiga...")
        conn.execute(text("DROP TABLE orcamentos"))
        conn.execute(text("ALTER TABLE orcamentos_new RENAME TO orcamentos"))

        print("  - Recriando índices...")
        conn.execute(text("""
            CREATE UNIQUE INDEX IF NOT EXISTS idx_orcamentos_codigo
            ON orcamentos(codigo)
        """))

        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_orcamentos_cliente_id
            ON orcamentos(cliente_id)
        """))

    print("✅ Migration 010 completed - Orçamento refatorado para estrutura única")


def downgrade(engine):
    """
    Reverte para estrutura anterior (adiciona tipo e versao de volta)
    """
    print("Rolling back migration 010...")

    with engine.begin() as conn:
        print("  - Criando estrutura antiga...")

        conn.execute(text("""
            CREATE TABLE orcamentos_old (
                id INTEGER PRIMARY KEY,
                codigo VARCHAR(100) NOT NULL UNIQUE,
                versao VARCHAR(10),
                tipo VARCHAR(20) NOT NULL DEFAULT 'cliente',
                cliente_id INTEGER,
                data_criacao DATE NOT NULL,
                data_evento VARCHAR(200),
                local_evento VARCHAR(200),
                descricao_proposta TEXT,
                valor_total DECIMAL(10, 2),
                total_parcial_1 DECIMAL(10, 2),
                total_parcial_2 DECIMAL(10, 2),
                notas_contratuais TEXT,
                status VARCHAR(20) NOT NULL DEFAULT 'rascunho',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (cliente_id) REFERENCES clientes(id)
            )
        """))

        print("  - Migrando dados de volta...")
        conn.execute(text("""
            INSERT INTO orcamentos_old (
                id, codigo, versao, tipo, cliente_id, data_criacao, data_evento, local_evento,
                descricao_proposta, valor_total, total_parcial_1, total_parcial_2,
                notas_contratuais, status, created_at, updated_at
            )
            SELECT
                id, codigo, NULL, 'cliente', cliente_id, data_criacao, data_evento, local_evento,
                descricao_proposta, valor_total, total_parcial_1, total_parcial_2,
                notas_contratuais, status, created_at, updated_at
            FROM orcamentos
        """))

        conn.execute(text("DROP TABLE orcamentos"))
        conn.execute(text("ALTER TABLE orcamentos_old RENAME TO orcamentos"))

    print("✅ Migration 010 rolled back")
