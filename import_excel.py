#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de importação de dados do Excel via JSON
Importa dados reais gerados pelo Claude Chat
"""
import json
import sys
from pathlib import Path
from datetime import datetime, date
from decimal import Decimal

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

# Load environment
load_dotenv()

# Import models
from database.models import (
    Cliente, Fornecedor, Projeto, Despesa, Boletim,
    TipoProjeto, EstadoProjeto, TipoDespesa, EstadoDespesa,
    Socio, EstadoBoletim, EstatutoFornecedor
)

# Import managers
from logic.clientes import ClientesManager
from logic.fornecedores import FornecedoresManager
from logic.projetos import ProjetosManager
from logic.despesas import DespesasManager
from logic.boletins import BoletinsManager


class DataImporter:
    """Importador de dados do JSON"""

    def __init__(self, db_session):
        self.db = db_session
        self.clientes_manager = ClientesManager(db_session)
        self.fornecedores_manager = FornecedoresManager(db_session)
        self.projetos_manager = ProjetosManager(db_session)
        self.despesas_manager = DespesasManager(db_session)
        self.boletins_manager = BoletinsManager(db_session)

        # Cache de IDs para fazer matching
        self.clientes_cache = {}
        self.fornecedores_cache = {}
        self.projetos_cache = {}

        # Estatísticas
        self.stats = {
            'clientes': {'ok': 0, 'erro': 0},
            'fornecedores': {'ok': 0, 'erro': 0},
            'projetos': {'ok': 0, 'erro': 0},
            'despesas': {'ok': 0, 'erro': 0},
            'boletins': {'ok': 0, 'erro': 0}
        }
        self.errors = []

    def parse_date(self, date_str):
        """Parse date string to date object"""
        if not date_str:
            return None
        try:
            return datetime.strptime(date_str, "%Y-%m-%d").date()
        except:
            return None

    def import_clientes(self, clientes_data):
        """Import clientes"""
        print("\n📇 Importando Clientes...")

        for idx, cliente_data in enumerate(clientes_data, 1):
            try:
                nome = cliente_data.get('nome')
                if not nome:
                    self.errors.append(f"Cliente #{idx}: Nome obrigatório")
                    self.stats['clientes']['erro'] += 1
                    continue

                # Verificar se já existe
                existing = self.db.query(Cliente).filter(Cliente.nome == nome).first()
                if existing:
                    print(f"   ⚠️  Cliente '{nome}' já existe (#{existing.numero})")
                    self.clientes_cache[nome] = existing.id
                    continue

                success, cliente, msg = self.clientes_manager.criar(
                    nome=nome,
                    nif=cliente_data.get('nif'),
                    morada=cliente_data.get('morada'),
                    pais=cliente_data.get('pais', 'Portugal'),
                    contacto=cliente_data.get('contacto'),
                    email=cliente_data.get('email'),
                    angariacao=cliente_data.get('angariacao'),
                    nota=cliente_data.get('nota')
                )

                if success:
                    print(f"   ✅ {cliente.numero} - {nome}")
                    self.clientes_cache[nome] = cliente.id
                    self.stats['clientes']['ok'] += 1
                else:
                    print(f"   ❌ {nome}: {msg}")
                    self.errors.append(f"Cliente '{nome}': {msg}")
                    self.stats['clientes']['erro'] += 1

            except Exception as e:
                print(f"   ❌ Cliente #{idx}: {str(e)}")
                self.errors.append(f"Cliente #{idx}: {str(e)}")
                self.stats['clientes']['erro'] += 1

    def import_fornecedores(self, fornecedores_data):
        """Import fornecedores"""
        print("\n🏢 Importando Fornecedores...")

        for idx, fornecedor_data in enumerate(fornecedores_data, 1):
            try:
                nome = fornecedor_data.get('nome')
                if not nome:
                    self.errors.append(f"Fornecedor #{idx}: Nome obrigatório")
                    self.stats['fornecedores']['erro'] += 1
                    continue

                # Verificar se já existe
                existing = self.db.query(Fornecedor).filter(Fornecedor.nome == nome).first()
                if existing:
                    print(f"   ⚠️  Fornecedor '{nome}' já existe (#{existing.numero})")
                    self.fornecedores_cache[nome] = existing.id
                    continue

                # Parse estatuto
                estatuto_str = fornecedor_data.get('estatuto', 'FREELANCER')
                try:
                    estatuto = EstatutoFornecedor[estatuto_str]
                except:
                    estatuto = EstatutoFornecedor.FREELANCER

                # Parse data do seguro
                validade_seguro = self.parse_date(fornecedor_data.get('validade_seguro_trabalho'))

                success, fornecedor, msg = self.fornecedores_manager.criar(
                    nome=nome,
                    estatuto=estatuto,
                    area=fornecedor_data.get('area'),
                    funcao=fornecedor_data.get('funcao'),
                    classificacao=fornecedor_data.get('classificacao'),
                    nif=fornecedor_data.get('nif'),
                    iban=fornecedor_data.get('iban'),
                    morada=fornecedor_data.get('morada'),
                    contacto=fornecedor_data.get('contacto'),
                    email=fornecedor_data.get('email'),
                    validade_seguro_trabalho=validade_seguro,
                    nota=fornecedor_data.get('nota')
                )

                if success:
                    print(f"   ✅ {fornecedor.numero} - {nome}")
                    self.fornecedores_cache[nome] = fornecedor.id
                    self.stats['fornecedores']['ok'] += 1
                else:
                    print(f"   ❌ {nome}: {msg}")
                    self.errors.append(f"Fornecedor '{nome}': {msg}")
                    self.stats['fornecedores']['erro'] += 1

            except Exception as e:
                print(f"   ❌ Fornecedor #{idx}: {str(e)}")
                self.errors.append(f"Fornecedor #{idx}: {str(e)}")
                self.stats['fornecedores']['erro'] += 1

    def import_projetos(self, projetos_data):
        """Import projetos"""
        print("\n🎬 Importando Projetos...")

        for idx, projeto_data in enumerate(projetos_data, 1):
            try:
                # Parse tipo
                tipo_str = projeto_data.get('tipo', 'EMPRESA')
                try:
                    tipo = TipoProjeto[tipo_str]
                except:
                    tipo = TipoProjeto.EMPRESA

                # Find cliente
                cliente_nome = projeto_data.get('cliente_nome')
                cliente_id = self.clientes_cache.get(cliente_nome)
                if not cliente_id and cliente_nome:
                    cliente = self.db.query(Cliente).filter(Cliente.nome == cliente_nome).first()
                    if cliente:
                        cliente_id = cliente.id
                        self.clientes_cache[cliente_nome] = cliente_id

                # Parse datas
                data_inicio = self.parse_date(projeto_data.get('data_inicio'))
                data_fim = self.parse_date(projeto_data.get('data_fim'))
                data_faturacao = self.parse_date(projeto_data.get('data_faturacao'))
                data_vencimento = self.parse_date(projeto_data.get('data_vencimento'))

                # Nota: data_recebimento não existe no modelo Projeto
                # Se fornecida, usar como data_faturacao se estado=RECEBIDO
                data_recebimento = self.parse_date(projeto_data.get('data_recebimento'))

                # Parse estado
                estado_str = projeto_data.get('estado', 'NAO_FATURADO')
                try:
                    estado = EstadoProjeto[estado_str]
                except:
                    estado = EstadoProjeto.NAO_FATURADO

                # Se projeto RECEBIDO e tem data_recebimento mas não tem data_faturacao
                if estado == EstadoProjeto.RECEBIDO and data_recebimento and not data_faturacao:
                    data_faturacao = data_recebimento

                success, projeto, msg = self.projetos_manager.criar(
                    tipo=tipo,
                    cliente_id=cliente_id,
                    descricao=projeto_data.get('descricao', ''),
                    valor_sem_iva=projeto_data.get('valor_sem_iva', 0),
                    data_inicio=data_inicio,
                    data_fim=data_fim,
                    data_faturacao=data_faturacao,
                    data_vencimento=data_vencimento,
                    premio_bruno=projeto_data.get('premio_bruno', 0),
                    premio_rafael=projeto_data.get('premio_rafael', 0),
                    estado=estado,
                    nota=projeto_data.get('nota')
                )

                if success:
                    print(f"   ✅ {projeto.numero} - {projeto.descricao[:40]}")
                    self.projetos_cache[projeto.descricao] = projeto.id
                    self.stats['projetos']['ok'] += 1
                else:
                    print(f"   ❌ Projeto #{idx}: {msg}")
                    self.errors.append(f"Projeto #{idx}: {msg}")
                    self.stats['projetos']['erro'] += 1

            except Exception as e:
                print(f"   ❌ Projeto #{idx}: {str(e)}")
                self.errors.append(f"Projeto #{idx}: {str(e)}")
                self.stats['projetos']['erro'] += 1

    def import_despesas(self, despesas_data):
        """Import despesas"""
        print("\n💸 Importando Despesas...")

        for idx, despesa_data in enumerate(despesas_data, 1):
            try:
                # Parse tipo
                tipo_str = despesa_data.get('tipo', 'FIXA_MENSAL')
                try:
                    tipo = TipoDespesa[tipo_str]
                except:
                    tipo = TipoDespesa.FIXA_MENSAL

                # Parse data
                data = self.parse_date(despesa_data.get('data'))
                if not data:
                    data = date.today()

                # Find credor
                credor_nome = despesa_data.get('credor_nome')
                credor_id = self.fornecedores_cache.get(credor_nome)
                if not credor_id and credor_nome:
                    credor = self.db.query(Fornecedor).filter(Fornecedor.nome == credor_nome).first()
                    if credor:
                        credor_id = credor.id
                        self.fornecedores_cache[credor_nome] = credor_id

                # Find projeto
                projeto_desc = despesa_data.get('projeto_descricao')
                projeto_id = self.projetos_cache.get(projeto_desc)
                if not projeto_id and projeto_desc:
                    projeto = self.db.query(Projeto).filter(Projeto.descricao == projeto_desc).first()
                    if projeto:
                        projeto_id = projeto.id
                        self.projetos_cache[projeto_desc] = projeto_id

                # Parse estado
                estado_str = despesa_data.get('estado', 'ATIVO')
                try:
                    estado = EstadoDespesa[estado_str]
                except:
                    estado = EstadoDespesa.ATIVO

                # Parse data pagamento
                data_pagamento = self.parse_date(despesa_data.get('data_pagamento'))

                success, despesa, msg = self.despesas_manager.criar(
                    tipo=tipo,
                    data=data,
                    credor_id=credor_id,
                    projeto_id=projeto_id,
                    descricao=despesa_data.get('descricao', ''),
                    valor_sem_iva=despesa_data.get('valor_sem_iva', 0),
                    valor_com_iva=despesa_data.get('valor_com_iva', 0),
                    estado=estado,
                    data_pagamento=data_pagamento,
                    nota=despesa_data.get('nota')
                )

                if success:
                    print(f"   ✅ {despesa.numero} - {despesa.descricao[:40]}")
                    self.stats['despesas']['ok'] += 1
                else:
                    print(f"   ❌ Despesa #{idx}: {msg}")
                    self.errors.append(f"Despesa #{idx}: {msg}")
                    self.stats['despesas']['erro'] += 1

            except Exception as e:
                print(f"   ❌ Despesa #{idx}: {str(e)}")
                self.errors.append(f"Despesa #{idx}: {str(e)}")
                self.stats['despesas']['erro'] += 1

    def import_boletins(self, boletins_data):
        """Import boletins"""
        print("\n📄 Importando Boletins...")

        for idx, boletim_data in enumerate(boletins_data, 1):
            try:
                # Parse socio
                socio_str = boletim_data.get('socio', 'BRUNO')
                try:
                    socio = Socio[socio_str]
                except:
                    socio = Socio.BRUNO

                # Parse datas
                data_emissao = self.parse_date(boletim_data.get('data_emissao'))
                if not data_emissao:
                    data_emissao = date.today()

                data_pagamento = self.parse_date(boletim_data.get('data_pagamento'))

                # Parse estado
                estado_str = boletim_data.get('estado', 'PENDENTE')
                try:
                    estado = EstadoBoletim[estado_str]
                except:
                    estado = EstadoBoletim.PENDENTE

                success, boletim, msg = self.boletins_manager.emitir(
                    socio=socio,
                    data_emissao=data_emissao,
                    valor=boletim_data.get('valor', 0),
                    descricao=boletim_data.get('descricao', ''),
                    nota=boletim_data.get('nota')
                )

                if success:
                    # Se já estava pago, marcar como pago
                    if estado == EstadoBoletim.PAGO and data_pagamento:
                        self.boletins_manager.marcar_como_pago(boletim.id, data_pagamento)

                    print(f"   ✅ {boletim.numero} - {socio.value} - €{boletim.valor}")
                    self.stats['boletins']['ok'] += 1
                else:
                    print(f"   ❌ Boletim #{idx}: {msg}")
                    self.errors.append(f"Boletim #{idx}: {msg}")
                    self.stats['boletins']['erro'] += 1

            except Exception as e:
                print(f"   ❌ Boletim #{idx}: {str(e)}")
                self.errors.append(f"Boletim #{idx}: {str(e)}")
                self.stats['boletins']['erro'] += 1

    def print_summary(self):
        """Print import summary"""
        print("\n" + "=" * 70)
        print("📊 RESUMO DA IMPORTAÇÃO")
        print("=" * 70)

        for entity, stats in self.stats.items():
            total = stats['ok'] + stats['erro']
            if total > 0:
                print(f"\n{entity.upper()}:")
                print(f"   ✅ Sucesso: {stats['ok']}")
                if stats['erro'] > 0:
                    print(f"   ❌ Erros: {stats['erro']}")
                print(f"   📊 Total: {total}")

        if self.errors:
            print(f"\n⚠️  {len(self.errors)} erro(s) encontrado(s):")
            for error in self.errors[:10]:  # Show first 10 errors
                print(f"   • {error}")
            if len(self.errors) > 10:
                print(f"   ... e mais {len(self.errors) - 10} erro(s)")

        print("\n" + "=" * 70)


def main():
    """Main function"""
    print("=" * 70)
    print("📥 IMPORTAÇÃO DE DADOS DO EXCEL")
    print("=" * 70)

    # Check if JSON file exists
    json_file = Path("dados_excel.json")
    if not json_file.exists():
        print("\n❌ Ficheiro 'dados_excel.json' não encontrado!")
        print("\n📋 Instruções:")
        print("   1. Usa o Claude Chat para gerar o JSON do teu Excel")
        print("   2. Guarda o JSON como 'dados_excel.json' nesta pasta")
        print("   3. Executa este script novamente")
        print("\n")
        sys.exit(1)

    # Load JSON
    print("\n📖 A ler ficheiro JSON...")
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"   ✅ JSON carregado com sucesso")
    except Exception as e:
        print(f"   ❌ Erro ao ler JSON: {e}")
        sys.exit(1)

    # Show what will be imported
    print("\n📋 Dados a importar:")
    print(f"   • Clientes: {len(data.get('clientes', []))}")
    print(f"   • Fornecedores: {len(data.get('fornecedores', []))}")
    print(f"   • Projetos: {len(data.get('projetos', []))}")
    print(f"   • Despesas: {len(data.get('despesas', []))}")
    print(f"   • Boletins: {len(data.get('boletins', []))}")

    if 'mapeamento_explicacao' in data:
        print(f"\n📝 Notas do mapeamento:")
        explicacao = data['mapeamento_explicacao'].get('descricao', '')
        if explicacao:
            # Print first 200 chars
            print(f"   {explicacao[:200]}...")

    # Confirm
    print("\n⚠️  ATENÇÃO: Esta operação vai adicionar dados à base de dados!")
    response = input("\nContinuar? (sim/não): ").strip().lower()
    if response not in ['sim', 's', 'yes', 'y']:
        print("\n❌ Importação cancelada.")
        sys.exit(0)

    # Ask if should clear existing data
    print("\n🗑️  Limpar TODOS os dados existentes antes de importar?")
    print("   ⚠️  Isto vai APAGAR:")
    print("      • Todos os clientes")
    print("      • Todos os fornecedores")
    print("      • Todos os projetos")
    print("      • Todas as despesas")
    print("      • Todos os boletins")
    print("   ✅ Isto NÃO vai apagar:")
    print("      • Utilizadores (Bruno e Rafael)")

    clear_response = input("\nLimpar tudo? (sim/não): ").strip().lower()
    clear_all = clear_response in ['sim', 's', 'yes', 'y']

    # Setup database
    database_url = os.getenv("DATABASE_URL", "sqlite:///./agora_media.db")
    engine = create_engine(database_url)
    Session = sessionmaker(bind=engine)
    session = Session()

    # Clear existing data if requested
    if clear_all:
        print("\n🗑️  A limpar dados existentes...")
        try:
            # Delete in reverse order (to respect foreign keys)
            deleted_boletins = session.query(Boletim).delete()
            deleted_despesas = session.query(Despesa).delete()
            deleted_projetos = session.query(Projeto).delete()
            deleted_fornecedores = session.query(Fornecedor).delete()
            deleted_clientes = session.query(Cliente).delete()

            session.commit()

            print(f"   ✅ Apagados:")
            print(f"      • {deleted_boletins} boletim(ns)")
            print(f"      • {deleted_despesas} despesa(s)")
            print(f"      • {deleted_projetos} projeto(s)")
            print(f"      • {deleted_fornecedores} fornecedor(es)")
            print(f"      • {deleted_clientes} cliente(s)")
        except Exception as e:
            print(f"   ❌ Erro ao limpar dados: {e}")
            session.rollback()
            sys.exit(1)

    # Import data
    importer = DataImporter(session)

    try:
        # Import in order (clientes/fornecedores first, then projetos, then despesas/boletins)
        if data.get('clientes'):
            importer.import_clientes(data['clientes'])

        if data.get('fornecedores'):
            importer.import_fornecedores(data['fornecedores'])

        if data.get('projetos'):
            importer.import_projetos(data['projetos'])

        if data.get('despesas'):
            importer.import_despesas(data['despesas'])

        if data.get('boletins'):
            importer.import_boletins(data['boletins'])

        # Print summary
        importer.print_summary()

        print("\n✅ Importação concluída!")
        print("\n💡 Podes agora executar: python3 main.py")

    except Exception as e:
        print(f"\n❌ Erro durante importação: {e}")
        session.rollback()
        sys.exit(1)
    finally:
        session.close()


if __name__ == "__main__":
    main()
