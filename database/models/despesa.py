# -*- coding: utf-8 -*-
"""
Modelo Despesa - Despesas da empresa e despesas pessoais dos sócios
"""
from datetime import datetime, date
from sqlalchemy import Column, Integer, String, DateTime, Date, Numeric, ForeignKey, Text, Enum as SQLEnum, Boolean
from sqlalchemy.orm import relationship
from database.models.base import Base
import enum


class TipoDespesa(enum.Enum):
    """
    Enum para tipo de despesa - CRÍTICO para cálculo de saldos!

    FIXA_MENSAL: Dividida por 2, cada sócio desconta metade nos OUTs
    PESSOAL_BRUNO/PESSOAL_RAFAEL: Desconta apenas do sócio específico
    EQUIPAMENTO: Pode descontar do saldo se for para uso pessoal
    """
    FIXA_MENSAL = "FIXA_MENSAL"
    PESSOAL_BRUNO = "PESSOAL_BRUNO"
    PESSOAL_RAFAEL = "PESSOAL_RAFAEL"
    EQUIPAMENTO = "EQUIPAMENTO"
    PROJETO = "PROJETO"  # Despesa associada a um projeto específico


class EstadoDespesa(enum.Enum):
    """Enum para estado da despesa"""
    PENDENTE = "PENDENTE"
    VENCIDO = "VENCIDO"
    PAGO = "PAGO"


class Despesa(Base):
    """
    Modelo para armazenar despesas da empresa

    IMPORTANTE: O campo 'tipo' determina como impacta os saldos pessoais:
    - FIXA_MENSAL: Divide por 2, cada sócio desconta metade
    - PESSOAL_BRUNO/PESSOAL_RAFAEL: Desconta apenas do sócio específico
    - EQUIPAMENTO: Pode descontar do saldo se configurado
    - PROJETO: Associada a projeto, não impacta saldos diretamente
    """
    __tablename__ = 'despesas'

    id = Column(Integer, primary_key=True, autoincrement=True)
    numero = Column(String(20), unique=True, nullable=False, index=True)  # Ex: #D000001
    tipo = Column(SQLEnum(TipoDespesa), nullable=False, default=TipoDespesa.FIXA_MENSAL, index=True)

    # Data
    data = Column(Date, nullable=False, index=True)

    # Credor/Fornecedor
    credor_id = Column(Integer, ForeignKey('fornecedores.id'), nullable=True)
    credor = relationship("Fornecedor", back_populates="despesas")

    # Projeto associado (opcional)
    projeto_id = Column(Integer, ForeignKey('projetos.id'), nullable=True)
    projeto = relationship("Projeto", back_populates="despesas")

    # Descrição
    descricao = Column(Text, nullable=False)

    # Valores
    valor_sem_iva = Column(Numeric(10, 2), nullable=False, default=0)
    valor_com_iva = Column(Numeric(10, 2), nullable=False, default=0)

    # Estado
    estado = Column(SQLEnum(EstadoDespesa), nullable=False, default=EstadoDespesa.PENDENTE, index=True)
    data_pagamento = Column(Date, nullable=True)

    # Metadata
    nota = Column(Text, nullable=True)

    # Recorrência (para despesas automáticas mensais)
    is_recorrente = Column(Boolean, nullable=False, default=False)  # Se True, é um template de despesa recorrente
    dia_recorrencia = Column(Integer, nullable=True)  # Dia do mês (1-31) para gerar automaticamente
    despesa_template_id = Column(Integer, ForeignKey('despesas.id'), nullable=True)  # FK para o template que gerou esta despesa
    despesa_template = relationship("Despesa", remote_side=[id], backref="despesas_geradas")

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<Despesa(id={self.id}, numero='{self.numero}', tipo='{self.tipo.value}', valor={self.valor_sem_iva})>"

    def to_dict(self):
        """Converte para dicionário"""
        return {
            'id': self.id,
            'numero': self.numero,
            'tipo': self.tipo.value if self.tipo else None,
            'data': self.data.isoformat() if self.data else None,
            'credor_id': self.credor_id,
            'credor_nome': self.credor.nome if self.credor else None,
            'projeto_id': self.projeto_id,
            'projeto_numero': self.projeto.numero if self.projeto else None,
            'descricao': self.descricao,
            'valor_sem_iva': float(self.valor_sem_iva) if self.valor_sem_iva else 0,
            'valor_com_iva': float(self.valor_com_iva) if self.valor_com_iva else 0,
            'estado': self.estado.value if self.estado else None,
            'data_pagamento': self.data_pagamento.isoformat() if self.data_pagamento else None,
            'nota': self.nota,
            'is_recorrente': self.is_recorrente,
            'dia_recorrencia': self.dia_recorrencia,
            'despesa_template_id': self.despesa_template_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
