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

Ficheiro: lib/agora/saldos.ts

---
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
---

1.2 API ENDPOINT
--------------------

Ficheiro: app/api/agora/saldos/route.ts

---
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
---

1.3 UI COMPONENTE: SALDO CARD
--------------------

Ficheiro: components/agora/saldo-card.tsx

ESTRUTURA:
- Card com gradient background baseado em saldo positivo/negativo
- Header: Nome sócio + badge valor saldo
- Secção INs (verde): projetos pessoais + prémios + investimento
- Secção OUTs (vermelho): despesas fixas + boletins + despesas pessoais
- Card sugestão boletim (azul) se saldo > 0

PROPS:
---
interface SaldoCardProps {
  data: SaldoResult
  showDetails?: boolean
}
---

LÓGICA PRINCIPAL:
---
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
---

1.4 PÁGINA SALDOS
--------------------

Ficheiro: app/(app)/saldos/page.tsx

ESTRUTURA:
- Server Component (fetch data no servidor)
- Grid 2 colunas com SaldoCard para cada sócio
- Card explicação (como funciona o cálculo)
- Suspense com loading skeleton

CÓDIGO SIMPLIFICADO:
---
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
---

==================================================
FEATURE 2: GESTÃO FISCAL (IMPOSTOS)
==================================================

OBJECTIVO: Calcular IVA, retenções e IRC estimado

2.1 LÓGICA CÁLCULO IMPOSTOS
--------------------

Ficheiro: lib/agora/impostos.ts

INTERFACES:
---
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
---

FUNÇÃO: calculateIVATrimestre
---
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
---

FUNÇÃO: calculateRetencoes
---
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
---

FUNÇÃO: estimateIRCAnual
---
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
---

2.2 API ENDPOINT IMPOSTOS
--------------------

Ficheiro: app/api/agora/impostos/route.ts

---
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
---

2.3 UI COMPONENTES FISCAIS
--------------------

Ficheiro: components/agora/iva-summary.tsx

ESTRUTURA:
- Selector trimestre (Q1, Q2, Q3, Q4)
- Card IVA Liquidado (verde)
- Card IVA Dedutível (vermelho)
- Card IVA a Pagar (azul se pagar, verde se receber)
- Tabela detalhes vendas/compras

Ficheiro: components/agora/retencoes-table.tsx

ESTRUTURA:
- Tabela com colunas: Data | Descrição | Valor Base | Taxa | Retido
- Total acumulado
- Botão exportar CSV

Ficheiro: components/agora/irc-estimado.tsx

ESTRUTURA:
- Card receitas total
- Card despesas total
- Card lucro tributável
- Card IRC (23%)
- Timeline estimativas trimestrais (Julho, Setembro, Dezembro)

2.4 PÁGINA IMPOSTOS
--------------------

Ficheiro: app/(app)/impostos/page.tsx

LAYOUT:
---
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

==================================================
FEATURE 3: GESTÃO DE EQUIPAMENTO
==================================================

OBJECTIVO: Catálogo de equipamento com amortização automática e gestão de custos

3.1 MODELO PRISMA (JÁ CRIADO NA FASE 1)
--------------------

Schema já incluído em schema.prisma:
---
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
---

3.2 LÓGICA EQUIPAMENTO
--------------------

Ficheiro: lib/agora/equipamento.ts

---
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
---

3.3 API ENDPOINTS EQUIPAMENTO
--------------------

Ficheiro: app/api/agora/equipamento/route.ts

---
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
---

Ficheiro: app/api/agora/equipamento/[id]/route.ts

---
import { NextRequest, NextResponse } from 'next/server'
import { prisma } from '@/lib/db'
import { auth } from '@/lib/auth'
import { calculateDepreciation } from '@/lib/agora/equipamento'

