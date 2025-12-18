===============================================================================
ARQUITETURA TÉCNICA: Agora Contabilidade sobre TaxHacker
Estrutura de ficheiros, extensões e organização do código
===============================================================================

==================================================
ESTRUTURA BASE TAXHACKER (EXISTENTE)
==================================================

```
TaxHacker/
├── app/
│   ├── (app)/                      # App routes (autenticado)
│   │   ├── transactions/           # Lista de transações
│   │   ├── projects/               # Gestão de projetos
│   │   ├── categories/             # Gestão de categorias
│   │   ├── fields/                 # Custom fields
│   │   ├── settings/               # Configurações
│   │   └── files/                  # Upload de ficheiros
│   │
│   ├── (auth)/                     # Auth routes
│   │   ├── login/
│   │   └── signup/
│   │
│   ├── api/                        # API routes
│   │   ├── auth/
│   │   ├── transactions/
│   │   ├── files/
│   │   └── export/
│   │
│   ├── layout.tsx                  # Root layout
│   └── globals.css                 # Global styles
│
├── lib/                            # Business logic
│   ├── auth.ts                     # Better Auth config
│   ├── db.ts                       # Prisma client
│   ├── files.ts                    # File handling
│   ├── stats.ts                    # Statistics
│   ├── utils.ts                    # Utilities
│   └── email.ts                    # Email (Resend)
│
├── prisma/
│   ├── schema.prisma               # Database schema
│   └── migrations/                 # DB migrations
│
├── components/                     # React components
│   ├── ui/                         # Radix UI components
│   └── [feature-components]/
│
└── public/                         # Static assets
```

==================================================
EXTENSÕES AGORA MEDIA (ADICIONAR)
==================================================

```
TaxHacker/
├── lib/
│   ├── agora/                      # NOVA PASTA - Lógica Agora Media
│   │   ├── saldos.ts               # Cálculo saldos sócios
│   │   ├── impostos.ts             # IVA, retenções, IRC
│   │   ├── equipamento.ts          # Gestão equipamento
│   │   ├── orcamentos.ts           # Workflow orçamentos
│   │   └── toconline/              # Integração TOConline
│   │       ├── client.ts           # API client
│   │       ├── invoices.ts         # Emissão facturas
│   │       ├── customers.ts        # Sync clientes
│   │       └── types.ts            # TypeScript types
│   │
│   └── migrations/                 # Scripts migração Python -> Prisma
│       ├── migrate-projects.ts
│       ├── migrate-despesas.ts
│       ├── migrate-boletins.ts
│       └── validate-saldos.ts      # Comparar cálculos
│
├── app/
│   ├── (app)/
│   │   ├── saldos/                 # NOVA ROTA - Dashboard saldos
│   │   │   ├── page.tsx            # Vista principal
│   │   │   ├── components/
│   │   │   │   ├── saldo-card.tsx  # Card sócio
│   │   │   │   ├── breakdown.tsx   # Detalhe INs/OUTs
│   │   │   │   └── historico.tsx   # Gráfico evolução
│   │   │   └── actions.ts          # Server actions
│   │   │
│   │   ├── impostos/               # NOVA ROTA - Fiscal dashboard
│   │   │   ├── page.tsx
│   │   │   ├── components/
│   │   │   │   ├── iva-summary.tsx
│   │   │   │   ├── retencoes.tsx
│   │   │   │   └── irc-estimado.tsx
│   │   │   └── actions.ts
│   │   │
│   │   ├── equipamento/            # NOVA ROTA - Catálogo equipamento
│   │   │   ├── page.tsx
│   │   │   ├── [id]/
│   │   │   │   └── page.tsx        # Detalhe equipamento
│   │   │   ├── components/
│   │   │   │   ├── equipment-table.tsx
│   │   │   │   ├── depreciation-calc.tsx
│   │   │   │   └── equipment-form.tsx
│   │   │   └── actions.ts
│   │   │
│   │   ├── orcamentos/             # NOVA ROTA - Gestão orçamentos
│   │   │   ├── page.tsx            # Lista orçamentos
│   │   │   ├── novo/
│   │   │   │   └── page.tsx        # Criar orçamento
│   │   │   ├── [id]/
│   │   │   │   ├── page.tsx        # Detalhe/editar
│   │   │   │   └── pdf/
│   │   │   │       └── route.ts    # Gerar PDF
│   │   │   ├── components/
│   │   │   │   ├── budget-form.tsx
│   │   │   │   ├── budget-items.tsx
│   │   │   │   ├── equipment-picker.tsx
│   │   │   │   └── convert-to-project.tsx
│   │   │   └── actions.ts
│   │   │
│   │   └── toconline/              # NOVA ROTA - Config integração
│   │       ├── page.tsx            # Settings TOConline
│   │       └── actions.ts
│   │
│   └── api/
│       ├── agora/                  # NOVOS ENDPOINTS
│       │   ├── saldos/
│       │   │   └── route.ts        # GET /api/agora/saldos
│       │   ├── impostos/
│       │   │   └── route.ts        # GET /api/agora/impostos
│       │   ├── equipamento/
│       │   │   └── route.ts        # CRUD equipamento
│       │   ├── orcamentos/
│       │   │   ├── route.ts        # CRUD orçamentos
│       │   │   └── [id]/
│       │   │       ├── convert/
│       │   │       │   └── route.ts    # POST converter em projeto
│       │   │       └── pdf/
│       │   │           └── route.ts    # GET PDF orçamento
│       │   └── toconline/
│       │       ├── invoices/
│       │       │   └── route.ts    # POST emitir factura
│       │       └── sync/
│       │           └── route.ts    # POST sync clientes
│       │
│       └── webhooks/
│           └── toconline/
│               └── route.ts        # Webhook TOConline
│
├── prisma/
│   └── schema.prisma               # MODIFICADO - adicionar modelos
│
└── components/
    └── agora/                      # NOVOS COMPONENTES
        ├── saldo-card.tsx
        ├── fiscal-dashboard.tsx
        ├── equipment-table.tsx
        ├── budget-form.tsx
        └── toconline-status.tsx
```

