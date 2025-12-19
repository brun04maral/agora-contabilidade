#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para importar equipamentos do Excel
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

from database.models.equipamento import Equipamento

def importar_equipamentos(excel_path='excel/CONTABILIDADE_FINAL_20251108.xlsx'):
    """
    Importa equipamentos do Excel
    """
    print("=" * 80)
    print("🔧 IMPORTAÇÃO DE EQUIPAMENTOS")
    print("=" * 80)
    print(f"Excel: {excel_path}\n")

    # Setup database
    database_url = os.getenv("DATABASE_URL", "sqlite:///./agora_media.db")
    engine = create_engine(database_url)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Ler Excel
        print("📖 A ler aba EQUIPAMENTO...")
        xl = pd.ExcelFile(excel_path)
        df = pd.read_excel(xl, 'EQUIPAMENTO', header=1)  # Header na linha 1

        # Filtrar apenas equipamentos com dados
        df_clean = df[df['Nº EQUIPAMENTO'].notna() & df['Nº EQUIPAMENTO'].astype(str).str.startswith('#E')]
        df_equipamentos = df_clean[df_clean['PRODUTO'].notna()]

        print(f"   Total de equipamentos encontrados: {len(df_equipamentos)}")
        print()

        # Limpar equipamentos existentes
        print("🗑️  A limpar equipamentos existentes...")
        deleted = session.query(Equipamento).delete()
        session.commit()
        print(f"   Removidos: {deleted}")
        print()

        # Importar equipamentos
        print("📥 A importar equipamentos...")
        sucesso = 0
        erros = 0

        for idx, row in df_equipamentos.iterrows():
            try:
                # Parse data
                data_compra = None
                if pd.notna(row.get('DATA COMPRA')):
                    try:
                        data_compra = pd.to_datetime(row['DATA COMPRA']).date()
                    except:
                        pass

                # Parse valores
                valor_compra = 0
                if pd.notna(row.get('VALOR s/IVA')):
                    try:
                        valor_compra = float(row['VALOR s/IVA'])
                    except:
                        pass

                preco_aluguer = 0
                if pd.notna(row.get('PREÇO ALUGUER s/IVA')):
                    try:
                        preco_aluguer = float(row['PREÇO ALUGUER s/IVA'])
                    except:
                        pass

                quantidade = 1
                if pd.notna(row.get('QUANTIDADE')):
                    try:
                        quantidade = int(row['QUANTIDADE'])
                    except:
                        pass

                # Criar equipamento
                equipamento = Equipamento(
                    numero=str(row['Nº EQUIPAMENTO']).strip(),
                    produto=str(row['PRODUTO']).strip() if pd.notna(row.get('PRODUTO')) else None,
                    tipo=str(row['TIPO']).strip() if pd.notna(row.get('TIPO')) else None,
                    label=str(row['LABEL']).strip() if pd.notna(row.get('LABEL')) else None,
                    descricao=str(row['DESCRIÇÃO']).strip() if pd.notna(row.get('DESCRIÇÃO')) else None,
                    numero_serie=str(row['Nº SÉRIE']).strip() if pd.notna(row.get('Nº SÉRIE')) else None,
                    mac_address=str(row['MAC']).strip() if pd.notna(row.get('MAC')) else None,
                    quantidade=quantidade,
                    referencia=str(row['REFERÊNCIA']).strip() if pd.notna(row.get('REFERÊNCIA')) else None,
                    estado=str(row['ESTADO']).strip() if pd.notna(row.get('ESTADO')) else None,
                    data_compra=data_compra,
                    fornecedor=str(row['FORNECEDORES']).strip() if pd.notna(row.get('FORNECEDORES')) else None,
                    valor_compra=valor_compra,
                    preco_aluguer=preco_aluguer,
                    fatura_url=str(row['FATURA']).strip() if pd.notna(row.get('FATURA')) else None,
                    foto_url=str(row['FOTO']).strip() if pd.notna(row.get('FOTO')) else None,
                    tamanho=str(row['TAMANHO']).strip() if pd.notna(row.get('TAMANHO')) else None,
                    nota=str(row['NOTA']).strip() if pd.notna(row.get('NOTA')) else None,
                )

                session.add(equipamento)
                sucesso += 1

                # Mostrar progresso
                aluguer_info = f"€{preco_aluguer:,.2f}/dia" if preco_aluguer > 0 else "Sem preço"
                print(f"  ✅ {equipamento.numero}: {equipamento.produto} - {aluguer_info}")

            except Exception as e:
                erros += 1
                print(f"  ❌ Erro na linha {idx}: {e}")
                continue

        # Commit final
        session.commit()

        print()
        print("=" * 80)
        print("📊 RESUMO DA IMPORTAÇÃO")
        print("=" * 80)
        print(f"✅ Importados com sucesso: {sucesso}")
        print(f"❌ Erros: {erros}")
        print()

        # Estatísticas
        total_investido = session.query(Equipamento).count()
        valor_total = session.query(Equipamento).with_entities(
            func.sum(Equipamento.valor_compra)
        ).scalar() or 0

        print(f"💰 Total de equipamentos: {total_investido}")
        print(f"💵 Valor total investido: €{float(valor_total):,.2f}")
        print()

        # Listar equipamentos com preço de aluguer
        equipamentos_aluguer = session.query(Equipamento).filter(
            Equipamento.preco_aluguer > 0
        ).all()

        if equipamentos_aluguer:
            print("🏷️  EQUIPAMENTOS COM PREÇO DE ALUGUER:")
            for eq in equipamentos_aluguer:
                print(f"  • {eq.numero}: {eq.produto} - €{float(eq.preco_aluguer):,.2f}/dia")
            print()

        print("=" * 80)
        print("✅ IMPORTAÇÃO CONCLUÍDA!")
        print("=" * 80)

        session.close()
        return True

    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        session.rollback()
        session.close()
        return False


if __name__ == '__main__':
    from sqlalchemy import func
    importar_equipamentos()
