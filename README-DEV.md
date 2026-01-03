# 🛠️ Guia de Desenvolvimento - Agora Contabilidade

**Para:** Bruno & Rafael
**Objetivo:** Desenvolvimento ágil e organizado com Claude Code (VS Code Extension)
**Última Atualização:** 2026-01-03

---

## 🎯 Ambiente de Desenvolvimento ATUAL

**Trabalhamos DIRETAMENTE no servidor via VS Code Extension!**

### ✅ Novo Workflow (VS Code Extension)

```
┌─────────────────────────────────────────┐
│  VS Code (local) + Claude Extension    │
│           ↕ (SSH/Remote)                │
│  Servidor: ~/amp/docker/app/            │
│  - Código Django (agora_web/)           │
│  - Docker containers (web + db)         │
│  - Git repo                             │
└─────────────────────────────────────────┘
```

**Vantagens:**
- ✅ **Sem sincronização** - mudanças diretas no servidor
- ✅ **Teste imediato** - rebuild e teste na mesma máquina
- ✅ **Contexto completo** - tudo num só lugar
- ✅ **Deploy simples** - já estamos em produção

### ❌ Workflow ANTIGO (Descontinuado)

~~Claude standalone app → worktrees → push → pull no servidor~~

**Não usamos mais isto!** Documentação antiga em `archive-old-tkinter-app/`

---

## 🚀 Setup Inicial (Primeira Vez)

### 1. VS Code + Claude Extension

```bash
# Instalar extensão Claude Code no VS Code
# Abrir pasta remota via SSH: ~/amp/docker/app/

# Verificar ambiente
git status
docker compose ps
```

### 2. Checklist Ambiente

- [ ] VS Code conectado ao servidor via SSH
- [ ] Claude Extension instalada e ativa
- [ ] Git configurado (`git config user.name/email`)
- [ ] Docker containers a correr (`agora_web`, `agora_db`)
- [ ] `.env` configurado (já existe no servidor)

---

## 📂 Estrutura do Projeto (Limpa!)

```
~/amp/docker/app/
├── agora_web/              # 🎯 Django App (ATUAL)
│   ├── core/               # Models, Admin, Views
│   ├── config/             # Settings Django
│   ├── templates/          # Templates customizados
│   ├── static/             # CSS, JS, logos
│   └── manage.py
│
├── docker-compose.yml      # Containers: web + db
├── deploy.sh               # Script de deployment
├── .env                    # Environment variables
│
├── docs/                   # 📚 Documentação técnica
│   ├── SOCIOS_MIGRATION.md
│   ├── SALDOS_DASHBOARD.md
│   └── DATABASE_MANUAL_CHANGES.md
│
├── .claude/                # 🤖 Contexto para Claude
│   └── claude.md           # ⭐ LEITURA OBRIGATÓRIA
│
├── scripts/                # SQL scripts manuais
├── backups/                # Backups BD
├── excel/                  # Ficheiros Excel import
└── media/                  # Logos da empresa

archive-old-tkinter-app/    # 📦 App antiga (apenas histórico)
```

---

## 🔄 Workflow de Desenvolvimento Diário

### **Passo a Passo para Novas Features**

#### 1️⃣ **Criar Feature Branch**

```bash
# Sempre partir de main atualizada
git checkout main
git pull origin main

# Criar branch com nomenclatura clara
git checkout -b claude/nome-da-feature-xxxxx
```

**Convenção de nomes:**
- `claude/feat-dashboard-xxx` - Nova funcionalidade
- `claude/fix-bug-saldos-xxx` - Correção de bug
- `claude/refactor-models-xxx` - Refactoring
- `claude/docs-update-xxx` - Atualização de docs

#### 2️⃣ **Desenvolver + Testar Localmente**

```bash
# Fazer mudanças no código (via Claude ou manual)

# Testar mudanças
docker compose down
docker compose up -d --build web

# Ver logs
docker compose logs -f web

# Testar no browser
# https://app.agoramediaproduction.pt
```

**Ciclo de desenvolvimento:**
1. Fazer mudanças no código
2. Rebuild container se necessário
3. Testar funcionalidade
4. Repetir até funcionar

#### 3️⃣ **Commits Descritivos**

```bash
# Adicionar ficheiros
git add agora_web/core/models.py
git add agora_web/core/admin.py

# Commit com mensagem clara
git commit -m "feat: add dashboard fiscal com cálculos IVA

- Criado modelo FiscalData para armazenar dados fiscais
- Adicionado dashboard no admin com cards de IVA
- Implementada lógica de cálculo trimestral

🤖 Generated with Claude Code
Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

**Prefixos de commits:**
| Prefixo | Uso | Exemplo |
|---------|-----|---------|
| `feat:` | Nova funcionalidade | `feat: add logout button to navbar` |
| `fix:` | Correção de bug | `fix: resolve 404 error in Traefik routing` |
| `docs:` | Documentação | `docs: update README-DEV with new workflow` |
| `refactor:` | Refactoring (sem mudar comportamento) | `refactor: extract saldos calculation to utils` |
| `test:` | Testes | `test: add unit tests for SaldosCalculator` |
| `chore:` | Manutenção (deps, configs) | `chore: update Django to 5.1` |

#### 4️⃣ **Push da Branch**

```bash
# Push da feature branch
git push -u origin claude/nome-da-feature-xxxxx
```

#### 5️⃣ **Testar Mais (Se Necessário)**

Se precisares fazer mais mudanças:

```bash
# Fazer mudanças
# Testar
git add .
git commit -m "fix: corrigir validação no formulário"
git push  # (já está com upstream configurado)
```

#### 6️⃣ **Merge para Main**

Quando a feature estiver **pronta e testada**:

```bash
# Voltar para main
git checkout main

