# -*- coding: utf-8 -*-
"""
Core models for Agora Contabilidade - Migrated from SQLAlchemy to Django ORM

Empresa: Amaral & Reigota - Produção Audiovisual, Lda (NIPC: 518 351 190)
Marca: Agora Media Production
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from simple_history.models import HistoricalRecords


class UserTrackingMixin(models.Model):
    """
    Mixin que adiciona tracking de user (created_by/updated_by)

    NOTA: Não redefine created_at/updated_at porque esses campos
    já existem nos modelos que usam este mixin.
    """
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_created',
        verbose_name=_('Criado por'),
        editable=False
    )
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_updated',
        verbose_name=_('Modificado por'),
        editable=False
    )

    class Meta:
        abstract = True


class Socio(UserTrackingMixin, models.Model):
    """
    Sócio da Amaral & Reigota - Produção Audiovisual, Lda
    """
    codigo = models.CharField(_('Código'), max_length=2, unique=True, primary_key=True)  # BA, RR
    nome_completo = models.CharField(_('Nome Completo'), max_length=100)
    nome_curto = models.CharField(_('Nome Curto'), max_length=50)  # Bruno, Rafael
    email = models.EmailField(_('Email'))
    telefone = models.CharField(_('Telefone'), max_length=50, blank=True, null=True)
    percentagem_participacao = models.DecimalField(_('% Participação'), max_digits=5, decimal_places=2, default=50.00)
    ativo = models.BooleanField(_('Ativo'), default=True)
    cor_tema = models.CharField(_('Cor Tema'), max_length=7, default='#1976d2', blank=True, null=True)  # Para UI
    created_at = models.DateTimeField(_('Criado em'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Atualizado em'), auto_now=True)

    # Histórico completo de alterações
    history = HistoricalRecords()

    class Meta:
        verbose_name = _('Sócio')
        verbose_name_plural = _('Sócios')
        ordering = ['codigo']
        db_table = 'socios'

    def __str__(self):
        return self.codigo

    def __repr__(self):
        return f"<Socio(codigo='{self.codigo}', nome='{self.nome_curto}')>"

    def get_num_projetos_pessoais(self):
        """Retorna o número de projetos pessoais do sócio"""
        return self.projetos.filter(tipo='PESSOAL').count()

    def get_num_despesas_pessoais(self):
        """Retorna o número de despesas pessoais do sócio (tag PESSOAL)"""
        from core.models import Despesa
        # Despesas com tag PESSOAL que pertencem a este sócio
        # Identificamos pelo credor sendo um fornecedor relacionado ao sócio
        # ou pela descrição contendo o nome do sócio
        return Despesa.objects.filter(tags__codigo='PESSOAL').filter(
            models.Q(credor__nome__icontains=self.nome_curto) |
            models.Q(credor__nome__icontains=self.nome_completo) |
            models.Q(descricao__icontains=self.nome_curto)
        ).distinct().count()

    def get_num_clientes_angariados(self):
        """Retorna o número de clientes angariados pelo sócio"""
        return self.clientes_angariados.count()


class Cliente(UserTrackingMixin, models.Model):
    """
    Modelo para armazenar informações de clientes

    Campos de Nome:
    - nome: Nome curto/informal usado em listagens e referências rápidas (max 120 chars)
    - nome_formal: Nome completo/formal da empresa (ex: "Empresa X, Lda.") usado em documentos oficiais (max 255 chars)
    """
    numero = models.CharField(_('Número'), max_length=20, unique=True, db_index=True)  # Ex: #C0001
    nome = models.CharField(_('Nome'), max_length=120)  # Nome curto para listagens
    nome_formal = models.CharField(_('Nome Formal'), max_length=255)  # Nome completo/formal
    nif = models.CharField(_('NIF'), max_length=20, blank=True, null=True)
    morada = models.TextField(_('Morada'), blank=True, null=True)
    pais = models.CharField(_('País'), max_length=100, default='Portugal', blank=True, null=True)
    contacto = models.CharField(_('Contacto'), max_length=50, blank=True, null=True)
    email = models.EmailField(_('Email'), max_length=255, blank=True, null=True)

    # Angariador: Sócio que angariou o cliente
    angariador = models.ForeignKey(
        Socio,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='clientes_angariados',
        verbose_name=_('Angariador'),
        help_text=_('Sócio responsável pela angariação deste cliente')
    )

    # DEPRECATED: Campo antigo mantido temporariamente
    angariacao = models.CharField(
        _('Angariação (antigo)'),
        max_length=255,
        blank=True,
        null=True,
        help_text=_('Campo deprecated - usar campo "angariador"')
    )

    nota = models.TextField(_('Nota'), blank=True, null=True)
    created_at = models.DateTimeField(_('Criado em'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Atualizado em'), auto_now=True)

    # Histórico completo de alterações
    history = HistoricalRecords()

    class Meta:
        verbose_name = _('Cliente')
        verbose_name_plural = _('Clientes')
        ordering = ['-created_at']
        db_table = 'clientes'

    def __str__(self):
        return self.nome

    def __repr__(self):
        return f"<Cliente(id={self.id}, numero='{self.numero}', nome='{self.nome}')>"


class EstatutoFornecedor(models.TextChoices):
    """Enum para estatuto do fornecedor"""
    EMPRESA = 'EMPRESA', _('Empresa')
    FREELANCER = 'FREELANCER', _('Freelancer')
    ESTADO = 'ESTADO', _('Estado')
    BANCO = 'BANCO', _('Banco')
    SOCIO_GERENTE = 'SOCIO_GERENTE', _('Sócio Gerente')


class Fornecedor(UserTrackingMixin, models.Model):
    """
    Modelo para armazenar informações de fornecedores/credores
    """
    numero = models.CharField(_('Número'), max_length=20, unique=True, db_index=True)  # Ex: #F0001
    nome = models.CharField(_('Nome'), max_length=255)
    estatuto = models.CharField(
        _('Estatuto'),
        max_length=20,
        choices=EstatutoFornecedor.choices,
        default=EstatutoFornecedor.FREELANCER
    )
    area = models.CharField(_('Área'), max_length=255, blank=True, null=True)  # Ex: Produção, Pós-produção
    funcao = models.CharField(_('Função'), max_length=255, blank=True, null=True)  # Ex: Técnico de som, Editor
    classificacao = models.IntegerField(_('Classificação'), blank=True, null=True)  # 1-5 estrelas
    validade_seguro_trabalho = models.DateTimeField(_('Validade Seguro Trabalho'), blank=True, null=True)
    nif = models.CharField(_('NIF'), max_length=20, blank=True, null=True)
    iban = models.CharField(_('IBAN'), max_length=50, blank=True, null=True)
    morada = models.TextField(_('Morada'), blank=True, null=True)
    pais = models.CharField(_('País'), max_length=100, default='Portugal', blank=True, null=True)  # País para IVA
    contacto = models.CharField(_('Contacto'), max_length=50, blank=True, null=True)
    email = models.EmailField(_('Email'), max_length=255, blank=True, null=True)
    website = models.URLField(_('Website'), max_length=255, blank=True, null=True)
    nota = models.TextField(_('Nota'), blank=True, null=True)

    # IRS Retenção na Fonte (para freelancers)
    taxa_retencao_irs = models.DecimalField(
        _('Taxa Retenção IRS'),
        max_digits=5,
        decimal_places=2,
        default=23.00,
        blank=True,
        null=True,
        help_text=_('Taxa de retenção aplicável (23%, 25%, 16.5%, etc). Apenas para FREELANCER')
    )
    created_at = models.DateTimeField(_('Criado em'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Atualizado em'), auto_now=True)

    # Histórico completo de alterações
    history = HistoricalRecords()

    class Meta:
        verbose_name = _('Fornecedor')
        verbose_name_plural = _('Fornecedores')
        ordering = ['-created_at']
        db_table = 'fornecedores'

    def __str__(self):
        return self.nome

    def __repr__(self):
        return f"<Fornecedor(id={self.id}, numero='{self.numero}', nome='{self.nome}')>"


class TipoProjeto(models.TextChoices):
    """Enum para tipo de projeto - CRÍTICO para cálculo de saldos!"""
    EMPRESA = 'EMPRESA', _('Empresa')  # Projeto da empresa (não entra nos INs pessoais, só prémios)
    PESSOAL = 'PESSOAL', _('Pessoal')  # Projeto freelance do sócio (owner) faturado pela empresa


class EstadoProjeto(models.TextChoices):
    """Enum para estado do projeto"""
    ATIVO = 'ATIVO', _('Ativo')  # Projeto em curso
    FINALIZADO = 'FINALIZADO', _('Finalizado')  # Trabalho concluído, aguarda pagamento
    PAGO = 'PAGO', _('Pago')  # Cliente pagou
    ANULADO = 'ANULADO', _('Anulado')  # Projeto cancelado


class Projeto(UserTrackingMixin, models.Model):
    """
    Modelo para armazenar projetos da Agora Media

    IMPORTANTE: O campo 'tipo' + 'owner' determina se o valor entra nos saldos pessoais:
    - EMPRESA: Apenas prémios entram nos saldos (owner indica quem angariou)
    - PESSOAL: Valor total entra nos INs do owner (BA ou RR)
    """
    numero = models.CharField(_('Número'), max_length=20, unique=True, db_index=True)  # Ex: #P0001
    tipo = models.CharField(
        _('Tipo'),
        max_length=20,
        choices=TipoProjeto.choices,
        default=TipoProjeto.EMPRESA,
        db_index=True
    )
    owner = models.CharField(_('Owner'), max_length=2, default='BA')  # 'BA' ou 'RR' - sócio responsável (DEPRECATED)
    socio = models.ForeignKey(
        Socio,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='projetos',
        verbose_name=_('Sócio Responsável')
    )

    # Cliente
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='projetos',
        verbose_name=_('Cliente')
    )

    # Datas
    data_inicio = models.DateField(_('Data Início'), blank=True, null=True)
    data_fim = models.DateField(_('Data Fim'), blank=True, null=True)

    # Descrição
    descricao = models.TextField(_('Descrição'))

    # Valores
    valor_sem_iva = models.DecimalField(_('Valor sem IVA'), max_digits=10, decimal_places=2, default=0)

    # Faturação
    data_faturacao = models.DateField(_('Data Faturação'), blank=True, null=True)
    data_vencimento = models.DateField(_('Data Vencimento'), blank=True, null=True)
    estado = models.CharField(
        _('Estado'),
        max_length=20,
        choices=EstadoProjeto.choices,
        default=EstadoProjeto.ATIVO,
        db_index=True
    )

    # Prémios (cachets + comissões) - para projetos da EMPRESA
    premio_bruno = models.DecimalField(_('Prémio Bruno'), max_digits=10, decimal_places=2, default=0, blank=True, null=True)
    premio_rafael = models.DecimalField(_('Prémio Rafael'), max_digits=10, decimal_places=2, default=0, blank=True, null=True)

    # Campos adicionais (importados da Google Sheet)
    data_recibo = models.DateField(
        _('Data Recibo'),
        blank=True,
        null=True,
        help_text='Data em que o cliente pagou o projeto'
    )
    orcamento_url = models.URLField(
        _('Link Orçamento'),
        max_length=500,
        blank=True,
        null=True,
        help_text='Link para o orçamento relacionado'
    )
    equipa = models.IntegerField(
        _('Tamanho Equipa'),
        blank=True,
        null=True,
        help_text='Número de pessoas na equipa do projeto'
    )
    recursos_humanos = models.TextField(
        _('Recursos Humanos'),
        blank=True,
        null=True,
        help_text='Nomes das pessoas que trabalharam no projeto'
    )
    equipamento_usado = models.TextField(
        _('Equipamento Usado'),
        blank=True,
        null=True,
        help_text='Equipamento utilizado no projeto'
    )
    local = models.CharField(
        _('Local'),
        max_length=200,
        blank=True,
        null=True,
        help_text='Local onde o projeto foi realizado'
    )

    # Metadata
    nota = models.TextField(_('Nota'), blank=True, null=True)
    created_at = models.DateTimeField(_('Criado em'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Atualizado em'), auto_now=True)

    # Histórico completo de alterações
    history = HistoricalRecords()

    class Meta:
        verbose_name = _('Projeto')
        verbose_name_plural = _('Projetos')
        ordering = ['-created_at']
        db_table = 'projetos'

    def __str__(self):
        return f"{self.numero} - {self.descricao[:50]}"

    def __repr__(self):
        return f"<Projeto(id={self.id}, numero='{self.numero}', tipo='{self.tipo}', valor={self.valor_sem_iva})>"


class TipoDespesa(models.TextChoices):
    """
    Enum para tipo de despesa - CRÍTICO para cálculo de saldos!

    FIXA_MENSAL: Dividida por 2, cada sócio desconta metade nos OUTs
    PESSOAL_BA/PESSOAL_RR: Desconta apenas do sócio específico
    EQUIPAMENTO: Pode descontar do saldo se for para uso pessoal
    """
    FIXA_MENSAL = 'FIXA_MENSAL', _('Fixa Mensal')
    PESSOAL_BA = 'PESSOAL_BA', _('Pessoal BA')
    PESSOAL_RR = 'PESSOAL_RR', _('Pessoal RR')
    EQUIPAMENTO = 'EQUIPAMENTO', _('Equipamento')
    PROJETO = 'PROJETO', _('Projeto')  # Despesa associada a um projeto específico


class EstadoDespesa(models.TextChoices):
    """Enum para estado da despesa"""
    PENDENTE = 'PENDENTE', _('Pendente')
    VENCIDO = 'VENCIDO', _('Vencido')
    PAGO = 'PAGO', _('Pago')


class TagDespesa(models.Model):
    """
    Tag para categorização de despesas (sistema de tags compostas)

    As despesas na Google Sheet têm tipos compostos (ex: "Equipamento, Pessoal").
    Este modelo permite associar múltiplas tags a uma despesa via ManyToMany.

    Campos:
    - codigo: Identificador único (PK) - ex: "EQUIPAMENTO", "PESSOAL"
    - nome: Nome apresentável - ex: "Equipamento", "Pessoal"
    - impacta_saldos: Se True, despesas com esta tag afetam saldos pessoais
    - impacta_irc: Se True, despesas com esta tag são dedutíveis para IRC
    """
    codigo = models.CharField(
        _('Código'),
        max_length=50,
        unique=True,
        primary_key=True,
        help_text='Código único da tag (ex: EQUIPAMENTO, PESSOAL)'
    )
    nome = models.CharField(
        _('Nome'),
        max_length=100,
        help_text='Nome apresentável da tag'
    )
    impacta_saldos = models.BooleanField(
        _('Impacta Saldos Pessoais'),
        default=False,
        help_text='Despesas com esta tag afetam os saldos pessoais dos sócios'
    )
    impacta_irc = models.BooleanField(
        _('Impacta IRC'),
        default=False,
        help_text='Despesas com esta tag são dedutíveis para cálculo de IRC'
    )
    ordem = models.IntegerField(
        _('Ordem'),
        default=0,
        help_text='Ordem de apresentação (menor = primeiro)'
    )

    class Meta:
        verbose_name = _('Tag de Despesa')
        verbose_name_plural = _('Tags de Despesa')
        ordering = ['ordem', 'nome']
        db_table = 'tags_despesa'

    def __str__(self):
        return self.nome

    def __repr__(self):
        return f"<TagDespesa(codigo='{self.codigo}', nome='{self.nome}')>"


class DespesaTemplate(UserTrackingMixin, models.Model):
    """
    Template de despesa recorrente mensal

    Não representa uma despesa real, apenas um template para gerar despesas automáticas.
    Não entra em cálculos financeiros.

    Exemplo: Salário pago dia 27 de cada mês
    """
    numero = models.CharField(_('Número'), max_length=20, unique=True, db_index=True)  # Ex: #TD000001
    tipo = models.CharField(
        _('Tipo'),
        max_length=20,
        choices=TipoDespesa.choices,
        default=TipoDespesa.FIXA_MENSAL,
        db_index=True
    )

    # Credor/Fornecedor
    credor = models.ForeignKey(
        Fornecedor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_('Credor')
    )

    # Projeto associado (opcional)
    projeto = models.ForeignKey(
        Projeto,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_('Projeto')
    )

    # Descrição
    descricao = models.TextField(_('Descrição'))

    # Valores
    valor_sem_iva = models.DecimalField(_('Valor sem IVA'), max_digits=10, decimal_places=2, default=0)
    valor_com_iva = models.DecimalField(_('Valor com IVA'), max_digits=10, decimal_places=2, default=0)

    # IRS Retenção na Fonte
    irs_retido = models.DecimalField(_('IRS Retido'), max_digits=10, decimal_places=2, default=0, blank=True, null=True, help_text=_('Retenção na fonte (normalmente 23% para freelancers)'))
    taxa_retencao_irs = models.DecimalField(_('Taxa Retenção IRS'), max_digits=5, decimal_places=2, default=0, blank=True, null=True, help_text=_('Taxa aplicada (23%, 25%, 16.5%, etc)'))

    # Dia do mês para gerar (1-31)
    dia_mes = models.IntegerField(_('Dia do Mês'))  # Dia do mês em que a despesa deve ser gerada

    # Metadata
    nota = models.TextField(_('Nota'), blank=True, null=True)
    created_at = models.DateTimeField(_('Criado em'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Atualizado em'), auto_now=True)

    # Histórico completo de alterações
    history = HistoricalRecords()

    class Meta:
        verbose_name = _('Template de Despesa')
        verbose_name_plural = _('Templates de Despesa')
        ordering = ['dia_mes', '-created_at']
        db_table = 'despesa_templates'

    def __str__(self):
        return f"{self.numero} - {self.descricao[:30]} (dia {self.dia_mes})"

    def __repr__(self):
        return f"<DespesaTemplate(id={self.id}, numero='{self.numero}', descricao='{self.descricao[:30]}', dia={self.dia_mes})>"


class Despesa(UserTrackingMixin, models.Model):
    """
    Modelo para armazenar despesas da empresa

    IMPORTANTE: O campo 'tipo' determina como impacta os saldos pessoais:
    - FIXA_MENSAL: Divide por 2, cada sócio desconta metade
    - PESSOAL_BA/PESSOAL_RR: Desconta apenas do sócio específico
    - EQUIPAMENTO: Pode descontar do saldo se configurado
    - PROJETO: Associada a projeto, não impacta saldos diretamente
    """
    numero = models.CharField(_('Número'), max_length=20, unique=True, db_index=True)  # Ex: #D000001

    # DEPRECATED: Campo antigo mantido por compatibilidade
    tipo = models.CharField(
        _('Tipo (deprecated)'),
        max_length=20,
        choices=TipoDespesa.choices,
        default=TipoDespesa.FIXA_MENSAL,
        db_index=True,
        blank=True,
        null=True,
        help_text='Campo antigo - usar tags em vez disto'
    )

    # Sistema de tags (novo)
    tags = models.ManyToManyField(
        TagDespesa,
        related_name='despesas',
        verbose_name=_('Tags'),
        blank=True,
        help_text='Tags que categorizam esta despesa (ex: Equipamento, Pessoal)'
    )
    tipo_original = models.CharField(
        _('Tipo Original'),
        max_length=200,
        blank=True,
        null=True,
        help_text='Tipo original da Google Sheet (para auditoria)'
    )

    # Data
    data = models.DateField(_('Data'), db_index=True)

    # Credor/Fornecedor
    credor = models.ForeignKey(
        Fornecedor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='despesas',
        verbose_name=_('Credor')
    )

    # Projeto associado (opcional)
    projeto = models.ForeignKey(
        Projeto,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='despesas',
        verbose_name=_('Projeto')
    )

    # Descrição
    descricao = models.TextField(_('Descrição'))

    # Valores
    valor_sem_iva = models.DecimalField(_('Valor sem IVA'), max_digits=10, decimal_places=2, default=0)
    valor_com_iva = models.DecimalField(_('Valor com IVA'), max_digits=10, decimal_places=2, default=0)

    # IRS Retenção na Fonte
    irs_retido = models.DecimalField(_('IRS Retido'), max_digits=10, decimal_places=2, default=0, blank=True, null=True, help_text=_('Retenção na fonte (normalmente 23% para freelancers)'))
    taxa_retencao_irs = models.DecimalField(_('Taxa Retenção IRS'), max_digits=5, decimal_places=2, default=0, blank=True, null=True, help_text=_('Taxa aplicada (23%, 25%, 16.5%, etc)'))

    # Estado
    estado = models.CharField(
        _('Estado'),
        max_length=20,
        choices=EstadoDespesa.choices,
        default=EstadoDespesa.PENDENTE,
        db_index=True
    )
    data_pagamento = models.DateField(_('Data Pagamento'), blank=True, null=True)

    # Metadata
    nota = models.TextField(_('Nota'), blank=True, null=True)

    # Rastreamento de origem (se foi gerada de um template)
    despesa_template = models.ForeignKey(
        DespesaTemplate,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='despesas_geradas',
        verbose_name=_('Template de Origem')
    )
    created_at = models.DateTimeField(_('Criado em'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Atualizado em'), auto_now=True)

    # Histórico completo de alterações
    history = HistoricalRecords()

    class Meta:
        verbose_name = _('Despesa')
        verbose_name_plural = _('Despesas')
        ordering = ['-data', '-created_at']
        db_table = 'despesas'

    def __str__(self):
        return f"{self.numero} - {self.descricao[:30]}"

    def __repr__(self):
        tags_str = ', '.join([t.codigo for t in self.tags.all()]) if self.tags.exists() else 'sem tags'
        return f"<Despesa(id={self.id}, numero='{self.numero}', tags=[{tags_str}], valor={self.valor_sem_iva})>"

    # Helper methods para tags
    def has_tag(self, codigo):
        """Verifica se a despesa tem uma tag específica"""
        return self.tags.filter(codigo=codigo).exists()

    @property
    def is_pessoal(self):
        """Retorna True se a despesa tem tag PESSOAL"""
        return self.has_tag('PESSOAL')

    @property
    def is_fixa_mensal(self):
        """Retorna True se a despesa é fixa mensal (Administrativo, Ordenado, Sub.Alimentação)"""
        return self.has_tag('ADMINISTRATIVO') or \
               self.has_tag('ORDENADO') or \
               self.has_tag('SUB_ALIMENTACAO')

    @property
    def is_premio(self):
        """Retorna True se a despesa é prémio ou comissão"""
        return self.has_tag('PREMIO') or self.has_tag('COMISSAO_VENDA')

    @property
    def impacta_saldos(self):
        """Retorna True se alguma tag da despesa impacta saldos"""
        return self.tags.filter(impacta_saldos=True).exists()

    @property
    def impacta_irc(self):
        """Retorna True se alguma tag da despesa impacta IRC"""
        return self.tags.filter(impacta_irc=True).exists()


class CodigoSocio(models.TextChoices):
    """Enum para código do sócio (deprecated - usar modelo Socio)"""
    BA = 'BA', _('Bruno')
    RR = 'RR', _('Rafael')


class EstadoBoletim(models.TextChoices):
    """Enum para estado do boletim"""
    PENDENTE = 'PENDENTE', _('Pendente')
    PAGO = 'PAGO', _('Pago')


class TipoDeslocacao(models.TextChoices):
    """Enum para tipo de deslocação"""
    NACIONAL = 'NACIONAL', _('Nacional')
    ESTRANGEIRO = 'ESTRANGEIRO', _('Estrangeiro')


class Boletim(UserTrackingMixin, models.Model):
    """
    Modelo para boletins de ajudas de custo (Boletim Itinerário)

    Sistema expandido com suporte para múltiplas linhas de deslocação.
    Cada boletim contém:
    - Cabeçalho: mês/ano, valores de referência do ano, totais calculados
    - Linhas: deslocações individuais (BoletimLinha)

    Totais calculados automaticamente:
    - total_ajudas_nacionais = sum(linha.dias where tipo==NACIONAL) × val_dia_nacional
    - total_ajudas_estrangeiro = sum(linha.dias where tipo==ESTRANGEIRO) × val_dia_estrangeiro
    - total_kms = sum(linha.kms) × val_km
    - valor_total = soma dos 3 totais

    IMPORTANTE: Boletins descontam do saldo quando PAGOS (não quando emitidos).
    """
    numero = models.CharField(_('Número'), max_length=20, unique=True, db_index=True)  # Ex: #B0001
    socio_old = models.CharField(
        _('Sócio (OLD)'),
        max_length=2,
        db_column='socio',
        null=True,
        blank=True,
        editable=False
    )  # DEPRECATED - coluna órfã da migração
    socio_codigo = models.CharField(
        _('Sócio (código)'),
        max_length=2,
        choices=CodigoSocio.choices,
        db_index=True,
        null=True,
        blank=True,
        default='BA'
    )  # DEPRECATED - usar campo 'socio' (FK)
    socio = models.ForeignKey(
        Socio,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='boletins',
        verbose_name=_('Sócio')
    )

    # Período
    mes = models.IntegerField(_('Mês'), blank=True, null=True, db_index=True)  # 1-12
    ano = models.IntegerField(_('Ano'), blank=True, null=True, db_index=True)  # Ex: 2025

    # Datas
    data_emissao = models.DateField(_('Data Emissão'), db_index=True)
    data_pagamento = models.DateField(_('Data Pagamento'), blank=True, null=True)

    # Valores de Referência (copiados do ano vigente)
    val_dia_nacional = models.DecimalField(_('Valor Dia Nacional'), max_digits=10, decimal_places=2, blank=True, null=True)
    val_dia_estrangeiro = models.DecimalField(_('Valor Dia Estrangeiro'), max_digits=10, decimal_places=2, blank=True, null=True)
    val_km = models.DecimalField(_('Valor KM'), max_digits=10, decimal_places=2, blank=True, null=True)

    # Totais Calculados Automaticamente
    total_ajudas_nacionais = models.DecimalField(_('Total Ajudas Nacionais'), max_digits=10, decimal_places=2, default=0)
    total_ajudas_estrangeiro = models.DecimalField(_('Total Ajudas Estrangeiro'), max_digits=10, decimal_places=2, default=0)
    total_kms = models.DecimalField(_('Total KMs'), max_digits=10, decimal_places=2, default=0)
    valor_total = models.DecimalField(_('Valor Total'), max_digits=10, decimal_places=2, default=0)

    # Valor antigo (manter para compatibilidade temporária)
    valor = models.DecimalField(_('Valor (antigo)'), max_digits=10, decimal_places=2, default=0, blank=True, null=True)

    # Descrição (manter para compatibilidade temporária)
    descricao = models.TextField(_('Descrição (antigo)'), blank=True, null=True)

    # Estado
    estado = models.CharField(
        _('Estado'),
        max_length=20,
        choices=EstadoBoletim.choices,
        default=EstadoBoletim.PENDENTE,
        db_index=True
    )

    # Metadata
    nota = models.TextField(_('Nota'), blank=True, null=True)
    created_at = models.DateTimeField(_('Criado em'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Atualizado em'), auto_now=True)

    # Histórico completo de alterações
    history = HistoricalRecords()

    class Meta:
        verbose_name = _('Boletim')
        verbose_name_plural = _('Boletins')
        ordering = ['-data_emissao', '-created_at']
        db_table = 'boletins'

    def __str__(self):
        return f"{self.numero} - {self.socio} - {self.mes}/{self.ano}"

    def __repr__(self):
        return f"<Boletim(id={self.id}, numero='{self.numero}', socio='{self.socio}', valor={self.valor_total}, estado='{self.estado}')>"


class BoletimLinha(models.Model):
    """
    Modelo para linhas de deslocação de um boletim itinerário

    Cada linha representa uma deslocação (viagem/trabalho) realizada,
    com informações sobre local, projeto associado (opcional), datas,
    tipo de ajuda de custo (nacional/estrangeiro) e quilómetros percorridos.

    Campos calculados:
    - Dias: Inserido manualmente pelo usuário (cálculo complexo)
    - Horas: Informativas apenas (não usadas em cálculos)

    Relação com projetos:
    - Opcional: Deslocação pode ou não estar associada a projeto
    - Se projeto apagado: projeto_id = NULL (mantém texto em 'servico')
    """
    boletim = models.ForeignKey(
        Boletim,
        on_delete=models.CASCADE,
        related_name='linhas',
        verbose_name=_('Boletim'),
        db_index=True
    )
    ordem = models.IntegerField(_('Ordem'))  # Ordenação (1, 2, 3...)

    # Relação opcional com projeto
    projeto = models.ForeignKey(
        Projeto,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_('Projeto'),
        db_index=True
    )

    # Informação da deslocação
    servico = models.TextField(_('Serviço'))  # Ex: "vMix Novobanco", "reunião com cliente"
    localidade = models.CharField(_('Localidade'), max_length=100, blank=True, null=True)  # Ex: "Aguieira", "Lisboa"

    # Datas e horas (horas são informativas)
    data_inicio = models.DateField(_('Data Início'), blank=True, null=True)
    hora_inicio = models.TimeField(_('Hora Início'), blank=True, null=True)  # Informativa
    data_fim = models.DateField(_('Data Fim'), blank=True, null=True)
    hora_fim = models.TimeField(_('Hora Fim'), blank=True, null=True)  # Informativa

    # Tipo e valores
    tipo = models.CharField(
        _('Tipo'),
        max_length=20,
        choices=TipoDeslocacao.choices,
        default=TipoDeslocacao.NACIONAL
    )
    dias = models.DecimalField(_('Dias'), max_digits=10, decimal_places=2, default=0)  # Inserido manualmente
    kms = models.IntegerField(_('KMs'), default=0)

    # Metadata
    created_at = models.DateTimeField(_('Criado em'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Atualizado em'), auto_now=True)

    class Meta:
        verbose_name = _('Linha de Boletim')
        verbose_name_plural = _('Linhas de Boletim')
        ordering = ['boletim', 'ordem']
        db_table = 'boletim_linhas'

    def __str__(self):
        return f"Linha {self.ordem} - {self.servico[:30]}"

    def __repr__(self):
        return f"<BoletimLinha(id={self.id}, boletim_id={self.boletim_id}, servico='{self.servico[:30]}', tipo={self.tipo}, dias={self.dias}, kms={self.kms})>"


# ===================================================================
# EQUIPAMENTO
# ===================================================================

class EstadoEquipamento(models.TextChoices):
    """Enum para estado do equipamento"""
    ATIVO = 'ATIVO', _('Ativo')
    AVARIADO = 'AVARIADO', _('Avariado')
    VENDIDO = 'VENDIDO', _('Vendido')
    DESCARTADO = 'DESCARTADO', _('Descartado')


class UsoEquipamento(models.TextChoices):
    """Enum para uso pessoal do equipamento"""
    EMPRESA = 'EMPRESA', _('Empresa')
    BRUNO = 'BRUNO', _('Bruno')
    RAFAEL = 'RAFAEL', _('Rafael')
    PARTILHADO = 'PARTILHADO', _('Partilhado')


class Equipamento(UserTrackingMixin, models.Model):
    """Modelo para gestão de equipamento da empresa"""
    numero = models.CharField(_('Número'), max_length=20, unique=True, db_index=True)
    produto = models.CharField(_('Produto'), max_length=255)
    tipo = models.CharField(_('Tipo'), max_length=100, blank=True, null=True)
    label = models.CharField(_('Label'), max_length=100, blank=True, null=True)
    descricao = models.TextField(_('Descrição'), blank=True, null=True)
    numero_serie = models.CharField(_('Número de Série'), max_length=100, blank=True, null=True)
    mac_address = models.CharField(_('MAC Address'), max_length=50, blank=True, null=True)
    referencia = models.CharField(_('Referência'), max_length=100, blank=True, null=True)
    quantidade = models.IntegerField(_('Quantidade'), default=1)
    tamanho = models.CharField(_('Tamanho'), max_length=100, blank=True, null=True)
    data_compra = models.DateField(_('Data de Compra'), blank=True, null=True)
    valor_compra = models.DecimalField(_('Valor de Compra'), max_digits=10, decimal_places=2, default=0)
    fornecedor = models.CharField(_('Fornecedor'), max_length=255, blank=True, null=True)
    fatura_url = models.TextField(_('URL da Fatura'), blank=True, null=True)
    preco_aluguer = models.DecimalField(_('Preço Aluguer/Dia'), max_digits=10, decimal_places=2, default=0)
    amortizacao_vezes = models.IntegerField(_('Amortização (nº alugueres)'), default=0)
    rendimento_acumulado = models.DecimalField(_('Rendimento Acumulado'), max_digits=10, decimal_places=2, default=0)
    estado = models.CharField(_('Estado'), max_length=50, choices=EstadoEquipamento.choices, default=EstadoEquipamento.ATIVO)
    localizacao = models.CharField(_('Localização'), max_length=255, blank=True, null=True)
    foto_url = models.TextField(_('URL da Foto'), blank=True, null=True)
    uso_pessoal = models.CharField(_('Uso Pessoal'), max_length=50, choices=UsoEquipamento.choices, default=UsoEquipamento.EMPRESA)
    nota = models.TextField(_('Nota'), blank=True, null=True)
    created_at = models.DateTimeField(_('Criado em'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Atualizado em'), auto_now=True)

    # Histórico completo de alterações
    history = HistoricalRecords()

    class Meta:
        verbose_name = _('Equipamento')
        verbose_name_plural = _('Equipamento')
        ordering = ['-created_at']
        db_table = 'equipamento'

    def __str__(self):
        return f"{self.numero} - {self.produto}"


# ===================================================================
# ORÇAMENTOS
# ===================================================================

class StatusOrcamento(models.TextChoices):
    """Enum para status do orçamento"""
    RASCUNHO = 'RASCUNHO', _('Rascunho')
    ENVIADO = 'ENVIADO', _('Enviado')
    APROVADO = 'APROVADO', _('Aprovado')
    RECUSADO = 'RECUSADO', _('Recusado')
    CANCELADO = 'CANCELADO', _('Cancelado')


class Orcamento(UserTrackingMixin, models.Model):
    """Orçamento/Proposta para cliente"""
    codigo = models.CharField(_('Código'), max_length=100, unique=True, db_index=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.SET_NULL, null=True, blank=True, related_name='orcamentos', verbose_name=_('Cliente'))
    projeto = models.ForeignKey(Projeto, on_delete=models.SET_NULL, null=True, blank=True, related_name='orcamentos', verbose_name=_('Projeto'))
    owner = models.CharField(_('Owner'), max_length=2, default='BA')  # DEPRECATED
    socio = models.ForeignKey(
        Socio,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='orcamentos',
        verbose_name=_('Sócio Responsável')
    )
    data_criacao = models.DateField(_('Data de Criação'))
    data_evento = models.CharField(_('Data do Evento'), max_length=200, blank=True, null=True)
    local_evento = models.CharField(_('Local do Evento'), max_length=200, blank=True, null=True)
    descricao_proposta = models.TextField(_('Descrição da Proposta'), blank=True, null=True)
    valor_total = models.DecimalField(_('Valor Total'), max_digits=10, decimal_places=2, default=0)
    total_parcial_1 = models.DecimalField(_('Total Parcial 1'), max_digits=10, decimal_places=2, default=0, blank=True, null=True)
    total_parcial_2 = models.DecimalField(_('Total Parcial 2'), max_digits=10, decimal_places=2, default=0, blank=True, null=True)
    notas_contratuais = models.TextField(_('Notas Contratuais'), blank=True, null=True)
    status = models.CharField(_('Status'), max_length=20, choices=StatusOrcamento.choices, default=StatusOrcamento.RASCUNHO)
    tem_versao_cliente = models.BooleanField(_('Tem Versão Cliente'), default=False)
    titulo_cliente = models.CharField(_('Título para Cliente'), max_length=255, blank=True, null=True)
    descricao_cliente = models.TextField(_('Descrição para Cliente'), blank=True, null=True)
    created_at = models.DateTimeField(_('Criado em'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Atualizado em'), auto_now=True)

    # Histórico completo de alterações
    history = HistoricalRecords()

    class Meta:
        verbose_name = _('Orçamento')
        verbose_name_plural = _('Orçamentos')
        ordering = ['-data_criacao', '-created_at']
        db_table = 'orcamentos'

    def __str__(self):
        return f"{self.codigo} - {self.cliente or 'Sem cliente'}"


class TipoSecao(models.TextChoices):
    """Tipo de secção do orçamento"""
    SERVICO = 'SERVICO', _('Serviço')
    EQUIPAMENTO = 'EQUIPAMENTO', _('Equipamento')
    DESLOCACAO = 'DESLOCACAO', _('Deslocação')
    OUTRO = 'OUTRO', _('Outro')


class OrcamentoSecao(models.Model):
    """Secção do orçamento (pode ser hierárquica)"""
    orcamento = models.ForeignKey(Orcamento, on_delete=models.CASCADE, related_name='secoes', verbose_name=_('Orçamento'))
    tipo = models.CharField(_('Tipo'), max_length=50, choices=TipoSecao.choices, default=TipoSecao.SERVICO)
    nome = models.CharField(_('Nome'), max_length=100)
    ordem = models.IntegerField(_('Ordem'))
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subsecoes', verbose_name=_('Secção Pai'))
    subtotal = models.DecimalField(_('Subtotal'), max_digits=10, decimal_places=2, default=0)

    class Meta:
        verbose_name = _('Secção de Orçamento')
        verbose_name_plural = _('Secções de Orçamento')
        ordering = ['orcamento', 'ordem']
        db_table = 'orcamento_secoes'

    def __str__(self):
        return f"{self.orcamento.codigo} - {self.nome}"


class TipoItem(models.TextChoices):
    """Tipo de item do orçamento"""
    SERVICO = 'SERVICO', _('Serviço')
    EQUIPAMENTO = 'EQUIPAMENTO', _('Equipamento')
    DESLOCACAO = 'DESLOCACAO', _('Deslocação')
    REFEICAO = 'REFEICAO', _('Refeição')
    FIXO = 'FIXO', _('Valor Fixo')


class OrcamentoItem(models.Model):
    """Item individual de uma secção do orçamento"""
    orcamento = models.ForeignKey(Orcamento, on_delete=models.CASCADE, related_name='itens', verbose_name=_('Orçamento'))
    secao = models.ForeignKey(OrcamentoSecao, on_delete=models.CASCADE, related_name='itens', verbose_name=_('Secção'))
    tipo = models.CharField(_('Tipo'), max_length=20, choices=TipoItem.choices, default=TipoItem.SERVICO)
    descricao = models.TextField(_('Descrição'))
    ordem = models.IntegerField(_('Ordem'))
    equipamento = models.ForeignKey(Equipamento, on_delete=models.SET_NULL, null=True, blank=True, related_name='orcamento_itens', verbose_name=_('Equipamento'))
    quantidade = models.IntegerField(_('Quantidade'), default=1)
    dias = models.IntegerField(_('Dias'), default=1)
    preco_unitario = models.DecimalField(_('Preço Unitário'), max_digits=10, decimal_places=2, default=0)
    desconto = models.DecimalField(_('Desconto'), max_digits=5, decimal_places=4, default=0)
    kms = models.DecimalField(_('KMs'), max_digits=10, decimal_places=2, default=0)
    valor_por_km = models.DecimalField(_('Valor por KM'), max_digits=10, decimal_places=2, default=0)
    num_refeicoes = models.IntegerField(_('Número de Refeições'), default=0)
    valor_por_refeicao = models.DecimalField(_('Valor por Refeição'), max_digits=10, decimal_places=2, default=0)
    valor_fixo = models.DecimalField(_('Valor Fixo'), max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(_('Total'), max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = _('Item de Orçamento')
        verbose_name_plural = _('Itens de Orçamento')
        ordering = ['orcamento', 'secao', 'ordem']
        db_table = 'orcamento_itens'

    def __str__(self):
        return f"{self.descricao[:50]}"


class TipoReparticao(models.TextChoices):
    """Tipo de repartição interna"""
    FORNECEDOR = 'FORNECEDOR', _('Fornecedor')
    EQUIPAMENTO = 'EQUIPAMENTO', _('Equipamento')
    FREELANCER = 'FREELANCER', _('Freelancer')
    OUTRO = 'OUTRO', _('Outro')


class OrcamentoReparticao(models.Model):
    """Repartição interna de custos do orçamento"""
    orcamento = models.ForeignKey(Orcamento, on_delete=models.CASCADE, related_name='reparticoes', verbose_name=_('Orçamento'))
    tipo = models.CharField(_('Tipo'), max_length=20, choices=TipoReparticao.choices, blank=True, null=True)
    entidade = models.CharField(_('Entidade'), max_length=50, blank=True, null=True)
    fornecedor = models.ForeignKey(Fornecedor, on_delete=models.SET_NULL, null=True, blank=True, related_name='orcamento_reparticoes', verbose_name=_('Fornecedor'))
    equipamento = models.ForeignKey(Equipamento, on_delete=models.SET_NULL, null=True, blank=True, related_name='orcamento_reparticoes', verbose_name=_('Equipamento'))
    beneficiario = models.CharField(_('Beneficiário'), max_length=50, blank=True, null=True)
    valor = models.DecimalField(_('Valor'), max_digits=10, decimal_places=2, default=0)
    percentagem = models.DecimalField(_('Percentagem'), max_digits=5, decimal_places=2, default=0)
    ordem = models.IntegerField(_('Ordem'))
    descricao = models.TextField(_('Descrição'), blank=True, null=True)
    quantidade = models.IntegerField(_('Quantidade'), default=0)
    dias = models.IntegerField(_('Dias'), default=0)
    valor_unitario = models.DecimalField(_('Valor Unitário'), max_digits=10, decimal_places=2, default=0)
    base_calculo = models.DecimalField(_('Base de Cálculo'), max_digits=10, decimal_places=2, default=0)
    kms = models.DecimalField(_('KMs'), max_digits=10, decimal_places=2, default=0)
    valor_por_km = models.DecimalField(_('Valor por KM'), max_digits=10, decimal_places=2, default=0)
    num_refeicoes = models.IntegerField(_('Número de Refeições'), default=0)
    valor_por_refeicao = models.DecimalField(_('Valor por Refeição'), max_digits=10, decimal_places=2, default=0)
    valor_fixo = models.DecimalField(_('Valor Fixo'), max_digits=10, decimal_places=2, default=0)
    item_cliente_id = models.IntegerField(_('ID Item Cliente'), blank=True, null=True)
    total = models.DecimalField(_('Total'), max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = _('Repartição de Orçamento')
        verbose_name_plural = _('Repartições de Orçamento')
        ordering = ['orcamento', 'ordem']
        db_table = 'orcamento_reparticoes'

    def __str__(self):
        return f"{self.orcamento.codigo} - {self.entidade or self.beneficiario}"





class Saldo(models.Model):
    """
    Proxy model para mostrar Saldos Pessoais no admin
    Não tem tabela na BD - usa SaldosCalculator para calcular dados
    """
    id = models.IntegerField(primary_key=True)  # Dummy field

    class Meta:
        managed = False  # Django não cria tabela
        verbose_name = _('Saldo Pessoal')
        verbose_name_plural = _('Saldos Pessoais')
        db_table = 'saldos_view'  # Tabela fictícia
        default_permissions = ()  # Sem permissões de add/change/delete


class Fiscal(models.Model):
    """
    Proxy model para mostrar Estado Fiscal no admin
    Não tem tabela na BD - usa FiscalCalculator para calcular IVA, IRS, IRC
    """
    id = models.IntegerField(primary_key=True)  # Dummy field

    class Meta:
        managed = False  # Django não cria tabela
        verbose_name = _('Fiscal')
        verbose_name_plural = _('Fiscal')
        db_table = 'fiscal_view'  # Tabela fictícia
        default_permissions = ()  # Sem permissões de add/change/delete


class ImportacaoDados(models.Model):
    """
    Proxy model para sistema de importação de dados via Excel
    Não tem tabela na BD - fornece interface de upload no admin
    """
    id = models.IntegerField(primary_key=True)  # Dummy field

    class Meta:
        managed = False  # Django não cria tabela
        verbose_name = _('Importação de Dados')
        verbose_name_plural = _('Importação de Dados')
        db_table = 'importacao_view'  # Tabela fictícia
        default_permissions = ()  # Sem permissões de add/change/delete
