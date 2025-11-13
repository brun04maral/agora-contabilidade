# -*- coding: utf-8 -*-
"""
Lógica de gestão de Templates de Despesas Recorrentes (CRUD)
"""
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import desc
from decimal import Decimal

from database.models import DespesaTemplate, Fornecedor, Projeto, TipoDespesa


class DespesaTemplatesManager:
    """
    Gestor de Templates de Despesas Recorrentes - CRUD operations
    """

    def __init__(self, db_session: Session):
        """
        Initialize manager

        Args:
            db_session: SQLAlchemy database session
        """
        self.db_session = db_session

    def listar_todos(self) -> List[DespesaTemplate]:
        """
        Lista todos os templates ordenados por dia do mês

        Returns:
            Lista de objetos DespesaTemplate
        """
        return self.db_session.query(DespesaTemplate).order_by(DespesaTemplate.dia_mes).all()

    def listar_por_tipo(self, tipo: TipoDespesa) -> List[DespesaTemplate]:
        """
        Lista templates por tipo

        Args:
            tipo: TipoDespesa enum

        Returns:
            Lista de templates do tipo especificado
        """
        return self.db_session.query(DespesaTemplate).filter(
            DespesaTemplate.tipo == tipo
        ).order_by(DespesaTemplate.dia_mes).all()

    def obter_por_id(self, template_id: int) -> Optional[DespesaTemplate]:
        """
        Obtém um template por ID

        Args:
            template_id: ID do template

        Returns:
            Objeto DespesaTemplate ou None se não encontrado
        """
        return self.db_session.query(DespesaTemplate).filter(DespesaTemplate.id == template_id).first()

    def gerar_proximo_numero(self) -> str:
        """
        Gera próximo número de template

        Returns:
            Próximo número (ex: #TD000001, #TD000002, ...)
        """
        ultimo = self.db_session.query(DespesaTemplate).order_by(
            desc(DespesaTemplate.id)
        ).first()

        if not ultimo:
            return "#TD000001"

        # Extract number from #TD000001 format
        try:
            num = int(ultimo.numero.replace("#TD", ""))
            return f"#TD{num + 1:06d}"
        except:
            return "#TD000001"

    def criar(
        self,
        tipo: TipoDespesa,
        descricao: str,
        valor_sem_iva: Decimal,
        valor_com_iva: Decimal,
        dia_mes: int,
        credor_id: Optional[int] = None,
        projeto_id: Optional[int] = None,
        nota: Optional[str] = None
    ) -> Tuple[bool, Optional[DespesaTemplate], Optional[str]]:
        """
        Cria um novo template de despesa recorrente

        Args:
            tipo: Tipo da despesa
            descricao: Descrição
            valor_sem_iva: Valor sem IVA
            valor_com_iva: Valor com IVA
            dia_mes: Dia do mês (1-31)
            credor_id: ID do fornecedor/credor (opcional)
            projeto_id: ID do projeto associado (opcional)
            nota: Nota adicional (opcional)

        Returns:
            Tuple (sucesso, template, mensagem_erro)
        """
        try:
            # Validar dia do mês
            if dia_mes < 1 or dia_mes > 31:
                return False, None, "Dia do mês deve estar entre 1 e 31"

            # Gerar número do template
            numero = self.gerar_proximo_numero()

            # Criar template
            template = DespesaTemplate(
                numero=numero,
                tipo=tipo,
                credor_id=credor_id,
                projeto_id=projeto_id,
                descricao=descricao,
                valor_sem_iva=valor_sem_iva,
                valor_com_iva=valor_com_iva,
                dia_mes=dia_mes,
                nota=nota
            )

            self.db_session.add(template)
            self.db_session.commit()
            self.db_session.refresh(template)

            return True, template, None

        except Exception as e:
            self.db_session.rollback()
            return False, None, str(e)

    def atualizar(
        self,
        template_id: int,
        tipo: Optional[TipoDespesa] = None,
        descricao: Optional[str] = None,
        valor_sem_iva: Optional[Decimal] = None,
        valor_com_iva: Optional[Decimal] = None,
        dia_mes: Optional[int] = None,
        credor_id: Optional[int] = None,
        projeto_id: Optional[int] = None,
        nota: Optional[str] = None
    ) -> Tuple[bool, Optional[str]]:
        """
        Atualiza um template existente

        Args:
            template_id: ID do template
            (outros): Campos a atualizar

        Returns:
            Tuple (sucesso, mensagem_erro)
        """
        try:
            template = self.obter_por_id(template_id)
            if not template:
                return False, "Template não encontrado"

            if tipo is not None:
                template.tipo = tipo
            if descricao is not None:
                template.descricao = descricao
            if valor_sem_iva is not None:
                template.valor_sem_iva = valor_sem_iva
            if valor_com_iva is not None:
                template.valor_com_iva = valor_com_iva
            if dia_mes is not None:
                if dia_mes < 1 or dia_mes > 31:
                    return False, "Dia do mês deve estar entre 1 e 31"
                template.dia_mes = dia_mes
            if credor_id is not None:
                template.credor_id = credor_id
            if projeto_id is not None:
                template.projeto_id = projeto_id
            if nota is not None:
                template.nota = nota

            self.db_session.commit()
            return True, None

        except Exception as e:
            self.db_session.rollback()
            return False, str(e)

    def apagar(self, template_id: int) -> Tuple[bool, Optional[str]]:
        """
        Apaga um template

        Args:
            template_id: ID do template

        Returns:
            Tuple (sucesso, mensagem_erro)
        """
        try:
            template = self.obter_por_id(template_id)
            if not template:
                return False, "Template não encontrado"

            self.db_session.delete(template)
            self.db_session.commit()
            return True, None

        except Exception as e:
            self.db_session.rollback()
            return False, str(e)

    def obter_fornecedores(self) -> List[Fornecedor]:
        """
        Obtém lista de todos os fornecedores

        Returns:
            Lista de fornecedores
        """
        return self.db_session.query(Fornecedor).order_by(Fornecedor.nome).all()

    def obter_projetos(self) -> List[Projeto]:
        """
        Obtém lista de todos os projetos

        Returns:
            Lista de projetos
        """
        return self.db_session.query(Projeto).order_by(desc(Projeto.created_at)).all()
