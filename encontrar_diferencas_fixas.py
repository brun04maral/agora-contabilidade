#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import pandas as pd
from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

from database.models import Despesa, TipoDespesa, EstadoDespesa

# Setup database
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///agora_media.db')
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

print("="*80)
print("🔍 IDENTIFICAR 4 DESPESAS EXTRAS NA DB")
print("="*80)

# Ler despesas fixas do Excel
xl_path = 'CONTABILIDADE_FINAL_20251029.xlsx'
df = pd.read_excel(xl_path, sheet_name='DESPESAS', header=4)

hoje = date(2025, 10, 29)

numeros_excel = set()

for idx, row in df.iterrows():
    # Coluna 8 = Periodicidade
    periodicidade = str(row.iloc[8]) if pd.notna(row.iloc[8]) else ''

    # Verificar se é despesa fixa (periodicidade "Mensal")
    if 'mensal' not in periodicidade.lower():
        continue

    # Verificar se não é ordenado/sub. alimentação
    tipo_str = str(row.iloc[6]) if pd.notna(row.iloc[6]) else ''
    if any(x in tipo_str.lower() for x in ['ordenado', 'alimentação']):
        continue

    # Construir data_vencimento
    ano = int(row.iloc[1]) if pd.notna(row.iloc[1]) else None
    mes = int(row.iloc[2]) if pd.notna(row.iloc[2]) else None
    dia = int(row.iloc[3]) if pd.notna(row.iloc[3]) else None

    data_vencimento = None
    if ano and mes and dia:
        try:
            data_vencimento = date(ano, mes, dia)
        except:
            pass

    if data_vencimento and data_vencimento <= hoje:
        numero = str(row.iloc[0]) if pd.notna(row.iloc[0]) else ''
        numeros_excel.add(numero)

print(f"\n📄 Excel: {len(numeros_excel)} despesas fixas PAGAS")

# Ler despesas fixas da DB
session = SessionLocal()

despesas_db = session.query(Despesa).filter(
    Despesa.tipo == TipoDespesa.FIXA_MENSAL,
    Despesa.estado == EstadoDespesa.PAGO
).all()

print(f"💾 DB: {len(despesas_db)} despesas FIXA_MENSAL PAGAS\n")

numeros_db = set(d.numero for d in despesas_db)

# Encontrar diferenças
so_na_db = numeros_db - numeros_excel
so_no_excel = numeros_excel - numeros_db

if so_na_db:
    print("=" * 80)
    print(f"⚠️  {len(so_na_db)} DESPESAS na DB (FIXA_MENSAL PAGO) mas NÃO no Excel:")
    print("=" * 80)

    total_extras = 0
    for num in sorted(so_na_db):
        desp = next(d for d in despesas_db if d.numero == num)
        print(f"\n{num}:")
        print(f"   Descrição: {desp.descricao}")
        print(f"   Valor: €{float(desp.valor_com_iva):.2f}")
        print(f"   Data: {desp.data}")
        print(f"   Estado: {desp.estado.value}")
        total_extras += float(desp.valor_com_iva)

        # Verificar no Excel o que tem essa despesa
        excel_row = df[df.iloc[:, 0].astype(str) == num]
        if not excel_row.empty:
            row = excel_row.iloc[0]
            periodicidade = str(row.iloc[8]) if pd.notna(row.iloc[8]) else ''
            tipo_str = str(row.iloc[6]) if pd.notna(row.iloc[6]) else ''
            print(f"   Excel:")
            print(f"      Periodicidade: '{periodicidade}'")
            print(f"      Tipo: '{tipo_str}'")
        else:
            print(f"   Excel: NÃO ENCONTRADO")

    print(f"\nTotal dessas {len(so_na_db)} despesas: €{total_extras:.2f}")
    print(f"Diferença calculada: €{7939.66 - 7826.01:.2f}")

if so_no_excel:
    print("\n" + "=" * 80)
    print(f"⚠️  {len(so_no_excel)} DESPESAS no Excel mas NÃO na DB:")
    print("=" * 80)
    for num in sorted(so_no_excel):
        print(f"   {num}")

session.close()

print("\n" + "="*80)
