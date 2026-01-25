# Motor de Despesas - Automação e Gestão Inteligente

**Versão:** 0.3.6 (2026-01-25)
**Autor:** Claude Code (com Zumine)
**Contexto:** Refatoração completa do sistema de Templates de Despesas para suportar frequências múltiplas e blueprints manuais.

---

## 📋 Índice

1. [Conceitos Fundamentais](#conceitos-fundamentais)
2. [Frequências Suportadas](#frequências-suportadas)
3. [Blueprints Manuais](#blueprints-manuais)
4. [Cálculo de Vencimentos](#cálculo-de-vencimentos)
5. [Lógica de Agendamento](#lógica-de-agendamento)
6. [Arquitetura Técnica](#arquitetura-técnica)
7. [Casos de Uso](#casos-de-uso)
8. [Troubleshooting](#troubleshooting)

---

## Conceitos Fundamentais

### Templates vs. Despesas

**Template (`DespesaTemplate`):**
- Modelo/Blueprint para gerar despesas automaticamente
- **NÃO** representa uma despesa real
- **NÃO** entra em cálculos financeiros (saldos, relatórios fiscais)
- Contém configuração de **quando** e **como** gerar despesas

**Despesa (`Despesa`):**
- Registo real de uma despesa da empresa
- **Entra** em cálculos financeiros
- Pode ser criada:
  - Automaticamente (via comando `criar_despesas_fixas`)
  - Manualmente (via admin action ou form)

### Tipos de Templates

#### 1. Templates Automáticos (Agendados)
- **Frequência:** MENSAL, TRIMESTRAL, SEMESTRAL, ANUAL
- **Comportamento:** Sistema gera despesas automaticamente no dia configurado
- **Exemplos:**
  - Ordenados (MENSAL, dia 27)
  - Seguro profissional (TRIMESTRAL, dia 15)
  - Renda de escritório (MENSAL, dia 1)
  - Taxa de certificação (ANUAL, dia 10)

#### 2. Blueprints Manuais
- **Frequência:** MANUAL
- **Comportamento:** Nunca gera automaticamente, só via action do admin
- **Exemplos:**
  - Software pontual (vMix, Adobe, etc.)
  - Consultorias esporádicas
  - Despesas não-recorrentes com configuração padrão

---

## Frequências Suportadas

### MENSAL
**Descrição:** Gera despesa todo mês no `dia_mes` configurado.

**Exemplo:**
```python
DespesaTemplate(
    numero='#TD000001',
    descricao='Ordenado Rafael',
    frequencia='MENSAL',
    dia_mes=27,  # Dia 27 de cada mês
    valor_sem_iva=1500.00,
    ativa=True
)
```

**Geração:**
- 27/01/2026 → Cria despesa #D000001
- 27/02/2026 → Cria despesa #D000002
- 27/03/2026 → Cria despesa #D000003
- ...

---

### TRIMESTRAL
**Descrição:** Gera despesa a cada 3 meses.

**Exemplo:**
```python
DespesaTemplate(
    numero='#TD000002',
    descricao='Seguro Profissional',
    frequencia='TRIMESTRAL',
    dia_mes=15,
    valor_sem_iva=350.00,
    ativa=True
)
```

**Geração:**
- 15/01/2026 → Cria despesa #D000010
- 15/04/2026 → Cria despesa #D000045 (3 meses depois)
- 15/07/2026 → Cria despesa #D000078
- 15/10/2026 → Cria despesa #D000112
- ...

---

### SEMESTRAL
**Descrição:** Gera despesa a cada 6 meses.

**Exemplo:**
```python
DespesaTemplate(
    numero='#TD000003',
    descricao='Revisão Fiscal Semestral',
    frequencia='SEMESTRAL',
    dia_mes=1,
    valor_sem_iva=500.00,
    ativa=True
)
```

**Geração:**
- 01/01/2026 → Cria despesa
- 01/07/2026 → Cria despesa (6 meses depois)
- 01/01/2027 → Cria despesa
- ...

---

### ANUAL
**Descrição:** Gera despesa a cada 12 meses.

**Exemplo:**
```python
DespesaTemplate(
    numero='#TD000004',
    descricao='Taxa Certificação APOTEC',
    frequencia='ANUAL',
    dia_mes=10,
    valor_sem_iva=150.00,
    ativa=True
)
```

**Geração:**
- 10/01/2026 → Cria despesa
- 10/01/2027 → Cria despesa (12 meses depois)
- 10/01/2028 → Cria despesa
- ...

---

### MANUAL (Blueprint)
**Descrição:** Nunca gera automaticamente. Usa-se via action do admin quando necessário.

**Exemplo:**
```python
DespesaTemplate(
    numero='#TD000005',
    descricao='vMix Streaming (Pontual)',
    frequencia='MANUAL',
    dia_mes=1,  # Ignorado (não é usado)
    prazo_pagamento_dias=30,
    valor_sem_iva=150.00,
    ativa=True
)
```

**Como Usar:**
1. Aceder `/admin/core/despesatemplate/`
2. Selecionar template(s) manual(is)
3. Action: "🔨 Gerar Despesa Agora (Manual)"
4. Sistema cria despesa com:
   - `data` = HOJE
   - `data_vencimento` = HOJE + 30 dias
   - Todos os campos copiados do template

---

## Cálculo de Vencimentos

### Campo `prazo_pagamento_dias`

Cada template define um prazo padrão de pagamento em dias.

**Comportamento:**
```python
data_vencimento = data_emissão + prazo_pagamento_dias
```

**Exemplos:**

| `prazo_pagamento_dias` | `data_emissão` | `data_vencimento` | Descrição |
|------------------------|----------------|-------------------|-----------|
| `0` | 25/01/2026 | 25/01/2026 | Pronto pagamento |
| `30` | 25/01/2026 | 24/02/2026 | 30 dias |
| `60` | 25/01/2026 | 26/03/2026 | 60 dias |
| `90` | 25/01/2026 | 25/04/2026 | 90 dias |

### Estados Calculados da Despesa

A propriedade `Despesa.get_estado_despesa` calcula automaticamente o estado baseado nas datas:

```python
if data_pagamento:
    return ('PAGO', 'Pago', 'success')  # Verde
elif data_vencimento < hoje:
    return ('VENCIDO', 'Vencido', 'danger')  # Vermelho
elif (data_vencimento - hoje).days <= 3:
    return ('A_VENCER', 'A Vencer (2d)', 'warning')  # Laranja
else:
    return ('EM_ABERTO', 'Em Aberto', 'info')  # Azul
```

**Uso futuro:**
- Dashboard de tesouraria (Aging)
- Alertas de despesas vencidas
- Filtros inteligentes no admin

---

## Lógica de Agendamento

### Método `deve_gerar_hoje()`

Determina se um template deve gerar uma despesa hoje.

#### Regra 1: Templates Inativos/Manuais
```python
if not self.ativa or self.frequencia == 'MANUAL':
    return False  # Nunca gera automaticamente
```

#### Regra 2: Primeira Geração
```python
if not ultima_despesa:
    # Tolerância: Gera mesmo se passou o dia
    return hoje.day >= self.dia_mes
```

**Exemplo:**
- Template: `dia_mes=27`
- Hoje: 28/01/2026 (script atrasou 1 dia)
- Resultado: `True` (gera na mesma)

#### Regra 3: Cálculo de Próxima Data

```python
# Mapa de frequências
frequencia_meses = {
    'MENSAL': 1,
    'TRIMESTRAL': 3,
    'SEMESTRAL': 6,
    'ANUAL': 12,
}

# Calcula próxima data
proxima_data_alvo = data_ultima_geracao + relativedelta(months=meses_intervalo)
proxima_data_alvo = proxima_data_alvo.replace(day=self.dia_mes)

# Retorna True se chegou a hora
return hoje >= proxima_data_alvo
```

**Exemplo (TRIMESTRAL):**
- Última despesa: 15/01/2026
- Próxima data: 15/04/2026 (15/01 + 3 meses)
- Hoje: 16/04/2026 (atrasou 1 dia)
- Resultado: `True` (tolerância a falhas)

#### Regra 4: Dias Inválidos

```python
try:
    proxima_data_alvo = proxima_data_alvo.replace(day=31)
except ValueError:
    # Fevereiro só tem 28/29 dias
    proxima_data_alvo = proxima_data_alvo + relativedelta(day=31)  # Último dia do mês
```

**Exemplo:**
- Template: `dia_mes=31`
- Última despesa: 31/01/2026
- Próxima data tentativa: 31/02/2026 (não existe!)
- Próxima data real: 28/02/2026 (último dia do mês)

---

## Arquitetura Técnica

### Separação de Responsabilidades (DRY)

#### Modelo: `DespesaTemplate` ([models.py:631-897](agora_web/core/models.py#L631-L897))

**Métodos públicos:**

1. **`gerar_despesa(user=None)`** - Cria nova despesa
   - Gera número sequencial
   - Calcula datas (emissão, vencimento)
   - Copia todos os campos e tags
   - Transaction atómica
   - Retorna objeto `Despesa`

2. **`deve_gerar_hoje()`** - Verifica se deve gerar hoje
   - Valida estado (ativa, frequência)
   - Busca última despesa gerada
   - Calcula próxima data baseado em frequência
   - Retorna `bool`

#### Admin Action ([admin.py:914-955](agora_web/core/admin.py#L914-L955))

```python
def gerar_despesa_agora(self, request, queryset):
    for template in queryset:
        try:
            nova_despesa = template.gerar_despesa(user=request.user)
            despesas_criadas.append(nova_despesa)
        except Exception as e:
            erros.append((template.numero, str(e)))
```

**Responsabilidade:** Apenas UI/UX (mensagens, tratamento de erros)

#### Comando de Gestão ([criar_despesas_fixas.py](agora_web/core/management/commands/criar_despesas_fixas.py))

```python
templates = DespesaTemplate.objects.filter(ativa=True).exclude(frequencia='MANUAL')

for template in templates:
    if template.deve_gerar_hoje():
        if not dry_run:
            template.gerar_despesa(user=None)
```

**Responsabilidade:** Apenas orchestration (iterar, logar, dry-run)

### Benefícios da Arquitetura

✅ **DRY:** Lógica centralizada no modelo
✅ **Testável:** Métodos podem ser testados unitariamente
✅ **Manutenível:** Mudança na lógica afeta apenas `models.py`
✅ **Reutilizável:** Admin e comando usam mesmos métodos

---

## Casos de Uso

### Caso 1: Ordenado Mensal com Pronto Pagamento

**Requisito:**
Pagar ordenado de Rafael dia 27 de cada mês, vencimento imediato.

**Solução:**
```python
DespesaTemplate.objects.create(
    numero='#TD000010',
    descricao='Ordenado Rafael - Mensal',
    frequencia='MENSAL',
    dia_mes=27,
    prazo_pagamento_dias=0,  # Pronto pagamento
    valor_sem_iva=1500.00,
    estado_default='PAGO',  # Já pago no momento da criação
    ativa=True,
    tags=[tag_ordenado, tag_pessoal],
    tag_irs=tag_irs_trabalho_dependente
)
```

**Resultado:**
- Comando cria despesa dia 27 de cada mês
- `data_vencimento = data_emissão` (vence no dia)
- Estado: PAGO (porque `estado_default='PAGO'`)

---

### Caso 2: Seguro Trimestral com 30 Dias de Prazo

**Requisito:**
Seguro profissional pago a cada 3 meses, dia 15, com 30 dias para pagar.

**Solução:**
```python
DespesaTemplate.objects.create(
    numero='#TD000011',
    descricao='Seguro Profissional - Trimestral',
    frequencia='TRIMESTRAL',
    dia_mes=15,
    prazo_pagamento_dias=30,
    valor_sem_iva=350.00,
    estado_default='PENDENTE',
    ativa=True,
    tags=[tag_seguro, tag_fixo],
    tag_irc=tag_irc_dedutivel_100
)
```

**Resultado:**
- 15/01/2026 → Despesa criada, vencimento 14/02/2026
- 15/04/2026 → Despesa criada, vencimento 14/05/2026
- 15/07/2026 → Despesa criada, vencimento 14/08/2026
- ...

---

### Caso 3: Software Pontual (Blueprint Manual)

**Requisito:**
vMix usado esporadicamente, sempre com 30 dias de prazo. Criar despesa quando necessário.

**Solução:**
```python
DespesaTemplate.objects.create(
    numero='#TD000012',
    descricao='vMix Streaming - Pontual',
    frequencia='MANUAL',  # Blueprint
    dia_mes=1,  # Ignorado
    prazo_pagamento_dias=30,
    valor_sem_iva=150.00,
    estado_default='PENDENTE',
    ativa=True,  # Ativa para aparecer no admin, mas não gera automaticamente
    tags=[tag_software, tag_projeto],
    credor=fornecedor_vmix
)
```

**Uso:**
1. Projeto precisa de vMix
2. Admin: Selecionar template #TD000012
3. Action: "🔨 Gerar Despesa Agora"
4. Despesa criada:
   - `data = HOJE`
   - `data_vencimento = HOJE + 30 dias`
   - Todos os campos copiados (credor, tags, etc.)

---

### Caso 4: Taxa Anual no Início do Ano

**Requisito:**
Taxa de certificação APOTEC, paga todo ano dia 10 de janeiro.

**Solução:**
```python
DespesaTemplate.objects.create(
    numero='#TD000013',
    descricao='Taxa Certificação APOTEC',
    frequencia='ANUAL',
    dia_mes=10,
    prazo_pagamento_dias=0,
    valor_sem_iva=150.00,
    estado_default='PENDENTE',
    ativa=True,
    tags=[tag_certificacao, tag_fixo],
    tag_irc=tag_irc_dedutivel_100
)
```

**Resultado:**
- 10/01/2026 → Despesa criada
- 10/01/2027 → Despesa criada (12 meses depois)
- 10/01/2028 → Despesa criada
- ...

---

## Troubleshooting

### Problema: Template não está a gerar despesas

**Checklist:**
1. ✅ Template está `ativa=True`?
2. ✅ Frequência não é `MANUAL`?
3. ✅ Comando `criar_despesas_fixas` está a correr diariamente?
4. ✅ Já passou o `dia_mes` este mês?
5. ✅ Já gerou despesa este mês? (proteção dupla geração)

**Debug:**
```bash
# Dry-run manual
docker compose exec web python manage.py criar_despesas_fixas --dry-run

# Ver última despesa gerada deste template
docker compose exec web python manage.py shell
>>> from core.models import DespesaTemplate
>>> t = DespesaTemplate.objects.get(numero='#TD000001')
>>> t.despesas_geradas.order_by('-data').first()
```

---

### Problema: Despesa duplicada no mesmo dia

**Causa:** Comando executado múltiplas vezes no mesmo dia.

**Proteção automática:**
```python
# Comando verifica se já gerou hoje
ultima_despesa = template.despesas_geradas.order_by('-data').first()
if ultima_despesa and ultima_despesa.data == hoje:
    continue  # Pula
```

**Solução:**
Sistema já tem proteção. Se ocorrer, é bug - reportar.

---

### Problema: Dia 31 não gera em fevereiro

**Comportamento esperado:**
Template com `dia_mes=31` gera no último dia do mês (28 ou 29 fev).

**Lógica:**
```python
try:
    proxima_data = proxima_data.replace(day=31)
except ValueError:
    proxima_data = proxima_data + relativedelta(day=31)  # Último dia
```

**Exemplo:**
- Template: `dia_mes=31`
- Janeiro: 31/01/2026 → OK
- Fevereiro: 28/02/2026 → Ajustado para último dia
- Março: 31/03/2026 → OK

---

### Problema: Como testar sem afetar produção?

**Solução 1: Dry-run**
```bash
docker compose exec web python manage.py criar_despesas_fixas --dry-run
```

**Solução 2: Template de teste**
```python
# Criar template MANUAL
template_teste = DespesaTemplate.objects.create(
    numero='#TD999999',
    descricao='TESTE - Não Usar',
    frequencia='MANUAL',
    ...
)

# Gerar despesa manualmente
despesa = template_teste.gerar_despesa(user=request.user)

# Validar resultado
assert despesa.data_vencimento == date.today() + timedelta(days=30)

# Apagar se ok
despesa.delete()
```

---

## Manutenção Futura

### TODO: Refatorar `estado_default`

**Localização:** [models.py:756](agora_web/core/models.py#L756)

```python
# TODO: Refatorar futuramente para boolean 'pago_automatico'
estado_default = models.CharField(...)
```

**Proposta:**
Substituir por campo boolean `pago_automatico`:
- `True` → Despesas criadas com `data_pagamento=data_emissão`
- `False` → Despesas criadas com `data_pagamento=None`

**Benefício:**
Mais simples e semântico que `estado_default='PAGO'`.

---

## Conclusão

O Motor de Despesas foi completamente refatorado para:

✅ **Suportar múltiplas frequências** (MENSAL, TRIMESTRAL, SEMESTRAL, ANUAL)
✅ **Blueprints manuais** para despesas esporádicas
✅ **Gestão de vencimentos** automática via `prazo_pagamento_dias`
✅ **DRY (Don't Repeat Yourself)** - lógica centralizada no modelo
✅ **Tolerância a falhas** - gera mesmo se script atrasar
✅ **Proteção contra duplicados** - não gera 2x no mesmo dia

**Próximos passos:**
1. Criar dashboard de tesouraria (Aging de despesas)
2. Alertas automáticos de despesas vencidas
3. Integração com Email (lembrete 3 dias antes do vencimento)
4. Refatorar `estado_default` → `pago_automatico` (ver TODO)

---

**Documentação mantida em:** [DESPESAS_AUTOMATION.md](docs/DESPESAS_AUTOMATION.md)
**Última atualização:** 2026-01-25 (v0.3.6)
