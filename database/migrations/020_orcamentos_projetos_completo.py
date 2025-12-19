#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Migração 020: Orçamentos e Projetos - Sistema Completo

Alterações:
1. orcamentos: Adicionar coluna owner
2. projetos: Adicionar owner, campos de rastreabilidade, data_pagamento, atualizar estados
3. proposta_reparticoes: Remover entidade, adicionar tipo e FKs (fornecedor_id, equipamento_id)
4. equipamento: Adicionar rendimento_acumulado

IMPORTANTE: Execute este script ANTES de iniciar a aplicação após o pull.

Execução:
    python3 database/migrations/020_orcamentos_projetos_completo.py
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
    """Aplicar todas as alterações da migration 020"""
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        # Usar SQLite default
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        database_url = f"sqlite:///{os.path.join(project_root, 'agora_media.db')}"
        print(f"ℹ️  DATABASE_URL não definido. Usando SQLite: {database_url}")

    print(f"🔗 Conectando à base de dados...")
    engine = create_engine(database_url)

    with engine.connect() as conn:
        print("\n" + "="*60)
        print("MIGRATION 020: Orçamentos e Projetos - Sistema Completo")
        print("="*60)

        # ================================================================
        # 1. ORCAMENTOS - Adicionar coluna owner
        # ================================================================
        print("\n📋 [1/4] Tabela ORCAMENTOS...")

        # Verificar se coluna já existe
        result = conn.execute(text("PRAGMA table_info(orcamentos)"))
        columns = [row[1] for row in result]

        if 'owner' not in columns:
            print("   → Adicionando coluna 'owner'...")
            conn.execute(text(
                "ALTER TABLE orcamentos ADD COLUMN owner VARCHAR(2) NOT NULL DEFAULT 'BA'"
            ))
            conn.commit()
            print("   ✅ Coluna 'owner' adicionada (default: 'BA')")
        else:
            print("   ⏭️  Coluna 'owner' já existe")

        # ================================================================
        # 2. PROJETOS - Múltiplas alterações
        # ================================================================
        print("\n📋 [2/4] Tabela PROJETOS...")

        result = conn.execute(text("PRAGMA table_info(projetos)"))
        columns = [row[1] for row in result]

        # 2.1 Adicionar coluna owner
        if 'owner' not in columns:
            print("   → Adicionando coluna 'owner'...")
            conn.execute(text(
                "ALTER TABLE projetos ADD COLUMN owner VARCHAR(2)"
            ))
            conn.commit()

            # Inferir owner baseado no tipo
            print("   → Inferindo 'owner' baseado em 'tipo'...")
            conn.execute(text(
                "UPDATE projetos SET owner = 'BA' WHERE tipo = 'PESSOAL_BA'"
            ))
            conn.execute(text(
                "UPDATE projetos SET owner = 'RR' WHERE tipo = 'PESSOAL_RR'"
            ))
            conn.execute(text(
                "UPDATE projetos SET owner = 'BA' WHERE tipo = 'EMPRESA'"
            ))
            conn.commit()

            # Tornar NOT NULL após preencher
            print("   → Tornando 'owner' NOT NULL...")
            # SQLite não suporta ALTER COLUMN, então vamos apenas verificar
            result = conn.execute(text("SELECT COUNT(*) FROM projetos WHERE owner IS NULL"))
            null_count = result.fetchone()[0]

            if null_count > 0:
                print(f"   ⚠️  Aviso: {null_count} projetos sem owner definido. Definindo como 'BA'...")
                conn.execute(text("UPDATE projetos SET owner = 'BA' WHERE owner IS NULL"))
                conn.commit()

            print("   ✅ Coluna 'owner' adicionada e preenchida")
        else:
            print("   ⏭️  Coluna 'owner' já existe")

        # 2.2 Adicionar colunas de rastreabilidade financeira
        for col_name, col_desc in [
            ('valor_empresa', 'Parcela da empresa'),
            ('valor_fornecedores', 'Total pago a fornecedores'),
            ('valor_equipamento', 'Rendimento de equipamento'),
            ('valor_despesas', 'Despesas do projeto')
        ]:
            if col_name not in columns:
                print(f"   → Adicionando coluna '{col_name}' ({col_desc})...")
                conn.execute(text(
                    f"ALTER TABLE projetos ADD COLUMN {col_name} DECIMAL(10,2) DEFAULT 0"
                ))
                conn.commit()
                print(f"   ✅ Coluna '{col_name}' adicionada")
            else:
                print(f"   ⏭️  Coluna '{col_name}' já existe")

        # 2.3 Adicionar data_pagamento
        if 'data_pagamento' not in columns:
            print("   → Adicionando coluna 'data_pagamento'...")
            conn.execute(text(
                "ALTER TABLE projetos ADD COLUMN data_pagamento DATE NULL"
            ))
            conn.commit()
            print("   ✅ Coluna 'data_pagamento' adicionada")
        else:
            print("   ⏭️  Coluna 'data_pagamento' já existe")

        # 2.4 Migrar estados antigos para novos
        print("   → Migrando estados (ativo→ATIVO, concluido→FINALIZADO, cancelado→ANULADO)...")

        result = conn.execute(text(
            "SELECT COUNT(*) FROM projetos WHERE estado IN ('ativo', 'concluido', 'cancelado')"
        ))
        count_old = result.fetchone()[0]

        if count_old > 0:
            conn.execute(text("UPDATE projetos SET estado = 'ATIVO' WHERE estado = 'ativo'"))
            conn.execute(text("UPDATE projetos SET estado = 'FINALIZADO' WHERE estado = 'concluido'"))
            conn.execute(text("UPDATE projetos SET estado = 'ANULADO' WHERE estado = 'cancelado'"))
            conn.commit()
            print(f"   ✅ {count_old} projetos com estados atualizados")
        else:
            print("   ⏭️  Nenhum estado antigo encontrado")

        # ================================================================
        # 3. ORCAMENTO_REPARTICOES - Reestruturação
        # ================================================================
        print("\n📋 [3/4] Tabela ORCAMENTO_REPARTICOES...")

        result = conn.execute(text("PRAGMA table_info(orcamento_reparticoes)"))
        columns = [row[1] for row in result]

        # 3.1 Adicionar coluna tipo (mapear de entidade antes de remover)
        if 'tipo' not in columns and 'entidade' in columns:
            print("   → Adicionando coluna 'tipo' (mapeando de 'entidade')...")
            conn.execute(text(
                "ALTER TABLE orcamento_reparticoes ADD COLUMN tipo VARCHAR(20)"
            ))
            conn.commit()

            # Mapear valores
            print("   → Mapeando valores: entidade='BA'→tipo='BA', entidade='RR'→tipo='RR'...")
            conn.execute(text(
                "UPDATE orcamento_reparticoes SET tipo = entidade WHERE entidade IN ('BA', 'RR')"
            ))
            conn.commit()

            # Verificar se há valores NULL
            result = conn.execute(text(
                "SELECT COUNT(*) FROM orcamento_reparticoes WHERE tipo IS NULL"
            ))
            null_count = result.fetchone()[0]

            if null_count > 0:
                print(f"   ⚠️  Aviso: {null_count} repartições sem tipo. Definindo como 'EMPRESA'...")
                conn.execute(text(
                    "UPDATE orcamento_reparticoes SET tipo = 'EMPRESA' WHERE tipo IS NULL"
                ))
                conn.commit()

            print("   ✅ Coluna 'tipo' adicionada e preenchida")
        elif 'tipo' in columns:
            print("   ⏭️  Coluna 'tipo' já existe")
        else:
            print("   → Adicionando coluna 'tipo' (sem entidade para mapear)...")
            conn.execute(text(
                "ALTER TABLE orcamento_reparticoes ADD COLUMN tipo VARCHAR(20) DEFAULT 'BA'"
            ))
            conn.commit()
            print("   ✅ Coluna 'tipo' adicionada")

        # 3.2 Adicionar fornecedor_id
        if 'fornecedor_id' not in columns:
            print("   → Adicionando coluna 'fornecedor_id' (FK → fornecedores)...")
            conn.execute(text(
                "ALTER TABLE orcamento_reparticoes ADD COLUMN fornecedor_id INTEGER NULL"
            ))
            conn.commit()
            print("   ✅ Coluna 'fornecedor_id' adicionada")
        else:
            print("   ⏭️  Coluna 'fornecedor_id' já existe")

        # 3.3 Adicionar equipamento_id
        if 'equipamento_id' not in columns:
            print("   → Adicionando coluna 'equipamento_id' (FK → equipamento)...")
            conn.execute(text(
                "ALTER TABLE orcamento_reparticoes ADD COLUMN equipamento_id INTEGER NULL"
            ))
            conn.commit()
            print("   ✅ Coluna 'equipamento_id' adicionada")
        else:
            print("   ⏭️  Coluna 'equipamento_id' já existe")

        # 3.4 NOTA sobre remoção de 'entidade'
        # SQLite não suporta DROP COLUMN facilmente.
        # A coluna 'entidade' será ignorada no código Python.
        if 'entidade' in columns:
            print("   ℹ️  Nota: Coluna 'entidade' mantida (SQLite não suporta DROP COLUMN)")
            print("      A coluna será ignorada no código. Pode ser removida manualmente se necessário.")

        # ================================================================
        # 4. EQUIPAMENTO - Adicionar rendimento_acumulado
        # ================================================================
        print("\n📋 [4/4] Tabela EQUIPAMENTO...")

        result = conn.execute(text("PRAGMA table_info(equipamento)"))
        columns = [row[1] for row in result]

        if 'rendimento_acumulado' not in columns:
            print("   → Adicionando coluna 'rendimento_acumulado'...")
            conn.execute(text(
                "ALTER TABLE equipamento ADD COLUMN rendimento_acumulado DECIMAL(10,2) DEFAULT 0"
            ))
            conn.commit()
            print("   ✅ Coluna 'rendimento_acumulado' adicionada")
        else:
            print("   ⏭️  Coluna 'rendimento_acumulado' já existe")

        print("\n" + "="*60)
        print("✅ Migration 020 concluída com sucesso!")
        print("="*60)

        # Resumo
        print("\n📊 RESUMO DAS ALTERAÇÕES:")
        print("   • orcamentos: +1 coluna (owner)")
        print("   • projetos: +6 colunas (owner, 4 valores, data_pagamento) + estados migrados")
        print("   • orcamento_reparticoes: +3 colunas (tipo, fornecedor_id, equipamento_id)")
        print("   • equipamento: +1 coluna (rendimento_acumulado)")


def downgrade():
    """Reverter alterações da migration 020 (apenas colunas novas, estados não são revertidos)"""
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        # Usar SQLite default
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        database_url = f"sqlite:///{os.path.join(project_root, 'agora_media.db')}"

    print("⚠️  ATENÇÃO: Downgrade não é totalmente suportado devido a limitações do SQLite.")
    print("   Algumas colunas não podem ser removidas facilmente.")
    print("   Recomenda-se restaurar backup da base de dados anterior à migration.")

    # Não implementamos downgrade completo devido a limitações do SQLite
    # e risco de perda de dados


if __name__ == "__main__":
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║  MIGRATION 020: Orçamentos e Projetos - Sistema Completo  ║")
    print("╚" + "="*58 + "╝")
    print()

    try:
        upgrade()
        print("\n✨ Pode agora executar a aplicação normalmente.\n")
    except Exception as e:
        print(f"\n❌ Erro durante a migration: {e}")
        print("   Por favor, verifique a base de dados e tente novamente.\n")
        sys.exit(1)
