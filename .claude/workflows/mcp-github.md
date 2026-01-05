# 🌐 Workflow: MCP GitHub (Perplexity, Claude.ai)

Este guia explica como trabalhar no **Agora Contabilidade** usando **ferramentas AI com MCP GitHub** (Perplexity, Claude.ai).

---

## 🎯 Overview

**Ferramenta:** Perplexity AI ou Claude.ai (com MCP GitHub integration)
**Acesso:** Via GitHub API (edição remota)
**Vantagem Principal:** Trabalhar de qualquer device, criar PRs diretamente

---

## 🚀 Setup Inicial

### 1. Configurar MCP GitHub (Perplexity)

#### No Perplexity Desktop/App:

1. Abrir **Settings** → **Integrations**
2. Ativar **GitHub MCP Server**
3. Autorizar acesso ao repositório `brun04maral/agora-contabilidade`
4. Confirmar permissões:
   - Read repository content
   - Create/edit files
   - Create pull requests
   - Manage branches

#### Verificar Configuração:

No Perplexity, enviar:
```
List files in brun04maral/agora-contabilidade repository, main branch
```

Deves ver a estrutura do projeto Django.

---

## 🔄 Workflow Diário

### **Cenário 1: Quick Fix / Edição Pequena**

#### Prompt para Perplexity:

```markdown
Vou fazer uma edição no projeto Agora Contabilidade (brun04maral/agora-contabilidade).

**Contexto:**
- Repositório: brun04maral/agora-contabilidade
- Ficheiro para editar: [caminho/do/ficheiro.py]
- Mudança necessária: [descrição clara]

**Passos:**
1. Lê o ficheiro atual em main
2. Mostra-me a mudança proposta
3. Cria uma nova branch: quickfix-[nome]-YYYYMMDD
4. Aplica a mudança
5. Cria um commit descritivo
6. Abre pull request

Vamos!
```

---

### **Cenário 2: Atualizar Documentação**

#### Prompt para Perplexity:

```markdown
Atualizar documentação do Agora Contabilidade.

**Ficheiro:** docs/SALDOS_DASHBOARD.md
**Mudanças:**
- Adicionar explicação do novo cálculo de prémios
- Atualizar exemplo de saldo atual vs projetado

**Passos:**
1. Lê ficheiro atual
2. Aplica mudanças
3. Cria branch: docs-saldos-update-20260105
4. Commit: "docs: update SALDOS_DASHBOARD with new premio calculation"
5. Abre PR

Vamos!
```

---

### **Cenário 3: Code Review**

#### Prompt para Perplexity:

```markdown
Code review do PR #45 no Agora Contabilidade.

**PR:** brun04maral/agora-contabilidade#45

**Objetivos:**
- Verificar código Django (models, views, admin)
- Verificar queries PostgreSQL
- Verificar segurança (OWASP top 10)
- Sugerir melhorias

Faz review e comenta no PR!
```

---

## 📝 Templates de Commits

### Feature

```bash
feat: add [funcionalidade]

- [detalhe 1]
- [detalhe 2]

🤖 Generated with [Perplexity/Claude.ai]
Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
```

### Bug Fix

```bash
fix: resolve [problema]

- Root cause: [explicação]
- Solution: [como foi resolvido]

Closes #[issue-number]

🤖 Generated with [Perplexity/Claude.ai]
Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
```

### Documentação

```bash
docs: update [ficheiro]

- [mudança 1]
- [mudança 2]

🤖 Generated with [Perplexity/Claude.ai]
Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
```

---

## 🎯 Casos de Uso Ideais

### ✅ Quando Usar MCP GitHub

1. **Documentação**
   - Atualizar README, README-DEV
   - Criar/editar ficheiros em `docs/`
   - Changelog updates

2. **Quick Fixes**
   - Corrigir typos
   - Atualizar configs (settings.py - não secrets!)
   - Pequenas mudanças CSS em templates

3. **Configuração**
   - Editar `.env.example`
   - Atualizar `requirements.txt`
   - Modificar `docker-compose.yml`

4. **Code Review**
   - Revisar PRs
   - Comentar em issues
   - Sugerir mudanças

5. **Trabalho Mobile**
   - Qualquer edição enquanto estás fora

---

## ⚠️ Limitações

### ❌ Quando NÃO Usar MCP GitHub

1. **Django Development**
   - Criar/modificar models (precisa migrations)
   - Modificar views complexas
   - Debugging com Django shell

2. **Database Changes**
   - Migrations
   - SQL manual
   - Queries complexas

3. **Testing**
   - Não consegues rodar Docker
   - Não consegues testar no servidor
   - Não consegues fazer collectstatic

**Solução:** Usa [VS Code Extension workflow](vscode-extension.md) para estes casos.

---

