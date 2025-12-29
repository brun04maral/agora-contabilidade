"""
Django management command para importar Despesas com lookup de foreign keys

Uso:
    python manage.py import_despesas despesas_export.json
"""

import json
from django.core.management.base import BaseCommand
from core.models import Despesa, Fornecedor, Projeto, DespesaTemplate


class Command(BaseCommand):
    help = 'Importa despesas de um ficheiro JSON com lookup de FKs'

    def add_arguments(self, parser):
        parser.add_argument('json_file', type=str, help='Caminho para o ficheiro JSON de export')

    def handle(self, *args, **options):
        json_file = options['json_file']

        self.stdout.write(f"📦 A importar despesas de: {json_file}")

        with open(json_file, 'r', encoding='utf-8') as f:
            fixtures = json.load(f)

        despesas_importadas = 0
        despesas_sem_credor = 0
        despesas_sem_projeto = 0
        erros = []

        for fixture in fixtures:
            try:
                fields = fixture["fields"]

                # Lookup do credor (fornecedor) pelo numero
                credor = None
                credor_numero = fields.pop("credor_numero", None)
                if credor_numero:
                    try:
                        credor = Fornecedor.objects.get(numero=credor_numero)
                    except Fornecedor.DoesNotExist:
                        despesas_sem_credor += 1
                        self.stdout.write(
                            self.style.WARNING(
                                f"⚠️  Fornecedor {credor_numero} não encontrado para despesa {fields['numero']}"
                            )
                        )

                # Lookup do projeto pelo numero
                projeto = None
                projeto_numero = fields.pop("projeto_numero", None)
                if projeto_numero:
                    try:
                        projeto = Projeto.objects.get(numero=projeto_numero)
                    except Projeto.DoesNotExist:
                        despesas_sem_projeto += 1
                        self.stdout.write(
                            self.style.WARNING(
                                f"⚠️  Projeto {projeto_numero} não encontrado para despesa {fields['numero']}"
                            )
                        )

                # DespesaTemplate - ignorar por agora (pode não existir)
                fields.pop("despesa_template_numero", None)

                # Cria a despesa
                despesa = Despesa(
                    credor=credor,
                    projeto=projeto,
                    despesa_template=None,  # Ignorar templates por agora
                    **fields
                )
                despesa.save()
                despesas_importadas += 1

            except Exception as e:
                erros.append(f"Erro ao importar {fields.get('numero', '???')}: {str(e)}")

        # Resumo
        self.stdout.write(self.style.SUCCESS(f"\n✅ {despesas_importadas} despesas importadas!"))

        if despesas_sem_credor > 0:
            self.stdout.write(
                self.style.WARNING(f"⚠️  {despesas_sem_credor} despesas ficaram sem credor associado")
            )

        if despesas_sem_projeto > 0:
            self.stdout.write(
                self.style.WARNING(f"⚠️  {despesas_sem_projeto} despesas ficaram sem projeto associado")
            )

        if erros:
            self.stdout.write(self.style.ERROR(f"\n❌ {len(erros)} erros:"))
            for erro in erros[:10]:
                self.stdout.write(self.style.ERROR(f"   - {erro}"))
