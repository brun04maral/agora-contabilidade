# -*- coding: utf-8 -*-
"""
Management command para migrar dados de owner/socio_codigo para FK Socio
"""
from django.core.management.base import BaseCommand
from core.models import Socio, Projeto, Boletim, Orcamento


class Command(BaseCommand):
    help = 'Migra dados de owner/socio_codigo para FK Socio'

    def handle(self, *args, **options):
        self.stdout.write('🔄 Migrando dados para modelo Socio...\n')

        # Verificar se os sócios existem
        try:
            socio_ba = Socio.objects.get(codigo='BA')
            socio_rr = Socio.objects.get(codigo='RR')
            self.stdout.write(f'   ✅ Sócios encontrados: {socio_ba}, {socio_rr}')
        except Socio.DoesNotExist:
            self.stdout.write(self.style.ERROR('   ❌ Sócios não encontrados! Execute: python manage.py loaddata socios.json'))
            return

        # Migrar Projetos
        self.stdout.write('\n📦 Migrando Projetos...')
        projetos_ba = Projeto.objects.filter(owner='BA', socio__isnull=True)
        projetos_rr = Projeto.objects.filter(owner='RR', socio__isnull=True)

        count_ba = projetos_ba.update(socio=socio_ba)
        count_rr = projetos_rr.update(socio=socio_rr)

        self.stdout.write(f'   ✅ {count_ba} projetos BA atualizados')
        self.stdout.write(f'   ✅ {count_rr} projetos RR atualizados')

        # Migrar Boletins
        self.stdout.write('\n📦 Migrando Boletins...')
        boletins_ba = Boletim.objects.filter(socio_codigo='BA', socio__isnull=True)
        boletins_rr = Boletim.objects.filter(socio_codigo='RR', socio__isnull=True)

        count_ba = boletins_ba.update(socio=socio_ba)
        count_rr = boletins_rr.update(socio=socio_rr)

        self.stdout.write(f'   ✅ {count_ba} boletins BA atualizados')
        self.stdout.write(f'   ✅ {count_rr} boletins RR atualizados')

        # Migrar Orçamentos
        self.stdout.write('\n📦 Migrando Orçamentos...')
        orcamentos_ba = Orcamento.objects.filter(owner='BA', socio__isnull=True)
        orcamentos_rr = Orcamento.objects.filter(owner='RR', socio__isnull=True)

        count_ba = orcamentos_ba.update(socio=socio_ba)
        count_rr = orcamentos_rr.update(socio=socio_rr)

        self.stdout.write(f'   ✅ {count_ba} orçamentos BA atualizados')
        self.stdout.write(f'   ✅ {count_rr} orçamentos RR atualizados')

        # Estatísticas finais
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('✅ Migração concluída com sucesso!'))
        self.stdout.write('\n📊 Estatísticas:')
        self.stdout.write(f'   Projetos com socio definido: {Projeto.objects.filter(socio__isnull=False).count()}')
        self.stdout.write(f'   Boletins com socio definido: {Boletim.objects.filter(socio__isnull=False).count()}')
        self.stdout.write(f'   Orçamentos com socio definido: {Orcamento.objects.filter(socio__isnull=False).count()}')
        self.stdout.write('\n💡 Próximo passo: Verificar no admin se está tudo correto!')
        self.stdout.write('   Depois, pode remover os campos antigos (owner, socio_codigo)')
