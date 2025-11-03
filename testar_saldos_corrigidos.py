# -*- coding: utf-8 -*-
"""
Testar a lógica corrigida de saldos
"""
from dotenv import load_dotenv
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from logic.saldos import SaldosCalculator
from database.models import Socio

load_dotenv()

database_url = os.getenv("DATABASE_URL", "sqlite:///./agora_media.db")
engine = create_engine(database_url)
Session = sessionmaker(bind=engine)
db = Session()

try:
    print("=" * 80)
    print("TESTE DA LÓGICA DE SALDOS - CORRIGIDA")
    print("=" * 80)

    calculator = SaldosCalculator(db)

    # Bruno
    saldo_bruno = calculator.calcular_saldo_bruno(incluir_investimento=False)

    print(f"\n👤 BRUNO:")
    print(f"  INs:  €{saldo_bruno['ins']['total']:>10,.2f}")
    print(f"    • Projetos pessoais: €{saldo_bruno['ins']['projetos_pessoais']:>10,.2f}")
    print(f"    • Prémios:           €{saldo_bruno['ins']['premios']:>10,.2f}")
    print(f"  OUTs: €{saldo_bruno['outs']['total']:>10,.2f}")
    print(f"    • Fixas (÷2):        €{saldo_bruno['outs']['despesas_fixas']:>10,.2f}")
    print(f"    • Boletins:          €{saldo_bruno['outs']['boletins']:>10,.2f}")
    print(f"    • Desp. pessoais:    €{saldo_bruno['outs']['despesas_pessoais']:>10,.2f}")
    print(f"  SALDO: €{saldo_bruno['saldo_total']:>10,.2f}")
    print(f"  Excel esperado: €4,821.98")
    print(f"  Match: {'✅' if abs(saldo_bruno['saldo_total'] - 4821.98) < 1 else '❌'}")

    # Rafael
    saldo_rafael = calculator.calcular_saldo_rafael(incluir_investimento=False)

    print(f"\n👤 RAFAEL:")
    print(f"  INs:  €{saldo_rafael['ins']['total']:>10,.2f}")
    print(f"    • Projetos pessoais: €{saldo_rafael['ins']['projetos_pessoais']:>10,.2f}")
    print(f"    • Prémios:           €{saldo_rafael['ins']['premios']:>10,.2f}")
    print(f"  OUTs: €{saldo_rafael['outs']['total']:>10,.2f}")
    print(f"    • Fixas (÷2):        €{saldo_rafael['outs']['despesas_fixas']:>10,.2f}")
    print(f"    • Boletins:          €{saldo_rafael['outs']['boletins']:>10,.2f}")
    print(f"    • Desp. pessoais:    €{saldo_rafael['outs']['despesas_pessoais']:>10,.2f}")
    print(f"  SALDO: €{saldo_rafael['saldo_total']:>10,.2f}")
    print(f"  Excel esperado: €2,711.00")
    print(f"  Match: {'✅' if abs(saldo_rafael['saldo_total'] - 2711) < 1 else '❌'}")

    print("\n" + "=" * 80)
    print("✅ TESTE CONCLUÍDO!")
    print("=" * 80)

except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()
