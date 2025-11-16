# 📝 TODO - Agora Contabilidade

**Última atualização:** 16/11/2025 (22:00)
**Estado atual:** ✅ MVP Completo | Produção Ready | Melhorias incrementais

---

- [ ] ✨ **Implementar Dialogs CRUD Específicos por Tipo - Orçamentos V2**
  - Lado CLIENTE: ServicoDialog, EquipamentoDialog, TransporteDialog, RefeicaoDialog, OutroDialog
  - Lado EMPRESA: ServicoEmpresaDialog, EquipamentoEmpresaDialog, ComissaoDialog
  - Renderização tabular de items por tipo
  - Sincronização automática despesas CLIENTE→EMPRESA
  - Validação bloqueio aprovação (TOTAL_CLIENTE = TOTAL_EMPRESA)
  - Auto-preenchimento de comissões
  - Testes de fluxo completo (criar, editar, aprovar)

## 🔥 AGORA (Foco Imediato)

<!-- Máximo 3 tarefas. Apenas o que está a ser trabalhado AGORA -->

- [ ] 🧪 **Fase 4: Testes & Ajustes - Sistema Boletim Itinerário**
  - Executar migrações localmente: `python run_migrations_016_019.py`
  - Criar dados de teste (valores referência, templates, boletins com linhas)
  - Testar cálculos automáticos de totais
  - Testar geração recorrente de boletins
  - Validar edge cases (valores zero, projetos apagados, meses sem 31 dias)

---

## 📋 Próximos Passos (Backlog Priorizado)

### 🔴 Alta Prioridade

## 🔴 Alta Prioridade - SISTEMA FISCAL

- [ ] 💰 **Implementar Sistema Fiscal Completo** (NOVO 15/11/2025)
  - **Contexto:** Agora precisa cumprir obrigações fiscais (IVA, IRS, IRC)
  - **Prioridade:** ALTA - Obrigações legais com prazos rígidos
  - **Dependências:** Migration 020 concluída, tabela receitas implementada
  
  **Objetivo:** Sistema completo para gestão de obrigações fiscais portuguesas
  
  **Componentes principais:**
  
  ### 1. Tabela Receitas
  - Criar tabela `receitas` (estrutura em FISCAL.md)
  - Campos: numero, fatura_numero, projeto_id, cliente_id, valores (s/IVA, IVA, c/IVA), datas, estado, tipo
  - Estados: EMITIDO, RECEBIDO, CANCELADO
  - Tipos: PROJETO, OUTRO
  - Link bidirecional com projetos
  - CRUD completo
  
  ### 2. IRS Retido (Fornecedores Freelancers)
  - Adicionar campos em `despesas`: irs_retido, taxa_retencao_irs, irs_entregue
  - Adicionar campos em `fornecedores`: tipo (EMPRESA/FREELANCER), taxa_retencao_irs, isento_retencao
  - Cálculo automático retenção ao criar despesa com fornecedor freelancer
  - Taxa default: 23% (configurável por fornecedor: 23%, 25%, 16.5%, etc)
  - Lógica: valor_sem_iva × taxa_retencao = irs_retido
  
  ### 3. IVA Trimestral
  - Tabela `iva_trimestral` (histórico e controlo)
  - Cálculo automático: IVA Liquidado (receitas) - IVA Dedutível (despesas)
  - Período: trimestre (Jan-Mar, Abr-Jun, Jul-Set, Out-Dez)
  - Filtro: apenas receitas RECEBIDAS e despesas PAGAS no período
  - Separar por taxa (23%, 13%, 6%)
  - Estados: APURADO, DECLARADO, PAGO
  
  ### 4. IRS Mensal
  - Tabela `irs_mensal` (histórico e controlo)
  - Cálculo automático: soma de todas as retenções do mês
  - Listagem de despesas com retenção por mês
  - Estados: APURADO, DECLARADO, PAGO
  
  ### 5. UI - Novos Screens
  - **ReceitasScreen:** CRUD receitas, filtros, estados
  - **IVATrimestralScreen:** Seletor ano/trimestre, tabelas receitas/despesas, apuramento, export Excel
  - **IRSRetidoScreen:** Seletor ano/mês, tabela despesas com retenção, total, export Excel
  - **FiscalDashboardScreen:** Calendário obrigações, alertas prazos, resumos
  
  ### 6. Relatórios e Exports
  - Export IVA trimestral para Excel (enviar TOC)
  - Export IRS mensal para Excel (enviar TOC)
  - Export receitas anuais (Excel)
  - Export despesas anuais (Excel)
  - Relatório anual completo (para TOC preparar IRC)
  
  ### 7. Validações e Alertas
  - Validar valores IVA coerentes (valor_c_iva >= valor_sem_iva)
  - Calcular taxa_iva automaticamente
  - Alertas de prazos (notificações 7 dias antes)
  - Dashboard com próximas obrigações
  
  **Ficheiros afetados:**
  - `database/models/receita.py` (novo)
  - `database/models/despesa.py` (adicionar campos IRS)
  - `database/models/fornecedor.py` (adicionar campos)
  - `database/migrations/021_sistema_fiscal.py` (novo - ver FISCAL.md)
  - `logic/receitas.py` (novo)
  - `logic/iva_trimestral.py` (novo)
  - `logic/irs_mensal.py` (novo)
  - `logic/fiscal_exports.py` (novo)
  - `ui/screens/receitas.py` (novo)
  - `ui/screens/iva_trimestral.py` (novo)
  - `ui/screens/irs_retido.py` (novo)
  - `ui/screens/fiscal_dashboard.py` (novo)
  
  **Fases de implementação:**
  
  **Fase 1 - Receitas (1 semana):**
  - Migration 021 (tabela receitas)
  - Model + CRUD
  - UI básico
  - Link com projetos
  
  **Fase 2 - IRS Retido (3 dias):**
  - Adicionar campos despesas/fornecedores
  - Cálculo automático
  - Relatório mensal
  
  **Fase 3 - IVA Trimestral (1 semana):**
  - Tabela + cálculo
  - UI completo
  - Export Excel
  
  **Fase 4 - Dashboard Fiscal (3 dias):**
  - Calendário obrigações
  - Alertas
  - Resumos
  
  **Total estimado:** 3-4 semanas
  
  **Decisões pendentes (validar com TOC):**
  - IRS retido: declaração mensal vs Modelo 10 anual?
  - Receitas: criar ao emitir fatura ou ao receber pagamento?
  - Integração TOConline: API ou export manual?
  - Derrama municipal: aplicável? Que taxa?
  
  **Ver:**
  - FISCAL.md (documentação completa)
  - DECISIONS.md (decisões sobre receitas e IRS)
  - DATABASE_SCHEMA.md (estrutura tabelas)

