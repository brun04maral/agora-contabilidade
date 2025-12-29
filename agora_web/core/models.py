# -*- coding: utf-8 -*-
"""
Core models for Agora Contabilidade - Migrated from SQLAlchemy to Django ORM
"""
from django.db import models
from django.utils.translation import gettext_lazy as _


class Cliente(models.Model):
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
    angariacao = models.CharField(_('Angariação'), max_length=255, blank=True, null=True)  # Como foi angariado
    nota = models.TextField(_('Nota'), blank=True, null=True)
    created_at = models.DateTimeField(_('Criado em'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Atualizado em'), auto_now=True)

    class Meta:
        verbose_name = _('Cliente')
        verbose_name_plural = _('Clientes')
        ordering = ['-created_at']
        db_table = 'clientes'

    def __str__(self):
        return f"{self.numero} - {self.nome}"

    def __repr__(self):
        return f"<Cliente(id={self.id}, numero='{self.numero}', nome='{self.nome}')>"


class EstatutoFornecedor(models.TextChoices):
    """Enum para estatuto do fornecedor"""
    EMPRESA = 'EMPRESA', _('Empresa')
    FREELANCER = 'FREELANCER', _('Freelancer')
    ESTADO = 'ESTADO', _('Estado')


class Fornecedor(models.Model):
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
    created_at = models.DateTimeField(_('Criado em'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Atualizado em'), auto_now=True)

    class Meta:
        verbose_name = _('Fornecedor')
        verbose_name_plural = _('Fornecedores')
        ordering = ['-created_at']
        db_table = 'fornecedores'

    def __str__(self):
        return f"{self.numero} - {self.nome}"

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


class Projeto(models.Model):
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
    owner = models.CharField(_('Owner'), max_length=2, default='BA')  # 'BA' ou 'RR' - sócio responsável

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

    # Metadata
    nota = models.TextField(_('Nota'), blank=True, null=True)
    created_at = models.DateTimeField(_('Criado em'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Atualizado em'), auto_now=True)

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


class DespesaTemplate(models.Model):
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

    # Dia do mês para gerar (1-31)
    dia_mes = models.IntegerField(_('Dia do Mês'))  # Dia do mês em que a despesa deve ser gerada

    # Metadata
    nota = models.TextField(_('Nota'), blank=True, null=True)
    created_at = models.DateTimeField(_('Criado em'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Atualizado em'), auto_now=True)

    class Meta:
        verbose_name = _('Template de Despesa')
        verbose_name_plural = _('Templates de Despesa')
        ordering = ['dia_mes', '-created_at']
        db_table = 'despesa_templates'

    def __str__(self):
        return f"{self.numero} - {self.descricao[:30]} (dia {self.dia_mes})"

    def __repr__(self):
        return f"<DespesaTemplate(id={self.id}, numero='{self.numero}', descricao='{self.descricao[:30]}', dia={self.dia_mes})>"


class Despesa(models.Model):
    """
    Modelo para armazenar despesas da empresa

    IMPORTANTE: O campo 'tipo' determina como impacta os saldos pessoais:
    - FIXA_MENSAL: Divide por 2, cada sócio desconta metade
    - PESSOAL_BA/PESSOAL_RR: Desconta apenas do sócio específico
    - EQUIPAMENTO: Pode descontar do saldo se configurado
    - PROJETO: Associada a projeto, não impacta saldos diretamente
    """
    numero = models.CharField(_('Número'), max_length=20, unique=True, db_index=True)  # Ex: #D000001
    tipo = models.CharField(
        _('Tipo'),
        max_length=20,
        choices=TipoDespesa.choices,
        default=TipoDespesa.FIXA_MENSAL,
        db_index=True
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

    class Meta:
        verbose_name = _('Despesa')
        verbose_name_plural = _('Despesas')
        ordering = ['-data', '-created_at']
        db_table = 'despesas'

    def __str__(self):
        return f"{self.numero} - {self.descricao[:30]}"

    def __repr__(self):
        return f"<Despesa(id={self.id}, numero='{self.numero}', tipo='{self.tipo}', valor={self.valor_sem_iva})>"


class Socio(models.TextChoices):
    """Enum para identificar o sócio"""
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


class Boletim(models.Model):
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
    socio = models.CharField(
        _('Sócio'),
        max_length=2,
        choices=Socio.choices,
        db_index=True
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
