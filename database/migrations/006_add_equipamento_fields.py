# -*- coding: utf-8 -*-
"""
Migration 006: Adicionar campos de equipamento
"""
from sqlalchemy import text


def upgrade(connection):
    """
    Adiciona novos campos à tabela equipamento para suportar orçamentos
    """

    # Adicionar campos de identificação
    try:
        connection.execute(text("ALTER TABLE equipamento ADD COLUMN produto VARCHAR(255)"))
    except Exception:
        pass

    try:
        connection.execute(text("ALTER TABLE equipamento ADD COLUMN tipo VARCHAR(100)"))
    except Exception:
        pass

    try:
        connection.execute(text("ALTER TABLE equipamento ADD COLUMN label VARCHAR(100)"))
    except Exception:
        pass

    try:
        connection.execute(text("ALTER TABLE equipamento ADD COLUMN descricao TEXT"))
    except Exception:
        pass

    # Adicionar especificações técnicas
    try:
        connection.execute(text("ALTER TABLE equipamento ADD COLUMN numero_serie VARCHAR(100)"))
    except Exception:
        pass

    try:
        connection.execute(text("ALTER TABLE equipamento ADD COLUMN mac_address VARCHAR(50)"))
    except Exception:
        pass

    try:
        connection.execute(text("ALTER TABLE equipamento ADD COLUMN referencia VARCHAR(100)"))
    except Exception:
        pass

    try:
        connection.execute(text("ALTER TABLE equipamento ADD COLUMN quantidade INTEGER DEFAULT 1"))
    except Exception:
        pass

    try:
        connection.execute(text("ALTER TABLE equipamento ADD COLUMN tamanho VARCHAR(100)"))
    except Exception:
        pass

    try:
        connection.execute(text("ALTER TABLE equipamento ADD COLUMN fatura_url TEXT"))
    except Exception:
        pass

    # Adicionar campos de aluguer (IMPORTANTE!)
    try:
        connection.execute(text("ALTER TABLE equipamento ADD COLUMN preco_aluguer DECIMAL(10, 2) DEFAULT 0"))
    except Exception:
        pass

    try:
        connection.execute(text("ALTER TABLE equipamento ADD COLUMN amortizacao_vezes INTEGER DEFAULT 0"))
    except Exception:
        pass

    try:
        connection.execute(text("ALTER TABLE equipamento ADD COLUMN foto_url TEXT"))
    except Exception:
        pass

    print("✅ Migration 006: Campos de equipamento adicionados")


def downgrade(connection):
    """
    Remove os campos adicionados (se necessário)
    """
    # SQLite não suporta DROP COLUMN facilmente
    # Deixar como está
    pass
