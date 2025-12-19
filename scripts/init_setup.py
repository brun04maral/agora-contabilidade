#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de inicialização completa - resolve problemas de configuração
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv, set_key, find_dotenv

print("=" * 60)
print("🚀 INICIALIZAÇÃO - Agora Media Contabilidade")
print("=" * 60)

# 1. Limpar sessão antiga
print("\n[1/5] Limpando sessão antiga...")
session_file = Path.home() / '.agora_contabilidade' / 'session.json'
if session_file.exists():
    session_file.unlink()
    print("      ✅ Sessão removida")
else:
    print("      ℹ️  Nenhuma sessão encontrada")

# 2. Verificar/criar .env
print("\n[2/5] Verificando ficheiro .env...")
env_file = find_dotenv()

if not env_file:
    env_file = Path(".env")
    print(f"      ⚠️  Ficheiro .env não encontrado")
    print(f"      Criando novo ficheiro .env...")

    with open(env_file, 'w') as f:
        f.write("""# Database Configuration - USE SQLITE LOCALLY
DATABASE_URL=sqlite:///./agora_media.db

# Application Settings
APP_NAME=Agora Media Contabilidade
DEBUG=True

# JWT Secret (para autenticação)
JWT_SECRET_KEY=agora-media-secret-key-change-in-production
SESSION_EXPIRY_HOURS=24

# Sócios
SOCIO_1_NOME=Bruno Amaral
SOCIO_2_NOME=Rafael Reigota
""")
    print("      ✅ Ficheiro .env criado")
else:
    print(f"      ✅ Ficheiro .env encontrado: {env_file}")

# 3. Forçar SQLite
print("\n[3/5] Configurando base de dados para SQLite...")
load_dotenv(override=True)

# Verificar se está a usar PostgreSQL
database_url = os.getenv("DATABASE_URL", "")

if "postgresql" in database_url or "postgres" in database_url:
    print("      ⚠️  Detectado PostgreSQL - alterando para SQLite...")
    set_key(env_file, "DATABASE_URL", "sqlite:///./agora_media.db")
    os.environ["DATABASE_URL"] = "sqlite:///./agora_media.db"
    print("      ✅ Configuração alterada para SQLite")
else:
    print("      ✅ Já configurado para SQLite")

# Recarregar .env
load_dotenv(override=True)
database_url = os.getenv("DATABASE_URL")
print(f"      DATABASE_URL: {database_url}")

# 4. Verificar/criar base de dados
print("\n[4/5] Verificando base de dados...")
db_file = Path("./agora_media.db")

if not db_file.exists():
    print("      ⚠️  Base de dados não existe - criando...")

    # Importar e executar setup
    try:
        from database.models.base import Base
        from database.models import *  # Importar todos os modelos
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker

        # Criar engine
        engine = create_engine(database_url)

        # Criar todas as tabelas
        Base.metadata.create_all(engine)
        print("      ✅ Tabelas criadas")

        # Criar utilizadores
        Session = sessionmaker(bind=engine)
        session = Session()

        from logic.auth import AuthManager
        auth = AuthManager(session)

        # Criar Bruno
        success, user = auth.create_user(
            email="bruno@agoramedia.pt",
            password="bruno123",
            name="Bruno Amaral",
            role="admin"
        )
        if success:
            print("      ✅ Utilizador Bruno criado")

        # Criar Rafael
        success, user = auth.create_user(
            email="rafael@agoramedia.pt",
            password="rafael123",
            name="Rafael Reigota",
            role="admin"
        )
        if success:
            print("      ✅ Utilizador Rafael criado")

        session.close()

    except Exception as e:
        print(f"      ❌ Erro ao criar base de dados: {e}")
        print("      Execute manualmente: python3 setup_database.py")
        sys.exit(1)
else:
    print(f"      ✅ Base de dados existe")
    print(f"         Tamanho: {db_file.stat().st_size:,} bytes")

# 5. Teste de conexão
print("\n[5/5] Testando conexão...")
try:
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    engine = create_engine(database_url)
    Session = sessionmaker(bind=engine)
    session = Session()

    # Tentar contar utilizadores
    from database.models.user import User
    count = session.query(User).count()

    print(f"      ✅ Conexão OK - {count} utilizador(es) encontrado(s)")

    # Listar utilizadores
    users = session.query(User).all()
    if users:
        print("\n      📋 Utilizadores disponíveis:")
        for user in users:
            print(f"         • {user.email} ({user.name})")

    session.close()

except Exception as e:
    print(f"      ❌ Erro na conexão: {e}")
    sys.exit(1)

# Sucesso!
print("\n" + "=" * 60)
print("✅ CONFIGURAÇÃO COMPLETA!")
print("=" * 60)
print("\n📋 Credenciais de login:")
print("   • Bruno: bruno@agoramedia.pt / bruno123")
print("   • Rafael: rafael@agoramedia.pt / rafael123")
print("\n🚀 Execute agora: python3 main.py")
print("=" * 60 + "\n")
