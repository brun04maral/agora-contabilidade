# -*- coding: utf-8 -*-
"""
Modelo não-gerenciado para visualizar Saldos no admin Django

Este modelo não cria tabela na BD - serve apenas para mostrar
dados calculados dinamicamente pelo SaldosCalculator no admin.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _


class Saldo(models.Model):
    """
    Modelo não-gerenciado (unmanaged) para visualizar saldos no admin.
    Os dados são calculados dinamicamente pelo SaldosCalculator.
    """
    socio = models.CharField(_('Sócio'), max_length=2, primary_key=True)  # 'BA' ou 'RR'
    nome = models.CharField(_('Nome'), max_length=50)

    # INs (entradas)
    projetos_pessoais = models.DecimalField(_('Projetos Pessoais'), max_digits=10, decimal_places=2, default=0)
    premios = models.DecimalField(_('Prémios'), max_digits=10, decimal_places=2, default=0)
    investimento_inicial = models.DecimalField(_('Investimento Inicial'), max_digits=10, decimal_places=2, default=0)
    total_ins = models.DecimalField(_('Total INs'), max_digits=10, decimal_places=2, default=0)

    # OUTs (saídas)
    despesas_fixas = models.DecimalField(_('Despesas Fixas ÷2'), max_digits=10, decimal_places=2, default=0)
    despesas_pessoais = models.DecimalField(_('Despesas Pessoais'), max_digits=10, decimal_places=2, default=0)
    boletins = models.DecimalField(_('Boletins'), max_digits=10, decimal_places=2, default=0)
    total_outs = models.DecimalField(_('Total OUTs'), max_digits=10, decimal_places=2, default=0)

    # Saldo final
    saldo_final = models.DecimalField(_('Saldo Final'), max_digits=10, decimal_places=2, default=0)

    class Meta:
        managed = False  # Não cria tabela na BD
        verbose_name = _('Saldo')
        verbose_name_plural = _('Saldos')
        db_table = 'saldos_view'  # Nome fictício

    def __str__(self):
        return f"Saldo {self.nome}: €{self.saldo_final}"
