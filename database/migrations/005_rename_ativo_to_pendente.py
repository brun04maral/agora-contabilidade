#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Migração 005: Renomear estado ATIVO para PENDENTE em despesas

IMPORTANTE: Execute este script ANTES de iniciar a aplicação após o pull
para atualizar os valores na base de dados.

Execução:
    python3 database/migrations/005_rename_ativo_to_pendente.py
"""
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️  Aviso: módulo dotenv não encontrado. A usar variáveis de ambiente do sistema.")

from sqlalchemy import create_engine, text


def upgrade():
    """Atualizar valores ATIVO para PENDENTE"""
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        print("❌ Erro: DATABASE_URL não encontrado nas variáveis de ambiente")
        print("   Por favor, configure o ficheiro .env com DATABASE_URL")
        sys.exit(1)

    print(f"🔗 Conectando à base de dados...")
    engine = create_engine(database_url)

    with engine.connect() as conn:
        # Atualizar todos os registos com estado ATIVO para PENDENTE
        print("🔄 Atualizando despesas com estado ATIVO para PENDENTE...")
        result = conn.execute(
            text("UPDATE despesas SET estado = 'PENDENTE' WHERE estado = 'ATIVO'")
        )
        conn.commit()

        rows_updated = result.rowcount
        print(f"✅ Migração 005 concluída: {rows_updated} despesas atualizadas")


def downgrade():
    """Reverter: PENDENTE para ATIVO (apenas se necessário)"""
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        print("❌ Erro: DATABASE_URL não encontrado")
        sys.exit(1)

    engine = create_engine(database_url)

    with engine.connect() as conn:
        # Reverter PENDENTE para ATIVO
        result = conn.execute(
            text("UPDATE despesas SET estado = 'ATIVO' WHERE estado = 'PENDENTE'")
        )
        conn.commit()

        rows_updated = result.rowcount
        print(f"✅ Rollback 005: {rows_updated} despesas revertidas")


if __name__ == "__main__":
    print("=" * 60)
    print("Migração 005: Renomear estado ATIVO → PENDENTE")
    print("=" * 60)
    upgrade()
    print("\n✨ Migração concluída com sucesso!")
    print("   Pode agora executar a aplicação normalmente.")
    print("=" * 60)