==================================================
PRISMA SCHEMA - EXTENSÕES
==================================================

prisma/schema.prisma - ADICIONAR ao schema existente:

```prisma
model Equipment {
  id            String   @id @default(uuid()) @db.Uuid
  userId        String   @map("user_id") @db.Uuid
  user          User     @relation(fields: [userId], references: [id], onDelete: Cascade)
  
  name          String
  category      String
  
  purchaseDate  DateTime @map("purchase_date")
  purchasePrice Int      @map("purchase_price")      // cêntimos
  lifeYears     Int      @map("life_years")          // anos úteis
  currentValue  Int      @map("current_value")       // calculado
  
  dailyRate     Int?     @map("daily_rate")          // taxa dia (cêntimos)
  
  note          String?
  createdAt     DateTime @default(now()) @map("created_at")
  updatedAt     DateTime @updatedAt @map("updated_at")
  
  budgetItems   BudgetItem[]
  
  @@index([userId])
  @@map("equipment")
}

model Budget {
  id              String       @id @default(uuid()) @db.Uuid
  userId          String       @map("user_id") @db.Uuid
  user            User         @relation(fields: [userId], references: [id], onDelete: Cascade)
  
  numero          String       @unique
  description     String?
  
  clienteName     String?      @map("cliente_name")
  clienteNIF      String?      @map("cliente_nif")
  clienteEmail    String?      @map("cliente_email")
  
  subtotal        Int
  iva             Int
  total           Int
  
  status          BudgetStatus @default(DRAFT)
  validUntil      DateTime     @map("valid_until")
  approvedAt      DateTime?    @map("approved_at")
  
  convertedToTransactionId String? @unique @map("converted_to_transaction_id")
  convertedTransaction     Transaction? @relation(fields: [convertedToTransactionId], references: [id])
  
  items           BudgetItem[]
  
  note            String?
  createdAt       DateTime     @default(now()) @map("created_at")
  updatedAt       DateTime     @updatedAt @map("updated_at")
  
  @@index([userId])
  @@index([status])
  @@map("budgets")
}

model BudgetItem {
  id          String     @id @default(uuid()) @db.Uuid
  budgetId    String     @map("budget_id") @db.Uuid
  budget      Budget     @relation(fields: [budgetId], references: [id], onDelete: Cascade)
  
  description String
  quantity    Int
  unitPrice   Int        @map("unit_price")
  total       Int
  
  equipmentId String?    @map("equipment_id") @db.Uuid
  equipment   Equipment? @relation(fields: [equipmentId], references: [id])
  
  createdAt   DateTime   @default(now()) @map("created_at")
  
  @@index([budgetId])
  @@map("budget_items")
}

enum BudgetStatus {
  DRAFT
  SENT
  APPROVED
  REJECTED
  CONVERTED
}

model Transaction {
  // ... campos existentes ...
  
  convertedFromBudget Budget?
  
  // ... resto dos campos ...
}

model User {
  // ... campos existentes ...
  
  equipment Equipment[]
  budgets   Budget[]
  
  // ... resto dos campos ...
}
```

