# 🖥️ Workflow: Claude Code (VS Code Extension)

Este guia explica como trabalhar no **Agora Contabilidade** usando a **Claude Code Extension** no VS Code.

---

## 🎯 Overview

**Ambiente:** VS Code local conectado ao servidor via SSH
**Localização:** `/home/zumine/amp/docker/app/`
**Vantagem Principal:** Mudanças diretas no servidor, sem sincronização

---

## 🚀 Setup Inicial

### 1. Conectar VS Code ao Servidor

```bash
# No VS Code:
# 1. Abrir Command Palette (Cmd/Ctrl + Shift + P)
# 2. "Remote-SSH: Connect to Host"
# 3. Selecionar: zumine@[servidor]
# 4. Abrir pasta: /home/zumine/amp/docker/app
```

### 2. Verificar Claude Extension

- Extensão "Claude Code" instalada e ativa
- Fazer login com conta Anthropic
- Confirmar que aparece no sidebar

### 3. Checklist Ambiente

```bash
# No terminal integrado do VS Code:

# Verificar git
git status
git config user.name
git config user.email

# Verificar Docker
docker compose ps

# Verificar .env
ls -la .env
```

---

## 🔄 Workflow Diário

### **Passo 1: Criar Feature Branch**

```bash
# Atualizar main
git checkout main
git pull origin main

# Criar branch nova
git checkout -b claude/feat-nome-feature-$(date +%Y%m%d)
```

**Convenção de nomes:**
- `claude/feat-*` - Nova feature
- `claude/fix-*` - Bug fix
- `claude/refactor-*` - Refactoring
- `claude/docs-*` - Documentação

### **Passo 2: Desenvolvimento com Claude**

#### Prompt Inicial (copiar para Claude):

```markdown
Vou trabalhar no projeto Agora Contabilidade.

**Contexto:**
- Lê .claude/claude.md para contexto completo
- Branch atual: [nome-da-branch]
- Tarefa: [descrever feature/fix]

**Antes de começar:**
1. Verifica estado atual (git status, docker ps)
2. Confirma que estamos na branch correta
3. Cria plano com TodoWrite

Vamos começar!
```

#### Durante o Desenvolvimento:

1. **Claude edita ficheiros** diretamente no servidor
2. **Testar mudanças:**
   ```bash
   docker compose down
   docker compose up -d --build web
   ```
3. **Ver logs:**
   ```bash
   docker compose logs -f web
   ```
4. **Testar no browser:**
   - https://app.agoramediaproduction.pt

### **Passo 3: Testing Django**

```bash
# Django shell
docker compose exec web python manage.py shell

# Testar query
>>> from core.models import Projeto, Socio
>>> Socio.objects.all()
>>> Projeto.objects.filter(socio__codigo='BA').count()

# Verificar migrations
docker compose exec web python manage.py showmigrations

# Aplicar migrations (se criaste alguma)
docker compose exec web python manage.py migrate

# Check do sistema
docker compose exec web python manage.py check --deploy
```

### **Passo 4: Commit**

```bash
# Adicionar ficheiros
git add agora_web/core/models.py
git add agora_web/core/admin.py

# Commit descritivo
git commit -m "feat: add dashboard de receitas mensais

- Criado modelo ReceitaMensal
- Adicionado dashboard no admin
- Implementada lógica de cálculo

🤖 Generated with Claude Code
Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

### **Passo 5: Push**

```bash
git push -u origin claude/feat-nome-feature-xxxxx
```

### **Passo 6: Merge & Deploy**

```bash
# Voltar para main
git checkout main
git pull origin main

# Merge
git merge claude/feat-nome-feature-xxxxx

# Push
git push origin main

# Deploy (já estamos no servidor!)
./deploy.sh
```

---

## 🧪 Testing

### Django Shell Testing

```bash
# Entrar no shell
docker compose exec web python manage.py shell

# Testar model
>>> from core.models import Socio, Projeto
>>> ba = Socio.objects.get(codigo='BA')
>>> ba.projetos.count()

# Testar cálculos
>>> from core.utils.saldos import SaldosCalculator
>>> calc = SaldosCalculator()
>>> saldo = calc.calcular_saldo_bruno()
>>> print(saldo['saldo_atual'])
```

### Database Testing

```bash
# Aceder PostgreSQL
docker compose exec db psql -U agora -d agora_production

# Ver tabelas
\dt

# Query teste
SELECT COUNT(*) FROM projetos WHERE socio_id = 'BA';
```

### API/Admin Testing

1. Abrir https://app.agoramediaproduction.pt/admin
2. Login com superuser
3. Testar funcionalidade nova
4. Verificar se não quebrou nada existente

---

## 🐛 Debugging

### Ver Logs Detalhados

```bash
# Logs do Django
docker compose logs -f web

