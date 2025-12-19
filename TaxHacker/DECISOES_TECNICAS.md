===============================================================================
DECISÕES TÉCNICAS: Rationale e Trade-offs
Documentação das escolhas arquiteturais e justificações
===============================================================================

==================================================
VISÃO GERAL
==================================================

Este documento regista as decisões técnicas importantes tomadas no projeto,
incluindo o contexto, alternativas consideradas, e razões para cada escolha.

FORMATO: Cada decisão segue padrão ADR (Architecture Decision Record)

OBJECTIVO: 
- Documentar o "porquê" das escolhas
- Facilitar manutenção futura
- Evitar repetir discussões já resolvidas

==================================================
DT-001: FORK TAXHACKER VS DESENVOLVIMENTO DO ZERO
==================================================

DATA: Dezembro 2025
STATUS: ✅ Aceite

CONTEXTO:
Precisamos de sistema contabilidade interno para Agora Media. Duas opções:
1. Desenvolver sistema completo do zero
2. Fork de projeto open-source existente

DECISÃO: Fork do TaxHacker

JUSTIFICAÇÃO:

PRÓS TaxHacker:
✅ 80% da funcionalidade core já existe
  - Transactions (receitas/despesas)
  - Categories e Projects
  - Custom Fields (campos adicionais)
  - Upload ficheiros
  - Export CSV
  - Auth completa
  
✅ Stack moderna e mantida
  - Next.js 15 + React 19
  - Prisma ORM
  - TypeScript
  - Shadcn UI
  
✅ Self-hosted friendly
  - Sem dependências cloud obrigatórias
  - Docker ready
  - PostgreSQL (não vendor lock-in)
  
✅ Poupança tempo estimada: 6-8 semanas

CONTRAS:
❌ Dependência de código externo (mitigado: fork próprio)
❌ Features desnecessárias para remover (AI, Stripe)
❌ Curva aprendizagem codebase existente

ALTERNATIVAS CONSIDERADAS:

Opção A: Desenvolvimento do zero
  PRÓS: Controlo total, sem código extra
  CONTRAS: 8-12 semanas desenvolvimento, reinventar roda
  DECISÃO: Rejeitado - tempo/custo não justificam

Opção B: Adaptar app Python existente
  PRÓS: Já tem lógica negócio Agora
  CONTRAS: Flask/SQLAlchemy desactualizados, UI básica, difícil manter
  DECISÃO: Rejeitado - melhor migrar dados e descartar

Opção C: SaaS (Xero, QuickBooks)
  PRÓS: Zero desenvolvimento
  CONTRAS: Não customizável para regras específicas Agora, custos recorrentes
  DECISÃO: Rejeitado - lógica saldos pessoais não suportada

CONSEQUÊNCIAS:
- Desenvolvimento mais rápido (2-3 meses vs 6+ meses)
- Manutenção facilitada (comunidade TaxHacker)
- Risco mitigado (código testado em produção)
- Flexibilidade para customizar conforme necessário

==================================================
DT-002: PRISMA ORM VS RAW SQL
==================================================

DATA: Dezembro 2025
STATUS: ✅ Aceite

CONTEXTO:
TaxHacker usa Prisma. Podíamos manter ou migrar para raw SQL/outro ORM.

DECISÃO: Manter Prisma ORM

JUSTIFICAÇÃO:

PRÓS PRISMA:
✅ Type safety (TypeScript auto-generated)
✅ Migrations versionadas e rastreáveis
✅ Query builder intuitivo
✅ Prisma Studio (GUI debug)
✅ Performance adequada para escala Agora Media

EXEMPLO:
```typescript
// Prisma (type-safe)
const saldo = await prisma.transaction.aggregate({
  where: { userId, type: 'income' },
  _sum: { total: true }
})

// Raw SQL (error-prone)
const result = await db.query('SELECT SUM(total) FROM transactions WHERE user_id = $1', [userId])
// Sem validação tipos, fácil erros runtime
```

CONTRAS:
❌ Abstração (menos controlo fino queries)
❌ Curva aprendizagem (mas menor que SQL direto)

ALTERNATIVAS:

Opção A: Raw SQL
  PRÓS: Máximo controlo, queries optimizadas
  CONTRAS: Sem type safety, migrations manuais, SQL injection risks
  DECISÃO: Rejeitado

Opção B: TypeORM
  PRÓS: Alternativa madura
  CONTRAS: Menos type-safe que Prisma, decorators verbosos
  DECISÃO: Rejeitado - não justifica migração

