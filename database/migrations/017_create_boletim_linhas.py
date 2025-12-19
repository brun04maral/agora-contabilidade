# -*- coding: utf-8 -*-
"""
Migration 017 - Criar tabela boletim_linhas

Cria tabela para linhas de deslocação de boletins itinerários.
Cada linha representa uma deslocação/viagem realizada.
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers
revision = '017'
down_revision = '016'
branch_labels = None
depends_on = None


def upgrade():
    """
    Cria tabela boletim_linhas
    """
    op.create_table(
        'boletim_linhas',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('boletim_id', sa.Integer(), nullable=False, index=True),
        sa.Column('ordem', sa.Integer(), nullable=False),
        sa.Column('projeto_id', sa.Integer(), nullable=True, index=True),
        sa.Column('servico', sa.Text(), nullable=False),
        sa.Column('localidade', sa.String(100), nullable=True),
        sa.Column('data_inicio', sa.Date(), nullable=True),
        sa.Column('hora_inicio', sa.Time(), nullable=True),
        sa.Column('data_fim', sa.Date(), nullable=True),
        sa.Column('hora_fim', sa.Time(), nullable=True),
        sa.Column('tipo', sa.Enum('NACIONAL', 'ESTRANGEIRO', name='tipodeslocacao'), nullable=False, server_default='NACIONAL'),
        sa.Column('dias', sa.Numeric(10, 2), nullable=False, default=0),
        sa.Column('kms', sa.Integer(), nullable=False, default=0),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # Foreign keys
    op.create_foreign_key(
        'fk_boletim_linha_boletim',
        'boletim_linhas', 'boletins',
        ['boletim_id'], ['id'],
        ondelete='CASCADE'
    )

    op.create_foreign_key(
        'fk_boletim_linha_projeto',
        'boletim_linhas', 'projetos',
        ['projeto_id'], ['id'],
        ondelete='SET NULL'
    )


def downgrade():
    """Remove tabela boletim_linhas"""
    op.drop_table('boletim_linhas')
