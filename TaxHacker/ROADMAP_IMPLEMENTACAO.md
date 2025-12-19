===============================================================================
ROADMAP DE IMPLEMENTAÇÃO: Plano Faseado de Desenvolvimento
Sprints organizados com prioridades e dependências
===============================================================================

==================================================
VISÃO GERAL
==================================================

DURAÇÃO TOTAL ESTIMADA: 8-10 semanas (part-time, 2-3h/dia)
SPRINTS: 5 fases principais
MILESTONE FINAL: Sistema completo substituindo app Python

PRINCÍPIOS:
✓ Entregas incrementais (cada sprint = funcionalidade utilizável)
✓ Validação contínua (testar contra dados reais)
✓ Prioridade: features core antes de polish

==================================================
FASE 0: PREPARAÇÃO (1 semana)
==================================================

OBJECTIVO: Fork configurado, ambiente de dev pronto, decisões tomadas

TAREFAS:
-------------------------------------------------

□ 0.1 Fork e Setup Local [2h]
  - Fork TaxHacker → agora-contabilidade
  - git clone + npm install
  - Copiar .env.example → .env
  - Criar database PostgreSQL local
  - npx prisma generate && npx prisma migrate dev
  - npm run dev → confirmar http://localhost:7331 funciona

□ 0.2 Remover Features Desnecessárias [3h]
  - Remover/comentar código AI (lib/llm-providers.ts)
  - Remover billing/Stripe (lib/stripe.ts)
  - Simplificar landing page (app/landing/)
  - Limpar componentes não usados
  DECISÃO: Manter ou remover completamente?

□ 0.3 Configurar Ambiente de Produção [2h]
  - Escolher: Raspberry Pi / VPS / Vercel
  - Se self-hosted: preparar Docker
  - Criar database PostgreSQL produção
  - Configurar variáveis ambiente produção

□ 0.4 Estudar Código TaxHacker [4h]
  - Ler prisma/schema.prisma (entender modelos)
  - Explorar lib/db.ts (como fazer queries)
  - Ver app/(app)/transactions/page.tsx (padrão UI)
  - Testar criar transaction manualmente na UI
  - Confirmar como funciona sistema de custom fields

□ 0.5 Decisões Técnicas [1h]
  - TypeScript: usar strict mode?
  - Testes: adicionar Jest/Vitest?
  - Linting: manter ESLint config existente
  - Git workflow: branches? main direto?

ENTREGÁVEL:
✅ App TaxHacker rodando localmente
✅ Familiarização com código base
✅ Ambiente prod configurado (se aplicável)

VALIDAÇÃO:
- Consegues criar users, transactions, projects na UI
- Código compila sem erros (npm run build)

==================================================
FASE 1: MIGRAÇÃO DE DADOS (1.5 semanas)
==================================================

OBJECTIVO: Dados Python migrados para TaxHacker, saldos validados

SPRINT 1.1: Extensão do Schema Prisma [4h]
-------------------------------------------------

□ 1.1.1 Adicionar Modelos ao schema.prisma [2h]
  Ficheiro: `prisma/schema.prisma`
  
  Adicionar:
  - model Equipment { ... }
  - model Budget { ... }
  - model BudgetItem { ... }
  - enum BudgetStatus { ... }
  
  Relações:
  - User → Equipment[]
  - User → Budget[]
  - Budget → BudgetItem[]
  - Transaction ← Budget (convertedFromBudget)

□ 1.1.2 Criar Migration [1h]
  ```bash
  npx prisma migrate dev --name add_agora_models
  npx prisma generate
  ```
  
  Validar:
  - Migration criada em prisma/migrations/
  - Types TypeScript gerados
  - npm run build funciona