// GET - Buscar equipamento específico
export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const session = await auth.api.getSession({ headers: request.headers })
    if (!session) {
      return NextResponse.json({ error: 'Não autenticado' }, { status: 401 })
    }
    
    const equipment = await prisma.equipment.findFirst({
      where: {
        id: params.id,
        userId: session.user.id
      }
    })
    
    if (!equipment) {
      return NextResponse.json({ error: 'Equipamento não encontrado' }, { status: 404 })
    }
    
    return NextResponse.json(equipment)
  } catch (error) {
    console.error('Erro ao buscar equipamento:', error)
    return NextResponse.json({ error: 'Erro interno' }, { status: 500 })
  }
}

// PUT - Actualizar equipamento
export async function PUT(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const session = await auth.api.getSession({ headers: request.headers })
    if (!session) {
      return NextResponse.json({ error: 'Não autenticado' }, { status: 401 })
    }
    
    const body = await request.json()
    
    // Recalcular valor actual se mudaram parâmetros
    let currentValue = body.currentValue
    if (body.purchaseDate || body.purchasePrice || body.lifeYears) {
      const existing = await prisma.equipment.findFirst({
        where: { id: params.id, userId: session.user.id }
      })
      
      if (!existing) {
        return NextResponse.json({ error: 'Equipamento não encontrado' }, { status: 404 })
      }
      
      const depreciation = calculateDepreciation({
        purchaseDate: body.purchaseDate ? new Date(body.purchaseDate) : existing.purchaseDate,
        purchasePrice: body.purchasePrice ?? existing.purchasePrice,
        lifeYears: body.lifeYears ?? existing.lifeYears
      })
      
      currentValue = depreciation.currentValue
    }
    
    const equipment = await prisma.equipment.update({
      where: { id: params.id },
      data: {
        ...(body.name && { name: body.name }),
        ...(body.category && { category: body.category }),
        ...(body.purchaseDate && { purchaseDate: new Date(body.purchaseDate) }),
        ...(body.purchasePrice !== undefined && { purchasePrice: body.purchasePrice }),
        ...(body.lifeYears !== undefined && { lifeYears: body.lifeYears }),
        ...(currentValue !== undefined && { currentValue }),
        ...(body.dailyRate !== undefined && { dailyRate: body.dailyRate }),
        ...(body.note !== undefined && { note: body.note })
      }
    })
    
    return NextResponse.json(equipment)
  } catch (error) {
    console.error('Erro ao actualizar equipamento:', error)
    return NextResponse.json({ error: 'Erro interno' }, { status: 500 })
  }
}

// DELETE - Remover equipamento
export async function DELETE(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const session = await auth.api.getSession({ headers: request.headers })
    if (!session) {
      return NextResponse.json({ error: 'Não autenticado' }, { status: 401 })
    }
    
    await prisma.equipment.delete({
      where: {
        id: params.id,
        userId: session.user.id
      }
    })
    
    return NextResponse.json({ success: true })
  } catch (error) {
    console.error('Erro ao remover equipamento:', error)
    return NextResponse.json({ error: 'Erro interno' }, { status: 500 })
  }
}
---

3.4 UI COMPONENTES EQUIPAMENTO
--------------------

Ficheiro: components/agora/equipment-table.tsx

ESTRUTURA:
- Tabela com colunas: Nome | Categoria | Valor Compra | Valor Actual | Idade | Taxa/dia | Acções
- Badge estado baseado em idade:
  * Verde: < 2 anos (novo)
  * Amarelo: 2-5 anos (usado)
  * Vermelho: > 5 anos (antigo)
- Filtros: categoria, ordenação
- Acções: editar, remover

PROPS:
---
interface EquipmentTableProps {
  equipment: EquipmentWithDepreciation[]
  onEdit: (id: string) => void
  onDelete: (id: string) => void
}
---

Ficheiro: components/agora/equipment-form.tsx

CAMPOS:
- Nome (text, obrigatório)
- Categoria (select: Câmara, Drone, Iluminação, Áudio, Outro)
- Data de compra (date, obrigatório)
- Valor de compra (number, obrigatório, em euros)
- Vida útil (number, obrigatório, em anos, default: 5)
- Taxa diária aluguer (number, opcional, em euros)
- Notas (textarea, opcional)

