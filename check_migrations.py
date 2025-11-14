#!/usr/bin/env python3
"""
Script para verificar migrations pendentes na DB local
"""
import sqlite3
import os
from pathlib import Path

def check_column_exists(cursor, table, column):
    """Verifica se uma coluna existe numa tabela"""
    cursor.execute(f"PRAGMA table_info({table})")
    columns = [row[1] for row in cursor.fetchall()]
    return column in columns

def check_table_exists(cursor, table):
    """Verifica se uma tabela existe"""
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
    return cursor.fetchone() is not None

# Path para a DB (assumindo que estás na raiz do projeto)
db_path = "agora_media.db"

if not os.path.exists(db_path):
    print("❌ Base de dados não encontrada: agora_media.db")
    print("   Certifica-te que estás no diretório do projeto!")
    exit(1)

print("=" * 70)
print("🔍 VERIFICAÇÃO DE MIGRATIONS PENDENTES")
print("=" * 70)
print(f"📁 Base de dados: {db_path}")
print()

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Lista de verificações por migration
migrations = {
    "001": [
        ("tabela", "users", "001_create_users_table")
    ],
    "002": [
        ("tabela", "clientes", "002_create_main_tables"),
        ("tabela", "fornecedores", "002_create_main_tables"),
        ("tabela", "projetos", "002_create_main_tables"),
        ("tabela", "despesas", "002_create_main_tables"),
        ("tabela", "boletins", "002_create_main_tables"),
    ],
    "003": [
        ("coluna", "fornecedores", "pais", "003_add_pais_to_fornecedor")
    ],
    "004": [
        # Esta migration adiciona valor ANULADO ao enum, difícil de verificar
        ("skip", None, None, "004_add_anulado_estado (verificação manual)")
    ],
    "005": [
        # Esta migration renomeia enum, difícil de verificar
        ("skip", None, None, "005_rename_ativo_to_pendente (verificação manual)")
    ],
    "006": [
        ("tabela", "equipamento", "006_add_equipamento_fields")
    ],
    "007": [
        ("tabela", "orcamentos", "007_create_orcamento_tables"),
        ("tabela", "orcamento_secoes", "007_create_orcamento_tables"),
        ("tabela", "orcamento_itens", "007_create_orcamento_tables"),
        ("tabela", "orcamento_reparticoes", "007_create_orcamento_tables"),
    ],
    "008": [
        # Renomeia coluna, difícil verificar
        ("skip", None, None, "008_rename_orcamento_tipo (verificação manual)")
    ],
    "009": [
        ("coluna", "equipamento", "aluguer_mensal", "009_create_equipamento_aluguer")
    ],
    "010": [
        ("coluna", "orcamentos", "tem_versao_cliente", "010_refactor_orcamento_unico"),
        ("coluna", "orcamentos", "titulo_cliente", "010_refactor_orcamento_unico"),
    ],
    "011": [
        # Remove tabelas antigas, adiciona novas colunas
        ("coluna", "orcamento_secoes", "proposta_cliente", "011_create_proposta_tables"),
    ],
    "012": [
        ("coluna", "fornecedores", "website", "012_add_website_to_fornecedor")
    ],
    "013": [
        ("coluna", "despesas", "despesa_template_id", "013_add_recorrencia_to_despesas")
    ],
    "014": [
        ("tabela", "despesa_templates", "014_create_despesa_templates")
    ],
    "015": [
        # Remove colunas is_recorrente e dia_recorrencia (difícil verificar que foram removidas)
        ("skip", None, None, "015_remove_recorrencia_from_despesas (verificação manual)")
    ],
    "016": [
        ("tabela", "valores_referencia_anual", "016_create_valores_referencia_anual")
    ],
    "017": [
        ("tabela", "boletim_linhas", "017_create_boletim_linhas")
    ],
    "018": [
        ("tabela", "boletim_templates", "018_create_boletim_templates")
    ],
    "019": [
        ("coluna", "boletins", "mes", "019_expand_boletins"),
        ("coluna", "boletins", "ano", "019_expand_boletins"),
        ("coluna", "boletins", "val_dia_nacional", "019_expand_boletins"),
    ],
}

pendentes = []
aplicadas = []

for migration_num, checks in migrations.items():
    for check in checks:
        if check[0] == "skip":
            # Verificação manual necessária
            aplicadas.append(f"  {migration_num}: {check[3]} (⚠️  verificação manual)")
            continue

        # Unpack correto: tabelas têm 3 elementos, colunas têm 4
        if len(check) == 3:
            check_type, target, migration_file = check
            field = None
        else:
            check_type, target, field, migration_file = check

        if check_type == "tabela":
            if check_table_exists(cursor, target):
                aplicadas.append(f"  {migration_num}: ✅ Tabela '{target}' existe")
            else:
                pendentes.append(f"  {migration_num}: ❌ Tabela '{target}' NÃO existe → {migration_file}")

        elif check_type == "coluna":
            if check_table_exists(cursor, target):
                if check_column_exists(cursor, target, field):
                    aplicadas.append(f"  {migration_num}: ✅ Coluna '{target}.{field}' existe")
                else:
                    pendentes.append(f"  {migration_num}: ❌ Coluna '{target}.{field}' NÃO existe → {migration_file}")
            else:
                pendentes.append(f"  {migration_num}: ❌ Tabela '{target}' não existe (coluna '{field}' não pode ser verificada)")

conn.close()

# Mostrar resultados
print("✅ MIGRATIONS APLICADAS:")
print()
for item in aplicadas:
    print(item)

if pendentes:
    print()
    print("=" * 70)
    print("❌ MIGRATIONS PENDENTES (PRECISAS EXECUTAR):")
    print("=" * 70)
    print()
    for item in pendentes:
        print(item)

    print()
    print("=" * 70)
    print("🔧 COMO EXECUTAR:")
    print("=" * 70)
    print()

    # Identificar migration mais baixa pendente
    pendente_nums = []
    for item in pendentes:
        num = item.split(":")[0].strip().split()[0]
        pendente_nums.append(int(num))

    primeira_pendente = min(pendente_nums)

    # Verificar quais migrations estão pendentes
    tem_009_ou_010 = 9 in pendente_nums or 10 in pendente_nums
    tem_011 = 11 in pendente_nums

    print(f"Executar na seguinte ordem:")
    print()

    if tem_009_ou_010:
        print("  1️⃣ python3 scripts/run_migrations_009_010.py")
        if tem_011:
            print("  2️⃣ python3 scripts/run_migration_011.py")
    elif tem_011:
        print("  python3 scripts/run_migration_011.py")
    elif primeira_pendente == 12:
        print("  python3 run_migration_012.py")
        print("  python3 run_migration_013.py")
        print("  python3 run_migration_014.py")
        print("  python3 run_migration_015.py")
        print("  python3 run_migrations_016_019.py")
    elif primeira_pendente >= 16:
        print("  python3 run_migrations_016_019.py")

    print()
else:
    print()
    print("=" * 70)
    print("🎉 Todas as migrations estão aplicadas!")
    print("=" * 70)
