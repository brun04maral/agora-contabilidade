#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Setup completo - Cria base de dados do zero
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.models.base import Base

print("="*80)
print("🚀 SETUP COMPLETO - Criar Base de Dados do Zero")
print("="*80)

# 1. Remove base de dados antiga se existir
db_path = "./agora_media.db"
if os.path.exists(db_path):
    print(f"\n[1/3] Removendo base de dados antiga...")
    os.remove(db_path)
    print("      ✅ Removida")
else:
    print(f"\n[1/3] Base de dados não existe (tudo OK)")

# 2. Criar todas as tabelas
print("\n[2/3] Criando todas as tabelas...")
from dotenv import load_dotenv
load_dotenv()

database_url = os.getenv("DATABASE_URL", "sqlite:///./agora_media.db")
engine = create_engine(database_url)

# Import all models to register them
from database.models.user import User
from database.models.cliente import Cliente
from database.models.fornecedor import Fornecedor
from database.models.projeto import Projeto
from database.models.despesa import Despesa
from database.models.boletim import Boletim
from database.models.equipamento import Equipamento

# Create all tables
Base.metadata.create_all(engine)
print("      ✅ Todas as tabelas criadas!")

# 3. Criar utilizador admin
print("\n[3/3] Criando utilizador admin...")
Session = sessionmaker(bind=engine)
session = Session()

from database.models import UserRole
import bcrypt

# Check if user already exists
existing_user = session.query(User).filter(User.email == "admin@agoramedia.pt").first()

if existing_user:
    print("      ℹ️  Utilizador admin já existe")
else:
    # Hash password
    password = "admin123"
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    # Create admin user
    admin = User(
        email="admin@agoramedia.pt",
        password_hash=password_hash,
        name="Administrador",
        role=UserRole.ADMIN,
        is_active=True
    )

    session.add(admin)
    session.commit()
    print("      ✅ Utilizador criado!")
    print("         Email: admin@agoramedia.pt")
    print("         Password: admin123")

session.close()

print("\n" + "="*80)
print("✅ SETUP COMPLETO!")
print("="*80)
print("\nPróximos passos:")
print("  1. Execute: python3 import_from_excel.py")
print("  2. Execute: python3 main.py")
print("="*80)
