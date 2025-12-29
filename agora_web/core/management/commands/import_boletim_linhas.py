"""
Django management command para importar BoletimLinhas com lookup de foreign keys

Uso:
    python manage.py import_boletim_linhas boletim_linhas_export.json
"""

import json
from django.core.management.base import BaseCommand
from core.models import BoletimLinha, Boletim, Projeto


class Command(BaseCommand):
    help = 'Importa linhas de boletim de um ficheiro JSON com lookup de FKs'

    def add_arguments(self, parser):
        parser.add_argument('json_file', type=str, help='Caminho para o ficheiro JSON de export')

    def handle(self, *args, **options):
        json_file = options['json_file']

        self.stdout.write(f"📦 A importar linhas de boletim de: {json_file}")

        with open(json_file, 'r', encoding='utf-8') as f:
            fixtures = json.load(f)

        linhas_importadas = 0
        linhas_sem_boletim = 0
        linhas_sem_projeto = 0
        erros = []

        for fixture in fixtures:
            try:
                fields = fixture["fields"]

                # Lookup do boletim pelo numero (OBRIGATÓRIO)
                boletim_numero = fields.pop("boletim_numero", None)
                if not boletim_numero:
                    linhas_sem_boletim += 1
                    continue

                try:
                    boletim = Boletim.objects.get(numero=boletim_numero)
                except Boletim.DoesNotExist:
                    linhas_sem_boletim += 1
                    self.stdout.write(
                        self.style.ERROR(
                            f"❌ Boletim {boletim_numero} não encontrado! Linha ignorada."
                        )
                    )
                    continue

                # Lookup do projeto pelo numero (OPCIONAL)
                projeto = None
                projeto_numero = fields.pop("projeto_numero", None)
                if projeto_numero:
                    try:
                        projeto = Projeto.objects.get(numero=projeto_numero)
                    except Projeto.DoesNotExist:
                        linhas_sem_projeto += 1
                        self.stdout.write(
                            self.style.WARNING(
                                f"⚠️  Projeto {projeto_numero} não encontrado para linha do boletim {boletim_numero}"
                            )
                        )

                # Cria a linha
                linha = BoletimLinha(
                    boletim=boletim,
                    projeto=projeto,
                    **fields
                )
                linha.save()
                linhas_importadas += 1

            except Exception as e:
                erros.append(f"Erro ao importar linha: {str(e)}")

        # Resumo
        self.stdout.write(self.style.SUCCESS(f"\n✅ {linhas_importadas} linhas de boletim importadas!"))

        if linhas_sem_boletim > 0:
            self.stdout.write(
                self.style.ERROR(f"❌ {linhas_sem_boletim} linhas sem boletim associado (ignoradas)")
            )

        if linhas_sem_projeto > 0:
            self.stdout.write(
                self.style.WARNING(f"⚠️  {linhas_sem_projeto} linhas ficaram sem projeto associado")
            )

        if erros:
            self.stdout.write(self.style.ERROR(f"\n❌ {len(erros)} erros:"))
            for erro in erros[:10]:
                self.stdout.write(self.style.ERROR(f"   - {erro}"))
