"""
FastAPI Backend for Agora Contabilidade
Reutiliza a lógica existente Python
"""
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import os

from database import get_db, engine, Base
from models import Socio, Projeto, Despesa, Cliente, Fornecedor
from schemas import (
    SocioOut, SocioCreate,
    ProjetoOut, ProjetoCreate,
    DespesaOut, DespesaCreate,
    ClienteOut, ClienteCreate,
    FornecedorOut, FornecedorCreate,
    SaldosResponse
)

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Agora Contabilidade API",
    description="API REST para gestão contabilística",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # Vite dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# SALDOS (Core feature)
# ============================================================================

@app.get("/api/saldos", response_model=SaldosResponse, tags=["Saldos"])
def get_saldos(db: Session = Depends(get_db)):
    """Calcula saldos dos sócios (50/50)"""
    socios = db.query(Socio).filter(Socio.ativo == True).all()

    saldos = {}
    for socio in socios:
        saldo = socio.calcular_saldo(db)
        saldos[socio.nome] = {
            "nome_completo": socio.nome_completo,
            "saldo": float(saldo),
            "ins": 0.0,  # TODO: implementar breakdown
            "outs": 0.0,
        }

    return {"saldos": saldos}


# ============================================================================
# SÓCIOS
# ============================================================================

@app.get("/api/socios", response_model=List[SocioOut], tags=["Sócios"])
def list_socios(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Listar todos os sócios"""
    socios = db.query(Socio).offset(skip).limit(limit).all()
    return socios


@app.get("/api/socios/{socio_id}", response_model=SocioOut, tags=["Sócios"])
def get_socio(socio_id: int, db: Session = Depends(get_db)):
    """Obter sócio por ID"""
    socio = db.query(Socio).filter(Socio.id == socio_id).first()
    if not socio:
        raise HTTPException(status_code=404, detail="Sócio não encontrado")
    return socio


@app.post("/api/socios", response_model=SocioOut, tags=["Sócios"])
def create_socio(socio: SocioCreate, db: Session = Depends(get_db)):
    """Criar novo sócio"""
    db_socio = Socio(**socio.dict())
    db.add(db_socio)
    db.commit()
    db.refresh(db_socio)
    return db_socio


# ============================================================================
# CLIENTES
# ============================================================================

@app.get("/api/clientes", response_model=List[ClienteOut], tags=["Clientes"])
def list_clientes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Listar todos os clientes"""
    clientes = db.query(Cliente).offset(skip).limit(limit).all()
    return clientes


@app.post("/api/clientes", response_model=ClienteOut, tags=["Clientes"])
def create_cliente(cliente: ClienteCreate, db: Session = Depends(get_db)):
    """Criar novo cliente"""
    db_cliente = Cliente(**cliente.dict())
    db.add(db_cliente)
    db.commit()
    db.refresh(db_cliente)
    return db_cliente


# ============================================================================
# PROJETOS
# ============================================================================

@app.get("/api/projetos", response_model=List[ProjetoOut], tags=["Projetos"])
def list_projetos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Listar todos os projetos"""
    projetos = db.query(Projeto).offset(skip).limit(limit).all()
    return projetos


@app.post("/api/projetos", response_model=ProjetoOut, tags=["Projetos"])
def create_projeto(projeto: ProjetoCreate, db: Session = Depends(get_db)):
    """Criar novo projeto"""
    db_projeto = Projeto(**projeto.dict())
    db.add(db_projeto)
    db.commit()
    db.refresh(db_projeto)
    return db_projeto


# ============================================================================
# DESPESAS
# ============================================================================

@app.get("/api/despesas", response_model=List[DespesaOut], tags=["Despesas"])
def list_despesas(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Listar todas as despesas"""
    despesas = db.query(Despesa).offset(skip).limit(limit).all()
    return despesas


@app.post("/api/despesas", response_model=DespesaOut, tags=["Despesas"])
def create_despesa(despesa: DespesaCreate, db: Session = Depends(get_db)):
    """Criar nova despesa"""
    db_despesa = Despesa(**despesa.dict())
    db.add(db_despesa)
    db.commit()
    db.refresh(db_despesa)
    return db_despesa


# ============================================================================
# HEALTH CHECK
# ============================================================================

@app.get("/health", tags=["Health"])
def health_check():
    """Health check endpoint"""
    return {"status": "ok", "message": "Agora API is running"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