VALIDAÇÕES:
- Valor compra > 0
- Vida útil entre 1 e 20 anos
- Data compra não pode ser futura

Ficheiro: components/agora/depreciation-chart.tsx

COMPONENTE:
- Gráfico linha mostrando depreciação ao longo do tempo
- Eixo X: anos
- Eixo Y: valor em euros
- Linha descendente do valor compra até 0
- Marcador valor actual

3.5 PÁGINAS EQUIPAMENTO
--------------------

Ficheiro: app/(app)/equipamento/page.tsx

LAYOUT:
---
<div>
  <div className="flex justify-between">
    <h1>Catálogo de Equipamento</h1>
    <Button onClick={() => router.push('/equipamento/novo')}>
      Adicionar Equipamento
    </Button>
  </div>
  
  <div className="grid grid-cols-3 gap-4 mb-6">
    <Card>
      <CardTitle>Total Items</CardTitle>
      <CardContent>{stats.totalItems}</CardContent>
    </Card>
    <Card>
      <CardTitle>Valor Compra</CardTitle>
      <CardContent>{formatEuros(stats.totalPurchaseValue)}</CardContent>
    </Card>
    <Card>
      <CardTitle>Valor Actual</CardTitle>
      <CardContent>{formatEuros(stats.totalCurrentValue)}</CardContent>
    </Card>
  </div>
  
  <EquipmentTable equipment={equipment} />
</div>
---

Ficheiro: app/(app)/equipamento/novo/page.tsx

ESTRUTURA:
- Form para criar novo equipamento
- Validação client-side com Zod
- Preview cálculo amortização em tempo real
- Botão guardar → POST /api/agora/equipamento

Ficheiro: app/(app)/equipamento/[id]/page.tsx

ESTRUTURA:
- Modo visualização/edição
- Detalhes completos do equipamento
- Gráfico depreciação
- Histórico de uso (se implementado)
- Botões: Editar, Remover

==================================================
FEATURE 4: SISTEMA DE ORÇAMENTOS
==================================================

OBJECTIVO: Criar orçamentos profissionais e converter em projetos facturáveis

4.1 MODELOS PRISMA (JÁ CRIADOS NA FASE 1)
--------------------

Schema já incluído:
---
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
  DRAFT        // Rascunho
  SENT         // Enviado ao cliente
  APPROVED     // Aprovado
  REJECTED     // Rejeitado
  CONVERTED    // Convertido em projeto
}
---

4.2 LÓGICA ORÇAMENTOS
--------------------

Ficheiro: lib/agora/orcamentos.ts

---
import { prisma } from '@/lib/db'
import { BudgetStatus } from '@prisma/client'

export interface BudgetWithItems {
  id: string
  numero: string
  description?: string
  clienteName?: string
  clienteNIF?: string
  clienteEmail?: string
  subtotal: number
  iva: number
  total: number
  status: BudgetStatus
  validUntil: Date
  items: Array<{
    id: string
    description: string
    quantity: number
    unitPrice: number
    total: number
    equipment?: {
      id: string
      name: string
    }
  }>
  note?: string
  createdAt: Date
}

// Gerar número de orçamento sequencial
export async function generateBudgetNumber(): Promise<string> {
  const lastBudget = await prisma.budget.findFirst({
    orderBy: { numero: 'desc' },
    select: { numero: true }
  })
  
  if (!lastBudget) {
    return 'ORC-0001'
  }
  
  // Extrair número e incrementar
  const match = lastBudget.numero.match(/ORC-(\d+)/)
  if (match) {
    const nextNum = parseInt(match[1]) + 1
    return `ORC-${nextNum.toString().padStart(4, '0')}`
  }
  
  return 'ORC-0001'
}

// Calcular totais de orçamento
export function calculateBudgetTotals(items: Array<{
  quantity: number
  unitPrice: number
}>, ivaRate: number = 23): {
  subtotal: number
  iva: number
  total: number
} {
  const subtotal = items.reduce((sum, item) => {
    return sum + (item.quantity * item.unitPrice)
  }, 0)
  
  const iva = Math.round(subtotal * (ivaRate / 100))
  const total = subtotal + iva
  
  return { subtotal, iva, total }
}

