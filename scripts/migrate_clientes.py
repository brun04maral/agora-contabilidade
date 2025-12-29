#!/usr/bin/env python3
"""
Script para migrar CLIENTES da app desktop (SQLite) para a web app (PostgreSQL/Docker)

Uso:
    python scripts/migrate_clientes.py export    # Exporta clientes do desktop para JSON
    python scripts/migrate_clientes.py import    # Importa JSON para web app via Docker
    python scripts/migrate_clientes.py migrate   # Faz export + import automaticamente
"""

import sys
import json
import sqlite3
import subprocess
from pathlib import Path
from datetime import datetime

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DESKTOP_DB = BASE_DIR / "agora_media.db"  # Base de dados desktop
EXPORT_FILE = BASE_DIR / "clientes_export.json"


def export_clientes():
    """Exporta clientes da base SQLite desktop para JSON (formato Django fixtures)"""

    if not DESKTOP_DB.exists():
        print(f"❌ Base de dados desktop não encontrada: {DESKTOP_DB}")
        print(f"   Por favor verifica se o ficheiro existe.")
        sys.exit(1)

    print(f"📊 A ler clientes de: {DESKTOP_DB}")

    conn = sqlite3.connect(DESKTOP_DB)
    conn.row_factory = sqlite3.Row  # Permite aceder às colunas por nome
    cursor = conn.cursor()

    # Lê todos os clientes
    cursor.execute("""
        SELECT
            id, numero, nome, nome_formal, nif, morada, pais,
            contacto, email, angariacao, nota,
            created_at, updated_at
        FROM clientes
        ORDER BY id
    """)

    clientes = cursor.fetchall()
    conn.close()

    if not clientes:
        print("⚠️  Nenhum cliente encontrado na base desktop!")
        return

    # Converte para formato Django fixtures
    fixtures = []
    for cliente in clientes:
        # Django não usa o id do SQLite, vai autogenerar
        fixture = {
            "model": "core.cliente",
            "fields": {
                "numero": cliente["numero"],
                "nome": cliente["nome"],
                "nome_formal": cliente["nome_formal"],
                "nif": cliente["nif"] or "",
                "morada": cliente["morada"] or "",
                "pais": cliente["pais"] or "Portugal",
                "contacto": cliente["contacto"] or "",
                "email": cliente["email"] or "",
                "angariacao": cliente["angariacao"] or "",
                "nota": cliente["nota"] or "",
                # Preserva timestamps originais ou usa data atual
                "created_at": cliente["created_at"] or datetime.now().isoformat(),
                "updated_at": cliente["updated_at"] or datetime.now().isoformat(),
            }
        }
        fixtures.append(fixture)

    # Guarda JSON
    with open(EXPORT_FILE, 'w', encoding='utf-8') as f:
        json.dump(fixtures, f, ensure_ascii=False, indent=2)

    print(f"✅ {len(fixtures)} clientes exportados para: {EXPORT_FILE}")
    print(f"\n📋 Preview dos primeiros 3:")
    for i, cliente in enumerate(clientes[:3], 1):
        print(f"   {i}. {cliente['numero']} - {cliente['nome']}")

    if len(clientes) > 3:
        print(f"   ... e mais {len(clientes) - 3} clientes")


def import_clientes():
    """Importa clientes do JSON para a web app via Docker"""

    if not EXPORT_FILE.exists():
        print(f"❌ Ficheiro de export não encontrado: {EXPORT_FILE}")
        print(f"   Corre primeiro: python scripts/migrate_clientes.py export")
        sys.exit(1)

    print(f"📦 A importar clientes para a web app via Docker...")

    # Copia fixture para dentro do container
    web_dir = BASE_DIR / "agora_web"

    # Verifica se estamos no contexto correto
    if not web_dir.exists():
        print(f"❌ Diretório agora_web não encontrado: {web_dir}")
        sys.exit(1)

    # Copia fixture para dentro do projeto web (será mapeado no container)
    import shutil
    fixture_dest = web_dir / "clientes_export.json"
    shutil.copy(EXPORT_FILE, fixture_dest)
    print(f"✅ Fixture copiado para: {fixture_dest}")

    # Comando para importar no container
    # IMPORTANTE: Este comando assume que estás no servidor com Docker
    cmd = [
        "docker", "compose", "-f", "docker-compose.cloudflare.yml",
        "exec", "web",
        "python", "manage.py", "loaddata", "clientes_export.json"
    ]

    print(f"\n🚀 A executar no Docker:")
    print(f"   cd ~/zumine/amp/docker/app/agora_web")
    print(f"   {' '.join(cmd[2:])}")  # Mostra comando sem 'docker compose'

    print(f"\n⚠️  ATENÇÃO: Este script deve ser executado NO SERVIDOR via SSH!")
    print(f"   Ou corre manualmente os comandos abaixo:\n")
    print(f"   # 1. Copia fixture para o servidor")
    print(f"   scp {EXPORT_FILE} teu-usuario@servidor:~/zumine/amp/docker/app/agora_web/")
    print(f"\n   # 2. No servidor, importa os dados")
    print(f"   ssh teu-usuario@servidor")
    print(f"   cd ~/zumine/amp/docker/app/agora_web")
    print(f"   docker compose -f docker-compose.cloudflare.yml exec web python manage.py loaddata clientes_export.json")


def migrate():
    """Executa export + import automaticamente"""
    print("🔄 Migração completa: Desktop → Web\n")
    export_clientes()
    print("\n" + "="*60 + "\n")
    import_clientes()


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in ['export', 'import', 'migrate']:
        print(__doc__)
        sys.exit(1)

    command = sys.argv[1]

    if command == 'export':
        export_clientes()
    elif command == 'import':
        import_clientes()
    elif command == 'migrate':
        migrate()


if __name__ == '__main__':
    main()
