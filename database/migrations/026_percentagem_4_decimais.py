"""
Migration 026: Alterar Percentagem de Comissões para 4 Casas Decimais

Altera:
- Campo percentagem em orcamento_reparticoes: NUMERIC(8,3) → NUMERIC(8,4)

Motivo:
- Suportar ajuste de comissões com precisão de 0.0001% (4 casas decimais)
- Fix bug: valores truncados para 3 casas após commit/reload

Data: 2025-11-18
"""

from sqlalchemy import text


def upgrade(engine):
    """Aplica as mudanças da migration"""

    with engine.connect() as conn:
        print("\n🔧 Migration 026: Alterar percentagem para 4 casas decimais")

        # ============================================================
        # IMPORTANTE: SQLite não suporta ALTER COLUMN diretamente
        # Precisamos recriar a tabela com a nova definição
        # ============================================================

        # 1. Criar tabela temporária com schema correto
        print("📋 Criando tabela temporária com nova precisão...")
        conn.execute(text("""
            CREATE TABLE orcamento_reparticoes_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                orcamento_id INTEGER NOT NULL,
                tipo VARCHAR(20) NOT NULL,
                descricao TEXT NOT NULL,
                ordem INTEGER NOT NULL DEFAULT 0,
                beneficiario VARCHAR(50),
                quantidade INTEGER,
                dias INTEGER,
                valor_unitario NUMERIC(10, 2),
                percentagem NUMERIC(8, 4),
                base_calculo NUMERIC(10, 2),
                kms NUMERIC(10, 2),
                valor_por_km NUMERIC(10, 2),
                num_refeicoes INTEGER,
                valor_por_refeicao NUMERIC(10, 2),
                valor_fixo NUMERIC(10, 2),
                item_cliente_id INTEGER,
                total NUMERIC(10, 2) NOT NULL,
                equipamento_id INTEGER,
                fornecedor_id INTEGER,

                FOREIGN KEY (orcamento_id) REFERENCES orcamentos(id) ON DELETE CASCADE,
                FOREIGN KEY (item_cliente_id) REFERENCES orcamento_itens(id) ON DELETE SET NULL,
                FOREIGN KEY (equipamento_id) REFERENCES equipamento(id) ON DELETE SET NULL,
                FOREIGN KEY (fornecedor_id) REFERENCES fornecedores(id) ON DELETE SET NULL
            )
        """))

        # 2. Copiar dados da tabela antiga para a nova
        print("📦 Copiando dados existentes...")
        conn.execute(text("""
            INSERT INTO orcamento_reparticoes_new
            SELECT
                id, orcamento_id, tipo, descricao, ordem, beneficiario,
                quantidade, dias, valor_unitario, percentagem, base_calculo,
                kms, valor_por_km, num_refeicoes, valor_por_refeicao, valor_fixo,
                item_cliente_id, total, equipamento_id, fornecedor_id
            FROM orcamento_reparticoes
        """))

        # 3. Remover tabela antiga
        print("🗑️  Removendo tabela antiga...")
        conn.execute(text("DROP TABLE orcamento_reparticoes"))

        # 4. Renomear tabela nova
        print("✏️  Renomeando tabela nova...")
        conn.execute(text("ALTER TABLE orcamento_reparticoes_new RENAME TO orcamento_reparticoes"))

        # 5. Recriar índices (se houver)
        print("🔗 Recriando índices...")
        try:
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_orcamento_reparticoes_orcamento ON orcamento_reparticoes(orcamento_id)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_orcamento_reparticoes_tipo ON orcamento_reparticoes(tipo)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_orcamento_reparticoes_beneficiario ON orcamento_reparticoes(beneficiario)"))
        except Exception as e:
            print(f"⚠️ Aviso ao criar índices: {e}")

        conn.commit()
        print("\n✅ Campo 'percentagem' alterado para NUMERIC(8,4) com sucesso!")
        print("🎉 Migration 026 aplicada com sucesso!")


def downgrade(engine):
    """Reverte as mudanças da migration"""

    with engine.connect() as conn:
        print("\n🔧 Downgrade Migration 026: Reverter percentagem para 3 casas decimais")

        # Recriar tabela com NUMERIC(8,3)
        conn.execute(text("""
            CREATE TABLE orcamento_reparticoes_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                orcamento_id INTEGER NOT NULL,
                tipo VARCHAR(20) NOT NULL,
                descricao TEXT NOT NULL,
                ordem INTEGER NOT NULL DEFAULT 0,
                beneficiario VARCHAR(50),
                quantidade INTEGER,
                dias INTEGER,
                valor_unitario NUMERIC(10, 2),
                percentagem NUMERIC(8, 3),
                base_calculo NUMERIC(10, 2),
                kms NUMERIC(10, 2),
                valor_por_km NUMERIC(10, 2),
                num_refeicoes INTEGER,
                valor_por_refeicao NUMERIC(10, 2),
                valor_fixo NUMERIC(10, 2),
                item_cliente_id INTEGER,
                total NUMERIC(10, 2) NOT NULL,
                equipamento_id INTEGER,
                fornecedor_id INTEGER,

                FOREIGN KEY (orcamento_id) REFERENCES orcamentos(id) ON DELETE CASCADE,
                FOREIGN KEY (item_cliente_id) REFERENCES orcamento_itens(id) ON DELETE SET NULL,
                FOREIGN KEY (equipamento_id) REFERENCES equipamento(id) ON DELETE SET NULL,
                FOREIGN KEY (fornecedor_id) REFERENCES fornecedores(id) ON DELETE SET NULL
            )
        """))

        # Copiar dados (percentagem será truncada para 3 casas)
        conn.execute(text("""
            INSERT INTO orcamento_reparticoes_new
            SELECT * FROM orcamento_reparticoes
        """))

        conn.execute(text("DROP TABLE orcamento_reparticoes"))
        conn.execute(text("ALTER TABLE orcamento_reparticoes_new RENAME TO orcamento_reparticoes"))

        # Recriar índices
        try:
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_orcamento_reparticoes_orcamento ON orcamento_reparticoes(orcamento_id)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_orcamento_reparticoes_tipo ON orcamento_reparticoes(tipo)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_orcamento_reparticoes_beneficiario ON orcamento_reparticoes(beneficiario)"))
        except Exception as e:
            print(f"⚠️ Aviso ao criar índices: {e}")

        conn.commit()
        print("✅ Migration 026 revertida (percentagem volta para NUMERIC(8,3))")


if __name__ == "__main__":
    print("⚠️ Execute este script via run_migration.py ou main.py")