---

## 🟡 Média Prioridade - FISCAL

- [ ] 📊 **Integração TOConline** (NOVO 15/11/2025)
  - **Contexto:** Após sistema fiscal básico implementado
  - **Objetivo:** Enviar dados automaticamente para TOC processar
  
  **A discutir com TOC:**
  - Formato preferido: API vs Export SAF-T vs Excel
  - Periodicidade: Tempo real vs Mensal
  - Dados necessários: Receitas, Despesas, Boletins
  - Validações antes de enviar
  
  **Possíveis abordagens:**
  1. Export manual Excel (mais simples, menos automatizado)
  2. Export SAF-T XML (standard, aceite por todos software contabilidade)
  3. API TOConline (se existir, mais automatizado)
  
  **Benefícios:**
  - Elimina retrabalho (TOC não tem que inserir dados manualmente)
  - Reduz erros
  - Mais rápido fechar contas mensais
  
  **Ver:** FISCAL.md Secção 9.4

- [ ] 📄 **Emissão de Faturas Certificadas** (NOVO 15/11/2025)
  - **Contexto:** Atualmente faturas são emitidas fora do sistema
  - **Objetivo:** Integrar emissão de faturas no sistema Agora
  
  **Requisitos:**
  - Software faturação certificado (AT)
  - Comunicação automática SAF-T
  - Séries de numeração sequencial
  - Diferentes tipos: Fatura, Fatura-Recibo, Nota de Crédito
  - Impressão/PDF
  
  **Integrações possíveis:**
  - InvoiceXpress (API)
  - Moloni (API)
  - Vendus (API)
  - Ou: desenvolver módulo próprio + certificação AT
  
  **Impacto:**
  - Link automático fatura → receita
  - Comunicação automática AT (dia 5 de cada mês)
  - Menos trabalho manual
  
  **Prioridade:** Média (sistema funciona sem isto, mas melhora muito workflow)
  
  **Ver:** FISCAL.md Secção 2.4

---

## 🟢 Baixa Prioridade - FISCAL

- [ ] 📈 **Relatórios Fiscais Avançados** (NOVO 15/11/2025)
  - Gráficos evolução IVA trimestral
  - Comparação ano a ano (IVA, IRS retido, IRC estimado)
  - Previsões fiscais (estimativa IRC fim de ano)
  - Análise margens por projeto (valor facturado vs custos)
  - Cash-flow fiscal (receitas vs despesas mensais)
  
  **Ver:** FISCAL.md Secção 9.4

- [ ] 🔔 **Sistema de Alertas Fiscais** (NOVO 15/11/2025)
  - Notificações 7 dias antes de prazos
  - Email automático para TOC
  - Badge no dashboard com obrigações pendentes
  - Histórico de cumprimento (on-time vs atrasos)
  
  **Ver:** FISCAL.md Secção 9.3

- [ ] 🌍 **Suporte Multi-moeda** (NOVO 15/11/2025)
  - Receitas/despesas em EUR, USD, GBP, etc
  - Conversão automática para EUR (taxa ECB)
  - Histórico de taxas de câmbio
  - Relatórios em moeda original e EUR
  
  **Aplicável:** Se Agora faturar clientes estrangeiros

