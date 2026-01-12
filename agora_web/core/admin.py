# -*- coding: utf-8 -*-
"""
Core admin customizations for Agora Contabilidade with Unfold theme
"""
from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline
from unfold.decorators import display
from simple_history.admin import SimpleHistoryAdmin
from .models import (
    Socio, Cliente, Fornecedor, Projeto, Despesa, DespesaTemplate, Boletim, BoletimLinha,
    Equipamento, Orcamento, OrcamentoSecao, OrcamentoItem, OrcamentoReparticao, Saldo, Fiscal, ImportacaoDados
)


# Custom admin base que combina Unfold + SimpleHistory
class UnfoldHistoryAdmin(SimpleHistoryAdmin, ModelAdmin):
    """
    Admin base que combina django-simple-history com Unfold theme

    IMPORTANTE: A ordem de herança importa! SimpleHistoryAdmin deve vir primeiro
    para que seus métodos sejam usados corretamente.
    """
    # Configurações do SimpleHistory
    history_list_display = ['history_date', 'history_user', 'history_type']

    def get_readonly_fields(self, request, obj=None):
        """Adiciona campos de audit trail aos readonly fields + link para histórico"""
        readonly = super().get_readonly_fields(request, obj)
        fields = list(readonly) + ['created_at', 'updated_at', 'created_by', 'updated_by']

        # Adiciona link para histórico APENAS se objeto já existe
        if obj and obj.pk:
            fields.append('history_link')

        return fields

    @display(description='')
    def history_link(self, obj):
        """Link para a página de histórico do objeto"""
        if obj and obj.pk:
            from django.urls import reverse
            from django.utils.html import format_html

            history_url = reverse(
                f'admin:{obj._meta.app_label}_{obj._meta.model_name}_history',
                args=[obj.pk]
            )
            return format_html(
                '<a href="{}" class="button">Ver</a>',
                history_url
            )
        return ''


@admin.register(Socio)
class SocioAdmin(UnfoldHistoryAdmin):
    """Admin para Sócio com Unfold customization + History"""
    list_display = ['codigo', 'nome_completo', 'nome_curto', 'email', 'percentagem_participacao', 'ativo', 'created_at']
    list_filter = ['ativo']
    search_fields = ['codigo', 'nome_completo', 'nome_curto', 'email']
    ordering = ['codigo']

    fieldsets = (
        ('Identificação', {
            'fields': ('codigo', 'nome_completo', 'nome_curto')
        }),
        ('Contactos', {
            'fields': ('email', 'telefone')
        }),
        ('Participação', {
            'fields': ('percentagem_participacao', 'ativo')
        }),
        ('UI', {
            'fields': ('cor_tema',),
            'classes': ['collapse']
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at', 'created_by', 'updated_by', 'history_link'),
            'classes': ['collapse']
        }),
    )

    def get_urls(self):
        """Adiciona URL customizada para dashboard do sócio"""
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('<path:object_id>/dashboard/', self.admin_site.admin_view(self.dashboard_view), name='core_socio_dashboard'),
        ]
        return custom_urls + urls

    def dashboard_view(self, request, object_id):
        """View para dashboard de estatísticas do sócio"""
        from django.shortcuts import render, get_object_or_404
        from core.models import Socio, Projeto, Despesa

        socio = get_object_or_404(Socio, pk=object_id)

        # Estatísticas
        num_projetos_pessoais = socio.get_num_projetos_pessoais()
        num_despesas_pessoais = socio.get_num_despesas_pessoais()
        num_clientes_angariados = socio.get_num_clientes_angariados()

        # Listas detalhadas
        projetos_pessoais = socio.projetos.filter(tipo='PESSOAL').order_by('-data_faturacao')[:10]
        clientes_angariados = socio.clientes_angariados.order_by('-created_at')[:10]

        context = {
            **self.admin_site.each_context(request),
            'title': f'Dashboard - {socio.nome_completo}',
            'socio': socio,
            'num_projetos_pessoais': num_projetos_pessoais,
            'num_despesas_pessoais': num_despesas_pessoais,
            'num_clientes_angariados': num_clientes_angariados,
            'projetos_pessoais': projetos_pessoais,
            'clientes_angariados': clientes_angariados,
            'opts': self.model._meta,
        }

        return render(request, 'admin/core/socio/dashboard.html', context)


