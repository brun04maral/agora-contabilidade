# 📝 Changelog - Agora Contabilidade

Registo de mudanças significativas no projeto.

---

## [2025-11-14 - Tarde] Script de Verificação de Migrations & Execução 009-011

### ✨ Adicionado
- 🔍 **Script de Verificação de Migrations** (`check_migrations.py`, ~200 linhas)
  - Verifica automaticamente todas as migrations 001-019
  - Detecta tabelas e colunas existentes via `PRAGMA table_info`
  - Lista migrations **aplicadas** ✅ e **pendentes** ❌
  - Mostra comandos exatos para executar migrations pendentes
  - Reconhece scripts combinados (009+010, 016-019)
  - Uso simples: `python3 check_migrations.py`

### 🗄️ Database
- ✅ **Migrations 009-011 Executadas** (14/11/2025)
  - 009: Tabela `equipamento_alugueres` para registo de alugueres
  - 010: Refatoração da tabela `orcamentos` para estrutura única (tem_versao_cliente, titulo_cliente, etc.)
  - 011: Tabelas `proposta_secoes` e `proposta_itens` para versão cliente
- ✅ **Todas as migrations 001-019 agora aplicadas e verificadas**

### 🐛 Bugs Corrigidos
1. **Script check_migrations.py: ValueError no unpack**
   - Erro: `not enough values to unpack (expected 4, got 3)`
   - Causa: Tabelas têm 3 elementos, colunas têm 4
   - Fix: Verificar `len(check)` antes de fazer unpack
2. **Verificações incorretas para migrations 009 e 011**
   - Migration 009: Verificava coluna `equipamento.aluguer_mensal` (errado) → Corrigido para tabela `equipamento_alugueres`
   - Migration 011: Verificava coluna `orcamento_secoes.proposta_cliente` (errado) → Corrigido para tabelas `proposta_secoes` e `proposta_itens`

### 🐞 Bug Resolvido (Usuário)
- **Erro ao clicar em Orçamentos:** `no such column: orcamentos.tem_versao_cliente`
  - Causa: Migration 010 não estava aplicada na DB local do usuário
  - Resolução: Execução de `scripts/run_migrations_009_010.py` + `scripts/run_migration_011.py`
  - Status: ✅ Resolvido com script de verificação

### 📦 Commits
- `1682321` - 🔧 Tools: Script para verificar migrations pendentes na DB local
- `5ae262a` - 🐛 Fix: Corrigir bug no unpack de migrations (tabelas têm 3 elementos)
- `1fc2786` - 🔧 Fix: Script reconhece que migrations 009 e 010 são o mesmo comando
- `0db2dac` - 🐛 Fix: Corrigir verificações das migrations 009 e 011

### 🎯 Status
- ✅ **Todas migrations 001-019 aplicadas em dev e user local**
- ✅ **Script de verificação funcional e pronto para uso futuro**
- ✅ **Erro de Orçamentos resolvido**

---

## [2025-11-14 - Manhã] Sistema de Importação Incremental & Migrations

