# 🔄 Git Workflow - Claude Code com Worktrees

**Última atualização:** 2025-12-20 WET
**Autor:** Claude Sonnet 4.5 + Bruno Amaral

---

## 📌 Visão Geral

Este documento explica como funciona o workflow de Git quando trabalhas com Claude Code, incluindo worktrees, branches, pull requests e merge.

---

## 🏗️ Arquitetura: 2 Repositórios, 1 Histórico Git

### **Pasta Principal (Tua)**
```
/Users/brunoamaral/Documents/github/agora-contabilidade/
├── Branch: main
├── Uso: Desenvolvimento manual, produção
└── Sincronizado com: origin/main (GitHub)
```

### **Worktree Claude (Temporário)**
```
~/.claude-worktrees/agora-contabilidade/<branch-name>/
├── Branch: <branch-name> (ex: nervous-mendeleev)
├── Uso: Sessões Claude Code
├── Partilha: Mesmo .git que pasta principal
└── Sincronizado com: origin/<branch-name> (GitHub)
```

**IMPORTANTE:** Ambos partilham o **mesmo histórico Git**, mas em pastas diferentes.

---

## 🔄 Workflow Completo - Sessão Claude Code

### **Fase 1: Início de Sessão**

1. **Claude Code cria worktree automático**
   ```
   Local: ~/.claude-worktrees/agora-contabilidade/<branch-name>/
   Branch: <branch-name> (criado do main)
   ```

2. **Claude trabalha no worktree**
   - Lê ficheiros
   - Edita código
   - Executa testes
   - Faz commits

### **Fase 2: Desenvolvimento**

3. **Commits locais**
   ```bash
   # Claude faz commits no worktree
   git add .
   git commit -m "feat: nova feature"
   ```

4. **Push para GitHub**
   ```bash
   git push origin <branch-name>
   ```

### **Fase 3: Pull Request**

5. **Criar PR no GitHub**
   ```bash
   # Via CLI
   gh pr create --base main --head <branch-name> --title "..." --body "..."

   # Ou via Web
   https://github.com/brun04maral/agora-contabilidade/pulls
   ```

6. **Resolver conflitos (se houver)**
   ```bash
   # Fetch latest main
   git fetch origin main

   # Merge main into branch
   git merge origin/main

   # Resolver conflitos manualmente
   # Em caso de dúvida, aceitar alterações da branch atual:
   git checkout --ours <ficheiro>

   # Commit merge
   git add .
   git commit -m "Merge main into <branch-name>"
   git push origin <branch-name>
   ```

### **Fase 4: Merge para Main**

7. **Merge via GitHub**
   - Opção 1: Via Web Interface (RECOMENDADO)
     1. Abrir PR: `gh pr view <numero> --web`
     2. Clicar "Merge pull request"
     3. Escolher "Create a merge commit"
     4. Confirmar merge
     5. Clicar "Delete branch" (opcional)

   - Opção 2: Via CLI
     ```bash
     gh pr merge <numero> --merge --delete-branch
     ```

   - Opção 3: Via Terminal Manual
     ```bash
     cd /Users/brunoamaral/Documents/github/agora-contabilidade/
     git checkout main
     git pull origin main
     git merge <branch-name>
     git push origin main
     ```

### **Fase 5: Atualizar Pasta Principal**

8. **Sincronizar main local**
   ```bash
   cd /Users/brunoamaral/Documents/github/agora-contabilidade/
   git checkout main
   git pull origin main
   ```

### **Fase 6: Limpeza**

9. **Apagar branch remota** (se não foi apagada no merge)
   ```bash
   git push origin --delete <branch-name>
   ```

10. **Apagar branch local** (opcional)
    ```bash
    git branch -d <branch-name>
    ```

11. **Apagar worktree** (opcional, Claude limpa automaticamente)
    ```bash
    rm -rf ~/.claude-worktrees/agora-contabilidade/<branch-name>
    ```

---

## 🧹 Limpeza de Branches Antigas

### **Listar branches**
```bash
# Locais
git branch

# Remotas
git branch -r

# Todas
git branch -a
```

### **Apagar múltiplas branches locais**
```bash
# Apagar todas branches claude/* locais
git branch | grep 'claude/' | xargs -n 1 git branch -D
```

### **Apagar múltiplas branches remotas**
```bash
# Apagar todas branches claude/* remotas
git branch -r | grep 'origin/claude/' | sed 's|origin/||' | xargs -I {} git push origin --delete {}
```

---

## 📊 Estados das Branches

### **Branch Main**
- **Local:** `/Users/brunoamaral/Documents/github/agora-contabilidade/`
- **Remota:** `origin/main` (GitHub)
- **Uso:** Código de produção, sempre estável
- **Atualização:** Após merge de PRs

### **Branch de Trabalho (ex: nervous-mendeleev)**
- **Local:** `~/.claude-worktrees/agora-contabilidade/nervous-mendeleev/`
- **Remota:** `origin/nervous-mendeleev` (GitHub)
- **Uso:** Desenvolvimento de features
- **Vida útil:** Até merge para main, depois apagar

---

## ⚠️ Problemas Comuns

### **Problema 1: "Pull Request is not mergeable"**
**Causa:** Conflitos com main