# ⚠️ IMPORTANTE: Sincronizar com remote primeiro!
git pull origin main

# Merge da feature branch
git merge claude/nome-da-feature-xxxxx

# Push para produção
git push origin main
```

#### 7️⃣ **Deployment Final**

```bash
# Já estamos no servidor, basta fazer deploy
./deploy.sh

# OU manualmente:
docker compose down
docker compose build --no-cache web
docker compose up -d
docker compose exec web python manage.py migrate
docker compose exec web python manage.py collectstatic --noinput

# Verificar logs
docker compose logs -f web

# Testar no browser
# https://app.agoramediaproduction.pt
```

#### 8️⃣ **Limpeza (Opcional)**

```bash
# Apagar branch local (se já não for necessária)
git branch -d claude/nome-da-feature-xxxxx

# Apagar branch remote (se quiser limpar)
git push origin --delete claude/nome-da-feature-xxxxx
```

---

## 🎨 Boas Práticas

### ✅ **FAZER**

- ✅ Criar **feature branches** para cada tarefa
- ✅ **Commitar frequentemente** com mensagens claras
- ✅ **Testar localmente** antes de merge para main
- ✅ **Rebuild Docker** após mudanças de código (`--build`)
- ✅ Fazer **backup da BD** antes de mudanças grandes
- ✅ Atualizar **documentação** quando arquitetura muda
- ✅ Usar script `deploy.sh` para deployment
- ✅ Fazer `git pull` antes de merge

### ❌ **NÃO FAZER**

- ❌ Commit direto em `main` (usar branches!)
- ❌ Commit de ficheiros `.env` ou secrets
- ❌ Mudanças sem testar
- ❌ Esquecer `collectstatic` após mudanças CSS
- ❌ Mudar nome do volume `agora_web_postgres_data`
- ❌ Deployment sem backup
- ❌ Assumir que código está atualizado (sempre `git pull`)

---

## 🐛 Troubleshooting Comum

### **Problema: Docker não atualiza código**

```bash
# Código está na imagem Docker, não em volume
# Solução: rebuild
docker compose down
docker compose build --no-cache web
docker compose up -d
```

### **Problema: CSS não carrega**

```bash
# Solução: collectstatic
docker compose exec web python manage.py collectstatic --noinput --clear
```

### **Problema: Migration conflicting**

```bash
# Ver histórico de migrations
git log --oneline -- agora_web/core/migrations/

# Solução: criar merge migration ou fake
# Ver docs/DATABASE_MANUAL_CHANGES.md
```

### **Problema: Container não inicia**

```bash
# Ver logs completos
docker compose logs web

# Verificar BD
docker compose exec db psql -U agora -d agora_production

# Rebuild completo
docker compose down -v  # ⚠️ CUIDADO: apaga volumes!
docker compose up -d --build
```

### **Problema: Git conflicts ao fazer merge**

```bash
# Ver ficheiros em conflito
git status

# Resolver manualmente ou
git mergetool

# Após resolver
git add .
git commit -m "merge: resolve conflicts from claude/feature-xxx"
```

---

## 🔧 Comandos Úteis

### **Django**

```bash
# Shell Django
docker compose exec web python manage.py shell

# DB Shell
docker compose exec web python manage.py dbshell

# Check do sistema
docker compose exec web python manage.py check

# Criar superuser
docker compose exec web python manage.py createsuperuser

# Ver migrations
docker compose exec web python manage.py showmigrations

# Aplicar migrations
docker compose exec web python manage.py migrate

# Criar migration
docker compose exec web python manage.py makemigrations
```

### **Git**

```bash
# Estado atual
git status
git branch

# Histórico
git log --oneline --graph --all
git log --oneline -- agora_web/core/

# Ver diferenças
git diff
git diff main..HEAD
git show HEAD

# Branches remotas
git branch -r
git fetch --all
```

### **Docker**

```bash
# Estado dos containers
docker compose ps

# Logs
docker compose logs -f web
docker compose logs -f db

# Entrar no container
docker compose exec web bash
docker compose exec db bash

# Rebuild
docker compose up -d --build web

# Restart
docker compose restart web

# Parar tudo
docker compose down
```

### **PostgreSQL**

```bash
# Aceder à DB
docker compose exec db psql -U agora -d agora_production