## 🔀 Workflow Híbrido (Recomendado)

### Combinar MCP + VS Code Extension

#### 1️⃣ **Planeamento** (MCP GitHub - Perplexity)

```markdown
Agora Contabilidade - Planear feature: Dashboard fiscal

**Requisitos:**
- Dashboard com IVA trimestral
- Cálculo automático de IRS
- Exportação para Excel

**Tarefas:**
1. Criar RFC em docs/rfcs/dashboard-fiscal.md
2. Listar models que serão afetados
3. Propor arquitetura

Cria o RFC e abre issue no GitHub!
```

#### 2️⃣ **Implementação** (VS Code Extension)

- Conectar ao servidor via SSH
- Criar models Django
- Criar migrations
- Implementar views/admin
- Testar no servidor

#### 3️⃣ **Documentação** (MCP GitHub - Perplexity)

```markdown
Agora Contabilidade - Documentar dashboard fiscal

**Atualizar:**
- README.md (adicionar na lista de features)
- docs/DASHBOARD_FISCAL.md (novo ficheiro)
- CHANGELOG.md (adicionar na próxima versão)

Cria PR com estas atualizações!
```

---

## 🛠️ Comandos Úteis (via Perplexity)

### Ler Ficheiro Django

```
Read file agora_web/core/models.py from brun04maral/agora-contabilidade (main branch)
```

### Criar Documentação

```
Create new file docs/NEW_FEATURE.md in brun04maral/agora-contabilidade:

Branch: docs-new-feature-20260105
Content: [conteúdo aqui]
Commit: "docs: add new feature documentation"
```

### Editar Config

```
Edit file .env.example in brun04maral/agora-contabilidade:

Branch: chore-update-env-example
Add line: FEATURE_FLAG_DASHBOARD_FISCAL=false
Commit: "chore: add FEATURE_FLAG_DASHBOARD_FISCAL to .env.example"
```

---

## 📚 Prompts Reutilizáveis

### Atualizar Documentação Django

```markdown
Agora Contabilidade - Atualizar documentação

**Ficheiro:** [caminho]
**Mudanças:** [lista de mudanças]

**Contexto Django:**
- Models afetados: [listar]
- Views afetadas: [listar]
- Admin customizations: [listar]

**Passos:**
1. Ler ficheiro atual
2. Aplicar mudanças
3. Criar branch: docs-update-YYYYMMDD
4. Commit descritivo
5. Abrir PR

Executa!
```

### Code Review Django

```markdown
Agora Contabilidade - Review PR #[número]

**Focar em:**
- Django best practices
- PostgreSQL query optimization
- Security (SQL injection, XSS, etc.)
- Unfold admin UI consistency

Faz review completo e comenta!
```

---

## 🔄 Sincronização com Servidor

### Depois de Merge do PR

Como o MCP GitHub **não tem acesso ao servidor**, precisas fazer deploy manual:

```bash
# SSH para o servidor
ssh zumine@[servidor]

# Ir para o projeto
cd ~/amp/docker/app

# Pull das mudanças
git pull origin main

# Deploy
./deploy.sh
```

**Nota:** O `deploy.sh` já faz:
- Backup da BD
- Build Docker
- Apply migrations
- Collectstatic
- Health checks

---

## 💡 Tips & Tricks

### Para Perplexity

1. **Seja específico** - branch name, commit message, etc.
2. **Menciona Django** - ajuda a AI a dar contexto correto
3. **Peça para ler ficheiros** antes de editar
4. **Verifique PRs** antes de mergear (especialmente migrations!)

### Para Claude.ai

1. **Cria projetos** para manter contexto
2. **Usa MCP** para edição direta no GitHub
3. **Documenta bem** - Django é complexo, contexto é importante

---

## 🆘 Troubleshooting

### MCP GitHub não funciona

**Solução:**
1. Verificar autorização GitHub (Settings → Integrations)
2. Re-autorizar se necessário
3. Verificar permissões do repositório privado

### PR não cria migrations

**Solução:**
- MCP GitHub edita apenas código
- Migrations precisam ser criadas no servidor com `makemigrations`
- Adicionar nota no PR: "⚠️ Precisa criar migrations no servidor"

### Mudanças não aplicadas em produção

**Solução:**
- MCP GitHub edita apenas o repositório
- Precisa SSH + `git pull` + `./deploy.sh`

---

## 📚 Recursos

- **Contexto Universal:** [`.claude/claude.md`](../claude.md)
- **Guia Geral:** [`README-DEV.md`](../../README-DEV.md)
- **Workflow VS Code:** [`vscode-extension.md`](vscode-extension.md)
- **Prompts:** [`.claude/prompts/`](../prompts/)
- **Docs Django:** [`docs/`](../../docs/)

---

**Última Atualização:** 2026-01-05
