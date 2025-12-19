"""
Migration 025: Tabelas Freelancers e Fornecedores Expandidas

Cria:
1. Tabela freelancers - Profissionais externos
2. Tabela freelancer_trabalhos - Histórico de trabalhos
3. Tabela fornecedor_compras - Histórico de compras

Expande:
- Tabela fornecedores (adiciona numero, categoria, iban)

Data: 2025-11-17
"""

from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, Boolean, Date, Index, text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


def upgrade(engine):
    """Aplica as mudanças da migration"""

    with engine.connect() as conn:
        # ============================================================
        # 1. CRIAR TABELA FREELANCERS
        # ============================================================
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS freelancers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                numero VARCHAR(20) NOT NULL UNIQUE,
                nome VARCHAR(120) NOT NULL,
                nif VARCHAR(20),
                email VARCHAR(120),
                telefone VARCHAR(20),
                iban VARCHAR(50),
                morada TEXT,
                especialidade VARCHAR(100),
                notas TEXT,
                ativo BOOLEAN NOT NULL DEFAULT 1,
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """))

        # Índices para freelancers
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_freelancers_ativo ON freelancers(ativo)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_freelancers_nome ON freelancers(nome)"))

        print("✅ Tabela 'freelancers' criada com sucesso")

        # ============================================================
        # 2. CRIAR TABELA FREELANCER_TRABALHOS
        # ============================================================
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS freelancer_trabalhos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                freelancer_id INTEGER NOT NULL,
                orcamento_id INTEGER,
                projeto_id INTEGER,
                descricao TEXT NOT NULL,
                valor NUMERIC(10, 2) NOT NULL,
                data DATE NOT NULL,
                status VARCHAR(20) NOT NULL DEFAULT 'a_pagar',
                data_pagamento DATE,
                nota TEXT,
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (freelancer_id) REFERENCES freelancers(id) ON DELETE CASCADE,
                FOREIGN KEY (orcamento_id) REFERENCES orcamentos(id) ON DELETE SET NULL,
                FOREIGN KEY (projeto_id) REFERENCES projetos(id) ON DELETE SET NULL,

                CHECK (status IN ('a_pagar', 'pago', 'cancelado'))
            )
        """))

        # Índices para freelancer_trabalhos
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_freelancer_trabalhos_freelancer ON freelancer_trabalhos(freelancer_id)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_freelancer_trabalhos_status ON freelancer_trabalhos(status)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_freelancer_trabalhos_data ON freelancer_trabalhos(data)"))

        print("✅ Tabela 'freelancer_trabalhos' criada com sucesso")

        # ============================================================
        # 3. CRIAR TABELA FORNECEDOR_COMPRAS
        # ============================================================
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS fornecedor_compras (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fornecedor_id INTEGER NOT NULL,
                orcamento_id INTEGER,
                projeto_id INTEGER,
                descricao TEXT NOT NULL,
                valor NUMERIC(10, 2) NOT NULL,
                data DATE NOT NULL,
                status VARCHAR(20) NOT NULL DEFAULT 'a_pagar',
                data_pagamento DATE,
                nota TEXT,
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (fornecedor_id) REFERENCES fornecedores(id) ON DELETE CASCADE,
                FOREIGN KEY (orcamento_id) REFERENCES orcamentos(id) ON DELETE SET NULL,
                FOREIGN KEY (projeto_id) REFERENCES projetos(id) ON DELETE SET NULL,

                CHECK (status IN ('a_pagar', 'pago', 'cancelado'))
            )
        """))

        # Índices para fornecedor_compras
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_fornecedor_compras_fornecedor ON fornecedor_compras(fornecedor_id)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_fornecedor_compras_status ON fornecedor_compras(status)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_fornecedor_compras_data ON fornecedor_compras(data)"))

        print("✅ Tabela 'fornecedor_compras' criada com sucesso")

        # ============================================================
        # 4. EXPANDIR TABELA FORNECEDORES
        # ============================================================

        # Verificar se colunas já existem
        result = conn.execute(text("PRAGMA table_info(fornecedores)"))
        columns = [row[1] for row in result.fetchall()]

        if 'numero' not in columns:
            conn.execute(text("ALTER TABLE fornecedores ADD COLUMN numero VARCHAR(20)"))
            print("✅ Coluna 'numero' adicionada à tabela 'fornecedores'")

        if 'categoria' not in columns:
            conn.execute(text("ALTER TABLE fornecedores ADD COLUMN categoria VARCHAR(50)"))
            print("✅ Coluna 'categoria' adicionada à tabela 'fornecedores'")

        if 'iban' not in columns:
            conn.execute(text("ALTER TABLE fornecedores ADD COLUMN iban VARCHAR(50)"))
            print("✅ Coluna 'iban' adicionada à tabela 'fornecedores'")

        # Criar índice para categoria (se ainda não existe)
        try:
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_fornecedores_categoria ON fornecedores(categoria)"))
            print("✅ Índice 'idx_fornecedores_categoria' criado")
        except:
            pass

        # ============================================================
        # 5. GERAR NÚMEROS PARA FORNECEDORES EXISTENTES
        # ============================================================

        # Obter fornecedores sem número
        result = conn.execute(text("SELECT id FROM fornecedores WHERE numero IS NULL ORDER BY id"))
        fornecedores_sem_numero = result.fetchall()

        for idx, (fornecedor_id,) in enumerate(fornecedores_sem_numero, start=1):
            numero = f"#FO{idx:05d}"
            conn.execute(
                text("UPDATE fornecedores SET numero = :numero WHERE id = :id"),
                {"numero": numero, "id": fornecedor_id}
            )

        if fornecedores_sem_numero:
            print(f"✅ Números gerados para {len(fornecedores_sem_numero)} fornecedores existentes")

        conn.commit()
        print("\n🎉 Migration 025 aplicada com sucesso!")


def downgrade(engine):
    """Reverte as mudanças da migration"""

    with engine.connect() as conn:
        # Remover tabelas criadas
        conn.execute(text("DROP TABLE IF EXISTS fornecedor_compras"))
        conn.execute(text("DROP TABLE IF EXISTS freelancer_trabalhos"))
        conn.execute(text("DROP TABLE IF EXISTS freelancers"))

        # Remover colunas de fornecedores (SQLite não suporta DROP COLUMN diretamente)
        # Seria necessário recriar a tabela, mas como é um downgrade, apenas avisar
        print("⚠️ Downgrade parcial: tabelas removidas, mas colunas em fornecedores mantidas")
        print("   (SQLite não suporta DROP COLUMN - requer recriação da tabela)")

        conn.commit()
        print("✅ Migration 025 revertida (parcialmente)")


if __name__ == "__main__":
    print("⚠️ Execute este script via run_migration_025.py")
