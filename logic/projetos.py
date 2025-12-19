# -*- coding: utf-8 -*-
"""
Lógica de gestão de Projetos (CRUD)
"""
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import date
from decimal import Decimal
import logging

from database.models import Projeto, Cliente, TipoProjeto, EstadoProjeto

logger = logging.getLogger(__name__)


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
        owner: str = 'BA',
        data_inicio: Optional[date] = None,
        data_fim: Optional[date] = None,
        data_faturacao: Optional[date] = None,
        data_vencimento: Optional[date] = None,
        estado: EstadoProjeto = EstadoProjeto.ATIVO,
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
                owner=owner,
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
        owner: Optional[str] = None,
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
            if owner is not None:
                projeto.owner = owner
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

    def filtrar_por_texto(self, search_text: str) -> List[Projeto]:
        """
        Filtra projetos por texto de pesquisa (nome cliente ou descrição)

        Busca case-insensitive e com substring matching em:
        - Nome do cliente
        - Descrição do projeto

        Args:
            search_text: Texto a pesquisar (mínimo 1 caracter)

        Returns:
            Lista de projetos que correspondem à pesquisa
        """
        if not search_text or len(search_text.strip()) == 0:
            return self.listar_todos()

        # Normalize search text (lowercase, strip whitespace)
        search_term = f"%{search_text.strip().lower()}%"

        # Query with JOIN to Cliente table
        projetos = self.db_session.query(Projeto).outerjoin(
            Cliente, Projeto.cliente_id == Cliente.id
        ).filter(
            # Search in cliente.nome OR projeto.descricao (case-insensitive)
            # Use func.lower() for case-insensitive LIKE
            (Cliente.nome.ilike(search_term)) |
            (Projeto.descricao.ilike(search_term))
        ).order_by(desc(Projeto.created_at)).all()

        return projetos

    def obter_clientes(self) -> List[Cliente]:
        """
        Obtém lista de todos os clientes

        Returns:
            Lista de clientes
        """
        return self.db_session.query(Cliente).order_by(Cliente.nome).all()

    def duplicar_projeto(self, projeto_id: int) -> Tuple[bool, Optional[Projeto], Optional[str]]:
        """
        Duplica um projeto existente

        Args:
            projeto_id: ID do projeto a duplicar

        Returns:
            Tuple (sucesso, novo_projeto, mensagem_erro)
        """
        try:
            projeto_original = self.obter_por_id(projeto_id)
            if not projeto_original:
                return False, None, "Projeto não encontrado"

            # Gerar novo número
            ultimo_projeto = self.db_session.query(Projeto).order_by(
                desc(Projeto.id)
            ).first()

            if ultimo_projeto:
                ultimo_num = int(ultimo_projeto.numero.replace('#P', ''))
                novo_num = ultimo_num + 1
            else:
                novo_num = 1

            numero = f"#P{novo_num:04d}"

            # Criar cópia do projeto
            novo_projeto = Projeto(
                numero=numero,
                tipo=projeto_original.tipo,
                cliente_id=projeto_original.cliente_id,
                descricao=f"{projeto_original.descricao} (Cópia)",
                valor_sem_iva=projeto_original.valor_sem_iva,
                data_inicio=None,  # Resetar datas
                data_fim=None,
                data_faturacao=None,
                data_vencimento=None,
                data_pagamento=None,
                estado=EstadoProjeto.ATIVO,  # Sempre começa como ATIVO
                premio_bruno=projeto_original.premio_bruno,
                premio_rafael=projeto_original.premio_rafael,
                nota=projeto_original.nota
            )

            self.db_session.add(novo_projeto)
            self.db_session.commit()
            self.db_session.refresh(novo_projeto)

            logger.info(f"Projeto {projeto_original.numero} duplicado como {numero}")
            return True, novo_projeto, None

        except Exception as e:
            self.db_session.rollback()
            logger.error(f"Erro ao duplicar projeto: {e}")
            return False, None, str(e)

    def mudar_estado(
        self,
        projeto_id: int,
        novo_estado: EstadoProjeto,
        data_pagamento: Optional[date] = None
    ) -> Tuple[bool, Optional[str]]:
        """
        Muda o estado de um projeto

        Args:
            projeto_id: ID do projeto
            novo_estado: Novo estado do projeto
            data_pagamento: Data de pagamento (opcional, apenas para PAGO)

        Returns:
            Tuple (sucesso, mensagem_erro)
        """
        try:
            projeto = self.obter_por_id(projeto_id)
            if not projeto:
                return False, "Projeto não encontrado"

            estado_anterior = projeto.estado
            projeto.estado = novo_estado

            # Se marcar como PAGO, definir data_pagamento
            if novo_estado == EstadoProjeto.PAGO and data_pagamento:
                projeto.data_pagamento = data_pagamento
            elif novo_estado != EstadoProjeto.PAGO:
                # Se não for PAGO, limpar data_pagamento
                projeto.data_pagamento = None

            self.db_session.commit()

            logger.info(
                f"Projeto {projeto.numero}: estado alterado de "
                f"{estado_anterior.value} para {novo_estado.value}"
            )
            return True, None

        except Exception as e:
            self.db_session.rollback()
            logger.error(f"Erro ao mudar estado do projeto: {e}")
            return False, str(e)

    def atualizar_estados_projetos(self) -> int:
        """
        Atualiza projetos ATIVO para FINALIZADO quando data_fim < hoje

        Conforme BUSINESS_LOGIC.md Secção 3.2:
        - Projetos com estado ATIVO e data_fim no passado → FINALIZADO
        - Transição automática

        Returns:
            Número de projetos atualizados
        """
        try:
            hoje = date.today()

            # Buscar projetos ativos com data_fim no passado
            projetos_a_finalizar = self.db_session.query(Projeto).filter(
                Projeto.estado == EstadoProjeto.ATIVO,
                Projeto.data_fim.isnot(None),
                Projeto.data_fim < hoje
            ).all()

            count = 0
            for projeto in projetos_a_finalizar:
                projeto.estado = EstadoProjeto.FINALIZADO
                logger.info(
                    f"Projeto {projeto.numero} finalizado automaticamente "
                    f"(data_fim: {projeto.data_fim})"
                )
                count += 1

            if count > 0:
                self.db_session.commit()
                logger.info(f"Total de {count} projeto(s) finalizado(s) automaticamente")

            return count

        except Exception as e:
            logger.error(f"Erro ao atualizar estados de projetos: {e}")
            self.db_session.rollback()
            return 0
