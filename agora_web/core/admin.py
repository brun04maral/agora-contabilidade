# -*- coding: utf-8 -*-
"""
Core admin customizations for Agora Contabilidade with Unfold theme
"""
from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.contrib.admin.actions import delete_selected
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import path, reverse
from django.utils.html import format_html
from unfold.admin import ModelAdmin, TabularInline
from unfold.decorators import display, action
from simple_history.admin import SimpleHistoryAdmin
from .models import (
    Socio, Cliente, Fornecedor, Projeto, Despesa, DespesaTemplate, Boletim, BoletimLinha,
    Equipamento, Orcamento, OrcamentoSecao, OrcamentoItem, OrcamentoReparticao, Saldo, Fiscal, ImportacaoDados, Documentacao,
    TagIRC, TagIVA, TagIRS, TagTSU
)


# Filtros customizados simples para evitar erro 400
class SocioListFilter(SimpleListFilter):
    """Filtro simples para Socio"""
    title = 'sócio'
    parameter_name = 'socio'

    def lookups(self, request, model_admin):
        socios = Socio.objects.all()
        return [(s.codigo, s.nome_completo) for s in socios]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(socio__codigo=self.value())
        return queryset


class AngariadorListFilter(SimpleListFilter):
    """Filtro simples para Angariador"""
    title = 'angariador'
    parameter_name = 'angariador'

    def lookups(self, request, model_admin):
        socios = Socio.objects.all()
        return [(s.codigo, s.nome_completo) for s in socios]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(angariador__codigo=self.value())
        return queryset


class TagListFilter(SimpleListFilter):
    """Filtro simples para Tags (evita erro 400 com ManyToMany)"""
    title = 'tags'
    parameter_name = 'tags'

    def lookups(self, request, model_admin):
        from core.models import TagDespesa
        tags = TagDespesa.objects.all().order_by('codigo')
        return [(tag.codigo, f"{tag.codigo} - {tag.nome}") for tag in tags]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(tags__codigo=self.value()).distinct()
        return queryset


# Custom admin base que combina Unfold + SimpleHistory
class UnfoldHistoryAdmin(SimpleHistoryAdmin, ModelAdmin):
    """
    Admin base que combina django-simple-history com Unfold theme

    IMPORTANTE: A ordem de herança importa! SimpleHistoryAdmin deve vir primeiro
    para que seus métodos sejam usados corretamente.
    """
    # Configurações do SimpleHistory
    history_list_display = ['history_date', 'history_user', 'history_type']

    @action(description='Remover selecionados', permissions=['delete'])
    def delete_selected(self, request, queryset):
        """Ação de remoção em lote (wrapper para delete_selected do Django)"""
        from django.contrib.admin.actions import delete_selected as django_delete_selected
        return django_delete_selected(self, request, queryset)

    def has_delete_permission(self, request, obj=None):
        """Permissão para deletar (necessário para a ação delete_selected)"""
        return super().has_delete_permission(request, obj)

    def get_readonly_fields(self, request, obj=None):
        """Adiciona campos de audit trail aos readonly fields + link para histórico"""
        readonly = super().get_readonly_fields(request, obj)
        fields = list(readonly) + ['created_at', 'updated_at', 'created_by', 'updated_by']

        # Adiciona link para histórico APENAS se objeto já existe
        if obj and obj.pk:
            fields.append('history_link')

        return fields

    def get_fieldsets(self, request, obj=None):
        """Remove history_link dos fieldsets quando estamos criando um novo objeto"""
        fieldsets = super().get_fieldsets(request, obj)

        # Se estamos criando (não existe obj), remover history_link dos fieldsets
        if not obj or not obj.pk:
            fieldsets = list(fieldsets)  # Make mutable copy
            for i, (name, options) in enumerate(fieldsets):
                if 'fields' in options and 'history_link' in options['fields']:
                    # Create mutable copy of fields tuple
                    fields = list(options['fields'])
                    if 'history_link' in fields:
                        fields.remove('history_link')
                    # Update the fieldset with new fields
                    options = dict(options)
                    options['fields'] = tuple(fields)
                    fieldsets[i] = (name, options)

        return fieldsets

    def get_changeform_initial_data(self, request):
        """Pré-preenche o próximo código/número na sequência ao criar novo objeto"""
        initial = super().get_changeform_initial_data(request)

        # Detectar o nome do campo (pode ser 'numero' ou 'codigo')
        field_name = None
        prefix = None

        if hasattr(self.model, 'numero'):
            field_name = 'numero'
            # Mapear modelo -> prefixo
            model_name = self.model.__name__
            prefix_map = {
                'Projeto': 'P',
                'Despesa': 'D',
                'Cliente': 'C',
                'Fornecedor': 'F',
                'DespesaTemplate': 'TD',
                'Boletim': 'B',
                'Equipamento': 'E',
            }
            prefix = prefix_map.get(model_name)
        elif hasattr(self.model, 'codigo') and self.model.__name__ == 'Orcamento':
            field_name = 'codigo'
            # Orçamento usa padrão diferente, skip por agora
            prefix = None

        if field_name and prefix:
            # Buscar o último código com esse prefixo
            import re
            from django.db.models import Max

            # Obter todos os códigos que começam com o prefixo
            all_codes = self.model.objects.filter(
                **{f'{field_name}__startswith': f'#{prefix}'}
            ).values_list(field_name, flat=True)

            # Extrair números e encontrar o maior
            max_num = 0
            pattern = rf'#?{re.escape(prefix)}(\d+)'
            for code in all_codes:
                match = re.match(pattern, code)
                if match:
                    num = int(match.group(1))
                    max_num = max(max_num, num)

            # Próximo número
            next_num = max_num + 1

            # Formato com padding (ex: P0081, D000001, E000028)
            if prefix == 'P':
                next_code = f'#{prefix}{next_num:04d}'
            elif prefix in ['D', 'TD', 'E']:
                next_code = f'#{prefix}{next_num:06d}'
            else:
                next_code = f'#{prefix}{next_num:04d}'

            initial[field_name] = next_code

        return initial

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

    def history_view(self, request, object_id, extra_context=None):
        """
        Override history_view para adicionar comparação campo-a-campo
        """
        # Obter objeto atual
        model = self.model
        obj = self.get_object(request, object_id)

        # Obter histórico ordenado (mais recente primeiro)
        history = list(model.history.filter(id=object_id).order_by('-history_date'))

        # Processar cada item do histórico criando wrappers
        action_list = []

        for i, record in enumerate(history):
            # Criar wrapper como dicionário (melhor compatibilidade com Django templates)
            wrapper = {
                'history_instance': record,
                'history_type': record.history_type,
                'history_date': record.history_date,
                'history_user': record.history_user,
                'prev_record': None,
                'diff_against_prev': []
            }

            # Se tem registo anterior, calcular diferenças
            if i < len(history) - 1 and record.history_type == '~':
                prev_record = history[i + 1]
                wrapper['prev_record'] = prev_record

                try:
                    delta = record.diff_against(prev_record)
                    changes = []

                    for change in delta.changes:
                        # Obter verbose_name do campo
                        try:
                            field = model._meta.get_field(change.field)
                            field_verbose_name = field.verbose_name
                        except:
                            field_verbose_name = change.field

                        changes.append({
                            'field': change.field,
                            'field_verbose_name': field_verbose_name,
                            'old_value': change.old,
                            'new_value': change.new,
                        })

                    wrapper['diff_against_prev'] = changes
                except Exception as e:
                    # Se falhar o diff, deixa vazio
                    wrapper['diff_against_prev'] = []

            action_list.append(wrapper)

        # Preparar context com todas as variáveis necessárias do admin
        context = {
            **self.admin_site.each_context(request),
            'title': f'Histórico de modificações: {obj}',
            'action_list': action_list,
            'object': obj,
            'opts': model._meta,
            'app_label': model._meta.app_label,
            'has_view_permission': self.has_view_permission(request, obj),
            'has_change_permission': self.has_change_permission(request, obj),
        }

        if extra_context:
            context.update(extra_context)

        # Renderizar template customizado
        from django.template.response import TemplateResponse
        return TemplateResponse(request, 'simple_history/object_history.html', context)


