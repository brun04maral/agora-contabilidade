# -*- coding: utf-8 -*-
"""
Lógica de gestão de Projetos (CRUD)
"""
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import date
from decimal import Decimal

from database.models import Projeto, Cliente, TipoProjeto, EstadoProjeto


class ProjetosManager:
    """
    Gestor de Projetos - CRUD operations
    """

    def __init__(self, db_session: Session):
        """
        Initialize manager

        Args:
            db_session: SQLAlchemy database session
        """
        self.db_session = db_session

    def listar_todos(self) -> List[Projeto]:
        """
        Lista todos os projetos ordenados por data (mais recentes primeiro)

        Returns:
            Lista de objetos Projeto
        """
        return self.db_session.query(Projeto).order_by(desc(Projeto.created_at)).all()

    def listar_por_tipo(self, tipo: TipoProjeto) -> List[Projeto]:
        """
        Lista projetos por tipo

        Args:
            tipo: TipoProjeto enum

        Returns:
            Lista de projetos do tipo especificado
        """
        return self.db_session.query(Projeto).filter(
            Projeto.tipo == tipo
        ).order_by(desc(Projeto.created_at)).all()

    def listar_por_estado(self, estado: EstadoProjeto) -> List[Projeto]:
        """
        Lista projetos por estado

        Args:
            estado: EstadoProjeto enum

        Returns:
            Lista de projetos com o estado especificado
        """
        return self.db_session.query(Projeto).filter(
            Projeto.estado == estado
        ).order_by(desc(Projeto.created_at)).all()

    def obter_por_id(self, projeto_id: int) -> Optional[Projeto]:
        """
        Obtém um projeto por ID

        Args:
            projeto_id: ID do projeto

        Returns:
            Objeto Projeto ou None se não encontrado
        """
        return self.db_session.query(Projeto).filter(Projeto.id == projeto_id).first()

    def criar(
        self,
        tipo: TipoProjeto,
        cliente_id: Optional[int],
        descricao: str,
        valor_sem_iva: Decimal,
        data_inicio: Optional[date] = None,
        data_fim: Optional[date] = None,
        data_faturacao: Optional[date] = None,
        data_vencimento: Optional[date] = None,
        estado: EstadoProjeto = EstadoProjeto.NAO_FATURADO,
        premio_bruno: Optional[Decimal] = None,
        premio_rafael: Optional[Decimal] = None,
        nota: Optional[str] = None
    ) -> Tuple[bool, Optional[Projeto], Optional[str]]:
        """
        Cria um novo projeto

        Args:
            tipo: Tipo do projeto
            cliente_id: ID do cliente (opcional)
            descricao: Descrição do projeto
            valor_sem_iva: Valor sem IVA
            data_inicio: Data de início (opcional)
            data_fim: Data de fim (opcional)
            data_faturacao: Data de faturação (opcional)
            data_vencimento: Data de vencimento (opcional)
            estado: Estado do projeto
            premio_bruno: Prémio do Bruno (opcional)
            premio_rafael: Prémio do Rafael (opcional)
            nota: Nota adicional (opcional)

        Returns:
            Tuple (sucesso, projeto, mensagem_erro)
        """
        try:
            # Gerar número do projeto
            ultimo_projeto = self.db_session.query(Projeto).order_by(
                desc(Projeto.id)
            ).first()

            if ultimo_projeto:
                # Extrair número do último projeto (#P0001 -> 1)
                ultimo_num = int(ultimo_projeto.numero.replace('#P', ''))
                novo_num = ultimo_num + 1
            else:
                novo_num = 1

            numero = f"#P{novo_num:04d}"

            # Criar projeto
            projeto = Projeto(
                numero=numero,
                tipo=tipo,
                cliente_id=cliente_id,
                descricao=descricao,
                valor_sem_iva=valor_sem_iva,
                data_inicio=data_inicio,
                data_fim=data_fim,
                data_faturacao=data_faturacao,
                data_vencimento=data_vencimento,
                estado=estado,
                premio_bruno=premio_bruno or Decimal("0.00"),
                premio_rafael=premio_rafael or Decimal("0.00"),
                nota=nota
            )

            self.db_session.add(projeto)
            self.db_session.commit()
            self.db_session.refresh(projeto)

            return True, projeto, None

        except Exception as e:
            self.db_session.rollback()
            return False, None, str(e)

    def atualizar(
        self,
        projeto_id: int,
        tipo: Optional[TipoProjeto] = None,
        cliente_id: Optional[int] = None,
        descricao: Optional[str] = None,
        valor_sem_iva: Optional[Decimal] = None,
        data_inicio: Optional[date] = None,
        data_fim: Optional[date] = None,
        data_faturacao: Optional[date] = None,
        data_vencimento: Optional[date] = None,
        estado: Optional[EstadoProjeto] = None,
        premio_bruno: Optional[Decimal] = None,
        premio_rafael: Optional[Decimal] = None,
        nota: Optional[str] = None
    ) -> Tuple[bool, Optional[str]]:
        """
        Atualiza um projeto existente

        Args:
            projeto_id: ID do projeto
            (outros): Campos a atualizar (apenas os fornecidos serão atualizados)

        Returns:
            Tuple (sucesso, mensagem_erro)
        """
        try:
            projeto = self.obter_por_id(projeto_id)
            if not projeto:
                return False, "Projeto não encontrado"

            # Atualizar apenas campos fornecidos
            if tipo is not None:
                projeto.tipo = tipo
            if cliente_id is not None:
                projeto.cliente_id = cliente_id
            if descricao is not None:
                projeto.descricao = descricao
            if valor_sem_iva is not None:
                projeto.valor_sem_iva = valor_sem_iva
            if data_inicio is not None:
                projeto.data_inicio = data_inicio
            if data_fim is not None:
                projeto.data_fim = data_fim
            if data_faturacao is not None:
                projeto.data_faturacao = data_faturacao
            if data_vencimento is not None:
                projeto.data_vencimento = data_vencimento
            if estado is not None:
                projeto.estado = estado
            if premio_bruno is not None:
                projeto.premio_bruno = premio_bruno
            if premio_rafael is not None:
                projeto.premio_rafael = premio_rafael
            if nota is not None:
                projeto.nota = nota

            self.db_session.commit()
            return True, None

        except Exception as e:
            self.db_session.rollback()
            return False, str(e)

    def apagar(self, projeto_id: int) -> Tuple[bool, Optional[str]]:
        """
        Apaga um projeto

        Args:
            projeto_id: ID do projeto

        Returns:
            Tuple (sucesso, mensagem_erro)
        """
        try:
            projeto = self.obter_por_id(projeto_id)
            if not projeto:
                return False, "Projeto não encontrado"

            self.db_session.delete(projeto)
            self.db_session.commit()
            return True, None

        except Exception as e:
            self.db_session.rollback()
            return False, str(e)

    def obter_clientes(self) -> List[Cliente]:
        """
        Obtém lista de todos os clientes

        Returns:
            Lista de clientes
        """
        return self.db_session.query(Cliente).order_by(Cliente.nome).all()
