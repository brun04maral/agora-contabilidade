# -*- coding: utf-8 -*-
"""
Lógica de gestão de Valores de Referência Anuais (CRUD)
"""
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import desc
from decimal import Decimal
from datetime import datetime

from database.models.valor_referencia_anual import ValorReferenciaAnual


# Valores default (fallback se ano não existir na BD)
DEFAULT_VAL_DIA_NACIONAL = Decimal('72.65')
DEFAULT_VAL_DIA_ESTRANGEIRO = Decimal('167.07')
DEFAULT_VAL_KM = Decimal('0.40')


class ValoresReferenciaManager:
    """
    Gestor de Valores de Referência Anuais - CRUD operations
    """

    def __init__(self, db_session: Session):
        """
        Initialize manager

        Args:
            db_session: SQLAlchemy database session
        """
        self.db_session = db_session

    def listar_todos(self) -> List[ValorReferenciaAnual]:
        """
        Lista todos os valores de referência ordenados por ano DESC

        Returns:
            Lista de objetos ValorReferenciaAnual
        """
        return self.db_session.query(ValorReferenciaAnual).order_by(
            desc(ValorReferenciaAnual.ano)
        ).all()

    def obter_por_ano(self, ano: int) -> Optional[ValorReferenciaAnual]:
        """
        Obtém valores de referência de um ano específico

        Args:
            ano: Ano (ex: 2025)

        Returns:
            Objeto ValorReferenciaAnual ou None se não encontrado
        """
        return self.db_session.query(ValorReferenciaAnual).filter(
            ValorReferenciaAnual.ano == ano
        ).first()

    def obter_ou_default(self, ano: int) -> Tuple[Decimal, Decimal, Decimal]:
        """
        Obtém valores de referência de um ano ou retorna defaults

        Args:
            ano: Ano (ex: 2025)

        Returns:
            Tupla (val_dia_nacional, val_dia_estrangeiro, val_km)
        """
        valores = self.obter_por_ano(ano)
        if valores:
            return (
                valores.val_dia_nacional,
                valores.val_dia_estrangeiro,
                valores.val_km
            )
        return (
            DEFAULT_VAL_DIA_NACIONAL,
            DEFAULT_VAL_DIA_ESTRANGEIRO,
            DEFAULT_VAL_KM
        )

    def criar(
        self,
        ano: int,
        val_dia_nacional: Decimal,
        val_dia_estrangeiro: Decimal,
        val_km: Decimal
    ) -> Tuple[bool, Optional[ValorReferenciaAnual], Optional[str]]:
        """
        Cria valores de referência para um ano

        Args:
            ano: Ano (ex: 2025)
            val_dia_nacional: Valor diário nacional
            val_dia_estrangeiro: Valor diário estrangeiro
            val_km: Valor por quilómetro

        Returns:
            Tupla (sucesso, objeto, mensagem_erro)
        """
        try:
            # Verificar se já existe
            existente = self.obter_por_ano(ano)
            if existente:
                return False, None, f"Já existem valores para o ano {ano}"

            # Validações
            if ano < 2020 or ano > 2100:
                return False, None, "Ano inválido (deve estar entre 2020 e 2100)"

            if val_dia_nacional <= 0:
                return False, None, "Valor dia nacional deve ser maior que 0"

            if val_dia_estrangeiro <= 0:
                return False, None, "Valor dia estrangeiro deve ser maior que 0"

            if val_km <= 0:
                return False, None, "Valor por km deve ser maior que 0"

            # Criar
            novo = ValorReferenciaAnual(
                ano=ano,
                val_dia_nacional=val_dia_nacional,
                val_dia_estrangeiro=val_dia_estrangeiro,
                val_km=val_km,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )

            self.db_session.add(novo)
            self.db_session.commit()
            self.db_session.refresh(novo)

            return True, novo, None

        except Exception as e:
            self.db_session.rollback()
            return False, None, f"Erro ao criar valores: {str(e)}"

    def atualizar(
        self,
        ano: int,
        val_dia_nacional: Decimal,
        val_dia_estrangeiro: Decimal,
        val_km: Decimal
    ) -> Tuple[bool, Optional[ValorReferenciaAnual], Optional[str]]:
        """
        Atualiza valores de referência de um ano

        Args:
            ano: Ano (ex: 2025)
            val_dia_nacional: Valor diário nacional
            val_dia_estrangeiro: Valor diário estrangeiro
            val_km: Valor por quilómetro

        Returns:
            Tupla (sucesso, objeto, mensagem_erro)
        """
        try:
            valores = self.obter_por_ano(ano)
            if not valores:
                return False, None, f"Valores para o ano {ano} não encontrados"

            # Validações
            if val_dia_nacional <= 0:
                return False, None, "Valor dia nacional deve ser maior que 0"

            if val_dia_estrangeiro <= 0:
                return False, None, "Valor dia estrangeiro deve ser maior que 0"

            if val_km <= 0:
                return False, None, "Valor por km deve ser maior que 0"

            # Atualizar
            valores.val_dia_nacional = val_dia_nacional
            valores.val_dia_estrangeiro = val_dia_estrangeiro
            valores.val_km = val_km
            valores.updated_at = datetime.utcnow()

            self.db_session.commit()
            self.db_session.refresh(valores)

            return True, valores, None

        except Exception as e:
            self.db_session.rollback()
            return False, None, f"Erro ao atualizar valores: {str(e)}"

    def eliminar(self, ano: int) -> Tuple[bool, Optional[str]]:
        """
        Elimina valores de referência de um ano

        Args:
            ano: Ano (ex: 2025)

        Returns:
            Tupla (sucesso, mensagem_erro)
        """
        try:
            valores = self.obter_por_ano(ano)
            if not valores:
                return False, f"Valores para o ano {ano} não encontrados"

            self.db_session.delete(valores)
            self.db_session.commit()

            return True, None

        except Exception as e:
            self.db_session.rollback()
            return False, f"Erro ao eliminar valores: {str(e)}"
