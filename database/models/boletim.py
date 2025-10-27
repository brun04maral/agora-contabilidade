# -*- coding: utf-8 -*-
"""
Modelo Boletim - Boletins de ajudas de custo emitidos aos sócios
"""
from datetime import datetime, date
from sqlalchemy import Column, Integer, String, DateTime, Date, Numeric, Text, Enum as SQLEnum
from database.models.base import Base
import enum


class Socio(enum.Enum):
    """Enum para identificar o sócio"""
    BRUNO = "BRUNO"
    RAFAEL = "RAFAEL"


class EstadoBoletim(enum.Enum):
    """Enum para estado do boletim"""
    PENDENTE = "PENDENTE"
    PAGO = "PAGO"


class Boletim(Base):
    """
    Modelo para boletins de ajudas de custo

    IMPORTANTE: Quando um boletim é EMITIDO, desconta IMEDIATAMENTE do saldo pessoal.
    Quando é PAGO, apenas muda o estado (já tinha descontado ao ser emitido).

    Exemplo:
    - Bruno tem saldo de €1000
    - Emite boletim de €400 → Saldo passa para €600 (estado: PENDENTE)
    - Marca boletim como PAGO → Saldo continua €600 (estado: PAGO)
    """
    __tablename__ = 'boletins'

    id = Column(Integer, primary_key=True, autoincrement=True)
    numero = Column(String(20), unique=True, nullable=False, index=True)  # Ex: #B0001
    socio = Column(SQLEnum(Socio), nullable=False, index=True)

    # Datas
    data_emissao = Column(Date, nullable=False, index=True)
    data_pagamento = Column(Date, nullable=True)

    # Valor
    valor = Column(Numeric(10, 2), nullable=False, default=0)

    # Descrição
    descricao = Column(Text, nullable=True)  # Ex: "Ajudas de custo Janeiro 2025"

    # Estado
    estado = Column(SQLEnum(EstadoBoletim), nullable=False, default=EstadoBoletim.PENDENTE, index=True)

    # Metadata
    nota = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<Boletim(id={self.id}, numero='{self.numero}', socio='{self.socio.value}', valor={self.valor}, estado='{self.estado.value}')>"

    def to_dict(self):
        """Converte para dicionário"""
        return {
            'id': self.id,
            'numero': self.numero,
            'socio': self.socio.value if self.socio else None,
            'data_emissao': self.data_emissao.isoformat() if self.data_emissao else None,
            'data_pagamento': self.data_pagamento.isoformat() if self.data_pagamento else None,
            'valor': float(self.valor) if self.valor else 0,
            'descricao': self.descricao,
            'estado': self.estado.value if self.estado else None,
            'nota': self.nota,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
