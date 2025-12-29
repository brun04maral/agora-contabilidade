#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para exportar Orçamentos do desktop (SQLite) para JSON intermediário
Este script exporta para JSON com IDs para lookup, depois usamos management command para importar
"""
import sqlite3
import json
from datetime import datetime
from pathlib import Path

DESKTOP_DB = Path(__file__).parent.parent / 'agora_media.db'
FIXTURE_FILE = Path(__file__).parent.parent / 'agora_web' / 'core' / 'fixtures' / 'orcamentos_raw.json'


def export_orcamentos():
    """Exporta orçamentos e tabelas relacionadas para JSON"""

    conn = sqlite3.connect(DESKTOP_DB)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    print(f"📦 Exportando orçamentos de {DESKTOP_DB}...")

    # Exportar orçamentos
    cursor.execute("""
        SELECT
            id, codigo, cliente_id, projeto_id, owner, data_criacao, data_evento,
            local_evento, descricao_proposta, valor_total, notas_contratuais,
            status, tem_versao_cliente, titulo_cliente, descricao_cliente,
            created_at, updated_at
        FROM orcamentos
        ORDER BY id
    """)
    orcamentos = [dict(row) for row in cursor.fetchall()]
    print(f"   Encontrados {len(orcamentos)} orçamentos")

    # Para cada orçamento, buscar as tabelas relacionadas
    data_export = []

    for orc in orcamentos:
        orc_id = orc['id']

        # Buscar secções
        cursor.execute("""
            SELECT id, orcamento_id, tipo, nome, ordem, parent_id, subtotal
            FROM orcamento_secoes
            WHERE orcamento_id = ?
            ORDER BY ordem
        """, (orc_id,))
        secoes = [dict(row) for row in cursor.fetchall()]

        # Buscar itens
        cursor.execute("""
            SELECT
                id, orcamento_id, secao_id, tipo, descricao, ordem, equipamento_id,
                quantidade, dias, preco_unitario, desconto, kms, valor_por_km,
                num_refeicoes, valor_por_refeicao, valor_fixo, total
            FROM orcamento_itens
            WHERE orcamento_id = ?
            ORDER BY ordem
        """, (orc_id,))
        itens = [dict(row) for row in cursor.fetchall()]

        # Buscar repartições
        cursor.execute("""
            SELECT
                id, orcamento_id, tipo, entidade, fornecedor_id, equipamento_id,
                beneficiario, valor, percentagem, ordem, descricao, quantidade,
                dias, valor_unitario, base_calculo, kms, valor_por_km,
                num_refeicoes, valor_por_refeicao, valor_fixo, item_cliente_id, total
            FROM orcamento_reparticoes
            WHERE orcamento_id = ?
            ORDER BY ordem
        """, (orc_id,))
        reparticoes = [dict(row) for row in cursor.fetchall()]

        # Buscar cliente_numero e projeto_numero se existirem
        cliente_numero = None
        if orc['cliente_id']:
            cursor.execute("SELECT numero FROM clientes WHERE id = ?", (orc['cliente_id'],))
            row = cursor.fetchone()
            if row:
                cliente_numero = row['numero']

        projeto_numero = None
        if orc['projeto_id']:
            cursor.execute("SELECT numero FROM projetos WHERE id = ?", (orc['projeto_id'],))
            row = cursor.fetchone()
            if row:
                projeto_numero = row['numero']

        # Montar estrutura completa
        data_export.append({
            'orcamento': orc,
            'cliente_numero': cliente_numero,
            'projeto_numero': projeto_numero,
            'secoes': secoes,
            'itens': itens,
            'reparticoes': reparticoes
        })

        print(f"   Orçamento {orc['codigo']}: {len(secoes)} secções, {len(itens)} itens, {len(reparticoes)} repartições")

    conn.close()

    # Criar diretório de fixtures se não existir
    FIXTURE_FILE.parent.mkdir(parents=True, exist_ok=True)

    # Escrever JSON
    with open(FIXTURE_FILE, 'w', encoding='utf-8') as f:
        json.dump(data_export, f, indent=2, ensure_ascii=False, default=str)

    print(f"\n✅ Exportados {len(data_export)} orçamentos completos para {FIXTURE_FILE}")
    print("\n📋 Próximos passos:")
    print("   1. Copiar fixtures/orcamentos_raw.json para o servidor")
    print("   2. Executar: docker compose -f docker-compose.cloudflare.yml exec web python manage.py import_orcamentos")


if __name__ == '__main__':
    export_orcamentos()