Opção C: Drizzle ORM
  PRÓS: Performance superior
  CONTRAS: Menos maduro, migração custosa
  DECISÃO: Rejeitado - Prisma suficiente

CONSEQUÊNCIAS:
- Desenvolvimento mais seguro (tipos compilam)
- Migrations simples (prisma migrate)
- Facilita onboarding novos devs

==================================================
DT-003: VALORES MONETÁRIOS EM CÊNTIMOS (INT)
==================================================

DATA: Dezembro 2025
STATUS: ✅ Aceite

CONTEXTO:
Como representar valores monetários em database? TaxHacker usa Int (cêntimos).

DECISÃO: Manter Int (cêntimos), não Decimal

JUSTIFICAÇÃO:

EXEMPLO:
```
150.00 EUR → 15000 (guardado como Int)
```

PRÓS:
✅ Precisão perfeita (sem floating point errors)
✅ Operações aritméticas rápidas (CPU nativa)
✅ Consistência com TaxHacker
✅ Simples conversão display (/ 100)

CONTRAS:
❌ Conversão necessária UI/API (x100 ao guardar, /100 ao mostrar)
❌ Risco esquecimento conversão

ALTERNATIVAS:

Opção A: DECIMAL(10,2)
  PRÓS: Armazena directamente €150.00
  CONTRAS: 
    - Floating point errors em operações
    - Mais lento que Int
    - Problemas precisão (0.1 + 0.2 != 0.3)
  DECISÃO: Rejeitado

Opção B: String (ex: "150.00")
  PRÓS: Zero ambiguidade
  CONTRAS: 
    - Impossível operações aritméticas SQL
    - Conversões constantes
  DECISÃO: Rejeitado

PADRÃO IMPLEMENTAÇÃO:

```typescript
// Helper conversão
export function toCents(euros: number): number {
  return Math.round(euros * 100)
}

export function toEuros(cents: number): number {
  return cents / 100
}

// Uso
const transaction = await prisma.transaction.create({
  data: {
    total: toCents(150.00) // 15000
  }
})

// Display
const euros = toEuros(transaction.total) // 150.00
```

REGRA CRÍTICA:
- Database: SEMPRE cêntimos (Int)
- UI: SEMPRE euros (Number com 2 decimais)
- API: euros (converter ao receber/enviar)

CONSEQUÊNCIAS:
- Zero erros arredondamento
- Performance queries agregação
- Compatibilidade TaxHacker mantida
- Requer disciplina conversões (mitigado com helpers)

==================================================
DT-004: CUSTOM FIELDS VS COLUNAS DEDICADAS
==================================================

DATA: Dezembro 2025
STATUS: ✅ Aceite

CONTEXTO:
Agora Media precisa campos específicos (premio_bruno, premio_rafael, socio).
Como adicionar?

DECISÃO: Usar campo extra (JSON) + Custom Fields TaxHacker

JUSTIFICAÇÃO:

MODELO:
```prisma
model Transaction {
  // ... campos standard ...
  extra  Json?   // Dados específicos Agora Media
}
```

Exemplo extra JSON:
```json
{
  "premio_bruno": 50000,      // cêntimos
  "premio_rafael": 0,
  "socio": "BRUNO",
  "cliente_nome": "RTP",
  "estado_pagamento": "PAGO"
}
```

PRÓS:
✅ Flexibilidade (adicionar campos sem migrations)
✅ Aproveita sistema Custom Fields TaxHacker
✅ Não polui schema base
✅ Fácil extensão futura

CONTRAS:
❌ Queries JSON mais lentas que colunas
❌ Sem type safety no JSON (mitigado com Zod schemas)
❌ Indexes JSON limitados (PostgreSQL suporta mas verboso)

ALTERNATIVAS:

Opção A: Colunas dedicadas
```prisma
model Transaction {
  premio_bruno  Int?
  premio_rafael Int?
  socio         String?
}
```

PRÓS: Type-safe, queries rápidas, indexes simples
CONTRAS: 
  - Modifica schema TaxHacker (dificulta updates upstream)
  - Migration para cada novo campo
  - Schema fica específico Agora Media
DECISÃO: Rejeitado

Opção B: Tabela relacionada TransactionExtra
PRÓS: Schema limpo, relação 1:1
CONTRAS: 
  - JOIN em todas as queries
  - Complexidade desnecessária
DECISÃO: Rejeitado - overkill para poucos campos

PADRÃO IMPLEMENTAÇÃO:

