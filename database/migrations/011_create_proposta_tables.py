#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Migration 011: Criar tabelas para Proposta (versão cliente)
- Cria tabela proposta_secoes
- Cria tabela proposta_itens
"""
from sqlalchemy import text


def upgrade(engine):
    """
    Cria tabelas para gestão independente dos itens da proposta (versão cliente)
    """
    print("🔄 Criando tabelas proposta_secoes e proposta_itens...")

    with engine.connect() as conn:
        # Criar tabela proposta_secoes
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS proposta_secoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                orcamento_id INTEGER NOT NULL,
                nome VARCHAR(100) NOT NULL,
                ordem INTEGER NOT NULL DEFAULT 0,
                subtotal DECIMAL(10, 2),
                FOREIGN KEY (orcamento_id) REFERENCES orcamentos(id) ON DELETE CASCADE
            )
        """))

        # Criar tabela proposta_itens
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS proposta_itens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                orcamento_id INTEGER NOT NULL,
                secao_id INTEGER NOT NULL,
                descricao TEXT NOT NULL,
                quantidade INTEGER NOT NULL DEFAULT 1,
                dias INTEGER NOT NULL DEFAULT 1,
                preco_unitario DECIMAL(10, 2) NOT NULL,
                desconto DECIMAL(5, 4) NOT NULL DEFAULT 0,
                total DECIMAL(10, 2) NOT NULL,
                ordem INTEGER NOT NULL DEFAULT 0,
                FOREIGN KEY (orcamento_id) REFERENCES orcamentos(id) ON DELETE CASCADE,
                FOREIGN KEY (secao_id) REFERENCES proposta_secoes(id) ON DELETE CASCADE
            )
        """))

        conn.commit()

    print("✅ Tabelas criadas com sucesso!")


def downgrade(engine):
    """
    Remove tabelas de proposta
    """
    print("🔄 Removendo tabelas proposta_secoes e proposta_itens...")

    with engine.connect() as conn:
        conn.execute(text("DROP TABLE IF EXISTS proposta_itens"))
        conn.execute(text("DROP TABLE IF EXISTS proposta_secoes"))
        conn.commit()

    print("✅ Tabelas removidas com sucesso!")


if __name__ == '__main__':
    import os
    import sys
    from sqlalchemy import create_engine
    from dotenv import load_dotenv

    load_dotenv()

    database_url = os.getenv("DATABASE_URL", "sqlite:///./agora.db")
    engine = create_engine(database_url)

    if len(sys.argv) > 1 and sys.argv[1] == 'down':
        downgrade(engine)
    else:
        upgrade(engine)
