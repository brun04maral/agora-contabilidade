# Especificação para Revisão da Lógica de Saldos Pessoais

**Status:** 🚧 PENDENTE - Especificação aprovada, implementação futura
**Data:** 2026-01-14
**Prioridade:** ALTA (core business logic)

---

## ⚠️ Problema Atual

A lógica de cálculo de saldos em `core/utils/saldos.py` tem **inconsistências** entre:
- Campos de datas (`data_recibo`, `data_faturacao`, `data_fim`)
- Campo `estado` dos projetos
- Critérios para INs ATUAL vs PROJETADO

**Resultado:** Projetos pagos podem não aparecer nos saldos se faltarem campos específicos.

---

## 🎯 Conceito Core (Confirmado)

**Empresa = Intermediário Financeiro entre Sócios e Clientes**

```
Cliente → paga → Empresa → deve → Sócio
                    ↓
                  (Custos)
                    ↓
Empresa → paga → Sócio (via boletins/despesas)
```

**Saldo = Quanto a empresa DEVE ao sócio**

---

## 📊 Especificação: SALDO ATUAL vs PROJETADO

### **SALDO ATUAL** (Dinheiro já devido - pode levantar HOJE)

#### INs (Empresa DEVE ao sócio):

**1. Projetos Pessoais PAGOS:**
```python
Projeto.objects.filter(
    tipo=PESSOAL,
    socio=socio_codigo,
    data_recibo__isnull=False,  # Cliente JÁ PAGOU
    estado__in=[PAGO, FINALIZADO, ATIVO]  # Exclui CANCELADO
).aggregate(Sum('valor_sem_iva'))
```
✅ **Critério:** `data_recibo` existe (cliente pagou)
✅ **Ignora:** Projetos `CANCELADO`

**2. Prémios de Trabalho FEITO:**
```python
Projeto.objects.filter(
    Q(premio_bruno__gt=0) | Q(premio_rafael__gt=0),
    data_fim__lt=date.today(),  # Trabalho JÁ ACONTECEU
    estado__in=[PAGO, FINALIZADO, ATIVO]  # Exclui CANCELADO
).aggregate(Sum(campo_premio))
```
✅ **Critério:** `data_fim < hoje` (trabalho aconteceu)
✅ **Ignora:** Projetos `CANCELADO`
⚠️ **Nota:** Não precisa `data_faturacao` - prémio é devido assim que trabalho termina

#### OUTs (Empresa PAGOU ao sócio):

**3. Despesas Fixas PAGAS ÷ 2:**
```python
Despesa.objects.filter(
    tags__codigo__in=['ADMINISTRATIVO', 'ORDENADO', 'SUB_ALIMENTACAO'],
    data__isnull=False  # Despesa tem data (já aconteceu)
).aggregate(Sum('valor_sem_iva')) / 2
```
✅ **Dividido por 2** (50/50 entre sócios)
✅ **Todas as despesas fixas** com data (assumido como pagas)

**4. Boletins PAGOS:**
```python
Boletim.objects.filter(
    socio__codigo=socio_codigo,
    estado=PAGO
).aggregate(Sum('valor_total'))
```
✅ **Critério:** `estado=PAGO`

**5. Despesas Pessoais PAGAS:**
```python
Despesa.objects.filter(
    tags__codigo=f'PESSOAL_{socio_codigo}'  # PESSOAL_BA ou PESSOAL_RR
).aggregate(Sum('valor_sem_iva'))
```
✅ **Todas as despesas pessoais** (assumido como pagas)

---

### **SALDO PROJETADO** (Planeamento futuro - fim do ano)

#### INs (Empresa DEVE ou VAI DEVER ao sócio):

**1. Projetos Pessoais PAGOS:**
```python
# Mesmo que SALDO ATUAL
Projeto.objects.filter(
    tipo=PESSOAL,
    socio=socio_codigo,
    data_recibo__isnull=False,
    estado__in=[PAGO, FINALIZADO, ATIVO]
)
```

**2. Projetos Pessoais A RECEBER (FINALIZADOS sem recibo):**
```python
Projeto.objects.filter(
    tipo=PESSOAL,
    socio=socio_codigo,
    estado=FINALIZADO,  # Trabalho feito
    data_recibo__isnull=True  # Mas cliente ainda não pagou
).aggregate(Sum('valor_sem_iva'))
```
✅ **Novo!** Conta projetos finalizados mas ainda não pagos pelo cliente

**3. Prémios de TODOS os Projetos (incluindo futuros):**
```python
Projeto.objects.filter(
    Q(premio_bruno__gt=0) | Q(premio_rafael__gt=0),
    estado__in=[PAGO, FINALIZADO, ATIVO]  # Exclui CANCELADO
    # SEM filtro de data_fim!
).aggregate(Sum(campo_premio))
```
✅ **Critério:** Todos os prémios de projetos ativos/finalizados/pagos
✅ **Inclui futuros:** Projetos com `data_fim` no futuro
✅ **Ignora:** Projetos `CANCELADO`

