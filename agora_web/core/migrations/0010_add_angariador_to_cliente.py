# Generated manually on 2026-01-12 20:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_merge_fiscal_and_socio'),
    ]

    operations = [
        # NOTA: Este campo foi adicionado manualmente via SQL direto no banco de dados
        # porque havia problemas com migrations anteriores.
        #
        # SQL executado:
        # ALTER TABLE clientes ADD COLUMN angariador_id VARCHAR(2) REFERENCES socios(codigo) ON DELETE SET NULL;
        # CREATE INDEX clientes_angariador_id_idx ON clientes(angariador_id);
        # ALTER TABLE core_historicalcliente ADD COLUMN angariador_id VARCHAR(2);
        #
        # Este migration está aqui apenas para manter o histórico de mudanças sincronizado.
    ]
