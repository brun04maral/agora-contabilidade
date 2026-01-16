# Refatoração das Datas do Projeto

**Status:** 🚧 PROPOSTA - Aguarda aprovação final
**Data:** 2026-01-14
**Prioridade:** MÉDIA

---

## 📋 Situação Atual

### Campos de Data no Modelo `Projeto`:

```python
# Período do projeto
data_inicio = DateField(blank=True, null=True)
data_fim = DateField(blank=True, null=True)

# Faturação e pagamento
data_faturacao = DateField(blank=True, null=True)
data_vencimento = DateField(blank=True, null=True)  # ❌ REDUNDANTE
data_recibo = DateField(blank=True, null=True)      # ❌ REDUNDANTE COM data_vencimento
```

### Problemas Identificados:

1. **Redundância:** `data_vencimento` e `data_recibo` representam essencialmente a mesma coisa (quando foi/será pago)
2. **UX Separado:** `data_inicio` e `data_fim` são campos separados, mas representam um período contínuo
3. **Confusão Semântica:**
   - `data_vencimento` → quando DEVERIA ser pago (prazo)
   - `data_recibo` → quando FOI pago (facto)
   - Na prática, só importa quando FOI pago!

---

## 🎯 Proposta de Mudanças

### 1. Eliminar `data_vencimento` (REDUNDANTE)

**Justificação:**
- Só precisamos saber **quando o cliente pagou** (`data_recibo`)
- `data_vencimento` é informação que não usamos nos cálculos de saldos
- Simplifica o modelo e reduz confusão

**Impacto:**
- ⚠️ **Migration necessária:** Remover coluna `data_vencimento`
- ✅ **Sem impacto nos saldos:** Não é usado em `saldos.py`
- ⚠️ **Verificar se há dados:** Backup antes de remover

### 2. Substituir `data_inicio` + `data_fim` por DateRange Widget

**Opção A: Manter campos separados, melhorar UI**
```python
# Modelo mantém-se igual
data_inicio = DateField(blank=True, null=True)
data_fim = DateField(blank=True, null=True)

# Admin usa widget de date range
class ProjetoAdmin(UnfoldHistoryAdmin):
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # Usar widget date range picker (ex: django-daterange-filter)
        return form
```

**✅ Vantagens:**
- Sem migration necessária
- Mantém compatibilidade com dados existentes
- Melhora UX no admin (escolher período visualmente)

**❌ Desvantagens:**
- Ainda são 2 campos separados no modelo

---

**Opção B: PostgreSQL DateRange field**
```python
from django.contrib.postgres.fields import DateRangeField

# Novo campo
periodo = DateRangeField(
    verbose_name='Período do Projeto',
    blank=True,
    null=True,
    help_text='Período de execução do projeto'
)

# Manter campos antigos temporariamente (backward compat)
data_inicio = DateField(blank=True, null=True)  # DEPRECATED
data_fim = DateField(blank=True, null=True)      # DEPRECATED
```

**✅ Vantagens:**
- Semânticamente correto (período É um range)
- Queries mais poderosas (overlaps, contains, etc.)
- Widget nativo de date range no admin

**❌ Desvantagens:**
- ⚠️ **Migration complexa:** Migrar dados de 2 campos para 1
- ⚠️ **PostgreSQL specific:** Não funciona com SQLite (testes)
- 🔧 **Código existente precisa atualização:** Lógica de saldos usa `data_fim`

---

## 💡 Recomendação: Abordagem Híbrida

### Fase 1: Quick Wins (Imediato - 1h)

**1.1. Remover `data_vencimento`**
```python
# Migration
class Migration:
    operations = [
        migrations.RemoveField(
            model_name='projeto',
            name='data_vencimento',
        ),
    ]
```

**1.2. Atualizar fieldsets do ProjetoAdmin**
```python
('Datas', {
    'fields': ('data_inicio', 'data_fim', 'data_faturacao', 'data_recibo')
    # ❌ Removido: 'data_vencimento'
}),
```

**1.3. Atualizar help_text**
```python
data_recibo = models.DateField(
    _('Data Pagamento'),  # Nome mais claro
    blank=True,
    null=True,
    help_text='Data em que o cliente efetivamente pagou o projeto'
)
```

---