#### OUTs (Empresa PAGOU ou VAI PAGAR ao sócio):

**4. Despesas Fixas ÷ 2 (todas):**
```python
# Mesmo que SALDO ATUAL, mas SEM filtro de data
# (ou com filtro até final do ano)
Despesa.objects.filter(
    tags__codigo__in=['ADMINISTRATIVO', 'ORDENADO', 'SUB_ALIMENTACAO']
).aggregate(Sum('valor_sem_iva')) / 2
```
✅ **Inclui despesas fixas futuras** (até fim do ano se houver)

**5. Boletins TODOS (PAGO + PENDENTE):**
```python
Boletim.objects.filter(
    socio__codigo=socio_codigo,
    estado__in=[PAGO, PENDENTE]
).aggregate(Sum('valor_total'))
```
✅ **Critério:** `estado=PAGO` OU `estado=PENDENTE`
✅ **Inclui obrigações fiscais** já declaradas mas ainda não pagas

**6. Despesas Pessoais (todas):**
```python
# Mesmo que SALDO ATUAL
Despesa.objects.filter(
    tags__codigo=f'PESSOAL_{socio_codigo}'
)
```

---

## 🔄 Mudanças Necessárias no Código

### 1. Adicionar Filtros de `estado` em Projetos

**Problema atual:**
```python
# ❌ NÃO filtra por estado - projetos CANCELADOS contam!
Projeto.objects.filter(tipo=PESSOAL, data_recibo__isnull=False)
```

**Correção:**
```python
# ✅ Exclui projetos CANCELADOS
Projeto.objects.filter(
    tipo=PESSOAL,
    data_recibo__isnull=False,
    estado__in=[EstadoProjeto.PAGO, EstadoProjeto.FINALIZADO, EstadoProjeto.ATIVO]
)
```

### 2. Adicionar Categoria "A Receber" no PROJETADO

**Nova query (não existe atualmente):**
```python
# Projetos FINALIZADOS mas cliente ainda não pagou
projetos_a_receber = Projeto.objects.filter(
    tipo=PESSOAL,
    socio=socio_codigo,
    estado=EstadoProjeto.FINALIZADO,
    data_recibo__isnull=True
).aggregate(Sum('valor_sem_iva'))['total'] or Decimal('0.00')
```

**Retornar no dict:**
```python
return {
    'ins': {
        'projetos_pessoais_pagos': ...,
        'projetos_pessoais_a_receber': ...,  # ✅ NOVO
        'premios': ...,
    }
}
```

### 3. Remover Filtro de `data_fim` dos Prémios PROJETADO

**Problema atual:**
```python
# ❌ Só conta prémios passados no PROJETADO
query_premios_todos = Projeto.objects.filter(
    premio_bruno__gt=0
    # SEM filtro de data_fim
)
```

**Está correto!** Mas deve adicionar filtro de `estado`:
```python
# ✅ Todos os prémios (passado + futuro), exceto CANCELADO
query_premios_todos = Projeto.objects.filter(
    premio_bruno__gt=0,
    estado__in=[EstadoProjeto.PAGO, EstadoProjeto.FINALIZADO, EstadoProjeto.ATIVO]
)
```

### 4. Template: Mostrar "A Receber" separadamente

**No breakdown anual:**
```django
<!-- INs PAGOS -->
<div class="green-bg">
    Projetos Pessoais (pagos): €{{ breakdown.ins_pagos.projetos_pessoais }}
</div>

<!-- INs A RECEBER (NOVO) -->
{% if breakdown.ins_a_receber.projetos_pessoais > 0 %}
<div class="blue-bg">
    Projetos Pessoais (a receber): €{{ breakdown.ins_a_receber.projetos_pessoais }}
</div>
{% endif %}
```

---

## ⚡ Mudanças Automáticas de Estado (Futura)

**Especificação adicional (não urgente):**

### Estado Automático: ATIVO → FINALIZADO

```python
# Management command ou signal
# Quando data_fim < hoje e estado=ATIVO → mudar para FINALIZADO

Projeto.objects.filter(
    data_fim__lt=date.today(),
    estado=EstadoProjeto.ATIVO
).update(estado=EstadoProjeto.FINALIZADO)
```

**Executar:**
- Diariamente (cron job ou Celery)
- Ou ao aceder dashboard de saldos
- Ou em signal `pre_save` do modelo Projeto

---

## 📋 Checklist de Implementação

### Fase 1: Corrigir Lógica Core (PRIORITÁRIO)
- [ ] Adicionar filtros `estado__in=[PAGO, FINALIZADO, ATIVO]` em todas as queries de Projeto
- [ ] Adicionar query "Projetos A Receber" (FINALIZADO sem data_recibo)
- [ ] Atualizar `SaldosCalculator._calcular_saldo()` com nova lógica
- [ ] Testar no Django shell com dados reais

