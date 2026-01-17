"""
Management command para criar despesas fixas mensais automaticamente.

Uso:
    python manage.py criar_despesas_fixas

Este comando deve ser executado diariamente via cron job.
Verifica templates ativos e cria despesas para o dia atual se ainda não existirem.
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
from core.models import DespesaTemplate, Despesa
from datetime import date


class Command(BaseCommand):
    help = 'Cria despesas fixas mensais baseadas em templates ativos'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Mostra o que seria criado sem efetivamente criar',
        )
        parser.add_argument(
            '--dia',
            type=int,
            help='Dia específico do mês para processar (default: hoje)',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        dia_especifico = options.get('dia')

        # Determina o dia a processar
        hoje = date.today()
        if dia_especifico:
            dia_processo = dia_especifico
            mes_processo = hoje.month
            ano_processo = hoje.year
        else:
            dia_processo = hoje.day
            mes_processo = hoje.month
            ano_processo = hoje.year

        self.stdout.write(
            self.style.SUCCESS(
                f'\n{"[DRY RUN] " if dry_run else ""}Processando despesas fixas para dia {dia_processo}/{mes_processo}/{ano_processo}\n'
            )
        )

        # Busca templates ativos para o dia atual
        templates = DespesaTemplate.objects.filter(
            ativa=True,
            dia_mes=dia_processo
        ).select_related('credor', 'projeto').prefetch_related('tags')

        if not templates.exists():
            self.stdout.write(
                self.style.WARNING(
                    f'Nenhum template ativo encontrado para dia {dia_processo}'
                )
            )
            return

        self.stdout.write(f'Encontrados {templates.count()} templates ativos:\n')

        despesas_criadas = 0
        despesas_existentes = 0
        erros = 0

        for template in templates:
            try:
                # Data da despesa = dia do template no mês/ano atual
                try:
                    data_despesa = date(ano_processo, mes_processo, dia_processo)
                except ValueError:
                    # Dia não existe neste mês (ex: 31 em fevereiro)
                    self.stdout.write(
                        self.style.WARNING(
                            f'  ⚠ {template.numero}: Dia {dia_processo} não existe em {mes_processo}/{ano_processo}'
                        )
                    )
                    continue

                # Verifica se já existe despesa criada deste template neste mês
                despesa_existente = Despesa.objects.filter(
                    despesa_template=template,
                    data__year=ano_processo,
                    data__month=mes_processo
                ).first()

                if despesa_existente:
                    despesas_existentes += 1
                    self.stdout.write(
                        self.style.WARNING(
                            f'  ⊗ {template.numero}: Já existe ({despesa_existente.numero}) - {template.descricao[:50]}'
                        )
                    )
                    continue

                # Cria a despesa
                if not dry_run:
                    with transaction.atomic():
                        # Gera número sequencial para despesa
                        ultimo_numero = Despesa.objects.filter(
                            numero__startswith='#D'
                        ).order_by('-numero').first()

                        if ultimo_numero:
                            # Extrai número e incrementa
                            try:
                                num_seq = int(ultimo_numero.numero[2:]) + 1
                            except (ValueError, IndexError):
                                num_seq = 1
                        else:
                            num_seq = 1

                        numero_despesa = f'#D{num_seq:06d}'

                        despesa = Despesa.objects.create(
                            numero=numero_despesa,
                            data=data_despesa,
                            credor=template.credor,
                            projeto=template.projeto,
                            descricao=template.descricao,
                            valor_sem_iva=template.valor_sem_iva,
                            valor_com_iva=template.valor_com_iva,
                            irs_retido=template.irs_retido,
                            taxa_retencao_irs=template.taxa_retencao_irs,
                            estado=template.estado_default,
                            despesa_template=template,
                            nota=f'Criada automaticamente de {template.numero}'
                        )

                        # Copia tags
                        despesa.tags.set(template.tags.all())

                        self.stdout.write(
                            self.style.SUCCESS(
                                f'  ✓ {template.numero} → {despesa.numero}: {template.descricao[:50]} (€{template.valor_sem_iva})'
                            )
                        )
                        despesas_criadas += 1
                else:
                    # Dry run - apenas mostra o que seria criado
                    self.stdout.write(
                        f'  [DRY RUN] {template.numero}: {template.descricao[:50]} (€{template.valor_sem_iva})'
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
        self.stdout.write('\n' + '=' * 60)
        self.stdout.write(
            self.style.SUCCESS(
                f'\n{"[DRY RUN] " if dry_run else ""}Resumo:\n'
                f'  Despesas criadas: {despesas_criadas}\n'
                f'  Já existentes: {despesas_existentes}\n'
                f'  Erros: {erros}\n'
            )
        )
