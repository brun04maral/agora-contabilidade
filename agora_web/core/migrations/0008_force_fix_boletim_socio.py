# Migration to forcefully fix boletim socio columns

from django.db import migrations


def force_fix_socio(apps, schema_editor):
    """Forcefully fix the boletim.socio mess"""
    with schema_editor.connection.cursor() as cursor:
        # Get current columns
        cursor.execute("""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_name = 'boletins'
            AND column_name IN ('socio', 'socio_id', 'socio_codigo', 'socio_codigo_id')
            ORDER BY column_name
        """)
        columns = cursor.fetchall()
        print(f"DEBUG: Current boletim columns related to socio: {columns}")

        # Step 1: If 'socio' CharField exists, rename it to avoid conflict
        cursor.execute("""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_name = 'boletins'
            AND column_name = 'socio'
        """)
        socio_col = cursor.fetchone()

        if socio_col and socio_col[1] in ('character varying', 'text'):
            # It's the old CharField, rename it
            print("DEBUG: Renaming old CharField 'socio' to 'socio_old'")
            cursor.execute('ALTER TABLE boletins RENAME COLUMN socio TO socio_old')

        # Step 2: Ensure socio_id exists and is nullable
        cursor.execute("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = 'boletins'
            AND column_name = 'socio_id'
        """)
        if not cursor.fetchone():
            # socio_id doesn't exist, create it
            print("DEBUG: Creating socio_id column")
            cursor.execute('''
                ALTER TABLE boletins
                ADD COLUMN socio_id VARCHAR(2) NULL
                REFERENCES socios(codigo) ON DELETE PROTECT
            ''')
        else:
            # Make sure it's nullable
            print("DEBUG: Ensuring socio_id is nullable")
            cursor.execute('ALTER TABLE boletins ALTER COLUMN socio_id DROP NOT NULL')

        # Step 3: Drop old columns
        cursor.execute('ALTER TABLE boletins DROP COLUMN IF EXISTS socio_old')
        cursor.execute('ALTER TABLE boletins DROP COLUMN IF EXISTS socio_codigo')
        cursor.execute('ALTER TABLE boletins DROP COLUMN IF EXISTS socio_codigo_id')

        # Final check
        cursor.execute("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'boletins'
            AND column_name LIKE '%socio%'
            ORDER BY column_name
        """)
        final_cols = cursor.fetchall()
        print(f"DEBUG: Final boletim socio columns: {final_cols}")


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_boletim_socio_allow_null'),
    ]

    operations = [
        migrations.RunPython(force_fix_socio, migrations.RunPython.noop),
    ]