# Entrar no container
docker compose exec web bash

# Ver ficheiros
ls -la /app/agora_web/
python manage.py check
```

### Database Debugging

```bash
# PostgreSQL shell
docker compose exec db psql -U agora -d agora_production

# Ver schema
\d projetos

# Query debug
SELECT * FROM socios;
SELECT * FROM projetos WHERE data_inicio >= '2025-01-01';
```

### Rebuild Completo

```bash
docker compose down
docker compose build --no-cache web
docker compose up -d

# Aplicar migrations
docker compose exec web python manage.py migrate

# Collectstatic
docker compose exec web python manage.py collectstatic --noinput
```

---

## 📝 Prompts Úteis para Claude

### Nova Feature (Django)

```markdown
Adicionar feature ao Agora Contabilidade:

**Feature:** [descrição clara]
**Porquê:** [problema que resolve]
**Requisitos:**
- [lista de requisitos]

**Stack:**
- Backend: Django 5.0
- Database: PostgreSQL 16 + Django ORM
- Admin: Unfold Theme

**Models afetados:** [listar]
**Precisa migration?** [Sim/Não]

Cria plano de implementação!
```

### Debugging Django

```markdown
Erro no Agora Contabilidade:

**Erro:** [colar erro completo]

**Contexto:**
- O que estava a fazer: [descrição]
- Quando aconteceu: [após deploy/mudança/etc]

**Logs Django:**
[colar docker compose logs web]

**Traceback:**
[colar traceback completo]

Ajuda a debugar!
```

### Database Migration

```markdown
Criar migration Django:

**Mudança no schema:**
- Tabela: [nome]
- Campos novos: [listar]
- Campos modificados: [listar]
- ForeignKeys: [listar]

**Precauções:**
- Backup da BD antes
- Testar em ambiente dev primeiro
- Verificar se afeta dados existentes

Cria migration e testa!
```

---

## 💡 Tips & Tricks

### Django Specific

```bash
# Criar migration
docker compose exec web python manage.py makemigrations

# Ver SQL da migration
docker compose exec web python manage.py sqlmigrate core 0005

# Fake migration (se já aplicada manualmente)
docker compose exec web python manage.py migrate core 0005 --fake

# Resetar migrations (CUIDADO!)
# Apenas em desenvolvimento!
docker compose exec web python manage.py migrate core zero
```

### Admin Customization

- Admin classes em `agora_web/core/admin.py`
- Templates custom em `agora_web/core/templates/admin/`
- Unfold config em `config/settings.py` → `UNFOLD` dict

### Database Backup

```bash
# Backup manual
docker compose exec db pg_dump -U agora agora_production > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore (CUIDADO!)
cat backup.sql | docker compose exec -T db psql -U agora -d agora_production
```

---

## ⚠️ Boas Práticas

### ✅ FAZER

- ✅ Criar feature branch para cada tarefa
- ✅ Testar localmente antes de merge
- ✅ Criar migrations se mudares models
- ✅ Fazer backup da BD antes de migrations grandes
- ✅ Testar no Django shell antes de deploy
- ✅ Usar `./deploy.sh` para deployment
- ✅ Collectstatic após mudanças CSS/JS

### ❌ NÃO FAZER

- ❌ Commit direto em `main`
- ❌ Commit de `.env` ou secrets
- ❌ Migrations sem backup
- ❌ Deployment sem testar
- ❌ Mudar nome do volume `agora_web_postgres_data`
- ❌ Force push em branches partilhadas
- ❌ SQL direto sem migration

---

## 🆘 Troubleshooting

### Problema: Código não atualiza

**Solução:**
```bash
# Código está na imagem Docker
docker compose down
docker compose build --no-cache web
docker compose up -d
```

### Problema: CSS não carrega

**Solução:**
```bash
docker compose exec web python manage.py collectstatic --noinput --clear
```

### Problema: Migration conflicts

**Solução:**
```bash
# Ver histórico
git log --oneline -- agora_web/core/migrations/

# Criar merge migration
docker compose exec web python manage.py makemigrations --merge

# Ou consultar docs/DATABASE_MANUAL_CHANGES.md
```

---

## 📚 Recursos

- **Contexto Universal:** [`.claude/claude.md`](../claude.md)
- **Guia Geral:** [`README-DEV.md`](../../README-DEV.md)
- **Workflow MCP:** [`mcp-github.md`](mcp-github.md)
- **Prompts:** [`.claude/prompts/`](../prompts/)
- **Docs Técnicos:** [`docs/`](../../docs/)

---

**Última Atualização:** 2026-01-05
