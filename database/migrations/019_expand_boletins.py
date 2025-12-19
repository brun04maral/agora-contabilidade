# -*- coding: utf-8 -*-
"""
Migration 019 - Expandir tabela boletins

Adiciona campos para sistema de Boletim Itinerário:
- Mês e ano
- Valores de referência
- Totais calculados automaticamente
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers
revision = '019'
down_revision = '018'
branch_labels = None
depends_on = None


def upgrade():
    """
    Adiciona novos campos à tabela boletins
    """
    # Período
    op.add_column('boletins', sa.Column('mes', sa.Integer(), nullable=True, index=True))
    op.add_column('boletins', sa.Column('ano', sa.Integer(), nullable=True, index=True))

    # Valores de Referência
    op.add_column('boletins', sa.Column('val_dia_nacional', sa.Numeric(10, 2), nullable=True))
    op.add_column('boletins', sa.Column('val_dia_estrangeiro', sa.Numeric(10, 2), nullable=True))
    op.add_column('boletins', sa.Column('val_km', sa.Numeric(10, 2), nullable=True))

    # Totais Calculados
    op.add_column('boletins', sa.Column('total_ajudas_nacionais', sa.Numeric(10, 2), nullable=False, server_default='0'))
    op.add_column('boletins', sa.Column('total_ajudas_estrangeiro', sa.Numeric(10, 2), nullable=False, server_default='0'))
    op.add_column('boletins', sa.Column('total_kms', sa.Numeric(10, 2), nullable=False, server_default='0'))
    op.add_column('boletins', sa.Column('valor_total', sa.Numeric(10, 2), nullable=False, server_default='0'))

    # Copiar valor existente para valor_total (compatibilidade)
    op.execute("UPDATE boletins SET valor_total = valor WHERE valor IS NOT NULL")


def downgrade():
    """Remove campos adicionados"""
    op.drop_column('boletins', 'mes')
    op.drop_column('boletins', 'ano')
    op.drop_column('boletins', 'val_dia_nacional')
    op.drop_column('boletins', 'val_dia_estrangeiro')
    op.drop_column('boletins', 'val_km')
    op.drop_column('boletins', 'total_ajudas_nacionais')
    op.drop_column('boletins', 'total_ajudas_estrangeiro')
    op.drop_column('boletins', 'total_kms')
    op.drop_column('boletins', 'valor_total')
