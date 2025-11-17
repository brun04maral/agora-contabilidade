# -*- coding: utf-8 -*-
"""
Logic de gestão de Compras a Fornecedores
"""
from sqlalchemy.orm import Session
from sqlalchemy import desc
from database.models import FornecedorCompra, StatusTrabalho, Fornecedor
from typing import List, Tuple, Optional
from decimal import Decimal
from datetime import date


class FornecedorComprasManager:
    """
    Gestor de operações CRUD para FornecedorCompra
    Rastreabilidade de compras a fornecedores
    """

    def __init__(self, db_session: Session):
        """
        Initialize manager

        Args:
            db_session: SQLAlchemy database session
        """
        self.db = db_session

    def listar_todos(self, fornecedor_id: int = None, status: StatusTrabalho = None) -> List[FornecedorCompra]:
        """
        List all compras

        Args:
            fornecedor_id: Filter by fornecedor (optional)
            status: Filter by status (optional)

        Returns:
            List of FornecedorCompra objects
        """
        query = self.db.query(FornecedorCompra)

        if fornecedor_id:
            query = query.filter(FornecedorCompra.fornecedor_id == fornecedor_id)

        if status:
            query = query.filter(FornecedorCompra.status == status)

        return query.order_by(desc(FornecedorCompra.data)).all()

    def listar_a_pagar(self, fornecedor_id: int = None) -> List[FornecedorCompra]:
        """
        List compras com status 'a_pagar'

        Args:
            fornecedor_id: Filter by fornecedor (optional)

        Returns:
            List of FornecedorCompra objects with status a_pagar
        """
        query = self.db.query(FornecedorCompra).filter(
            FornecedorCompra.status == StatusTrabalho.A_PAGAR
        )

        if fornecedor_id:
            query = query.filter(FornecedorCompra.fornecedor_id == fornecedor_id)

        return query.order_by(desc(FornecedorCompra.data)).all()

    def buscar_por_id(self, compra_id: int) -> Optional[FornecedorCompra]:
        """
        Find compra by ID

        Args:
            compra_id: Compra ID

        Returns:
            FornecedorCompra object or None
        """
        return self.db.query(FornecedorCompra).filter(FornecedorCompra.id == compra_id).first()

    def criar(
        self,
        fornecedor_id: int,
        descricao: str,
        valor: Decimal,
        data: date,
        orcamento_id: int = None,
        projeto_id: int = None,
        status: StatusTrabalho = StatusTrabalho.A_PAGAR,
        data_pagamento: date = None,
        nota: str = None
    ) -> Tuple[bool, Optional[FornecedorCompra], str]:
        """
        Create new compra

        Args:
            fornecedor_id: ID do fornecedor
            descricao: Descrição da compra
            valor: Valor a pagar
            data: Data da compra
            orcamento_id: ID do orçamento (opcional)
            projeto_id: ID do projeto (opcional)
            status: Status (default: a_pagar)
            data_pagamento: Data de pagamento (opcional)
            nota: Nota adicional (opcional)

        Returns:
            Tuple (success, compra, message)
        """
        # Validações
        if not fornecedor_id:
            return False, None, "Fornecedor é obrigatório"

        # Verificar se fornecedor existe
        fornecedor = self.db.query(Fornecedor).filter(Fornecedor.id == fornecedor_id).first()
        if not fornecedor:
            return False, None, f"Fornecedor ID {fornecedor_id} não encontrado"

        if not descricao or not descricao.strip():
            return False, None, "Descrição é obrigatória"

        if not valor or valor <= 0:
            return False, None, "Valor deve ser maior que 0"

        if not data:
            return False, None, "Data é obrigatória"

        try:
            nova_compra = FornecedorCompra(
                fornecedor_id=fornecedor_id,
                orcamento_id=orcamento_id,
                projeto_id=projeto_id,
                descricao=descricao.strip(),
                valor=valor,
                data=data,
                status=status,
                data_pagamento=data_pagamento,
                nota=nota.strip() if nota else None
            )

            self.db.add(nova_compra)
            self.db.commit()
            self.db.refresh(nova_compra)

            return True, nova_compra, f"Compra criada com sucesso (€{float(valor):.2f})"

        except Exception as e:
            self.db.rollback()
            return False, None, f"Erro ao criar compra: {str(e)}"

    def atualizar(self, compra_id: int, **kwargs) -> Tuple[bool, Optional[FornecedorCompra], str]:
        """
        Update compra

        Args:
            compra_id: Compra ID
            **kwargs: Fields to update

        Returns:
            Tuple (success, compra, message)
        """
        compra = self.buscar_por_id(compra_id)

        if not compra:
            return False, None, "Compra não encontrada"

        # Validações
        if 'valor' in kwargs and (not kwargs['valor'] or kwargs['valor'] <= 0):
            return False, None, "Valor deve ser maior que 0"

        if 'descricao' in kwargs and (not kwargs['descricao'] or not kwargs['descricao'].strip()):
            return False, None, "Descrição é obrigatória"

        try:
            for key, value in kwargs.items():
                if hasattr(compra, key):
                    # Strip strings
                    if isinstance(value, str):
                        value = value.strip() if value else None
                    setattr(compra, key, value)

            self.db.commit()
            self.db.refresh(compra)

            return True, compra, "Compra atualizada com sucesso"

        except Exception as e:
            self.db.rollback()
            return False, None, f"Erro ao atualizar compra: {str(e)}"

    def marcar_como_pago(
        self,
        compra_id: int,
        data_pagamento: date = None
    ) -> Tuple[bool, Optional[FornecedorCompra], str]:
        """
        Mark compra as paid

        Args:
            compra_id: Compra ID
            data_pagamento: Data de pagamento (default: hoje)

        Returns:
            Tuple (success, compra, message)
        """
        if not data_pagamento:
            data_pagamento = date.today()

        return self.atualizar(
            compra_id,
            status=StatusTrabalho.PAGO,
            data_pagamento=data_pagamento
        )

    def cancelar(self, compra_id: int) -> Tuple[bool, Optional[FornecedorCompra], str]:
        """
        Cancel compra

        Args:
            compra_id: Compra ID

        Returns:
            Tuple (success, compra, message)
        """
        return self.atualizar(compra_id, status=StatusTrabalho.CANCELADO)

    def apagar(self, compra_id: int) -> Tuple[bool, str]:
        """
        Delete compra

        Args:
            compra_id: Compra ID

        Returns:
            Tuple (success, message)
        """
        compra = self.buscar_por_id(compra_id)

        if not compra:
            return False, "Compra não encontrada"

        try:
            self.db.delete(compra)
            self.db.commit()

            return True, "Compra apagada com sucesso"

        except Exception as e:
            self.db.rollback()
            return False, f"Erro ao apagar compra: {str(e)}"

    def calcular_total_a_pagar(self, fornecedor_id: int = None) -> Decimal:
        """
        Calculate total amount to pay

        Args:
            fornecedor_id: Filter by fornecedor (optional)

        Returns:
            Total amount to pay
        """
        query = self.db.query(FornecedorCompra).filter(
            FornecedorCompra.status == StatusTrabalho.A_PAGAR
        )

        if fornecedor_id:
            query = query.filter(FornecedorCompra.fornecedor_id == fornecedor_id)

        compras = query.all()
        total = sum(compra.valor for compra in compras)

        return Decimal(str(total))
