# 🎯 Prompt: Nova Feature

Use este template quando quiser adicionar uma nova funcionalidade ao RAIA.

---

## Template Completo

```markdown
Adicionar feature ao RAIA:

**Feature:** [Nome claro da feature]

**Porquê:** [Problema que resolve ou valor que adiciona]

**Requisitos Funcionais:**
- [Requisito 1]
- [Requisito 2]
- [Requisito 3]

**Stack Tecnológica:**
- Frontend: Svelte 5 (Runes API)
- Backend: SvelteKit API routes
- Database: SQLite + Drizzle ORM
- [Outras tecnologias se relevante]

**Contexto do Projeto:**
- Lê `.claude/claude.md` para contexto completo
- Branch atual: [nome-da-branch ou "criar nova"]
- Ficheiros relevantes: [listar se souber]

**Antes de começar:**
1. Verifica estado atual (git status, docker ps se VS Code)
2. Cria plano de implementação com TodoWrite
3. Lista ficheiros que serão criados/modificados
4. Identifica potenciais breaking changes

**Entregas Esperadas:**
- [ ] Código funcional
- [ ] Testes (se aplicável)
- [ ] Documentação atualizada
- [ ] Migration SQL (se alterar schema)

Cria plano de implementação!
```

---

## Exemplo Prático 1: Dashboard Widget

```markdown
Adicionar feature ao RAIA:

**Feature:** Widget de Receita Mensal no Dashboard

**Porquê:** Utilizador quer ver rapidamente quanto faturou no mês corrente.

**Requisitos Funcionais:**
- Mostrar total do mês corrente (€)
- Breakdown: FREELAS vs PESSOAIS vs PRÉMIOS
- Comparação com mês anterior (% variação)
- Click para ver detalhes dos trabalhos

**Stack Tecnológica:**
- Frontend: Svelte 5 (novo componente em src/lib/components/)
- Backend: Novo endpoint GET /api/dashboard/monthly-revenue
- Database: Query em work_entries (campo 'total')

**Contexto do Projeto:**
- Lê `.claude/claude.md` para contexto completo
- Branch nova: claude/feat-monthly-revenue-widget-20260105
- Ficheiros relevantes:
  - src/routes/+page.svelte (dashboard)
  - src/routes/api/dashboard/+server.ts (pode já existir)

**Antes de começar:**
1. Verifica estado atual
2. Cria plano com TodoWrite
3. Lista ficheiros: MonthlyRevenueWidget.svelte, endpoint API, queries
4. Sem breaking changes esperados

**Entregas Esperadas:**
- [x] Componente Svelte 5 com widget
- [x] Endpoint API /api/dashboard/monthly-revenue
- [x] Queries Drizzle ORM otimizadas
- [x] Documentação em docs/DASHBOARD.md
- [ ] Migration SQL (não necessária)

Cria plano de implementação!
```

---

## Exemplo Prático 2: Sistema de Tags

```markdown
Adicionar feature ao RAIA:

**Feature:** Sistema de Tags para Trabalhos

**Porquê:** Categorizar trabalhos além de FREELAS/PESSOAIS/PRÉMIOS (ex: "urgente", "longo-prazo", "cliente-vip")

**Requisitos Funcionais:**
- CRUD de tags (criar, editar, apagar)
- Associar múltiplas tags a um trabalho
- Filtrar trabalhos por tag
- Cores customizáveis para cada tag
- Tag suggestions ao criar trabalho

**Stack Tecnológica:**
- Frontend: Svelte 5
- Backend: SvelteKit API routes
- Database: SQLite + Drizzle ORM
  - Nova tabela: `tags`
  - Nova tabela junction: `work_entry_tags` (many-to-many)

**Contexto do Projeto:**
- Lê `.claude/claude.md` para contexto completo
- Branch nova: claude/feat-tags-system-20260105
- Ficheiros relevantes:
  - src/lib/db/schema.ts (adicionar tabelas)
  - src/routes/trabalhos/* (integrar tags)
  - src/routes/api/tags/ (novo)

**Antes de começar:**
1. Verifica estado atual
2. Cria plano com TodoWrite
3. Lista ficheiros: schema, API endpoints, componentes UI
4. ⚠️ **BREAKING CHANGE:** Precisa migration SQL

**Entregas Esperadas:**
- [ ] Migration SQL: 006_add_tags.sql
- [ ] Schema Drizzle: tables tags + work_entry_tags
- [ ] API endpoints: /api/tags (CRUD)
- [ ] Componente: TagPicker.svelte
- [ ] Integração em trabalhos/novo e trabalhos/[id]/editar
- [ ] Filtro por tag na lista de trabalhos
- [ ] Documentação: docs/TAGS_SYSTEM.md

Cria plano de implementação!
```

---

## Dicas

1. **Seja específico** nos requisitos
2. **Liste ficheiros** que serão afetados (ajuda a AI a planejar)
3. **Identifique breaking changes** antecipadamente
4. **Mencione migrations** se alterar database schema
5. **Use TodoWrite** para features complexas

---

**Última Atualização:** 2026-01-05
