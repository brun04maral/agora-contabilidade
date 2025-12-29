# -*- coding: utf-8 -*-
"""
Core admin customizations for Agora Contabilidade with Unfold theme
"""
from django.contrib import admin
from unfold.admin import ModelAdmin
from unfold.decorators import display
from .models import Cliente, Fornecedor, Projeto


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
