# -*- coding: utf-8 -*-
"""
Modelos para Equipamento - Gestão de equipamento da empresa
"""
from django.db import models
from django.utils.translation import gettext_lazy as _


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


class Equipamento(models.Model):
    """
    Modelo para gestão de equipamento da empresa

    Funcionalidades:
    - Controlo de inventário
    - Gestão de aluguer (preço por dia)
    - Amortização (X alugueres para amortizar)
    - Uso pessoal vs empresa
    - Rendimento acumulado de alugueres
    """
    numero = models.CharField(_('Número'), max_length=20, unique=True, db_index=True)  # Ex: #EQ0001

    # Identificação do produto
    produto = models.CharField(_('Produto'), max_length=255)  # Ex: "Sony A7S III"
    tipo = models.CharField(_('Tipo'), max_length=100, blank=True, null=True)  # Ex: "Câmara", "Microfone"
    label = models.CharField(_('Label'), max_length=100, blank=True, null=True)  # Label para identificação rápida
    descricao = models.TextField(_('Descrição'), blank=True, null=True)

    # Identificação técnica
    numero_serie = models.CharField(_('Número de Série'), max_length=100, blank=True, null=True)
    mac_address = models.CharField(_('MAC Address'), max_length=50, blank=True, null=True)
    referencia = models.CharField(_('Referência'), max_length=100, blank=True, null=True)

    # Quantidade e tamanho
    quantidade = models.IntegerField(_('Quantidade'), default=1)
    tamanho = models.CharField(_('Tamanho'), max_length=100, blank=True, null=True)  # Ex: "Full Frame", "35mm"

    # Compra
    data_compra = models.DateField(_('Data de Compra'), blank=True, null=True)
    valor_compra = models.DecimalField(_('Valor de Compra'), max_digits=10, decimal_places=2, default=0)
    fornecedor = models.CharField(_('Fornecedor'), max_length=255, blank=True, null=True)
    fatura_url = models.TextField(_('URL da Fatura'), blank=True, null=True)

    # Aluguer e amortização
    preco_aluguer = models.DecimalField(_('Preço Aluguer/Dia'), max_digits=10, decimal_places=2, default=0)
    amortizacao_vezes = models.IntegerField(_('Amortização (nº alugueres)'), default=0, help_text='Número de alugueres necessários para amortizar o equipamento')
    rendimento_acumulado = models.DecimalField(_('Rendimento Acumulado'), max_digits=10, decimal_places=2, default=0, help_text='Total ganho com alugueres deste equipamento')

    # Estado e localização
    estado = models.CharField(
        _('Estado'),
        max_length=50,
        choices=EstadoEquipamento.choices,
        default=EstadoEquipamento.ATIVO
    )
    localizacao = models.CharField(_('Localização'), max_length=255, blank=True, null=True)
    foto_url = models.TextField(_('URL da Foto'), blank=True, null=True)

    # Uso pessoal
    uso_pessoal = models.CharField(
        _('Uso Pessoal'),
        max_length=50,
        choices=UsoEquipamento.choices,
        default=UsoEquipamento.EMPRESA,
        help_text='Indica se o equipamento é de uso pessoal de algum sócio'
    )

    # Metadata
    nota = models.TextField(_('Nota'), blank=True, null=True)
    created_at = models.DateTimeField(_('Criado em'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Atualizado em'), auto_now=True)

    class Meta:
        verbose_name = _('Equipamento')
        verbose_name_plural = _('Equipamento')
        ordering = ['-created_at']
        db_table = 'equipamento'

    def __str__(self):
        return f"{self.numero} - {self.produto}"

    @property
    def percentagem_amortizacao(self):
        """Calcula percentagem de amortização baseado nos alugueres"""
        if self.amortizacao_vezes == 0 or self.preco_aluguer == 0:
            return 0
        alugueres_realizados = self.rendimento_acumulado / self.preco_aluguer if self.preco_aluguer > 0 else 0
        return min(100, (alugueres_realizados / self.amortizacao_vezes) * 100)

    @property
    def valor_amortizado(self):
        """Valor já amortizado"""
        return min(self.valor_compra, self.rendimento_acumulado)

    @property
    def valor_por_amortizar(self):
        """Valor ainda por amortizar"""
        return max(0, self.valor_compra - self.rendimento_acumulado)
