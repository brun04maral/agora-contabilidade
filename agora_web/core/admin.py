# -*- coding: utf-8 -*-
"""
Core admin customizations for Agora Contabilidade with Unfold theme
"""
from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline
from unfold.decorators import display
from .models import (
    Cliente, Fornecedor, Projeto, Despesa, DespesaTemplate, Boletim, BoletimLinha,
    Equipamento, Orcamento, OrcamentoSecao, OrcamentoItem, OrcamentoReparticao
)


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


@admin.register(Equipamento)
class EquipamentoAdmin(ModelAdmin):
    """Admin para Equipamento com Unfold customization"""
    list_display = ['numero', 'produto', 'tipo', 'estado', 'uso_pessoal', 'preco_aluguer', 'rendimento_acumulado', 'created_at']
    list_filter = ['estado', 'uso_pessoal', 'tipo', 'created_at']
    search_fields = ['numero', 'produto', 'tipo', 'label', 'referencia', 'numero_serie']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']

    fieldsets = (
        ('Identificação', {
            'fields': ('numero', 'produto', 'tipo', 'label')
        }),
        ('Detalhes', {
            'fields': ('descricao', 'referencia', 'numero_serie', 'mac_address', 'quantidade', 'tamanho', 'estado', 'uso_pessoal', 'localizacao')
        }),
        ('Valores', {
            'fields': ('valor_compra', 'preco_aluguer', 'amortizacao_vezes', 'rendimento_acumulado')
        }),
        ('Aquisição', {
            'fields': ('data_compra', 'fornecedor', 'fatura_url'),
            'classes': ['collapse']
        }),
        ('Mídia', {
            'fields': ('foto_url',),
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


class OrcamentoSecaoInline(TabularInline):
    """Inline para secções do orçamento"""
    model = OrcamentoSecao
    extra = 1
    fields = ['ordem', 'tipo', 'nome', 'parent', 'subtotal']
    autocomplete_fields = ['parent']


class OrcamentoItemInline(TabularInline):
    """Inline para itens do orçamento"""
    model = OrcamentoItem
    extra = 1
    fields = ['ordem', 'secao', 'tipo', 'descricao', 'quantidade', 'dias', 'preco_unitario', 'total']
    autocomplete_fields = ['secao', 'equipamento']


class OrcamentoReparticaoInline(TabularInline):
    """Inline para repartições do orçamento"""
    model = OrcamentoReparticao
    extra = 1
    fields = ['ordem', 'tipo', 'entidade', 'beneficiario', 'valor', 'percentagem']
    autocomplete_fields = ['fornecedor', 'equipamento']


@admin.register(Orcamento)
class OrcamentoAdmin(ModelAdmin):
    """Admin para Orcamento com Unfold customization"""
    list_display = ['codigo', 'cliente', 'projeto', 'owner', 'data_criacao', 'valor_total', 'status', 'created_at']
    list_filter = ['status', 'owner', 'data_criacao', 'created_at']
    search_fields = ['codigo', 'titulo_cliente', 'cliente__nome', 'projeto__numero', 'descricao_proposta']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-data_criacao', '-created_at']
    autocomplete_fields = ['cliente', 'projeto']
    date_hierarchy = 'data_criacao'
    inlines = [OrcamentoSecaoInline, OrcamentoItemInline, OrcamentoReparticaoInline]

    fieldsets = (
        ('Identificação', {
            'fields': ('codigo', 'cliente', 'projeto', 'owner')
        }),
        ('Datas e Local', {
            'fields': ('data_criacao', 'data_evento', 'local_evento')
        }),
        ('Valores', {
            'fields': ('valor_total',)
        }),
        ('Estado', {
            'fields': ('status',)
        }),
        ('Proposta', {
            'fields': ('descricao_proposta', 'notas_contratuais')
        }),
        ('Versão Cliente', {
            'fields': ('tem_versao_cliente', 'titulo_cliente', 'descricao_cliente'),
            'classes': ['collapse']
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ['collapse']
        }),
    )


@admin.register(OrcamentoSecao)
class OrcamentoSecaoAdmin(ModelAdmin):
    """Admin para OrcamentoSecao com Unfold customization"""
    list_display = ['orcamento', 'nome', 'tipo', 'ordem', 'parent', 'subtotal']
    list_filter = ['tipo']
    search_fields = ['nome', 'orcamento__codigo']
    autocomplete_fields = ['orcamento', 'parent']
    ordering = ['orcamento', 'ordem']


@admin.register(OrcamentoItem)
class OrcamentoItemAdmin(ModelAdmin):
    """Admin para OrcamentoItem com Unfold customization"""
    list_display = ['orcamento', 'secao', 'descricao_short', 'tipo', 'quantidade', 'dias', 'preco_unitario', 'total']
    list_filter = ['tipo']
    search_fields = ['descricao', 'orcamento__codigo']
    autocomplete_fields = ['orcamento', 'secao', 'equipamento']
    ordering = ['orcamento', 'secao', 'ordem']

    @display(description='Descrição', ordering='descricao')
    def descricao_short(self, obj):
        """Mostra descrição truncada"""
        return obj.descricao[:50] + '...' if len(obj.descricao) > 50 else obj.descricao


@admin.register(OrcamentoReparticao)
class OrcamentoReparticaoAdmin(ModelAdmin):
    """Admin para OrcamentoReparticao com Unfold customization"""
    list_display = ['orcamento', 'tipo', 'entidade', 'beneficiario', 'valor', 'percentagem', 'total']
    list_filter = ['tipo']
    search_fields = ['entidade', 'beneficiario', 'descricao', 'orcamento__codigo']
    autocomplete_fields = ['orcamento', 'fornecedor', 'equipamento']
    ordering = ['orcamento', 'ordem']
