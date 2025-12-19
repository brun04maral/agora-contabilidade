# -*- coding: utf-8 -*-
"""
Migration 016 - Criar tabela valores_referencia_anual

Cria tabela para armazenar valores de referência anuais dos boletins.
Valores podem mudar anualmente (leis laborais).
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers
revision = '016'
down_revision = '015'
branch_labels = None
depends_on = None


def upgrade():
    """
    Cria tabela valores_referencia_anual
    """
    op.create_table(
        'valores_referencia_anual',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('ano', sa.Integer(), nullable=False, unique=True, index=True),
        sa.Column('val_dia_nacional', sa.Numeric(10, 2), nullable=False),
        sa.Column('val_dia_estrangeiro', sa.Numeric(10, 2), nullable=False),
        sa.Column('val_km', sa.Numeric(10, 2), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # Inserir valor default para 2025
    op.execute("""
        INSERT INTO valores_referencia_anual (ano, val_dia_nacional, val_dia_estrangeiro, val_km, created_at, updated_at)
        VALUES (2025, 72.65, 167.07, 0.40, datetime('now'), datetime('now'))
    """)


def downgrade():
    """Remove tabela valores_referencia_anual"""
    op.drop_table('valores_referencia_anual')
