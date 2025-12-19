# -*- coding: utf-8 -*-
"""
Migration 023: Corrigir constraints nullable em orcamento_itens

As colunas quantidade, dias, preco_unitario, desconto devem ser nullable
porque não são usadas em todos os tipos de items (ex: transporte usa kms/valor_por_km)
"""
from sqlalchemy import create_engine, text


def upgrade(connection):
    """
    Altera tabela orcamento_itens para ter campos nullable corretos

    Em SQLite, não podemos alterar constraints diretamente.
    Precisamos recriar a tabela.
    """

    # 1. Criar tabela temporária com estrutura correta
    connection.execute(text("""
        CREATE TABLE orcamento_itens_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            orcamento_id INTEGER NOT NULL,
            secao_id INTEGER NOT NULL,
            tipo VARCHAR(20) NOT NULL,
            descricao TEXT NOT NULL,
            ordem INTEGER NOT NULL DEFAULT 0,

            -- Para serviços e equipamento (NULLABLE)
            quantidade INTEGER NULL,
            dias INTEGER NULL,
            preco_unitario NUMERIC(10, 2) NULL,
            desconto NUMERIC(5, 4) NULL DEFAULT 0,

            -- Para despesas tipo transporte (NULLABLE)
            kms NUMERIC(10, 2) NULL,
            valor_por_km NUMERIC(10, 2) NULL,

            -- Para despesas tipo refeição (NULLABLE)
            num_refeicoes INTEGER NULL,
            valor_por_refeicao NUMERIC(10, 2) NULL,

            -- Para despesas tipo outro (NULLABLE)
            valor_fixo NUMERIC(10, 2) NULL,

            -- Total calculado
            total NUMERIC(10, 2) NOT NULL,

            -- Relação com equipamento (opcional)
            equipamento_id INTEGER NULL,

            -- Foreign keys
            FOREIGN KEY (orcamento_id) REFERENCES orcamentos(id) ON DELETE CASCADE,
            FOREIGN KEY (secao_id) REFERENCES orcamento_secoes(id) ON DELETE CASCADE,
            FOREIGN KEY (equipamento_id) REFERENCES equipamento(id)
        )
    """))

    # 2. Copiar dados da tabela antiga para a nova
    connection.execute(text("""
        INSERT INTO orcamento_itens_new (
            id, orcamento_id, secao_id, tipo, descricao, ordem,
            quantidade, dias, preco_unitario, desconto,
            kms, valor_por_km, num_refeicoes, valor_por_refeicao, valor_fixo,
            total, equipamento_id
        )
        SELECT
            id, orcamento_id, secao_id, tipo, descricao, ordem,
            quantidade, dias, preco_unitario, desconto,
            kms, valor_por_km, num_refeicoes, valor_por_refeicao, valor_fixo,
            total, equipamento_id
        FROM orcamento_itens
    """))

    # 3. Dropar tabela antiga
    connection.execute(text("DROP TABLE orcamento_itens"))

    # 4. Renomear tabela nova
    connection.execute(text("ALTER TABLE orcamento_itens_new RENAME TO orcamento_itens"))

    # 5. Recriar índices se existirem
    connection.execute(text("""
        CREATE INDEX IF NOT EXISTS idx_orcamento_itens_orcamento
        ON orcamento_itens(orcamento_id)
    """))

    connection.execute(text("""
        CREATE INDEX IF NOT EXISTS idx_orcamento_itens_secao
        ON orcamento_itens(secao_id)
    """))

    connection.commit()


def downgrade(connection):
    """
    Reverter para estrutura anterior (NOT NULL)
    """
    # Criar tabela com constraints antigas
    connection.execute(text("""
        CREATE TABLE orcamento_itens_old (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            orcamento_id INTEGER NOT NULL,
            secao_id INTEGER NOT NULL,
            tipo VARCHAR(20) NOT NULL,
            descricao TEXT NOT NULL,
            ordem INTEGER NOT NULL DEFAULT 0,

            quantidade INTEGER NOT NULL,
            dias INTEGER NOT NULL,
            preco_unitario NUMERIC(10, 2) NOT NULL,
            desconto NUMERIC(5, 4) NOT NULL DEFAULT 0,

            kms NUMERIC(10, 2) NULL,
            valor_por_km NUMERIC(10, 2) NULL,
            num_refeicoes INTEGER NULL,
            valor_por_refeicao NUMERIC(10, 2) NULL,
            valor_fixo NUMERIC(10, 2) NULL,

            total NUMERIC(10, 2) NOT NULL,
            equipamento_id INTEGER NULL,

            FOREIGN KEY (orcamento_id) REFERENCES orcamentos(id) ON DELETE CASCADE,
            FOREIGN KEY (secao_id) REFERENCES orcamento_secoes(id) ON DELETE CASCADE,
            FOREIGN KEY (equipamento_id) REFERENCES equipamento(id)
        )
    """))

    # Copiar dados (com defaults para NULLs)
    connection.execute(text("""
        INSERT INTO orcamento_itens_old
        SELECT
            id, orcamento_id, secao_id, tipo, descricao, ordem,
            COALESCE(quantidade, 0), COALESCE(dias, 0),
            COALESCE(preco_unitario, 0), COALESCE(desconto, 0),
            kms, valor_por_km, num_refeicoes, valor_por_refeicao, valor_fixo,
            total, equipamento_id
        FROM orcamento_itens
    """))

    connection.execute(text("DROP TABLE orcamento_itens"))
    connection.execute(text("ALTER TABLE orcamento_itens_old RENAME TO orcamento_itens"))

    connection.commit()


if __name__ == "__main__":
    """Executar migration standalone"""
    import os
    import sys

    # Adicionar path do projeto
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

    # Criar engine
    engine = create_engine('sqlite:///agora_media.db')

    with engine.connect() as conn:
        print("🔧 Executando migration 023: fix nullable fields...")
        upgrade(conn)
        print("✅ Migration 023 aplicada com sucesso!")

        # Verificar estrutura
        result = conn.execute(text('PRAGMA table_info(orcamento_itens);'))
        print("\n📊 Estrutura da tabela orcamento_itens:")
        for row in result:
            if row[1] in ['quantidade', 'dias', 'preco_unitario', 'desconto']:
                notnull = "NOT NULL" if row[3] == 1 else "NULL"
                print(f"  {row[1]}: {row[2]} {notnull}")
