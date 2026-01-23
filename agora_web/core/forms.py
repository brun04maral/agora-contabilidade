# -*- coding: utf-8 -*-
"""
Formulários personalizados para Agora Contabilidade
"""
from django import forms
from django.utils.translation import gettext_lazy as _
from .models import TipoProjeto, Socio


class RelatorioProjetosForm(forms.Form):
    """
    Formulário para geração de relatórios personalizados de projetos
    """

    TIPO_RELATORIO_CHOICES = [
        ('simples', 'Relatório Simples'),
        ('detalhado', 'Relatório Detalhado'),
        ('fiscal', 'Relatório Fiscal'),
    ]

    FORMATO_CHOICES = [
        ('pdf', 'PDF'),
        ('excel', 'Excel'),
    ]

    AGRUPAMENTO_CHOICES = [
        ('nenhum', 'Sem Agrupamento'),
        ('socio', 'Por Sócio'),
        ('cliente', 'Por Cliente'),
        ('mes', 'Por Mês'),
        ('cancelado', 'Por Estado (Ativo/Cancelado)'),
    ]

    # Tipo de relatório
    tipo_relatorio = forms.ChoiceField(
        label='Tipo de Relatório',
        choices=TIPO_RELATORIO_CHOICES,
        initial='simples',
        widget=forms.RadioSelect,
        help_text='Escolha o tipo de relatório que deseja gerar'
    )

    # Formato
    formato = forms.ChoiceField(
        label='Formato',
        choices=FORMATO_CHOICES,
        initial='pdf',
        widget=forms.RadioSelect,
        help_text='Escolha o formato de exportação'
    )

    # Filtros
    socio = forms.ModelChoiceField(
        label='Sócio',
        queryset=Socio.objects.all(),
        required=False,
        empty_label='Todos',
        help_text='Filtrar por sócio responsável'
    )

    tipo = forms.ChoiceField(
        label='Tipo de Projeto',
        choices=[('', 'Todos')] + list(TipoProjeto.choices),
        required=False,
        help_text='Filtrar por tipo de projeto'
    )

    cancelado = forms.ChoiceField(
        label='Estado',
        choices=[
            ('', 'Todos'),
            ('ativo', 'Ativos'),
            ('cancelado', 'Cancelados')
        ],
        required=False,
        help_text='Filtrar por estado do projeto'
    )

    cliente = forms.CharField(
        label='Cliente',
        max_length=100,
        required=False,
        help_text='Nome do cliente (busca parcial)',
        widget=forms.TextInput(attrs={'placeholder': 'Digite o nome do cliente...'})
    )

    # Período
    data_inicio = forms.DateField(
        label='Data Início',
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'}),
        help_text='Data de início do período (faturação)'
    )

    data_fim = forms.DateField(
        label='Data Fim',
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'}),
        help_text='Data de fim do período (faturação)'
    )

    # Agrupamento
    agrupamento = forms.ChoiceField(
        label='Agrupamento',
        choices=AGRUPAMENTO_CHOICES,
        initial='nenhum',
        required=False,
        help_text='Como agrupar os dados no relatório'
    )

    # Incluir campos adicionais
    incluir_premios = forms.BooleanField(
        label='Incluir Prémios',
        initial=True,
        required=False,
        help_text='Mostrar campos de prémios (Bruno/Rafael)'
    )

    incluir_datas = forms.BooleanField(
        label='Incluir Datas Completas',
        initial=True,
        required=False,
        help_text='Mostrar datas de início, fim, vencimento'
    )

    def clean(self):
        """Validação customizada"""
        cleaned_data = super().clean()
        data_inicio = cleaned_data.get('data_inicio')
        data_fim = cleaned_data.get('data_fim')

        # Validar que data_fim > data_inicio
        if data_inicio and data_fim and data_fim < data_inicio:
            raise forms.ValidationError(
                'Data de fim deve ser posterior à data de início.'
            )

        return cleaned_data
