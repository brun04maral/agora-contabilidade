===============================================================================
MIGRAÇÃO DE DADOS: Python SQLAlchemy → TaxHacker Prisma
Scripts e procedimentos para migração completa com validação
===============================================================================

==================================================
VISÃO GERAL
==================================================

OBJECTIVO: Migrar todos os dados da app Python para TaxHacker mantendo integridade

DADOS A MIGRAR:
✓ Users (Bruno e Rafael)
✓ Clientes
✓ Fornecedores
✓ Projetos → Transactions (income)
✓ Despesas → Transactions (expense)
✓ Boletins → Transactions (expense)
✓ Equipamento (se existir)

TEMPO ESTIMADO: 4-6 horas
COMPLEXIDADE: Média (conversões de tipos, mapeamentos)

PRÉ-REQUISITOS:
- App Python com dados actuais
- TaxHacker instalado e funcional
- PostgreSQL acessível
- Node.js + TypeScript funcionando

==================================================
FASE 1: PREPARAÇÃO
==================================================

1.1 BACKUP DOS DADOS ORIGINAIS
--------------------

CRÍTICO: Fazer backup antes de qualquer migração!

Via Python:
---
# Script: backup_database.py

import sqlite3
import json
from datetime import datetime

def backup_to_json():
    conn = sqlite3.connect('agora_media.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    backup = {
        'metadata': {
            'backup_date': datetime.now().isoformat(),
            'version': '1.0'
        },
        'data': {}
    }
    
    # Tabelas para backup
    tables = ['projetos', 'despesas', 'boletins', 'clientes', 'fornecedores', 'equipamento']
    
    for table in tables:
        cursor.execute(f"SELECT * FROM {table}")
        rows = cursor.fetchall()
        backup['data'][table] = [dict(row) for row in rows]
        print(f"✓ Backup {table}: {len(rows)} registos")
    
    # Guardar JSON
    filename = f"backup_agora_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(backup, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"\n✅ Backup guardado: {filename}")
    conn.close()

if __name__ == '__main__':
    backup_to_json()
---

Executar:
---
python backup_database.py
---

Output esperado:
---
✓ Backup projetos: 45 registos
✓ Backup despesas: 120 registos
✓ Backup boletins: 24 registos
✓ Backup clientes: 15 registos
✓ Backup fornecedores: 8 registos
✓ Backup equipamento: 12 registos

✅ Backup guardado: backup_agora_20251218_143000.json
---

1.2 EXPORTAR DADOS PARA CSV
--------------------

Alternativa: exportar CSVs para análise

---
import pandas as pd

# Ler de SQLite
conn = sqlite3.connect('agora_media.db')

# Exportar cada tabela
tables = ['projetos', 'despesas', 'boletins', 'clientes', 'fornecedores']

for table in tables:
    df = pd.read_sql_query(f"SELECT * FROM {table}", conn)
    df.to_csv(f"export_{table}.csv", index=False, encoding='utf-8')
    print(f"✓ {table}.csv: {len(df)} linhas")

conn.close()
---

1.3 ANALISAR DADOS
--------------------

Verificar estatísticas antes de migrar:

---
# Script: analyze_data.py

import sqlite3

conn = sqlite3.connect('agora_media.db')
cursor = conn.cursor()

print("=" * 60)
print("ANÁLISE DE DADOS PRÉ-MIGRAÇÃO")
print("=" * 60)

# Projetos
cursor.execute("SELECT tipo, estado, COUNT(*), SUM(valor_sem_iva) FROM projetos GROUP BY tipo, estado")
print("\nPROJETOS por tipo e estado:")
for row in cursor.fetchall():
    print(f"  {row[0]:20} {row[1]:15} {row[2]:3} projetos  Total: €{row[3]:,.2f}")

# Despesas
cursor.execute("SELECT tipo, estado, COUNT(*), SUM(valor_sem_iva) FROM despesas GROUP BY tipo, estado")
print("\nDESPESAS por tipo e estado:")
for row in cursor.fetchall():
    print(f"  {row[0]:20} {row[1]:15} {row[2]:3} despesas  Total: €{row[3]:,.2f}")

# Boletins
cursor.execute("SELECT socio, estado, COUNT(*), SUM(valor) FROM boletins GROUP BY socio, estado")
print("\nBOLETINS por sócio e estado:")
for row in cursor.fetchall():
    print(f"  {row[0]:20} {row[1]:15} {row[2]:3} boletins  Total: €{row[3]:,.2f}")

