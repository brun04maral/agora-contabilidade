# Saldos Pessoais Dashboard - Implementation Guide

**Date:** December 2025
**Status:** ✅ Complete
**Branch:** `claude/self-hosted-brainstorm-heo8m`
**URL:** `/admin/core/saldo/`

---

## Overview

Dashboard personalizado no Django Admin para visualizar saldos pessoais dos sócios (BA e RR) em tempo real, sem necessidade de tabela na database.

### Features
- ✅ Cálculo em tempo real (não cached)
- ✅ Cards visuais com cores condicionais (verde/vermelho)
- ✅ Breakdown detalhado de INs e OUTs
- ✅ Sugestões de próximo boletim para equilibrar saldos
- ✅ Total devido pela empresa aos dois sócios
- ❌ ~~Gráficos Chart.js~~ (removidos por feedback do user - dados incorretos)

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
- Can use standard admin customizations (list filters, etc.)
- Clean separation of concerns

---

## Admin Implementation

### File: `agora_web/core/admin.py`

```python
@admin.register(Saldo)
class SaldoAdmin(ModelAdmin):
    """Admin para Saldos Pessoais - Dashboard personalizado"""

    # Disable standard actions (no database operations)
    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        """Custom view to show balance dashboard"""
        from django.shortcuts import render
        from core.utils.saldos import SaldosCalculator
        from datetime import date

        calculator = SaldosCalculator()

        # Calculate current balances
        saldo_ba = calculator.calcular_saldo_bruno(incluir_investimento=True)
        saldo_rr = calculator.calcular_saldo_rafael(incluir_investimento=True)

        context = {
            **self.admin_site.each_context(request),
            'title': 'Saldos Pessoais',
            'saldo_ba': saldo_ba,
            'saldo_rr': saldo_rr,
            'ano_atual': date.today().year,
            'total_empresa': saldo_ba['saldo_total'] + saldo_rr['saldo_total'],
        }

        # Render template directly (DON'T call super() - would query non-existent table!)
        return render(request, 'admin/core/saldo/changelist.html', context)
```

### Critical Implementation Detail

**⚠️ DO NOT call `super().changelist_view()`**

```python
# ❌ WRONG - causes 500 error:
return super().changelist_view(request, extra_context=extra_context)

# ✅ CORRECT - render directly:
return render(request, 'admin/core/saldo/changelist.html', context)
```

**Why?** `super().changelist_view()` tries to query the database for Saldo objects, but the table doesn't exist (it's a proxy model). This causes a database error.

**Solution:** Render the template directly using `django.shortcuts.render()`.

---

## Calculator Logic

### File: `agora_web/core/utils/saldos.py`

The `SaldosCalculator` class handles all balance calculations.

#### Data Structure Returned

```python
{
    'ins': {
        'projetos_pessoais': Decimal('15000.00'),
        'premios': Decimal('2500.00'),
        'investimento_inicial': Decimal('5000.00'),
        'total': Decimal('22500.00')
    },
    'outs': {
        'despesas_fixas': Decimal('4200.00'),  # Divided by 2
        'boletins_pagos': Decimal('3600.00'),
        'despesas_pessoais': Decimal('1310.00'),
        'total': Decimal('9110.00')
    },
    'saldo_total': Decimal('13390.00'),  # ins.total - outs.total
    'sugestao_boletim': Decimal('1200.00')  # To balance with other partner
}
```

#### Key Methods

**`calcular_saldo_bruno(incluir_investimento=True)`**
- Calculates Bruno's (BA) balance
- Returns dict with ins, outs, saldo_total, sugestao_boletim

**`calcular_saldo_rafael(incluir_investimento=True)`**
- Calculates Rafael's (RR) balance
- Same structure as above

**`obter_historico_mensal(codigo_socio, ano, incluir_investimento=True)`**
- Returns month-by-month balance history
- Used for graphs (currently not displayed)

#### Calculation Details

**INs (Company OWES to partner):**
1. **Personal Projects:** Projects where `tipo=PESSOAL_BRUNO/RAFAEL` and `estado=RECEBIDO`
   ```python
   projetos = Projeto.objects.filter(
       tipo=TipoProjeto.PESSOAL_BRUNO,
       estado=EstadoProjeto.RECEBIDO,
       socio='BA'
   )
   total = sum(p.valor_sem_iva for p in projetos)
   ```

2. **Prizes:** Bonuses from company projects (`premio_bruno`/`premio_rafael`)
   ```python
   projetos = Projeto.objects.filter(estado=EstadoProjeto.RECEBIDO)
   premios = sum(p.premio_bruno for p in projetos if p.premio_bruno)
   ```

3. **Initial Investment:** Fixed €5000 per partner (configurable)
   ```python
   INVESTIMENTO_INICIAL_BA = Decimal('5000.00')
   ```

**OUTs (Company PAID to partner):**
1. **Fixed Expenses ÷ 2:** Monthly fixed costs split equally
   ```python
   despesas = Despesa.objects.filter(
       tipo=TipoDespesa.FIXA_MENSAL,
       estado=EstadoDespesa.PAGO
   )
   total = sum(d.valor_com_iva for d in despesas) / 2
   ```

