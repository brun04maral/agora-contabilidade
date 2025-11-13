# 📝 TODO - Agora Contabilidade

**Última atualização:** 13/11/2025
**Estado atual:** ✅ MVP Completo | Produção Ready | Melhorias incrementais

---

## 🔥 AGORA (Foco Imediato)

<!-- Máximo 3 tarefas. Apenas o que está a ser trabalhado AGORA -->

*Nada no momento - aguardando próxima prioridade*

---

## 📋 Próximos Passos (Backlog Priorizado)

### 🔴 Alta Prioridade

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

- [ ] 🔁 **Sistema de Templates para Boletins Recorrentes**
  - Aplicar arquitetura semelhante ao sistema de Templates de Despesas
  - Tabela separada `boletim_templates` para boletins mensais fixos
  - **Apenas 2 templates necessários:** Template BA (#TB000001) e Template RR (#TB000002)
  - Templates armazenam periodicidade (mensal) e sócio fixo
  - Geração automática de boletins via botão "🔁 Gerar Recorrentes"
  - Screen dedicado com CRUD completo (simples, max 2 templates)
  - Indicador visual em boletins gerados de template
  - **Motivação:** Boletins mensais fixos (ex: salário base BA/RR) atualmente precisam ser criados manualmente
- [ ] 📄 **Exportação de Boletins para PDF Assinados**
  - Sistema de exportação de boletins individuais para PDF
  - Template PDF profissional com informação fiscal completa
  - **Assinatura digital:** Campo para assinatura ou espaço para assinatura manual
  - Logo Agora Media Production no cabeçalho
  - Dados completos: Sócio, Data, Valor, Descrição, etc.
  - Botão "📄 Exportar PDF" no screen Boletins
  - **Objetivo:** Enviar boletins assinados para contabilidade oficial
  - Formato oficial compatível com requisitos fiscais portugueses
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
