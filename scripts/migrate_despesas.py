#!/usr/bin/env python3
"""
Script para migrar DESPESAS da app desktop (SQLite) para a web app (PostgreSQL/Docker)

IMPORTANTE: Este script precisa que FORNECEDORES e PROJETOS já tenham sido importados!

Uso:
    python scripts/migrate_despesas.py export    # Exporta despesas do desktop para JSON
    python scripts/migrate_despesas.py import    # Importa JSON para web app via Docker
    python scripts/migrate_despesas.py migrate   # Faz export + import automaticamente
"""

import sys
import json
import sqlite3
from pathlib import Path
from datetime import datetime

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DESKTOP_DB = BASE_DIR / "agora_media.db"
EXPORT_FILE = BASE_DIR / "despesas_export.json"


def export_despesas():
    """Exporta despesas da base SQLite desktop para JSON"""

    if not DESKTOP_DB.exists():
        print(f"❌ Base de dados desktop não encontrada: {DESKTOP_DB}")
        sys.exit(1)

    print(f"📊 A ler despesas de: {DESKTOP_DB}")

    conn = sqlite3.connect(DESKTOP_DB)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Mapas de IDs para números
    cursor.execute("SELECT id, numero FROM fornecedores")
    fornecedores_map = {row["id"]: row["numero"] for row in cursor.fetchall()}

    cursor.execute("SELECT id, numero FROM projetos")
    projetos_map = {row["id"]: row["numero"] for row in cursor.fetchall()}

    # Lê todas as despesas
    cursor.execute("""
        SELECT
            id, numero, tipo, data, credor_id, projeto_id,
            descricao, valor_sem_iva, valor_com_iva,
            estado, data_pagamento, nota,
            despesa_template_id, created_at, updated_at
        FROM despesas
        ORDER BY data DESC, id DESC
    """)

    despesas = cursor.fetchall()
    conn.close()

    if not despesas:
        print("⚠️  Nenhuma despesa encontrada na base desktop!")
        return

    # Converte para fixtures
    fixtures = []
    despesas_sem_credor = 0
    despesas_sem_projeto = 0

    for despesa in despesas:
        credor_numero = None
        if despesa["credor_id"]:
            credor_numero = fornecedores_map.get(despesa["credor_id"])
            if not credor_numero:
                despesas_sem_credor += 1

        projeto_numero = None
        if despesa["projeto_id"]:
            projeto_numero = projetos_map.get(despesa["projeto_id"])
            if not projeto_numero:
                despesas_sem_projeto += 1

        fixture = {
            "model": "core.despesa",
            "fields": {
                "numero": despesa["numero"],
                "tipo": despesa["tipo"] or "FIXA_MENSAL",
                "data": despesa["data"],
                "credor_numero": credor_numero,
                "projeto_numero": projeto_numero,
                "descricao": despesa["descricao"] or "",
                "valor_sem_iva": str(despesa["valor_sem_iva"] or 0),
                "valor_com_iva": str(despesa["valor_com_iva"] or 0),
                "estado": despesa["estado"] or "PENDENTE",
                "data_pagamento": despesa["data_pagamento"],
                "nota": despesa["nota"] or "",
                "despesa_template_numero": None,  # Ignorar templates por agora
                "created_at": despesa["created_at"] or datetime.now().isoformat(),
                "updated_at": despesa["updated_at"] or datetime.now().isoformat(),
            }
        }
        fixtures.append(fixture)

    # Guarda JSON
    with open(EXPORT_FILE, 'w', encoding='utf-8') as f:
        json.dump(fixtures, f, ensure_ascii=False, indent=2)

    print(f"✅ {len(fixtures)} despesas exportadas para: {EXPORT_FILE}")

    if despesas_sem_credor > 0:
        print(f"⚠️  {despesas_sem_credor} despesas sem credor associado")

    if despesas_sem_projeto > 0:
        print(f"⚠️  {despesas_sem_projeto} despesas sem projeto associado")

    print(f"\n📋 Preview das primeiras 3:")
    for i, despesa in enumerate(despesas[:3], 1):
        credor_num = fornecedores_map.get(despesa["credor_id"], "SEM CREDOR") if despesa["credor_id"] else "SEM CREDOR"
        print(f"   {i}. {despesa['numero']} - {despesa['descricao'][:40]} (€{despesa['valor_sem_iva']}, Credor: {credor_num})")

    if len(despesas) > 3:
        print(f"   ... e mais {len(despesas) - 3} despesas")


def import_despesas():
    """Instruções para importar despesas"""

    if not EXPORT_FILE.exists():
        print(f"❌ Ficheiro de export não encontrado: {EXPORT_FILE}")
        print(f"   Corre primeiro: python scripts/migrate_despesas.py export")
        sys.exit(1)

    print(f"📦 Ficheiro pronto para importação!")
    print(f"\n🚀 Comandos para executar NO SERVIDOR:\n")
    print(f"   # 1. Envia para o servidor")
    print(f"   scp {EXPORT_FILE} zumine@instante:~/zumine/amp/docker/app/agora_web/")
    print(f"\n   # 2. No servidor, importa com o comando customizado")
    print(f"   ssh zumine@instante")
    print(f"   cd ~/zumine/amp/docker/app/agora_web")
    print(f"   docker cp despesas_export.json agora_web:/app/")
    print(f"   docker compose -f docker-compose.cloudflare.yml exec web python manage.py import_despesas /app/despesas_export.json")


def migrate():
    """Executa export + import automaticamente"""
    print("🔄 Migração completa: Desktop → Web\n")
    export_despesas()
    print("\n" + "="*60 + "\n")
    import_despesas()


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in ['export', 'import', 'migrate']:
        print(__doc__)
        sys.exit(1)

    command = sys.argv[1]

    if command == 'export':
        export_despesas()
    elif command == 'import':
        import_despesas()
    elif command == 'migrate':
        migrate()


if __name__ == '__main__':
    main()
