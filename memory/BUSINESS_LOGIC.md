# 🧠 Lógica de Negócio - Agora Contabilidade

## 1. ORÇAMENTOS

### 1.1 Conceito

Um orçamento tem **dois lados espelhados**:

**LADO CLIENTE** (o que o cliente vê/paga)
- Estrutura hierárquica: Secções → Itens
- Exportado para PDF com branding
- Define o valor total prometido ao cliente

**LADO EMPRESA** (distribuição interna)
- Repartições: como dividimos o valor entre nós
- 6 tipos: BA, RR, EMPRESA, FORNECEDOR, EQUIPAMENTO, DESPESA
- Deve fazer match com o total do lado cliente

---

### 1.2 Estados e Transições
```
RASCUNHO ──aprovar──> APROVADO ──anular──> ANULADO
   ↑                                          ↓
   └──────────── não volta atrás ─────────────┘
```

**RASCUNHO:**
- Pode ser gravado vazio ou incompleto
- Pode ser editado livremente
- Sem validação de totais

**APROVADO:**
- ✅ Totais devem coincidir (Cliente = Empresa)
- ✅ Converte automaticamente em Projeto
- ❌ Não pode ser editado
- ❌ Não pode voltar a Rascunho

**ANULADO:**
- Pode anular orçamento aprovado
- Projeto associado também fica anulado
- Estado final (não reverte)

---

### 1.3 Regras de Validação

**Antes de Aprovar:**
```python
total_cliente = sum(item.total for secao in secoes for item in secao.itens)
total_empresa = sum(reparticao.valor for reparticao in reparticoes)

if total_cliente != total_empresa:
    raise ValidationError(f"Totais não coincidem (diferença: €{abs(total_cliente - total_empresa)})")
```

**Campos Obrigatórios:**
- Owner (BA ou RR)
- Cliente
- Pelo menos 1 secção com 1 item (lado cliente)
- Pelo menos 1 repartição (lado empresa)

---

### 1.4 Conversão Orçamento → Projeto

**Trigger:** Automático ao aprovar orçamento

**Dados copiados:**
```python
projeto = Projeto(
    owner = orcamento.owner,                    # BA ou RR
    orcamento_id = orcamento.id,                # Link bidirecional
    cliente_id = orcamento.cliente_id,
    tipo = 'EMPRESA',
    valor = total_lado_cliente,
    
    # Prémios (soma das repartições):
    premio_ba = sum(valor onde tipo='BA'),
    premio_rr = sum(valor onde tipo='RR'),
    
    # Novos campos (rastreabilidade):
    valor_empresa = sum(valor onde tipo='EMPRESA'),
    valor_fornecedores = sum(valor onde tipo='FORNECEDOR'),
    valor_equipamento = sum(valor onde tipo='EQUIPAMENTO'),
    valor_despesas = sum(valor onde tipo='DESPESA'),
    
    estado = 'EM_CURSO',
    data_inicio = hoje
)
```

**Efeitos colaterais:**
1. Atualizar `equipamento.rendimento_acumulado` para cada repartição tipo='EQUIPAMENTO'
2. Marcar orçamento como APROVADO
3. Criar link bidirecional: `orcamento.projeto_id = projeto.id`

---

### 1.5 Estrutura de Dados

**Tabelas envolvidas:**
```
orcamentos
├─ owner: 'BA' | 'RR'
├─ cliente_id: FK → clientes
├─ estado: 'RASCUNHO' | 'APROVADO' | 'ANULADO'
├─ valor_total: DECIMAL (calculado do lado cliente)
└─ projeto_id: FK → projetos (após aprovação)

proposta_secoes
├─ orcamento_id: FK
├─ nome: VARCHAR
└─ ordem: INT

proposta_itens
├─ secao_id: FK
├─ descricao: VARCHAR
├─ quantidade: DECIMAL
├─ preco_unitario: DECIMAL
└─ total: DECIMAL (calculado: qtd × preço)

proposta_reparticoes
├─ orcamento_id: FK
├─ tipo: 'BA' | 'RR' | 'EMPRESA' | 'FORNECEDOR' | 'EQUIPAMENTO' | 'DESPESA'
├─ valor: DECIMAL
├─ fornecedor_id: FK → fornecedores (se tipo='FORNECEDOR')
└─ equipamento_id: FK → equipamento (se tipo='EQUIPAMENTO')
```