### ✨ Adicionado
- 🔄 **Sistema de Importação Incremental Completo**
  - Script reescrito (`scripts/import_from_excel.py`, ~1.000 linhas)
  - **Modo incremental:** Skip automático de registos existentes (preserva alterações locais)
  - **Flags:** `--dry-run` (preview), `--excel PATH`, `--clear-all`
  - **Matching inteligente:** Por número único (#C001, #P001, #D001, etc.)
  - **Update seletivo:** Prémios de projetos podem ser atualizados se mudarem
  - **Validações robustas:** Skip de despesas sem data, validação de campos obrigatórios
  - **Estatísticas detalhadas:** NEW/SKIP/UPDATED/ERROR para cada entidade
  - **Guia completo:** `IMPORT_GUIDE.md` (311 linhas, 4 cenários práticos)

### 🗄️ Database
- ✅ **Migrations 012-019 Executadas** (14/11/2025)
  - 012: Campo `website` em fornecedores
  - 013-015: Sistema de despesas recorrentes (templates)
  - 016-019: Sistema completo de Boletim Itinerário
    - Valores de referência editáveis por ano
    - Linhas de deslocação múltiplas com cálculos automáticos
    - Templates recorrentes com geração mensal
- ✅ **Importação Real Concluída** (Excel: CONTABILIDADE_FINAL_20251114.xlsx)
  - 1 cliente novo (#C0020: RD LIGHT LDA)
  - 3 despesas novas (#D000239, #D000242, #D000243)
  - 2 prémios atualizados (#P0061, #P0053)
  - **Total na DB:** 19 clientes, 44 fornecedores, 75 projetos, 165 despesas, 34 boletins

### 🗑️ Removido
- ❌ Processo de importação via JSON obsoleto
  - Apagado `scripts/import_excel.py` (522 linhas)
  - Apagado `memory/archive/importacao/INSTRUCOES_IMPORTACAO.md` (358 linhas)
  - Apagado `dados_excel.json` (138KB)
  - Limpeza total: ~6.000 linhas de código/docs obsoletos

### 🐛 Bugs Corrigidos
1. **Maps guardavam objetos em vez de IDs**
   - Afetava: clientes_map, fornecedores_map, projetos_map
   - Erro: `AttributeError: 'int' object has no attribute 'id'` e `type 'Projeto' is not supported`
   - Fix: Guardar IDs diretamente nos maps (linhas 432, 467, 598, 603, 609, 614)
2. **Despesas sem data causavam crash**
   - Erro: `NOT NULL constraint failed: despesas.data`
   - Fix: Skip com aviso para despesas sem data (linhas 558-562)
3. **Processamento de prémios esperava objetos**
   - Erro após fix anterior nos maps
   - Fix: Buscar objeto Projeto a partir do ID (linhas 676-677)

### 📦 Commits
- `9bd9e76` - 🗑️ Cleanup: Remover processo via JSON
- `6396a90` - ✨ Feature: Importação incremental com --dry-run
- `777ded7` - 📝 Docs: Guia completo de importação
- `3e0edea` - 🐛 Fix: Bugs no script + migrations 012-019
- `4336038` - 🐛 Fix: Bugs críticos na importação de despesas
- `5e4e573` - 🐛 Fix: Processamento de prémios
- `944e65d` - 📊 DB: Importação incremental (14/11/2025)

### 🎯 Status
- ✅ **Sistema incremental 100% funcional e testado**
- ✅ **Pronto para produção**
- ✅ **Documentação completa**

---

## [2025-11-13] Planeamento UX: Orçamentos e Boletins

### 📝 Documentado
- 🎨 **Melhorias UX para Orçamentos e Boletins**
  - **Feedback do utilizador:** Ambos os screens identificados como "muito maus e algo confusos"
  - **Status:** Documentado em `memory/TODO.md` como tarefa prioritária (Média Prioridade)

  **ORÇAMENTOS - 7 Propostas de Melhoria:**
  1. **Wizard multi-step** - Dividir criação em 3 passos (info básica → secções/itens → repartições)
  2. **Preview visual lateral** - Mostrar totais em tempo real (geral, subtotais, repartições BA/RR)
  3. **Gráfico de repartições** - Pie chart ou barra horizontal para visualizar BA vs RR
  4. **Botão "Duplicar Orçamento"** - Criar cópia completa (secções + itens + repartições)
  5. **Simplificar formulário** - Agrupar campos em frames claramente separados (se não wizard)
  6. **Validação em tempo real** - Mostrar erros inline, não apenas no save
  7. **Tooltips informativos** - Explicar campos complexos (ex: "Repartição = divisão de prémios")

  **BOLETINS - 11 Propostas de Melhoria:**
  1. **Remover formulário legacy** - Apagar `FormularioBoletimDialog` completamente
  2. **Simplificar buttons** - Reduzir de 4 para 2 botões (Novo + Config dropdown)
  3. **Vista de cards** - Substituir tabela por cards visuais com badges de estado
  4. **Edição inline de linhas** - Não abrir dialog, editar diretamente na tabela
  5. **Auto-save de linhas** - Salvar automaticamente ao mudar foco
  6. **Drag & drop** - Reordenar linhas arrastando
  7. **Templates rápidos** - Botão "Adicionar Template" com dropdown
  8. **Calculadora visual** - Breakdown em tempo real (dias × valor + kms × valor = total)
  9. **Geração recorrente visível** - Dashboard ou notificação mensal
  10. **Filtros rápidos** - Por sócio, estado, mês/ano
  11. **Pesquisa** - Campo busca por número, projeto, nota

  **Impacto esperado:** Reduzir significativamente tempo de operação e erros
  **Prioridade:** Alta (afeta usabilidade diária)

### 📦 Commits
- `24a156b` - 📝 Docs: Document UX improvements for Orçamentos and Boletins

---

## [2025-11-13] Sistema de Boletim Itinerário (Implementação Completa)

### ✨ Adicionado

#### 🗄️ **Fase 1 - Modelo de Dados** (Commit: `8d14f0c`)
- **3 Novas Tabelas:**
  1. `valores_referencia_anual` - Valores de referência editáveis por ano
     - Campos: ano (unique), val_dia_nacional, val_dia_estrangeiro, val_km
     - Seed data: 2025 → 72.65€, 167.07€, 0.40€
  2. `boletim_linhas` - Deslocações individuais de boletim
     - 14 campos incluindo projeto_id (opcional, SET NULL), tipo (NACIONAL/ESTRANGEIRO)
     - FK: boletim_id (CASCADE DELETE), projeto_id (SET NULL)
  3. `boletim_templates` - Templates para geração recorrente
     - Campos: numero (#TB000001), nome, socio, dia_mes, ativo
- **1 Tabela Expandida:**
  4. `boletins` - 9 novos campos adicionados
     - Período: mes, ano
     - Valores ref: val_dia_nacional, val_dia_estrangeiro, val_km
     - Totais: total_ajudas_nacionais, total_ajudas_estrangeiro, total_kms, valor_total
     - Relação: linhas (1:N com boletim_linhas, cascade delete)
- **4 Migrações SQL:**
  - `016_create_valores_referencia_anual.py`
  - `017_create_boletim_linhas.py`
  - `018_create_boletim_templates.py`
  - `019_expand_boletins.py`
  - Script único: `run_migrations_016_019.py`

#### ⚙️ **Fase 2 - Business Logic** (Commit: `9616f7a`)
- **3 Novos Managers:**
  1. `logic/valores_referencia.py` (195 linhas)
     - CRUD completo de valores de referência
     - `obter_ou_default(ano)` → retorna defaults se ano não existe
     - Defaults: 72.65€, 167.07€, 0.40€
  2. `logic/boletim_linhas.py` (288 linhas)
     - CRUD de linhas de deslocação
     - **`recalcular_totais_boletim()`** - Calcula automaticamente:
       * Soma dias por tipo × valores de referência
       * Soma kms × val_km
       * Atualiza todos os totais no boletim
     - Chamado automaticamente após cada criar/atualizar/eliminar
  3. `logic/boletim_templates.py` (309 linhas)
     - CRUD de templates recorrentes
     - **`gerar_boletins_recorrentes_mes(ano, mes)`** - Geração automática:
       * Verifica templates ativos
       * Previne duplicados (socio + mes + ano)
       * Cria boletim com valores de referência do ano
       * Opção pré-preencher projetos (nice-to-have implementado)
- **1 Manager Expandido:**
  4. `logic/boletins.py` - Métodos adicionados:
     - `gerar_proximo_numero()` - Auto-increment de #B000001
     - `criar()` - Novo método para modelo expandido (com valores ref)
     - `emitir()` - DEPRECATED mas mantido para compatibilidade

#### 🎨 **Fase 3 - UI Completa** (Commit: `fe1b032`)
- **4 Novas/Atualizadas Telas:**
  1. `ui/screens/valores_referencia.py` (328 linhas)
     - CRUD de valores de referência por ano
     - Validações: ano 2020-2100, valores > 0
     - Ano bloqueado ao editar (unique constraint)
     - Info label explicativo
  2. `ui/screens/templates_boletins.py` (340 linhas)
     - CRUD de templates recorrentes
     - Tabela: numero, nome, socio, dia_mes, ativo
     - Switch ativo/inativo
     - Validação: dia_mes 1-31
  3. `ui/screens/boletins.py` (atualizado, +140 linhas)
     - **Nova coluna "Linhas"** - mostra count de deslocações
     - **Botão "🔁 Gerar Recorrentes"** - abre dialog
     - `GerarRecorrentesDialog` (195 linhas):
       * Dropdown mês em português
       * Validações ano/mês
       * Integração com `BoletimTemplatesManager`
       * Feedback de sucesso com count gerado
  4. `ui/screens/boletim_form.py` (850 linhas) - **NOVO EDITOR COMPLETO**
     - **Seção Header:**
       * Sócio, Mês, Ano, Data Emissão
       * Valores de referência (display read-only, auto-fetch por ano)
       * Totais calculados (read-only, auto-atualizado)
       * Descrição e Nota (opcionais)
     - **Seção Deslocações:**
       * Tabela 7 colunas: ordem, projeto, servico, localidade, tipo, dias, kms
       * Botão "➕ Adicionar Deslocação"
       * Double-click para editar
       * Botão "🗑️ Apagar Linha Selecionada"
     - **LinhaDialog** (300 linhas nested):
       * Dropdown projetos (opcional, FK)
       * Tipo: NACIONAL/ESTRANGEIRO
       * Dias (Decimal), Kms (int)
       * Data/Hora início/fim (informativas, opcionais)
       * Auto-recalcula totais ao gravar

### 🔧 Arquitetura e Fluxo de Dados

**Cálculo de Totais (Automático):**
```
Adicionar/Editar/Apagar Linha
  ↓
BoletimLinhasManager.recalcular_totais_boletim()
  ↓
1. Soma linhas NACIONAIS: total_dias_nacionais × val_dia_nacional
2. Soma linhas ESTRANGEIRO: total_dias_estrangeiro × val_dia_estrangeiro
3. Soma todos kms: total_kms × val_km
4. TOTAL = ajudas_nacionais + ajudas_estrangeiro + kms
  ↓
Atualiza boletim.valor_total (e boletim.valor para compatibilidade)
  ↓
UI refresh mostra novos totais
```

**Geração de Recorrentes:**
```
Botão "🔁 Gerar Recorrentes" → GerarRecorrentesDialog
  ↓
Seleciona Ano + Mês
  ↓
BoletimTemplatesManager.gerar_boletins_recorrentes_mes()
  ↓
Para cada template ativo:
  1. Verifica duplicado (socio + mes + ano)
  2. Obtém valores de referência do ano
  3. Cria boletim com header vazio
  4. Opcional: pré-preenche linhas com projetos do sócio
  ↓
Retorna (count_generated, erros)
```

### 📝 Decisões Técnicas
1. **Valores de Referência por Ano** - Tabela separada editável (podem mudar anualmente)
2. **Campo "Dias"** - Inserido manualmente (não calculado de horas)
3. **Horas** - Informativas apenas (não usadas em cálculos)
4. **Dados de Sócio** - Dicionário fixo em Python (não BD)
5. **Dropdown Projetos** - Opcional em deslocações (pode ser genérico)
6. **Templates** - Cabeçalho vazio (nice-to-have: pré-preencher com projetos)
7. **Totais** - Calculados automaticamente via manager (não editáveis)

### 📦 Commits
- `8d14f0c` - 🗄️ Database: Fase 1 - Modelo de Dados Boletim Itinerário
- `9616f7a` - ⚙️ Logic: Fase 2 - Business Logic Boletim Itinerário
- `fe1b032` - ✨ Feature: Fase 3 - UI completa para Sistema de Boletim Itinerário

### 📋 Próximos Passos
- **Fase 4:** Testes & Ajustes
  - Executar migrações localmente: `python run_migrations_016_019.py`
  - Criar dados de teste (valores referência, templates, boletins)
  - Testar cálculos automáticos
  - Testar geração recorrente
  - Validar edge cases

---

## [2025-11-13] Melhorias UX + Planeamento Sistema Boletim Itinerário

### ✨ Adicionado
- 🎨 **Strikethrough em Projetos Anulados**
  - Texto riscado (overstrike) em todos os campos exceto "Estado"
  - Aplicado via parâmetro `_strikethrough_except` em DataTableV2
  - Mantém cores existentes (cinza para anulado)
  - Visual claro: fundo cinza + texto riscado
- 📋 **Planeamento completo: Sistema de Boletim Itinerário**
  - Arquitetura definida com 4 novas tabelas
  - Modelo expandido de Boletim com suporte para múltiplas deslocações
  - Templates recorrentes com geração automática
  - Nice-to-have: Pré-preencher linhas com projetos do mês
  - Documentação detalhada em memory/

### 🔧 Alterado
- 🎨 **UX: Removidos popups de sucesso em TODAS as gravações**
  - Mantém apenas popups de erro
  - Afeta 7 screens: projetos, despesas, templates_despesas, boletins, equipamento, orcamentos, relatorios
  - Total: ~24 popups removidos
  - Workflow mais rápido e menos intrusivo
  - Feedback visual imediato via lista atualizada

### 📝 Decisões Técnicas Tomadas
1. **Strikethrough seletivo** via `_strikethrough_except` (lista de colunas)
2. **Silent success** - Apenas erros têm popup
3. **Boletim Itinerário** - Sistema completo (não simplificado):
   - Valores de referência editáveis por ano (tabela separada)
   - Dropdown de projetos opcional em deslocações
   - Horas informativas (não para cálculo)
   - Dados de sócio fixos em dicionário Python
   - Templates criam cabeçalho vazio (opcionalmente pré-preenchido com projetos)
   - Cálculos automáticos de totais

### 📝 Ficheiros Modificados
- `ui/components/data_table_v2.py` - Suporte para strikethrough seletivo
- `ui/screens/projetos.py` - Strikethrough em anulados + remover popup
- `ui/screens/despesas.py` - Remover 4 popups de sucesso
- `ui/screens/templates_despesas.py` - Remover 2 popups
- `ui/screens/boletins.py` - Remover 2 popups
- `ui/screens/equipamento.py` - Remover 2 popups
- `ui/screens/orcamentos.py` - Remover ~10 popups (sed)
- `ui/screens/relatorios.py` - Remover 2 popups (sed)

### 📋 Próxima Fase: Implementação Boletim Itinerário
**Tabelas a criar:**
1. `valores_referencia_anual` - Configuração de valores por ano
2. `boletins` (expandir) - Adicionar mes, ano, valores_ref, totais calculados
3. `boletim_linhas` - Deslocações individuais com projeto_id opcional
4. `boletim_templates` - Templates para geração recorrente

**UI a criar:**
1. `ui/screens/valores_referencia.py` - Configurações (escondido)
2. `ui/screens/boletim_form.py` - Editor completo de boletim
3. `ui/screens/templates_boletins.py` - Gestão de templates
4. Atualizar `ui/screens/boletins.py` - Adicionar coluna, botão gerar

### 📦 Commits
- `23381b1` - ✨ Feature: Strikethrough em projetos anulados
- `76a9967` - 🎨 UI: Remover popups de sucesso ao gravar

---

## [2025-11-13] Sistema de Templates de Despesas Recorrentes

### ✨ Adicionado
- 🔁 **Sistema de Templates de Despesas Recorrentes**
  - Tabela separada `despesa_templates` para moldes de despesas fixas mensais
  - Template ID único: formato #TD000001, #TD000002, etc.
  - Templates armazenam dia do mês (1-31) em vez de data completa
  - Templates NÃO entram em cálculos financeiros
  - Geração automática de despesas mensais a partir de templates
  - Link entre despesas geradas e template de origem (FK)
- 🎨 **UI para Templates de Despesas**
  - Screen dedicado `TemplatesDespesasScreen` com CRUD completo
  - Botão "📝 Editar Recorrentes" no screen Despesas
  - Janela modal para gestão de templates (1000x700px)
  - FormularioTemplateDialog com validação de dia do mês (1-31)
  - Barra de seleção com botão "Apagar Selecionados"
  - Info text explicando que templates não são despesas reais
- ✨ **Indicadores Visuais**
  - Asterisco (*) no tipo quando despesa foi gerada de template (ex: "Fixa Mensal*")
  - Botão "🗑️ Apagar Selecionadas" em Despesas e Templates
  - Confirmação especial ao apagar despesas geradas de templates
  - Aviso: despesas apagadas não serão recriadas automaticamente
- 🔄 **Lógica de Geração Automática**
  - Botão "🔁 Gerar Recorrentes" gera despesas do mês atual
  - Verifica se despesa já foi gerada para evitar duplicados
  - Tratamento inteligente de meses com diferentes dias (Feb 31 → Feb 28/29)
  - Mantém link template-despesa via `despesa_template_id`

### 🐛 Corrigido
- **ValueError:** `['show_actions', 'on_edit', 'on_delete'] are not supported arguments`
  - DataTableV2 não suporta parâmetros show_actions, on_edit, on_delete
  - Solução: Botão "Apagar Selecionadas" na barra de seleção
  - Mantido double-click para editar (on_row_double_click)
  - Interface consistente entre Despesas e Templates

### ♻️ Refatorado
- **Migração do sistema de recorrência**
  - ANTES: Campos `is_recorrente` e `dia_recorrencia` na tabela despesas
  - DEPOIS: Tabela separada `despesa_templates` (arquitetura mais limpa)
  - Separação clara: Templates vs Despesas Reais
  - Migration 014: Criar tabela despesa_templates
  - Migration 015: Remover campos obsoletos de recorrência de despesas
- **DespesasManager refatorado**
  - Método `gerar_despesas_recorrentes_mes()` agora usa DespesaTemplate
  - Removidos parâmetros is_recorrente/dia_recorrencia de criar() e atualizar()
  - FK despesa_template_id agora aponta para despesa_templates.id
- **UI de Despesas limpa**
  - Removidos 100+ linhas de código de recorrência do FormularioDespesaDialog
  - Removidos campos checkbox e dia_recorrencia do formulário
  - Interface mais simples e focada

### 📦 Commits
- `dcf5a9c` - 🔄 Refactor: Sistema de Templates de Despesas Recorrentes (Parte 1/2)
- `898a18d` - ♻️ Refactor: Atualizar DespesasManager para usar templates (Parte 2a)
- `04f333c` - ♻️ Refactor: Remover campos obsoletos de recorrência (Parte 2b)
- `48ae2ca` - ✨ Feature: UI completa para Templates de Despesas Recorrentes
- `f6d1a7f` - 🐛 Fix: Corrigir parâmetros inválidos do DataTableV2

### 📝 Ficheiros Criados
- `database/models/despesa_template.py` - Model DespesaTemplate
- `database/migrations/014_create_despesa_templates.py` - Criar tabela templates
- `database/migrations/015_remove_recorrencia_from_despesas.py` - Limpar despesas
- `logic/despesa_templates.py` - DespesaTemplatesManager com CRUD
- `ui/screens/templates_despesas.py` - Screen e dialog de templates (450+ linhas)
- `run_migration_014.py` - Script para aplicar migration 014
- `run_migration_015.py` - Script para aplicar migration 015

### 📝 Ficheiros Alterados
- `database/models/despesa.py` - FK agora aponta para despesa_templates
- `logic/despesas.py` - Refatorado para usar templates
- `ui/screens/despesas.py` - UI limpa + botões de gestão

### 🎯 Benefícios
- ✅ Separação clara entre templates e despesas reais
- ✅ Templates podem ser editados/deletados sem afetar despesas já geradas
- ✅ Rastreabilidade: despesas sabem de qual template vieram
- ✅ Não há duplicação de lógica de recorrência
- ✅ Interface intuitiva e profissional

---

## [2025-11-13] Date Pickers Profissionais com Formato Inteligente

### ✨ Adicionado
- 🎨 **DatePickerDropdown** - Calendário inline para seleção de data única
  - Calendário visual com navegação mês/ano
  - Click outside para fechar
  - Integração com CustomTkinter
- 🎨 **DateRangePickerDropdown** - Seleção de período com formato inteligente
  - Formato compacto baseado no contexto:
    - Mesmo mês: `15-20/11/2025`
    - Meses diferentes (mesmo ano): `28/11-05/12/2025`
    - Anos diferentes: `28/12/2024-05/01/2025`
  - Seleção visual de início e fim
  - Range destacado visualmente no calendário
  - Botões "Limpar" e "Confirmar"
- 🎨 **Date Pickers em TODOS os screens CRUD**
  - **Projetos:** Campo "Período do Projeto" único (DateRangePickerDropdown)
    - Substituído dois campos separados (Data Início + Data Fim)
    - Layout mais limpo e intuitivo
    - Formato inteligente no display
  - **Despesas:** DatePickerDropdown para "Data" e "Data Pagamento"
  - **Boletins:** DatePickerDropdown para "Data Emissão" (default=hoje)
  - **Orçamentos:** Substituídos antigos DatePickerEntry e DateRangePicker
  - **Equipamento:** DatePickerDropdown para "Data Compra"
  - **Fornecedores:** DatePickerDropdown para "Validade Seguro Trabalho"
- 🎨 **Fornecedores: Campo Website com Link Clicável**
  - Campo de texto para URL do website
  - Botão "🔗 Abrir" que abre URL no browser
  - Adiciona automaticamente `https://` se necessário
  - Integrado com módulo `webbrowser` do Python
- 🎨 **Fornecedores: Seguro visível apenas para FREELANCER**
  - Campo "Validade Seguro Trabalho" só aparece se Estatuto = FREELANCER
  - Toggle dinâmico ao mudar radio buttons de estatuto
  - Método `_toggle_seguro_field()` com pack/pack_forget

### 🐛 Corrigido
- **AttributeError:** `'str' object has no attribute 'winfo_children'`
  - Adicionado `isinstance(widget, str)` check no `_check_click_outside()`
  - Proteção com `hasattr()` antes de chamar métodos de widget
- **ValueError:** `'width' and 'height' must be passed to constructor`
  - Movido `width` e `height` do `place()` para o construtor do `CTkFrame`
  - Compliance com constraints do CustomTkinter
- **ImportError:** `cannot import name 'engine' from 'database.models.base'`
  - Script `run_migration_012.py` tentava importar engine não exportado
  - Corrigido: engine criado localmente com `create_engine()`
  - Carrega DATABASE_URL do .env com fallback
- **TypeError:** `FornecedoresManager.atualizar() got an unexpected keyword argument 'website'`
  - Parâmetro `website` não estava nos métodos `criar()` e `atualizar()`
  - Adicionado parâmetro em ambos os métodos
  - Incluída lógica de criação e update do campo website
- **TclError:** `window isn't packed` ao fazer toggle de seguro_frame
  - Pack inicial do seguro_frame causava conflito com toggle
  - Removido pack() inicial, agora controlado apenas por `_toggle_seguro_field()`
  - Corrigido `before=self.nota_entry.master` para `before=self.nota_entry`

### 📝 Ficheiros Alterados
- `ui/components/date_picker_dropdown.py` - Bug fixes e comentários
- `ui/components/date_range_picker_dropdown.py` - Formato inteligente + bug fixes
- `ui/screens/projetos.py` - Campo "Período do Projeto" único
- `ui/screens/despesas.py` - DatePickerDropdown para Data e Data Pagamento
- `ui/screens/boletins.py` - DatePickerDropdown para Data Emissão
- `ui/screens/orcamentos.py` - Substituir antigos date pickers
- `ui/screens/equipamento.py` - DatePickerDropdown para Data Compra
- `ui/screens/fornecedores.py` - Website clicável + Seguro dinâmico + Bug fixes
- `logic/fornecedores.py` - Adicionado parâmetro website aos métodos criar/atualizar
- `database/models/fornecedor.py` - Adicionada coluna `website`
- `database/migrations/012_add_website_to_fornecedor.py` - Migration criada
- `run_migration_012.py` - Script de migration corrigido

### 🔧 Documentação
- Atualizado `SESSION_IMPORT.md` - Workflow mais claro com fluxograma
- Atualizado `memory/README.md` - Sistema de "frase-chave" para atualizar docs
- Atualizado `README.md` - Frase Mágica v2.0 (ordem garantida)

---

## [2025-11-11] Navegação Clicável em Saldos Pessoais

### ✨ Adicionado
- 🎨 **Navegação clicável completa em Saldos Pessoais**
  - 10 botões clicáveis com navegação automática e filtros aplicados
  - INs: Projetos Pessoais, Prémios (para cada sócio)
  - OUTs: Despesas Fixas, Boletins Pendentes, Boletins Pagos, Despesas Pessoais
- 🎨 **Cores semânticas consistentes**
  - Verde (#E8F5E0/#4A7028) para INs - match Recebido
  - Laranja (#FFE5D0/#8B4513) para OUTs - match Não Faturado
- 🖼️ **Ícones PNG customizados**
  - ins.png e outs.png (convertidos para Base64)
  - Substituem emojis 💰 e 💸
- ✨ **Efeitos hover profissionais**
  - Border width aumenta 2→3 pixels
  - Cursor hand2 em toda a extensão do card
  - Texto branco para melhor contraste

### 🔧 Alterado
- **Boletins** separados em duas linhas: "Boletins pendentes" e "Boletins pagos"
- **Títulos** simplificados: "INs (Entradas)" → "INs" e "OUTs (Saídas)" → "OUTs"
- **TOTAL** sem bullet point (separadores visuais em vez de "• TOTAL")
- Filtros propagados para Projetos, Despesas, Boletins (filtro_tipo, filtro_premio_socio, filtro_estado, filtro_socio)

### 🐛 Problemas Identificados
- **Scroll em popup de Projetos** propaga para lista por trás
  - Múltiplas tentativas: bind_all, event detection, unbind parent
  - Código implementado mas ainda não resolvido
  - Documentado em memory/TODO.md como Alta Prioridade

### 📝 Ficheiros Alterados
- `ui/screens/saldos.py` - Navegação, cores, ícones, boletins separados
- `logic/saldos.py` - Boletins separados em pendentes/pagos
- `assets/resources.py` - Novos ícones INS e OUTS (Base64)
- `ui/main_window.py` - Propagação de filtros (show_projetos, show_despesas, show_boletins)
- `ui/screens/projetos.py` - Tentativa de fix para scroll no popup
- `ui/screens/despesas.py` - Suporte para filtro_tipo
- `ui/screens/boletins.py` - Suporte para filtro_socio

---

## [2025-11-09] Sistema de Memória & Ícones Completo

### ✨ Adicionado
- 🧠 **Sistema de Memória** completo em `/memory/`
  - `CURRENT_STATE.md` - estado atual do projeto
  - `ARCHITECTURE.md` - arquitetura detalhada
  - `DECISIONS.md` - decisões técnicas registadas
  - `CHANGELOG.md` - este ficheiro
  - `README.md` - guia do sistema de memória
- 🎨 **Ícones PNG aplicados a TODAS as screens**
  - Dashboard, Saldos, Projetos, Orçamentos, Despesas
  - Boletins, Clientes, Fornecedores, Equipamento, Relatórios
- 🖼️ **Logos PNG de alta qualidade** (fornecidos manualmente)
  - 71KB e 156KB (muito melhor que os 4KB-17KB anteriores)
  - Sistema de PNGs manuais (não conversão automática)

### 🔧 Alterado
- Movidos ficheiros de dev para `/memory/`
  - `GUIA_COMPLETO.md`
  - `PLANO_ORCAMENTOS.md`
  - `TODO.md`
  - `BUILD_ASSETS_README.md` → `ASSET_SYSTEM.md`
- Sistema de assets simplificado (PNGs manuais)

### 🗑️ Removido
- Scripts de conversão automática SVG→PNG
  - `extract_logo_png.py`
  - `build_assets.py` → deprecado para `_build_assets.py.deprecated`
- `logo_original.png` (temporário, não necessário)

---

## [2025-11-08] Sistema de Ícones Base64

### ✨ Adicionado
- Sistema de ícones PNG embutidos como Base64
- Ícones aplicados na sidebar (10 menus)
- Conversão automática Excel→Base64 (`convert_icons_to_base64.py`)
- 10 ícones PNG profissionais

### 🔧 Alterado
- Sidebar usa ícones PNG em vez de emojis
- Sistema de fallback para ícones (Base64 → Emoji)

---

## [2025-11-07] Importação de Dados Legados

### ✨ Adicionado
- Script de importação Excel → SQLite
- Mapeamento de dados antigos para novo schema
- Validações e limpeza de dados
- Documentação em `IMPORTACAO_*.md`

### 🐛 Corrigido
- Encoding issues com dados portugueses
- Conversão de datas inconsistentes
- Valores decimais com vírgula vs ponto

---

## [2025-11-06] Sistema de Orçamentos

### ✨ Adicionado
- Model `Orcamento` com versões
- Screen de gestão de orçamentos
- Estados: Pendente, Aprovado, Rejeitado
- Integração com Clientes

### 📝 Documentação
- `PLANO_ORCAMENTOS.md` - plano completo da feature

---

## [2025-11-05] Core Features Completas

### ✨ Adicionado
- **Saldos Pessoais** (CORE) - cálculo 50/50
- **Projetos** - gestão completa
- **Despesas** - gestão completa
- **Boletins** - gestão completa
- **Clientes** - gestão completa
- **Fornecedores** - gestão completa
- **Relatórios** - exportação Excel

### 🔧 Alterado
- DataTable V2 - componente melhorado
- Forms reutilizáveis

---

## [2025-11-04] Setup Inicial

### ✨ Adicionado
- Estrutura base do projeto
- SQLAlchemy + Alembic
- CustomTkinter UI
- Models base: Sócio, Projeto, Despesa, Boletim
- Dashboard inicial

### 📝 Documentação
- `README.md` - setup e uso básico
- `GUIA_COMPLETO.md` - documentação detalhada

---

## Formato

Seguimos [Keep a Changelog](https://keepachangelog.com/):
- **Adicionado** - novas features
- **Alterado** - mudanças em features existentes
- **Deprecado** - features que serão removidas
- **Removido** - features removidas
- **Corrigido** - bug fixes
- **Segurança** - vulnerabilidades

---

**Mantido por:** Equipa Agora