// Converter orçamento em projeto (Transaction)
export async function convertBudgetToProject(
  budgetId: string,
  userId: string
): Promise<{ transactionId: string; budgetId: string }> {
  // Buscar orçamento
  const budget = await prisma.budget.findFirst({
    where: {
      id: budgetId,
      userId
    },
    include: {
      items: {
        include: {
          equipment: true
        }
      }
    }
  })
  
  if (!budget) {
    throw new Error('Orçamento não encontrado')
  }
  
  if (budget.status !== BudgetStatus.APPROVED) {
    throw new Error('Apenas orçamentos aprovados podem ser convertidos')
  }
  
  if (budget.convertedToTransactionId) {
    throw new Error('Orçamento já foi convertido')
  }
  
  // Criar Transaction (projeto)
  const transaction = await prisma.transaction.create({
    data: {
      userId,
      type: 'income',
      name: budget.description || `Orçamento ${budget.numero}`,
      total: budget.total,
      projectCode: 'EMPRESA', // Ou determinar dinamicamente
      categoryCode: 'NAO_FATURADO',
      issuedAt: new Date(),
      extra: {
        tipo_origem: 'ORCAMENTO',
        orcamento_id: budget.id,
        orcamento_numero: budget.numero,
        cliente_nome: budget.clienteName,
        cliente_nif: budget.clienteNIF,
        cliente_email: budget.clienteEmail,
        items: budget.items.map(item => ({
          description: item.description,
          quantity: item.quantity,
          unitPrice: item.unitPrice,
          total: item.total,
          equipment: item.equipment ? {
            id: item.equipment.id,
            name: item.equipment.name
          } : null
        }))
      }
    }
  })
  
  // Actualizar budget
  await prisma.budget.update({
    where: { id: budgetId },
    data: {
      status: BudgetStatus.CONVERTED,
      convertedToTransactionId: transaction.id
    }
  })
  
  return {
    transactionId: transaction.id,
    budgetId: budget.id
  }
}

// Estatísticas de orçamentos
export async function getBudgetStats(userId: string, ano: number) {
  const startDate = new Date(ano, 0, 1)
  const endDate = new Date(ano, 11, 31)
  
  const budgets = await prisma.budget.findMany({
    where: {
      userId,
      createdAt: {
        gte: startDate,
        lte: endDate
      }
    },
    select: {
      status: true,
      total: true
    }
  })
  
  const stats = {
    total: budgets.length,
    draft: 0,
    sent: 0,
    approved: 0,
    rejected: 0,
    converted: 0,
    totalValue: 0,
    approvedValue: 0,
    conversionRate: 0
  }
  
  budgets.forEach(b => {
    stats.totalValue += b.total
    
    switch (b.status) {
      case BudgetStatus.DRAFT:
        stats.draft++
        break
      case BudgetStatus.SENT:
        stats.sent++
        break
      case BudgetStatus.APPROVED:
        stats.approved++
        stats.approvedValue += b.total
        break
      case BudgetStatus.REJECTED:
        stats.rejected++
        break
      case BudgetStatus.CONVERTED:
        stats.converted++
        stats.approvedValue += b.total
        break
    }
  })
  
  const totalSubmitted = stats.sent + stats.approved + stats.rejected + stats.converted
  if (totalSubmitted > 0) {
    stats.conversionRate = ((stats.approved + stats.converted) / totalSubmitted) * 100
  }
  
  return stats
}
---

4.3 API ENDPOINTS ORÇAMENTOS
--------------------

Ficheiro: app/api/agora/orcamentos/route.ts

---
import { NextRequest, NextResponse } from 'next/server'
import { prisma } from '@/lib/db'
import { auth } from '@/lib/auth'
import { generateBudgetNumber, calculateBudgetTotals } from '@/lib/agora/orcamentos'

