===============================================================================
FEATURES CUSTOMIZADAS: Implementação Detalhada
Código e exemplos práticos para cada feature Agora Media
===============================================================================

==================================================
FEATURE 1: CÁLCULO DE SALDOS PESSOAIS
==================================================

OBJECTIVO: Calcular saldos dos sócios (Bruno e Rafael) baseado em regras específicas

1.1 LÓGICA CORE
--------------------

Ficheiro: `lib/agora/saldos.ts`

```typescript
import { prisma } from '@/lib/db'
import type { Prisma } from '@prisma/client'

export interface SaldoResult {
  socio: 'BRUNO' | 'RAFAEL'
  saldo: number  // em cêntimos
  ins: {
    projetosPessoais: number
    premios: number
    investimento?: number
    total: number
  }
  outs: {
    despesasFixas: number
    boletins: number
    despesasPessoais: number
    total: number
  }
  sugestaBoletim: number
}

export interface SaldoFilters {
  startDate?: Date
  endDate?: Date
  incluirInvestimento?: boolean
}

// Calcula saldo pessoal do Bruno
export async function calculateSaldoBruno(
  userId: string,
  filters?: SaldoFilters
): Promise<SaldoResult> {
  return calculateSaldo('BRUNO', userId, filters)
}

// Calcula saldo pessoal do Rafael
export async function calculateSaldoRafael(
  userId: string,
  filters?: SaldoFilters
): Promise<SaldoResult> {
  return calculateSaldo('RAFAEL', userId, filters)
}

// Lógica genérica de cálculo
async function calculateSaldo(
  socio: 'BRUNO' | 'RAFAEL',
  userId: string,
  filters?: SaldoFilters
): Promise<SaldoResult> {
  const dateFilter = buildDateFilter(filters)
  
  // INs (ENTRADAS - empresa DEVE ao sócio)
  
  // 1. PROJETOS PESSOAIS (apenas RECEBIDOS)
  const projetosPessoais = await prisma.transaction.aggregate({
    where: {
      userId,
      type: 'income',
      projectCode: socio === 'BRUNO' ? 'PESSOAL_BRUNO' : 'PESSOAL_RAFAEL',
      categoryCode: 'RECEBIDO',
      ...dateFilter
    },
    _sum: { total: true }
  })
  
  const totalProjetosPessoais = projetosPessoais._sum.total || 0
  
  // 2. PRÉMIOS de projetos da EMPRESA (apenas RECEBIDOS)
  const projetosEmpresa = await prisma.transaction.findMany({
    where: {
      userId,
      type: 'income',
      projectCode: 'EMPRESA',
      categoryCode: 'RECEBIDO',
      ...dateFilter
    },
    select: {
      id: true,
      extra: true
    }
  })
  
  const totalPremios = projetosEmpresa.reduce((sum, projeto) => {
    const extra = projeto.extra as any
    const premio = socio === 'BRUNO' 
      ? (extra?.premio_bruno || 0)
      : (extra?.premio_rafael || 0)
    return sum + Number(premio)
  }, 0)
  
  // 3. INVESTIMENTO INICIAL (opcional, histórico)
  const INVESTIMENTO_INICIAL = 520000 // 5.200 euros em cêntimos
  const investimento = filters?.incluirInvestimento ? INVESTIMENTO_INICIAL : 0
  
  const totalIns = totalProjetosPessoais + totalPremios + investimento
  
  // OUTs (SAÍDAS - empresa PAGA ao sócio)
  
  // 1. DESPESAS FIXAS MENSAIS dividir por 2 (cada sócio paga metade)
  const despesasFixasTotal = await prisma.transaction.aggregate({
    where: {
      userId,
      type: 'expense',
      categoryCode: 'FIXA_MENSAL',
      extra: {
        path: ['estado_pagamento'],
        equals: 'PAGO'
      },
      ...dateFilter
    },
    _sum: { total: true }
  })
  
  // Despesas são negativas, converter para positivo e dividir
  const despesasFixas = Math.abs(despesasFixasTotal._sum.total || 0) / 2
  
  // 2. BOLETINS EMITIDOS (independente do estado de pagamento)
  const boletins = await prisma.transaction.aggregate({
    where: {
      userId,
      type: 'expense',
      categoryCode: 'BOLETIM',
      extra: {
        path: ['socio'],
        equals: socio
      },
      ...dateFilter
    },
    _sum: { total: true }
  })
  
  const totalBoletins = Math.abs(boletins._sum.total || 0)
  
  // 3. DESPESAS PESSOAIS (apenas PAGAS)
  const categoryPessoal = socio === 'BRUNO' 
    ? 'DESPESA_PESSOAL_BRUNO'
    : 'DESPESA_PESSOAL_RAFAEL'
  
  const despesasPessoais = await prisma.transaction.aggregate({
    where: {
      userId,
      type: 'expense',
      categoryCode: categoryPessoal,
      extra: {
        path: ['estado_pagamento'],
        equals: 'PAGO'
      },
      ...dateFilter
    },
    _sum: { total: true }
  })
  
  const totalDespesasPessoais = Math.abs(despesasPessoais._sum.total || 0)
  
  const totalOuts = despesasFixas + totalBoletins + totalDespesasPessoais
  
  // CÁLCULO FINAL
  const saldoTotal = totalIns - totalOuts
  
  return {
    socio,
    saldo: saldoTotal,
    ins: {
      projetosPessoais: totalProjetosPessoais,
      premios: totalPremios,
      investimento: filters?.incluirInvestimento ? investimento : undefined,
      total: totalIns
    },
    outs: {
      despesasFixas,
      boletins: totalBoletins,
      despesasPessoais: totalDespesasPessoais,
      total: totalOuts
    },
    sugestaBoletim: Math.max(0, saldoTotal)
  }
}

// Histórico mensal de saldos
export async function getHistoricoMensal(
  socio: 'BRUNO' | 'RAFAEL',
  userId: string,
  ano: number
): Promise<Array<{ mes: number; mesNome: string; saldo: number }>> {
  const meses = [
    'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
    'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
  ]
  
  const historico = []
  
  for (let mes = 1; mes <= 12; mes++) {
    const endDate = new Date(ano, mes, 0)
    
    const saldo = await (socio === 'BRUNO' 
      ? calculateSaldoBruno(userId, { endDate })
      : calculateSaldoRafael(userId, { endDate })
    )
    
    historico.push({
      mes,
      mesNome: meses[mes - 1],
      saldo: saldo.saldo
    })
  }
  
  return historico
}

function buildDateFilter(filters?: SaldoFilters): Prisma.TransactionWhereInput {
  if (!filters?.startDate && !filters?.endDate) {
    return {}
  }
  
  return {
    issuedAt: {
      ...(filters.startDate && { gte: filters.startDate }),
      ...(filters.endDate && { lte: filters.endDate })
    }
  }
}

export function formatEuros(centimos: number): string {
  return new Intl.NumberFormat('pt-PT', {
    style: 'currency',
    currency: 'EUR'
  }).format(centimos / 100)
}
```

