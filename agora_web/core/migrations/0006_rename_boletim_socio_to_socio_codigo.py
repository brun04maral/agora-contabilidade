# Migration to rename Boletim.socio to socio_codigo to avoid conflict with FK

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_remove_tagdespesa_timestamps'),
    ]

    operations = [
        migrations.RenameField(
            model_name='boletim',
            old_name='socio',
            new_name='socio_codigo',
        ),
    ]
