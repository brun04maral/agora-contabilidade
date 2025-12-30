# Generated manually for Fiscal System

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_add_irs_retido_to_despesas'),
    ]

    operations = [
        # Add taxa_retencao_irs to Despesa
        migrations.AddField(
            model_name='despesa',
            name='taxa_retencao_irs',
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                default=0,
                help_text='Taxa aplicada (23%, 25%, 16.5%, etc)',
                max_digits=5,
                null=True,
                verbose_name='Taxa Retenção IRS'
            ),
        ),
        # Add taxa_retencao_irs to DespesaTemplate
        migrations.AddField(
            model_name='despesatemplate',
            name='taxa_retencao_irs',
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                default=0,
                help_text='Taxa aplicada (23%, 25%, 16.5%, etc)',
                max_digits=5,
                null=True,
                verbose_name='Taxa Retenção IRS'
            ),
        ),
        # Add taxa_retencao_irs to Fornecedor
        migrations.AddField(
            model_name='fornecedor',
            name='taxa_retencao_irs',
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                default=23.00,
                help_text='Taxa de retenção aplicável (23%, 25%, 16.5%, etc). Apenas para FREELANCER',
                max_digits=5,
                null=True,
                verbose_name='Taxa Retenção IRS'
            ),
        ),
    ]