□ 1.1.3 Seed Categories e Projects [1h]
  Ficheiro: `prisma/seed.ts` (criar se não existe)
  
  Código:
  ```typescript
  const categories = [
    { code: 'RECEBIDO', name: 'Recebido', color: '#22c55e' },
    { code: 'FATURADO', name: 'Faturado', color: '#f59e0b' },
    { code: 'NAO_FATURADO', name: 'Não Faturado', color: '#9ca3af' },
    { code: 'FIXA_MENSAL', name: 'Despesa Fixa', color: '#ef4444' },
    { code: 'DESPESA_PESSOAL_BRUNO', name: 'Despesa Bruno', color: '#3b82f6' },
    { code: 'DESPESA_PESSOAL_RAFAEL', name: 'Despesa Rafael', color: '#8b5cf6' },
    { code: 'BOLETIM', name: 'Boletim', color: '#ec4899' }
  ]
  
  const projects = [
    { code: 'EMPRESA', name: 'Agora Media', color: '#10b981' },
    { code: 'PESSOAL_BRUNO', name: 'Projetos Bruno', color: '#3b82f6' },
    { code: 'PESSOAL_RAFAEL', name: 'Projetos Rafael', color: '#8b5cf6' }
  ]
  ```
  
  Run: `npx prisma db seed`

SPRINT 1.2: Scripts de Migração [8h]
-------------------------------------------------

□ 1.2.1 Script Migrar Users [1h]
  Ficheiro: `lib/migrations/migrate-users.ts`
  
  Input: Python SQLite (agora_media.db)
  Output: TaxHacker PostgreSQL
  
  Lógica:
  - Ler users de SQLite
  - Criar em Prisma com Better Auth
  - Mapear Bruno/Rafael emails
  - Gerar passwords temporários

□ 1.2.2 Script Migrar Projetos [3h]
  Ficheiro: `lib/migrations/migrate-projects.ts`
  
  Mapeamento:
  - Projeto Python → Transaction (type: 'income')
  - tipo → projectCode
  - estado → categoryCode
  - valor_sem_iva * 100 → total (cêntimos!)
  - premio_bruno/rafael → extra JSON
  - cliente info → extra JSON
  
  Validações:
  - Todos projetos RECEBIDOS migrados
  - Valores convertidos correctamente (x100)
  - Relações preservadas

□ 1.2.3 Script Migrar Despesas [2h]
  Ficheiro: `lib/migrations/migrate-despesas.ts`
  
  Mapeamento:
  - Despesa Python → Transaction (type: 'expense')
  - tipo → categoryCode
  - valor_sem_iva * -100 → total (negativo + cêntimos!)
  - estado → extra.estado_pagamento
  - fornecedor info → extra JSON
  
  Atenção:
  - Despesas são NEGATIVAS
  - Multiplicar por 100 (cêntimos)

□ 1.2.4 Script Migrar Boletins [1h]
  Ficheiro: `lib/migrations/migrate-boletins.ts`
  
  Mapeamento:
  - Boletim Python → Transaction (type: 'expense')
  - socio → extra.socio
  - valor * -100 → total
  - estado → categoryCode (BOLETIM_PENDENTE/PAGO)

□ 1.2.5 Run All Migrations [1h]
  Script master: `lib/migrations/run-all.ts`
  
  ```typescript
  import { migrateUsers } from './migrate-users'
  import { migrateProjects } from './migrate-projects'
  import { migrateDespesas } from './migrate-despesas'
  import { migrateBoletins } from './migrate-boletins'
  
  async function runMigrations() {
    console.log('🚀 Iniciando migrações...')
    
    await migrateUsers()
    console.log('✅ Users migrados')
    
    await migrateProjects()
    console.log('✅ Projetos migrados')
    
    await migrateDespesas()
    console.log('✅ Despesas migradas')
    
    await migrateBoletins()
    console.log('✅ Boletins migrados')
    
    console.log('🎉 Migração completa!')
  }
  ```

SPRINT 1.3: Validação de Saldos [4h]
-------------------------------------------------

