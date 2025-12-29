# -*- coding: utf-8 -*-
"""
Core admin customizations for Agora Contabilidade with Unfold theme
"""
from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline
from unfold.decorators import display
from .models import Cliente, Fornecedor, Projeto, Despesa, DespesaTemplate, Boletim, BoletimLinha


@admin.register(Cliente)
class ClienteAdmin(ModelAdmin):
    """Admin para Cliente com Unfold customization"""
    list_display = ['numero', 'nome', 'nome_formal', 'nif', 'pais', 'email', 'created_at']
    list_filter = ['pais', 'created_at']
    search_fields = ['numero', 'nome', 'nome_formal', 'nif', 'email']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']

    fieldsets = (
        ('Identificação', {
            'fields': ('numero', 'nome', 'nome_formal')
        }),
        ('Dados Fiscais', {
            'fields': ('nif', 'pais')
        }),
        ('Contactos', {
            'fields': ('morada', 'contacto', 'email')
        }),
        ('Informações Adicionais', {
            'fields': ('angariacao', 'nota')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ['collapse']
        }),
    )


@admin.register(Fornecedor)
class FornecedorAdmin(ModelAdmin):
    """Admin para Fornecedor com Unfold customization"""
    list_display = ['numero', 'nome', 'estatuto', 'area', 'funcao', 'classificacao', 'email', 'created_at']
    list_filter = ['estatuto', 'area', 'funcao', 'classificacao', 'pais', 'created_at']
    search_fields = ['numero', 'nome', 'nif', 'email', 'area', 'funcao']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']

    fieldsets = (
        ('Identificação', {
            'fields': ('numero', 'nome', 'estatuto')
        }),
        ('Profissional', {
            'fields': ('area', 'funcao', 'classificacao', 'validade_seguro_trabalho')
        }),
        ('Dados Fiscais', {
            'fields': ('nif', 'iban', 'pais')
        }),
        ('Contactos', {
            'fields': ('morada', 'contacto', 'email', 'website')
        }),
        ('Informações Adicionais', {
            'fields': ('nota',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ['collapse']
        }),
    )


@admin.register(Projeto)
class ProjetoAdmin(ModelAdmin):
    """Admin para Projeto com Unfold customization"""
    list_display = ['numero', 'tipo', 'owner', 'descricao_short', 'cliente', 'valor_sem_iva', 'estado', 'data_faturacao', 'created_at']
    list_filter = ['tipo', 'owner', 'estado', 'data_faturacao', 'created_at']
    search_fields = ['numero', 'descricao', 'cliente__nome']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    autocomplete_fields = ['cliente']

    fieldsets = (
        ('Identificação', {
            'fields': ('numero', 'tipo', 'owner', 'cliente')
        }),
        ('Descrição', {
            'fields': ('descricao',)
        }),
        ('Valores', {
            'fields': ('valor_sem_iva', 'premio_bruno', 'premio_rafael')
        }),
        ('Datas', {
            'fields': ('data_inicio', 'data_fim', 'data_faturacao', 'data_vencimento')
        }),
        ('Estado', {
            'fields': ('estado',)
        }),
        ('Informações Adicionais', {
            'fields': ('nota',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ['collapse']
        }),
    )

    @display(description='Descrição', ordering='descricao')
    def descricao_short(self, obj):
        """Mostra descrição truncada"""
        return obj.descricao[:50] + '...' if len(obj.descricao) > 50 else obj.descricao


@admin.register(DespesaTemplate)
class DespesaTemplateAdmin(ModelAdmin):
    """Admin para DespesaTemplate com Unfold customization"""
    list_display = ['numero', 'tipo', 'descricao_short', 'credor', 'valor_sem_iva', 'valor_com_iva', 'dia_mes', 'created_at']
    list_filter = ['tipo', 'dia_mes', 'created_at']
    search_fields = ['numero', 'descricao', 'credor__nome']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['dia_mes', '-created_at']
    autocomplete_fields = ['credor', 'projeto']

    fieldsets = (
        ('Identificação', {
            'fields': ('numero', 'tipo')
        }),
        ('Fornecedor/Projeto', {
            'fields': ('credor', 'projeto')
        }),
        ('Descrição', {
            'fields': ('descricao',)
        }),
        ('Valores', {
            'fields': ('valor_sem_iva', 'valor_com_iva')
        }),
        ('Recorrência', {
            'fields': ('dia_mes',)
        }),
        ('Informações Adicionais', {
            'fields': ('nota',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ['collapse']
        }),
    )

    @display(description='Descrição', ordering='descricao')
    def descricao_short(self, obj):
        """Mostra descrição truncada"""
        return obj.descricao[:30] + '...' if len(obj.descricao) > 30 else obj.descricao


@admin.register(Despesa)
class DespesaAdmin(ModelAdmin):
    """Admin para Despesa com Unfold customization"""
    list_display = ['numero', 'tipo', 'data', 'descricao_short', 'credor', 'projeto', 'valor_sem_iva', 'valor_com_iva', 'estado', 'data_pagamento', 'created_at']
    list_filter = ['tipo', 'estado', 'data', 'data_pagamento', 'created_at']
    search_fields = ['numero', 'descricao', 'credor__nome', 'projeto__numero']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-data', '-created_at']
    autocomplete_fields = ['credor', 'projeto', 'despesa_template']
    date_hierarchy = 'data'

    fieldsets = (
        ('Identificação', {
            'fields': ('numero', 'tipo', 'data')
        }),
        ('Fornecedor/Projeto', {
            'fields': ('credor', 'projeto')
        }),
        ('Descrição', {
            'fields': ('descricao',)
        }),
        ('Valores', {
            'fields': ('valor_sem_iva', 'valor_com_iva')
        }),
        ('Estado', {
            'fields': ('estado', 'data_pagamento')
        }),
        ('Origem', {
            'fields': ('despesa_template',),
            'classes': ['collapse']
        }),
        ('Informações Adicionais', {
            'fields': ('nota',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ['collapse']
        }),
    )

    @display(description='Descrição', ordering='descricao')
    def descricao_short(self, obj):
        """Mostra descrição truncada"""
        return obj.descricao[:30] + '...' if len(obj.descricao) > 30 else obj.descricao


class BoletimLinhaInline(TabularInline):
    """Inline para linhas de boletim"""
    model = BoletimLinha
    extra = 1
    fields = ['ordem', 'projeto', 'servico', 'localidade', 'data_inicio', 'hora_inicio', 'data_fim', 'hora_fim', 'tipo', 'dias', 'kms']
    autocomplete_fields = ['projeto']


@admin.register(Boletim)
class BoletimAdmin(ModelAdmin):
    """Admin para Boletim com Unfold customization"""
    list_display = ['numero', 'socio', 'mes', 'ano', 'data_emissao', 'valor_total', 'total_ajudas_nacionais', 'total_ajudas_estrangeiro', 'total_kms', 'estado', 'data_pagamento', 'created_at']
    list_filter = ['socio', 'estado', 'mes', 'ano', 'data_emissao', 'created_at']
    search_fields = ['numero', 'nota']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-data_emissao', '-created_at']
    date_hierarchy = 'data_emissao'
    inlines = [BoletimLinhaInline]

    fieldsets = (
        ('Identificação', {
            'fields': ('numero', 'socio', 'mes', 'ano')
        }),
        ('Datas', {
            'fields': ('data_emissao', 'data_pagamento')
        }),
        ('Valores de Referência', {
            'fields': ('val_dia_nacional', 'val_dia_estrangeiro', 'val_km'),
            'classes': ['collapse']
        }),
        ('Totais', {
            'fields': ('total_ajudas_nacionais', 'total_ajudas_estrangeiro', 'total_kms', 'valor_total')
        }),
        ('Estado', {
            'fields': ('estado',)
        }),
        ('Compatibilidade (antigo)', {
            'fields': ('valor', 'descricao'),
            'classes': ['collapse']
        }),
        ('Informações Adicionais', {
            'fields': ('nota',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ['collapse']
        }),
    )


@admin.register(BoletimLinha)
class BoletimLinhaAdmin(ModelAdmin):
    """Admin para BoletimLinha com Unfold customization"""
    list_display = ['boletim', 'ordem', 'servico_short', 'localidade', 'projeto', 'data_inicio', 'data_fim', 'tipo', 'dias', 'kms', 'created_at']
    list_filter = ['tipo', 'data_inicio', 'created_at']
    search_fields = ['servico', 'localidade', 'boletim__numero']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['boletim', 'ordem']
    autocomplete_fields = ['boletim', 'projeto']

    fieldsets = (
        ('Boletim', {
            'fields': ('boletim', 'ordem')
        }),
        ('Serviço', {
            'fields': ('projeto', 'servico', 'localidade')
        }),
        ('Datas e Horas', {
            'fields': ('data_inicio', 'hora_inicio', 'data_fim', 'hora_fim')
        }),
        ('Tipo e Valores', {
            'fields': ('tipo', 'dias', 'kms')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ['collapse']
        }),
    )

    @display(description='Serviço', ordering='servico')
    def servico_short(self, obj):
        """Mostra serviço truncado"""
        return obj.servico[:30] + '...' if len(obj.servico) > 30 else obj.servico