### Fase 2: Melhorar UX com Date Range Widget (Futuro - 2h)

**2.1. Instalar django-daterange-filter**
```bash
pip install django-daterange-filter
```

**2.2. Configurar no ProjetoAdmin**
```python
from daterange_filter.filter import DateRangeFilter

class ProjetoAdmin(UnfoldHistoryAdmin):
    # Widget para campos de data no formulário
    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name in ['data_inicio', 'data_fim']:
            # Aplicar widget de date range
            pass
        return super().formfield_for_dbfield(db_field, **kwargs)
```

**Nota:** Unfold pode já ter suporte nativo para date ranges - verificar docs!

---

## 🔍 Análise de Impacto

### Código que usa `data_vencimento`:

```bash
# Buscar referências
grep -r "data_vencimento" agora_web/
```

**Resultado esperado:**
- ✅ `models.py` - definição do campo
- ✅ `admin.py` - fieldsets (já identificado)
- ❓ `saldos.py` - **NÃO** usa (confirmado)
- ❓ Templates - verificar se há menções
- ❓ Fixtures/imports - verificar se Excel usa este campo

---

### Código que usa `data_inicio` / `data_fim`:

**Locais conhecidos:**
1. ✅ `models.py` - definição
2. ✅ `admin.py` - fieldsets, list_display
3. ⚠️ **`saldos.py`** - usa `data_fim` para determinar "trabalho feito"
4. ❓ Templates - verificar relatórios/dashboards
5. ❓ Management commands - import_from_excel

**Impacto em `saldos.py`:**
```python
# ATUAL
query_premios_feitos = Projeto.objects.filter(
    premio_bruno__gt=0,
    data_fim__lt=hoje  # ✅ CRÍTICO - não pode quebrar!
)
```

**Se mudar para DateRange:**
```python
# FUTURO (se usar DateRangeField)
from django.contrib.postgres.fields import DateRangeField
from psycopg2.extras import DateRange

query_premios_feitos = Projeto.objects.filter(
    premio_bruno__gt=0,
    periodo__endswith__lt=hoje  # DateRange query
)
```

---

## 📊 Análise de Dados Existentes (14 Jan 2026)

### Resultados da Query:

```
Total de projetos: 81
Com data_vencimento: 62 (76.5%)
Com data_recibo: 59 (72.8%)

Projetos com ambos os campos: 59
  - Iguais: 35 (59%)
  - Diferentes: 24 (41%) ⚠️
```

### ⚠️ **PROBLEMA IDENTIFICADO:**

**41% dos projetos** têm `data_vencimento` ≠ `data_recibo`!

**Exemplo real:**
```
Projeto #P0080:
  data_vencimento = 2025-12-03 (quando DEVERIA pagar)
  data_recibo = 2025-12-09 (quando EFETIVAMENTE pagou)
  → Cliente pagou 6 dias atrasado
```

### 💡 **Interpretação:**

- `data_vencimento` = **prazo/deadline** (quando cliente devia pagar)
- `data_recibo` = **pagamento real** (quando cliente efetivamente pagou)

**Estes campos NÃO são redundantes!** Têm significados diferentes.

---

## 🔄 **REVISÃO DA PROPOSTA**

### ❌ Proposta Original (REJEITADA):
~~Remover `data_vencimento` por ser redundante~~

### ✅ Nova Proposta (AJUSTADA):

**Manter ambos os campos, mas clarificar semântica:**

```python
# Renomear para maior clareza
data_vencimento → data_prazo (ou manter como está)
data_recibo → data_pagamento (mais claro)

# Help texts claros
data_vencimento = DateField(
    verbose_name='Data Vencimento',
    help_text='Prazo acordado para pagamento (deadline)'
)

data_recibo = DateField(
    verbose_name='Data Pagamento',  # ✅ Nome mais claro
    help_text='Data em que o cliente efetivamente pagou'
)
```

---

## 📝 Plano de Implementação AJUSTADO

### ✅ Fase 1: Clarificar Semântica (APROVADO)

**Mudanças mínimas:**
- [ ] Renomear label: `data_recibo` → **"Data Pagamento"**
- [ ] Adicionar help_text claro em ambos os campos
- [ ] Atualizar `admin.py` fieldsets com labels claros:
  ```python
  ('Datas', {
      'fields': ('data_inicio', 'data_fim', 'data_faturacao', 'data_vencimento', 'data_recibo')
  }),
  ```
