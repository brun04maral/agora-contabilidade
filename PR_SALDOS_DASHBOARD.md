# Pull Request: Redesign Saldos Dashboard

**Branch:** `claude/review-balance-logic-0omT0` → `main`
**Title:** `feat: redesign saldos dashboard with yearly breakdown and improved UX`

---

## 📊 Redesign do Dashboard de Saldos Pessoais

### Resumo
Redesenho completo do dashboard de saldos pessoais com foco em usabilidade e clareza de informação, separando saldos totais (all-time) de breakdown anual detalhado.

### ✨ Principais Alterações

#### 1. **Nova Estrutura de Página**
- **Cards de Topo (2 colunas):** Saldo projetado total (all-time) para BA e RR
- **Breakdown Anual (2 colunas):** Detalhes do ano corrente (2025) por sócio
- Removido card "Total Devido pela Empresa" (informação redundante)

#### 2. **Breakdown Detalhado por Ano**
Novo método `SaldosCalculator.calcular_saldo_ano(socio, ano)` que retorna:

**INs (Entradas):**
- Projetos Pessoais (pagos) - verde
- Prémios (pagos) - verde
- A Receber (finalizados) - azul

**OUTs (Saídas):**
- Despesas Fixas ÷2 - vermelho
- Boletins Pagos - vermelho
- Despesas Pessoais - vermelho
- Por Pagar (boletins pendentes) - laranja

**Resumo:**
- **Saldo Efetivo:** Apenas valores pagos (INs pagos - OUTs pagos)
- **Saldo Projetado:** Com valores pendentes (INs total - OUTs total)
- **Sugestão de Boletim:** Saldo projetado ÷ meses restantes sem boletim

#### 3. **Melhorias de UX**
- ✅ Color coding consistente (verde/vermelho/azul/laranja)
- ✅ Dark mode support
- ✅ Layout responsivo (2 colunas → 1 coluna em mobile)
- ✅ Separação clara entre pagos vs pendentes
- ✅ Conditional rendering (esconde secções vazias)

### 🐛 Bugs Corrigidos

1. **Template Syntax Error** (b84be19)
   - Corrigida sintaxe Django inválida misturando `{% if %}` com `{% with %}`

2. **Boletim Filtering Error** (933fee8)
   - Corrigido uso de `socio_codigo` em vez de `socio` para filtrar Boletim

3. **Template Cache in Docker**
   - Documentado workaround para sync de templates em Docker

### 📝 Ficheiros Alterados

**Core:**
- `agora_web/core/utils/saldos.py` - Novo método `calcular_saldo_ano()`
- `agora_web/core/admin.py` - Atualizado `SaldoAdmin.changelist_view()`
- `agora_web/core/templates/admin/core/saldo/changelist.html` - Template redesenhado

**Documentação:**
- `.claude/claude.md` - Atualizada secção de Saldos
- `docs/SALDOS_DASHBOARD.md` - Reescrita completa com nova estrutura

### 🧪 Testing

```python
from core.utils.saldos import SaldosCalculator
from datetime import date

calc = SaldosCalculator()
ano = date.today().year

# Saldos totais (all-time)
saldo_ba = calc.calcular_saldo_bruno(incluir_investimento=False)
saldo_rr = calc.calcular_saldo_rafael(incluir_investimento=False)

# Breakdown anual (2025)
breakdown_ba = calc.calcular_saldo_ano('BA', ano)
breakdown_rr = calc.calcular_saldo_ano('RR', ano)
```

### 📸 Layout

```
┌────────────────────┬────────────────────┐
│ Bruno Amaral (BA)  │ Rafael Reigota(RR) │
│ € 12,345.67        │ € 8,901.23         │
│ Saldo Projetado    │ Saldo Projetado    │
└────────────────────┴────────────────────┘

┌─────── Breakdown 2025 ─────────────────┐
│ BA                 │ RR                 │
├────────────────────┼────────────────────┤
│ • INs Pagos        │ • INs Pagos        │
│ • A Receber        │ • A Receber        │
│ • OUTs Pagos       │ • OUTs Pagos       │
│ • Por Pagar        │ • Por Pagar        │
│ • Saldo Efetivo    │ • Saldo Efetivo    │
│ • Saldo Projetado  │ • Saldo Projetado  │
│ • Sugestão Boletim │ • Sugestão Boletim │
└────────────────────┴────────────────────┘
```

### 📚 Documentação
Ver `docs/SALDOS_DASHBOARD.md` para documentação completa incluindo:
- Architecture details
- Calculator logic
- Error history & solutions
- Testing guide

### 🎯 Commits Principais

- `9675326` - docs: completely rewrite SALDOS_DASHBOARD.md with new structure
- `2b2c521` - docs: update saldos documentation and remove debug code
- `92e2d20` - refactor: simplify saldos dashboard - remove company total card
- `b84be19` - fix: correct Django template syntax
- `933fee8` - fix: use socio_codigo instead of socio for Boletim filtering
- `88b66f2` - fix: calculate total_empresa correctly (BA+RR)
- `f1e713a` - debug: add try-except to show detailed error (later removed)

---

**Reviewed-by:** User feedback during development
**Tested:** Manual testing + shell calculations verified
**Ready to merge:** ✅ Yes
