# 🎬 Agora Contabilidade

Sistema de gestão contabilística para **Amaral & Reigota - Produção Audiovisual, Lda**

**Marca:** Agora Media Production
**NIPC:** 518 351 190
**Sócios:** Bruno Amaral (BA) e Rafael Reigota (RR)

---

## 📖 Quick Start

### Para Developers

```bash
# Ver guia completo de desenvolvimento
cat README-DEV.md

# Para Claude AI: ler contexto completo
cat .claude/claude.md
```

### Para Deployment

```bash
# Deploy rápido (no servidor)
./deploy.sh

# Ver logs
docker compose logs -f web

# Acesso: https://app.agoramediaproduction.pt
```

---

## 🎯 Tech Stack

| Camada | Tecnologia | Versão |
|--------|------------|--------|
| Backend | Django | 5.0 |
| Database | PostgreSQL | 16 |
| Admin UI | Unfold Theme | Latest |
| Containers | Docker Compose | - |
| Reverse Proxy | Traefik | v3.3 |
| DNS/SSL | Cloudflare | - |
| Python | CPython | 3.11 |
| WSGI Server | Gunicorn | Latest |

---

## ✨ Features Principais

### 💰 Saldos Pessoais (CORE Feature)
Dashboard que calcula automaticamente quanto a empresa deve a cada sócio com **dois tipos de saldo**:

**Saldo Atual** (decisões financeiras HOJE):
- **INs:** Projetos pagos (data_recibo) + Prémios de trabalho FEITO (data_fim < hoje)
- **OUTs:** Despesas fixas ÷ 2 + Boletins PAGOS + Despesas pessoais

**Saldo Projetado** (planeamento médio prazo):
- **INs:** Projetos pagos + Prémios de TODOS os projetos (incluindo futuros)
- **OUTs:** Despesas fixas ÷ 2 + Boletins TODOS (PAGO + PENDENTE) + Despesas pessoais

**Funcionalidades:**
- Breakdown anual com filtros de data
- Sugestão de boletim baseada em saldo projetado e meses restantes
- Sistema de tags para categorização flexível de despesas

Ver [docs/SALDOS_DASHBOARD.md](docs/SALDOS_DASHBOARD.md) para detalhes técnicos.

### 📊 Gestão Completa

| Módulo | Funcionalidade |
|--------|----------------|
| **Projetos** | Gestão com prémios individuais (BA/RR) |
| **Orçamentos** | Versões e aprovações |
| **Despesas** | Fixas mensais e variáveis |
| **Boletins** | Recibos verdes com cálculos automáticos |
| **Clientes** | Base de dados completa |
| **Fornecedores** | Gestão de fornecedores |
| **Equipamento** | Inventário de equipamento |
| **Sócios** | BA e RR com participação 50/50 |
| **Importação** | Upload web de ficheiros Excel |

### 🎨 Interface

