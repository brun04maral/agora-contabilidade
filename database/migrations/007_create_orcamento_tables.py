"""
Migration 007: Create Orcamento tables
Cria as tabelas para o sistema de Orçamentos (Budgets)
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


def upgrade():
    """Cria as tabelas de orçamentos"""

    # Tabela principal de Orçamentos
    op.create_table(
        'orcamentos',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('codigo', sa.String(length=100), nullable=False),
        sa.Column('versao', sa.String(length=10), nullable=True),
        sa.Column('tipo', sa.String(length=20), nullable=False, server_default='frontend'),
        sa.Column('cliente_id', sa.Integer(), nullable=True),
        sa.Column('data_criacao', sa.Date(), nullable=False),
        sa.Column('data_evento', sa.String(length=200), nullable=True),
        sa.Column('local_evento', sa.String(length=200), nullable=True),
        sa.Column('descricao_proposta', sa.Text(), nullable=True),
        sa.Column('valor_total', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('total_parcial_1', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('total_parcial_2', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('notas_contratuais', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='rascunho'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['cliente_id'], ['clientes.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('codigo')
    )
    op.create_index(op.f('ix_orcamentos_codigo'), 'orcamentos', ['codigo'], unique=True)
    op.create_index(op.f('ix_orcamentos_cliente_id'), 'orcamentos', ['cliente_id'], unique=False)
    op.create_index(op.f('ix_orcamentos_status'), 'orcamentos', ['status'], unique=False)

    # Tabela de Secções do Orçamento
    op.create_table(
        'orcamento_secoes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('orcamento_id', sa.Integer(), nullable=False),
        sa.Column('tipo', sa.String(length=50), nullable=False),
        sa.Column('nome', sa.String(length=100), nullable=False),
        sa.Column('ordem', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('parent_id', sa.Integer(), nullable=True),
        sa.Column('subtotal', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.ForeignKeyConstraint(['orcamento_id'], ['orcamentos.id'], ),
        sa.ForeignKeyConstraint(['parent_id'], ['orcamento_secoes.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_orcamento_secoes_orcamento_id'), 'orcamento_secoes', ['orcamento_id'], unique=False)
    op.create_index(op.f('ix_orcamento_secoes_tipo'), 'orcamento_secoes', ['tipo'], unique=False)

    # Tabela de Items/Linhas do Orçamento
    op.create_table(
        'orcamento_itens',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('orcamento_id', sa.Integer(), nullable=False),
        sa.Column('secao_id', sa.Integer(), nullable=False),
        sa.Column('descricao', sa.Text(), nullable=False),
        sa.Column('quantidade', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('dias', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('preco_unitario', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('desconto', sa.Numeric(precision=5, scale=4), nullable=False, server_default='0'),
        sa.Column('total', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('ordem', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('equipamento_id', sa.Integer(), nullable=True),
        sa.Column('reparticao', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('afetacao', sa.String(length=50), nullable=True),
        sa.Column('investimento', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('amortizacao', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.ForeignKeyConstraint(['orcamento_id'], ['orcamentos.id'], ),
        sa.ForeignKeyConstraint(['secao_id'], ['orcamento_secoes.id'], ),
        sa.ForeignKeyConstraint(['equipamento_id'], ['equipamentos.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_orcamento_itens_orcamento_id'), 'orcamento_itens', ['orcamento_id'], unique=False)
    op.create_index(op.f('ix_orcamento_itens_secao_id'), 'orcamento_itens', ['secao_id'], unique=False)

    # Tabela de Repartição do Orçamento
    op.create_table(
        'orcamento_reparticoes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('orcamento_id', sa.Integer(), nullable=False),
        sa.Column('entidade', sa.String(length=50), nullable=False),
        sa.Column('valor', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('percentagem', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('ordem', sa.Integer(), nullable=False, server_default='0'),
        sa.ForeignKeyConstraint(['orcamento_id'], ['orcamentos.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_orcamento_reparticoes_orcamento_id'), 'orcamento_reparticoes', ['orcamento_id'], unique=False)


def downgrade():
    """Remove as tabelas de orçamentos"""
    op.drop_index(op.f('ix_orcamento_reparticoes_orcamento_id'), table_name='orcamento_reparticoes')
    op.drop_table('orcamento_reparticoes')

    op.drop_index(op.f('ix_orcamento_itens_secao_id'), table_name='orcamento_itens')
    op.drop_index(op.f('ix_orcamento_itens_orcamento_id'), table_name='orcamento_itens')
    op.drop_table('orcamento_itens')

    op.drop_index(op.f('ix_orcamento_secoes_tipo'), table_name='orcamento_secoes')
    op.drop_index(op.f('ix_orcamento_secoes_orcamento_id'), table_name='orcamento_secoes')
    op.drop_table('orcamento_secoes')

    op.drop_index(op.f('ix_orcamentos_status'), table_name='orcamentos')
    op.drop_index(op.f('ix_orcamentos_cliente_id'), table_name='orcamentos')
    op.drop_index(op.f('ix_orcamentos_codigo'), table_name='orcamentos')
    op.drop_table('orcamentos')
