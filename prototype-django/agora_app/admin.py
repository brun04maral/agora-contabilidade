"""
Django Admin com Unfold Theme
Configuração personalizada para Agora Contabilidade
"""
from django.contrib import admin
from django.db.models import Sum
from django.utils.html import format_html
from unfold.admin import ModelAdmin
from unfold.decorators import display
from .models import Socio, Cliente, Fornecedor, Projeto, Despesa


@admin.register(Socio)
class SocioAdmin(ModelAdmin):
    """Admin para Sócios com cálculo de saldos"""
    list_display = ['nome', 'nome_completo', 'email', 'display_saldo', 'ativo']
    list_filter = ['ativo']
    search_fields = ['nome', 'nome_completo', 'email']
    readonly_fields = ['created_at', 'updated_at', 'display_saldo_detalhado']

    fieldsets = (
        ('Informação Básica', {
            'fields': ('nome', 'nome_completo', 'email', 'telefone', 'ativo')
        }),
        ('Dados Financeiros', {
            'fields': ('nif', 'iban')
        }),
        ('Saldo Atual', {
            'fields': ('display_saldo_detalhado',),
            'classes': ('wide',),
        }),
        ('Metadados', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    @display(description="Saldo", ordering="-nome")
    def display_saldo(self, obj):
        """Mostrar saldo com cor"""
        saldo = obj.calcular_saldo()
        color = 'green' if saldo >= 0 else 'red'
        return format_html(
            '<span style="color: {}; font-weight: bold;">€{:,.2f}</span>',
            color,
            saldo
        )

    @display(description="Breakdown Saldo")
    def display_saldo_detalhado(self, obj):
        """Mostrar breakdown detalhado do saldo"""
        saldo = obj.calcular_saldo()
        color = 'green' if saldo >= 0 else 'red'

        return format_html(
            '<div style="padding: 15px; background: #f8f9fa; border-radius: 5px;">'
            '<h3 style="margin-top: 0;">💰 Saldo: <span style="color: {};">€{:,.2f}</span></h3>'
            '<p><em>Cálculo completo será implementado</em></p>'
            '</div>',
            color,
            saldo
        )


@admin.register(Cliente)
class ClienteAdmin(ModelAdmin):
    """Admin para Clientes"""
    list_display = ['nome', 'nif', 'email', 'telefone', 'ativo', 'total_projetos']
    list_filter = ['ativo']
    search_fields = ['nome', 'nif', 'email']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Informação Básica', {
            'fields': ('nome', 'nif', 'ativo')
        }),
        ('Contactos', {
            'fields': ('email', 'telefone', 'morada')
        }),
        ('Notas', {
            'fields': ('notas',),
            'classes': ('collapse',),
        }),
        ('Metadados', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    @display(description="Projetos", ordering="-nome")
    def total_projetos(self, obj):
        """Mostrar total de projetos do cliente"""
        total = obj.projetos.count()
        return format_html(
            '<span style="font-weight: bold;">{}</span>',
            total
        )


@admin.register(Fornecedor)
class FornecedorAdmin(ModelAdmin):
    """Admin para Fornecedores"""
    list_display = ['nome', 'nif', 'email', 'telefone', 'ativo']
    list_filter = ['ativo']
    search_fields = ['nome', 'nif', 'email']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Informação Básica', {
            'fields': ('nome', 'nif', 'ativo')
        }),
        ('Contactos', {
            'fields': ('email', 'telefone', 'morada', 'iban')
        }),
        ('Notas', {
            'fields': ('notas',),
            'classes': ('collapse',),
        }),
        ('Metadados', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )


@admin.register(Projeto)
class ProjetoAdmin(ModelAdmin):
    """Admin para Projetos"""
    list_display = ['numero', 'nome', 'cliente', 'tipo', 'estado', 'display_valor', 'data_inicio']
    list_filter = ['tipo', 'estado', 'data_inicio']
    search_fields = ['numero', 'nome', 'cliente__nome']
    readonly_fields = ['created_at', 'updated_at']
    autocomplete_fields = ['cliente', 'owner']

    fieldsets = (
        ('Informação Básica', {
            'fields': ('numero', 'nome', 'cliente', 'owner', 'tipo', 'estado')
        }),
        ('Valores', {
            'fields': ('valor_total', 'premio_bruno', 'premio_rafael'),
            'classes': ('wide',),
        }),
        ('Datas', {
            'fields': ('data_inicio', 'data_entrega', 'data_pagamento')
        }),
        ('Detalhes', {
            'fields': ('descricao', 'notas'),
            'classes': ('collapse',),
        }),
        ('Metadados', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    @display(description="Valor", ordering="-valor_total")
    def display_valor(self, obj):
        """Mostrar valor formatado"""
        return format_html(
            '<span style="font-weight: bold;">€{:,.2f}</span>',
            obj.valor_total
        )

    def get_queryset(self, request):
        """Otimizar queries com select_related"""
        qs = super().get_queryset(request)
        return qs.select_related('cliente', 'owner')


@admin.register(Despesa)
class DespesaAdmin(ModelAdmin):
    """Admin para Despesas"""
    list_display = ['numero', 'descricao', 'tipo', 'fornecedor', 'display_valor', 'estado', 'data_despesa']
    list_filter = ['tipo', 'estado', 'data_despesa']
    search_fields = ['numero', 'descricao', 'fornecedor__nome']
    readonly_fields = ['created_at', 'updated_at']
    autocomplete_fields = ['fornecedor', 'socio', 'projeto']

    fieldsets = (
        ('Informação Básica', {
            'fields': ('numero', 'tipo', 'descricao', 'fornecedor')
        }),
        ('Valores', {
            'fields': ('valor', 'iva', 'estado')
        }),
        ('Datas', {
            'fields': ('data_despesa', 'data_pagamento')
        }),
        ('Relações', {
            'fields': ('socio', 'projeto'),
            'classes': ('collapse',),
        }),
        ('Notas', {
            'fields': ('notas',),
            'classes': ('collapse',),
        }),
        ('Metadados', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    @display(description="Valor", ordering="-valor")
    def display_valor(self, obj):
        """Mostrar valor formatado com IVA"""
        total = obj.valor + obj.iva
        return format_html(
            '<span style="font-weight: bold;">€{:,.2f}</span> <small>(+IVA €{:,.2f})</small>',
            obj.valor,
            obj.iva
        )

    def get_queryset(self, request):
        """Otimizar queries com select_related"""
        qs = super().get_queryset(request)
        return qs.select_related('fornecedor', 'socio', 'projeto')


# Customizar Admin Site
admin.site.site_header = "Agora Contabilidade"
admin.site.site_title = "Agora Admin"
admin.site.index_title = "Bem-vindo ao painel de gestão"
