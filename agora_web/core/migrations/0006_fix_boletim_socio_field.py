# Migration to fix Boletim socio field confusion

from django.db import migrations


def fix_boletim_socio(apps, schema_editor):
    """
    Fix the Boletim.socio field confusion:
    - Migration 0003 created 'socio' as CharField
    - Migration 0004 tried to add 'socio' as ForeignKey (conflict!)
    - This migration cleans up the mess
    """
    with schema_editor.connection.cursor() as cursor:
        # Check what columns exist
        cursor.execute("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = 'boletins'
            AND column_name IN ('socio', 'socio_codigo', 'socio_id', 'socio_codigo_id')
        """)
        existing_columns = [row[0] for row in cursor.fetchall()]

        # If socio_codigo_id exists, rename it to socio_id
        if 'socio_codigo_id' in existing_columns and 'socio_id' not in existing_columns:
            cursor.execute('ALTER TABLE boletins RENAME COLUMN socio_codigo_id TO socio_id')

        # Drop old CharField column if it exists
        if 'socio' in existing_columns and 'socio_id' in existing_columns:
            # We have both, drop the CharField (the one without _id)
            cursor.execute('ALTER TABLE boletins DROP COLUMN IF EXISTS socio')

        if 'socio_codigo' in existing_columns:
            cursor.execute('ALTER TABLE boletins DROP COLUMN IF EXISTS socio_codigo')


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_remove_tagdespesa_timestamps'),
    ]

    operations = [
        migrations.RunPython(fix_boletim_socio, migrations.RunPython.noop),
    ]
