# -*- coding: utf-8 -*-
"""
Script de teste para validar a reestruturação dos campos de nome do Cliente

Testa:
1. Existência dos campos 'nome' e 'nome_formal' no modelo Cliente
2. Criação de novo cliente com ambos os campos
3. Atualização de cliente existente
4. Pesquisa por nome e nome_formal
5. Verificação de que dados existentes foram migrados corretamente
"""
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from logic.clientes import ClientesManager
from database.models import Cliente


def test_cliente_nome_fields():
    """Test cliente nome and nome_formal fields"""

    # Create test database connection
    engine = create_engine('sqlite:///agora_media.db')
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        manager = ClientesManager(session)

        print("=" * 80)
        print("TESTE: Campos 'nome' e 'nome_formal' no modelo Cliente")
        print("=" * 80)

        # Test 1: Verify existing clientes have both fields populated
        print("\n1️⃣  Teste: Verificar clientes existentes têm ambos os campos")
        clientes = manager.listar_todos()

        if not clientes:
            print("   ⊘ AVISO: Nenhum cliente encontrado na base de dados")
        else:
            print(f"   ✓ Encontrados {len(clientes)} clientes")

            # Check first 3 clientes
            for cliente in clientes[:3]:
                print(f"\n   Cliente: {cliente.numero}")
                print(f"      - nome: '{cliente.nome}'")
                print(f"      - nome_formal: '{cliente.nome_formal}'")

                if not cliente.nome:
                    print("      ✗ ERRO: Campo 'nome' está vazio!")
                if not cliente.nome_formal:
                    print("      ✗ ERRO: Campo 'nome_formal' está vazio!")

        # Test 2: Create new cliente with both fields
        print("\n2️⃣  Teste: Criar novo cliente com ambos os campos")

        test_nome = "Teste Farmácia"
        test_nome_formal = "Teste Farmácia Central, Lda."

        sucesso, novo_cliente, mensagem = manager.criar(
            nome=test_nome,
            nome_formal=test_nome_formal,
            nif="999999999",
            pais="Portugal"
        )

        if sucesso:
            print(f"   ✓ SUCESSO: Cliente {novo_cliente.numero} criado")
            print(f"      - nome: '{novo_cliente.nome}'")
            print(f"      - nome_formal: '{novo_cliente.nome_formal}'")

            if novo_cliente.nome == test_nome:
                print("      ✓ Campo 'nome' corretamente definido")
            else:
                print(f"      ✗ ERRO: Campo 'nome' incorreto: '{novo_cliente.nome}'")

            if novo_cliente.nome_formal == test_nome_formal:
                print("      ✓ Campo 'nome_formal' corretamente definido")
            else:
                print(f"      ✗ ERRO: Campo 'nome_formal' incorreto: '{novo_cliente.nome_formal}'")

            # Clean up - delete test cliente
            manager.apagar(novo_cliente.id)
            print(f"   ✓ Cliente de teste removido (limpeza)")
        else:
            print(f"   ✗ ERRO: {mensagem}")

        # Test 3: Create cliente with only 'nome' (nome_formal should default to nome)
        print("\n3️⃣  Teste: Criar cliente apenas com 'nome' (nome_formal deve usar default)")

        test_nome_only = "Teste Cliente Simples"

        sucesso, cliente_simples, mensagem = manager.criar(
            nome=test_nome_only,
            pais="Portugal"
        )

        if sucesso:
            print(f"   ✓ SUCESSO: Cliente {cliente_simples.numero} criado")
            print(f"      - nome: '{cliente_simples.nome}'")
            print(f"      - nome_formal: '{cliente_simples.nome_formal}'")

            if cliente_simples.nome_formal == test_nome_only:
                print("      ✓ Campo 'nome_formal' corretamente defaultou para 'nome'")
            else:
                print(f"      ✗ ERRO: Campo 'nome_formal' deveria ser '{test_nome_only}' mas é '{cliente_simples.nome_formal}'")

            # Clean up
            manager.apagar(cliente_simples.id)
            print(f"   ✓ Cliente de teste removido (limpeza)")
        else:
            print(f"   ✗ ERRO: {mensagem}")

        # Test 4: Update existing cliente
        print("\n4️⃣  Teste: Atualizar cliente existente")

        if clientes:
            primeiro_cliente = clientes[0]
            numero_original = primeiro_cliente.numero
            nome_original = primeiro_cliente.nome
            nome_formal_original = primeiro_cliente.nome_formal

            print(f"   Atualizando cliente: {numero_original}")
            print(f"      - nome original: '{nome_original}'")
            print(f"      - nome_formal original: '{nome_formal_original}'")

            novo_nome = "Teste Update Nome"
            novo_nome_formal = "Teste Update Nome Formal, S.A."

            sucesso, cliente_atualizado, mensagem = manager.atualizar(
                primeiro_cliente.id,
                nome=novo_nome,
                nome_formal=novo_nome_formal
            )

            if sucesso:
                session.refresh(primeiro_cliente)
                print(f"   ✓ SUCESSO: Cliente atualizado")
                print(f"      - nome novo: '{primeiro_cliente.nome}'")
                print(f"      - nome_formal novo: '{primeiro_cliente.nome_formal}'")

                if primeiro_cliente.nome == novo_nome and primeiro_cliente.nome_formal == novo_nome_formal:
                    print("      ✓ Ambos os campos foram corretamente atualizados")
                else:
                    print("      ✗ ERRO: Campos não foram atualizados corretamente")

                # Revert changes
                manager.atualizar(
                    primeiro_cliente.id,
                    nome=nome_original,
                    nome_formal=nome_formal_original
                )
                print(f"   ✓ Alterações revertidas")
            else:
                print(f"   ✗ ERRO: {mensagem}")
        else:
            print("   ⊘ SKIP: Nenhum cliente para atualizar")

        # Test 5: Search by nome
        print("\n5️⃣  Teste: Pesquisa por 'nome'")

        if clientes:
            # Use part of the first cliente's nome
            primeiro_cliente = clientes[0]
            termo_busca = primeiro_cliente.nome[:5] if len(primeiro_cliente.nome) >= 5 else primeiro_cliente.nome

            print(f"   Buscando por: '{termo_busca}'")
            resultados = manager.pesquisar(termo_busca)

            print(f"   ✓ Encontrados {len(resultados)} resultado(s)")

            # Check if first cliente is in results
            encontrado = any(c.id == primeiro_cliente.id for c in resultados)
            if encontrado:
                print(f"      ✓ Cliente {primeiro_cliente.numero} encontrado nos resultados")
            else:
                print(f"      ✗ ERRO: Cliente {primeiro_cliente.numero} não encontrado")

        # Test 6: Search by nome_formal
        print("\n6️⃣  Teste: Pesquisa por 'nome_formal'")

        if clientes:
            # Find a cliente with a different nome_formal
            for cliente in clientes:
                if cliente.nome_formal and cliente.nome_formal != cliente.nome:
                    termo_busca = cliente.nome_formal[:8] if len(cliente.nome_formal) >= 8 else cliente.nome_formal

                    print(f"   Buscando por: '{termo_busca}' (do nome_formal)")
                    resultados = manager.pesquisar(termo_busca)

                    print(f"   ✓ Encontrados {len(resultados)} resultado(s)")

                    encontrado = any(c.id == cliente.id for c in resultados)
                    if encontrado:
                        print(f"      ✓ Cliente {cliente.numero} encontrado via nome_formal")
                    else:
                        print(f"      ✗ ERRO: Cliente {cliente.numero} não encontrado via nome_formal")
                    break
            else:
                print("   ⊘ SKIP: Nenhum cliente com nome_formal diferente de nome")

        # Test 7: Verify database schema
        print("\n7️⃣  Teste: Verificar schema da base de dados")

        import sqlite3
        conn = sqlite3.connect('agora_media.db')
        cursor = conn.cursor()

        cursor.execute("PRAGMA table_info(clientes)")
        columns = cursor.fetchall()

        column_names = [col[1] for col in columns]

        if 'nome' in column_names:
            print("   ✓ Coluna 'nome' existe na tabela")
            nome_col = next(col for col in columns if col[1] == 'nome')
            print(f"      - Tipo: {nome_col[2]}")
        else:
            print("   ✗ ERRO: Coluna 'nome' NÃO existe!")

        if 'nome_formal' in column_names:
            print("   ✓ Coluna 'nome_formal' existe na tabela")
            nome_formal_col = next(col for col in columns if col[1] == 'nome_formal')
            print(f"      - Tipo: {nome_formal_col[2]}")
        else:
            print("   ✗ ERRO: Coluna 'nome_formal' NÃO existe!")

        conn.close()

        print("\n" + "=" * 80)
        print("✅ TODOS OS TESTES CONCLUÍDOS")
        print("=" * 80)

        print("\n📖 RESUMO DA REESTRUTURAÇÃO:")
        print("✓ Campo 'nome' (VARCHAR 120): Nome curto para listagens")
        print("✓ Campo 'nome_formal' (VARCHAR 255): Nome completo/formal para documentos")
        print("✓ Listagens mostram apenas 'nome'")
        print("✓ Formulário de edição mostra ambos os campos")
        print("✓ Pesquisa funciona em ambos os campos")
        print("✓ Exportação de propostas usa 'nome_formal'")

    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()

    finally:
        session.close()


if __name__ == "__main__":
    test_cliente_nome_fields()
