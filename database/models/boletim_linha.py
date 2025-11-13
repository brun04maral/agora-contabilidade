# -*- coding: utf-8 -*-
"""
Modelo BoletimLinha - Linhas de deslocação de um boletim itinerário
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Date, Time, Numeric, ForeignKey, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
from database.models.base import Base
import enum


class TipoDeslocacao(enum.Enum):
    """Enum para tipo de deslocação"""
    NACIONAL = "NACIONAL"
    ESTRANGEIRO = "ESTRANGEIRO"


class BoletimLinha(Base):
    """
    Modelo para linhas de deslocação de um boletim itinerário

    Cada linha representa uma deslocação (viagem/trabalho) realizada,
    com informações sobre local, projeto associado (opcional), datas,
    tipo de ajuda de custo (nacional/estrangeiro) e quilómetros percorridos.

    Campos calculados:
    - Dias: Inserido manualmente pelo usuário (cálculo complexo)
    - Horas: Informativas apenas (não usadas em cálculos)

    Relação com projetos:
    - Opcional: Deslocação pode ou não estar associada a projeto
    - Se projeto apagado: projeto_id = NULL (mantém texto em 'servico')
    """
    __tablename__ = 'boletim_linhas'

    id = Column(Integer, primary_key=True, autoincrement=True)
    boletim_id = Column(Integer, ForeignKey('boletins.id', ondelete='CASCADE'), nullable=False, index=True)
    ordem = Column(Integer, nullable=False)  # Ordenação (1, 2, 3...)

    # Relação opcional com projeto
    projeto_id = Column(Integer, ForeignKey('projetos.id', ondelete='SET NULL'), nullable=True, index=True)

    # Informação da deslocação
    servico = Column(Text, nullable=False)  # Ex: "vMix Novobanco", "reunião com cliente"
    localidade = Column(String(100), nullable=True)  # Ex: "Aguieira", "Lisboa", "Copenhaga"

    # Datas e horas (horas são informativas)
    data_inicio = Column(Date, nullable=True)
    hora_inicio = Column(Time, nullable=True)  # Informativa
    data_fim = Column(Date, nullable=True)
    hora_fim = Column(Time, nullable=True)  # Informativa

    # Tipo e valores
    tipo = Column(SQLEnum(TipoDeslocacao), nullable=False, default=TipoDeslocacao.NACIONAL)
    dias = Column(Numeric(10, 2), nullable=False, default=0)  # Inserido manualmente
    kms = Column(Integer, nullable=False, default=0)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relações
    boletim = relationship("Boletim", back_populates="linhas")
    projeto = relationship("Projeto")

    def __repr__(self):
        return f"<BoletimLinha(id={self.id}, boletim_id={self.boletim_id}, servico='{self.servico[:30]}', tipo={self.tipo.value}, dias={self.dias}, kms={self.kms})>"

    def to_dict(self):
        """Converte para dicionário"""
        return {
            'id': self.id,
            'boletim_id': self.boletim_id,
            'ordem': self.ordem,
            'projeto_id': self.projeto_id,
            'servico': self.servico,
            'localidade': self.localidade,
            'data_inicio': self.data_inicio.isoformat() if self.data_inicio else None,
            'hora_inicio': self.hora_inicio.isoformat() if self.hora_inicio else None,
            'data_fim': self.data_fim.isoformat() if self.data_fim else None,
            'hora_fim': self.hora_fim.isoformat() if self.hora_fim else None,
            'tipo': self.tipo.value if self.tipo else None,
            'dias': float(self.dias) if self.dias else 0,
            'kms': self.kms,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