@admin.register(Cliente)
class ClienteAdmin(UnfoldHistoryAdmin):
    """Admin para Cliente com Unfold customization + History"""
    list_display = ['numero', 'nome', 'nome_formal', 'angariador', 'nif', 'pais', 'email', 'created_at']
    list_filter = ['angariador', 'pais', 'created_at']
    search_fields = ['numero', 'nome', 'nome_formal', 'nif', 'email', 'angariador__nome_completo']
    ordering = ['-created_at']

    fieldsets = (
        ('Identificação', {
            'fields': ('numero', 'nome', 'nome_formal')
        }),
        ('Angariação', {
            'fields': ('angariador',)
        }),
        ('Dados Fiscais', {
            'fields': ('nif', 'pais')
        }),
        ('Contactos', {
            'fields': ('morada', 'contacto', 'email')
        }),
        ('Informações Adicionais', {
            'fields': ('nota',)
        }),
        ('Deprecated', {
            'fields': ('angariacao',),
            'classes': ['collapse'],
            'description': 'Campo antigo mantido por compatibilidade - usar campo "angariador"'
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at', 'created_by', 'updated_by', 'history_link'),
            'classes': ['collapse']
        }),
    )


@admin.register(Fornecedor)
class FornecedorAdmin(UnfoldHistoryAdmin):
    """Admin para Fornecedor com Unfold customization"""
    list_display = ['numero', 'nome', 'estatuto', 'area', 'funcao', 'classificacao', 'email', 'created_at']
    list_filter = ['estatuto', 'area', 'funcao', 'classificacao', 'pais', 'created_at']
    search_fields = ['numero', 'nome', 'nif', 'email', 'area', 'funcao']
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
            'fields': ('created_at', 'updated_at', 'created_by', 'updated_by', 'history_link'),
            'classes': ['collapse']
        }),
    )


