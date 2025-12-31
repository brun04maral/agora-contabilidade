# Saldos Pessoais Dashboard - Implementation Guide

**Date:** December 2025
**Status:** ✅ Complete (Redesigned)
**Branch:** `claude/review-balance-logic-0omT0`
**URL:** `/admin/core/saldo/`

---

## Overview

Dashboard personalizado no Django Admin para visualizar saldos pessoais dos sócios (BA e RR) em tempo real, sem necessidade de tabela na database.

**Empresa:** Amaral & Reigota - Produção Audiovisual, Lda (NIPC: 518 351 190)
**Marca:** Agora Media Production

### Features
- ✅ **Saldos Totais All-Time:** Cards de topo mostram saldo projetado acumulado desde sempre
- ✅ **Breakdown Anual:** Detalhes do ano corrente (2025) com separação de pagos vs pendentes
- ✅ **Saldo Efetivo vs Projetado:** Distinção clara entre valores já pagos e valores projetados (com pendentes)
- ✅ **Sugestão de Boletim:** Baseada no saldo projetado do ano ÷ meses restantes
- ✅ **Dark Mode Support:** Layout funciona com tema claro e escuro do Unfold
- ✅ **Responsive Design:** Layout adaptativo para mobile (2 colunas → 1 coluna)
- ❌ ~~Total Devido pela Empresa~~ (removido - informação redundante)
- ❌ ~~Gráficos Chart.js~~ (removidos - dados incorretos)

---

## Dashboard Structure

### Layout

```
┌─────────────────────────────────────────────────────┐
│ Saldos Pessoais                                     │
│ Saldo projetado total e breakdown do ano 2025      │
├──────────────────────┬──────────────────────────────┤
│  BRUNO AMARAL (BA)   │   RAFAEL REIGOTA (RR)       │
│  € 12,345.67         │   € 8,901.23                │
│  Saldo Projetado     │   Saldo Projetado           │
│  Total INs: €X       │   Total INs: €X             │
│  Total OUTs: €X      │   Total OUTs: €X            │
└──────────────────────┴──────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│ Breakdown 2025                                      │
│ Detalhes de entradas e saídas do ano corrente      │
├──────────────────────┬──────────────────────────────┤
│ Bruno Amaral (BA)    │ Rafael Reigota (RR)         │
├──────────────────────┼──────────────────────────────┤
│ ENTRADAS (INs) 2025  │ ENTRADAS (INs) 2025         │
│ • Projetos Pessoais  │ • Projetos Pessoais         │
│ • Prémios (pagos)    │ • Prémios (pagos)           │
│ • A Receber (azul)   │ • A Receber (azul)          │
│ Total INs 2025       │ Total INs 2025              │
│                      │                             │
│ SAÍDAS (OUTs) 2025   │ SAÍDAS (OUTs) 2025          │
│ • Despesas Fixas ÷2  │ • Despesas Fixas ÷2         │
│ • Boletins Pagos     │ • Boletins Pagos            │
│ • Despesas Pessoais  │ • Despesas Pessoais         │
│ • Por Pagar (laranja)│ • Por Pagar (laranja)       │
│ Total OUTs 2025      │ Total OUTs 2025             │
│                      │                             │
│ RESUMO 2025          │ RESUMO 2025                 │
│ • Saldo Efetivo      │ • Saldo Efetivo             │
│ • Saldo Projetado    │ • Saldo Projetado           │
│                      │                             │
│ SUGESTÃO BOLETIM     │ SUGESTÃO BOLETIM            │
│ € X.XX / mês         │ € X.XX / mês                │
└──────────────────────┴──────────────────────────────┘
```

### Color Coding

| Categoria | Cor | Significado |
|-----------|-----|-------------|
| **Verde** | `green-text`, `green-bg`, `green-border` | Entradas (INs), valores positivos |
| **Vermelho** | `red-text`, `red-bg`, `red-border` | Saídas (OUTs), valores negativos |
| **Azul** | `blue-text`, `blue-bg` | A Receber (finalizados mas não pagos) |
| **Laranja** | `orange-text`, `orange-bg`, `orange-border` | Por Pagar (boletins pendentes), Sugestões |

