#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de migração para uniformizar nomes dos sócios: BRUNO→BA, RAFAEL→RR

Atualiza:
- Boletins: campo 'socio' (BRUNO→BA, RAFAEL→RR)
- Despesas: campo 'tipo' (PESSOAL_BRUNO→PESSOAL_BA, PESSOAL_RAFAEL→PESSOAL_RR)
"""
import sqlite3
import os

def migrate_socio_names():
    """Migra nomes dos sócios na base de dados"""
    # Path to database - try agora_media.db first, then agora.db
    project_root = os.path.join(os.path.dirname(__file__), '..')

    db_candidates = [
        os.path.join(project_root, 'agora_media.db'),
        os.path.join(project_root, 'agora.db'),
        os.path.join(project_root, 'data', 'agora_contabilidade.db'),
    ]

    db_path = None
    for candidate in db_candidates:
        if os.path.exists(candidate):
            db_path = candidate
            break

    if not db_path:
        print(f"❌ Base de dados não encontrada!")
        print(f"   Tentei:")
        for candidate in db_candidates:
            print(f"   - {candidate}")
        print(f"\n💡 Execute: python3 scripts/check_database.py")
        print(f"   para ver quais bases de dados existem")
        return

    print(f"📁 Base de dados: {db_path}")

    # Verify tables exist
    try:
        test_conn = sqlite3.connect(db_path)
        test_cursor = test_conn.cursor()
        test_cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='boletins'")
        if not test_cursor.fetchone():
            print(f"\n⚠️  A base de dados não tem a tabela 'boletins'")
            test_cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
            tables = test_cursor.fetchall()
            if tables:
                print(f"   Tabelas encontradas: {', '.join([t[0] for t in tables])}")
            else:
                print(f"   Nenhuma tabela encontrada - base de dados vazia?")
            test_conn.close()
            print(f"\n💡 Execute: python3 scripts/check_database.py")
            return
        test_conn.close()
    except Exception as e:
        print(f"❌ Erro ao verificar base de dados: {str(e)}")
        return

    print("=" * 80)
    print("MIGRAÇÃO: Uniformizar nomes dos sócios (BRUNO→BA, RAFAEL→RR)")
    print("=" * 80)

    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # 1. Verificar registos antes
        print("\n=== ANTES DA MIGRAÇÃO ===")
        cursor.execute("SELECT COUNT(*) FROM boletins WHERE socio IN ('BRUNO', 'RAFAEL')")
        boletins_before = cursor.fetchone()[0]
        print(f"Boletins com BRUNO/RAFAEL: {boletins_before}")

        cursor.execute("SELECT COUNT(*) FROM despesas WHERE tipo IN ('PESSOAL_BRUNO', 'PESSOAL_RAFAEL')")
        despesas_before = cursor.fetchone()[0]
        print(f"Despesas com PESSOAL_BRUNO/PESSOAL_RAFAEL: {despesas_before}")

        # 2. Atualizar boletins
        print("\n1. Atualizando boletins...")
        cursor.execute("UPDATE boletins SET socio = 'BA' WHERE socio = 'BRUNO'")
        bruno_count = cursor.rowcount
        print(f"   - {bruno_count} boletins: BRUNO → BA")

        cursor.execute("UPDATE boletins SET socio = 'RR' WHERE socio = 'RAFAEL'")
        rafael_count = cursor.rowcount
        print(f"   - {rafael_count} boletins: RAFAEL → RR")

        # 3. Atualizar despesas
        print("\n2. Atualizando despesas...")
        cursor.execute("UPDATE despesas SET tipo = 'PESSOAL_BA' WHERE tipo = 'PESSOAL_BRUNO'")
        bruno_desp_count = cursor.rowcount
        print(f"   - {bruno_desp_count} despesas: PESSOAL_BRUNO → PESSOAL_BA")

        cursor.execute("UPDATE despesas SET tipo = 'PESSOAL_RR' WHERE tipo = 'PESSOAL_RAFAEL'")
        rafael_desp_count = cursor.rowcount
        print(f"   - {rafael_desp_count} despesas: PESSOAL_RAFAEL → PESSOAL_RR")

        # Commit
        conn.commit()

        # 4. Verificar registos depois
        print("\n=== DEPOIS DA MIGRAÇÃO ===")
        cursor.execute("SELECT COUNT(*) FROM boletins WHERE socio IN ('BRUNO', 'RAFAEL')")
        boletins_after = cursor.fetchone()[0]
        print(f"Boletins com BRUNO/RAFAEL: {boletins_after}")

        cursor.execute("SELECT COUNT(*) FROM despesas WHERE tipo IN ('PESSOAL_BRUNO', 'PESSOAL_RAFAEL')")
        despesas_after = cursor.fetchone()[0]
        print(f"Despesas com PESSOAL_BRUNO/PESSOAL_RAFAEL: {despesas_after}")

        cursor.execute("SELECT COUNT(*) FROM boletins WHERE socio IN ('BA', 'RR')")
        boletins_new = cursor.fetchone()[0]
        print(f"Boletins com BA/RR: {boletins_new}")

        cursor.execute("SELECT COUNT(*) FROM despesas WHERE tipo IN ('PESSOAL_BA', 'PESSOAL_RR')")
        despesas_new = cursor.fetchone()[0]
        print(f"Despesas com PESSOAL_BA/PESSOAL_RR: {despesas_new}")

        print("\n" + "=" * 80)
        print("✅ MIGRAÇÃO COMPLETA!")
        print("=" * 80)

        if boletins_after == 0 and despesas_after == 0:
            print("\n✅ Todos os registos foram migrados com sucesso!")
        else:
            print(f"\n⚠️  Ainda existem registos por migrar:")
            print(f"   - Boletins: {boletins_after}")
            print(f"   - Despesas: {despesas_after}")

    except Exception as e:
        print(f"\n❌ ERRO durante migração: {str(e)}")
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    migrate_socio_names()
