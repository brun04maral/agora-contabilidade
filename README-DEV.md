# 🛠️ Guia de Desenvolvimento - Agora Contabilidade

**Para:** Bruno & Rafael
**Objetivo:** Desenvolvimento limpo e organizado com ou sem AI assistants

---

## 🚀 Começar Nova Sessão de Desenvolvimento

### 1. **Prompt Inicial (Copiar & Colar para Claude)**

```
Olá! Vou trabalhar no projeto Agora Contabilidade.

**Contexto do projeto:**
- Lê `.claude/claude.md` para contexto completo
- Branch atual: [nome-da-branch]
- Tarefa: [descrever o que queres fazer]

**Antes de começar:**
1. Verifica o estado atual do projeto (git status, containers running)
2. Confirma que estamos na branch correta
3. Cria um plano de trabalho usando TodoWrite

Vamos começar!
```

### 2. **Checklist Antes de Começar**

- [ ] Branch correta (`git branch`)
- [ ] Base de dados a correr (`docker compose ps`)
- [ ] `.env` configurado corretamente
- [ ] Última versão do código (`git pull`)

---

## 🔄 Continuar Sessão Existente

### **Prompt de Continuação**

```
Vou continuar a trabalhar no projeto Agora Contabilidade.

**Última sessão:**
- Branch: [nome]
- Última tarefa: [o que estavas a fazer]
- Estado: [completo/incompleto/bloqueado]

**Próximo passo:**
[descrever o que queres fazer agora]

**Contexto adicional:**
[qualquer info relevante - erros, mudanças, etc]

Continua de onde parámos!
```

---

## 📦 Workflow de Desenvolvimento Limpo

### **Passo a Passo para Novas Features**

#### 1. **Criar Feature Branch**
```bash
# Nomenclatura: claude/nome-da-feature-xxxxx
git checkout main
git pull origin main
git checkout -b claude/nova-feature-abc12
```

#### 2. **Desenvolver**
- Faz alterações incrementais
- Testa cada mudança
- Commita frequentemente com mensagens claras

#### 3. **Commits Descritivos**
```bash
# ✅ BOM
git commit -m "feat: add fiscal dashboard with IVA calculations"
git commit -m "fix: resolve 404 error in Traefik routing"
git commit -m "docs: update claude.md with deployment steps"

# ❌ MAU
git commit -m "fixes"
git commit -m "stuff"
git commit -m "asdf"
```

**Prefixos úteis:**
- `feat:` - Nova funcionalidade
- `fix:` - Correção de bug
- `docs:` - Documentação
- `refactor:` - Refactoring (sem mudar comportamento)
- `test:` - Testes
- `chore:` - Manutenção (deps, configs, etc)

#### 4. **Testar Localmente**
```bash
# Rebuild após mudanças
docker compose down
docker compose up -d --build web

# Ver logs
docker compose logs -f web

# Testar migrations
docker compose exec web python manage.py migrate --check
docker compose exec web python manage.py check
```

#### 5. **Push & Merge**
```bash
# Push da feature branch
git push -u origin claude/nova-feature-abc12

# Quando pronta, merge para main
git checkout main
git merge claude/nova-feature-abc12
git push origin main
```

---

## 🎯 Deployment para Produção

### **NO SERVIDOR** (~/amp/docker/app/)

```bash
# Opção Automática (Recomendada)
cd ~/amp/docker/app
./deploy.sh

# Ou Manual
git pull origin main
docker compose down
docker compose build --no-cache web
docker compose up -d
docker compose exec web python manage.py migrate
docker compose exec web python manage.py collectstatic --noinput
```

---

## 📝 Arquivar Sessão de Desenvolvimento

### **Prompt de Finalização (para Claude)**

```
Sessão de desenvolvimento terminada!

**Resumo do trabalho:**
- Features implementadas: [lista]
- Bugs resolvidos: [lista]
- Commits criados: [número]

**Antes de terminar:**
1. Atualiza `.claude/claude.md` se houver mudanças na arquitetura
2. Cria/atualiza documentação em `docs/` se necessário
3. Faz commit de todas as mudanças (incluindo docs)
4. Verifica que está tudo em produção (se aplicável)
5. Cria resumo desta sessão para próxima vez

**Estado final:**
- Branch: [nome]
- Último commit: [hash + mensagem]
- Produção atualizada: [sim/não]
- Issues conhecidos: [lista ou "nenhum"]

Cria um resumo conciso desta sessão que posso guardar!
```

### **Template de Resumo de Sessão**

Guarda isto num ficheiro `.session-notes/YYYY-MM-DD.md`:

```markdown
# Sessão Dev - [Data]

## 🎯 Objetivo
[O que querias fazer]

## ✅ Completado
- [x] Feature X implementada
- [x] Bug Y resolvido
- [x] Docs atualizadas

## 🔧 Mudanças Técnicas
- Ficheiros alterados: [lista]
- Migrations criadas: [sim/não]
- Deployment: [sim/não]

## 📝 Notas para Próxima Sessão
- [Qualquer coisa importante]
- [TODOs pendentes]

## 🔗 Commits
- `abc1234` - feat: descrição
- `def5678` - fix: descrição
```

