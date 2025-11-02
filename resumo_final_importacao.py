# -*- coding: utf-8 -*-
"""
Resumo final da importação e validação
"""
from dotenv import load_dotenv
import os
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from database.models import Projeto, TipoProjeto, EstadoProjeto, Despesa, TipoDespesa, EstadoDespesa, Boletim, Socio, EstadoBoletim, Cliente, Fornecedor
from decimal import Decimal

load_dotenv()

database_url = os.getenv("DATABASE_URL", "sqlite:///./agora_media.db")
engine = create_engine(database_url)
Session = sessionmaker(bind=engine)
db = Session()

try:
    print("=" * 90)
    print("📊 RESUMO FINAL - IMPORTAÇÃO COMPLETA")
    print("=" * 90)

    # Contagens
    print("\n📦 REGISTOS NA BASE DE DADOS:")
    print(f"   • Clientes: {db.query(Cliente).count()}")
    print(f"   • Fornecedores: {db.query(Fornecedor).count()}")
    print(f"   • Projetos: {db.query(Projeto).count()}")
    print(f"   • Despesas: {db.query(Despesa).count()}")
    print(f"   • Boletins: {db.query(Boletim).count()}")

    # Prémios totais
    print("\n" + "=" * 90)
    print("🏆 PRÉMIOS (TODOS OS PROJETOS)")
    print("=" * 90)

    bruno_total = db.query(func.sum(Projeto.premio_bruno)).scalar() or Decimal(0)
    rafael_total = db.query(func.sum(Projeto.premio_rafael)).scalar() or Decimal(0)

    print(f"   • Bruno: €{float(bruno_total):,.2f}")
    print(f"   • Rafael: €{float(rafael_total):,.2f}")

    # Prémios apenas RECEBIDOS
    bruno_recebido = db.query(func.sum(Projeto.premio_bruno)).filter(
        Projeto.estado == EstadoProjeto.RECEBIDO
    ).scalar() or Decimal(0)

    rafael_recebido = db.query(func.sum(Projeto.premio_rafael)).filter(
        Projeto.estado == EstadoProjeto.RECEBIDO
    ).scalar() or Decimal(0)

    print(f"\n🏆 PRÉMIOS DE PROJETOS RECEBIDOS (contam no saldo):")
    print(f"   • Bruno: €{float(bruno_recebido):,.2f}")
    print(f"   • Rafael: €{float(rafael_recebido):,.2f}")

    # Saldos completos
    print("\n" + "=" * 90)
    print("💰 SALDOS PESSOAIS")
    print("=" * 90)

    for socio_nome, socio_enum in [("BRUNO", Socio.BRUNO), ("RAFAEL", Socio.RAFAEL)]:
        print(f"\n👤 {socio_nome}:")
        print("-" * 90)

        # INs
        if socio_nome == "BRUNO":
            projetos_pessoais = db.query(func.sum(Projeto.valor_sem_iva)).filter(
                Projeto.tipo == TipoProjeto.PESSOAL_BRUNO,
                Projeto.estado == EstadoProjeto.RECEBIDO
            ).scalar() or Decimal(0)

            premios = bruno_recebido
        else:
            projetos_pessoais = db.query(func.sum(Projeto.valor_sem_iva)).filter(
                Projeto.tipo == TipoProjeto.PESSOAL_RAFAEL,
                Projeto.estado == EstadoProjeto.RECEBIDO
            ).scalar() or Decimal(0)

            premios = rafael_recebido

        # OUTs
        despesas_fixas = db.query(func.sum(Despesa.valor_sem_iva)).filter(
            Despesa.tipo == TipoDespesa.FIXA_MENSAL,
            Despesa.estado == EstadoDespesa.PAGO
        ).scalar() or Decimal(0)
        despesas_fixas_metade = despesas_fixas / 2

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

        boletins = db.query(func.sum(Boletim.valor)).filter(
            Boletim.socio == socio_enum,
            Boletim.estado == EstadoBoletim.PAGO
        ).scalar() or Decimal(0)

        total_in = projetos_pessoais + premios
        total_out = despesas_fixas_metade + despesas_pessoais + boletins
        saldo = total_in - total_out

        print(f"  📈 INs: €{float(total_in):,.2f}")
        print(f"     • Projetos pessoais: €{float(projetos_pessoais):,.2f}")
        print(f"     • Prémios: €{float(premios):,.2f}")

        print(f"\n  📉 OUTs: €{float(total_out):,.2f}")
        print(f"     • Despesas fixas (÷2): €{float(despesas_fixas_metade):,.2f}")
        print(f"     • Despesas pessoais: €{float(despesas_pessoais):,.2f}")
        print(f"     • Boletins pagos: €{float(boletins):,.2f}")

        print(f"\n  💰 SALDO: €{float(saldo):,.2f}")

    print("\n" + "=" * 90)
    print("✅ IMPORTAÇÃO E VALIDAÇÃO COMPLETAS!")
    print("=" * 90)

except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()
