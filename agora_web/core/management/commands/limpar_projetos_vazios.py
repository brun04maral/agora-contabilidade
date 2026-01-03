"""
Django management command para limpar projetos vazios/inválidos

Uso:
    python manage.py limpar_projetos_vazios --dry-run  # Preview
    python manage.py limpar_projetos_vazios            # Execução real

Critério de projeto "vazio":
- Descrição vazia ou NULL
- Cliente NULL
- Valor sem IVA = 0

IMPORTANTE: Preserva os números dos projetos (#P0001, etc.) para manter
coerência com a folha Excel durante a fase de transição.
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from core.models import Projeto


class Command(BaseCommand):
    help = 'Remove projetos vazios preservando números para coerência com Excel'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simula a limpeza sem apagar nada'
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']

        if dry_run:
            self.stdout.write(self.style.WARNING('🔍 DRY RUN MODE - Nenhum projeto será apagado'))

        self.stdout.write('\n' + '='*80)
        self.stdout.write('🧹 LIMPEZA DE PROJETOS VAZIOS')
        self.stdout.write('='*80 + '\n')

        # Estado inicial
        total_antes = Projeto.objects.count()
        self.stdout.write(f'📊 Total de projetos ANTES: {total_antes}\n')

        # Identificar projetos vazios
        projetos_vazios = Projeto.objects.filter(
            descricao__isnull=True,
            cliente__isnull=True,
            valor_sem_iva=0
        ) | Projeto.objects.filter(
            descricao='',
            cliente__isnull=True,
            valor_sem_iva=0
        )

        count_vazios = projetos_vazios.count()
        self.stdout.write(f'🗑️  Projetos vazios encontrados: {count_vazios}')
        self.stdout.write(f'✅ Projetos válidos (serão mantidos): {total_antes - count_vazios}\n')

        if count_vazios == 0:
            self.stdout.write(self.style.SUCCESS('✨ Nenhum projeto vazio encontrado!'))
            return

        # Mostrar amostra
        self.stdout.write('📋 Amostra dos primeiros 20 projetos que serão apagados:\n')
        for p in projetos_vazios[:20]:
            desc_preview = p.descricao[:40] if p.descricao else 'VAZIO'
            self.stdout.write(
                f'   {p.numero}: "{desc_preview}" | '
                f'cliente={p.cliente or "NULL"} | '
                f'valor=€{p.valor_sem_iva}'
            )

        if count_vazios > 20:
            self.stdout.write(f'   ... e mais {count_vazios - 20} projetos\n')
        else:
            self.stdout.write('')

        # Confirmação em modo real
        if not dry_run:
            self.stdout.write(self.style.WARNING(
                f'\n⚠️  ATENÇÃO: Vai apagar {count_vazios} projetos!'
            ))
            confirm = input('\nTem certeza? Digite "APAGAR" para confirmar: ')

            if confirm != 'APAGAR':
                self.stdout.write(self.style.ERROR('❌ Operação cancelada!'))
                return

        # Executar limpeza
        if dry_run:
            self.stdout.write(self.style.SUCCESS(
                f'\n✅ DRY RUN: {count_vazios} projetos SERIAM apagados'
            ))
        else:
            with transaction.atomic():
                # Apagar projetos vazios
                numeros_apagados = list(projetos_vazios.values_list('numero', flat=True))
                deleted_count, _ = projetos_vazios.delete()

                self.stdout.write(self.style.SUCCESS(
                    f'\n✅ {deleted_count} projetos apagados com sucesso!'
                ))

                # Mostrar alguns números apagados
                self.stdout.write('\n📝 Exemplos de números apagados (preservados para referência):')
                for num in numeros_apagados[:10]:
                    self.stdout.write(f'   {num}')
                if len(numeros_apagados) > 10:
                    self.stdout.write(f'   ... e mais {len(numeros_apagados) - 10}')

        # Estado final
        total_depois = Projeto.objects.count() if not dry_run else (total_antes - count_vazios)

        self.stdout.write('\n' + '='*80)
        self.stdout.write('📊 RESUMO')
        self.stdout.write('='*80)
        self.stdout.write(f'Antes:  {total_antes} projetos')
        self.stdout.write(f'Depois: {total_depois} projetos')
        self.stdout.write(f'Apagados: {count_vazios} projetos vazios')
        self.stdout.write('='*80 + '\n')

        if not dry_run:
            self.stdout.write(self.style.SUCCESS(
                '✨ Limpeza concluída! Os números dos projetos foram preservados.'
            ))
            self.stdout.write(
                '\n💡 Nota: Quando criar novos projetos na app, os números vazios '
                '(ex: #P0100-#P1699) continuam disponíveis se necessário.\n'
            )
