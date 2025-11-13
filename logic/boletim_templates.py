# -*- coding: utf-8 -*-
"""
Lógica de gestão de Templates de Boletins Recorrentes (CRUD + Geração)
"""
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_
from datetime import datetime, date
from decimal import Decimal

from database.models.boletim_template import BoletimTemplate
from database.models.boletim import Boletim, Socio, EstadoBoletim
from database.models.boletim_linha import BoletimLinha, TipoDeslocacao
from database.models.projeto import Projeto, EstadoProjeto


class BoletimTemplatesManager:
    """
    Gestor de Templates de Boletins Recorrentes - CRUD + geração automática
    """

    def __init__(self, db_session: Session):
        """
        Initialize manager

        Args:
            db_session: SQLAlchemy database session
        """
        self.db_session = db_session

    def listar_todos(self) -> List[BoletimTemplate]:
        """
        Lista todos os templates ordenados por sócio e nome

        Returns:
            Lista de objetos BoletimTemplate
        """
        return self.db_session.query(BoletimTemplate).order_by(
            BoletimTemplate.socio,
            BoletimTemplate.nome
        ).all()

    def listar_ativos(self) -> List[BoletimTemplate]:
        """
        Lista apenas templates ativos

        Returns:
            Lista de templates ativos
        """
        return self.db_session.query(BoletimTemplate).filter(
            BoletimTemplate.ativo == True
        ).order_by(
            BoletimTemplate.socio,
            BoletimTemplate.nome
        ).all()

    def obter_por_id(self, template_id: int) -> Optional[BoletimTemplate]:
        """
        Obtém um template por ID

        Args:
            template_id: ID do template

        Returns:
            Objeto BoletimTemplate ou None se não encontrado
        """
        return self.db_session.query(BoletimTemplate).filter(
            BoletimTemplate.id == template_id
        ).first()

    def gerar_proximo_numero(self) -> str:
        """
        Gera próximo número de template

        Returns:
            Próximo número (ex: #TB000001, #TB000002, ...)
        """
        ultimo = self.db_session.query(BoletimTemplate).order_by(
            desc(BoletimTemplate.id)
        ).first()

        if not ultimo:
            return "#TB000001"

        # Extract number from #TB000001 format
        try:
            num = int(ultimo.numero.replace("#TB", ""))
            return f"#TB{num + 1:06d}"
        except:
            return "#TB000001"

    def criar(
        self,
        nome: str,
        socio: Socio,
        dia_mes: int,
        ativo: bool = True
    ) -> Tuple[bool, Optional[BoletimTemplate], Optional[str]]:
        """
        Cria um novo template de boletim recorrente

        Args:
            nome: Nome do template
            socio: Sócio (BRUNO/RAFAEL)
            dia_mes: Dia do mês para gerar (1-31)
            ativo: Se o template está ativo

        Returns:
            Tupla (sucesso, objeto, mensagem_erro)
        """
        try:
            # Validações
            if not nome or not nome.strip():
                return False, None, "Nome é obrigatório"

            if dia_mes < 1 or dia_mes > 31:
                return False, None, "Dia do mês deve estar entre 1 e 31"

            # Gerar número
            numero = self.gerar_proximo_numero()

            # Criar
            novo = BoletimTemplate(
                numero=numero,
                nome=nome.strip(),
                socio=socio,
                dia_mes=dia_mes,
                ativo=ativo,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )

            self.db_session.add(novo)
            self.db_session.commit()
            self.db_session.refresh(novo)

            return True, novo, None

        except Exception as e:
            self.db_session.rollback()
            return False, None, f"Erro ao criar template: {str(e)}"

    def atualizar(
        self,
        template_id: int,
        nome: str,
        socio: Socio,
        dia_mes: int,
        ativo: bool
    ) -> Tuple[bool, Optional[BoletimTemplate], Optional[str]]:
        """
        Atualiza um template de boletim

        Args:
            template_id: ID do template
            nome, socio, dia_mes, ativo: Dados a atualizar

        Returns:
            Tupla (sucesso, objeto, mensagem_erro)
        """
        try:
            template = self.obter_por_id(template_id)
            if not template:
                return False, None, "Template não encontrado"

            # Validações
            if not nome or not nome.strip():
                return False, None, "Nome é obrigatório"

            if dia_mes < 1 or dia_mes > 31:
                return False, None, "Dia do mês deve estar entre 1 e 31"

            # Atualizar
            template.nome = nome.strip()
            template.socio = socio
            template.dia_mes = dia_mes
            template.ativo = ativo
            template.updated_at = datetime.utcnow()

            self.db_session.commit()
            self.db_session.refresh(template)

            return True, template, None

        except Exception as e:
            self.db_session.rollback()
            return False, None, f"Erro ao atualizar template: {str(e)}"

    def eliminar(self, template_id: int) -> Tuple[bool, Optional[str]]:
        """
        Elimina um template de boletim

        Args:
            template_id: ID do template

        Returns:
            Tupla (sucesso, mensagem_erro)
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
            return False, f"Erro ao eliminar template: {str(e)}"

    def gerar_boletins_recorrentes_mes(
        self,
        ano: int,
        mes: int,
        preencher_projetos: bool = False
    ) -> Tuple[int, List[str]]:
        """
        Gera boletins recorrentes para um mês específico baseado em templates ativos

        Args:
            ano: Ano (ex: 2025)
            mes: Mês (1-12)
            preencher_projetos: Se deve pré-preencher com projetos do sócio (nice-to-have)

        Returns:
            Tuple (quantidade_gerada, lista_de_erros)
        """
        from logic.valores_referencia import ValoresReferenciaManager
        from logic.boletins import BoletinsManager

        templates = self.listar_ativos()
        gerados = 0
        erros = []

        valores_manager = ValoresReferenciaManager(self.db_session)
        boletins_manager = BoletinsManager(self.db_session)

        # Obter valores de referência do ano
        val_nacional, val_estrangeiro, val_km = valores_manager.obter_ou_default(ano)

        for template in templates:
            try:
                # Verificar se já existe boletim para este template neste mês
                ja_existe = self.db_session.query(Boletim).filter(
                    and_(
                        Boletim.socio == template.socio,
                        Boletim.mes == mes,
                        Boletim.ano == ano
                    )
                ).first()

                if ja_existe:
                    erros.append(f"{template.nome}: Já existe boletim para {mes}/{ano}")
                    continue

                # Criar boletim com cabeçalho
                numero = boletins_manager.gerar_proximo_numero()

                novo_boletim = Boletim(
                    numero=numero,
                    socio=template.socio,
                    mes=mes,
                    ano=ano,
                    data_emissao=date.today(),
                    val_dia_nacional=val_nacional,
                    val_dia_estrangeiro=val_estrangeiro,
                    val_km=val_km,
                    total_ajudas_nacionais=Decimal('0'),
                    total_ajudas_estrangeiro=Decimal('0'),
                    total_kms=Decimal('0'),
                    valor_total=Decimal('0'),
                    valor=Decimal('0'),
                    estado=EstadoBoletim.PENDENTE,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )

                self.db_session.add(novo_boletim)
                self.db_session.flush()  # Get ID

                # Nice-to-have: Pré-preencher com projetos do sócio
                if preencher_projetos:
                    projetos = self._obter_projetos_socio_mes(template.socio, mes, ano)
                    for i, projeto in enumerate(projetos, 1):
                        linha = BoletimLinha(
                            boletim_id=novo_boletim.id,
                            ordem=i,
                            projeto_id=projeto.id,
                            servico=f"{projeto.numero} - {projeto.descricao}",
                            localidade="",  # Usuário preenche
                            tipo=TipoDeslocacao.NACIONAL,  # Default
                            dias=Decimal('0'),  # Usuário preenche
                            kms=0,  # Usuário preenche
                            created_at=datetime.utcnow(),
                            updated_at=datetime.utcnow()
                        )
                        self.db_session.add(linha)

                self.db_session.commit()
                gerados += 1

            except Exception as e:
                self.db_session.rollback()
                erros.append(f"{template.nome}: {str(e)}")

        return gerados, erros

    def _obter_projetos_socio_mes(self, socio: Socio, mes: int, ano: int) -> List[Projeto]:
        """
        Obtém projetos ativos de um sócio num mês específico

        Args:
            socio: Sócio (BRUNO/RAFAEL)
            mes: Mês (1-12)
            ano: Ano (ex: 2025)

        Returns:
            Lista de projetos
        """
        # Critério: Projetos com data_inicio no mês OU em progresso
        primeiro_dia = date(ano, mes, 1)

        if mes == 12:
            ultimo_dia = date(ano + 1, 1, 1)
        else:
            ultimo_dia = date(ano, mes + 1, 1)

        # Projetos que começaram neste mês ou estão em progresso
        return self.db_session.query(Projeto).filter(
            and_(
                # Filtrar por sócio responsável (se existir esse campo)
                # Projeto.socio_responsavel == socio,  # Comentado: verificar se campo existe
                # OU projetos ativos
                Projeto.estado.in_([EstadoProjeto.ATIVO, EstadoProjeto.EM_PROGRESSO]),
                # Que começaram neste mês
                and_(
                    Projeto.data_inicio >= primeiro_dia,
                    Projeto.data_inicio < ultimo_dia
                )
            )
        ).limit(10).all()  # Limitar a 10 para não sobrecarregar