□ 1.3.1 Implementar Cálculo Saldos TypeScript [2h]
  Ficheiro: `lib/agora/saldos.ts`
  
  Funções:
  - calculateSaldoBruno(userId, filters?)
  - calculateSaldoRafael(userId, filters?)
  
  Lógica:
  - Buscar transactions com Prisma
  - Filtrar por projectCode, categoryCode
  - Agregar totais
  - Aplicar regras negócio (despesas fixas ÷ 2)

□ 1.3.2 Script de Validação [1h]
  Ficheiro: `lib/migrations/validate-saldos.ts`
  
  Comparar:
  - Saldos calculados em Python (app original)
  - Saldos calculados em TypeScript (TaxHacker)
  
  Output:
  ```
  BRUNO:
    Python:     €1,225.00
    TypeScript: €1,225.00
    ✅ MATCH
    
  RAFAEL:
    Python:     €1,700.00
    TypeScript: €1,700.00
    ✅ MATCH
  ```

□ 1.3.3 Corrigir Discrepâncias [1h]
  Se valores não batem:
  - Debug queries Prisma
  - Verificar conversão cêntimos
  - Confirmar filtros (RECEBIDO, PAGO)
  - Re-run migrations se necessário

ENTREGÁVEL FASE 1:
✅ Todos os dados migrados
✅ Saldos validados (match Python)
✅ Database production-ready

VALIDAÇÃO:
- Query manualmente no PostgreSQL
- Ver transactions na UI TaxHacker
- Saldos Bruno e Rafael correctos

==================================================
FASE 2: FEATURES CORE (2 semanas)
==================================================

OBJECTIVO: Saldos + Impostos funcionais na UI

SPRINT 2.1: Dashboard Saldos [6h]
-------------------------------------------------

□ 2.1.1 API Endpoint Saldos [1h]
  Ficheiro: `app/api/agora/saldos/route.ts`
  
  ```typescript
  export async function GET(request: Request) {
    const { searchParams } = new URL(request.url)
    const startDate = searchParams.get('startDate')
    const endDate = searchParams.get('endDate')
    
    const user = await getCurrentUser()
    
    const saldoBruno = await calculateSaldoBruno(user.id, { startDate, endDate })
    const saldoRafael = await calculateSaldoRafael(user.id, { startDate, endDate })
    
    return Response.json({ bruno: saldoBruno, rafael: saldoRafael })
  }
  ```

□ 2.1.2 Componente SaldoCard [2h]
  Ficheiro: `components/agora/saldo-card.tsx`
  
  Props:
  - socio: 'BRUNO' | 'RAFAEL'
  - saldo: number
  - ins: { projetosPessoais, premios, total }
  - outs: { despesasFixas, boletins, despesasPessoais, total }
  - sugestaBoletim: number
  
  Layout:
  - Card com badge de valor
  - Secção INs (verde)
  - Secção OUTs (vermelho)
  - Destaque sugestão boletim (azul)

□ 2.1.3 Página Saldos [2h]
  Ficheiro: `app/(app)/saldos/page.tsx`
  
  Layout:
  ```typescript
  <div className="grid grid-cols-2 gap-6">
    <SaldoCard socio="BRUNO" {...saldoBruno} />
    <SaldoCard socio="RAFAEL" {...saldoRafael} />
  </div>
  
  <div className="mt-8">
    <BreakdownDetalhado />
  </div>
  ```

□ 2.1.4 Adicionar ao Menu [1h]
  Ficheiro: `app/(app)/layout.tsx`
  
  Adicionar item:
  ```typescript
  {
    href: '/saldos',
    label: 'Saldos Pessoais',
    icon: Scale
  }
  ```

SPRINT 2.2: Gestão Fiscal (Impostos) [8h]
-------------------------------------------------