# Totais
cursor.execute("SELECT SUM(valor_sem_iva) FROM projetos WHERE estado = 'RECEBIDO'")
total_recebido = cursor.fetchone()[0] or 0

cursor.execute("SELECT SUM(valor_sem_iva) FROM despesas WHERE estado = 'PAGO'")
total_despesas = cursor.fetchone()[0] or 0

print(f"\n{'='*60}")
print(f"Total Receitas (RECEBIDAS): €{total_recebido:,.2f}")
print(f"Total Despesas (PAGAS):     €{total_despesas:,.2f}")
print(f"Diferença:                  €{total_recebido - total_despesas:,.2f}")
print(f"{'='*60}")

conn.close()
---

==================================================
FASE 2: SCRIPTS DE MIGRAÇÃO
==================================================

2.1 ESTRUTURA DOS SCRIPTS
--------------------

Criar pasta: lib/migrations/

Ficheiros:
---
lib/migrations/
├── 00-config.ts          # Configuração comum
├── 01-migrate-users.ts   # Criar Bruno e Rafael
├── 02-seed-categories.ts # Categories e Projects
├── 03-migrate-clientes.ts
├── 04-migrate-fornecedores.ts
├── 05-migrate-projetos.ts
├── 06-migrate-despesas.ts
├── 07-migrate-boletins.ts
├── 08-migrate-equipamento.ts
├── 99-validate.ts        # Validação final
└── run-all.ts            # Script master
---

2.2 CONFIG COMUM
--------------------

Ficheiro: lib/migrations/00-config.ts

---
import { PrismaClient } from '@prisma/client'
import sqlite3 from 'sqlite3'
import { open } from 'sqlite'

export const prisma = new PrismaClient()

// Path para database Python
export const SQLITE_PATH = process.env.PYTHON_DB_PATH || '../agora-app-python/agora_media.db'

// User IDs fixos (gerar UUIDs consistentes)
export const USER_IDS = {
  BRUNO: 'b1234567-89ab-cdef-0123-456789abcdef',
  RAFAEL: 'r1234567-89ab-cdef-0123-456789abcdef'
}

// Abrir SQLite
export async function openSQLite() {
  return open({
    filename: SQLITE_PATH,
    driver: sqlite3.Database
  })
}

// Helper: converter Decimal para cêntimos
export function toCents(value: number | string | null): number {
  if (!value) return 0
  const num = typeof value === 'string' ? parseFloat(value) : value
  return Math.round(num * 100)
}

// Helper: formatar data
export function parseDate(dateStr: string | null): Date | null {
  if (!dateStr) return null
  return new Date(dateStr)
}

// Logger
export function log(message: string, data?: any) {
  console.log(`[${new Date().toISOString()}] ${message}`)
  if (data) console.log(JSON.stringify(data, null, 2))
}
---

2.3 MIGRAR USERS
--------------------

Ficheiro: lib/migrations/01-migrate-users.ts

---
import { prisma, USER_IDS, log } from './00-config'
import bcrypt from 'bcryptjs'

export async function migrateUsers() {
  log('🔵 Iniciando migração de users...')
  
  const users = [
    {
      id: USER_IDS.BRUNO,
      email: 'bruno@agoramedia.pt',
      name: 'Bruno Amaral',
      password: 'bruno123' // MUDAR em produção!
    },
    {
      id: USER_IDS.RAFAEL,
      email: 'rafael@agoramedia.pt',
      name: 'Rafael Amaral',
      password: 'rafael123' // MUDAR em produção!
    }
  ]
  
  for (const userData of users) {
    // Verificar se já existe
    const existing = await prisma.user.findUnique({
      where: { email: userData.email }
    })
    
    if (existing) {
      log(`⚠️  User ${userData.email} já existe, pulando...`)
      continue
    }
    
    // Criar user
    const user = await prisma.user.create({
      data: {
        id: userData.id,
        email: userData.email,
        name: userData.name,
        emailVerified: true
      }
    })
    
    // Criar account (Better Auth)
    const hashedPassword = await bcrypt.hash(userData.password, 10)
    
    await prisma.account.create({
      data: {
        userId: user.id,
        accountId: userData.email,
        providerId: 'credential',
        password: hashedPassword
      }
    })
    
    log(`✅ User criado: ${userData.name}`)
  }
  
  log('✅ Migração de users completa\n')
}
---