---

## Architecture

### Proxy Model (No Database Table)

**File:** `agora_web/core/models.py`

```python
class Saldo(models.Model):
    """Proxy model para mostrar Saldos Pessoais no admin"""
    id = models.IntegerField(primary_key=True)  # Dummy field

    class Meta:
        managed = False  # Django doesn't create table
        verbose_name = _('Saldo Pessoal')
        verbose_name_plural = _('Saldos Pessoais')
        db_table = 'saldos_view'  # Fictitious table name
        default_permissions = ()  # No add/change/delete permissions
```

**Why proxy model?**
- No database table needed - all calculations are done in Python
- Appears in Django admin sidebar
- Can use standard admin customizations
- Clean separation of concerns

---

## Admin Implementation

### File: `agora_web/core/admin.py`

```python
@admin.register(Saldo)
class SaldoAdmin(ModelAdmin):
    """Admin para Saldos Pessoais - Dashboard personalizado"""

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        """Vista personalizada para mostrar dashboard de saldos"""
        from django.shortcuts import render
        from core.utils.saldos import SaldosCalculator
        from datetime import date

        calculator = SaldosCalculator()
        ano_atual = date.today().year

        # Calcular saldos TOTAIS (de sempre)
        saldo_total_ba = calculator.calcular_saldo_bruno(incluir_investimento=False)
        saldo_total_rr = calculator.calcular_saldo_rafael(incluir_investimento=False)

        # Calcular breakdown do ANO CORRENTE
        breakdown_ba = calculator.calcular_saldo_ano('BA', ano_atual)
        breakdown_rr = calculator.calcular_saldo_ano('RR', ano_atual)

        context = {
            **self.admin_site.each_context(request),
            'title': 'Saldos Pessoais',
            'ano_atual': ano_atual,
            'saldo_total_ba': saldo_total_ba,
            'saldo_total_rr': saldo_total_rr,
            'breakdown_ba': breakdown_ba,
            'breakdown_rr': breakdown_rr,
        }

        return render(request, 'admin/core/saldo/changelist.html', context)
```

**⚠️ CRITICAL:** DO NOT call `super().changelist_view()` - it would try to query the non-existent table!

---

## Calculator Logic

### File: `agora_web/core/utils/saldos.py`

The `SaldosCalculator` class provides two types of calculations:

#### 1. Total All-Time Balance

**Methods:** `calcular_saldo_bruno()` / `calcular_saldo_rafael()`

**Returns:**
```python
{
    'socio': 'BA',
    'saldo_total': 12500.45,  # Saldo com só valores PAGOS
    'saldo_projetado': 15200.30,  # Saldo com PAGOS + FINALIZADOS + PENDENTES (ou None)
    'ins': {
        'projetos_pessoais': 18000.00,  # PAGO
        'premios': 2500.00,  # PAGO
        'premios_nao_faturados': 1200.00,  # FINALIZADO
        'pessoais_nao_faturados': 500.00,  # FINALIZADO
        'investimento_inicial': 0.00,  # Não incluído (incluir_investimento=False)
        'total': 20500.00
    },
    'outs': {
        'despesas_fixas': 4200.50,
        'boletins_pendentes': 1500.00,
        'boletins_pagos': 3600.00,
        'boletins_total': 5100.00,
        'despesas_pessoais': 1310.20,
        'total': 9110.70
    },
    'sugestao_boletim': 1200.00
}
```

#### 2. Yearly Breakdown

**Method:** `calcular_saldo_ano(socio, ano)`

