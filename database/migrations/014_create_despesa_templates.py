# -*- coding: utf-8 -*-
"""
Migration 014 - Criar tabela despesa_templates

Cria tabela separada para templates de despesas recorrentes.
Templates não são despesas reais, apenas moldes para gerar despesas automáticas.
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers
revision = '014'
down_revision = '013'
branch_labels = None
depends_on = None


def upgrade():
    """
    Cria tabela despesa_templates para templates de despesas recorrentes
    """
    op.create_table(
        'despesa_templates',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('numero', sa.String(20), nullable=False, unique=True, index=True),
        sa.Column('tipo', sa.Enum('FIXA_MENSAL', 'PESSOAL_BRUNO', 'PESSOAL_RAFAEL', 'EQUIPAMENTO', 'PROJETO', name='tipodespesa'), nullable=False),
        sa.Column('credor_id', sa.Integer(), nullable=True),
        sa.Column('projeto_id', sa.Integer(), nullable=True),
        sa.Column('descricao', sa.Text(), nullable=False),
        sa.Column('valor_sem_iva', sa.Numeric(10, 2), nullable=False, default=0),
        sa.Column('valor_com_iva', sa.Numeric(10, 2), nullable=False, default=0),
        sa.Column('dia_mes', sa.Integer(), nullable=False),  # Dia do mês (1-31)
        sa.Column('nota', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # Foreign keys
    op.create_foreign_key(
        'fk_despesa_template_credor',
        'despesa_templates', 'fornecedores',
        ['credor_id'], ['id'],
        ondelete='SET NULL'
    )

    op.create_foreign_key(
        'fk_despesa_template_projeto',
        'despesa_templates', 'projetos',
        ['credor_id'], ['id'],
        ondelete='SET NULL'
    )


def downgrade():
    """Remove tabela despesa_templates"""
    op.drop_table('despesa_templates')
