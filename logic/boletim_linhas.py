# -*- coding: utf-8 -*-
"""
Lógica de gestão de Linhas de Boletim (CRUD + Cálculos)
"""
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from datetime import datetime, date, time
from decimal import Decimal

from database.models.boletim_linha import BoletimLinha, TipoDeslocacao
from database.models.boletim import Boletim


class BoletimLinhasManager:
    """
    Gestor de Linhas de Boletim - CRUD operations + cálculos automáticos
    """

    def __init__(self, db_session: Session):
        """
        Initialize manager

        Args:
            db_session: SQLAlchemy database session
        """
        self.db_session = db_session

    def listar_por_boletim(self, boletim_id: int) -> List[BoletimLinha]:
        """
        Lista todas as linhas de um boletim ordenadas por ordem

        Args:
            boletim_id: ID do boletim

        Returns:
            Lista de objetos BoletimLinha
        """
        return self.db_session.query(BoletimLinha).filter(
            BoletimLinha.boletim_id == boletim_id
        ).order_by(BoletimLinha.ordem).all()

    def obter_por_id(self, linha_id: int) -> Optional[BoletimLinha]:
        """
        Obtém uma linha por ID

        Args:
            linha_id: ID da linha

        Returns:
            Objeto BoletimLinha ou None se não encontrado
        """
        return self.db_session.query(BoletimLinha).filter(
            BoletimLinha.id == linha_id
        ).first()

    def criar(
        self,
        boletim_id: int,
        servico: str,
        tipo: TipoDeslocacao = TipoDeslocacao.NACIONAL,
        dias: Decimal = Decimal('0'),
        kms: int = 0,
        projeto_id: Optional[int] = None,
        localidade: Optional[str] = None,
        data_inicio: Optional[date] = None,
        hora_inicio: Optional[time] = None,
        data_fim: Optional[date] = None,
        hora_fim: Optional[time] = None
    ) -> Tuple[bool, Optional[BoletimLinha], Optional[str]]:
        """
        Cria uma nova linha de boletim

        Args:
            boletim_id: ID do boletim
            servico: Descrição do serviço/deslocação
            tipo: Tipo de deslocação (NACIONAL/ESTRANGEIRO)
            dias: Número de dias (decimal, manual)
            kms: Quilómetros percorridos
            projeto_id: ID do projeto (opcional)
            localidade: Local da deslocação
            data_inicio, hora_inicio, data_fim, hora_fim: Datas/horas (informativas)

        Returns:
            Tupla (sucesso, objeto, mensagem_erro)
        """
        try:
            # Validações
            if not servico or not servico.strip():
                return False, None, "Serviço é obrigatório"

            if dias < 0:
                return False, None, "Dias não pode ser negativo"

            if kms < 0:
                return False, None, "Kms não pode ser negativo"

            # Calcular próxima ordem
            ultima_linha = self.db_session.query(BoletimLinha).filter(
                BoletimLinha.boletim_id == boletim_id
            ).order_by(BoletimLinha.ordem.desc()).first()

            ordem = (ultima_linha.ordem + 1) if ultima_linha else 1

            # Criar
            nova_linha = BoletimLinha(
                boletim_id=boletim_id,
                ordem=ordem,
                projeto_id=projeto_id,
                servico=servico.strip(),
                localidade=localidade.strip() if localidade else None,
                data_inicio=data_inicio,
                hora_inicio=hora_inicio,
                data_fim=data_fim,
                hora_fim=hora_fim,
                tipo=tipo,
                dias=dias,
                kms=kms,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )

            self.db_session.add(nova_linha)
            self.db_session.commit()
            self.db_session.refresh(nova_linha)

            # Recalcular totais do boletim
            self.recalcular_totais_boletim(boletim_id)

            return True, nova_linha, None

        except Exception as e:
            self.db_session.rollback()
            return False, None, f"Erro ao criar linha: {str(e)}"

    def atualizar(
        self,
        linha_id: int,
        servico: str,
        tipo: TipoDeslocacao,
        dias: Decimal,
        kms: int,
        projeto_id: Optional[int] = None,
        localidade: Optional[str] = None,
        data_inicio: Optional[date] = None,
        hora_inicio: Optional[time] = None,
        data_fim: Optional[date] = None,
        hora_fim: Optional[time] = None
    ) -> Tuple[bool, Optional[BoletimLinha], Optional[str]]:
        """
        Atualiza uma linha de boletim

        Args:
            linha_id: ID da linha
            (outros args iguais ao criar)

        Returns:
            Tupla (sucesso, objeto, mensagem_erro)
        """
        try:
            linha = self.obter_por_id(linha_id)
            if not linha:
                return False, None, "Linha não encontrada"

            # Validações
            if not servico or not servico.strip():
                return False, None, "Serviço é obrigatório"

            if dias < 0:
                return False, None, "Dias não pode ser negativo"

            if kms < 0:
                return False, None, "Kms não pode ser negativo"

            # Atualizar
            linha.projeto_id = projeto_id
            linha.servico = servico.strip()
            linha.localidade = localidade.strip() if localidade else None
            linha.data_inicio = data_inicio
            linha.hora_inicio = hora_inicio
            linha.data_fim = data_fim
            linha.hora_fim = hora_fim
            linha.tipo = tipo
            linha.dias = dias
            linha.kms = kms
            linha.updated_at = datetime.utcnow()

            self.db_session.commit()
            self.db_session.refresh(linha)

            # Recalcular totais do boletim
            self.recalcular_totais_boletim(linha.boletim_id)

            return True, linha, None

        except Exception as e:
            self.db_session.rollback()
            return False, None, f"Erro ao atualizar linha: {str(e)}"

    def eliminar(self, linha_id: int) -> Tuple[bool, Optional[str]]:
        """
        Elimina uma linha de boletim

        Args:
            linha_id: ID da linha

        Returns:
            Tupla (sucesso, mensagem_erro)
        """
        try:
            linha = self.obter_por_id(linha_id)
            if not linha:
                return False, "Linha não encontrada"

            boletim_id = linha.boletim_id

            self.db_session.delete(linha)
            self.db_session.commit()

            # Recalcular totais do boletim
            self.recalcular_totais_boletim(boletim_id)

            return True, None

        except Exception as e:
            self.db_session.rollback()
            return False, f"Erro ao eliminar linha: {str(e)}"

    def reordenar(self, boletim_id: int, linhas_ordem: List[Tuple[int, int]]) -> Tuple[bool, Optional[str]]:
        """
        Reordena linhas de um boletim

        Args:
            boletim_id: ID do boletim
            linhas_ordem: Lista de tuplas (linha_id, nova_ordem)

        Returns:
            Tupla (sucesso, mensagem_erro)
        """
        try:
            for linha_id, nova_ordem in linhas_ordem:
                linha = self.obter_por_id(linha_id)
                if linha and linha.boletim_id == boletim_id:
                    linha.ordem = nova_ordem
                    linha.updated_at = datetime.utcnow()

            self.db_session.commit()
            return True, None

        except Exception as e:
            self.db_session.rollback()
            return False, f"Erro ao reordenar linhas: {str(e)}"

    def recalcular_totais_boletim(self, boletim_id: int) -> bool:
        """
        Recalcula os totais de um boletim baseado nas suas linhas

        Args:
            boletim_id: ID do boletim

        Returns:
            True se sucesso, False se erro
        """
        try:
            boletim = self.db_session.query(Boletim).filter(
                Boletim.id == boletim_id
            ).first()

            if not boletim:
                return False

            # Se não tem valores de referência, não pode calcular
            if not boletim.val_dia_nacional or not boletim.val_dia_estrangeiro or not boletim.val_km:
                return False

            # Obter todas as linhas
            linhas = self.listar_por_boletim(boletim_id)

            # Calcular totais
            total_dias_nacionais = sum(
                linha.dias for linha in linhas if linha.tipo == TipoDeslocacao.NACIONAL
            )
            total_dias_estrangeiro = sum(
                linha.dias for linha in linhas if linha.tipo == TipoDeslocacao.ESTRANGEIRO
            )
            total_kms_percorridos = sum(linha.kms for linha in linhas)

            # Aplicar valores de referência
            boletim.total_ajudas_nacionais = total_dias_nacionais * boletim.val_dia_nacional
            boletim.total_ajudas_estrangeiro = total_dias_estrangeiro * boletim.val_dia_estrangeiro
            boletim.total_kms = Decimal(str(total_kms_percorridos)) * boletim.val_km

            # Calcular valor total
            boletim.valor_total = (
                boletim.total_ajudas_nacionais +
                boletim.total_ajudas_estrangeiro +
                boletim.total_kms
            )

            # Atualizar também campo 'valor' antigo (compatibilidade)
            boletim.valor = boletim.valor_total

            boletim.updated_at = datetime.utcnow()

            self.db_session.commit()
            return True

        except Exception as e:
            self.db_session.rollback()
            print(f"Erro ao recalcular totais: {e}")
            return False