**Returns:**
```python
{
    'socio': 'BA',
    'ano': 2025,
    'ins_pagos': {
        'projetos_pessoais': 15000.00,  # PAGO
        'premios': 2000.00,  # PAGO
        'total': 17000.00
    },
    'ins_a_receber': {
        'projetos_pessoais': 500.00,  # FINALIZADO
        'premios': 300.00,  # FINALIZADO
        'total': 800.00
    },
    'ins_total': 17800.00,
    'outs_pagos': {
        'despesas_fixas': 3200.50,  # FIXA_MENSAL ÷ 2
        'boletins': 2500.00,  # PAGO
        'despesas_pessoais': 800.00,  # PAGO
        'total': 6500.50
    },
    'outs_por_pagar': {
        'boletins': 1200.00,  # PENDENTE
        'total': 1200.00
    },
    'outs_total': 7700.50,
    'saldo_efetivo': 10499.50,  # ins_pagos - outs_pagos
    'saldo_projetado': 10099.50,  # ins_total - outs_total
    'sugestao_boletim': 1260.00  # saldo_projetado ÷ meses_restantes
}
```

### Calculation Details

**INs (Company OWES to partner):**

1. **Projetos Pessoais (Pagos):**
   ```python
   Projeto.objects.filter(
       tipo=TipoProjeto.PESSOAL,
       owner=socio,  # 'BA' or 'RR'
       estado=EstadoProjeto.PAGO,
       data_faturacao__year=ano
   )
   ```

2. **Prémios (Pagos):**
   ```python
   Projeto.objects.filter(
       premio_bruno__gt=0,  # or premio_rafael
       estado=EstadoProjeto.PAGO,
       data_faturacao__year=ano
   )
   ```

3. **A Receber (Finalizados):**
   - Same as above but with `estado=EstadoProjeto.FINALIZADO`

**OUTs (Company PAID to partner):**

1. **Despesas Fixas ÷ 2:**
   ```python
   Despesa.objects.filter(
       tipo=TipoDespesa.FIXA_MENSAL,
       estado=EstadoDespesa.PAGO,
       data__year=ano
   ).aggregate(Sum('valor_sem_iva')) / Decimal('2.00')
   ```

2. **Boletins (Pagos):**
   ```python
   Boletim.objects.filter(
       socio_codigo=socio,  # 'BA' or 'RR'
       estado=EstadoBoletim.PAGO,
       data_emissao__year=ano
   )
   ```

3. **Boletins (Pendentes):**
   - Same as above but with `estado=EstadoBoletim.PENDENTE`

4. **Despesas Pessoais:**
   ```python
   Despesa.objects.filter(
       tipo=TipoDespesa.PESSOAL_BA,  # or PESSOAL_RR
       estado=EstadoDespesa.PAGO,
       data__year=ano
   )
   ```

**Sugestão de Boletim:**
```python
# Meses que já têm boletim
meses_com_boletim = Boletim.objects.filter(
    socio_codigo=socio,
    ano=ano
).values_list('mes', flat=True)

# Meses restantes sem boletim
mes_atual = today().month
meses_restantes = [m for m in range(mes_atual, 13) if m not in meses_com_boletim]

# Sugestão = saldo_projetado ÷ número de meses sem boletim
sugestao = max(0, saldo_projetado / len(meses_restantes))
```

---

## Template

### File: `agora_web/core/templates/admin/core/saldo/changelist.html`

### Key Features

**1. Responsive Grid:**
```css
.saldo-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 1rem;
}

@media (max-width: 768px) {
    .saldo-grid {
        grid-template-columns: 1fr;
    }
}
```

**2. Dark Mode Support:**
```css
/* Light mode */
.saldo-card { background-color: white; }
.saldo-header { color: rgb(17, 24, 39); }

/* Dark mode */
.dark .saldo-card { background-color: rgb(31, 41, 55); }
.dark .saldo-header { color: rgb(243, 244, 246); }
```

**3. Conditional Rendering:**
```django
{% if breakdown_ba.ins_a_receber.total > 0 %}
<div class="blue-bg">
    A Receber: €{{ breakdown_ba.ins_a_receber.total|floatformat:2 }}
</div>
{% endif %}
```

---

## Error History & Solutions

### Bug 1: Template Syntax Error

**Error:**
```
TemplateSyntaxError: Invalid block tag on line 61: 'else', expected 'endwith'
```

**Cause:** Invalid Django template syntax mixing `{% if %}` with `{% with %}`:
```django
{% if saldo %}{% with val=saldo %}{% else %}{% with val=other %}{% endif %}
```

