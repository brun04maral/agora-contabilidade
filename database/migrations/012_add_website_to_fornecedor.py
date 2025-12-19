# -*- coding: utf-8 -*-
"""
Migration: Adicionar campo website ao modelo Fornecedor
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers
revision = '012'
down_revision = '011'
branch_labels = None
depends_on = None


def upgrade():
    """Adicionar campo website"""
    op.add_column('fornecedores', sa.Column('website', sa.String(255), nullable=True))


def downgrade():
    """Remover campo website"""
    op.drop_column('fornecedores', 'website')
