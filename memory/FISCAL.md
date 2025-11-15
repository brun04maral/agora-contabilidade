# 💰 FISCAL.md - Obrigações Fiscais da Agora Media Production

## ⚠️ IMPORTANTE
Este documento descreve as obrigações fiscais e contabilísticas da Agora Media Production enquanto Sociedade por Quotas em regime de contabilidade organizada.

**Status:** Documentação base criada em 15/11/2025  
**Revisão:** Aguarda validação do TOC (Técnico Oficial de Contas)

---

## 📋 Índice

1. [Regime Fiscal da Agora](#1-regime-fiscal-da-agora)
2. [Receitas e Faturação](#2-receitas-e-faturação)
3. [Despesas e IVA Dedutível](#3-despesas-e-iva-dedutível)
4. [IVA Trimestral](#4-iva-trimestral)
5. [IRS Retido na Fonte (Fornecedores)](#5-irs-retido-na-fonte-fornecedores)
6. [IRC Anual](#6-irc-anual)
7. [Outras Obrigações](#7-outras-obrigações)
8. [Calendário Fiscal](#8-calendário-fiscal)
9. [Implementação Técnica](#9-implementação-técnica)

---

## 1. REGIME FISCAL DA AGORA

### 1.1 Identificação

**Entidade:** Agora Media Production, Lda.  
**Forma Jurídica:** Sociedade por Quotas  
**NIF:** [a preencher]  
**CAE Principal:** [a preencher]  

**Sócios-Gerentes:**
- Bruno Amaral (BA) - 50% - Ordenado
- Rafael Reigota (RR) - 50% - Ordenado

---

### 1.2 Regime de IRC

**Tipo:** Contabilidade Organizada (obrigatório para sociedades)  
**Fundamentação:** Todas as sociedades por quotas são obrigadas a contabilidade organizada (Código IRC)

**Taxa IRC (2025):**
- **16%** sobre os primeiros €50.000 de matéria coletável (PME)
- **20%** sobre o excedente (taxa geral)

**Derrama Municipal:** Variável por município (até 1,5% sobre lucro tributável)

**Período de tributação:** Ano civil (01/Jan a 31/Dez)

---

### 1.3 Regime de IVA

**Enquadramento:** Regime Normal - Periodicidade **Trimestral**

**Fundamentação:**
- Volume de negócios < €650.000 → periodicidade trimestral
- Opção por regime mensal é facultativa (requer 3 anos mínimo)

**Taxa aplicável:** **23%** (taxa normal)

**Taxas especiais:**
- 13% - bens/serviços com taxa intermédia (se aplicável)
- 6% - bens/serviços com taxa reduzida (se aplicável)
- 0% - exportações e operações intracomunitárias

---

### 1.4 Estrutura Operacional

**Cenário:** Empresa fatura todos os projetos

```
AGORA MEDIA PRODUCTION
├─ Emite faturas aos clientes (com IVA 23%)
├─ Paga fornecedores (retém IRS se recibos verdes)
├─ Paga despesas (deduz IVA quando aplicável)
├─ Paga IRC sobre lucros
└─ Paga ordenados aos sócios (BA + RR)
```

**Fluxo fiscal:**
1. Cliente paga à Agora → Receita com IVA (liquidado)
2. Agora paga fornecedor freelancer → Retém 23% de IRS
3. Agora paga despesas → Deduz IVA (se aplicável)
4. Trimestre fecha → Apura IVA a pagar/receber
5. Ano fecha → Apura IRC sobre lucros

---

## 2. RECEITAS E FATURAÇÃO

### 2.1 Conceito de Receita

**Receita = Valor total faturado ao cliente (incluindo IVA)**

**Tipos de receita:**
- **PROJETO:** Pagamento de projeto (valor total)
- **OUTRO:** Receitas avulsas (subsídios, vendas equipamento, etc)

**Pagamentos parciais:** Possível (a implementar)
- Exemplo: 50% início, 50% entrega final
- Cada pagamento = 1 receita separada
- Link comum ao mesmo projeto

---

### 2.2 Faturação

**Responsável:** Agora Media Production (empresa)

**Obrigações:**
- Emitir fatura através de programa certificado
- Comunicar faturas à AT até dia 5 do mês seguinte (SAF-T)
- Aplicar IVA 23% sobre valor total (salvo exceções)

**Estrutura de fatura:**
```
Fatura #2025/0001
Cliente: Europalco, Lda.
Projeto: #P0050 - Evento Corporativo

Serviços prestados            €10.000,00
IVA 23%                         €2.300,00
──────────────────────────────────────
TOTAL A PAGAR                 €12.300,00
```

**Campos relevantes:**
- Valor sem IVA: €10.000,00
- IVA liquidado: €2.300,00
- Total com IVA: €12.300,00

---

### 2.3 Integração com Sistema de Receitas

**Quando criar receita:**
- Ao emitir fatura? OU
- Ao receber pagamento? ← **Recomendado (regime de caixa)**

**Tabela `receitas` (proposta):**
```sql
receitas
├─ numero: VARCHAR(20)           -- #R000001
├─ fatura_numero: VARCHAR(20)    -- Fatura #2025/0001
├─ projeto_id: INTEGER NULL      -- Link para projeto
├─ cliente_id: INTEGER           -- Cliente que pagou
├─ descricao: TEXT
├─ valor_sem_iva: DECIMAL(10,2)  -- €10.000,00
├─ iva_liquidado: DECIMAL(10,2)  -- €2.300,00
├─ valor_c_iva: DECIMAL(10,2)    -- €12.300,00
├─ data_fatura: DATE             -- Data emissão
├─ data_recebimento: DATE NULL   -- Data pagamento
├─ estado: VARCHAR(20)           -- EMITIDO | RECEBIDO | CANCELADO
├─ tipo: VARCHAR(20)             -- PROJETO | OUTRO
└─ metodo_pagamento: VARCHAR(20) -- TRANSFERENCIA | MB | DINHEIRO
```

**Estados:**
- **EMITIDO:** Fatura emitida, aguarda pagamento
- **RECEBIDO:** Cliente pagou
- **CANCELADO:** Fatura anulada/creditada

---

### 2.4 Integração TOConline (Futuro)

**Objetivo:** Enviar faturas automaticamente para TOC processar

**Possível integração:**
- API ou export de ficheiro SAF-T
- TOC importa para software contabilidade
- Sincronização automática

**A discutir com TOC:**
- Formato preferido de integração
- Periodicidade de envio (mensal? tempo real?)
- Validações necessárias

---

## 3. DESPESAS E IVA DEDUTÍVEL

### 3.1 Todos os Tipos de Despesa São Dedutíveis

**Princípio:** Para efeitos fiscais, TODAS as despesas são empresariais.

**Tipos atuais:**
- FIXA_MENSAL
- PESSOAL_BA
- PESSOAL_RR
- EQUIPAMENTO
- PROJETO

**IVA dedutível:** Todas podem ter IVA dedutível (se fornecedor cobrar IVA)

**Campos em `despesas`:**
```sql
despesas
├─ valor_sem_iva: DECIMAL(10,2)    -- Base tributável
├─ valor_c_iva: DECIMAL(10,2)      -- Total pago
├─ iva_dedutivel: DECIMAL(10,2)    -- Calculado: valor_c_iva - valor_sem_iva
├─ taxa_iva: DECIMAL(5,2)          -- 23%, 13%, 6%, 0%
```

**Cálculo automático:**
```python
iva_dedutivel = valor_c_iva - valor_sem_iva
taxa_iva = (iva_dedutivel / valor_sem_iva) * 100  # se > 0
```

---

### 3.2 Despesas Sem IVA

**Exemplos:**
- Fornecedores isentos de IVA (art. 53º CIVA)
- Despesas no estrangeiro (regime reverse charge)
- Salários e ordenados
- Seguros

**Nesses casos:**
```python
valor_sem_iva = valor_c_iva
iva_dedutivel = 0
taxa_iva = 0
```

---

### 3.3 Validações

**Ao criar/editar despesa:**
1. Se `valor_c_iva` preenchido e `valor_sem_iva` vazio:
   - Assumir sem IVA: `valor_sem_iva = valor_c_iva`
   
2. Se ambos preenchidos:
   - Validar: `valor_c_iva >= valor_sem_iva`
   - Calcular: `iva_dedutivel = valor_c_iva - valor_sem_iva`
   
3. Se `taxa_iva` fornecida manualmente:
   - Validar coerência com valores
   
4. Estados:
   - IVA só é dedutível quando despesa está **PAGO**
   - Despesas PENDENTE não contam para apuramento IVA trimestral

---

## 4. IVA TRIMESTRAL

### 4.1 Conceito

**IVA a pagar = IVA Liquidado (receitas) - IVA Dedutível (despesas)**

**Periodicidade:** Trimestral (4 vezes por ano)

**Trimestres:**
- **1º Trimestre:** Janeiro, Fevereiro, Março
- **2º Trimestre:** Abril, Maio, Junho
- **3º Trimestre:** Julho, Agosto, Setembro
- **4º Trimestre:** Outubro, Novembro, Dezembro

---

### 4.2 Prazos (2025)

**Entrega da Declaração Periódica:**
- Até dia **20 do 2º mês** seguinte ao trimestre
- Via Portal das Finanças (transmissão eletrónica)

**Pagamento do IVA apurado:**
- Até dia **25 do 2º mês** seguinte ao trimestre

**Calendário 2025:**

| Trimestre | Período       | Entrega até | Pagamento até |
|-----------|---------------|-------------|---------------|
| 1º        | Jan-Mar 2025  | 20 Mai 2025 | 25 Mai 2025   |
| 2º        | Abr-Jun 2025  | 22 Ago 2025*| 25 Ago 2025   |
| 3º        | Jul-Set 2025  | 20 Nov 2025 | 25 Nov 2025   |
| 4º        | Out-Dez 2025  | 20 Fev 2026 | 25 Fev 2026   |

*Dia 22 porque dia 20 cai em fim de semana (ajustado)

**Nota:** Se data cair em fim de semana ou feriado, passa para dia útil seguinte.

---

### 4.3 Cálculo Trimestral

**Exemplo - 1º Trimestre 2025 (Jan-Mar):**

```python
# IVA LIQUIDADO (Receitas faturadas no trimestre)
receitas_q1 = [
    {'valor_sem_iva': 10000, 'iva': 2300},  # Fatura #2025/0001
    {'valor_sem_iva': 5000, 'iva': 1150},   # Fatura #2025/0002
]
total_iva_liquidado = sum(r['iva'] for r in receitas_q1)  # €3.450

# IVA DEDUTÍVEL (Despesas pagas no trimestre)
despesas_q1 = [
    {'valor_sem_iva': 1000, 'iva': 230},   # Despesa #D000015
    {'valor_sem_iva': 500, 'iva': 115},    # Despesa #D000016
]
total_iva_dedutivel = sum(d['iva'] for d in despesas_q1)  # €345

# APURAMENTO
iva_a_pagar = total_iva_liquidado - total_iva_dedutivel
# €3.450 - €345 = €3.105

# Se negativo → IVA a recuperar (empresa recebe reembolso)
```

**Resultado:**
- IVA a pagar ao Estado: **€3.105**
- Prazo pagamento: até 25 de Maio de 2025

---

### 4.4 Declaração Periódica de IVA

**Onde entregar:** Portal das Finanças → IVA → Declaração Periódica

**Campos principais:**
- Campo 01: IVA liquidado (vendas taxa normal 23%)
- Campo 02: IVA liquidado (vendas taxa intermédia 13%)
- Campo 03: IVA liquidado (vendas taxa reduzida 6%)
- Campo 40: IVA dedutível (compras)
- Campo 98: Total a pagar (campo 01+02+03 - campo 40)

**Anexos possíveis:**
- Anexo recapitulativo (operações intracomunitárias)
- Anexo de regularizações

---

### 4.5 Implementação no Sistema

**Tabela nova:** `iva_trimestral` (opcional, para histórico)

```sql
iva_trimestral
├─ id: INTEGER PRIMARY KEY
├─ ano: INTEGER                    -- 2025
├─ trimestre: INTEGER              -- 1, 2, 3, 4
├─ data_inicio: DATE               -- 2025-01-01
├─ data_fim: DATE                  -- 2025-03-31
│
├─ IVA Liquidado (Receitas):
│  ├─ total_receitas_sem_iva: DECIMAL(10,2)
│  ├─ iva_liquidado_23: DECIMAL(10,2)
│  ├─ iva_liquidado_13: DECIMAL(10,2)
│  ├─ iva_liquidado_6: DECIMAL(10,2)
│  └─ iva_liquidado_total: DECIMAL(10,2)
│
├─ IVA Dedutível (Despesas):
│  ├─ total_despesas_sem_iva: DECIMAL(10,2)
│  ├─ iva_dedutivel_23: DECIMAL(10,2)
│  ├─ iva_dedutivel_13: DECIMAL(10,2)
│  ├─ iva_dedutivel_6: DECIMAL(10,2)
│  └─ iva_dedutivel_total: DECIMAL(10,2)
│
├─ Apuramento:
│  ├─ iva_a_pagar: DECIMAL(10,2)   -- ou iva_a_recuperar (negativo)
│  ├─ data_declaracao: DATE NULL   -- Quando foi entregue
│  ├─ data_pagamento: DATE NULL    -- Quando foi pago
│  └─ estado: VARCHAR(20)          -- APURADO | DECLARADO | PAGO
│
└─ Metadata:
   ├─ notas: TEXT
   ├─ created_at: DATETIME
   └─ updated_at: DATETIME
```

**Cálculo automático:**
```python
def calcular_iva_trimestral(ano, trimestre):
    """
    Calcula IVA trimestral baseado em receitas e despesas
    """
    # Definir período
    inicio, fim = get_periodo_trimestre(ano, trimestre)
    
    # IVA Liquidado (receitas RECEBIDAS no período)
    receitas = Receita.filter(
        data_recebimento >= inicio,
        data_recebimento <= fim,
        estado = 'RECEBIDO'
    )
    
    iva_liquidado = sum(r.iva_liquidado for r in receitas)
    
    # IVA Dedutível (despesas PAGAS no período)
    despesas = Despesa.filter(
        data_pagamento >= inicio,
        data_pagamento <= fim,
        estado = 'PAGO'
    )
    
    iva_dedutivel = sum(d.iva_dedutivel for d in despesas)
    
    # Apuramento
    iva_a_pagar = iva_liquidado - iva_dedutivel
    
    return {
        'iva_liquidado': iva_liquidado,
        'iva_dedutivel': iva_dedutivel,
        'iva_a_pagar': iva_a_pagar
    }
```

---

### 4.6 Relatório IVA Trimestral

**UI: Screen "IVA Trimestral"**

```
┌─────────────────────────────────────────────────────┐
│ IVA TRIMESTRAL - 1º Trimestre 2025 (Jan-Mar)       │
├─────────────────────────────────────────────────────┤
│                                                     │
│ 💰 IVA LIQUIDADO (Receitas)                        │
│ ─────────────────────────────────────────────      │
│ Receitas sem IVA              €15.000,00           │
│ IVA 23%                        €3.450,00           │
│                                                     │
│ 📤 IVA DEDUTÍVEL (Despesas)                        │
│ ─────────────────────────────────────────────      │
│ Despesas sem IVA               €1.500,00           │
│ IVA 23%                          €345,00           │
│                                                     │
│ ═══════════════════════════════════════════════    │
│ 📊 APURAMENTO                                      │
│ ═══════════════════════════════════════════════    │
│                                                     │
│ IVA Liquidado                  €3.450,00           │
│ (-) IVA Dedutível                €345,00           │
│ ═══════════════════════════════════════════════    │
│ IVA A PAGAR                    €3.105,00           │
│                                                     │
│ Prazo entrega: 20 Mai 2025                         │
│ Prazo pagamento: 25 Mai 2025                       │
│                                                     │
│ [📄 Exportar Resumo] [✅ Marcar como Declarado]   │
└─────────────────────────────────────────────────────┘
```

**Funcionalidades:**
- Seletor de ano/trimestre
- Tabela com receitas do período (clicável)
- Tabela com despesas do período (clicável)
- Botão "Exportar para Excel" (enviar para TOC)
- Botão "Marcar como Declarado" (registar data)
- Histórico de trimestres anteriores

---

## 5. IRS RETIDO NA FONTE (FORNECEDORES)

### 5.1 Quando Reter

**Obrigação:** Agora deve reter IRS quando paga a fornecedores **recibos verdes** (trabalhadores independentes).

**Condição:** Fornecedor tem contabilidade organizada (Agora tem)

**Não reter se:**
- Fornecedor é empresa (tem NIF coletivo)
- Fornecedor está isento (rende < €15.000/ano)
- Fornecedor é estrangeiro sem atividade em PT

---

### 5.2 Taxas de Retenção (2025)

**Taxa geral:** **23%** (desceu de 25% em 2025)

**Taxas específicas:**
- **16,5%:** Atividades hoteleiras, restauração, algumas prestações de serviços
- **11,5%:** Propriedade intelectual, profissionais com deficiência ≥60%
- **20%:** Situações específicas (ver Portaria 1011/2001)

**Opção do fornecedor:**
- Fornecedor pode optar por **25%** em vez de 23% (se preferir)
- Indicar no recibo verde

**Taxa variável:** Sim, depende da atividade do fornecedor

---

### 5.3 Como Funciona

**Exemplo:**
```
Fornecedor: Sara Designer (freelancer)
Recibo Verde: €1.000,00
Taxa retenção: 23%

Cálculo:
──────────────────────────────
Valor serviço         €1.000,00
IRS retido (23%)        €230,00
──────────────────────────────
A PAGAR               €770,00
```

**Agora paga:**
- €770 ao fornecedor (transferência)
- €230 ao Estado (via Portal Finanças)

**Fornecedor recebe:**
- €770 na conta
- Direito a descontar €230 na declaração IRS anual

---

### 5.4 Campos em `despesas`

**Adicionar colunas:**
```sql
despesas
├─ ... (campos existentes)
│
├─ Retenção IRS (NOVO):
│  ├─ irs_retido: DECIMAL(10,2) DEFAULT 0      -- Valor retido
│  ├─ taxa_retencao_irs: DECIMAL(5,2) DEFAULT 0 -- 23%, 25%, etc
│  └─ irs_entregue: BOOLEAN DEFAULT FALSE      -- Já entregue ao Estado?
```

**Só aplicável a:**
- `tipo = 'PROJETO'` ou outros tipos onde se pague a freelancers
- `fornecedor.tipo = 'FREELANCER'` (novo campo em fornecedores)

**Cálculo automático:**
```python
if fornecedor.tipo == 'FREELANCER' and fornecedor.taxa_retencao > 0:
    despesa.irs_retido = despesa.valor_sem_iva * (fornecedor.taxa_retencao / 100)
    despesa.taxa_retencao_irs = fornecedor.taxa_retencao
else:
    despesa.irs_retido = 0
    despesa.taxa_retencao_irs = 0
```

---

### 5.5 Obrigação Declarativa - MENSAL

**Declaração:** **DMR (Declaração Mensal de Remunerações)** OU **Modelo 10 Anual**

**Para Agora (contabilidade organizada):**
- **Opção recomendada:** Entregar valores retidos **mensalmente** via Portal Finanças
- **Prazo:** Até dia **20 do mês seguinte** àquele em que pagou ao fornecedor

**Alternativa:**
- Declaração **Modelo 10** (anual) - até **10 de Fevereiro** do ano seguinte
- Prorrogável até final de Fevereiro

**Nota:** Confirmar com TOC qual método preferem (mensal vs anual)

---

### 5.6 Pagamento do IRS Retido

**Quando pagar:** Junto com entrega da declaração mensal

**Prazo:** Até dia **25 do mês seguinte**

**Exemplo - Março 2025:**
```
Março:
- Pagou €1.000 a Sara → Reteve €230
- Pagou €800 a João → Reteve €184

Total retido: €414

Obrigação:
- Até 20 Abril: Declarar retenções de Março
- Até 25 Abril: Pagar €414 ao Estado
```

**Onde pagar:** Portal das Finanças (documento de cobrança gerado automaticamente)

---

### 5.7 Tabela de Fornecedores - Novos Campos

**Adicionar em `fornecedores`:**
```sql
fornecedores
├─ ... (campos existentes)
│
├─ Retenção IRS (NOVO):
│  ├─ tipo: VARCHAR(20)                -- 'EMPRESA' | 'FREELANCER' | 'OUTRO'
│  ├─ taxa_retencao_irs: DECIMAL(5,2)  -- 23%, 25%, 16.5%, etc
│  └─ isento_retencao: BOOLEAN DEFAULT FALSE
```

**Validações:**
```python
if fornecedor.tipo == 'FREELANCER':
    # Deve ter taxa definida
    if not fornecedor.taxa_retencao_irs:
        fornecedor.taxa_retencao_irs = 23.0  # Default
        
if fornecedor.tipo == 'EMPRESA':
    # Empresas não têm retenção
    fornecedor.taxa_retencao_irs = 0
    fornecedor.isento_retencao = True
```

---

### 5.8 Relatório Mensal IRS Retido

**UI: Screen "IRS Retido"**

```
┌─────────────────────────────────────────────────────┐
│ IRS RETIDO - Março 2025                            │
├─────────────────────────────────────────────────────┤
│                                                     │
│ Fornecedor        Valor    Taxa   IRS Retido       │
│ ─────────────────────────────────────────────────  │
│ Sara Designer     €1.000   23%     €230,00         │
│ João Fotógrafo      €800   23%     €184,00         │
│ Ana Editora         €500   25%*    €125,00         │
│                                                     │
│ ═══════════════════════════════════════════════    │
│ TOTAL IRS RETIDO                   €539,00         │
│                                                     │
│ Prazo declaração: 20 Abril 2025                    │
│ Prazo pagamento: 25 Abril 2025                     │
│                                                     │
│ Estado: ⚠️ POR DECLARAR                            │
│                                                     │
│ [📄 Exportar para TOC] [✅ Marcar como Entregue]  │
└─────────────────────────────────────────────────────┘

*Ana optou por taxa de 25%
```

**Funcionalidades:**
- Filtro por mês
- Lista de despesas com retenção
- Total a entregar ao Estado
- Exportação para Excel (enviar TOC)
- Marcar como entregue (registar data)

---

## 6. IRC ANUAL

### 6.1 Conceito

**IRC = Imposto sobre o Rendimento de Pessoas Coletivas**

Tributa os **lucros** da empresa.

**Base tributável:**
```
Lucro Contabilístico (receitas - despesas)
+ Correções fiscais (despesas não aceites)
- Deduções fiscais (benefícios, prejuízos anteriores)
═══════════════════════════════════════════
= MATÉRIA COLETÁVEL
```

**Matéria coletável × Taxa IRC = IRC a pagar**

---

### 6.2 Taxas IRC (2025)

**PME (Agora qualifica):**
- **16%** sobre os primeiros **€50.000**
- **20%** sobre o excedente

**Exemplo:**
```
Matéria coletável: €80.000

Cálculo:
€50.000 × 16% = €8.000
€30.000 × 20% = €6.000
────────────────────────
TOTAL IRC:      €14.000
```

**Derrama Municipal:**
- Taxa adicional aplicada por alguns municípios
- Até **1,5%** sobre lucro tributável
- Depende do município da sede

**Derrama Estadual:**
- Não aplicável (só para lucros > €1,5 milhões)

---

### 6.3 Apuramento Anual

**Período:** Ano civil (1 Jan - 31 Dez)

**Fórmula simplificada:**
```python
# Resultado Contabilístico
receitas_ano = sum(todas_receitas_2025)
despesas_ano = sum(todas_despesas_2025)
resultado_antes_impostos = receitas_ano - despesas_ano

# Correções fiscais (complexo - faz TOC)
# Exemplos:
# + Despesas não dedutíveis (multas, some tributações autónomas)
# - Benefícios fiscais (RFAI, SIFIDE, etc)
# - Prejuízos fiscais anos anteriores (carry forward 12 anos)

materia_coletavel = resultado_antes_impostos + correcoes

# IRC
if materia_coletavel <= 0:
    irc = 0  # Prejuízo, não paga IRC
else:
    if materia_coletavel <= 50000:
        irc = materia_coletavel * 0.16
    else:
        irc = (50000 * 0.16) + ((materia_coletavel - 50000) * 0.20)
```

**Nota:** Cálculo real é MUITO mais complexo (TOC faz)

---

### 6.4 Declaração Anual

**Documento:** **Modelo 22** (Declaração de Rendimentos IRC)

**Prazo entrega:** Até **31 de Maio** do ano seguinte

**Exemplo:** Rendimentos 2025 → Modelo 22 até 31 Maio 2026

**Anexos obrigatórios:**
- IES (Informação Empresarial Simplificada) - inclui balanço, demonstração resultados
- Modelo 22 propriamente dito
- Anexos específicos (depende da situação)

**Responsável:** TOC (Técnico Oficial de Contas) obrigatório

---

### 6.5 Pagamento do IRC

**Não há pagamentos por conta** (para Agora, em princípio)

**Pagamento:** Após liquidação pela AT

**Prazo:** Até **31 de Agosto** do ano da entrega (para IRC liquidado em Maio)

**Exemplo:**
```
2025: Exercício económico
Mai 2026: Entrega Modelo 22
Jun 2026: AT liquida IRC (emite documento cobrança)
Ago 2026: Pagamento até dia 31
```

**Pagamento em prestações:** Possível (mediante pedido)
- Até 36 prestações mensais
- Mínimo €30/prestação
- Sem garantia se dívida < €10.000

---

### 6.6 Regime de Contabilidade Organizada

**Obrigações contabilísticas:**

1. **Plano de Contas:** SNC (Sistema Normalização Contabilística)
   - Agora deve usar **SNC para Microentidades** (simplificado)
   
2. **Livros obrigatórios:**
   - Diário
   - Razão
   - Inventário (se tiver stock)
   - Livro de IVA

3. **Documentos anuais:**
   - Balanço
   - Demonstração de Resultados
   - Anexo (notas às demonstrações financeiras)

4. **Conservação:** 10 anos

**Responsável:** TOC obrigatório (contabilista certificado)

---

### 6.7 Implementação no Sistema

**O sistema Agora NÃO substitui contabilidade oficial.**

**Função:** Fornecer dados ao TOC

**Exports necessários:**
- Listagem de receitas (ano completo)
- Listagem de despesas (ano completo)
- Boletins pagos (ano completo)
- Projetos e estado (ano completo)

**Formato:** Excel ou CSV

**TOC:** Importa para software contabilidade profissional (PHC, Sage, Primavera, etc)

---

## 7. OUTRAS OBRIGAÇÕES

### 7.1 Declaração Mensal de Remunerações (DMR)

**Obrigação:** Declarar salários/ordenados dos sócios-gerentes

**Periodicidade:** Mensal

**Prazo:** Até dia **10 do mês seguinte** ao pagamento

**Responsável:** TOC ou RH da empresa

**Nota:** Agora tem 2 sócios com ordenado → DMR obrigatória

---

### 7.2 Segurança Social

**Quotizações:**
- Entidade patronal: 23,75%
- Trabalhador: 11%
- **Total:** 34,75% sobre salário bruto

**Declaração:** Incluída na DMR

**Pagamento:** Até dia **20 do mês seguinte**

---

### 7.3 Comunicação de Faturas

**SAF-T de Faturação:**
- Comunicar todas as faturas emitidas
- Até dia **5 do mês seguinte**
- Via Portal das Finanças (automático se programa certificado)

---

### 7.4 Inventário Anual

**Obrigação:** Comunicar inventário de existências à AT

**Prazo:** Até **31 de Janeiro** de cada ano

**Aplicável:** Se empresa tiver stock (equipamento, consumíveis)

**Agora:** Confirmar com TOC se aplicável

---

## 8. CALENDÁRIO FISCAL

### 8.1 Obrigações Mensais

**Dia 5:** Comunicação faturas (SAF-T)  
**Dia 10:** DMR (ordenados sócios)  
**Dia 20:** Segurança Social (pagamento)  
**Dia 20:** IRS retido - declaração (se mensal)  
**Dia 25:** IRS retido - pagamento (se mensal)

---

### 8.2 Obrigações Trimestrais

**IVA:**
- **20 do 2º mês:** Declaração periódica
- **25 do 2º mês:** Pagamento

**Segurança Social (trabalhadores independentes):**
- Declaração trimestral rendimentos (Agora não aplicável)

---

### 8.3 Obrigações Anuais

**Janeiro:**
- Dia 31: Inventário de existências (se aplicável)

**Fevereiro:**
- Dia 10 (prorrogável até 28): Modelo 10 (rendimentos pagos ano anterior)

**Abril a Junho:**
- IRS pessoal dos sócios (declaração Modelo 3)

**Maio:**
- Dia 31: Modelo 22 (IRC) + IES

**Agosto:**
- Dia 31: Pagamento IRC (se liquidado)

---

### 8.4 Calendário Visual 2025

```
┌────────────┬─────────────────────────────────────────┐
│ JAN 2025   │ • Inventário (31)                       │
├────────────┼─────────────────────────────────────────┤
│ FEV        │ • Modelo 10 (10, prorr. 28)            │
│            │ • IVA Q4/2024: declaração (20), pag (25)│
├────────────┼─────────────────────────────────────────┤
│ MAR        │                                         │
├────────────┼─────────────────────────────────────────┤
│ ABR        │ • IRS Modelo 3 (início)                │
├────────────┼─────────────────────────────────────────┤
│ MAI        │ • IRS Modelo 3 (até 30 Jun)            │
│            │ • IVA Q1: declaração (20), pag (25)    │
│            │ • IRC Modelo 22 + IES (31)             │
├────────────┼─────────────────────────────────────────┤
│ JUN        │ • IRS Modelo 3 (fim, 30)               │
├────────────┼─────────────────────────────────────────┤
│ JUL        │                                         │
├────────────┼─────────────────────────────────────────┤
│ AGO        │ • IVA Q2: declaração (22*), pag (25)   │
│            │ • IRC: pagamento (31)                   │
├────────────┼─────────────────────────────────────────┤
│ SET        │                                         │
├────────────┼─────────────────────────────────────────┤
│ OUT        │                                         │
├────────────┼─────────────────────────────────────────┤
│ NOV        │ • IVA Q3: declaração (20), pag (25)    │
├────────────┼─────────────────────────────────────────┤
│ DEZ        │                                         │
└────────────┴─────────────────────────────────────────┘

Mensalmente (todo o ano):
• Dia 5: Comunicação faturas
• Dia 10: DMR
• Dia 20: Segurança Social + IRS retido (declaração)
• Dia 25: IRS retido (pagamento)
```

---

## 9. IMPLEMENTAÇÃO TÉCNICA

### 9.1 Alterações na Base de Dados

**Migration 021: Sistema Fiscal Completo**

```sql
-- ════════════════════════════════════════════════════
-- RECEITAS (NOVA TABELA)
-- ════════════════════════════════════════════════════

CREATE TABLE receitas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    numero VARCHAR(20) UNIQUE NOT NULL,  -- #R000001
    
    -- Relações
    fatura_numero VARCHAR(50),           -- Fatura #2025/0001
    projeto_id INTEGER,
    cliente_id INTEGER NOT NULL,
    
    -- Valores
    descricao TEXT NOT NULL,
    valor_sem_iva DECIMAL(10,2) NOT NULL,
    iva_liquidado DECIMAL(10,2) NOT NULL DEFAULT 0,
    taxa_iva DECIMAL(5,2) NOT NULL DEFAULT 23.0,
    valor_c_iva DECIMAL(10,2) NOT NULL,
    
    -- Datas
    data_fatura DATE NOT NULL,
    data_recebimento DATE,
    
    -- Estado e tipo
    estado VARCHAR(20) NOT NULL DEFAULT 'EMITIDO',
      -- EMITIDO | RECEBIDO | CANCELADO
    tipo VARCHAR(20) NOT NULL DEFAULT 'PROJETO',
      -- PROJETO | OUTRO
    metodo_pagamento VARCHAR(20),
      -- TRANSFERENCIA | MB | DINHEIRO | CHEQUE
    
    -- Metadata
    nota TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    FOREIGN KEY (projeto_id) REFERENCES projetos(id) ON DELETE SET NULL,
    FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE RESTRICT
);

CREATE INDEX idx_receitas_projeto ON receitas(projeto_id);
CREATE INDEX idx_receitas_cliente ON receitas(cliente_id);
CREATE INDEX idx_receitas_data_recebimento ON receitas(data_recebimento);
CREATE INDEX idx_receitas_estado ON receitas(estado);


-- ════════════════════════════════════════════════════
-- DESPESAS (ADICIONAR COLUNAS IRS)
-- ════════════════════════════════════════════════════

ALTER TABLE despesas ADD COLUMN irs_retido DECIMAL(10,2) DEFAULT 0;
ALTER TABLE despesas ADD COLUMN taxa_retencao_irs DECIMAL(5,2) DEFAULT 0;
ALTER TABLE despesas ADD COLUMN irs_entregue BOOLEAN DEFAULT FALSE;


-- ════════════════════════════════════════════════════
-- FORNECEDORES (ADICIONAR COLUNAS)
-- ════════════════════════════════════════════════════

ALTER TABLE fornecedores ADD COLUMN tipo VARCHAR(20) DEFAULT 'EMPRESA';
  -- EMPRESA | FREELANCER | OUTRO

ALTER TABLE fornecedores ADD COLUMN taxa_retencao_irs DECIMAL(5,2) DEFAULT 0;
ALTER TABLE fornecedores ADD COLUMN isento_retencao BOOLEAN DEFAULT FALSE;


-- ════════════════════════════════════════════════════
-- IVA TRIMESTRAL (HISTÓRICO/CONTROLO)
-- ════════════════════════════════════════════════════

CREATE TABLE iva_trimestral (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ano INTEGER NOT NULL,
    trimestre INTEGER NOT NULL,  -- 1, 2, 3, 4
    data_inicio DATE NOT NULL,
    data_fim DATE NOT NULL,
    
    -- IVA Liquidado
    total_receitas_sem_iva DECIMAL(10,2) DEFAULT 0,
    iva_liquidado_23 DECIMAL(10,2) DEFAULT 0,
    iva_liquidado_13 DECIMAL(10,2) DEFAULT 0,
    iva_liquidado_6 DECIMAL(10,2) DEFAULT 0,
    iva_liquidado_total DECIMAL(10,2) DEFAULT 0,
    
    -- IVA Dedutível
    total_despesas_sem_iva DECIMAL(10,2) DEFAULT 0,
    iva_dedutivel_23 DECIMAL(10,2) DEFAULT 0,
    iva_dedutivel_13 DECIMAL(10,2) DEFAULT 0,
    iva_dedutivel_6 DECIMAL(10,2) DEFAULT 0,
    iva_dedutivel_total DECIMAL(10,2) DEFAULT 0,
    
    -- Apuramento
    iva_a_pagar DECIMAL(10,2) DEFAULT 0,  -- positivo ou negativo
    
    -- Controlo
    data_declaracao DATE,
    data_pagamento DATE,
    estado VARCHAR(20) DEFAULT 'APURADO',
      -- APURADO | DECLARADO | PAGO
    
    -- Metadata
    notas TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(ano, trimestre)
);

CREATE INDEX idx_iva_trimestral_periodo ON iva_trimestral(ano, trimestre);


-- ════════════════════════════════════════════════════
-- IRS MENSAL (HISTÓRICO RETENÇÕES)
-- ════════════════════════════════════════════════════

CREATE TABLE irs_mensal (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ano INTEGER NOT NULL,
    mes INTEGER NOT NULL,  -- 1-12
    
    -- Totais
    total_retido DECIMAL(10,2) DEFAULT 0,
    num_despesas INTEGER DEFAULT 0,
    
    -- Controlo
    data_declaracao DATE,
    data_pagamento DATE,
    estado VARCHAR(20) DEFAULT 'APURADO',
      -- APURADO | DECLARADO | PAGO
    
    -- Metadata
    notas TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(ano, mes)
);

CREATE INDEX idx_irs_mensal_periodo ON irs_mensal(ano, mes);
```

---

### 9.2 Lógica de Negócio

**Ficheiros novos:**
```
logic/
├─ receitas.py          # CRUD receitas
├─ iva_trimestral.py    # Cálculo IVA trimestral
├─ irs_mensal.py        # Cálculo IRS retido mensal
└─ fiscal_exports.py    # Exports para TOC
```

**Funcionalidades principais:**

1. **Receitas:**
   - CRUD completo
   - Cálculo automático IVA
   - Link bidirecional com projetos
   - Estados (EMITIDO → RECEBIDO)

2. **IVA Trimestral:**
   - Cálculo automático baseado em receitas/despesas pagas
   - Relatório detalhado
   - Export para Excel (TOC)

3. **IRS Mensal:**
   - Cálculo automático baseado em despesas a freelancers
   - Relatório por mês
   - Export para Excel (TOC)

4. **Exports Fiscais:**
   - Receitas anuais (Excel)
   - Despesas anuais (Excel)
   - IVA trimestral (Excel)
   - IRS mensal (Excel)
   - SAF-T (XML) - futuro

---

### 9.3 UI - Novos Screens

**1. Receitas (ReceitasScreen):**
```
ui/screens/receitas.py

- Tabela de receitas (filtros: período, cliente, estado)
- Botão "Nova Receita"
- Formulário: cliente, projeto (opcional), valores, datas
- Cálculo automático IVA
- Estados: EMITIDO → RECEBIDO → CANCELADO
```

**2. IVA Trimestral (IVATrimestralScreen):**
```
ui/screens/iva_trimestral.py

- Seletor ano/trimestre
- Tabela receitas do período (IVA liquidado)
- Tabela despesas do período (IVA dedutível)
- Apuramento automático
- Export Excel
- Marcar como declarado/pago
```

**3. IRS Retido (IRSRetidoScreen):**
```
ui/screens/irs_retido.py

- Seletor ano/mês
- Tabela despesas com retenção
- Total a entregar ao Estado
- Export Excel
- Marcar como declarado/pago
```

**4. Dashboard Fiscal (FiscalDashboardScreen):**
```
ui/screens/fiscal_dashboard.py

- Próximas obrigações (calendário)
- Alertas de prazos
- Resumo trimestre atual
- Resumo ano fiscal
- Atalhos para IVA/IRS/IRC
```

---

### 9.4 Integrações Futuras

**TOConline:**
- API ou export SAF-T
- Sincronização automática receitas/despesas
- A discutir com TOC

**Faturação:**
- Emissão de faturas certificadas
- Comunicação automática AT (SAF-T)
- Integração com receitas

**Contabilidade:**
- Export para PHC, Sage, Primavera, etc
- Mapeamento de contas (Plano Contas SNC)
- Validações contabilísticas

---

## 📚 ANEXOS

### A. Glossário Fiscal

- **AT:** Autoridade Tributária e Aduaneira
- **CIVA:** Código do IVA
- **CIRC:** Código do IRC
- **CIRS:** Código do IRS
- **DMR:** Declaração Mensal de Remunerações
- **IES:** Informação Empresarial Simplificada
- **PME:** Pequena e Média Empresa
- **SAF-T:** Standard Audit File for Tax purposes
- **SNC:** Sistema de Normalização Contabilística
- **TOC:** Técnico Oficial de Contas

---

### B. Links Úteis

- **Portal das Finanças:** https://www.portaldasfinancas.gov.pt
- **Segurança Social:** https://www.seg-social.pt
- **Ordem dos Contabilistas:** https://www.occ.pt
- **Códigos fiscais:** https://info.portaldasfinancas.gov.pt

---

### C. Contactos

**TOC da Agora:** [a preencher]  
**Telefone:** [a preencher]  
**Email:** [a preencher]  

**Repartição de Finanças:** [a preencher]  
**Segurança Social:** [a preencher]

---

_Última atualização: 15/11/2025_  
_Próxima revisão: Com TOC antes de implementar_