**Solução:**
```bash
git fetch origin main
git merge origin/main
# Resolver conflitos
git add .
git commit -m "Merge main into <branch>"
git push origin <branch-name>
```

### **Problema 2: "fatal: 'main' is already used by worktree"**
**Causa:** Tentar fazer checkout de branch que já está em uso

**Solução:** Fazer merge via GitHub Web Interface em vez de CLI

### **Problema 3: Branch local desatualizada**
**Causa:** Esqueceste de fazer pull após merge

**Solução:**
```bash
cd /Users/brunoamaral/Documents/github/agora-contabilidade/
git checkout main
git pull origin main
```

---

## 🎯 Boas Práticas

### ✅ **DO (Fazer)**
- ✅ Fazer pull da main antes de começar trabalho novo
- ✅ Commits frequentes com mensagens descritivas
- ✅ Testar tudo antes de fazer merge
- ✅ Apagar branches após merge
- ✅ Manter main sempre estável
- ✅ Usar PRs para revisão de código

### ❌ **DON'T (Não Fazer)**
- ❌ Trabalhar diretamente na main
- ❌ Fazer push --force para main
- ❌ Acumular muitas branches antigas
- ❌ Fazer merge sem testar
- ❌ Commitar ficheiros sensíveis (.env, credentials)
- ❌ Fazer commits com "WIP" na main

---

## 📋 Comandos Úteis - Cheat Sheet

### **Status e Info**
```bash
git status                    # Estado do repositório
git log --oneline -10        # Últimos 10 commits
git branch -a                # Todas as branches
git remote -v                # Remotes configurados
```

### **Navegação**
```bash
git checkout main            # Mudar para main
git checkout <branch>        # Mudar para branch
git checkout -b <branch>     # Criar e mudar para nova branch
```

### **Sincronização**
```bash
git fetch origin             # Buscar alterações do GitHub
git pull origin main         # Pull da main
git push origin <branch>     # Push da branch
```

### **Merge e Conflitos**
```bash
git merge <branch>           # Merge branch para atual
git merge --abort            # Cancelar merge
git checkout --ours <file>   # Aceitar versão atual
git checkout --theirs <file> # Aceitar versão da branch
```

### **Limpeza**
```bash
git branch -d <branch>                    # Apagar branch local
git push origin --delete <branch>         # Apagar branch remota
git remote prune origin                   # Limpar refs remotas antigas
```

### **GitHub CLI (gh)**
```bash
gh pr list                              # Listar PRs
gh pr create                            # Criar PR
gh pr view <numero>                     # Ver PR
gh pr view <numero> --web              # Abrir PR no browser
gh pr merge <numero> --merge           # Merge PR
```

---

## 🔗 Documentação Relacionada

- 📄 **SESSION_IMPORT.md** - Como importar sessão anterior
- 📄 **memory/CURRENT_STATE.md** - Estado atual do projeto
- 📄 **memory/CHANGELOG.md** - Histórico de alterações
- 📄 **README.md** - Visão geral do projeto

---

## 📊 Exemplo Prático - Sessão 20/12/2025

### **Situação Inicial**
- Branch: `nervous-mendeleev`
- Worktree: `~/.claude-worktrees/agora-contabilidade/nervous-mendeleev/`
- Commits: 2 (SPRINT 9 + DateRangePicker)

### **Passos Executados**

1. **Desenvolvimento**
   ```bash
   # Commit 1: SPRINT 9
   git commit -m "feat: SPRINT 9 - Completar migração BaseForm/BaseScreen (100%)"

   # Commit 2: DateRangePicker
   git commit -m "feat(ux): adicionar DateRangePickerDropdown"

   git push origin nervous-mendeleev
   ```

2. **Pull Request**
   ```bash
   gh pr create --base main --head nervous-mendeleev
   # PR #7 criado
   ```

3. **Resolver Conflitos**
   ```bash
   git fetch origin main
   git merge origin/main
   # 11 ficheiros com conflitos
   git checkout --ours .gitignore memory/CHANGELOG.md ...
   git add .
   git commit -m "Merge main into nervous-mendeleev"
   git push origin nervous-mendeleev
   ```

4. **Merge via GitHub**
   ```bash
   gh pr view 7 --web
   # Clicar "Merge pull request" → "Confirm merge"
   # PR #7 merged com sucesso
   ```

5. **Limpeza**
   ```bash
   # Apagar 35 branches antigas (17 locais + 18 remotas)
   git branch | grep 'claude/' | xargs -n 1 git branch -D
   git branch -r | grep 'origin/claude/' | sed 's|origin/||' | xargs -I {} git push origin --delete {}

   # Apagar branch nervous-mendeleev
   git push origin --delete nervous-mendeleev
   ```

6. **Atualizar Main**
   ```bash
   cd /Users/brunoamaral/Documents/github/agora-contabilidade/
   git checkout main
   git pull origin main
   # 12 ficheiros atualizados (322 linhas adicionadas, 87 removidas)
   ```

### **Resultado Final**
- ✅ Código na main
- ✅ 35 branches antigas apagadas
- ✅ Repositório limpo e organizado
- ✅ Pasta principal sincronizada

---

**Mantido por:** Bruno Amaral + Claude Code
**Para dúvidas:** Consultar este documento ou `memory/README.md`
