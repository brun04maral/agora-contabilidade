# -*- coding: utf-8 -*-
"""
Modelo Freelancer - Profissionais externos
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean
from sqlalchemy.orm import relationship
from database.models.base import Base


class Freelancer(Base):
    """
    Modelo para armazenar profissionais freelancers externos
    Usados como beneficiários em OrcamentoReparticao
    """
    __tablename__ = 'freelancers'

    id = Column(Integer, primary_key=True, autoincrement=True)
    numero = Column(String(20), unique=True, nullable=False, index=True)  # Ex: #F0001
    nome = Column(String(120), nullable=False, index=True)
    nif = Column(String(20), nullable=True)
    email = Column(String(120), nullable=True)
    telefone = Column(String(20), nullable=True)
    iban = Column(String(50), nullable=True)
    morada = Column(Text, nullable=True)
    especialidade = Column(String(100), nullable=True)  # Ex: Cinegrafista, Editor, etc
    notas = Column(Text, nullable=True)
    ativo = Column(Boolean, default=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relacionamentos
    trabalhos = relationship("FreelancerTrabalho", back_populates="freelancer", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Freelancer(id={self.id}, numero='{self.numero}', nome='{self.nome}')>"

    def to_dict(self):
        """Converte para dicionário"""
        return {
            'id': self.id,
            'numero': self.numero,
            'nome': self.nome,
            'nif': self.nif,
            'email': self.email,
            'telefone': self.telefone,
            'iban': self.iban,
            'morada': self.morada,
            'especialidade': self.especialidade,
            'notas': self.notas,
            'ativo': self.ativo,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