// GET - Listar orçamentos
export async function GET(request: NextRequest) {
  try {
    const session = await auth.api.getSession({ headers: request.headers })
    if (!session) {
      return NextResponse.json({ error: 'Não autenticado' }, { status: 401 })
    }
    
    const { searchParams } = new URL(request.url)
    const status = searchParams.get('status')
    
    const budgets = await prisma.budget.findMany({
      where: {
        userId: session.user.id,
        ...(status && { status: status as any })
      },
      include: {
        items: {
          include: {
            equipment: true
          }
        }
      },
      orderBy: { createdAt: 'desc' }
    })
    
    return NextResponse.json(budgets)
  } catch (error) {
    console.error('Erro ao buscar orçamentos:', error)
    return NextResponse.json({ error: 'Erro interno' }, { status: 500 })
  }
}

// POST - Criar orçamento
export async function POST(request: NextRequest) {
  try {
    const session = await auth.api.getSession({ headers: request.headers })
    if (!session) {
      return NextResponse.json({ error: 'Não autenticado' }, { status: 401 })
    }
    
    const body = await request.json()
    
    // Validações
    if (!body.items || body.items.length === 0) {
      return NextResponse.json({ error: 'Orçamento precisa ter pelo menos 1 item' }, { status: 400 })
    }
    
    // Gerar número
    const numero = await generateBudgetNumber()
    
    // Calcular totais
    const { subtotal, iva, total } = calculateBudgetTotals(body.items)
    
    // Criar orçamento
    const budget = await prisma.budget.create({
      data: {
        userId: session.user.id,
        numero,
        description: body.description,
        clienteName: body.clienteName,
        clienteNIF: body.clienteNIF,
        clienteEmail: body.clienteEmail,
        subtotal,
        iva,
        total,
        validUntil: new Date(body.validUntil),
        note: body.note,
        items: {
          create: body.items.map((item: any) => ({
            description: item.description,
            quantity: item.quantity,
            unitPrice: item.unitPrice,
            total: item.quantity * item.unitPrice,
            equipmentId: item.equipmentId || null
          }))
        }
      },
      include: {
        items: true
      }
    })
    
    return NextResponse.json(budget, { status: 201 })
  } catch (error) {
    console.error('Erro ao criar orçamento:', error)
    return NextResponse.json({ error: 'Erro interno' }, { status: 500 })
  }
}
---

Ficheiro: app/api/agora/orcamentos/[id]/convert/route.ts

---
import { NextRequest, NextResponse } from 'next/server'
import { auth } from '@/lib/auth'
import { convertBudgetToProject } from '@/lib/agora/orcamentos'

export async function POST(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const session = await auth.api.getSession({ headers: request.headers })
    if (!session) {
      return NextResponse.json({ error: 'Não autenticado' }, { status: 401 })
    }
    
    const result = await convertBudgetToProject(params.id, session.user.id)
    
    return NextResponse.json(result)
  } catch (error: any) {
    console.error('Erro ao converter orçamento:', error)
    return NextResponse.json({ error: error.message }, { status: 400 })
  }
}
---

4.4 UI COMPONENTES ORÇAMENTOS
--------------------

Ficheiro: components/agora/budget-form.tsx

SECÇÕES:
1. Info Cliente
   - Nome (text)
   - NIF (text, validar formato PT)
   - Email (email)

2. Items do Orçamento
   - Lista dinâmica (add/remove)
   - Por item:
     * Descrição (text OU picker equipamento)
     * Quantidade (number)
     * Valor unitário (number)
     * Total (calculado automaticamente)

3. Totais
   - Subtotal (calculado)
   - IVA 23% (calculado)
   - Total (calculado)

4. Metadata
   - Validade (date, default: +30 dias)
   - Notas (textarea)

Ficheiro: components/agora/equipment-picker.tsx

ESTRUTURA:
- Modal/Dialog com lista de equipamento
- Filtro por categoria
- Ao seleccionar:
  * Preenche descrição com nome equipamento
  * Preenche valor unitário com dailyRate (se definido)
  * Permite editar depois

Ficheiro: components/agora/budget-status-badge.tsx

