# -*- coding: utf-8 -*-
"""
Migration 009: Criar tabela equipamento_alugueres
- Tabela para registar cada aluguer de equipamento
- Usado para cálculo de amortização e ROI
"""

from sqlalchemy import text


def upgrade(engine):
    """
    Cria tabela equipamento_alugueres
    """
    print("Running migration 009: Criar tabela equipamento_alugueres...")

    with engine.begin() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS equipamento_alugueres (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                equipamento_id INTEGER NOT NULL,
                orcamento_id INTEGER,
                data_aluguer DATE NOT NULL,
                dias_alugados INTEGER NOT NULL DEFAULT 1,
                valor_alugado DECIMAL(10, 2) NOT NULL,
                descricao TEXT,
                notas TEXT,
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (equipamento_id) REFERENCES equipamento(id) ON DELETE CASCADE,
                FOREIGN KEY (orcamento_id) REFERENCES orcamentos(id) ON DELETE SET NULL
            )
        """))

        # Criar índices para melhorar performance
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_equipamento_alugueres_equipamento_id
            ON equipamento_alugueres(equipamento_id)
        """))

        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_equipamento_alugueres_orcamento_id
            ON equipamento_alugueres(orcamento_id)
        """))

        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_equipamento_alugueres_data
            ON equipamento_alugueres(data_aluguer)
        """))

    print("✅ Migration 009 completed - Tabela equipamento_alugueres criada")


def downgrade(engine):
    """
    Remove tabela equipamento_alugueres
    """
    print("Rolling back migration 009...")

    with engine.begin() as conn:
        # Remover índices primeiro
        conn.execute(text("DROP INDEX IF EXISTS idx_equipamento_alugueres_equipamento_id"))
        conn.execute(text("DROP INDEX IF EXISTS idx_equipamento_alugueres_orcamento_id"))
        conn.execute(text("DROP INDEX IF EXISTS idx_equipamento_alugueres_data"))

        # Remover tabela
        conn.execute(text("DROP TABLE IF EXISTS equipamento_alugueres"))

    print("✅ Migration 009 rolled back")