@admin.register(Socio)
class SocioAdmin(UnfoldHistoryAdmin):
    """Admin para Sócio com Unfold customization + History"""
    list_display = ['codigo', 'nome_completo', 'nome_curto', 'email', 'percentagem_participacao', 'ativo']
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
        """Adiciona URL customizada para editar sócio"""
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('<path:object_id>/edit/', self.admin_site.admin_view(self.edit_view), name='core_socio_edit'),
        ]
        return custom_urls + urls

    def change_view(self, request, object_id, form_url='', extra_context=None):
        """Override: Redirecionar para dashboard ao visualizar sócio"""
        from django.shortcuts import render, get_object_or_404
        from core.models import Socio

        # Se for POST (salvando), usar comportamento padrão
        if request.method == 'POST':
            return super().change_view(request, object_id, form_url, extra_context)

        # Se for GET (visualizando), mostrar dashboard
        socio = get_object_or_404(Socio, pk=object_id)

        # Estatísticas
        num_projetos_pessoais = socio.get_num_projetos_pessoais()
        num_despesas_pessoais = socio.get_num_despesas_pessoais()
        num_clientes_angariados = socio.get_num_clientes_angariados()

        context = {
            **self.admin_site.each_context(request),
            'title': socio.nome_completo,
            'socio': socio,
            'num_projetos_pessoais': num_projetos_pessoais,
            'num_despesas_pessoais': num_despesas_pessoais,
            'num_clientes_angariados': num_clientes_angariados,
            'opts': self.model._meta,
        }

        return render(request, 'admin/core/socio/dashboard.html', context)

    def edit_view(self, request, object_id):
        """View para editar sócio (formulário real)"""
        return super().change_view(request, object_id)


# ===================================================================
# TAGS FISCAIS - Categorização IRC, IVA, IRS, TSU
# ===================================================================

@admin.register(TagIRC)
class TagIRCAdmin(ModelAdmin):
    """Admin para Tags IRC (dedutibilidade IRC)"""
    list_display = ['codigo', 'nome', 'percentagem_dedutivel', 'ordem']
    list_editable = ['ordem']
    search_fields = ['codigo', 'nome', 'descricao']
    ordering = ['ordem', 'codigo']

    fieldsets = (
        (None, {
            'fields': ('codigo', 'nome', 'percentagem_dedutivel', 'ordem')
        }),
        ('Detalhes', {
            'fields': ('descricao',),
            'classes': ['collapse']
        }),
    )


@admin.register(TagIVA)
class TagIVAAdmin(ModelAdmin):
    """Admin para Tags IVA (dedutibilidade IVA)"""
    list_display = ['codigo', 'nome', 'percentagem_dedutivel', 'ordem']
    list_editable = ['ordem']
    search_fields = ['codigo', 'nome', 'descricao']
    ordering = ['ordem', 'codigo']

    fieldsets = (
        (None, {
            'fields': ('codigo', 'nome', 'percentagem_dedutivel', 'ordem')
        }),
        ('Detalhes', {
            'fields': ('descricao',),
            'classes': ['collapse']
        }),
    )


@admin.register(TagIRS)
class TagIRSAdmin(ModelAdmin):
    """Admin para Tags IRS (regime de retenção)"""
    list_display = ['codigo', 'nome', 'taxa_retencao_default', 'ordem']
    list_editable = ['ordem']
    search_fields = ['codigo', 'nome', 'descricao']
    ordering = ['ordem', 'codigo']

    fieldsets = (
        (None, {
            'fields': ('codigo', 'nome', 'taxa_retencao_default', 'ordem')
        }),
        ('Detalhes', {
            'fields': ('descricao',),
            'classes': ['collapse']
        }),
    )


@admin.register(TagTSU)
class TagTSUAdmin(ModelAdmin):
    """Admin para Tags TSU (Segurança Social)"""
    list_display = ['codigo', 'nome', 'taxa_empresa', 'taxa_trabalhador', 'ordem']
    list_editable = ['ordem']
    search_fields = ['codigo', 'nome', 'descricao']
    ordering = ['ordem', 'codigo']

    fieldsets = (
        (None, {
            'fields': ('codigo', 'nome', 'taxa_empresa', 'taxa_trabalhador', 'ordem')
        }),
        ('Detalhes', {
            'fields': ('descricao',),
            'classes': ['collapse']
        }),
    )


