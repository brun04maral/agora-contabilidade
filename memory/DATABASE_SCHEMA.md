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
- `nome` - Nome do cliente
- `nif` - NIF (opcional)
- `email` - Email (opcional)
- `telefone` - Telefone (opcional)
- `morada` - Morada (opcional)
- `ativo` - Boolean

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
