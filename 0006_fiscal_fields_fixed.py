# Generated manually - clean migration for fiscal fields

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_fiscal_system'),
    ]

    operations = [
        # Rename old 'socio' field to 'socio_codigo' in Boletim
        migrations.RenameField(
            model_name='boletim',
            old_name='socio',
            new_name='socio_codigo',
        ),
        # Alter socio_codigo to allow null and add default
        migrations.AlterField(
            model_name='boletim',
            name='socio_codigo',
            field=models.CharField(
                blank=True,
                choices=[('BA', 'Bruno Amaral'), ('RR', 'Rafael Reigota')],
                db_index=True,
                default='BA',
                max_length=2,
                null=True,
                verbose_name='Sócio (código)'
            ),
        ),
        # NOTE: The AddField for boletim.socio ForeignKey was moved to migration 0007
        # (after Socio model is created) to avoid circular dependency

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
