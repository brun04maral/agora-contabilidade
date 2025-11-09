# 📝 TODO - Agora Contabilidade

**Última atualização:** 09/11/2025
**Estado atual:** ✅ MVP Completo | Produção Ready | Melhorias incrementais

---

## 🔥 AGORA (Foco Imediato)

<!-- Máximo 3 tarefas. Apenas o que está a ser trabalhado AGORA -->

*Nada no momento - aguardando próxima prioridade*

---

## 📋 Próximos Passos (Backlog Priorizado)

### 🔴 Alta Prioridade

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

- [ ] 🎨 Melhorar inputs de data
  - Substituir Entry por Date Picker visual
  - Validação de datas em tempo real
  - Formatos PT (DD/MM/YYYY)
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
