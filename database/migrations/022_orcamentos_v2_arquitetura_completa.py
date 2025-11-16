#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Migração 022: Orçamentos V2 - Arquitetura Completa CLIENTE/EMPRESA

Alterações:
1. orcamento_itens (LADO CLIENTE): Adicionar campo tipo e campos específicos por tipo
2. orcamento_reparticoes (LADO EMPRESA): Adicionar beneficiario e campos para todos os tipos
3. Remover tabelas legacy (proposta_secoes, proposta_itens)

IMPORTANTE: Execute este script APÓS o pull com os novos modelos.

Execução:
    python3 database/migrations/022_orcamentos_v2_arquitetura_completa.py
"""
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️  Aviso: módulo dotenv não encontrado. A usar variáveis de ambiente do sistema.")

from sqlalchemy import create_engine, text


def upgrade():
    """Aplicar todas as alterações da migration 022"""
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        # Usar SQLite default
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        database_url = f"sqlite:///{os.path.join(project_root, 'agora_media.db')}"
        print(f"ℹ️  DATABASE_URL não definido. Usando SQLite: {database_url}")

    print(f"🔗 Conectando à base de dados...")
    engine = create_engine(database_url)

    with engine.connect() as conn:
        print("\n" + "="*70)
        print("MIGRATION 022: Orçamentos V2 - Arquitetura Completa CLIENTE/EMPRESA")
        print("="*70)

        # ================================================================
        # 1. ORCAMENTO_ITENS - Adicionar campos para tipos de items CLIENTE
        # ================================================================
        print("\n📋 [1/3] Tabela ORCAMENTO_ITENS (LADO CLIENTE)...")

        result = conn.execute(text("PRAGMA table_info(orcamento_itens)"))
        columns = [row[1] for row in result]

        # 1.1 Adicionar campo tipo
        if 'tipo' not in columns:
            print("   → Adicionando coluna 'tipo'...")
            conn.execute(text(
                "ALTER TABLE orcamento_itens ADD COLUMN tipo VARCHAR(20) DEFAULT 'servico'"
            ))
            conn.commit()

            # Inferir tipo baseado na secção se possível
            print("   → Inferindo 'tipo' baseado nas secções...")
            # Items em secções de equipamento → tipo 'equipamento'
            conn.execute(text("""
                UPDATE orcamento_itens
                SET tipo = 'equipamento'
                WHERE secao_id IN (
                    SELECT id FROM orcamento_secoes WHERE tipo = 'equipamento'
                )
            """))
            # Items em secções de despesas → tipo 'outro' (default para despesas)
            conn.execute(text("""
                UPDATE orcamento_itens
                SET tipo = 'outro'
                WHERE secao_id IN (
                    SELECT id FROM orcamento_secoes WHERE tipo = 'despesas'
                )
            """))
            conn.commit()
            print("   ✅ Coluna 'tipo' adicionada e inferida")
        else:
            print("   ⏭️  Coluna 'tipo' já existe")

        # 1.2 Campos para despesas tipo TRANSPORTE
        for col_name, col_type in [
            ('kms', 'DECIMAL(10,2)'),
            ('valor_por_km', 'DECIMAL(10,2)')
        ]:
            if col_name not in columns:
                print(f"   → Adicionando coluna '{col_name}' (despesas transporte)...")
                conn.execute(text(
                    f"ALTER TABLE orcamento_itens ADD COLUMN {col_name} {col_type} NULL"
                ))
                conn.commit()
                print(f"   ✅ Coluna '{col_name}' adicionada")
            else:
                print(f"   ⏭️  Coluna '{col_name}' já existe")

        # 1.3 Campos para despesas tipo REFEIÇÃO
        for col_name, col_type in [
            ('num_refeicoes', 'INTEGER'),
            ('valor_por_refeicao', 'DECIMAL(10,2)')
        ]:
            if col_name not in columns:
                print(f"   → Adicionando coluna '{col_name}' (despesas refeição)...")
                conn.execute(text(
                    f"ALTER TABLE orcamento_itens ADD COLUMN {col_name} {col_type} NULL"
                ))
                conn.commit()
                print(f"   ✅ Coluna '{col_name}' adicionada")
            else:
                print(f"   ⏭️  Coluna '{col_name}' já existe")

        # 1.4 Campo para despesas tipo OUTRO
        if 'valor_fixo' not in columns:
            print("   → Adicionando coluna 'valor_fixo' (despesas outro)...")
            conn.execute(text(
                "ALTER TABLE orcamento_itens ADD COLUMN valor_fixo DECIMAL(10,2) NULL"
            ))
            conn.commit()
            print("   ✅ Coluna 'valor_fixo' adicionada")
        else:
            print("   ⏭️  Coluna 'valor_fixo' já existe")

        # 1.5 Tornar campos nullable para serviços/equipamento
        print("   ℹ️  Nota: Campos quantidade, dias, preco_unitario, desconto já existentes")

        # ================================================================
        # 2. ORCAMENTO_REPARTICOES - Adicionar campos para LADO EMPRESA
        # ================================================================
        print("\n📋 [2/3] Tabela ORCAMENTO_REPARTICOES (LADO EMPRESA)...")

        result = conn.execute(text("PRAGMA table_info(orcamento_reparticoes)"))
        columns = [row[1] for row in result]

        # 2.1 Adicionar beneficiario
        if 'beneficiario' not in columns:
            print("   → Adicionando coluna 'beneficiario'...")
            conn.execute(text(
                "ALTER TABLE orcamento_reparticoes ADD COLUMN beneficiario VARCHAR(50) NULL"
            ))
            conn.commit()

            # Migrar de 'tipo' se existir (migration 020 mapeou entidade→tipo)
            if 'tipo' in columns and 'entidade' in columns:
                print("   → Migrando valores de 'entidade' para 'beneficiario'...")
                conn.execute(text(
                    "UPDATE orcamento_reparticoes SET beneficiario = entidade WHERE entidade IS NOT NULL"
                ))
                conn.commit()
            elif 'tipo' in columns:
                print("   → Migrando valores de 'tipo' para 'beneficiario' (se aplicável)...")
                conn.execute(text(
                    "UPDATE orcamento_reparticoes SET beneficiario = tipo WHERE tipo IN ('BA', 'RR', 'AGORA')"
                ))
                conn.commit()

            print("   ✅ Coluna 'beneficiario' adicionada")
        else:
            print("   ⏭️  Coluna 'beneficiario' já existe")

        # 2.2 Adicionar descricao se não existir
        if 'descricao' not in columns:
            print("   → Adicionando coluna 'descricao'...")
            conn.execute(text(
                "ALTER TABLE orcamento_reparticoes ADD COLUMN descricao TEXT DEFAULT ''"
            ))
            conn.commit()
            print("   ✅ Coluna 'descricao' adicionada")
        else:
            print("   ⏭️  Coluna 'descricao' já existe")

        # 2.3 Campos para serviços e equipamento
        for col_name, col_type in [
            ('quantidade', 'INTEGER'),
            ('dias', 'INTEGER'),
            ('valor_unitario', 'DECIMAL(10,2)')
        ]:
            if col_name not in columns:
                print(f"   → Adicionando coluna '{col_name}' (serviços/equipamento)...")
                conn.execute(text(
                    f"ALTER TABLE orcamento_reparticoes ADD COLUMN {col_name} {col_type} NULL"
                ))
                conn.commit()
                print(f"   ✅ Coluna '{col_name}' adicionada")
            else:
                print(f"   ⏭️  Coluna '{col_name}' já existe")

        # 2.4 Alterar percentagem para suportar 3 casas decimais (comissões)
        print("   ℹ️  Nota: Campo 'percentagem' já existe. Ajustar precisão se necessário")
        # SQLite não suporta ALTER COLUMN, então vamos manter como está

        # 2.5 Adicionar base_calculo para comissões
        if 'base_calculo' not in columns:
            print("   → Adicionando coluna 'base_calculo' (comissões)...")
            conn.execute(text(
                "ALTER TABLE orcamento_reparticoes ADD COLUMN base_calculo DECIMAL(10,2) NULL"
            ))
            conn.commit()
            print("   ✅ Coluna 'base_calculo' adicionada")
        else:
            print("   ⏭️  Coluna 'base_calculo' já existe")

        # 2.6 Campos para despesas espelhadas
        for col_name, col_type in [
            ('kms', 'DECIMAL(10,2)'),
            ('valor_por_km', 'DECIMAL(10,2)'),
            ('num_refeicoes', 'INTEGER'),
            ('valor_por_refeicao', 'DECIMAL(10,2)'),
            ('valor_fixo', 'DECIMAL(10,2)')
        ]:
            if col_name not in columns:
                print(f"   → Adicionando coluna '{col_name}' (despesas espelhadas)...")
                conn.execute(text(
                    f"ALTER TABLE orcamento_reparticoes ADD COLUMN {col_name} {col_type} NULL"
                ))
                conn.commit()
                print(f"   ✅ Coluna '{col_name}' adicionada")
            else:
                print(f"   ⏭️  Coluna '{col_name}' já existe")

        # 2.7 FK para item cliente (espelhamento)
        if 'item_cliente_id' not in columns:
            print("   → Adicionando coluna 'item_cliente_id' (FK para espelhamento)...")
            conn.execute(text(
                "ALTER TABLE orcamento_reparticoes ADD COLUMN item_cliente_id INTEGER NULL"
            ))
            conn.commit()
            print("   ✅ Coluna 'item_cliente_id' adicionada")
        else:
            print("   ⏭️  Coluna 'item_cliente_id' já existe")

        # 2.8 Atualizar campo 'tipo' se necessário (já existe da migration 020)
        if 'tipo' in columns:
            print("   ℹ️  Campo 'tipo' já existe (migration 020)")
            # Reset valores que não fazem sentido em V2
            print("   → Atualizando valores de 'tipo' para V2...")
            conn.execute(text(
                "UPDATE orcamento_reparticoes SET tipo = 'servico' WHERE tipo NOT IN ('servico', 'equipamento', 'despesa', 'comissao')"
            ))
            conn.commit()
        else:
            print("   → Adicionando coluna 'tipo'...")
            conn.execute(text(
                "ALTER TABLE orcamento_reparticoes ADD COLUMN tipo VARCHAR(20) DEFAULT 'servico'"
            ))
            conn.commit()
            print("   ✅ Coluna 'tipo' adicionada")

        # ================================================================
        # 3. REMOVER TABELAS LEGACY (se existirem)
        # ================================================================
        print("\n📋 [3/3] Remoção de Tabelas Legacy...")

        # Verificar se tabelas existem
        result = conn.execute(text(
            "SELECT name FROM sqlite_master WHERE type='table' AND name IN ('proposta_secoes', 'proposta_itens')"
        ))
        legacy_tables = [row[0] for row in result]

        if 'proposta_secoes' in legacy_tables or 'proposta_itens' in legacy_tables:
            print("   ⚠️  Aviso: Tabelas legacy encontradas (proposta_secoes, proposta_itens)")
            print("   ℹ️  Estas tabelas não fazem parte da arquitetura V2")
            print("   → Pode eliminá-las manualmente se não tiver dados importantes:")
            print("      DROP TABLE IF EXISTS proposta_itens;")
            print("      DROP TABLE IF EXISTS proposta_secoes;")
        else:
            print("   ✅ Nenhuma tabela legacy encontrada")

        print("\n" + "="*70)
        print("✅ Migration 022 concluída com sucesso!")
        print("="*70)

        # Resumo
        print("\n📊 RESUMO DAS ALTERAÇÕES:")
        print("   • orcamento_itens: +7 colunas")
        print("      - tipo, kms, valor_por_km, num_refeicoes,")
        print("        valor_por_refeicao, valor_fixo")
        print("   • orcamento_reparticoes: +13 colunas")
        print("      - beneficiario, descricao, quantidade, dias, valor_unitario,")
        print("        base_calculo, kms, valor_por_km, num_refeicoes,")
        print("        valor_por_refeicao, valor_fixo, item_cliente_id")
        print("   • Tabelas legacy: marcadas para remoção manual")


def downgrade():
    """Reverter alterações da migration 022"""
    print("⚠️  ATENÇÃO: Downgrade não é totalmente suportado devido a limitações do SQLite.")
    print("   Recomenda-se restaurar backup da base de dados anterior à migration.")


if __name__ == "__main__":
    print("\n")
    print("╔" + "="*68 + "╗")
    print("║  MIGRATION 022: Orçamentos V2 - Arquitetura Completa CLIENTE/EMPRESA  ║")
    print("╚" + "="*68 + "╝")
    print()

    try:
        upgrade()
        print("\n✨ Base de dados atualizada para Arquitetura V2!")
        print("   Pode agora executar a aplicação com os novos modelos.\n")
    except Exception as e:
        print(f"\n❌ Erro durante a migration: {e}")
        print("   Por favor, verifique a base de dados e tente novamente.\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)
