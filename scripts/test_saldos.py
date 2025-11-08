# -*- coding: utf-8 -*-
"""
Script de teste para a lógica de Saldos Pessoais
"""
from dotenv import load_dotenv
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import date
from decimal import Decimal

load_dotenv()

# Import models and logic
from database.models import (
    Base, Cliente, Fornecedor, EstatutoFornecedor,
    Projeto, TipoProjeto, EstadoProjeto,
    Despesa, TipoDespesa, EstadoDespesa,
    Boletim, Socio, EstadoBoletim
)
from logic.saldos import SaldosCalculator


def create_test_data(db_session):
    """Create test data"""
    print("Creating test data...")

    # Clear existing data
    db_session.query(Boletim).delete()
    db_session.query(Despesa).delete()
    db_session.query(Projeto).delete()
    db_session.query(Fornecedor).delete()
    db_session.query(Cliente).delete()
    db_session.commit()

    # Create cliente
    cliente = Cliente(
        numero="#C0001",
        nome="Cliente Teste Lda",
        nif="123456789"
    )
    db_session.add(cliente)

    # Create fornecedor
    fornecedor = Fornecedor(
        numero="#F0001",
        nome="Contabilidade XYZ",
        estatuto=EstatutoFornecedor.EMPRESA
    )
    db_session.add(fornecedor)

    db_session.flush()

    # BA: Projeto pessoal de €1000
    projeto_bruno = Projeto(
        numero="#P0001",
        tipo=TipoProjeto.PESSOAL_BRUNO,
        cliente_id=cliente.id,
        descricao="Projeto Pessoal BA",
        valor_sem_iva=Decimal("1000.00"),
        data_faturacao=date(2025, 1, 15),
        estado=EstadoProjeto.RECEBIDO
    )
    db_session.add(projeto_bruno)

    # RR: Projeto pessoal de €1500
    projeto_rafael = Projeto(
        numero="#P0002",
        tipo=TipoProjeto.PESSOAL_RAFAEL,
        cliente_id=cliente.id,
        descricao="Projeto Pessoal RR",
        valor_sem_iva=Decimal("1500.00"),
        data_faturacao=date(2025, 1, 20),
        estado=EstadoProjeto.RECEBIDO
    )
    db_session.add(projeto_rafael)

    # Projeto da empresa com prémios
    projeto_empresa = Projeto(
        numero="#P0003",
        tipo=TipoProjeto.EMPRESA,
        cliente_id=cliente.id,
        descricao="Projeto da Empresa",
        valor_sem_iva=Decimal("5000.00"),
        premio_bruno=Decimal("200.00"),
        premio_rafael=Decimal("200.00"),
        data_faturacao=date(2025, 1, 25),
        estado=EstadoProjeto.RECEBIDO
    )
    db_session.add(projeto_empresa)

    # Despesa fixa mensal: €900 (cada sócio paga €450)
    despesa_fixa = Despesa(
        numero="#D000001",
        tipo=TipoDespesa.FIXA_MENSAL,
        data=date(2025, 1, 31),
        credor_id=fornecedor.id,
        descricao="Despesas fixas Janeiro",
        valor_sem_iva=Decimal("900.00"),
        valor_com_iva=Decimal("1107.00"),
        estado=EstadoDespesa.PAGO
    )
    db_session.add(despesa_fixa)

    # Boletim BA: €400
    boletim_bruno = Boletim(
        numero="#B0001",
        socio=Socio.BRUNO,
        data_emissao=date(2025, 1, 31),
        valor=Decimal("400.00"),
        descricao="Ajudas de custo Janeiro",
        estado=EstadoBoletim.PENDENTE
    )
    db_session.add(boletim_bruno)

    db_session.commit()
    print("✓ Test data created!\n")