---

## 📚 Documentação Relacionada

**Ficheiros criados:**
- `FISCAL.md` - Documentação completa obrigações fiscais (15/11/2025)

**Secções relevantes:**
- FISCAL.md Secção 9: Implementação Técnica (migrations, models, UI)
- FISCAL.md Secção 8: Calendário Fiscal 2025 (todos os prazos)
- DATABASE_SCHEMA.md: Adicionar estrutura receitas + alterações despesas/fornecedores

**Próximo passo:**
1. ✅ Validar FISCAL.md com TOC
2. Implementar Migration 021 (receitas + campos fiscais)
3. Desenvolver por fases (Receitas → IRS → IVA → Dashboard)

- [ ] 🐛 **Bug: Scroll em popups modais propaga para lista de fundo** ⏸️ **POSTPONED**
  - **Problema:** Ao fazer scroll em popups de edição/criação, a lista por trás também faz scroll
  - **Comportamento esperado:** Scroll apenas dentro do popup, lista não deve mover
  - **Requerimento crítico:** Trackpad deve funcionar normalmente no popup
  - **Tentativas exaustivas realizadas (7+ abordagens):**
    1. Unbind/rebind mousewheel events → Trackpad parou de funcionar
    2. Smart detection com winfo_toplevel() → Lista continuou a scrollar
    3. Enter/Leave bindings com bind_all/unbind_all → Trackpad não funcionou
    4. Manual scroll redirection com bind_all + "break" → Quebrou DataTableV2 bindings
    5. Corrigido com add=True em bind_all → Lista continuou a scrollar
    6. Bind com "break" diretamente no tree → Lista continuou a scrollar
    7. bindtags() save/disable/restore → Lista continuou a scrollar
  - **Decisão:** Postponed após múltiplas tentativas sem sucesso (11/11/2025)
  - **Razão:** Provável limitação do CustomTkinter/Tkinter modal behavior
  - **Ficheiros afetados:** Todos os dialogs modais (Projetos, Despesas, Boletins, Clientes, Fornecedores, Equipamento, Orçamentos)
  - **Impacto:** UX issue menor, não bloqueia funcionalidades
  - **Próximos passos:** Pesquisar soluções na comunidade CustomTkinter ou aguardar updates do framework
- [ ] 📦 Build executável para Windows (PyInstaller)
  - Testar em ambiente Windows limpo
  - Configurar inclusão de assets
  - Criar instalador (.msi ou .exe)
- [ ] 🧪 Testes de integração completos
  - Testar fluxos críticos (Saldos, Projetos, Boletins)
  - Validar cálculos financeiros
  - Testar importação/exportação
- [ ] 💾 Sistema de backup automático
  - Backup diário da base de dados SQLite
  - Versionamento de backups (manter últimos 30 dias)
  - Notificação ao utilizador

### 🟡 Média Prioridade
- [ ] 🎨 **Melhorar UX/UI de Orçamentos e Boletins** (PRIORITY)
  - **Problema atual:** Ambos os screens são confusos e pouco intuitivos
  - **User feedback:** "estão ambos muito maus e algo confusos"

  **ORÇAMENTOS - Propostas de Melhoria:**
  - [ ] **Wizard multi-step:** Dividir criação em 3 passos
    1. Info básica (cliente, data, desconto geral)
    2. Secções e itens (tabela interativa)
    3. Repartições (BA/RR) com preview de totais
    - Navegação: Botões "Anterior", "Próximo", "Concluir"
    - Progresso visual (1/3, 2/3, 3/3)
  - [ ] **Preview visual lateral:** Durante edição, mostrar:
    - Total geral (grande e destacado)
    - Subtotais por secção
    - Total de repartições BA/RR (verde/azul)
    - Alerta se repartições ≠ valor_total
  - [ ] **Gráfico de repartições:** Pie chart ou barra horizontal BA vs RR
  - [ ] **Botão "Duplicar Orçamento":** Criar cópia completa (secções + itens + repartições)
  - [ ] **Simplificar formulário único:** Se não wizard, agrupar campos em frames claramente separados
  - [ ] **Validação em tempo real:** Mostrar erros inline (não apenas no save)
  - [ ] **Tooltips informativos:** Explicar campos complexos (ex: "Repartição = divisão de prémios")

  **BOLETINS - Propostas de Melhoria:**
  - [ ] **Remover formulário antigo:** Apagar completamente FormularioBoletimDialog (legacy)
  - [ ] **Simplificar header buttons:** Reduzir de 4 para 2 botões:
    - "➕ Novo Boletim" (abre BoletimFormScreen)
    - "⚙️ Configurações" (dropdown: Templates, Valores Ref, Gerar Recorrentes)
  - [ ] **Vista de cards:** Substituir tabela por cards visuais:
    - Card grande por boletim (sombra, border)
    - Info principal: Número, Sócio, Mês/Ano, Valor Total (destaque)
    - Linhas resumidas: "3 deslocações (2 nacionais, 1 estrangeiro)"
    - Botões: "✏️ Editar", "💰 Marcar Pago", "🗑️ Apagar"
    - Badge de estado: PENDENTE (laranja) / PAGO (verde)
  - [ ] **BoletimFormScreen - Melhorias:**
    - [ ] **Edição inline de linhas:** Não abrir dialog, editar diretamente na tabela
    - [ ] **Auto-save de linhas:** Salvar automaticamente ao mudar foco
    - [ ] **Drag & drop:** Reordenar linhas arrastando
    - [ ] **Templates rápidos:** Botão "Adicionar Template" (dropdown com templates)
    - [ ] **Calculadora visual:** Mostrar em tempo real:
      * Total Ajudas Nacionais = X dias × €72.65 = €XXX
      * Total Ajudas Estrangeiro = Y dias × €167.07 = €YYY
      * Total Kms = Z km × €0.40 = €ZZ
      * **TOTAL = €XXXXX** (grande e verde)
  - [ ] **Geração recorrente mais visível:** Dashboard ou notificação mensal
  - [ ] **Filtros rápidos:** Por sócio, por estado, por mês/ano
  - [ ] **Pesquisa:** Campo de busca por número, projeto, nota

  **PRIORIDADE:** Alta (afeta usabilidade diária)
  **IMPACTO:** Reduz significativamente tempo de operação e erros
  **FICHEIROS:** ui/screens/orcamentos.py (~800L), ui/screens/boletins.py (~650L), ui/screens/boletim_form.py (~850L)

