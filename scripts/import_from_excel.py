#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de importação INCREMENTAL do Excel CONTABILIDADE_FINAL.xlsx

MODO INCREMENTAL (padrão):
- Verifica se registo já existe (por número: #C001, #P001, etc.)
- Se existe → SKIP (não atualiza, preserva alterações locais)
- Se não existe → INSERT (cria novo)
- Exceção PROJETOS: Se existe mas prémios mudaram → UPDATE prémios

FLAGS:
--dry-run          Preview sem gravar nada
--clear-all        Limpar DB antes de importar (cuidado!)
--excel PATH       Caminho para ficheiro Excel (default: excel/CONTABILIDADE_FINAL_20251108.xlsx)

LÓGICA DE MATCHING:
- CLIENTES: Número (#C001, #C002, ...)
- FORNECEDORES: Número (#F001, #F002, ...)
- PROJETOS: Número (#P001, #P002, ...)
- DESPESAS: Número (#D001, #D002, ...)
- BOLETINS: Número (#D... extraído de DESPESAS)
"""
import sys
import os
import argparse
from datetime import datetime, date
from decimal import Decimal
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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
    """Importador incremental do Excel"""

    def __init__(self, session, excel_path, dry_run=False):
        self.excel_path = excel_path
        self.xl = None
        self.session = session
        self.dry_run = dry_run

        # Managers
        self.clientes_manager = ClientesManager(session)
        self.fornecedores_manager = FornecedoresManager(session)
        self.projetos_manager = ProjetosManager(session)
        self.despesas_manager = DespesasManager(session)
        self.boletins_manager = BoletinsManager(session)

        # Mapeamentos (nome → ID)
        self.clientes_map = {}
        self.fornecedores_map = {}
        self.projetos_map = {}

        # Estatísticas melhoradas
        self.stats = {
            'clientes': {'total': 0, 'new': 0, 'skip': 0, 'error': 0},
            'fornecedores': {'total': 0, 'new': 0, 'skip': 0, 'error': 0},
            'projetos': {'total': 0, 'new': 0, 'skip': 0, 'updated': 0, 'error': 0},
            'despesas': {'total': 0, 'new': 0, 'skip': 0, 'updated': 0, 'error': 0},
            'boletins': {'total': 0, 'new': 0, 'skip': 0, 'error': 0},
            'premios': {'bruno': Decimal('0'), 'rafael': Decimal('0')},
        }

        # Armazenar prémios para adicionar aos projetos depois
        self.premios_por_projeto = {}

        # Data de hoje para marcar fixas como PAGO
        self.hoje = date.today()

    # ========== MÉTODOS DE VERIFICAÇÃO DE EXISTÊNCIA ==========

    def _exists_cliente(self, numero):
        """Verifica se cliente já existe pelo número"""
        return self.session.query(Cliente).filter(Cliente.numero == numero).first()

    def _exists_fornecedor(self, numero):
        """Verifica se fornecedor já existe pelo número"""
        return self.session.query(Fornecedor).filter(Fornecedor.numero == numero).first()

    def _exists_projeto(self, numero):
        """Verifica se projeto já existe pelo número"""
        return self.session.query(Projeto).filter(Projeto.numero == numero).first()

    def _exists_despesa(self, numero):
        """Verifica se despesa já existe pelo número"""
        return self.session.query(Despesa).filter(Despesa.numero == numero).first()

    def _exists_boletim(self, socio, data_emissao, valor):
        """Verifica se boletim já existe (não tem número único)"""
        return self.session.query(Boletim).filter(
            Boletim.socio == socio,
            Boletim.data_emissao == data_emissao,
            Boletim.valor == valor
        ).first()

    # ========== MÉTODOS AUXILIARES (parsing) ==========

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
        """Mapeia tipo de projeto"""
        if not pd.isna(estado_str):
            estado = str(estado_str).lower()
            if 'pessoal' in estado:
                if not pd.isna(owner_str):
                    owner = str(owner_str).lower()
                    if 'bruno' in owner:
                        return TipoProjeto.PESSOAL_BRUNO
                    elif 'rafael' in owner:
                        return TipoProjeto.PESSOAL_RAFAEL
                return TipoProjeto.EMPRESA

        return TipoProjeto.EMPRESA

    def mapear_estado_projeto(self, data_recebimento, data_faturacao, data_vencimento):
        """Mapeia estado do projeto"""
        if data_recebimento:
            return EstadoProjeto.RECEBIDO
        elif data_vencimento and data_vencimento <= self.hoje:
            return EstadoProjeto.RECEBIDO
        elif data_faturacao:
            return EstadoProjeto.FATURADO
        else:
            return EstadoProjeto.NAO_FATURADO

    # ========== IMPORTAÇÃO DE CLIENTES ==========

    def importar_clientes(self):
        """Importa clientes (modo incremental)"""
        print("\n" + "=" * 80)
        print("📋 IMPORTANDO CLIENTES (modo incremental)")
        print("=" * 80)

        df = pd.read_excel(self.xl, sheet_name='CLIENTES', header=1)
        df_dados = df[df.iloc[:, 0].astype(str).str.startswith('#C', na=False)]

        print(f"Total de clientes no Excel: {len(df_dados)}")
        print()

        for idx, row in df_dados.iterrows():
            numero = self.safe_str(row.iloc[0])
            nome = self.safe_str(row.iloc[1])

            if not nome:
                continue

            self.stats['clientes']['total'] += 1

            # ✅ VERIFICAR SE JÁ EXISTE
            existing = self._exists_cliente(numero)
            if existing:
                self.stats['clientes']['skip'] += 1
                self.clientes_map[nome] = existing.id
                print(f"  ⏭️  {numero}: {nome} (já existe)")
                continue

            # DRY RUN: Não gravar
            if self.dry_run:
                self.stats['clientes']['new'] += 1
                print(f"  🔍 {numero}: {nome} (seria criado)")
                continue

            # CRIAR NOVO
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
                    # Manter número do Excel
                    cliente.numero = numero
                    self.session.add(cliente)
                    self.session.commit()

                    self.stats['clientes']['new'] += 1
                    self.clientes_map[nome] = cliente.id
                    print(f"  ✅ {numero}: {nome} (criado)")
                else:
                    self.stats['clientes']['error'] += 1
                    print(f"  ❌ {numero}: {nome} - {msg}")

            except Exception as e:
                self.session.rollback()
                self.stats['clientes']['error'] += 1
                print(f"  ❌ {numero}: {nome} - Erro: {e}")

        self._print_stats('clientes')

    # ========== IMPORTAÇÃO DE FORNECEDORES ==========

    def importar_fornecedores(self):
        """Importa fornecedores (modo incremental)"""
        print("\n" + "=" * 80)
        print("📋 IMPORTANDO FORNECEDORES (modo incremental)")
        print("=" * 80)

        df = pd.read_excel(self.xl, sheet_name='FORNECEDORES', header=1)
        df_dados = df[df.iloc[:, 0].astype(str).str.startswith('#F', na=False)]

        print(f"Total de fornecedores no Excel: {len(df_dados)}")
        print()

        for idx, row in df_dados.iterrows():
            numero = self.safe_str(row.iloc[0])
            nome = self.safe_str(row.iloc[1])

            if not nome:
                continue

            self.stats['fornecedores']['total'] += 1

            # ✅ VERIFICAR SE JÁ EXISTE
            existing = self._exists_fornecedor(numero)
            if existing:
                self.stats['fornecedores']['skip'] += 1
                self.fornecedores_map[nome] = existing.id
                print(f"  ⏭️  {numero}: {nome} (já existe)")
                continue

            # DRY RUN: Não gravar
            if self.dry_run:
                self.stats['fornecedores']['new'] += 1
                print(f"  🔍 {numero}: {nome} (seria criado)")
                continue

            # CRIAR NOVO
            estatuto_str = self.safe_str(row.iloc[2])
            estatuto = self.mapear_estatuto_fornecedor(estatuto_str)
            area = self.safe_str(row.iloc[3])
            funcao = self.safe_str(row.iloc[4])
            classificacao_str = self.safe_str(row.iloc[5])

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
                    pais=pais,
                    contacto=contacto,
                    email=email,
                    validade_seguro_trabalho=validade_seguro,
                    nota=nota
                )

                if success:
                    # Manter número do Excel
                    fornecedor.numero = numero
                    self.session.add(fornecedor)
                    self.session.commit()

                    self.stats['fornecedores']['new'] += 1
                    self.fornecedores_map[nome] = fornecedor.id
                    print(f"  ✅ {numero}: {nome} (criado)")
                else:
                    self.stats['fornecedores']['error'] += 1
                    print(f"  ❌ {numero}: {nome} - {msg}")

            except Exception as e:
                self.session.rollback()
                self.stats['fornecedores']['error'] += 1
                print(f"  ❌ {numero}: {nome} - Erro: {e}")

        self._print_stats('fornecedores')

    # ========== IMPORTAÇÃO DE PROJETOS ==========

    def importar_projetos(self):
        """Importa projetos (modo incremental + update prémios)"""
        print("\n" + "=" * 80)
        print("📋 IMPORTANDO PROJETOS (modo incremental + update prémios)")
        print("=" * 80)

        df = pd.read_excel(self.xl, sheet_name='PROJETOS', header=2)
        df_dados = df[df.iloc[:, 0].astype(str).str.startswith('#P', na=False)]

        print(f"Total de projetos no Excel: {len(df_dados)}")
        print()

        for idx, row in df_dados.iterrows():
            numero = self.safe_str(row.iloc[0])
            cliente_nome = self.safe_str(row.iloc[1])
            descricao = self.safe_str(row.iloc[4])

            if not descricao:
                continue

            self.stats['projetos']['total'] += 1

            # Parse dados do Excel
            data_inicio = self.parse_date(row.iloc[2])
            data_fim = self.parse_date(row.iloc[3])
            valor_sem_iva = self.safe_decimal(row.iloc[5])
            data_faturacao = self.parse_date(row.iloc[6])
            data_vencimento = self.parse_date(row.iloc[7])
            data_recebimento = self.parse_date(row.iloc[8])

            estado_str = self.safe_str(row.iloc[14]) if len(row) > 14 else None
            owner_str = self.safe_str(row.iloc[15]) if len(row) > 15 else None
            nota = self.safe_str(row.iloc[16]) if len(row) > 16 else None

            tipo = self.mapear_tipo_projeto(estado_str, owner_str)
            estado = self.mapear_estado_projeto(data_recebimento, data_faturacao, data_vencimento)

            if estado == EstadoProjeto.RECEBIDO and data_recebimento and not data_faturacao:
                data_faturacao = data_recebimento

            cliente_id = None
            if cliente_nome and cliente_nome in self.clientes_map:
                cliente_id = self.clientes_map[cliente_nome]
            elif cliente_nome:
                cliente = self.session.query(Cliente).filter(Cliente.nome == cliente_nome).first()
                if cliente:
                    cliente_id = cliente.id
                    self.clientes_map[cliente_nome] = cliente.id

            # Prémios (do Excel, inicialmente 0)
            premio_bruno = Decimal('0')
            premio_rafael = Decimal('0')

            # ✅ VERIFICAR SE JÁ EXISTE
            existing = self._exists_projeto(numero)
            if existing:
                # Projeto existe → verificar se prémios mudaram (serão atualizados depois em processar_premios)
                self.stats['projetos']['skip'] += 1
                self.projetos_map[numero] = existing.id
                print(f"  ⏭️  {numero}: {descricao[:40]} (já existe)")
                continue

            # DRY RUN: Não gravar
            if self.dry_run:
                self.stats['projetos']['new'] += 1
                tipo_icon = "🏢" if tipo == TipoProjeto.EMPRESA else ("👤B" if tipo == TipoProjeto.PESSOAL_BRUNO else "👤R")
                print(f"  🔍 {numero}: {tipo_icon} {descricao[:40]} (seria criado)")
                continue

            # CRIAR NOVO
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
                    # Manter número do Excel
                    projeto.numero = numero
                    self.session.add(projeto)
                    self.session.commit()

                    self.stats['projetos']['new'] += 1
                    self.projetos_map[numero] = projeto.id
                    tipo_icon = "🏢" if tipo == TipoProjeto.EMPRESA else ("👤B" if tipo == TipoProjeto.PESSOAL_BRUNO else "👤R")
                    estado_icon = "✅" if estado == EstadoProjeto.RECEBIDO else ("📄" if estado == EstadoProjeto.FATURADO else "⏳")
                    print(f"  {estado_icon} {numero}: {tipo_icon} {descricao[:40]} (criado)")
                else:
                    self.stats['projetos']['error'] += 1
                    print(f"  ❌ {numero}: {descricao[:40]} - {msg}")

            except Exception as e:
                self.session.rollback()
                self.stats['projetos']['error'] += 1
                print(f"  ❌ {numero}: {descricao[:40]} - Erro: {e}")

        self._print_stats('projetos')

    # ========== IMPORTAÇÃO DE DESPESAS ==========

    def importar_despesas(self):
        """Importa despesas (modo incremental, sem prémios e boletins)"""
        print("\n" + "=" * 80)
        print("📋 IMPORTANDO DESPESAS (modo incremental)")
        print("=" * 80)

        df = pd.read_excel(self.xl, sheet_name='DESPESAS', header=5)
        df_dados = df[df.iloc[:, 0].astype(str).str.startswith('#D', na=False)]

        print(f"Total de registos DESPESAS no Excel: {len(df_dados)}")
        print("(Prémios e Boletins serão processados separadamente)")
        print()

        for idx, row in df_dados.iterrows():
            numero = self.safe_str(row.iloc[0])
            credor_nome = self.safe_str(row.iloc[4])
            tipo_str = self.safe_str(row.iloc[6])
            descricao = self.safe_str(row.iloc[7])

            if not descricao:
                continue

            # SKIP Prémios (processados em processar_premios)
            if tipo_str and ('prém' in str(tipo_str).lower() or 'premio' in str(tipo_str).lower()):
                projeto_numero = self.safe_str(row.iloc[5])
                valor = self.safe_decimal(row.iloc[15])

                if projeto_numero and valor:
                    if projeto_numero not in self.premios_por_projeto:
                        self.premios_por_projeto[projeto_numero] = {'bruno': Decimal('0'), 'rafael': Decimal('0')}

                    if 'bruno' in str(credor_nome).lower():
                        self.premios_por_projeto[projeto_numero]['bruno'] += valor
                        self.stats['premios']['bruno'] += valor
                    elif 'rafael' in str(credor_nome).lower():
                        self.premios_por_projeto[projeto_numero]['rafael'] += valor
                        self.stats['premios']['rafael'] += valor

                continue

            # SKIP Boletins (processados em importar_boletins)
            if tipo_str and any(x in str(tipo_str).lower() for x in ['deslocação, pessoal', 'per diem pt, pessoal', 'per diem fora, pessoal']):
                continue

            self.stats['despesas']['total'] += 1

            # PROCESSAR DADOS DA LINHA (para criar OU atualizar)
            ano = self.safe_int(row.iloc[1])
            mes = self.safe_int(row.iloc[2])
            dia = self.safe_int(row.iloc[3])

            data_vencimento = None
            if ano and mes and dia:
                try:
                    data_vencimento = date(ano, mes, dia)
                except:
                    data_vencimento = None

            # Tentar ler DATA DE VENCIMENTO da coluna T (índice 19)
            # Se coluna T está preenchida → despesa PAGA
            # Se coluna T está vazia → despesa PENDENTE
            if not data_vencimento and len(row) > 19:
                data_vencimento = self.parse_date(row.iloc[19])

            projeto_numero = self.safe_str(row.iloc[5])
            periodicidade = self.safe_str(row.iloc[8])
            valor_sem_iva = self.safe_decimal(row.iloc[15])
            valor_com_iva = self.safe_decimal(row.iloc[16]) if len(row) > 16 else None
            nota = self.safe_str(row.iloc[22]) if len(row) > 22 else None
            out_col = self.safe_str(row.iloc[20]) if len(row) > 20 else None

            # Determinar tipo
            tipo = None
            if periodicidade and 'mensal' in str(periodicidade).lower():
                tipo = TipoDespesa.FIXA_MENSAL
            elif tipo_str and 'pessoal' in str(tipo_str).lower():
                if out_col and 'bruno' in str(out_col).lower():
                    tipo = TipoDespesa.PESSOAL_BRUNO
                elif out_col and 'rafael' in str(out_col).lower():
                    tipo = TipoDespesa.PESSOAL_RAFAEL
                else:
                    if 'bruno' in str(credor_nome).lower():
                        tipo = TipoDespesa.PESSOAL_BRUNO
                    elif 'rafael' in str(credor_nome).lower():
                        tipo = TipoDespesa.PESSOAL_RAFAEL
                    else:
                        tipo = TipoDespesa.PROJETO
            elif tipo_str and 'equipamento' in str(tipo_str).lower():
                tipo = TipoDespesa.EQUIPAMENTO
            else:
                tipo = TipoDespesa.PROJETO

            # ✅ LÓGICA DE ESTADO CORRETA
            #
            # A coluna T (DATA DE VENCIMENTO) determina o estado da despesa:
            # - Se PREENCHIDA → despesa foi PAGA (data_pagamento = data_vencimento)
            # - Se VAZIA → despesa está PENDENTE (data_pagamento = None)
            #
            # NOTAS IMPORTANTES:
            # 1. Coluna V (ATIVO) NÃO é usada para determinar estado PAGO/PENDENTE
            # 2. Despesas do tipo PRÉMIO ou COMISSÃO são filtradas antes (linhas 507-522)
            #    e processadas separadamente em processar_premios()
            # 3. Prémios são pagos através de boletins, não como despesas diretas
            #
            if data_vencimento:
                # Coluna T preenchida → PAGO
                estado = EstadoDespesa.PAGO
                data_pagamento = data_vencimento
            else:
                # Coluna T vazia → PENDENTE
                estado = EstadoDespesa.PENDENTE
                data_pagamento = None

            # Credor ID
            credor_id = None
            if credor_nome:
                if credor_nome in self.fornecedores_map:
                    credor_id = self.fornecedores_map[credor_nome]
                else:
                    credor = self.session.query(Fornecedor).filter(Fornecedor.nome == credor_nome).first()
                    if credor:
                        credor_id = credor.id
                        self.fornecedores_map[credor_nome] = credor.id

            # Projeto ID
            projeto_id = None
            if projeto_numero:
                if projeto_numero in self.projetos_map:
                    projeto_id = self.projetos_map[projeto_numero]
                else:
                    projeto = self.session.query(Projeto).filter(Projeto.numero == projeto_numero).first()
                    if projeto:
                        projeto_id = projeto.id
                        self.projetos_map[projeto_numero] = projeto.id

            # ✅ VERIFICAR SE JÁ EXISTE (após processar dados)
            existing = self._exists_despesa(numero)
            if existing:
                # Verificar se estado mudou no Excel
                if existing.estado != estado:
                    # Estado mudou → ATUALIZAR
                    if self.dry_run:
                        old_estado = existing.estado.value
                        new_estado = estado.value
                        print(f"  🔄 {numero}: {descricao[:40]} (estado: {old_estado} → {new_estado})")
                        self.stats['despesas']['updated'] += 1
                    else:
                        try:
                            existing.estado = estado
                            existing.data_pagamento = data_pagamento
                            self.session.commit()

                            old_estado = existing.estado.value if hasattr(existing.estado, 'value') else existing.estado
                            new_estado = estado.value
                            print(f"  🔄 {numero}: {descricao[:40]} (estado atualizado: {new_estado})")
                            self.stats['despesas']['updated'] += 1
                        except Exception as e:
                            print(f"  ❌ {numero}: Erro ao atualizar - {e}")
                            self.stats['despesas']['error'] += 1
                else:
                    # Estado igual → SKIP
                    self.stats['despesas']['skip'] += 1
                    # print(f"  ⏭️  {numero}: {descricao[:40]} (já existe)")
                continue

            # DRY RUN: Não gravar
            if self.dry_run:
                self.stats['despesas']['new'] += 1
                print(f"  🔍 {numero}: {descricao[:40]} (seria criado)")
                continue

            # CRIAR NOVA DESPESA
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
                    # Manter número do Excel
                    despesa.numero = numero
                    self.session.add(despesa)
                    self.session.commit()

                    self.stats['despesas']['new'] += 1
                    tipo_icon = "🔧" if tipo == TipoDespesa.FIXA_MENSAL else "💸"
                    print(f"  ✅ {numero}: {tipo_icon} {descricao[:40]} (criado)")
                else:
                    self.stats['despesas']['error'] += 1
                    print(f"  ❌ {numero}: {descricao[:40]} - {msg}")

            except Exception as e:
                self.session.rollback()
                self.stats['despesas']['error'] += 1
                print(f"  ❌ {numero}: {descricao[:40]} - Erro: {e}")

        self._print_stats('despesas')

    # ========== PROCESSAR PRÉMIOS ==========

    def processar_premios(self):
        """Adiciona/atualiza prémios nos projetos"""
        print("\n" + "=" * 80)
        print("🏆 PROCESSANDO PRÉMIOS")
        print("=" * 80)

        if not self.premios_por_projeto:
            print("Nenhum prémio encontrado no Excel.")
            return

        print(f"Total de projetos com prémios no Excel: {len(self.premios_por_projeto)}")
        print()

        for projeto_numero, premios in self.premios_por_projeto.items():
            # Buscar projeto (pode já existir ou ter sido criado agora)
            projeto = None
            if projeto_numero in self.projetos_map:
                # Map guarda ID, preciso buscar o objeto
                projeto_id = self.projetos_map[projeto_numero]
                projeto = self.session.query(Projeto).filter(Projeto.id == projeto_id).first()
            else:
                projeto = self._exists_projeto(projeto_numero)

            if not projeto:
                print(f"  ⚠️  {projeto_numero}: Projeto não encontrado")
                continue

            # Verificar se prémios mudaram
            premios_mudaram = False
            if premios['bruno'] > 0 and projeto.premio_bruno != premios['bruno']:
                premios_mudaram = True
            if premios['rafael'] > 0 and projeto.premio_rafael != premios['rafael']:
                premios_mudaram = True

            if not premios_mudaram:
                print(f"  ⏭️  {projeto_numero}: Prémios inalterados")
                continue

            # DRY RUN: Não gravar
            if self.dry_run:
                bruno_str = f"Bruno: €{float(premios['bruno']):,.2f}" if premios['bruno'] > 0 else ""
                rafael_str = f"Rafael: €{float(premios['rafael']):,.2f}" if premios['rafael'] > 0 else ""
                premios_str = " | ".join(filter(None, [bruno_str, rafael_str]))
                print(f"  🔍 {projeto_numero}: {premios_str} (seria atualizado)")
                continue

            # ATUALIZAR PRÉMIOS
            try:
                if premios['bruno'] > 0:
                    projeto.premio_bruno = premios['bruno']
                if premios['rafael'] > 0:
                    projeto.premio_rafael = premios['rafael']

                self.session.add(projeto)
                self.session.commit()

                self.stats['projetos']['updated'] += 1

                bruno_str = f"Bruno: €{float(premios['bruno']):,.2f}" if premios['bruno'] > 0 else ""
                rafael_str = f"Rafael: €{float(premios['rafael']):,.2f}" if premios['rafael'] > 0 else ""
                premios_str = " | ".join(filter(None, [bruno_str, rafael_str]))

                print(f"  🔄 {projeto_numero}: {premios_str} (atualizado)")

            except Exception as e:
                self.session.rollback()
                print(f"  ❌ {projeto_numero}: Erro ao atualizar - {e}")

        print(f"\n💰 Total prémios no Excel:")
        print(f"   Bruno: €{float(self.stats['premios']['bruno']):,.2f}")
        print(f"   Rafael: €{float(self.stats['premios']['rafael']):,.2f}")

    # ========== IMPORTAÇÃO DE BOLETINS ==========

    def importar_boletins(self):
        """Importa boletins (modo incremental)"""
        print("\n" + "=" * 80)
        print("📄 IMPORTANDO BOLETINS (modo incremental)")
        print("=" * 80)

        df = pd.read_excel(self.xl, sheet_name='DESPESAS', header=5)
        df_dados = df[df.iloc[:, 0].astype(str).str.startswith('#D', na=False)]

        # Filtrar boletins
        boletins_mask = df_dados.iloc[:, 6].astype(str).str.lower().str.contains('deslocação, pessoal|per diem pt, pessoal|per diem fora, pessoal', na=False)
        boletins_df = df_dados[boletins_mask]

        print(f"Total de boletins no Excel (com outubro): {len(boletins_df)}")

        # Excluir outubro 2025
        boletins_df = boletins_df[~boletins_df.iloc[:, 7].astype(str).str.contains('OUT2025', case=False, na=False)]

        print(f"Total de boletins no Excel (sem outubro): {len(boletins_df)}")
        print()

        for idx, row in boletins_df.iterrows():
            numero = self.safe_str(row.iloc[0])
            credor_nome = self.safe_str(row.iloc[4])
            descricao = self.safe_str(row.iloc[7])

            if not credor_nome:
                continue

            self.stats['boletins']['total'] += 1

            # Determinar sócio
            socio = None
            if 'bruno' in str(credor_nome).lower():
                socio = Socio.BRUNO
            elif 'rafael' in str(credor_nome).lower():
                socio = Socio.RAFAEL
            else:
                print(f"  ⚠️  {numero}: Não foi possível determinar sócio de '{credor_nome}'")
                continue

            # Datas
            ano = self.safe_int(row.iloc[1])
            mes = self.safe_int(row.iloc[2])
            dia = self.safe_int(row.iloc[3])

            data_emissao = None
            if ano and mes and dia:
                try:
                    data_emissao = date(ano, mes, dia)
                except:
                    pass

            if not data_emissao and len(row) > 19:
                data_emissao = self.parse_date(row.iloc[19])

            data_vencimento = None
            if len(row) > 19:
                data_vencimento = self.parse_date(row.iloc[19])

            valor = self.safe_decimal(row.iloc[15])

            if not valor:
                print(f"  ⚠️  {numero}: Sem valor")
                continue

            # ✅ VERIFICAR SE JÁ EXISTE (por socio + data + valor)
            existing = self._exists_boletim(socio, data_emissao, valor)
            if existing:
                self.stats['boletins']['skip'] += 1
                socio_icon = "👤B" if socio == Socio.BRUNO else "👤R"
                print(f"  ⏭️  {numero}: {socio_icon} €{float(valor):,.2f} (já existe)")
                continue

            # DRY RUN: Não gravar
            if self.dry_run:
                self.stats['boletins']['new'] += 1
                socio_icon = "👤B" if socio == Socio.BRUNO else "👤R"
                print(f"  🔍 {numero}: {socio_icon} €{float(valor):,.2f} (seria criado)")
                continue

            # CRIAR NOVO
            try:
                success, boletim, msg = self.boletins_manager.emitir(
                    socio=socio,
                    data_emissao=data_emissao,
                    valor=valor,
                    descricao=descricao
                )

                if success:
                    # Se vencido, marcar como PAGO
                    if data_vencimento and data_vencimento <= self.hoje:
                        self.boletins_manager.marcar_como_pago(boletim.id, data_vencimento)
                        estado_icon = "💰"
                    else:
                        estado_icon = "⏳"

                    self.stats['boletins']['new'] += 1
                    socio_icon = "👤B" if socio == Socio.BRUNO else "👤R"
                    print(f"  ✅ {numero}: {socio_icon} {estado_icon} €{float(valor):,.2f} (criado)")
                else:
                    self.stats['boletins']['error'] += 1
                    print(f"  ❌ {numero}: {msg}")

            except Exception as e:
                self.session.rollback()
                self.stats['boletins']['error'] += 1
                print(f"  ❌ {numero}: Erro - {e}")

        self._print_stats('boletins')

    # ========== MÉTODOS AUXILIARES ==========

    def _print_stats(self, entity):
        """Imprime estatísticas de uma entidade"""
        stats = self.stats[entity]
        total = stats['total']
        new = stats.get('new', 0)
        skip = stats.get('skip', 0)
        updated = stats.get('updated', 0)
        error = stats.get('error', 0)

        print(f"\n📊 {entity.upper()}:")
        if new > 0:
            print(f"   ✅ Novos: {new}")
        if skip > 0:
            print(f"   ⏭️  Skip: {skip}")
        if updated > 0:
            print(f"   🔄 Atualizados: {updated}")
        if error > 0:
            print(f"   ❌ Erros: {error}")
        print(f"   📋 Total processado: {total}")

    # ========== EXECUÇÃO PRINCIPAL ==========

    def executar(self, limpar_tudo=False):
        """Executa importação completa"""
        mode_str = "🔍 DRY RUN (preview)" if self.dry_run else "✅ MODO REAL (gravar na DB)"

        print("=" * 80)
        print(f"📊 IMPORTAÇÃO INCREMENTAL DO EXCEL - {mode_str}")
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

        # Limpar dados (se pedido)
        if limpar_tudo:
            print("\n⚠️  A LIMPAR TODOS OS DADOS...")
            if self.dry_run:
                print("   🔍 DRY RUN: Limpeza não executada")
            else:
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
            self.processar_premios()
            self.importar_boletins()

            # Resumo final
            print("\n" + "=" * 80)
            print("📊 RESUMO FINAL DA IMPORTAÇÃO")
            print("=" * 80)

            for entity in ['clientes', 'fornecedores', 'projetos', 'despesas', 'boletins']:
                stats = self.stats[entity]
                print(f"\n{entity.upper()}:")
                print(f"  ✅ Novos: {stats.get('new', 0)}")
                print(f"  ⏭️  Skip: {stats.get('skip', 0)}")
                if 'updated' in stats and stats['updated'] > 0:
                    print(f"  🔄 Atualizados: {stats['updated']}")
                if stats.get('error', 0) > 0:
                    print(f"  ❌ Erros: {stats['error']}")

            print()

            # Commit final (se não for dry run)
            if not self.dry_run:
                print("💾 A gravar todos os dados na base de dados...")
                self.session.commit()
                print("   ✅ Dados gravados com sucesso!")
                print()
                print("=" * 80)
                print("✅ IMPORTAÇÃO INCREMENTAL CONCLUÍDA!")
                print("=" * 80)
            else:
                print("=" * 80)
                print("🔍 DRY RUN CONCLUÍDO - Nenhum dado foi gravado")
                print("=" * 80)
                print("\n💡 Para gravar os dados, executa sem --dry-run")

            print()

            return True

        except Exception as e:
            print(f"\n❌ Erro durante importação: {e}")
            import traceback
            traceback.print_exc()
            if not self.dry_run:
                print("\n⚠️  A fazer rollback...")
                self.session.rollback()
                print("   ✅ Rollback concluído. Nenhuma alteração foi gravada.")
            return False


def main():
    parser = argparse.ArgumentParser(description='Importação incremental de dados do Excel')
    parser.add_argument('--dry-run', action='store_true', help='Preview sem gravar nada')
    parser.add_argument('--clear-all', action='store_true', help='Limpar DB antes de importar (cuidado!)')
    parser.add_argument('--excel', type=str, default='excel/CONTABILIDADE_FINAL_20251108.xlsx',
                        help='Caminho para ficheiro Excel')

    args = parser.parse_args()

    print("=" * 80)
    print("🚀 IMPORTAÇÃO INCREMENTAL DO EXCEL")
    print("=" * 80)
    print()

    if args.dry_run:
        print("🔍 MODO: DRY RUN (preview, não grava nada)")
    else:
        print("✅ MODO: REAL (grava na base de dados)")

    print(f"📁 Excel: {args.excel}")
    print()

    # Confirmar limpeza
    limpar = args.clear_all
    if limpar and not args.dry_run:
        print("⚠️  ATENÇÃO: Todos os dados serão apagados!")
        confirma = input("Tem certeza? (sim/não): ").strip().lower()
        if confirma not in ['sim', 's', 'yes', 'y']:
            print("❌ Cancelado!")
            return
    elif limpar and args.dry_run:
        print("🔍 DRY RUN: Limpeza não será executada (apenas preview)")

    print()

    # Setup database
    database_url = os.getenv("DATABASE_URL", "sqlite:///./agora_media.db")
    engine = create_engine(database_url)
    Session = sessionmaker(bind=engine)
    session = Session()

    # Executar
    importer = ExcelImporter(session, excel_path=args.excel, dry_run=args.dry_run)
    success = importer.executar(limpar_tudo=limpar)

    if not success:
        sys.exit(1)


if __name__ == '__main__':
    main()
