# Migration to allow NULL in boletim.socio_id

from django.db import migrations


def allow_null_socio(apps, schema_editor):
    """Allow NULL in boletim socio FK (model has null=True, blank=True)"""
    with schema_editor.connection.cursor() as cursor:
        # Check which column exists
        cursor.execute("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = 'boletins'
            AND column_name IN ('socio', 'socio_id')
        """)
        columns = [row[0] for row in cursor.fetchall()]

        # Remove NOT NULL constraint
        if 'socio_id' in columns:
            cursor.execute('ALTER TABLE boletins ALTER COLUMN socio_id DROP NOT NULL')
        elif 'socio' in columns:
            cursor.execute('ALTER TABLE boletins ALTER COLUMN socio DROP NOT NULL')


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_fix_boletim_socio_field'),
    ]

    operations = [
        migrations.RunPython(allow_null_socio, migrations.RunPython.noop),
    ]
