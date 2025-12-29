"""
Django management command para calcular e mostrar Saldos dos sócios

Uso:
    python manage.py calcular_saldos
"""

from django.core.management.base import BaseCommand
from core.utils.saldos import SaldosCalculator


class Command(BaseCommand):
    help = 'Calcula e mostra os saldos pessoais de BA e RR'

    def handle(self, *args, **options):
        calculator = SaldosCalculator()

        self.stdout.write("\n" + "="*80)
        self.stdout.write(self.style.SUCCESS("📊 SALDOS PESSOAIS - AGORA MEDIA PRODUCTION"))
        self.stdout.write("="*80 + "\n")

        # === BRUNO AMARAL ===
        saldo_ba = calculator.calcular_saldo_bruno(incluir_investimento=True)

        self.stdout.write(self.style.HTTP_INFO("👤 BRUNO AMARAL (BA)"))
        self.stdout.write("-" * 80)

        self.stdout.write("\n💚 INs (Entradas):")
        self.stdout.write(f"   • Projetos Pessoais:      €{saldo_ba['ins']['projetos_pessoais']:>12,.2f}")
        self.stdout.write(f"   • Prémios:               €{saldo_ba['ins']['premios']:>12,.2f}")
        self.stdout.write(f"   • Investimento Inicial:   €{saldo_ba['ins']['investimento_inicial']:>12,.2f}")
        self.stdout.write(self.style.SUCCESS(f"   TOTAL INs:               €{saldo_ba['ins']['total']:>12,.2f}"))

        self.stdout.write("\n🔴 OUTs (Saídas):")
        self.stdout.write(f"   • Despesas Fixas ÷2:     €{saldo_ba['outs']['despesas_fixas']:>12,.2f}")
        self.stdout.write(f"   • Despesas Pessoais:     €{saldo_ba['outs']['despesas_pessoais']:>12,.2f}")
        self.stdout.write(f"   • Boletins (pagos):      €{saldo_ba['outs']['boletins_pagos']:>12,.2f}")
        self.stdout.write(f"   • Boletins (pendentes):  €{saldo_ba['outs']['boletins_pendentes']:>12,.2f}")
        self.stdout.write(self.style.ERROR(f"   TOTAL OUTs:              €{saldo_ba['outs']['total']:>12,.2f}"))

        cor_ba = self.style.SUCCESS if saldo_ba['saldo_total'] >= 0 else self.style.ERROR
        self.stdout.write("\n" + "="*80)
        self.stdout.write(cor_ba(f"💰 SALDO FINAL (BA):        €{saldo_ba['saldo_total']:>12,.2f}"))
        self.stdout.write("="*80 + "\n\n")

        # === RAFAEL REIGOTA ===
        saldo_rr = calculator.calcular_saldo_rafael(incluir_investimento=True)

        self.stdout.write(self.style.HTTP_INFO("👤 RAFAEL REIGOTA (RR)"))
        self.stdout.write("-" * 80)

        self.stdout.write("\n💚 INs (Entradas):")
        self.stdout.write(f"   • Projetos Pessoais:      €{saldo_rr['ins']['projetos_pessoais']:>12,.2f}")
        self.stdout.write(f"   • Prémios:               €{saldo_rr['ins']['premios']:>12,.2f}")
        self.stdout.write(f"   • Investimento Inicial:   €{saldo_rr['ins']['investimento_inicial']:>12,.2f}")
        self.stdout.write(self.style.SUCCESS(f"   TOTAL INs:               €{saldo_rr['ins']['total']:>12,.2f}"))

        self.stdout.write("\n🔴 OUTs (Saídas):")
        self.stdout.write(f"   • Despesas Fixas ÷2:     €{saldo_rr['outs']['despesas_fixas']:>12,.2f}")
        self.stdout.write(f"   • Despesas Pessoais:     €{saldo_rr['outs']['despesas_pessoais']:>12,.2f}")
        self.stdout.write(f"   • Boletins (pagos):      €{saldo_rr['outs']['boletins_pagos']:>12,.2f}")
        self.stdout.write(f"   • Boletins (pendentes):  €{saldo_rr['outs']['boletins_pendentes']:>12,.2f}")
        self.stdout.write(self.style.ERROR(f"   TOTAL OUTs:              €{saldo_rr['outs']['total']:>12,.2f}"))

        cor_rr = self.style.SUCCESS if saldo_rr['saldo_total'] >= 0 else self.style.ERROR
        self.stdout.write("\n" + "="*80)
        self.stdout.write(cor_rr(f"💰 SALDO FINAL (RR):        €{saldo_rr['saldo_total']:>12,.2f}"))
        self.stdout.write("="*80 + "\n")

        # Resumo
        total_empresa = saldo_ba['saldo_total'] + saldo_rr['saldo_total']
        self.stdout.write("\n" + "="*80)
        self.stdout.write(self.style.WARNING(f"📈 TOTAL DEVIDO PELA EMPRESA: €{total_empresa:>12,.2f}"))
        self.stdout.write("="*80 + "\n")
