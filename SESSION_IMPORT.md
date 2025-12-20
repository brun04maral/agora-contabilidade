# 🔄 Workflow Claude Code - Guia Rápido

**Última atualização:** 2025-12-20 WET

---

## 📌 Como Funciona

**Claude Code trabalha com worktrees** - cria automaticamente um branch isolado a cada sessão em:
```
~/.claude-worktrees/agora-contabilidade/<branch-name>/
```

Este worktree partilha o mesmo histórico Git que a pasta principal (`/Users/brunoamaral/Documents/github/agora-contabilidade/`) mas trabalha numa branch separada.

---

## 🎯 Para Novas Sessões Claude

### **Início Simples:**
```
Lê README.md e memory/CURRENT_STATE.md para contexto completo do projeto.
```

**Isto é suficiente!** O Claude começa sempre da `main` que está atualizada (após merges de PRs anteriores).

---

## 🔄 Workflow Completo

### **Durante a Sessão:**

1. **Claude trabalha no worktree**
   - Edita ficheiros
   - Faz commits
   - Executa testes

2. **Push para GitHub**
   ```bash
   git push origin <branch-name>
   ```

3. **Criar Pull Request**
   ```bash
   gh pr create --base main --head <branch-name>
   ```

### **Após a Sessão:**

4. **Merge via GitHub**
   - Abrir PR no browser: `gh pr view <numero> --web`
   - Clicar "Merge pull request"
   - Escolher "Create a merge commit"
   - Confirmar merge

5. **Sync pasta principal (tua)**
   ```bash
   cd /Users/brunoamaral/Documents/github/agora-contabilidade/
   git checkout main
   git pull origin main
   ```

6. **Limpeza (opcional)**
   ```bash
   # Apagar branch remota
   git push origin --delete <branch-name>

   # Apagar branch local (se existir)
   git branch -d <branch-name>
   ```

---

## 📚 Documentação Detalhada

Para workflow completo, problemas comuns, comandos úteis e mais:

👉 **Ver [`memory/GIT_WORKFLOW.md`](./memory/GIT_WORKFLOW.md)** (20KB+, guia completo)

---

## 🆘 Troubleshooting Rápido

### Problema: "Conflitos de merge no PR"
**Solução:**
```bash
git fetch origin main
git merge origin/main
# Resolver conflitos
git add .
git commit -m "Merge main into <branch>"
git push origin <branch-name>
```

### Problema: "Branch desatualizada após merge"
**Solução:**
```bash
cd /Users/brunoamaral/Documents/github/agora-contabilidade/
git checkout main
git pull origin main
```

### Problema: "Muitas branches antigas"
**Solução:**
```bash
# Apagar todas branches claude/* locais
git branch | grep 'claude/' | xargs -n 1 git branch -D

# Apagar todas branches claude/* remotas
git branch -r | grep 'origin/claude/' | sed 's|origin/||' | xargs -I {} git push origin --delete {}
```

---

## 🎯 Cheat Sheet - Comandos Essenciais

```bash
# Ver branches
git branch -a

# Ver status
git status

# Commit
git add .
git commit -m "mensagem"

# Push
git push origin <branch-name>

# Pull Request
gh pr create --base main --head <branch-name>
gh pr view <numero> --web

# Sync main local
cd /Users/brunoamaral/Documents/github/agora-contabilidade/
git checkout main
git pull origin main
```

---

## 📖 Links Úteis

- 📚 **Workflow completo:** [`memory/GIT_WORKFLOW.md`](./memory/GIT_WORKFLOW.md)
- 📊 **Estado do projeto:** [`memory/CURRENT_STATE.md`](./memory/CURRENT_STATE.md)
- 📝 **Tarefas:** [`memory/TODO.md`](./memory/TODO.md)
- 🏗️ **Arquitectura:** [`memory/ARCHITECTURE.md`](./memory/ARCHITECTURE.md)

---

**© 2025 Agora Media Production**
**Mantido por:** Bruno Amaral + Claude Code
