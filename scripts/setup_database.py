# -*- coding: utf-8 -*-
"""
Script de setup completo da base de dados
Cria todas as tabelas e dados de teste
"""
from dotenv import load_dotenv
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import date
from decimal import Decimal

load_dotenv()

# Import models
from database.models import (
    Base, User, Cliente, Fornecedor, EstatutoFornecedor,
    Projeto, TipoProjeto, EstadoProjeto,
    Despesa, TipoDespesa, EstadoDespesa,
    Boletim, Socio, EstadoBoletim
)
from logic.auth import AuthManager


def setup_database():
    """Setup complete database"""
    print("=" * 70)
    print("SETUP DA BASE DE DADOS - AGORA MEDIA CONTABILIDADE")
    print("=" * 70)

    # Get database URL
    database_url = os.getenv("DATABASE_URL", "sqlite:///./agora_media.db")
    print(f"\n📁 Database: {database_url.split('@')[-1] if '@' in database_url else database_url}")

    # Create engine and session
    engine = create_engine(database_url)
    Session = sessionmaker(bind=engine)
    db_session = Session()

    try:
        # 1. Create all tables
        print("\n1️⃣  Criando tabelas...")
        Base.metadata.create_all(engine)
        print("   ✓ Tabelas criadas!")

        # 2. Create users
        print("\n2️⃣  Criando utilizadores...")
        auth_manager = AuthManager(db_session)

        # Check if users already exist
        existing_users = db_session.query(User).count()
        if existing_users == 0:
            # Create Bruno
            success, user = auth_manager.create_user(
                email="bruno@agoramedia.pt",
                password="bruno123",
                name="Bruno Amaral",
                role="socio"
            )
            if success:
                print("   ✓ Criado: bruno@agoramedia.pt (senha: bruno123)")

            # Create Rafael
            success, user = auth_manager.create_user(
                email="rafael@agoramedia.pt",
                password="rafael123",
                name="Rafael Reigota",
                role="socio"
            )
            if success:
                print("   ✓ Criado: rafael@agoramedia.pt (senha: rafael123)")
        else:
            print(f"   ⚠️  Já existem {existing_users} utilizadores na base de dados")

        # 3. Create test data
        print("\n3️⃣  Criando dados de teste...")

        # Check if data already exists
        existing_projetos = db_session.query(Projeto).count()
        if existing_projetos > 0:
            print(f"   ⚠️  Já existem {existing_projetos} projetos. A saltar criação de dados.")
        else:
            # Cliente
            cliente = Cliente(
                numero="#C0001",
                nome="RTP - Rádio e Televisão de Portugal",
                nif="500776088",
                pais="Portugal",
                email="producao@rtp.pt"
            )
            db_session.add(cliente)

            cliente2 = Cliente(
                numero="#C0002",
                nome="Câmara Municipal de Lisboa",
                nif="500182412",
                pais="Portugal"
            )
            db_session.add(cliente2)

            # Fornecedores
            fornecedor1 = Fornecedor(
                numero="#F0001",
                nome="Contabilidade Silva & Associados",
                estatuto=EstatutoFornecedor.EMPRESA,
                area="Serviços",
                nif="123456789"
            )
            db_session.add(fornecedor1)

            fornecedor2 = Fornecedor(
                numero="#F0002",
                nome="João Editor Freelancer",
                estatuto=EstatutoFornecedor.FREELANCER,
                area="Pós-produção",
                funcao="Editor de vídeo",
                classificacao=5
            )
            db_session.add(fornecedor2)

            db_session.flush()

            # Projeto pessoal Bruno - €1500
            projeto1 = Projeto(
                numero="#P0001",
                tipo=TipoProjeto.PESSOAL_BRUNO,
                cliente_id=cliente.id,
                descricao="Vídeo Corporativo - Bruno (Freelance)",
                valor_sem_iva=Decimal("1500.00"),
                data_inicio=date(2025, 1, 10),
                data_faturacao=date(2025, 1, 20),
                estado=EstadoProjeto.PAGO
            )
            db_session.add(projeto1)

            # Projeto pessoal Rafael - €2000
            projeto2 = Projeto(
                numero="#P0002",
                tipo=TipoProjeto.PESSOAL_RAFAEL,
                cliente_id=cliente2.id,
                descricao="Documentário - Rafael (Freelance)",
                valor_sem_iva=Decimal("2000.00"),
                data_inicio=date(2025, 1, 15),
                data_faturacao=date(2025, 1, 25),
                estado=EstadoProjeto.PAGO
            )
            db_session.add(projeto2)

            # Projeto da empresa com prémios
            projeto3 = Projeto(
                numero="#P0003",
                tipo=TipoProjeto.EMPRESA,
                cliente_id=cliente.id,
                descricao="Série Documental RTP - 3 Episódios",
                valor_sem_iva=Decimal("8000.00"),
                premio_bruno=Decimal("500.00"),
                premio_rafael=Decimal("500.00"),
                data_inicio=date(2025, 1, 5),
                data_faturacao=date(2025, 1, 30),
                estado=EstadoProjeto.PAGO
            )
            db_session.add(projeto3)

            # Despesas fixas mensais - Janeiro
            despesa1 = Despesa(
                numero="#D000001",
                tipo=TipoDespesa.FIXA_MENSAL,
                data=date(2025, 1, 31),
                credor_id=fornecedor1.id,
                descricao="Contabilidade - Janeiro 2025",
                valor_sem_iva=Decimal("150.00"),
                valor_com_iva=Decimal("184.50"),
                estado=EstadoDespesa.PAGO
            )
            db_session.add(despesa1)

            despesa2 = Despesa(
                numero="#D000002",
                tipo=TipoDespesa.FIXA_MENSAL,
                data=date(2025, 1, 31),
                credor_id=None,
                descricao="Seguro da empresa - Janeiro 2025",
                valor_sem_iva=Decimal("80.00"),
                valor_com_iva=Decimal("98.40"),
                estado=EstadoDespesa.PAGO
            )
            db_session.add(despesa2)

            despesa3 = Despesa(
                numero="#D000003",
                tipo=TipoDespesa.FIXA_MENSAL,
                data=date(2025, 1, 31),
                credor_id=None,
                descricao="Software e subscrições - Janeiro 2025",
                valor_sem_iva=Decimal("120.00"),
                valor_com_iva=Decimal("147.60"),
                estado=EstadoDespesa.PAGO
            )
            db_session.add(despesa3)

            # Despesa de projeto
            despesa4 = Despesa(
                numero="#D000004",
                tipo=TipoDespesa.PROJETO,
                data=date(2025, 1, 20),
                credor_id=fornecedor2.id,
                projeto_id=projeto3.id,
                descricao="Edição - Série Documental",
                valor_sem_iva=Decimal("1200.00"),
                valor_com_iva=Decimal("1476.00"),
                estado=EstadoDespesa.PAGO
            )
            db_session.add(despesa4)

            # Boletim Bruno - €600
            boletim1 = Boletim(
                numero="#B0001",
                socio=Socio.BA,
                data_emissao=date(2025, 1, 31),
                valor=Decimal("600.00"),
                descricao="Ajudas de custo - Janeiro 2025",
                estado=EstadoBoletim.PAGO,
                data_pagamento=date(2025, 2, 5)
            )
            db_session.add(boletim1)

            # Boletim Rafael - €800 (pendente)
            boletim2 = Boletim(
                numero="#B0002",
                socio=Socio.RR,
                data_emissao=date(2025, 1, 31),
                valor=Decimal("800.00"),
                descricao="Ajudas de custo - Janeiro 2025",
                estado=EstadoBoletim.PENDENTE
            )
            db_session.add(boletim2)

            db_session.commit()

            print("   ✓ Clientes criados")
            print("   ✓ Fornecedores criados")
            print("   ✓ Projetos criados")
            print("   ✓ Despesas criadas")
            print("   ✓ Boletins criados")

        print("\n" + "=" * 70)
        print("✅ SETUP CONCLUÍDO COM SUCESSO!")
        print("=" * 70)
        print("\n📊 Próximos passos:")
        print("   1. Execute: python main.py")
        print("   2. Faça login com:")
        print("      • bruno@agoramedia.pt / bruno123")
        print("      • rafael@agoramedia.pt / rafael123")
        print("   3. Vá para 'Saldos Pessoais' para ver os cálculos!")
        print("\n" + "=" * 70)

    except Exception as e:
        print(f"\n❌ Erro durante setup: {e}")
        import traceback
        traceback.print_exc()
        db_session.rollback()

    finally:
        db_session.close()


if __name__ == "__main__":
    setup_database()