==================================================
FLUXO DE DADOS: SALDOS
==================================================

CÁLCULO DE SALDOS (lib/agora/saldos.ts):

```typescript
import { prisma } from '@/lib/db'

export async function calculateSaldoBruno(
  userId: string,
  filters?: { startDate?: Date; endDate?: Date }
) {
  // 1. BUSCAR PROJETOS PESSOAIS (INs)
  const projetosPessoais = await prisma.transaction.aggregate({
    where: {
      userId,
      type: 'income',
      projectCode: 'PESSOAL_BRUNO',
      categoryCode: 'RECEBIDO',
      issuedAt: {
        gte: filters?.startDate,
        lte: filters?.endDate
      }
    },
    _sum: { total: true }
  })
  
  // 2. BUSCAR PRÉMIOS (INs)
  const premios = await prisma.transaction.findMany({
    where: {
      userId,
      type: 'income',
      projectCode: 'EMPRESA',
      categoryCode: 'RECEBIDO',
      issuedAt: {
        gte: filters?.startDate,
        lte: filters?.endDate
      }
    },
    select: { extra: true }
  })
  
  const totalPremios = premios.reduce((sum, t) => {
    const extra = t.extra as any
    return sum + (extra?.premio_bruno || 0)
  }, 0)
  
  // 3. DESPESAS FIXAS ÷ 2 (OUTs)
  const despesasFixas = await prisma.transaction.aggregate({
    where: {
      userId,
      type: 'expense',
      categoryCode: 'FIXA_MENSAL',
      extra: { path: ['estado_pagamento'], equals: 'PAGO' },
      issuedAt: {
        gte: filters?.startDate,
        lte: filters?.endDate
      }
    },
    _sum: { total: true }
  })
  
  const despesasFixasBruno = Math.abs(despesasFixas._sum.total || 0) / 2
  
  // 4. BOLETINS (OUTs)
  const boletins = await prisma.transaction.aggregate({
    where: {
      userId,
      type: 'expense',
      categoryCode: 'BOLETIM',
      extra: { path: ['socio'], equals: 'BRUNO' },
      issuedAt: {
        gte: filters?.startDate,
        lte: filters?.endDate
      }
    },
    _sum: { total: true }
  })
  
  // 5. DESPESAS PESSOAIS (OUTs)
  const despesasPessoais = await prisma.transaction.aggregate({
    where: {
      userId,
      type: 'expense',
      categoryCode: 'DESPESA_PESSOAL_BRUNO',
      extra: { path: ['estado_pagamento'], equals: 'PAGO' },
      issuedAt: {
        gte: filters?.startDate,
        lte: filters?.endDate
      }
    },
    _sum: { total: true }
  })
  
  // CÁLCULO FINAL
  const totalIns = (projetosPessoais._sum.total || 0) + totalPremios
  const totalOuts = despesasFixasBruno + 
                    Math.abs(boletins._sum.total || 0) +
                    Math.abs(despesasPessoais._sum.total || 0)
  
  const saldoTotal = totalIns - totalOuts
  
  return {
    socio: 'BRUNO',
    saldo: saldoTotal,
    ins: {
      projetosPessoais: projetosPessoais._sum.total || 0,
      premios: totalPremios,
      total: totalIns
    },
    outs: {
      despesasFixas: despesasFixasBruno,
      boletins: Math.abs(boletins._sum.total || 0),
      despesasPessoais: Math.abs(despesasPessoais._sum.total || 0),
      total: totalOuts
    },
    sugestaBoletim: Math.max(0, saldoTotal)
  }
}
```

