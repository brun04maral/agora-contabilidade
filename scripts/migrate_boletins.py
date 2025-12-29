#!/usr/bin/env python3
"""
Script para migrar BOLETINS + BOLETIM LINHAS da app desktop (SQLite) para a web app

IMPORTANTE: Boletins têm BoletimLinhas (relação one-to-many).
            As linhas podem ter relação com Projetos (opcional).

Uso:
    python scripts/migrate_boletins.py export    # Exporta boletins + linhas
    python scripts/migrate_boletins.py import    # Instruções de importação
    python scripts/migrate_boletins.py migrate   # Export + import
"""

import sys
import json
import sqlite3
from pathlib import Path
from datetime import datetime

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DESKTOP_DB = BASE_DIR / "agora_media.db"
BOLETINS_EXPORT = BASE_DIR / "boletins_export.json"
LINHAS_EXPORT = BASE_DIR / "boletim_linhas_export.json"


def export_boletins():
    """Exporta boletins e linhas da base SQLite desktop para JSON"""

    if not DESKTOP_DB.exists():
        print(f"❌ Base de dados desktop não encontrada: {DESKTOP_DB}")
        sys.exit(1)

    print(f"📊 A ler boletins de: {DESKTOP_DB}")

    conn = sqlite3.connect(DESKTOP_DB)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # === BOLETINS ===
    cursor.execute("""
        SELECT
            id, numero, socio, mes, ano,
            data_emissao, data_pagamento,
            val_dia_nacional, val_dia_estrangeiro, val_km,
            total_ajudas_nacionais, total_ajudas_estrangeiro, total_kms,
            valor_total, valor, descricao,
            estado, nota, created_at, updated_at
        FROM boletins
        ORDER BY data_emissao DESC, id DESC
    """)

    boletins = cursor.fetchall()

    boletins_fixtures = []
    for boletim in boletins:
        fixture = {
            "model": "core.boletim",
            "fields": {
                "numero": boletim["numero"],
                "socio": boletim["socio"],
                "mes": boletim["mes"],
                "ano": boletim["ano"],
                "data_emissao": boletim["data_emissao"],
                "data_pagamento": boletim["data_pagamento"],
                "val_dia_nacional": str(boletim["val_dia_nacional"] or 0),
                "val_dia_estrangeiro": str(boletim["val_dia_estrangeiro"] or 0),
                "val_km": str(boletim["val_km"] or 0),
                "total_ajudas_nacionais": str(boletim["total_ajudas_nacionais"] or 0),
                "total_ajudas_estrangeiro": str(boletim["total_ajudas_estrangeiro"] or 0),
                "total_kms": str(boletim["total_kms"] or 0),
                "valor_total": str(boletim["valor_total"] or 0),
                "valor": str(boletim["valor"] or 0),
                "descricao": boletim["descricao"] or "",
                "estado": boletim["estado"] or "PENDENTE",
                "nota": boletim["nota"] or "",
                "created_at": boletim["created_at"] or datetime.now().isoformat(),
                "updated_at": boletim["updated_at"] or datetime.now().isoformat(),
            }
        }
        boletins_fixtures.append(fixture)

    # Guarda Boletins
    with open(BOLETINS_EXPORT, 'w', encoding='utf-8') as f:
        json.dump(boletins_fixtures, f, ensure_ascii=False, indent=2)

    print(f"✅ {len(boletins_fixtures)} boletins exportados para: {BOLETINS_EXPORT}")

    # === BOLETIM LINHAS ===
    # Mapas para lookups
    cursor.execute("SELECT id, numero FROM boletins")
    boletins_map = {row["id"]: row["numero"] for row in cursor.fetchall()}

    cursor.execute("SELECT id, numero FROM projetos")
    projetos_map = {row["id"]: row["numero"] for row in cursor.fetchall()}

    cursor.execute("""
        SELECT
            id, boletim_id, ordem, projeto_id,
            servico, localidade,
            data_inicio, hora_inicio, data_fim, hora_fim,
            tipo, dias, kms,
            created_at, updated_at
        FROM boletim_linhas
        ORDER BY boletim_id, ordem
    """)

    linhas = cursor.fetchall()
    conn.close()

    linhas_fixtures = []
    linhas_sem_boletim = 0
    linhas_sem_projeto = 0

    for linha in linhas:
        boletim_numero = boletins_map.get(linha["boletim_id"])
        if not boletim_numero:
            linhas_sem_boletim += 1
            continue  # Skip se não encontrar boletim

        projeto_numero = None
        if linha["projeto_id"]:
            projeto_numero = projetos_map.get(linha["projeto_id"])
            if not projeto_numero:
                linhas_sem_projeto += 1

        fixture = {
            "model": "core.boletimlinha",
            "fields": {
                "boletim_numero": boletim_numero,
                "projeto_numero": projeto_numero,
                "ordem": linha["ordem"],
                "servico": linha["servico"] or "",
                "localidade": linha["localidade"] or "",
                "data_inicio": linha["data_inicio"],
                "hora_inicio": linha["hora_inicio"],
                "data_fim": linha["data_fim"],
                "hora_fim": linha["hora_fim"],
                "tipo": linha["tipo"] or "NACIONAL",
                "dias": str(linha["dias"] or 0),
                "kms": linha["kms"] or 0,
                "created_at": linha["created_at"] or datetime.now().isoformat(),
                "updated_at": linha["updated_at"] or datetime.now().isoformat(),
            }
        }
        linhas_fixtures.append(fixture)

    # Guarda Linhas
    with open(LINHAS_EXPORT, 'w', encoding='utf-8') as f:
        json.dump(linhas_fixtures, f, ensure_ascii=False, indent=2)

    print(f"✅ {len(linhas_fixtures)} linhas de boletim exportadas para: {LINHAS_EXPORT}")

    if linhas_sem_boletim > 0:
        print(f"⚠️  {linhas_sem_boletim} linhas sem boletim associado (ignoradas)")

    if linhas_sem_projeto > 0:
        print(f"⚠️  {linhas_sem_projeto} linhas sem projeto associado")

    # Preview
    print(f"\n📋 Preview dos primeiros 3 boletins:")
    for i, boletim in enumerate(boletins[:3], 1):
        print(f"   {i}. {boletim['numero']} - {boletim['socio']} {boletim['mes']}/{boletim['ano']} (€{boletim['valor_total']})")

    if len(boletins) > 3:
        print(f"   ... e mais {len(boletins) - 3} boletins")