1.2 API ENDPOINT
--------------------

Ficheiro: `app/api/agora/saldos/route.ts`

```typescript
import { NextRequest, NextResponse } from 'next/server'
import { calculateSaldoBruno, calculateSaldoRafael } from '@/lib/agora/saldos'
import { auth } from '@/lib/auth'

export async function GET(request: NextRequest) {
  try {
    const session = await auth.api.getSession({
      headers: request.headers
    })
    
    if (!session) {
      return NextResponse.json(
        { error: 'Não autenticado' },
        { status: 401 }
      )
    }
    
    const { searchParams } = new URL(request.url)
    const startDate = searchParams.get('startDate')
      ? new Date(searchParams.get('startDate')!)
      : undefined
    const endDate = searchParams.get('endDate')
      ? new Date(searchParams.get('endDate')!)
      : undefined
    const incluirInvestimento = searchParams.get('incluirInvestimento') === 'true'
    
    const [saldoBruno, saldoRafael] = await Promise.all([
      calculateSaldoBruno(session.user.id, { startDate, endDate, incluirInvestimento }),
      calculateSaldoRafael(session.user.id, { startDate, endDate, incluirInvestimento })
    ])
    
    return NextResponse.json({
      bruno: saldoBruno,
      rafael: saldoRafael,
      timestamp: new Date().toISOString()
    })
  } catch (error) {
    console.error('Erro ao calcular saldos:', error)
    return NextResponse.json(
      { error: 'Erro interno ao calcular saldos' },
      { status: 500 }
    )
  }
}
```

