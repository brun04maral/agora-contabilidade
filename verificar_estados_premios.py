# -*- coding: utf-8 -*-
"""
Script para verificar estados dos projetos com prémios
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
    print("=" * 90)
    print("PROJETOS COM PRÉMIOS - POR ESTADO")
    print("=" * 90)

    projetos = db.query(Projeto).filter(
        (Projeto.premio_bruno > 0) | (Projeto.premio_rafael > 0)
    ).order_by(Projeto.estado, Projeto.numero).all()

    bruno_recebido = 0
    rafael_recebido = 0
    bruno_outros = 0
    rafael_outros = 0

    for estado in [EstadoProjeto.RECEBIDO, EstadoProjeto.FATURADO, EstadoProjeto.NAO_FATURADO]:
        projetos_estado = [p for p in projetos if p.estado == estado]

        if projetos_estado:
            print(f"\n📌 {estado.value}")
            print("-" * 90)

            for proj in projetos_estado:
                bruno = float(proj.premio_bruno) if proj.premio_bruno else 0
                rafael = float(proj.premio_rafael) if proj.premio_rafael else 0

                if estado == EstadoProjeto.RECEBIDO:
                    bruno_recebido += bruno
                    rafael_recebido += rafael
                else:
                    bruno_outros += bruno
                    rafael_outros += rafael

                print(f"  {proj.numero:<10} B:€{bruno:>7.2f}  R:€{rafael:>7.2f}  | {proj.descricao[:50]}")

    print("\n" + "=" * 90)
    print("RESUMO")
    print("=" * 90)
    print(f"\n✅ Projetos RECEBIDOS:")
    print(f"   Bruno: €{bruno_recebido:,.2f}")
    print(f"   Rafael: €{rafael_recebido:,.2f}")

    print(f"\n⏳ Projetos FATURADOS/NÃO FATURADOS:")
    print(f"   Bruno: €{bruno_outros:,.2f}")
    print(f"   Rafael: €{rafael_outros:,.2f}")

    print(f"\n💰 TOTAL:")
    print(f"   Bruno: €{bruno_recebido + bruno_outros:,.2f}")
    print(f"   Rafael: €{rafael_recebido + rafael_outros:,.2f}")

    print("\n" + "=" * 90)

except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()
