#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de importação DIRETA do Excel CONTABILIDADE_FINAL.xlsx - VERSÃO CORRIGIDA

Lógica correta baseada em análise detalhada:

PROJETOS:
- Tipo: Se coluna 14 tem "Pessoal", usar coluna 15 (owner) para PESSOAL_BRUNO/RAFAEL, senão EMPRESA
- Estado: data_recebimento → RECEBIDO, data_faturacao → FATURADO, senão NAO_FATURADO

DESPESAS:
- Ordenados (tipo "Ordenado"): Despesas fixas mensais, credor indica de quem é
- Fixas Mensais: Periodicidade "Mensal" (88 despesas)
- Prémios: Despesas com tipo contendo "Prémio" (26 despesas)

FORNECEDORES:
- Agora com campo 'pais' para cálculo de IVA
"""
import sys
import os
from datetime import datetime, date
from decimal import Decimal
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Import models
from database.models import (
    Cliente, Fornecedor, Projeto, Despesa, Boletim,
    TipoProjeto, EstadoProjeto,
    TipoDespesa, EstadoDespesa,
    EstatutoFornecedor, Socio, EstadoBoletim
)

# Import managers
from logic.clientes import ClientesManager
from logic.fornecedores import FornecedoresManager
from logic.projetos import ProjetosManager
from logic.despesas import DespesasManager
from logic.boletins import BoletinsManager


class ExcelImporter:
    """Importador direto do Excel - LÓGICA CORRIGIDA"""

    def __init__(self, session, excel_path='CONTABILIDADE_FINAL.xlsx'):
        self.excel_path = excel_path
        self.xl = None
        self.session = session

        # Managers
        self.clientes_manager = ClientesManager(session)
        self.fornecedores_manager = FornecedoresManager(session)
        self.projetos_manager = ProjetosManager(session)
        self.despesas_manager = DespesasManager(session)
        self.boletins_manager = BoletinsManager(session)

        # Mapeamentos
        self.clientes_map = {}
        self.fornecedores_map = {}
        self.projetos_map = {}

        # Estatísticas
        self.stats = {
            'clientes': {'total': 0, 'sucesso': 0, 'erro': 0},
            'fornecedores': {'total': 0, 'sucesso': 0, 'erro': 0},
            'projetos': {'total': 0, 'sucesso': 0, 'erro': 0},
            'despesas': {'total': 0, 'sucesso': 0, 'erro': 0},
            'despesas_fixas_pagas': 0,
            'ordenados': 0,
            'premios': {'bruno': Decimal('0'), 'rafael': Decimal('0')},
        }

        # Data de hoje para marcar fixas como PAGO
        self.hoje = date(2025, 10, 29)

    def parse_date(self, value):
        """Converte valor para date"""
        if pd.isna(value):
            return None
        if isinstance(value, datetime):
            return value.date()
        if isinstance(value, date):
            return value
        if isinstance(value, str):
            try:
                return datetime.strptime(value, "%Y-%m-%d").date()
            except:
                try:
                    return datetime.strptime(value, "%Y-%m-%d %H:%M:%S").date()
                except:
                    return None
        return None

    def safe_str(self, value):
        """Converte para string segura"""
        if pd.isna(value):
            return None
        return str(value).strip() if str(value).strip() else None

    def safe_decimal(self, value):
        """Converte para Decimal seguro"""
        if pd.isna(value):
            return None
        try:
            return Decimal(str(value))
        except:
            return None

    def safe_int(self, value):
        """Converte para int seguro"""
        if pd.isna(value):
            return None
        try:
            return int(float(value))
        except:
            return None

    def mapear_estatuto_fornecedor(self, estatuto_str):
        """Mapeia estatuto do Excel para enum"""
        if pd.isna(estatuto_str):
            return EstatutoFornecedor.FREELANCER

        estatuto = str(estatuto_str).upper().strip()

        if 'EMPRESA' in estatuto:
            return EstatutoFornecedor.EMPRESA
        elif 'FREELANCER' in estatuto or 'FREELANCE' in estatuto:
            return EstatutoFornecedor.FREELANCER
        elif 'ESTADO' in estatuto or 'BANCO' in estatuto:
            return EstatutoFornecedor.ESTADO
        else:
            return EstatutoFornecedor.FREELANCER

    def mapear_tipo_projeto(self, estado_str, owner_str):
        """
        Mapeia tipo de projeto - LÓGICA CORRETA

        Se coluna 14 (estado_str) contém "Pessoal":
          - Usar coluna 15 (owner_str) para determinar PESSOAL_BRUNO ou PESSOAL_RAFAEL
        Senão:
          - EMPRESA
        """
        if not pd.isna(estado_str):
            estado = str(estado_str).lower()
            if 'pessoal' in estado:
                # É projeto pessoal, ver de quem
                if not pd.isna(owner_str):
                    owner = str(owner_str).lower()
                    if 'bruno' in owner:
                        return TipoProjeto.PESSOAL_BRUNO
                    elif 'rafael' in owner:
                        return TipoProjeto.PESSOAL_RAFAEL
                # Default se não conseguir determinar
                return TipoProjeto.EMPRESA

        # Se não é "Pessoal", é da empresa
        return TipoProjeto.EMPRESA

    def mapear_estado_projeto(self, data_recebimento, data_faturacao):
        """
        Mapeia estado do projeto - LÓGICA CORRETA

        - Se tem data_recebimento → RECEBIDO
        - Senão, se tem data_faturacao → FATURADO
        - Senão → NAO_FATURADO
        """
        if data_recebimento:
            return EstadoProjeto.RECEBIDO
        elif data_faturacao:
            return EstadoProjeto.FATURADO
        else:
            return EstadoProjeto.NAO_FATURADO

    def importar_clientes(self):
        """Importa clientes"""
        print("\n" + "=" * 80)
        print("📋 IMPORTANDO CLIENTES")
        print("=" * 80)

        df = pd.read_excel(self.xl, sheet_name='CLIENTES', header=1)

        # Filtrar apenas linhas de dados (começam com #C)
        df_dados = df[df.iloc[:, 0].astype(str).str.startswith('#C', na=False)]

        print(f"Total de clientes: {len(df_dados)}")

        for idx, row in df_dados.iterrows():
            numero = self.safe_str(row.iloc[0])
            nome = self.safe_str(row.iloc[1])

            if not nome:
                continue

            self.stats['clientes']['total'] += 1

            nif = self.safe_str(row.iloc[2])
            morada = self.safe_str(row.iloc[3])
            pais = self.safe_str(row.iloc[4])
            angariacao = self.safe_str(row.iloc[5])
            nota = self.safe_str(row.iloc[7]) if len(row) > 7 else None

            try:
                success, cliente, msg = self.clientes_manager.criar(
                    nome=nome,
                    nif=nif,
                    morada=morada,
                    pais=pais,
                    angariacao=angariacao,
                    nota=nota
                )

                if success:
                    self.stats['clientes']['sucesso'] += 1
                    self.clientes_map[nome] = cliente
                    print(f"  ✅ {numero}: {nome}")
                else:
                    self.stats['clientes']['erro'] += 1
                    print(f"  ❌ {numero}: {nome} - {msg}")

            except Exception as e:
                self.stats['clientes']['erro'] += 1
                print(f"  ❌ {numero}: {nome} - Erro: {e}")

        print(f"\n✅ Clientes: {self.stats['clientes']['sucesso']}/{self.stats['clientes']['total']}")

    def importar_fornecedores(self):
        """Importa fornecedores"""
        print("\n" + "=" * 80)
        print("📋 IMPORTANDO FORNECEDORES")
        print("=" * 80)

        df = pd.read_excel(self.xl, sheet_name='FORNECEDORES', header=1)

        # Filtrar apenas linhas de dados
        df_dados = df[df.iloc[:, 0].astype(str).str.startswith('#F', na=False)]

        print(f"Total de fornecedores: {len(df_dados)}")

        for idx, row in df_dados.iterrows():
            numero = self.safe_str(row.iloc[0])
            nome = self.safe_str(row.iloc[1])

            if not nome:
                continue

            self.stats['fornecedores']['total'] += 1

            estatuto_str = self.safe_str(row.iloc[2])
            estatuto = self.mapear_estatuto_fornecedor(estatuto_str)
            area = self.safe_str(row.iloc[3])
            funcao = self.safe_str(row.iloc[4])
            classificacao_str = self.safe_str(row.iloc[5])

            # Classificação: converter "*" em número
            classificacao = None
            if classificacao_str:
                classificacao = classificacao_str.count('*')
                if classificacao > 5:
                    classificacao = 5

            validade_seguro = self.parse_date(row.iloc[6]) if len(row) > 6 else None
            nif = self.safe_str(row.iloc[7]) if len(row) > 7 else None
            iban = self.safe_str(row.iloc[8]) if len(row) > 8 else None
            morada = self.safe_str(row.iloc[9]) if len(row) > 9 else None
            pais = self.safe_str(row.iloc[10]) if len(row) > 10 else None
            contacto = self.safe_str(row.iloc[11]) if len(row) > 11 else None
            email = self.safe_str(row.iloc[12]) if len(row) > 12 else None
            nota = self.safe_str(row.iloc[13]) if len(row) > 13 else None

            try:
                success, fornecedor, msg = self.fornecedores_manager.criar(
                    nome=nome,
                    estatuto=estatuto,
                    area=area,
                    funcao=funcao,
                    classificacao=classificacao,
                    nif=nif,
                    iban=iban,
                    morada=morada,
                    pais=pais,  # ✅ Agora funciona!
                    contacto=contacto,
                    email=email,
                    validade_seguro_trabalho=validade_seguro,
                    nota=nota
                )

                if success:
                    self.stats['fornecedores']['sucesso'] += 1
                    self.fornecedores_map[nome] = fornecedor
                    print(f"  ✅ {numero}: {nome}")
                else:
                    self.stats['fornecedores']['erro'] += 1
                    print(f"  ❌ {numero}: {nome} - {msg}")

            except Exception as e:
                self.stats['fornecedores']['erro'] += 1
                print(f"  ❌ {numero}: {nome} - Erro: {e}")

        print(f"\n✅ Fornecedores: {self.stats['fornecedores']['sucesso']}/{self.stats['fornecedores']['total']}")

    def importar_projetos(self):
        """Importa projetos - LÓGICA CORRIGIDA"""
        print("\n" + "=" * 80)
        print("📋 IMPORTANDO PROJETOS")
        print("=" * 80)

        df = pd.read_excel(self.xl, sheet_name='PROJETOS', header=3)

        # Filtrar linhas de dados
        df_dados = df[df.iloc[:, 0].astype(str).str.startswith('#P', na=False)]

        print(f"Total de projetos: {len(df_dados)}")

        for idx, row in df_dados.iterrows():
            numero = self.safe_str(row.iloc[0])
            cliente_nome = self.safe_str(row.iloc[1])
            descricao = self.safe_str(row.iloc[4])

            if not descricao:
                continue

            self.stats['projetos']['total'] += 1

            # Datas
            data_inicio = self.parse_date(row.iloc[2])
            data_fim = self.parse_date(row.iloc[3])
            valor_sem_iva = self.safe_decimal(row.iloc[5])
            data_faturacao = self.parse_date(row.iloc[6])
            data_vencimento = self.parse_date(row.iloc[7])
            data_recebimento = self.parse_date(row.iloc[8])

            # LÓGICA CORRETA: Coluna 14 (estado/tipo), Coluna 15 (owner)
            estado_str = self.safe_str(row.iloc[14]) if len(row) > 14 else None
            owner_str = self.safe_str(row.iloc[15]) if len(row) > 15 else None
            nota = self.safe_str(row.iloc[16]) if len(row) > 16 else None

            # Mapear tipo e estado
            tipo = self.mapear_tipo_projeto(estado_str, owner_str)
            estado = self.mapear_estado_projeto(data_recebimento, data_faturacao)

            # Se RECEBIDO e tem data_recebimento mas não tem data_faturacao, usar recebimento
            if estado == EstadoProjeto.RECEBIDO and data_recebimento and not data_faturacao:
                data_faturacao = data_recebimento

            # Cliente ID
            cliente_id = None
            if cliente_nome and cliente_nome in self.clientes_map:
                cliente_id = self.clientes_map[cliente_nome].id

            # Prémios (por enquanto 0)
            premio_bruno = Decimal('0')
            premio_rafael = Decimal('0')

            try:
                success, projeto, msg = self.projetos_manager.criar(
                    tipo=tipo,
                    cliente_id=cliente_id,
                    descricao=descricao,
                    valor_sem_iva=valor_sem_iva,
                    data_inicio=data_inicio,
                    data_fim=data_fim,
                    data_faturacao=data_faturacao,
                    data_vencimento=data_vencimento,
                    premio_bruno=premio_bruno,
                    premio_rafael=premio_rafael,
                    estado=estado,
                    nota=nota
                )

                if success:
                    self.stats['projetos']['sucesso'] += 1
                    self.projetos_map[numero] = projeto
                    tipo_icon = "🏢" if tipo == TipoProjeto.EMPRESA else ("👤B" if tipo == TipoProjeto.PESSOAL_BRUNO else "👤R")
                    estado_icon = "✅" if estado == EstadoProjeto.RECEBIDO else ("📄" if estado == EstadoProjeto.FATURADO else "⏳")
                    print(f"  {estado_icon} {numero}: {tipo_icon} {descricao[:45]}")
                else:
                    self.stats['projetos']['erro'] += 1
                    print(f"  ❌ {numero}: {descricao[:45]} - {msg}")

            except Exception as e:
                self.stats['projetos']['erro'] += 1
                print(f"  ❌ {numero}: {descricao[:45]} - Erro: {e}")

        print(f"\n✅ Projetos: {self.stats['projetos']['sucesso']}/{self.stats['projetos']['total']}")

    def importar_despesas(self):
        """Importa despesas - LÓGICA CORRIGIDA"""
        print("\n" + "=" * 80)
        print("📋 IMPORTANDO DESPESAS")
        print("=" * 80)

        df = pd.read_excel(self.xl, sheet_name='DESPESAS', header=5)

        # Filtrar linhas de dados
        df_dados = df[df.iloc[:, 0].astype(str).str.startswith('#D', na=False)]

        print(f"Total de despesas: {len(df_dados)}")

        for idx, row in df_dados.iterrows():
            numero = self.safe_str(row.iloc[0])
            credor_nome = self.safe_str(row.iloc[4])
            tipo_str = self.safe_str(row.iloc[6])
            descricao = self.safe_str(row.iloc[7])

            if not descricao:
                continue

            self.stats['despesas']['total'] += 1

            # Data
            ano = self.safe_int(row.iloc[1])
            mes = self.safe_int(row.iloc[2])
            dia = self.safe_int(row.iloc[3])

            data_vencimento = None
            if ano and mes and dia:
                try:
                    data_vencimento = date(ano, mes, dia)
                except:
                    data_vencimento = None

            if not data_vencimento and len(row) > 19:
                data_vencimento = self.parse_date(row.iloc[19])

            projeto_numero = self.safe_str(row.iloc[5])
            periodicidade = self.safe_str(row.iloc[8])
            valor_sem_iva = self.safe_decimal(row.iloc[9])
            valor_com_iva = self.safe_decimal(row.iloc[12])
            nota = self.safe_str(row.iloc[22]) if len(row) > 22 else None

            # LÓGICA CORRIGIDA para determinar tipo
            tipo = None
            eh_premio = False
            eh_ordenado = False

            # 1. Verificar se é Prémio
            if tipo_str and ('prém' in str(tipo_str).lower() or 'premio' in str(tipo_str).lower()):
                eh_premio = True
                # Prémios são despesas pessoais - determinar de quem pelo credor
                if 'bruno' in str(credor_nome).lower():
                    tipo = TipoDespesa.PESSOAL_BRUNO
                elif 'rafael' in str(credor_nome).lower():
                    tipo = TipoDespesa.PESSOAL_RAFAEL
                else:
                    tipo = TipoDespesa.PROJETO

            # 2. Verificar se é Ordenado
            elif tipo_str and 'ordenado' in str(tipo_str).lower():
                eh_ordenado = True
                tipo = TipoDespesa.FIXA_MENSAL
                self.stats['ordenados'] += 1

            # 3. Verificar se é Fixa Mensal (periodicidade "Mensal")
            elif periodicidade and 'mensal' in str(periodicidade).lower():
                tipo = TipoDespesa.FIXA_MENSAL

            # 4. Verificar se é Equipamento
            elif tipo_str and 'equipamento' in str(tipo_str).lower():
                tipo = TipoDespesa.EQUIPAMENTO

            # 5. Default: PROJETO
            else:
                tipo = TipoDespesa.PROJETO

            # Estado: Fixas mensais vencidas → PAGO
            estado = EstadoDespesa.ATIVO
            data_pagamento = None

            if tipo == TipoDespesa.FIXA_MENSAL and data_vencimento and data_vencimento <= self.hoje:
                estado = EstadoDespesa.PAGO
                data_pagamento = data_vencimento
                self.stats['despesas_fixas_pagas'] += 1

            # Credor/Fornecedor ID
            credor_id = None
            if credor_nome and credor_nome in self.fornecedores_map:
                credor_id = self.fornecedores_map[credor_nome].id

            # Projeto ID
            projeto_id = None
            if projeto_numero and projeto_numero in self.projetos_map:
                projeto_id = self.projetos_map[projeto_numero].id

            try:
                success, despesa, msg = self.despesas_manager.criar(
                    tipo=tipo,
                    data=data_vencimento,
                    credor_id=credor_id,
                    projeto_id=projeto_id,
                    descricao=descricao,
                    valor_sem_iva=valor_sem_iva,
                    valor_com_iva=valor_com_iva,
                    estado=estado,
                    data_pagamento=data_pagamento,
                    nota=nota
                )

                if success:
                    self.stats['despesas']['sucesso'] += 1

                    # Acumular prémios
                    if eh_premio and valor_sem_iva:
                        if tipo == TipoDespesa.PESSOAL_BRUNO:
                            self.stats['premios']['bruno'] += valor_sem_iva
                        elif tipo == TipoDespesa.PESSOAL_RAFAEL:
                            self.stats['premios']['rafael'] += valor_sem_iva

                    tipo_icon = "🔧" if tipo == TipoDespesa.FIXA_MENSAL else ("🏆" if eh_premio else ("💰" if eh_ordenado else "💸"))
                    print(f"  ✅ {numero}: {tipo_icon} {descricao[:42]}")
                else:
                    self.stats['despesas']['erro'] += 1
                    print(f"  ❌ {numero}: {descricao[:42]} - {msg}")

            except Exception as e:
                self.stats['despesas']['erro'] += 1
                print(f"  ❌ {numero}: {descricao[:42]} - Erro: {e}")

        print(f"\n✅ Despesas: {self.stats['despesas']['sucesso']}/{self.stats['despesas']['total']}")
        print(f"   🔧 Despesas fixas marcadas PAGO: {self.stats['despesas_fixas_pagas']}")
        print(f"   💰 Ordenados: {self.stats['ordenados']}")
        print(f"   🏆 Prémios Bruno: €{float(self.stats['premios']['bruno']):,.2f}")
        print(f"   🏆 Prémios Rafael: €{float(self.stats['premios']['rafael']):,.2f}")

    def executar(self, limpar_tudo=False):
        """Executa importação completa"""
        print("=" * 80)
        print("📊 IMPORTAÇÃO DIRETA DO EXCEL - LÓGICA CORRIGIDA")
        print("=" * 80)
        print(f"Ficheiro: {self.excel_path}")
        print()

        # Abrir Excel
        print("📖 A abrir Excel...")
        try:
            self.xl = pd.ExcelFile(self.excel_path)
            print(f"   ✅ Excel aberto ({len(self.xl.sheet_names)} abas)")
        except Exception as e:
            print(f"   ❌ Erro ao abrir Excel: {e}")
            return False

        # Limpar dados
        if limpar_tudo:
            print("\n⚠️  A LIMPAR TODOS OS DADOS...")
            try:
                self.session.query(Boletim).delete()
                self.session.query(Despesa).delete()
                self.session.query(Projeto).delete()
                self.session.query(Fornecedor).delete()
                self.session.query(Cliente).delete()
                self.session.commit()
                print("   ✅ Dados limpos")
            except Exception as e:
                self.session.rollback()
                print(f"   ❌ Erro ao limpar: {e}")
                return False

        # Importar
        try:
            self.importar_clientes()
            self.importar_fornecedores()
            self.importar_projetos()
            self.importar_despesas()

            # Resumo
            print("\n" + "=" * 80)
            print("📊 RESUMO DA IMPORTAÇÃO")
            print("=" * 80)
            print(f"✅ Clientes: {self.stats['clientes']['sucesso']}/{self.stats['clientes']['total']}")
            print(f"✅ Fornecedores: {self.stats['fornecedores']['sucesso']}/{self.stats['fornecedores']['total']}")
            print(f"✅ Projetos: {self.stats['projetos']['sucesso']}/{self.stats['projetos']['total']}")
            print(f"✅ Despesas: {self.stats['despesas']['sucesso']}/{self.stats['despesas']['total']}")
            print()
            print(f"💰 Ordenados: {self.stats['ordenados']}")
            print(f"🏆 Prémios Bruno: €{float(self.stats['premios']['bruno']):,.2f}")
            print(f"🏆 Prémios Rafael: €{float(self.stats['premios']['rafael']):,.2f}")
            print()
            print("=" * 80)
            print("✅ IMPORTAÇÃO CONCLUÍDA!")
            print("=" * 80)
            print()
            print("Próximo passo:")
            print("  → Abrir a app: python3 main.py")
            print("  → Verificar dashboard 'Saldos Pessoais'")
            print()

            return True

        except Exception as e:
            print(f"\n❌ Erro durante importação: {e}")
            import traceback
            traceback.print_exc()
            return False


def main():
    print("=" * 80)
    print("🚀 IMPORTAÇÃO DIRETA DO EXCEL - VERSÃO CORRIGIDA")
    print("=" * 80)
    print()

    resposta = input("Limpar todos os dados antes? (sim/não): ").strip().lower()
    limpar = resposta in ['sim', 's', 'yes', 'y']

    if limpar:
        print("\n⚠️  ATENÇÃO: Todos os dados serão apagados!")
        confirma = input("Tem certeza? (sim/não): ").strip().lower()
        if confirma not in ['sim', 's', 'yes', 'y']:
            print("❌ Cancelado!")
            return

    print()

    # Setup database
    database_url = os.getenv("DATABASE_URL", "sqlite:///./agora_media.db")
    engine = create_engine(database_url)
    Session = sessionmaker(bind=engine)
    session = Session()

    # Executar
    importer = ExcelImporter(session)
    success = importer.executar(limpar_tudo=limpar)

    if not success:
        sys.exit(1)


if __name__ == '__main__':
    main()