2.4 SEED CATEGORIES E PROJECTS
--------------------

Ficheiro: lib/migrations/02-seed-categories.ts

---
import { prisma, USER_IDS, log } from './00-config'

export async function seedCategoriesAndProjects() {
  log('🔵 Seeding categories e projects...')
  
  // Categories
  const categories = [
    { code: 'RECEBIDO', name: 'Recebido', color: '#22c55e' },
    { code: 'FATURADO', name: 'Faturado', color: '#f59e0b' },
    { code: 'NAO_FATURADO', name: 'Não Faturado', color: '#9ca3af' },
    { code: 'FIXA_MENSAL', name: 'Despesa Fixa Mensal', color: '#ef4444' },
    { code: 'DESPESA_PESSOAL_BRUNO', name: 'Despesa Pessoal Bruno', color: '#3b82f6' },
    { code: 'DESPESA_PESSOAL_RAFAEL', name: 'Despesa Pessoal Rafael', color: '#8b5cf6' },
    { code: 'DESPESA_EQUIPAMENTO', name: 'Despesa Equipamento', color: '#6366f1' },
    { code: 'DESPESA_PROJETO', name: 'Despesa Projeto', color: '#f97316' },
    { code: 'BOLETIM', name: 'Boletim', color: '#ec4899' }
  ]
  
  for (const cat of categories) {
    // Criar para cada user
    for (const userId of Object.values(USER_IDS)) {
      await prisma.category.upsert({
        where: {
          userId_code: {
            userId,
            code: cat.code
          }
        },
        update: {},
        create: {
          userId,
          code: cat.code,
          name: cat.name,
          color: cat.color
        }
      })
    }
  }
  
  log(`✅ ${categories.length} categories criadas`)
  
  // Projects
  const projects = [
    { code: 'EMPRESA', name: 'Agora Media', color: '#10b981' },
    { code: 'PESSOAL_BRUNO', name: 'Projetos Pessoais Bruno', color: '#3b82f6' },
    { code: 'PESSOAL_RAFAEL', name: 'Projetos Pessoais Rafael', color: '#8b5cf6' }
  ]
  
  for (const proj of projects) {
    for (const userId of Object.values(USER_IDS)) {
      await prisma.project.upsert({
        where: {
          userId_code: {
            userId,
            code: proj.code
          }
        },
        update: {},
        create: {
          userId,
          code: proj.code,
          name: proj.name,
          color: proj.color
        }
      })
    }
  }
  
  log(`✅ ${projects.length} projects criados`)
  log('✅ Seed completo\n')
}
---

2.5 MIGRAR PROJETOS
--------------------

Ficheiro: lib/migrations/05-migrate-projetos.ts

---
import { prisma, openSQLite, USER_IDS, toCents, parseDate, log } from './00-config'

export async function migrateProjetos() {
  log('🔵 Iniciando migração de projetos...')
  
  const db = await openSQLite()
  
  // Buscar projetos do SQLite
  const projetos = await db.all('SELECT * FROM projetos ORDER BY id')
  
  log(`Encontrados ${projetos.length} projetos`)
  
  let migrated = 0
  let skipped = 0
  
  for (const proj of projetos) {
    try {
      // Determinar userId baseado no tipo
      let userId = USER_IDS.BRUNO // default
      let projectCode = 'EMPRESA'
      
      if (proj.tipo === 'PESSOAL_BRUNO') {
        userId = USER_IDS.BRUNO
        projectCode = 'PESSOAL_BRUNO'
      } else if (proj.tipo === 'PESSOAL_RAFAEL') {
        userId = USER_IDS.RAFAEL
        projectCode = 'PESSOAL_RAFAEL'
      }
      
      // Mapear estado para categoryCode
      const categoryCode = proj.estado || 'NAO_FATURADO'
      
      // Buscar cliente (se existir)
      let clienteInfo: any = {}
      if (proj.cliente_id) {
        const cliente = await db.get('SELECT * FROM clientes WHERE id = ?', proj.cliente_id)
        if (cliente) {
          clienteInfo = {
            cliente_id: cliente.id,
            cliente_nome: cliente.nome,
            cliente_nif: cliente.nif,
            cliente_email: cliente.email
          }
        }
      }
      
      // Criar transaction
      await prisma.transaction.create({
        data: {
          userId,
          type: 'income',
          name: proj.descricao,
          total: toCents(proj.valor_sem_iva),
          projectCode,
          categoryCode,
          issuedAt: parseDate(proj.data_faturacao) || parseDate(proj.data_inicio) || new Date(),
          note: proj.nota,
          extra: {
            // Dados originais
            numero_projeto: proj.numero,
            tipo_origem: 'PROJETO_PYTHON',
            
            // Datas
            data_inicio: proj.data_inicio,
            data_fim: proj.data_fim,
            data_faturacao: proj.data_faturacao,
            data_vencimento: proj.data_vencimento,
            
            // Prémios
            premio_bruno: toCents(proj.premio_bruno),
            premio_rafael: toCents(proj.premio_rafael),
            
            // Cliente
            ...clienteInfo
          }
        }
      })
      
      migrated++
      
      if (migrated % 10 === 0) {
        log(`  ... ${migrated} projetos migrados`)
      }
    } catch (error: any) {
      log(`❌ Erro ao migrar projeto ${proj.numero}: ${error.message}`)
      skipped++
    }
  }
  
  await db.close()
  
  log(`✅ Projetos migrados: ${migrated}`)
  if (skipped > 0) {
    log(`⚠️  Projetos com erro: ${skipped}`)
  }
  log('')
}
---