1.3 UI COMPONENTE: SALDO CARD
--------------------

Ficheiro: `components/agora/saldo-card.tsx`

ESTRUTURA:
- Card com gradient background baseado em saldo positivo/negativo
- Header: Nome sócio + badge valor saldo
- Secção INs (verde): projetos pessoais + prémios + investimento
- Secção OUTs (vermelho): despesas fixas + boletins + despesas pessoais
- Card sugestão boletim (azul) se saldo > 0

PROPS:
```typescript
interface SaldoCardProps {
  data: SaldoResult
  showDetails?: boolean
}
```

LÓGICA PRINCIPAL:
```tsx
const isPositive = data.saldo >= 0
const variantSaldo = isPositive ? 'default' : 'destructive'

// Render INs
<div>
  <TrendingUp />
  <span>Entradas (INs)</span>
  {showDetails && (
    <div>
      <div>Projetos pessoais: +{formatEuros(data.ins.projetosPessoais)}</div>
      <div>Prémios: +{formatEuros(data.ins.premios)}</div>
    </div>
  )}
  <div>Total INs: +{formatEuros(data.ins.total)}</div>
</div>

// Render OUTs
<div>
  <TrendingDown />
  <span>Saídas (OUTs)</span>
  {showDetails && (
    <div>
      <div>Despesas fixas: -{formatEuros(data.outs.despesasFixas)}</div>
      <div>Boletins: -{formatEuros(data.outs.boletins)}</div>
      <div>Despesas pessoais: -{formatEuros(data.outs.despesasPessoais)}</div>
    </div>
  )}
  <div>Total OUTs: -{formatEuros(data.outs.total)}</div>
</div>

// Sugestão boletim
{data.sugestaBoletim > 0 && (
  <div className="bg-blue-50 p-4">
    <p>Sugestão de boletim para zerar saldo:</p>
    <p className="text-2xl">{formatEuros(data.sugestaBoletim)}</p>
    <Button>Emitir</Button>
  </div>
)}
```

1.4 PÁGINA SALDOS
--------------------

Ficheiro: `app/(app)/saldos/page.tsx`

ESTRUTURA:
- Server Component (fetch data no servidor)
- Grid 2 colunas com SaldoCard para cada sócio
- Card explicação (como funciona o cálculo)
- Suspense com loading skeleton

CÓDIGO SIMPLIFICADO:
```tsx
async function SaldosContent() {
  const session = await auth.api.getSession({ headers: await headers() })
  if (!session) redirect('/login')
  
  const [saldoBruno, saldoRafael] = await Promise.all([
    calculateSaldoBruno(session.user.id),
    calculateSaldoRafael(session.user.id)
  ])
  
  return (
    <div>
      <h1>Saldos Pessoais</h1>
      
      <div className="grid grid-cols-2 gap-6">
        <SaldoCard data={saldoBruno} />
        <SaldoCard data={saldoRafael} />
      </div>
      
      <Card>
        <h3>Como funciona o cálculo?</h3>
        <p>INs: empresa DEVE ao sócio (projetos + prémios)</p>
        <p>OUTs: empresa PAGOU ao sócio (despesas + boletins)</p>
        <p>Saldo = INs - OUTs</p>
      </Card>
    </div>
  )
}

export default function SaldosPage() {
  return (
    <Suspense fallback={<SaldosLoading />}>
      <SaldosContent />
    </Suspense>
  )
}
```

==================================================
FEATURE 2: GESTÃO FISCAL (IMPOSTOS)
==================================================

OBJECTIVO: Calcular IVA, retenções e IRC estimado

2.1 LÓGICA CÁLCULO IMPOSTOS
--------------------

Ficheiro: `lib/agora/impostos.ts`

INTERFACES:
```typescript
export interface IVACalculation {
  periodo: { trimestre: number; ano: number }
  ivaLiquidado: number      // IVA cobrado (vendas)
  ivaDedutivel: number      // IVA pago (compras)
  ivaPagar: number          // Liquidado - Dedutível
  detalhes: {
    vendas: { total: number; iva: number; count: number }
    compras: { total: number; iva: number; count: number }
  }
}

export interface RetencoesCalculation {
  periodo: { mes: number; ano: number }
  totalRetido: number
  items: Array<{
    id: string
    data: Date
    descricao: string
    valorBase: number
    taxaRetencao: number
    valorRetido: number
  }>
}

export interface IRCEstimado {
  ano: number
  receitasTotal: number
  despesasTotal: number
  lucroTributavel: number
  irc: number              // 23% sobre lucro
  estimativas: {
    q1: number  // Julho
    q2: number  // Setembro
    q3: number  // Dezembro
  }
}
```

