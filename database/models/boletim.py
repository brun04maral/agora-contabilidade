# -*- coding: utf-8 -*-
"""
Modelo Boletim - Boletins de ajudas de custo emitidos aos sócios (Boletim Itinerário)
"""
from datetime import datetime, date
from sqlalchemy import Column, Integer, String, DateTime, Date, Numeric, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
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
    Modelo para boletins de ajudas de custo (Boletim Itinerário)

    Sistema expandido com suporte para múltiplas linhas de deslocação.
    Cada boletim contém:
    - Cabeçalho: mês/ano, valores de referência do ano, totais calculados
    - Linhas: deslocações individuais (BoletimLinha)

    Totais calculados automaticamente:
    - total_ajudas_nacionais = sum(linha.dias where tipo==NACIONAL) × val_dia_nacional
    - total_ajudas_estrangeiro = sum(linha.dias where tipo==ESTRANGEIRO) × val_dia_estrangeiro
    - total_kms = sum(linha.kms) × val_km
    - valor_total = soma dos 3 totais

    IMPORTANTE: Boletins descontam do saldo quando PAGOS (não quando emitidos).

    Exemplo:
    - Bruno tem saldo de €1000
    - Emite boletim de €400 → Saldo continua €1000 (estado: PENDENTE)
    - Marca boletim como PAGO → Saldo passa para €600 (estado: PAGO)
    """
    __tablename__ = 'boletins'

    id = Column(Integer, primary_key=True, autoincrement=True)
    numero = Column(String(20), unique=True, nullable=False, index=True)  # Ex: #B0001
    socio = Column(SQLEnum(Socio), nullable=False, index=True)

    # Período
    mes = Column(Integer, nullable=True, index=True)  # 1-12
    ano = Column(Integer, nullable=True, index=True)  # Ex: 2025

    # Datas
    data_emissao = Column(Date, nullable=False, index=True)
    data_pagamento = Column(Date, nullable=True)

    # Valores de Referência (copiados do ano vigente)
    val_dia_nacional = Column(Numeric(10, 2), nullable=True)  # Ex: 72.65€
    val_dia_estrangeiro = Column(Numeric(10, 2), nullable=True)  # Ex: 167.07€
    val_km = Column(Numeric(10, 2), nullable=True)  # Ex: 0.40€

    # Totais Calculados Automaticamente
    total_ajudas_nacionais = Column(Numeric(10, 2), nullable=False, default=0)
    total_ajudas_estrangeiro = Column(Numeric(10, 2), nullable=False, default=0)
    total_kms = Column(Numeric(10, 2), nullable=False, default=0)
    valor_total = Column(Numeric(10, 2), nullable=False, default=0)  # Soma dos 3 totais

    # Valor antigo (manter para compatibilidade temporária)
    valor = Column(Numeric(10, 2), nullable=True, default=0)

    # Descrição (manter para compatibilidade temporária)
    descricao = Column(Text, nullable=True)

    # Estado
    estado = Column(SQLEnum(EstadoBoletim), nullable=False, default=EstadoBoletim.PENDENTE, index=True)

    # Metadata
    nota = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relações
    linhas = relationship("BoletimLinha", back_populates="boletim", cascade="all, delete-orphan", lazy="joined")

    def __repr__(self):
        return f"<Boletim(id={self.id}, numero='{self.numero}', socio='{self.socio.value}', valor={self.valor}, estado='{self.estado.value}')>"

    def to_dict(self):
        """Converte para dicionário"""
        return {
            'id': self.id,
            'numero': self.numero,
            'socio': self.socio.value if self.socio else None,
            'mes': self.mes,
            'ano': self.ano,
            'data_emissao': self.data_emissao.isoformat() if self.data_emissao else None,
            'data_pagamento': self.data_pagamento.isoformat() if self.data_pagamento else None,
            'val_dia_nacional': float(self.val_dia_nacional) if self.val_dia_nacional else 0,
            'val_dia_estrangeiro': float(self.val_dia_estrangeiro) if self.val_dia_estrangeiro else 0,
            'val_km': float(self.val_km) if self.val_km else 0,
            'total_ajudas_nacionais': float(self.total_ajudas_nacionais) if self.total_ajudas_nacionais else 0,
            'total_ajudas_estrangeiro': float(self.total_ajudas_estrangeiro) if self.total_ajudas_estrangeiro else 0,
            'total_kms': float(self.total_kms) if self.total_kms else 0,
            'valor_total': float(self.valor_total) if self.valor_total else 0,
            'valor': float(self.valor) if self.valor else 0,  # Compatibilidade
            'descricao': self.descricao,  # Compatibilidade
            'estado': self.estado.value if self.estado else None,
            'nota': self.nota,
            'linhas_count': len(self.linhas) if self.linhas else 0,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
