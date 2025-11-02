# -*- coding: utf-8 -*-
"""
Script para verificar prémios na base de dados
"""
from dotenv import load_dotenv
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.models import Projeto

load_dotenv()

# Get database URL
database_url = os.getenv("DATABASE_URL", "sqlite:///./agora_media.db")
engine = create_engine(database_url)
Session = sessionmaker(bind=engine)
db_session = Session()

try:
    print("=" * 80)
    print("PRÉMIOS ATUAIS NA BASE DE DADOS")
    print("=" * 80)

    projetos = db_session.query(Projeto).order_by(Projeto.numero).all()

    print(f"\n{'Nº Projeto':<12} {'Descrição':<40} {'Prémio Bruno':<15} {'Prémio Rafael':<15}")
    print("-" * 80)

    total_bruno = 0
    total_rafael = 0

    for proj in projetos:
        premio_bruno = float(proj.premio_bruno) if proj.premio_bruno else 0
        premio_rafael = float(proj.premio_rafael) if proj.premio_rafael else 0

        total_bruno += premio_bruno
        total_rafael += premio_rafael

        print(f"{proj.numero:<12} {proj.descricao[:40]:<40} €{premio_bruno:>12.2f}  €{premio_rafael:>12.2f}")

    print("-" * 80)
    print(f"{'TOTAL':<52} €{total_bruno:>12.2f}  €{total_rafael:>12.2f}")
    print("=" * 80)

except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()
finally:
    db_session.close()