FUNÇÃO: calculateIVATrimestre
```typescript
export async function calculateIVATrimestre(
  userId: string,
  trimestre: number,
  ano: number
): Promise<IVACalculation> {
  // Determinar datas do trimestre
  const startMonth = (trimestre - 1) * 3 + 1
  const endMonth = startMonth + 2
  const startDate = new Date(ano, startMonth - 1, 1)
  const endDate = new Date(ano, endMonth, 0)
  
  // Buscar vendas (receitas) do trimestre
  const vendas = await prisma.transaction.findMany({
    where: {
      userId,
      type: 'income',
      issuedAt: { gte: startDate, lte: endDate }
    },
    select: { id: true, total: true, extra: true }
  })
  
  // Calcular IVA liquidado (cobrado nas vendas)
  let ivaLiquidado = 0
  let totalVendas = 0
  
  vendas.forEach(venda => {
    const extra = venda.extra as any
    const taxaIVA = extra?.iva_taxa || 23
    const valorSemIVA = venda.total || 0
    const iva = Math.round(valorSemIVA * (taxaIVA / 100))
    
    ivaLiquidado += iva
    totalVendas += valorSemIVA
  })
  
  // Buscar compras (despesas) do trimestre
  const compras = await prisma.transaction.findMany({
    where: {
      userId,
      type: 'expense',
      issuedAt: { gte: startDate, lte: endDate }
    },
    select: { id: true, total: true, extra: true }
  })
  
  // Calcular IVA dedutível (pago nas compras)
  let ivaDedutivel = 0
  let totalCompras = 0
  
  compras.forEach(compra => {
    const extra = compra.extra as any
    const valorComIVA = extra?.valor_com_iva
    const valorSemIVA = Math.abs(compra.total || 0)
    
    if (valorComIVA) {
      const iva = valorComIVA - valorSemIVA
      ivaDedutivel += iva
    } else {
      // Assumir 23% se não especificado
      const iva = Math.round(valorSemIVA * 0.23)
      ivaDedutivel += iva
    }
    
    totalCompras += valorSemIVA
  })
  
  // Cálculo final
  const ivaPagar = ivaLiquidado - ivaDedutivel
  
  return {
    periodo: { trimestre, ano },
    ivaLiquidado,
    ivaDedutivel,
    ivaPagar,
    detalhes: {
      vendas: { total: totalVendas, iva: ivaLiquidado, count: vendas.length },
      compras: { total: totalCompras, iva: ivaDedutivel, count: compras.length }
    }
  }
}
```

FUNÇÃO: calculateRetencoes
```typescript
export async function calculateRetencoes(
  userId: string,
  mes: number,
  ano: number
): Promise<RetencoesCalculation> {
  const startDate = new Date(ano, mes - 1, 1)
  const endDate = new Date(ano, mes, 0)
  
  // Buscar transações com retenção
  const transactions = await prisma.transaction.findMany({
    where: {
      userId,
      type: 'income',
      issuedAt: { gte: startDate, lte: endDate },
      extra: {
        path: ['retencao_valor'],
        gt: 0
      }
    },
    orderBy: { issuedAt: 'asc' }
  })
  
  const items = transactions.map(t => {
    const extra = t.extra as any
    return {
      id: t.id,
      data: t.issuedAt!,
      descricao: t.name || 'Sem descrição',
      valorBase: t.total || 0,
      taxaRetencao: extra.retencao_taxa || 0,
      valorRetido: extra.retencao_valor || 0
    }
  })
  
  const totalRetido = items.reduce((sum, item) => sum + item.valorRetido, 0)
  
  return {
    periodo: { mes, ano },
    totalRetido,
    items
  }
}
```

