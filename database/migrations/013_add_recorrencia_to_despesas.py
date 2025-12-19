# -*- coding: utf-8 -*-
"""
Migration 013 - Adicionar campos de recorrência a despesas

Adiciona suporte para despesas recorrentes automáticas (ex: salários mensais)
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers
revision = '013'
down_revision = '012'
branch_labels = None
depends_on = None


def upgrade():
    """
    Adiciona campos para despesas recorrentes:
    - is_recorrente: Boolean indicando se é template de despesa recorrente
    - dia_recorrencia: Dia do mês (1-31) para gerar automaticamente
    - despesa_template_id: FK para o template que gerou esta despesa
    """
    # Add is_recorrente column (default False)
    op.add_column('despesas', sa.Column('is_recorrente', sa.Boolean(), nullable=False, server_default='0'))

    # Add dia_recorrencia column (1-31, NULL if not recorrente)
    op.add_column('despesas', sa.Column('dia_recorrencia', sa.Integer(), nullable=True))

    # Add despesa_template_id (FK to despesas.id for tracking which template generated this)
    op.add_column('despesas', sa.Column('despesa_template_id', sa.Integer(), nullable=True))
    op.create_foreign_key(
        'fk_despesa_template',
        'despesas', 'despesas',
        ['despesa_template_id'], ['id'],
        ondelete='SET NULL'
    )


def downgrade():
    """Remove campos de recorrência"""
    op.drop_constraint('fk_despesa_template', 'despesas', type_='foreignkey')
    op.drop_column('despesas', 'despesa_template_id')
    op.drop_column('despesas', 'dia_recorrencia')
    op.drop_column('despesas', 'is_recorrente')