---

### 1.6 Casos de Uso

**UC1: Criar Orçamento Completo**
1. Preencher owner, cliente
2. Adicionar secções e itens (lado cliente)
3. Adicionar repartições (lado empresa)
4. Verificar que totais coincidem
5. Gravar rascunho (ou aprovar se válido)

**UC2: Aprovar Orçamento**
1. Validar totais coincidem
2. Criar projeto automaticamente
3. Atualizar rendimento de equipamentos
4. Marcar orçamento como APROVADO

**UC3: Anular Orçamento Aprovado**
1. Marcar orçamento como ANULADO
2. Marcar projeto associado como ANULADO
3. Rendimentos de equipamento não revertem

---

## 2. BOLETINS ITINERÁRIO

### 2.1 Conceito

Boletim de deslocações e ajudas de custo para sócios (BA ou RR).

**Estrutura:**
- Header: Sócio, Mês/Ano, Descrição
- Linhas de Deslocação: múltiplas linhas com detalhes
- Total: calculado automaticamente (soma das linhas)

**Cálculo por linha:**
```
Total Linha = (dias_nacional × €72.65) + 
              (dias_estrangeiro × €167.07) + 
              (kms × €0.40)
```

**Valores de referência:** editáveis por ano (tabela `valores_referencia_anual`)

---

### 2.2 Estados e Transições
```
PENDENTE ──marcar pago──> PAGO
   ↑                        │
   └────── pode voltar ─────┘
```

**PENDENTE:**
- Boletim criado mas ainda não pago
- Pode ser editado livremente
- Não afeta saldos dos sócios

**PAGO:**
- Marca data de pagamento
- **Desconta do saldo do sócio** (entra como despesa)
- Pode voltar a PENDENTE (se marcado por engano)
- Pode ser editado mesmo depois de pago

**Nota:** Não existe estado ANULADO. Para cancelar, apaga-se o boletim.

---

### 2.3 Criação de Boletins

**Métodos:**

1. **Manual (normal):**
   - Criar novo boletim vazio
   - Adicionar linhas uma a uma
   - Total calcula automaticamente

2. **Duplicar existente:**
   - Copiar boletim completo (header + todas as linhas)
   - Útil para boletins mensais repetidos
   - Permite editar depois de duplicar

**Removido:** Sistema de templates recorrentes (demasiado complexo)

---

### 2.4 Linhas de Deslocação

**Campos por linha:**
- Data início / Data fim
- Dias nacional (0+)
- Dias estrangeiro (0+)
- Kms (0+)
- Projeto (opcional) - dropdown com autocomplete
- Nota (opcional)
- **Total:** calculado automaticamente

**Validações:**
- Pelo menos 1 linha para gravar boletim
- Pelo menos 1 valor > 0 por linha (dias ou kms)
- Projeto é sempre opcional (FK com ON DELETE SET NULL)

**Cálculo automático:**
```python
# Por linha:
total_linha = (dias_nacional * valor_dia_nacional) + 
              (dias_estrangeiro * valor_dia_estrangeiro) + 
              (kms * valor_km)

# Total do boletim:
total_boletim = sum(linha.total for linha in linhas)
```

---

## 2. BOLETINS ITINERÁRIO

### 2.1 Conceito

Boletim de deslocações e ajudas de custo para sócios (BA ou RR).

**Estrutura:**
- Header: Sócio, Mês/Ano, Descrição
- Linhas de Deslocação: múltiplas linhas com detalhes
- Total: calculado automaticamente (soma das linhas)

**Cálculo por linha:**
```
Total Linha = (dias_nacional × €72.65) + 
              (dias_estrangeiro × €167.07) + 
              (kms × €0.40)
```

**Valores de referência:** editáveis por ano (tabela `valores_referencia_anual`)

---

