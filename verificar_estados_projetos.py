# -*- coding: utf-8 -*-
"""
Script para verificar estados dos projetos
"""
from dotenv import load_dotenv
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.models import Projeto, EstadoProjeto

load_dotenv()

database_url = os.getenv("DATABASE_URL", "sqlite:///./agora_media.db")
engine = create_engine(database_url)
Session = sessionmaker(bind=engine)
db = Session()

try:
    print("=" * 80)
    print("ESTADOS DOS PROJETOS")
    print("=" * 80)

    projetos = db.query(Projeto).order_by(Projeto.numero).all()

    print(f"\n{'Nº':<10} {'Estado':<15} {'Prémio Bruno':<15} {'Prémio Rafael':<15} {'Descrição':<40}")
    print("-" * 95)

    total_bruno_recebido = 0
    total_rafael_recebido = 0
    total_bruno_todos = 0
    total_rafael_todos = 0

    for proj in projetos:
        premio_bruno = float(proj.premio_bruno) if proj.premio_bruno else 0
        premio_rafael = float(proj.premio_rafael) if proj.premio_rafael else 0

        total_bruno_todos += premio_bruno
        total_rafael_todos += premio_rafael

        if proj.estado == EstadoProjeto.RECEBIDO:
            total_bruno_recebido += premio_bruno
            total_rafael_recebido += premio_rafael

        if premio_bruno > 0 or premio_rafael > 0:
            print(f"{proj.numero:<10} {proj.estado.value:<15} €{premio_bruno:>12.2f}  €{premio_rafael:>12.2f}  {proj.descricao[:40]}")

    print("-" * 95)
    print(f"\n📊 TOTAIS:")
    print(f"   Todos os projetos:")
    print(f"      Bruno: €{total_bruno_todos:,.2f}")
    print(f"      Rafael: €{total_rafael_todos:,.2f}")
    print()
    print(f"   Apenas RECEBIDOS:")
    print(f"      Bruno: €{total_bruno_recebido:,.2f}")
    print(f"      Rafael: €{total_rafael_recebido:,.2f}")

    print("\n" + "=" * 80)
    print("CONTAGEM POR ESTADO:")
    print("=" * 80)

    estados = db.query(Projeto.estado, func.count(Projeto.id)).group_by(Projeto.estado).all()
    from sqlalchemy import func
    estados = db.query(Projeto.estado, func.count(Projeto.id)).group_by(Projeto.estado).all()

    for estado, count in estados:
        print(f"  {estado.value}: {count} projetos")

except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()
