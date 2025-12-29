"""
Django management command para importar Projetos com lookup de foreign keys

Uso:
    python manage.py import_projetos projetos_export.json
"""

import json
from django.core.management.base import BaseCommand
from core.models import Projeto, Cliente


class Command(BaseCommand):
    help = 'Importa projetos de um ficheiro JSON com lookup de clientes'

    def add_arguments(self, parser):
        parser.add_argument('json_file', type=str, help='Caminho para o ficheiro JSON de export')

    def handle(self, *args, **options):
        json_file = options['json_file']

        self.stdout.write(f"📦 A importar projetos de: {json_file}")

        with open(json_file, 'r', encoding='utf-8') as f:
            fixtures = json.load(f)

        projetos_importados = 0
        projetos_sem_cliente = 0
        erros = []

        for fixture in fixtures:
            try:
                fields = fixture["fields"]

                # Lookup do cliente pelo numero
                cliente = None
                cliente_numero = fields.pop("cliente_numero", None)

                if cliente_numero:
                    try:
                        cliente = Cliente.objects.get(numero=cliente_numero)
                    except Cliente.DoesNotExist:
                        projetos_sem_cliente += 1
                        self.stdout.write(
                            self.style.WARNING(
                                f"⚠️  Cliente {cliente_numero} não encontrado para projeto {fields['numero']}"
                            )
                        )

                # Cria o projeto
                projeto = Projeto(
                    cliente=cliente,
                    **fields
                )
                projeto.save()
                projetos_importados += 1

            except Exception as e:
                erros.append(f"Erro ao importar {fields.get('numero', '???')}: {str(e)}")

        # Resumo
        self.stdout.write(self.style.SUCCESS(f"\n✅ {projetos_importados} projetos importados!"))

        if projetos_sem_cliente > 0:
            self.stdout.write(
                self.style.WARNING(f"⚠️  {projetos_sem_cliente} projetos ficaram sem cliente associado")
            )

        if erros:
            self.stdout.write(self.style.ERROR(f"\n❌ {len(erros)} erros:"))
            for erro in erros[:10]:  # Mostra só os primeiros 10
                self.stdout.write(self.style.ERROR(f"   - {erro}"))