```typescript
// Zod schema para validação
const TransactionExtraSchema = z.object({
  premio_bruno: z.number().optional(),
  premio_rafael: z.number().optional(),
  socio: z.enum(['BRUNO', 'RAFAEL']).optional(),
  cliente_nome: z.string().optional(),
  estado_pagamento: z.enum(['PENDENTE', 'PAGO']).optional()
})

// Uso
const transaction = await prisma.transaction.create({
  data: {
    // ... campos normais ...
    extra: {
      premio_bruno: 50000,
      socio: 'BRUNO'
    }
  }
})

// Query JSON field (PostgreSQL)
const transactions = await prisma.transaction.findMany({
  where: {
    extra: {
      path: ['socio'],
      equals: 'BRUNO'
    }
  }
})
```

CONSEQUÊNCIAS:
- Extensibilidade máxima
- Compatibilidade com TaxHacker mantida
- Performance aceitável (escala Agora Media)
- Requer validação runtime (Zod ajuda)

==================================================
DT-005: EQUIPAMENTO E ORÇAMENTOS - NOVOS MODELOS
==================================================

DATA: Dezembro 2025
STATUS: ✅ Aceite

CONTEXTO:
Equipamento e Orçamentos não existem no TaxHacker. Como implementar?

DECISÃO: Criar modelos Prisma dedicados (não usar Transactions)

JUSTIFICAÇÃO:

MODELOS CRIADOS:
```prisma
model Equipment {
  id            String @id @default(uuid())
  name          String
  purchasePrice Int    // cêntimos
  currentValue  Int    // calculado amortização
  // ...
}

model Budget {
  id     String @id @default(uuid())
  total  Int
  status BudgetStatus
  items  BudgetItem[]
  // ...
}
```

PRÓS:
✅ Semântica clara (equipamento != transaction)
✅ Campos específicos (vida útil, taxa aluguer)
✅ Queries optimizadas (sem filtros complexos)
✅ Facilita relatórios específicos

CONTRAS:
❌ Mais modelos para manter
❌ Migrations adicionais

ALTERNATIVAS:

Opção A: Equipamento como Transaction
  Guardar cada compra equipamento como transaction expense
  Extra JSON com metadados (vida útil, etc)
  
  CONTRAS:
  - Confunde receitas/despesas com assets
  - Difícil calcular amortização
  - Queries complexas
  DECISÃO: Rejeitado

Opção B: Tudo no extra JSON de User
  CONTRAS:
  - Sem relações
  - Queries impossíveis
  - Escalabilidade zero
  DECISÃO: Rejeitado

CONSEQUÊNCIAS:
- Schema mais limpo e semântico
- Queries eficientes
- Fácil adicionar features (ex: histórico manutenção equipamento)
- Migrations simples (não afecta TaxHacker core)

==================================================
DT-006: AUTHENTICATION - BETTER AUTH VS NEXTAUTH
==================================================

DATA: Dezembro 2025
STATUS: ✅ Aceite (herdado TaxHacker)

CONTEXTO:
TaxHacker usa Better Auth. Manter ou migrar para NextAuth v5?

DECISÃO: Manter Better Auth

JUSTIFICAÇÃO:

PRÓS BETTER AUTH:
✅ Já integrado e funcional
✅ Simples e lightweight
✅ Suporta credential auth (email/password)
✅ Sem dependências externas obrigatórias

CONTRAS:
❌ Menos conhecido que NextAuth
❌ Comunidade menor

ALTERNATIVAS:

Opção A: NextAuth v5 (Auth.js)
  PRÓS: Mais popular, OAuth integrado
  CONTRAS: 
    - Migração custosa
    - Overkill (não precisamos OAuth)
    - Breaking changes v4 → v5
  DECISÃO: Rejeitado - não justifica esforço

Opção B: Clerk / Auth0
  PRÓS: SaaS gerido, features avançadas
  CONTRAS:
    - Custos mensais
    - Vendor lock-in
    - Não self-hosted
  DECISÃO: Rejeitado - contra princípio self-hosted

CONSEQUÊNCIAS:
- Zero esforço migração auth
- Self-hosted mantido
- Suficiente para 2 users (Bruno e Rafael)

==================================================
DT-007: INTEGRAÇÃO TOCONLINE - API DIRETA VS WEBHOOK
==================================================

DATA: Dezembro 2025
STATUS: ✅ Aceite

CONTEXTO:
Como integrar com TOConline para emitir facturas AT?

