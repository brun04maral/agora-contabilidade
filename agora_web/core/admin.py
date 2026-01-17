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
    Equipamento, Orcamento, OrcamentoSecao, OrcamentoItem, OrcamentoReparticao, Saldo, Fiscal, ImportacaoDados
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
    autocomplete_fields = ['credor', 'projeto']
    filter_horizontal = ['tags']  # Melhor UX para ManyToMany

    fieldsets = (
        ('Identificação', {
            'fields': ('numero',)
        }),
        ('Categorização', {
            'fields': ('tags',),
            'description': 'Sistema moderno de categorização (substitui campo "tipo" deprecated)'
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
    list_display = ['numero', 'tags_display', 'data_formatted', 'descricao_short', 'credor', 'projeto_id_display', 'valor_sem_iva', 'valor_com_iva', 'irs_retido', 'estado']
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
    autocomplete_fields = ['credor', 'projeto', 'despesa_template']
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
