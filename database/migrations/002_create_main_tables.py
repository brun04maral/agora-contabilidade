"""
Migration: Create main tables (clientes, fornecedores, projetos, despesas, boletins, equipamento)

Run this script to create all main tables in your database.
"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Load environment variables
load_dotenv()

# Import models
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from database.models import (
    Base, Cliente, Fornecedor, Projeto, Despesa, Boletim, Equipamento
)


def create_tables(engine):
    """
    Create all database tables

    Args:
        engine: SQLAlchemy engine
    """
    print("Creating database tables...")
    Base.metadata.create_all(engine)
    print("Tables created successfully!")
    print("\nCreated tables:")
    print("  - users")
    print("  - clientes")
    print("  - fornecedores")
    print("  - projetos")
    print("  - despesas")
    print("  - boletins")
    print("  - equipamento")


def seed_example_data(db_session):
    """
    Seed some example data for testing

    Args:
        db_session: SQLAlchemy database session
    """
    print("\nSeeding example data...")

    from database.models import (
        Cliente, Fornecedor, EstatutoFornecedor,
        Projeto, TipoProjeto, EstadoProjeto,
        Despesa, TipoDespesa, EstadoDespesa,
        Boletim, Socio, EstadoBoletim
    )
    from datetime import date
    from decimal import Decimal

    # Check if data already exists
    existing_clientes = db_session.query(Cliente).count()
    if existing_clientes > 0:
        print(f"Data already exists in database ({existing_clientes} clientes found). Skipping seed.")
        return

    # Create example client
    cliente1 = Cliente(
        numero="#C0001",
        nome="Cliente Exemplo Lda",
        nif="123456789",
        pais="Portugal",
        email="cliente@exemplo.pt"
    )
    db_session.add(cliente1)

    # Create example supplier
    fornecedor1 = Fornecedor(
        numero="#F0001",
        nome="Fornecedor Exemplo",
        estatuto=EstatutoFornecedor.FREELANCER,
        area="Pós-produção",
        funcao="Editor",
        nif="987654321"
    )
    db_session.add(fornecedor1)

    db_session.flush()  # Get IDs

    # Create example project - Bruno's personal project
    projeto1 = Projeto(
        numero="#P0001",
        tipo=TipoProjeto.PESSOAL_BRUNO,
        cliente_id=cliente1.id,
        descricao="Projeto Pessoal Bruno - Vídeo Corporativo",
        valor_sem_iva=Decimal("1500.00"),
        data_inicio=date(2025, 1, 15),
        estado=EstadoProjeto.RECEBIDO
    )
    db_session.add(projeto1)

    # Create example project - Company project with prizes
    projeto2 = Projeto(
        numero="#P0002",
        tipo=TipoProjeto.EMPRESA,
        cliente_id=cliente1.id,
        descricao="Projeto Empresa - Documentário",
        valor_sem_iva=Decimal("5000.00"),
        premio_bruno=Decimal("500.00"),
        premio_rafael=Decimal("500.00"),
        data_inicio=date(2025, 1, 20),
        estado=EstadoProjeto.FATURADO
    )
    db_session.add(projeto2)

    # Create example expense - Fixed monthly
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

    # Create example boletim
    boletim1 = Boletim(
        numero="#B0001",
        socio=Socio.BRUNO,
        data_emissao=date(2025, 1, 31),
        valor=Decimal("500.00"),
        descricao="Ajudas de custo - Janeiro 2025",
        estado=EstadoBoletim.PAGO,
        data_pagamento=date(2025, 2, 5)
    )
    db_session.add(boletim1)

    db_session.commit()

    print("  ✓ Created example client")
    print("  ✓ Created example supplier")
    print("  ✓ Created 2 example projects")
    print("  ✓ Created example expense")
    print("  ✓ Created example boletim")
    print("\nExample data seeded successfully!")


def run_migration():
    """Run the migration"""
    print("=" * 60)
    print("Migration: Create Main Tables")
    print("=" * 60)

    # Get database URL
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        print("\n⚠️  WARNING: DATABASE_URL not set in .env file")
        print("Using SQLite database as fallback: ./agora_media.db")
        database_url = "sqlite:///./agora_media.db"

    print(f"\nDatabase: {database_url.split('@')[-1] if '@' in database_url else database_url}")

    try:
        # Create engine and session
        engine = create_engine(database_url)
        Session = sessionmaker(bind=engine)
        db_session = Session()

        # Create tables
        create_tables(engine)

        # Ask to seed example data
        should_seed = input("\nDo you want to seed example data? (y/n): ").lower().strip()
        if should_seed == 'y':
            seed_example_data(db_session)

        # Close session
        db_session.close()

        print("\n" + "=" * 60)
        print("Migration completed successfully!")
        print("=" * 60)
        print("\n📊 Next steps:")
        print("  1. Run the application: python main.py")
        print("  2. The Saldos Pessoais calculation is now ready!")

    except Exception as e:
        print(f"\n❌ Migration failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_migration()
