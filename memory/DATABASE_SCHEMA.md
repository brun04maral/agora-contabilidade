# 🗄️ Database Schema - Agora Contabilidade

**Última atualização:** 2025-11-17 09:10 WET  
**Branch:** claude/sync-latest-updates-012SDyaYGLD1zvqARajAPDPC

Visão geral da estrutura da base de dados SQLite do sistema Agora Contabilidade.

---

## 📊 Diagrama de Entidades (Resumo)

┌─────────────┐
│   Socio     │ (2 fixos: BA, RR)
└──────┬──────┘
       │
       ├─────┬──────────────┬──────────────┬──────────────┐
       │     │              │              │              │
       ▼     ▼              ▼              ▼              ▼
 ┌─────────┐ ┌──────────┐ ┌─────────┐ ┌──────────┐ ┌──────────┐
 │ Projeto │ │ Despesa  │ │ Boletim │ │Orcamento │ │Equipment │
 └────┬────┘ └────┬─────┘ └────┬────┘ └────┬─────┘ └──────────┘
      │           │             │           │
      │           │             │           │
      ▼           ▼             ▼           ▼
 ┌─────────┐ ┌──────────────────┐ ┌──────────────┐ ┌──────────┐
 │ Cliente │ │DespesaTemplate   │ │BoletimLinhas │ │OrcItens  │
 └─────────┘ │(Recorrentes)     │ │(Deslocações) │ │OrcRepat  │
             └──────────────────┘ └──────────────┘ └──────────┘

 ┌────────────┐  ┌─────────────────────┐  ┌───────────────────┐
 │Fornecedor  │  │ValorRefAnual        │  │(BoletimTemplates) │
 │            │  │(Config por Ano)     │  │    [LEGACY]       │
 └────────────┘  └─────────────────────┘  └───────────────────┘

---

## 📋 Tabelas Implementadas

### 🔹 Core - Entidades Fundamentais

#### `socios` - Sócios da Empresa

**Campos principais:**
- `id` - PK
- `codigo` - "BA" ou "RR" (UNIQUE)
- `nome` - Nome completo
- `nif` - Número fiscal
- `iban` - Conta bancária
- `percentagem` - % da sociedade (50.0)

**Constantes:**
Socio.BRUNO = "BA"
Socio.RAFAEL = "RR"

**Relações:**
- `projetos` → Lista de projetos (one-to-many)
- `despesas` → Lista de despesas (one-to-many)
- `boletins` → Lista de boletins (one-to-many)

---

#### `clientes` - Clientes da Agora Media