### 2.2 Estados e Transições
```
PENDENTE ──marcar pago──> PAGO
   ↑                        │
   └────── pode voltar ─────┘
```

**PENDENTE:**
- Boletim criado mas ainda não pago
- Pode ser editado livremente
- Não afeta saldos dos sócios

**PAGO:**
- Marca data de pagamento
- **Desconta do saldo do sócio** (entra como despesa)
- Pode voltar a PENDENTE (se marcado por engano)
- Pode ser editado mesmo depois de pago

**Nota:** Não existe estado ANULADO. Para cancelar, apaga-se o boletim.

---

### 2.3 Criação de Boletins

**Métodos:**

1. **Manual (normal):**
   - Criar novo boletim vazio
   - Adicionar linhas uma a uma
   - Total calcula automaticamente

2. **Duplicar existente:**
   - Copiar boletim completo (header + todas as linhas)
   - Útil para boletins mensais repetidos
   - Permite editar depois de duplicar

**Removido:** Sistema de templates recorrentes (demasiado complexo)

---

### 2.4 Linhas de Deslocação

**Campos por linha:**
- Data início / Data fim
- Dias nacional (0+)
- Dias estrangeiro (0+)
- Kms (0+)
- Projeto (opcional) - dropdown com autocomplete
- Nota (opcional)
- **Total:** calculado automaticamente

**Validações:**
- **Boletim DEVE ter pelo menos 1 linha** (bloqueia gravação se vazio)
- Pelo menos 1 valor > 0 por linha (dias ou kms)
- Projeto é sempre opcional (FK com ON DELETE SET NULL)

**Cálculo automático:**
```python
# Por linha:
total_linha = (dias_nacional * valor_dia_nacional) + 
              (dias_estrangeiro * valor_dia_estrangeiro) + 
              (kms * valor_km)

# Total do boletim:
total_boletim = sum(linha.total for linha in linhas)
```

---

### 2.5 Impacto Financeiro

**Quando marca como PAGO:**

1. **Cria despesa automaticamente:**
```python
despesa = Despesa(
    tipo = 'FIXA_MENSAL',
    credor_socio = boletim.socio,  # 'BA' ou 'RR'
    descricao = f"Boletim {boletim.numero} - {boletim.mes}/{boletim.ano}",
    valor_c_iva = boletim.total,
    data = boletim.data_pagamento,
    estado = 'PAGO',
    boletim_id = boletim.id  # Link
)
```

2. **Desconta do saldo do sócio:**
- Saldo BA/RR diminui pelo valor do boletim
- Aparece como OUT no cálculo de Saldos Pessoais

**Quando volta a PENDENTE:**
- Despesa associada muda estado para PENDENTE
- Saldo do sócio volta ao normal (despesa pendente não desconta)

---

### 2.6 Relação com Projetos

**Opcional nas linhas:**
- Linha pode ter `projeto_id` (rastreabilidade)
- Se projeto apagado → `projeto_id = NULL` (linha mantém-se)
- Dropdown com autocomplete (mesmo sistema dos orçamentos)

**Útil para:**
- Saber que deslocações foram feitas para que projeto
- Relatórios futuros (custo real vs orçamentado)

---

### 2.7 Valores de Referência

**Tabela `valores_referencia_anual`:**
- Valores editáveis por ano
- Defaults: €72.65 (nacional), €167.07 (estrangeiro), €0.40 (km)
- Acesso via botão em configurações

**Lógica de fallback:**
```python
def get_valores_referencia(ano):
    valores = ValoresReferencia.get(ano)
    
    if valores:
        return valores
    
    # Se ano não existe, usa ano anterior
    ano_anterior = ano - 1
    valores_anteriores = ValoresReferencia.get(ano_anterior)
    
    if valores_anteriores:
        return valores_anteriores
    
    # Fallback final: hardcoded
    return {
        'valor_dia_nacional': 72.65,
        'valor_dia_estrangeiro': 167.07,
        'valor_km': 0.40
    }
```

---

