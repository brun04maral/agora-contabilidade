# -*- coding: utf-8 -*-
"""
Admin customizado para visualização de Saldos calculados dinamicamente
"""
from django.contrib import admin
from django.urls import path
from django.shortcuts import render
from django.utils.html import format_html
from unfold.admin import ModelAdmin
from .models_saldo import Saldo
from .utils.saldos import SaldosCalculator


class SaldoAdmin(ModelAdmin):
    """
    Admin customizado para visualizar Saldos calculados dinamicamente.
    Usa o SaldosCalculator para obter dados em tempo real.
    """

    list_display = ['socio', 'nome', 'total_ins_display', 'total_outs_display', 'saldo_final_display']

    # Desabilita ações de edição/criação/exclusão
    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        """Override para mostrar saldos calculados"""
        calculator = SaldosCalculator()

        # Calcula saldos de Bruno
        saldo_bruno = calculator.calcular_saldo_bruno(incluir_investimento=True)
        bruno = Saldo(
            socio='BA',
            nome='Bruno Amaral',
            projetos_pessoais=saldo_bruno['projetos_pessoais'],
            premios=saldo_bruno['premios'],
            investimento_inicial=saldo_bruno['investimento_inicial'],
            total_ins=saldo_bruno['total_ins'],
            despesas_fixas=saldo_bruno['despesas_fixas'],
            despesas_pessoais=saldo_bruno['despesas_pessoais'],
            boletins=saldo_bruno['boletins'],
            total_outs=saldo_bruno['total_outs'],
            saldo_final=saldo_bruno['saldo_final'],
        )

        # Calcula saldos de Rafael
        saldo_rafael = calculator.calcular_saldo_rafael(incluir_investimento=True)
        rafael = Saldo(
            socio='RR',
            nome='Rafael Reigota',
            projetos_pessoais=saldo_rafael['projetos_pessoais'],
            premios=saldo_rafael['premios'],
            investimento_inicial=saldo_rafael['investimento_inicial'],
            total_ins=saldo_rafael['total_ins'],
            despesas_fixas=saldo_rafael['despesas_fixas'],
            despesas_pessoais=saldo_rafael['despesas_pessoais'],
            boletins=saldo_rafael['boletins'],
            total_outs=saldo_rafael['total_outs'],
            saldo_final=saldo_rafael['saldo_final'],
        )

        # Mock queryset com os 2 saldos
        class MockQuerySet:
            def __iter__(self):
                return iter([bruno, rafael])

            def __len__(self):
                return 2

            def count(self):
                return 2

        extra_context = extra_context or {}
        extra_context['cl'] = type('obj', (object,), {
            'result_list': MockQuerySet(),
            'result_count': 2,
        })()

        return super().changelist_view(request, extra_context=extra_context)

    @admin.display(description='Total INs')
    def total_ins_display(self, obj):
        return format_html('<strong style="color: green;">€{:.2f}</strong>', obj.total_ins)

    @admin.display(description='Total OUTs')
    def total_outs_display(self, obj):
        return format_html('<strong style="color: red;">€{:.2f}</strong>', obj.total_outs)

    @admin.display(description='Saldo Final')
    def saldo_final_display(self, obj):
        color = 'green' if obj.saldo_final >= 0 else 'red'
        return format_html('<strong style="color: {}; font-size: 1.2em;">€{:.2f}</strong>', color, obj.saldo_final)


# Regista o admin
admin.site.register(Saldo, SaldoAdmin)
