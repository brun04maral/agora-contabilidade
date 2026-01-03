# Changelog - Agora Contabilidade

Todas as mudanças importantes neste projeto serão documentadas neste ficheiro.

---

## [2.1.0] - 2026-01-03

### 🎉 Sessão Épica: Importação e Sincronização de Dados

**Objetivo**: Importar dados da folha Excel CONTABILIDADE_FINAL_20251231.xlsx para a base de dados PostgreSQL e garantir sincronização perfeita.

### ✨ Added

#### Comandos de Management Django

1. **`import_from_excel.py`** - Importação completa do Excel
   - Importa fornecedores, clientes, projetos, despesas e boletins
   - Agrega prémios por projeto (premio_bruno, premio_rafael)
   - Agrega boletins por (sócio, mês, ano)
   - Sistema de tags para despesas
   - Dry-run mode para preview
   - Estatísticas detalhadas de importação

2. **`limpar_projetos_vazios.py`** - Limpeza de projetos inválidos
   - Remove projetos com descrição vazia + cliente NULL + valor 0
   - Preserva números dos projetos para coerência com Excel
   - Dry-run mode + confirmação obrigatória
   - Estatísticas antes/depois

3. **`limpar_despesas_vazias.py`** - Limpeza de despesas inválidas
   - Remove despesas com descrição vazia + credor NULL + valor 0
   - Preserva números das despesas para coerência com Excel
   - Dry-run mode + confirmação obrigatória
   - Estatísticas antes/depois

4. **`auditar_importacao.py`** - Auditoria Excel vs DB
   - Compara quantidades e valores entre Excel e base de dados
   - Valida fornecedores, clientes, projetos, despesas e boletins
   - Verifica agregação de prémios e boletins
   - Gera relatório categorizado (✅ OK, ⚠️ Avisos, ❌ Incongruências)

5. **`analisar_caixa.py`** - Análise de fórmulas do Excel
   - Extrai fórmulas da aba CAIXA usando openpyxl
   - Compara lógica Excel vs SaldosCalculator
   - Gera documentação em Markdown
   - Interpreta fórmulas complexas (SUMIFS, FILTER, REGEXMATCH)

### 🔄 Changed

#### SaldosCalculator - Refatoração Completa

**Antes**: Lógica única, filtros por `estado=PAGO`

**Depois**: Lógica dual (Saldo Atual vs Saldo Projetado)

**Saldo Atual** (decisões financeiras HOJE):
- INs: Projetos pagos (data_recibo exists) + Prémios trabalho feito (data_fim < hoje)
- OUTs: Despesas fixas ÷2 + Boletins PAGOS + Despesas pessoais

**Saldo Projetado** (planeamento médio prazo):
- INs: Projetos pagos + Prémios TODOS (incluindo futuros)
- OUTs: Despesas fixas ÷2 + Boletins TODOS (PAGO + PENDENTE) + Despesas pessoais

**Mudanças técnicas**:
- Substituídos filtros `ano__gte/lte` por `data__gte/lte` (Despesa tem campo `data`, não `ano`)
- Tags para categorização: `ADMINISTRATIVO`, `ORDENADO`, `SUB_ALIMENTACAO`, `PESSOAL`
- Retorna sempre ambos os saldos + breakdown detalhado
- Sugestão de boletim baseada em saldo projetado

#### Admin View - SaldoAdmin

- Atualizado para usar filtros de data em vez de método inexistente `calcular_saldo_ano()`
- Breakdown do ano corrente usando `data_inicio` e `data_fim`
- Compatível com novo SaldosCalculator

### 🐛 Fixed

1. **Erro 500 no `/admin/core/saldo/`**
   - Causa: `SaldoAdmin` chamava `calcular_saldo_ano()` que não existia
   - Fix: Usar `calcular_saldo_bruno/rafael()` com filtros de data

2. **FieldError: Cannot resolve keyword 'ano'**
   - Causa: Filtros `ano__gte` em modelo Despesa que só tem campo `data`
   - Fix: Substituir por `data__gte/lte`

3. **Boletim import constraint violation**
   - Causa: Coluna órfã `socio` (NOT NULL) não mapeada no Django
   - Fix: Adicionar campo `socio_old` mapeando para coluna órfã

### 📊 Database State

**Estado final após limpeza**:
- **Fornecedores**: 45 (2 com nome NULL não importaram)
- **Clientes**: 18 (2 com nome NULL não importaram)
- **Projetos**: 80 válidos (1,619 vazios removidos)
- **Despesas**: 236 válidas (639 vazias removidas)
- **Boletins**: 24 (agregados por sócio/mês/ano)

**Validação**:
- ✅ Quantidades de projetos: 100% correto (80)
- ✅ Valores de projetos: 100% correto (€78,746.31)
- ✅ Prémios Rafael: 100% correto (€9,916.19)
- ⚠️ Prémio Bruno #P0032: €225.00 faltam (despesa #D000120 não importada)

### 📚 Documentation

#### Novo
- `CHANGELOG.md` - Este ficheiro
- `docs/CAIXA_ANALYSIS.md` - Análise das fórmulas Excel da aba CAIXA

#### Atualizado
- `README.md` - Seções de Features, Comandos, Documentação e Notas de Versão
- `docs/EXCEL_IMPORT_ANALYSIS.md` - Processo de importação documentado

### 🔧 Technical Details

**Commits principais**:
- `715f31f` - Importação Excel executada
- `1b64dd3` - Limpeza de 1,619 projetos vazios
- `ebe3805` - Auditoria Excel vs DB
- `231c18b` - Análise da aba CAIXA
- `7a1b86d` - Refatoração do SaldosCalculator
- `e016d1a` - Fix erro 500 no admin
- `7b8161c` - Comando limpar_despesas_vazias

**Ferramentas utilizadas**:
- openpyxl (leitura de Excel com fórmulas)
- Django ORM (queries otimizadas)
- PostgreSQL 16 (base de dados)
- Docker Compose (ambiente de desenvolvimento)

---

## [2.0.0] - 2025-12

### 🎉 Lançamento Inicial - Django App

**Migração completa de Tkinter+SQLite para Django+PostgreSQL**

### Added
- Django 5.0 como framework principal
- PostgreSQL 16 como base de dados
- Unfold Admin Theme para interface moderna
- Docker + Traefik + Cloudflare para deployment
- Dashboard de Saldos Pessoais
- Modelo Socio com migração de dados
- Gestão completa: Projetos, Orçamentos, Despesas, Boletins, Clientes, Fornecedores

### Changed
- Arquitetura: Desktop → Web
- Database: SQLite → PostgreSQL 16
- Interface: Tkinter → Django Admin + Unfold
- Deployment: Manual → Docker Compose

### Deprecated
- Aplicação Tkinter (movida para `archive-old-tkinter-app/`)

---

## Formato

Este changelog segue [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere a [Semantic Versioning](https://semver.org/lang/pt-BR/).

### Tipos de mudanças
- **Added** - Novas funcionalidades
- **Changed** - Mudanças em funcionalidades existentes
- **Deprecated** - Funcionalidades obsoletas (a serem removidas)
- **Removed** - Funcionalidades removidas
- **Fixed** - Correções de bugs
- **Security** - Correções de vulnerabilidades
