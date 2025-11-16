# 🗄️ Database Schema - Agora Contabilidade

Visão geral da estrutura da base de dados SQLite.

---

## 📊 Diagrama de Entidades (Resumo)

```
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
 │ Cliente │ │DespesaTemplate   │ │BoletimLinhas │ │OrcLinhas │
 └─────────┘ │(Recorrentes)     │ │(Deslocações) │ └──────────┘
             └──────────────────┘ └──────────────┘

 ┌────────────┐  ┌─────────────────────┐  ┌───────────────────┐
 │Fornecedor  │  │BoletimTemplates     │  │ValorRefAnual      │
 │            │  │(Geração Recorrente) │  │(Config por Ano)   │
 └────────────┘  └─────────────────────┘  └───────────────────┘
```

---

---

## 🆕 ORÇAMENTOS V2 - Modelo de Dados Completo (Migration 022)

### Tabela: orcamentos

**Campos principais:**
- `id` - INTEGER PRIMARY KEY
- `codigo` - VARCHAR(20) UNIQUE NOT NULL (ex: #O000001)
- `owner` - VARCHAR(2) NOT NULL ('BA' ou 'RR')
- `cliente_id` - INTEGER NOT NULL (FK para clientes)
- `status` - VARCHAR(20) ('rascunho', 'aprovado', 'rejeitado')
- `data_criacao` - DATE
- `data_evento` - TEXT (texto formatado do período)
- `local_evento` - TEXT
- `valor_total` - DECIMAL(10,2)
- `created_at` / `updated_at` - TIMESTAMP

### Tabela: orcamento_itens (LADO CLIENTE)

**Campos comuns a todos os tipos:**
- `id` - INTEGER PRIMARY KEY
- `orcamento_id` - INTEGER NOT NULL (FK CASCADE DELETE)
- `secao_id` - INTEGER NOT NULL (FK CASCADE DELETE)
- `tipo` - VARCHAR(20) NOT NULL ('servico', 'equipamento', 'transporte', 'refeicao', 'outro')
- `descricao` - TEXT NOT NULL
- `total` - DECIMAL(10,2) NOT NULL
- `ordem` - INTEGER DEFAULT 0

**Para tipo 'servico' e 'equipamento':**
- `quantidade` - INTEGER
- `dias` - INTEGER
- `preco_unitario` - DECIMAL(10,2)
- `desconto` - DECIMAL(5,2) DEFAULT 0 (percentagem)
- `equipamento_id` - INTEGER (FK opcional)

**Para tipo 'transporte':**
- `kms` - DECIMAL(10,2)
- `valor_por_km` - DECIMAL(10,2)

**Para tipo 'refeicao':**
- `num_refeicoes` - INTEGER
- `valor_por_refeicao` - DECIMAL(10,2)

**Para tipo 'outro':**
- `valor_fixo` - DECIMAL(10,2)

### Tabela: orcamento_reparticoes (LADO EMPRESA)

**Campos comuns a todos os tipos:**
- `id` - INTEGER PRIMARY KEY
- `orcamento_id` - INTEGER NOT NULL (FK CASCADE DELETE)
- `tipo` - VARCHAR(20) NOT NULL ('servico', 'equipamento', 'despesa', 'comissao')
- `beneficiario` - VARCHAR(50) NOT NULL ('BA', 'RR', 'AGORA', 'FREELANCER_[id]', 'FORNECEDOR_[id]')
- `descricao` - TEXT
- `valor` - DECIMAL(10,2) NOT NULL
- `ordem` - INTEGER DEFAULT 0

**Para tipo 'servico' e 'equipamento':**
- `quantidade` - INTEGER
- `dias` - INTEGER
- `valor_unitario` - DECIMAL(10,2)
- `equipamento_id` - INTEGER (FK opcional)
- `fornecedor_id` - INTEGER (FK opcional)

**Para tipo 'comissao':**
- `percentagem` - DECIMAL(6,3) (3 casas decimais, ex: 5.125%)
- `base_calculo` - DECIMAL(10,2)

**Para tipo 'despesa' (espelhadas do CLIENTE):**
- `item_cliente_id` - INTEGER (FK CASCADE DELETE)
- `kms` - DECIMAL(10,2)
- `valor_por_km` - DECIMAL(10,2)
- `num_refeicoes` - INTEGER
- `valor_por_refeicao` - DECIMAL(10,2)
- `valor_fixo` - DECIMAL(10,2)

### Enums e Valores Permitidos

**orcamento_itens.tipo:**
- `servico` - Serviço manual
- `equipamento` - Equipamento
- `transporte` - Despesa de transporte (kms × valor/km)
- `refeicao` - Despesa de refeição (nº × valor/refeição)
- `outro` - Despesa com valor fixo

**orcamento_reparticoes.tipo:**
- `servico` - Serviço com beneficiário
- `equipamento` - Equipamento com beneficiário
- `despesa` - Despesa espelhada do CLIENTE (readonly)
- `comissao` - Comissão (venda ou empresa)

**orcamento_reparticoes.beneficiario:**
- `BA` - Sócio Bruno Amaral
- `RR` - Sócio Rafael Rodrigues
- `AGORA` - Empresa
- `FREELANCER_[id]` - Freelancer
- `FORNECEDOR_[id]` - Fornecedor

**orcamentos.status:**
- `rascunho` - Editável, sem validação
- `aprovado` - Validado (totais coincidem), readonly
- `rejeitado` - Anulado

### Índices Recomendados

CREATE INDEX idx_orcamento_itens_orcamento ON orcamento_itens(orcamento_id);
CREATE INDEX idx_orcamento_itens_tipo ON orcamento_itens(tipo);
CREATE INDEX idx_orcamento_reparticoes_orcamento ON orcamento_reparticoes(orcamento_id);
CREATE INDEX idx_orcamento_reparticoes_beneficiario ON orcamento_reparticoes(beneficiario);
CREATE INDEX idx_orcamento_reparticoes_item_cliente ON orcamento_reparticoes(item_cliente_id);

---


## 📋 Tabelas

### `socios` - Sócios da Empresa

**Campos principais:**
- `id` - PK
- `codigo` - "BA" ou "RR"
- `nome` - Nome completo
- `nif` - Número fiscal
- `iban` - Conta bancária
- `percentagem` - % da sociedade (50.0)

**Enums:**
- Nenhum

**Relações:**
- `projetos` → Lista de projetos
- `despesas` → Lista de despesas
- `boletins` → Lista de boletins

**Constantes:**
```python
Socio.BRUNO = "BA"
Socio.RAFAEL = "RR"
```

---

### `projetos` - Projetos de Clientes

**Campos principais:**
- `id` - PK
- `codigo` - "P001", "P002", etc.
- `nome` - Nome do projeto
- `cliente_id` - FK → clientes
- `socio_responsavel` - FK → socios
- `tipo` - ENUM (frontend/backend/fullstack)
- `estado` - ENUM (ativo/concluido/cancelado)
- `data_inicio` - Date
- `data_fim` - Date (opcional)
- `valor_frontend` - Decimal
- `valor_backend` - Decimal
- `valor_total` - Decimal
- `premio_bruno` - Decimal
- `premio_rafael` - Decimal
- `valor_pago` - Decimal

**Enums:**
```python
TipoProjeto:
  - FRONTEND
  - BACKEND
  - FULLSTACK

EstadoProjeto:
  - ATIVO
  - CONCLUIDO
  - CANCELADO
```

**Relações:**
- `cliente` → Cliente (many-to-one)
- `socio` → Socio (many-to-one)

**Regras de negócio:**
- `valor_total` = `valor_frontend` + `valor_backend`
- Prémios individuais por sócio
- Valor pago ≤ valor total

---

### `clientes` - Clientes da Agora Media

**Campos principais:**
- `id` - PK
- `numero` - String única (#C0001, #C0002, etc.)
- `nome` - **VARCHAR(120)** - Nome curto para listagens e referências rápidas
- `nome_formal` - **VARCHAR(255)** - Nome completo/formal da empresa (usado em documentos oficiais)
- `nif` - NIF (opcional)
- `pais` - País (default: "Portugal")
- `morada` - Morada completa (opcional, TEXT)
- `contacto` - Telefone/contacto (opcional)
- `email` - Email (opcional)
- `angariacao` - Informação sobre origem/angariação (opcional)
- `nota` - Notas adicionais (opcional, TEXT)
- `created_at` - Timestamp de criação
- `updated_at` - Timestamp de última atualização

**Campos de Nome (desde Migration 021):**
- **nome:** Nome curto usado em listagens, tabelas, dropdowns (ex: "Farmácia do Povo")
- **nome_formal:** Nome completo/legal usado em documentos formais e PDFs (ex: "Farmácia Popular do Centro, Lda.")
- **Comportamento:** Se nome_formal não fornecido, usa automaticamente o valor de nome
- **Pesquisa:** Ambos os campos são pesquisáveis (ILIKE case-insensitive)

**Relações:**
- `projetos` → Lista de projetos (one-to-many)
- `orcamentos` → Lista de orçamentos (one-to-many)

---

### `despesas` - Despesas da Empresa

**Campos principais:**
- `id` - PK
- `numero` - String única (#D000001, #D000002, etc.)
- `tipo` - ENUM (fixa_mensal, pessoal_bruno, pessoal_rafael, equipamento, projeto)
- `credor_id` - FK → fornecedores (opcional)
- `projeto_id` - FK → projetos (opcional)
- `descricao` - Text
- `valor_sem_iva` - Decimal
- `valor_com_iva` - Decimal
- `data` - Date
- `estado` - ENUM (pendente, vencido, pago)
- `data_pagamento` - Date (opcional)
- `nota` - Text (opcional)
- `despesa_template_id` - FK → despesa_templates (se foi gerada de template)

**Enums:**
```python
TipoDespesa:
  - FIXA_MENSAL      # Despesas fixas mensais (ex: software, servidor)
  - PESSOAL_BRUNO    # Despesas pessoais de Bruno
  - PESSOAL_RAFAEL   # Despesas pessoais de Rafael
  - EQUIPAMENTO      # Equipamento da empresa
  - PROJETO          # Despesas específicas de projeto

EstadoDespesa:
  - PENDENTE         # Por pagar
  - VENCIDO          # Atrasada
  - PAGO             # Paga
```

**Relações:**
- `credor` → Fornecedor (many-to-one, opcional)
- `projeto` → Projeto (many-to-one, opcional)
- `despesa_template` → DespesaTemplate (many-to-one, opcional - se gerada de template)

**Regras de negócio:**
- **Fixas Mensais:** Divididas 50/50 no cálculo de saldos
- **Pessoais:** Cada sócio paga as suas (não divididas)
- **Equipamento e Projeto:** Divididas 50/50
- **Templates:** Despesas podem ser geradas automaticamente de templates (ver despesa_templates)
- **Indicador visual:** Tipo mostra "*" quando gerada de template (ex: "Fixa Mensal*")

---

### `despesa_templates` - Templates de Despesas Recorrentes (NOVO 13/11/2025)

**Descrição:** Templates para geração automática de despesas fixas mensais. NÃO são despesas reais, são moldes.

**Campos principais:**
- `id` - PK
- `numero` - String única (#TD000001, #TD000002, etc.)
- `tipo` - ENUM (normalmente FIXA_MENSAL)
- `credor_id` - FK → fornecedores (opcional)
- `projeto_id` - FK → projetos (opcional)
- `descricao` - Text
- `valor_sem_iva` - Decimal
- `valor_com_iva` - Decimal
- `dia_mes` - Integer (1-31) - Dia do mês para gerar despesa
- `nota` - Text (opcional)

**Enums:**
- Usa TipoDespesa (mesmo enum de despesas)

**Relações:**
- `credor` → Fornecedor (many-to-one, opcional)
- `projeto` → Projeto (many-to-one, opcional)
- `despesas_geradas` → Despesas (one-to-many) - Despesas geradas deste template

**Regras de negócio:**
- **NÃO entram em cálculos financeiros** (não são despesas reais)
- Geram despesas automaticamente via botão "🔁 Gerar Recorrentes"
- **dia_mes:** 1-31 - Se dia não existir no mês (ex: 31 Feb), usa último dia do mês
- Templates podem ser editados/deletados sem afetar despesas já geradas
- Despesas mantêm FK para template de origem (rastreabilidade)

**Acesso UI:**
- Screen dedicado via botão "📝 Editar Recorrentes" em Despesas
- Modal 1000x700px com CRUD completo

---

### `valores_referencia_anual` - Valores de Referência por Ano

**Campos principais:**
- `id` - PK
- `ano` - Integer (unique, indexed) - Ex: 2025, 2026
- `val_dia_nacional` - Decimal - Ex: 72.65€
- `val_dia_estrangeiro` - Decimal - Ex: 167.07€
- `val_km` - Decimal - Ex: 0.40€
- `created_at` - DateTime
- `updated_at` - DateTime

**Relações:**
- Nenhuma (configuração global)

**Regras de negócio:**
- Um registo por ano
- Editável via configurações (botão escondido)
- Novos boletins copiam valores do ano vigente
- Se ano não existe, usa defaults hard-coded

**Acesso UI:**
- Screen `valores_referencia.py` (configurações)
- Botão "escondido" (pouco usado)

---

### `boletins` - Boletins Itinerário (Ajudas de Custo)

**Campos principais:**
- `id` - PK
- `numero` - String única (#B0001, #B0002, etc.)
- `socio` - ENUM (BRUNO/RAFAEL)
- `mes` - Integer (1-12, indexed)
- `ano` - Integer (ex: 2025, indexed)
- `data_emissao` - Date (indexed)
- `data_pagamento` - Date (nullable)
- `estado` - ENUM (PENDENTE/PAGO, indexed)

**Valores de Referência (copiados do ano):**
- `val_dia_nacional` - Decimal - Ex: 72.65€
- `val_dia_estrangeiro` - Decimal - Ex: 167.07€
- `val_km` - Decimal - Ex: 0.40€

**Totais Calculados Automaticamente:**
- `total_ajudas_nacionais` - Decimal - Soma dias nacionais × val_dia_nacional
- `total_ajudas_estrangeiro` - Decimal - Soma dias estrangeiro × val_dia_estrangeiro
- `total_kms` - Decimal - Soma kms × val_km
- `valor_total` - Decimal - Soma dos 3 totais

**Metadata:**
- `nota` - Text (nullable)
- `created_at` - DateTime
- `updated_at` - DateTime

**Enums:**
```python
EstadoBoletim:
  - PENDENTE  # Emitido mas não pago (desconta do saldo imediatamente)
  - PAGO      # Pago (DESCONTA do saldo)
```

**Relações:**
- `linhas` → BoletimLinha (one-to-many) - Deslocações deste boletim

**Regras de negócio:**
- Totais calculados automaticamente ao editar linhas
- Valores de referência copiados do ano vigente na criação
- **IMPORTANTE:** Boletins descontam do saldo quando PAGOS (não quando emitidos)

**Cálculos:**
```python
total_ajudas_nacionais = sum(linha.dias for linha in linhas if linha.tipo == NACIONAL) × val_dia_nacional
total_ajudas_estrangeiro = sum(linha.dias for linha in linhas if linha.tipo == ESTRANGEIRO) × val_dia_estrangeiro
total_kms = sum(linha.kms for linha in linhas) × val_km
valor_total = total_ajudas_nacionais + total_ajudas_estrangeiro + total_kms
```

**Acesso UI:**
- Screen `boletins.py` (lista) + coluna "Linhas" (contador)
- Botão "🔁 Gerar Recorrentes"
- Duplo-clique abre `BoletimForm` (editor completo)

---

### `boletim_linhas` - Linhas de Deslocação (NOVO - Planeado)

**Campos principais:**
- `id` - PK
- `boletim_id` - FK → boletins (CASCADE DELETE, indexed)
- `ordem` - Integer (ordenação: 1, 2, 3...)
- `projeto_id` - FK → projetos (NULLABLE, SET NULL) - **Dropdown opcional**
- `servico` - Text (not null) - Ex: "vMix Novobanco", "reunião com cliente"
- `localidade` - String(100) - Ex: "Aguieira", "Lisboa", "Copenhaga"
- `data_inicio` - Date
- `hora_inicio` - Time (informativa)
- `data_fim` - Date
- `hora_fim` - Time (informativa)
- `tipo` - ENUM (NACIONAL/ESTRANGEIRO)
- `dias` - Decimal (inserido manualmente: 0, 0.5, 1, 6)
- `kms` - Integer (ex: 400, 206)
- `created_at` - DateTime
- `updated_at` - DateTime

**Enums:**
```python
TipoDeslocacao:
  - NACIONAL      # Deslocação em Portugal
  - ESTRANGEIRO   # Deslocação fora de Portugal
```

**Relações:**
- `boletim` → Boletim (many-to-one)
- `projeto` → Projeto (many-to-one, nullable)

**Regras de negócio:**
- Ordenação via campo `ordem`
- Se `projeto_id` preenchido, `servico` auto-preenche mas é editável
- Horas são informativas (não usadas em cálculo)
- Dias inseridos manualmente (cálculo complexo, usuário decide)
- Trigger recalcula totais do boletim ao adicionar/editar/remover

**Comportamento ao apagar projeto:**
- SET NULL: `projeto_id` = NULL (mantém texto em `servico`)

---

### `boletim_templates` - Templates de Boletins Recorrentes (NOVO - Planeado)

**Campos principais:**
- `id` - PK
- `numero` - String única (#TB000001, #TB000002)
- `nome` - String(200) - Ex: "Boletim Bruno Mensal"
- `socio` - ENUM (BRUNO/RAFAEL)
- `dia_mes` - Integer (1-31) - Dia para gerar automaticamente
- `ativo` - Boolean (default=True)
- `created_at` - DateTime
- `updated_at` - DateTime

**Relações:**
- Nenhuma (não armazena linhas pré-definidas)

**Regras de negócio:**
- **NÃO armazena valores de referência** (usa ano vigente na geração)
- **NÃO armazena linhas pré-definidas**
- Geração cria boletim com cabeçalho vazio
- **🎯 NICE-TO-HAVE:** Pré-preencher linhas com projetos do sócio no mês
- Apenas 2 templates esperados: BA (#TB000001) e RR (#TB000002)

**Comportamento geração:**
```python
def gerar_boletim(template, mes, ano):
    # 1. Criar boletim com valores do ano vigente
    boletim = Boletim(
        socio=template.socio,
        mes=mes,
        ano=ano,
        val_dia_nacional=get_valor_ano(ano, 'nacional'),
        ...
    )
    # 2. (Opcional) Pré-preencher com projetos do mês
    # projetos = query_projetos_socio_mes(template.socio, mes, ano)
    # for projeto in projetos:
    #     criar_linha_sugerida(boletim, projeto)
```

**Acesso UI:**
- Screen `templates_boletins.py` (CRUD simples)
- Similar a `templates_despesas.py`

---

### `orcamentos` - Orçamentos para Clientes

**Campos principais:**
- `id` - PK
- `cliente_id` - FK → clientes
- `codigo` - "ORC001", "ORC002", etc.
- `versao` - "v1.0", "v1.1", etc.
- `data_criacao` - Date
- `data_validade` - Date
- `valor_total` - Decimal
- `estado` - ENUM (pendente/aprovado/rejeitado)
- `observacoes` - Text

**Enums:**
```python
EstadoOrcamento:
  - PENDENTE
  - APROVADO
  - REJEITADO
```

**Relações:**
- `cliente` → Cliente (many-to-one)
- `linhas` → Lista de linhas de orçamento (one-to-many)

**Regras de negócio:**
- Múltiplas versões do mesmo orçamento (código base igual)
- Valor total calculado a partir das linhas

---

### `orcamento_linhas` - Linhas de Orçamento

**Campos principais:**
- `id` - PK
- `orcamento_id` - FK → orcamentos
- `descricao` - Descrição do item
- `quantidade` - Decimal
- `preco_unitario` - Decimal
- `preco_total` - Decimal

**Relações:**
- `orcamento` → Orcamento (many-to-one)

**Regras de negócio:**
- `preco_total` = `quantidade` × `preco_unitario`

---

### `fornecedores` - Fornecedores/Credores

**Campos principais:**
- `id` - PK
- `nome` - Nome do fornecedor
- `nif` - NIF (opcional)
- `email` - Email (opcional)
- `telefone` - Telefone (opcional)
- `morada` - Morada (opcional)
- `ativo` - Boolean
- `estatuto` - ENUM (credor/fornecedor)

**Enums:**
```python
EstatutoFornecedor:
  - CREDOR
  - FORNECEDOR
```

**Relações:**
- Nenhuma (independente)

---

### `equipamento` - Equipamento da Empresa

**Campos principais:**
- `id` - PK
- `nome` - Nome do equipamento
- `descricao` - Descrição
- `numero_serie` - Número de série (opcional)
- `data_aquisicao` - Date
- `valor_aquisicao` - Decimal
- `localizacao` - Localização física (opcional)
- `ativo` - Boolean

**Relações:**
- Nenhuma (independente)

**Exemplos:**
- Câmaras, lentes, tripés
- Computadores, monitores
- Software, licenças

---

## 🔑 Índices e Performance

### Índices Automáticos
- Primary Keys (todas as tabelas)
- Foreign Keys (todas as relações)

### Índices Adicionais (se necessário)
```sql
-- Procura de projetos por cliente
CREATE INDEX idx_projetos_cliente ON projetos(cliente_id);

-- Procura de boletins por sócio/mês/ano
CREATE INDEX idx_boletins_socio_mes_ano ON boletins(socio_id, mes, ano);
```

---

## 📊 Queries Comuns

### Saldos Pessoais (CORE)
```python
# Receitas por sócio
SELECT
  SUM(valor_frontend + valor_backend + premio_bruno) AS total_ba
FROM projetos
WHERE socio_responsavel = 'BA' AND estado = 'CONCLUIDO'

# Despesas por sócio (50/50)
SELECT
  SUM(valor) * 0.5 AS despesas_ba
FROM despesas
WHERE estado = 'PAGO'

# Boletins por sócio
SELECT
  SUM(vencimento_total) AS boletins_ba
FROM boletins
WHERE socio_id = 'BA' AND estado = 'PAGO'
```

### Projetos Ativos
```python
projetos = session.query(Projeto).filter(
    Projeto.estado == EstadoProjeto.ATIVO
).all()
```

### Despesas Pendentes
```python
despesas = session.query(Despesa).filter(
    Despesa.estado == EstadoDespesa.PENDENTE
).order_by(Despesa.data).all()
```

---

## 🔄 Migrations

### Histórico de Migrations
Ver `database/migrations/versions/`

### Criar Nova Migration
```bash
# 1. Alterar model em database/models/
# 2. Gerar migration
alembic revision --autogenerate -m "adicionar campo X"
# 3. Revisar migration gerada
# 4. Aplicar
alembic upgrade head
```

---

## 💾 Backup

### Backup Manual
```bash
cp agora_media.db agora_media_backup_$(date +%Y%m%d).db
```

### Backup Automático (futura implementação)
- Backup diário automático
- Rotação de backups (manter últimos 7 dias)
- Armazenamento em cloud (opcional)

---

**Mantido por:** Equipa Agora
**Última atualização:** 2025-11-09
# 🗄️ DATABASE_SCHEMA.md - ATUALIZAÇÕES (15/11/2025)

## ⚠️ INSTRUÇÕES
Adicionar esta secção ao final do ficheiro `DATABASE_SCHEMA.md` existente, antes de qualquer secção de "Histórico" ou "Changelog".

---

## 📋 ATUALIZAÇÕES PENDENTES

As seguintes alterações foram documentadas em `BUSINESS_LOGIC.md` e precisam ser implementadas via migrations.

---

### 1. Tabela `orcamentos` - Adicionar Coluna

**Coluna a adicionar:**
```sql
owner VARCHAR(2) NOT NULL  -- 'BA' ou 'RR'
```

**Migration:** 020
**Razão:** Todo orçamento precisa de um responsável (owner) definido. Determina quem gere o orçamento e posteriormente o projeto.

**Default para dados existentes:** 
- Pode usar 'BA' como default ou inferir do cliente
- Avaliar caso a caso durante migration

---

### 2. Tabela `projetos` - Múltiplas Alterações

**Colunas a adicionar:**
```sql
-- Owner (responsável pelo projeto)
owner VARCHAR(2) NOT NULL  -- 'BA' ou 'RR'

-- Rastreabilidade financeira (valores decompostos de orçamento)
valor_empresa DECIMAL(10,2) DEFAULT 0        -- Parcela da empresa
valor_fornecedores DECIMAL(10,2) DEFAULT 0   -- Total pago a fornecedores
valor_equipamento DECIMAL(10,2) DEFAULT 0    -- Rendimento de equipamento usado
valor_despesas DECIMAL(10,2) DEFAULT 0       -- Despesas do projeto

-- Data de pagamento
data_pagamento DATE NULL  -- Quando projeto foi marcado como PAGO
```

**Coluna a alterar:**
```sql
-- ANTES:
estado VARCHAR(20)  -- 'ativo' | 'concluido' | 'cancelado'

-- DEPOIS:
estado VARCHAR(20)  -- 'ATIVO' | 'FINALIZADO' | 'PAGO' | 'ANULADO'
```

**Migration:** 020

**Mapeamento de estados existentes:**
```python
# Durante migration:
'ativo' → 'ATIVO'
'concluido' → 'FINALIZADO'
'cancelado' → 'ANULADO'
```

**Razão das alterações:**
- **owner:** Necessário para gestão e cálculo de saldos pessoais
- **Estados:** 
  - ATIVO: Projeto em curso
  - FINALIZADO: Concluído mas não pago (transição automática por `data_fim`)
  - PAGO: Cliente pagou, prémios distribuídos
  - ANULADO: Cancelado
- **Rastreabilidade:** Permite saber distribuição de valores vindos de orçamentos
- **data_pagamento:** Rastrear quando projeto foi efetivamente pago

**Regra de transição automática:**
```python
# Job diário ou ao carregar dashboard/projetos:
for projeto in projetos:
    if projeto.estado == 'ATIVO' and projeto.data_fim and projeto.data_fim < hoje:
        projeto.estado = 'FINALIZADO'
        projeto.save()
```

---

### 3. Tabela `proposta_reparticoes` - Reestruturação

**Coluna a remover:**
```sql
entidade VARCHAR(10)  -- 'BA' ou 'RR' (DEPRECADO)
```

**Colunas a adicionar:**
```sql
tipo VARCHAR(20) NOT NULL  -- 'BA' | 'RR' | 'EMPRESA' | 'FORNECEDOR' | 'EQUIPAMENTO' | 'DESPESA'
fornecedor_id INTEGER NULL
equipamento_id INTEGER NULL
```

**Constraints a adicionar:**
```sql
FOREIGN KEY (fornecedor_id) REFERENCES fornecedores(id) ON DELETE SET NULL
FOREIGN KEY (equipamento_id) REFERENCES equipamento(id) ON DELETE SET NULL
```

**Migration:** 020

**Mapeamento de dados existentes:**
```python
# Durante migration:
# Repartições antigas com entidade='BA' → tipo='BA', fornecedor_id=NULL, equipamento_id=NULL
# Repartições antigas com entidade='RR' → tipo='RR', fornecedor_id=NULL, equipamento_id=NULL
```

**Razão:** 
- Repartições precisam suportar 6 tipos diferentes
- Tipos FORNECEDOR e EQUIPAMENTO precisam de FKs para rastreabilidade
- Sistema expandido permite distribuição completa de valores de orçamento

**Tipos de repartição:**
- **BA:** Prémio para Bruno Amaral
- **RR:** Prémio para Rafael Reigota  
- **EMPRESA:** Valor que fica na empresa
- **FORNECEDOR:** Pago a fornecedor específico (requer `fornecedor_id`)
- **EQUIPAMENTO:** Rendimento de equipamento usado (requer `equipamento_id`)
- **DESPESA:** Outras despesas do orçamento

---

### 4. Tabela `equipamento` - Adicionar Coluna

**Coluna a adicionar:**
```sql
rendimento_acumulado DECIMAL(10,2) DEFAULT 0
```

**Migration:** 020

**Razão:** Rastrear quanto cada equipamento já rendeu ao longo do tempo através de repartições em orçamentos.

**Atualização:**
- Ao aprovar orçamento com repartição tipo='EQUIPAMENTO' → incrementa rendimento
- Não reverte se projeto/orçamento anulado (mantém histórico)

---

### 5. Sistema de Templates de Boletins - A REMOVER

**Status:** Sistema será removido da UI mas tabelas podem permanecer (legacy)

**Tabelas afetadas:**
- `boletim_templates` (pode manter ou remover em limpeza futura)

**Razão:** Sistema de templates é demasiado complexo. Substituído por funcionalidade "Duplicar Boletim".

**Ver:** DECISIONS.md, TODO.md

---

### 6. NOVA Tabela `receitas` - A IMPLEMENTAR (Futuro)

**Status:** ⏳ Documentado mas não implementado
**Prioridade:** Média
**Migration:** 021 (futura)

**Estrutura proposta (a discutir):**
```sql
CREATE TABLE receitas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    numero VARCHAR(20) UNIQUE NOT NULL,  -- #R000001, #R000002, etc
    
    -- Relações
    projeto_id INTEGER NULL,
    cliente_id INTEGER NULL,
    
    -- Dados principais
    descricao TEXT NOT NULL,
    valor DECIMAL(10,2) NOT NULL,
    data DATE NOT NULL,
    
    -- Estado
    estado VARCHAR(20) NOT NULL,  -- 'ATIVO' | 'CANCELADO'
    tipo VARCHAR(20) NOT NULL,    -- 'PROJETO' | 'OUTRO'
    
    -- Metadata
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    FOREIGN KEY (projeto_id) REFERENCES projetos(id) ON DELETE SET NULL,
    FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE SET NULL
);

CREATE INDEX idx_receitas_projeto ON receitas(projeto_id);
CREATE INDEX idx_receitas_cliente ON receitas(cliente_id);
CREATE INDEX idx_receitas_data ON receitas(data);
CREATE INDEX idx_receitas_estado ON receitas(estado);
```

**Comportamento:**
- Ao marcar projeto como PAGO → criar receita ATIVO automaticamente
- Ao reverter projeto para FINALIZADO → marcar receita como CANCELADO (não apagar)
- Permite receitas avulsas (sem projeto): subsídios, vendas de equipamento, etc

**Decisões pendentes:**
- Receita sempre = valor total do projeto? Ou pode ser parcial?
- Permitir múltiplas receitas por projeto? (pagamentos faseados)
- Campos adicionais? (método pagamento, referência, etc)

**Ver:** 
- TODO.md (tarefa de implementação)
- DECISIONS.md (decisão sobre necessidade de receitas)
- BUSINESS_LOGIC.md Secção 3.4

---

## 📊 Resumo de Alterações

**Migration 020 (Prioritária):**
- ✅ `orcamentos.owner` (novo)
- ✅ `projetos.owner` (novo)
- ✅ `projetos.estado` (atualizar enum)
- ✅ `projetos.valor_empresa` (novo)
- ✅ `projetos.valor_fornecedores` (novo)
- ✅ `projetos.valor_equipamento` (novo)
- ✅ `projetos.valor_despesas` (novo)
- ✅ `projetos.data_pagamento` (novo)
- ✅ `proposta_reparticoes.entidade` (remover)
- ✅ `proposta_reparticoes.tipo` (novo)
- ✅ `proposta_reparticoes.fornecedor_id` (novo + FK)
- ✅ `proposta_reparticoes.equipamento_id` (novo + FK)
- ✅ `equipamento.rendimento_acumulado` (novo)

**Migration 021 (Futura):**
- ⏳ Criar tabela `receitas` completa

---

## 🔗 Referências

- **BUSINESS_LOGIC.md:** Lógica de negócio detalhada
- **DECISIONS.md:** Decisões técnicas e trade-offs
- **TODO.md:** Tarefas de implementação priorizadas

---

_Última atualização: 15/11/2025_
