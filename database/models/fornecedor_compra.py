# -*- coding: utf-8 -*-
"""
Modelo FornecedorCompra - Histórico de compras a fornecedores
"""
from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Numeric, DateTime, Date, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from database.models.base import Base
from database.models.freelancer_trabalho import StatusTrabalho  # Reusa enum


class FornecedorCompra(Base):
    """
    Modelo para histórico de compras a fornecedores
    Rastreabilidade: quanto foi pago a cada fornecedor por projeto/orçamento
    """
    __tablename__ = 'fornecedor_compras'

    id = Column(Integer, primary_key=True, autoincrement=True)
    fornecedor_id = Column(Integer, ForeignKey('fornecedores.id', ondelete='CASCADE'), nullable=False, index=True)
    orcamento_id = Column(Integer, ForeignKey('orcamentos.id', ondelete='SET NULL'), nullable=True)
    projeto_id = Column(Integer, ForeignKey('projetos.id', ondelete='SET NULL'), nullable=True)
    descricao = Column(Text, nullable=False)
    valor = Column(Numeric(10, 2), nullable=False)
    data = Column(Date, nullable=False, index=True)
    status = Column(SQLEnum(StatusTrabalho), nullable=False, default=StatusTrabalho.A_PAGAR, index=True)
    data_pagamento = Column(Date, nullable=True)
    nota = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relacionamentos
    fornecedor = relationship("Fornecedor", foreign_keys=[fornecedor_id])
    orcamento = relationship("Orcamento", foreign_keys=[orcamento_id])
    projeto = relationship("Projeto", foreign_keys=[projeto_id])

    def __repr__(self):
        return f"<FornecedorCompra(id={self.id}, fornecedor_id={self.fornecedor_id}, valor={self.valor})>"

    def to_dict(self):
        """Converte para dicionário"""
        return {
            'id': self.id,
            'fornecedor_id': self.fornecedor_id,
            'orcamento_id': self.orcamento_id,
            'projeto_id': self.projeto_id,
            'descricao': self.descricao,
            'valor': float(self.valor) if self.valor else 0.0,
            'data': self.data.isoformat() if self.data else None,
            'status': self.status.value if self.status else None,
            'data_pagamento': self.data_pagamento.isoformat() if self.data_pagamento else None,
            'nota': self.nota,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
