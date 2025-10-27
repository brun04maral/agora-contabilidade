# -*- coding: utf-8 -*-
"""
Modelo Fornecedor - Base de dados de fornecedores/credores
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from database.models.base import Base
import enum


class EstatutoFornecedor(enum.Enum):
    """Enum para estatuto do fornecedor"""
    EMPRESA = "EMPRESA"
    FREELANCER = "FREELANCER"
    ESTADO = "ESTADO"


class Fornecedor(Base):
    """
    Modelo para armazenar informações de fornecedores/credores
    """
    __tablename__ = 'fornecedores'

    id = Column(Integer, primary_key=True, autoincrement=True)
    numero = Column(String(20), unique=True, nullable=False, index=True)  # Ex: #F0001
    nome = Column(String(255), nullable=False)
    estatuto = Column(SQLEnum(EstatutoFornecedor), nullable=False, default=EstatutoFornecedor.FREELANCER)
    area = Column(String(255), nullable=True)  # Ex: Produção, Pós-produção, etc
    funcao = Column(String(255), nullable=True)  # Ex: Técnico de som, Editor, etc
    classificacao = Column(Integer, nullable=True)  # 1-5 estrelas
    validade_seguro_trabalho = Column(DateTime, nullable=True)
    nif = Column(String(20), nullable=True)
    iban = Column(String(50), nullable=True)
    morada = Column(Text, nullable=True)
    contacto = Column(String(50), nullable=True)
    email = Column(String(255), nullable=True)
    nota = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relacionamentos
    despesas = relationship("Despesa", back_populates="credor", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Fornecedor(id={self.id}, numero='{self.numero}', nome='{self.nome}')>"

    def to_dict(self):
        """Converte para dicionário"""
        return {
            'id': self.id,
            'numero': self.numero,
            'nome': self.nome,
            'estatuto': self.estatuto.value if self.estatuto else None,
            'area': self.area,
            'funcao': self.funcao,
            'classificacao': self.classificacao,
            'validade_seguro_trabalho': self.validade_seguro_trabalho.isoformat() if self.validade_seguro_trabalho else None,
            'nif': self.nif,
            'iban': self.iban,
            'morada': self.morada,
            'contacto': self.contacto,
            'email': self.email,
            'nota': self.nota,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