==================================================
FLUXO DE DADOS: ORÇAMENTOS -> PROJETOS
==================================================

WORKFLOW (lib/agora/orcamentos.ts):

```typescript
export async function convertBudgetToProject(budgetId: string) {
  const budget = await prisma.budget.findUnique({
    where: { id: budgetId },
    include: { items: true }
  })
  
  if (!budget || budget.status !== 'APPROVED') {
    throw new Error('Orçamento precisa estar aprovado')
  }
  
  // Criar Transaction (projeto)
  const transaction = await prisma.transaction.create({
    data: {
      userId: budget.userId,
      type: 'income',
      name: budget.description || `Projeto ${budget.numero}`,
      total: budget.total,
      projectCode: 'EMPRESA',
      categoryCode: 'NAO_FATURADO',
      extra: {
        numero_projeto: budget.numero,
        orcamento_id: budget.id,
        items: budget.items,
        cliente_nome: budget.clienteName,
        cliente_nif: budget.clienteNIF
      }
    }
  })
  
  // Actualizar budget
  await prisma.budget.update({
    where: { id: budgetId },
    data: {
      status: 'CONVERTED',
      convertedToTransactionId: transaction.id
    }
  })
  
  return transaction
}
```

==================================================
INTEGRAÇÃO TOCONLINE
==================================================

CLIENT (lib/agora/toconline/client.ts):

```typescript
import { TOConlineConfig } from './types'

export class TOConlineClient {
  private apiKey: string
  private baseUrl = 'https://api.toconline.pt'
  
  constructor(apiKey: string) {
    this.apiKey = apiKey
  }
  
  async createInvoice(data: {
    customer_id: string
    lines: Array<{
      description: string
      quantity: number
      unit_price: number
      vat_rate: string
    }>
  }) {
    const response = await fetch(`${this.baseUrl}/v1/invoices`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.apiKey}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        document_type: 'FT',
        customer_id: data.customer_id,
        lines: data.lines
      })
    })
    
    if (!response.ok) {
      throw new Error(`TOConline API error: ${response.statusText}`)
    }
    
    return response.json()
  }
  
  async getCustomer(email: string) {
    // Implementar busca de cliente
  }
  
  async createCustomer(data: {
    business_name: string
    email: string
    tax_registration_number: string
  }) {
    // Implementar criação de cliente
  }
}
```

==================================================
COMPONENTES UI - EXEMPLOS
==================================================

SALDO CARD (components/agora/saldo-card.tsx):