2.6 MIGRAR DESPESAS
--------------------

Ficheiro: lib/migrations/06-migrate-despesas.ts

---
import { prisma, openSQLite, USER_IDS, toCents, parseDate, log } from './00-config'

export async function migrateDespesas() {
  log('🔵 Iniciando migração de despesas...')
  
  const db = await openSQLite()
  const despesas = await db.all('SELECT * FROM despesas ORDER BY id')
  
  log(`Encontradas ${despesas.length} despesas`)
  
  let migrated = 0
  let skipped = 0
  
  for (const desp of despesas) {
    try {
      // Mapear tipo para categoryCode
      let categoryCode = 'FIXA_MENSAL'
      switch (desp.tipo) {
        case 'FIXA_MENSAL':
          categoryCode = 'FIXA_MENSAL'
          break
        case 'PESSOAL_BRUNO':
          categoryCode = 'DESPESA_PESSOAL_BRUNO'
          break
        case 'PESSOAL_RAFAEL':
          categoryCode = 'DESPESA_PESSOAL_RAFAEL'
          break
        case 'EQUIPAMENTO':
          categoryCode = 'DESPESA_EQUIPAMENTO'
          break
        case 'PROJETO':
          categoryCode = 'DESPESA_PROJETO'
          break
      }
      
      // Buscar fornecedor (credor)
      let fornecedorInfo: any = {}
      if (desp.credor_id) {
        const fornecedor = await db.get('SELECT * FROM fornecedores WHERE id = ?', desp.credor_id)
        if (fornecedor) {
          fornecedorInfo = {
            fornecedor_id: fornecedor.id,
            fornecedor_nome: fornecedor.nome,
            fornecedor_nif: fornecedor.nif
          }
        }
      }
      
      // Determinar projectCode se associado a projeto
      let projectCode: string | undefined
      if (desp.projeto_id) {
        const projeto = await db.get('SELECT tipo FROM projetos WHERE id = ?', desp.projeto_id)
        if (projeto) {
          projectCode = projeto.tipo === 'PESSOAL_BRUNO' ? 'PESSOAL_BRUNO' 
                      : projeto.tipo === 'PESSOAL_RAFAEL' ? 'PESSOAL_RAFAEL'
                      : 'EMPRESA'
        }
      }
      
      // Criar transaction (despesa é NEGATIVA!)
      await prisma.transaction.create({
        data: {
          userId: USER_IDS.BRUNO, // Despesas são sempre do sistema
          type: 'expense',
          name: desp.descricao,
          total: -Math.abs(toCents(desp.valor_sem_iva)), // NEGATIVO!
          categoryCode,
          projectCode,
          issuedAt: parseDate(desp.data) || new Date(),
          note: desp.nota,
          extra: {
            numero_despesa: desp.numero,
            tipo_origem: 'DESPESA_PYTHON',
            
            valor_com_iva: toCents(desp.valor_com_iva),
            estado_pagamento: desp.estado || 'PENDENTE',
            
            projeto_associado_id: desp.projeto_id,
            
            ...fornecedorInfo
          }
        }
      })
      
      migrated++
      
      if (migrated % 10 === 0) {
        log(`  ... ${migrated} despesas migradas`)
      }
    } catch (error: any) {
      log(`❌ Erro ao migrar despesa ${desp.numero}: ${error.message}`)
      skipped++
    }
  }
  
  await db.close()
  
  log(`✅ Despesas migradas: ${migrated}`)
  if (skipped > 0) {
    log(`⚠️  Despesas com erro: ${skipped}`)
  }
  log('')
}
---