DECISÃO: API direta síncrona + webhook opcional

PADRÃO:

```typescript
// 1. User clica "Emitir Factura"
// 2. Chamar API TOConline directamente
const invoice = await toconlineClient.createInvoice({
  customer_id: clienteId,
  lines: [...]
})

// 3. Actualizar transaction imediatamente
await prisma.transaction.update({
  where: { id: transactionId },
  data: {
    categoryCode: 'FATURADO',
    extra: {
      ...extra,
      toconline_invoice_id: invoice.id
    }
  }
})

// 4. (Opcional) Webhook para update status "PAGO"
// POST /api/webhooks/toconline
// Quando factura é paga na AT
```

PRÓS:
✅ Feedback imediato ao user
✅ Simples implementar
✅ Retry fácil se falhar

CONTRAS:
❌ User espera resposta API (pode ser lento)
❌ Timeout se TOConline down

ALTERNATIVAS:

Opção A: Queue assíncrona (BullMQ/Redis)
  User clica → job enqueued → processar background
  
  PRÓS: User não espera, resiliente
  CONTRAS:
    - Infraestrutura adicional (Redis)
    - Complexidade
    - Overkill para 2 users
  DECISÃO: Rejeitado - over-engineering

Opção B: Apenas webhook
  TOConline notifica quando factura criada
  
  CONTRAS:
    - Como triggerar criação factura?
    - Sem controlo fluxo
  DECISÃO: Rejeitado

CONSEQUÊNCIAS:
- Implementação simples
- UX direto (loading → sucesso/erro)
- Webhook adicional para auto-update "PAGO"
- Retry manual se necessário

==================================================
DT-008: DEPLOY - DOCKER VS VERCEL
==================================================

DATA: Dezembro 2025
STATUS: ⏳ A decidir (durante Fase 5)

CONTEXTO:
Onde hostear aplicação produção?

OPÇÕES:

Opção A: Self-hosted (Raspberry Pi / VPS)
  PRÓS:
  ✅ Controlo total
  ✅ Zero custos recorrentes (após hardware)
  ✅ Dados permanecem internos
  ✅ Docker compose simples
  
  CONTRAS:
  ❌ Manutenção manual
  ❌ Uptime depende de infraestrutura local
  ❌ Backup responsabilidade nossa

Opção B: Vercel + Vercel PostgreSQL
  PRÓS:
  ✅ Deploy automático (git push)
  ✅ Zero config
  ✅ CDN global
  
  CONTRAS:
  ❌ Custos mensais (~$20-50)
  ❌ Vendor lock-in
  ❌ PostgreSQL Vercel tem limites

Opção C: Railway / Render
  PRÓS:
  ✅ PostgreSQL incluído
  ✅ Deploy simples
  ✅ Preços justos
  
  CONTRAS:
  ❌ Custos recorrentes
  ❌ Menos controlo que self-hosted

RECOMENDAÇÃO PRELIMINAR:
- Fase 1-4: Desenvolvimento local
- Fase 5: Deploy Raspberry Pi (Agora Media já tem)
  - Docker Compose
  - Nginx reverse proxy
  - Backups para Google Drive
  - Custo: €0/mês
  
- Alternativa: Railway se Raspberry Pi não viável

DECISÃO FINAL: Durante Fase 5 após testes

==================================================
DT-009: TYPESCRIPT STRICT MODE
==================================================

DATA: Dezembro 2025
STATUS: ✅ Aceite

CONTEXTO:
TaxHacker usa TypeScript. Qual nível strictness?

DECISÃO: Strict mode habilitado

CONFIGURAÇÃO (tsconfig.json):
```json
{
  "compilerOptions": {
    "strict": true,
    "strictNullChecks": true,
    "noImplicitAny": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true
  }
}
```

JUSTIFICAÇÃO:

PRÓS:
✅ Catch erros compile-time
✅ Refactoring seguro
✅ Autocomplete melhor
✅ Documentação implícita (tipos)

CONTRAS:
❌ Desenvolvimento inicial mais lento (definir tipos)
❌ Curva aprendizagem TypeScript

EXEMPLO BENEFÍCIO:
```typescript
// Sem strict
function calcSaldo(user) {
  return user.transactions.reduce((sum, t) => sum + t.total, 0)
}
// Runtime error se user null, ou transactions undefined!

// Com strict
function calcSaldo(user: User | null): number {
  if (!user || !user.transactions) return 0
  return user.transactions.reduce((sum, t) => sum + t.total, 0)
}
// Compile error se não tratar nulls!
```