□ 2.2.1 Lógica Cálculo Impostos [3h]
  Ficheiro: `lib/agora/impostos.ts`
  
  Funções:
  - calculateIVAPeriodo(trimestre, ano)
  - calculateRetencoes(periodo)
  - calculateIRCEstimado(ano)
  
  Lógica:
  - Buscar transactions do período
  - Calcular IVA liquidado (vendas) - IVA dedutível (compras)
  - Somar retenções na fonte
  - Estimar IRC (23% sobre lucro)

□ 2.2.2 Componentes Fiscais [3h]
  Ficheiros:
  - `components/agora/iva-summary.tsx`
  - `components/agora/retencoes-table.tsx`
  - `components/agora/irc-estimado.tsx`
  
  Features:
  - Selector trimestre
  - Tabela breakdown IVA
  - Lista retenções com download
  - Estimativa IRC com explicação

□ 2.2.3 Página Impostos [1h]
  Ficheiro: `app/(app)/impostos/page.tsx`
  
  Layout 3 colunas:
  - IVA a pagar
  - Retenções acumuladas
  - IRC estimado

□ 2.2.4 API Endpoint [1h]
  Ficheiro: `app/api/agora/impostos/route.ts`
  
  Query params:
  - periodo (trimestre ou mês)
  - ano

SPRINT 2.3: Custom Fields UI [4h]
-------------------------------------------------

□ 2.3.1 Criar Custom Fields via UI [2h]
  Navegar: `/fields` (já existe no TaxHacker)
  
  Criar manualmente:
  - premio_bruno (number)
  - premio_rafael (number)
  - socio (select: BRUNO/RAFAEL)
  - cliente_nome (string)
  - fornecedor_nome (string)
  - estado_pagamento (select: PENDENTE/PAGO)

□ 2.3.2 Testar em Transactions [1h]
  - Criar transaction de teste
  - Preencher custom fields
  - Confirmar salvam no extra JSON
  - Testar filtros por custom fields

□ 2.3.3 Script Seed Custom Fields [1h]
  Alternativa: automatizar criação via seed
  Ficheiro: `prisma/seed-custom-fields.ts`

ENTREGÁVEL FASE 2:
✅ Dashboard saldos funcional
✅ Fiscal dashboard operacional
✅ Custom fields configurados

VALIDAÇÃO:
- Abrir /saldos → ver saldos Bruno e Rafael
- Abrir /impostos → ver IVA trimestre actual
- Criar transaction → preencher custom fields

==================================================
FASE 3: EQUIPAMENTO + ORÇAMENTOS (2 semanas)
==================================================

OBJECTIVO: Workflow completo orçamento → projeto

SPRINT 3.1: Catálogo Equipamento [8h]
-------------------------------------------------

□ 3.1.1 CRUD Equipamento [3h]
  Ficheiros:
  - `app/(app)/equipamento/page.tsx` (lista)
  - `app/(app)/equipamento/novo/page.tsx` (criar)
  - `app/(app)/equipamento/[id]/page.tsx` (editar)
  - `app/api/agora/equipamento/route.ts` (API)
  
  Campos form:
  - Nome, categoria
  - Data compra, valor compra
  - Vida útil (anos)
  - Taxa diária aluguer

□ 3.1.2 Cálculo Amortização [2h]
  Ficheiro: `lib/agora/equipamento.ts`
  
  Função:
  ```typescript
  function calculateDepreciation(equipment: Equipment): number {
    const ageYears = (Date.now() - equipment.purchaseDate) / (1000*60*60*24*365)
    const depreciationRate = 1 / equipment.lifeYears
    const currentValue = equipment.purchasePrice * (1 - depreciationRate * ageYears)
    return Math.max(0, currentValue)
  }
  ```

□ 3.1.3 UI Tabela Equipamento [2h]
  Componente: `components/agora/equipment-table.tsx`
  
  Colunas:
  - Nome | Categoria | Valor Actual | Taxa/dia | Acções
  
  Features:
  - Sort por valor
  - Filtro por categoria
  - Badge estado (novo/usado/antigo)

□ 3.1.4 Testes [1h]
  - Criar 5 equipamentos teste
  - Validar cálculo amortização
  - Testar edit/delete

