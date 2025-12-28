"""
Pydantic Schemas para validação e serialização
"""
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any
from datetime import date, datetime
from decimal import Decimal


# ============================================================================
# SÓCIO
# ============================================================================

class SocioBase(BaseModel):
    nome: str
    nome_completo: str
    email: Optional[EmailStr] = None
    telefone: Optional[str] = None
    nif: Optional[str] = None
    iban: Optional[str] = None
    ativo: bool = True


class SocioCreate(SocioBase):
    pass


class SocioOut(SocioBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============================================================================
# CLIENTE
# ============================================================================

class ClienteBase(BaseModel):
    nome: str
    nif: Optional[str] = None
    email: Optional[EmailStr] = None
    telefone: Optional[str] = None
    morada: Optional[str] = None
    notas: Optional[str] = None
    ativo: bool = True


class ClienteCreate(ClienteBase):
    pass


class ClienteOut(ClienteBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============================================================================
# FORNECEDOR
# ============================================================================

class FornecedorBase(BaseModel):
    nome: str
    nif: Optional[str] = None
    email: Optional[EmailStr] = None
    telefone: Optional[str] = None
    morada: Optional[str] = None
    iban: Optional[str] = None
    notas: Optional[str] = None
    ativo: bool = True


class FornecedorCreate(FornecedorBase):
    pass


class FornecedorOut(FornecedorBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============================================================================
# PROJETO
# ============================================================================

class ProjetoBase(BaseModel):
    numero: str
    nome: str
    tipo: str
    estado: str = "ORCAMENTO"
    cliente_id: int
    owner_id: Optional[int] = None
    valor_total: Decimal
    premio_bruno: Decimal = Decimal('0.00')
    premio_rafael: Decimal = Decimal('0.00')
    data_inicio: date
    data_entrega: Optional[date] = None
    data_pagamento: Optional[date] = None
    descricao: Optional[str] = None
    notas: Optional[str] = None


class ProjetoCreate(ProjetoBase):
    pass


class ProjetoOut(ProjetoBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============================================================================
# DESPESA
# ============================================================================

class DespesaBase(BaseModel):
    numero: str
    tipo: str
    descricao: str
    fornecedor_id: Optional[int] = None
    socio_id: Optional[int] = None
    projeto_id: Optional[int] = None
    valor: Decimal
    iva: Decimal = Decimal('0.00')
    data_despesa: date
    data_pagamento: Optional[date] = None
    estado: str = "PENDENTE"
    notas: Optional[str] = None


class DespesaCreate(DespesaBase):
    pass


class DespesaOut(DespesaBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============================================================================
# SALDOS
# ============================================================================

class SaldoSocio(BaseModel):
    nome_completo: str
    saldo: float
    ins: float
    outs: float


class SaldosResponse(BaseModel):
    saldos: Dict[str, SaldoSocio]
