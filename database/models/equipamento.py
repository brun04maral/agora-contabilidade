# -*- coding: utf-8 -*-
"""
Modelo Equipamento - Inventário de equipamento da empresa
"""
from datetime import datetime, date
from sqlalchemy import Column, Integer, String, DateTime, Date, Numeric, Text
from database.models.base import Base


class Equipamento(Base):
    """
    Modelo para inventário de equipamento

    Usado em orçamentos para calcular custos e amortização
    """
    __tablename__ = 'equipamento'

    id = Column(Integer, primary_key=True, autoincrement=True)
    numero = Column(String(20), unique=True, nullable=False, index=True)  # Ex: #E0001

    # Identificação
    produto = Column(String(255), nullable=True)  # Nome/Descrição do produto
    tipo = Column(String(100), nullable=True)  # Ex: Vídeo, Áudio, Iluminação
    label = Column(String(100), nullable=True)  # Categoria/Label
    descricao = Column(Text, nullable=True)  # Descrição detalhada

    # Especificações técnicas
    numero_serie = Column(String(100), nullable=True)
    mac_address = Column(String(50), nullable=True)
    referencia = Column(String(100), nullable=True)  # Referência interna
    quantidade = Column(Integer, default=1, nullable=True)
    tamanho = Column(String(100), nullable=True)

    # Compra
    data_compra = Column(Date, nullable=True)
    valor_compra = Column(Numeric(10, 2), nullable=True, default=0)  # VALOR s/IVA
    fornecedor = Column(String(255), nullable=True)
    fatura_url = Column(Text, nullable=True)  # Link para fatura

    # Aluguer (IMPORTANTE para orçamentos!)
    preco_aluguer = Column(Numeric(10, 2), nullable=True, default=0)  # PREÇO ALUGUER s/IVA
    amortizacao_vezes = Column(Integer, default=0, nullable=True)  # Vezes que foi alugado

    # Estado
    estado = Column(String(50), nullable=True)  # Ex: Novo, Usado, Manutenção
    localizacao = Column(String(255), nullable=True)
    foto_url = Column(Text, nullable=True)  # Link para foto

    # Uso pessoal (se aplicável)
    uso_pessoal = Column(String(50), nullable=True)  # Ex: Bruno, Rafael, Empresa

    # Metadata
    nota = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<Equipamento(id={self.id}, numero='{self.numero}', produto='{self.produto}')>"

    def to_dict(self):
        """Converte para dicionário"""
        return {
            'id': self.id,
            'numero': self.numero,
            'produto': self.produto,
            'tipo': self.tipo,
            'label': self.label,
            'descricao': self.descricao,
            'numero_serie': self.numero_serie,
            'mac_address': self.mac_address,
            'referencia': self.referencia,
            'quantidade': self.quantidade,
            'tamanho': self.tamanho,
            'data_compra': self.data_compra.isoformat() if self.data_compra else None,
            'valor_compra': float(self.valor_compra) if self.valor_compra else 0,
            'fornecedor': self.fornecedor,
            'fatura_url': self.fatura_url,
            'preco_aluguer': float(self.preco_aluguer) if self.preco_aluguer else 0,
            'amortizacao_vezes': self.amortizacao_vezes or 0,
            'estado': self.estado,
            'localizacao': self.localizacao,
            'foto_url': self.foto_url,
            'uso_pessoal': self.uso_pessoal,
            'nota': self.nota,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
