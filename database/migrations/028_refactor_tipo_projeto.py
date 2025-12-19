# -*- coding: utf-8 -*-
"""
Migration 028: Refatorar TipoProjeto para EMPRESA|PESSOAL

Converte:
- PESSOAL_BRUNO -> PESSOAL (owner ja definido como 'BA')
- PESSOAL_RAFAEL -> PESSOAL (owner ja definido como 'RR')
- EMPRESA -> EMPRESA (mantido)
"""
from sqlalchemy import create_engine, text
import os


def run_migration():
    """Execute the migration"""

    db_path = os.path.join(os.path.dirname(__file__), '..', '..', 'agora_media.db')
    engine = create_engine('sqlite:///' + db_path)

    with engine.connect() as conn:
        # Check current tipos
        result = conn.execute(text("SELECT DISTINCT tipo FROM projetos"))
        tipos = [row[0] for row in result.fetchall()]
        print("Tipos atuais: {}".format(tipos))

        # Convert PESSOAL_BRUNO and PESSOAL_RAFAEL to PESSOAL
        if 'PESSOAL_BRUNO' in tipos or 'PESSOAL_RAFAEL' in tipos:
            print("Convertendo PESSOAL_BRUNO e PESSOAL_RAFAEL para PESSOAL...")

            conn.execute(text("UPDATE projetos SET tipo = 'PESSOAL' WHERE tipo = 'PESSOAL_BRUNO'"))
            conn.execute(text("UPDATE projetos SET tipo = 'PESSOAL' WHERE tipo = 'PESSOAL_RAFAEL'"))

            conn.commit()

            # Verify
            result = conn.execute(text("""
                SELECT tipo, owner, COUNT(*) as count
                FROM projetos
                GROUP BY tipo, owner
            """))
            print("\nDistribuicao final:")
            for row in result.fetchall():
                print("  {} ({}): {} projetos".format(row[0], row[1], row[2]))

            print("\nMigracao 028 concluida!")
        else:
            print("Tipos ja estao no formato correto (EMPRESA|PESSOAL)")

        return True


if __name__ == '__main__':
    run_migration()