```typescript
'use client'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { TrendingUp, TrendingDown } from 'lucide-react'

interface SaldoCardProps {
  socio: 'BRUNO' | 'RAFAEL'
  saldo: number
  ins: { total: number }
  outs: { total: number }
  sugestaBoletim: number
}

export function SaldoCard({ socio, saldo, ins, outs, sugestaBoletim }: SaldoCardProps) {
  const isPositive = saldo >= 0
  
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <span>Saldo {socio}</span>
          <Badge variant={isPositive ? 'default' : 'destructive'}>
            {formatEuros(saldo)}
          </Badge>
        </CardTitle>
      </CardHeader>
      
      <CardContent className="space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <TrendingUp className="h-4 w-4 text-green-500" />
            <span className="text-sm text-muted-foreground">Entradas (INs)</span>
          </div>
          <span className="font-semibold text-green-600">
            +{formatEuros(ins.total)}
          </span>
        </div>
        
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <TrendingDown className="h-4 w-4 text-red-500" />
            <span className="text-sm text-muted-foreground">Saídas (OUTs)</span>
          </div>
          <span className="font-semibold text-red-600">
            -{formatEuros(outs.total)}
          </span>
        </div>
        
        {sugestaBoletim > 0 && (
          <div className="rounded-lg bg-blue-50 p-3">
            <p className="text-xs text-blue-600 mb-1">Sugestão de boletim:</p>
            <p className="text-lg font-bold text-blue-700">
              {formatEuros(sugestaBoletim)}
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  )
}

function formatEuros(cents: number): string {
  return new Intl.NumberFormat('pt-PT', {
    style: 'currency',
    currency: 'EUR'
  }).format(cents / 100)
}
```

==================================================
NAVEGAÇÃO - MENU SIDEBAR
==================================================

ADICIONAR ao menu existente (app/(app)/layout.tsx):

```typescript
const menuItems = [
  // Existentes do TaxHacker
  { href: '/transactions', label: 'Transactions', icon: FileText },
  { href: '/projects', label: 'Projects', icon: Folder },
  
  // NOVOS ITEMS AGORA MEDIA
  { href: '/saldos', label: 'Saldos Pessoais', icon: Scale },
  { href: '/impostos', label: 'Impostos', icon: Calculator },
  { href: '/orcamentos', label: 'Orçamentos', icon: FileSpreadsheet },
  { href: '/equipamento', label: 'Equipamento', icon: Camera },
  
  { divider: true },
  
  // Existentes
  { href: '/categories', label: 'Categories', icon: Tag },
  { href: '/settings', label: 'Settings', icon: Settings }
]
```

==================================================
RESUMO FICHEIROS A CRIAR
==================================================

TOTAL: ~35 novos ficheiros

**lib/** (8 ficheiros):
- lib/agora/saldos.ts
- lib/agora/impostos.ts
- lib/agora/equipamento.ts
- lib/agora/orcamentos.ts
- lib/agora/toconline/client.ts
- lib/agora/toconline/invoices.ts
- lib/agora/toconline/customers.ts
- lib/agora/toconline/types.ts

**app/saldos/** (4 ficheiros):
- app/(app)/saldos/page.tsx
- app/(app)/saldos/actions.ts
- app/(app)/saldos/components/saldo-card.tsx
- app/(app)/saldos/components/breakdown.tsx

**app/impostos/** (5 ficheiros):
- app/(app)/impostos/page.tsx
- app/(app)/impostos/actions.ts
- app/(app)/impostos/components/iva-summary.tsx
- app/(app)/impostos/components/retencoes.tsx
- app/(app)/impostos/components/irc-estimado.tsx

**app/equipamento/** (5 ficheiros):
- app/(app)/equipamento/page.tsx
- app/(app)/equipamento/[id]/page.tsx
- app/(app)/equipamento/actions.ts
- app/(app)/equipamento/components/equipment-table.tsx
- app/(app)/equipamento/components/equipment-form.tsx

**app/orcamentos/** (7 ficheiros):
- app/(app)/orcamentos/page.tsx
- app/(app)/orcamentos/novo/page.tsx
- app/(app)/orcamentos/[id]/page.tsx
- app/(app)/orcamentos/[id]/pdf/route.ts
- app/(app)/orcamentos/actions.ts
- app/(app)/orcamentos/components/budget-form.tsx
- app/(app)/orcamentos/components/convert-to-project.tsx

**API routes** (6 ficheiros):
- app/api/agora/saldos/route.ts
- app/api/agora/impostos/route.ts
- app/api/agora/equipamento/route.ts
- app/api/agora/orcamentos/route.ts
- app/api/agora/orcamentos/[id]/convert/route.ts
- app/api/agora/toconline/invoices/route.ts

**prisma/** (1 ficheiro):
- Modificar prisma/schema.prisma

==================================================
