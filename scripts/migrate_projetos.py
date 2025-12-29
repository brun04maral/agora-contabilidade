#!/usr/bin/env python3
"""
Script para migrar PROJETOS da app desktop (SQLite) para a web app (PostgreSQL/Docker)

IMPORTANTE: Este script precisa que os CLIENTES já tenham sido importados primeiro!
            Os projetos têm relações com clientes (foreign key).

Uso:
    python scripts/migrate_projetos.py export    # Exporta projetos do desktop para JSON
    python scripts/migrate_projetos.py import    # Importa JSON para web app via Docker
    python scripts/migrate_projetos.py migrate   # Faz export + import automaticamente
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
EXPORT_FILE = BASE_DIR / "projetos_export.json"


def export_projetos():
    """Exporta projetos da base SQLite desktop para JSON (formato Django fixtures)"""

    if not DESKTOP_DB.exists():
        print(f"❌ Base de dados desktop não encontrada: {DESKTOP_DB}")
        print(f"   Por favor verifica se o ficheiro existe.")
        sys.exit(1)

    print(f"📊 A ler projetos de: {DESKTOP_DB}")

    conn = sqlite3.connect(DESKTOP_DB)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Primeiro, cria um mapa de cliente_id -> numero
    cursor.execute("SELECT id, numero FROM clientes")
    clientes_map = {row["id"]: row["numero"] for row in cursor.fetchall()}

    # Lê todos os projetos
    cursor.execute("""
        SELECT
            id, numero, tipo, owner, cliente_id,
            data_inicio, data_fim, descricao,
            valor_sem_iva, data_faturacao, data_vencimento,
            estado, premio_bruno, premio_rafael,
            nota, created_at, updated_at
        FROM projetos
        ORDER BY id
    """)

    projetos = cursor.fetchall()
    conn.close()

    if not projetos:
        print("⚠️  Nenhum projeto encontrado na base desktop!")
        return

    # Converte para formato Django fixtures
    fixtures = []
    projetos_sem_cliente = []

    for projeto in projetos:
        cliente_numero = None
        if projeto["cliente_id"]:
            cliente_numero = clientes_map.get(projeto["cliente_id"])
            if not cliente_numero:
                projetos_sem_cliente.append(projeto["numero"])

        fixture = {
            "model": "core.projeto",
            "fields": {
                "numero": projeto["numero"],
                "tipo": projeto["tipo"] or "EMPRESA",
                "owner": projeto["owner"] or "BA",
                "cliente_numero": cliente_numero,  # Usamos isso para lookup depois
                "data_inicio": projeto["data_inicio"],
                "data_fim": projeto["data_fim"],
                "descricao": projeto["descricao"] or "",
                "valor_sem_iva": str(projeto["valor_sem_iva"] or 0),
                "data_faturacao": projeto["data_faturacao"],
                "data_vencimento": projeto["data_vencimento"],
                "estado": projeto["estado"] or "ATIVO",
                "premio_bruno": str(projeto["premio_bruno"] or 0) if projeto["premio_bruno"] else "0",
                "premio_rafael": str(projeto["premio_rafael"] or 0) if projeto["premio_rafael"] else "0",
                "nota": projeto["nota"] or "",
                "created_at": projeto["created_at"] or datetime.now().isoformat(),
                "updated_at": projeto["updated_at"] or datetime.now().isoformat(),
            }
        }
        fixtures.append(fixture)

    # Guarda JSON
    with open(EXPORT_FILE, 'w', encoding='utf-8') as f:
        json.dump(fixtures, f, ensure_ascii=False, indent=2)

    print(f"✅ {len(fixtures)} projetos exportados para: {EXPORT_FILE}")

    if projetos_sem_cliente:
        print(f"\n⚠️  {len(projetos_sem_cliente)} projetos sem cliente associado:")
        for num in projetos_sem_cliente[:5]:
            print(f"   - {num}")
        if len(projetos_sem_cliente) > 5:
            print(f"   ... e mais {len(projetos_sem_cliente) - 5}")

    print(f"\n📋 Preview dos primeiros 3:")
    for i, projeto in enumerate(projetos[:3], 1):
        cliente_num = clientes_map.get(projeto["cliente_id"], "SEM CLIENTE") if projeto["cliente_id"] else "SEM CLIENTE"
        print(f"   {i}. {projeto['numero']} - {projeto['descricao'][:40]} (Cliente: {cliente_num})")

    if len(projetos) > 3:
        print(f"   ... e mais {len(projetos) - 3} projetos")


def import_projetos():
    """Importa projetos do JSON para a web app via Docker"""

    if not EXPORT_FILE.exists():
        print(f"❌ Ficheiro de export não encontrado: {EXPORT_FILE}")
        print(f"   Corre primeiro: python scripts/migrate_projetos.py export")
        sys.exit(1)

    print(f"📦 Preparando importação de projetos...")
    print(f"\n⚠️  IMPORTANTE: Os CLIENTES precisam estar já importados!")
    print(f"   Caso contrário, os projetos ficarão sem cliente associado.\n")

    # Lê o JSON para processar as relações
    with open(EXPORT_FILE, 'r', encoding='utf-8') as f:
        fixtures = json.load(f)

    print(f"📊 Vou criar um script Python para fazer o import com lookups...")

    # Cria script de import customizado
    import_script = '''
import json
import sys
from django.core.management import setup_environ
from core.models import Projeto, Cliente

with open("/app/projetos_export.json", "r", encoding="utf-8") as f:
    fixtures = json.load(f)

projetos_importados = 0
projetos_sem_cliente = 0

for fixture in fixtures:
    fields = fixture["fields"]

    # Lookup do cliente pelo numero
    cliente = None
    if fields.get("cliente_numero"):
        try:
            cliente = Cliente.objects.get(numero=fields["cliente_numero"])
        except Cliente.DoesNotExist:
            projetos_sem_cliente += 1
            print(f"⚠️  Cliente {fields['cliente_numero']} não encontrado para projeto {fields['numero']}")

    # Remove cliente_numero dos fields (não é um campo do modelo)
    cliente_numero = fields.pop("cliente_numero", None)

    # Cria o projeto
    projeto = Projeto(
        cliente=cliente,
        **fields
    )
    projeto.save()
    projetos_importados += 1

print(f"✅ {projetos_importados} projetos importados!")
if projetos_sem_cliente > 0:
    print(f"⚠️  {projetos_sem_cliente} projetos ficaram sem cliente associado")
'''

    # Guarda o script
    import_script_path = BASE_DIR / "import_projetos_script.py"
    with open(import_script_path, 'w', encoding='utf-8') as f:
        f.write(import_script)

    print(f"✅ Script de import criado: {import_script_path}")
    print(f"\n📋 Instruções para importar NO SERVIDOR:\n")
    print(f"   # 1. Envia os ficheiros para o servidor")
    print(f"   scp {EXPORT_FILE} zumine@instante:~/zumine/amp/docker/app/agora_web/")
    print(f"   scp {import_script_path} zumine@instante:~/zumine/amp/docker/app/agora_web/")
    print(f"\n   # 2. No servidor, copia para o container e executa")
    print(f"   ssh zumine@instante")
    print(f"   cd ~/zumine/amp/docker/app/agora_web")
    print(f"   docker cp projetos_export.json agora_web:/app/")
    print(f"   docker cp import_projetos_script.py agora_web:/app/")
    print(f"   docker compose -f docker-compose.cloudflare.yml exec web python import_projetos_script.py")


def migrate():
    """Executa export + import automaticamente"""
    print("🔄 Migração completa: Desktop → Web\n")
    export_projetos()
    print("\n" + "="*60 + "\n")
    import_projetos()


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in ['export', 'import', 'migrate']:
        print(__doc__)
        sys.exit(1)

    command = sys.argv[1]

    if command == 'export':
        export_projetos()
    elif command == 'import':
        import_projetos()
    elif command == 'migrate':
        migrate()


if __name__ == '__main__':
    main()
