#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de correção: Migrar estados antigos de projetos para novos valores

Execução:
    python3 fix_estados_projetos.py
"""
import os
import sys
from sqlalchemy import create_engine, text

# Criar engine
project_root = os.path.dirname(__file__)
database_url = f"sqlite:///{os.path.join(project_root, 'agora_media.db')}"

print("╔" + "="*58 + "╗")
print("║  CORREÇÃO: Migrar Estados de Projetos                     ║")
print("╚" + "="*58 + "╝")
print()

engine = create_engine(database_url)

with engine.connect() as conn:
    # Verificar estados atuais
    print("🔍 Verificando estados atuais na base de dados...")
    result = conn.execute(text("SELECT DISTINCT estado FROM projetos ORDER BY estado"))
    estados_atuais = [row[0] for row in result.fetchall()]

    print(f"   Estados encontrados: {estados_atuais}")
    print()

    # Mapear todos os estados antigos para novos (case-insensitive)
    migrations = [
        ("ativo", "ATIVO"),
        ("ATIVO", "ATIVO"),  # Já está correto
        ("nao_faturado", "ATIVO"),
        ("NAO_FATURADO", "ATIVO"),
        ("Não Faturado", "ATIVO"),

        ("concluido", "FINALIZADO"),
        ("CONCLUIDO", "FINALIZADO"),
        ("faturado", "FINALIZADO"),
        ("FATURADO", "FINALIZADO"),
        ("Faturado", "FINALIZADO"),

        ("recebido", "PAGO"),
        ("RECEBIDO", "PAGO"),
        ("Recebido", "PAGO"),
        ("PAGO", "PAGO"),  # Já está correto

        ("cancelado", "ANULADO"),
        ("CANCELADO", "ANULADO"),
        ("anulado", "ANULADO"),
        ("ANULADO", "ANULADO"),  # Já está correto
    ]

    total_migrados = 0

    for estado_antigo, estado_novo in migrations:
        # Verificar quantos registos têm este estado
        result = conn.execute(
            text("SELECT COUNT(*) FROM projetos WHERE estado = :estado"),
            {"estado": estado_antigo}
        )
        count = result.fetchone()[0]

        if count > 0:
            print(f"   Migrando {count} projeto(s): '{estado_antigo}' → '{estado_novo}'")

            # Migrar
            conn.execute(
                text("UPDATE projetos SET estado = :novo WHERE estado = :antigo"),
                {"novo": estado_novo, "antigo": estado_antigo}
            )
            conn.commit()
            total_migrados += count

    print()
    print("="*60)

    if total_migrados > 0:
        print(f"✅ Migração concluída: {total_migrados} projeto(s) atualizado(s)")
    else:
        print("✅ Nenhuma migração necessária (todos os estados já estão corretos)")

    # Verificar estados finais
    print()
    print("📊 Estados após migração:")
    result = conn.execute(text("""
        SELECT estado, COUNT(*) as count
        FROM projetos
        GROUP BY estado
        ORDER BY estado
    """))

    for row in result.fetchall():
        print(f"   • {row[0]}: {row[1]} projeto(s)")

    print()
    print("="*60)
    print("✨ Script concluído com sucesso!")
    print("   A aplicação pode agora ser executada normalmente.")
    print("="*60)
