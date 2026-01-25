"""
Management command para criar despesas fixas automaticamente.

Uso:
    python manage.py criar_despesas_fixas [--dry-run]

Este comando deve ser executado diariamente via cron job.
Verifica templates ativos e cria despesas baseado na frequência configurada.

Suporte a frequências:
- MENSAL: Gera todo mês no dia configurado
- TRIMESTRAL: Gera a cada 3 meses
- SEMESTRAL: Gera a cada 6 meses
- ANUAL: Gera a cada 12 meses
- MANUAL: Nunca gera automaticamente (apenas via action do admin)
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from core.models import DespesaTemplate
from datetime import date


class Command(BaseCommand):
    help = 'Cria despesas fixas baseadas em templates ativos e suas frequências'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Mostra o que seria criado sem efetivamente criar',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        hoje = date.today()

        self.stdout.write(
            self.style.SUCCESS(
                f'\n{"[DRY RUN] " if dry_run else ""}Processando despesas automáticas para {hoje.strftime("%d/%m/%Y")}\n'
            )
        )

        # Busca TODOS os templates ativos (não filtra por dia_mes)
        # A lógica de frequência está no método deve_gerar_hoje()
        templates = DespesaTemplate.objects.filter(
            ativa=True
        ).exclude(
            frequencia='MANUAL'  # Exclui blueprints manuais
        ).select_related('credor', 'projeto').prefetch_related('tags')

        if not templates.exists():
            self.stdout.write(
                self.style.WARNING(
                    'Nenhum template ativo encontrado (excluindo MANUAL)'
                )
            )
            return

        self.stdout.write(f'Encontrados {templates.count()} templates ativos:\n')

        despesas_criadas = 0
        despesas_puladas = 0
        erros = 0

        for template in templates:
            try:
                # Verifica se deve gerar hoje baseado na frequência
                if not template.deve_gerar_hoje():
                    despesas_puladas += 1
                    self.stdout.write(
                        self.style.WARNING(
                            f'  ⊗ {template.numero}: Não gera hoje ({template.get_frequencia_display()}, dia {template.dia_mes}) - {template.descricao[:40]}'
                        )
                    )
                    continue

                # Verifica se já gerou hoje (proteção contra execuções múltiplas)
                ultima_despesa = template.despesas_geradas.order_by('-data').first()
                if ultima_despesa and ultima_despesa.data == hoje:
                    despesas_puladas += 1
                    self.stdout.write(
                        self.style.WARNING(
                            f'  ⊗ {template.numero}: Já gerou hoje ({ultima_despesa.numero}) - {template.descricao[:40]}'
                        )
                    )
                    continue

                # Gera a despesa (se não for dry-run)
                if not dry_run:
                    nova_despesa = template.gerar_despesa(user=None)
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'  ✓ {template.numero} → {nova_despesa.numero}: {template.descricao[:40]} (€{template.valor_sem_iva}) [{template.get_frequencia_display()}]'
                        )
                    )
                    despesas_criadas += 1
                else:
                    # Dry run - apenas mostra o que seria criado
                    self.stdout.write(
                        f'  [DRY RUN] {template.numero}: {template.descricao[:40]} (€{template.valor_sem_iva}) [{template.get_frequencia_display()}]'
                    )
                    despesas_criadas += 1

            except Exception as e:
                erros += 1
                self.stdout.write(
                    self.style.ERROR(
                        f'  ✗ Erro ao processar {template.numero}: {str(e)}'
                    )
                )

        # Resumo
        self.stdout.write('\n' + '=' * 80)
        self.stdout.write(
            self.style.SUCCESS(
                f'\n{"[DRY RUN] " if dry_run else ""}Resumo:\n'
                f'  Templates avaliados: {templates.count()}\n'
                f'  Despesas criadas: {despesas_criadas}\n'
                f'  Puladas (não gera hoje): {despesas_puladas}\n'
                f'  Erros: {erros}\n'
            )
        )