SPRINT 3.2: Sistema de Orçamentos [12h]
-------------------------------------------------

□ 3.2.1 CRUD Orçamentos Backend [3h]
  Ficheiro: `app/api/agora/orcamentos/route.ts`
  
  Endpoints:
  - POST /api/agora/orcamentos (criar)
  - GET /api/agora/orcamentos (listar)
  - GET /api/agora/orcamentos/[id] (detalhe)
  - PUT /api/agora/orcamentos/[id] (editar)
  - DELETE /api/agora/orcamentos/[id]

□ 3.2.2 Formulário Orçamento [4h]
  Ficheiro: `app/(app)/orcamentos/novo/page.tsx`
  
  Secções:
  1. Info Cliente (nome, NIF, email)
  2. Items:
     - Descrição manual OU
     - Picker de equipamento (preenche automático)
     - Quantidade, valor unitário
     - Subtotal calculado
  3. Totais (subtotal + IVA + total)
  4. Validade, notas
  
  Features:
  - Add/remove items dinamicamente
  - Calcular totais em tempo real
  - Validação campos obrigatórios

□ 3.2.3 Listagem Orçamentos [2h]
  Ficheiro: `app/(app)/orcamentos/page.tsx`
  
  Tabela:
  - Número | Cliente | Total | Estado | Acções
  
  Filtros:
  - Estado (DRAFT/SENT/APPROVED/REJECTED/CONVERTED)
  - Data
  
  Acções:
  - Ver/Editar
  - Gerar PDF
  - Enviar email
  - Converter em projeto

□ 3.2.4 Conversão para Projeto [2h]
  Ficheiro: `app/api/agora/orcamentos/[id]/convert/route.ts`
  
  Lógica:
  - Validar budget.status === 'APPROVED'
  - Criar Transaction (type: 'income')
  - Copiar items para extra JSON
  - Actualizar budget.status = 'CONVERTED'
  - Link budget ↔ transaction
  
  UI:
  Botão "Converter em Projeto" (só se APPROVED)

□ 3.2.5 Gerar PDF Orçamento [1h]
  Ficheiro: `app/api/agora/orcamentos/[id]/pdf/route.ts`
  
  Usar: @react-pdf/renderer (já incluído!)
  
  Template:
  - Header com logo Agora Media
  - Info cliente
  - Tabela items
  - Totais
  - Footer (validade, condições)

ENTREGÁVEL FASE 3:
✅ Catálogo equipamento funcional
✅ Sistema orçamentos completo
✅ Workflow orçamento → projeto operacional

VALIDAÇÃO:
- Criar equipamento → aparece na lista
- Criar orçamento com equipamento → valores correctos
- Aprovar orçamento → converter → ver como transaction

==================================================
FASE 4: INTEGRAÇÃO TOCONLINE (1.5 semanas)
==================================================

OBJECTIVO: Emitir facturas AT automaticamente

SPRINT 4.1: TOConline API Client [6h]
-------------------------------------------------

□ 4.1.1 Obter Credenciais [1h]
  - Registar conta TOConline
  - Gerar API key
  - Testar endpoint ping
  - Documentar em .env.example

