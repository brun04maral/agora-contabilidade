# -*- coding: utf-8 -*-
"""
Lógica de negócio para Orçamentos
"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from database.models.orcamento import Orcamento, OrcamentoSecao, OrcamentoItem, OrcamentoReparticao
from database.models.cliente import Cliente
from database.models.freelancer_trabalho import StatusTrabalho
from database.models.projeto import TipoProjeto, EstadoProjeto
from typing import List, Optional, Tuple, Dict
from datetime import date, datetime
from decimal import Decimal


class OrcamentoManager:
    """Gerencia operações de orçamentos"""

    def __init__(self, db_session: Session):
        self.db = db_session

    def listar_orcamentos(
        self,
        filtro_status: Optional[str] = None,
        filtro_cliente_id: Optional[int] = None,
        filtro_com_versao_cliente: Optional[bool] = None,
        pesquisa: Optional[str] = None
    ) -> List[Orcamento]:
        """
        Lista orçamentos com filtros opcionais

        Args:
            filtro_status: Filtrar por status (rascunho, enviado, aprovado, rejeitado)
            filtro_cliente_id: Filtrar por cliente
            filtro_com_versao_cliente: Filtrar orçamentos com versão cliente (True/False/None)
            pesquisa: Termo de pesquisa (código, descrição)

        Returns:
            Lista de orçamentos
        """
        query = self.db.query(Orcamento)

        # Filtros
        if filtro_com_versao_cliente is not None:
            query = query.filter(Orcamento.tem_versao_cliente == filtro_com_versao_cliente)

        if filtro_status and filtro_status != "Todos":
            query = query.filter(Orcamento.status == filtro_status)

        if filtro_cliente_id:
            query = query.filter(Orcamento.cliente_id == filtro_cliente_id)

        if pesquisa:
            termo = f"%{pesquisa}%"
            query = query.filter(
                (Orcamento.codigo.ilike(termo)) |
                (Orcamento.descricao_proposta.ilike(termo))
            )

        return query.order_by(Orcamento.data_criacao.desc()).all()

    def obter_orcamento(self, orcamento_id: int) -> Optional[Orcamento]:
        """Obtém orçamento por ID com todas as relações"""
        return self.db.query(Orcamento).filter(Orcamento.id == orcamento_id).first()

    def obter_por_codigo(self, codigo: str) -> Optional[Orcamento]:
        """
        Obtém orçamento por código

        Args:
            codigo: Código do orçamento (ex: "20250909_Orçamento-SGS_Conf")

        Returns:
            Orçamento encontrado ou None
        """
        return self.db.query(Orcamento).filter(Orcamento.codigo == codigo).first()

    def _criar_secoes_padrao(self, orcamento_id: int):
        """
        Cria secções padrão para um orçamento

        Estrutura:
        - Serviços
        - Equipamento
          - Vídeo
          - Som
          - Iluminação
        - Despesas

        Args:
            orcamento_id: ID do orçamento
        """
        # 1. Serviços (ordem 1)
        sucesso, secao_servicos, erro = self.adicionar_secao(
            orcamento_id=orcamento_id,
            tipo='servicos',
            nome='Serviços',
            ordem=1
        )

        # 2. Equipamento (ordem 2)
        sucesso, secao_equipamento, erro = self.adicionar_secao(
            orcamento_id=orcamento_id,
            tipo='equipamento',
            nome='Equipamento',
            ordem=2
        )

        if secao_equipamento:
            # 2.1 Vídeo (subsecção)
            self.adicionar_secao(
                orcamento_id=orcamento_id,
                tipo='video',
                nome='Vídeo',
                ordem=1,
                parent_id=secao_equipamento.id
            )

            # 2.2 Som (subsecção)
            self.adicionar_secao(
                orcamento_id=orcamento_id,
                tipo='som',
                nome='Som',
                ordem=2,
                parent_id=secao_equipamento.id
            )

            # 2.3 Iluminação (subsecção)
            self.adicionar_secao(
                orcamento_id=orcamento_id,
                tipo='iluminacao',
                nome='Iluminação',
                ordem=3,
                parent_id=secao_equipamento.id
            )

        # 3. Despesas (ordem 3)
        self.adicionar_secao(
            orcamento_id=orcamento_id,
            tipo='despesas',
            nome='Despesas',
            ordem=3
        )

    def gerar_proximo_codigo(self) -> str:
        """
        Gera o próximo código de orçamento automaticamente
        Formato: OR-00001, OR-00002, OR-00003...

        Returns:
            Próximo código disponível
        """
        # Obter último orçamento por código (ordenado alfabeticamente)
        ultimo_orcamento = self.db.query(Orcamento)\
            .filter(Orcamento.codigo.like('OR-%'))\
            .order_by(Orcamento.codigo.desc())\
            .first()

        if not ultimo_orcamento:
            # Primeiro orçamento
            return "OR-00001"

        # Extrair número do último código
        try:
            ultimo_codigo = ultimo_orcamento.codigo
            # Formato esperado: OR-00001
            if ultimo_codigo.startswith('OR-'):
                numero_str = ultimo_codigo.split('-')[1]
                numero = int(numero_str)
                proximo_numero = numero + 1
                # Formatar com 5 dígitos zero-padded
                return f"OR-{proximo_numero:05d}"
            else:
                # Formato antigo, começar do 1
                return "OR-00001"
        except (ValueError, IndexError):
            # Erro ao parsear, começar do 1
            return "OR-00001"

    def criar_orcamento(
        self,
        codigo: str,
        data_criacao: date,
        cliente_id: Optional[int] = None,
        **kwargs
    ) -> Tuple[bool, Optional[Orcamento], Optional[str]]:
        """
        Cria novo orçamento

        Args:
            codigo: Código único do orçamento (ex: "20250909_Orçamento-SGS_Conf")
            data_criacao: Data da criação do orçamento
            cliente_id: ID do cliente (opcional)
            **kwargs: Outros campos opcionais (tem_versao_cliente, titulo_cliente, etc.)

        Returns:
            (sucesso, orcamento, mensagem_erro)
        """
        try:
            # Verificar se código já existe
            existe = self.obter_por_codigo(codigo)
            if existe:
                return False, None, f"Orçamento {codigo} já existe"

            # Criar orçamento
            orcamento = Orcamento(
                codigo=codigo,
                data_criacao=data_criacao,
                cliente_id=cliente_id,
                **kwargs
            )

            self.db.add(orcamento)
            self.db.commit()
            self.db.refresh(orcamento)

            # Criar secções automáticas
            self._criar_secoes_padrao(orcamento.id)

            return True, orcamento, None

        except Exception as e:
            self.db.rollback()
            return False, None, str(e)

    def atualizar_orcamento(
        self,
        orcamento_id: int,
        **kwargs
    ) -> Tuple[bool, Optional[Orcamento], Optional[str]]:
        """
        Atualiza orçamento existente

        Returns:
            (sucesso, orcamento, mensagem_erro)
        """
        try:
            orcamento = self.obter_orcamento(orcamento_id)
            if not orcamento:
                return False, None, "Orçamento não encontrado"

            # Atualizar campos
            for key, value in kwargs.items():
                if hasattr(orcamento, key):
                    setattr(orcamento, key, value)

            orcamento.updated_at = datetime.now()

            self.db.commit()
            self.db.refresh(orcamento)

            return True, orcamento, None

        except Exception as e:
            self.db.rollback()
            return False, None, str(e)

    def eliminar_orcamento(self, orcamento_id: int) -> Tuple[bool, Optional[str]]:
        """
        Elimina orçamento (e todas as secções, items e repartições relacionadas)

        Returns:
            (sucesso, mensagem_erro)
        """
        try:
            orcamento = self.obter_orcamento(orcamento_id)
            if not orcamento:
                return False, "Orçamento não encontrado"

            # Cascade delete irá eliminar secções, items e repartições automaticamente
            self.db.delete(orcamento)
            self.db.commit()

            return True, None

        except Exception as e:
            self.db.rollback()
            return False, str(e)

    # ==================== Secções ====================

    def adicionar_secao(
        self,
        orcamento_id: int,
        tipo: str,
        nome: str,
        ordem: int = 0,
        parent_id: Optional[int] = None
    ) -> Tuple[bool, Optional[OrcamentoSecao], Optional[str]]:
        """
        Adiciona nova secção ao orçamento

        Args:
            orcamento_id: ID do orçamento
            tipo: Tipo da secção (servicos, equipamento, video, som, iluminacao, despesas)
            nome: Nome de exibição
            ordem: Ordem de apresentação
            parent_id: ID da secção pai (para subsecções)

        Returns:
            (sucesso, secao, mensagem_erro)
        """
        try:
            secao = OrcamentoSecao(
                orcamento_id=orcamento_id,
                tipo=tipo,
                nome=nome,
                ordem=ordem,
                parent_id=parent_id
            )

            self.db.add(secao)
            self.db.commit()
            self.db.refresh(secao)

            return True, secao, None

        except Exception as e:
            self.db.rollback()
            return False, None, str(e)

    def obter_secoes(self, orcamento_id: int) -> List[OrcamentoSecao]:
        """Obtém todas as secções de um orçamento ordenadas"""
        return self.db.query(OrcamentoSecao)\
            .filter(OrcamentoSecao.orcamento_id == orcamento_id)\
            .order_by(OrcamentoSecao.ordem)\
            .all()

    def atualizar_secao(
        self,
        secao_id: int,
        **kwargs
    ) -> Tuple[bool, Optional[OrcamentoSecao], Optional[str]]:
        """
        Atualiza secção existente

        Returns:
            (sucesso, secao, mensagem_erro)
        """
        try:
            secao = self.db.query(OrcamentoSecao).filter(OrcamentoSecao.id == secao_id).first()
            if not secao:
                return False, None, "Secção não encontrada"

            # Atualizar campos
            for key, value in kwargs.items():
                if hasattr(secao, key):
                    setattr(secao, key, value)

            self.db.commit()
            self.db.refresh(secao)

            return True, secao, None

        except Exception as e:
            self.db.rollback()
            return False, None, str(e)

    def eliminar_secao(self, secao_id: int) -> Tuple[bool, Optional[str]]:
        """
        Elimina secção do orçamento (cascade elimina items e subsecções)

        Returns:
            (sucesso, mensagem_erro)
        """
        try:
            secao = self.db.query(OrcamentoSecao).filter(OrcamentoSecao.id == secao_id).first()
            if not secao:
                return False, "Secção não encontrada"

            orcamento_id = secao.orcamento_id
            self.db.delete(secao)
            self.db.commit()

            # Recalcular totais do orçamento
            self.recalcular_totais(orcamento_id)

            return True, None

        except Exception as e:
            self.db.rollback()
            return False, str(e)

    # ==================== Items ====================

    def adicionar_item(
        self,
        orcamento_id: int,
        secao_id: int,
        descricao: str,
        quantidade: int,
        dias: int,
        preco_unitario: Decimal,
        desconto: Decimal = Decimal('0'),
        ordem: int = 0,
        **kwargs
    ) -> Tuple[bool, Optional[OrcamentoItem], Optional[str]]:
        """
        Adiciona novo item ao orçamento

        Args:
            orcamento_id: ID do orçamento
            secao_id: ID da secção
            descricao: Descrição do item
            quantidade: Quantidade
            dias: Número de dias
            preco_unitario: Preço unitário
            desconto: Desconto (0 a 1, ex: 0.1 = 10%)
            ordem: Ordem de apresentação
            **kwargs: Campos opcionais (equipamento_id, reparticao, afetacao, etc.)

        Returns:
            (sucesso, item, mensagem_erro)
        """
        try:
            # Calcular total
            total = (quantidade * dias * preco_unitario) * (1 - desconto)

            item = OrcamentoItem(
                orcamento_id=orcamento_id,
                secao_id=secao_id,
                descricao=descricao,
                quantidade=quantidade,
                dias=dias,
                preco_unitario=preco_unitario,
                desconto=desconto,
                total=total,
                ordem=ordem,
                **kwargs
            )

            self.db.add(item)
            self.db.commit()
            self.db.refresh(item)

            # Recalcular totais do orçamento
            self.recalcular_totais(orcamento_id)

            return True, item, None

        except Exception as e:
            self.db.rollback()
            return False, None, str(e)

    def atualizar_item(
        self,
        item_id: int,
        **kwargs
    ) -> Tuple[bool, Optional[OrcamentoItem], Optional[str]]:
        """
        Atualiza item existente e recalcula o total

        Returns:
            (sucesso, item, mensagem_erro)
        """
        try:
            item = self.db.query(OrcamentoItem).filter(OrcamentoItem.id == item_id).first()
            if not item:
                return False, None, "Item não encontrado"

            # Atualizar campos
            for key, value in kwargs.items():
                if hasattr(item, key):
                    setattr(item, key, value)

            # Recalcular total
            item.total = (item.quantidade * item.dias * item.preco_unitario) * (1 - item.desconto)

            self.db.commit()
            self.db.refresh(item)

            # Recalcular totais do orçamento
            self.recalcular_totais(item.orcamento_id)

            return True, item, None

        except Exception as e:
            self.db.rollback()
            return False, None, str(e)

    def eliminar_item(self, item_id: int) -> Tuple[bool, Optional[str]]:
        """
        Elimina item do orçamento

        Returns:
            (sucesso, mensagem_erro)
        """
        try:
            item = self.db.query(OrcamentoItem).filter(OrcamentoItem.id == item_id).first()
            if not item:
                return False, "Item não encontrado"

            orcamento_id = item.orcamento_id
            self.db.delete(item)
            self.db.commit()

            # Recalcular totais do orçamento
            self.recalcular_totais(orcamento_id)

            return True, None

        except Exception as e:
            self.db.rollback()
            return False, str(e)

    def obter_itens(self, orcamento_id: int, secao_id: Optional[int] = None) -> List[OrcamentoItem]:
        """
        Obtém items de um orçamento, opcionalmente filtrados por secção

        Args:
            orcamento_id: ID do orçamento
            secao_id: ID da secção (opcional)

        Returns:
            Lista de items ordenados
        """
        query = self.db.query(OrcamentoItem).filter(OrcamentoItem.orcamento_id == orcamento_id)

        if secao_id:
            query = query.filter(OrcamentoItem.secao_id == secao_id)

        return query.order_by(OrcamentoItem.ordem).all()

    # ==================== Items V2 (Tipo-específicos) ====================

    def adicionar_item_v2(
        self,
        orcamento_id: int,
        secao_id: int,
        tipo: str,
        descricao: str,
        ordem: int = 0,
        **kwargs
    ) -> Tuple[bool, Optional[OrcamentoItem], Optional[str]]:
        """
        Adiciona novo item V2 ao orçamento (suporta todos os tipos)

        Args:
            orcamento_id: ID do orçamento
            secao_id: ID da secção
            tipo: Tipo do item ('servico', 'equipamento', 'transporte', 'refeicao', 'outro')
            descricao: Descrição do item
            ordem: Ordem de apresentação
            **kwargs: Campos específicos por tipo

        Returns:
            (sucesso, item, mensagem_erro)
        """
        try:
            # Criar item com campos base
            item = OrcamentoItem(
                orcamento_id=orcamento_id,
                secao_id=secao_id,
                tipo=tipo,
                descricao=descricao,
                ordem=ordem,
                total=Decimal('0')  # Será calculado
            )

            # Adicionar campos específicos por tipo
            for key, value in kwargs.items():
                if hasattr(item, key):
                    setattr(item, key, value)

            # Calcular total usando método do modelo
            item.total = item.calcular_total()

            self.db.add(item)
            self.db.commit()
            self.db.refresh(item)

            # Recalcular totais do orçamento
            self.recalcular_totais(orcamento_id)

            return True, item, None

        except Exception as e:
            self.db.rollback()
            return False, None, str(e)

    def atualizar_item_v2(
        self,
        item_id: int,
        **kwargs
    ) -> Tuple[bool, Optional[OrcamentoItem], Optional[str]]:
        """
        Atualiza item V2 existente e recalcula o total

        Returns:
            (sucesso, item, mensagem_erro)
        """
        try:
            item = self.db.query(OrcamentoItem).filter(OrcamentoItem.id == item_id).first()
            if not item:
                return False, None, "Item não encontrado"

            # Atualizar campos fornecidos
            for key, value in kwargs.items():
                if hasattr(item, key):
                    setattr(item, key, value)

            # Recalcular total usando método do modelo
            item.total = item.calcular_total()

            self.db.commit()
            self.db.refresh(item)

            # Recalcular totais do orçamento
            self.recalcular_totais(item.orcamento_id)

            return True, item, None

        except Exception as e:
            self.db.rollback()
            return False, None, str(e)

    # ==================== Cálculos ====================

    def recalcular_totais(self, orcamento_id: int) -> bool:
        """
        Recalcula os totais do orçamento (Total Parcial 1, 2 e Total)

        Total Parcial 1 = Soma de items de Serviços + Equipamento
        Total Parcial 2 = Soma de items de Despesas
        Total = Total Parcial 1 + Total Parcial 2

        Returns:
            True se sucesso, False caso contrário
        """
        try:
            orcamento = self.obter_orcamento(orcamento_id)
            if not orcamento:
                return False

            # Obter todas as secções
            secoes = self.obter_secoes(orcamento_id)

            # IDs de secções de serviços e equipamento (incluindo subsecções)
            secoes_parcial_1 = []
            secoes_parcial_2 = []

            for secao in secoes:
                if secao.tipo in ['servicos', 'equipamento', 'video', 'som', 'iluminacao']:
                    secoes_parcial_1.append(secao.id)
                elif secao.tipo in ['despesas', 'custos_variaveis']:
                    secoes_parcial_2.append(secao.id)

            # Calcular Total Parcial 1
            if secoes_parcial_1:
                total_parcial_1 = self.db.query(func.sum(OrcamentoItem.total))\
                    .filter(OrcamentoItem.orcamento_id == orcamento_id)\
                    .filter(OrcamentoItem.secao_id.in_(secoes_parcial_1))\
                    .scalar() or Decimal('0')
            else:
                total_parcial_1 = Decimal('0')

            # Calcular Total Parcial 2
            if secoes_parcial_2:
                total_parcial_2 = self.db.query(func.sum(OrcamentoItem.total))\
                    .filter(OrcamentoItem.orcamento_id == orcamento_id)\
                    .filter(OrcamentoItem.secao_id.in_(secoes_parcial_2))\
                    .scalar() or Decimal('0')
            else:
                total_parcial_2 = Decimal('0')

            # Atualizar orçamento
            orcamento.total_parcial_1 = total_parcial_1
            orcamento.total_parcial_2 = total_parcial_2
            orcamento.valor_total = total_parcial_1 + total_parcial_2
            orcamento.updated_at = datetime.now()

            self.db.commit()
            return True

        except Exception as e:
            self.db.rollback()
            print(f"Erro ao recalcular totais: {e}")
            return False

    # ==================== Repartição (Backend) ====================

    def adicionar_reparticao(
        self,
        orcamento_id: int,
        entidade: str,
        valor: Decimal,
        percentagem: Optional[Decimal] = None,
        ordem: int = 0
    ) -> Tuple[bool, Optional[OrcamentoReparticao], Optional[str]]:
        """
        Adiciona repartição ao orçamento (Contas finais - económico interno)

        Args:
            orcamento_id: ID do orçamento
            entidade: Nome da entidade (BA, RR, Agora, Freelancers, Despesas)
            valor: Valor atribuído
            percentagem: Percentagem do total (opcional)
            ordem: Ordem de apresentação

        Returns:
            (sucesso, reparticao, mensagem_erro)
        """
        try:
            reparticao = OrcamentoReparticao(
                orcamento_id=orcamento_id,
                entidade=entidade,
                valor=valor,
                percentagem=percentagem,
                ordem=ordem
            )

            self.db.add(reparticao)
            self.db.commit()
            self.db.refresh(reparticao)

            return True, reparticao, None

        except Exception as e:
            self.db.rollback()
            return False, None, str(e)

    def obter_reparticoes(self, orcamento_id: int) -> List[OrcamentoReparticao]:
        """Obtém todas as repartições de um orçamento"""
        return self.db.query(OrcamentoReparticao)\
            .filter(OrcamentoReparticao.orcamento_id == orcamento_id)\
            .order_by(OrcamentoReparticao.ordem)\
            .all()

    def atualizar_reparticao(
        self,
        reparticao_id: int,
        **kwargs
    ) -> Tuple[bool, Optional[OrcamentoReparticao], Optional[str]]:
        """
        Atualiza repartição existente

        Args:
            reparticao_id: ID da repartição
            **kwargs: Campos a atualizar (entidade, valor, percentagem, ordem)

        Returns:
            (sucesso, reparticao, mensagem_erro)
        """
        try:
            reparticao = self.db.query(OrcamentoReparticao).filter(
                OrcamentoReparticao.id == reparticao_id
            ).first()

            if not reparticao:
                return False, None, "Repartição não encontrada"

            # Atualizar campos fornecidos
            for key, value in kwargs.items():
                if hasattr(reparticao, key):
                    setattr(reparticao, key, value)

            self.db.commit()
            self.db.refresh(reparticao)

            return True, reparticao, None

        except Exception as e:
            self.db.rollback()
            return False, None, str(e)

    def eliminar_reparticao(self, reparticao_id: int) -> Tuple[bool, Optional[str]]:
        """
        Elimina repartição do orçamento

        Args:
            reparticao_id: ID da repartição

        Returns:
            (sucesso, mensagem_erro)
        """
        try:
            reparticao = self.db.query(OrcamentoReparticao).filter(
                OrcamentoReparticao.id == reparticao_id
            ).first()

            if not reparticao:
                return False, "Repartição não encontrada"

            self.db.delete(reparticao)
            self.db.commit()

            return True, None

        except Exception as e:
            self.db.rollback()
            return False, str(e)

    # ==================== Utilidades ====================

    def duplicar_orcamento(
        self,
        orcamento_id: int,
        novo_codigo: str
    ) -> Tuple[bool, Optional[Orcamento], Optional[str]]:
        """
        Duplica um orçamento com novo código

        Args:
            orcamento_id: ID do orçamento a duplicar
            novo_codigo: Novo código para o orçamento duplicado

        Returns:
            (sucesso, novo_orcamento, mensagem_erro)
        """
        try:
            orcamento_original = self.obter_orcamento(orcamento_id)
            if not orcamento_original:
                return False, None, "Orçamento não encontrado"

            # Verificar se novo código já existe
            existe = self.obter_por_codigo(novo_codigo)
            if existe:
                return False, None, f"Orçamento {novo_codigo} já existe"

            # Criar novo orçamento com dados duplicados
            novo_orcamento = Orcamento(
                codigo=novo_codigo,
                cliente_id=orcamento_original.cliente_id,
                data_criacao=orcamento_original.data_criacao,
                data_evento=orcamento_original.data_evento,
                local_evento=orcamento_original.local_evento,
                descricao_proposta=orcamento_original.descricao_proposta,
                notas_contratuais=orcamento_original.notas_contratuais,
                tem_versao_cliente=orcamento_original.tem_versao_cliente,
                titulo_cliente=orcamento_original.titulo_cliente,
                descricao_cliente=orcamento_original.descricao_cliente,
                status='rascunho'
            )

            self.db.add(novo_orcamento)
            self.db.flush()  # Para obter o ID

            # Duplicar secções
            secoes_map = {}  # Mapear IDs antigos para novos
            for secao in orcamento_original.secoes:
                nova_secao = OrcamentoSecao(
                    orcamento_id=novo_orcamento.id,
                    tipo=secao.tipo,
                    nome=secao.nome,
                    ordem=secao.ordem,
                    parent_id=None  # Será atualizado depois
                )
                self.db.add(nova_secao)
                self.db.flush()
                secoes_map[secao.id] = nova_secao.id

            # Atualizar parent_ids das subsecções
            for secao_antiga in orcamento_original.secoes:
                if secao_antiga.parent_id:
                    secao_nova_id = secoes_map[secao_antiga.id]
                    secao_nova = self.db.query(OrcamentoSecao).get(secao_nova_id)
                    secao_nova.parent_id = secoes_map.get(secao_antiga.parent_id)

            # Duplicar items
            for item in orcamento_original.itens:
                novo_item = OrcamentoItem(
                    orcamento_id=novo_orcamento.id,
                    secao_id=secoes_map[item.secao_id],
                    descricao=item.descricao,
                    quantidade=item.quantidade,
                    dias=item.dias,
                    preco_unitario=item.preco_unitario,
                    desconto=item.desconto,
                    total=item.total,
                    ordem=item.ordem,
                    equipamento_id=item.equipamento_id,
                    reparticao=item.reparticao,
                    afetacao=item.afetacao,
                    investimento=item.investimento,
                    amortizacao=item.amortizacao
                )
                self.db.add(novo_item)

            # Duplicar repartições (se backend)
            for reparticao in orcamento_original.reparticoes:
                nova_reparticao = OrcamentoReparticao(
                    orcamento_id=novo_orcamento.id,
                    entidade=reparticao.entidade,
                    valor=reparticao.valor,
                    percentagem=reparticao.percentagem,
                    ordem=reparticao.ordem
                )
                self.db.add(nova_reparticao)

            self.db.commit()
            self.db.refresh(novo_orcamento)

            # Recalcular totais
            self.recalcular_totais(novo_orcamento.id)

            return True, novo_orcamento, None

        except Exception as e:
            self.db.rollback()
            return False, None, str(e)

    def obter_status(self) -> List[str]:
        """Obtém lista de status possíveis"""
        return ["Todos", "rascunho", "enviado", "aprovado", "rejeitado"]

    def aprovar_orcamento(self, orcamento_id: int) -> Tuple[bool, Optional[Orcamento], Optional[str]]:
        """
        Aprova um orçamento após validações completas

        Validações:
        1. Orçamento existe
        2. Tem pelo menos 1 item CLIENTE
        3. Tem pelo menos 1 item EMPRESA
        4. TOTAL_CLIENTE == TOTAL_EMPRESA (tolerância 0.01€)

        Args:
            orcamento_id: ID do orçamento a aprovar

        Returns:
            (sucesso, orcamento_atualizado, mensagem_erro)
        """
        try:
            # 1. Validar que orçamento existe
            orcamento = self.obter_orcamento(orcamento_id)
            if not orcamento:
                return False, None, "Orçamento não encontrado"

            # 2. Validar que tem items CLIENTE (mínimo 1)
            itens_cliente = self.obter_itens(orcamento_id)
            if not itens_cliente or len(itens_cliente) == 0:
                return False, None, "Orçamento deve ter pelo menos 1 item CLIENTE"

            # 3. Validar que tem items EMPRESA (mínimo 1)
            itens_empresa = self.obter_reparticoes(orcamento_id)
            if not itens_empresa or len(itens_empresa) == 0:
                return False, None, "Orçamento deve ter pelo menos 1 item EMPRESA"

            # 4. Validar TOTAL_CLIENTE == TOTAL_EMPRESA (tolerância 0.01€)
            total_cliente = sum(item.total for item in itens_cliente)
            total_empresa = sum(item.total for item in itens_empresa)

            diferenca = abs(total_cliente - total_empresa)
            tolerancia = Decimal('0.01')

            if diferenca > tolerancia:
                return False, None, (
                    f"Totais não coincidem: CLIENTE €{float(total_cliente):.2f} vs "
                    f"EMPRESA €{float(total_empresa):.2f} (diferença: €{float(diferenca):.2f})"
                )

            # 4.5. Criar registos históricos para beneficiários externos (freelancers/fornecedores)
            # Import managers here to avoid circular imports
            from logic.freelancer_trabalhos import FreelancerTrabalhosManager
            from logic.fornecedor_compras import FornecedorComprasManager

            freelancer_manager = FreelancerTrabalhosManager(self.db)
            fornecedor_manager = FornecedorComprasManager(self.db)

            for reparticao in itens_empresa:
                beneficiario = reparticao.beneficiario

                # Criar registo para Freelancer
                if beneficiario and beneficiario.startswith("FREELANCER_"):
                    try:
                        freelancer_id = int(beneficiario.replace("FREELANCER_", ""))
                        sucesso, trabalho, msg = freelancer_manager.criar(
                            freelancer_id=freelancer_id,
                            orcamento_id=orcamento_id,
                            projeto_id=orcamento.projeto_id,
                            descricao=reparticao.descricao or "Trabalho do orçamento",
                            valor=reparticao.total,
                            data=date.today(),
                            status=StatusTrabalho.A_PAGAR
                        )
                        if not sucesso:
                            return False, None, f"Erro ao criar trabalho freelancer: {msg}"
                    except ValueError as e:
                        return False, None, f"Erro ao processar beneficiário freelancer: {str(e)}"

                # Criar registo para Fornecedor
                elif beneficiario and beneficiario.startswith("FORNECEDOR_"):
                    try:
                        fornecedor_id = int(beneficiario.replace("FORNECEDOR_", ""))
                        sucesso, compra, msg = fornecedor_manager.criar(
                            fornecedor_id=fornecedor_id,
                            orcamento_id=orcamento_id,
                            projeto_id=orcamento.projeto_id,
                            descricao=reparticao.descricao or "Compra do orçamento",
                            valor=reparticao.total,
                            data=date.today(),
                            status=StatusTrabalho.A_PAGAR
                        )
                        if not sucesso:
                            return False, None, f"Erro ao criar compra fornecedor: {msg}"
                    except ValueError as e:
                        return False, None, f"Erro ao processar beneficiário fornecedor: {str(e)}"

            # 5. Atualizar status = "aprovado"
            orcamento.status = 'aprovado'
            orcamento.updated_at = datetime.now()

            self.db.commit()
            self.db.refresh(orcamento)

            return True, orcamento, None

        except Exception as e:
            self.db.rollback()
            return False, None, f"Erro ao aprovar orçamento: {str(e)}"

    def estatisticas(self) -> dict:
        """
        Retorna estatísticas de orçamentos

        Returns:
            Dicionário com estatísticas
        """
        total = self.db.query(Orcamento).count()

        # Valor total de orçamentos aprovados
        valor_aprovado = self.db.query(func.sum(Orcamento.valor_total))\
            .filter(Orcamento.status == 'aprovado')\
            .scalar() or Decimal('0')

        # Por status
        por_status = {}
        status_counts = self.db.query(
            Orcamento.status,
            func.count(Orcamento.id)
        ).group_by(Orcamento.status).all()

        for status, count in status_counts:
            por_status[status] = count

        # Com/sem versão cliente
        com_versao_cliente = self.db.query(Orcamento)\
            .filter(Orcamento.tem_versao_cliente == True)\
            .count()

        return {
            'total': total,
            'valor_total_aprovado': float(valor_aprovado),
            'por_status': por_status,
            'com_versao_cliente': com_versao_cliente
        }

    def converter_em_projeto(self, orcamento_id: int) -> Tuple[bool, Optional[int], Optional[str]]:
        """
        Converte orçamento aprovado em projeto, distribuindo valores por beneficiário.

        Args:
            orcamento_id: ID do orçamento a converter

        Returns:
            Tuple (sucesso, projeto_id, mensagem_erro_ou_confirmacao)

        Processo:
            1. Verifica se orçamento está aprovado
            2. Verifica se já foi convertido (projeto_id existe)
            3. Calcula totais por tipo de beneficiário (BA, RR, AGORA, externos)
            4. Cria projeto com campos rastreabilidade preenchidos
            5. Atualiza orçamento.projeto_id
            6. Retorna mensagem com distribuição de valores
        """
        # Import aqui para evitar circular imports
        from logic.projetos import ProjetosManager

        # 1. Obter orçamento
        orcamento = self.obter_orcamento(orcamento_id)
        if not orcamento:
            return False, None, "Orçamento não encontrado"

        # 2. Verificar se está aprovado
        if orcamento.status != 'aprovado':
            return False, None, "Orçamento precisa estar aprovado para converter em projeto"

        # 3. Verificar se já foi convertido
        if orcamento.projeto_id:
            return False, None, f"Orçamento já foi convertido em projeto #P{orcamento.projeto_id:04d}"

        # 4. Calcular totais por tipo de beneficiário
        totais = {
            'BA': Decimal('0'),
            'RR': Decimal('0'),
            'AGORA': Decimal('0'),
            'freelancers': Decimal('0'),
            'fornecedores': Decimal('0')
        }

        reparticoes = self.obter_reparticoes(orcamento_id)

        for reparticao in reparticoes:
            beneficiario = reparticao.beneficiario
            if not beneficiario:
                continue

            if beneficiario == 'BA':
                totais['BA'] += reparticao.total
            elif beneficiario == 'RR':
                totais['RR'] += reparticao.total
            elif beneficiario == 'AGORA':
                totais['AGORA'] += reparticao.total
            elif beneficiario.startswith('FREELANCER_'):
                totais['freelancers'] += reparticao.total
            elif beneficiario.startswith('FORNECEDOR_'):
                totais['fornecedores'] += reparticao.total

        # 5. Validar soma de totais (tolerância 0.01€)
        soma_totais = sum(totais.values())
        if abs(soma_totais - orcamento.valor_total) > Decimal('0.01'):
            return False, None, (
                f"Erro na distribuição: Soma dos beneficiários (€{float(soma_totais):.2f}) "
                f"difere do total do orçamento (€{float(orcamento.valor_total):.2f})"
            )

        # 6. Criar projeto
        projetos_manager = ProjetosManager(self.db)

        # Determinar tipo de projeto (usar FULLSTACK como padrão se não especificado)
        tipo_projeto = TipoProjeto.FULLSTACK

        sucesso, projeto, msg_erro = projetos_manager.criar_projeto(
            codigo=None,  # Gerar automaticamente
            cliente_id=orcamento.cliente_id,
            socio_responsavel=orcamento.owner,
            tipo=tipo_projeto,
            nome=f"Projeto {orcamento.codigo}",
            valor_frontend=Decimal('0'),  # Pode ajustar se necessário
            valor_backend=Decimal('0'),   # Pode ajustar se necessário
            valor_total=orcamento.valor_total,
            premio_bruno=totais['BA'],
            premio_rafael=totais['RR'],
            valor_empresa=totais['AGORA'],
            valor_fornecedores=totais['freelancers'] + totais['fornecedores'],
            data_inicio=date.today(),
            estado=EstadoProjeto.ATIVO
        )

        if not sucesso:
            return False, None, f"Erro ao criar projeto: {msg_erro}"

        # 7. Atualizar orçamento com link para projeto
        orcamento.projeto_id = projeto.id
        orcamento.updated_at = datetime.now()
        self.db.commit()

        # 8. Criar mensagem de confirmação com distribuição
        mensagem = f"""Projeto criado com sucesso!
{projeto.codigo} - Valor total: €{float(orcamento.valor_total):,.2f}

Distribuição:
- Bruno: €{float(totais['BA']):,.2f}
- Rafael: €{float(totais['RR']):,.2f}
- Empresa: €{float(totais['AGORA']):,.2f}
- Externos: €{float(totais['freelancers'] + totais['fornecedores']):,.2f}"""

        return True, projeto.id, mensagem
