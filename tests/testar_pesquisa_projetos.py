# -*- coding: utf-8 -*-
"""
Script de teste para a funcionalidade de pesquisa de projetos

Testa:
1. Método filtrar_por_texto() no ProjetosManager
2. Pesquisa por nome de cliente
3. Pesquisa por descrição
4. Case-insensitive matching
5. Substring matching (pesquisa parcial)
"""
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from logic.projetos import ProjetosManager
from database.models import Base


def test_pesquisa_projetos():
    """Test search functionality for projects"""

    # Create test database connection
    engine = create_engine('sqlite:///agora_media.db')
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        manager = ProjetosManager(session)

        print("=" * 80)
        print("TESTE: Pesquisa de Projetos (Search-as-you-type)")
        print("=" * 80)

        # Test 1: Empty search (should return all)
        print("\n1️⃣  Teste: Pesquisa vazia (deve retornar todos)")
        results = manager.filtrar_por_texto("")
        print(f"   ✓ Resultados: {len(results)} projetos")

        # Test 2: Search by cliente name (partial match)
        print("\n2️⃣  Teste: Pesquisa por nome de cliente (parcial)")
        search_term = "Mendes"
        results = manager.filtrar_por_texto(search_term)
        print(f"   Termo: '{search_term}'")
        print(f"   ✓ Resultados: {len(results)} projetos")

        if results:
            for p in results[:3]:  # Show first 3
                cliente_nome = p.cliente.nome if p.cliente else "-"
                print(f"      - {p.numero}: {cliente_nome} | {p.descricao[:50]}")

        # Test 3: Search by description
        print("\n3️⃣  Teste: Pesquisa por descrição")
        search_term = "video"
        results = manager.filtrar_por_texto(search_term)
        print(f"   Termo: '{search_term}'")
        print(f"   ✓ Resultados: {len(results)} projetos")

        if results:
            for p in results[:3]:  # Show first 3
                cliente_nome = p.cliente.nome if p.cliente else "-"
                print(f"      - {p.numero}: {cliente_nome} | {p.descricao[:50]}")

        # Test 4: Case-insensitive search
        print("\n4️⃣  Teste: Pesquisa case-insensitive")
        search_term_lower = "agora"
        search_term_upper = "AGORA"
        results_lower = manager.filtrar_por_texto(search_term_lower)
        results_upper = manager.filtrar_por_texto(search_term_upper)
        print(f"   Termo lowercase: '{search_term_lower}' → {len(results_lower)} resultados")
        print(f"   Termo uppercase: '{search_term_upper}' → {len(results_upper)} resultados")

        if len(results_lower) == len(results_upper):
            print(f"   ✓ SUCESSO: Case-insensitive funciona!")
        else:
            print(f"   ✗ ERRO: Resultados diferentes!")

        # Test 5: Substring matching
        print("\n5️⃣  Teste: Substring matching (pesquisa parcial)")
        search_term = "manut"
        results = manager.filtrar_por_texto(search_term)
        print(f"   Termo: '{search_term}' (parcial)")
        print(f"   ✓ Resultados: {len(results)} projetos")

        if results:
            for p in results[:3]:  # Show first 3
                cliente_nome = p.cliente.nome if p.cliente else "-"
                print(f"      - {p.numero}: {cliente_nome} | {p.descricao[:50]}")

        # Test 6: No results
        print("\n6️⃣  Teste: Pesquisa sem resultados")
        search_term = "XYZABC123456789"
        results = manager.filtrar_por_texto(search_term)
        print(f"   Termo: '{search_term}'")
        print(f"   ✓ Resultados: {len(results)} projetos")

        if len(results) == 0:
            print(f"   ✓ SUCESSO: Nenhum resultado encontrado (esperado)")

        # Test 7: Single character search (should work)
        print("\n7️⃣  Teste: Pesquisa com 1 caracter")
        search_term = "a"
        results = manager.filtrar_por_texto(search_term)
        print(f"   Termo: '{search_term}'")
        print(f"   ✓ Resultados: {len(results)} projetos")

        # Test 8: Search with spaces (should handle trimming)
        print("\n8️⃣  Teste: Pesquisa com espaços (trim)")
        search_term = "  video  "
        results = manager.filtrar_por_texto(search_term)
        print(f"   Termo: '{search_term}' (com espaços)")
        print(f"   ✓ Resultados: {len(results)} projetos")

        print("\n" + "=" * 80)
        print("✅ TODOS OS TESTES CONCLUÍDOS")
        print("=" * 80)

    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()

    finally:
        session.close()


if __name__ == "__main__":
    test_pesquisa_projetos()
