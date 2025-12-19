# -*- coding: utf-8 -*-
"""
Migration 027: Adicionar campo owner ao Projeto
"""
from sqlalchemy import create_engine, text
import os


def run_migration():
    """Execute the migration"""

    # Get database path
    db_path = os.path.join(os.path.dirname(__file__), '..', '..', 'agora_media.db')
    engine = create_engine('sqlite:///' + db_path)

    with engine.connect() as conn:
        # Check if column already exists
        result = conn.execute(text("PRAGMA table_info(projetos)"))
        columns = [row[1] for row in result.fetchall()]

        if 'owner' in columns:
            print("Coluna 'owner' ja existe na tabela projetos")
            return True

        print("Adicionando coluna 'owner' a tabela projetos...")

        # Add column with default 'BA'
        conn.execute(text("ALTER TABLE projetos ADD COLUMN owner VARCHAR(2) DEFAULT 'BA'"))

        # Update existing records based on tipo
        conn.execute(text("UPDATE projetos SET owner = 'BA' WHERE tipo = 'PESSOAL_BRUNO'"))
        conn.execute(text("UPDATE projetos SET owner = 'RR' WHERE tipo = 'PESSOAL_RAFAEL'"))

        conn.commit()

        # Verify
        result = conn.execute(text("SELECT COUNT(*) FROM projetos WHERE owner IS NOT NULL"))
        count = result.scalar()
        print("Migracao 027 concluida! {} projetos atualizados com owner.".format(count))

        return True


if __name__ == '__main__':
    run_migration()
