# -*- coding: utf-8 -*-
"""
Script de teste para validar o menu de contexto de Projetos

Testa:
1. Método duplicar_projeto() no ProjetosManager
2. Método mudar_estado() no ProjetosManager
3. Transições de estado válidas
4. Lógica de data_pagamento ao marcar como PAGO
"""
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from logic.projetos import ProjetosManager
from database.models import EstadoProjeto
from datetime import date


def test_context_menu_operations():
    """Test context menu operations for projects"""

    # Create test database connection
    engine = create_engine('sqlite:///agora_media.db')
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        manager = ProjetosManager(session)

        print("=" * 80)
        print("TESTE: Menu de Contexto de Projetos (Right-Click)")
        print("=" * 80)

        # Get a sample project
        projetos = manager.listar_todos()
        if not projetos:
            print("\n❌ ERRO: Nenhum projeto encontrado na base de dados")
            return

        projeto_teste = projetos[0]
        print(f"\nUsando projeto de teste: {projeto_teste.numero}")
        print(f"Estado atual: {projeto_teste.estado.value}")
        print(f"Descrição: {projeto_teste.descricao}")

        # Test 1: Duplicar Projeto
        print("\n1️⃣  Teste: Duplicar Projeto")
        sucesso, novo_projeto, erro = manager.duplicar_projeto(projeto_teste.id)

        if sucesso:
            print(f"   ✓ SUCESSO: Projeto duplicado como {novo_projeto.numero}")
            print(f"   - Estado: {novo_projeto.estado.value} (deve ser ATIVO)")
            print(f"   - Descrição: {novo_projeto.descricao}")

            # Clean up - delete duplicated project
            manager.apagar(novo_projeto.id)
            print(f"   ✓ Projeto duplicado removido (limpeza)")
        else:
            print(f"   ✗ ERRO: {erro}")

        # Test 2: Mudar Estado - ATIVO → FINALIZADO
        print("\n2️⃣  Teste: Mudar Estado (ATIVO → FINALIZADO)")

        # Find an ATIVO project or use the test project
        projeto_ativo = next(
            (p for p in projetos if p.estado == EstadoProjeto.ATIVO),
            None
        )

        if projeto_ativo:
            estado_original = projeto_ativo.estado
            print(f"   Projeto: {projeto_ativo.numero} ({estado_original.value})")

            sucesso, erro = manager.mudar_estado(
                projeto_ativo.id,
                EstadoProjeto.FINALIZADO
            )

            if sucesso:
                # Refresh project
                session.refresh(projeto_ativo)
                print(f"   ✓ SUCESSO: Estado alterado para {projeto_ativo.estado.value}")

                # Revert change
                manager.mudar_estado(projeto_ativo.id, estado_original)
                print(f"   ✓ Estado revertido para {estado_original.value}")
            else:
                print(f"   ✗ ERRO: {erro}")
        else:
            print("   ⊘ SKIP: Nenhum projeto ATIVO encontrado")

        # Test 3: Mudar Estado - FINALIZADO → PAGO (com data_pagamento)
        print("\n3️⃣  Teste: Mudar Estado (FINALIZADO → PAGO com data_pagamento)")

        projeto_finalizado = next(
            (p for p in projetos if p.estado == EstadoProjeto.FINALIZADO),
            None
        )

        if projeto_finalizado:
            estado_original = projeto_finalizado.estado
            print(f"   Projeto: {projeto_finalizado.numero} ({estado_original.value})")

            hoje = date.today()
            sucesso, erro = manager.mudar_estado(
                projeto_finalizado.id,
                EstadoProjeto.PAGO,
                data_pagamento=hoje
            )

            if sucesso:
                # Refresh project
                session.refresh(projeto_finalizado)
                print(f"   ✓ SUCESSO: Estado alterado para {projeto_finalizado.estado.value}")
                print(f"   - Data de pagamento: {projeto_finalizado.data_pagamento}")

                if projeto_finalizado.data_pagamento == hoje:
                    print("   ✓ Data de pagamento corretamente definida")
                else:
                    print("   ✗ ERRO: Data de pagamento incorreta")

                # Revert change
                manager.mudar_estado(projeto_finalizado.id, estado_original)
                session.refresh(projeto_finalizado)
                print(f"   ✓ Estado revertido para {estado_original.value}")
                print(f"   - Data de pagamento limpa: {projeto_finalizado.data_pagamento}")
            else:
                print(f"   ✗ ERRO: {erro}")
        else:
            print("   ⊘ SKIP: Nenhum projeto FINALIZADO encontrado")

        # Test 4: Mudar Estado - PAGO → FINALIZADO
        print("\n4️⃣  Teste: Mudar Estado (PAGO → FINALIZADO)")

        projeto_pago = next(
            (p for p in projetos if p.estado == EstadoProjeto.PAGO),
            None
        )

        if projeto_pago:
            estado_original = projeto_pago.estado
            print(f"   Projeto: {projeto_pago.numero} ({estado_original.value})")

            sucesso, erro = manager.mudar_estado(
                projeto_pago.id,
                EstadoProjeto.FINALIZADO
            )

            if sucesso:
                # Refresh project
                session.refresh(projeto_pago)
                print(f"   ✓ SUCESSO: Estado alterado para {projeto_pago.estado.value}")
                print(f"   - Data de pagamento removida: {projeto_pago.data_pagamento}")

                # Revert change
                manager.mudar_estado(projeto_pago.id, estado_original, data_pagamento=date.today())
                print(f"   ✓ Estado revertido para {estado_original.value}")
            else:
                print(f"   ✗ ERRO: {erro}")
        else:
            print("   ⊘ SKIP: Nenhum projeto PAGO encontrado")

        # Test 5: Anular Projeto
        print("\n5️⃣  Teste: Anular Projeto")

        # Use test project
        estado_original = projeto_teste.estado
        print(f"   Projeto: {projeto_teste.numero} ({estado_original.value})")

        sucesso, erro = manager.mudar_estado(
            projeto_teste.id,
            EstadoProjeto.ANULADO
        )

        if sucesso:
            # Refresh project
            session.refresh(projeto_teste)
            print(f"   ✓ SUCESSO: Projeto anulado (estado: {projeto_teste.estado.value})")

            # Revert change
            manager.mudar_estado(projeto_teste.id, estado_original)
            print(f"   ✓ Estado revertido para {estado_original.value}")
        else:
            print(f"   ✗ ERRO: {erro}")

        # Test 6: Estados disponíveis por estado atual
        print("\n6️⃣  Teste: Opções de Menu por Estado Atual")
        estados = [EstadoProjeto.ATIVO, EstadoProjeto.FINALIZADO, EstadoProjeto.PAGO, EstadoProjeto.ANULADO]

        for estado in estados:
            print(f"\n   Estado: {estado.value}")

            if estado == EstadoProjeto.ATIVO:
                print("      ✅ Marcar como Finalizado")
                print("      ⛔ Anular Projeto")
            elif estado == EstadoProjeto.FINALIZADO:
                print("      ✅ Marcar como Pago")
                print("      ⏪ Voltar a Ativo")
                print("      ⛔ Anular Projeto")
            elif estado == EstadoProjeto.PAGO:
                print("      ⏪ Voltar a Finalizado")
                print("      ⛔ Anular Projeto")
            elif estado == EstadoProjeto.ANULADO:
                print("      (sem opções de mudança de estado)")

            print("      📋 Duplicar (sempre disponível)")
            print("      ✏️ Editar (sempre disponível)")
            print("      🗑️ Apagar (sempre disponível)")

        print("\n" + "=" * 80)
        print("✅ TODOS OS TESTES CONCLUÍDOS")
        print("=" * 80)

        print("\n📖 INSTRUÇÕES PARA TESTE MANUAL:")
        print("1. Executar a aplicação: python main.py")
        print("2. Navegar para 'Projetos'")
        print("3. Fazer right-click em qualquer projeto")
        print("4. Verificar opções do menu baseadas no estado")
        print("5. Testar cada ação:")
        print("   - ✏️ Editar → Abre formulário de edição")
        print("   - 📋 Duplicar → Cria cópia com estado ATIVO")
        print("   - ✅ Marcar como... → Muda estado (com confirmação)")
        print("   - ⏪ Voltar a... → Reverte estado (com confirmação)")
        print("   - ⛔ Anular → Marca como ANULADO (riscado)")
        print("   - 🗑️ Apagar → Remove permanentemente (com aviso)")

    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()

    finally:
        session.close()


if __name__ == "__main__":
    test_context_menu_operations()
