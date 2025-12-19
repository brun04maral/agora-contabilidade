#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de migração para uniformizar nomes dos sócios: BRUNO→BA, RAFAEL→RR

Atualiza:
- Boletins: campo 'socio' (BRUNO→BA, RAFAEL→RR)
- Despesas: campo 'tipo' (PESSOAL_BRUNO→PESSOAL_BA, PESSOAL_RAFAEL→PESSOAL_RR)
"""
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

load_dotenv()


def migrate_socio_names():
    """Migra nomes dos sócios na base de dados"""
    # Get database URL from environment
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise ValueError("DATABASE_URL not found in environment variables")

    # Create engine and session
    engine = create_engine(database_url)
    Session = sessionmaker(bind=engine)
    db = Session()

    try:
        print("=" * 80)
        print("MIGRAÇÃO: Uniformizar nomes dos sócios (BRUNO→BA, RAFAEL→RR)")
        print("=" * 80)

        # 1. Atualizar tabela boletins
        print("\n1. Atualizando tabela 'boletins'...")

        # Contar registos a migrar
        result = db.execute(text("SELECT COUNT(*) FROM boletins WHERE socio IN ('BRUNO', 'RAFAEL')"))
        count = result.scalar()
        print(f"   - Encontrados {count} boletins a atualizar")

        if count > 0:
            # Atualizar BRUNO → BA
            result = db.execute(text("UPDATE boletins SET socio = 'BA' WHERE socio = 'BRUNO'"))
            bruno_count = result.rowcount
            print(f"   - Atualizados {bruno_count} boletins: BRUNO → BA")

            # Atualizar RAFAEL → RR
            result = db.execute(text("UPDATE boletins SET socio = 'RR' WHERE socio = 'RAFAEL'"))
            rafael_count = result.rowcount
            print(f"   - Atualizados {rafael_count} boletins: RAFAEL → RR")
        else:
            print("   - Nenhum boletim a atualizar (já migrados ou não existem)")

        # 2. Atualizar tabela despesas
        print("\n2. Atualizando tabela 'despesas'...")

        # Contar registos a migrar
        result = db.execute(text("SELECT COUNT(*) FROM despesas WHERE tipo IN ('PESSOAL_BRUNO', 'PESSOAL_RAFAEL')"))
        count = result.scalar()
        print(f"   - Encontradas {count} despesas a atualizar")

        if count > 0:
            # Atualizar PESSOAL_BRUNO → PESSOAL_BA
            result = db.execute(text("UPDATE despesas SET tipo = 'PESSOAL_BA' WHERE tipo = 'PESSOAL_BRUNO'"))
            bruno_count = result.rowcount
            print(f"   - Atualizadas {bruno_count} despesas: PESSOAL_BRUNO → PESSOAL_BA")

            # Atualizar PESSOAL_RAFAEL → PESSOAL_RR
            result = db.execute(text("UPDATE despesas SET tipo = 'PESSOAL_RR' WHERE tipo = 'PESSOAL_RAFAEL'"))
            rafael_count = result.rowcount
            print(f"   - Atualizadas {rafael_count} despesas: PESSOAL_RAFAEL → PESSOAL_RR")
        else:
            print("   - Nenhuma despesa a atualizar (já migradas ou não existem)")

        # Commit das alterações
        db.commit()

        print("\n" + "=" * 80)
        print("✅ MIGRAÇÃO COMPLETA!")
        print("=" * 80)

        # Verificação final
        print("\n3. Verificação final...")
        result = db.execute(text("SELECT COUNT(*) FROM boletins WHERE socio IN ('BRUNO', 'RAFAEL')"))
        remaining_boletins = result.scalar()

        result = db.execute(text("SELECT COUNT(*) FROM despesas WHERE tipo IN ('PESSOAL_BRUNO', 'PESSOAL_RAFAEL')"))
        remaining_despesas = result.scalar()

        if remaining_boletins == 0 and remaining_despesas == 0:
            print("   ✅ Todos os registos foram migrados com sucesso!")
        else:
            print(f"   ⚠️  Ainda existem registos por migrar:")
            print(f"      - Boletins: {remaining_boletins}")
            print(f"      - Despesas: {remaining_despesas}")

    except Exception as e:
        print(f"\n❌ ERRO durante migração: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    migrate_socio_names()
