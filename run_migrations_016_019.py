# -*- coding: utf-8 -*-
"""
Script para aplicar migrations 016-019: Sistema de Boletim Itinerário

Migrations:
- 016: Criar tabela valores_referencia_anual
- 017: Criar tabela boletim_linhas
- 018: Criar tabela boletim_templates
- 019: Expandir tabela boletins

IMPORTANTE: Faz backup da base de dados antes de executar!
"""
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

def run_migrations():
    """Executar migrations 016-019"""
    load_dotenv()

    database_url = os.getenv("DATABASE_URL", "sqlite:///./agora_media.db")
    engine = create_engine(database_url)

    print("=" * 70)
    print("MIGRATIONS 016-019: Sistema de Boletim Itinerário")
    print("=" * 70)
    print()
    print("⚠️  IMPORTANTE: Certifica-te que fizeste backup da BD!")
    print()

    with engine.connect() as conn:
        try:
            # MIGRATION 016: valores_referencia_anual
            print("[016] Criando tabela valores_referencia_anual...")
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS valores_referencia_anual (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ano INTEGER UNIQUE NOT NULL,
                    val_dia_nacional NUMERIC(10, 2) NOT NULL,
                    val_dia_estrangeiro NUMERIC(10, 2) NOT NULL,
                    val_km NUMERIC(10, 2) NOT NULL,
                    created_at DATETIME NOT NULL,
                    updated_at DATETIME NOT NULL
                )
            """))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_valores_ref_ano ON valores_referencia_anual(ano)"))

            # Inserir valores default 2025
            conn.execute(text("""
                INSERT OR IGNORE INTO valores_referencia_anual
                (ano, val_dia_nacional, val_dia_estrangeiro, val_km, created_at, updated_at)
                VALUES (2025, 72.65, 167.07, 0.40, datetime('now'), datetime('now'))
            """))
            print("✅ Tabela valores_referencia_anual criada (com valores 2025)")
            print()

            # MIGRATION 017: boletim_linhas
            print("[017] Criando tabela boletim_linhas...")
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS boletim_linhas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    boletim_id INTEGER NOT NULL,
                    ordem INTEGER NOT NULL,
                    projeto_id INTEGER,
                    servico TEXT NOT NULL,
                    localidade VARCHAR(100),
                    data_inicio DATE,
                    hora_inicio TIME,
                    data_fim DATE,
                    hora_fim TIME,
                    tipo VARCHAR(20) NOT NULL DEFAULT 'NACIONAL',
                    dias NUMERIC(10, 2) NOT NULL DEFAULT 0,
                    kms INTEGER NOT NULL DEFAULT 0,
                    created_at DATETIME NOT NULL,
                    updated_at DATETIME NOT NULL,
                    FOREIGN KEY (boletim_id) REFERENCES boletins(id) ON DELETE CASCADE,
                    FOREIGN KEY (projeto_id) REFERENCES projetos(id) ON DELETE SET NULL
                )
            """))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_boletim_linhas_boletim ON boletim_linhas(boletim_id)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_boletim_linhas_projeto ON boletim_linhas(projeto_id)"))
            print("✅ Tabela boletim_linhas criada")
            print()

            # MIGRATION 018: boletim_templates
            print("[018] Criando tabela boletim_templates...")
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS boletim_templates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    numero VARCHAR(20) UNIQUE NOT NULL,
                    nome VARCHAR(200) NOT NULL,
                    socio VARCHAR(20) NOT NULL,
                    dia_mes INTEGER NOT NULL,
                    ativo BOOLEAN NOT NULL DEFAULT 1,
                    created_at DATETIME NOT NULL,
                    updated_at DATETIME NOT NULL
                )
            """))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_boletim_templates_numero ON boletim_templates(numero)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_boletim_templates_socio ON boletim_templates(socio)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_boletim_templates_ativo ON boletim_templates(ativo)"))
            print("✅ Tabela boletim_templates criada")
            print()

            # MIGRATION 019: Expand boletins
            print("[019] Expandindo tabela boletins...")

            # Verificar se colunas já existem
            result = conn.execute(text("PRAGMA table_info(boletins)"))
            existing_columns = [row[1] for row in result]

            columns_to_add = [
                ("mes", "INTEGER"),
                ("ano", "INTEGER"),
                ("val_dia_nacional", "NUMERIC(10, 2)"),
                ("val_dia_estrangeiro", "NUMERIC(10, 2)"),
                ("val_km", "NUMERIC(10, 2)"),
                ("total_ajudas_nacionais", "NUMERIC(10, 2) NOT NULL DEFAULT 0"),
                ("total_ajudas_estrangeiro", "NUMERIC(10, 2) NOT NULL DEFAULT 0"),
                ("total_kms", "NUMERIC(10, 2) NOT NULL DEFAULT 0"),
                ("valor_total", "NUMERIC(10, 2) NOT NULL DEFAULT 0")
            ]

            for col_name, col_type in columns_to_add:
                if col_name not in existing_columns:
                    conn.execute(text(f"ALTER TABLE boletins ADD COLUMN {col_name} {col_type}"))
                    print(f"   + Adicionada coluna '{col_name}'")

            # Copiar valor para valor_total (compatibilidade)
            conn.execute(text("UPDATE boletins SET valor_total = COALESCE(valor, 0) WHERE valor_total = 0"))

            # Criar índices
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_boletins_mes ON boletins(mes)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_boletins_ano ON boletins(ano)"))

            print("✅ Tabela boletins expandida")
            print()

            conn.commit()

            print("=" * 70)
            print("✅ TODAS AS MIGRATIONS APLICADAS COM SUCESSO!")
            print("=" * 70)
            print()
            print("Próximos passos:")
            print("1. Implementar Business Logic (Managers)")
            print("2. Implementar UI (Screens)")
            print("3. Testar criação de boletins com novas funcionalidades")

        except Exception as e:
            error_msg = str(e).lower()
            if "already exists" in error_msg or "duplicate" in error_msg:
                print("⚠️  Algumas tabelas já existem - migrations parcialmente aplicadas")
            else:
                print(f"❌ Erro ao aplicar migrations: {e}")
                raise


if __name__ == "__main__":
    run_migrations()
