"""
Modelo Projeto - Projetos da Agora Media e projetos pessoais dos sócios
"""
from datetime import datetime, date
from sqlalchemy import Column, Integer, String, DateTime, Date, Numeric, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from database.models.base import Base
import enum


class TipoProjeto(enum.Enum):
    """Enum para tipo de projeto - CRÍTICO para cálculo de saldos!"""
    EMPRESA = "EMPRESA"  # Projeto da empresa (não entra nos INs pessoais, só prémios)
    PESSOAL_BRUNO = "PESSOAL_BRUNO"  # Projeto freelance do Bruno faturado pela empresa
    PESSOAL_RAFAEL = "PESSOAL_RAFAEL"  # Projeto freelance do Rafael faturado pela empresa


class EstadoProjeto(enum.Enum):
    """Enum para estado do projeto"""
    NAO_FATURADO = "NAO_FATURADO"
    FATURADO = "FATURADO"
    RECEBIDO = "RECEBIDO"


class Projeto(Base):
    """
    Modelo para armazenar projetos da Agora Media

    IMPORTANTE: O campo 'tipo' determina se o valor entra nos saldos pessoais:
    - EMPRESA: Apenas prémios entram nos saldos
    - PESSOAL_BRUNO/PESSOAL_RAFAEL: Valor total entra nos INs do sócio
    """
    __tablename__ = 'projetos'

    id = Column(Integer, primary_key=True, autoincrement=True)
    numero = Column(String(20), unique=True, nullable=False, index=True)  # Ex: #P0001
    tipo = Column(SQLEnum(TipoProjeto), nullable=False, default=TipoProjeto.EMPRESA, index=True)

    # Cliente
    cliente_id = Column(Integer, ForeignKey('clientes.id'), nullable=True)
    cliente = relationship("Cliente", back_populates="projetos")

    # Datas
    data_inicio = Column(Date, nullable=True)
    data_fim = Column(Date, nullable=True)

    # Descrição
    descricao = Column(Text, nullable=False)

    # Valores
    valor_sem_iva = Column(Numeric(10, 2), nullable=False, default=0)

    # Faturação
    data_faturacao = Column(Date, nullable=True)
    data_vencimento = Column(Date, nullable=True)
    estado = Column(SQLEnum(EstadoProjeto), nullable=False, default=EstadoProjeto.NAO_FATURADO, index=True)

    # Prémios (cachets + comissões) - para projetos da EMPRESA
    premio_bruno = Column(Numeric(10, 2), nullable=True, default=0)
    premio_rafael = Column(Numeric(10, 2), nullable=True, default=0)

    # Metadata
    nota = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relacionamentos
    despesas = relationship("Despesa", back_populates="projeto")

    def __repr__(self):
        return f"<Projeto(id={self.id}, numero='{self.numero}', tipo='{self.tipo.value}', valor={self.valor_sem_iva})>"

    def to_dict(self):
        """Converte para dicionário"""
        return {
            'id': self.id,
            'numero': self.numero,
            'tipo': self.tipo.value if self.tipo else None,
            'cliente_id': self.cliente_id,
            'cliente_nome': self.cliente.nome if self.cliente else None,
            'data_inicio': self.data_inicio.isoformat() if self.data_inicio else None,
            'data_fim': self.data_fim.isoformat() if self.data_fim else None,
            'descricao': self.descricao,
            'valor_sem_iva': float(self.valor_sem_iva) if self.valor_sem_iva else 0,
            'data_faturacao': self.data_faturacao.isoformat() if self.data_faturacao else None,
            'data_vencimento': self.data_vencimento.isoformat() if self.data_vencimento else None,
            'estado': self.estado.value if self.estado else None,
            'premio_bruno': float(self.premio_bruno) if self.premio_bruno else 0,
            'premio_rafael': float(self.premio_rafael) if self.premio_rafael else 0,
            'nota': self.nota,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
