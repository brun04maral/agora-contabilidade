# -*- coding: utf-8 -*-
"""
Script de verificação do schema da tabela clientes

Verifica se a migration 021 foi aplicada corretamente:
- Campo 'nome' (VARCHAR 120) existe
- Campo 'nome_formal' (VARCHAR 255) existe
- Dados foram migrados corretamente
"""
import sqlite3
import os

def verify_cliente_schema():
    """Verify clientes table schema"""

    db_path = 'agora_media.db'

    if not os.path.exists(db_path):
        print(f"❌ Base de dados não encontrada: {db_path}")
        return False

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        print("=" * 80)
        print("VERIFICAÇÃO: Schema da Tabela Clientes")
        print("=" * 80)

        # Check table structure
        print("\n1️⃣  Estrutura da Tabela:")
        cursor.execute("PRAGMA table_info(clientes)")
        columns = cursor.fetchall()

        print("\n   Colunas encontradas:")
        has_nome = False
        has_nome_formal = False

        for col in columns:
            col_id, col_name, col_type, not_null, default_val, pk = col
            print(f"      - {col_name}: {col_type} {'NOT NULL' if not_null else 'NULL'}")

            if col_name == 'nome':
                has_nome = True
                if 'VARCHAR(120)' in col_type:
                    print(f"        ✓ Tipo correto: {col_type}")
                else:
                    print(f"        ⚠ Tipo: {col_type} (esperado: VARCHAR(120))")

            if col_name == 'nome_formal':
                has_nome_formal = True
                if 'VARCHAR(255)' in col_type:
                    print(f"        ✓ Tipo correto: {col_type}")
                else:
                    print(f"        ⚠ Tipo: {col_type} (esperado: VARCHAR(255))")

        print("\n2️⃣  Verificação de Campos Obrigatórios:")
        if has_nome:
            print("   ✓ Campo 'nome' existe")
        else:
            print("   ✗ ERRO: Campo 'nome' NÃO existe!")

        if has_nome_formal:
            print("   ✓ Campo 'nome_formal' existe")
        else:
            print("   ✗ ERRO: Campo 'nome_formal' NÃO existe!")

        # Check data migration
        print("\n3️⃣  Verificação de Dados Migrados:")
        cursor.execute("SELECT COUNT(*) FROM clientes")
        total_clientes = cursor.fetchone()[0]
        print(f"   Total de clientes: {total_clientes}")

        if total_clientes > 0:
            # Check if all clientes have both fields populated
            cursor.execute("""
                SELECT COUNT(*) FROM clientes
                WHERE nome IS NULL OR nome = '' OR nome_formal IS NULL OR nome_formal = ''
            """)
            empty_fields = cursor.fetchone()[0]

            if empty_fields == 0:
                print(f"   ✓ Todos os {total_clientes} clientes têm ambos os campos preenchidos")
            else:
                print(f"   ⚠ AVISO: {empty_fields} cliente(s) com campos vazios")

            # Show sample data
            print("\n4️⃣  Amostra de Dados (primeiros 5 clientes):")
            cursor.execute("""
                SELECT numero, nome, nome_formal
                FROM clientes
                ORDER BY numero DESC
                LIMIT 5
            """)

            samples = cursor.fetchall()
            for numero, nome, nome_formal in samples:
                nome_display = nome[:40] + "..." if len(nome) > 40 else nome
                nome_formal_display = nome_formal[:40] + "..." if len(nome_formal) > 40 else nome_formal

                print(f"\n   {numero}:")
                print(f"      nome: '{nome_display}'")
                print(f"      nome_formal: '{nome_formal_display}'")

                if nome and nome_formal:
                    print("      ✓ Ambos os campos preenchidos")
                else:
                    print("      ✗ ERRO: Campos vazios detectados")

        print("\n" + "=" * 80)
        if has_nome and has_nome_formal:
            print("✅ SCHEMA VERIFICADO COM SUCESSO")
            print("=" * 80)
            print("\n📋 Próximos Passos - Testes Manuais:")
            print("1. Executar: python main.py")
            print("2. Navegar para 'Clientes'")
            print("3. Verificar que a tabela mostra apenas 'Nome' (campo curto)")
            print("4. Clicar em 'Novo Cliente':")
            print("   - Verificar campo 'Nome' (obrigatório, 120 chars)")
            print("   - Verificar campo 'Nome Formal' (opcional, 255 chars)")
            print("5. Editar cliente existente:")
            print("   - Verificar que ambos os campos estão preenchidos")
            print("   - Testar atualização de ambos os campos")
            print("6. Testar pesquisa:")
            print("   - Pesquisar por parte do nome curto")
            print("   - Pesquisar por parte do nome formal")
            print("7. Verificar exportação de proposta:")
            print("   - Gerar PDF de orçamento")
            print("   - Confirmar que mostra 'Nome Formal' do cliente")
            return True
        else:
            print("❌ ERRO: Schema incompleto!")
            print("=" * 80)
            return False

    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        conn.close()


if __name__ == "__main__":
    import sys
    success = verify_cliente_schema()
    sys.exit(0 if success else 1)