### 2.8 Estrutura de Dados
```
boletins
├─ socio: 'BA' | 'RR'
├─ mes: INT (1-12)
├─ ano: INT (2024, 2025...)
├─ descricao: VARCHAR (ex: "SET2025")
├─ total: DECIMAL (calculado)
├─ estado: 'PENDENTE' | 'PAGO'
├─ data_emissao: DATE
├─ data_pagamento: DATE (NULL se pendente)
└─ despesa_id: FK → despesas (quando pago)

boletim_linhas
├─ boletim_id: FK
├─ data_inicio: DATE
├─ data_fim: DATE
├─ dias_nacional: DECIMAL
├─ dias_estrangeiro: DECIMAL
├─ kms: DECIMAL
├─ total: DECIMAL (calculado)
├─ projeto_id: FK → projetos (ON DELETE SET NULL)
└─ nota: TEXT

valores_referencia_anual
├─ ano: INT (PK)
├─ valor_dia_nacional: DECIMAL (72.65)
├─ valor_dia_estrangeiro: DECIMAL (167.07)
└─ valor_km: DECIMAL (0.40)
```

---

### 2.9 Casos de Uso

**UC1: Criar Boletim Manual**
1. Selecionar sócio (BA/RR)
2. Definir mês/ano
3. Adicionar linhas de deslocação (dias, kms, projeto opcional)
4. Total calcula automaticamente
5. Gravar como PENDENTE

**UC2: Duplicar Boletim**
1. Selecionar boletim existente
2. Clicar "Duplicar"
3. Copia header + todas as linhas
4. Permite editar antes de gravar

**UC3: Marcar como Pago**
1. Validar boletim tem linhas
2. Criar despesa automática
3. Atualizar estado para PAGO
4. Desconta do saldo do sócio

**UC4: Reverter Pagamento**
1. Marcar boletim como PENDENTE novamente
2. Despesa associada volta a PENDENTE
3. Saldo do sócio volta ao normal

---

### 2.10 Interface

**Screen Principal (BoletinsScreen):**
- Tabela com colunas: Número, Sócio, Mês/Ano, Linhas (qtd), Valor, Estado, Data Pagamento
- Filtros: Sócio (Todos/BA/RR), Estado (Todos/Pendente/Pago)
- Botões: 
  - `+ Novo Boletim` → abre BoletimFormScreen
  - `⚙️ Configurações` → Valores Referência

**BoletimFormScreen (editor completo):**
- Header: Sócio, Mês, Ano, Descrição
- Tabela de Linhas (CRUD inline):
  - Adicionar/Editar/Apagar linhas
  - Projeto: dropdown com autocomplete + "➕ Criar Novo"
  - Total por linha calculado em tempo real
- Footer: **TOTAL BOLETIM: €XXX** (destaque)
- Botões: `Gravar`, `Duplicar`, `Marcar Pago/Pendente`

**REMOVER:**
- `FormularioBoletimDialog` (legacy)
- Botão "Emitir Boletim" (laranja)
- Sistema de templates (`boletim_templates`, botão "Gerar Recorrentes")

---

## 3. PROJETOS

### 3.1 Conceito

Projetos representam trabalhos para clientes, podendo ter ou não orçamento associado.

**Tipos:**
- **PESSOAL (BA/RR):** Projeto individual de um sócio, sem orçamento
- **EMPRESA:** Projeto da empresa, tipicamente criado a partir de orçamento aprovado

**Owner:**
- Todo projeto tem owner (BA ou RR)
- Projetos PESSOAL: owner é automaticamente o sócio do tipo (PESSOAL_BA → owner=BA)
- Projetos EMPRESA: owner define quem gere o projeto

**Cliente:**
- TODO projeto tem cliente (obrigatório)
- Mesmo projetos PESSOAL têm cliente associado

---

### 3.2 Estados e Transições
```
ATIVO ──data_fim passa──> FINALIZADO ──marcar pago──> PAGO ──anular──> ANULADO
  ↑         (automático)        │         (manual)      │               │
  └───────────────────────── pode voltar atrás ────────────────────────┘
```

