# -*- coding: utf-8 -*-
"""
Logic de gestão de Trabalhos de Freelancers
"""
from sqlalchemy.orm import Session
from sqlalchemy import desc
from database.models import FreelancerTrabalho, StatusTrabalho, Freelancer
from typing import List, Tuple, Optional
from decimal import Decimal
from datetime import date


class FreelancerTrabalhosManager:
    """
    Gestor de operações CRUD para FreelancerTrabalho
    Rastreabilidade de trabalhos pagos a freelancers
    """

    def __init__(self, db_session: Session):
        """
        Initialize manager

        Args:
            db_session: SQLAlchemy database session
        """
        self.db = db_session

    def listar_todos(self, freelancer_id: int = None, status: StatusTrabalho = None) -> List[FreelancerTrabalho]:
        """
        List all trabalhos

        Args:
            freelancer_id: Filter by freelancer (optional)
            status: Filter by status (optional)

        Returns:
            List of FreelancerTrabalho objects
        """
        query = self.db.query(FreelancerTrabalho)

        if freelancer_id:
            query = query.filter(FreelancerTrabalho.freelancer_id == freelancer_id)

        if status:
            query = query.filter(FreelancerTrabalho.status == status)

        return query.order_by(desc(FreelancerTrabalho.data)).all()

    def listar_a_pagar(self, freelancer_id: int = None) -> List[FreelancerTrabalho]:
        """
        List trabalhos com status 'a_pagar'

        Args:
            freelancer_id: Filter by freelancer (optional)

        Returns:
            List of FreelancerTrabalho objects with status a_pagar
        """
        query = self.db.query(FreelancerTrabalho).filter(
            FreelancerTrabalho.status == StatusTrabalho.A_PAGAR
        )

        if freelancer_id:
            query = query.filter(FreelancerTrabalho.freelancer_id == freelancer_id)

        return query.order_by(desc(FreelancerTrabalho.data)).all()

    def buscar_por_id(self, trabalho_id: int) -> Optional[FreelancerTrabalho]:
        """
        Find trabalho by ID

        Args:
            trabalho_id: Trabalho ID

        Returns:
            FreelancerTrabalho object or None
        """
        return self.db.query(FreelancerTrabalho).filter(FreelancerTrabalho.id == trabalho_id).first()

    def criar(
        self,
        freelancer_id: int,
        descricao: str,
        valor: Decimal,
        data: date,
        orcamento_id: int = None,
        projeto_id: int = None,
        status: StatusTrabalho = StatusTrabalho.A_PAGAR,
        data_pagamento: date = None,
        nota: str = None
    ) -> Tuple[bool, Optional[FreelancerTrabalho], str]:
        """
        Create new trabalho

        Args:
            freelancer_id: ID do freelancer
            descricao: Descrição do trabalho
            valor: Valor a pagar
            data: Data do trabalho
            orcamento_id: ID do orçamento (opcional)
            projeto_id: ID do projeto (opcional)
            status: Status (default: a_pagar)
            data_pagamento: Data de pagamento (opcional)
            nota: Nota adicional (opcional)

        Returns:
            Tuple (success, trabalho, message)
        """
        # Validações
        if not freelancer_id:
            return False, None, "Freelancer é obrigatório"

        # Verificar se freelancer existe
        freelancer = self.db.query(Freelancer).filter(Freelancer.id == freelancer_id).first()
        if not freelancer:
            return False, None, f"Freelancer ID {freelancer_id} não encontrado"

        if not descricao or not descricao.strip():
            return False, None, "Descrição é obrigatória"

        if not valor or valor <= 0:
            return False, None, "Valor deve ser maior que 0"

        if not data:
            return False, None, "Data é obrigatória"

        try:
            novo_trabalho = FreelancerTrabalho(
                freelancer_id=freelancer_id,
                orcamento_id=orcamento_id,
                projeto_id=projeto_id,
                descricao=descricao.strip(),
                valor=valor,
                data=data,
                status=status,
                data_pagamento=data_pagamento,
                nota=nota.strip() if nota else None
            )

            self.db.add(novo_trabalho)
            self.db.commit()
            self.db.refresh(novo_trabalho)

            return True, novo_trabalho, f"Trabalho criado com sucesso (€{float(valor):.2f})"

        except Exception as e:
            self.db.rollback()
            return False, None, f"Erro ao criar trabalho: {str(e)}"

    def atualizar(self, trabalho_id: int, **kwargs) -> Tuple[bool, Optional[FreelancerTrabalho], str]:
        """
        Update trabalho

        Args:
            trabalho_id: Trabalho ID
            **kwargs: Fields to update

        Returns:
            Tuple (success, trabalho, message)
        """
        trabalho = self.buscar_por_id(trabalho_id)

        if not trabalho:
            return False, None, "Trabalho não encontrado"

        # Validações
        if 'valor' in kwargs and (not kwargs['valor'] or kwargs['valor'] <= 0):
            return False, None, "Valor deve ser maior que 0"

        if 'descricao' in kwargs and (not kwargs['descricao'] or not kwargs['descricao'].strip()):
            return False, None, "Descrição é obrigatória"

        try:
            for key, value in kwargs.items():
                if hasattr(trabalho, key):
                    # Strip strings
                    if isinstance(value, str):
                        value = value.strip() if value else None
                    setattr(trabalho, key, value)

            self.db.commit()
            self.db.refresh(trabalho)

            return True, trabalho, "Trabalho atualizado com sucesso"

        except Exception as e:
            self.db.rollback()
            return False, None, f"Erro ao atualizar trabalho: {str(e)}"

    def marcar_como_pago(
        self,
        trabalho_id: int,
        data_pagamento: date = None
    ) -> Tuple[bool, Optional[FreelancerTrabalho], str]:
        """
        Mark trabalho as paid

        Args:
            trabalho_id: Trabalho ID
            data_pagamento: Data de pagamento (default: hoje)

        Returns:
            Tuple (success, trabalho, message)
        """
        if not data_pagamento:
            data_pagamento = date.today()

        return self.atualizar(
            trabalho_id,
            status=StatusTrabalho.PAGO,
            data_pagamento=data_pagamento
        )

    def cancelar(self, trabalho_id: int) -> Tuple[bool, Optional[FreelancerTrabalho], str]:
        """
        Cancel trabalho

        Args:
            trabalho_id: Trabalho ID

        Returns:
            Tuple (success, trabalho, message)
        """
        return self.atualizar(trabalho_id, status=StatusTrabalho.CANCELADO)

    def apagar(self, trabalho_id: int) -> Tuple[bool, str]:
        """
        Delete trabalho

        Args:
            trabalho_id: Trabalho ID

        Returns:
            Tuple (success, message)
        """
        trabalho = self.buscar_por_id(trabalho_id)

        if not trabalho:
            return False, "Trabalho não encontrado"

        try:
            self.db.delete(trabalho)
            self.db.commit()

            return True, "Trabalho apagado com sucesso"

        except Exception as e:
            self.db.rollback()
            return False, f"Erro ao apagar trabalho: {str(e)}"

    def calcular_total_a_pagar(self, freelancer_id: int = None) -> Decimal:
        """
        Calculate total amount to pay

        Args:
            freelancer_id: Filter by freelancer (optional)

        Returns:
            Total amount to pay
        """
        query = self.db.query(FreelancerTrabalho).filter(
            FreelancerTrabalho.status == StatusTrabalho.A_PAGAR
        )

        if freelancer_id:
            query = query.filter(FreelancerTrabalho.freelancer_id == freelancer_id)

        trabalhos = query.all()
        total = sum(trabalho.valor for trabalho in trabalhos)

        return Decimal(str(total))
