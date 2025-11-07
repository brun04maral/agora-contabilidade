"""
Migration 004: Adicionar valor ANULADO ao enum EstadoProjeto

Adiciona o valor 'ANULADO' ao enum de estado dos projetos.
Para SQLite: Não é necessária alteração na DB pois o enum é armazenado como VARCHAR.
Para PostgreSQL: Seria necessário ALTER TYPE.
"""
from sqlalchemy import text


def upgrade(connection):
    """
    Adiciona valor ANULADO ao enum EstadoProjeto

    NOTA: Para SQLite, o SQLAlchemy implementa ENUMs como VARCHAR,
    então não é necessária nenhuma alteração no schema da database.
    O novo valor será aceito automaticamente.

    Esta migração serve apenas como documentação da mudança.
    """
    # Para SQLite: Nenhuma ação necessária
    # Para PostgreSQL seria:
    # ALTER TYPE estadoprojeto ADD VALUE IF NOT EXISTS 'ANULADO';

    print("✅ Valor 'ANULADO' adicionado ao enum EstadoProjeto (Python)")
    print("   (Nenhuma alteração necessária no schema SQLite)")


def downgrade(connection):
    """
    Remove valor ANULADO do enum EstadoProjeto

    NOTA: Para SQLite não há ação necessária.
    Para PostgreSQL seria necessário recriar o tipo.
    """
    # Para SQLite: Nenhuma ação necessária
    # Para PostgreSQL seria necessário um processo mais complexo de recriação do tipo

    print("✅ Valor 'ANULADO' removido do enum EstadoProjeto (Python)")
    print("   (Nenhuma alteração necessária no schema SQLite)")
