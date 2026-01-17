# Generated manually for DespesaTemplate improvements
from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_add_angariador_to_cliente'),
    ]

    operations = [
        # Adicionar campo 'ativa' ao DespesaTemplate
        migrations.AddField(
            model_name='despesatemplate',
            name='ativa',
            field=models.BooleanField(
                default=True,
                help_text='Se desativada, não cria despesas automaticamente',
                verbose_name='Ativa'
            ),
        ),
        # Adicionar campo 'ativa' à tabela histórica
        migrations.AddField(
            model_name='historicaldespesatemplate',
            name='ativa',
            field=models.BooleanField(
                default=True,
                help_text='Se desativada, não cria despesas automaticamente',
                verbose_name='Ativa'
            ),
        ),
        # Adicionar campo 'estado_default' ao DespesaTemplate
        migrations.AddField(
            model_name='despesatemplate',
            name='estado_default',
            field=models.CharField(
                choices=[
                    ('PENDENTE', 'Pendente'),
                    ('VENCIDO', 'Vencido'),
                    ('PAGO', 'Pago')
                ],
                default='PENDENTE',
                help_text='Estado que as despesas criadas terão',
                max_length=20,
                verbose_name='Estado Default'
            ),
        ),
        # Adicionar campo 'estado_default' à tabela histórica
        migrations.AddField(
            model_name='historicaldespesatemplate',
            name='estado_default',
            field=models.CharField(
                choices=[
                    ('PENDENTE', 'Pendente'),
                    ('VENCIDO', 'Vencido'),
                    ('PAGO', 'Pago')
                ],
                default='PENDENTE',
                help_text='Estado que as despesas criadas terão',
                max_length=20,
                verbose_name='Estado Default'
            ),
        ),
        # Adicionar validators ao campo dia_mes
        migrations.AlterField(
            model_name='despesatemplate',
            name='dia_mes',
            field=models.IntegerField(
                help_text='Dia do mês para criação automática (1-28)',
                validators=[
                    django.core.validators.MinValueValidator(1),
                    django.core.validators.MaxValueValidator(28)
                ],
                verbose_name='Dia do Mês'
            ),
        ),
        # Adicionar ManyToMany para tags
        migrations.AddField(
            model_name='despesatemplate',
            name='tags',
            field=models.ManyToManyField(
                blank=True,
                help_text='Tags que categorizam esta despesa (ex: Equipamento, Pessoal)',
                related_name='templates',
                to='core.tagdespesa',
                verbose_name='Tags'
            ),
        ),
        # Atualizar tipo para deprecated
        migrations.AlterField(
            model_name='despesatemplate',
            name='tipo',
            field=models.CharField(
                blank=True,
                choices=[
                    ('FIXA_MENSAL', 'Fixa Mensal'),
                    ('PESSOAL_BA', 'Pessoal BA'),
                    ('PESSOAL_RR', 'Pessoal RR'),
                    ('EQUIPAMENTO', 'Equipamento'),
                    ('PROJETO', 'Projeto')
                ],
                db_index=True,
                default='FIXA_MENSAL',
                help_text='Campo antigo - usar tags em vez disto',
                max_length=20,
                null=True,
                verbose_name='Tipo (deprecated)'
            ),
        ),
        # Atualizar Meta.verbose_name e verbose_name_plural
        migrations.AlterModelOptions(
            name='despesatemplate',
            options={
                'ordering': ['dia_mes', '-created_at'],
                'verbose_name': 'Despesa Fixa Mensal',
                'verbose_name_plural': 'Despesas Fixas Mensais'
            },
        ),
    ]
