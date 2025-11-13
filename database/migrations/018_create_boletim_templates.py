# -*- coding: utf-8 -*-
"""
Migration 018 - Criar tabela boletim_templates

Cria tabela para templates de boletins recorrentes.
Templates permitem gerar boletins automaticamente mensalmente.
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers
revision = '018'
down_revision = '017'
branch_labels = None
depends_on = None


def upgrade():
    """
    Cria tabela boletim_templates
    """
    op.create_table(
        'boletim_templates',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('numero', sa.String(20), nullable=False, unique=True, index=True),
        sa.Column('nome', sa.String(200), nullable=False),
        sa.Column('socio', sa.Enum('BRUNO', 'RAFAEL', name='socio'), nullable=False, index=True),
        sa.Column('dia_mes', sa.Integer(), nullable=False),
        sa.Column('ativo', sa.Boolean(), nullable=False, default=True, index=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    """Remove tabela boletim_templates"""
    op.drop_table('boletim_templates')
