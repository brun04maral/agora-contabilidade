# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_boletim_boletimlinha'),
    ]

    operations = [
        migrations.AddField(
            model_name='despesa',
            name='irs_retido',
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                default=0,
                help_text='Retenção na fonte (normalmente 25% para freelancers)',
                max_digits=10,
                null=True,
                verbose_name='IRS Retido'
            ),
        ),
        migrations.AddField(
            model_name='despesatemplate',
            name='irs_retido',
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                default=0,
                help_text='Retenção na fonte (normalmente 25% para freelancers)',
                max_digits=10,
                null=True,
                verbose_name='IRS Retido'
            ),
        ),
    ]
