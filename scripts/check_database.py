#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar qual base de dados usar e quais tabelas existem
"""
import sqlite3
import os
import glob

def check_databases():
    """Verifica todas as bases de dados .db no projeto"""
    project_root = os.path.join(os.path.dirname(__file__), '..')

    # Find all .db files
    db_files = []
    for root, dirs, files in os.walk(project_root):
        for file in files:
            if file.endswith('.db'):
                db_files.append(os.path.join(root, file))

    print("=" * 80)
    print("BASES DE DADOS ENCONTRADAS:")
    print("=" * 80)

    for db_path in db_files:
        rel_path = os.path.relpath(db_path, project_root)
        print(f"\n📁 {rel_path}")

        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # Get all tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
            tables = cursor.fetchall()

            if tables:
                print(f"   Tabelas ({len(tables)}):")
                for table in tables:
                    cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
                    count = cursor.fetchone()[0]
                    print(f"   - {table[0]}: {count} registos")
            else:
                print("   ⚠️  Sem tabelas")

            conn.close()
        except Exception as e:
            print(f"   ❌ Erro ao abrir: {str(e)}")

    print("\n" + "=" * 80)
    print("RECOMENDAÇÃO:")
    print("=" * 80)

    # Check for agora_media.db
    media_db = os.path.join(project_root, 'agora_media.db')
    if os.path.exists(media_db):
        print(f"✅ Use: agora_media.db")
        print(f"   Caminho completo: {media_db}")
    else:
        print("⚠️  Base de dados 'agora_media.db' não encontrada")
        if db_files:
            print(f"   Considere usar: {db_files[0]}")

if __name__ == "__main__":
    check_databases()
