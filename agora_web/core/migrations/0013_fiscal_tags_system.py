# Generated manually for Fiscal Tags System
from django.db import migrations, models
import django.db.models.deletion
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0012_despesatemplate_improvements'),
    ]

    operations = [
        # Criar modelos de tags fiscais (SEM histórico - django-simple-history cuida disso)
        migrations.CreateModel(
            name='TagIRC',
            fields=[
                ('codigo', models.CharField(
                    help_text='Código único (ex: IRC_DEDUTIVEL_100, IRC_NAO_DEDUTIVEL)',
                    max_length=50,
                    primary_key=True,
                    serialize=False,
                    unique=True,
                    verbose_name='Código'
                )),
                ('nome', models.CharField(help_text='Nome apresentável', max_length=100, verbose_name='Nome')),
                ('descricao', models.TextField(blank=True, help_text='Descrição detalhada da categoria', null=True, verbose_name='Descrição')),
                ('percentagem_dedutivel', models.DecimalField(
                    decimal_places=2,
                    default=0,
                    help_text='Percentagem dedutível (0-100%)',
                    max_digits=5,
                    validators=[
                        django.core.validators.MinValueValidator(0),
                        django.core.validators.MaxValueValidator(100)
                    ],
                    verbose_name='% Dedutível'
                )),
                ('ordem', models.IntegerField(default=0, verbose_name='Ordem')),
            ],
            options={
                'verbose_name': 'Tag IRC',
                'verbose_name_plural': 'Tags IRC',
                'ordering': ['ordem', 'nome'],
                'db_table': 'tags_irc',
            },
        ),
        migrations.CreateModel(
            name='TagIVA',
            fields=[
                ('codigo', models.CharField(
                    help_text='Código único (ex: IVA_DEDUTIVEL_100, IVA_NAO_DEDUTIVEL)',
                    max_length=50,
                    primary_key=True,
                    serialize=False,
                    unique=True,
                    verbose_name='Código'
                )),
                ('nome', models.CharField(help_text='Nome apresentável', max_length=100, verbose_name='Nome')),
                ('descricao', models.TextField(blank=True, help_text='Descrição detalhada da categoria', null=True, verbose_name='Descrição')),
                ('percentagem_dedutivel', models.DecimalField(
                    decimal_places=2,
                    default=0,
                    help_text='Percentagem de IVA dedutível (0-100%)',
                    max_digits=5,
                    validators=[
                        django.core.validators.MinValueValidator(0),
                        django.core.validators.MaxValueValidator(100)
                    ],
                    verbose_name='% Dedutível'
                )),
                ('ordem', models.IntegerField(default=0, verbose_name='Ordem')),
            ],
            options={
                'verbose_name': 'Tag IVA',
                'verbose_name_plural': 'Tags IVA',
                'ordering': ['ordem', 'nome'],
                'db_table': 'tags_iva',
            },
        ),
        migrations.CreateModel(
            name='TagIRS',
            fields=[
                ('codigo', models.CharField(
                    help_text='Código único (ex: IRS_ISENTO, IRS_RETENCAO_TRABALHO)',
                    max_length=50,
                    primary_key=True,
                    serialize=False,
                    unique=True,
                    verbose_name='Código'
                )),
                ('nome', models.CharField(help_text='Nome apresentável', max_length=100, verbose_name='Nome')),
                ('descricao', models.TextField(blank=True, help_text='Descrição detalhada da categoria', null=True, verbose_name='Descrição')),
                ('taxa_retencao_default', models.DecimalField(
                    decimal_places=2,
                    default=0,
                    help_text='Taxa de retenção padrão (pode ser sobreposta por cada despesa)',
                    max_digits=5,
                    validators=[
                        django.core.validators.MinValueValidator(0),
                        django.core.validators.MaxValueValidator(100)
                    ],
                    verbose_name='Taxa Retenção Default'
                )),
                ('ordem', models.IntegerField(default=0, verbose_name='Ordem')),
            ],
            options={
                'verbose_name': 'Tag IRS',
                'verbose_name_plural': 'Tags IRS',
                'ordering': ['ordem', 'nome'],
                'db_table': 'tags_irs',
            },
        ),
        migrations.CreateModel(
            name='TagTSU',
            fields=[
                ('codigo', models.CharField(
                    help_text='Código único (ex: TSU_GERENTE, TSU_TRABALHADOR)',
                    max_length=50,
                    primary_key=True,
                    serialize=False,
                    unique=True,
                    verbose_name='Código'
                )),
                ('nome', models.CharField(help_text='Nome apresentável', max_length=100, verbose_name='Nome')),
                ('descricao', models.TextField(blank=True, help_text='Descrição detalhada da categoria', null=True, verbose_name='Descrição')),
                ('taxa_empresa', models.DecimalField(
                    decimal_places=2,
                    default=0,
                    help_text='Taxa paga pela empresa (%)',
                    max_digits=5,
                    validators=[
                        django.core.validators.MinValueValidator(0),
                        django.core.validators.MaxValueValidator(100)
                    ],
                    verbose_name='Taxa Empresa'
                )),
                ('taxa_trabalhador', models.DecimalField(
                    decimal_places=2,
                    default=0,
                    help_text='Taxa descontada ao trabalhador (%)',
                    max_digits=5,
                    validators=[
                        django.core.validators.MinValueValidator(0),
                        django.core.validators.MaxValueValidator(100)
                    ],
                    verbose_name='Taxa Trabalhador'
                )),
                ('ordem', models.IntegerField(default=0, verbose_name='Ordem')),
            ],
            options={
                'verbose_name': 'Tag TSU',
                'verbose_name_plural': 'Tags TSU',
                'ordering': ['ordem', 'nome'],
                'db_table': 'tags_tsu',
            },
        ),

        # Adicionar campos fiscais ao DespesaTemplate (SEM histórico)
        migrations.AddField(
            model_name='despesatemplate',
            name='tag_irc',
            field=models.ForeignKey(
                blank=True,
                help_text='Categoria de dedutibilidade IRC',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='templates',
                to='core.tagirc',
                verbose_name='Tag IRC'
            ),
        ),
        migrations.AddField(
            model_name='despesatemplate',
            name='tag_iva',
            field=models.ForeignKey(
                blank=True,
                help_text='Categoria de dedutibilidade IVA',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='templates',
                to='core.tagiva',
                verbose_name='Tag IVA'
            ),
        ),
        migrations.AddField(
            model_name='despesatemplate',
            name='tag_irs',
            field=models.ForeignKey(
                blank=True,
                help_text='Regime de retenção IRS',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='templates',
                to='core.tagirs',
                verbose_name='Tag IRS'
            ),
        ),
        migrations.AddField(
            model_name='despesatemplate',
            name='tag_tsu',
            field=models.ForeignKey(
                blank=True,
                help_text='Regime de Segurança Social',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='templates',
                to='core.tagtsu',
                verbose_name='Tag TSU'
            ),
        ),

        # Adicionar campos fiscais ao Despesa (SEM histórico)
        migrations.AddField(
            model_name='despesa',
            name='tag_irc',
            field=models.ForeignKey(
                blank=True,
                help_text='Categoria de dedutibilidade IRC',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='despesas',
                to='core.tagirc',
                verbose_name='Tag IRC'
            ),
        ),
        migrations.AddField(
            model_name='despesa',
            name='tag_iva',
            field=models.ForeignKey(
                blank=True,
                help_text='Categoria de dedutibilidade IVA',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='despesas',
                to='core.tagiva',
                verbose_name='Tag IVA'
            ),
        ),
        migrations.AddField(
            model_name='despesa',
            name='tag_irs',
            field=models.ForeignKey(
                blank=True,
                help_text='Regime de retenção IRS',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='despesas',
                to='core.tagirs',
                verbose_name='Tag IRS'
            ),
        ),
        migrations.AddField(
            model_name='despesa',
            name='tag_tsu',
            field=models.ForeignKey(
                blank=True,
                help_text='Regime de Segurança Social',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='despesas',
                to='core.tagtsu',
                verbose_name='Tag TSU'
            ),
        ),
    ]
