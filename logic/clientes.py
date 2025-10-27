# -*- coding: utf-8 -*-
"""
Logic de gestão de Clientes
"""
from sqlalchemy.orm import Session
from sqlalchemy import desc
from database.models import Cliente
from typing import List, Tuple, Optional


class ClientesManager:
    """
    Gestor de operações CRUD para Clientes
    """

    def __init__(self, db_session: Session):
        """
        Initialize manager

        Args:
            db_session: SQLAlchemy database session
        """
        self.db = db_session

    def listar_todos(self, order_by: str = 'numero') -> List[Cliente]:
        """
        List all clientes

        Args:
            order_by: Field to order by (numero, nome, pais)

        Returns:
            List of Cliente objects
        """
        query = self.db.query(Cliente)

        if order_by == 'numero':
            query = query.order_by(desc(Cliente.numero))
        elif order_by == 'nome':
            query = query.order_by(Cliente.nome)
        elif order_by == 'pais':
            query = query.order_by(Cliente.pais, Cliente.nome)

        return query.all()

    def buscar_por_id(self, cliente_id: int) -> Optional[Cliente]:
        """
        Find cliente by ID

        Args:
            cliente_id: Cliente ID

        Returns:
            Cliente object or None
        """
        return self.db.query(Cliente).filter(Cliente.id == cliente_id).first()

    def buscar_por_numero(self, numero: str) -> Optional[Cliente]:
        """
        Find cliente by numero

        Args:
            numero: Cliente numero (e.g., #C0001)

        Returns:
            Cliente object or None
        """
        return self.db.query(Cliente).filter(Cliente.numero == numero).first()

    def pesquisar(self, termo: str) -> List[Cliente]:
        """
        Search clientes by nome, NIF, or email

        Args:
            termo: Search term

        Returns:
            List of matching Cliente objects
        """
        termo_like = f"%{termo}%"
        return self.db.query(Cliente).filter(
            (Cliente.nome.ilike(termo_like)) |
            (Cliente.nif.ilike(termo_like)) |
            (Cliente.email.ilike(termo_like))
        ).order_by(Cliente.nome).all()

    def gerar_proximo_numero(self) -> str:
        """
        Generate next cliente numero

        Returns:
            Next numero (e.g., #C0001, #C0002, ...)
        """
        ultimo = self.db.query(Cliente).order_by(desc(Cliente.numero)).first()

        if not ultimo:
            return "#C0001"

        # Extract number from #C0001 format
        try:
            num = int(ultimo.numero.replace("#C", ""))
            return f"#C{num + 1:04d}"
        except:
            return "#C0001"

    def criar(
        self,
        nome: str,
        nif: str = None,
        morada: str = None,
        pais: str = "Portugal",
        contacto: str = None,
        email: str = None,
        angariacao: str = None,
        nota: str = None
    ) -> Tuple[bool, Optional[Cliente], str]:
        """
        Create new cliente

        Args:
            nome: Nome do cliente (required)
            nif: NIF/Tax ID
            morada: Morada completa
            pais: País (default: Portugal)
            contacto: Contacto telefónico
            email: Email address
            angariacao: Como foi angariado o cliente
            nota: Notas adicionais

        Returns:
            Tuple (success, cliente_object, message)
        """
        try:
            # Validate
            if not nome or nome.strip() == "":
                return False, None, "Nome é obrigatório"

            # Generate numero
            numero = self.gerar_proximo_numero()

            # Create cliente
            cliente = Cliente(
                numero=numero,
                nome=nome.strip(),
                nif=nif.strip() if nif else None,
                morada=morada.strip() if morada else None,
                pais=pais.strip() if pais else "Portugal",
                contacto=contacto.strip() if contacto else None,
                email=email.strip() if email else None,
                angariacao=angariacao.strip() if angariacao else None,
                nota=nota.strip() if nota else None
            )

            self.db.add(cliente)
            self.db.commit()
            self.db.refresh(cliente)

            return True, cliente, f"Cliente {numero} criado com sucesso"

        except Exception as e:
            self.db.rollback()
            return False, None, f"Erro ao criar cliente: {str(e)}"

    def atualizar(
        self,
        cliente_id: int,
        nome: str = None,
        nif: str = None,
        morada: str = None,
        pais: str = None,
        contacto: str = None,
        email: str = None,
        angariacao: str = None,
        nota: str = None
    ) -> Tuple[bool, Optional[Cliente], str]:
        """
        Update cliente

        Args:
            cliente_id: Cliente ID
            nome: Nome do cliente
            nif: NIF/Tax ID
            morada: Morada completa
            pais: País
            contacto: Contacto telefónico
            email: Email address
            angariacao: Como foi angariado
            nota: Notas adicionais

        Returns:
            Tuple (success, cliente_object, message)
        """
        try:
            cliente = self.buscar_por_id(cliente_id)
            if not cliente:
                return False, None, "Cliente não encontrado"

            # Update fields if provided
            if nome is not None:
                if nome.strip() == "":
                    return False, None, "Nome não pode estar vazio"
                cliente.nome = nome.strip()

            if nif is not None:
                cliente.nif = nif.strip() if nif.strip() else None

            if morada is not None:
                cliente.morada = morada.strip() if morada.strip() else None

            if pais is not None:
                cliente.pais = pais.strip() if pais.strip() else "Portugal"

            if contacto is not None:
                cliente.contacto = contacto.strip() if contacto.strip() else None

            if email is not None:
                cliente.email = email.strip() if email.strip() else None

            if angariacao is not None:
                cliente.angariacao = angariacao.strip() if angariacao.strip() else None

            if nota is not None:
                cliente.nota = nota.strip() if nota.strip() else None

            self.db.commit()
            self.db.refresh(cliente)

            return True, cliente, f"Cliente {cliente.numero} atualizado com sucesso"

        except Exception as e:
            self.db.rollback()
            return False, None, f"Erro ao atualizar cliente: {str(e)}"

    def apagar(self, cliente_id: int) -> Tuple[bool, str]:
        """
        Delete cliente

        Args:
            cliente_id: Cliente ID

        Returns:
            Tuple (success, message)
        """
        try:
            cliente = self.buscar_por_id(cliente_id)
            if not cliente:
                return False, "Cliente não encontrado"

            # Check if cliente has projetos
            if cliente.projetos:
                return False, f"Não é possível apagar cliente com {len(cliente.projetos)} projeto(s) associado(s)"

            numero = cliente.numero
            self.db.delete(cliente)
            self.db.commit()

            return True, f"Cliente {numero} apagado com sucesso"

        except Exception as e:
            self.db.rollback()
            return False, f"Erro ao apagar cliente: {str(e)}"

    def contar_projetos(self, cliente_id: int) -> int:
        """
        Count number of projetos for a cliente

        Args:
            cliente_id: Cliente ID

        Returns:
            Number of projetos
        """
        cliente = self.buscar_por_id(cliente_id)
        if not cliente:
            return 0
        return len(cliente.projetos)