**ATIVO:**
- Projeto em curso, trabalho a decorrer
- Estado inicial ao criar projeto
- Pode ter `data_fim` definida ou não

**FINALIZADO:**
- Trabalho concluído, aguarda pagamento
- **Transição automática:** quando `data_fim` passa (< hoje)
- Pode editar e voltar para ATIVO se necessário
- Prémios aparecem em "Prémios Não Faturados" nos Saldos Pessoais

**PAGO:**
- Cliente pagou o projeto
- **Transição manual:** botão "Marcar como Pago"
- Distribui prémios BA/RR aos saldos
- Prémios entram nos Saldos Pessoais (INs)
- Pode voltar para FINALIZADO se marcado por engano

**ANULADO:**
- Projeto cancelado (cliente desistiu, orçamento rejeitado, etc)
- Não conta para saldos
- Pode voltar para ATIVO se reativar projeto

**Nota:** Sistema de receitas será implementado futuramente (ver TODO)

---

### 3.3 Criação de Projetos

**Método 1: A partir de Orçamento (automático)**
- Quando orçamento é aprovado
- Copia dados do orçamento (ver Secção 1.4)
- Estado inicial: ATIVO
- Link bidirecional: `projeto.orcamento_id` ↔ `orcamento.projeto_id`

**Método 2: Manual (sem orçamento)**
- Criar projeto diretamente
- Campos obrigatórios: owner, tipo, cliente, valor
- Prémios BA/RR podem ser 0 (projetos pessoais)
- `orcamento_id = NULL`
- Estado inicial: ATIVO

---

### 3.4 Impacto Financeiro

**Quando marca como PAGO:**

1. **Distribui prémios aos sócios:**
```python
# Prémios entram nos Saldos Pessoais (INs)
if projeto.premio_ba > 0:
    # Saldo BA aumenta
    saldo_ba_ins += projeto.premio_ba

if projeto.premio_rr > 0:
    # Saldo RR aumenta
    saldo_rr_ins += projeto.premio_rr
```

2. **Atualiza estado:**
```python
projeto.estado = 'PAGO'
projeto.data_pagamento = hoje
```

3. **Futuro - Sistema de Receitas (TODO):**
```python
# Quando implementado, criar receita:
# receita = Receita(
#     projeto_id = projeto.id,
#     cliente_id = projeto.cliente_id,
#     valor = projeto.valor,
#     data = hoje
# )
```

**Quando volta a FINALIZADO:**
- Prémios são revertidos dos saldos
- `estado = 'FINALIZADO'`
- `data_pagamento = NULL`
- **Futuro:** Receita marcada como CANCELADA (não apagada)

---

### 3.5 Prémios Não Faturados

**Feature:** Mostrar prémios de projetos FINALIZADOS (mas não pagos) nos Saldos Pessoais

**Interface - Saldos Pessoais:**
```
┌─────────────────────────────────────────────┐
│ BA                                          │
├─────────────────────────────────────────────┤
│ Saldo Atual: €12.120,98                     │
│ Saldo Projetado: €14.120,98 (+€2.000) ⬅ só se houver não faturados
├─────────────────────────────────────────────┤
│ 💰 INs                                      │
│                                             │
│ Projetos pessoais (PAGO)      €10.000,00   │
│ Prémios (PAGO)                 €5.000,00   │
│ 💡 Prémios não faturados       €2.000,00   │ ← Clicável
│                                             │
│ TOTAL INs:                    €17.000,00   │
└─────────────────────────────────────────────┘
```

**Cálculo:**
```python
premios_nao_faturados_ba = sum(
    projeto.premio_ba 
    for projeto in projetos 
    if projeto.estado == 'FINALIZADO' and projeto.premio_ba > 0
)

# Saldo Projetado (só mostrar se houver não faturados)
if premios_nao_faturados_ba > 0:
    saldo_projetado = saldo_atual + premios_nao_faturados_ba
```

