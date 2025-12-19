# -*- coding: utf-8 -*-
"""
Script para executar migration 015 - Remover campos de recorrência da tabela despesas
"""
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

def run_migration():
    """Executar migration 015"""
    load_dotenv()

    # Get database URL from environment or use default
    database_url = os.getenv("DATABASE_URL", "sqlite:///./agora_media.db")
    engine = create_engine(database_url)

    with engine.connect() as conn:
        try:
            # SQLite doesn't support DROP COLUMN directly
            # Need to recreate table without those columns

            # 1. Create temporary table with new schema (without is_recorrente and dia_recorrencia)
            conn.execute(text("""
                CREATE TABLE despesas_new (
                    id INTEGER PRIMARY KEY,
                    numero VARCHAR(20) UNIQUE NOT NULL,
                    tipo VARCHAR(50) NOT NULL,
                    data DATE NOT NULL,
                    credor_id INTEGER,
                    projeto_id INTEGER,
                    descricao TEXT NOT NULL,
                    valor_sem_iva NUMERIC(10, 2) NOT NULL DEFAULT 0,
                    valor_com_iva NUMERIC(10, 2) NOT NULL DEFAULT 0,
                    estado VARCHAR(50) NOT NULL,
                    data_pagamento DATE,
                    nota TEXT,
                    despesa_template_id INTEGER,
                    created_at DATETIME NOT NULL,
                    updated_at DATETIME NOT NULL,
                    FOREIGN KEY (credor_id) REFERENCES fornecedores(id) ON DELETE SET NULL,
                    FOREIGN KEY (projeto_id) REFERENCES projetos(id) ON DELETE SET NULL,
                    FOREIGN KEY (despesa_template_id) REFERENCES despesa_templates(id) ON DELETE SET NULL
                )
            """))

            # 2. Copy data from old table (excluding is_recorrente and dia_recorrencia)
            conn.execute(text("""
                INSERT INTO despesas_new (
                    id, numero, tipo, data, credor_id, projeto_id, descricao,
                    valor_sem_iva, valor_com_iva, estado, data_pagamento, nota,
                    despesa_template_id, created_at, updated_at
                )
                SELECT
                    id, numero, tipo, data, credor_id, projeto_id, descricao,
                    valor_sem_iva, valor_com_iva, estado, data_pagamento, nota,
                    despesa_template_id, created_at, updated_at
                FROM despesas
            """))

            # 3. Drop old table
            conn.execute(text("DROP TABLE despesas"))

            # 4. Rename new table
            conn.execute(text("ALTER TABLE despesas_new RENAME TO despesas"))

            # 5. Recreate indexes
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_despesas_numero ON despesas(numero)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_despesas_tipo ON despesas(tipo)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_despesas_data ON despesas(data)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_despesas_estado ON despesas(estado)"))

            conn.commit()
            print("✅ Migration 015 aplicada com sucesso!")
            print("   - Removidos campos 'is_recorrente' e 'dia_recorrencia' da tabela despesas")
            print("   - Mantido campo 'despesa_template_id' para rastrear origem")
            print("   - Templates agora ficam em tabela separada (despesa_templates)")

        except Exception as e:
            error_msg = str(e).lower()
            if "no such column" in error_msg and ("is_recorrente" in error_msg or "dia_recorrencia" in error_msg):
                print("⚠️  Campos já foram removidos - migration já foi aplicada")
            else:
                print(f"❌ Erro ao aplicar migration: {e}")
                raise

if __name__ == "__main__":
    run_migration()
