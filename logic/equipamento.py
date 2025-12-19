# -*- coding: utf-8 -*-
"""
Lógica de negócio para Equipamento
"""
from sqlalchemy.orm import Session
from database.models.equipamento import Equipamento
from typing import List, Optional, Tuple
from datetime import date
from decimal import Decimal


class EquipamentoManager:
    """Gerencia operações de equipamento"""

    def __init__(self, db_session: Session):
        self.db = db_session

    def listar_equipamentos(
        self,
        filtro_tipo: Optional[str] = None,
        filtro_com_aluguer: bool = False,
        pesquisa: Optional[str] = None
    ) -> List[Equipamento]:
        """
        Lista equipamentos com filtros opcionais

        Args:
            filtro_tipo: Filtrar por tipo (Vídeo, Áudio, etc)
            filtro_com_aluguer: Mostrar apenas equipamentos com preço de aluguer
            pesquisa: Termo de pesquisa (produto, número)

        Returns:
            Lista de equipamentos
        """
        query = self.db.query(Equipamento)

        # Filtros
        if filtro_tipo and filtro_tipo != "Todos":
            query = query.filter(Equipamento.tipo == filtro_tipo)

        if filtro_com_aluguer:
            query = query.filter(Equipamento.preco_aluguer > 0)

        if pesquisa:
            termo = f"%{pesquisa}%"
            query = query.filter(
                (Equipamento.produto.ilike(termo)) |
                (Equipamento.numero.ilike(termo)) |
                (Equipamento.descricao.ilike(termo))
            )

        return query.order_by(Equipamento.numero).all()

    def obter_equipamento(self, equipamento_id: int) -> Optional[Equipamento]:
        """Obtém equipamento por ID"""
        return self.db.query(Equipamento).filter(Equipamento.id == equipamento_id).first()

    def obter_por_numero(self, numero: str) -> Optional[Equipamento]:
        """Obtém equipamento por número (ex: #E0001)"""
        return self.db.query(Equipamento).filter(Equipamento.numero == numero).first()

    def criar_equipamento(
        self,
        numero: str,
        produto: str,
        tipo: Optional[str] = None,
        label: Optional[str] = None,
        descricao: Optional[str] = None,
        valor_compra: Decimal = Decimal('0'),
        preco_aluguer: Decimal = Decimal('0'),
        **kwargs
    ) -> Tuple[bool, Optional[Equipamento], Optional[str]]:
        """
        Cria novo equipamento

        Returns:
            (sucesso, equipamento, mensagem_erro)
        """
        try:
            # Verificar se número já existe
            existe = self.obter_por_numero(numero)
            if existe:
                return False, None, f"Equipamento {numero} já existe"

            # Criar equipamento
            equipamento = Equipamento(
                numero=numero,
                produto=produto,
                tipo=tipo,
                label=label,
                descricao=descricao,
                valor_compra=valor_compra,
                preco_aluguer=preco_aluguer,
                **kwargs
            )

            self.db.add(equipamento)
            self.db.commit()
            self.db.refresh(equipamento)

            return True, equipamento, None

        except Exception as e:
            self.db.rollback()
            return False, None, str(e)

    def atualizar_equipamento(
        self,
        equipamento_id: int,
        **kwargs
    ) -> Tuple[bool, Optional[Equipamento], Optional[str]]:
        """
        Atualiza equipamento existente

        Returns:
            (sucesso, equipamento, mensagem_erro)
        """
        try:
            equipamento = self.obter_equipamento(equipamento_id)
            if not equipamento:
                return False, None, "Equipamento não encontrado"

            # Atualizar campos
            for key, value in kwargs.items():
                if hasattr(equipamento, key):
                    setattr(equipamento, key, value)

            self.db.commit()
            self.db.refresh(equipamento)

            return True, equipamento, None

        except Exception as e:
            self.db.rollback()
            return False, None, str(e)

    def eliminar_equipamento(self, equipamento_id: int) -> Tuple[bool, Optional[str]]:
        """
        Elimina equipamento

        Returns:
            (sucesso, mensagem_erro)
        """
        try:
            equipamento = self.obter_equipamento(equipamento_id)
            if not equipamento:
                return False, "Equipamento não encontrado"

            # TODO: Verificar se está a ser usado em orçamentos

            self.db.delete(equipamento)
            self.db.commit()

            return True, None

        except Exception as e:
            self.db.rollback()
            return False, str(e)

    def proximo_numero(self) -> str:
        """
        Gera próximo número de equipamento

        Returns:
            Próximo número disponível (ex: #E0028)
        """
        # Obter último número
        ultimo = self.db.query(Equipamento).order_by(Equipamento.numero.desc()).first()

        if not ultimo:
            return "#E0001"

        # Extrair número e incrementar
        try:
            numero_atual = int(ultimo.numero.replace("#E", ""))
            proximo = numero_atual + 1
            return f"#E{proximo:04d}"
        except:
            return "#E0001"

    def obter_tipos(self) -> List[str]:
        """Obtém lista de tipos de equipamento únicos"""
        tipos = self.db.query(Equipamento.tipo).distinct().filter(Equipamento.tipo.isnot(None)).all()
        return ["Todos"] + [t[0] for t in tipos if t[0]]

    def calcular_amortizacao(self, equipamento_id: int) -> dict:
        """
        Calcula amortização de um equipamento

        Amortização = valor_compra - total_já_alugado

        Args:
            equipamento_id: ID do equipamento

        Returns:
            Dicionário com:
            - valor_compra: Valor de compra original
            - total_alugado: Total já recuperado em alugueres
            - amortizacao_restante: Quanto falta amortizar
            - percentagem_amortizada: % já amortizada
            - roi: Return on Investment (pode ser > 100% se já recuperou tudo)
        """
        from sqlalchemy import func
        from database.models.equipamento import EquipamentoAluguer

        equipamento = self.obter_equipamento(equipamento_id)
        if not equipamento:
            return None

        valor_compra = equipamento.valor_compra or Decimal('0')

        # Calcular total já alugado
        total_alugado = self.db.query(func.sum(EquipamentoAluguer.valor_alugado))\
            .filter(EquipamentoAluguer.equipamento_id == equipamento_id)\
            .scalar() or Decimal('0')

        # Calcular amortização restante
        amortizacao_restante = valor_compra - total_alugado

        # Calcular percentagens
        if valor_compra > 0:
            percentagem_amortizada = (total_alugado / valor_compra) * 100
            roi = (total_alugado / valor_compra) * 100
        else:
            percentagem_amortizada = Decimal('0')
            roi = Decimal('0')

        return {
            'valor_compra': float(valor_compra),
            'total_alugado': float(total_alugado),
            'amortizacao_restante': float(amortizacao_restante),
            'percentagem_amortizada': float(percentagem_amortizada),
            'roi': float(roi)
        }

    def obter_historico_alugueres(self, equipamento_id: int) -> List:
        """
        Obtém histórico de alugueres de um equipamento

        Args:
            equipamento_id: ID do equipamento

        Returns:
            Lista de alugueres ordenados por data (mais recente primeiro)
        """
        from database.models.equipamento import EquipamentoAluguer

        return self.db.query(EquipamentoAluguer)\
            .filter(EquipamentoAluguer.equipamento_id == equipamento_id)\
            .order_by(EquipamentoAluguer.data_aluguer.desc())\
            .all()

    def estatisticas(self) -> dict:
        """
        Retorna estatísticas de equipamento

        Returns:
            Dicionário com estatísticas
        """
        total = self.db.query(Equipamento).count()

        # Valor total investido
        from sqlalchemy import func
        valor_total = self.db.query(func.sum(Equipamento.valor_compra)).scalar() or 0

        # Equipamentos com preço de aluguer
        com_aluguer = self.db.query(Equipamento).filter(Equipamento.preco_aluguer > 0).count()

        # Por tipo
        por_tipo = {}
        tipos = self.db.query(
            Equipamento.tipo,
            func.count(Equipamento.id)
        ).filter(Equipamento.tipo.isnot(None)).group_by(Equipamento.tipo).all()

        for tipo, count in tipos:
            por_tipo[tipo] = count

        return {
            'total': total,
            'valor_total_investido': float(valor_total),
            'com_preco_aluguer': com_aluguer,
            'por_tipo': por_tipo
        }