**Solution:** Rewrite to use nested `{% if %}` blocks without `{% with %}`:
```django
{% if saldo %}{{ saldo }}{% else %}{{ other }}{% endif %}
```

**Commit:** b84be19

---

### Bug 2: Boletim Filtering Error

**Error:**
```
ValueError: Cannot assign "'BA'": "Boletim.socio" must be a "Socio" instance.
```

**Cause:** Filtering Boletim by `socio='BA'` when `socio` is a ForeignKey:
```python
Boletim.objects.filter(socio='BA')  # ❌ WRONG
```

**Solution:** Use `socio_codigo` field instead:
```python
Boletim.objects.filter(socio_codigo='BA')  # ✅ CORRECT
```

**Commit:** 933fee8

---

### Bug 3: Template Cache in Docker

**Problem:** Changes to template file not reflected in browser after git pull.

**Cause:** Docker container has stale copy of template file (volume mount not syncing).

**Solution:** Manually copy template to container:
```bash
docker cp core/templates/admin/core/saldo/changelist.html \
    $(docker compose -f docker-compose.cloudflare.yml ps -q web):/app/core/templates/admin/core/saldo/changelist.html

docker compose -f docker-compose.cloudflare.yml restart web
```

**Alternative:** Full rebuild with `--force-recreate`:
```bash
docker compose -f docker-compose.cloudflare.yml up -d --build --force-recreate web
```

---

## Testing

### Manual Testing

1. **Access:** `/admin/core/saldo/`
2. **Verify Top Cards:** Check all-time projected balances for BA and RR
3. **Verify Breakdown:** Check 2025 details match database
4. **Test Dark Mode:** Toggle theme and verify colors
5. **Test Mobile:** Resize browser to check responsive layout

### Shell Testing

```python
from core.utils.saldos import SaldosCalculator
from datetime import date

calc = SaldosCalculator()
ano = date.today().year

# Test all-time balances
saldo_ba = calc.calcular_saldo_bruno(incluir_investimento=False)
print(f"BA Total: €{saldo_ba['saldo_total']:,.2f}")
print(f"BA Projetado: €{saldo_ba.get('saldo_projetado', 'N/A')}")

# Test yearly breakdown
breakdown = calc.calcular_saldo_ano('BA', ano)
print(f"\nBreakdown {ano}:")
print(f"  INs Pagos: €{breakdown['ins_pagos']['total']:,.2f}")
print(f"  A Receber: €{breakdown['ins_a_receber']['total']:,.2f}")
print(f"  OUTs Pagos: €{breakdown['outs_pagos']['total']:,.2f}")
print(f"  Por Pagar: €{breakdown['outs_por_pagar']['total']:,.2f}")
print(f"  Saldo Efetivo: €{breakdown['saldo_efetivo']:,.2f}")
print(f"  Saldo Projetado: €{breakdown['saldo_projetado']:,.2f}")
print(f"  Sugestão Boletim: €{breakdown['sugestao_boletim']:,.2f}")
```

---

## Performance

**Current:** ~100-200ms page load
- Multiple database queries (Projeto, Despesa, Boletim)
- No caching (always real-time)
- PostgreSQL indexes on filtered fields

**Future Optimization (if needed):**
1. Add Redis caching (5-minute TTL)
2. Use `select_related()` / `prefetch_related()`
3. Create monthly snapshots table

---

## Lessons Learned

1. ✅ **Django template syntax** is strict - can't mix `{% if %}` with `{% with %}`
2. ✅ **ForeignKey filtering** requires correct field name (`socio_codigo` not `socio`)
3. ✅ **Docker volume mounts** may not sync immediately - use `docker cp` for critical files
4. ✅ **Separation of concerns** - all-time vs yearly breakdowns serve different purposes
5. ✅ **Color coding** improves UX - green/red/blue/orange for different categories
6. ✅ **Responsive design** is essential - 2 columns → 1 column on mobile

---

**Documentation by:** Claude Code
**Last Updated:** 2025-12-31
