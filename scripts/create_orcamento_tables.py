#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para criar tabelas de Orçamentos
"""
import os
import sys

# Adicionar diretório raiz ao path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import create_engine
from dotenv import load_dotenv
from database.models.base import Base
from database.models.orcamento import Orcamento, OrcamentoSecao, OrcamentoItem, OrcamentoReparticao
from database.models.equipamento import Equipamento  # Necessário para foreign key
from database.models.cliente import Cliente  # Necessário para foreign key

# Load environment
load_dotenv()

def create_orcamento_tables():
    """Cria as tabelas de orçamentos"""
    print("=" * 80)
    print("🔄 CRIANDO TABELAS DE ORÇAMENTOS")
    print("=" * 80)
    print()

    # Setup database
    database_url = os.getenv("DATABASE_URL", "sqlite:///./agora_media.db")
    engine = create_engine(database_url)

    print(f"Database: {database_url}")
    print()

    try:
        # Criar apenas as tabelas de Orcamento
        print("Criando tabelas:")
        print("  - orcamentos")
        print("  - orcamento_secoes")
        print("  - orcamento_itens")
        print("  - orcamento_reparticoes")

        # Usar create_all com as tabelas específicas
        Base.metadata.create_all(
            engine,
            tables=[
                Orcamento.__table__,
                OrcamentoSecao.__table__,
                OrcamentoItem.__table__,
                OrcamentoReparticao.__table__
            ]
        )

        print()
        print("=" * 80)
        print("✅ TABELAS DE ORÇAMENTOS CRIADAS COM SUCESSO")
        print("=" * 80)

    except Exception as e:
        print()
        print("=" * 80)
        print(f"❌ ERRO: {e}")
        print("=" * 80)
        raise

if __name__ == '__main__':
    create_orcamento_tables()
