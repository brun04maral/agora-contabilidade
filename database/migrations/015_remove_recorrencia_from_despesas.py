# -*- coding: utf-8 -*-
"""
Migration 015 - Remover campos de recorrência da tabela despesas

Remove is_recorrente e dia_recorrencia da tabela despesas.
Mantém apenas despesa_template_id para rastrear origem.

Agora templates ficam em tabela separada (despesa_templates).
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers
revision = '015'
down_revision = '014'
branch_labels = None
depends_on = None


def upgrade():
    """
    Remove campos is_recorrente e dia_recorrencia da tabela despesas
    Mantém despesa_template_id
    """
    # Remove colunas não mais necessárias
    op.drop_column('despesas', 'is_recorrente')
    op.drop_column('despesas', 'dia_recorrencia')


def downgrade():
    """Restaura campos removidos"""
    op.add_column('despesas', sa.Column('is_recorrente', sa.Boolean(), nullable=False, server_default='0'))
    op.add_column('despesas', sa.Column('dia_recorrencia', sa.Integer(), nullable=True))
