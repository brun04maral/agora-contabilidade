# -*- coding: utf-8 -*-
"""
Migration 021: Adicionar campo 'nome' e renomear campo existente para 'nome_formal'

Mudanças na tabela clientes:
- Renomear coluna 'nome' para 'nome_formal' (nome completo/formal da empresa)
- Adicionar nova coluna 'nome' (nome curto para listagens, 120 chars)
- Copiar dados de 'nome_formal' para 'nome' (para garantir compatibilidade)

Data: 2025-11-15
"""
import sqlite3
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


def run_migration():
    """Execute migration 021"""

    db_path = 'agora_media.db'

    if not os.path.exists(db_path):
        print(f"❌ Base de dados não encontrada: {db_path}")
        return False

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        print("=" * 80)
        print("MIGRATION 021: Cliente - Nome e Nome Formal")
        print("=" * 80)

        # Check if migration already applied
        cursor.execute("PRAGMA table_info(clientes)")
        columns = {col[1]: col for col in cursor.fetchall()}

        if 'nome_formal' in columns and 'nome' in columns and columns['nome'][2] == 'VARCHAR(120)':
            print("✓ Migration 021 já aplicada anteriormente")
            conn.close()
            return True

        print("\n📝 Passos:")
        print("1. Renomear coluna 'nome' para 'nome_formal'")
        print("2. Adicionar nova coluna 'nome' (VARCHAR(120))")
        print("3. Copiar dados de 'nome_formal' para 'nome'")

        # Step 1: Rename 'nome' to 'nome_formal'
        print("\n1️⃣  Renomeando 'nome' para 'nome_formal'...")

        # SQLite 3.25+ supports RENAME COLUMN
        try:
            cursor.execute("ALTER TABLE clientes RENAME COLUMN nome TO nome_formal")
            print("   ✓ Coluna renomeada com sucesso")
        except sqlite3.OperationalError as e:
            if "no such column" in str(e).lower():
                # Column already renamed
                print("   ✓ Coluna já estava renomeada")
            else:
                raise

        # Step 2: Add new 'nome' column
        print("\n2️⃣  Adicionando nova coluna 'nome'...")

        try:
            cursor.execute("""
                ALTER TABLE clientes
                ADD COLUMN nome VARCHAR(120) NOT NULL DEFAULT ''
            """)
            print("   ✓ Coluna 'nome' adicionada")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e).lower():
                print("   ✓ Coluna 'nome' já existe")
            else:
                raise

        # Step 3: Copy data from 'nome_formal' to 'nome'
        print("\n3️⃣  Copiando dados de 'nome_formal' para 'nome'...")

        cursor.execute("""
            UPDATE clientes
            SET nome = nome_formal
            WHERE nome = '' OR nome IS NULL
        """)
        affected = cursor.rowcount
        print(f"   ✓ {affected} registro(s) atualizado(s)")

        # Commit changes
        conn.commit()

        # Verify final state
        print("\n✅ Verificação Final:")
        cursor.execute("PRAGMA table_info(clientes)")
        columns_after = cursor.fetchall()

        has_nome = any(col[1] == 'nome' for col in columns_after)
        has_nome_formal = any(col[1] == 'nome_formal' for col in columns_after)

        if has_nome and has_nome_formal:
            print("   ✓ Coluna 'nome' existe")
            print("   ✓ Coluna 'nome_formal' existe")

            # Show sample data
            cursor.execute("SELECT numero, nome, nome_formal FROM clientes LIMIT 3")
            samples = cursor.fetchall()

            if samples:
                print("\n📊 Amostra de dados:")
                for numero, nome, nome_formal in samples:
                    print(f"   {numero}: nome='{nome[:30]}...' | nome_formal='{nome_formal[:30]}...'")

            print("\n✅ MIGRATION 021 CONCLUÍDA COM SUCESSO!")
            return True
        else:
            print("   ❌ Estrutura final incorreta")
            return False

    except Exception as e:
        conn.rollback()
        print(f"\n❌ ERRO durante migration: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        conn.close()


if __name__ == "__main__":
    success = run_migration()
    sys.exit(0 if success else 1)