@admin.register(Cliente)
class ClienteAdmin(UnfoldHistoryAdmin):
    """Admin para Cliente com Unfold customization + History"""
    list_display = ['numero', 'nome', 'nome_formal', 'angariador', 'nif', 'pais', 'email']
    list_filter = [AngariadorListFilter, 'pais']
    search_fields = ['numero', 'nome', 'nome_formal', 'nif', 'email', 'angariador__nome_completo']
    ordering = ['-created_at']
    actions = ['delete_selected', 'exportar_pdf', 'exportar_excel']

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

    @action(description='Exportar PDF')
    def exportar_pdf(self, request, queryset):
        """Exporta clientes selecionados como PDF"""
        from core.utils.relatorios import gerar_relatorio_clientes_pdf
        filtros = {
            'tipo_relatorio': 'Selecionados',
            'filters': {k: v for k, v in request.GET.items() if k not in ['action', '_selected_action', 'csrfmiddlewaretoken', 'select_across', 'index']}
        }
        return gerar_relatorio_clientes_pdf(queryset, filtros=filtros)

    @action(description='Exportar Excel')
    def exportar_excel(self, request, queryset):
        """Exporta clientes selecionados como Excel"""
        from core.utils.relatorios import gerar_relatorio_clientes_excel
        filtros = {
            'tipo_relatorio': 'Selecionados',
            'filters': {k: v for k, v in request.GET.items() if k not in ['action', '_selected_action', 'csrfmiddlewaretoken', 'select_across', 'index']}
        }
        return gerar_relatorio_clientes_excel(queryset, filtros=filtros)


@admin.register(Fornecedor)
class FornecedorAdmin(UnfoldHistoryAdmin):
    """Admin para Fornecedor com Unfold customization"""
    list_display = ['numero', 'nome', 'estatuto', 'area', 'funcao', 'classificacao', 'email']
    list_filter = ['estatuto', 'area', 'funcao', 'classificacao', 'pais']
    search_fields = ['numero', 'nome', 'nif', 'email', 'area', 'funcao']
    ordering = ['-created_at']
    actions = ['delete_selected', 'exportar_pdf', 'exportar_excel']

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

    @action(description='Exportar PDF')
    def exportar_pdf(self, request, queryset):
        """Exporta fornecedores selecionados como PDF"""
        from core.utils.relatorios import gerar_relatorio_fornecedores_pdf
        filtros = {
            'tipo_relatorio': 'Selecionados',
            'filters': {k: v for k, v in request.GET.items() if k not in ['action', '_selected_action', 'csrfmiddlewaretoken', 'select_across', 'index']}
        }
        return gerar_relatorio_fornecedores_pdf(queryset, filtros=filtros)

    @action(description='Exportar Excel')
    def exportar_excel(self, request, queryset):
        """Exporta fornecedores selecionados como Excel"""
        from core.utils.relatorios import gerar_relatorio_fornecedores_excel
        filtros = {
            'tipo_relatorio': 'Selecionados',
            'filters': {k: v for k, v in request.GET.items() if k not in ['action', '_selected_action', 'csrfmiddlewaretoken', 'select_across', 'index']}
        }
        return gerar_relatorio_fornecedores_excel(queryset, filtros=filtros)