---

## 🆘 Troubleshooting Comum

### **Problema: "Lost changes after deployment"**
**Solução:**
1. SEMPRE faz commit antes de deploy
2. Verifica que código está em Git: `git status`
3. Verifica que DB está no volume correto (ver `.claude/claude.md`)

### **Problema: "Migrations conflicting"**
**Solução:**
1. Verifica qual branch tem qual migration: `git log --oneline -- agora_web/core/migrations/`
2. Merge cuidadosamente ou cria nova migration vazia
3. Se necessário, marca como fake: ver `docs/DATABASE_MANUAL_CHANGES.md`

### **Problema: "Docker não atualiza código"**
**Solução:**
```bash
docker compose down
docker compose build --no-cache web
docker compose up -d
```

### **Problema: "CSS não carrega"**
**Solução:**
```bash
docker compose exec web python manage.py collectstatic --noinput --clear
```

---

## 🎨 Boas Práticas

### ✅ **FAZER**
- Criar feature branches para cada tarefa
- Commitar frequentemente com mensagens claras
- Testar localmente antes de fazer push
- Atualizar documentação quando arquitetura muda
- Fazer backup da DB antes de mudanças grandes
- Usar o script `deploy.sh` para deployment

### ❌ **NÃO FAZER**
- Commit direto em `main` (pre-commit hook vai bloquear!)
- Commit de ficheiros `.env` ou secrets
- Mudanças sem testar
- Esquecer de fazer `collectstatic` após mudanças de CSS
- Mudar nome do volume `agora_web_postgres_data`
- Fazer deployment sem backup

---

## 🔐 Segurança

### **Ficheiros NUNCA Commitados**
- `.env`
- `.env.production`
- `secrets.json`
- `credentials.json`
- Backups SQL (*.sql, *.sql.gz)

**O pre-commit hook vai bloquear isto automaticamente!**

### **Secrets Management**
- SEMPRE usa variáveis de ambiente
- NUNCA hardcodes passwords/tokens no código
- Guarda `.env` fora do Git
- Em produção: `.env` está em `~/amp/docker/app/.env` no servidor

---

## 📚 Recursos Úteis

### **Documentação do Projeto**
- **`.claude/claude.md`** - Contexto completo (LEITURA OBRIGATÓRIA!)
- **`docs/SALDOS_DASHBOARD.md`** - Dashboard de saldos
- **`docs/SOCIOS_MIGRATION.md`** - Modelo de sócios
- **`docs/DATABASE_MANUAL_CHANGES.md`** - Mudanças manuais na DB

### **Comandos Úteis**
```bash
# Django
docker compose exec web python manage.py shell
docker compose exec web python manage.py dbshell
docker compose exec web python manage.py check

# Git
git log --oneline --graph --all
git diff main..HEAD
git show HEAD

# Docker
docker compose ps
docker compose logs -f web
docker compose exec web bash
```

---

## 🎓 Prompts Especializados

### **Para Debugging**
```
Estou com um erro no Agora Contabilidade:

**Erro:** [colar erro completo]

**Contexto:**
- O que estava a fazer: [descrição]
- Quando aconteceu: [após deploy/após mudança/etc]
- Tentativas de fix: [o que já tentaste]

**Logs relevantes:**
[colar logs se tiveres]

Ajuda-me a debugar isto!
```

### **Para Refactoring**
```
Quero refatorar código no Agora Contabilidade:

**Código atual:** [ficheiro/função]
**Problema:** [o que está mal]
**Objetivo:** [como deve ficar]

**Restrições:**
- Não quebrar compatibilidade com DB
- Manter testes a passar
- Manter mesmo comportamento

Mostra-me um plano de refactoring!
```

### **Para Novas Features**
```
Quero adicionar uma nova feature ao Agora Contabilidade:

**Feature:** [descrição clara]
**Porquê:** [razão/problema que resolve]
**Contexto:** [onde encaixa na app]

**Requisitos:**
- [lista de requisitos]

**Questões:**
- [dúvidas que tens]

Cria um plano de implementação detalhado!
```

---

## 🎯 Workflow Recomendado (Resumo)

```
1. git checkout -b claude/feature-xxxxx
2. [desenvolver + testar localmente]
3. git add . && git commit -m "feat: descrição"
4. git push -u origin claude/feature-xxxxx
5. [testar mais se necessário]
6. git checkout main && git merge claude/feature-xxxxx
7. git push origin main
8. [NO SERVIDOR] ./deploy.sh
9. ✅ Verificar produção
10. 🎉 Done!
```

---

**Última atualização:** 2026-01-02
**Mantido por:** Bruno & Rafael
**Versão:** 1.0

---

**💡 Tip:** Guarda este ficheiro aberto enquanto desenvolves. É o teu GPS! 🗺️
