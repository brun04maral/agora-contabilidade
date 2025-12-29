#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para migrar Equipamentos do desktop (SQLite) para web (Django fixtures)
"""
import sqlite3
import json
from datetime import datetime
from pathlib import Path

DESKTOP_DB = Path(__file__).parent.parent / 'agora_media.db'
FIXTURE_FILE = Path(__file__).parent.parent / 'agora_web' / 'core' / 'fixtures' / 'equipamentos.json'


def export_equipamentos():
    """Exporta equipamentos do desktop DB para fixture Django"""

    conn = sqlite3.connect(DESKTOP_DB)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    print(f"📦 Exportando equipamentos de {DESKTOP_DB}...")

    cursor.execute("""
        SELECT
            id, numero, produto, tipo, label, descricao, numero_serie, mac_address,
            referencia, quantidade, tamanho, data_compra, valor_compra, fornecedor,
            fatura_url, preco_aluguer, amortizacao_vezes, rendimento_acumulado,
            estado, localizacao, foto_url, uso_pessoal, nota, created_at, updated_at
        FROM equipamento
        ORDER BY id
    """)

    equipamentos = cursor.fetchall()
    conn.close()

    print(f"   Encontrados {len(equipamentos)} equipamentos")

    fixtures = []
    for eq in equipamentos:
        fixture = {
            "model": "core.equipamento",
            "fields": {
                "numero": eq["numero"],
                "produto": eq["produto"],
                "tipo": eq["tipo"] or "",
                "label": eq["label"] or "",
                "descricao": eq["descricao"] or "",
                "numero_serie": eq["numero_serie"] or "",
                "mac_address": eq["mac_address"] or "",
                "referencia": eq["referencia"] or "",
                "quantidade": eq["quantidade"] or 1,
                "tamanho": eq["tamanho"] or "",
                "data_compra": eq["data_compra"],
                "valor_compra": str(eq["valor_compra"]) if eq["valor_compra"] else "0.00",
                "fornecedor": eq["fornecedor"] or "",
                "fatura_url": eq["fatura_url"] or "",
                "preco_aluguer": str(eq["preco_aluguer"]) if eq["preco_aluguer"] else "0.00",
                "amortizacao_vezes": eq["amortizacao_vezes"] or 0,
                "rendimento_acumulado": str(eq["rendimento_acumulado"]) if eq["rendimento_acumulado"] else "0.00",
                "estado": eq["estado"] or "ATIVO",
                "localizacao": eq["localizacao"] or "",
                "foto_url": eq["foto_url"] or "",
                "uso_pessoal": eq["uso_pessoal"] or "EMPRESA",
                "nota": eq["nota"] or "",
                "created_at": eq["created_at"] or datetime.now().isoformat(),
                "updated_at": eq["updated_at"] or datetime.now().isoformat(),
            }
        }
        fixtures.append(fixture)

    # Criar diretório de fixtures se não existir
    FIXTURE_FILE.parent.mkdir(parents=True, exist_ok=True)

    # Escrever fixtures
    with open(FIXTURE_FILE, 'w', encoding='utf-8') as f:
        json.dump(fixtures, f, indent=2, ensure_ascii=False)

    print(f"✅ Exportados {len(fixtures)} equipamentos para {FIXTURE_FILE}")
    print("\n📋 Próximos passos:")
    print("   1. Copiar fixtures/equipamentos.json para o servidor")
    print("   2. Executar: docker compose -f docker-compose.cloudflare.yml exec web python manage.py loaddata equipamentos.json")


if __name__ == '__main__':
    export_equipamentos()