- [ ] 📄 **Exportação de Boletins para PDF Assinados**
  - Sistema de exportação de boletins individuais para PDF
  - Template PDF profissional com informação fiscal completa
  - **Assinatura digital:** Campo para assinatura ou espaço para assinatura manual
  - Logo Agora Media Production no cabeçalho
  - Dados completos: Sócio, Data, Valor, Descrição, etc.
  - Botão "📄 Exportar PDF" no screen Boletins
  - **Objetivo:** Enviar boletins assinados para contabilidade oficial
  - Formato oficial compatível com requisitos fiscais portugueses
- [ ] 🔄 **Converter Orçamento Aprovado → Projeto** (Automação)
  - **Contexto:** Atualmente o processo é totalmente manual
  - **Problema:** Quando orçamento é aprovado, tem que criar projeto manualmente e copiar:
    * Cliente
    * Valor total
    * Prémios BA/RR (soma das repartições)
  - **Solução escolhida:** Botão "🔄 Converter em Projeto"
    * Visível apenas quando status = "aprovado"
    * Cria projeto automaticamente:
      - Tipo: EMPRESA
      - Cliente: mesmo do orçamento
      - Valor: valor_total do orçamento
      - **Prémio BA:** soma de todas repartições com entidade='BA'
      - **Prémio RR:** soma de todas repartições com entidade='RR'
      - Descrição: "Projeto criado a partir do orçamento [código]"
      - Data início: data aprovação do orçamento
    * Mostra notificação: "✅ Projeto #P0123 criado!"
    * Opcional: Link bidirecional (projeto.orcamento_id, orcamento.projeto_id)
  - **Alternativa rejeitada:** Conversão automática ao aprovar (menos controlo)
  - **Benefício:** Elimina trabalho manual repetitivo + previne erros de cópia
  - **Ficheiros:** logic/orcamentos.py (novo método), ui/screens/orcamentos.py (botão)
- [ ] 📊 **Aprimorar Sistema de Relatórios**
  - Adicionar mais tipos de relatórios:
    - Relatório de Despesas por Tipo/Credor
    - Relatório de Evolução Mensal de Saldos
    - Relatório Anual Fiscal (resumo para impostos)
  - Melhorar UI do screen Relatórios:
    - Seleção de tipo de relatório (dropdown)
    - Preview antes de exportar
    - Mais opções de filtros (período, sócio, tipo)
  - Adicionar exportação para PDF (além de Excel)
  - Templates profissionais para relatórios
  - Gráficos e visualizações nos relatórios exportados
- [ ] 📝 Documentação de utilizador final
  - Manual de utilização (PDF)
  - Screenshots de cada módulo
  - FAQ comum
- [ ] ♻️ Refatorar validações de formulários
  - Centralizar validações comuns
  - Mensagens de erro consistentes
  - Feedback visual melhorado
- [ ] 📊 Dashboard: Adicionar mais gráficos
  - Gráfico de evolução mensal de saldos
  - Gráfico de despesas por categoria
  - Comparação Bruno vs Rafael

### 🟢 Baixa Prioridade (Nice-to-have)

- [ ] 🔄 Botão de atualização na tela Info
  - Check de atualizações automático
  - Download e instalação de novas versões
  - Notificação quando nova versão disponível
