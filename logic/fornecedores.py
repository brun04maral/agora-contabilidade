# -*- coding: utf-8 -*-
"""
Logic de gestão de Fornecedores
"""
from sqlalchemy.orm import Session
from sqlalchemy import desc
from database.models import Fornecedor, EstatutoFornecedor
from typing import List, Tuple, Optional
from datetime import datetime


class FornecedoresManager:
    """
    Gestor de operações CRUD para Fornecedores
    """

    def __init__(self, db_session: Session):
        """
        Initialize manager

        Args:
            db_session: SQLAlchemy database session
        """
        self.db = db_session

    def listar_todos(self, estatuto: Optional[EstatutoFornecedor] = None, order_by: str = 'numero') -> List[Fornecedor]:
        """
        List all fornecedores

        Args:
            estatuto: Filter by estatuto (optional)
            order_by: Field to order by (numero, nome, estatuto, area)

        Returns:
            List of Fornecedor objects
        """
        query = self.db.query(Fornecedor)

        # Filter by estatuto if provided
        if estatuto:
            query = query.filter(Fornecedor.estatuto == estatuto)

        # Order by
        if order_by == 'numero':
            query = query.order_by(desc(Fornecedor.numero))
        elif order_by == 'nome':
            query = query.order_by(Fornecedor.nome)
        elif order_by == 'estatuto':
            query = query.order_by(Fornecedor.estatuto, Fornecedor.nome)
        elif order_by == 'area':
            query = query.order_by(Fornecedor.area, Fornecedor.nome)

        return query.all()

    def buscar_por_id(self, fornecedor_id: int) -> Optional[Fornecedor]:
        """
        Find fornecedor by ID

        Args:
            fornecedor_id: Fornecedor ID

        Returns:
            Fornecedor object or None
        """
        return self.db.query(Fornecedor).filter(Fornecedor.id == fornecedor_id).first()

    def buscar_por_numero(self, numero: str) -> Optional[Fornecedor]:
        """
        Find fornecedor by numero

        Args:
            numero: Fornecedor numero (e.g., #F0001)

        Returns:
            Fornecedor object or None
        """
        return self.db.query(Fornecedor).filter(Fornecedor.numero == numero).first()

    def pesquisar(self, termo: str) -> List[Fornecedor]:
        """
        Search fornecedores by nome, NIF, area, funcao, or email

        Args:
            termo: Search term

        Returns:
            List of matching Fornecedor objects
        """
        termo_like = f"%{termo}%"
        return self.db.query(Fornecedor).filter(
            (Fornecedor.nome.ilike(termo_like)) |
            (Fornecedor.nif.ilike(termo_like)) |
            (Fornecedor.area.ilike(termo_like)) |
            (Fornecedor.funcao.ilike(termo_like)) |
            (Fornecedor.email.ilike(termo_like))
        ).order_by(Fornecedor.nome).all()

    def gerar_proximo_numero(self) -> str:
        """
        Generate next fornecedor numero

        Returns:
            Next numero (e.g., #F0001, #F0002, ...)
        """
        ultimo = self.db.query(Fornecedor).order_by(desc(Fornecedor.numero)).first()

        if not ultimo:
            return "#F0001"

        # Extract number from #F0001 format
        try:
            num = int(ultimo.numero.replace("#F", ""))
            return f"#F{num + 1:04d}"
        except:
            return "#F0001"

    def criar(
        self,
        nome: str,
        estatuto: EstatutoFornecedor,
        area: str = None,
        funcao: str = None,
        classificacao: int = None,
        validade_seguro_trabalho: datetime = None,
        nif: str = None,
        iban: str = None,
        morada: str = None,
        contacto: str = None,
        email: str = None,
        nota: str = None
    ) -> Tuple[bool, Optional[Fornecedor], str]:
        """
        Create new fornecedor

        Args:
            nome: Nome do fornecedor (required)
            estatuto: Estatuto (EMPRESA, FREELANCER, ESTADO) (required)
            area: Área de atuação
            funcao: Função específica
            classificacao: Classificação 1-5
            validade_seguro_trabalho: Validade do seguro de trabalho
            nif: NIF/Tax ID
            iban: IBAN
            morada: Morada completa
            contacto: Contacto telefónico
            email: Email address
            nota: Notas adicionais

        Returns:
            Tuple (success, fornecedor_object, message)
        """
        try:
            # Validate
            if not nome or nome.strip() == "":
                return False, None, "Nome é obrigatório"

            if not estatuto:
                return False, None, "Estatuto é obrigatório"

            if classificacao is not None and (classificacao < 1 or classificacao > 5):
                return False, None, "Classificação deve ser entre 1 e 5"

            # Generate numero
            numero = self.gerar_proximo_numero()

            # Create fornecedor
            fornecedor = Fornecedor(
                numero=numero,
                nome=nome.strip(),
                estatuto=estatuto,
                area=area.strip() if area else None,
                funcao=funcao.strip() if funcao else None,
                classificacao=classificacao,
                validade_seguro_trabalho=validade_seguro_trabalho,
                nif=nif.strip() if nif else None,
                iban=iban.strip() if iban else None,
                morada=morada.strip() if morada else None,
                contacto=contacto.strip() if contacto else None,
                email=email.strip() if email else None,
                nota=nota.strip() if nota else None
            )

            self.db.add(fornecedor)
            self.db.commit()
            self.db.refresh(fornecedor)

            return True, fornecedor, f"Fornecedor {numero} criado com sucesso"

        except Exception as e:
            self.db.rollback()
            return False, None, f"Erro ao criar fornecedor: {str(e)}"

    def atualizar(
        self,
        fornecedor_id: int,
        nome: str = None,
        estatuto: EstatutoFornecedor = None,
        area: str = None,
        funcao: str = None,
        classificacao: int = None,
        validade_seguro_trabalho: datetime = None,
        nif: str = None,
        iban: str = None,
        morada: str = None,
        contacto: str = None,
        email: str = None,
        nota: str = None
    ) -> Tuple[bool, Optional[Fornecedor], str]:
        """
        Update fornecedor

        Args:
            fornecedor_id: Fornecedor ID
            nome: Nome do fornecedor
            estatuto: Estatuto
            area: Área de atuação
            funcao: Função
            classificacao: Classificação 1-5
            validade_seguro_trabalho: Validade do seguro
            nif: NIF/Tax ID
            iban: IBAN
            morada: Morada
            contacto: Contacto
            email: Email
            nota: Nota

        Returns:
            Tuple (success, fornecedor_object, message)
        """
        try:
            fornecedor = self.buscar_por_id(fornecedor_id)
            if not fornecedor:
                return False, None, "Fornecedor não encontrado"

            # Update fields if provided
            if nome is not None:
                if nome.strip() == "":
                    return False, None, "Nome não pode estar vazio"
                fornecedor.nome = nome.strip()

            if estatuto is not None:
                fornecedor.estatuto = estatuto

            if area is not None:
                fornecedor.area = area.strip() if area.strip() else None

            if funcao is not None:
                fornecedor.funcao = funcao.strip() if funcao.strip() else None

            if classificacao is not None:
                if classificacao != 0 and (classificacao < 1 or classificacao > 5):
                    return False, None, "Classificação deve ser entre 1 e 5"
                fornecedor.classificacao = classificacao if classificacao != 0 else None

            if validade_seguro_trabalho is not None:
                fornecedor.validade_seguro_trabalho = validade_seguro_trabalho

            if nif is not None:
                fornecedor.nif = nif.strip() if nif.strip() else None

            if iban is not None:
                fornecedor.iban = iban.strip() if iban.strip() else None

            if morada is not None:
                fornecedor.morada = morada.strip() if morada.strip() else None

            if contacto is not None:
                fornecedor.contacto = contacto.strip() if contacto.strip() else None

            if email is not None:
                fornecedor.email = email.strip() if email.strip() else None

            if nota is not None:
                fornecedor.nota = nota.strip() if nota.strip() else None

            self.db.commit()
            self.db.refresh(fornecedor)

            return True, fornecedor, f"Fornecedor {fornecedor.numero} atualizado com sucesso"

        except Exception as e:
            self.db.rollback()
            return False, None, f"Erro ao atualizar fornecedor: {str(e)}"

    def apagar(self, fornecedor_id: int) -> Tuple[bool, str]:
        """
        Delete fornecedor

        Args:
            fornecedor_id: Fornecedor ID

        Returns:
            Tuple (success, message)
        """
        try:
            fornecedor = self.buscar_por_id(fornecedor_id)
            if not fornecedor:
                return False, "Fornecedor não encontrado"

            # Check if fornecedor has despesas
            if fornecedor.despesas:
                return False, f"Não é possível apagar fornecedor com {len(fornecedor.despesas)} despesa(s) associada(s)"

            numero = fornecedor.numero
            self.db.delete(fornecedor)
            self.db.commit()

            return True, f"Fornecedor {numero} apagado com sucesso"

        except Exception as e:
            self.db.rollback()
            return False, f"Erro ao apagar fornecedor: {str(e)}"

    def contar_despesas(self, fornecedor_id: int) -> int:
        """
        Count number of despesas for a fornecedor

        Args:
            fornecedor_id: Fornecedor ID

        Returns:
            Number of despesas
        """
        fornecedor = self.buscar_por_id(fornecedor_id)
        if not fornecedor:
            return 0
        return len(fornecedor.despesas)
