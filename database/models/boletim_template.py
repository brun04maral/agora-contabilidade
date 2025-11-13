# -*- coding: utf-8 -*-
"""
Modelo BoletimTemplate - Templates para geração recorrente de boletins
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum as SQLEnum
from database.models.base import Base
from database.models.boletim import Socio  # Reutilizar enum


class BoletimTemplate(Base):
    """
    Modelo para templates de boletins recorrentes

    Templates permitem gerar boletins automaticamente mensalmente.
    Armazenam informações básicas (sócio, dia do mês) mas NÃO armazenam:
    - Valores de referência (usa sempre valores do ano vigente)
    - Linhas pré-definidas (cada mês é diferente)

    Apenas 2 templates esperados: Bruno (#TB000001) e Rafael (#TB000002)

    Geração automática:
    - Verificação por dia do mês (dia_mes)
    - Cria boletim com cabeçalho vazio
    - Valores de referência copiados do ano vigente
    - Nice-to-have: Pré-preencher com projetos do sócio no mês
    """
    __tablename__ = 'boletim_templates'

    id = Column(Integer, primary_key=True, autoincrement=True)
    numero = Column(String(20), unique=True, nullable=False, index=True)  # Ex: #TB000001
    nome = Column(String(200), nullable=False)  # Ex: "Boletim Bruno Mensal"
    socio = Column(SQLEnum(Socio), nullable=False, index=True)
    dia_mes = Column(Integer, nullable=False)  # 1-31: Dia do mês para gerar

    # Controlo
    ativo = Column(Boolean, nullable=False, default=True, index=True)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<BoletimTemplate(numero='{self.numero}', nome='{self.nome}', socio={self.socio.value}, dia={self.dia_mes}, ativo={self.ativo})>"

    def to_dict(self):
        """Converte para dicionário"""
        return {
            'id': self.id,
            'numero': self.numero,
            'nome': self.nome,
            'socio': self.socio.value if self.socio else None,
            'dia_mes': self.dia_mes,
            'ativo': self.ativo,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