@admin.register(Projeto)
class ProjetoAdmin(UnfoldHistoryAdmin):
    """Admin para Projeto com Unfold customization"""
    list_display = ['numero', 'tipo', 'socio', 'descricao_short', 'cliente', 'valor_sem_iva', 'estado', 'data_faturacao', 'created_at']
    list_filter = ['tipo', 'socio', 'estado', 'data_faturacao', 'created_at']
    search_fields = [
        '^numero',              # Prioridade: match exato no início (ex: "P0001")
        'descricao',            # Contains na descrição
        'cliente__nome',        # Contains no nome do cliente
        'cliente__nome_formal', # Contains no nome formal do cliente
        'tipo',                 # Contains no tipo (PESSOAL/EMPRESA)
        'socio__nome_completo', # Contains no nome do sócio
        'estado',               # Contains no estado
        'nota',                 # Contains nas notas
    ]
    ordering = ['-created_at']
    autocomplete_fields = ['cliente']
    date_hierarchy = 'data_faturacao'  # Filtro de navegação por ano/mês/dia no cabeçalho
    actions = ['exportar_pdf', 'exportar_excel']

    fieldsets = (
        ('Identificação', {
            'fields': ('numero', 'tipo', 'socio', 'cliente')
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
            'fields': ('created_at', 'updated_at', 'created_by', 'updated_by', 'history_link'),
            'classes': ['collapse']
        }),
    )

    @display(description='Descrição', ordering='descricao')
    def descricao_short(self, obj):
        """Mostra descrição truncada"""
        return obj.descricao[:50] + '...' if len(obj.descricao) > 50 else obj.descricao

    @admin.action(description='Exportar PDF')
    def exportar_pdf(self, request, queryset):
        """Exporta projetos selecionados como PDF"""
        from core.utils.relatorios import gerar_relatorio_projetos_pdf
        return gerar_relatorio_projetos_pdf(queryset, filtros={'tipo_relatorio': 'Selecionados'})

    @admin.action(description='Exportar Excel')
    def exportar_excel(self, request, queryset):
        """Exporta projetos selecionados como Excel"""
        from core.utils.relatorios import gerar_relatorio_projetos_excel
        return gerar_relatorio_projetos_excel(queryset, filtros={'tipo_relatorio': 'Selecionados'})

    def get_urls(self):
        """Adiciona URL customizada para relatório personalizado"""
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('relatorio-personalizado/', self.admin_site.admin_view(self.relatorio_personalizado_view), name='core_projeto_relatorio'),
        ]
        return custom_urls + urls

    def relatorio_personalizado_view(self, request):
        """View para formulário de relatório personalizado"""
        from django.shortcuts import render, redirect
        from django.contrib import messages
        from core.forms import RelatorioProjetosForm
        from core.utils.relatorios import gerar_relatorio_projetos_pdf, gerar_relatorio_projetos_excel

        if request.method == 'POST':
            form = RelatorioProjetosForm(request.POST)
            if form.is_valid():
                # Obter dados do formulário
                cleaned_data = form.cleaned_data

                # Construir queryset baseado nos filtros
                queryset = Projeto.objects.all()

                if cleaned_data.get('socio'):
                    queryset = queryset.filter(socio=cleaned_data['socio'])

                if cleaned_data.get('tipo'):
                    queryset = queryset.filter(tipo=cleaned_data['tipo'])

                if cleaned_data.get('estado'):
                    queryset = queryset.filter(estado=cleaned_data['estado'])

                if cleaned_data.get('cliente'):
                    queryset = queryset.filter(cliente__nome__icontains=cleaned_data['cliente'])

                if cleaned_data.get('data_inicio'):
                    queryset = queryset.filter(data_faturacao__gte=cleaned_data['data_inicio'])

                if cleaned_data.get('data_fim'):
                    queryset = queryset.filter(data_faturacao__lte=cleaned_data['data_fim'])

                # Preparar filtros para o relatório
                filtros = {
                    'tipo_relatorio': dict(form.TIPO_RELATORIO_CHOICES).get(cleaned_data['tipo_relatorio']),
                    'socio': str(cleaned_data['socio']) if cleaned_data.get('socio') else None,
                    'estado': cleaned_data.get('estado'),
                    'data_inicio': cleaned_data.get('data_inicio'),
                    'data_fim': cleaned_data.get('data_fim'),
                }

                # Gerar relatório no formato escolhido
                if cleaned_data['formato'] == 'pdf':
                    return gerar_relatorio_projetos_pdf(queryset, filtros)
                else:
                    return gerar_relatorio_projetos_excel(queryset, filtros)
        else:
            form = RelatorioProjetosForm()

        context = {
            **self.admin_site.each_context(request),
            'title': 'Criar Relatório Personalizado de Projetos',
            'form': form,
            'opts': self.model._meta,
        }

        return render(request, 'admin/core/projeto/relatorio_form.html', context)


@admin.register(DespesaTemplate)
class DespesaTemplateAdmin(UnfoldHistoryAdmin):
    """Admin para DespesaTemplate com Unfold customization"""
    list_display = ['numero', 'tipo', 'descricao_short', 'credor', 'valor_sem_iva', 'valor_com_iva', 'irs_retido', 'dia_mes', 'created_at']
    list_filter = ['tipo', 'dia_mes', 'created_at']
    search_fields = ['numero', 'descricao', 'credor__nome']
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
            'fields': ('valor_sem_iva', 'valor_com_iva', 'irs_retido')
        }),
        ('Recorrência', {
            'fields': ('dia_mes',)
        }),
        ('Informações Adicionais', {
            'fields': ('nota',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at', 'created_by', 'updated_by', 'history_link'),
            'classes': ['collapse']
        }),
    )

    @display(description='Descrição', ordering='descricao')
    def descricao_short(self, obj):
        """Mostra descrição truncada"""
        return obj.descricao[:30] + '...' if len(obj.descricao) > 30 else obj.descricao