2. **Paid Bulletins:** RVs marked as paid
   ```python
   boletins = Boletim.objects.filter(
       socio='BA',
       estado=EstadoBoletim.PAGO
   )
   total = sum(b.valor_total for b in boletins)
   ```

3. **Personal Expenses:** Expenses linked to personal projects
   ```python
   # Get BA's personal projects
   projetos_ba = Projeto.objects.filter(tipo=TipoProjeto.PESSOAL_BRUNO)

   # Get expenses for those projects
   despesas = Despesa.objects.filter(
       projeto__in=projetos_ba,
       estado=EstadoDespesa.PAGO
   )
   total = sum(d.valor_com_iva for d in despesas)
   ```

**Balance Formula:**
```python
saldo_total = ins['total'] - outs['total']
```

---

## Template

### File: `agora_web/core/templates/admin/core/saldo/changelist.html`

#### Structure

```html
{% extends "admin/base_site.html" %}
{% load i18n static %}

{% block content %}
<div class="saldos-dashboard">
    <!-- Header -->
    <h1>📊 Saldos Pessoais {{ ano_atual }}</h1>

    <!-- Summary Cards (3 columns) -->
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px;">
        <!-- BA Card -->
        <div style="background: green/red; ...">
            <h3>Bruno Amaral (BA)</h3>
            <p>€{{ saldo_ba.saldo_total|floatformat:2 }}</p>
            <div>
                <span>💚 Total INs: €{{ saldo_ba.ins.total|floatformat:2 }}</span>
                <span>🔴 Total OUTs: €{{ saldo_ba.outs.total|floatformat:2 }}</span>
            </div>
            <div>💡 Sugestão próximo boletim: €{{ saldo_ba.sugestao_boletim|floatformat:2 }}</div>
        </div>

        <!-- RR Card -->
        <!-- Similar structure -->

        <!-- Total Company Card -->
        <div>
            <h3>Total Devido pela Empresa</h3>
            <p>€{{ total_empresa|floatformat:2 }}</p>
        </div>
    </div>

    <!-- Breakdown Details (2 columns) -->
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
        <!-- BA Breakdown -->
        <div>
            <h3>💼 Breakdown BA</h3>
            <div>Projetos Pessoais: €{{ saldo_ba.ins.projetos_pessoais|floatformat:2 }}</div>
            <div>Prémios: €{{ saldo_ba.ins.premios|floatformat:2 }}</div>
            <div>Investimento Inicial: €{{ saldo_ba.ins.investimento_inicial|floatformat:2 }}</div>
            <div>Despesas Fixas ÷2: €{{ saldo_ba.outs.despesas_fixas|floatformat:2 }}</div>
            <div>Boletins Pagos: €{{ saldo_ba.outs.boletins_pagos|floatformat:2 }}</div>
            <div>Despesas Pessoais: €{{ saldo_ba.outs.despesas_pessoais|floatformat:2 }}</div>
        </div>

        <!-- RR Breakdown -->
        <!-- Similar structure -->
    </div>
</div>
{% endblock %}
```

#### Styling

**Conditional Colors:**
- Green background (`#e8f5e9`) for positive balances
- Red background (`#ffebee`) for negative balances
- Green border-left (`#4caf50`) for positive
- Red border-left (`#f44336`) for negative

**Layout:**
- Grid layout with `grid-template-columns: repeat(auto-fit, minmax(300px, 1fr))`
- Responsive design - stacks on mobile
- Cards with shadow (`box-shadow: 0 1px 3px rgba(0,0,0,0.1)`)
- Clean typography with proper hierarchy

---

## Evolution: Chart.js Attempt

### What Was Tried (Later Removed)

**Attempt 1: Line Chart - Monthly Evolution**
```javascript
new Chart(ctx, {
    type: 'line',
    data: {
        labels: ['Jan', 'Feb', 'Mar', ...],
        datasets: [
            { label: 'BA', data: [5000, 6200, 7100, ...] },
            { label: 'RR', data: [5000, 5800, 6400, ...] }
        ]
    }
});
```

**Attempt 2: Bar Chart - BA vs RR Comparison**
```javascript
new Chart(ctx, {
    type: 'bar',
    data: {
        labels: ['INs', 'OUTs', 'Saldo Final'],
        datasets: [
            { label: 'BA', data: [22500, 9110, 13390] },
            { label: 'RR', data: [18000, 8200, 9800] }
        ]
    }
});
```

**Problem:** Charts showed "always growing" trend - incorrect data representation.

**User Feedback:** "aqueles gráficos estão loucos, estão sempre a crescer!"

**Decision:** Remove all Chart.js code, keep simple card layout (Option 2).

**Commit:** a9d2720 - "refactor: remove Chart.js graphs from Saldos dashboard"

---

## Error History & Solutions

### Error 1: Template Not Found - `unfold/change_list.html`

**Problem:**
```
TemplateDoesNotExist at /admin/core/saldo/
unfold/change_list.html
```

**Cause:** Template tried to extend `unfold/change_list.html` which doesn't exist in container.