BADGES:
- DRAFT: cinzento
- SENT: azul
- APPROVED: verde
- REJECTED: vermelho
- CONVERTED: roxo

4.5 PÁGINAS ORÇAMENTOS
--------------------

Ficheiro: app/(app)/orcamentos/page.tsx

LAYOUT:
---
<div>
  <div className="flex justify-between">
    <h1>Orçamentos</h1>
    <Button href="/orcamentos/novo">Novo Orçamento</Button>
  </div>
  
  <Tabs defaultValue="all">
    <TabsList>
      <TabsTrigger value="all">Todos</TabsTrigger>
      <TabsTrigger value="DRAFT">Rascunhos</TabsTrigger>
      <TabsTrigger value="SENT">Enviados</TabsTrigger>
      <TabsTrigger value="APPROVED">Aprovados</TabsTrigger>
    </TabsList>
    
    <TabsContent value="all">
      <BudgetTable budgets={allBudgets} />
    </TabsContent>
  </Tabs>
</div>
---

Ficheiro: app/(app)/orcamentos/novo/page.tsx

ESTRUTURA:
- Form criação orçamento
- Validação Zod
- Preview em tempo real
- Botão "Guardar Rascunho" (status: DRAFT)
- Botão "Guardar e Enviar" (status: SENT, gera PDF)

Ficheiro: app/(app)/orcamentos/[id]/page.tsx

ESTRUTURA:
- Visualização completa orçamento
- Botões acção baseados em status:
  * DRAFT: Editar, Enviar, Remover
  * SENT: Marcar Aprovado/Rejeitado, Download PDF
  * APPROVED: Converter em Projeto, Download PDF
  * CONVERTED: Ver Projeto (link)

==================================================
FEATURE 5: INTEGRAÇÃO TOCONLINE
==================================================

OBJECTIVO: Emitir facturas certificadas AT automaticamente

5.1 CLIENTE TOCONLINE API
--------------------

Ficheiro: lib/agora/toconline/client.ts

---
export interface TOConlineConfig {
  apiKey: string
  baseUrl?: string
}

export interface TOConlineCustomer {
  id: string
  business_name: string
  email: string
  tax_registration_number: string
  address?: string
  postal_code?: string
  city?: string
  country: string
}

export interface TOConlineInvoice {
  id: string
  document_number: string
  document_type: 'FT' | 'FR' | 'FS'
  customer_id: string
  issue_date: string
  due_date?: string
  status: 'draft' | 'finalized' | 'sent' | 'paid'
  subtotal: number
  tax_total: number
  total: number
  pdf_url?: string
}

export class TOConlineClient {
  private apiKey: string
  private baseUrl: string
  