@admin.register(Despesa)
class DespesaAdmin(UnfoldHistoryAdmin):
    """Admin para Despesa com Unfold customization"""
    list_display = ['numero', 'tags_display', 'data', 'descricao_short', 'credor', 'projeto', 'valor_sem_iva', 'valor_com_iva', 'irs_retido', 'estado', 'data_pagamento', 'created_at']
    list_filter = ['tags', 'estado', 'data', 'data_pagamento', 'created_at']
    search_fields = [
        '^numero',              # Prioridade: match exato no início (ex: "D0001")
        'descricao',            # Contains na descrição
        'credor__nome',         # Contains no nome do credor/fornecedor
        'projeto__numero',      # Contains no número do projeto
        '^projeto__numero',     # Prioridade: projeto exato (ex: "P0001")
        'tipo_original',        # Contains no tipo original
        'tags__codigo',         # Contains nos códigos das tags
        'tags__nome',           # Contains nos nomes das tags
        'estado',               # Contains no estado (PAGO/PENDENTE)
        'nota',                 # Contains nas notas
    ]
    ordering = ['-data', '-created_at']
    autocomplete_fields = ['credor', 'projeto', 'despesa_template']
    date_hierarchy = 'data'
    filter_horizontal = ['tags']  # Interface melhor para ManyToMany

    fieldsets = (
        ('Identificação', {
            'fields': ('numero', 'data')
        }),
        ('Categorização', {
            'fields': ('tags', 'tipo_original')
        }),
        ('Fornecedor/Projeto', {
            'fields': ('credor', 'projeto')
        }),
        ('Descrição', {
            'fields': ('descricao',)
        }),
        ('Valores', {
            'fields': ('valor_sem_iva', 'valor_com_iva', 'irs_retido')
        }),
        ('Estado', {
            'fields': ('estado', 'data_pagamento')
        }),
        ('Deprecated', {
            'fields': ('tipo',),
            'classes': ['collapse'],
            'description': 'Campo antigo mantido por compatibilidade - usar tags'
        }),
        ('Origem', {
            'fields': ('despesa_template',),
            'classes': ['collapse']
        }),
        ('Informações Adicionais', {
            'fields': ('nota',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at', 'created_by', 'updated_by', 'history_link'),
            'classes': ['collapse']
        }),
    )

    @display(description='Tags', ordering='tags')
    def tags_display(self, obj):
        """Mostra tags da despesa"""
        tags = obj.tags.all()
        if not tags:
            return '-'
        return ', '.join([tag.codigo for tag in tags[:3]])  # Mostra até 3 tags

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
class BoletimAdmin(UnfoldHistoryAdmin):
    """Admin para Boletim com Unfold customization"""
    list_display = ['numero', 'socio', 'mes', 'ano', 'data_emissao', 'valor_total', 'total_ajudas_nacionais', 'total_ajudas_estrangeiro', 'total_kms', 'estado', 'data_pagamento', 'created_at']
    list_filter = ['socio', 'estado', 'mes', 'ano', 'data_emissao', 'created_at']
    search_fields = [
        '^numero',              # Prioridade: match exato no início (ex: "RV2024001")
        'socio__codigo',        # Contains no código do sócio (BA/RR)
        'socio__nome_completo', # Contains no nome do sócio
        'socio__nome_curto',    # Contains no nome curto do sócio
        'mes',                  # Contains no mês
        'ano',                  # Contains no ano
        'estado',               # Contains no estado (PAGO/PENDENTE)
        'descricao',            # Contains na descrição (campo antigo)
        'nota',                 # Contains nas notas
    ]
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
            'fields': ('created_at', 'updated_at', 'created_by', 'updated_by', 'history_link'),
            'classes': ['collapse']
        }),
    )


