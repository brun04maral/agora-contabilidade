# -*- coding: utf-8 -*-
"""
Lógica de gestão de Boletins (CRUD) - Sistema de Boletim Itinerário
"""
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import date, datetime
from decimal import Decimal

from database.models import Boletim, Socio, EstadoBoletim
from logic.saldos import SaldosCalculator


class BoletinsManager:
    """
    Gestor de Boletins - CRUD operations
    """

    def __init__(self, db_session: Session):
        """
        Initialize manager

        Args:
            db_session: SQLAlchemy database session
        """
        self.db_session = db_session
        self.saldos_calculator = SaldosCalculator(db_session)

    def listar_todos(self) -> List[Boletim]:
        """
        Lista todos os boletins ordenados por data (mais recentes primeiro)

        Returns:
            Lista de objetos Boletim
        """
        return self.db_session.query(Boletim).order_by(desc(Boletim.data_emissao)).all()

    def listar_por_socio(self, socio: Socio) -> List[Boletim]:
        """
        Lista boletins por sócio

        Args:
            socio: Socio enum

        Returns:
            Lista de boletins do sócio
        """
        return self.db_session.query(Boletim).filter(
            Boletim.socio == socio
        ).order_by(desc(Boletim.data_emissao)).all()

    def listar_por_estado(self, estado: EstadoBoletim) -> List[Boletim]:
        """
        Lista boletins por estado

        Args:
            estado: EstadoBoletim enum

        Returns:
            Lista de boletins com o estado especificado
        """
        return self.db_session.query(Boletim).filter(
            Boletim.estado == estado
        ).order_by(desc(Boletim.data_emissao)).all()

    def obter_por_id(self, boletim_id: int) -> Optional[Boletim]:
        """
        Obtém um boletim por ID

        Args:
            boletim_id: ID do boletim

        Returns:
            Objeto Boletim ou None se não encontrado
        """
        return self.db_session.query(Boletim).filter(Boletim.id == boletim_id).first()

    def gerar_proximo_numero(self) -> str:
        """
        Gera próximo número de boletim

        Returns:
            Próximo número (ex: #B0001, #B0002, ...)
        """
        ultimo_boletim = self.db_session.query(Boletim).order_by(
            desc(Boletim.id)
        ).first()

        if ultimo_boletim:
            try:
                ultimo_num = int(ultimo_boletim.numero.replace('#B', ''))
                novo_num = ultimo_num + 1
            except:
                novo_num = 1
        else:
            novo_num = 1

        return f"#B{novo_num:04d}"

    def criar(
        self,
        socio: Socio,
        mes: int,
        ano: int,
        data_emissao: date,
        val_dia_nacional: Decimal,
        val_dia_estrangeiro: Decimal,
        val_km: Decimal,
        nota: Optional[str] = None
    ) -> Tuple[bool, Optional[Boletim], Optional[str]]:
        """
        Cria um novo boletim itinerário (modelo expandido)

        Args:
            socio: Sócio (BRUNO/RAFAEL)
            mes: Mês (1-12)
            ano: Ano (ex: 2025)
            data_emissao: Data de emissão
            val_dia_nacional, val_dia_estrangeiro, val_km: Valores de referência
            nota: Nota adicional (opcional)

        Returns:
            Tuple (sucesso, boletim, mensagem_erro)
        """
        try:
            # Validações
            if mes < 1 or mes > 12:
                return False, None, "Mês deve estar entre 1 e 12"

            if ano < 2020 or ano > 2100:
                return False, None, "Ano inválido"

            # Gerar número
            numero = self.gerar_proximo_numero()

            # Criar boletim com totais zerados (serão calculados pelas linhas)
            boletim = Boletim(
                numero=numero,
                socio=socio,
                mes=mes,
                ano=ano,
                data_emissao=data_emissao,
                val_dia_nacional=val_dia_nacional,
                val_dia_estrangeiro=val_dia_estrangeiro,
                val_km=val_km,
                total_ajudas_nacionais=Decimal('0'),
                total_ajudas_estrangeiro=Decimal('0'),
                total_kms=Decimal('0'),
                valor_total=Decimal('0'),
                valor=Decimal('0'),  # Compatibilidade
                estado=EstadoBoletim.PENDENTE,
                nota=nota,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )

            self.db_session.add(boletim)
            self.db_session.commit()
            self.db_session.refresh(boletim)

            return True, boletim, None

        except Exception as e:
            self.db_session.rollback()
            return False, None, f"Erro ao criar boletim: {str(e)}"

    def sugerir_valor(self, socio: Socio) -> Decimal:
        """
        Sugere valor de boletim baseado no saldo atual do sócio

        Args:
            socio: Socio enum

        Returns:
            Valor sugerido (saldo atual)
        """
        if socio == Socio.BRUNO:
            saldo_data = self.saldos_calculator.calcular_saldo_bruno()
        else:
            saldo_data = self.saldos_calculator.calcular_saldo_rafael()

        return Decimal(str(max(0, saldo_data['saldo_total'])))

    def emitir(
        self,
        socio: Socio,
        data_emissao: date,
        valor: Decimal,
        descricao: Optional[str] = None,
        nota: Optional[str] = None
    ) -> Tuple[bool, Optional[Boletim], Optional[str]]:
        """
        Emite um novo boletim (DEPRECATED - usar criar() para novos boletins)

        IMPORTANTE: Este método mantém compatibilidade com modelo antigo.
        Use criar() para boletins itinerário com múltiplas linhas.

        Args:
            socio: Sócio (BRUNO ou RAFAEL)
            data_emissao: Data de emissão
            valor: Valor do boletim
            descricao: Descrição (opcional)
            nota: Nota adicional (opcional)

        Returns:
            Tuple (sucesso, boletim, mensagem_erro)
        """
        try:
            # Gerar número do boletim
            numero = self.gerar_proximo_numero()

            # Criar boletim (modelo antigo - sem mes/ano/valores_ref)
            boletim = Boletim(
                numero=numero,
                socio=socio,
                data_emissao=data_emissao,
                valor=valor,
                valor_total=valor,  # Compatibilidade
                descricao=descricao,
                estado=EstadoBoletim.PENDENTE,
                nota=nota,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )

            self.db_session.add(boletim)
            self.db_session.commit()
            self.db_session.refresh(boletim)

            return True, boletim, None

        except Exception as e:
            self.db_session.rollback()
            return False, None, str(e)

    def atualizar(
        self,
        boletim_id: int,
        socio: Optional[Socio] = None,
        mes: Optional[int] = None,
        ano: Optional[int] = None,
        data_emissao: Optional[date] = None,
        val_dia_nacional: Optional[Decimal] = None,
        val_dia_estrangeiro: Optional[Decimal] = None,
        val_km: Optional[Decimal] = None,
        valor: Optional[Decimal] = None,  # Compatibilidade
        descricao: Optional[str] = None,  # Compatibilidade
        nota: Optional[str] = None
    ) -> Tuple[bool, Optional[str]]:
        """
        Atualiza um boletim existente

        Args:
            boletim_id: ID do boletim
            (outros): Campos a atualizar (opcionais)

        Returns:
            Tuple (sucesso, mensagem_erro)
        """
        try:
            boletim = self.obter_por_id(boletim_id)
            if not boletim:
                return False, "Boletim não encontrado"

            # Campos básicos
            if socio is not None:
                boletim.socio = socio
            if mes is not None:
                if mes < 1 or mes > 12:
                    return False, "Mês deve estar entre 1 e 12"
                boletim.mes = mes
            if ano is not None:
                if ano < 2020 or ano > 2100:
                    return False, "Ano inválido"
                boletim.ano = ano
            if data_emissao is not None:
                boletim.data_emissao = data_emissao

            # Valores de referência
            if val_dia_nacional is not None:
                boletim.val_dia_nacional = val_dia_nacional
            if val_dia_estrangeiro is not None:
                boletim.val_dia_estrangeiro = val_dia_estrangeiro
            if val_km is not None:
                boletim.val_km = val_km

            # Compatibilidade com modelo antigo
            if valor is not None:
                boletim.valor = valor
                boletim.valor_total = valor
            if descricao is not None:
                boletim.descricao = descricao

            if nota is not None:
                boletim.nota = nota

            boletim.updated_at = datetime.utcnow()

            self.db_session.commit()
            return True, None

        except Exception as e:
            self.db_session.rollback()
            return False, str(e)

    def marcar_como_pago(
        self,
        boletim_id: int,
        data_pagamento: Optional[date] = None
    ) -> Tuple[bool, Optional[str]]:
        """
        Marca um boletim como pago

        Args:
            boletim_id: ID do boletim
            data_pagamento: Data de pagamento (usa hoje se não fornecida)

        Returns:
            Tuple (sucesso, mensagem_erro)
        """
        try:
            boletim = self.obter_por_id(boletim_id)
            if not boletim:
                return False, "Boletim não encontrado"

            if boletim.estado == EstadoBoletim.PAGO:
                return False, "Boletim já está marcado como pago"

            boletim.estado = EstadoBoletim.PAGO
            boletim.data_pagamento = data_pagamento or date.today()

            self.db_session.commit()
            return True, None

        except Exception as e:
            self.db_session.rollback()
            return False, str(e)

    def marcar_como_pendente(self, boletim_id: int) -> Tuple[bool, Optional[str]]:
        """
        Marca um boletim como pendente (desfaz pagamento)

        Args:
            boletim_id: ID do boletim

        Returns:
            Tuple (sucesso, mensagem_erro)
        """
        try:
            boletim = self.obter_por_id(boletim_id)
            if not boletim:
                return False, "Boletim não encontrado"

            boletim.estado = EstadoBoletim.PENDENTE
            boletim.data_pagamento = None

            self.db_session.commit()
            return True, None

        except Exception as e:
            self.db_session.rollback()
            return False, str(e)

    def apagar(self, boletim_id: int) -> Tuple[bool, Optional[str]]:
        """
        Apaga um boletim

        Args:
            boletim_id: ID do boletim

        Returns:
            Tuple (sucesso, mensagem_erro)
        """
        try:
            boletim = self.obter_por_id(boletim_id)
            if not boletim:
                return False, "Boletim não encontrado"

            self.db_session.delete(boletim)
            self.db_session.commit()
            return True, None

        except Exception as e:
            self.db_session.rollback()
            return False, str(e)