- [ ] 🎨 Temas (Dark/Light mode)
  - Toggle no menu de definições
  - Persistir preferência do utilizador
- [ ] ⌨️ Atalhos de teclado
  - Ctrl+N: Novo item
  - Ctrl+S: Guardar
  - Ctrl+F: Pesquisar
  - Esc: Fechar diálogo
- [ ] 📄 Exportação de boletins para PDF
  - Template de boletim profissional
  - Logo da empresa
  - Informação fiscal
- [ ] 🔍 Pesquisa global (cross-module)
  - Pesquisar em todos os módulos simultaneamente
  - Resultados agregados
- [ ] 📈 Relatório anual de atividade
  - Resumo financeiro do ano
  - Gráficos e estatísticas
  - Exportação para Excel/PDF

---

## 💡 Ideias/Futuro (Brainstorming)

<!-- Ideias não comprometidas, para discussão -->

- 📅 **DateRangePicker Visual Unificado**
  - Componente único para seleção de períodos (data início + data fim)
  - Calendário visual com seleção de range (arrastar no calendário)
  - Alternativa aos dois campos separados (Data Início + Data Fim)
  - Mais intuitivo para períodos de projetos/deslocações
  - Preview visual do período selecionado
  - Aplicável em: Boletim Linhas, Projetos, Relatórios
  - **Prioridade:** Baixa (campos separados funcionam bem)
- 💰 **Screen de Financeiro**
  - Consulta de saldo bancário (integração/manual)
  - Visualização de lucros (mensal/anual)
  - Cálculo de impostos a pagar
  - Previsões financeiras
- 🔌 **Integração TOConline API**
  - Importar faturas emitidas automaticamente
  - Sincronizar clientes/fornecedores
  - Obter PDFs de faturas
- 🌐 **Multi-utilizador**
  - Permissões e roles
  - Auditoria de alterações
- 💱 **Multi-moeda**
  - Suporte para USD, GBP, etc.
  - Conversão automática de taxas
- 📱 **Versão mobile/web**
  - App complementar para consulta rápida
  - Sincronização com desktop
- 🤖 **Automações**
  - Email automático de boletins
  - Alertas de faturas vencidas
  - Lembretes de pagamentos
- 📊 **Business Intelligence**
  - Análise preditiva de cashflow
  - Identificação de padrões
  - Sugestões de otimização

---

## ✅ Concluído Recentemente

<!-- Últimas 10 tarefas - manter histórico curto para contexto -->

- [x] 🎨 **15/11** - Auto-preenchimento de datas de projeto em Boletim Linhas
  - **Funcionalidade:** Quando utilizador seleciona projeto numa linha, campos data_inicio e data_fim preenchem automaticamente
  - **Comportamento inteligente:**
    - Só preenche se campos estiverem vazios (não sobrescreve edições)
    - Usa data_inicio e data_fim do modelo Projeto
    - Projetos sem datas → nada acontece
    - Datas aparecem **visualmente imediatamente** após seleção
  - **Fix crítico no DatePickerDropdown:**
    - Componente inicializava com `date.today()` quando `default_date=None`
    - Mudado para: `self.selected_date = None` (aceita None como valor válido)
    - `get_date()` agora retorna None quando campo vazio
    - `set_date()` força atualização visual com `update_idletasks()`
  - **Commits:** ebbf8d1 (feature), 88d0fa0 (fix None), ad548c6 (fix visual)
  - Ficheiros: ui/screens/boletim_form.py (+10L), ui/components/date_picker_dropdown.py (3 fixes)

- [x] 🐛 **15/11** - Fix: Right-click context menu funciona sempre
  - **Problema:** Menu só aparecia quando 7+ itens selecionados
  - **Causa:** Right-click bound apenas ao row_frame, labels não propagavam eventos
  - **Solução:** Adicionar binding de right-click a TODAS as labels dentro da row
  - **Técnica:** Similar a Button-1 e Double-Button-1, propagar eventos das labels
  - **Resultado:** Menu funciona independentemente de:
    - Número de itens selecionados (0, 1, 7, 100...)
    - Onde utilizador clica (texto, espaço vazio, bordas)
  - Commit: 697f71a
  - Ficheiro: ui/components/data_table_v2.py (+6L)