CONSEQUÊNCIAS:
- Menos bugs produção
- Manutenção facilitada
- Onboarding devs mais fácil (tipos = documentação)

==================================================
DT-010: TESTES - ESTRATÉGIA
==================================================

DATA: Dezembro 2025
STATUS: ⏳ A implementar (Fase 5)

CONTEXTO:
Qual estratégia de testes para garantir qualidade?

DECISÃO: Testes críticos apenas (pragmático)

ESTRATÉGIA:

1. UNIT TESTS (lib/agora/)
   Framework: Vitest
   
   Testar:
   ✅ Cálculo saldos (crítico!)
   ✅ Conversões monetárias (cêntimos ↔ euros)
   ✅ Lógica impostos (IVA, retenções)
   
   Exemplo:
   ```typescript
   describe('calculateSaldoBruno', () => {
     it('soma projetos pessoais RECEBIDOS', async () => {
       // Mock transactions
       const saldo = await calculateSaldoBruno(userId)
       expect(saldo.ins.projetosPessoais).toBe(150000) // €1500
     })
   })
   ```

2. E2E TESTS (críticos)
   Framework: Playwright
   
   Testar:
   ✅ Login → dashboard
   ✅ Criar projeto → ver saldo actualizado
   ✅ Converter orçamento → ver transaction criada
   ✅ Emitir factura TOConline
   
   NÃO testar:
   ❌ Cada página individual
   ❌ CSS/styling
   ❌ Edge cases raros

3. MANUAL TESTING
   ✅ Antes deploy produção
   ✅ Após mudanças críticas

JUSTIFICAÇÃO:

PRÓS:
✅ Foco em lógica crítica (dinheiro!)
✅ Rápido implementar (não 100% cobertura)
✅ Suficiente para 2 users

CONTRAS:
❌ Cobertura não completa
❌ Alguns bugs podem passar

ALTERNATIVAS:

Opção A: TDD completo (100% cobertura)
  CONTRAS: 
    - Desenvolvimento 2x mais lento
    - Overkill para projeto interno
  DECISÃO: Rejeitado

Opção B: Zero testes
  CONTRAS:
    - Risco alto bugs dinheiro
    - Refactoring assustador
  DECISÃO: Rejeitado

CONSEQUÊNCIAS:
- Confiança em cálculos críticos
- Deploy mais seguro
- Manutenção facilitada
- Pragmatismo (não perfectionism)

==================================================
RESUMO PRINCÍPIOS DECISÕES
==================================================

PRIORIDADES AGORA MEDIA:

1. PRAGMATISMO > Perfectionism
   - Features suficientes > features perfeitas
   - Deploy funcional > arquitetura ideal

2. SELF-HOSTED > Cloud
   - Controlo dados
   - Zero custos recorrentes
   - Raspberry Pi suficiente

3. SIMPLES > Complexo
   - Evitar over-engineering
   - 2 users, não 2000 users
   - Adicionar complexidade apenas quando necessário

4. TYPE-SAFE > Flexível
   - TypeScript strict
   - Prisma schemas
   - Catch erros compile-time

5. DOCUMENTADO > Implícito
   - Decisões registadas (este doc!)
   - Código comentado quando não óbvio
   - README actualizado

TRADE-OFFS ACEITES:

✅ Fork TaxHacker = menos controlo, mas -6 semanas dev
✅ Custom Fields JSON = menos type-safe, mas flexível
✅ API síncrona TOConline = user espera, mas simples
✅ Testes críticos apenas = cobertura parcial, mas pragmático
✅ Self-hosted = manutenção manual, mas €0/mês

==================================================
PROCESSO NOVAS DECISÕES
==================================================

Quando surgir nova decisão técnica importante:

1. Documentar aqui (DT-XXX)
2. Incluir:
   - Contexto (porquê precisamos decidir?)
   - Opções consideradas
   - Prós/contras cada opção
   - Decisão tomada
   - Justificação
   - Consequências

3. Discutir com equipa antes de implementar

4. Actualizar este doc após implementação

FORMATO:
```
==================================================
DT-XXX: TÍTULO DA DECISÃO
==================================================

DATA: YYYY-MM-DD
STATUS: ✅ Aceite / ⏳ Em discussão / ❌ Rejeitado

CONTEXTO:
...

DECISÃO:
...

JUSTIFICAÇÃO:
...

ALTERNATIVAS:
...

CONSEQUÊNCIAS:
...
```

==================================================