  constructor(config: TOConlineConfig) {
    this.apiKey = config.apiKey
    this.baseUrl = config.baseUrl || 'https://api.toconline.pt'
  }
  
  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}/v1${endpoint}`
    
    const response = await fetch(url, {
      ...options,
      headers: {
        'Authorization': `Bearer ${this.apiKey}`,
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        ...options.headers
      }
    })
    
    if (!response.ok) {
      const error = await response.json().catch(() => ({}))
      throw new TOConlineError(
        error.message || `API error: ${response.status}`,
        response.status,
        error
      )
    }
    
    return response.json()
  }
  
  // CUSTOMERS
  
  async getCustomer(email: string): Promise<TOConlineCustomer | null> {
    try {
      const data = await this.request<{ customers: TOConlineCustomer[] }>(
        `/customers?email=${encodeURIComponent(email)}`
      )
      return data.customers[0] || null
    } catch (error) {
      if ((error as any).status === 404) return null
      throw error
    }
  }
  
  async createCustomer(data: {
    business_name: string
    email: string
    tax_registration_number: string
    address?: string
    postal_code?: string
    city?: string
    country?: string
  }): Promise<TOConlineCustomer> {
    return this.request<TOConlineCustomer>('/customers', {
      method: 'POST',
      body: JSON.stringify({
        business_name: data.business_name,
        email: data.email,
        tax_registration_number: data.tax_registration_number,
        address: data.address || '',
        postal_code: data.postal_code || '',
        city: data.city || '',
        country: data.country || 'PT'
      })
    })
  }
  
  async getOrCreateCustomer(data: {
    business_name: string
    email: string
    tax_registration_number: string
  }): Promise<TOConlineCustomer> {
    const existing = await this.getCustomer(data.email)
    if (existing) return existing
    
    return this.createCustomer(data)
  }
  
  // INVOICES
  
  async createInvoice(data: {
    customer_id: string
    document_type?: 'FT' | 'FR' | 'FS'
    lines: Array<{
      description: string
      quantity: number
      unit_price: number
      vat_rate: string
    }>
    notes?: string
  }): Promise<TOConlineInvoice> {
    return this.request<TOConlineInvoice>('/invoices', {
      method: 'POST',
      body: JSON.stringify({
        document_type: data.document_type || 'FT',
        customer_id: data.customer_id,
        lines: data.lines,
        notes: data.notes
      })
    })
  }
  
  async finalizeInvoice(invoiceId: string): Promise<TOConlineInvoice> {
    return this.request<TOConlineInvoice>(`/invoices/${invoiceId}/finalize`, {
      method: 'POST'
    })
  }
  
  async getInvoice(invoiceId: string): Promise<TOConlineInvoice> {
    return this.request<TOConlineInvoice>(`/invoices/${invoiceId}`)
  }
  
  async downloadInvoicePDF(invoiceId: string): Promise<Blob> {
    const url = `${this.baseUrl}/v1/invoices/${invoiceId}/pdf`
    
    const response = await fetch(url, {
      headers: {
        'Authorization': `Bearer ${this.apiKey}`
      }
    })
    
    if (!response.ok) {
      throw new Error(`Failed to download PDF: ${response.status}`)
    }
    
    return response.blob()
  }
}

export class TOConlineError extends Error {
  constructor(
    message: string,
    public status: number,
    public data?: any
  ) {
    super(message)
    this.name = 'TOConlineError'
  }
}
---

5.2 INTEGRAÇÃO COM TRANSACTIONS
--------------------

Ficheiro: lib/agora/toconline/invoices.ts

---
import { TOConlineClient } from './client'
import { prisma } from '@/lib/db'
import { formatEuros } from '../saldos'

export async function emitirFactura(
  transactionId: string,
  userId: string
): Promise<{ invoiceId: string; pdfUrl: string }> {
  // Buscar transaction
  const transaction = await prisma.transaction.findFirst({
    where: {
      id: transactionId,
      userId
    }
  })
  
  if (!transaction) {
    throw new Error('Transaction não encontrada')
  }
  
  if (transaction.type !== 'income') {
    throw new Error('Apenas receitas podem ser facturadas')
  }
  
  if (transaction.categoryCode === 'RECEBIDO') {
    throw new Error('Transaction já está marcada como recebida')
  }
  
  const extra = transaction.extra as any
  if (!extra?.cliente_nome || !extra?.cliente_nif) {
    throw new Error('Transaction precisa ter dados de cliente (nome e NIF)')
  }
  
  // Obter API key do TOConline
  const apiKeySetting = await prisma.setting.findFirst({
    where: {
      userId,
      code: 'TOCONLINE_API_KEY'
    }
  })
  
  if (!apiKeySetting?.value) {
    throw new Error('TOConline API Key não configurada')
  }
  
  // Inicializar cliente
  const client = new TOConlineClient({
    apiKey: apiKeySetting.value
  })
  
  // Buscar ou criar cliente
  const customer = await client.getOrCreateCustomer({
    business_name: extra.cliente_nome,
    email: extra.cliente_email || `${extra.cliente_nif}@placeholder.com`,
    tax_registration_number: extra.cliente_nif
  })
  
  // Preparar linhas da factura
  const lines = []
  
  if (extra.items && Array.isArray(extra.items)) {
    // Se tem items detalhados
    lines.push(...extra.items.map((item: any) => ({
      description: item.description,
      quantity: item.quantity,
      unit_price: item.unitPrice / 100, // converter de cêntimos
      vat_rate: '23'
    })))
  } else {
    // Linha única
    lines.push({
      description: transaction.name || 'Serviços prestados',
      quantity: 1,
      unit_price: (transaction.total || 0) / 100,
      vat_rate: '23'
    })
  }
  
  // Emitir factura
  const invoice = await client.createInvoice({
    customer_id: customer.id,
    document_type: 'FT',
    lines,
    notes: transaction.note || undefined
  })
  
  // Finalizar (certificar AT)
  const finalizedInvoice = await client.finalizeInvoice(invoice.id)
  
  // Actualizar transaction
  await prisma.transaction.update({
    where: { id: transactionId },
    data: {
      categoryCode: 'FATURADO',
      extra: {
        ...extra,
        toconline_invoice_id: finalizedInvoice.id,
        toconline_document_number: finalizedInvoice.document_number,
        data_faturacao: new Date().toISOString()
      }
    }
  })
  
  return {
    invoiceId: finalizedInvoice.id,
    pdfUrl: finalizedInvoice.pdf_url || ''
  }
}
---

5.3 API ENDPOINT EMISSÃO
--------------------

Ficheiro: app/api/agora/toconline/invoices/route.ts

---
import { NextRequest, NextResponse } from 'next/server'
import { auth } from '@/lib/auth'
import { emitirFactura } from '@/lib/agora/toconline/invoices'

export async function POST(request: NextRequest) {
  try {
    const session = await auth.api.getSession({ headers: request.headers })
    if (!session) {
      return NextResponse.json({ error: 'Não autenticado' }, { status: 401 })
    }
    
    const body = await request.json()
    
    if (!body.transactionId) {
      return NextResponse.json(
        { error: 'transactionId é obrigatório' },
        { status: 400 }
      )
    }
    
    const result = await emitirFactura(body.transactionId, session.user.id)
    
    return NextResponse.json(result)
  } catch (error: any) {
    console.error('Erro ao emitir factura:', error)
    return NextResponse.json(
      { error: error.message || 'Erro interno' },
      { status: 500 }
    )
  }
}
---

5.4 UI INTEGRAÇÃO
--------------------

Ficheiro: components/agora/emit-invoice-button.tsx

LÓGICA:
---
// Mostrar botão apenas se:
// - Transaction type === 'income'
// - categoryCode !== 'RECEBIDO'
// - extra.cliente_nome existe
// - extra.toconline_invoice_id NÃO existe (ainda não facturado)

async function handleEmitInvoice() {
  setLoading(true)
  
  try {
    const response = await fetch('/api/agora/toconline/invoices', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ transactionId })
    })
    
    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.error)
    }
    
    const result = await response.json()
    
    toast.success('Factura emitida com sucesso!')
    
    // Abrir PDF
    if (result.pdfUrl) {
      window.open(result.pdfUrl, '_blank')
    }
    
    // Refresh page
    router.refresh()
  } catch (error: any) {
    toast.error(`Erro: ${error.message}`)
  } finally {
    setLoading(false)
  }
}
---

Ficheiro: app/(app)/toconline/page.tsx

PÁGINA SETTINGS:
---
<div>
  <h1>Configuração TOConline</h1>
  
  <Form>
    <FormField name="apiKey" type="password" label="API Key" />
    <Button onClick={handleSaveApiKey}>Guardar</Button>
    <Button onClick={handleTestConnection}>Testar Conexão</Button>
  </Form>
  
  {connectionStatus && (
    <Alert variant={connectionStatus.success ? 'success' : 'error'}>
      {connectionStatus.message}
    </Alert>
  )}
  
  <Card>
    <CardTitle>Estatísticas</CardTitle>
    <CardContent>
      <p>Facturas emitidas este mês: {stats.thisMonth}</p>
      <p>Total facturas: {stats.total}</p>
      <p>Última sincronização: {stats.lastSync}</p>
    </CardContent>
  </Card>
</div>
---

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