- **Unfold Admin Theme** - Interface moderna e limpa
- **Cards visuais** - Dashboard com breakdown claro
- **Responsive** - Funciona em desktop e mobile
- **Cores personalizadas** - Verde (#2ECC71) para BA, Azul (#3498DB) para RR

---

## 🏗️ Arquitetura

### Infraestrutura

```
Internet
  ↓
Cloudflare (DNS + CDN + SSL)
  ↓
Servidor (porta 80/443)
  ↓
Traefik v3.3 (Reverse Proxy)
  ↓
Docker Network: traefik_proxy
  ↓
agora_web (Django + Gunicorn :8000)
  ↓
Docker Network: agora_internal
  ↓
agora_db (PostgreSQL 16 :5432)
```

### Estrutura de Código

```
agora_web/
├── core/                   # Main Django app
│   ├── models.py          # Socio, Projeto, Despesa, Boletim, etc
│   ├── admin.py           # Admin customizations
│   ├── utils/
│   │   └── saldos.py      # SaldosCalculator (lógica core)
│   ├── templates/         # Custom templates
│   └── migrations/        # Database migrations
├── config/                # Django settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── static/                # CSS, JS, logos
```

---

## 🚀 Development Workflow

### Setup Inicial

```bash
# 1. Clonar repo (se necessário)
git clone <repo-url>
cd agora-contabilidade

# 2. Configurar .env
cp .env.example .env
# Editar .env com credenciais

# 3. Iniciar containers
docker compose up -d

# 4. Aplicar migrations
docker compose exec web python manage.py migrate

# 5. Criar superuser
docker compose exec web python manage.py createsuperuser

# 6. Acesso: https://app.agoramediaproduction.pt/admin
```

### Workflow Diário

**Ver [README-DEV.md](README-DEV.md) para guia completo!**

Resumo:
```bash
# 1. Criar branch
git checkout -b claude/feature-xxx

# 2. Desenvolver + testar
docker compose up -d --build web

# 3. Commit + push
git commit -m "feat: descrição"
git push -u origin claude/feature-xxx

# 4. Merge quando pronto
git checkout main && git pull
git merge claude/feature-xxx
git push origin main

# 5. Deploy
./deploy.sh
```

---

## 💡 Core Concepts

### Sócios (Partners)
- **BA** (Bruno Amaral) - Código: `BA`
- **RR** (Rafael Reigota) - Código: `RR`
- Participação: **50% cada**
- Campos: codigo (PK), nome_completo, email, percentagem_participacao, cor_tema

### Saldos Pessoais
**Conceito:** Sócios fazem trabalhos freelance mas faturam pela empresa → empresa fica a dever.

**Fórmula:**
```
Saldo = INs - OUTs

INs (empresa DEVE ao sócio):
  • Projetos pessoais (tipo=PESSOAL_BA/RR, estado=PAGO)
  • Prémios individuais (premio_bruno/rafael, estado=PAGO)
  • A Receber: projetos/prémios FINALIZADOS (não pagos ainda)

OUTs (empresa PAGOU ao sócio):
  • Despesas fixas mensais ÷ 2
  • Boletins emitidos (estado=PAGO ou PENDENTE)
  • Despesas pessoais (tipo=PESSOAL_BA/RR)
```

**Exemplo:**
```
Bruno em 2025:
INs:  €15.000 (projetos pessoais) + €3.000 (prémios) = €18.000
OUTs: €2.100 (despesas fixas ÷2) + €8.000 (boletins) = €10.100
Saldo: €18.000 - €10.100 = €7.900 (empresa deve a Bruno)
```

---

## 🗄️ Database

**PostgreSQL 16** com as seguintes tabelas principais:

| Tabela | Modelo | Descrição |
|--------|--------|-----------|
| `socios` | Socio | BA e RR (criada manualmente via SQL) |
| `projetos` | Projeto | Projetos com FK `socio_id` |
| `despesas` | Despesa | Despesas da empresa |
| `boletins` | Boletim | Recibos verdes com FK `socio_id` |
| `orcamentos` | Orcamento | Orçamentos com FK `socio_id` |

**Nota:** Tabela `socios` foi criada manualmente. Ver [docs/DATABASE_MANUAL_CHANGES.md](docs/DATABASE_MANUAL_CHANGES.md)

---

## 🔧 Comandos Úteis

### Django Management

```bash
# Django shell
docker compose exec web python manage.py shell

# Database shell
docker compose exec web python manage.py dbshell

# Check system
docker compose exec web python manage.py check

# Migrations
docker compose exec web python manage.py showmigrations
docker compose exec web python manage.py migrate
docker compose exec web python manage.py makemigrations

# Static files
docker compose exec web python manage.py collectstatic --noinput

# Importação e limpeza de dados
docker compose exec web python manage.py import_from_excel excel/CONTABILIDADE_FINAL_20251231.xlsx
docker compose exec web python manage.py limpar_projetos_vazios --dry-run
docker compose exec web python manage.py limpar_despesas_vazias --dry-run
docker compose exec web python manage.py auditar_importacao excel/CONTABILIDADE_FINAL_20251231.xlsx
docker compose exec web python manage.py analisar_caixa excel/CONTABILIDADE_FINAL_20251231.xlsx --output docs/CAIXA_ANALYSIS.md
```

### Docker

```bash
# Ver logs
docker compose logs -f web
docker compose logs -f db

# Rebuild
docker compose down
docker compose up -d --build web

# Entrar no container
docker compose exec web bash
docker compose exec db psql -U agora -d agora_production
```

### Database Backup

```bash
# Backup
docker compose exec db pg_dump -U agora agora_production > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore (CUIDADO!)
cat backup.sql | docker compose exec -T db psql -U agora -d agora_production
```

---

## 📚 Documentação

### Para Developers
| Ficheiro | Descrição |
|----------|-----------|
| [README-DEV.md](README-DEV.md) | ⭐ **Guia de desenvolvimento completo** |
| [.claude/claude.md](.claude/claude.md) | Contexto completo para AI assistants |

### Documentação Técnica
| Ficheiro | Descrição |
|----------|-----------|
| [docs/SALDOS_DASHBOARD.md](docs/SALDOS_DASHBOARD.md) | Implementação do dashboard de saldos |
| [docs/IMPORT_SYSTEM.md](docs/IMPORT_SYSTEM.md) | Sistema de importação web (Excel upload) |
| [docs/EXCEL_IMPORT_ANALYSIS.md](docs/EXCEL_IMPORT_ANALYSIS.md) | Análise e processo de importação Excel |
| [docs/CAIXA_ANALYSIS.md](docs/CAIXA_ANALYSIS.md) | Análise das fórmulas da aba CAIXA |
| [docs/SOCIOS_MIGRATION.md](docs/SOCIOS_MIGRATION.md) | Como modelo Socio foi criado |
| [docs/DATABASE_MANUAL_CHANGES.md](docs/DATABASE_MANUAL_CHANGES.md) | Mudanças manuais na BD |
| [docs/README.md](docs/README.md) | Índice completo de documentação |

### Histórico
| Pasta | Descrição |
|-------|-----------|
| [archive-old-tkinter-app/](archive-old-tkinter-app/) | App antiga (Tkinter + SQLite) - apenas referência |

---

## 🐛 Known Issues & Solutions

### Docker código não atualiza
```bash
# Código está na imagem, não em volume
docker compose down
docker compose build --no-cache web
docker compose up -d
```

### CSS não carrega
```bash
docker compose exec web python manage.py collectstatic --noinput --clear
```

### Migration conflicts
```bash
# Ver histórico
git log --oneline -- agora_web/core/migrations/

# Solução: criar merge migration
# Ver docs/DATABASE_MANUAL_CHANGES.md
```

Mais troubleshooting em [README-DEV.md](README-DEV.md#-troubleshooting-comum)

---

## 🔐 Segurança

### Secrets (NUNCA Commitar!)
- `.env` - Environment variables
- `*.sql` - Database dumps
- `secrets.json`, `credentials.json`

### Environment Variables
Ver `.env.example` para template.

Principais variáveis:
- `DEBUG=False` (produção)
- `SECRET_KEY` - Django secret
- `DB_NAME`, `DB_USER`, `DB_PASSWORD` - PostgreSQL
- `ALLOWED_HOSTS` - Domain

---

## 🌐 Acesso

- **Produção:** https://app.agoramediaproduction.pt
- **Admin:** https://app.agoramediaproduction.pt/admin
- **Credenciais:** Ver gestão de secrets

---

## 📝 Notas de Versão

### v2.1 - Importação e Limpeza de Dados (03 Jan 2026)
- ✅ Sistema completo de importação Excel → PostgreSQL (CLI)
- ✅ **NOVO:** Interface web para upload de Excel (admin panel)
- ✅ Comandos de limpeza: `limpar_projetos_vazios`, `limpar_despesas_vazias`
- ✅ Comando de auditoria: `auditar_importacao`
- ✅ Análise de fórmulas Excel: `analisar_caixa`
- ✅ SaldosCalculator refatorado com lógica dual (Atual vs Projetado)
- ✅ Sistema de tags para despesas (substituindo enums)
- ✅ Base de dados sincronizada com Excel (81 projetos, 239 despesas, 24 boletins)
- ✅ Proteção contra importação de linhas vazias (skip automático)

### v2.0 - Django App (Dez 2025)
- ✅ Django 5.0 + PostgreSQL 16
- ✅ Dashboard de Saldos Pessoais
- ✅ Modelo Socio com migração de dados
- ✅ Docker + Traefik + Cloudflare
- ✅ Unfold Admin Theme

### v1.0 - Tkinter App (Descontinuada)
- ❌ Aplicação desktop (Tkinter + SQLite)
- ❌ Arquivada em `archive-old-tkinter-app/`

---

## 🆘 Suporte

### Para Developers
1. Consultar [README-DEV.md](README-DEV.md)
2. Ver [docs/](docs/) para questões técnicas
3. Procurar em `git log` para histórico

### Para AI Assistants (Claude)
1. Ler [.claude/claude.md](.claude/claude.md) para contexto completo
2. Consultar [README-DEV.md](README-DEV.md) para workflow
3. Verificar [docs/](docs/) antes de implementar features

---

## 📊 Project Status

| Métrica | Status |
|---------|--------|
| **Ambiente** | ✅ Produção |
| **Deployment** | ✅ Docker + Traefik |
| **Database** | ✅ PostgreSQL 16 |
| **Features Core** | ✅ Completas |
| **Documentação** | ✅ Atualizada |
| **Branch Produção** | `main` |
| **Workflow** | VS Code Extension (servidor direto) |

---

**© 2025 Agora Media Production**
**Última Atualização:** 2026-01-03
**Versão:** 2.0 (Django App)
