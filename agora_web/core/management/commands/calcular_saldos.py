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
        self.stdout.write(f"   • Projetos Pessoais:      €{saldo_ba['projetos_pessoais']:>12,.2f}")
        self.stdout.write(f"   • Prémios:               €{saldo_ba['premios']:>12,.2f}")
        self.stdout.write(f"   • Investimento Inicial:   €{saldo_ba['investimento_inicial']:>12,.2f}")
        self.stdout.write(self.style.SUCCESS(f"   TOTAL INs:               €{saldo_ba['total_ins']:>12,.2f}"))

        self.stdout.write("\n🔴 OUTs (Saídas):")
        self.stdout.write(f"   • Despesas Fixas ÷2:     €{saldo_ba['despesas_fixas']:>12,.2f}")
        self.stdout.write(f"   • Despesas Pessoais:     €{saldo_ba['despesas_pessoais']:>12,.2f}")
        self.stdout.write(f"   • Boletins:              €{saldo_ba['boletins']:>12,.2f}")
        self.stdout.write(self.style.ERROR(f"   TOTAL OUTs:              €{saldo_ba['total_outs']:>12,.2f}"))

        cor_ba = self.style.SUCCESS if saldo_ba['saldo_final'] >= 0 else self.style.ERROR
        self.stdout.write("\n" + "="*80)
        self.stdout.write(cor_ba(f"💰 SALDO FINAL (BA):        €{saldo_ba['saldo_final']:>12,.2f}"))
        self.stdout.write("="*80 + "\n\n")

        # === RAFAEL REIGOTA ===
        saldo_rr = calculator.calcular_saldo_rafael(incluir_investimento=True)

        self.stdout.write(self.style.HTTP_INFO("👤 RAFAEL REIGOTA (RR)"))
        self.stdout.write("-" * 80)

        self.stdout.write("\n💚 INs (Entradas):")
        self.stdout.write(f"   • Projetos Pessoais:      €{saldo_rr['projetos_pessoais']:>12,.2f}")
        self.stdout.write(f"   • Prémios:               €{saldo_rr['premios']:>12,.2f}")
        self.stdout.write(f"   • Investimento Inicial:   €{saldo_rr['investimento_inicial']:>12,.2f}")
        self.stdout.write(self.style.SUCCESS(f"   TOTAL INs:               €{saldo_rr['total_ins']:>12,.2f}"))

        self.stdout.write("\n🔴 OUTs (Saídas):")
        self.stdout.write(f"   • Despesas Fixas ÷2:     €{saldo_rr['despesas_fixas']:>12,.2f}")
        self.stdout.write(f"   • Despesas Pessoais:     €{saldo_rr['despesas_pessoais']:>12,.2f}")
        self.stdout.write(f"   • Boletins:              €{saldo_rr['boletins']:>12,.2f}")
        self.stdout.write(self.style.ERROR(f"   TOTAL OUTs:              €{saldo_rr['total_outs']:>12,.2f}"))

        cor_rr = self.style.SUCCESS if saldo_rr['saldo_final'] >= 0 else self.style.ERROR
        self.stdout.write("\n" + "="*80)
        self.stdout.write(cor_rr(f"💰 SALDO FINAL (RR):        €{saldo_rr['saldo_final']:>12,.2f}"))
        self.stdout.write("="*80 + "\n")

        # Resumo
        total_empresa = saldo_ba['saldo_final'] + saldo_rr['saldo_final']
        self.stdout.write("\n" + "="*80)
        self.stdout.write(self.style.WARNING(f"📈 TOTAL DEVIDO PELA EMPRESA: €{total_empresa:>12,.2f}"))
        self.stdout.write("="*80 + "\n")
