# -*- coding: utf-8 -*-
"""
Modelo FreelancerTrabalho - Histórico de trabalhos de freelancers
"""
from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Numeric, DateTime, Date, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from database.models.base import Base
import enum


class StatusTrabalho(enum.Enum):
    """Enum para status de trabalho/compra"""
    A_PAGAR = "a_pagar"
    PAGO = "pago"
    CANCELADO = "cancelado"


class FreelancerTrabalho(Base):
    """
    Modelo para histórico de trabalhos de freelancers
    Rastreabilidade: quanto foi pago a cada freelancer por projeto/orçamento
    """
    __tablename__ = 'freelancer_trabalhos'

    id = Column(Integer, primary_key=True, autoincrement=True)
    freelancer_id = Column(Integer, ForeignKey('freelancers.id', ondelete='CASCADE'), nullable=False, index=True)
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
    freelancer = relationship("Freelancer", back_populates="trabalhos")
    orcamento = relationship("Orcamento", foreign_keys=[orcamento_id])
    projeto = relationship("Projeto", foreign_keys=[projeto_id])

    def __repr__(self):
        return f"<FreelancerTrabalho(id={self.id}, freelancer_id={self.freelancer_id}, valor={self.valor})>"

    def to_dict(self):
        """Converte para dicionário"""
        return {
            'id': self.id,
            'freelancer_id': self.freelancer_id,
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
