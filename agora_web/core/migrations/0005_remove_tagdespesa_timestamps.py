# Migration to remove created_at and updated_at from TagDespesa
# (these fields exist in Socio model but not in TagDespesa model)

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_add_socio_and_tags'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tagdespesa',
            name='created_at',
        ),
        migrations.RemoveField(
            model_name='tagdespesa',
            name='updated_at',
        ),
    ]