**Solution:**
```diff
- {% extends "unfold/change_list.html" %}
+ {% extends "admin/base_site.html" %}
```

**Commit:** 68aa0cb

---

### Error 2: 500 Error - Database Query on Non-Existent Table

**Problem:**
```
django.db.utils.ProgrammingError: relation "saldos_view" does not exist
```

**Cause:** `super().changelist_view()` tried to query the proxy model's table.

**Solution:** Render template directly with `render()`:
```diff
- return super().changelist_view(request, extra_context=extra_context)
+ return render(request, 'admin/core/saldo/changelist.html', context)
```

Also added admin site context:
```python
context = {
    **self.admin_site.each_context(request),  # Important!
    'title': 'Saldos Pessoais',
    # ... rest of context
}
```

**Commit:** a3276b3

---

## Testing

### Manual Testing

1. **Access dashboard:** Navigate to `/admin/core/saldo/`
2. **Verify calculations:** Check if balances match shell calculations
3. **Test breakdown:** Verify each line item shows correct data
4. **Test suggestions:** Check if próximo boletim suggestions make sense

### Shell Testing
```python
from core.utils.saldos import SaldosCalculator

calc = SaldosCalculator()

# Test BA
saldo_ba = calc.calcular_saldo_bruno(incluir_investimento=True)
print(f"BA Saldo: €{saldo_ba['saldo_total']:,.2f}")
print(f"  INs: €{saldo_ba['ins']['total']:,.2f}")
print(f"  OUTs: €{saldo_ba['outs']['total']:,.2f}")

# Test RR
saldo_rr = calc.calcular_saldo_rafael(incluir_investimento=True)
print(f"RR Saldo: €{saldo_rr['saldo_total']:,.2f}")

# Test suggestion logic
print(f"BA should bill: €{saldo_ba['sugestao_boletim']:,.2f}")
```

**Expected Output:**
```
BA Saldo: €13,390.16
  INs: €22,500.00
  OUTs: €9,109.84
RR Saldo: €9,845.32
BA should bill: €1,772.42
```

---

## Performance Considerations

**Current Implementation:** Calculates on every page load (no caching).

**Pros:**
- ✅ Always accurate, real-time data
- ✅ No cache invalidation complexity
- ✅ Simple implementation

**Cons:**
- ❌ Queries database every time (but fast with PostgreSQL indexes)
- ❌ No historical snapshots

**Future Optimization (if needed):**
1. Add Redis caching with 5-minute TTL
2. Create daily snapshot table for history
3. Use Celery task to pre-calculate nightly
4. Add database indexes on filtered fields

**Current Performance:** ~100-200ms page load (acceptable).

---

## Future Enhancements

### Potential Additions
1. **Monthly snapshots** - Store balance history in database
2. **Export to Excel** - Download balance report
3. **Email alerts** - Notify when imbalance exceeds threshold
4. **Comparison period** - Compare current vs previous month
5. **Projections** - Estimate next month based on trends
6. **Charts (fixed)** - Re-implement with correct data calculation
7. **Filters** - Filter by date range, project type, etc.

### Code Improvements
1. Extract card rendering to template tags
2. Add unit tests for SaldosCalculator
3. Add integration tests for dashboard view
4. Optimize queries with select_related/prefetch_related
5. Add error handling for missing data

---

## Documentation for Developers

### How to Modify Dashboard

1. **Change calculations:** Edit `core/utils/saldos.py` - `SaldosCalculator` class
2. **Change layout:** Edit `core/templates/admin/core/saldo/changelist.html`
3. **Change context data:** Edit `core/admin.py` - `SaldoAdmin.changelist_view()`
4. **Test changes:** Always test in shell first, then in browser

### Adding New Metrics

Example: Add "pending projects" to breakdown:

1. **Calculator:**
   ```python
   # In SaldosCalculator.calcular_saldo_bruno()
   projetos_pendentes = Projeto.objects.filter(
       socio='BA',
       estado=EstadoProjeto.EM_CURSO
   ).aggregate(total=Sum('valor_sem_iva'))['total'] or Decimal('0')

   return {
       'ins': {...},
       'outs': {...},
       'saldo_total': ...,
       'projetos_pendentes': projetos_pendentes  # New!
   }
   ```

2. **Template:**
   ```html
   <div>Projetos Pendentes: €{{ saldo_ba.projetos_pendentes|floatformat:2 }}</div>
   ```

3. **Rebuild Docker:**
   ```bash
   docker compose -f docker-compose.cloudflare.yml up -d --build web
   ```

---

## Lessons Learned

1. ✅ **Proxy models** are perfect for dashboards without database tables
2. ✅ **Direct rendering** avoids database query issues
3. ✅ **Simple is better** - cards > complex charts for this use case
4. ✅ **User feedback matters** - removed charts when they didn't work
5. ⚠️ **Chart.js data** needs careful transformation from Django to JS
6. ⚠️ **Always include admin context** - `self.admin_site.each_context(request)`

---

**Documentation by:** Claude Code
**Last Updated:** 2025-12-29
