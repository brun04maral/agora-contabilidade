"""
Modelos de dados para o sistema de Orçamentos
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Date, Boolean, Numeric
from sqlalchemy.orm import relationship
from datetime import datetime
from database.models.base import Base


class Orcamento(Base):
    """
    Modelo para Orçamentos (Budgets)
    Representa tanto versões Cliente (apresentação) quanto Empresa (económico interno)
    """
    __tablename__ = 'orcamentos'

    id = Column(Integer, primary_key=True)

    # Identificação
    codigo = Column(String(100), nullable=False, unique=True)  # Ex: "20250909_Orçamento-SGS_Conf"
    versao = Column(String(10), nullable=True)  # Ex: "V1", "V2", null para Empresa ECO_
    tipo = Column(String(20), nullable=False, default='cliente')  # 'cliente' ou 'empresa'

    # Dados do cliente
    cliente_id = Column(Integer, ForeignKey('clientes.id'), nullable=True)
    cliente = relationship("Cliente", back_populates="orcamentos")

    # Metadados do orçamento
    data_criacao = Column(Date, nullable=False)  # Data da proposta
    data_evento = Column(String(200), nullable=True)  # Pode ter múltiplas datas
    local_evento = Column(String(200), nullable=True)
    descricao_proposta = Column(Text, nullable=True)

    # Valores
    valor_total = Column(Numeric(10, 2), nullable=True)
    total_parcial_1 = Column(Numeric(10, 2), nullable=True)  # Serviços + Equipamento
    total_parcial_2 = Column(Numeric(10, 2), nullable=True)  # Despesas

    # Notas e status
    notas_contratuais = Column(Text, nullable=True)
    status = Column(String(20), nullable=False, default='rascunho')  # rascunho, enviado, aprovado, rejeitado

    # Timestamps
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Relacionamentos
    secoes = relationship("OrcamentoSecao", back_populates="orcamento", cascade="all, delete-orphan")
    itens = relationship("OrcamentoItem", back_populates="orcamento", cascade="all, delete-orphan")
    reparticoes = relationship("OrcamentoReparticao", back_populates="orcamento", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Orcamento(codigo='{self.codigo}', versao='{self.versao}', cliente='{self.cliente.nome if self.cliente else 'N/A'}')>"


class OrcamentoSecao(Base):
    """
    Modelo para Secções do Orçamento (Serviços, Equipamento, Despesas, etc.)
    Suporta hierarquia com subsecções (ex: Vídeo e Som dentro de Equipamento)
    """
    __tablename__ = 'orcamento_secoes'

    id = Column(Integer, primary_key=True)
    orcamento_id = Column(Integer, ForeignKey('orcamentos.id'), nullable=False)

    # Tipo de secção
    tipo = Column(String(50), nullable=False)  # 'servicos', 'equipamento', 'despesas', 'video', 'som', 'iluminacao'
    nome = Column(String(100), nullable=False)  # Nome de exibição
    ordem = Column(Integer, nullable=False, default=0)  # Ordem de apresentação

    # Hierarquia (para subsecções)
    parent_id = Column(Integer, ForeignKey('orcamento_secoes.id'), nullable=True)

    # Subtotal (opcional, calculado)
    subtotal = Column(Numeric(10, 2), nullable=True)

    # Relacionamentos
    orcamento = relationship("Orcamento", back_populates="secoes")
    parent = relationship("OrcamentoSecao", remote_side=[id], backref="subsecoes")
    itens = relationship("OrcamentoItem", back_populates="secao", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<OrcamentoSecao(nome='{self.nome}', tipo='{self.tipo}')>"


class OrcamentoItem(Base):
    """
    Modelo para Items/Linhas do Orçamento
    Cada item representa uma linha no orçamento (serviço, equipamento, ou despesa)
    """
    __tablename__ = 'orcamento_itens'

    id = Column(Integer, primary_key=True)
    orcamento_id = Column(Integer, ForeignKey('orcamentos.id'), nullable=False)
    secao_id = Column(Integer, ForeignKey('orcamento_secoes.id'), nullable=False)

    # Dados do item
    descricao = Column(Text, nullable=False)
    quantidade = Column(Integer, nullable=False, default=1)
    dias = Column(Integer, nullable=False, default=1)
    preco_unitario = Column(Numeric(10, 2), nullable=False)
    desconto = Column(Numeric(5, 4), nullable=False, default=0)  # 0.1 = 10%
    total = Column(Numeric(10, 2), nullable=False)  # Calculado: (quantidade * dias * preco_unitario) * (1 - desconto)

    # Ordem
    ordem = Column(Integer, nullable=False, default=0)

    # Relação com equipamento (opcional, para items de equipamento)
    equipamento_id = Column(Integer, ForeignKey('equipamento.id'), nullable=True)
    equipamento = relationship("Equipamento")

    # Campos exclusivos para orçamentos Empresa (ECO_)
    reparticao = Column(Numeric(5, 2), nullable=True)  # % de distribuição
    afetacao = Column(String(50), nullable=True)  # BA, RR, Agora, Freelancers, Despesa
    investimento = Column(Numeric(10, 2), nullable=True)
    amortizacao = Column(Numeric(10, 2), nullable=True)

    # Relacionamentos
    orcamento = relationship("Orcamento", back_populates="itens")
    secao = relationship("OrcamentoSecao", back_populates="itens")

    def calcular_total(self):
        """Calcula o total do item"""
        return (self.quantidade * self.dias * self.preco_unitario) * (1 - self.desconto)

    def __repr__(self):
        return f"<OrcamentoItem(descricao='{self.descricao[:30]}...', total={self.total})>"


class OrcamentoReparticao(Base):
    """
    Modelo para Repartição/Distribuição do Orçamento
    Representa a secção "Contas finais" nos orçamentos Empresa (ECO_)
    Mostra a distribuição por entidade: BA, RR, Agora, Freelancers, Despesas
    """
    __tablename__ = 'orcamento_reparticoes'

    id = Column(Integer, primary_key=True)
    orcamento_id = Column(Integer, ForeignKey('orcamentos.id'), nullable=False)

    # Entidade
    entidade = Column(String(50), nullable=False)  # 'BA', 'RR', 'Agora', 'Freelancers', 'Despesas'

    # Valores
    valor = Column(Numeric(10, 2), nullable=False)
    percentagem = Column(Numeric(5, 2), nullable=True)  # % do total

    # Ordem
    ordem = Column(Integer, nullable=False, default=0)

    # Relacionamento
    orcamento = relationship("Orcamento", back_populates="reparticoes")

    def __repr__(self):
        return f"<OrcamentoReparticao(entidade='{self.entidade}', valor={self.valor})>"