□ 4.1.2 Client Base [2h]
  Ficheiro: `lib/agora/toconline/client.ts`
  
  ```typescript
  export class TOConlineClient {
    constructor(private apiKey: string) {}
    
    async request(endpoint: string, options: RequestInit) {
      const response = await fetch(`https://api.toconline.pt/v1${endpoint}`, {
        ...options,
        headers: {
          'Authorization': `Bearer ${this.apiKey}`,
          'Content-Type': 'application/json',
          ...options.headers
        }
      })
      
      if (!response.ok) {
        throw new TOConlineError(await response.json())
      }
      
      return response.json()
    }
  }
  ```

□ 4.1.3 Módulo Customers [1h]
  Ficheiro: `lib/agora/toconline/customers.ts`
  
  Funções:
  - getCustomer(email): buscar cliente
  - createCustomer(data): criar se não existe
  - updateCustomer(id, data)

□ 4.1.4 Módulo Invoices [2h]
  Ficheiro: `lib/agora/toconline/invoices.ts`
  
  Funções:
  - createInvoice(data): emitir factura
  - getInvoice(id): buscar
  - downloadPDF(id): obter PDF certificado

SPRINT 4.2: Integração com Projetos [6h]
-------------------------------------------------

□ 4.2.1 UI Botão "Emitir Factura" [2h]
  Local: `app/(app)/transactions/[id]/page.tsx`
  
  Condições para mostrar:
  - Transaction type = 'income'
  - categoryCode != 'RECEBIDO' (ainda não facturado)
  - extra.cliente_nome existe
  
  Ao clicar:
  - Modal confirmação
  - Chamar API

□ 4.2.2 API Endpoint Emitir [3h]
  Ficheiro: `app/api/agora/toconline/invoices/route.ts`
  
  Fluxo:
  1. Buscar transaction
  2. Verificar/criar cliente TOConline
  3. Emitir factura
  4. Salvar invoice_id em extra JSON
  5. Actualizar categoryCode → 'FATURADO'
  6. Retornar PDF URL

□ 4.2.3 Sincronização Automática [1h]
  Opcional: webhook TOConline
  
  Quando factura é paga na AT:
  - Receber webhook
  - Actualizar transaction → 'RECEBIDO'

SPRINT 4.3: Settings TOConline [3h]
-------------------------------------------------

□ 4.3.1 Página Settings [2h]
  Ficheiro: `app/(app)/toconline/page.tsx`
  
  Form:
  - API Key (password field)
  - Testar conexão (botão)
  - Log últimas sincronizações
  - Estatísticas (X facturas emitidas)

□ 4.3.2 Salvar Settings [1h]
  Usar: model Setting (já existe TaxHacker)
  
  ```typescript
  await prisma.setting.upsert({
    where: { userId_code: { userId, code: 'TOCONLINE_API_KEY' } },
    create: { userId, code: 'TOCONLINE_API_KEY', value: apiKey },
    update: { value: apiKey }
  })
  ```

ENTREGÁVEL FASE 4:
✅ Integração TOConline funcional
✅ Emissão facturas AT automatizada
✅ Download PDFs certificados

VALIDAÇÃO:
- Emitir factura de teste
- Verificar aparece no TOConline
- Download PDF funciona
- Transaction muda estado

==================================================
FASE 5: POLISH & DEPLOY (1 semana)
==================================================

OBJECTIVO: App production-ready

SPRINT 5.1: UI/UX Refinements [6h]
-------------------------------------------------

□ 5.1.1 Dark Mode [1h]
  TaxHacker já tem (next-themes)
  Validar todos os novos componentes

□ 5.1.2 Loading States [2h]
  Adicionar Suspense/Loading:
  - Saldos (skeleton)
  - Impostos (spinner)
  - Orçamentos (table skeleton)

□ 5.1.3 Error Handling [2h]
  - Toast notifications (Sonner já incluído)
  - Error boundaries
  - Validation messages

□ 5.1.4 Mobile Responsive [1h]
  Testar em mobile:
  - Dashboard saldos (stack cards)
  - Tabelas (horizontal scroll)
  - Forms (full width)

SPRINT 5.2: Performance [4h]
-------------------------------------------------

□ 5.2.1 Database Indexes [1h]
  Adicionar no schema.prisma:
  ```prisma
  @@index([userId, projectCode])
  @@index([userId, categoryCode])
  @@index([issuedAt])
  ```

□ 5.2.2 Query Optimization [2h]
  - Usar Prisma select (só campos necessários)
  - Batch queries onde possível
  - Cache cálculos pesados (Redis?)

□ 5.2.3 Bundle Size [1h]
  - npm run build → verificar size
  - Remover imports desnecessários
  - Dynamic imports para rotas pesadas

SPRINT 5.3: Testes E2E [6h]
-------------------------------------------------

□ 5.3.1 Testes Críticos [4h]
  Framework: Playwright (adicionar)
  
  Cenários:
  1. Login → ver dashboard
  2. Criar projeto → ver em /transactions
  3. Calcular saldos → valores correctos
  4. Criar orçamento → converter em projeto
  5. Emitir factura TOConline

□ 5.3.2 Testes Unitários Saldos [2h]
  Framework: Vitest
  
  Ficheiro: `lib/agora/__tests__/saldos.test.ts`
  
  Testes:
  - Projetos pessoais contam
  - Prémios somam correctamente
  - Despesas fixas dividem por 2
  - Boletins descontam

SPRINT 5.4: Deploy [4h]
-------------------------------------------------

□ 5.4.1 Docker Build [1h]
  - Testar Dockerfile existente
  - Build image: `docker build -t agora-contabilidade .`
  - Run local: `docker-compose up`

□ 5.4.2 Deploy Production [2h]
  Opção A: Self-hosted (Raspberry Pi)
  - SSH para server
  - git clone repo
  - docker-compose up -d
  - Configurar nginx reverse proxy
  
  Opção B: Cloud (Railway/Vercel)
  - Conectar repo GitHub
  - Configure env vars
  - Deploy automático

□ 5.4.3 Backup Strategy [1h]
  - Configurar backup diário PostgreSQL
  - Script: pg_dump → upload para cloud
  - Testar restore

SPRINT 5.5: Documentação [4h]
-------------------------------------------------

□ 5.5.1 README.md [1h]
  - Setup instructions
  - ENV vars necessárias
  - Como rodar localmente
  - Deploy instructions

□ 5.5.2 User Guide [2h]
  - Como usar dashboard saldos
  - Workflow orçamentos
  - Integração TOConline
  - Troubleshooting comum

□ 5.5.3 Developer Docs [1h]
  - Estrutura código
  - Como adicionar features
  - Database schema overview
  - API endpoints

ENTREGÁVEL FASE 5:
✅ App deployada em produção
✅ Backups configurados
✅ Documentação completa
✅ Testes críticos passam

VALIDAÇÃO FINAL:
- Bruno e Rafael conseguem usar app
- Todos os workflows core funcionam
- Performance aceitável
- Dados seguros (backups)

==================================================
RESUMO CRONOGRAMA
==================================================

SEMANA 1: Fase 0 (Preparação)
SEMANAS 2-3: Fase 1 (Migração Dados)
SEMANAS 4-5: Fase 2 (Features Core)
SEMANAS 6-7: Fase 3 (Equipamento + Orçamentos)
SEMANAS 8-9: Fase 4 (TOConline)
SEMANA 10: Fase 5 (Polish + Deploy)

MARCO IMPORTANTE: Fim Semana 5
→ MVP utilizável (saldos + impostos funcionais)
→ Decisão: continuar ou ajustar roadmap

==================================================
GESTÃO DE RISCOS
==================================================

RISCO: Demora mais que esperado
MITIGAÇÃO: MVP reduzido fim Semana 5, resto é bónus

RISCO: TOConline API muda/problema
MITIGAÇÃO: Integração é Fase 4, não bloqueia resto

RISCO: Performance PostgreSQL lenta
MITIGAÇÃO: Adicionar indexes, usar cache

RISCO: Bugs críticos em produção
MITIGAÇÃO: Manter app Python como fallback Mês 1

==================================================
TRACKING PROGRESSO
==================================================

RECOMENDAÇÃO: Usar GitHub Projects ou Trello

COLUNAS:
- Backlog
- In Progress
- Testing
- Done

REVIEW: Fim de cada sprint (sexta-feira)
- O que foi feito?
- Bloqueios?
- Ajustar próximo sprint

==================================================
