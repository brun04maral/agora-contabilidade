# -*- coding: utf-8 -*-
"""
Lógica de gestão de Despesas (CRUD)
"""
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_
from datetime import date, datetime
from decimal import Decimal
from calendar import monthrange

from database.models import Despesa, Fornecedor, Projeto, TipoDespesa, EstadoDespesa


class DespesasManager:
    """
    Gestor de Despesas - CRUD operations
    """

    def __init__(self, db_session: Session):
        """
        Initialize manager

        Args:
            db_session: SQLAlchemy database session
        """
        self.db_session = db_session

    def listar_todas(self) -> List[Despesa]:
        """
        Lista todas as despesas ordenadas por data (mais recentes primeiro)

        Returns:
            Lista de objetos Despesa
        """
        return self.db_session.query(Despesa).order_by(desc(Despesa.data)).all()

    def listar_por_tipo(self, tipo: TipoDespesa) -> List[Despesa]:
        """
        Lista despesas por tipo

        Args:
            tipo: TipoDespesa enum

        Returns:
            Lista de despesas do tipo especificado
        """
        return self.db_session.query(Despesa).filter(
            Despesa.tipo == tipo
        ).order_by(desc(Despesa.data)).all()

    def listar_por_estado(self, estado: EstadoDespesa) -> List[Despesa]:
        """
        Lista despesas por estado

        Args:
            estado: EstadoDespesa enum

        Returns:
            Lista de despesas com o estado especificado
        """
        return self.db_session.query(Despesa).filter(
            Despesa.estado == estado
        ).order_by(desc(Despesa.data)).all()

    def obter_por_id(self, despesa_id: int) -> Optional[Despesa]:
        """
        Obtém uma despesa por ID

        Args:
            despesa_id: ID da despesa

        Returns:
            Objeto Despesa ou None se não encontrado
        """
        return self.db_session.query(Despesa).filter(Despesa.id == despesa_id).first()

    def criar(
        self,
        tipo: TipoDespesa,
        data: date,
        descricao: str,
        valor_sem_iva: Decimal,
        valor_com_iva: Decimal,
        credor_id: Optional[int] = None,
        projeto_id: Optional[int] = None,
        estado: EstadoDespesa = EstadoDespesa.PENDENTE,
        data_pagamento: Optional[date] = None,
        nota: Optional[str] = None,
        is_recorrente: bool = False,
        dia_recorrencia: Optional[int] = None,
        despesa_template_id: Optional[int] = None
    ) -> Tuple[bool, Optional[Despesa], Optional[str]]:
        """
        Cria uma nova despesa

        Args:
            tipo: Tipo da despesa
            data: Data da despesa
            descricao: Descrição
            valor_sem_iva: Valor sem IVA
            valor_com_iva: Valor com IVA
            credor_id: ID do fornecedor/credor (opcional)
            projeto_id: ID do projeto associado (opcional)
            estado: Estado da despesa
            data_pagamento: Data de pagamento (opcional)
            nota: Nota adicional (opcional)
            is_recorrente: Se True, é template de despesa recorrente mensal (opcional)
            dia_recorrencia: Dia do mês (1-31) para gerar automaticamente (opcional)
            despesa_template_id: ID do template que gerou esta despesa (opcional)

        Returns:
            Tuple (sucesso, despesa, mensagem_erro)
        """
        try:
            # Gerar número da despesa
            ultima_despesa = self.db_session.query(Despesa).order_by(
                desc(Despesa.id)
            ).first()

            if ultima_despesa:
                # Extrair número (#D000001 -> 1)
                ultimo_num = int(ultima_despesa.numero.replace('#D', ''))
                novo_num = ultimo_num + 1
            else:
                novo_num = 1

            numero = f"#D{novo_num:06d}"

            # Criar despesa
            despesa = Despesa(
                numero=numero,
                tipo=tipo,
                data=data,
                credor_id=credor_id,
                projeto_id=projeto_id,
                descricao=descricao,
                valor_sem_iva=valor_sem_iva,
                valor_com_iva=valor_com_iva,
                estado=estado,
                data_pagamento=data_pagamento,
                nota=nota,
                is_recorrente=is_recorrente,
                dia_recorrencia=dia_recorrencia,
                despesa_template_id=despesa_template_id
            )

            self.db_session.add(despesa)
            self.db_session.commit()
            self.db_session.refresh(despesa)

            return True, despesa, None

        except Exception as e:
            self.db_session.rollback()
            return False, None, str(e)

    def atualizar(
        self,
        despesa_id: int,
        tipo: Optional[TipoDespesa] = None,
        data: Optional[date] = None,
        descricao: Optional[str] = None,
        valor_sem_iva: Optional[Decimal] = None,
        valor_com_iva: Optional[Decimal] = None,
        credor_id: Optional[int] = None,
        projeto_id: Optional[int] = None,
        estado: Optional[EstadoDespesa] = None,
        data_pagamento: Optional[date] = None,
        nota: Optional[str] = None,
        is_recorrente: Optional[bool] = None,
        dia_recorrencia: Optional[int] = None
    ) -> Tuple[bool, Optional[str]]:
        """
        Atualiza uma despesa existente

        Args:
            despesa_id: ID da despesa
            (outros): Campos a atualizar

        Returns:
            Tuple (sucesso, mensagem_erro)
        """
        try:
            despesa = self.obter_por_id(despesa_id)
            if not despesa:
                return False, "Despesa não encontrada"

            if tipo is not None:
                despesa.tipo = tipo
            if data is not None:
                despesa.data = data
            if descricao is not None:
                despesa.descricao = descricao
            if valor_sem_iva is not None:
                despesa.valor_sem_iva = valor_sem_iva
            if valor_com_iva is not None:
                despesa.valor_com_iva = valor_com_iva
            if credor_id is not None:
                despesa.credor_id = credor_id
            if projeto_id is not None:
                despesa.projeto_id = projeto_id
            if estado is not None:
                despesa.estado = estado
            if data_pagamento is not None:
                despesa.data_pagamento = data_pagamento
            if nota is not None:
                despesa.nota = nota
            if is_recorrente is not None:
                despesa.is_recorrente = is_recorrente
            if dia_recorrencia is not None:
                despesa.dia_recorrencia = dia_recorrencia

            self.db_session.commit()
            return True, None

        except Exception as e:
            self.db_session.rollback()
            return False, str(e)

    def apagar(self, despesa_id: int) -> Tuple[bool, Optional[str]]:
        """
        Apaga uma despesa

        Args:
            despesa_id: ID da despesa

        Returns:
            Tuple (sucesso, mensagem_erro)
        """
        try:
            despesa = self.obter_por_id(despesa_id)
            if not despesa:
                return False, "Despesa não encontrada"

            self.db_session.delete(despesa)
            self.db_session.commit()
            return True, None

        except Exception as e:
            self.db_session.rollback()
            return False, str(e)

    def obter_fornecedores(self) -> List[Fornecedor]:
        """
        Obtém lista de todos os fornecedores

        Returns:
            Lista de fornecedores
        """
        return self.db_session.query(Fornecedor).order_by(Fornecedor.nome).all()

    def obter_projetos(self) -> List[Projeto]:
        """
        Obtém lista de todos os projetos

        Returns:
            Lista de projetos
        """
        return self.db_session.query(Projeto).order_by(desc(Projeto.created_at)).all()

    # ========== Métodos de Despesas Recorrentes ==========

    def listar_despesas_recorrentes(self) -> List[Despesa]:
        """
        Lista todos os templates de despesas recorrentes

        Returns:
            Lista de despesas recorrentes (templates)
        """
        return self.db_session.query(Despesa).filter(
            Despesa.is_recorrente == True
        ).order_by(Despesa.dia_recorrencia).all()

    def gerar_despesas_recorrentes_mes(self, ano: int, mes: int) -> Tuple[int, List[str]]:
        """
        Gera despesas recorrentes para um mês específico

        Args:
            ano: Ano (ex: 2025)
            mes: Mês (1-12)

        Returns:
            Tuple (quantidade_gerada, lista_de_erros)
        """
        templates = self.listar_despesas_recorrentes()
        geradas = 0
        erros = []

        for template in templates:
            try:
                # Verificar se já existe despesa gerada para este template neste mês
                ja_existe = self.db_session.query(Despesa).filter(
                    and_(
                        Despesa.despesa_template_id == template.id,
                        Despesa.data >= date(ano, mes, 1),
                        Despesa.data < date(ano, mes + 1, 1) if mes < 12 else date(ano + 1, 1, 1)
                    )
                ).first()

                if ja_existe:
                    continue  # Já foi gerada para este mês

                # Calcular a data correta (ajustar se o dia não existir no mês)
                ultimo_dia_mes = monthrange(ano, mes)[1]
                dia = min(template.dia_recorrencia, ultimo_dia_mes)
                data_despesa = date(ano, mes, dia)

                # Criar a despesa baseada no template
                sucesso, despesa, erro = self.criar(
                    tipo=template.tipo,
                    data=data_despesa,
                    descricao=template.descricao,
                    valor_sem_iva=template.valor_sem_iva,
                    valor_com_iva=template.valor_com_iva,
                    credor_id=template.credor_id,
                    projeto_id=template.projeto_id,
                    estado=EstadoDespesa.PENDENTE,
                    data_pagamento=None,
                    nota=f"Gerada automaticamente do template {template.numero}",
                    is_recorrente=False,  # A despesa gerada não é template
                    dia_recorrencia=None,
                    despesa_template_id=template.id  # Rastrear o template
                )

                if sucesso:
                    geradas += 1
                else:
                    erros.append(f"Erro ao gerar despesa do template {template.numero}: {erro}")

            except Exception as e:
                erros.append(f"Erro ao processar template {template.numero}: {str(e)}")

        return geradas, erros

    def verificar_e_gerar_recorrentes_pendentes(self) -> Tuple[int, List[str]]:
        """
        Verifica e gera despesas recorrentes pendentes para o mês atual

        Returns:
            Tuple (quantidade_gerada, lista_de_erros)
        """
        hoje = date.today()
        return self.gerar_despesas_recorrentes_mes(hoje.year, hoje.month)
