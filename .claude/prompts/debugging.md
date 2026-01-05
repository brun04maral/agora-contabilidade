# 🐛 Prompt: Debugging

Use este template quando tiver um bug ou erro no RAIA.

---

## Template Completo

```markdown
Erro no RAIA:

**Erro:** [Colar mensagem de erro completa ou screenshot]

**Contexto:**
- O que estava a fazer: [descrição passo-a-passo]
- Quando aconteceu: [após deploy? após edição? intermitente?]
- Ambiente: [desenvolvimento local / servidor produção]
- Branch: [nome da branch]

**Comportamento Esperado:**
[O que deveria acontecer]

**Comportamento Atual:**
[O que está a acontecer]

**Tentativas de Resolução:**
- [x] Tentativa 1: [resultado]
- [x] Tentativa 2: [resultado]
- [ ] Ainda não tentei: [ideias]

**Logs Relevantes:**
```
[Colar logs aqui - docker compose logs, browser console, etc.]
```

**Ficheiros Possivelmente Relacionados:**
- [caminho/ficheiro1.ts]
- [caminho/ficheiro2.svelte]

**Stack Trace (se houver):**
```
[Colar stack trace completo]
```

Ajuda a debugar!
```

---

## Exemplo Prático 1: Erro 500 na API

```markdown
Erro no RAIA:

**Erro:**
```
500 Internal Server Error
POST /api/work-entries
```

**Contexto:**
- O que estava a fazer: Criar novo trabalho do tipo PRÉMIOS
- Quando aconteceu: Ao submeter formulário em /trabalhos/novo
- Ambiente: Servidor produção (https://raia.planogeral.pt)
- Branch: main

**Comportamento Esperado:**
Trabalho criado com sucesso, redirect para lista de trabalhos

**Comportamento Atual:**
Erro 500, trabalho não é criado na database

**Tentativas de Resolução:**
- [x] Verificar logs Docker: erro "field 'numero_dias' is required"
- [x] Verificar schema Drizzle: campo existe na tabela
- [ ] Ainda não tentei: verificar se frontend envia o campo

**Logs Relevantes:**
```bash
$ docker compose logs raia
[2026-01-05 14:32:18] ERROR: POST /api/work-entries
[2026-01-05 14:32:18] DrizzleError: NULL constraint failed: work_entries.numero_dias
[2026-01-05 14:32:18]   at insert (/app/src/routes/api/work-entries/+server.ts:45)
```

**Ficheiros Possivelmente Relacionados:**
- src/routes/api/work-entries/+server.ts (linha 45)
- src/routes/trabalhos/novo/+page.svelte (formulário)
- src/lib/db/schema.ts (definição da tabela)

**Stack Trace:**
```
DrizzleError: NULL constraint failed: work_entries.numero_dias
    at /app/node_modules/drizzle-orm/sqlite-core/db.js:123:15
    at /app/src/routes/api/work-entries/+server.ts:45:20
```

Ajuda a debugar!
```

---

## Exemplo Prático 2: UI Bug

```markdown
Erro no RAIA:

**Erro:**
Dashboard mostra "NaN€" no total de prémios

**Contexto:**
- O que estava a fazer: Navegar para página inicial (dashboard)
- Quando aconteceu: Após adicionar trabalho do tipo PRÉMIOS
- Ambiente: Servidor produção
- Branch: main

**Comportamento Esperado:**
Dashboard mostra valor correto (ex: "1.250,00€")

**Comportamento Atual:**
Dashboard mostra "NaN€"

**Tentativas de Resolução:**
- [x] Verificar browser console: erro "Cannot read property 'total' of undefined"
- [x] Verificar API response: campo 'total' vem como null para PRÉMIOS
- [ ] Ainda não tentei: verificar query SQL no endpoint /api/dashboard

**Logs Relevantes:**
```javascript
// Browser console
GET /api/dashboard
Response: {
  "trabalhos_mes": 5,
  "total_freelas": 3500.00,
  "total_pessoais": 2000.00,
  "total_premios": null  // ❌ Deveria ser número
}

// Client error
TypeError: Cannot read property 'toFixed' of null
  at DashboardCard.svelte:23
```

**Ficheiros Possivelmente Relacionados:**
- src/routes/api/dashboard/+server.ts (query SQL)
- src/routes/+page.svelte (dashboard)
- src/lib/components/DashboardCard.svelte (linha 23)

**Stack Trace:**
```
TypeError: Cannot read property 'toFixed' of null
    at DashboardCard.svelte:23:35
    at update (svelte internals)
```

Ajuda a debugar!
```

---

## Exemplo Prático 3: Google Calendar Sync Issue

```markdown
Erro no RAIA:

**Erro:**
Trabalho criado mas não sincronizou com Google Calendar

**Contexto:**
- O que estava a fazer: Criar trabalho FREELAS em /trabalhos/novo
- Quando aconteceu: Após submeter formulário
- Ambiente: Servidor produção
- Branch: main
- Google Calendar: Conectado e autorizado (verificado em /definicoes)

**Comportamento Esperado:**
- Trabalho criado ✅
- Evento aparece em Google Calendar "FREELAS - A Faturar"

**Comportamento Atual:**
- Trabalho criado ✅
- Evento NÃO aparece em Calendar ❌

**Tentativas de Resolução:**
- [x] Verificar tokens OAuth: válidos e não expirados
- [x] Verificar logs: erro 403 Forbidden ao criar evento
- [x] Verificar permissões Google Cloud: parecem OK
- [ ] Ainda não tentei: verificar se calendar ID existe

**Logs Relevantes:**
```bash
$ docker compose logs raia | grep calendar
[2026-01-05 15:10:22] INFO: Creating work entry...
[2026-01-05 15:10:23] INFO: Work entry created: id=123
[2026-01-05 15:10:23] INFO: Syncing to Google Calendar...
[2026-01-05 15:10:24] ERROR: Failed to create calendar event
[2026-01-05 15:10:24] Google API Error: 403 Forbidden
[2026-01-05 15:10:24] Message: "Insufficient permissions to create event"
```

**Ficheiros Possivelmente Relacionados:**
- src/lib/server/calendar-sync.ts (lógica de sync)
- src/lib/server/google-calendar.ts (OAuth + API calls)
- src/routes/api/work-entries/+server.ts (trigger de sync)

**Google API Response:**
```json
{
  "error": {
    "code": 403,
    "message": "Insufficient permissions to create event",
    "status": "PERMISSION_DENIED"
  }
}
```

Ajuda a debugar!
```

---

## Dicas para Bom Debugging

1. **Copia logs completos** (não apenas a última linha)
2. **Descreve passos para reproduzir** o erro
3. **Menciona o que já tentaste** (poupa tempo)
4. **Inclui browser console** se for erro de UI
5. **Verifica ficheiros relacionados** antes de pedir ajuda

---

**Última Atualização:** 2026-01-05