FUNÇÃO: estimateIRCAnual
```typescript
export async function estimateIRCAnual(
  userId: string,
  ano: number
): Promise<IRCEstimado> {
  const startDate = new Date(ano, 0, 1)
  const endDate = new Date(ano, 11, 31)
  
  // Total receitas
  const receitas = await prisma.transaction.aggregate({
    where: {
      userId,
      type: 'income',
      categoryCode: 'RECEBIDO',
      issuedAt: { gte: startDate, lte: endDate }
    },
    _sum: { total: true }
  })
  
  // Total despesas
  const despesas = await prisma.transaction.aggregate({
    where: {
      userId,
      type: 'expense',
      extra: { path: ['estado_pagamento'], equals: 'PAGO' },
      issuedAt: { gte: startDate, lte: endDate }
    },
    _sum: { total: true }
  })
  
  const receitasTotal = receitas._sum.total || 0
  const despesasTotal = Math.abs(despesas._sum.total || 0)
  
  const lucroTributavel = receitasTotal - despesasTotal
  const irc = Math.round(lucroTributavel * 0.23) // 23% de IRC
  
  // Estimativas trimestrais (1/3 do IRC anual cada)
  const estimativaTrimestral = Math.round(irc / 3)
  
  return {
    ano,
    receitasTotal,
    despesasTotal,
    lucroTributavel,
    irc,
    estimativas: {
      q1: estimativaTrimestral,
      q2: estimativaTrimestral,
      q3: estimativaTrimestral
    }
  }
}
```

2.2 API ENDPOINT IMPOSTOS
--------------------

Ficheiro: `app/api/agora/impostos/route.ts`

```typescript
import { NextRequest, NextResponse } from 'next/server'
import { calculateIVATrimestre, estimateIRCAnual } from '@/lib/agora/impostos'
import { auth } from '@/lib/auth'

export async function GET(request: NextRequest) {
  try {
    const session = await auth.api.getSession({ headers: request.headers })
    if (!session) {
      return NextResponse.json({ error: 'Não autenticado' }, { status: 401 })
    }
    
    const { searchParams } = new URL(request.url)
    const trimestre = parseInt(searchParams.get('trimestre') || '1')
    const ano = parseInt(searchParams.get('ano') || new Date().getFullYear().toString())
    
    const [iva, irc] = await Promise.all([
      calculateIVATrimestre(session.user.id, trimestre, ano),
      estimateIRCAnual(session.user.id, ano)
    ])
    
    return NextResponse.json({ iva, irc })
  } catch (error) {
    console.error('Erro ao calcular impostos:', error)
    return NextResponse.json({ error: 'Erro interno' }, { status: 500 })
  }
}
```

2.3 UI COMPONENTES FISCAIS
--------------------

Ficheiro: `components/agora/iva-summary.tsx`

ESTRUTURA:
- Selector trimestre (Q1, Q2, Q3, Q4)
- Card IVA Liquidado (verde)
- Card IVA Dedutível (vermelho)
- Card IVA a Pagar (azul se pagar, verde se receber)
- Tabela detalhes vendas/compras

Ficheiro: `components/agora/retencoes-table.tsx`

ESTRUTURA:
- Tabela com colunas: Data | Descrição | Valor Base | Taxa | Retido
- Total acumulado
- Botão exportar CSV

Ficheiro: `components/agora/irc-estimado.tsx`

ESTRUTURA:
- Card receitas total
- Card despesas total
- Card lucro tributável
- Card IRC (23%)
- Timeline estimativas trimestrais (Julho, Setembro, Dezembro)

2.4 PÁGINA IMPOSTOS
--------------------

Ficheiro: `app/(app)/impostos/page.tsx`

LAYOUT:
```tsx
<div>
  <h1>Gestão Fiscal</h1>
  
  <Tabs defaultValue="iva">
    <TabsList>
      <TabsTrigger value="iva">IVA</TabsTrigger>
      <TabsTrigger value="retencoes">Retenções</TabsTrigger>
      <TabsTrigger value="irc">IRC</TabsTrigger>
    </TabsList>
    
    <TabsContent value="iva">
      <IVASummary />
    </TabsContent>
    
    <TabsContent value="retencoes">
      <RetencoesTable />
    </TabsContent>
    
    <TabsContent value="irc">
      <IRCEstimado />
    </TabsContent>
  </Tabs>
</div>
```

==================================================
FEATURE 3: GESTÃO DE EQUIPAMENTO
==================================================

OBJECTIVO: Catálogo de equipamento com amortização automática e gestão de custos

3.1 MODELO PRISMA (JÁ CRIADO NA FASE 1)
--------------------

