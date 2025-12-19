# -*- coding: utf-8 -*-
"""
Logic de gestão de Freelancers
"""
from sqlalchemy.orm import Session
from sqlalchemy import desc
from database.models import Freelancer
from typing import List, Tuple, Optional


class FreelancersManager:
    """
    Gestor de operações CRUD para Freelancers
    """

    def __init__(self, db_session: Session):
        """
        Initialize manager

        Args:
            db_session: SQLAlchemy database session
        """
        self.db = db_session

    def listar_todos(self, order_by: str = 'numero', incluir_inativos: bool = False) -> List[Freelancer]:
        """
        List all freelancers

        Args:
            order_by: Field to order by (numero, nome)
            incluir_inativos: Include inactive freelancers

        Returns:
            List of Freelancer objects
        """
        query = self.db.query(Freelancer)

        if not incluir_inativos:
            query = query.filter(Freelancer.ativo == True)

        if order_by == 'numero':
            query = query.order_by(desc(Freelancer.numero))
        elif order_by == 'nome':
            query = query.order_by(Freelancer.nome)

        return query.all()

    def listar_ativos(self) -> List[Freelancer]:
        """
        List only active freelancers

        Returns:
            List of active Freelancer objects
        """
        return self.db.query(Freelancer).filter(Freelancer.ativo == True).order_by(Freelancer.nome).all()

    def buscar_por_id(self, freelancer_id: int) -> Optional[Freelancer]:
        """
        Find freelancer by ID

        Args:
            freelancer_id: Freelancer ID

        Returns:
            Freelancer object or None
        """
        return self.db.query(Freelancer).filter(Freelancer.id == freelancer_id).first()

    def buscar_por_numero(self, numero: str) -> Optional[Freelancer]:
        """
        Find freelancer by numero

        Args:
            numero: Freelancer numero (e.g., #F0001)

        Returns:
            Freelancer object or None
        """
        return self.db.query(Freelancer).filter(Freelancer.numero == numero).first()

    def pesquisar(self, termo: str, incluir_inativos: bool = False) -> List[Freelancer]:
        """
        Search freelancers by nome, NIF, email, or especialidade

        Args:
            termo: Search term
            incluir_inativos: Include inactive freelancers

        Returns:
            List of matching Freelancer objects
        """
        termo_like = f"%{termo}%"
        query = self.db.query(Freelancer).filter(
            (Freelancer.nome.ilike(termo_like)) |
            (Freelancer.nif.ilike(termo_like)) |
            (Freelancer.email.ilike(termo_like)) |
            (Freelancer.especialidade.ilike(termo_like))
        )

        if not incluir_inativos:
            query = query.filter(Freelancer.ativo == True)

        return query.order_by(Freelancer.nome).all()

    def gerar_proximo_numero(self) -> str:
        """
        Generate next freelancer numero

        Returns:
            Next numero (e.g., #F0001, #F0002, ...)
        """
        ultimo = self.db.query(Freelancer).order_by(desc(Freelancer.numero)).first()

        if not ultimo:
            return "#F0001"

        # Extract number from #F0001 format
        try:
            numero_str = ultimo.numero.replace('#F', '')
            numero_int = int(numero_str)
            proximo = numero_int + 1
            return f"#F{proximo:04d}"
        except (ValueError, AttributeError):
            return "#F0001"

    def criar(self, nome: str, nif: str = None, email: str = None, telefone: str = None,
              iban: str = None, morada: str = None, especialidade: str = None,
              notas: str = None, ativo: bool = True) -> Tuple[bool, Freelancer, str]:
        """
        Create new freelancer

        Args:
            nome: Nome do freelancer
            nif: NIF (opcional)
            email: Email (opcional)
            telefone: Telefone (opcional)
            iban: IBAN (opcional)
            morada: Morada (opcional)
            especialidade: Especialidade (opcional)
            notas: Notas (opcional)
            ativo: Ativo (default True)

        Returns:
            Tuple (success, freelancer, message)
        """
        # Validação
        if not nome or not nome.strip():
            return False, None, "Nome é obrigatório"

        # Gerar número
        numero = self.gerar_proximo_numero()

        # Criar freelancer
        try:
            novo_freelancer = Freelancer(
                numero=numero,
                nome=nome.strip(),
                nif=nif.strip() if nif else None,
                email=email.strip() if email else None,
                telefone=telefone.strip() if telefone else None,
                iban=iban.strip() if iban else None,
                morada=morada.strip() if morada else None,
                especialidade=especialidade.strip() if especialidade else None,
                notas=notas.strip() if notas else None,
                ativo=ativo
            )

            self.db.add(novo_freelancer)
            self.db.commit()
            self.db.refresh(novo_freelancer)

            return True, novo_freelancer, f"Freelancer {numero} criado com sucesso"

        except Exception as e:
            self.db.rollback()
            return False, None, f"Erro ao criar freelancer: {str(e)}"

    def atualizar(self, freelancer_id: int, **kwargs) -> Tuple[bool, Optional[Freelancer], str]:
        """
        Update freelancer

        Args:
            freelancer_id: Freelancer ID
            **kwargs: Fields to update (nome, nif, email, telefone, iban, morada, especialidade, notas, ativo)

        Returns:
            Tuple (success, freelancer, message)
        """
        freelancer = self.buscar_por_id(freelancer_id)

        if not freelancer:
            return False, None, "Freelancer não encontrado"

        # Validação
        if 'nome' in kwargs and (not kwargs['nome'] or not kwargs['nome'].strip()):
            return False, None, "Nome é obrigatório"

        # Update fields
        try:
            for key, value in kwargs.items():
                if hasattr(freelancer, key):
                    # Strip strings
                    if isinstance(value, str):
                        value = value.strip() if value else None
                    setattr(freelancer, key, value)

            self.db.commit()
            self.db.refresh(freelancer)

            return True, freelancer, f"Freelancer {freelancer.numero} atualizado com sucesso"

        except Exception as e:
            self.db.rollback()
            return False, None, f"Erro ao atualizar freelancer: {str(e)}"

    def apagar(self, freelancer_id: int) -> Tuple[bool, str]:
        """
        Delete freelancer

        Args:
            freelancer_id: Freelancer ID

        Returns:
            Tuple (success, message)
        """
        freelancer = self.buscar_por_id(freelancer_id)

        if not freelancer:
            return False, "Freelancer não encontrado"

        try:
            numero = freelancer.numero
            self.db.delete(freelancer)
            self.db.commit()

            return True, f"Freelancer {numero} apagado com sucesso"

        except Exception as e:
            self.db.rollback()
            return False, f"Erro ao apagar freelancer: {str(e)}"

    def marcar_inativo(self, freelancer_id: int) -> Tuple[bool, Optional[Freelancer], str]:
        """
        Mark freelancer as inactive

        Args:
            freelancer_id: Freelancer ID

        Returns:
            Tuple (success, freelancer, message)
        """
        return self.atualizar(freelancer_id, ativo=False)

    def marcar_ativo(self, freelancer_id: int) -> Tuple[bool, Optional[Freelancer], str]:
        """
        Mark freelancer as active

        Args:
            freelancer_id: Freelancer ID

        Returns:
            Tuple (success, freelancer, message)
        """
        return self.atualizar(freelancer_id, ativo=True)
