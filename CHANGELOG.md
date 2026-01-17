# Changelog - Agora Contabilidade

All notable changes to this project will be documented in this file.

## [0.2.43] - 2026-01-17

### Changed - UI/UX Improvements

#### 1. Nomenclatura Simplificada
- **"Número" → "ID"**
  - Alterado em todos os modelos: Cliente, Fornecedor, Projeto, Despesa, Boletim, Equipamento
  - Objetivo: Terminologia mais concisa e internacional
  - Afeta: Formulários de criação/edição, colunas de listagem, labels

- **"Sócio Responsável" → "Gestor"**
  - Alterado nos modelos: Projeto, Orçamento
  - Objetivo: Termo mais claro e direto para o papel de gestão
  - Afeta: Formulários de projeto/orçamento, filtros, colunas

#### 2. Listas Admin Mais Limpas
- **Removida coluna "Criado em" de todas as listas**
  - Afeta: Sócios, Clientes, Fornecedores, Projetos, Despesas Templates, Despesas, Boletins, Linhas de Boletim, Equipamento, Orçamentos
  - Objetivo: Reduzir ruído visual e focar em informação relevante
  - Nota: Campo ainda disponível na visualização detalhada de cada registo

#### 3. Ficheiros Alterados
- **`core/models.py`**:
  - 7× alterações: `verbose_name=_('Número')` → `verbose_name=_('ID')`
  - 2× alterações: `verbose_name=_('Sócio Responsável')` → `verbose_name=_('Gestor')`

- **`core/admin.py`**:
  - 10× remoções de `'created_at'` dos `list_display`
  - 3× remoções de `'created_at_formatted'` dos `list_display`

#### 4. Impacto
- ✅ Melhor legibilidade das listas admin
- ✅ Terminologia mais consistente e profissional
- ✅ Redução de scroll horizontal em ecrãs pequenos
- ⚠️ Não afeta dados ou funcionalidade - apenas labels

---

## [0.2.42] - 2026-01-16

### Added - Total de Seleção com Floating Box