2.7 MIGRAR BOLETINS
--------------------

Ficheiro: lib/migrations/07-migrate-boletins.ts

---
import { prisma, openSQLite, USER_IDS, toCents, parseDate, log } from './00-config'

export async function migrateBoletins() {
  log('🔵 Iniciando migração de boletins...')
  
  const db = await openSQLite()
  const boletins = await db.all('SELECT * FROM boletins ORDER BY id')
  
  log(`Encontrados ${boletins.length} boletins`)
  
  let migrated = 0
  let skipped = 0
  
  for (const bol of boletins) {
    try {
      // Determinar userId
      const userId = bol.socio === 'BRUNO' ? USER_IDS.BRUNO : USER_IDS.RAFAEL
      
      // Criar transaction (boletim é NEGATIVO!)
      await prisma.transaction.create({
        data: {
          userId,
          type: 'expense',
          name: bol.descricao,
          total: -Math.abs(toCents(bol.valor)), // NEGATIVO!
          categoryCode: 'BOLETIM',
          issuedAt: parseDate(bol.data_emissao) || new Date(),
          note: bol.nota,
          extra: {
            numero_boletim: bol.numero,
            tipo_origem: 'BOLETIM_PYTHON',
            
            socio: bol.socio,
            estado_boletim: bol.estado || 'PENDENTE',
            data_pagamento: bol.data_pagamento
          }
        }
      })
      
      migrated++
    } catch (error: any) {
      log(`❌ Erro ao migrar boletim ${bol.numero}: ${error.message}`)
      skipped++
    }
  }
  
  await db.close()
  
  log(`✅ Boletins migrados: ${migrated}`)
  if (skipped > 0) {
    log(`⚠️  Boletins com erro: ${skipped}`)
  }
  log('')
}
---

2.8 SCRIPT VALIDAÇÃO
--------------------

Ficheiro: lib/migrations/99-validate.ts

---
import { prisma, openSQLite, toCents, log } from './00-config'
import { calculateSaldoBruno, calculateSaldoRafael } from '../agora/saldos'