**Apresentação:**
- Linha separada após "Prémios" (com ícone 💡)
- Cor laranja claro (#FFE5D0 bg, #CC6600 text)
- Clicável → navega para Projetos filtrados por estado=FINALIZADO
- Tooltip: "Projetos concluídos aguardando pagamento"
- **Saldo Projetado:** só aparece quando há prémios não faturados, ao lado do Saldo Atual

---

### 3.6 Relação com Outras Entidades

**Orçamentos:**
- Projeto pode ter `orcamento_id` (se criado por aprovação)
- Link bidirecional mantido
- Se orçamento anulado → projeto também anula

**Despesas:**
- Despesas podem ter `projeto_id` (opcional)
- Útil para rastrear custos reais vs orçamentados
- **Ao apagar/anular projeto:** aviso se tem despesas associadas
```
  ⚠️ Atenção! Este projeto tem 5 despesas associadas.
  As despesas ficarão sem projeto associado.
  Deseja continuar?
```
- Se confirmar: despesas ficam com `projeto_id = NULL` (órfãs)

**Boletins (linhas):**
- Linhas de boletim podem ter `projeto_id` (opcional)
- Se projeto apagado/anulado → `projeto_id = NULL`
- Sem aviso (impacto menor)

---

### 3.7 Estrutura de Dados
```
projetos
├─ owner: 'BA' | 'RR'                          ← NOVO
├─ orcamento_id: FK → orcamentos (nullable)
├─ cliente_id: FK → clientes
├─ codigo: VARCHAR (ex: #P0001)
├─ tipo: 'PESSOAL_BA' | 'PESSOAL_RR' | 'EMPRESA'
├─ estado: 'ATIVO' | 'FINALIZADO' | 'PAGO' | 'ANULADO'  ← ATUALIZADO
├─ data_inicio: DATE
├─ data_fim: DATE (nullable)
├─ valor: DECIMAL
│
├─ Prémios:
│  ├─ premio_ba: DECIMAL                      ← De orçamento ou manual
│  └─ premio_rr: DECIMAL                      ← De orçamento ou manual
│
├─ Rastreabilidade (de orçamento):            ← NOVO
│  ├─ valor_empresa: DECIMAL
│  ├─ valor_fornecedores: DECIMAL
│  ├─ valor_equipamento: DECIMAL
│  └─ valor_despesas: DECIMAL
│
└─ Pagamento:
   └─ data_pagamento: DATE (nullable)
```

---

### 3.8 Casos de Uso

**UC1: Criar Projeto Manual (PESSOAL)**
1. Selecionar tipo: PESSOAL_BA
2. Owner = BA (automático)
3. Selecionar cliente
4. Definir valor
5. Prémio BA = valor total (automático)
6. Prémio RR = 0
7. Estado inicial: ATIVO

**UC2: Criar Projeto via Orçamento**
1. Orçamento aprovado
2. Sistema cria projeto automaticamente
3. Copia todos os dados (ver Secção 1.4)
4. Estado inicial: ATIVO
5. Link bidirecional criado

**UC3: Finalizar Projeto (Automático)**
1. Projeto tem `data_fim = 2025-11-10`
2. Hoje = 2025-11-15
3. Sistema detecta data_fim < hoje
4. Muda estado para FINALIZADO
5. Prémios aparecem em "Não Faturados"

**UC4: Marcar como Pago**
1. Validar projeto está FINALIZADO
2. Distribuir prémios aos saldos
3. Marcar estado = PAGO
4. Registar data_pagamento

**UC5: Apagar Projeto com Despesas**
1. Tentar apagar projeto #P0050
2. Sistema deteta 5 despesas associadas
3. Mostrar aviso: "Atenção! Este projeto tem 5 despesas associadas..."
4. Se confirmar: despesas ficam com projeto_id = NULL
5. Projeto é apagado

---

### 3.9 Validações

**Antes de apagar/anular:**
- Verificar se tem despesas associadas → mostrar aviso
- Verificar se tem boletim linhas associadas (informativo apenas)

**Campos obrigatórios:**
- owner (BA ou RR)
- tipo
- cliente_id
- valor > 0

**Regras de estado:**
- FINALIZADO: só se `data_fim` preenchida e passou
- PAGO: só se estado anterior era FINALIZADO
- Pode voltar atrás em qualquer transição (corrigir enganos)

---

## 4. CÁLCULOS FINANCEIROS

### 4.1 Saldos Pessoais (CORE)

Sistema de divisão 50/50 entre os sócios BA e RR.

**Princípio:** Cada sócio tem seu próprio saldo baseado em:
- **INs:** O que entra (projetos pessoais + prémios de projetos EMPRESA)
- **OUTs:** O que sai (despesas fixas ÷ 2 + boletins + despesas pessoais)

---

### 4.2 Fórmula - Sócio BA
```python
# ────────────────────────────────────────────────────────
# INs (Entradas)
# ────────────────────────────────────────────────────────

# Projetos Pessoais (tipo PESSOAL_BA, estado PAGO)
projetos_pessoais_ba = sum(
    projeto.valor 
    for projeto in projetos 
    if projeto.tipo == 'PESSOAL_BA' 
    and projeto.estado == 'PAGO'
)

# Prémios de Projetos EMPRESA (estado PAGO)
premios_ba = sum(
    projeto.premio_ba 
    for projeto in projetos 
    if projeto.tipo == 'EMPRESA' 
    and projeto.estado == 'PAGO'
    and projeto.premio_ba > 0
)

# Prémios Não Faturados (estado FINALIZADO) - NÃO CONTA NO SALDO ATUAL
premios_nao_faturados_ba = sum(
    projeto.premio_ba 
    for projeto in projetos 
    if projeto.estado == 'FINALIZADO'
    and projeto.premio_ba > 0
)

TOTAL_INs_BA = projetos_pessoais_ba + premios_ba


# ────────────────────────────────────────────────────────
# OUTs (Saídas)
# ────────────────────────────────────────────────────────

# Despesas Fixas Mensais (divididas 50/50, estado PAGO)
despesas_fixas_ba = sum(
    despesa.valor_c_iva / 2
    for despesa in despesas
    if despesa.tipo == 'FIXA_MENSAL'
    and despesa.estado == 'PAGO'
)

# Boletins do Sócio BA (estado PAGO)
boletins_ba = sum(
    boletim.total
    for boletim in boletins
    if boletim.socio == 'BA'
    and boletim.estado == 'PAGO'
)

# Despesas Pessoais BA (estado PAGO)
despesas_pessoais_ba = sum(
    despesa.valor_c_iva
    for despesa in despesas
    if despesa.tipo == 'PESSOAL_BA'
    and despesa.estado == 'PAGO'
)

TOTAL_OUTs_BA = despesas_fixas_ba + boletins_ba + despesas_pessoais_ba


# ────────────────────────────────────────────────────────
# Saldos
# ────────────────────────────────────────────────────────

SALDO_ATUAL_BA = TOTAL_INs_BA - TOTAL_OUTs_BA

# Saldo Projetado (só mostrar se houver prémios não faturados)
if premios_nao_faturados_ba > 0:
    SALDO_PROJETADO_BA = SALDO_ATUAL_BA + premios_nao_faturados_ba
```

---

### 4.3 Fórmula - Sócio RR
```python
# Idêntico ao BA, substituindo:
# - PESSOAL_BA → PESSOAL_RR
# - premio_ba → premio_rr
# - socio == 'BA' → socio == 'RR'
# - tipo == 'PESSOAL_BA' → tipo == 'PESSOAL_RR'

TOTAL_INs_RR = projetos_pessoais_rr + premios_rr
TOTAL_OUTs_RR = despesas_fixas_rr + boletins_rr + despesas_pessoais_rr
SALDO_ATUAL_RR = TOTAL_INs_RR - TOTAL_OUTs_RR

if premios_nao_faturados_rr > 0:
    SALDO_PROJETADO_RR = SALDO_ATUAL_RR + premios_nao_faturados_rr
```

---

### 4.4 Regras Importantes

**Estados que contam:**
- ✅ **PAGO:** Despesas, Boletins, Projetos
- ❌ **PENDENTE:** Não conta para saldos
- ❌ **FINALIZADO:** Não conta (exceto para Prémios Não Faturados)
- ❌ **ANULADO:** Não conta

**Divisão 50/50:**
- Apenas despesas **FIXA_MENSAL** são divididas
- Despesas PESSOAL_BA/PESSOAL_RR são 100% do respetivo sócio
- Despesas EQUIPAMENTO e PROJETO também divididas 50/50

**Tipos de Despesa (atualização):**
```python
# Despesas divididas 50/50:
- FIXA_MENSAL     # Ex: software, servidor, escritório
- EQUIPAMENTO     # Equipamento da empresa
- PROJETO         # Custos de projetos EMPRESA

# Despesas individuais (100%):
- PESSOAL_BA      # Só desconta de BA
- PESSOAL_RR      # Só desconta de RR
```

---

### 4.5 Cálculo de Totais - Orçamentos

**Total Lado Cliente:**
```python
total_cliente = sum(
    item.total 
    for secao in orcamento.secoes 
    for item in secao.itens
)

# Onde item.total = item.quantidade × item.preco_unitario
```

**Total Lado Empresa:**
```python
total_empresa = sum(
    reparticao.valor 
    for reparticao in orcamento.reparticoes
)
```

**Validação:**
```python
if total_cliente != total_empresa:
    diferenca = abs(total_cliente - total_empresa)
    raise ValidationError(f"Totais não coincidem (diferença: €{diferenca:.2f})")
```

---

### 4.6 Cálculo de Totais - Boletins

**Total por Linha:**
```python
# Buscar valores de referência do ano
valores_ano = get_valores_referencia(boletim.ano)

total_linha = (
    (linha.dias_nacional × valores_ano.valor_dia_nacional) +
    (linha.dias_estrangeiro × valores_ano.valor_dia_estrangeiro) +
    (linha.kms × valores_ano.valor_km)
)
```

**Total do Boletim:**
```python
total_boletim = sum(linha.total for linha in boletim.linhas)
```

**Valores de Referência (defaults):**
- Dia Nacional: €72.65
- Dia Estrangeiro: €167.07
- Km: €0.40

**Fallback:** Se ano não tem valores definidos, usa ano anterior ou defaults.

---

### 4.7 Interface - Apresentação de Saldos

**Screen Saldos Pessoais:**
```
┌─────────────────────────────────────────────────────────────┐
│ BA                                    RR                    │
├─────────────────────────────────────────────────────────────┤
│ Saldo Atual: €12.120,98              Saldo Atual: €8.450,33 │
│ Saldo Projetado: €14.120,98          (sem não faturados)    │
│ (+€2.000)                                                   │
├─────────────────────────────────────────────────────────────┤
│ 💰 INs                               💰 INs                 │
│                                                             │
│ Projetos pessoais     €10.000,00     Projetos pessoais  €0 │
│ Prémios               €5.000,00      Prémios      €7.500,00│
│ 💡 Prémios não fat.   €2.000,00                             │
│                                                             │
│ TOTAL INs:           €17.000,00      TOTAL INs:  €7.500,00 │
│                                                             │
│ 📤 OUTs                              📤 OUTs                │
│                                                             │
│ Despesas fixas (÷2)  €12.249,70      Despesas fixas  €12.249│
│ Boletins pendentes   €4.201,80       Boletins pend. €3.446 │
│ Boletins pagos       €1.013,56       Boletins pagos €1.203 │
│ Despesas pessoais    €0,00           Despesas pess. €1.064 │
│                                                             │
│ TOTAL OUTs:          €17.465,06      TOTAL OUTs:  €17.963  │
└─────────────────────────────────────────────────────────────┘
```

**Cores:**
- INs: Verde (#E8F5E0 bg, #4A7028 text)
- OUTs: Laranja (#FFE5D0 bg, #8B4513 text)
- Prémios Não Faturados: Laranja claro (#FFF4E6 bg, #CC6600 text)
- Saldo Positivo: Verde
- Saldo Negativo: Vermelho

**Interatividade:**
- Cada linha clicável → navega para screen respetivo com filtros aplicados
- "Prémios não faturados" → Projetos filtrados por FINALIZADO

---