# Backup
docker compose exec db pg_dump -U agora agora_production > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore (CUIDADO!)
cat backup.sql | docker compose exec -T db psql -U agora -d agora_production
```

---

## 📝 Documentação Importante

### **Essenciais (Ler Sempre!)**

| Ficheiro | Descrição |
|----------|-----------|
| [`.claude/claude.md`](.claude/claude.md) | ⭐ **Contexto completo do projeto** - arquitetura, deployment, issues conhecidos |
| [`README-DEV.md`](README-DEV.md) | 📖 Este ficheiro - workflow de desenvolvimento |
| [`docs/SALDOS_DASHBOARD.md`](docs/SALDOS_DASHBOARD.md) | Implementação do dashboard de saldos (feature principal) |
| [`docs/SOCIOS_MIGRATION.md`](docs/SOCIOS_MIGRATION.md) | Como modelo Socio foi implementado |

### **Técnicas**

| Ficheiro | Descrição |
|----------|-----------|
| [`docs/DATABASE_MANUAL_CHANGES.md`](docs/DATABASE_MANUAL_CHANGES.md) | Mudanças manuais na BD (SQL scripts) |
| [`docker-compose.yml`](docker-compose.yml) | Configuração Docker (web + db + traefik) |
| [`.env.example`](.env.example) | Template de environment variables |

---

## 🎓 Prompts para Claude

### **Iniciar Nova Sessão**

```
Vou trabalhar no projeto Agora Contabilidade.

**Contexto:**
- Lê .claude/claude.md para contexto completo
- Branch atual: [nome-da-branch]
- Tarefa: [descrever o que queres fazer]

**Antes de começar:**
1. Verifica estado atual (git status, docker ps)
2. Confirma que estamos na branch correta
3. Cria plano com TodoWrite

Vamos começar!
```

### **Continuar Sessão Existente**

```
Continuar trabalho no Agora Contabilidade.

**Última sessão:**
- Branch: [nome]
- Última tarefa: [o que estavas a fazer]
- Estado: [completo/incompleto/bloqueado]

**Próximo passo:**
[descrever o que queres fazer agora]

Continua!
```

### **Debugging**

```
Erro no Agora Contabilidade:

**Erro:** [colar erro completo]

**Contexto:**
- O que estava a fazer: [descrição]
- Quando aconteceu: [após deploy/mudança/etc]
- Tentativas: [o que já tentaste]

**Logs:**
[colar logs relevantes]

Ajuda a debugar!
```

### **Nova Feature**

```
Adicionar feature ao Agora Contabilidade:

**Feature:** [descrição clara]
**Porquê:** [problema que resolve]
**Requisitos:**
- [lista de requisitos]

**Questões:**
- [dúvidas que tens]

Cria plano de implementação!
```

---

## 🔐 Segurança

### **Ficheiros NUNCA Commitados**

```bash
.env                    # Environment variables
.env.production         # Production env (symlink)
secrets.json           # Secrets
credentials.json       # Credentials
*.sql                  # DB dumps
*.sql.gz               # Compressed backups
```

### **Secrets Management**

- ✅ **SEMPRE** usa variáveis de ambiente (`.env`)
- ❌ **NUNCA** hardcodes passwords/tokens no código
- ✅ `.env` está em `~/amp/docker/app/.env` no servidor
- ✅ `.gitignore` bloqueia commits de secrets

---

## 📊 Workflow Resumido (TL;DR)

```bash
# 1. Criar branch
git checkout -b claude/feature-xxx

# 2. Desenvolver + testar
# [fazer mudanças]
docker compose up -d --build web

# 3. Commit
git add .
git commit -m "feat: descrição"

# 4. Push
git push -u origin claude/feature-xxx

# 5. Quando pronto: merge
git checkout main
git pull origin main
git merge claude/feature-xxx
git push origin main

# 6. Deploy
./deploy.sh

# 7. ✅ Verificar produção
# https://app.agoramediaproduction.pt
```

---

## 🎯 Tech Stack Atual

| Camada | Tecnologia | Notas |
|--------|------------|-------|
| **Backend** | Django 5.0 | Framework web |
| **Database** | PostgreSQL 16 | Relational DB |
| **ORM** | Django ORM | Built-in |
| **Admin** | Unfold Theme | Modern admin UI |
| **Containers** | Docker Compose | web + db |
| **Reverse Proxy** | Traefik v3.3 | HTTP routing |
| **DNS/SSL** | Cloudflare | CDN + SSL |
| **Python** | 3.11 | Runtime |
| **WSGI** | Gunicorn | Production server |

---

## 💡 Tips Finais

1. **Sempre rebuild** após mudanças de código Python
2. **Consulta docs/** antes de implementar features existentes
3. **Testa no shell primeiro** antes de deploy (especialmente saldos)
4. **Faz backup** antes de mudanças grandes na BD
5. **Commita frequentemente** - commits pequenos são melhores
6. **Documenta decisões** importantes em `docs/`
7. **Usa TodoWrite** para planear tarefas complexas (Claude)

---

**© 2025 Agora Media Production**
**Última Atualização:** 2026-01-03
**Versão:** 2.0 (VS Code Workflow)