- [ ] Atualizar documentação

**Estimativa:** 15min

**⚠️ NÃO REMOVER `data_vencimento`** - tem informação útil!

---

### ⏳ Fase 2: Date Range Widget (PENDENTE - Discussão)

**Questões a decidir:**

1. **Manter campos separados ou usar DateRangeField?**
   - Opção A: Campos separados + widget bonito (simples)
   - Opção B: DateRangeField PostgreSQL (correto semanticamente)

2. **Unfold já tem date range picker nativo?**
   - Verificar docs do Unfold antes de instalar libs externas

3. **Vale a pena o esforço?**
   - Benefício principal: UX mais agradável ao selecionar período
   - Custo: Migration + refactor de código que usa `data_fim`

**Recomendação:** **Deixar para depois da revisão de saldos** (prioridade maior)

---

## 🧪 Queries de Verificação

### Verificar uso de `data_vencimento`:
```sql
-- Quantos projetos têm data_vencimento?
SELECT COUNT(*) FROM projetos WHERE data_vencimento IS NOT NULL;

-- Comparar com data_recibo (são iguais?)
SELECT
    COUNT(*) as total,
    COUNT(CASE WHEN data_vencimento = data_recibo THEN 1 END) as iguais,
    COUNT(CASE WHEN data_vencimento != data_recibo THEN 1 END) as diferentes
FROM projetos
WHERE data_vencimento IS NOT NULL AND data_recibo IS NOT NULL;
```

### Verificar uso de `data_inicio` / `data_fim`:
```sql
-- Quantos projetos têm período definido?
SELECT
    COUNT(*) as total,
    COUNT(data_inicio) as com_inicio,
    COUNT(data_fim) as com_fim,
    COUNT(CASE WHEN data_inicio IS NOT NULL AND data_fim IS NOT NULL THEN 1 END) as ambos
FROM projetos;

-- Projetos com data_fim no passado (trabalho feito)
SELECT COUNT(*) FROM projetos
WHERE data_fim < CURRENT_DATE;
```

---

## 📊 Comparação de Opções

| Aspecto | Opção A: Manter Separado + Widget | Opção B: DateRangeField PostgreSQL |
|---------|-----------------------------------|-------------------------------------|
| **Migration** | ✅ Não precisa | ❌ Complexa (2 campos → 1) |
| **Código existente** | ✅ Continua funcionando | ❌ Precisa refactor (saldos.py) |
| **UX** | ✅ Bom (com widget) | ✅ Bom (nativo) |
| **Semântica** | ⚠️ Ainda são 2 campos | ✅ Correto (IS-A range) |
| **Queries** | ✅ Simples (`data_fim__lt`) | ⚠️ Mais complexas (`periodo__endswith__lt`) |
| **Portabilidade** | ✅ Qualquer DB | ❌ PostgreSQL only |
| **Esforço** | 🟢 Baixo (1-2h) | 🔴 Alto (4-6h) |

**Vencedor:** **Opção A** (manter separado + melhorar widget)
- Pragmático: funciona bem, baixo risco
- Pode migrar para Opção B no futuro se necessário

---

## 🎯 Decisão Final Recomendada

### Ação Imediata (HOJE):
1. ✅ **Remover `data_vencimento`** - redundante com `data_recibo`
2. ✅ **Renomear label** `data_recibo` → "Data Pagamento" (mais claro)

### Ação Futura (DEPOIS da revisão de saldos):
3. ⏳ **Avaliar date range widget** - melhorar UX de `data_inicio` + `data_fim`
4. ⏳ **Considerar DateRangeField** - se houver necessidade de queries complexas

---

## 📚 Referências

- Django DateRangeField: https://docs.djangoproject.com/en/5.0/ref/contrib/postgres/fields/#daterangefield
- Unfold Admin: https://unfoldadmin.com/ (verificar date widgets)
- django-daterange-filter: https://github.com/tzulberti/django-datefilter

---

**Documentado por:** Claude Sonnet 4.5
**Aguarda aprovação de:** Bruno
**Próximos passos:** Decidir sobre date range widget (Fase 2)