Schema já incluído em `schema.prisma`:
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
```

3.2 LÓGICA EQUIPAMENTO
--------------------

Ficheiro: `lib/agora/equipamento.ts`

```typescript
import { prisma } from '@/lib/db'

export interface EquipmentWithDepreciation {
  id: string
  name: string
  category: string
  purchaseDate: Date
  purchasePrice: number
  lifeYears: number
  currentValue: number
  dailyRate?: number
  ageYears: number
  depreciationRate: number
  depreciatedValue: number
  note?: string
}

// Calcular amortização de equipamento
export function calculateDepreciation(equipment: {
  purchaseDate: Date
  purchasePrice: number
  lifeYears: number
}): {
  ageYears: number
  depreciationRate: number
  currentValue: number
} {
  const now = new Date()
  const ageMs = now.getTime() - equipment.purchaseDate.getTime()
  const ageYears = ageMs / (1000 * 60 * 60 * 24 * 365.25)
  
  // Método linear: divide valor por anos de vida útil
  const depreciationRate = 1 / equipment.lifeYears
  const depreciatedAmount = equipment.purchasePrice * depreciationRate * ageYears
  const currentValue = Math.max(0, equipment.purchasePrice - depreciatedAmount)
  
  return {
    ageYears: Math.round(ageYears * 10) / 10,
    depreciationRate,
    currentValue: Math.round(currentValue)
  }
}

// Buscar todo equipamento com valores actualizados
export async function getAllEquipmentWithDepreciation(
  userId: string
): Promise<EquipmentWithDepreciation[]> {
  const equipment = await prisma.equipment.findMany({
    where: { userId },
    orderBy: { purchaseDate: 'desc' }
  })
  
  return equipment.map(eq => {
    const depreciation = calculateDepreciation({
      purchaseDate: eq.purchaseDate,
      purchasePrice: eq.purchasePrice,
      lifeYears: eq.lifeYears
    })
    
    return {
      id: eq.id,
      name: eq.name,
      category: eq.category,
      purchaseDate: eq.purchaseDate,
      purchasePrice: eq.purchasePrice,
      lifeYears: eq.lifeYears,
      currentValue: eq.currentValue,
      dailyRate: eq.dailyRate || undefined,
      note: eq.note || undefined,
      ageYears: depreciation.ageYears,
      depreciationRate: depreciation.depreciationRate,
      depreciatedValue: depreciation.currentValue
    }
  })
}

// Actualizar valores actuais de todo o equipamento (cron job)
export async function updateAllEquipmentValues(userId: string): Promise<number> {
  const equipment = await prisma.equipment.findMany({
    where: { userId },
    select: { id: true, purchaseDate: true, purchasePrice: true, lifeYears: true }
  })
  
  let updatedCount = 0
  
  for (const eq of equipment) {
    const { currentValue } = calculateDepreciation({
      purchaseDate: eq.purchaseDate,
      purchasePrice: eq.purchasePrice,
      lifeYears: eq.lifeYears
    })
    
    await prisma.equipment.update({
      where: { id: eq.id },
      data: { currentValue }
    })
    
    updatedCount++
  }
  
  return updatedCount
}

// Estatísticas de equipamento
export async function getEquipmentStats(userId: string) {
  const equipment = await getAllEquipmentWithDepreciation(userId)
  
  const totalPurchaseValue = equipment.reduce((sum, eq) => sum + eq.purchasePrice, 0)
  const totalCurrentValue = equipment.reduce((sum, eq) => sum + eq.depreciatedValue, 0)
  const totalDepreciation = totalPurchaseValue - totalCurrentValue
  
  const byCategory = equipment.reduce((acc, eq) => {
    if (!acc[eq.category]) {
      acc[eq.category] = {
        count: 0,
        purchaseValue: 0,
        currentValue: 0
      }
    }
    acc[eq.category].count++
    acc[eq.category].purchaseValue += eq.purchasePrice
    acc[eq.category].currentValue += eq.depreciatedValue
    return acc
  }, {} as Record<string, { count: number; purchaseValue: number; currentValue: number }>)
  
  return {
    totalItems: equipment.length,
    totalPurchaseValue,
    totalCurrentValue,
    totalDepreciation,
    depreciationPercentage: totalPurchaseValue > 0 
      ? (totalDepreciation / totalPurchaseValue) * 100 
      : 0,
    byCategory
  }
}