### Fase 2: Atualizar Template
- [ ] Adicionar secção "A Receber" no breakdown (azul)
- [ ] Verificar cores e layout
- [ ] Testar com dados reais (incluir screenshot no commit)

### Fase 3: Documentação
- [ ] Atualizar `docs/SALDOS_DASHBOARD.md` com nova lógica
- [ ] Atualizar docstrings em `core/utils/saldos.py`
- [ ] Atualizar `.claude/claude.md` com critérios atualizados

### Fase 4: Estados Automáticos (OPCIONAL)
- [ ] Criar management command `update_project_states`
- [ ] Adicionar ao cron ou scheduler
- [ ] Ou implementar em signal `pre_save` de Projeto

### Fase 5: Testes & Validação
- [ ] Criar testes unitários para `SaldosCalculator`
- [ ] Validar com dados de 2025 completos
- [ ] Comparar com Excel antigo (se aplicável)

---

## 🧪 Cenários de Teste

### Cenário 1: Projeto Pessoal Pago
```
Projeto #P0081:
  tipo=PESSOAL, socio=BA
  valor_sem_iva=€250
  estado=PAGO
  data_recibo=2026-01-14

Esperado:
  ✅ ATUAL INs: +€250
  ✅ PROJETADO INs: +€250
```

### Cenário 2: Projeto Finalizado mas Não Pago
```
Projeto #P0082:
  tipo=PESSOAL, socio=RR
  valor_sem_iva=€1000
  estado=FINALIZADO
  data_recibo=None

Esperado:
  ❌ ATUAL INs: +€0 (cliente não pagou ainda)
  ✅ PROJETADO INs: +€1000 (A Receber - azul)
```

### Cenário 3: Projeto Futuro com Prémio
```
Projeto #P0083:
  tipo=EMPRESA, socio=None
  premio_bruno=€500
  data_fim=2026-02-15 (futuro)
  estado=ATIVO

Esperado:
  ❌ ATUAL INs: +€0 (trabalho ainda não aconteceu)
  ✅ PROJETADO INs: +€500 (trabalho agendado)
```

### Cenário 4: Projeto Cancelado
```
Projeto #P0084:
  tipo=PESSOAL, socio=BA
  valor_sem_iva=€2000
  estado=CANCELADO
  data_recibo=2026-01-10

Esperado:
  ❌ ATUAL INs: +€0 (cancelado, não conta)
  ❌ PROJETADO INs: +€0 (cancelado, não conta)
```

### Cenário 5: Boletim Pendente
```
Boletim #B-BA-2026-01:
  socio=BA
  valor_total=€1200
  estado=PENDENTE

Esperado:
  ❌ ATUAL OUTs: +€0 (ainda não pago ao sócio)
  ✅ PROJETADO OUTs: +€1200 (declarado às finanças, vai ser pago)
```

---

## 🔍 Questões em Aberto

### 1. Despesas Futuras no PROJETADO
**Pergunta:** Como saber quais despesas fixas vão acontecer até fim do ano?
- Opção A: Todas as despesas fixas com `data <= 31/12/2026`
- Opção B: Projetar baseado em média mensal × meses restantes
- **Decisão:** ⏳ PENDENTE

### 2. Prémios de Projetos FINALIZADOS sem Faturação
**Pergunta:** Prémio de projeto `FINALIZADO` mas sem `data_faturacao` conta no ATUAL ou só PROJETADO?
- Opção A: Conta no ATUAL (trabalho feito = prémio devido)
- Opção B: Só conta no PROJETADO (precisa faturar primeiro)
- **Decisão:** ✅ **Opção A** (especificado: trabalho feito = `data_fim < hoje`)

### 3. Investimento Inicial
**Pergunta:** Os €5.200 de cada sócio devem contar?
- **Decisão atual:** ❌ NÃO (é histórico, não operacional)
- **Manter?** ⏳ PENDENTE

---

## 📝 Notas de Implementação

### Performance
- Queries atuais: ~8-10 por sócio
- Com novos filtros: ~10-12 por sócio
- **Estimativa:** +20-50ms no carregamento do dashboard
- **Otimização futura:** Cache Redis (5min TTL)

### Backward Compatibility
- ⚠️ **Breaking change:** Saldos vão mudar!
- **Antes de deploy:** Documentar valores atuais para comparação
- **Comunicar:** Avisar que valores podem mudar ligeiramente

### Database Indexes
Garantir indexes em:
- `projetos.estado`
- `projetos.data_recibo`
- `projetos.data_fim`
- `despesas.data`
- `boletins.estado`

---

**Documentado por:** Claude Sonnet 4.5
**Aprovado por:** Bruno (14 Jan 2026)
**Status:** 📝 Especificação completa, aguarda implementação
**Estimativa:** 3-4h de trabalho (código + testes + docs)
