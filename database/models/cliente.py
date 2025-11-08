# -*- coding: utf-8 -*-
"""
Modelo Cliente - Base de dados de clientes da Agora Media
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.orm import relationship
from database.models.base import Base


class Cliente(Base):
    """
    Modelo para armazenar informações de clientes
    """
    __tablename__ = 'clientes'

    id = Column(Integer, primary_key=True, autoincrement=True)
    numero = Column(String(20), unique=True, nullable=False, index=True)  # Ex: #C0001
    nome = Column(String(255), nullable=False)
    nif = Column(String(20), nullable=True)
    morada = Column(Text, nullable=True)
    pais = Column(String(100), nullable=True, default='Portugal')
    contacto = Column(String(50), nullable=True)
    email = Column(String(255), nullable=True)
    angariacao = Column(String(255), nullable=True)  # Como foi angariado
    nota = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relacionamentos
    projetos = relationship("Projeto", back_populates="cliente", cascade="all, delete-orphan")
    orcamentos = relationship("Orcamento", back_populates="cliente", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Cliente(id={self.id}, numero='{self.numero}', nome='{self.nome}')>"

    def to_dict(self):
        """Converte para dicionário"""
        return {
            'id': self.id,
            'numero': self.numero,
            'nome': self.nome,
            'nif': self.nif,
            'morada': self.morada,
            'pais': self.pais,
            'contacto': self.contacto,
            'email': self.email,
            'angariacao': self.angariacao,
            'nota': self.nota,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
