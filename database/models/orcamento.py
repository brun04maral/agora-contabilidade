"""
Modelos de dados para o sistema de Orçamentos
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Date, Boolean, Numeric
from sqlalchemy.orm import relationship
from datetime import datetime
from database.models.base import Base


class Orcamento(Base):
    """
    Modelo para Orçamentos V2
    Sistema dual: LADO CLIENTE (proposta comercial) + LADO EMPRESA (repartição interna)
    """
    __tablename__ = 'orcamentos'

    id = Column(Integer, primary_key=True)

    # Identificação
    codigo = Column(String(100), nullable=False, unique=True)

    # Owner (BA ou RR) - responsável pelo orçamento
    owner = Column(String(2), nullable=False)  # 'BA' ou 'RR'

    # Dados do cliente
    cliente_id = Column(Integer, ForeignKey('clientes.id'), nullable=False)
    cliente = relationship("Cliente", back_populates="orcamentos")

    # Metadados do orçamento
    data_criacao = Column(Date, nullable=False)
    data_evento = Column(String(200), nullable=True)  # Texto livre com datas
    local_evento = Column(String(200), nullable=True)

    # Valores (calculados automaticamente)
    valor_total = Column(Numeric(10, 2), nullable=True)  # TOTAL CLIENTE

    # Status do orçamento
    status = Column(String(20), nullable=False, default='rascunho')  # 'rascunho', 'aprovado', 'rejeitado'

    # Link para projeto (quando convertido)
    projeto_id = Column(Integer, ForeignKey('projetos.id'), nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Relacionamentos
    secoes = relationship("OrcamentoSecao", back_populates="orcamento", cascade="all, delete-orphan")
    itens = relationship("OrcamentoItem", back_populates="orcamento", cascade="all, delete-orphan")
    reparticoes = relationship("OrcamentoReparticao", back_populates="orcamento", cascade="all, delete-orphan")
    projeto = relationship("Projeto", back_populates="orcamentos")

    def __repr__(self):
        return f"<Orcamento(codigo='{self.codigo}', owner='{self.owner}', cliente='{self.cliente.nome if self.cliente else 'N/A'}')>"


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
    Modelo para Items do LADO CLIENTE
    Tipos: servico, equipamento, transporte, refeicao, outro
    """
    __tablename__ = 'orcamento_itens'

    id = Column(Integer, primary_key=True)
    orcamento_id = Column(Integer, ForeignKey('orcamentos.id'), nullable=False)
    secao_id = Column(Integer, ForeignKey('orcamento_secoes.id'), nullable=False)

    # Tipo de item (V2)
    tipo = Column(String(20), nullable=False)  # 'servico', 'equipamento', 'transporte', 'refeicao', 'outro'

    # Dados comuns
    descricao = Column(Text, nullable=False)
    ordem = Column(Integer, nullable=False, default=0)

    # Para serviços e equipamento
    quantidade = Column(Integer, nullable=True)
    dias = Column(Integer, nullable=True)
    preco_unitario = Column(Numeric(10, 2), nullable=True)
    desconto = Column(Numeric(5, 4), nullable=True, default=0)  # 0-1 (ex: 0.1 = 10%)

    # Para despesas tipo transporte (campos específicos)
    kms = Column(Numeric(10, 2), nullable=True)
    valor_por_km = Column(Numeric(10, 2), nullable=True)

    # Para despesas tipo refeição (campos específicos)
    num_refeicoes = Column(Integer, nullable=True)
    valor_por_refeicao = Column(Numeric(10, 2), nullable=True)

    # Para despesas tipo outro (valor fixo)
    valor_fixo = Column(Numeric(10, 2), nullable=True)

    # Total calculado
    total = Column(Numeric(10, 2), nullable=False)

    # Relação com equipamento (opcional)
    equipamento_id = Column(Integer, ForeignKey('equipamento.id'), nullable=True)
    equipamento = relationship("Equipamento")

    # Relacionamentos
    orcamento = relationship("Orcamento", back_populates="itens")
    secao = relationship("OrcamentoSecao", back_populates="itens")

    def calcular_total(self):
        """Calcula o total do item baseado no tipo"""
        if self.tipo in ['servico', 'equipamento']:
            # Total = Quantidade × Dias × Preço_Unitário × (1 - Desconto)
            return (self.quantidade or 0) * (self.dias or 1) * (self.preco_unitario or 0) * (1 - (self.desconto or 0))
        elif self.tipo == 'transporte':
            # Total = Kms × Valor_por_Km
            return (self.kms or 0) * (self.valor_por_km or 0)
        elif self.tipo == 'refeicao':
            # Total = Nº_Refeições × Valor_por_Refeição
            return (self.num_refeicoes or 0) * (self.valor_por_refeicao or 0)
        elif self.tipo == 'outro':
            # Total = Valor fixo
            return self.valor_fixo or 0
        return 0

    def __repr__(self):
        return f"<OrcamentoItem(tipo='{self.tipo}', descricao='{self.descricao[:30]}...', total={self.total})>"