**Campos principais:**
- `id` - PK
- `numero` - VARCHAR(20) UNIQUE (#C0001, #C0002, etc.)
- `nome` - **VARCHAR(120)** - Nome curto para listagens
- `nome_formal` - **VARCHAR(255)** - Nome completo/legal para documentos
- `nif` - VARCHAR(20) (nullable)
- `pais` - VARCHAR(50) DEFAULT "Portugal"
- `morada` - TEXT (nullable)
- `contacto` - VARCHAR(50) (nullable)
- `email` - VARCHAR(100) (nullable)
- `angariacao` - TEXT (nullable)
- `nota` - TEXT (nullable)
- `created_at` / `updated_at` - TIMESTAMP

**Campos de Nome (desde Migration 021):**
- **nome:** Nome curto para listagens/tabelas/dropdowns
- **nome_formal:** Nome legal para PDFs/contratos/documentos oficiais
- Se `nome_formal` vazio → usa automaticamente `nome`
- Ambos pesquisáveis (case-insensitive)

**Exemplos:**
- nome: "Farmácia do Povo"
- nome_formal: "Farmácia Popular do Centro, Lda."

**Relações:**
- `projetos` → Lista de projetos (one-to-many)
- `orcamentos` → Lista de orçamentos (one-to-many)

---

#### `fornecedores` - Fornecedores/Credores

**Campos principais:**
- `id` - PK
- `nome` - VARCHAR(200)
- `nif` - VARCHAR(20) (nullable)
- `email` - VARCHAR(100) (nullable)
- `telefone` - VARCHAR(50) (nullable)
- `morada` - TEXT (nullable)
- `website` - VARCHAR(200) (nullable) - Desde Migration 012
- `ativo` - BOOLEAN
- `estatuto` - ENUM

**Enums:**
EstatutoFornecedor:
  - CREDOR
  - FORNECEDOR

**Relações:**
- `despesas` → Via credor_id (one-to-many)

---

### 🔹 Projetos e Orçamentos

#### `projetos` - Projetos de Clientes

**Campos principais:**
- `id` - PK
- `codigo` - VARCHAR(20) UNIQUE (#P0001, etc.)
- `nome` - VARCHAR(200)
- `owner` - VARCHAR(2) NOT NULL - Desde Migration 020
- `cliente_id` - FK → clientes
- `socio_responsavel` - FK → socios
- `tipo` - ENUM
- `estado` - ENUM - Atualizado Migration 020
- `data_inicio` / `data_fim` - DATE
- `data_pagamento` - DATE (nullable) - Desde Migration 020
- `valor_frontend` / `valor_backend` / `valor_total` - DECIMAL(10,2)
- `premio_bruno` / `premio_rafael` - DECIMAL(10,2)
- `valor_pago` - DECIMAL(10,2)

**Rastreabilidade Financeira (desde Migration 020):**
- `valor_empresa` - DECIMAL(10,2) - Parcela empresa
- `valor_fornecedores` - DECIMAL(10,2) - Pago a fornecedores
- `valor_equipamento` - DECIMAL(10,2) - Rendimento equipamento
- `valor_despesas` - DECIMAL(10,2) - Despesas do projeto

**Enums:**
TipoProjeto:
  - FRONTEND
  - BACKEND
  - FULLSTACK

EstadoProjeto:
  - ATIVO       # Em curso
  - FINALIZADO  # Concluído, aguarda pagamento
  - PAGO        # Cliente pagou
  - ANULADO     # Cancelado

**Regras:**
- `valor_total` = `valor_frontend` + `valor_backend`
- Transição ATIVO → FINALIZADO: automática quando `data_fim < hoje`
- Transição FINALIZADO → PAGO: manual (distribui prémios)

**Relações:**
- `cliente` → Cliente (many-to-one)
- `socio` → Socio (many-to-one)
- `despesas` → Lista despesas (one-to-many via projeto_id)
- `orcamento` → Orçamento origem (one-to-one, nullable)

---

#### `orcamentos` - Orçamentos para Clientes

**Campos principais:**
- `id` - PK
- `codigo` - VARCHAR(20) UNIQUE (#O000001, etc.)
- `owner` - VARCHAR(2) NOT NULL - Desde Migration 022
- `cliente_id` - INTEGER NOT NULL (FK)
- `status` - VARCHAR(20)
- `data_criacao` - DATE
- `data_evento` - TEXT (período formatado)
- `local_evento` - TEXT
- `valor_total` - DECIMAL(10,2)
- `created_at` / `updated_at` - TIMESTAMP

**Enums:**
StatusOrcamento:
  - rascunho  # Editável, sem validação
  - aprovado  # Validado (totais coincidem), readonly
  - rejeitado # Anulado

**Regras:**
- Ao aprovar: totais CLIENTE = EMPRESA (validação obrigatória)
- Aprovação cria projeto automaticamente

**Relações:**
- `cliente` → Cliente (many-to-one)
- `itens` → orcamento_itens (one-to-many, CASCADE DELETE)
- `reparticoes` → orcamento_reparticoes (one-to-many, CASCADE DELETE)

---

#### `orcamento_itens` - Items do Lado CLIENTE (Migration 022-023)

**Estrutura:** Sistema tipo-específico com campos condicionais

**Campos comuns:**
- `id` - PK
- `orcamento_id` - INTEGER NOT NULL (FK CASCADE DELETE)
- `secao_id` - INTEGER NOT NULL (FK CASCADE DELETE)
- `tipo` - VARCHAR(20) NOT NULL
- `descricao` - TEXT NOT NULL
- `total` - DECIMAL(10,2) NOT NULL
- `ordem` - INTEGER DEFAULT 0

**Campos específicos por tipo:**

**SERVICO / EQUIPAMENTO:**
- `quantidade` - INTEGER (nullable)
- `dias` - INTEGER (nullable)
- `preco_unitario` - DECIMAL(10,2) (nullable)
- `desconto` - DECIMAL(5,2) (nullable, percentagem 0-100)
- `equipamento_id` - INTEGER FK (nullable)
- **Cálculo:** (qtd × dias × preço) × (1 - desconto/100)

**TRANSPORTE:**
- `kms` - DECIMAL(10,2) (nullable)
- `valor_por_km` - DECIMAL(10,2) (nullable)
- **Cálculo:** kms × valor_km

**REFEICAO:**
- `num_refeicoes` - INTEGER (nullable)
- `valor_por_refeicao` - DECIMAL(10,2) (nullable)
- **Cálculo:** num × valor

**OUTRO:**
- `valor_fixo` - DECIMAL(10,2) (nullable)
- **Cálculo:** valor_fixo

**Tipos suportados:**
- `servico` - Serviço manual
- `equipamento` - Equipamento
- `transporte` - Despesa transporte
- `refeicao` - Despesa refeição
- `outro` - Valor fixo

**Índices:**
CREATE INDEX idx_orcamento_itens_orcamento ON orcamento_itens(orcamento_id);
CREATE INDEX idx_orcamento_itens_tipo ON orcamento_itens(tipo);

---

#### `orcamento_reparticoes` - Repartições Lado EMPRESA (Migration 022-023)

**Estrutura:** Sistema de beneficiários com tipos múltiplos

**Campos comuns:**
- `id` - PK
- `orcamento_id` - INTEGER NOT NULL (FK CASCADE DELETE)
- `tipo` - VARCHAR(20) NOT NULL
- `beneficiario` - VARCHAR(50) NOT NULL
- `descricao` - TEXT
- `valor` - DECIMAL(10,2) NOT NULL
- `ordem` - INTEGER DEFAULT 0

**Beneficiários suportados:**
- `BA` - Sócio Bruno Amaral
- `RR` - Sócio Rafael Rodrigues
- `AGORA` - Empresa
- `FREELANCER_[id]` - Freelancer externo (futura Migration 025)
- `FORNECEDOR_[id]` - Fornecedor externo (futura Migration 025)

**Campos específicos por tipo:**

**SERVICO / EQUIPAMENTO:**
- `quantidade`, `dias`, `valor_unitario` - INTEGER/DECIMAL (nullable)
- `equipamento_id` - FK (nullable)
- `fornecedor_id` - FK (nullable, desde Migration 020)

**COMISSAO:**
- `percentagem` - DECIMAL(6,3) (3 decimais, ex: 5.125%)
- `base_calculo` - DECIMAL(10,2)
- **Cálculo:** base × (percentagem / 100)

**DESPESA (espelhadas do CLIENTE):**
- `item_cliente_id` - INTEGER (FK CASCADE DELETE)
- `kms`, `valor_por_km` - DECIMAL (nullable)
- `num_refeicoes`, `valor_por_refeicao` - INTEGER/DECIMAL (nullable)
- `valor_fixo` - DECIMAL (nullable)

**Tipos:**
- `servico` - Serviço com beneficiário
- `equipamento` - Equipamento com beneficiário
- `despesa` - Despesa espelhada (readonly)
- `comissao` - Comissão (venda/empresa)

**Índices:**
CREATE INDEX idx_orcamento_reparticoes_orcamento ON orcamento_reparticoes(orcamento_id);
CREATE INDEX idx_orcamento_reparticoes_beneficiario ON orcamento_reparticoes(beneficiario);
CREATE INDEX idx_orcamento_reparticoes_item_cliente ON orcamento_reparticoes(item_cliente_id);

---

### 🔹 Despesas

#### `despesas` - Despesas da Empresa

**Campos principais:**
- `id` - PK
- `numero` - VARCHAR(20) UNIQUE (#D000001, etc.)
- `tipo` - ENUM
- `credor_id` - FK → fornecedores (nullable)
- `projeto_id` - FK → projetos (nullable)
- `descricao` - TEXT
- `valor_sem_iva` - DECIMAL(10,2)
- `valor_com_iva` - DECIMAL(10,2)
- `data` - DATE
- `estado` - ENUM
- `data_pagamento` - DATE (nullable)
- `nota` - TEXT (nullable)
- `despesa_template_id` - FK → despesa_templates (nullable)

**Enums:**
TipoDespesa:
  - FIXA_MENSAL     # Fixas mensais (divididas 50/50)
  - PESSOAL_BRUNO   # Despesas pessoais BA (100% BA)
  - PESSOAL_RAFAEL  # Despesas pessoais RR (100% RR)
  - EQUIPAMENTO     # Equipamento empresa (50/50)
  - PROJETO         # Despesas projeto (50/50)

EstadoDespesa:
  - PENDENTE  # Por pagar
  - VENCIDO   # Atrasada
  - PAGO      # Paga

**Regras de cálculo saldos:**
- FIXA_MENSAL, EQUIPAMENTO, PROJETO → cada sócio paga 50%
- PESSOAL_BA → 100% Bruno
- PESSOAL_RAFAEL → 100% Rafael

**Indicador visual:**
- Tipo mostra "*" quando gerada de template (ex: "Fixa Mensal*")

**Relações:**
- `credor` → Fornecedor (many-to-one)
- `projeto` → Projeto (many-to-one)
- `template` → DespesaTemplate origem (many-to-one)

---

#### `despesa_templates` - Templates Recorrentes (Migration 014)

**Descrição:** Templates para geração automática de despesas fixas mensais. **NÃO são despesas reais.**

**Campos principais:**
- `id` - PK
- `numero` - VARCHAR(20) UNIQUE (#TD000001, etc.)
- `tipo` - ENUM (usa TipoDespesa)
- `credor_id` - FK → fornecedores (nullable)
- `projeto_id` - FK → projetos (nullable)
- `descricao` - TEXT
- `valor_sem_iva` - DECIMAL(10,2)
- `valor_com_iva` - DECIMAL(10,2)
- `dia_mes` - INTEGER (1-31)
- `nota` - TEXT (nullable)

**Regras:**
- **NÃO entram em cálculos financeiros**
- Geram despesas via botão "🔁 Gerar Recorrentes"
- Se dia não existe no mês (ex: 31/Feb) → usa último dia
- Despesas geradas mantêm FK para template (rastreabilidade)

**UI:** Screen dedicado (modal 1000x700) via botão "📝 Editar Recorrentes" em Despesas

**Relações:**
- `credor` → Fornecedor (many-to-one)
- `projeto` → Projeto (many-to-one)
- `despesas_geradas` → Despesas (one-to-many)

---

### 🔹 Boletins Itinerário

#### `boletins` - Boletins de Ajudas de Custo (Migrations 016-019)

**Campos principais:**
- `id` - PK
- `numero` - VARCHAR(20) UNIQUE (#B0001, etc.)
- `socio` - ENUM (BRUNO/RAFAEL)
- `mes` - INTEGER (1-12, indexed)
- `ano` - INTEGER (indexed)
- `data_emissao` - DATE (indexed)
- `data_pagamento` - DATE (nullable)
- `estado` - ENUM (indexed)

**Valores de Referência (copiados na criação):**
- `val_dia_nacional` - DECIMAL (ex: 72.65€)
- `val_dia_estrangeiro` - DECIMAL (ex: 167.07€)
- `val_km` - DECIMAL (ex: 0.40€)

**Totais Calculados Automaticamente:**
- `total_ajudas_nacionais` - DECIMAL
- `total_ajudas_estrangeiro` - DECIMAL
- `total_kms` - DECIMAL
- `valor_total` - DECIMAL (soma dos 3)

**Metadata:**
- `nota` - TEXT (nullable)
- `created_at` / `updated_at` - DATETIME

**Enums:**
EstadoBoletim:
  - PENDENTE  # Emitido mas não pago
  - PAGO      # Pago (desconta do saldo do sócio)

**Cálculos:**
total_ajudas_nacionais = sum(linha.dias where tipo=NACIONAL) × val_dia_nacional
total_ajudas_estrangeiro = sum(linha.dias where tipo=ESTRANGEIRO) × val_dia_estrangeiro
total_kms = sum(linha.kms) × val_km
valor_total = total_ajudas_nacionais + total_ajudas_estrangeiro + total_kms

**Regras:**
- Totais recalculados automaticamente ao modificar linhas
- Valores de referência copiados do ano vigente
- **Desconta do saldo quando PAGO**, não quando PENDENTE

**Relações:**
- `linhas` → BoletimLinha (one-to-many, CASCADE DELETE)

**UI:** 
- Lista com coluna "Linhas" (contador)
- Duplo-clique abre editor completo (BoletimForm)

---

#### `boletim_linhas` - Linhas de Deslocação (Migration 017)

**Campos principais:**
- `id` - PK
- `boletim_id` - FK → boletins (CASCADE DELETE, indexed)
- `ordem` - INTEGER (ordenação)
- `projeto_id` - FK → projetos (NULLABLE, SET NULL)
- `servico` - TEXT NOT NULL
- `localidade` - VARCHAR(100)
- `data_inicio` / `data_fim` - DATE
- `hora_inicio` / `hora_fim` - TIME (informativas)
- `tipo` - ENUM (NACIONAL/ESTRANGEIRO)
- `dias` - DECIMAL (inserido manualmente)
- `kms` - INTEGER
- `created_at` / `updated_at` - DATETIME

**Enums:**
TipoDeslocacao:
  - NACIONAL     # Deslocação em Portugal
  - ESTRANGEIRO  # Deslocação fora de Portugal

**Regras:**
- Horas informativas (não usadas em cálculo)
- Dias inseridos manualmente (usuário decide)
- Se `projeto_id` preenchido → `servico` auto-preenche mas é editável
- Trigger recalcula totais do boletim ao modificar

**Relações:**
- `boletim` → Boletim (many-to-one)
- `projeto` → Projeto (many-to-one, nullable, ON DELETE SET NULL)

---

#### `valores_referencia_anual` - Configuração por Ano (Migration 016)

**Campos principais:**
- `id` - PK
- `ano` - INTEGER (unique, indexed)
- `val_dia_nacional` - DECIMAL (default: 72.65)
- `val_dia_estrangeiro` - DECIMAL (default: 167.07)
- `val_km` - DECIMAL (default: 0.40)
- `created_at` / `updated_at` - DATETIME

**Regras:**
- Um registo por ano
- Editável via configurações
- Novos boletins copiam valores do ano atual
- Fallback: usa ano anterior ou defaults

**UI:** Screen dedicado (botão "escondido" em configurações)

---

#### `boletim_templates` - Templates Recorrentes [LEGACY] (Migration 018)

**Status:** ⚠️ **LEGACY** - Tabela existe mas funcionalidade removida da UI (13/11/2025)

**Razão remoção:** Sistema considerado demasiado complexo. Substituído por funcionalidade "Duplicar Boletim".

**Campos (mantidos por compatibilidade):**
- `id`, `numero`, `nome`, `socio`, `dia_mes`, `ativo`
- `created_at` / `updated_at`

**Futuro:** Considerar remover em limpeza de schema (baixa prioridade).

**Ver:** DECISIONS.md, CHANGELOG.md (13/11/2025)

---

### 🔹 Equipamento

#### `equipamento` - Equipamento da Empresa

**Campos principais:**
- `id` - PK
- `nome` - VARCHAR(200)
- `descricao` - TEXT
- `numero_serie` - VARCHAR(100) (nullable)
- `data_aquisicao` - DATE
- `valor_aquisicao` - DECIMAL(10,2)
- `localizacao` - VARCHAR(100) (nullable)
- `rendimento_acumulado` - DECIMAL(10,2) DEFAULT 0 - Desde Migration 020
- `ativo` - BOOLEAN

**Regras:**
- `rendimento_acumulado` incrementa ao aprovar orçamentos com repartição tipo='EQUIPAMENTO'
- Não reverte se orçamento anulado (mantém histórico)

**Exemplos:**
- Câmaras, lentes, tripés
- Computadores, monitores
- Software, licenças

---

## 🔑 Índices e Performance

### Índices Automáticos
- Primary Keys (todas as tabelas)
- Foreign Keys (todas as relações)

### Índices Adicionais Recomendados

-- Projetos
CREATE INDEX idx_projetos_cliente ON projetos(cliente_id);
CREATE INDEX idx_projetos_estado ON projetos(estado);
CREATE INDEX idx_projetos_owner ON projetos(owner);

-- Despesas
CREATE INDEX idx_despesas_tipo ON despesas(tipo);
CREATE INDEX idx_despesas_estado ON despesas(estado);
CREATE INDEX idx_despesas_data ON despesas(data);

-- Boletins
CREATE INDEX idx_boletins_socio_mes_ano ON boletins(socio, mes, ano);
CREATE INDEX idx_boletins_estado ON boletins(estado);

-- Orçamentos
CREATE INDEX idx_orcamentos_cliente ON orcamentos(cliente_id);
CREATE INDEX idx_orcamentos_status ON orcamentos(status);
CREATE INDEX idx_orcamentos_owner ON orcamentos(owner);

---

## 📊 Queries Comuns

### Saldos Pessoais (CORE)

**Receitas por sócio (BA):**
-- Projetos PAGO
SELECT SUM(
  CASE 
    WHEN tipo = 'PESSOAL_BA' THEN valor 
    WHEN tipo = 'EMPRESA' THEN premio_bruno 
  END
) AS total_ba
FROM projetos
WHERE estado = 'PAGO' AND owner = 'BA'

**Despesas por sócio (BA):**
-- Divididas 50/50 + Pessoais
SELECT 
  SUM(CASE WHEN tipo IN ('FIXA_MENSAL', 'EQUIPAMENTO', 'PROJETO') 
      THEN valor_com_iva * 0.5 END) +
  SUM(CASE WHEN tipo = 'PESSOAL_BA' THEN valor_com_iva END)
AS despesas_ba
FROM despesas
WHERE estado = 'PAGO'

**Boletins por sócio:**
SELECT SUM(valor_total) AS boletins_ba
FROM boletins
WHERE socio = 'BA' AND estado = 'PAGO'

### Projetos Ativos
session.query(Projeto).filter(
    Projeto.estado == 'ATIVO'
).order_by(Projeto.data_inicio.desc()).all()

### Despesas Pendentes
session.query(Despesa).filter(
    Despesa.estado == 'PENDENTE'
).order_by(Despesa.data).all()

### Orçamentos por Status
session.query(Orcamento).filter(
    Orcamento.status == 'aprovado'
).all()

---

## 🔄 Histórico de Migrations

**Nota:** Sistema não usa Alembic tracking (tabela `alembic_version` não existe). Migrations aplicadas via scripts Python diretos.

### ✅ Aplicadas

#### Migration 012 - Fornecedor Website (13/11/2025)
- ✅ `fornecedores.website` VARCHAR(200)

---

#### Migrations 013-015 - Sistema Despesas Recorrentes (13/11/2025)
- ✅ 014: Criar tabela `despesa_templates`
- ✅ 015: Remover campos obsoletos de recorrência de `despesas`

**Decisão:** Tabela separada para templates (não campos na tabela despesas).  
**Ver:** DECISIONS.md (Secção "Sistema de Recorrência")

---

#### Migrations 016-019 - Sistema Boletim Itinerário (13-14/11/2025)
- ✅ 016: Criar `valores_referencia_anual` com seed 2025
- ✅ 017: Criar `boletim_linhas`
- ✅ 018: Criar `boletim_templates` (LEGACY desde 13/11)
- ✅ 019: Expandir `boletins` (mes, ano, valores_ref, totais)

---

#### Migration 020 - Orçamentos e Projetos Completo (15/11/2025)
**Status:** ✅ Aplicada manualmente

**Alterações implementadas:**

**Tabela `orcamentos`:**
- ✅ `owner` VARCHAR(2) NOT NULL DEFAULT 'BA'

**Tabela `projetos`:**
- ✅ `owner` VARCHAR(2) NOT NULL
- ✅ Estados atualizados: ATIVO | FINALIZADO | PAGO | ANULADO
- ✅ Rastreabilidade: `valor_empresa`, `valor_fornecedores`, `valor_equipamento`, `valor_despesas`
- ✅ `data_pagamento` DATE

**Tabela `orcamento_reparticoes`:**
- ✅ `tipo` VARCHAR(20) (substituiu `entidade`)
- ✅ FK `fornecedor_id` INTEGER (ON DELETE SET NULL)
- ✅ FK `equipamento_id` INTEGER (ON DELETE SET NULL)

**Tabela `equipamento`:**
- ✅ `rendimento_acumulado` DECIMAL(10,2) DEFAULT 0

**Verificação realizada:** 2025-11-17 via sqlite3 PRAGMA table_info

---

#### Migration 021 - Cliente Nome e Nome Formal (15/11/2025)
- ✅ `clientes.nome` VARCHAR(120) - Nome curto
- ✅ `clientes.nome_formal` VARCHAR(255) - Nome legal
- ✅ Lógica: Se nome_formal vazio → usa nome

---

#### Migrations 022-023 - Orçamentos V2 (16-17/11/2025)
- ✅ 022: Tabelas `orcamento_itens` e `orcamento_reparticoes` com sistema tipo-específico
- ✅ 023: Campos nullable para tipos específicos (fix constraint errors)

**Ver:** ARCHITECTURE.md, BUSINESS_LOGIC.md (Secção 1)

---

#### Migration 024 - Campo projeto_id em Orcamentos (17/11/2025)
**Status:** ✅ Aplicada
**Commit:** 18ee88f

**Alterações:**
- ✅ `orcamentos.projeto_id` INTEGER NULL (FK para projetos.id)
- ✅ Índice `idx_orcamentos_projeto` para performance
- ✅ Relationship bidirecional: `orcamento.projeto` ↔ `projeto.orcamentos`

**Objetivo:**
- Link bidirecional orçamento ↔ projeto
- Prevenir conversão dupla (verificar se `projeto_id` já existe)
- Rastreabilidade completa de conversões
- Histórico de qual projeto foi criado de qual orçamento

**Ficheiros:**
- Migration: `database/migrations/024_add_projeto_id_to_orcamento.py`
- Script: `scripts/run_migration_024.py`
- Modelos: `database/models/orcamento.py:41`, `database/models/projeto.py:71`

**Ver:** memory/CHANGELOG.md (17/11/2025 - Migration 024)

---

#### Migration 025 - Freelancers e Fornecedores (17/11/2025)
**Status:** ✅ Aplicada
**Commit:** 7592a88, 1aa4ee5, 1b6d2e1

**3 Novas Tabelas:**

1. **`freelancers` - Profissionais Externos:**
   - Campos: id, numero (#F0001), nome, nif, email, telefone, iban, morada, especialidade, notas, ativo
   - Índices: ativo, nome
   - Relação: trabalhos → freelancer_trabalhos (one-to-many)

2. **`freelancer_trabalhos` - Histórico de Trabalhos:**
   - Campos: id, freelancer_id (FK CASCADE), orcamento_id (FK SET NULL), projeto_id (FK SET NULL), descricao, valor, data, status (a_pagar/pago/cancelado), data_pagamento, nota
   - Gerados automaticamente ao aprovar orçamentos
   - Índices: freelancer_id, status, data
   - Status workflow: a_pagar → pago → cancelado

3. **`fornecedor_compras` - Histórico de Compras:**
   - Estrutura idêntica a freelancer_trabalhos
   - fornecedor_id (FK CASCADE) em vez de freelancer_id
   - Mesmo status workflow

**Expansão `fornecedores`:**
- ✅ Campos adicionados: `numero` (#FN0001 UNIQUE), `categoria`, `iban`
- ✅ Índice: `idx_fornecedores_categoria`

**Integração `orcamento_reparticoes`:**
- ✅ Campo beneficiario agora suporta: BA, RR, AGORA, FREELANCER_{id}, FORNECEDOR_{id}
- ✅ Validações: verifica existência e status ativo antes de salvar
- ✅ Aprovação cria registos históricos automaticamente

**Ficheiros:**
- Migration: `database/migrations/025_freelancers_fornecedores.py`
- Script: `scripts/run_migration_025.py`
- Modelos: `database/models/freelancer.py`, `freelancer_trabalho.py`, `fornecedor_compra.py`
- Managers: `logic/freelancers.py`, `freelancer_trabalhos.py`, `fornecedor_compras.py`
- UI: Dialogs EMPRESA atualizados (servico, equipamento, comissao)

**Rastreabilidade:**
- Registos criados automaticamente ao aprovar orçamentos
- Links: orcamento_id, projeto_id (SET NULL se apagado)
- Gestão futura: marcar como pago, calcular totais a pagar

**Ver:** memory/CHANGELOG.md (17/11/2025 - Orçamentos V2 Sistema Multi-Entidade Completo)

---

### 📋 Planeadas (Futuro)

#### Migration 026 - Sistema Fiscal - Receitas (PLANEADO)
**Prioridade:** 🟡 Média  
**Status:** 📝 Documentado, aguarda implementação

**Novas tabelas:**

**`freelancers` - Profissionais Externos:**
- Campos: id, numero (#F0001), nome, nif, email, telefone, iban, morada, especialidade, notas, ativo
- Índices: ativo, nome
- Relação: trabalhos → freelancer_trabalhos (one-to-many)

**`freelancer_trabalhos` - Histórico Trabalhos:**
- Campos: id, freelancer_id (FK), orcamento_id (FK), projeto_id (FK), descricao, valor, data, status (a_pagar/pago/cancelado), data_pagamento, nota
- Gerados automaticamente ao aprovar orçamentos
- Índices: freelancer_id, status, data

**`fornecedor_compras` - Histórico Compras:**
- Estrutura idêntica a freelancer_trabalhos
- `fornecedor_id` em vez de `freelancer_id`

**Expansões:**

**`fornecedores` (adicionar campos):**
- `numero` VARCHAR(20) UNIQUE (#FN0001)
- `categoria` VARCHAR(50) (ex: "Aluguer Equipamento")
- `iban` VARCHAR(50)

**`orcamento_reparticoes` (beneficiario):**
- Suporte completo para FREELANCER_[id] e FORNECEDOR_[id]

**Ver:** Secção "FREELANCERS E FORNECEDORES - Spec Detalhada" (fim deste ficheiro)

---

#### Migration 026 - Sistema Fiscal - Receitas (PLANEADO)
**Prioridade:** 🔴 Alta
**Status:** 📝 Documentado em FISCAL.md (39KB), aguarda validação TOC

**Nova tabela:**
receitas (
  id, numero (#R000001), projeto_id, cliente_id,
  fatura_numero, valor_sem_iva, iva_liquidado, valor_c_iva,
  data_fatura, data_recebimento, estado (ATIVO/CANCELADO),
  tipo (PROJETO/OUTRO), metodo_pagamento, referencia, nota
)

**Comportamento:**
- Ao marcar projeto PAGO → criar receita ATIVO automaticamente
- Ao reverter PAGO → FINALIZADO → marcar receita CANCELADO (não apagar)
- Suporta receitas avulsas sem projeto (subsídios, vendas equipamento)

**Decisões pendentes:**
- Receita = valor total projeto? Ou pode ser parcial?
- Múltiplas receitas por projeto? (pagamentos faseados)
- Campos adicionais de IVA?

**Ver:** 
- FISCAL.md (Secção 1.1 - Receitas e Faturação)
- TODO.md (tarefa "💰 Sistema Fiscal Completo")
- BUSINESS_LOGIC.md (Secção 3.4)

---

## 💾 Backup

### Backup Manual
cp agora_media.db agora_media_backup_$(date +%Y%m%d).db

### Backup Automático (futura implementação)
- Backup diário automático
- Rotação de backups (últimos 7 dias)
- Armazenamento cloud (opcional)

---

## 👥 FREELANCERS E FORNECEDORES - Especificação Completa (Migration 025)

**Status:** ✅ Implementado (17/11/2025)

Esta secção documenta em detalhe as tabelas implementadas para gestão de freelancers e fornecedores externos.

### Tabela: freelancers - Profissionais Externos

**Descrição:** Freelancers contratados para projetos específicos (cameramen, editores, designers, motion graphics, locutores, etc).

**Estrutura completa:**
CREATE TABLE freelancers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    numero VARCHAR(20) UNIQUE NOT NULL,
    nome VARCHAR(200) NOT NULL,
    nif VARCHAR(20) NULL,
    email VARCHAR(200) NULL,
    telefone VARCHAR(50) NULL,
    iban VARCHAR(50) NULL,
    morada TEXT NULL,
    especialidade VARCHAR(100) NULL,
    notas TEXT NULL,
    ativo BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_freelancers_ativo ON freelancers(ativo);
CREATE INDEX idx_freelancers_nome ON freelancers(nome);

**Regras de negócio:**
- Número gerado automaticamente (#F0001, #F0002, etc)
- Podem estar inativos (não apagados, mantém histórico)
- IBAN obrigatório para processamento pagamentos

**Relações:**
- `trabalhos` → freelancer_trabalhos (one-to-many)
- `reparticoes` → orcamento_reparticoes (via beneficiario='FREELANCER_[id]')

---

### Tabela: freelancer_trabalhos - Histórico de Trabalhos

**Descrição:** Registo de trabalhos realizados por freelancers. Gerados automaticamente ao aprovar orçamentos.

**Estrutura completa:**
CREATE TABLE freelancer_trabalhos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    freelancer_id INTEGER NOT NULL,
    orcamento_id INTEGER NULL,
    projeto_id INTEGER NULL,
    descricao TEXT NOT NULL,
    valor DECIMAL(10,2) NOT NULL,
    data DATE NOT NULL,
    status VARCHAR(20) NOT NULL,
    data_pagamento DATE NULL,
    nota TEXT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (freelancer_id) REFERENCES freelancers(id) ON DELETE CASCADE,
    FOREIGN KEY (orcamento_id) REFERENCES orcamentos(id) ON DELETE SET NULL,
    FOREIGN KEY (projeto_id) REFERENCES projetos(id) ON DELETE SET NULL
);

CREATE INDEX idx_freelancer_trabalhos_freelancer ON freelancer_trabalhos(freelancer_id);
CREATE INDEX idx_freelancer_trabalhos_status ON freelancer_trabalhos(status);
CREATE INDEX idx_freelancer_trabalhos_data ON freelancer_trabalhos(data);

**Enums:**
StatusTrabalho:
  - a_pagar   # Trabalho concluído, aguarda pagamento
  - pago      # Freelancer já recebeu
  - cancelado # Orçamento anulado ou trabalho cancelado

**Comportamento:**
- Criado automaticamente quando orçamento aprovado tem repartição FREELANCER_[id]
- FK com SET NULL: se orçamento/projeto apagado → mantém registo histórico

**Funcionalidade Rastreabilidade (PLANEADO):**
- ✅ Registos criados automaticamente na aprovação orçamento (já implementado)
- 📝 Visualizados em ficha individual freelancer (a implementar)
  - Screen: FreelancerForm com tabela de trabalhos históricos
  - Colunas: Data | Orçamento | Projeto | Descrição | Valor | Status | Ações
  - Totais: A Pagar | Pago | Total Geral
- 📝 Dashboard mostra totais status='a_pagar' (a implementar)
  - Card: "💰 Freelancers A Pagar: €XXX"
  - Clique: navega para FreelancersScreen com filtro
- 📝 Botão marcar pago (a implementar)
  - Atualiza: status='pago', data_pagamento=hoje
  - Manager: FreelancerTrabalhosManager.marcar_como_pago()
- ⚠️ Histórico permanente: NUNCA apagar registos (manter auditoria contabilística)
  - Status 'cancelado' permite anular sem perder rastreabilidade

**Ver:** BUSINESS_LOGIC.md (Secção 7), ARCHITECTURE.md (Orçamentos V2 - Totais por Beneficiário), TODO.md (Tarefa 7)

---

### Tabela: fornecedor_compras - Histórico de Compras

**Descrição:** Registo de compras/serviços contratados a fornecedores. Gerados ao aprovar orçamentos.

**Estrutura completa:**
CREATE TABLE fornecedor_compras (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fornecedor_id INTEGER NOT NULL,
    orcamento_id INTEGER NULL,
    projeto_id INTEGER NULL,
    descricao TEXT NOT NULL,
    valor DECIMAL(10,2) NOT NULL,
    data DATE NOT NULL,
    status VARCHAR(20) NOT NULL,
    data_pagamento DATE NULL,
    nota TEXT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (fornecedor_id) REFERENCES fornecedores(id) ON DELETE CASCADE,
    FOREIGN KEY (orcamento_id) REFERENCES orcamentos(id) ON DELETE SET NULL,
    FOREIGN KEY (projeto_id) REFERENCES projetos(id) ON DELETE SET NULL
);

CREATE INDEX idx_fornecedor_compras_fornecedor ON fornecedor_compras(fornecedor_id);
CREATE INDEX idx_fornecedor_compras_status ON fornecedor_compras(status);
CREATE INDEX idx_fornecedor_compras_data ON fornecedor_compras(data);

**Enums:**
StatusCompra:
  - a_pagar   # Serviço contratado, aguarda pagamento
  - pago      # Fornecedor já recebeu
  - cancelado # Orçamento anulado ou compra cancelada

**Funcionalidade Rastreabilidade (PLANEADO):**
- ✅ Registos criados automaticamente na aprovação orçamento (já implementado)
- 📝 Visualizados em ficha individual fornecedor (a implementar)
  - Screen: FornecedorForm expandido com tabela de compras históricas
  - Colunas: Data | Orçamento | Projeto | Descrição | Valor | Status | Ações
  - Totais: A Pagar | Pago | Total Geral
- 📝 Dashboard mostra totais status='a_pagar' (a implementar)
  - Card: "🏢 Fornecedores A Pagar: €XXX"
  - Clique: navega para FornecedoresScreen com filtro
- 📝 Botão marcar pago (a implementar)
  - Atualiza: status='pago', data_pagamento=hoje
  - Manager: FornecedorComprasManager.marcar_como_pago()
- ⚠️ Histórico permanente: NUNCA apagar registos (manter auditoria contabilística)
  - Status 'cancelado' permite anular sem perder rastreabilidade

**Ver:** BUSINESS_LOGIC.md (Secção 7), ARCHITECTURE.md (Orçamentos V2 - Totais por Beneficiário), TODO.md (Tarefa 7)

---

### Expansão: fornecedores (ATUALIZAÇÃO em Migration 025)

**Campos a adicionar:**
ALTER TABLE fornecedores ADD COLUMN numero VARCHAR(20) UNIQUE;
ALTER TABLE fornecedores ADD COLUMN categoria VARCHAR(50) NULL;
ALTER TABLE fornecedores ADD COLUMN iban VARCHAR(50) NULL;

CREATE INDEX idx_fornecedores_categoria ON fornecedores(categoria);

**Campos existentes mantidos:**
- id, nome, nif, email, telefone, morada, website, ativo, estatuto

**Relações novas:**
- `compras` → fornecedor_compras (one-to-many)
- `reparticoes` → orcamento_reparticoes (via fornecedor_id FK e beneficiario)

---

### Integração: orcamento_reparticoes - Validações Expandidas

**Campo beneficiario - Validações completas:**

**Formatos suportados:**
- `BA` / `RR` / `AGORA` → Sempre válidos
- `FREELANCER_[id]` → Verificar se existe e está ativo
- `FORNECEDOR_[id]` → Verificar se existe e está ativo

**Lógica de validação (pseudo-código):**
def validar_beneficiario(beneficiario):
    if beneficiario in ['BA', 'RR', 'AGORA']:
        return True
    
    if beneficiario.startswith('FREELANCER_'):
        id = int(beneficiario.split('_')[1])
        freelancer = FreelancerManager.obter(id)
        if not freelancer:
            raise ValueError(f"Freelancer #{id} não existe")
        if not freelancer.ativo:
            avisar(f"Freelancer '{freelancer.nome}' está inativo")
        return True
    
    if beneficiario.startswith('FORNECEDOR_'):
        id = int(beneficiario.split('_')[1])
        fornecedor = FornecedorManager.obter(id)
        if not fornecedor:
            raise ValueError(f"Fornecedor #{id} não existe")
        if not fornecedor.ativo:
            avisar(f"Fornecedor '{fornecedor.nome}' está inativo")
        return True
    
    raise ValueError(f"Formato inválido: {beneficiario}")

**Criação de registos ao aprovar orçamento:**
def aprovar_orcamento(orcamento_id):
    # ... validações totais ...
    
    for reparticao in reparticoes:
        if reparticao.beneficiario.startswith('FREELANCER_'):
            FreelancerTrabalhoManager.criar(
                freelancer_id=extract_id(reparticao.beneficiario),
                orcamento_id=orcamento_id,
                descricao=reparticao.descricao,
                valor=reparticao.valor,
                status='a_pagar'
            )
        
        elif reparticao.beneficiario.startswith('FORNECEDOR_'):
            FornecedorCompraManager.criar(
                fornecedor_id=extract_id(reparticao.beneficiario),
                orcamento_id=orcamento_id,
                descricao=reparticao.descricao,
                valor=reparticao.valor,
                status='a_pagar'
            )

---

## 🔗 Referências Cruzadas

- **BUSINESS_LOGIC.md** - Lógica de negócio detalhada (33KB)
- **ARCHITECTURE.md** - Arquitetura e fluxos (15KB)
- **DECISIONS.md** - Decisões técnicas e trade-offs (30KB)
- **FISCAL.md** - Sistema fiscal (39KB, 9 secções)
- **TODO.md** - Tarefas priorizadas (34KB)
- **CHANGELOG.md** - Histórico completo (53KB)

---

**Mantido por:** Equipa Agora  
**Última atualização:** 2025-11-17 09:10 WET
