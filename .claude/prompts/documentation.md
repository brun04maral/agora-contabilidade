# 📝 Prompt: Documentação

Use este template quando quiser criar ou atualizar documentação do RAIA.

---

## Template Completo

```markdown
Atualizar documentação do RAIA:

**Tipo de Documentação:**
- [ ] README principal
- [ ] README-DEV (workflow)
- [ ] Documentação técnica (docs/)
- [ ] API endpoints
- [ ] Comentários em código
- [ ] CHANGELOG

**Ficheiro(s) a Atualizar/Criar:**
- [caminho/ficheiro1.md]
- [caminho/ficheiro2.md]

**Mudanças Necessárias:**
1. [Mudança 1]
2. [Mudança 2]
3. [Mudança 3]

**Contexto:**
- Relacionado com: [feature/bug/refactor recente]
- PR/Issue relacionado: #[número]
- Branch: [nome ou "criar nova"]

**Audiência:**
- [ ] Developers (técnico)
- [ ] Utilizadores finais (user-facing)
- [ ] AI assistants (contexto)

**Antes de começar:**
1. Lê ficheiro atual (se já existir)
2. Verifica outros ficheiros relacionados
3. Mantém estilo consistente

Atualiza documentação!
```

---

## Exemplo Prático 1: Documentar Nova Feature

```markdown
Atualizar documentação do RAIA:

**Tipo de Documentação:**
- [x] README principal (adicionar feature à lista)
- [x] Documentação técnica (novo ficheiro em docs/)
- [x] CHANGELOG

**Ficheiro(s) a Atualizar/Criar:**
- README.md (secção "Features")
- docs/TAGS_SYSTEM.md (novo ficheiro)
- CHANGELOG.md (versão 1.5.0)

**Mudanças Necessárias:**
1. README.md:
   - Adicionar "Sistema de Tags" na lista de features
   - Breve descrição (2-3 linhas)
   - Screenshot (se tiver)

2. docs/TAGS_SYSTEM.md (novo):
   - Como funciona o sistema
   - Como criar/editar tags
   - Como filtrar trabalhos por tag
   - Schema database (tabelas tags + work_entry_tags)
   - Endpoints API

3. CHANGELOG.md:
   - Adicionar entrada para v1.5.0
   - Listar mudanças: "Sistema de tags para categorização de trabalhos"

**Contexto:**
- Relacionado com: Feature de tags implementada
- PR relacionado: #45
- Branch: docs-tags-system-20260105

**Audiência:**
- [x] Developers (docs/TAGS_SYSTEM.md)
- [x] Utilizadores finais (README.md)
- [ ] AI assistants (não específico)

Atualiza documentação!
```

---

## Exemplo Prático 2: Atualizar API Docs

```markdown
Atualizar documentação do RAIA:

**Tipo de Documentação:**
- [x] API endpoints (docs/api_endpoints.md)

**Ficheiro(s) a Atualizar/Criar:**
- docs/api_endpoints.md

**Mudanças Necessárias:**
1. Adicionar novo endpoint: GET /api/dashboard/monthly-revenue
   - Descrição
   - Parâmetros (query params)
   - Response format (JSON schema)
   - Exemplo de request/response

2. Atualizar endpoint existente: POST /api/work-entries
   - Adicionar campo 'tags' (array de IDs)
   - Atualizar exemplo de request

**Contexto:**
- Relacionado com: Novos endpoints adicionados
- PR relacionado: #46
- Branch: docs-api-update-20260105

**Audiência:**
- [x] Developers (referência de API)

**Formato esperado:**
```markdown
### GET /api/dashboard/monthly-revenue

Retorna receita do mês corrente.

**Query Parameters:**
- `month` (optional): YYYY-MM (default: mês corrente)
- `breakdown` (optional): boolean (default: false)

**Response:**
```json
{
  "month": "2026-01",
  "total": 5500.00,
  "breakdown": {
    "FREELAS": 3500.00,
    "PESSOAIS": 1500.00,
    "PREMIOS": 500.00
  }
}
```

Atualiza documentação!
```

---

## Exemplo Prático 3: Atualizar Contexto AI

```markdown
Atualizar documentação do RAIA:

**Tipo de Documentação:**
- [x] AI context (.claude/claude.md)

**Ficheiro(s) a Atualizar/Criar:**
- .claude/claude.md

**Mudanças Necessárias:**
1. Secção "Core Concepts":
   - Adicionar explicação do sistema de tags
   - Como tags se relacionam com trabalhos

2. Secção "Database":
   - Adicionar tabelas 'tags' e 'work_entry_tags'
   - Explicar relação many-to-many

3. Secção "Recent Major Changes":
   - Adicionar entrada: "Sistema de Tags (v1.5.0)"

**Contexto:**
- Relacionado com: Feature de tags implementada
- PR relacionado: #45
- Branch: docs-claude-context-update-20260105

**Audiência:**
- [ ] Developers
- [ ] Utilizadores finais
- [x] AI assistants (Claude, Perplexity, etc.)

**Notas:**
- Manter linguagem clara e concisa
- Focar em conceitos, não em código específico
- Usar exemplos práticos

Atualiza documentação!
```

---

## Exemplo Prático 4: CHANGELOG Update

```markdown
Atualizar documentação do RAIA:

**Tipo de Documentação:**
- [x] CHANGELOG

**Ficheiro(s) a Atualizar/Criar:**
- CHANGELOG.md

**Mudanças Necessárias:**
1. Adicionar nova versão: v1.5.0 (2026-01-05)
2. Listar todas as mudanças desta release:
   - ✅ Sistema de tags
   - ✅ Widget de receita mensal
   - 🐛 Fix: Erro NaN no dashboard
   - 🐛 Fix: Google Calendar sync 403 error
   - 📝 Docs: Atualizar API endpoints

**Contexto:**
- Relacionado com: Release v1.5.0
- PRs: #45, #46, #47, #48
- Branch: main

**Audiência:**
- [x] Developers
- [x] Utilizadores finais

**Formato esperado:**
```markdown
## [1.5.0] - 2026-01-05

### Added
- ✅ Sistema de tags para categorização de trabalhos
- ✅ Widget de receita mensal no dashboard
- ✅ Filtro por tag na lista de trabalhos

### Fixed
- 🐛 Dashboard mostrando "NaN€" para prémios
- 🐛 Google Calendar sync falhando com erro 403

### Changed
- 📝 API: POST /api/work-entries aceita campo 'tags'
- 📝 Database: Novas tabelas 'tags' e 'work_entry_tags'

### Documentation
- 📚 Novo: docs/TAGS_SYSTEM.md
- 📚 Atualizado: docs/api_endpoints.md
```

Atualiza CHANGELOG!
```

---

## Dicas para Boa Documentação

1. **Seja claro e conciso** - evita jargão desnecessário
2. **Use exemplos** - código, JSON, screenshots
3. **Estrutura clara** - headers, listas, code blocks
4. **Mantém atualizado** - documenta ao implementar, não depois
5. **Pensa na audiência** - técnico vs user-facing
6. **Links internos** - referencia outros docs quando relevante

---

## Checklist de Documentação

Quando implementares uma feature, assegura:

- [ ] README.md atualizado (se feature user-facing)
- [ ] README-DEV.md atualizado (se afetar workflow)
- [ ] docs/ com documentação técnica detalhada
- [ ] API endpoints documentados (se aplicável)
- [ ] CHANGELOG.md atualizado
- [ ] .claude/claude.md atualizado (se mudança arquitetural)
- [ ] Comentários em código (se lógica complexa)

---

**Última Atualização:** 2026-01-05
