"""
Modelo Equipamento - Inventário de equipamento da empresa
"""
from datetime import datetime, date
from sqlalchemy import Column, Integer, String, DateTime, Date, Numeric, Text
from database.models.base import Base


class Equipamento(Base):
    """
    Modelo para inventário de equipamento

    Compras de equipamento para uso pessoal podem descontar do saldo pessoal
    """
    __tablename__ = 'equipamento'

    id = Column(Integer, primary_key=True, autoincrement=True)
    numero = Column(String(20), unique=True, nullable=False, index=True)  # Ex: #E0001

    # Descrição
    nome = Column(String(255), nullable=False)
    categoria = Column(String(100), nullable=True)  # Ex: Câmera, Iluminação, Áudio
    marca = Column(String(100), nullable=True)
    modelo = Column(String(100), nullable=True)

    # Compra
    data_compra = Column(Date, nullable=True)
    valor_compra = Column(Numeric(10, 2), nullable=False, default=0)
    fornecedor = Column(String(255), nullable=True)

    # Estado
    estado = Column(String(50), nullable=True)  # Ex: Novo, Usado, Manutenção
    localizacao = Column(String(255), nullable=True)

    # Uso pessoal (se aplicável)
    uso_pessoal = Column(String(50), nullable=True)  # Ex: Bruno, Rafael, Empresa

    # Metadata
    nota = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<Equipamento(id={self.id}, numero='{self.numero}', nome='{self.nome}')>"

    def to_dict(self):
        """Converte para dicionário"""
        return {
            'id': self.id,
            'numero': self.numero,
            'nome': self.nome,
            'categoria': self.categoria,
            'marca': self.marca,
            'modelo': self.modelo,
            'data_compra': self.data_compra.isoformat() if self.data_compra else None,
            'valor_compra': float(self.valor_compra) if self.valor_compra else 0,
            'fornecedor': self.fornecedor,
            'estado': self.estado,
            'localizacao': self.localizacao,
            'uso_pessoal': self.uso_pessoal,
            'nota': self.nota,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
