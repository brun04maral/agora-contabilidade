#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para limpar sessão e verificar configuração
"""
import os
from pathlib import Path
from dotenv import load_dotenv

print("🔧 Limpando sessão e verificando configuração...\n")

# Limpar sessão
session_file = Path.home() / '.agora_contabilidade' / 'session.json'
if session_file.exists():
    session_file.unlink()
    print("✅ Sessão antiga removida")
else:
    print("ℹ️  Nenhuma sessão encontrada")

# Verificar .env
load_dotenv()
database_url = os.getenv("DATABASE_URL")

print(f"\n📁 Configuração atual:")
print(f"   DATABASE_URL: {database_url}")

if database_url and "sqlite" in database_url:
    print("✅ Configurado para usar SQLite (correto)")
elif database_url and "postgresql" in database_url:
    print("⚠️  Configurado para usar PostgreSQL - altere para SQLite no .env")
    print("   DATABASE_URL=sqlite:///./agora_media.db")
else:
    print("⚠️  DATABASE_URL não configurado")

# Verificar base de dados
db_file = Path("./agora_media.db")
if db_file.exists():
    print(f"\n✅ Base de dados existe: {db_file.absolute()}")
    print("   Tamanho:", db_file.stat().st_size, "bytes")
else:
    print(f"\n⚠️  Base de dados não existe!")
    print("   Execute: python3 setup_database.py")

print("\n✨ Verificação completa! Agora execute: python3 main.py")
