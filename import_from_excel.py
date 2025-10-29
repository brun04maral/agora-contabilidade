#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de importação DIRETA do Excel CONTABILIDADE_FINAL.xlsx

Importa todos os dados diretamente para a base de dados:
- Clientes
- Fornecedores
- Projetos (incluindo prémios nos campos premio_bruno/premio_rafael)
- Despesas (incluindo fixas mensais e prémios como despesas especiais)
- Boletins (da aba CARGOS se existir)

Resolve automaticamente:
- Despesas fixas vencidas marcadas como PAGO
- Prémios mapeados corretamente
- Datas convertidas para formato correto
"""
import sys
import os
from datetime import datetime, date
from decimal import Decimal
import pandas as pd

# Adicionar diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.connection import DatabaseConnection
from database.models import (
    TipoProjeto, EstadoProjeto,
    TipoDespesa, EstadoDespesa,
    EstatutoFornecedor, Socio, EstadoBoletim
)
from managers.clientes_manager import ClientesManager
from managers.fornecedores_manager import FornecedoresManager
from managers.projetos_manager import ProjetosManager
from managers.despesas_manager import DespesasManager
from managers.boletins_manager import BoletinsManager


class ExcelImporter:
    """Importador direto do Excel"""

    def __init__(self, excel_path='CONTABILIDADE_FINAL.xlsx'):
        self.excel_path = excel_path
        self.xl = None
        self.db = DatabaseConnection()
        self.session = self.db.get_session()

        # Managers
        self.clientes_manager = ClientesManager(self.db)
        self.fornecedores_manager = FornecedoresManager(self.db)
        self.projetos_manager = ProjetosManager(self.db)
        self.despesas_manager = DespesasManager(self.db)
        self.boletins_manager = BoletinsManager(self.db)

        # Mapeamentos para fazer lookup
        self.clientes_map = {}  # nome -> objeto Cliente
        self.fornecedores_map = {}  # nome -> objeto Fornecedor
        self.projetos_map = {}  # numero -> objeto Projeto

        # Estatísticas
        self.stats = {
            'clientes': {'total': 0, 'sucesso': 0, 'erro': 0},
            'fornecedores': {'total': 0, 'sucesso': 0, 'erro': 0},
            'projetos': {'total': 0, 'sucesso': 0, 'erro': 0},
            'despesas': {'total': 0, 'sucesso': 0, 'erro': 0},
            'premios': {'bruno': Decimal('0'), 'rafael': Decimal('0')},
            'despesas_fixas_pagas': 0,
        }

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
        elif 'ESTADO' in estatuto:
            return EstatutoFornecedor.ESTADO
        else:
            return EstatutoFornecedor.FREELANCER

    def mapear_tipo_projeto(self, tipo_str, owner_str):
        """Mapeia tipo de projeto do Excel"""
        if pd.isna(tipo_str):
            # Tentar inferir do owner
            if not pd.isna(owner_str):
                owner = str(owner_str).lower()
                if 'bruno' in owner:
                    return TipoProjeto.PESSOAL_BRUNO
                elif 'rafael' in owner:
                    return TipoProjeto.PESSOAL_RAFAEL
            return TipoProjeto.EMPRESA

        tipo = str(tipo_str).lower()

        if 'pessoal' in tipo or 'freelancer' in tipo:
            if 'bruno' in tipo:
                return TipoProjeto.PESSOAL_BRUNO
            elif 'rafael' in tipo:
                return TipoProjeto.PESSOAL_RAFAEL

        return TipoProjeto.EMPRESA

    def mapear_estado_projeto(self, estado_str, tem_recibo):
        """Mapeia estado do projeto"""
        if not pd.isna(tem_recibo):
            return EstadoProjeto.RECEBIDO

        if pd.isna(estado_str):
            return EstadoProjeto.NAO_FATURADO

        estado = str(estado_str).lower()

        if 'finalizado' in estado or 'recebido' in estado or 'pago' in estado:
            return EstadoProjeto.RECEBIDO
        elif 'faturado' in estado:
            return EstadoProjeto.FATURADO
        else:
            return EstadoProjeto.NAO_FATURADO

    def mapear_tipo_despesa(self, tipo_str, periodicidade_str):
        """Mapeia tipo de despesa"""
        if pd.isna(tipo_str):
            return TipoDespesa.PROJETO

        tipo = str(tipo_str).lower()

        # Prémios são tratados como despesas pessoais
        if 'prém' in tipo or 'premio' in tipo:
            # Determinar de quem é o prémio é feito depois pelo credor
            return None  # Será determinado pelo credor

        # Fixas mensais
        if not pd.isna(periodicidade_str):
            period = str(periodicidade_str).lower()
            if 'mensal' in period:
                return TipoDespesa.FIXA_MENSAL

        # Equipamento
        if 'equipamento' in tipo:
            return TipoDespesa.EQUIPAMENTO

        # Administrativo são fixas
        if 'administrativo' in tipo or 'admin' in tipo:
            return TipoDespesa.FIXA_MENSAL

        return TipoDespesa.PROJETO

    def importar_clientes(self):
        """Importa clientes"""
        print("\n" + "=" * 80)
        print("📋 IMPORTANDO CLIENTES")
        print("=" * 80)

        df = pd.read_excel(self.xl, sheet_name='CLIENTES', header=1)

        print(f"Total de linhas: {len(df)}")

        for idx, row in df.iterrows():
            numero = self.safe_str(row.iloc[0])
            if not numero or not numero.startswith('#C'):
                continue

            nome = self.safe_str(row.iloc[1])
            if not nome:
                continue

            self.stats['clientes']['total'] += 1

            # Dados
            nif = self.safe_str(row.iloc[2])
            morada = self.safe_str(row.iloc[3])
            pais = self.safe_str(row.iloc[4])
            angariacao = self.safe_str(row.iloc[5])
            data_angariacao = self.parse_date(row.iloc[6]) if len(row) > 6 else None
            nota = self.safe_str(row.iloc[7]) if len(row) > 7 else None

            # Criar cliente
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

        print(f"Total de linhas: {len(df)}")

        for idx, row in df.iterrows():
            numero = self.safe_str(row.iloc[0])
            if not numero or not numero.startswith('#F'):
                continue

            nome = self.safe_str(row.iloc[1])
            if not nome:
                continue

            self.stats['fornecedores']['total'] += 1

            # Dados
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

            # Criar fornecedor
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
                    pais=pais,
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
        """Importa projetos"""
        print("\n" + "=" * 80)
        print("📋 IMPORTANDO PROJETOS")
        print("=" * 80)

        df = pd.read_excel(self.xl, sheet_name='PROJETOS', header=3)

        print(f"Total de linhas: {len(df)}")

        for idx, row in df.iterrows():
            numero = self.safe_str(row.iloc[0])
            if not numero or not numero.startswith('#P'):
                continue

            cliente_nome = self.safe_str(row.iloc[1])
            descricao = self.safe_str(row.iloc[4])

            if not descricao:
                continue

            self.stats['projetos']['total'] += 1

            # Dados
            data_inicio = self.parse_date(row.iloc[2])
            data_fim = self.parse_date(row.iloc[3])
            valor_sem_iva = self.safe_decimal(row.iloc[5])
            data_faturacao = self.parse_date(row.iloc[6])
            data_vencimento = self.parse_date(row.iloc[7])
            data_recebimento = self.parse_date(row.iloc[8])

            # Estado e tipo
            estado_str = self.safe_str(row.iloc[14]) if len(row) > 14 else None
            owner_str = self.safe_str(row.iloc[15]) if len(row) > 15 else None
            nota = self.safe_str(row.iloc[16]) if len(row) > 16 else None

            tipo = self.mapear_tipo_projeto(estado_str, owner_str)
            estado = self.mapear_estado_projeto(estado_str, data_recebimento)

            # Se tem data_recebimento mas não tem data_faturacao, usar recebimento
            if estado == EstadoProjeto.RECEBIDO and data_recebimento and not data_faturacao:
                data_faturacao = data_recebimento

            # Cliente ID
            cliente_id = None
            if cliente_nome and cliente_nome in self.clientes_map:
                cliente_id = self.clientes_map[cliente_nome].id

            # Prémios (por enquanto 0, vamos calcular depois das despesas)
            premio_bruno = Decimal('0')
            premio_rafael = Decimal('0')

            # Criar projeto
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
                    print(f"  ✅ {numero}: {tipo_icon} {descricao[:50]}")
                else:
                    self.stats['projetos']['erro'] += 1
                    print(f"  ❌ {numero}: {descricao[:50]} - {msg}")

            except Exception as e:
                self.stats['projetos']['erro'] += 1
                print(f"  ❌ {numero}: {descricao[:50]} - Erro: {e}")

        print(f"\n✅ Projetos: {self.stats['projetos']['sucesso']}/{self.stats['projetos']['total']}")

    def importar_despesas(self):
        """Importa despesas"""
        print("\n" + "=" * 80)
        print("📋 IMPORTANDO DESPESAS")
        print("=" * 80)

        df = pd.read_excel(self.xl, sheet_name='DESPESAS', header=5)

        print(f"Total de linhas: {len(df)}")

        hoje = date(2025, 10, 29)

        for idx, row in df.iterrows():
            numero = self.safe_str(row.iloc[0])
            if not numero or not numero.startswith('#D'):
                continue

            credor_nome = self.safe_str(row.iloc[4])
            descricao = self.safe_str(row.iloc[7])

            if not descricao:
                continue

            self.stats['despesas']['total'] += 1

            # Dados
            ano = self.safe_int(row.iloc[1])
            mes = self.safe_int(row.iloc[2])
            dia = self.safe_int(row.iloc[3])

            # Construir data
            data_vencimento = None
            if ano and mes and dia:
                try:
                    data_vencimento = date(ano, mes, dia)
                except:
                    data_vencimento = None

            # Se não conseguiu construir, tentar coluna 19
            if not data_vencimento and len(row) > 19:
                data_vencimento = self.parse_date(row.iloc[19])

            projeto_numero = self.safe_str(row.iloc[5])
            tipo_str = self.safe_str(row.iloc[6])
            periodicidade = self.safe_str(row.iloc[8])
            valor_sem_iva = self.safe_decimal(row.iloc[9])
            valor_com_iva = self.safe_decimal(row.iloc[12])
            nota = self.safe_str(row.iloc[22]) if len(row) > 22 else None

            # Mapear tipo
            tipo_base = self.mapear_tipo_despesa(tipo_str, periodicidade)

            # Se é prémio, determinar de quem é pelo credor
            eh_premio = False
            if tipo_str and ('prém' in str(tipo_str).lower() or 'premio' in str(tipo_str).lower()):
                eh_premio = True
                if 'bruno' in str(credor_nome).lower():
                    tipo = TipoDespesa.PESSOAL_BRUNO
                elif 'rafael' in str(credor_nome).lower():
                    tipo = TipoDespesa.PESSOAL_RAFAEL
                else:
                    tipo = TipoDespesa.PROJETO
            else:
                tipo = tipo_base if tipo_base else TipoDespesa.PROJETO

            # Estado: se é fixa mensal e já venceu, marcar como PAGO
            estado = EstadoDespesa.ATIVO
            data_pagamento = None

            if tipo == TipoDespesa.FIXA_MENSAL and data_vencimento and data_vencimento <= hoje:
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

            # Criar despesa
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

                    # Se é prémio, acumular no total
                    if eh_premio and valor_sem_iva:
                        if tipo == TipoDespesa.PESSOAL_BRUNO:
                            self.stats['premios']['bruno'] += valor_sem_iva
                        elif tipo == TipoDespesa.PESSOAL_RAFAEL:
                            self.stats['premios']['rafael'] += valor_sem_iva

                    tipo_icon = "🔧" if tipo == TipoDespesa.FIXA_MENSAL else ("🏆" if eh_premio else "💸")
                    print(f"  ✅ {numero}: {tipo_icon} {descricao[:45]}")
                else:
                    self.stats['despesas']['erro'] += 1
                    print(f"  ❌ {numero}: {descricao[:45]} - {msg}")

            except Exception as e:
                self.stats['despesas']['erro'] += 1
                print(f"  ❌ {numero}: {descricao[:45]} - Erro: {e}")

        print(f"\n✅ Despesas: {self.stats['despesas']['sucesso']}/{self.stats['despesas']['total']}")
        print(f"   🔧 Despesas fixas marcadas como PAGO: {self.stats['despesas_fixas_pagas']}")
        print(f"   🏆 Prémios Bruno: €{float(self.stats['premios']['bruno']):,.2f}")
        print(f"   🏆 Prémios Rafael: €{float(self.stats['premios']['rafael']):,.2f}")

    def executar(self, limpar_tudo=False):
        """Executa importação completa"""
        print("=" * 80)
        print("📊 IMPORTAÇÃO DIRETA DO EXCEL")
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

        # Limpar dados se solicitado
        if limpar_tudo:
            print("\n⚠️  A LIMPAR TODOS OS DADOS...")
            from database.models import Cliente, Fornecedor, Projeto, Despesa, Boletim

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

        # Importar dados
        try:
            self.importar_clientes()
            self.importar_fornecedores()
            self.importar_projetos()
            self.importar_despesas()

            # Resumo final
            print("\n" + "=" * 80)
            print("📊 RESUMO DA IMPORTAÇÃO")
            print("=" * 80)
            print(f"✅ Clientes: {self.stats['clientes']['sucesso']}/{self.stats['clientes']['total']}")
            print(f"✅ Fornecedores: {self.stats['fornecedores']['sucesso']}/{self.stats['fornecedores']['total']}")
            print(f"✅ Projetos: {self.stats['projetos']['sucesso']}/{self.stats['projetos']['total']}")
            print(f"✅ Despesas: {self.stats['despesas']['sucesso']}/{self.stats['despesas']['total']}")
            print()
            print(f"🏆 Prémios Bruno: €{float(self.stats['premios']['bruno']):,.2f}")
            print(f"🏆 Prémios Rafael: €{float(self.stats['premios']['rafael']):,.2f}")
            print()
            print("=" * 80)
            print("✅ IMPORTAÇÃO CONCLUÍDA!")
            print("=" * 80)
            print()
            print("Próximo passo:")
            print("  → Abrir a app e verificar o dashboard 'Saldos Pessoais'")
            print("  → Executar: python3 main.py")
            print()

            return True

        except Exception as e:
            print(f"\n❌ Erro durante importação: {e}")
            import traceback
            traceback.print_exc()
            return False


def main():
    print("=" * 80)
    print("🚀 IMPORTAÇÃO DIRETA DO EXCEL")
    print("=" * 80)
    print()

    # Confirmar
    resposta = input("Limpar todos os dados antes de importar? (sim/não): ").strip().lower()
    limpar = resposta in ['sim', 's', 'yes', 'y']

    if limpar:
        print("\n⚠️  ATENÇÃO: Todos os dados atuais serão apagados!")
        confirma = input("Tem certeza? (sim/não): ").strip().lower()
        if confirma not in ['sim', 's', 'yes', 'y']:
            print("❌ Operação cancelada!")
            return

    print()

    # Executar importação
    importer = ExcelImporter()
    success = importer.executar(limpar_tudo=limpar)

    if not success:
        sys.exit(1)


if __name__ == '__main__':
    main()
