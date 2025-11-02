# -*- coding: utf-8 -*-
"""
Script para verificar saldos reais após importação
"""
from dotenv import load_dotenv
import os
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from database.models import Projeto, TipoProjeto, EstadoProjeto, Despesa, TipoDespesa, EstadoDespesa, Boletim, Socio, EstadoBoletim
from decimal import Decimal

load_dotenv()

database_url = os.getenv("DATABASE_URL", "sqlite:///./agora_media.db")
engine = create_engine(database_url)
Session = sessionmaker(bind=engine)
db = Session()

try:
    print("=" * 80)
    print("SALDOS PESSOAIS REAIS")
    print("=" * 80)

    for socio_nome in ["BRUNO", "RAFAEL"]:
        print(f"\n👤 {socio_nome}:")
        print("-" * 80)

        # 1. Projetos pessoais
        if socio_nome == "BRUNO":
            projetos_pessoais = db.query(func.sum(Projeto.valor_sem_iva)).filter(
                Projeto.tipo == TipoProjeto.PESSOAL_BRUNO,
                Projeto.estado == EstadoProjeto.RECEBIDO
            ).scalar() or Decimal(0)
        else:
            projetos_pessoais = db.query(func.sum(Projeto.valor_sem_iva)).filter(
                Projeto.tipo == TipoProjeto.PESSOAL_RAFAEL,
                Projeto.estado == EstadoProjeto.RECEBIDO
            ).scalar() or Decimal(0)

        # 2. Prémios
        if socio_nome == "BRUNO":
            premios = db.query(func.sum(Projeto.premio_bruno)).filter(
                Projeto.premio_bruno > 0,
                Projeto.estado == EstadoProjeto.RECEBIDO
            ).scalar() or Decimal(0)
        else:
            premios = db.query(func.sum(Projeto.premio_rafael)).filter(
                Projeto.premio_rafael > 0,
                Projeto.estado == EstadoProjeto.RECEBIDO
            ).scalar() or Decimal(0)

        # 3. Despesas fixas (÷2)
        despesas_fixas = db.query(func.sum(Despesa.valor_sem_iva)).filter(
            Despesa.tipo == TipoDespesa.FIXA_MENSAL,
            Despesa.estado == EstadoDespesa.PAGO
        ).scalar() or Decimal(0)
        despesas_fixas_metade = despesas_fixas / 2

        # 4. Despesas pessoais
        if socio_nome == "BRUNO":
            despesas_pessoais = db.query(func.sum(Despesa.valor_sem_iva)).filter(
                Despesa.tipo == TipoDespesa.PESSOAL_BRUNO,
                Despesa.estado == EstadoDespesa.PAGO
            ).scalar() or Decimal(0)
        else:
            despesas_pessoais = db.query(func.sum(Despesa.valor_sem_iva)).filter(
                Despesa.tipo == TipoDespesa.PESSOAL_RAFAEL,
                Despesa.estado == EstadoDespesa.PAGO
            ).scalar() or Decimal(0)

        # 5. Boletins
        if socio_nome == "BRUNO":
            boletins = db.query(func.sum(Boletim.valor)).filter(
                Boletim.socio == Socio.BRUNO,
                Boletim.estado == EstadoBoletim.PAGO
            ).scalar() or Decimal(0)
        else:
            boletins = db.query(func.sum(Boletim.valor)).filter(
                Boletim.socio == Socio.RAFAEL,
                Boletim.estado == EstadoBoletim.PAGO
            ).scalar() or Decimal(0)

        # Cálculo do saldo
        total_in = projetos_pessoais + premios
        total_out = despesas_fixas_metade + despesas_pessoais + boletins
        saldo = total_in - total_out

        print(f"  📈 INs:")
        print(f"     • Projetos pessoais: €{projetos_pessoais:,.2f}")
        print(f"     • Prémios: €{premios:,.2f}")
        print(f"     ────────────────")
        print(f"     TOTAL INs: €{total_in:,.2f}")
        print()
        print(f"  📉 OUTs:")
        print(f"     • Despesas fixas (÷2): €{despesas_fixas_metade:,.2f}")
        print(f"     • Despesas pessoais: €{despesas_pessoais:,.2f}")
        print(f"     • Boletins: €{boletins:,.2f}")
        print(f"     ────────────────")
        print(f"     TOTAL OUTs: €{total_out:,.2f}")
        print()
        print(f"  💰 SALDO TOTAL: €{saldo:,.2f}")

    print("\n" + "=" * 80)

except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()
