# -*- coding: utf-8 -*-
"""
Script para executar migration 014 - Criar tabela despesa_templates
"""
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

def run_migration():
    """Executar migration 014"""
    load_dotenv()

    # Get database URL from environment or use default
    database_url = os.getenv("DATABASE_URL", "sqlite:///./agora_media.db")
    engine = create_engine(database_url)

    with engine.connect() as conn:
        try:
            # Create despesa_templates table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS despesa_templates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    numero VARCHAR(20) UNIQUE NOT NULL,
                    tipo VARCHAR(50) NOT NULL,
                    credor_id INTEGER,
                    projeto_id INTEGER,
                    descricao TEXT NOT NULL,
                    valor_sem_iva NUMERIC(10, 2) NOT NULL DEFAULT 0,
                    valor_com_iva NUMERIC(10, 2) NOT NULL DEFAULT 0,
                    dia_mes INTEGER NOT NULL,
                    nota TEXT,
                    created_at DATETIME NOT NULL,
                    updated_at DATETIME NOT NULL,
                    FOREIGN KEY (credor_id) REFERENCES fornecedores(id) ON DELETE SET NULL,
                    FOREIGN KEY (projeto_id) REFERENCES projetos(id) ON DELETE SET NULL
                )
            """))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_despesa_templates_numero ON despesa_templates(numero)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_despesa_templates_tipo ON despesa_templates(tipo)"))

            conn.commit()
            print("✅ Migration 014 aplicada com sucesso!")
            print("   - Criada tabela 'despesa_templates' para templates de despesas recorrentes")
            print("   - Templates não entram em cálculos financeiros")
            print("   - Formato: #TD000001, #TD000002, ...")

        except Exception as e:
            error_msg = str(e).lower()
            if "already exists" in error_msg or "duplicate" in error_msg:
                print("⚠️  Tabela 'despesa_templates' já existe - migration já foi aplicada")
            else:
                print(f"❌ Erro ao aplicar migration: {e}")
                raise

if __name__ == "__main__":
    run_migration()
