# -*- coding: utf-8 -*-
"""
Modelo ValorReferenciaAnual - Valores de referência para boletins por ano
"""
from datetime import datetime
from sqlalchemy import Column, Integer, Numeric, DateTime
from database.models.base import Base


class ValorReferenciaAnual(Base):
    """
    Modelo para valores de referência anuais dos boletins

    Armazena os valores de referência usados nos cálculos de boletins:
    - Ajuda de custo nacional (por dia)
    - Ajuda de custo estrangeiro (por dia)
    - Valor por quilómetro

    Estes valores podem mudar anualmente (leis laborais).
    Novos boletins copiam os valores do ano vigente na criação.
    """
    __tablename__ = 'valores_referencia_anual'

    id = Column(Integer, primary_key=True, autoincrement=True)
    ano = Column(Integer, unique=True, nullable=False, index=True)  # Ex: 2025, 2026

    # Valores de referência
    val_dia_nacional = Column(Numeric(10, 2), nullable=False)  # Ex: 72.65€
    val_dia_estrangeiro = Column(Numeric(10, 2), nullable=False)  # Ex: 167.07€
    val_km = Column(Numeric(10, 2), nullable=False)  # Ex: 0.40€

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<ValorReferenciaAnual(ano={self.ano}, nacional={self.val_dia_nacional}€, estrangeiro={self.val_dia_estrangeiro}€, km={self.val_km}€)>"

    def to_dict(self):
        """Converte para dicionário"""
        return {
            'id': self.id,
            'ano': self.ano,
            'val_dia_nacional': float(self.val_dia_nacional) if self.val_dia_nacional else 0,
            'val_dia_estrangeiro': float(self.val_dia_estrangeiro) if self.val_dia_estrangeiro else 0,
            'val_km': float(self.val_km) if self.val_km else 0,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
