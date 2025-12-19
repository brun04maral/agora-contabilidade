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

Script: `backup_database.py`

```python
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
```

Executar:
```bash
python backup_database.py
```

Output esperado:
```
✓ Backup projetos: 45 registos
✓ Backup despesas: 120 registos
✓ Backup boletins: 24 registos
✓ Backup clientes: 15 registos
✓ Backup fornecedores: 8 registos
✓ Backup equipamento: 12 registos

✅ Backup guardado: backup_agora_20251218_143000.json
```

1.2 EXPORTAR DADOS PARA CSV
--------------------

Alternativa: exportar CSVs para análise

```python
import pandas as pd
import sqlite3

# Ler de SQLite
conn = sqlite3.connect('agora_media.db')

# Exportar cada tabela
tables = ['projetos', 'despesas', 'boletins', 'clientes', 'fornecedores']

for table in tables:
    df = pd.read_sql_query(f"SELECT * FROM {table}", conn)
    df.to_csv(f"export_{table}.csv", index=False, encoding='utf-8')
    print(f"✓ {table}.csv: {len(df)} linhas")

conn.close()
```

1.3 ANALISAR DADOS
--------------------

Verificar estatísticas antes de migrar:

Script: `analyze_data.py`

```python
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
```

==================================================
FASE 2: SCRIPTS DE MIGRAÇÃO
==================================================

2.1 ESTRUTURA DOS SCRIPTS
--------------------

Criar pasta: `lib/migrations/`

Ficheiros:
```
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
```

2.2 CONFIG COMUM
--------------------

Ficheiro: `lib/migrations/00-config.ts`

```typescript
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
```

2.3 MIGRAR USERS
--------------------

Ficheiro: `lib/migrations/01-migrate-users.ts`

```typescript
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
```

2.4 SEED CATEGORIES E PROJECTS
--------------------

Ficheiro: `lib/migrations/02-seed-categories.ts`

```typescript
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
```

2.5 MIGRAR PROJETOS
--------------------

Ficheiro: `lib/migrations/05-migrate-projetos.ts`

```typescript
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
```

(Continua com mais 3 ficheiros de migração...)

==================================================
FASE 3: EXECUTAR MIGRAÇÃO
==================================================

3.1 INSTALAR DEPENDÊNCIAS
--------------------

```bash
npm install sqlite sqlite3 bcryptjs
npm install --save-dev @types/bcryptjs
```

3.2 CONFIGURAR .env
--------------------

Adicionar ao `.env`:
```bash
PYTHON_DB_PATH="../agora-app-python/agora_media.db"
```

3.3 EXECUTAR
--------------------

```bash
npx ts-node lib/migrations/run-all.ts
```

Output esperado:
```
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
```

==================================================
FASE 4: PÓS-MIGRAÇÃO
==================================================

4.1 VERIFICAÇÃO MANUAL
--------------------

Abrir Prisma Studio:
```bash
npx prisma studio
```

Verificar:
□ Users: Bruno e Rafael existem
□ Transactions: contagens correctas
□ Extra JSON: dados preservados
□ Dates: formatos correctos
□ Valores: em cêntimos (x100)

4.2 TESTAR APP
--------------------

```bash
npm run dev
```

Testes manuais:
□ Login com Bruno/Rafael funciona
□ /transactions mostra dados migrados
□ /saldos calcula valores correctos
□ Filtros funcionam
□ Export CSV funciona

4.3 COMPARAR SALDOS
--------------------

Executar na app Python:
```bash
python calculate_saldos.py
```

Comparar com `/saldos` no TaxHacker

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
```bash
npm install sqlite sqlite3
```

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
```bash
# Limpar database
npx prisma migrate reset
# OU ajustar script para skip
```

==================================================
ROLLBACK
==================================================

Se algo correr mal:

1. Parar migração (Ctrl+C)

2. Limpar database:
```bash
npx prisma migrate reset --force
```

3. Restaurar backup Python:
```bash
cp backup_agora_YYYYMMDD.db agora_media.db
```

4. Analisar erros e ajustar scripts

5. Tentar novamente

==================================================