class OrcamentoReparticao(Base):
    """
    Modelo para Items do LADO EMPRESA
    Tipos: servico, equipamento, despesa (espelhada), comissao
    """
    __tablename__ = 'orcamento_reparticoes'

    id = Column(Integer, primary_key=True)
    orcamento_id = Column(Integer, ForeignKey('orcamentos.id'), nullable=False)

    # Tipo de item empresa (V2)
    tipo = Column(String(20), nullable=False)  # 'servico', 'equipamento', 'despesa', 'comissao'

    # Dados comuns
    descricao = Column(Text, nullable=False)
    ordem = Column(Integer, nullable=False, default=0)

    # Beneficiário (obrigatório exceto para despesas espelhadas)
    beneficiario = Column(String(50), nullable=True)  # 'BA', 'RR', 'AGORA', 'FREELANCER_[id]', 'FORNECEDOR_[id]'

    # Para serviços e equipamento
    quantidade = Column(Integer, nullable=True)
    dias = Column(Integer, nullable=True)
    valor_unitario = Column(Numeric(10, 2), nullable=True)

    # Para comissões
    percentagem = Column(Numeric(8, 3), nullable=True)  # Ex: 5.125% = 5.125
    base_calculo = Column(Numeric(10, 2), nullable=True)  # Base para cálculo da comissão

    # Para despesas espelhadas (campos replicados do lado CLIENTE)
    kms = Column(Numeric(10, 2), nullable=True)
    valor_por_km = Column(Numeric(10, 2), nullable=True)
    num_refeicoes = Column(Integer, nullable=True)
    valor_por_refeicao = Column(Numeric(10, 2), nullable=True)
    valor_fixo = Column(Numeric(10, 2), nullable=True)

    # ID do item cliente correspondente (para despesas espelhadas)
    item_cliente_id = Column(Integer, ForeignKey('orcamento_itens.id'), nullable=True)

    # Total calculado
    total = Column(Numeric(10, 2), nullable=False)

    # Relações opcionais
    equipamento_id = Column(Integer, ForeignKey('equipamento.id'), nullable=True)
    equipamento = relationship("Equipamento")

    fornecedor_id = Column(Integer, ForeignKey('fornecedores.id'), nullable=True)
    fornecedor = relationship("Fornecedor")

    # Relacionamento
    orcamento = relationship("Orcamento", back_populates="reparticoes")

    def calcular_total(self):
        """Calcula o total baseado no tipo"""
        if self.tipo in ['servico', 'equipamento']:
            # Total = Quantidade × Dias × Valor_Unitário
            return (self.quantidade or 0) * (self.dias or 1) * (self.valor_unitario or 0)
        elif self.tipo == 'comissao':
            # Total = Base × (Percentagem / 100)
            return (self.base_calculo or 0) * ((self.percentagem or 0) / 100)
        elif self.tipo == 'despesa':
            # Replicado do item cliente - calcular baseado nos campos
            if self.kms is not None:
                return (self.kms or 0) * (self.valor_por_km or 0)
            elif self.num_refeicoes is not None:
                return (self.num_refeicoes or 0) * (self.valor_por_refeicao or 0)
            elif self.valor_fixo is not None:
                return self.valor_fixo or 0
        return 0

    def __repr__(self):
        return f"<OrcamentoReparticao(tipo='{self.tipo}', beneficiario='{self.beneficiario}', total={self.total})>"


