#!/usr/bin/env python3
"""
Script para migrar FORNECEDORES da app desktop (SQLite) para a web app (PostgreSQL/Docker)

Uso:
    python scripts/migrate_fornecedores.py export    # Exporta fornecedores do desktop para JSON
    python scripts/migrate_fornecedores.py import    # Importa JSON para web app via Docker
    python scripts/migrate_fornecedores.py migrate   # Faz export + import automaticamente
"""

import sys
import json
import sqlite3
from pathlib import Path
from datetime import datetime

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DESKTOP_DB = BASE_DIR / "agora_media.db"  # Base de dados desktop
EXPORT_FILE = BASE_DIR / "fornecedores_export.json"


def export_fornecedores():
    """Exporta fornecedores da base SQLite desktop para JSON (formato Django fixtures)"""

    if not DESKTOP_DB.exists():
        print(f"❌ Base de dados desktop não encontrada: {DESKTOP_DB}")
        print(f"   Por favor verifica se o ficheiro existe.")
        sys.exit(1)

    print(f"📊 A ler fornecedores de: {DESKTOP_DB}")

    conn = sqlite3.connect(DESKTOP_DB)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Lê todos os fornecedores
    cursor.execute("""
        SELECT
            id, numero, nome, estatuto, area, funcao,
            classificacao, validade_seguro_trabalho,
            nif, iban, morada, pais, contacto, email, website,
            nota, created_at, updated_at
        FROM fornecedores
        ORDER BY id
    """)

    fornecedores = cursor.fetchall()
    conn.close()

    if not fornecedores:
        print("⚠️  Nenhum fornecedor encontrado na base desktop!")
        return

    # Converte para formato Django fixtures
    fixtures = []
    for fornecedor in fornecedores:
        fixture = {
            "model": "core.fornecedor",
            "fields": {
                "numero": fornecedor["numero"],
                "nome": fornecedor["nome"],
                "estatuto": fornecedor["estatuto"] or "FREELANCER",
                "area": fornecedor["area"] or "",
                "funcao": fornecedor["funcao"] or "",
                "classificacao": fornecedor["classificacao"],
                "validade_seguro_trabalho": fornecedor["validade_seguro_trabalho"],
                "nif": fornecedor["nif"] or "",
                "iban": fornecedor["iban"] or "",
                "morada": fornecedor["morada"] or "",
                "pais": fornecedor["pais"] or "Portugal",
                "contacto": fornecedor["contacto"] or "",
                "email": fornecedor["email"] or "",
                "website": fornecedor["website"] or "",
                "nota": fornecedor["nota"] or "",
                "created_at": fornecedor["created_at"] or datetime.now().isoformat(),
                "updated_at": fornecedor["updated_at"] or datetime.now().isoformat(),
            }
        }
        fixtures.append(fixture)

    # Guarda JSON
    with open(EXPORT_FILE, 'w', encoding='utf-8') as f:
        json.dump(fixtures, f, ensure_ascii=False, indent=2)

    print(f"✅ {len(fixtures)} fornecedores exportados para: {EXPORT_FILE}")
    print(f"\n📋 Preview dos primeiros 3:")
    for i, fornecedor in enumerate(fornecedores[:3], 1):
        print(f"   {i}. {fornecedor['numero']} - {fornecedor['nome']} ({fornecedor['estatuto']})")

    if len(fornecedores) > 3:
        print(f"   ... e mais {len(fornecedores) - 3} fornecedores")


def import_fornecedores():
    """Importa fornecedores do JSON para a web app via Docker"""

    if not EXPORT_FILE.exists():
        print(f"❌ Ficheiro de export não encontrado: {EXPORT_FILE}")
        print(f"   Corre primeiro: python scripts/migrate_fornecedores.py export")
        sys.exit(1)

    print(f"📦 A importar fornecedores para a web app via Docker...")

    web_dir = BASE_DIR / "agora_web"

    if not web_dir.exists():
        print(f"❌ Diretório agora_web não encontrado: {web_dir}")
        sys.exit(1)

    import shutil
    fixture_dest = web_dir / "fornecedores_export.json"
    shutil.copy(EXPORT_FILE, fixture_dest)
    print(f"✅ Fixture copiado para: {fixture_dest}")

    print(f"\n🚀 Comandos para executar NO SERVIDOR:\n")
    print(f"   # 1. Envia para o servidor")
    print(f"   scp {EXPORT_FILE} zumine@instante:~/zumine/amp/docker/app/agora_web/")
    print(f"\n   # 2. No servidor, importa")
    print(f"   ssh zumine@instante")
    print(f"   cd ~/zumine/amp/docker/app/agora_web")
    print(f"   docker cp fornecedores_export.json agora_web:/app/")
    print(f"   docker compose -f docker-compose.cloudflare.yml exec web python manage.py loaddata /app/fornecedores_export.json")


def migrate():
    """Executa export + import automaticamente"""
    print("🔄 Migração completa: Desktop → Web\n")
    export_fornecedores()
    print("\n" + "="*60 + "\n")
    import_fornecedores()


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in ['export', 'import', 'migrate']:
        print(__doc__)
        sys.exit(1)

    command = sys.argv[1]

    if command == 'export':
        export_fornecedores()
    elif command == 'import':
        import_fornecedores()
    elif command == 'migrate':
        migrate()


if __name__ == '__main__':
    main()