- [x] 🔁 **13/11** - Sistema Completo de Boletim Itinerário (3 Fases - COMPLETO)
  - **Fase 1 - Modelo de Dados (Commit: 8d14f0c):**
    * 3 novas tabelas: valores_referencia_anual, boletim_linhas, boletim_templates
    * 1 tabela expandida: boletins (+9 campos: mes, ano, valores_ref, totais calculados)
    * 4 migrações SQL + script único run_migrations_016_019.py
  - **Fase 2 - Business Logic (Commit: 9616f7a):**
    * 3 novos managers: ValoresReferenciaManager (195L), BoletimLinhasManager (288L), BoletimTemplatesManager (309L)
    * 1 manager expandido: BoletinsManager (criar + gerar_proximo_numero, emitir DEPRECATED)
    * Cálculos automáticos de totais: dias × valores ref + kms
    * Geração recorrente mensal com verificação de duplicados
  - **Fase 3 - UI Completa (Commit: fe1b032):**
    * ValoresReferenciaScreen (328L) - CRUD valores ref por ano
    * TemplatesBoletinsScreen (340L) - CRUD templates recorrentes
    * BoletimFormScreen (850L) - Editor completo (header + linhas CRUD, dropdown projetos, cálculos em tempo real)
    * BoletinsScreen (atualizado +140L) - coluna "Linhas", botão "🔁 Gerar Recorrentes", GerarRecorrentesDialog
  - **Total:** 4 ficheiros DB, 3 logic, 4 UI = ~2600 linhas de código
  - **Decisões técnicas:** Valores ref por ano editáveis, dias manual, horas informativas, projetos opcionais
  - **Próximo:** Fase 4 - Testes & Ajustes locais

