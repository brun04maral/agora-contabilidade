# -*- coding: utf-8 -*-
"""
Modelos para Orçamentos - Sistema complexo de orçamentação de projetos
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from .models import Cliente, Projeto, Fornecedor
from .models_equipamento import Equipamento


class StatusOrcamento(models.TextChoices):
    """Enum para status do orçamento"""
    RASCUNHO = 'RASCUNHO', _('Rascunho')
    ENVIADO = 'ENVIADO', _('Enviado')
    APROVADO = 'APROVADO', _('Aprovado')
    RECUSADO = 'RECUSADO', _('Recusado')
    CANCELADO = 'CANCELADO', _('Cancelado')


class Orcamento(models.Model):
    """
    Orçamento/Proposta para cliente

    Sistema hierárquico:
    - Orçamento (este modelo)
      - Secções (OrcamentoSecao) - podem ser hierárquicas (parent_id)
        - Itens (OrcamentoItem) - linha individual
      - Repartições (OrcamentoReparticao) - divisão de custos internos
    """
    codigo = models.CharField(_('Código'), max_length=100, unique=True, db_index=True)  # Ex: "ORC-2025-001"

    # Cliente
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orcamentos',
        verbose_name=_('Cliente')
    )

    # Projeto associado (se aprovado e convertido)
    projeto = models.ForeignKey(
        Projeto,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orcamentos',
        verbose_name=_('Projeto'),
        help_text='Projeto criado quando orçamento aprovado'
    )

    # Owner
    owner = models.CharField(_('Owner'), max_length=2, default='BA')  # 'BA' ou 'RR'

    # Datas e local
    data_criacao = models.DateField(_('Data de Criação'))
    data_evento = models.CharField(_('Data do Evento'), max_length=200, blank=True, null=True)
    local_evento = models.CharField(_('Local do Evento'), max_length=200, blank=True, null=True)

    # Descrição (versão interna)
    descricao_proposta = models.TextField(_('Descrição da Proposta'), blank=True, null=True)

    # Valores
    valor_total = models.DecimalField(_('Valor Total'), max_digits=10, decimal_places=2, default=0)
    total_parcial_1 = models.DecimalField(_('Total Parcial 1'), max_digits=10, decimal_places=2, default=0, blank=True, null=True)
    total_parcial_2 = models.DecimalField(_('Total Parcial 2'), max_digits=10, decimal_places=2, default=0, blank=True, null=True)

    # Notas contratuais
    notas_contratuais = models.TextField(_('Notas Contratuais'), blank=True, null=True)

    # Status
    status = models.CharField(
        _('Status'),
        max_length=20,
        choices=StatusOrcamento.choices,
        default=StatusOrcamento.RASCUNHO
    )

    # Versão para cliente (simplificada)
    tem_versao_cliente = models.BooleanField(_('Tem Versão Cliente'), default=False)
    titulo_cliente = models.CharField(_('Título para Cliente'), max_length=255, blank=True, null=True)
    descricao_cliente = models.TextField(_('Descrição para Cliente'), blank=True, null=True)

    # Metadata
    created_at = models.DateTimeField(_('Criado em'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Atualizado em'), auto_now=True)

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
    """
    Secção do orçamento (pode ser hierárquica)

    Exemplo:
    - Produção (parent=None)
      - Câmaras (parent=Produção)
      - Áudio (parent=Produção)
    - Pós-Produção (parent=None)
      - Edição (parent=Pós-Produção)
    """
    orcamento = models.ForeignKey(
        Orcamento,
        on_delete=models.CASCADE,
        related_name='secoes',
        verbose_name=_('Orçamento')
    )

    tipo = models.CharField(
        _('Tipo'),
        max_length=50,
        choices=TipoSecao.choices,
        default=TipoSecao.SERVICO
    )

    nome = models.CharField(_('Nome'), max_length=100)
    ordem = models.IntegerField(_('Ordem'))

    # Hierarquia (para sub-secções)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='subsecoes',
        verbose_name=_('Secção Pai')
    )

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
    """
    Item individual de uma secção do orçamento

    Suporta vários tipos de cálculo:
    - Serviço: quantidade × dias × preço_unitario
    - Equipamento: quantidade × dias × preço_unitario
    - Deslocação: kms × valor_por_km
    - Refeição: num_refeicoes × valor_por_refeicao
    - Fixo: valor_fixo
    """
    orcamento = models.ForeignKey(
        Orcamento,
        on_delete=models.CASCADE,
        related_name='itens',
        verbose_name=_('Orçamento')
    )

    secao = models.ForeignKey(
        OrcamentoSecao,
        on_delete=models.CASCADE,
        related_name='itens',
        verbose_name=_('Secção')
    )

    tipo = models.CharField(
        _('Tipo'),
        max_length=20,
        choices=TipoItem.choices,
        default=TipoItem.SERVICO
    )

    descricao = models.TextField(_('Descrição'))
    ordem = models.IntegerField(_('Ordem'))

    # Equipamento associado (se aplicável)
    equipamento = models.ForeignKey(
        Equipamento,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orcamento_itens',
        verbose_name=_('Equipamento')
    )

    # Cálculo padrão (serviço/equipamento)
    quantidade = models.IntegerField(_('Quantidade'), default=1)
    dias = models.IntegerField(_('Dias'), default=1)
    preco_unitario = models.DecimalField(_('Preço Unitário'), max_digits=10, decimal_places=2, default=0)
    desconto = models.DecimalField(_('Desconto'), max_digits=5, decimal_places=4, default=0, help_text='Ex: 0.10 para 10%')

    # Deslocação
    kms = models.DecimalField(_('KMs'), max_digits=10, decimal_places=2, default=0)
    valor_por_km = models.DecimalField(_('Valor por KM'), max_digits=10, decimal_places=2, default=0)

    # Refeições
    num_refeicoes = models.IntegerField(_('Número de Refeições'), default=0)
    valor_por_refeicao = models.DecimalField(_('Valor por Refeição'), max_digits=10, decimal_places=2, default=0)

    # Valor fixo
    valor_fixo = models.DecimalField(_('Valor Fixo'), max_digits=10, decimal_places=2, default=0)

    # Total calculado
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
    """
    Repartição interna de custos do orçamento

    Usado para calcular:
    - Quanto vai para fornecedores
    - Quanto vai para freelancers
    - Quanto é margem da empresa
    - Custos de equipamento interno
    """
    orcamento = models.ForeignKey(
        Orcamento,
        on_delete=models.CASCADE,
        related_name='reparticoes',
        verbose_name=_('Orçamento')
    )

    tipo = models.CharField(
        _('Tipo'),
        max_length=20,
        choices=TipoReparticao.choices,
        blank=True,
        null=True
    )

    # Entidades
    entidade = models.CharField(_('Entidade'), max_length=50, blank=True, null=True)
    fornecedor = models.ForeignKey(
        Fornecedor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orcamento_reparticoes',
        verbose_name=_('Fornecedor')
    )
    equipamento = models.ForeignKey(
        Equipamento,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orcamento_reparticoes',
        verbose_name=_('Equipamento')
    )
    beneficiario = models.CharField(_('Beneficiário'), max_length=50, blank=True, null=True)

    # Valores
    valor = models.DecimalField(_('Valor'), max_digits=10, decimal_places=2, default=0)
    percentagem = models.DecimalField(_('Percentagem'), max_digits=5, decimal_places=2, default=0)
    ordem = models.IntegerField(_('Ordem'))

    # Cálculo detalhado
    descricao = models.TextField(_('Descrição'), blank=True, null=True)
    quantidade = models.IntegerField(_('Quantidade'), default=0)
    dias = models.IntegerField(_('Dias'), default=0)
    valor_unitario = models.DecimalField(_('Valor Unitário'), max_digits=10, decimal_places=2, default=0)
    base_calculo = models.DecimalField(_('Base de Cálculo'), max_digits=10, decimal_places=2, default=0)

    # Deslocação/Refeições (mesmo sistema dos itens)
    kms = models.DecimalField(_('KMs'), max_digits=10, decimal_places=2, default=0)
    valor_por_km = models.DecimalField(_('Valor por KM'), max_digits=10, decimal_places=2, default=0)
    num_refeicoes = models.IntegerField(_('Número de Refeições'), default=0)
    valor_por_refeicao = models.DecimalField(_('Valor por Refeição'), max_digits=10, decimal_places=2, default=0)
    valor_fixo = models.DecimalField(_('Valor Fixo'), max_digits=10, decimal_places=2, default=0)

    # Relação com item do cliente
    item_cliente_id = models.IntegerField(_('ID Item Cliente'), blank=True, null=True)

    # Total
    total = models.DecimalField(_('Total'), max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = _('Repartição de Orçamento')
        verbose_name_plural = _('Repartições de Orçamento')
        ordering = ['orcamento', 'ordem']
        db_table = 'orcamento_reparticoes'

    def __str__(self):
        return f"{self.orcamento.codigo} - {self.entidade or self.beneficiario}"
