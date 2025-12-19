# -*- coding: utf-8 -*-
"""
Modelo DespesaTemplate - Templates para despesas recorrentes mensais
Templates não entram nos cálculos financeiros, servem apenas para gerar despesas automáticas
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Numeric, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from database.models.base import Base
from database.models.despesa import TipoDespesa


class DespesaTemplate(Base):
    """
    Template de despesa recorrente mensal

    Não representa uma despesa real, apenas um template para gerar despesas automáticas.
    Não entra em cálculos financeiros.

    Exemplo: Salário pago dia 27 de cada mês
    """
    __tablename__ = 'despesa_templates'

    id = Column(Integer, primary_key=True, autoincrement=True)
    numero = Column(String(20), unique=True, nullable=False, index=True)  # Ex: #TD000001
    tipo = Column(SQLEnum(TipoDespesa), nullable=False, default=TipoDespesa.FIXA_MENSAL, index=True)

    # Credor/Fornecedor
    credor_id = Column(Integer, ForeignKey('fornecedores.id'), nullable=True)
    credor = relationship("Fornecedor")

    # Projeto associado (opcional)
    projeto_id = Column(Integer, ForeignKey('projetos.id'), nullable=True)
    projeto = relationship("Projeto")

    # Descrição
    descricao = Column(Text, nullable=False)

    # Valores
    valor_sem_iva = Column(Numeric(10, 2), nullable=False, default=0)
    valor_com_iva = Column(Numeric(10, 2), nullable=False, default=0)

    # Dia do mês para gerar (1-31)
    dia_mes = Column(Integer, nullable=False)  # Dia do mês em que a despesa deve ser gerada

    # Metadata
    nota = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<DespesaTemplate(id={self.id}, numero='{self.numero}', descricao='{self.descricao[:30]}', dia={self.dia_mes})>"

    def to_dict(self):
        """Converte para dicionário"""
        return {
            'id': self.id,
            'numero': self.numero,
            'tipo': self.tipo.value if self.tipo else None,
            'credor_id': self.credor_id,
            'credor_nome': self.credor.nome if self.credor else None,
            'projeto_id': self.projeto_id,
            'projeto_numero': self.projeto.numero if self.projeto else None,
            'descricao': self.descricao,
            'valor_sem_iva': float(self.valor_sem_iva) if self.valor_sem_iva else 0,
            'valor_com_iva': float(self.valor_com_iva) if self.valor_com_iva else 0,
            'dia_mes': self.dia_mes,
            'nota': self.nota,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
