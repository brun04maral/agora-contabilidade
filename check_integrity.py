#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de verificação de integridade do sistema
Executa antes de main.py para detectar problemas
"""
import sys
import os
from pathlib import Path

print("=" * 70)
print("🔍 VERIFICAÇÃO DE INTEGRIDADE - Agora Media Contabilidade")
print("=" * 70)

errors = []
warnings = []

# 1. Verificar Python version
print("\n[1/7] Verificando versão do Python...")
if sys.version_info < (3, 11):
    warnings.append(f"Python {sys.version_info.major}.{sys.version_info.minor} detectado. Recomendado: Python 3.11+")
    print(f"      ⚠️  Python {sys.version_info.major}.{sys.version_info.minor} (recomendado 3.11+)")
else:
    print(f"      ✅ Python {sys.version_info.major}.{sys.version_info.minor}")

# 2. Verificar dependências
print("\n[2/7] Verificando dependências...")
required_packages = {
    'customtkinter': 'customtkinter',
    'sqlalchemy': 'SQLAlchemy',
    'dotenv': 'python-dotenv',
    'jwt': 'PyJWT',
    'bcrypt': 'bcrypt'
}

for module, package in required_packages.items():
    try:
        __import__(module)
        print(f"      ✅ {package}")
    except ImportError:
        errors.append(f"Pacote {package} não instalado")
        print(f"      ❌ {package} - execute: pip install {package}")

# 3. Verificar ficheiro .env
print("\n[3/7] Verificando configuração (.env)...")
env_file = Path(".env")
if not env_file.exists():
    errors.append("Ficheiro .env não encontrado")
    print("      ❌ .env não existe")
else:
    print("      ✅ .env existe")

    # Verificar DATABASE_URL
    from dotenv import load_dotenv
    load_dotenv()
    db_url = os.getenv("DATABASE_URL")

    if not db_url:
        errors.append("DATABASE_URL não configurado no .env")
        print("      ❌ DATABASE_URL não configurado")
    elif "postgresql" in db_url or "postgres" in db_url:
        warnings.append("DATABASE_URL aponta para PostgreSQL (recomendado SQLite local)")
        print("      ⚠️  Usando PostgreSQL (recomendado SQLite)")
    else:
        print(f"      ✅ DATABASE_URL configurado: {db_url[:30]}...")

# 4. Verificar base de dados
print("\n[4/7] Verificando base de dados...")
db_file = Path("agora_media.db")
if db_file.exists():
    size = db_file.stat().st_size
    print(f"      ✅ Base de dados existe ({size:,} bytes)")

    # Testar conexão
    try:
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker

        engine = create_engine(os.getenv("DATABASE_URL", "sqlite:///./agora_media.db"))
        Session = sessionmaker(bind=engine)
        session = Session()

        from database.models.user import User
        user_count = session.query(User).count()

        if user_count == 0:
            warnings.append("Base de dados sem utilizadores")
            print(f"      ⚠️  Nenhum utilizador encontrado - execute: python3 setup_database.py")
        else:
            print(f"      ✅ {user_count} utilizador(es) na base de dados")

        session.close()

    except Exception as e:
        errors.append(f"Erro ao conectar à base de dados: {e}")
        print(f"      ❌ Erro de conexão: {str(e)[:50]}...")
else:
    warnings.append("Base de dados não existe")
    print("      ⚠️  Base de dados não existe - execute: python3 setup_database.py")

# 5. Verificar sintaxe dos ficheiros principais
print("\n[5/7] Verificando sintaxe de ficheiros Python...")
import py_compile

files_to_check = [
    'main.py',
    'ui/main_window.py',
    'ui/screens/dashboard.py',
    'ui/screens/saldos.py',
    'ui/screens/projetos.py',
    'ui/screens/despesas.py',
    'ui/screens/boletins.py',
    'ui/screens/clientes.py',
    'ui/screens/fornecedores.py',
    'logic/saldos.py',
    'logic/auth.py'
]

syntax_errors = 0
for file in files_to_check:
    if not Path(file).exists():
        warnings.append(f"Ficheiro {file} não encontrado")
        continue

    try:
        py_compile.compile(file, doraise=True)
    except py_compile.PyCompileError as e:
        syntax_errors += 1
        errors.append(f"Erro de sintaxe em {file}")
        print(f"      ❌ {file}")

if syntax_errors == 0:
    print(f"      ✅ {len(files_to_check)} ficheiros verificados")
else:
    print(f"      ❌ {syntax_errors} ficheiro(s) com erros de sintaxe")

# 6. Verificar imports dos modelos
print("\n[6/7] Verificando modelos de base de dados...")
try:
    from database.models import (
        User, Cliente, Fornecedor, Projeto, Despesa, Boletim,
        TipoProjeto, EstadoProjeto, TipoDespesa, EstadoDespesa,
        Socio, EstadoBoletim, EstatutoFornecedor
    )
    print("      ✅ Todos os modelos importados com sucesso")

    # Verificar enums
    assert hasattr(EstadoDespesa, 'ATIVO'), "EstadoDespesa.ATIVO não existe"
    assert hasattr(EstadoDespesa, 'VENCIDO'), "EstadoDespesa.VENCIDO não existe"
    assert hasattr(EstadoDespesa, 'PAGO'), "EstadoDespesa.PAGO não existe"
    assert hasattr(EstadoBoletim, 'PENDENTE'), "EstadoBoletim.PENDENTE não existe"
    assert hasattr(EstadoBoletim, 'PAGO'), "EstadoBoletim.PAGO não existe"
    print("      ✅ Todos os enums verificados")

except Exception as e:
    errors.append(f"Erro ao importar modelos: {e}")
    print(f"      ❌ Erro ao importar: {str(e)[:50]}...")

# 7. Verificar estrutura de diretórios
print("\n[7/7] Verificando estrutura de diretórios...")
required_dirs = [
    'ui', 'ui/screens', 'ui/components',
    'logic', 'database', 'database/models', 'utils'
]

missing_dirs = []
for dir_path in required_dirs:
    if not Path(dir_path).exists():
        missing_dirs.append(dir_path)

if missing_dirs:
    errors.append(f"{len(missing_dirs)} diretório(s) em falta")
    for d in missing_dirs:
        print(f"      ❌ {d}/")
else:
    print(f"      ✅ Todos os {len(required_dirs)} diretórios existem")

# RESULTADO FINAL
print("\n" + "=" * 70)

if errors:
    print("❌ VERIFICAÇÃO FALHOU")
    print("=" * 70)
    print(f"\n🔴 {len(errors)} erro(s) encontrado(s):")
    for i, error in enumerate(errors, 1):
        print(f"   {i}. {error}")

    if warnings:
        print(f"\n⚠️  {len(warnings)} aviso(s):")
        for i, warning in enumerate(warnings, 1):
            print(f"   {i}. {warning}")

    print("\n" + "=" * 70)
    sys.exit(1)

elif warnings:
    print("⚠️  VERIFICAÇÃO COM AVISOS")
    print("=" * 70)
    print(f"\n⚠️  {len(warnings)} aviso(s) encontrado(s):")
    for i, warning in enumerate(warnings, 1):
        print(f"   {i}. {warning}")

    print("\n✅ O sistema pode funcionar, mas recomenda-se resolver os avisos.")
    print("\n💡 Sugestões:")
    if any("utilizador" in w for w in warnings):
        print("   • Execute: python3 setup_database.py")
    if any("PostgreSQL" in w for w in warnings):
        print("   • Execute: python3 init_setup.py")

    print("\n" + "=" * 70)

else:
    print("✅ VERIFICAÇÃO COMPLETA - TUDO OK!")
    print("=" * 70)
    print("\n✅ Sistema pronto para executar!")
    print("\n🚀 Execute: python3 main.py")
    print("\n📋 Credenciais de login:")
    print("   • Bruno: bruno@agoramedia.pt / bruno123")
    print("   • Rafael: rafael@agoramedia.pt / rafael123")
    print("\n" + "=" * 70)
