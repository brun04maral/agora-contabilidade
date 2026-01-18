# Generated manually for DespesaTemplate improvements
from django.conf import settings
from django.db import migrations, models
import django.core.validators
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0010_add_angariador_to_cliente'),
    ]

    operations = [
        # ========== STEP 1: Criar modelo histórico PRIMEIRO ==========
        migrations.CreateModel(
            name='HistoricalDespesaTemplate',
            fields=[
                ('id', models.BigIntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('numero', models.CharField(db_index=True, help_text='Código único', max_length=20, verbose_name='Número')),
                ('tipo', models.CharField(blank=True, choices=[('FIXA_MENSAL', 'Fixa Mensal'), ('PESSOAL_BA', 'Pessoal BA'), ('PESSOAL_RR', 'Pessoal RR'), ('EQUIPAMENTO', 'Equipamento'), ('PROJETO', 'Projeto')], db_index=True, default='FIXA_MENSAL', help_text='Campo antigo - usar tags em vez disto', max_length=20, null=True, verbose_name='Tipo (deprecated)')),
                ('descricao', models.TextField(help_text='Descrição da despesa', verbose_name='Descrição')),
                ('valor_sem_iva', models.DecimalField(decimal_places=2, help_text='Valor sem IVA', max_digits=10, verbose_name='Valor s/ IVA')),
                ('valor_com_iva', models.DecimalField(decimal_places=2, help_text='Valor com IVA', max_digits=10, verbose_name='Valor c/ IVA')),
                ('irs_retido', models.DecimalField(blank=True, decimal_places=2, help_text='Valor de IRS retido (se aplicável)', max_digits=10, null=True, verbose_name='IRS Retido')),
                ('taxa_retencao_irs', models.DecimalField(blank=True, decimal_places=2, help_text='Taxa de retenção IRS (%)', max_digits=5, null=True, verbose_name='Taxa Retenção IRS')),
                ('dia_mes', models.IntegerField(help_text='Dia do mês para criação automática (1-28)', verbose_name='Dia do Mês')),
                ('nota', models.TextField(blank=True, help_text='Notas adicionais', null=True, verbose_name='Nota')),
                ('created_at', models.DateTimeField(blank=True, editable=False, verbose_name='Criado em')),
                ('updated_at', models.DateTimeField(blank=True, editable=False, verbose_name='Atualizado em')),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('created_by', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='Criado por')),
                ('credor', models.ForeignKey(blank=True, db_constraint=False, help_text='Fornecedor da despesa', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='core.fornecedor', verbose_name='Credor')),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('projeto', models.ForeignKey(blank=True, db_constraint=False, help_text='Projeto relacionado (opcional)', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='core.projeto', verbose_name='Projeto')),
                ('updated_by', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='Atualizado por')),
            ],
            options={
                'verbose_name': 'historical Despesa Fixa Mensal',
                'verbose_name_plural': 'historical Despesas Fixas Mensais',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
        ),

        # ========== STEP 2: Adicionar campo 'ativa' ==========
        migrations.AddField(
            model_name='despesatemplate',
            name='ativa',
            field=models.BooleanField(
                default=True,
                help_text='Se desativada, não cria despesas automaticamente',
                verbose_name='Ativa'
            ),
        ),
        migrations.AddField(
            model_name='historicaldespesatemplate',
            name='ativa',
            field=models.BooleanField(
                default=True,
                help_text='Se desativada, não cria despesas automaticamente',
                verbose_name='Ativa'
            ),
        ),

        # ========== STEP 3: Adicionar campo 'estado_default' ==========
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

        # ========== STEP 4: Adicionar validators ao dia_mes ==========
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

        # ========== STEP 5: Adicionar ManyToMany tags ==========
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

        # ========== STEP 6: Marcar 'tipo' como deprecated ==========
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

        # ========== STEP 7: Atualizar Meta options ==========
        migrations.AlterModelOptions(
            name='despesatemplate',
            options={
                'ordering': ['dia_mes', '-created_at'],
                'verbose_name': 'Despesa Fixa Mensal',
                'verbose_name_plural': 'Despesas Fixas Mensais'
            },
        ),
    ]
