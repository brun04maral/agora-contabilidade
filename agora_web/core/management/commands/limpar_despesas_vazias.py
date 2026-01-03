"""
Django management command para limpar despesas vazias/inválidas

Uso:
    python manage.py limpar_despesas_vazias --dry-run  # Preview
    python manage.py limpar_despesas_vazias            # Execução real

Critério de despesa "vazia":
- Descrição vazia ou NULL
- Credor NULL
- Valor sem IVA = 0

IMPORTANTE: Preserva os números das despesas (#D0001, etc.) para manter
coerência com a folha Excel durante a fase de transição.
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from core.models import Despesa


class Command(BaseCommand):
    help = 'Remove despesas vazias preservando números para coerência com Excel'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simula a limpeza sem apagar nada'
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']

        if dry_run:
            self.stdout.write(self.style.WARNING('🔍 DRY RUN MODE - Nenhuma despesa será apagada'))

        self.stdout.write('\n' + '='*80)
        self.stdout.write('🧹 LIMPEZA DE DESPESAS VAZIAS')
        self.stdout.write('='*80 + '\n')

        # Estado inicial
        total_antes = Despesa.objects.count()
        self.stdout.write(f'📊 Total de despesas ANTES: {total_antes}\n')

        # Identificar despesas vazias
        despesas_vazias = Despesa.objects.filter(
            descricao__isnull=True,
            credor__isnull=True,
            valor_sem_iva=0
        ) | Despesa.objects.filter(
            descricao='',
            credor__isnull=True,
            valor_sem_iva=0
        )

        count_vazias = despesas_vazias.count()
        self.stdout.write(f'🗑️  Despesas vazias encontradas: {count_vazias}')
        self.stdout.write(f'✅ Despesas válidas (serão mantidas): {total_antes - count_vazias}\n')

        if count_vazias == 0:
            self.stdout.write(self.style.SUCCESS('✨ Nenhuma despesa vazia encontrada!'))
            return

        # Mostrar amostra
        self.stdout.write('📋 Amostra das primeiras 20 despesas que serão apagadas:\n')
        for d in despesas_vazias[:20]:
            desc_preview = d.descricao[:40] if d.descricao else 'VAZIO'
            self.stdout.write(
                f'   {d.numero}: "{desc_preview}" | '
                f'credor={d.credor or "NULL"} | '
                f'valor=€{d.valor_sem_iva}'
            )

        if count_vazias > 20:
            self.stdout.write(f'   ... e mais {count_vazias - 20} despesas\n')
        else:
            self.stdout.write('')

        # Confirmação em modo real
        if not dry_run:
            self.stdout.write(self.style.WARNING(
                f'\n⚠️  ATENÇÃO: Vai apagar {count_vazias} despesas!'
            ))
            confirm = input('\nTem certeza? Digite "APAGAR" para confirmar: ')

            if confirm != 'APAGAR':
                self.stdout.write(self.style.ERROR('❌ Operação cancelada!'))
                return

        # Executar limpeza
        if dry_run:
            self.stdout.write(self.style.SUCCESS(
                f'\n✅ DRY RUN: {count_vazias} despesas SERIAM apagadas'
            ))
        else:
            with transaction.atomic():
                # Apagar despesas vazias
                numeros_apagados = list(despesas_vazias.values_list('numero', flat=True))
                deleted_count, _ = despesas_vazias.delete()

                self.stdout.write(self.style.SUCCESS(
                    f'\n✅ {deleted_count} despesas apagadas com sucesso!'
                ))

                # Mostrar alguns números apagados
                self.stdout.write('\n📝 Exemplos de números apagados (preservados para referência):')
                for num in numeros_apagados[:10]:
                    self.stdout.write(f'   {num}')
                if len(numeros_apagados) > 10:
                    self.stdout.write(f'   ... e mais {len(numeros_apagados) - 10}')

        # Estado final
        total_depois = Despesa.objects.count() if not dry_run else (total_antes - count_vazias)

        self.stdout.write('\n' + '='*80)
        self.stdout.write('📊 RESUMO')
        self.stdout.write('='*80)
        self.stdout.write(f'Antes:  {total_antes} despesas')
        self.stdout.write(f'Depois: {total_depois} despesas')
        self.stdout.write(f'Apagados: {count_vazias} despesas vazias')
        self.stdout.write('='*80 + '\n')

        if not dry_run:
            self.stdout.write(self.style.SUCCESS(
                '✨ Limpeza concluída! Os números das despesas foram preservados.'
            ))
            self.stdout.write(
                '\n💡 Nota: Quando criar novas despesas na app, os números vazios '
                'continuam disponíveis se necessário.\n'
            )
