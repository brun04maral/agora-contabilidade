"""
SQLAlchemy Models
REUTILIZA a lógica existente do projeto
"""
from sqlalchemy import Column, Integer, String, Decimal, Date, DateTime, Boolean, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import enum as py_enum


class TipoProjeto(py_enum.Enum):
    EMPRESA = "EMPRESA"
    PESSOAL_BRUNO = "PESSOAL_BRUNO"
    PESSOAL_RAFAEL = "PESSOAL_RAFAEL"


class EstadoProjeto(py_enum.Enum):
    ORCAMENTO = "ORCAMENTO"
    EM_CURSO = "EM_CURSO"
    CONCLUIDO = "CONCLUIDO"
    FATURADO = "FATURADO"
    RECEBIDO = "RECEBIDO"
    ANULADO = "ANULADO"


class TipoDespesa(py_enum.Enum):
    FIXA_MENSAL = "FIXA_MENSAL"
    PESSOAL_BRUNO = "PESSOAL_BRUNO"
    PESSOAL_RAFAEL = "PESSOAL_RAFAEL"
    EQUIPAMENTO = "EQUIPAMENTO"
    PROJETO = "PROJETO"


class EstadoDespesa(py_enum.Enum):
    PENDENTE = "PENDENTE"
    PAGO = "PAGO"
    CANCELADO = "CANCELADO"


class Socio(Base):
    __tablename__ = "socios"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), unique=True, nullable=False)
    nome_completo = Column(String(200), nullable=False)
    email = Column(String(200))
    telefone = Column(String(20))
    nif = Column(String(9))
    iban = Column(String(34))
    ativo = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    projetos_owner = relationship("Projeto", back_populates="owner", foreign_keys="Projeto.owner_id")
    despesas_socio = relationship("Despesa", back_populates="socio")

    def calcular_saldo(self, db):
        """Calcula saldo do sócio (IN - OUT)"""
        from decimal import Decimal

        ins = Decimal('0.00')
        outs = Decimal('0.00')

        # INs: Projetos pessoais RECEBIDOS
        projetos = db.query(Projeto).filter(
            Projeto.owner_id == self.id,
            Projeto.estado == EstadoProjeto.RECEBIDO
        ).all()
        ins += sum([p.valor_total for p in projetos], Decimal('0.00'))

        # Prémios
        if self.nome == 'BA':
            projetos_empresa = db.query(Projeto).filter(
                Projeto.estado == EstadoProjeto.RECEBIDO
            ).all()
            ins += sum([p.premio_bruno for p in projetos_empresa], Decimal('0.00'))
        elif self.nome == 'RR':
            projetos_empresa = db.query(Projeto).filter(
                Projeto.estado == EstadoProjeto.RECEBIDO
            ).all()
            ins += sum([p.premio_rafael for p in projetos_empresa], Decimal('0.00'))

        # OUTs: Despesas fixas (÷2) + Despesas pessoais
        despesas_fixas = db.query(Despesa).filter(
            Despesa.tipo == TipoDespesa.FIXA_MENSAL,
            Despesa.estado == EstadoDespesa.PAGO
        ).all()
        outs += sum([d.valor for d in despesas_fixas], Decimal('0.00')) / 2

        despesas_pessoais = db.query(Despesa).filter(
            Despesa.socio_id == self.id,
            Despesa.estado == EstadoDespesa.PAGO,
            Despesa.tipo != TipoDespesa.FIXA_MENSAL
        ).all()
        outs += sum([d.valor for d in despesas_pessoais], Decimal('0.00'))

        return ins - outs


class Cliente(Base):
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(200), nullable=False)
    nif = Column(String(9))
    email = Column(String(200))
    telefone = Column(String(20))
    morada = Column(Text)
    notas = Column(Text)
    ativo = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    projetos = relationship("Projeto", back_populates="cliente")


class Fornecedor(Base):
    __tablename__ = "fornecedores"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(200), nullable=False)
    nif = Column(String(9))
    email = Column(String(200))
    telefone = Column(String(20))
    morada = Column(Text)
    iban = Column(String(34))
    notas = Column(Text)
    ativo = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    despesas = relationship("Despesa", back_populates="fornecedor")


class Projeto(Base):
    __tablename__ = "projetos"

    id = Column(Integer, primary_key=True, index=True)
    numero = Column(String(20), unique=True, nullable=False)
    nome = Column(String(200), nullable=False)
    tipo = Column(Enum(TipoProjeto), nullable=False)
    estado = Column(Enum(EstadoProjeto), default=EstadoProjeto.ORCAMENTO)

    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False)
    owner_id = Column(Integer, ForeignKey("socios.id"))

    valor_total = Column(Decimal(10, 2), nullable=False)
    premio_bruno = Column(Decimal(10, 2), default=0)
    premio_rafael = Column(Decimal(10, 2), default=0)

    data_inicio = Column(Date, nullable=False)
    data_entrega = Column(Date)
    data_pagamento = Column(Date)

    descricao = Column(Text)
    notas = Column(Text)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    cliente = relationship("Cliente", back_populates="projetos")
    owner = relationship("Socio", back_populates="projetos_owner", foreign_keys=[owner_id])
    despesas = relationship("Despesa", back_populates="projeto")


class Despesa(Base):
    __tablename__ = "despesas"

    id = Column(Integer, primary_key=True, index=True)
    numero = Column(String(20), unique=True, nullable=False)
    tipo = Column(Enum(TipoDespesa), nullable=False)
    descricao = Column(String(200), nullable=False)

    fornecedor_id = Column(Integer, ForeignKey("fornecedores.id"))
    socio_id = Column(Integer, ForeignKey("socios.id"))
    projeto_id = Column(Integer, ForeignKey("projetos.id"))

    valor = Column(Decimal(10, 2), nullable=False)
    iva = Column(Decimal(10, 2), default=0)

    data_despesa = Column(Date, nullable=False)
    data_pagamento = Column(Date)

    estado = Column(Enum(EstadoDespesa), default=EstadoDespesa.PENDENTE)

    notas = Column(Text)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    fornecedor = relationship("Fornecedor", back_populates="despesas")
    socio = relationship("Socio", back_populates="despesas_socio")
    projeto = relationship("Projeto", back_populates="despesas")
