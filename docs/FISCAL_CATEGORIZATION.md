# Sistema de Categorização Fiscal - Agora Contabilidade

**Data:** 17 Janeiro 2026
**Versão:** v0.3.0 (Draft)
**Status:** 📝 ESPECIFICAÇÃO - Aguarda validação do contabilista

---

## 📋 Índice

1. [Visão Geral](#-visão-geral)
2. [Conceitos Fundamentais](#-conceitos-fundamentais)
3. [Tags Operacionais vs Tags Fiscais](#-tags-operacionais-vs-tags-fiscais)
4. [Categorias Fiscais](#-categorias-fiscais)
5. [Mapeamento Automático](#-mapeamento-automático)
6. [Questões para o Contabilista](#-questões-para-o-contabilista)
7. [Implementação Técnica](#-implementação-técnica)
8. [Casos de Uso](#-casos-de-uso)

---

## 🎯 Visão Geral

Este documento estrutura o sistema de **categorização fiscal** para a Agora Media Production, separando:

- **Tags Operacionais**: Como categorizamos despesas internamente (ex: "Ordenado", "Equipamento", "Produção")
- **Tags Fiscais**: Como essas despesas são tratadas para efeitos fiscais (IRC, IVA, IRS, TSU)

**Objetivo:** Permitir relatórios fiscais precisos e facilitar o trabalho do contabilista, mantendo a flexibilidade operacional.

---

## 🧠 Conceitos Fundamentais

### Empresa = Intermediário Financeiro

```
Cliente → paga → Empresa → deve → Sócio
                    ↓
                  (Custos)
                    ↓
Empresa → paga → Sócio (via boletins/despesas)
```

### Obrigações Fiscais da Agora Media

A empresa tem obrigações fiscais periódicas:

| Imposto | Periodicidade | Prazo Declaração | Prazo Pagamento | Calculado em |
|---------|---------------|------------------|-----------------|--------------|
| **IVA** | Trimestral | Dia 20 do 2º mês seguinte | Dia 25 do 2º mês seguinte | [fiscal.py:51](../agora_web/core/utils/fiscal.py#L51) |
| **IRS Retido** | Mensal | Dia 20 do mês seguinte | Dia 25 do mês seguinte | [fiscal.py:184](../agora_web/core/utils/fiscal.py#L184) |
| **IRC** | Anual | 31 Maio (ano seguinte) | 31 Agosto (ano seguinte) | [fiscal.py:278](../agora_web/core/utils/fiscal.py#L278) |
| **TSU** | Mensal | Dia 10 do mês seguinte | Dia 15-20 do mês seguinte | ⚠️ NÃO IMPLEMENTADO |

---

## 🏷️ Tags Operacionais vs Tags Fiscais

### Tags Operacionais (Atuais)

Sistema existente em [tags_despesa.json](../agora_web/core/fixtures/tags_despesa.json):

| Código | Nome | Uso |
|--------|------|-----|
| `EQUIPAMENTO` | Equipamento | Compras de material |
| `PESSOAL` | Pessoal | Despesas pessoais dos sócios |
| `SERVICO` | Serviço | Serviços externos |
| `PREMIO` | Prémio | Prémios de projetos |
| `ORDENADO` | Ordenado | Salários fixos |
| `SUB_ALIMENTACAO` | Sub. Alimentação | Subsídio alimentação |
| `ADMINISTRATIVO` | Administrativo | Custos administrativos |
| `PRODUCAO` | Produção | Custos de produção |
| `DESLOCACAO` | Deslocação | Viagens e deslocações |
| `ALIMENTACAO` | Alimentação | Refeições |
| `PER_DIEM_PT` | Per Diem Portugal | Ajudas de custo PT |
| `PER_DIEM_FORA` | Per Diem Estrangeiro | Ajudas de custo fora de PT |

### Tags Fiscais (NOVO)

**Sistema dual:** Tags operacionais + Tags fiscais automáticas (editáveis)

#### 1. IRC - Dedutibilidade

| Tag Fiscal | Descrição | Taxa Dedução | Aplicável a |
|------------|-----------|--------------|-------------|
| `IRC_DEDUTIVEL_100` | Totalmente dedutível em IRC | 100% | Despesas operacionais normais |
| `IRC_DEDUTIVEL_PARCIAL` | Dedutível parcialmente | Variável | Viaturas, representação, bónus |
| `IRC_NAO_DEDUTIVEL` | Não dedutível | 0% | Multas, bónus acima de limites |
| `IRC_INVESTIMENTO` | Investimento (amortizável) | Depreciação | Equipamento >€1.000 |

**Regras IRC (Portugal - CIRC):**
- Despesas operacionais gerais: 100% dedutível
- Viaturas ligeiras: Limite de €25.000 por viatura (depreciação)
- Combustíveis: 100% se viatura <€25k, 50% se >€25k
- Bónus e prémios: Limite legal por trabalhador
- Representação/Entretenimento: Limitações (% volume negócios)

#### 2. IVA - Dedutibilidade

| Tag Fiscal | Descrição | Taxa Dedução | Aplicável a |
|------------|-----------|--------------|-------------|
| `IVA_DEDUTIVEL_100` | IVA totalmente dedutível | 100% | Despesas com fatura com IVA |
| `IVA_NAO_DEDUTIVEL` | IVA não dedutível | 0% | Despesas isentas, sem fatura |
| `IVA_MISTO` | Uso misto (pro-rata) | % variável | Viaturas uso misto |

**Regras IVA (Portugal - CIVA):**
- Só é dedutível IVA de despesas com **fatura válida** e relacionadas com atividade
- Viaturas de turismo: IVA NÃO dedutível (exceto táxis, rent-a-car, autoescolas)
- Combustíveis: IVA dedutível se viatura for comercial/mercadorias
- Alojamento/Alimentação: IVA dedutível se relacionado com atividade

#### 3. IRS - Retenção na Fonte

| Tag Fiscal | Descrição | Taxa Retenção | Aplicável a |
|------------|-----------|---------------|-------------|
| `IRS_ISENTO` | Isento de retenção | 0% | Ordenados baixos, subsidios isentos |
| `IRS_RETENCAO_TRABALHO` | Trabalho dependente | Tabela AT | Ordenados (varia conforme escalão) |
| `IRS_RETENCAO_25` | Trabalho independente | 25% | Freelancers (recibos verdes) |
| `IRS_RETENCAO_20` | Rendimentos prediais | 28% | Rendas (se aplicável) |
| `IRS_RETENCAO_11_5` | Prestação de serviços | 11,5% | Certos serviços profissionais |

**Regras IRS (Portugal - CIRS):**
- **Trabalho dependente** (Categoria A): Tabelas de retenção mensais (0-48%)
- **Trabalho independente** (Categoria B): 25% sobre 70% do valor (= 17,5% efetivo) para recibos verdes
- **Subsídio alimentação**: Isento até €10,20/dia (2026) se pago em vales
- **Ajudas de custo**: Isentas até limites legais (€62,75/dia PT, varies exterior)

#### 4. TSU - Segurança Social

| Tag Fiscal | Descrição | Taxa | Aplicável a |
|------------|-----------|------|-------------|
| `TSU_GERENTE` | Gerentes/Administradores | 21,4% empresa + 9,3% trabalhador | Sócios-gerentes |
| `TSU_TRABALHADOR` | Trabalhadores conta outrem | 23,75% empresa + 11% trabalhador | Empregados |
| `TSU_ISENTO` | Isento TSU | 0% | Freelancers (pagam regime próprio) |

**Regras TSU (Portugal - Seg. Social):**
- **Gerentes**: Base de incidência = Remuneração declarada (mínimo 1x IAS = €522,50/mês em 2026)
- **Trabalhadores**: Base = Remuneração total (ordenado + subsídios)
- **Subsídio alimentação**: Isento TSU se ≤€10,20/dia (2026) em vales
- **Freelancers**: Não há TSU da empresa, eles pagam regime próprio trabalhadores independentes

---

## 🔄 Mapeamento Automático

### Regras de Auto-Atribuição

Quando o utilizador seleciona uma **tag operacional**, o sistema sugere automaticamente as **tags fiscais** correspondentes (editáveis).

| Tag Operacional | → | Tags Fiscais Auto-Sugeridas | Observações |
|-----------------|---|----------------------------|-------------|
| `ORDENADO` | → | `IRC_DEDUTIVEL_100`, `IVA_NAO_DEDUTIVEL`, `IRS_RETENCAO_TRABALHO`, `TSU_GERENTE` | Assumindo gerentes. Se empregados: `TSU_TRABALHADOR` |
| `SUB_ALIMENTACAO` | → | `IRC_DEDUTIVEL_100`, `IVA_NAO_DEDUTIVEL`, `IRS_ISENTO`, `TSU_ISENTO` | Se ≤€10,20/dia em vales |
| `EQUIPAMENTO` | → | `IRC_INVESTIMENTO` (se >€1k) OU `IRC_DEDUTIVEL_100` (se <€1k), `IVA_DEDUTIVEL_100` | Depende do valor |
| `DESLOCACAO` | → | `IRC_DEDUTIVEL_100`, `IVA_MISTO` (se viatura) OU `IVA_DEDUTIVEL_100` (se transportes públicos) | Depende do tipo |
| `ALIMENTACAO` | → | `IRC_DEDUTIVEL_PARCIAL`, `IVA_DEDUTIVEL_100` | Pode ter limites |
| `PER_DIEM_PT` | → | `IRC_DEDUTIVEL_100`, `IVA_NAO_DEDUTIVEL`, `IRS_ISENTO`, `TSU_ISENTO` | Se dentro dos limites (€62,75/dia) |
| `PER_DIEM_FORA` | → | `IRC_DEDUTIVEL_100`, `IVA_NAO_DEDUTIVEL`, `IRS_ISENTO`, `TSU_ISENTO` | Se dentro dos limites (varia por país) |
| `PREMIO` | → | `IRC_DEDUTIVEL_PARCIAL`, `IVA_NAO_DEDUTIVEL`, `IRS_RETENCAO_TRABALHO`, `TSU_GERENTE` | Pode ter limites IRC |
| `SERVICO` | → | `IRC_DEDUTIVEL_100`, `IVA_DEDUTIVEL_100`, `IRS_RETENCAO_25` (se freelancer PT) | Depende do fornecedor |
| `PRODUCAO` | → | `IRC_DEDUTIVEL_100`, `IVA_DEDUTIVEL_100` | Custos diretos de produção |
| `ADMINISTRATIVO` | → | `IRC_DEDUTIVEL_100`, `IVA_DEDUTIVEL_100` | Despesas gerais |

### Lógica de Sugestão (Pseudo-código)

```python
def sugerir_tags_fiscais(tag_operacional, despesa):
    """
    Baseado na tag operacional e características da despesa,
    sugere tags fiscais (editáveis pelo utilizador)
    """
    sugestoes = {
        'irc': None,
        'iva': None,
        'irs': None,
        'tsu': None
    }

    if tag_operacional == 'ORDENADO':
        sugestoes['irc'] = 'IRC_DEDUTIVEL_100'
        sugestoes['iva'] = 'IVA_NAO_DEDUTIVEL'
        sugestoes['irs'] = 'IRS_RETENCAO_TRABALHO'
        sugestoes['tsu'] = 'TSU_GERENTE'  # ou TSU_TRABALHADOR se empregado

    elif tag_operacional == 'SUB_ALIMENTACAO':
        # Verificar valor diário
        if despesa.valor_sem_iva / 30 <= 10.20:  # Aproximação mensal
            sugestoes['irc'] = 'IRC_DEDUTIVEL_100'
            sugestoes['iva'] = 'IVA_NAO_DEDUTIVEL'
            sugestoes['irs'] = 'IRS_ISENTO'
            sugestoes['tsu'] = 'TSU_ISENTO'
        else:
            # Acima do limite, pode tributar
            sugestoes['irs'] = 'IRS_RETENCAO_TRABALHO'

    elif tag_operacional == 'EQUIPAMENTO':
        if despesa.valor_sem_iva > 1000:
            sugestoes['irc'] = 'IRC_INVESTIMENTO'
        else:
            sugestoes['irc'] = 'IRC_DEDUTIVEL_100'
        sugestoes['iva'] = 'IVA_DEDUTIVEL_100'

    # ... (continuar para outras tags)

    return sugestoes
```

---

## ❓ Questões para o Contabilista

### Seção 1: IRC - Dedutibilidade

**Q1.1:** As despesas de "Ordenado" e "Sub. Alimentação" dos sócios-gerentes são 100% dedutíveis em IRC?
- **Contexto:** Atualmente estamos a separar ordenado de subsídio alimentação. Está correto? Há limites?
- **Valor típico:** Ordenado BA: €X/mês, Sub. Alimentação: €Y/mês

**Q1.2:** Prémios pagos aos gerentes têm algum limite de dedutibilidade em IRC?
- **Contexto:** Pagamos prémios variáveis baseados em projetos. Há % máximo de remuneração variável?

**Q1.3:** Equipamentos acima de que valor devem ser considerados investimento (amortizável) vs despesa corrente?
- **Valor de corte:** €1.000? €500? Outro?
- **Taxa de depreciação:** Equipamento informático/audiovisual - quantos anos?

**Q1.4:** Despesas de representação e entretenimento têm limites?
- **Contexto:** Almoços com clientes, brindes, eventos.
- **Há % máximo sobre volume de negócios?**

**Q1.5:** Viaturas - Confirmação de regras:
- Limite €25.000 para depreciação?
- Combustíveis: 100% dedutível se viatura <€25k, 50% se >€25k?
- Como classificar uso misto (empresa/pessoal)?

### Seção 2: IVA - Dedutibilidade

**Q2.1:** Viaturas - Confirmação:
- IVA **não dedutível** em viaturas ligeiras de passageiros?
- Combustíveis: IVA dedutível apenas se viatura comercial?

**Q2.2:** Alimentação e alojamento em trabalho:
- IVA dedutível se relacionado com projetos?
- Precisa de justificação específica (projeto, cliente)?

**Q2.3:** Equipamento:
- IVA sempre dedutível se usado para atividade?
- Há restrições?

### Seção 3: IRS - Retenção na Fonte

**Q3.1:** Sócios-gerentes - Retenção:
- Aplicamos tabela de trabalho dependente (Categoria A)?
- Base de incidência = Ordenado + Sub. Alimentação + Prémios?
- Ou Sub. Alimentação isento se ≤€10,20/dia?

**Q3.2:** Subsídio de Alimentação - Limites isenção:
- Valor atual (2026): €10,20/dia?
- Tem de ser pago em vales ou pode ser dinheiro?
- Se ultrapassar, tributa só o excesso ou tudo?

**Q3.3:** Ajudas de Custo (Per Diems):
- Limites isenção Portugal: €62,75/dia (2026)?
- Estrangeiro: Varia por país? Onde consultar tabela?
- Precisa de mapa de deslocações justificativo?

**Q3.4:** Prémios:
- Entram na base de retenção mensal?
- Ou há regime especial (duodécimos, etc.)?

**Q3.5:** Freelancers (Prestadores de Serviços):
- Retemos 25% sobre valor total?
- Ou 11,5% (certos serviços)?
- Como distinguir? Depende do CAE do prestador?

### Seção 4: TSU - Segurança Social

**Q4.1:** Sócios-gerentes:
- Taxa: 21,4% empresa + 9,3% gerente?
- Base de incidência mínima: 1x IAS (€522,50/mês em 2026)?
- Máxima: 12x IAS?

**Q4.2:** Base de incidência:
- Ordenado + Prémios?
- Ou só ordenado fixo?
- Sub. Alimentação: Isento se ≤€10,20/dia em vales?

**Q4.3:** Se contratarmos trabalhadores (não gerentes):
- Taxa: 23,75% empresa + 11% trabalhador?
- Base: Remuneração total (incluindo subsídios)?

**Q4.4:** Freelancers:
- A empresa não paga TSU?
- Eles pagam regime próprio (trabalhadores independentes)?

### Seção 5: Estrutura de Tags

**Q5.1:** A estrutura de tags fiscais proposta faz sentido?
- IRC: `DEDUTIVEL_100`, `DEDUTIVEL_PARCIAL`, `NAO_DEDUTIVEL`, `INVESTIMENTO`
- IVA: `DEDUTIVEL_100`, `NAO_DEDUTIVEL`, `MISTO`
- IRS: `ISENTO`, `RETENCAO_TRABALHO`, `RETENCAO_25`, `RETENCAO_11_5`
- TSU: `GERENTE`, `TRABALHADOR`, `ISENTO`

**Q5.2:** Há outras categorias fiscais importantes que devemos rastrear?

**Q5.3:** Mapeamentos automáticos (tag operacional → tag fiscal) estão corretos?

### Seção 6: Relatórios

**Q6.1:** Que relatórios fiscais seriam úteis?
- Por categoria fiscal?
- Por período (mensal, trimestral, anual)?
- Breakdown por tipo de dedutibilidade?

**Q6.2:** Formato de exportação preferido?
- Excel?
- CSV?
- PDF?

---

## 🔧 Implementação Técnica

### Modelo de Dados (Proposta)

**Opção A: Campos Separados (mais explícito)**

```python
class Despesa(models.Model):
    # ... campos existentes ...

    # Tags operacionais (existente)
    tags = models.ManyToManyField('TagDespesa', related_name='despesas')

    # Tags fiscais (NOVO)
    tag_fiscal_irc = models.CharField(
        max_length=50,
        choices=TagFiscalIRC.choices,
        blank=True,
        null=True,
        verbose_name='Categoria IRC'
    )
    tag_fiscal_iva = models.CharField(
        max_length=50,
        choices=TagFiscalIVA.choices,
        blank=True,
        null=True,
        verbose_name='Categoria IVA'
    )
    tag_fiscal_irs = models.CharField(
        max_length=50,
        choices=TagFiscalIRS.choices,
        blank=True,
        null=True,
        verbose_name='Categoria IRS'
    )
    tag_fiscal_tsu = models.CharField(
        max_length=50,
        choices=TagFiscalTSU.choices,
        blank=True,
        null=True,
        verbose_name='Categoria TSU'
    )
```

**Opção B: Modelo Separado (mais flexível)**

```python
class TagFiscal(models.Model):
    """Tag fiscal para categorização de despesas"""
    codigo = models.CharField(max_length=50, primary_key=True)
    nome = models.CharField(max_length=100)
    tipo = models.CharField(
        max_length=10,
        choices=[('IRC', 'IRC'), ('IVA', 'IVA'), ('IRS', 'IRS'), ('TSU', 'TSU')]
    )
    descricao = models.TextField(blank=True)
    taxa_aplicavel = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        blank=True,
        null=True,
        help_text='Taxa de dedução/retenção (%)'
    )
    ordem = models.IntegerField(default=0)

class Despesa(models.Model):
    # ... campos existentes ...
    tags = models.ManyToManyField('TagDespesa', related_name='despesas')
    tags_fiscais = models.ManyToManyField('TagFiscal', related_name='despesas', blank=True)
```

### Signal para Auto-Atribuição

```python
from django.db.models.signals import m2m_changed
from django.dispatch import receiver

@receiver(m2m_changed, sender=Despesa.tags.through)
def auto_atribuir_tags_fiscais(sender, instance, action, **kwargs):
    """
    Quando tags operacionais mudam, sugere tags fiscais
    """
    if action == 'post_add':
        tags_operacionais = instance.tags.all()

        # Limpar tags fiscais existentes (opcional - pode manter)
        instance.tags_fiscais.clear()

        # Sugerir novas tags fiscais
        for tag_op in tags_operacionais:
            tags_fiscais_sugeridas = mapear_tags_fiscais(tag_op, instance)
            instance.tags_fiscais.add(*tags_fiscais_sugeridas)

def mapear_tags_fiscais(tag_operacional, despesa):
    """
    Retorna lista de TagFiscal baseado em tag operacional
    """
    mapeamento = {
        'ORDENADO': ['IRC_DEDUTIVEL_100', 'IVA_NAO_DEDUTIVEL', 'IRS_RETENCAO_TRABALHO', 'TSU_GERENTE'],
        'SUB_ALIMENTACAO': ['IRC_DEDUTIVEL_100', 'IVA_NAO_DEDUTIVEL', 'IRS_ISENTO', 'TSU_ISENTO'],
        'EQUIPAMENTO': ['IRC_DEDUTIVEL_100', 'IVA_DEDUTIVEL_100'],  # Simplificado
        # ... resto do mapeamento
    }

    codigos = mapeamento.get(tag_operacional.codigo, [])
    return TagFiscal.objects.filter(codigo__in=codigos)
```

### Admin Interface

```python
@admin.register(Despesa)
class DespesaAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Dados Básicos', {
            'fields': ['numero', 'descricao', 'credor', 'projeto']
        }),
        ('Valores', {
            'fields': ['valor_sem_iva', 'valor_com_iva', 'irs_retido', 'taxa_retencao_irs']
        }),
        ('Categorização', {
            'fields': ['tags', 'tags_fiscais'],
            'description': 'Tags fiscais são sugeridas automaticamente, mas podem ser editadas.'
        }),
        # ...
    ]
    filter_horizontal = ['tags', 'tags_fiscais']
```

---

## 📊 Casos de Uso

### Caso 1: Ordenado de Sócio-Gerente

**Input:**
- Despesa: "Ordenado Bruno - Janeiro 2026"
- Valor sem IVA: €1.500
- Tag operacional: `ORDENADO`

**Auto-sugestão de tags fiscais:**
- IRC: `IRC_DEDUTIVEL_100` (€1.500 dedutível)
- IVA: `IVA_NAO_DEDUTIVEL` (ordenado não tem IVA)
- IRS: `IRS_RETENCAO_TRABALHO` (aplicar tabela AT)
- TSU: `TSU_GERENTE` (21,4% empresa + 9,3% gerente)

**Cálculos:**
- IRS retido: ~€150 (depende da tabela, escalão)
- TSU empresa: €1.500 × 21,4% = €321
- TSU gerente: €1.500 × 9,3% = €139,50

### Caso 2: Subsídio de Alimentação

**Input:**
- Despesa: "Sub. Alimentação Bruno - Janeiro 2026"
- Valor sem IVA: €225 (22 dias × €10,20/dia - em vales)
- Tag operacional: `SUB_ALIMENTACAO`

**Auto-sugestão de tags fiscais:**
- IRC: `IRC_DEDUTIVEL_100` (€225 dedutível)
- IVA: `IVA_NAO_DEDUTIVEL`
- IRS: `IRS_ISENTO` (dentro do limite €10,20/dia em vales)
- TSU: `TSU_ISENTO` (isenção se ≤€10,20/dia em vales)

**Cálculos:**
- IRS retido: €0
- TSU: €0
- **Poupança fiscal vs ordenado:** ~€78 (IRS + TSU que não se paga)

### Caso 3: Equipamento (Câmara)

**Input:**
- Despesa: "Câmara Sony A7S III"
- Valor sem IVA: €3.500
- Valor com IVA: €4.305 (IVA 23% = €805)
- Tag operacional: `EQUIPAMENTO`

**Auto-sugestão de tags fiscais:**
- IRC: `IRC_INVESTIMENTO` (>€1.000, amortizar em X anos)
- IVA: `IVA_DEDUTIVEL_100` (€805 dedutível no trimestre)

**Cálculos:**
- IVA dedutível: €805
- IRC: €3.500 / X anos (ex: 5 anos = €700/ano)

### Caso 4: Freelancer (Serviço de Edição)

**Input:**
- Despesa: "Edição vídeo - João Silva (freelancer PT)"
- Valor sem IVA: €500
- Valor com IVA: €615 (IVA 23% = €115)
- Tag operacional: `SERVICO`

**Auto-sugestão de tags fiscais:**
- IRC: `IRC_DEDUTIVEL_100` (€500 dedutível)
- IVA: `IVA_DEDUTIVEL_100` (€115 dedutível)
- IRS: `IRS_RETENCAO_25` (reter 25%)
- TSU: `TSU_ISENTO` (freelancer paga regime próprio)

**Cálculos:**
- IRS a reter: €500 × 25% = €125
- Pagamento ao freelancer: €615 - €125 = €490
- IRS a entregar ao Estado: €125 (até dia 25 do mês seguinte)

### Caso 5: Ajuda de Custo (Deslocação a Madrid)

**Input:**
- Despesa: "Per Diem Madrid - Bruno (3 dias)"
- Valor sem IVA: €180 (3 dias × €60/dia)
- Tag operacional: `PER_DIEM_FORA`

**Auto-sugestão de tags fiscais:**
- IRC: `IRC_DEDUTIVEL_100` (se dentro do limite - verificar tabela Espanha)
- IVA: `IVA_NAO_DEDUTIVEL` (ajudas de custo não têm IVA)
- IRS: `IRS_ISENTO` (se dentro dos limites AT)
- TSU: `TSU_ISENTO`

**⚠️ QUESTÃO PARA CONTABILISTA:** Qual o limite diário para Espanha em 2026?

---

## 📈 Relatórios Fiscais

### Relatório 1: Breakdown por Categoria IRC

**Período:** Anual (2026)

| Categoria IRC | Valor Total | % do Total | Observações |
|---------------|-------------|------------|-------------|
| `IRC_DEDUTIVEL_100` | €50.000 | 80% | Dedutível totalmente |
| `IRC_DEDUTIVEL_PARCIAL` | €8.000 | 13% | Prémios, representação |
| `IRC_INVESTIMENTO` | €4.500 | 7% | Equipamento (amortizar) |
| `IRC_NAO_DEDUTIVEL` | €0 | 0% | - |
| **TOTAL** | **€62.500** | **100%** | - |

**Lucro Tributável Estimado:**
- Receitas: €100.000
- Despesas dedutíveis: €50.000 + €8.000 (parcial) + €900 (depreciação) = €58.900
- Lucro: €41.100
- IRC (16% sobre primeiros €50k): €6.576

### Relatório 2: IVA Trimestral (Q1 2026)

| Tipo | Descrição | Valor | IVA |
|------|-----------|-------|-----|
| **IVA Liquidado** | Projetos faturados PAGOS | €30.000 | €6.900 |
| **IVA Dedutível** | Despesas com IVA | €12.000 | €2.760 |
| **IVA a Pagar** | Diferença | - | **€4.140** |

**Prazo:** Declarar até 20 Maio 2026, Pagar até 25 Maio 2026

### Relatório 3: IRS Mensal (Janeiro 2026)

| Fornecedor | Descrição | Valor Base | Taxa | IRS Retido |
|------------|-----------|------------|------|------------|
| João Silva | Edição vídeo | €500 | 25% | €125 |
| Maria Costa | Design gráfico | €300 | 25% | €75 |
| Pedro Santos | Fotografia | €400 | 25% | €100 |
| **TOTAL** | - | **€1.200** | - | **€300** |

**Prazo:** Declarar até 20 Fevereiro 2026, Pagar até 25 Fevereiro 2026

---

## 🔗 Referências

### Documentação Interna
- [fiscal.py](../agora_web/core/utils/fiscal.py) - Calculadora fiscal existente (IVA, IRS, IRC)
- [tags_despesa.json](../agora_web/core/fixtures/tags_despesa.json) - Tags operacionais atuais
- [SALDOS_REVISION_SPEC.md](./SALDOS_REVISION_SPEC.md) - Lógica de saldos pessoais
- [CAIXA_ANALYSIS.md](./CAIXA_ANALYSIS.md) - Análise de cálculos de saldos

### Legislação Portuguesa
- **IRC:** Código do IRC (CIRC) - [Decreto-Lei n.º 442-B/88](https://info.portaldasfinancas.gov.pt/pt/informacao_fiscal/codigos_tributarios/circ/)
- **IVA:** Código do IVA (CIVA) - [Decreto-Lei n.º 394-B/84](https://info.portaldasfinancas.gov.pt/pt/informacao_fiscal/codigos_tributarios/civa/)
- **IRS:** Código do IRS (CIRS) - [Decreto-Lei n.º 442-A/88](https://info.portaldasfinancas.gov.pt/pt/informacao_fiscal/codigos_tributarios/cirs/)
- **TSU:** Segurança Social - [Código dos Regimes Contributivos](https://www.seg-social.pt/legislacao)
- **Tabelas IRS:** [Portal das Finanças - Tabelas de Retenção](https://www.portaldasfinancas.gov.pt/de/irs/tabelas_ret)
- **Ajudas de Custo:** [Portaria n.º 1553-D/2008](https://dre.pt/dre/detalhe/portaria/1553-d-2008-120897690) (limites per diems)

### Ferramentas
- **Calculadora IRS:** https://www.portaldasfinancas.gov.pt/simuladorIRS/
- **Simulador TSU:** https://www.seg-social.pt/simulador-contribuicoes

---

## 📝 Próximos Passos

1. **Validação:** Enviar secção "Questões para o Contabilista" para validação
2. **Decisão Técnica:** Opção A (campos separados) vs Opção B (modelo TagFiscal)
3. **Implementação:**
   - Criar modelo(s) de TagFiscal
   - Implementar lógica de auto-sugestão
   - Atualizar Admin interface
   - Criar relatórios fiscais
4. **Testes:** Validar com dados reais de 2025
5. **Documentação:** Atualizar `.claude/claude.md` com padrões fiscais

---

**Documentado por:** Claude Sonnet 4.5
**Data:** 2026-01-17
**Versão:** Draft v0.3.0
**Status:** 📝 Aguarda validação do contabilista