@admin.register(Projeto)
class ProjetoAdmin(UnfoldHistoryAdmin):
    """Admin para Projeto com Unfold customization"""
    list_display = ['numero', 'tipo', 'socio', 'descricao_short', 'cliente', 'valor_sem_iva', 'estado', 'data_projeto_formatted']
    list_filter = ['tipo', SocioListFilter, 'estado', 'data_faturacao']
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
    actions = ['delete_selected', 'exportar_pdf', 'exportar_excel']

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
            'fields': (('data_inicio', 'data_fim'), 'data_faturacao', 'data_vencimento', 'data_recibo'),
            'description': 'Período do projeto e datas de faturação/pagamento'
        }),
        ('Estado', {
            'fields': ('estado',)
        }),
        ('Informações Adicionais', {
            'fields': ('nota',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at', 'created_by', 'updated_by'),
            'classes': ['collapse']
        }),
    )

    @display(description='Descrição', ordering='descricao')
    def descricao_short(self, obj):
        """Mostra descrição truncada com tooltip"""
        if len(obj.descricao) > 50:
            truncated = obj.descricao[:50] + '...'
            return format_html('<span title="{}">{}</span>', obj.descricao, truncated)
        return obj.descricao

    @display(description='Data Projeto', ordering='data_inicio')
    def data_projeto_formatted(self, obj):
        """
        Mostra data do projeto no formato inteligente:
        - Mesmo dia: DD/MM/AAAA
        - Vários dias, mesmo mês: DD-DD/MM/AAAA
        - Atravessa meses: DD/MM-DD/MM/AAAA
        """
        if not obj.data_inicio:
            return '-'

        # Se não tem data fim, mostra só data início
        if not obj.data_fim:
            return obj.data_inicio.strftime('%d/%m/%Y')

        # Se é o mesmo dia
        if obj.data_inicio == obj.data_fim:
            return obj.data_inicio.strftime('%d/%m/%Y')

        # Se é o mesmo mês
        if obj.data_inicio.month == obj.data_fim.month and obj.data_inicio.year == obj.data_fim.year:
            return f"{obj.data_inicio.day}-{obj.data_fim.day}/{obj.data_inicio.month:02d}/{obj.data_inicio.year}"

        # Se atravessa meses (mesmo ano ou anos diferentes)
        return f"{obj.data_inicio.strftime('%d/%m')}-{obj.data_fim.strftime('%d/%m/%Y')}"

    @display(description='Data Faturação', ordering='data_faturacao')
    def data_faturacao_formatted(self, obj):
        """Mostra data de faturação no formato DD/MM/AAAA"""
        return obj.data_faturacao.strftime('%d/%m/%Y') if obj.data_faturacao else '-'

    @display(description='Data Pagamento', ordering='data_recibo')
    def data_recibo_formatted(self, obj):
        """Mostra data de pagamento no formato DD/MM/AAAA"""
        return obj.data_recibo.strftime('%d/%m/%Y') if obj.data_recibo else '-'

    @display(description='Criado em', ordering='created_at')
    def created_at_formatted(self, obj):
        """Mostra data de criação no formato DD/MM/AAAA"""
        return obj.created_at.strftime('%d/%m/%Y') if obj.created_at else '-'

    @action(description='Exportar PDF')
    def exportar_pdf(self, request, queryset):
        """Exporta projetos selecionados como PDF"""
        from core.utils.relatorios import gerar_relatorio_projetos_pdf
        filtros = {
            'tipo_relatorio': 'Selecionados',
            'filters': {k: v for k, v in request.GET.items() if k not in ['action', '_selected_action', 'csrfmiddlewaretoken', 'select_across', 'index']}
        }
        return gerar_relatorio_projetos_pdf(queryset, filtros=filtros)

    @action(description='Exportar Excel')
    def exportar_excel(self, request, queryset):
        """Exporta projetos selecionados como Excel"""
        from core.utils.relatorios import gerar_relatorio_projetos_excel
        filtros = {
            'tipo_relatorio': 'Selecionados',
            'filters': {k: v for k, v in request.GET.items() if k not in ['action', '_selected_action', 'csrfmiddlewaretoken', 'select_across', 'index']}
        }
        return gerar_relatorio_projetos_excel(queryset, filtros=filtros)

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
    """Admin para Despesas Fixas Mensais com Unfold customization"""
    list_display = ['ativa_icon', 'numero', 'descricao_short', 'credor', 'tags_display', 'valor_sem_iva', 'dia_mes', 'estado_default']
    list_filter = ['ativa', 'estado_default', 'dia_mes', 'tags']
    search_fields = ['numero', 'descricao', 'credor__nome']
    ordering = ['dia_mes', '-created_at']
    autocomplete_fields = ['credor', 'projeto', 'tag_irc', 'tag_iva', 'tag_irs', 'tag_tsu']
    filter_horizontal = ['tags']  # Melhor UX para ManyToMany

    fieldsets = (
        ('Identificação', {
            'fields': ('numero',)
        }),
        ('Categorização', {
            'fields': ('tags',),
            'description': 'Sistema moderno de categorização (substitui campo "tipo" deprecated)'
        }),
        ('Categorização Fiscal', {
            'fields': ('tag_irc', 'tag_iva', 'tag_irs', 'tag_tsu'),
            'description': 'Categorização fiscal automática conforme legislação 2026'
        }),
        ('Fornecedor/Projeto', {
            'fields': ('credor', 'projeto')
        }),
        ('Descrição', {
            'fields': ('descricao',)
        }),
        ('Valores', {
            'fields': ('valor_sem_iva', 'valor_com_iva', 'irs_retido', 'taxa_retencao_irs')
        }),
        ('Recorrência', {
            'fields': ('dia_mes', 'ativa', 'estado_default'),
            'description': 'Configuração da criação automática mensal'
        }),
        ('Informações Adicionais', {
            'fields': ('nota',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at', 'created_by', 'updated_by'),
            'classes': ['collapse']
        }),
    )

    @display(description='', ordering='ativa', boolean=True)
    def ativa_icon(self, obj):
        """Mostra ícone de ativo/inativo"""
        return obj.ativa

    @display(description='Descrição', ordering='descricao')
    def descricao_short(self, obj):
        """Mostra descrição truncada com tooltip"""
        if len(obj.descricao) > 40:
            truncated = obj.descricao[:40] + '...'
            return format_html('<span title="{}">{}</span>', obj.descricao, truncated)
        return obj.descricao

    @display(description='Tags')
    def tags_display(self, obj):
        """Mostra tags numa lista compacta"""
        tags = obj.tags.all()
        if not tags:
            return '-'
        tag_names = ', '.join([tag.nome for tag in tags[:3]])
        if obj.tags.count() > 3:
            tag_names += f' (+{obj.tags.count() - 3})'
        return tag_names


@admin.register(Despesa)
class DespesaAdmin(UnfoldHistoryAdmin):
    """Admin para Despesa com Unfold customization"""
    list_display = ['numero', 'tags_display', 'data_formatted', 'descricao_short', 'credor', 'valor_sem_iva', 'valor_com_iva', 'irs_retido', 'estado']
    list_filter = [TagListFilter, 'estado', 'data', 'data_pagamento']
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
    autocomplete_fields = ['credor', 'projeto', 'despesa_template', 'tag_irc', 'tag_iva', 'tag_irs', 'tag_tsu']
    date_hierarchy = 'data'
    filter_horizontal = ['tags']  # Interface melhor para ManyToMany
    actions = ['delete_selected', 'exportar_pdf', 'exportar_excel']

    fieldsets = (
        ('Identificação', {
            'fields': ('numero', 'data')
        }),
        ('Categorização', {
            'fields': ('tags', 'tipo_original')
        }),
        ('Categorização Fiscal', {
            'fields': ('tag_irc', 'tag_iva', 'tag_irs', 'tag_tsu'),
            'description': 'Categorização fiscal automática conforme legislação 2026'
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
        """Mostra descrição truncada com tooltip"""
        if len(obj.descricao) > 30:
            truncated = obj.descricao[:30] + '...'
            return format_html('<span title="{}">{}</span>', obj.descricao, truncated)
        return obj.descricao

    @display(description='Data', ordering='data')
    def data_formatted(self, obj):
        """Mostra data no formato DD/MM/AAAA"""
        return obj.data.strftime('%d/%m/%Y') if obj.data else '-'

    @display(description='Projeto', ordering='projeto__numero')
    def projeto_id_display(self, obj):
        """Mostra apenas o ID/número do projeto"""
        return obj.projeto.numero if obj.projeto else '-'

    @display(description='Data Pagamento', ordering='data_pagamento')
    def data_pagamento_formatted(self, obj):
        """Mostra data de pagamento no formato DD/MM/AAAA"""
        return obj.data_pagamento.strftime('%d/%m/%Y') if obj.data_pagamento else '-'

    @display(description='Criado em', ordering='created_at')
    def created_at_formatted(self, obj):
        """Mostra data de criação no formato DD/MM/AAAA"""
        return obj.created_at.strftime('%d/%m/%Y') if obj.created_at else '-'

    @action(description='Exportar PDF')
    def exportar_pdf(self, request, queryset):
        """Exporta despesas selecionadas como PDF"""
        from core.utils.relatorios import gerar_relatorio_despesas_pdf
        filtros = {
            'tipo_relatorio': 'Selecionadas',
            'filters': {k: v for k, v in request.GET.items() if k not in ['action', '_selected_action', 'csrfmiddlewaretoken', 'select_across', 'index']}
        }
        return gerar_relatorio_despesas_pdf(queryset, filtros=filtros)

    @action(description='Exportar Excel')
    def exportar_excel(self, request, queryset):
        """Exporta despesas selecionadas como Excel"""
        from core.utils.relatorios import gerar_relatorio_despesas_excel
        filtros = {
            'tipo_relatorio': 'Selecionadas',
            'filters': {k: v for k, v in request.GET.items() if k not in ['action', '_selected_action', 'csrfmiddlewaretoken', 'select_across', 'index']}
        }
        return gerar_relatorio_despesas_excel(queryset, filtros=filtros)


class BoletimLinhaInline(TabularInline):
    """Inline para linhas de boletim"""
    model = BoletimLinha
    extra = 1
    fields = ['ordem', 'projeto', 'servico', 'localidade', 'data_inicio', 'hora_inicio', 'data_fim', 'hora_fim', 'tipo', 'dias', 'kms']
    autocomplete_fields = ['projeto']


@admin.register(Boletim)
class BoletimAdmin(UnfoldHistoryAdmin):
    """Admin para Boletim com Unfold customization"""
    list_display = ['numero', 'socio', 'mes', 'ano', 'data_emissao_formatted', 'valor_total', 'total_ajudas_nacionais', 'total_ajudas_estrangeiro', 'total_kms', 'estado', 'data_pagamento_formatted']
    list_filter = [SocioListFilter, 'estado', 'mes', 'ano', 'data_emissao']
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
    actions = ['delete_selected', 'exportar_pdf', 'exportar_excel']

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

    @display(description='Data Emissão', ordering='data_emissao')
    def data_emissao_formatted(self, obj):
        """Mostra data de emissão no formato DD/MM/AAAA"""
        return obj.data_emissao.strftime('%d/%m/%Y') if obj.data_emissao else '-'

    @display(description='Data Pagamento', ordering='data_pagamento')
    def data_pagamento_formatted(self, obj):
        """Mostra data de pagamento no formato DD/MM/AAAA"""
        return obj.data_pagamento.strftime('%d/%m/%Y') if obj.data_pagamento else '-'

    @display(description='Criado em', ordering='created_at')
    def created_at_formatted(self, obj):
        """Mostra data de criação no formato DD/MM/AAAA"""
        return obj.created_at.strftime('%d/%m/%Y') if obj.created_at else '-'

    @action(description='Exportar PDF')
    def exportar_pdf(self, request, queryset):
        """Exporta boletins selecionados como PDF"""
        from core.utils.relatorios import gerar_relatorio_boletins_pdf
        filtros = {
            'tipo_relatorio': 'Selecionados',
            'filters': {k: v for k, v in request.GET.items() if k not in ['action', '_selected_action', 'csrfmiddlewaretoken', 'select_across', 'index']}
        }
        return gerar_relatorio_boletins_pdf(queryset, filtros=filtros)

    @action(description='Exportar Excel')
    def exportar_excel(self, request, queryset):
        """Exporta boletins selecionados como Excel"""
        from core.utils.relatorios import gerar_relatorio_boletins_excel
        filtros = {
            'tipo_relatorio': 'Selecionados',
            'filters': {k: v for k, v in request.GET.items() if k not in ['action', '_selected_action', 'csrfmiddlewaretoken', 'select_across', 'index']}
        }
        return gerar_relatorio_boletins_excel(queryset, filtros=filtros)


@admin.register(BoletimLinha)
class BoletimLinhaAdmin(ModelAdmin):
    """Admin para BoletimLinha com Unfold customization"""
    list_display = ['boletim', 'ordem', 'servico_short', 'localidade', 'projeto', 'data_inicio_formatted', 'data_fim_formatted', 'tipo', 'dias', 'kms']
    list_filter = ['tipo', 'data_inicio']
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
        """Mostra serviço truncado com tooltip"""
        if len(obj.servico) > 30:
            truncated = obj.servico[:30] + '...'
            return format_html('<span title="{}">{}</span>', obj.servico, truncated)
        return obj.servico

    @display(description='Data Início', ordering='data_inicio')
    def data_inicio_formatted(self, obj):
        """Mostra data de início no formato DD/MM/AAAA"""
        return obj.data_inicio.strftime('%d/%m/%Y') if obj.data_inicio else '-'

    @display(description='Data Fim', ordering='data_fim')
    def data_fim_formatted(self, obj):
        """Mostra data de fim no formato DD/MM/AAAA"""
        return obj.data_fim.strftime('%d/%m/%Y') if obj.data_fim else '-'

    @display(description='Criado em', ordering='created_at')
    def created_at_formatted(self, obj):
        """Mostra data de criação no formato DD/MM/AAAA"""
        return obj.created_at.strftime('%d/%m/%Y') if obj.created_at else '-'


@admin.register(Equipamento)
class EquipamentoAdmin(UnfoldHistoryAdmin):
    """Admin para Equipamento com Unfold customization"""
    list_display = ['numero', 'produto', 'tipo', 'estado', 'uso_pessoal', 'preco_aluguer', 'rendimento_acumulado']
    list_filter = ['estado', 'uso_pessoal', 'tipo']
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
    list_display = ['codigo', 'cliente', 'projeto', 'socio', 'data_criacao_formatted', 'valor_total', 'status']
    list_filter = ['status', SocioListFilter, 'data_criacao']
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
    actions = ['delete_selected', 'exportar_pdf', 'exportar_excel']
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

    @action(description='Exportar PDF')
    def exportar_pdf(self, request, queryset):
        """Exporta orçamentos selecionados como PDF"""
        from core.utils.relatorios import gerar_relatorio_orcamentos_pdf
        filtros = {
            'tipo_relatorio': 'Selecionados',
            'filters': {k: v for k, v in request.GET.items() if k not in ['action', '_selected_action', 'csrfmiddlewaretoken', 'select_across', 'index']}
        }
        return gerar_relatorio_orcamentos_pdf(queryset, filtros=filtros)

    @action(description='Exportar Excel')
    def exportar_excel(self, request, queryset):
        """Exporta orçamentos selecionados como Excel"""
        from core.utils.relatorios import gerar_relatorio_orcamentos_excel
        filtros = {
            'tipo_relatorio': 'Selecionados',
            'filters': {k: v for k, v in request.GET.items() if k not in ['action', '_selected_action', 'csrfmiddlewaretoken', 'select_across', 'index']}
        }
        return gerar_relatorio_orcamentos_excel(queryset, filtros=filtros)

    @display(description='Data Criação', ordering='data_criacao')
    def data_criacao_formatted(self, obj):
        """Mostra data de criação no formato DD/MM/AAAA"""
        return obj.data_criacao.strftime('%d/%m/%Y') if obj.data_criacao else '-'

    @display(description='Criado em', ordering='created_at')
    def created_at_formatted(self, obj):
        """Mostra data de criação no formato DD/MM/AAAA"""
        return obj.created_at.strftime('%d/%m/%Y') if obj.created_at else '-'


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
        """Mostra descrição truncada com tooltip"""
        if len(obj.descricao) > 50:
            truncated = obj.descricao[:50] + '...'
            return format_html('<span title="{}">{}</span>', obj.descricao, truncated)
        return obj.descricao


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

    def get_urls(self):
        """Adiciona URLs customizadas para páginas dedicadas"""
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('iva/', self.admin_site.admin_view(self.iva_view), name='core_fiscal_iva'),
            path('irs/', self.admin_site.admin_view(self.irs_view), name='core_fiscal_irs'),
            path('irc/', self.admin_site.admin_view(self.irc_view), name='core_fiscal_irc'),
        ]
        return custom_urls + urls

    def iva_view(self, request):
        """Página dedicada IVA com navegação trimestral"""
        from core.utils.fiscal import FiscalCalculator
        from core.models import Despesa, Projeto
        from datetime import datetime

        calculator = FiscalCalculator()
        hoje = datetime.now().date()

        ano = int(request.GET.get('ano', hoje.year))
        trimestre = int(request.GET.get('trimestre', ((hoje.month - 1) // 3) + 1))

        anos_despesas = Despesa.objects.dates('data', 'year', order='ASC').values_list('data__year', flat=True)
        anos_projetos = Projeto.objects.dates('data_inicio', 'year', order='ASC').values_list('data_inicio__year', flat=True)
        anos_disponiveis = sorted(set(list(anos_despesas) + list(anos_projetos)))

        iva = calculator.calcular_iva_trimestral(ano, trimestre)
        iva_breakdown = calculator.breakdown_iva_por_tags(ano, trimestre)

        context = {
            **self.admin_site.each_context(request),
            'title': 'IVA Trimestral',
            'ano_atual': ano,
            'trimestre_atual': trimestre,
            'anos_disponiveis': anos_disponiveis,
            'iva': iva,
            'iva_breakdown': iva_breakdown,
        }

        return render(request, 'admin/core/fiscal/iva.html', context)

    def irs_view(self, request):
        """Página dedicada IRS com navegação mensal"""
        from core.utils.fiscal import FiscalCalculator
        from core.models import Despesa, Projeto
        from datetime import datetime

        calculator = FiscalCalculator()
        hoje = datetime.now().date()

        ano = int(request.GET.get('ano', hoje.year))
        mes = int(request.GET.get('mes', hoje.month))

        anos_despesas = Despesa.objects.dates('data', 'year', order='ASC').values_list('data__year', flat=True)
        anos_projetos = Projeto.objects.dates('data_inicio', 'year', order='ASC').values_list('data_inicio__year', flat=True)
        anos_disponiveis = sorted(set(list(anos_despesas) + list(anos_projetos)))

        irs = calculator.calcular_irs_mensal(ano, mes)

        meses = [
            {'num': 1, 'nome': 'Janeiro'},
            {'num': 2, 'nome': 'Fevereiro'},
            {'num': 3, 'nome': 'Março'},
            {'num': 4, 'nome': 'Abril'},
            {'num': 5, 'nome': 'Maio'},
            {'num': 6, 'nome': 'Junho'},
            {'num': 7, 'nome': 'Julho'},
            {'num': 8, 'nome': 'Agosto'},
            {'num': 9, 'nome': 'Setembro'},
            {'num': 10, 'nome': 'Outubro'},
            {'num': 11, 'nome': 'Novembro'},
            {'num': 12, 'nome': 'Dezembro'},
        ]

        context = {
            **self.admin_site.each_context(request),
            'title': 'IRS Mensal',
            'ano_atual': ano,
            'mes_atual': mes,
            'anos_disponiveis': anos_disponiveis,
            'meses': meses,
            'irs': irs,
        }

        return render(request, 'admin/core/fiscal/irs.html', context)

    def irc_view(self, request):
        """Página dedicada IRC com navegação anual"""
        from core.utils.fiscal import FiscalCalculator
        from core.models import Despesa, Projeto
        from datetime import datetime

        calculator = FiscalCalculator()
        hoje = datetime.now().date()

        ano = int(request.GET.get('ano', hoje.year))

        anos_despesas = Despesa.objects.dates('data', 'year', order='ASC').values_list('data__year', flat=True)
        anos_projetos = Projeto.objects.dates('data_inicio', 'year', order='ASC').values_list('data_inicio__year', flat=True)
        anos_disponiveis = sorted(set(list(anos_despesas) + list(anos_projetos)))

        irc = calculator.estimar_irc_anual(ano)
        irc_breakdown = calculator.breakdown_irc_por_tags(ano)

        context = {
            **self.admin_site.each_context(request),
            'title': 'IRC Anual',
            'ano_atual': ano,
            'anos_disponiveis': anos_disponiveis,
            'irc': irc,
            'irc_breakdown': irc_breakdown,
        }

        return render(request, 'admin/core/fiscal/irc.html', context)

    def changelist_view(self, request, extra_context=None):
        """Vista personalizada para mostrar dashboard fiscal"""
        from django.shortcuts import render
        from core.utils.fiscal import FiscalCalculator
        from datetime import date
        from core.models import Despesa, Projeto

        calculator = FiscalCalculator()
        hoje = date.today()

        # Get year and trimestre from URL parameters
        ano_param = request.GET.get('ano')
        trimestre_param = request.GET.get('trimestre')

        # Determine current values
        mes_atual = hoje.month
        trimestre_atual_real = (mes_atual - 1) // 3 + 1

        ano_selecionado = int(ano_param) if ano_param else hoje.year
        trimestre_selecionado = int(trimestre_param) if trimestre_param else None
        trimestre_atual = trimestre_selecionado if trimestre_selecionado else trimestre_atual_real

        # Get available years from database (years with despesas or projetos)
        anos_despesas = Despesa.objects.dates('data', 'year', order='ASC').values_list('data__year', flat=True)
        anos_projetos = Projeto.objects.dates('data_inicio', 'year', order='ASC').values_list('data_inicio__year', flat=True)
        anos_disponiveis = sorted(set(list(anos_despesas) + list(anos_projetos)))

        # If no data, default to current year
        if not anos_disponiveis:
            anos_disponiveis = [hoje.year]

        # Build date_hierarchy context (Unfold format)
        date_hierarchy_context = {'show': True}

        if trimestre_param:
            # Level 2: Quarter selected - show back to year
            date_hierarchy_context['back'] = {
                'link': f'?ano={ano_selecionado}',
                'title': str(ano_selecionado)
            }
            date_hierarchy_context['choices'] = [
                {'title': f'Q{trimestre_param}', 'link': None}  # Current level, no link
            ]
        elif ano_param:
            # Level 1: Year selected - show back to root + quarters
            date_hierarchy_context['back'] = {
                'link': '?',
                'title': 'Todos os anos'
            }
            date_hierarchy_context['choices'] = [
                {'title': str(ano_selecionado), 'link': None},  # Current year, no link
            ] + [
                {'title': f'Q{q}', 'link': f'?ano={ano_selecionado}&trimestre={q}'}
                for q in [1, 2, 3, 4]
            ]
        else:
            # Level 0: Root - show all years
            date_hierarchy_context['choices'] = [
                {'title': str(ano), 'link': f'?ano={ano}'}
                for ano in anos_disponiveis
            ]

        # Calcular IVA (trimestre específico ou ano completo)
        if trimestre_selecionado:
            iva = calculator.calcular_iva_trimestral(ano_selecionado, trimestre_selecionado)
            iva_breakdown = calculator.breakdown_iva_por_tags(ano_selecionado, trimestre_selecionado)
        else:
            # Ano completo
            iva = calculator.calcular_iva_anual(ano_selecionado)
            iva_breakdown = calculator.breakdown_iva_por_tags(ano_selecionado, None)

        # Calcular IRS Mensal (mês atual)
        irs = calculator.calcular_irs_mensal(ano_selecionado, mes_atual)

        # Estimar IRC Anual (ano selecionado)
        irc = calculator.estimar_irc_anual(ano_selecionado)

        # Próximas obrigações
        obrigacoes = calculator.proximas_obrigacoes()

        # Breakdown IRC
        irc_breakdown = calculator.breakdown_irc_por_tags(ano_selecionado)

        context = {
            **self.admin_site.each_context(request),
            'title': 'Estado Fiscal',
            'ano_atual': ano_selecionado,
            'ano_selecionado': ano_selecionado,
            'trimestre_selecionado': trimestre_selecionado,  # None if viewing all year
            'mes_atual': mes_atual,
            'trimestre_atual': trimestre_atual,
            'iva': iva,
            'irs': irs,
            'irc': irc,
            'obrigacoes': obrigacoes[:5],  # Próximas 5 obrigações
            'iva_breakdown': iva_breakdown,
            'irc_breakdown': irc_breakdown,
            'date_hierarchy': date_hierarchy_context,  # Unfold date_hierarchy format
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


@admin.register(Documentacao)
class DocumentacaoAdmin(ModelAdmin):
    """Admin para Centro de Documentação"""

    # Documentation structure
    DOCS_STRUCTURE = {
        'overview': {
            'title': 'Visão Geral',
            'icon': 'info',
            'file': 'README.md',
            'description': 'Visão geral do projeto Agora Contabilidade'
        },
        'changelog': {
            'title': 'Changelog',
            'icon': 'history',
            'file': 'CHANGELOG.md',
            'description': 'Histórico completo de versões e alterações'
        },
        'database-manual': {
            'title': 'Alterações Manuais BD',
            'icon': 'build',
            'file': 'docs/DATABASE_MANUAL_CHANGES.md',
            'description': 'Histórico de alterações manuais na base de dados'
        },
        'docs-index': {
            'title': 'Índice da Documentação',
            'icon': 'list',
            'file': 'docs/README.md',
            'description': 'Índice completo da documentação do projeto'
        },
        'excel-import': {
            'title': 'Importação Excel',
            'icon': 'upload_file',
            'file': 'docs/EXCEL_IMPORT_ANALYSIS.md',
            'description': 'Análise do sistema de importação de dados via Excel'
        },
        'import-system': {
            'title': 'Sistema de Importação',
            'icon': 'cloud_upload',
            'file': 'docs/IMPORT_SYSTEM.md',
            'description': 'Documentação do sistema de importação'
        },
        'pwa': {
            'title': 'PWA & Branding',
            'icon': 'install_mobile',
            'file': 'docs/PWA_BRANDING.md',
            'description': 'Progressive Web App e configuração de branding'
        },
        'saldos-dashboard': {
            'title': 'Dashboard de Saldos',
            'icon': 'dashboard',
            'file': 'docs/SALDOS_DASHBOARD.md',
            'description': 'Documentação do dashboard de saldos pessoais'
        },
        'saldos-revision': {
            'title': 'Revisão de Saldos',
            'icon': 'fact_check',
            'file': 'docs/SALDOS_REVISION_SPEC.md',
            'description': 'Especificação para revisão da lógica de saldos'
        },
        'socios': {
            'title': 'Migração de Sócios',
            'icon': 'people',
            'file': 'docs/SOCIOS_MIGRATION.md',
            'description': 'Documentação da migração do modelo Socio'
        },
        'audit-trail': {
            'title': 'Audit Trail',
            'icon': 'history_edu',
            'file': 'docs/audit-trail-implementation.md',
            'description': 'Implementação do sistema de auditoria'
        },
        'claude': {
            'title': 'Contexto IA (Claude)',
            'icon': 'smart_toy',
            'file': '.claude/claude.md',
            'description': 'Contexto e instruções para assistente IA'
        },
        'logo-cleanup': {
            'title': 'Logo & Branding Cleanup',
            'icon': 'palette',
            'file': 'docs/LOGO_BRANDING_CLEANUP.md',
            'description': 'Limpeza e configuração de logos e favicons'
        },
        'fiscal-system': {
            'title': 'Sistema Fiscal',
            'icon': 'account_balance',
            'file': 'docs/FISCAL_SYSTEM_GUIDE.md',
            'description': 'Sistema de categorização fiscal completo (IRC, IVA, IRS, TSU)'
        },
        'fiscal-dashboard': {
            'title': 'Dashboard Fiscal',
            'icon': 'assessment',
            'file': 'docs/FISCAL_DASHBOARD.md',
            'description': 'Dashboard fiscal integrado com IVA/IRS/IRC'
        },
        'respostas-contabilista': {
            'title': 'Respostas do Contabilista',
            'icon': 'question_answer',
            'file': 'docs/RESPOSTAS_CONTABILISTA.md',
            'description': 'Respostas do contabilista sobre categorização fiscal'
        },
    }

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def get_urls(self):
        """Adiciona URLs customizadas para documentação"""
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('', self.admin_site.admin_view(self.docs_index_view), name='core_documentacao_index'),
            path('<str:doc_key>/', self.admin_site.admin_view(self.docs_detail_view), name='core_documentacao_detail'),
        ]
        return custom_urls + urls

    def get_doc_path(self, doc_key):
        """Get absolute path for a documentation file."""
        from django.conf import settings

        if doc_key not in self.DOCS_STRUCTURE:
            return None

        file_path = self.DOCS_STRUCTURE[doc_key]['file']

        # Build absolute path based on file location
        if file_path == 'README.md':
            return settings.DOCS_CONFIG['MAIN_README']
        elif file_path == 'CHANGELOG.md':
            return settings.DOCS_CONFIG['CHANGELOG']
        elif file_path == '.claude/claude.md':
            return settings.DOCS_CONFIG['CLAUDE_MD']
        else:
            # docs/ folder
            return settings.DOCS_CONFIG['ROOT_PATH'] / file_path.replace('docs/', '')

    def convert_md_links_to_urls(self, html):
        """Convert .md file links to documentation URLs."""
        import re

        # Mapeamento de ficheiros .md para doc_key
        md_to_key = {
            'README.md': 'overview',
            '../README.md': 'overview',
            'CHANGELOG.md': 'changelog',
            '../CHANGELOG.md': 'changelog',
            'docs/README.md': 'docs-index',
            './README.md': 'docs-index',
            'DATABASE_MANUAL_CHANGES.md': 'database-manual',
            './DATABASE_MANUAL_CHANGES.md': 'database-manual',
            'docs/DATABASE_MANUAL_CHANGES.md': 'database-manual',
            'EXCEL_IMPORT_ANALYSIS.md': 'excel-import',
            './EXCEL_IMPORT_ANALYSIS.md': 'excel-import',
            'IMPORT_SYSTEM.md': 'import-system',
            './IMPORT_SYSTEM.md': 'import-system',
            'PWA_BRANDING.md': 'pwa',
            './PWA_BRANDING.md': 'pwa',
            'SALDOS_DASHBOARD.md': 'saldos-dashboard',
            './SALDOS_DASHBOARD.md': 'saldos-dashboard',
            'SALDOS_REVISION_SPEC.md': 'saldos-revision',
            './SALDOS_REVISION_SPEC.md': 'saldos-revision',
            'SOCIOS_MIGRATION.md': 'socios',
            './SOCIOS_MIGRATION.md': 'socios',
            'audit-trail-implementation.md': 'audit-trail',
            './audit-trail-implementation.md': 'audit-trail',
            'LOGO_BRANDING_CLEANUP.md': 'logo-cleanup',
            './LOGO_BRANDING_CLEANUP.md': 'logo-cleanup',
            'FISCAL_SYSTEM_GUIDE.md': 'fiscal-system',
            './FISCAL_SYSTEM_GUIDE.md': 'fiscal-system',
            'FISCAL_DASHBOARD.md': 'fiscal-dashboard',
            './FISCAL_DASHBOARD.md': 'fiscal-dashboard',
            'RESPOSTAS_CONTABILISTA.md': 'respostas-contabilista',
            './RESPOSTAS_CONTABILISTA.md': 'respostas-contabilista',
            'claude.md': 'claude',
            '.claude/claude.md': 'claude',
            '../.claude/claude.md': 'claude',
        }

        pattern = r'href="([^"]+\.md)(#[^"]*)?\"'

        def replace_link(match):
            file_path = match.group(1)
            anchor = match.group(2) or ''

            if file_path in md_to_key:
                doc_key = md_to_key[file_path]
                return f'href="/admin/core/documentacao/{doc_key}/{anchor}"'

            return match.group(0)

        html = re.sub(pattern, replace_link, html)
        return html

    def render_markdown(self, content):
        """Render markdown to HTML with syntax highlighting and TOC."""
        import markdown
        from markdown.extensions.codehilite import CodeHiliteExtension
        from markdown.extensions.toc import TocExtension

        md = markdown.Markdown(extensions=[
            'fenced_code',
            'tables',
            'nl2br',
            CodeHiliteExtension(
                linenums=False,
                guess_lang=True,
                css_class='highlight'
            ),
            TocExtension(
                title='Índice',
                toc_depth='2-4'
            ),
        ])

        html = md.convert(content)
        toc = md.toc if hasattr(md, 'toc') else ''

        # Converter links .md para URLs do sistema de documentação
        html = self.convert_md_links_to_urls(html)

        return html, toc

    def extract_title(self, content):
        """Extract first H1 from markdown content."""
        import re
        match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        return match.group(1) if match else 'Documentação'

    def docs_index_view(self, request):
        """Documentation center index page."""
        from django.shortcuts import render
        from django.conf import settings

        # Group docs by category
        categories = {
            'Geral': ['overview', 'changelog', 'docs-index'],
            'Técnico': ['database-manual', 'saldos-dashboard', 'saldos-revision', 'socios', 'audit-trail'],
            'Features': ['excel-import', 'import-system', 'pwa', 'logo-cleanup'],
            'Fiscal': ['fiscal-system', 'fiscal-dashboard', 'respostas-contabilista'],
            'Suporte': ['claude'],
        }

        docs_by_category = {}
        for category, doc_keys in categories.items():
            docs_by_category[category] = [
                {**self.DOCS_STRUCTURE[key], 'key': key}
                for key in doc_keys
                if key in self.DOCS_STRUCTURE
            ]

        context = {
            **self.admin_site.each_context(request),
            'title': 'Centro de Documentação',
            'docs_by_category': docs_by_category,
            'github_repo': settings.DOCS_CONFIG['GITHUB_REPO'],
        }

        return render(request, 'admin/core/documentacao/index.html', context)

    def docs_detail_view(self, request, doc_key):
        """View a specific documentation page."""
        from django.shortcuts import render
        from django.http import Http404
        from django.conf import settings

        if doc_key not in self.DOCS_STRUCTURE:
            raise Http404("Documentação não encontrada")

        doc_info = self.DOCS_STRUCTURE[doc_key]
        doc_path = self.get_doc_path(doc_key)

        if not doc_path or not doc_path.exists():
            context = {
                **self.admin_site.each_context(request),
                'title': doc_info['title'],
                'doc_key': doc_key,
                'error': f"Ficheiro não encontrado: {doc_path}",
            }
            return render(request, 'admin/core/documentacao/document.html', context)

        try:
            with open(doc_path, 'r', encoding='utf-8') as f:
                content = f.read()

            html, toc = self.render_markdown(content)
            title = self.extract_title(content) or doc_info['title']

            # Generate GitHub edit URL
            github_edit_url = (
                f"https://github.com/{settings.DOCS_CONFIG['GITHUB_REPO']}/edit/"
                f"{settings.DOCS_CONFIG['GITHUB_BRANCH']}/{doc_info['file']}"
            )

            context = {
                **self.admin_site.each_context(request),
                'title': title,
                'doc_key': doc_key,
                'doc_info': doc_info,
                'content_html': html,
                'toc_html': toc,
                'github_edit_url': github_edit_url,
                'all_docs': self.DOCS_STRUCTURE,
            }

            return render(request, 'admin/core/documentacao/document.html', context)

        except Exception as e:
            context = {
                **self.admin_site.each_context(request),
                'title': doc_info['title'],
                'doc_key': doc_key,
                'error': f"Erro ao ler ficheiro: {str(e)}",
            }
            return render(request, 'admin/core/documentacao/document.html', context)