def test_saldos(db_session):
    """Test saldos calculation"""
    print("=" * 60)
    print("TESTE DE CÁLCULO DE SALDOS PESSOAIS")
    print("=" * 60)

    calculator = SaldosCalculator(db_session)

    # Test BA
    print("\n📊 SALDO BA:")
    saldo_bruno = calculator.calcular_saldo_bruno()
    print(f"\n  💰 SALDO TOTAL: €{saldo_bruno['saldo_total']:.2f}")
    print(f"\n  📈 INs (Entradas):")
    print(f"     • Projetos pessoais: €{saldo_bruno['ins']['projetos_pessoais']:.2f}")
    print(f"     • Prémios: €{saldo_bruno['ins']['premios']:.2f}")
    print(f"     ────────────────")
    print(f"     TOTAL INs: €{saldo_bruno['ins']['total']:.2f}")
    print(f"\n  📉 OUTs (Saídas):")
    print(f"     • Despesas fixas (÷2): €{saldo_bruno['outs']['despesas_fixas']:.2f}")
    print(f"     • Boletins: €{saldo_bruno['outs']['boletins']:.2f}")
    print(f"     • Despesas pessoais: €{saldo_bruno['outs']['despesas_pessoais']:.2f}")
    print(f"     ────────────────")
    print(f"     TOTAL OUTs: €{saldo_bruno['outs']['total']:.2f}")
    print(f"\n  💡 Sugestão de boletim: €{saldo_bruno['sugestao_boletim']:.2f}")

    # Test RR
    print("\n\n📊 SALDO RR:")
    saldo_rafael = calculator.calcular_saldo_rafael()
    print(f"\n  💰 SALDO TOTAL: €{saldo_rafael['saldo_total']:.2f}")
    print(f"\n  📈 INs (Entradas):")
    print(f"     • Projetos pessoais: €{saldo_rafael['ins']['projetos_pessoais']:.2f}")
    print(f"     • Prémios: €{saldo_rafael['ins']['premios']:.2f}")
    print(f"     ────────────────")
    print(f"     TOTAL INs: €{saldo_rafael['ins']['total']:.2f}")
    print(f"\n  📉 OUTs (Saídas):")
    print(f"     • Despesas fixas (÷2): €{saldo_rafael['outs']['despesas_fixas']:.2f}")
    print(f"     • Boletins: €{saldo_rafael['outs']['boletins']:.2f}")
    print(f"     • Despesas pessoais: €{saldo_rafael['outs']['despesas_pessoais']:.2f}")
    print(f"     ────────────────")
    print(f"     TOTAL OUTs: €{saldo_rafael['outs']['total']:.2f}")
    print(f"\n  💡 Sugestão de boletim: €{saldo_rafael['sugestao_boletim']:.2f}")

    print("\n" + "=" * 60)
    print("✅ TESTE CONCLUÍDO COM SUCESSO!")
    print("=" * 60)

    # Verify calculations
    print("\n🔍 Verificação dos cálculos:")
    print(f"\nBA esperado:")
    print(f"  INs: €1000 (projeto) + €200 (prémio) = €1200")
    print(f"  OUTs: €450 (fixas÷2) + €400 (boletim) = €850")
    print(f"  Saldo: €1200 - €850 = €350")
    print(f"  Calculado: €{saldo_bruno['saldo_total']:.2f}")
    print(f"  ✓ Correto!" if abs(saldo_bruno['saldo_total'] - 350) < 0.01 else "  ✗ Erro!")

    print(f"\nRR esperado:")
    print(f"  INs: €1500 (projeto) + €200 (prémio) = €1700")
    print(f"  OUTs: €450 (fixas÷2) + €0 (sem boletins) = €450")
    print(f"  Saldo: €1700 - €450 = €1250")
    print(f"  Calculado: €{saldo_rafael['saldo_total']:.2f}")
    print(f"  ✓ Correto!" if abs(saldo_rafael['saldo_total'] - 1250) < 0.01 else "  ✗ Erro!")


def main():
    # Get database URL
    database_url = os.getenv("DATABASE_URL", "sqlite:///./agora_media.db")

    # Create engine and session
    engine = create_engine(database_url)
    Session = sessionmaker(bind=engine)
    db_session = Session()

    try:
        # Create tables if needed
        Base.metadata.create_all(engine)

        # Create test data
        create_test_data(db_session)

        # Test saldos
        test_saldos(db_session)

    finally:
        db_session.close()


if __name__ == "__main__":
    main()
