# 🔧 Workflows de Desenvolvimento - Agora Contabilidade

Este diretório contém guias para diferentes workflows de desenvolvimento com IA.

---

## 📚 Workflows Disponíveis

### 🖥️ [VS Code Extension](vscode-extension.md)
**Ferramenta:** Claude Code (VS Code Extension)
**Quando usar:** Desenvolvimento ativo, múltiplos ficheiros, debugging, refactoring
**Acesso:** SSH direto ao servidor

**Vantagens:**
- ✅ Edição direta no servidor (sem sincronização)
- ✅ Terminal integrado
- ✅ Deploy imediato após mudanças
- ✅ Context completo do código
- ✅ Debugging interativo com Django shell

**Ideal para:**
- Desenvolver novas features complexas
- Criar/modificar models Django
- Debugging de issues
- Testing direto no servidor
- Migrations database

---

### 🌐 [MCP GitHub](mcp-github.md)
**Ferramenta:** Perplexity AI, Claude.ai (com MCP GitHub)
**Quando usar:** Edições rápidas, documentação, trabalho remoto
**Acesso:** Via GitHub API

**Vantagens:**
- ✅ Trabalhar de qualquer device
- ✅ Criar PRs diretamente
- ✅ Bom para documentação
- ✅ Não precisa de VS Code/SSH

**Ideal para:**
- Quick fixes
- Atualizar documentação
- Criar/editar ficheiros individuais
- Code review
- Trabalho mobile

---

## 📊 Comparação Rápida

| Feature | VS Code Extension | MCP GitHub |
|---------|------------------|-----------|
| **Editar múltiplos ficheiros** | ✅ Excelente | ⚠️ Possível mas lento |
| **Testing no servidor** | ✅ Direto (Docker) | ❌ Precisa SSH manual |
| **Deploy imediato** | ✅ Sim (`./deploy.sh`) | ❌ Não (merge → SSH manual) |
| **Criar PRs** | ✅ Via terminal (`gh`) | ✅ Direto no GitHub |
| **Django shell** | ✅ Sim | ❌ Não |
| **Migrations** | ✅ Direto | ❌ Precisa SSH |
| **Trabalhar mobile** | ❌ Difícil | ✅ Sim |
| **Documentação** | ✅ Bom | ✅ Excelente |

---

## 🎯 Quando Usar Cada Workflow?

### Use **VS Code Extension** quando:
- 🔧 Estiveres a desenvolver uma feature nova
- 🗄️ Modificares models ou schema database
- 🐛 Precisares de debugar com Django shell
- 🔄 Fizeres refactoring de múltiplos ficheiros
- ⚡ Quiseres testar mudanças imediatamente
- 📊 Criares/testares queries complexas

### Use **MCP GitHub** quando:
- 📝 Atualizares documentação
- 🐛 Fizeres um quick fix pequeno
- 📱 Estiveres em movimento (mobile/tablet)
- 👀 Fizeres code review
- ✍️ Criares ficheiros novos simples
- 🚀 Quiseres criar PR diretamente

---

## 🔀 Workflow Híbrido (Recomendado!)

**Combinação ideal:**

1. **Planeamento inicial** → MCP GitHub (Perplexity)
   - Criar issue/RFC
   - Documentar requisitos
   - Brainstorm soluções

2. **Desenvolvimento core** → VS Code Extension (Claude Code)
   - Implementar models Django
   - Criar migrations
   - Implementar views/admin
   - Testar no servidor

3. **Documentação final** → MCP GitHub (Perplexity)
   - Atualizar README/docs
   - Criar changelog
   - Finalizar PR

---

## 📖 Recursos Adicionais

- **Contexto Universal:** [`.claude/claude.md`](../claude.md)
- **Prompts Reutilizáveis:** [`.claude/prompts/`](../prompts/)
- **Guia Geral de Dev:** [`README-DEV.md`](../../README-DEV.md)

---

**Última Atualização:** 2026-01-05