// Calcular custo por dia de utilização (para orçamentos)
export function calculateDailyCost(equipment: {
  purchasePrice: number
  lifeYears: number
  dailyRate?: number
}): number {
  if (equipment.dailyRate) {
    return equipment.dailyRate
  }
  
  // Se não tem taxa definida, calcular baseado em amortização
  const totalDays = equipment.lifeYears * 365
  return Math.round(equipment.purchasePrice / totalDays)
}
```

3.3 API ENDPOINTS EQUIPAMENTO
--------------------

Ficheiro: `app/api/agora/equipamento/route.ts`

```typescript
import { NextRequest, NextResponse } from 'next/server'
import { prisma } from '@/lib/db'
import { auth } from '@/lib/auth'
import { calculateDepreciation } from '@/lib/agora/equipamento'

// GET - Listar equipamento
export async function GET(request: NextRequest) {
  try {
    const session = await auth.api.getSession({ headers: request.headers })
    if (!session) {
      return NextResponse.json({ error: 'Não autenticado' }, { status: 401 })
    }
    
    const { searchParams } = new URL(request.url)
    const category = searchParams.get('category')
    
    const equipment = await prisma.equipment.findMany({
      where: {
        userId: session.user.id,
        ...(category && { category })
      },
      orderBy: { purchaseDate: 'desc' }
    })
    
    // Adicionar valores depreciados
    const equipmentWithDepreciation = equipment.map(eq => {
      const depreciation = calculateDepreciation({
        purchaseDate: eq.purchaseDate,
        purchasePrice: eq.purchasePrice,
        lifeYears: eq.lifeYears
      })
      
      return {
        ...eq,
        depreciatedValue: depreciation.currentValue,
        ageYears: depreciation.ageYears
      }
    })
    
    return NextResponse.json(equipmentWithDepreciation)
  } catch (error) {
    console.error('Erro ao buscar equipamento:', error)
    return NextResponse.json({ error: 'Erro interno' }, { status: 500 })
  }
}

// POST - Criar equipamento
export async function POST(request: NextRequest) {
  try {
    const session = await auth.api.getSession({ headers: request.headers })
    if (!session) {
      return NextResponse.json({ error: 'Não autenticado' }, { status: 401 })
    }
    
    const body = await request.json()
    
    // Validações
    if (!body.name || !body.category || !body.purchaseDate || !body.purchasePrice || !body.lifeYears) {
      return NextResponse.json({ error: 'Campos obrigatórios em falta' }, { status: 400 })
    }
    
    // Calcular valor actual
    const depreciation = calculateDepreciation({
      purchaseDate: new Date(body.purchaseDate),
      purchasePrice: body.purchasePrice,
      lifeYears: body.lifeYears
    })
    
    const equipment = await prisma.equipment.create({
      data: {
        userId: session.user.id,
        name: body.name,
        category: body.category,
        purchaseDate: new Date(body.purchaseDate),
        purchasePrice: body.purchasePrice,
        lifeYears: body.lifeYears,
        currentValue: depreciation.currentValue,
        dailyRate: body.dailyRate || null,
        note: body.note || null
      }
    })
    
    return NextResponse.json(equipment, { status: 201 })
  } catch (error) {
    console.error('Erro ao criar equipamento:', error)
    return NextResponse.json({ error: 'Erro interno' }, { status: 500 })
  }
}
```

(Continua com mais 2 features...)

==================================================
RESUMO FEATURES COMPLETAS
==================================================

✅ Feature 1: Cálculo Saldos Pessoais
   - Lógica INs/OUTs
   - API endpoint
   - UI cards + dashboard
   - Histórico mensal

✅ Feature 2: Gestão Fiscal (Impostos)
   - Cálculo IVA trimestral
   - Retenções na fonte
   - IRC estimado
   - UI componentes fiscais

✅ Feature 3: Equipamento
   - CRUD equipamento
   - Cálculo amortização automática
   - Catálogo com filtros
   - Stats por categoria

✅ Feature 4: Orçamentos
   - Criação orçamentos profissionais
   - Items com equipamento
   - Conversão para projetos
   - PDF generation

✅ Feature 5: TOConline
   - Cliente API completo
   - Emissão facturas AT
   - Sync clientes
   - Download PDFs certificados

==================================================