def import_boletins():
    """Instruções para importar boletins e linhas"""

    if not BOLETINS_EXPORT.exists() or not LINHAS_EXPORT.exists():
        print(f"❌ Ficheiros de export não encontrados!")
        print(f"   Corre primeiro: python scripts/migrate_boletins.py export")
        sys.exit(1)

    print(f"📦 Ficheiros prontos para importação!")
    print(f"\n🚀 Comandos para executar NO SERVIDOR:\n")
    print(f"   # 1. Envia para o servidor")
    print(f"   scp {BOLETINS_EXPORT} {LINHAS_EXPORT} zumine@instante:~/zumine/amp/docker/app/agora_web/")
    print(f"\n   # 2. No servidor, importa BOLETINS primeiro, LINHAS depois")
    print(f"   ssh zumine@instante")
    print(f"   cd ~/zumine/amp/docker/app/agora_web")
    print(f"   ")
    print(f"   # Importa boletins (cabeçalho)")
    print(f"   docker cp boletins_export.json agora_web:/app/")
    print(f"   docker compose -f docker-compose.cloudflare.yml exec web python manage.py loaddata /app/boletins_export.json")
    print(f"   ")
    print(f"   # Importa linhas (com comando customizado)")
    print(f"   docker cp boletim_linhas_export.json agora_web:/app/")
    print(f"   docker compose -f docker-compose.cloudflare.yml exec web python manage.py import_boletim_linhas /app/boletim_linhas_export.json")


def migrate():
    """Executa export + import automaticamente"""
    print("🔄 Migração completa: Desktop → Web\n")
    export_boletins()
    print("\n" + "="*60 + "\n")
    import_boletins()


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in ['export', 'import', 'migrate']:
        print(__doc__)
        sys.exit(1)

    command = sys.argv[1]

    if command == 'export':
        export_boletins()
    elif command == 'import':
        import_boletins()
    elif command == 'migrate':
        migrate()


if __name__ == '__main__':
    main()
