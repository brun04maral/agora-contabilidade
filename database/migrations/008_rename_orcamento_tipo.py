# -*- coding: utf-8 -*-
"""
Migration 008: Atualizar nomenclatura de orçamentos
- Renomear valores de tipo: 'frontend' → 'cliente', 'backend' → 'empresa'
"""

from sqlalchemy import text


def upgrade(engine):
    """
    Atualiza valores de tipo de orçamentos
    """
    print("Running migration 008: Atualizar nomenclatura de orçamentos...")

    with engine.begin() as conn:
        # Update 'frontend' to 'cliente'
        conn.execute(text("""
            UPDATE orcamentos
            SET tipo = 'cliente'
            WHERE tipo = 'frontend'
        """))

        # Update 'backend' to 'empresa'
        conn.execute(text("""
            UPDATE orcamentos
            SET tipo = 'empresa'
            WHERE tipo = 'backend'
        """))

    print("✅ Migration 008 completed - Nomenclatura atualizada")


def downgrade(engine):
    """
    Reverte valores de tipo de orçamentos
    """
    print("Rolling back migration 008...")

    with engine.begin() as conn:
        # Revert 'cliente' to 'frontend'
        conn.execute(text("""
            UPDATE orcamentos
            SET tipo = 'frontend'
            WHERE tipo = 'cliente'
        """))

        # Revert 'empresa' to 'backend'
        conn.execute(text("""
            UPDATE orcamentos
            SET tipo = 'backend'
            WHERE tipo = 'empresa'
        """))

    print("✅ Migration 008 rolled back")