#### 1. Caixa Flutuante de Total sem IVA
- **Implementada caixa flutuante no canto inferior direito que mostra totais de seleção**
  - Formato: "X Projetos selecionados | TOTAL sem IVA: €12.345,67"
  - Deteta automaticamente o tipo de entidade (Projetos, Despesas ou Boletins)
  - Aparece apenas quando há registos selecionados com valores
  - Desaparece automaticamente quando não há seleção
  - Estilo integrado com tema Unfold (fundo branco, bordas cinza, sombra suave)
  - Total em cor dourada (#D4AF37) para destaque

#### 2. Funcionalidade Técnica
- **Parse robusto de valores monetários portugueses:**
  - Suporta formato "250,00 €", "1.234,56 €", etc.
  - Remove símbolos €, espaços, pontos de milhar
  - Converte vírgula decimal para ponto
  - Validação com `isNaN()` para segurança
- **Seleção de colunas inteligente:**
  - Procura por `.field-valor_sem_iva` primeiro
  - Fallback para `.field-valor`
  - Fallback para qualquer `td[class*="valor"]`
- **Event listeners otimizados:**
  - Evento `change` em checkboxes individuais
  - Evento `change` no checkbox "Selecionar todos"
  - Timeout de 500ms no carregamento para garantir DOM pronto
  - Atualização em tempo real sem recarregar página

#### 3. Resolução de Problemas Técnicos
- **Problema:** Template skeleton.html não incluía JavaScript customizado
  - **Solução:** Adicionado `<script src="{% static 'js/admin_custom.js' %}">` ao template
  - **Local:** `core/templates/unfold/layouts/skeleton.html` no bloco `extrahead`
- **Problema:** Selector `.paginator` não existe no Unfold 0.75.0
  - **Solução:** Mudado para floating box com `position: fixed`
  - **Benefício:** Sempre visível independente da estrutura do DOM
- **Problema:** Cache busting não funcionava com `docker compose restart`
  - **Solução:** Usar sempre `docker compose up -d --build web` para mudanças
  - **Documentado:** em `.claude/claude.md` secção "Docker Code Not Updating"

#### 4. Ficheiros Alterados
- **`static/js/admin_custom.js`** (v7.0.0-production):
  - Função `parseMoneyValue(text)` - parse de valores PT
  - Função `updateSelectionTotal()` - lógica principal
  - Função `initSelectionTotalListeners()` - setup de event listeners
  - Auto-deteção de tipo de entidade (Projetos/Despesas/Boletins)
  - Floating box com estilo Unfold integrado
- **`core/templates/unfold/layouts/skeleton.html`**:
  - Adicionado `{% load static %}` no topo
  - Adicionado `<script src="{% static 'js/admin_custom.js' %}?v=7.0.0-production">`
- **`config/settings.py`**:
  - Mantém funções `get_custom_js()` e `get_custom_css()` para cache busting
  - Configurado em `UNFOLD['SCRIPTS']` e `UNFOLD['STYLES']`

#### 5. Testing & Debug
- Testado com seleção de 1, 10, 81 projetos
- Verificado cálculo correto de totais (somou €84.917,47 em 81 projetos)
- Testado "Selecionar todos" e desseleção
- Validado formato de números português
- Confirmado aparecimento/desaparecimento automático da caixa

## [2.3.7] - 2026-01-16

### Changed - Usar Dropdown de Ações Nativo do Unfold

#### 1. Reverter para Dropdown de Ações (Melhor UX)
- **Removidos botões de ação no cabeçalho, voltando ao dropdown nativo do Unfold 0.75.0**
  - Dropdown do Unfold 0.75.0 tem UX superior ao da versão 0.20.0
  - Interface mais limpa e consistente
  - Todas as ações (Remover, Exportar PDF, Exportar Excel) agora no dropdown
- **Mudanças no código:**
  - Removido `actions_list_hide_default` do UnfoldHistoryAdmin
  - Mudado `actions_list` para `actions` em todos os admins
  - Removido JavaScript de enable/disable de botões (não necessário)
  - Removido CSS de botões disabled (não necessário)
  - Cache busting atualizado para v2.3.7
- **Ficheiros alterados:**
  - `core/admin.py` - actions_list → actions
  - `static/css/admin_custom.css` - removido CSS de action buttons
  - `static/js/admin_custom.js` - removido JS de action buttons
  - `config/settings.py` - cache busting v2.3.7

## [2.3.6] - 2026-01-16

### Changed - Atualização Major do Unfold Admin Theme

#### 1. Upgrade Unfold 0.20.0 → 0.75.0
- **Atualizado django-unfold de 0.20.0 para 0.75.0** (55 versões!)
  - Mais de 1 ano de melhorias, bug fixes e novas funcionalidades
  - Suporte nativo para `actions_list_hide_default` (adicionado na v0.70.0)
  - Melhorias de performance e UI/UX
  - Compatível com Django 5.0
- **Mudanças no código:**
  - Adicionado `actions_list_hide_default = True` no UnfoldHistoryAdmin (agora funciona nativamente)
  - Removido CSS manual para esconder dropdown (Unfold faz isso nativamente)
  - Cache busting atualizado para v2.3.6
- **Ficheiros alterados:**
  - `requirements.txt` - django-unfold==0.75.0
  - `core/admin.py` - actions_list_hide_default nativo
  - `static/css/admin_custom.css` - removido CSS hack
  - `config/settings.py` - cache busting v2.3.6
- **Referências:**
  - [Unfold 0.75.0 Release](https://pypi.org/project/django-unfold/0.75.0/)
  - [Unfold Documentation](https://unfoldadmin.com/docs/)
  - [Unfold GitHub Releases](https://github.com/unfoldadmin/django-unfold/releases)

## [2.3.5] - 2026-01-16

### Changed - Melhorias de UX em Listas

#### 1. Botões de Ação Substituem Dropdown
- **Dropdown de ações removido, substituído por botões visíveis**
  - Usado `actions_list` (botões no topo) ao invés de dropdown padrão
  - Configurado `actions_list_hide_default = True` no UnfoldHistoryAdmin para esconder dropdown nativo
  - Botões "Remover", "Exportar PDF" e "Exportar Excel" aparecem como botões no topo da lista
  - **Adicionada ação `delete_selected`** com permissões corretas
  - Aplicado em todos os admins: ClienteAdmin, FornecedorAdmin, ProjetoAdmin, DespesaAdmin, BoletimAdmin, OrcamentoAdmin
  - Substituído decorator `@admin.action` por `@action` do Unfold
- **Botões aparecem desabilitados quando nada está selecionado**
  - CSS customizado: `opacity: 0.4`, `cursor: not-allowed`, `pointer-events: none`
  - JavaScript gerencia estado dos botões baseado na seleção de checkboxes
  - MutationObserver detecta botões carregados dinamicamente
  - Sem hover effect quando desabilitado
  - Compatível com dark mode
- **Correções aplicadas:**
  - Adicionado `permissions=['delete']` ao decorator de `delete_selected`
  - Implementado `has_delete_permission()` no UnfoldHistoryAdmin
  - Usado propriedade nativa `actions_list_hide_default = True` conforme documentação oficial
- **Código:**
  - `core/admin.py` - configuração `actions_list` + `actions_list_hide_default = True` em UnfoldHistoryAdmin
  - `static/css/admin_custom.css` - estilos para estado desabilitado
  - `static/js/admin_custom.js` - lógica enable/disable dinâmica com console.log para debug
- **Referência:** [Unfold Actions Documentation](https://unfoldadmin.com/docs/actions/introduction/)

#### 2. Tooltips em Campos Truncados
- **Adicionados tooltips HTML em todos os campos truncados**
  - Ao passar o rato sobre texto truncado (`...`), mostra o texto completo
  - Implementado nos seguintes campos:
    - **ProjetoAdmin:** `descricao_short` (truncado em 50 caracteres)
    - **DespesaTemplateAdmin:** `descricao_short` (truncado em 30 caracteres)
    - **DespesaAdmin:** `descricao_short` (truncado em 30 caracteres)
    - **BoletimLinhaAdmin:** `servico_short` (truncado em 30 caracteres)
    - **OrcamentoItemAdmin:** `descricao_short` (truncado em 50 caracteres)
  - Usa `format_html()` com atributo `title` para tooltip nativo do browser
  - Código: todos os métodos `*_short()` em `core/admin.py`

### Changed - Melhorias nos Campos de Data

#### 3. Formato de Datas DD/MM/AAAA em Todas as Listas
- **Configurado formato global de datas para DD/MM/AAAA**
  - Settings: `DATE_FORMAT = 'd/m/Y'`, `USE_L10N = False`
  - Código: `config/settings.py:118-123`

#### 4. Métodos Formatados para Datas nas Listas
- **Criados métodos `*_formatted()` em todos os admins**
  - **ProjetoAdmin:**
    - `data_faturacao_formatted()` - Data Faturação
    - `data_recibo_formatted()` - Data Pagamento
    - `created_at_formatted()` - Criado em
  - **DespesaAdmin:**
    - `data_formatted()` - Data
    - `data_pagamento_formatted()` - Data Pagamento
    - `created_at_formatted()` - Criado em
  - **BoletimAdmin:**
    - `data_emissao_formatted()` - Data Emissão
    - `data_pagamento_formatted()` - Data Pagamento
    - `created_at_formatted()` - Criado em
  - **BoletimLinhaAdmin:**
    - `data_inicio_formatted()` - Data Início
    - `data_fim_formatted()` - Data Fim
    - `created_at_formatted()` - Criado em
  - **OrcamentoAdmin:**
    - `data_criacao_formatted()` - Data Criação
    - `created_at_formatted()` - Criado em

#### 5. UX Melhorado para Período do Projeto
- **Campos de data lado a lado no formulário de projetos**
  - `data_inicio` e `data_fim` aparecem na mesma linha
  - Descrição adicionada ao fieldset: "Período do projeto e datas de faturação/pagamento"
  - Código: `core/admin.py:471-473`

#### 6. Help Texts Claros em Todos os Campos de Data
- **Adicionados help texts descritivos no modelo Projeto**
  - `data_inicio`: "Início do período de execução do projeto"
  - `data_fim`: "Fim do período de execução do projeto"
  - `data_faturacao`: "Data em que a fatura foi emitida"
  - `data_vencimento`: "Prazo acordado para pagamento (deadline)"
  - `data_recibo` → renomeado para **"Data Pagamento"**: "Data em que o cliente efetivamente pagou o projeto"
  - Código: `core/models.py:261-311`

### Technical Details
- **Arquivos modificados:**
  - `agora_web/config/settings.py`: Formato global de datas
  - `agora_web/core/admin.py`: Métodos formatados em todos os admins
  - `agora_web/core/models.py`: Help texts nos campos de data do Projeto
- **Testing:**
  - Todas as listas mostram datas no formato DD/MM/AAAA ✅
  - Campos de período lado a lado no formulário ✅
  - Help texts visíveis ao preencher campos ✅

## [2.3.4] - 2026-01-14

### Added - Auto-Preenchimento de Códigos Sequenciais

#### 1. Próximo Código na Sequência
- **Implementado `get_changeform_initial_data()` no `UnfoldHistoryAdmin`**
  - Calcula automaticamente o próximo código disponível ao criar novos objetos
  - Usa regex para encontrar o maior número existente e incrementa
  - Formatos suportados: `#P0081`, `#D000336`, `#C0023`, `#F0047`, `#E000028`, `#TD000001`
  - Código: `core/admin.py:107-166`

#### 2. Modelos com Auto-Preenchimento
- **Projeto:** `#P0001` → `#P9999` (4 dígitos)
- **Despesa:** `#D000001` → `#D999999` (6 dígitos)
- **Cliente:** `#C0001` → `#C9999` (4 dígitos)
- **Fornecedor:** `#F0001` → `#F9999` (4 dígitos)
- **Equipamento:** `#E000001` → `#E999999` (6 dígitos)
- **DespesaTemplate:** `#TD000001` → `#TD999999` (6 dígitos)
- **Boletim:** Não implementado (usa formato especial `#B-{SOCIO}-{ANO}-{MÊS}`)

### Added - Campo Data Recibo em Projetos

#### 3. Campo Data Recibo Visível e Editável
- **Adicionado `data_recibo` aos fieldsets do ProjetoAdmin**
  - Campo aparece na secção "Datas" no formulário de edição
  - Campo aparece também na lista de projetos (`list_display`)
  - Código: `core/admin.py:472` e `core/admin.py:444`

#### 4. Importância do Campo
- **Campo `data_recibo` é CRÍTICO para cálculo de saldos**
  - Sistema de Saldos Pessoais (`core/utils/saldos.py`) só conta projetos pessoais que têm `data_recibo`
  - Representa quando o cliente efetivamente pagou (dinheiro entrou)
  - Projetos com `estado=PAGO` mas sem `data_recibo` **NÃO aparecem nos saldos**
  - **NOTA:** Lógica de saldos precisa de revisão futura para melhor clareza

### Changed - Melhorias de UI/UX (continuação v2.3.3)

#### 5. Remoção da Barra de Pesquisa da Sidebar
- (Já documentado em v2.3.3)

### Technical Details
- **Arquivos modificados:**
  - `agora_web/core/admin.py`:
    - Adicionado `get_changeform_initial_data()` ao `UnfoldHistoryAdmin`
    - Adicionado `data_recibo` aos fieldsets e list_display de ProjetoAdmin
- **Testing:**
  - Testado auto-preenchimento via Django shell - todos os formatos corretos ✅
  - Campo `data_recibo` confirmado visível no formulário ✅

### Known Issues
- **Lógica de Saldos Pessoais precisa de revisão:** ⚠️ **DOCUMENTADO**
  - Confusão entre `estado=PAGO`, `data_recibo`, `data_faturacao`
  - Projetos pagos podem não aparecer nos saldos se faltarem campos
  - Projetos `CANCELADO` não são excluídos (contam incorretamente)
  - Falta categoria "A Receber" para projetos `FINALIZADO` sem `data_recibo`
  - **Especificação completa:** `docs/SALDOS_REVISION_SPEC.md`
  - **Status:** 📝 Aprovado, aguarda implementação (estimativa: 3-4h)

---

## [2.3.3] - 2026-01-14

### Fixed - Bug Crítico ao Adicionar Novos Objetos

#### 1. Erro 500 na Página de Criação
- **Problema:** Erro "Unknown field(s) (history_link) specified" ao tentar adicionar novos projetos (ou qualquer modelo com histórico)
- **Causa raiz:** Campo `history_link` estava hardcoded nos fieldsets mas só funciona quando o objeto já existe (tem `pk`)
- **Impacto:** Impossível criar novos Projetos, Despesas, Clientes, etc. via admin (erro 500)

#### 2. Solução Implementada
- **Adicionado `get_fieldsets()` ao `UnfoldHistoryAdmin`**
  - Remove dinamicamente o campo `history_link` dos fieldsets quando `obj is None` (modo criação)
  - Mantém o campo quando `obj.pk` existe (modo edição)
  - Aplica-se automaticamente a todos os modelos que herdam de `UnfoldHistoryAdmin`
  - Código: `core/admin.py:87-105`

#### 3. Comportamento Correto
- **Página de criação (Add):** Não mostra link de histórico (porque não há histórico ainda)
- **Página de edição (Change):** Mostra link "Ver Histórico" no fieldset Metadata
- **Todos os modelos afetados:** Projeto, Despesa, Cliente, Fornecedor, Boletim, Equipamento, Orcamento, Socio, DespesaTemplate, ImportacaoDados

### Changed - Melhorias de UI/UX

#### 4. Remoção da Barra de Pesquisa da Sidebar
- **Configuração:** `UNFOLD["SIDEBAR"]["show_search"]` alterado para `False`
- **Motivo:** Simplificar interface e reduzir clutter visual
- **Ficheiro:** `config/settings.py:209`

### Technical Details
- **Arquivos modificados:**
  - `agora_web/core/admin.py` - Adicionado método `get_fieldsets()` ao `UnfoldHistoryAdmin`
  - `agora_web/config/settings.py` - Desativada barra de pesquisa na sidebar
- **Testing:**
  - Testado via Django shell com `add_view()` - Status 200 ✅
  - Verificado que todos os modelos herdam a correção automaticamente

---

## [2.3.2] - 2026-01-13

### Added - Melhorias de UI nas Listas do Admin

#### 1. Efeito Hover Interativo nas Linhas
- **Hover visual suave nas tabelas de lista**
  - Cor dourada (#D4AF37) com opacidade 8% seguindo tema Agora
  - Transição suave de 0.2s para melhor experiência
  - Leve movimento para direita (2px) ao fazer hover
  - Box-shadow sutil para elevação visual
  - Compatível com tema claro e escuro do Unfold
  - CSS: `static/css/admin_custom.css`

#### 2. Linhas Totalmente Clicáveis
- **JavaScript customizado para navegação intuitiva**
  - Clique em qualquer parte da linha para abrir o item
  - Suporte para Ctrl/Cmd+Click para abrir em nova aba
  - Preserva funcionalidade de elementos interativos (checkboxes, botões, links)
  - Múltiplos seletores para compatibilidade (Django Admin padrão + Unfold)
  - MutationObserver para conteúdo carregado dinamicamente
  - Logging detalhado no console para debugging
  - JavaScript: `static/js/admin_custom.js`

#### 3. Integração com Unfold Theme
- **Configuração via UNFOLD settings:**
  - `UNFOLD["STYLES"]` carrega CSS customizado via função helper
  - `UNFOLD["SCRIPTS"]` carrega JavaScript via função helper
  - Template customizado: `core/templates/admin/base_site.html`
  - Funções helper em `config/settings.py`: `get_custom_css()`, `get_custom_js()`

#### 4. Acessibilidade Mantida
- **Foco de teclado visível:**
  - Outline dourado em elementos focados
  - Navegação por teclado preservada
  - Screen readers compatíveis

### Technical Details
- **Arquivos criados:**
  - `agora_web/static/css/admin_custom.css` - 109 linhas
  - `agora_web/static/js/admin_custom.js` - 107 linhas
  - `agora_web/core/templates/admin/base_site.html`
- **Arquivos modificados:**
  - `agora_web/config/settings.py` - Adicionadas funções helper e config UNFOLD
- **Commits:**
  - `9f07810` - feat: adicionar efeito hover e linhas clicáveis nas listas do admin
  - `aa19f3b` - fix: tornar linhas das listas realmente clicáveis com JavaScript
  - `07b2a8e` - fix: corrigir funcionalidade de clique nas linhas com JavaScript robusto

---

## [2.3.1] - 2026-01-13

### Added - Sistema de Histórico e Auditoria Completo

#### 1. Comparação Visual Campo-a-Campo
- **Visual diff implementado na página de histórico**
  - Compara automaticamente versões consecutivas de cada objeto
  - Mostra apenas campos que mudaram em cada edição
  - Valores antigos (vermelho riscado) → valores novos (verde)
  - Trunca valores longos (máx 100 caracteres)
  - Identifica primeira versão vs alterações subsequentes
  - Método: `UnfoldHistoryAdmin.history_view()` (`admin.py:104-177`)

#### 2. Interface Unfold Completa
- **Layout admin completo na página de histórico**
  - Sidebar com navegação completa
  - Header com logo e user menu
  - Breadcrumbs clicáveis (Home > App > Model > Object > History)
  - Contexto admin completo via `self.admin_site.each_context(request)`
  - Template: `core/templates/simple_history/object_history.html`

#### 3. UI/UX Melhorias
- **Badges coloridos por tipo de operação:**
  - 🟢 Verde: Criado
  - 🔵 Azul: Atualizado
  - 🔴 Vermelho: Eliminado
- **Cards estilizados:**
  - Sombra e bordas arredondadas
  - Separadores visuais entre versões
  - CSS inline para consistência
- **Formatação portuguesa:**
  - Datas: dd/mm/YYYY HH:MM
  - Labels: "Criado", "Atualizado", "Eliminado"
  - User: fullname ou username

### Fixed - Correções Críticas no Sistema de Histórico

#### Issue #1: Tabelas Historical* Não Existiam
- **Sintoma:** Error 500 ao clicar "Ver Histórico"
- **Causa:** Comando `populate_history` nunca foi executado
- **Fix:**
  ```bash
  docker compose exec web python manage.py populate_history --auto
  ```
- **Resultado:** 9 tabelas criadas (core_historicalsocio, core_historicalcliente, etc.)

#### Issue #2: Signals Não Capturavam User
- **Sintoma:** Campos `created_by` e `updated_by` sempre NULL
- **Causa:** `get_current_user()` usando API incorreta para django-simple-history v3.4.0
- **Fix:** Corrigido para usar `HistoricalRecords.context.request.user` (`signals.py:26-30`)
- **Resultado:** User agora capturado corretamente em todas as edições

#### Issue #3: Template Sem Layout Unfold
- **Sintoma:** Página de histórico sem sidebar/header (só footer)
- **Causa:** Faltava `self.admin_site.each_context(request)` no contexto do template
- **Fix:** Adicionado contexto completo do admin (`admin.py:161-162`)
- **Resultado:** Sidebar, header e navegação completa agora aparecem

#### Issue #4: AttributeError ao Processar Histórico
- **Sintoma:** `property 'prev_record' of 'HistoricalProjeto' object has no setter`
- **Causa:** Tentativa de atribuir propriedades a objetos HistoricalRecord (read-only)
- **Fix:** Usar dicionários simples como wrappers (`admin.py:120-158`)
- **Resultado:** Processamento de versões funciona sem erros

#### Issue #5: Cache Django Bloqueava Template Changes
- **Sintoma:** Mudanças no template não apareciam após rebuild
- **Causa:** Django cacheia templates compilados
- **Fix:**
  ```bash
  docker compose exec web python manage.py shell -c "from django.core.cache import cache; cache.clear()"
  ```
- **Resultado:** Templates atualizam corretamente após rebuild

### Changed - Limpeza de Código

- **Removidos logs de debug** dos signals (`signals.py:43-67`)
  - Logging completo para troubleshooting foi removido
  - Mantido apenas exception handling essencial
  - Código production-ready

### Documentation

- **docs/audit-trail-implementation.md** atualizado (preservando histórico original)
  - Status de todos os bugs marcado como RESOLVIDO
  - Adicionadas instruções de troubleshooting
  - Exemplos visuais da interface

### Technical Details

**Files Modified:**
- `agora_web/core/admin.py`:
  - Método `history_view()` com comparação campo-a-campo (linhas 104-177)
  - Uso de dicionários wrapper para evitar AttributeError
  - Contexto admin completo com `each_context()`

- `agora_web/core/signals.py`:
  - Corrigido `get_current_user()` para API v3.4.0 (linhas 26-30)
  - Removidos logs de debug (código limpo)

- `agora_web/core/templates/simple_history/object_history.html`:
  - Template completo com layout Unfold
  - Breadcrumbs usando `unfold/helpers/breadcrumb_item.html`
  - Containers Tailwind CSS (`px-4 lg:px-12`, `container mx-auto`)
  - Loop de diff campo-a-campo (linhas 142-150)

**Testing:**
- [x] Histórico abre sem erro 500
- [x] Sidebar e header aparecem corretamente
- [x] Badges coloridos por tipo de operação
- [x] Comparação campo-a-campo funcional
- [x] Valores antigos → novos visíveis
- [x] User tracking funciona (created_by/updated_by)
- [x] Breadcrumbs clicáveis
- [x] Formatação PT (datas, labels)

**Known Limitations:**
- Histórico só funciona para objetos editados via Django ORM (não SQL direto)
- Objetos criados antes da implementação têm created_by/updated_by NULL
- Tabelas Historical* podem crescer muito (considerar archiving periódico)

**Commits:**
- feat: implementar sistema completo de histórico e auditoria (351aae8)

---

## [2.3.0] - 2026-01-13

### Added - Dashboard do Sócio e Sistema de Relatórios

#### 1. Dashboard do Sócio
- **Nova página de dashboard para sócios** com estatísticas personalizadas
  - Rota: `/admin/core/socio/<codigo>/dashboard/`
  - Template: `agora_web/core/templates/admin/core/socio/dashboard.html`
  - Mostra: Projetos Pessoais, Despesas Pessoais, Clientes Angariados
  - Cards clicáveis que levam às listas filtradas
  - Logo amarelo consistente com resto da aplicação

- **Novo campo `angariador` no modelo Cliente** (`models.py:148`)
  - ForeignKey para Socio (identificar quem angariou cada cliente)
  - Migração manual via SQL (devido a problemas com migrations anteriores)
  - Ficheiro: `agora_web/core/migrations/0010_add_angariador_to_cliente.py`
  - Tabelas atualizadas: `clientes` + `core_historicalcliente` (django-simple-history)

- **Método `get_num_clientes_angariados()` no modelo Socio** (`models.py:86-89`)
  - Conta clientes angariados por cada sócio

#### 2. Sistema de Relatórios (PDF e Excel)
- **Relatórios implementados para 5 tipos de listas:**
  - ✅ Projetos (já existia, mantido)
  - ✅ Despesas (NOVO)
  - ✅ Clientes (NOVO)
  - ✅ Fornecedores (NOVO)
  - ✅ Boletins (NOVO)
  - ✅ Orçamentos (NOVO)

- **Classes de relatório em `agora_web/core/utils/relatorios.py`:**
  - `RelatorioDespesas` (linhas 462-618)
  - `RelatorioClientes` (linhas 620-728)
  - `RelatorioFornecedores` (linhas 730-839)
  - `RelatorioBoletins` (linhas 841-963)
  - `RelatorioOrcamentos` (linhas 965-1089)

- **Ações de exportação adicionadas aos admins:**
  - DespesaAdmin: `exportar_pdf`, `exportar_excel`
  - ClienteAdmin: `exportar_pdf`, `exportar_excel`
  - FornecedorAdmin: `exportar_pdf`, `exportar_excel`
  - BoletimAdmin: `exportar_pdf`, `exportar_excel`
  - OrcamentoAdmin: `exportar_pdf`, `exportar_excel`

### Fixed - Filtros no Django Admin

#### 1. Filtros Customizados para evitar erro 400
- **Problema:** Filtros com ForeignKey usando CharField como PK causavam erro 400
  - Exemplos: Socio (PK='BA'/'RR'), Angariador
  - Causa: Django/Unfold tentava fazer AJAX lookup que falhava

- **Solução:** Criados filtros `SimpleListFilter` customizados
  - `SocioListFilter` (`admin.py:19-31`)
  - `AngariadorListFilter` (`admin.py:34-46`)
  - `TagListFilter` (`admin.py:49-62`) - Para ManyToManyField de tags

- **Admins atualizados:**
  - ProjetoAdmin: Usa `SocioListFilter`
  - ClienteAdmin: Usa `AngariadorListFilter`
  - DespesaAdmin: Usa `TagListFilter`
  - BoletimAdmin: Usa `SocioListFilter`
  - OrcamentoAdmin: Usa `SocioListFilter`

#### 2. Correção de método no modelo Socio
- **Bug:** `get_num_despesas_pessoais()` filtrava por tag `PESSOAL` genérica
  - Problema: Tags reais são `PESSOAL_BA` e `PESSOAL_RR`
  - Resultado: Mostrava sempre 0 despesas

- **Fix:** Método agora filtra por `PESSOAL_{self.codigo}` (`models.py:78-83`)
  - Bruno Amaral → `PESSOAL_BA`
  - Rafael Reigota → `PESSOAL_RR`

### Changed - Melhorias no Sistema de Relatórios

#### 1. Exclusão de parâmetros internos do Django
- **Problema:** Parâmetros internos apareciam nos nomes dos ficheiros
- **Solução:** Lista de exclusão expandida em todos os métodos `exportar_*`:
  ```python
  exclude_params = ['action', '_selected_action', 'csrfmiddlewaretoken',
                    'select_across', 'index']
  ```
- Aplicado em: ClienteAdmin, FornecedorAdmin, ProjetoAdmin, DespesaAdmin,
  BoletimAdmin, OrcamentoAdmin

#### 2. Correção de nomes de campos em Orçamentos
- **Problema:** Campos do modelo Orcamento estavam incorretos no relatório
- **Fix:** Mapeamento correto dos campos:
  - `numero` → `codigo`
  - `descricao` → `titulo_cliente`
  - `valor` → `valor_total`
  - `estado` → `status`
  - `data_emissao` → `data_criacao`

### Known Issues - Nomes de Ficheiros com Filtros

⚠️ **PENDENTE:** Nomes de ficheiros não incluem filtros aplicados
- **Comportamento esperado:** `despesas_tags_PESSOAL_BA_20260113.pdf`
- **Comportamento atual:** `despesas_20260113.pdf`
- **Causa:** Investigação em curso
- **Código implementado:**
  - Método `_gerar_nome_arquivo()` em todas as classes de relatório
  - Captura de filtros via `request.GET` nas ações de admin
  - Sanitização de valores (substituição de `/` e espaços por `_`)

**Próximos passos:**
1. Adicionar logging para debug (verificar o que está a ser capturado)
2. Validar que os filtros estão a ser passados corretamente
3. Testar com diferentes tipos de filtros

### Technical Details

**Files Created:**
- `agora_web/core/templates/admin/core/socio/dashboard.html` - Dashboard do sócio
- `agora_web/core/migrations/0010_add_angariador_to_cliente.py` - Migração do campo angariador

**Files Modified:**
- `agora_web/core/models.py`:
  - Added `angariador` field to Cliente (line 148)
  - Fixed `get_num_despesas_pessoais()` method (lines 78-83)
  - Added `get_num_clientes_angariados()` method (lines 86-89)

- `agora_web/core/admin.py`:
  - Added custom filters: SocioListFilter, AngariadorListFilter, TagListFilter (lines 19-62)
  - Updated list_filter in ProjetoAdmin, ClienteAdmin, DespesaAdmin, BoletimAdmin, OrcamentoAdmin
  - Added export actions to 5 admins (PDF + Excel)
  - Fixed parameter exclusion in all export methods

- `agora_web/core/utils/relatorios.py`:
  - Added 5 new report classes (RelatorioDespesas, RelatorioClientes, RelatorioFornecedores, RelatorioBoletins, RelatorioOrcamentos)
  - Implemented `_gerar_nome_arquivo()` methods with filter support
  - Fixed Orcamento field mapping

**Database Changes:**
- SQL executado diretamente:
  ```sql
  ALTER TABLE clientes ADD COLUMN angariador_id VARCHAR(2)
    REFERENCES socios(codigo) ON DELETE SET NULL;
  CREATE INDEX clientes_angariador_id_idx ON clientes(angariador_id);
  ALTER TABLE core_historicalcliente ADD COLUMN angariador_id VARCHAR(2);
  ```

**Testing:**
- [x] Dashboard do sócio funcional
- [x] Cards clicáveis levam às listas filtradas
- [x] Filtros customizados resolvem erro 400
- [x] Relatórios PDF/Excel geram corretamente
- [x] Despesas pessoais contam corretamente no dashboard
- [x] Campo angariador visível no admin de clientes
- [ ] Nomes de ficheiros com filtros (PENDENTE)

**Commits:**
- fix: remover listas de projetos e clientes do dashboard do sócio (0c41585)
- fix: inverter fluxo de visualização do sócio (8e87113)
- feat: adicionar angariador e dashboard de estatísticas do sócio (0e7c54e)
- fix: ajustar sistema de relatórios (26b4401)
- feat: implementar sistema completo de relatórios para projetos (464d216)

---

## [2.2.0] - 2026-01-12

### Changed - UI Improvements

- **Logo coloring fixed in Saldos and Fiscal dashboards**
  - Logo now displays in golden color (#d4af37) consistently across all pages
  - Added CSS filter directly to custom dashboard templates (Saldos Pessoais, Estado Fiscal)
  - Issue: Custom dashboards extended `admin/base_site.html` instead of `skeleton.html`
  - Solution: Duplicated logo CSS filter in both templates' extrahead block
  - Files: `agora_web/core/templates/admin/core/saldo/changelist.html`, `agora_web/core/templates/admin/core/fiscal/changelist.html`
  - Commit: 2bb2180

- **Smart search with field prefixes in all list views**
  - Implemented Django search field prefixes for intelligent search prioritization
  - `^field` - Starts with (exact match at beginning, highest priority)
  - `field` - Contains (default)

  **Projetos** (8 searchable fields):
  - Priority: `^numero` (exact code match)
  - Includes: descricao, cliente (nome + nome_formal), tipo, socio, estado, nota

  **Despesas** (10 searchable fields):
  - Priority: `^numero`, `^projeto__numero`
  - Includes: descricao, credor, tags (codigo + nome), tipo_original, estado, nota

  **Boletins** (9 searchable fields):
  - Priority: `^numero`
  - Includes: socio (codigo + nome_completo + nome_curto), mes, ano, estado, descricao, nota

  **Orçamentos** (12 searchable fields):
  - Priority: `^codigo`, `^projeto__numero`
  - Includes: titulo_cliente, cliente, projeto, socio, status, local_evento, descricao_proposta, notas_contratuais, descricao_cliente

  Files: `agora_web/core/admin.py` (lines 148-157, 238-249, 319-329, 464-477)

  **Note:** Full-text search prefix `@` was removed due to Django compatibility issues

- **Date hierarchy filter added to Projetos list**
  - Added `date_hierarchy = 'data_faturacao'` in ProjetoAdmin
  - Enables year/month/day navigation in list header (same as Despesas, Boletins, Orçamentos)
  - File: `agora_web/core/admin.py:160`
  - Commit: 3b0defc

### Added - Progressive Web App (PWA)
- **PWA Manifest** (`/media/manifest.json`)
  - App name, icons, colors, and shortcuts configured
  - Theme color: #d4af37 (golden Agora)
  - Shortcuts to Projetos, Despesas, Saldos
  - Installable on desktop and mobile devices

- **Service Worker** (`/media/sw.js`)
  - Basic offline support with resource caching
  - Version: v1.0.0
  - Scoped to /media/ only for security

- **PWA Meta Tags** (in `core/templates/unfold/layouts/skeleton.html`)
  - theme-color, apple-mobile-web-app-capable, mobile-web-app-capable
  - Open Graph tags for social media
  - Custom install prompt in Portuguese

### Added - Branding System
- **Logo transparente** configured
  - Using `a (yellow).svg` (transparent SVG)
  - Configured in Unfold SITE_LOGO and SITE_ICON
  - Appears in sidebar, favicon, and PWA icons

- **Primary color theme**: #d4af37 (golden Agora)
  - Complete color scale (50-950) in Unfold config
  - Applied to buttons, links, focus states, theme-color

- **Custom Templates**
  - `skeleton.html` - PWA meta tags and Service Worker registration
  - `base_simple.html` - Footer placeholder

### Added - Audit Trail System
- **django-simple-history integration**
  - Complete change history for all models
  - Inline "Ver Histórico" button in change forms
  - Auto-populate created_by/updated_by fields
  - Custom history visualization templates

### Documentation
- **docs/PWA_BRANDING.md** - Complete technical guide
- **BRANDING-PWA-IMPLEMENTATION.md** - Executive summary
- **media/BRANDING-PWA-README.md** - Detailed guide
- **media/logos/PWA-ICONS-README.md** - Icon generation instructions
- **README.md** - Updated with v2.2 release notes
- **docs/README.md** - Updated index with PWA links

### Changed
- **Template loading priority** - core/templates loads first for Unfold overrides
- **Unfold configuration** - Updated with new logo and color scheme
- **README structure** - Added PWA features and audit trail

### Fixed
- Template override structure (using skeleton.html instead of base.html)
- Logo transparency issue (SVG instead of PNG with white background)
- Template discovery by Django (DIRS priority corrected)

### Technical Details
**Commits:** 10 commits including docs
- feat: implementar branding completo e PWA (4b988d0)
- fix: corrigir template PWA para usar skeleton.html (6f3e053)
- fix: priorizar templates do core para override (9b7d92d)
- feat: usar logo novo na sidebar e ícones (f845298)
- fix: usar logo 'a' amarelo transparente (ddc2e1e)
- docs: documentação completa PWA (9ea2f92, f9e0510)

**Files Changed:** 14+ files, 700+ lines added

**Known Issues:**
- PWA icon PNGs not generated yet (192x192, 512x512, apple-touch-icon needed)
- New amp logo has white background (using temporary transparent 'a' logo)
- Login page customization removed (caused template conflicts)

### Testing
- [x] Manifest.json accessible and valid
- [x] Service Worker registered and active
- [x] PWA meta tags present in HTML
- [x] Logo appears in sidebar
- [x] Theme color #d4af37 applied
- [x] Install prompt works (Desktop Chrome)
- [ ] PNG icons generated (pending)
- [ ] Tested on Android/iOS (pending)
- [ ] Lighthouse PWA audit (pending)

---

## [2.1.5] - 2026-01-05

### Fixed - Validação Saldos Excel vs DB
- **Prémios 100% corretos** após correção de cálculo
  - Bruno: €5,844.67 (match perfeito com Excel CAIXA)
  - Rafael: €9,916.19 (match perfeito com Excel CAIXA)
  - Projetos Pessoais Rafael: €14,103.51 (100% match)

- **Correção crítica em prémios** (`import_from_excel.py:372-378, 446`)
  - Column P (TOTAL s/IVA) agora usado para prémios com quantidade/dias
  - Exemplo: #D000120 com quantidade=2 agora calcula €450 em vez de €225
  - Bug fix: prémios estavam a usar valor unitário (Column J) em vez de total

### Added - Sistema de Validação
- **Script crosscheck.py** - Compara Excel vs DB (projetos, despesas, boletins)
- **Documentação completa de validação:**
  - `docs/SALDOS_VALIDATION_RESULTS.md` - Resultados finais com comparações
  - `docs/SALDOS_CROSSCHECK.md` - Análise detalhada de discrepâncias

### Changed - Workflow de Desenvolvimento
- **Documentação atualizada** para refletir workflow real
  - Commits diretos em `main` para agilidade
  - Branches opcionais apenas para experimentação arriscada
  - `README-DEV.md` simplificado e atualizado
  - `.claude/claude.md` atualizado com workflow correto
  - `README.md` atualizado

### Validated - Cálculos de Saldos
- ✅ Despesas fixas: divisão por 2 funcionando corretamente
- ✅ Estrutura despesas pessoais + boletins validada
- ✅ Filtro de data 2024+ disponível e testado
- ✅ Sistema funcional com prémios 100% validados

### Technical Details
**Files Modified:**
- `agora_web/core/management/commands/import_from_excel.py` - Fix prémios calculation
- `docs/SALDOS_VALIDATION_RESULTS.md` - Validation results
- `docs/SALDOS_CROSSCHECK.md` - Discrepancy analysis
- `crosscheck.py` - Validation script
- `README-DEV.md` - Updated workflow
- `.claude/claude.md` - Updated workflow
- `README.md` - Updated workflow

**Known Differences (documented, not critical):**
- Bruno Projetos Pessoais: -€2,000 (filtro ESTADO vs tipo diferente)
- Despesas Fixas total: +€2,902 (critérios de data/tags diferentes)
- Despesas Pessoais breakdown (investigar fórmula Excel no futuro)

---

## [2.1.0] - 2026-01-03

### Added - Sistema de Importação Web
- **Interface web para importação de Excel** no Django Admin
  - Upload drag-and-drop de ficheiros .xlsx
  - Validação de formato e feedback em tempo real
  - Integração com comando `import_from_excel` existente
  - Localização: Core → Importação de Dados

- **Modelo proxy ImportacaoDados** (`models.py:993-1005`)
  - Sem tabela na BD (managed=False)
  - Fornece entry point no admin para upload

- **Template de upload** (`templates/admin/core/importacaodados/changelist.html`)
  - Design consistente com tema Unfold
  - Suporte a dark mode
  - Drag-and-drop funcional

### Added - Sistema de Tags para Despesas Pessoais
- **Tags PESSOAL_BA e PESSOAL_RR** para identificar despesas pessoais por sócio
  - Substitui lógica anterior baseada em nome do credor
  - Permite despesas pessoais com credores externos (Sara Fevereiro, PC Diga, etc.)

- **Leitura de Column U do Excel** (`import_from_excel.py:374`)
  - Column U identifica sócio responsável pela despesa PESSOAL
  - Conversão automática: PESSOAL → PESSOAL_BA/PESSOAL_RR
  - Testado com 62 despesas PESSOAL (29 BA + 33 RR)

### Changed - Melhorias no Admin de Despesas
- **Campo `tipo` movido para collapsed "Deprecated"** (`admin.py:218-222`)
  - Mantido apenas por compatibilidade
  - Novo campo `tipo_original` para referência histórica

- **Adicionada coluna `tags_display`** (`admin.py:236-242`)
  - Mostra tags reais em vez do campo deprecated
  - Interface `filter_horizontal` para melhor UX

### Changed - Refatoração do SaldosCalculator
- **Despesas pessoais agora filtradas por tags específicas** (`saldos.py:247-251`)
  - Antes: Filtrava por tag PESSOAL + nome no credor (FALHAVA!)
  - Agora: Filtra por PESSOAL_BA ou PESSOAL_RR (100% preciso)
  - **Fix crítico**: 9 despesas PESSOAL não estavam a ser contadas em nenhum saldo!

### Fixed - Proteção contra Linhas Vazias
- **Skip automático de projetos vazios** (`import_from_excel.py:254-256`)
  - Projetos sem descrição, cliente e valor=0 são ignorados
  - Previne criação de 1618+ registos vazios

- **Skip automático de despesas vazias** (`import_from_excel.py:376-378`)
  - Despesas sem descrição, credor e valor=0 são ignoradas
  - Previne criação de 636+ registos vazios

### Documentation
- **docs/IMPORT_SYSTEM.md** - Documentação completa do sistema de importação web
- **README.md** - Atualizado com info do sistema de importação
- **docs/README.md** - Adicionado link para IMPORT_SYSTEM.md

### Database Changes
- **Tags criadas**: PESSOAL_BA, PESSOAL_RR
- **Cleanup realizado**:
  - Projetos: 1699 → 81 (removidos 1618 vazios)
  - Despesas: 875 → 239 (removidas 636 vazias)

### Technical Details
**Files Modified:**
- `agora_web/core/models.py` - Added ImportacaoDados proxy model
- `agora_web/core/admin.py` - Added ImportacaoDadosAdmin + updated DespesaAdmin
- `agora_web/core/templates/admin/core/importacaodados/changelist.html` - Upload template
- `agora_web/core/management/commands/import_from_excel.py` - Column U reading + empty validation
- `agora_web/core/utils/saldos.py` - Fixed personal expenses filtering
- `docs/IMPORT_SYSTEM.md` - New documentation
- `README.md` - Updated with import system info

**Testing:**
- ✅ Excel column U verified (62 PESSOAL expenses, 100% populated)
- ✅ Tag conversion logic tested (PESSOAL → PESSOAL_BA/RR)
- ✅ Empty line validation tested (skip successful)
- ✅ Web upload interface tested
- ✅ Saldos calculation verified with new tags

### Breaking Changes
None - All changes are backwards compatible. Old PESSOAL tag still exists but will be automatically converted on next import.

### Migration Notes
After importing Excel with updated data:
1. All 62 PESSOAL despesas will be converted to PESSOAL_BA or PESSOAL_RR
2. Old tag PESSOAL can be removed if desired (not required)
3. Personal expenses will now be correctly counted in saldos

---

## [2.0.0] - 2025-12-31

### Added
- Django 5.0 + PostgreSQL 16 base application
- Dashboard de Saldos Pessoais (dual logic: Atual vs Projetado)
- Modelo Socio com migração de dados
- Docker + Traefik + Cloudflare infrastructure
- Unfold Admin Theme
- CLI import system (import_from_excel)

---

**Versão Atual:** 2.2.0
**Data:** 2026-01-12