export async function validate() {
  log('🔵 Iniciando validação...')
  log('='*60)
  
  const db = await openSQLite()
  
  // 1. VALIDAR CONTAGENS
  log('\n📊 CONTAGENS:')
  
  const countProjetos = await db.get('SELECT COUNT(*) as count FROM projetos')
  const countTransactionsIncome = await prisma.transaction.count({
    where: { type: 'income' }
  })
  log(`  Projetos Python:       ${countProjetos.count}`)
  log(`  Transactions (income): ${countTransactionsIncome}`)
  log(`  Match: ${countProjetos.count === countTransactionsIncome ? '✅' : '❌'}`)
  
  const countDespesas = await db.get('SELECT COUNT(*) as count FROM despesas')
  const countBoletins = await db.get('SELECT COUNT(*) as count FROM boletins')
  const countTransactionsExpense = await prisma.transaction.count({
    where: { type: 'expense' }
  })
  log(`  Despesas Python:       ${countDespesas.count}`)
  log(`  Boletins Python:       ${countBoletins.count}`)
  log(`  Total esperado:        ${countDespesas.count + countBoletins.count}`)
  log(`  Transactions (expense):${countTransactionsExpense}`)
  log(`  Match: ${countDespesas.count + countBoletins.count === countTransactionsExpense ? '✅' : '❌'}`)
  
  // 2. VALIDAR VALORES (CRÍTICO!)
  log('\n💰 VALORES:')
  
  // Python: total receitas RECEBIDAS
  const pythonReceitas = await db.get(`
    SELECT SUM(valor_sem_iva) as total 
    FROM projetos 
    WHERE estado = 'RECEBIDO'
  `)
  
  // Prisma: total transactions income RECEBIDO
  const prismaReceitas = await prisma.transaction.aggregate({
    where: {
      type: 'income',
      categoryCode: 'RECEBIDO'
    },
    _sum: { total: true }
  })
  
  const pythonReceitasEuros = pythonReceitas.total || 0
  const prismaReceitasEuros = (prismaReceitas._sum.total || 0) / 100
  
  log(`  Python receitas RECEBIDAS:  €${pythonReceitasEuros.toFixed(2)}`)
  log(`  Prisma receitas RECEBIDAS:  €${prismaReceitasEuros.toFixed(2)}`)
  log(`  Diferença:                  €${Math.abs(pythonReceitasEuros - prismaReceitasEuros).toFixed(2)}`)
  log(`  Match: ${Math.abs(pythonReceitasEuros - prismaReceitasEuros) < 0.01 ? '✅' : '❌'}`)
  
  // Python: total despesas PAGAS
  const pythonDespesas = await db.get(`
    SELECT SUM(valor_sem_iva) as total 
    FROM despesas 
    WHERE estado = 'PAGO'
  `)
  
  // Prisma: total despesas PAGAS
  const prismaDespesas = await prisma.transaction.aggregate({
    where: {
      type: 'expense',
      categoryCode: { not: 'BOLETIM' },
      extra: { path: ['estado_pagamento'], equals: 'PAGO' }
    },
    _sum: { total: true }
  })
  
  const pythonDespesasEuros = pythonDespesas.total || 0
  const prismaDespesasEuros = Math.abs((prismaDespesas._sum.total || 0) / 100)
  
  log(`  Python despesas PAGAS:      €${pythonDespesasEuros.toFixed(2)}`)
  log(`  Prisma despesas PAGAS:      €${prismaDespesasEuros.toFixed(2)}`)
  log(`  Diferença:                  €${Math.abs(pythonDespesasEuros - prismaDespesasEuros).toFixed(2)}`)
  log(`  Match: ${Math.abs(pythonDespesasEuros - prismaDespesasEuros) < 0.01 ? '✅' : '❌'}`)
  
  // 3. VALIDAR SALDOS
  log('\n🧮 SALDOS:')
  
  // Calcular saldos com TypeScript
  const saldoBruno = await calculateSaldoBruno(USER_IDS.BRUNO)
  const saldoRafael = await calculateSaldoRafael(USER_IDS.RAFAEL)
  
  log(`  Saldo Bruno (Prisma):  €${(saldoBruno.saldo / 100).toFixed(2)}`)
  log(`  Saldo Rafael (Prisma): €${(saldoRafael.saldo / 100).toFixed(2)}`)
  
  log('\n  ⚠️  COMPARA COM APP PYTHON MANUALMENTE!')
  
  await db.close()
  
  log('\n' + '='*60)
  log('✅ Validação completa\n')
}
---

2.9 SCRIPT MASTER
--------------------

Ficheiro: lib/migrations/run-all.ts

---
import { migrateUsers } from './01-migrate-users'
import { seedCategoriesAndProjects } from './02-seed-categories'
import { migrateProjetos } from './05-migrate-projetos'
import { migrateDespesas } from './06-migrate-despesas'
import { migrateBoletins } from './07-migrate-boletins'
import { validate } from './99-validate'
import { prisma } from './00-config'

async function runAll() {
  console.log('\n')
  console.log('='*70)
  console.log('  MIGRAÇÃO COMPLETA: Python SQLite → TaxHacker Prisma')
  console.log('='*70)
  console.log('\n')
  
  try {
    await migrateUsers()
    await seedCategoriesAndProjects()
    await migrateProjetos()
    await migrateDespesas()
    await migrateBoletins()
    await validate()
    
    console.log('\n')
    console.log('='*70)
    console.log('  ✅ MIGRAÇÃO COMPLETA COM SUCESSO!')
    console.log('='*70)
    console.log('\n')
  } catch (error) {
    console.error('\n❌ ERRO DURANTE MIGRAÇÃO:', error)
    process.exit(1)
  } finally {
    await prisma.$disconnect()
  }
}

runAll()
---

==================================================
FASE 3: EXECUTAR MIGRAÇÃO
==================================================

3.1 INSTALAR DEPENDÊNCIAS
--------------------

---
npm install sqlite sqlite3 bcryptjs
npm install --save-dev @types/bcryptjs
---

3.2 CONFIGURAR .env
--------------------

Adicionar ao .env:
---
PYTHON_DB_PATH="../agora-app-python/agora_media.db"
---

3.3 EXECUTAR
--------------------

---
npx ts-node lib/migrations/run-all.ts
---

Output esperado:
---
======================================================================
  MIGRAÇÃO COMPLETA: Python SQLite → TaxHacker Prisma