- [x] 🎨 **13/11** - UX: Remover popups de sucesso em TODAS as gravações
  - **Filosofia:** "Silent success" - apenas erros têm popup
  - **Afetadas:** 7 screens (projetos, despesas, templates_despesas, boletins, equipamento, orcamentos, relatorios)
  - **Total:** ~24 popups removidos
  - **Benefício:** Workflow mais rápido, menos intrusivo, feedback visual via lista atualizada
  - Ficheiros: ui/screens/*.py (7 screens)

- [x] 🎨 **13/11** - Strikethrough em Projetos Anulados
  - **Implementado:** Texto riscado em todos os campos exceto "Estado"
  - **Técnica:** Parâmetro `_strikethrough_except` em DataTableV2
  - **Visual:** Fundo cinza + texto riscado (overstrike)
  - **Código:** ui/components/data_table_v2.py (suporte genérico), ui/screens/projetos.py (aplicação)
  - Commit: 23381b1

- [x] 🔁 **13/11** - Sistema de Templates de Despesas Recorrentes (COMPLETO)
  - **Arquitetura:** Tabela separada `despesa_templates` (não misturada com despesas)
  - **Template ID:** Formato #TD000001, #TD000002, etc.
  - **Campos:** Armazena dia do mês (1-31) em vez de data completa
  - **UI Completa:**
    - Screen dedicado `TemplatesDespesasScreen` com CRUD
    - Botão "📝 Editar Recorrentes" no screen Despesas (janela modal 1000x700)
    - FormularioTemplateDialog com validação (dia 1-31)
    - Barra de seleção com "🗑️ Apagar Selecionados"
  - **Geração Automática:**
    - Botão "🔁 Gerar Recorrentes" no screen Despesas
    - Gera despesas para mês atual baseado em templates
    - Evita duplicados (verifica se já gerado)
    - Trata meses com dias diferentes (Feb 31 → Feb 28/29)
  - **Indicadores Visuais:**
    - Asterisco (*) no tipo quando gerada de template: "Fixa Mensal*"
    - Confirmação especial ao apagar despesas geradas
    - Info sobre não recriação automática
  - **Refatorações:**
    - Migration 014: Criar despesa_templates
    - Migration 015: Remover is_recorrente/dia_recorrencia de despesas
    - DespesasManager usa DespesaTemplate (não campos de recorrência)
    - FK despesa_template_id aponta para despesa_templates.id
    - UI limpa: removidos 100+ linhas de código de recorrência
  - **Bug Fix:** DataTableV2 não suportava show_actions/on_edit/on_delete → Solução com barra de seleção
  - Ficheiros: database/models/despesa_template.py, logic/despesa_templates.py, ui/screens/templates_despesas.py (450+ linhas), migrations 014/015, refactor em despesas.py e logic/despesas.py
  - Commits: dcf5a9c, 898a18d, 04f333c, 48ae2ca, f6d1a7f

- [x] 🎨 **13/11** - Fornecedores: Website clicável + Seguro dinâmico
  - **Campo Website com link clicável:**
    - Campo de texto para URL do website
    - Botão "🔗 Abrir" que abre URL no browser padrão
    - Adiciona automaticamente `https://` se necessário
    - Integrado com módulo `webbrowser` do Python
  - **Seguro visível apenas para FREELANCER:**
    - Campo "Validade Seguro Trabalho" só aparece se Estatuto = FREELANCER
    - Toggle dinâmico ao mudar radio buttons de estatuto
    - Método `_toggle_seguro_field()` com pack/pack_forget
  - **Migration 012:**
    - Adicionada coluna `website VARCHAR(255)` à tabela fornecedores
    - Script `run_migration_012.py` criado e corrigido (ImportError fix)
  - Ficheiros: ui/screens/fornecedores.py, database/models/fornecedor.py, database/migrations/012_add_website_to_fornecedor.py, run_migration_012.py

- [x] 🎨 **13/11** - Date Pickers profissionais rollout completo
  - **DatePickerDropdown:** Seleção de data única com calendário inline
  - **DateRangePickerDropdown:** Seleção de período com formato inteligente
    - Mesmo mês: `15-20/11/2025`
    - Meses diferentes: `28/11-05/12/2025`
    - Anos diferentes: `28/12/2024-05/01/2025`
  - **Implementado em 6 screens:**
    - **Projetos:** Campo "Período do Projeto" único (DateRangePickerDropdown)
    - **Despesas:** DatePickerDropdown para Data e Data Pagamento
    - **Boletins:** DatePickerDropdown para Data Emissão (default=hoje)
    - **Orçamentos:** Substituídos antigos DatePickerEntry e DateRangePicker
    - **Equipamento:** DatePickerDropdown para Data Compra
    - **Fornecedores:** DatePickerDropdown para Validade Seguro Trabalho
  - **Bugs corrigidos:**
    - AttributeError com widget string no _check_click_outside
    - ValueError com width/height no place() (CustomTkinter constraint)
    - ImportError em run_migration_012.py (engine import)
  - Ficheiros: ui/components/*.py, ui/screens/projetos.py, ui/screens/despesas.py, ui/screens/boletins.py, ui/screens/orcamentos.py, ui/screens/equipamento.py, ui/screens/fornecedores.py

- [x] 🎨 **11/11** - Clear selection after edit/cancel em todos os dialogs
  - **Comportamento implementado:** Após editar, criar ou cancelar qualquer item, a seleção é automaticamente limpa
  - **Padrão 1 (Callback):** Projetos, Despesas, Boletins
    - Método `after_save_callback()` adicionado aos screens
    - Callback passado aos dialogs via `self.parent`
    - `_on_close()` limpa seleção ao fechar (Cancel ou X)
  - **Padrão 2 (Wait Window):** Clientes, Fornecedores, Equipamento, Orçamentos
    - `table.clear_selection()` chamado após `dialog.wait_window()`
  - **7 screens atualizados:** Projetos, Despesas, Boletins, Clientes, Fornecedores, Equipamento, Orçamentos
  - **Benefício UX:** Interface mais limpa, evita confusão com item ainda selecionado
  - Ficheiros: ui/screens/*.py (7 screens CRUD)

- [x] 🎨 **11/11** - Navegação clicável completa em Saldos Pessoais
  - **10 botões clicáveis** com navegação e filtros automáticos:
    - INs: Projetos Pessoais, Prémios (para cada sócio)
    - OUTs: Despesas Fixas, Boletins Pendentes, Boletins Pagos, Despesas Pessoais
  - **Cores semânticas consistentes:**
    - Verde (#E8F5E0/#4A7028) para INs (match Recebido)
    - Laranja (#FFE5D0/#8B4513) para OUTs (match Não Faturado)
  - **Ícones PNG customizados:** ins.png e outs.png (base64)
  - **Títulos simplificados:** "INs (Entradas)" → "INs" e "OUTs (Saídas)" → "OUTs"
  - **Efeitos hover:** Border width 2→3, cursor hand2
  - **Boletins separados:** Mostrar Pendentes e Pagos como linhas distintas
  - Ficheiros: ui/screens/saldos.py, logic/saldos.py, assets/resources.py

- [x] ✨ **09/11** - Dashboard com navegação interativa
  - Cards BA/RR clicáveis → navegam para Saldos Pessoais
  - Cards Clientes/Fornecedores clicáveis → navegam para screens respetivos
  - Efeitos hover (border highlight, cursor pointer)
  - Métodos de navegação: navigate_to_saldos(), navigate_to_clientes(), navigate_to_fornecedores()

- [x] 🎨 **09/11** - Melhorias na Sidebar
  - Scroll vertical adicionado (CTkScrollableFrame)
  - Ícones aumentados de 20x20 para 27x27 pixels
  - "Definições" renomeado para "Info" com ícone PNG
  - Botões Info e Sair fixos no fundo
  - Separador visual antes da secção fixa

- [x] ℹ️ **09/11** - Nova tela Info
  - Criado ui/screens/info.py
  - Versão: v0.0.1
  - Créditos: "Desenvolvido por Bruno Amaral para Agora Media Production"
  - Layout centralizado e profissional
  - Preparado para botão "Atualizar" no futuro

- [x] 🎨 **09/11** - Dashboard com ícones PNG nos títulos de secções
  - Método create_section_title() reutilizável
  - 5 secções com ícones: Saldos, Projetos, Despesas, Boletins, Clientes

- [x] 🗂️ **09/11** - Organizar documentação histórica em `memory/archive/`
  - Criada estrutura: importacao/, setup_antigo/, migrations_docs/, problemas/
  - Raiz do repositório limpa (apenas essenciais)
  - Preservado histórico para referência futura

- [x] 🧠 **09/11** - Sistema de Memória completo
  - Pasta `memory/` com 11 ficheiros de documentação
  - CURRENT_STATE.md, ARCHITECTURE.md, DECISIONS.md, etc.
  - README.md na raiz com "Frase Mágica" para novas sessões

- [x] 🎨 **09/11** - Integração de ícones PNG em todos os screens
  - 10 screens com ícones nos títulos
  - Sistema de fallback (Icon → Emoji)
  - Padrão consistente em toda a app

- [x] 📝 **09/11** - Correção de naming: "Agora Media" → "Agora/Agora Media Production"
  - 39 ocorrências corrigidas em 11 ficheiros
  - Nome curto: "Agora" ✅
  - Nome completo: "Agora Media Production" ✅

- [x] 🐛 **09/11** - Fix: Documentação sobre boletins (regra de desconto)
  - Corrigido: Boletins descontam quando PAGOS (não EMITIDOS)
  - Código estava correto, docs é que estavam errados
  - Atualizado: README.md, GUIA_COMPLETO.md, DATABASE_SCHEMA.md

- [x] 🎨 **08/11** - Logos PNG de alta qualidade
  - Logo SVG continha PNG embutido (não vetorial)
  - Solução: PNGs manuais fornecidos (71KB, 156KB)
  - Scripts de conversão deprecados
  - Qualidade controlada manualmente

- [x] 💾 **08/11** - Importação Excel → SQLite completa
  - 19 Clientes, 44 Fornecedores, 75 Projetos
  - 162 Despesas, 34 Boletins
  - Prémios calculados e atribuídos
  - Saldos validados

- [x] 🖥️ **07/11** - MVP Fase 1 100% completo
  - 10 módulos funcionais
  - CRUD completo em todos os módulos
  - Lógica de negócio implementada
  - Sistema pronto para produção

- [x] 💰 **06/11** - Sistema de Saldos Pessoais (CORE)
  - Cálculo 50/50 automático
  - INs: Projetos pessoais + Prémios
  - OUTs: Despesas fixas ÷2 + Boletins + Despesas pessoais
  - Sugestão de boletim para zerar saldo

- [x] 🗄️ **05/11** - Database SQLite + Alembic
  - Migração de Supabase → SQLite
  - Migrations configuradas
  - Seed data para desenvolvimento
  - Modelos completos

---

## 🔗 Links Relacionados

- [CURRENT_STATE.md](./CURRENT_STATE.md) - Estado atual do projeto (ler sempre no início)
- [ARCHITECTURE.md](./ARCHITECTURE.md) - Arquitetura e estrutura do código
- [DECISIONS.md](./DECISIONS.md) - Decisões técnicas importantes (ADR)
- [DATABASE_SCHEMA.md](./DATABASE_SCHEMA.md) - Esquema da base de dados
- [CHANGELOG.md](./CHANGELOG.md) - Histórico completo de mudanças
- [DEV_SETUP.md](./DEV_SETUP.md) - Setup de desenvolvimento

---

## 📊 Legenda de Categorias

### Prioridade
- 🔴 **Alta** - Urgente/Bloqueante/Essencial para produção
- 🟡 **Média** - Importante mas não urgente
- 🟢 **Baixa** - Nice-to-have/Melhorias opcionais

### Tipo
- 🐛 **Bug** - Correção de erro
- ✨ **Feature** - Nova funcionalidade
- 🎨 **UI/UX** - Interface/experiência de utilizador
- 📝 **Docs** - Documentação
- 🔧 **DevOps** - Setup/CI/CD/Build
- ♻️ **Refactor** - Reestruturação de código
- 📊 **Data** - Database/migrations/imports
- 🗂️ **Organização** - Estrutura de ficheiros/limpeza
- 💾 **Backup** - Sistemas de backup/recuperação
- 🧪 **Testes** - Testing/QA
- 🔌 **Integração** - APIs externas/integrações
- 📦 **Build** - Compilação/distribuição

---

## 💬 Notas

### Como usar este ficheiro:
1. **Nova sessão?** Lê "🔥 AGORA" para ver prioridades imediatas
2. **Concluíste uma tarefa?** Move de "Próximos Passos" → "Concluído Recentemente"
3. **Nova ideia?** Adiciona a "💡 Ideias/Futuro" para discutir depois
4. **Algo urgente?** Adiciona a "🔥 AGORA" (máx. 3 tarefas!)

### Workflow:
```
💡 Ideias → 📋 Backlog → 🔥 AGORA → ✅ Concluído
```

### Manutenção:
- Atualizar data no topo sempre que houver mudanças
- Manter "Concluído Recentemente" com últimas 10 tarefas (apagar antigas)
- Rever prioridades semanalmente
- Mover tarefas de baixa prioridade não iniciadas para "Ideias" se passarem 1 mês

---

**📍 Lembrete:** Este ficheiro é complementar ao `CURRENT_STATE.md`. Usa ambos para contexto completo!
