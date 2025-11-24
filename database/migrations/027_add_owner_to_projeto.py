# -*- coding: utf-8 -*-
"""
Migration 027: Adicionar campo owner ao Projeto

Adiciona campo owner ('BA' ou 'RR') para identificar o sócio responsável.
Para projetos EMPRESA, indica quem angariou/gere o projeto.
Para projetos PESSOAIS, é derivado do tipo mas mantido para consistência.
"""
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os


def run_migration():
    """Execute the migration"""

    # Get database path
    db_path = os.path.join(os.path.dirname(__file__), '..', '..', 'agora_media.db')
    engine = create_engine(f'sqlite:///{db_path}')

    with engine.connect() as conn:
        # Check if column already exists
        result = conn.execute(text("PRAGMA table_info(projetos)"))
        columns = [row[1] for row in result.fetchall()]

        if 'owner' in columns:
            print("✅ Coluna 'owner' já existe na tabela projetos")
            return True

        print("🔄 Adicionando coluna 'owner' à tabela projetos...")

        # Add column with default 'BA'
        conn.execute(text("""
            ALTER TABLE projetos
            ADD COLUMN owner VARCHAR(2) DEFAULT 'BA'
        """))

        # Update existing records based on tipo
        # PESSOAL_BRUNO -> 'BA'
        conn.execute(text("""
            UPDATE projetos
            SET owner = 'BA'
            WHERE tipo = 'PESSOAL_BRUNO'
        """))

        # PESSOAL_RAFAEL -> 'RR'
        conn.execute(text("""
            UPDATE projetos
            SET owner = 'RR'
            WHERE tipo = 'PESSOAL_RAFAEL'
        """))

        # EMPRESA -> keep as 'BA' (default, can be changed by user)
        # Already set by default

        conn.commit()

        # Verify
        result = conn.execute(text("SELECT COUNT(*) FROM projetos WHERE owner IS NOT NULL"))
        count = result.scalar()
        print(f"✅ Migração 027 concluída! {count} projetos atualizados com owner.")

        # Show distribution
        result = conn.execute(text("""
            SELECT owner, tipo, COUNT(*) as count
            FROM projetos
            GROUP BY owner, tipo
        """))
        print("\nDistribuição:")
        for row in result.fetchall():
            print(f"  {row[0]} - {row[1]}: {row[2]} projetos")

        return True


if __name__ == '__main__':
    run_migration()