======================================================================

[2025-12-18T14:30:00.000Z] 🔵 Iniciando migração de users...
[2025-12-18T14:30:01.000Z] ✅ User criado: Bruno Amaral
[2025-12-18T14:30:02.000Z] ✅ User criado: Rafael Amaral
[2025-12-18T14:30:02.000Z] ✅ Migração de users completa

[2025-12-18T14:30:02.000Z] 🔵 Seeding categories e projects...
[2025-12-18T14:30:03.000Z] ✅ 9 categories criadas
[2025-12-18T14:30:03.000Z] ✅ 3 projects criados
[2025-12-18T14:30:03.000Z] ✅ Seed completo

[2025-12-18T14:30:03.000Z] 🔵 Iniciando migração de projetos...
[2025-12-18T14:30:03.000Z] Encontrados 45 projetos
[2025-12-18T14:30:10.000Z]   ... 10 projetos migrados
[2025-12-18T14:30:17.000Z]   ... 20 projetos migrados
[2025-12-18T14:30:24.000Z]   ... 30 projetos migrados
[2025-12-18T14:30:31.000Z]   ... 40 projetos migrados
[2025-12-18T14:30:35.000Z] ✅ Projetos migrados: 45

[...continua com despesas e boletins...]

[2025-12-18T14:32:00.000Z] 🔵 Iniciando validação...
============================================================

📊 CONTAGENS:
  Projetos Python:       45
  Transactions (income): 45
  Match: ✅
  
  Despesas Python:       120
  Boletins Python:       24
  Total esperado:        144
  Transactions (expense):144
  Match: ✅

💰 VALORES:
  Python receitas RECEBIDAS:  €45,230.00
  Prisma receitas RECEBIDAS:  €45,230.00
  Diferença:                  €0.00
  Match: ✅
  
  Python despesas PAGAS:      €12,450.00
  Prisma despesas PAGAS:      €12,450.00
  Diferença:                  €0.00
  Match: ✅

🧮 SALDOS:
  Saldo Bruno (Prisma):  €1,225.50
  Saldo Rafael (Prisma): €1,700.00
  
  ⚠️  COMPARA COM APP PYTHON MANUALMENTE!

============================================================
✅ Validação completa

======================================================================
  ✅ MIGRAÇÃO COMPLETA COM SUCESSO!
======================================================================
---

==================================================
FASE 4: PÓS-MIGRAÇÃO
==================================================

4.1 VERIFICAÇÃO MANUAL
--------------------

Abrir Prisma Studio:
---
npx prisma studio
---

Verificar:
□ Users: Bruno e Rafael existem
□ Transactions: contagens correctas
□ Extra JSON: dados preservados
□ Dates: formatos correctos
□ Valores: em cêntimos (x100)

4.2 TESTAR APP
--------------------

---
npm run dev
---

Testes manuais:
□ Login com Bruno/Rafael funciona
□ /transactions mostra dados migrados
□ /saldos calcula valores correctos
□ Filtros funcionam
□ Export CSV funciona

4.3 COMPARAR SALDOS
--------------------

Executar na app Python:
---
python calculate_saldos.py
---

Comparar com /saldos no TaxHacker

DEVE BATER AO CÊNTIMO!

Se não bater:
1. Verificar despesas fixas (dividir por 2?)
2. Verificar filtros RECEBIDO/PAGO
3. Debug queries Prisma

==================================================
TROUBLESHOOTING
==================================================

ERRO: Cannot find module 'sqlite'
SOLUÇÃO:
---
npm install sqlite sqlite3
---

ERRO: Valores não batem
SOLUÇÃO:
- Verificar conversão cêntimos (x100)
- Verificar despesas negativas (-)
- Verificar filtros estado

ERRO: Datas inválidas
SOLUÇÃO:
- Verificar formato datas Python (ISO 8601?)
- Usar parseDate helper

ERRO: Users já existem
SOLUÇÃO:
- Limpar database: npx prisma migrate reset
- OU ajustar script para skip

==================================================
ROLLBACK
==================================================

Se algo correr mal:

1. Parar migração (Ctrl+C)

2. Limpar database:
---
npx prisma migrate reset --force
---

3. Restaurar backup Python:
---
cp backup_agora_YYYYMMDD.db agora_media.db
---

4. Analisar erros e ajustar scripts

5. Tentar novamente

==================================================
