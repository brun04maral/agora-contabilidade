# Generated manually to add Socio, TagDespesa and new fields

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_boletim_boletimlinha'),
    ]

    operations = [
        # 1. Create Socio model
        migrations.CreateModel(
            name='Socio',
            fields=[
                ('codigo', models.CharField(max_length=2, primary_key=True, serialize=False, unique=True, verbose_name='Código')),
                ('nome_completo', models.CharField(max_length=100, verbose_name='Nome Completo')),
                ('nome_curto', models.CharField(max_length=50, verbose_name='Nome Curto')),
                ('email', models.EmailField(max_length=254, verbose_name='Email')),
                ('telefone', models.CharField(blank=True, max_length=50, null=True, verbose_name='Telefone')),
                ('percentagem_participacao', models.DecimalField(decimal_places=2, default=50.0, max_digits=5, verbose_name='% Participação')),
                ('ativo', models.BooleanField(default=True, verbose_name='Ativo')),
                ('cor_tema', models.CharField(blank=True, default='#1976d2', max_length=7, null=True, verbose_name='Cor Tema')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Criado em')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Atualizado em')),
            ],
            options={
                'verbose_name': 'Sócio',
                'verbose_name_plural': 'Sócios',
                'db_table': 'socios',
                'ordering': ['codigo'],
            },
        ),

        # 2. Create TagDespesa model
        migrations.CreateModel(
            name='TagDespesa',
            fields=[
                ('codigo', models.CharField(max_length=50, primary_key=True, serialize=False, verbose_name='Código')),
                ('nome', models.CharField(max_length=100, verbose_name='Nome')),
                ('impacta_saldos', models.BooleanField(default=False, help_text='Se True, despesas com esta tag afetam saldos pessoais', verbose_name='Impacta Saldos')),
                ('impacta_irc', models.BooleanField(default=False, help_text='Se True, despesas com esta tag são dedutíveis para IRC', verbose_name='Impacta IRC')),
                ('ordem', models.IntegerField(default=0, help_text='Ordem de exibição nas interfaces', verbose_name='Ordem')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Criado em')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Atualizado em')),
            ],
            options={
                'verbose_name': 'Tag de Despesa',
                'verbose_name_plural': 'Tags de Despesa',
                'db_table': 'tags_despesa',
                'ordering': ['ordem', 'nome'],
            },
        ),

        # 3. Add socio FK to Boletim (nullable)
        migrations.AddField(
            model_name='boletim',
            name='socio',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='boletins', to='core.socio', verbose_name='Sócio'),
        ),

        # 4. Add socio FK to Projeto (nullable)
        migrations.AddField(
            model_name='projeto',
            name='socio',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='projetos', to='core.socio', verbose_name='Sócio Responsável'),
        ),

        # 5. Add new fields to Projeto
        migrations.AddField(
            model_name='projeto',
            name='data_recibo',
            field=models.DateField(blank=True, help_text='Data em que o cliente pagou o projeto', null=True, verbose_name='Data Recibo'),
        ),
        migrations.AddField(
            model_name='projeto',
            name='orcamento_url',
            field=models.URLField(blank=True, help_text='Link para o orçamento relacionado', max_length=500, null=True, verbose_name='Link Orçamento'),
        ),
        migrations.AddField(
            model_name='projeto',
            name='equipa',
            field=models.IntegerField(blank=True, help_text='Número de pessoas na equipa do projeto', null=True, verbose_name='Tamanho Equipa'),
        ),
        migrations.AddField(
            model_name='projeto',
            name='recursos_humanos',
            field=models.TextField(blank=True, help_text='Nomes das pessoas que trabalharam no projeto', null=True, verbose_name='Recursos Humanos'),
        ),
        migrations.AddField(
            model_name='projeto',
            name='equipamento_usado',
            field=models.TextField(blank=True, help_text='Equipamento utilizado no projeto', null=True, verbose_name='Equipamento Usado'),
        ),
        migrations.AddField(
            model_name='projeto',
            name='local',
            field=models.CharField(blank=True, help_text='Local onde o projeto foi realizado', max_length=200, null=True, verbose_name='Local'),
        ),

        # 6. Add tipo_original to Despesa
        migrations.AddField(
            model_name='despesa',
            name='tipo_original',
            field=models.CharField(blank=True, help_text='Tipo original da Google Sheet (pode conter múltiplas tags)', max_length=200, null=True, verbose_name='Tipo Original'),
        ),

        # 7. Add ManyToMany tags to Despesa
        migrations.AddField(
            model_name='despesa',
            name='tags',
            field=models.ManyToManyField(blank=True, help_text='Tags que categorizam esta despesa', related_name='despesas', to='core.tagdespesa', verbose_name='Tags'),
        ),
    ]