@admin.register(BoletimLinha)
class BoletimLinhaAdmin(ModelAdmin):
    """Admin para BoletimLinha com Unfold customization"""
    list_display = ['boletim', 'ordem', 'servico_short', 'localidade', 'projeto', 'data_inicio', 'data_fim', 'tipo', 'dias', 'kms', 'created_at']
    list_filter = ['tipo', 'data_inicio', 'created_at']
    search_fields = ['servico', 'localidade', 'boletim__numero']
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
            'fields': ('created_at', 'updated_at', 'created_by', 'updated_by', 'history_link'),
            'classes': ['collapse']
        }),
    )

    @display(description='Serviço', ordering='servico')
    def servico_short(self, obj):
        """Mostra serviço truncado"""
        return obj.servico[:30] + '...' if len(obj.servico) > 30 else obj.servico


@admin.register(Equipamento)
class EquipamentoAdmin(UnfoldHistoryAdmin):
    """Admin para Equipamento com Unfold customization"""
    list_display = ['numero', 'produto', 'tipo', 'estado', 'uso_pessoal', 'preco_aluguer', 'rendimento_acumulado', 'created_at']
    list_filter = ['estado', 'uso_pessoal', 'tipo', 'created_at']
    search_fields = ['numero', 'produto', 'tipo', 'label', 'referencia', 'numero_serie']
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
            'fields': ('created_at', 'updated_at', 'created_by', 'updated_by', 'history_link'),
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
class OrcamentoAdmin(UnfoldHistoryAdmin):
    """Admin para Orcamento com Unfold customization"""
    list_display = ['codigo', 'cliente', 'projeto', 'socio', 'data_criacao', 'valor_total', 'status', 'created_at']
    list_filter = ['status', 'socio', 'data_criacao', 'created_at']
    search_fields = [
        '^codigo',              # Prioridade: match exato no início (ex: "ORC2024001")
        'titulo_cliente',       # Contains no título para o cliente
        'cliente__nome',        # Contains no nome do cliente
        'cliente__nome_formal', # Contains no nome formal do cliente
        '^projeto__numero',     # Prioridade: número exato do projeto
        'projeto__descricao',   # Contains na descrição do projeto
        'socio__nome_completo', # Contains no nome do sócio
        'status',               # Contains no status
        'local_evento',         # Contains no local do evento
        'descricao_proposta',   # Contains na descrição da proposta
        'notas_contratuais',    # Contains nas notas contratuais
        'descricao_cliente',    # Contains na descrição para cliente
    ]
    ordering = ['-data_criacao', '-created_at']
    autocomplete_fields = ['cliente', 'projeto']
    date_hierarchy = 'data_criacao'
    inlines = [OrcamentoSecaoInline, OrcamentoItemInline, OrcamentoReparticaoInline]

    fieldsets = (
        ('Identificação', {
            'fields': ('codigo', 'cliente', 'projeto', 'socio')
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
            'fields': ('created_at', 'updated_at', 'created_by', 'updated_by', 'history_link'),
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


@admin.register(Saldo)
class SaldoAdmin(ModelAdmin):
    """Admin para Saldos Pessoais - Dashboard personalizado"""
    
    # Desabilitar ações padrão já que não há tabela
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def changelist_view(self, request, extra_context=None):
        """Vista personalizada para mostrar dashboard de saldos"""
        from django.shortcuts import render
        from core.utils.saldos import SaldosCalculator
        from datetime import date

        calculator = SaldosCalculator()
        ano_atual = date.today().year

        # Calcular saldos TOTAIS (de sempre)
        saldo_total_ba = calculator.calcular_saldo_bruno(incluir_investimento=False)
        saldo_total_rr = calculator.calcular_saldo_rafael(incluir_investimento=False)

        # Calcular breakdown do ANO CORRENTE (usando filtros de data)
        data_inicio_ano = date(ano_atual, 1, 1)
        data_fim_ano = date(ano_atual, 12, 31)

        breakdown_ba = calculator.calcular_saldo_bruno(
            incluir_investimento=False,
            data_inicio=data_inicio_ano,
            data_fim=data_fim_ano
        )
        breakdown_rr = calculator.calcular_saldo_rafael(
            incluir_investimento=False,
            data_inicio=data_inicio_ano,
            data_fim=data_fim_ano
        )

        context = {
            **self.admin_site.each_context(request),
            'title': 'Saldos Pessoais',
            'ano_atual': ano_atual,
            # Saldos totais (de sempre) - para cards de topo
            'saldo_total_ba': saldo_total_ba,
            'saldo_total_rr': saldo_total_rr,
            # Breakdown do ano corrente - para secção de breakdown
            'breakdown_ba': breakdown_ba,
            'breakdown_rr': breakdown_rr,
        }

        # Render template directly (não chamar super() para evitar query na tabela inexistente)
        return render(request, 'admin/core/saldo/changelist.html', context)


@admin.register(Fiscal)
class FiscalAdmin(ModelAdmin):
    """Admin para Estado Fiscal - Dashboard personalizado"""

    # Desabilitar ações padrão já que não há tabela
    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        """Vista personalizada para mostrar dashboard fiscal"""
        from django.shortcuts import render
        from core.utils.fiscal import FiscalCalculator
        from datetime import date

        calculator = FiscalCalculator()
        hoje = date.today()
        ano_atual = hoje.year
        mes_atual = hoje.month
        trimestre_atual = (mes_atual - 1) // 3 + 1

        # Calcular IVA Trimestral (trimestre atual)
        iva = calculator.calcular_iva_trimestral(ano_atual, trimestre_atual)

        # Calcular IRS Mensal (mês atual)
        irs = calculator.calcular_irs_mensal(ano_atual, mes_atual)

        # Estimar IRC Anual (ano atual)
        irc = calculator.estimar_irc_anual(ano_atual)

        # Próximas obrigações
        obrigacoes = calculator.proximas_obrigacoes()

        context = {
            **self.admin_site.each_context(request),
            'title': 'Estado Fiscal',
            'ano_atual': ano_atual,
            'mes_atual': mes_atual,
            'trimestre_atual': trimestre_atual,
            'iva': iva,
            'irs': irs,
            'irc': irc,
            'obrigacoes': obrigacoes[:5],  # Próximas 5 obrigações
        }

        # Render template directly (não chamar super() para evitar query na tabela inexistente)
        return render(request, 'admin/core/fiscal/changelist.html', context)


@admin.register(ImportacaoDados)
class ImportacaoDadosAdmin(ModelAdmin):
    """Admin para Importação de Dados via Excel"""

    # Desabilitar ações padrão já que não há tabela
    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        """Vista personalizada para upload de Excel"""
        from django.shortcuts import render, redirect
        from django.contrib import messages
        from django.core.management import call_command
        from django.conf import settings
        import os
        from io import StringIO

        # Se POST com ficheiro
        if request.method == 'POST' and request.FILES.get('excel_file'):
            excel_file = request.FILES['excel_file']

            # Validar extensão
            if not excel_file.name.endswith('.xlsx'):
                messages.error(request, '❌ Ficheiro inválido! Apenas ficheiros .xlsx são aceites.')
                return redirect(request.path)

            # Guardar ficheiro temporário
            upload_dir = os.path.join(settings.BASE_DIR, 'uploads')
            os.makedirs(upload_dir, exist_ok=True)
            file_path = os.path.join(upload_dir, excel_file.name)

            with open(file_path, 'wb+') as destination:
                for chunk in excel_file.chunks():
                    destination.write(chunk)

            # Executar comando de importação
            try:
                # Capturar output do comando
                out = StringIO()
                call_command('import_from_excel', file_path, stdout=out)
                output = out.getvalue()

                # Processar resultado
                if 'SUCESSO' in output or '✅' in output:
                    messages.success(request, f'✅ Importação concluída com sucesso!\n\n{output}')
                else:
                    messages.warning(request, f'⚠️ Importação concluída com avisos:\n\n{output}')

            except Exception as e:
                messages.error(request, f'❌ Erro na importação: {str(e)}')

            finally:
                # Limpar ficheiro temporário
                if os.path.exists(file_path):
                    os.remove(file_path)

            return redirect(request.path)

        # GET - mostrar formulário
        context = {
            **self.admin_site.each_context(request),
            'title': 'Importação de Dados',
            'subtitle': 'Upload de ficheiro Excel com dados da contabilidade',
        }

        return render(request, 'admin/core/importacaodados/changelist.html', context)
