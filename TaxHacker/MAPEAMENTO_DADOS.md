===============================================================================
MAPEAMENTO DE DADOS: Python SQLAlchemy → TaxHacker Prisma
Baseado em análise REAL dos dois repositórios
===============================================================================

DATA: 18 Dezembro 2025
VERSÃO BASE: TaxHacker v0.6.0 + Agora Contabilidade (main branch)

==================================================
ANÁLISE: SCHEMA TAXHACKER (PRISMA) - O QUE EXISTE
==================================================

MODELO Transaction (CORE do TaxHacker):
----------------------------------------
```prisma
id                    String (UUID)
userId                String (UUID)
name                  String?           // Nome/descrição
description           String?
merchant              String?           // Fornecedor/Cliente
total                 Int?              // CÊNTIMOS (x100)
currencyCode          String?
convertedTotal        Int?
convertedCurrencyCode String?
type                  String?           // "expense" | "income"
items                 Json              // Array de line items
note                  String?
files                 Json              // Array de file IDs
extra                 Json?             // ⭐ CAMPO LIVRE - aqui guardamos custom data
categoryCode          String?           // FK para Category
projectCode           String?           // FK para Project
issuedAt              DateTime?         // Data da transação
createdAt             DateTime
updatedAt             DateTime
text                  String?           // Full-text search
```

MODELO Category:
----------------------------------------
```prisma
id         String (UUID)
userId     String (UUID)
code       String                        // Ex: "RECEBIDO", "FIXA_MENSAL"
name       String                        // Nome display
color      String                        // Hex color
llm_prompt String?                       // AI prompt (não usar)
```

MODELO Project:
----------------------------------------
```prisma
id         String (UUID)
userId     String (UUID)
code       String                        // Ex: "EMPRESA", "PESSOAL_BRUNO"
name       String
color      String
llm_prompt String?
```

MODELO Field (Custom Fields):
----------------------------------------
```prisma
id                  String (UUID)
userId              String (UUID)
code                String                // Ex: "premio_bruno"
name                String                // Display name
type                String                // "string"|"number"|"select"
llm_prompt          String?
options             Json?                 // Para select: {values: [...]}
isVisibleInList     Boolean
isVisibleInAnalysis Boolean
isRequired          Boolean
isExtra             Boolean               // Se é custom field
```

MODELO File:
----------------------------------------
```prisma
id                String (UUID)
userId            String (UUID)
filename          String
path              String
mimetype          String
metadata          Json?
isReviewed        Boolean
isSplitted        Boolean
cachedParseResult Json?
```

==================================================
ANÁLISE: MODELOS AGORA CONTABILIDADE (PYTHON)
==================================================

PROJETO (projeto.py):
----------------------------------------
```python
id                    Integer
numero                String(20)          // #P0001
tipo                  Enum                // EMPRESA|PESSOAL_BRUNO|PESSOAL_RAFAEL
cliente_id            Integer (FK)
data_inicio           Date
data_fim              Date
descricao             Text
valor_sem_iva         Numeric(10,2)
data_faturacao        Date
data_vencimento       Date
estado                Enum                // NAO_FATURADO|FATURADO|RECEBIDO
premio_bruno          Numeric(10,2)
premio_rafael         Numeric(10,2)
nota                  Text
created_at            DateTime
updated_at            DateTime
```

DESPESA (despesa.py):
----------------------------------------
```python
id                    Integer
numero                String(20)          // #D000001
tipo                  Enum                // FIXA_MENSAL|PESSOAL_X|EQUIPAMENTO|PROJETO
data                  Date
credor_id             Integer (FK fornecedor)
projeto_id            Integer (FK projeto)
descricao             Text
valor_sem_iva         Numeric(10,2)
valor_com_iva         Numeric(10,2)
estado                Enum                // PENDENTE|PAGO
nota                  Text
created_at            DateTime
updated_at            DateTime
```

BOLETIM (boletim.py):
----------------------------------------
```python
id                    Integer
numero                String(20)          // #B0001
socio                 Enum                // BRUNO|RAFAEL
data_emissao          Date
valor                 Numeric(10,2)
descricao             Text
estado                Enum                // PENDENTE|PAGO
data_pagamento        Date?
nota                  Text
created_at            DateTime
updated_at            DateTime
```

CLIENTE (cliente.py):
----------------------------------------
```python
id                    Integer
numero                String(20)          // #C0001
nome                  String(100)
nif                   String(20)
pais                  String(50)
email                 String(100)
morada                Text
```

FORNECEDOR (fornecedor.py):
----------------------------------------
```python
id                    Integer
numero                String(20)          // #F0001
nome                  String(100)
estatuto              Enum                // EMPRESA|FREELANCER
area                  String(50)
nif                   String(20)
funcao                String(100)
classificacao         Integer(1-5)
```

EQUIPAMENTO (equipamento.py):
----------------------------------------
```python
id                    Integer
nome                  String(100)
categoria             String(50)
data_compra           Date
valor_compra          Numeric(10,2)
vida_util_anos        Integer
valor_actual          Numeric(10,2)
nota                  Text
```

==================================================
MAPEAMENTO REAL: PROJETO → TRANSACTION
==================================================

TaxHacker Transaction permite:
✅ type: 'income' (para projetos = receitas)
✅ projectCode: mapear tipo de projeto
✅ categoryCode: mapear estado
✅ extra: JSON livre para campos específicos

ESTRATÉGIA MAPEAMENTO:
----------------------------------------

```
Projeto Python                →  TaxHacker Transaction
----------------------------------------
id                            →  id (gerar novo UUID)
numero (#P0001)               →  extra.numero_projeto
tipo (enum)                   →  projectCode
  - EMPRESA                      → 'EMPRESA'
  - PESSOAL_BRUNO                → 'PESSOAL_BRUNO'
  - PESSOAL_RAFAEL               → 'PESSOAL_RAFAEL'

descricao                     →  name
nota                          →  note
valor_sem_iva                 →  total (x100 para cêntimos!)
data_faturacao                →  issuedAt
estado (enum)                 →  categoryCode
  - NAO_FATURADO                 → 'NAO_FATURADO'
  - FATURADO                     → 'FATURADO'
  - RECEBIDO                     → 'RECEBIDO'

// CAMPOS ESPECÍFICOS → extra JSON:
premio_bruno                  →  extra.premio_bruno
premio_rafael                 →  extra.premio_rafael
data_inicio                   →  extra.data_inicio
data_fim                      →  extra.data_fim
data_vencimento               →  extra.data_vencimento

// CLIENTE → extra JSON (não há FK):
cliente_id                    →  extra.cliente_id
+ incluir:                       extra.cliente_nome
                                 extra.cliente_nif
                                 extra.cliente_email

type (fixo)                   →  'income'
userId                        →  ID do Bruno ou Rafael
```

EXEMPLO CONCRETO:
----------------------------------------

Projeto Python:
```json
{
  "id": 1,
  "numero": "#P0001",
  "tipo": "PESSOAL_BRUNO",
  "descricao": "Vídeo Corporativo RTP",
  "valor_sem_iva": 1500.00,
  "estado": "RECEBIDO",
  "premio_bruno": 0,
  "premio_rafael": 0,
  "data_faturacao": "2025-01-20"
}
```

Transaction TaxHacker:
```json
{
  "id": "uuid-generated",
  "userId": "bruno-uuid",
  "type": "income",
  "name": "Vídeo Corporativo RTP",
  "total": 150000,
  "projectCode": "PESSOAL_BRUNO",
  "categoryCode": "RECEBIDO",
  "issuedAt": "2025-01-20T00:00:00Z",
  "extra": {
    "numero_projeto": "#P0001",
    "premio_bruno": 0,
    "premio_rafael": 0,
    "data_inicio": "2025-01-10",
    "data_fim": null,
    "data_vencimento": null,
    "cliente_id": 1,
    "cliente_nome": "RTP",
    "cliente_nif": "500776088"
  }
}
```

NOTA: `total: 150000` = 1500.00 EUR × 100 cêntimos

==================================================
MAPEAMENTO REAL: DESPESA → TRANSACTION
==================================================

```
Despesa Python                →  TaxHacker Transaction
----------------------------------------
id                            →  id (novo UUID)
numero (#D000001)             →  extra.numero_despesa
tipo (enum)                   →  categoryCode
  - FIXA_MENSAL                  → 'FIXA_MENSAL'
  - PESSOAL_BRUNO                → 'DESPESA_PESSOAL_BRUNO'
  - PESSOAL_RAFAEL               → 'DESPESA_PESSOAL_RAFAEL'
  - EQUIPAMENTO                  → 'DESPESA_EQUIPAMENTO'
  - PROJETO                      → 'DESPESA_PROJETO'

descricao                     →  name
nota                          →  note
valor_sem_iva                 →  total (NEGATIVO, x100 cêntimos)
valor_com_iva                 →  extra.valor_com_iva
data                          →  issuedAt
estado                        →  extra.estado_pagamento
  - PENDENTE                     → 'PENDENTE'
  - PAGO                         → 'PAGO'

// FORNECEDOR → extra JSON:
credor_id                     →  extra.fornecedor_id
+ incluir:                       extra.fornecedor_nome
                                 extra.fornecedor_nif

// PROJETO ASSOCIADO:
projeto_id                    →  projectCode (se aplicável)
                                 extra.projeto_associado_id

type (fixo)                   →  'expense'
userId                        →  ID do user
```

EXEMPLO CONCRETO:
----------------------------------------

Despesa Python:
```json
{
  "id": 1,
  "numero": "#D000001",
  "tipo": "FIXA_MENSAL",
  "descricao": "Contabilidade - Janeiro 2025",
  "valor_sem_iva": 150.00,
  "valor_com_iva": 184.50,
  "estado": "PAGO",
  "data": "2025-01-31"
}
```

Transaction TaxHacker:
```json
{
  "id": "uuid-generated",
  "userId": "bruno-uuid",
  "type": "expense",
  "name": "Contabilidade - Janeiro 2025",
  "total": -15000,
  "categoryCode": "FIXA_MENSAL",
  "issuedAt": "2025-01-31T00:00:00Z",
  "extra": {
    "numero_despesa": "#D000001",
    "valor_com_iva": 18450,
    "estado_pagamento": "PAGO",
    "fornecedor_id": 1,
    "fornecedor_nome": "Silva Contabilidade"
  }
}
```

NOTA: `total: -15000` = NEGATIVO! 150.00 EUR × 100 cêntimos
NOTA: `valor_com_iva: 18450` = 184.50 × 100 também em cêntimos

==================================================
MAPEAMENTO REAL: BOLETIM → TRANSACTION
==================================================

```
Boletim Python                →  TaxHacker Transaction
----------------------------------------
id                            →  id (novo UUID)
numero (#B0001)               →  extra.numero_boletim
socio (enum)                  →  extra.socio
  - BRUNO                        → 'BRUNO'
  - RAFAEL                       → 'RAFAEL'

descricao                     →  name
valor                         →  total (NEGATIVO, x100)
data_emissao                  →  issuedAt
estado                        →  categoryCode
  - PENDENTE                     → 'BOLETIM_PENDENTE'
  - PAGO                         → 'BOLETIM_PAGO'

data_pagamento                →  extra.data_pagamento
nota                          →  note

type (fixo)                   →  'expense'
categoryCode                  →  'BOLETIM'
userId                        →  ID do sócio
```

EXEMPLO CONCRETO:
----------------------------------------

Boletim Python:
```json
{
  "id": 1,
  "numero": "#B0001",
  "socio": "BRUNO",
  "valor": 600.00,
  "descricao": "Ajudas de custo - Janeiro",
  "estado": "PAGO",
  "data_emissao": "2025-01-31",
  "data_pagamento": "2025-02-05"
}
```

Transaction TaxHacker:
```json
{
  "id": "uuid-generated",
  "userId": "bruno-uuid",
  "type": "expense",
  "name": "Ajudas de custo - Janeiro",
  "total": -60000,
  "categoryCode": "BOLETIM",
  "issuedAt": "2025-01-31T00:00:00Z",
  "extra": {
    "numero_boletim": "#B0001",
    "socio": "BRUNO",
    "estado_boletim": "PAGO",
    "data_pagamento": "2025-02-05"
  }
}
```

NOTA: `total: -60000` = NEGATIVO! 600 EUR × 100 cêntimos

==================================================
ENTIDADES QUE NÃO EXISTEM NO TAXHACKER
==================================================

EQUIPAMENTO:
----------------------------------------

❌ NÃO existe modelo Equipment no TaxHacker
✅ CRIAR NOVO modelo no Prisma:

```prisma
model Equipment {
  id            String   @id @default(uuid()) @db.Uuid
  userId        String   @map("user_id") @db.Uuid
  user          User     @relation(fields: [userId], references: [id])
  
  name          String
  category      String
  purchaseDate  DateTime @map("purchase_date")
  purchasePrice Int      @map("purchase_price")   // cêntimos
  lifeYears     Int      @map("life_years")
  currentValue  Int      @map("current_value")    // cêntimos
  
  note          String?
  createdAt     DateTime @default(now()) @map("created_at")
  updatedAt     DateTime @updatedAt @map("updated_at")
  
  @@map("equipment")
}
```

ORÇAMENTOS:
----------------------------------------

❌ NÃO existe modelo Budget no TaxHacker
✅ CRIAR NOVO modelo no Prisma:

```prisma
model Budget {
  id          String       @id @default(uuid()) @db.Uuid
  userId      String       @map("user_id") @db.Uuid
  user        User         @relation(fields: [userId], references: [id])
  
  numero      String       @unique
  description String?
  clienteName String?      @map("cliente_name")
  clienteNIF  String?      @map("cliente_nif")
  
  subtotal    Int                          // cêntimos
  iva         Int
  total       Int
  
  status      BudgetStatus @default(DRAFT)
  validUntil  DateTime     @map("valid_until")
  approvedAt  DateTime?    @map("approved_at")
  
  // Quando converter em projeto
  convertedToTransactionId String? @unique @map("converted_to_transaction_id")
  
  items       BudgetItem[]
  createdAt   DateTime     @default(now()) @map("created_at")
  updatedAt   DateTime     @updatedAt @map("updated_at")
  
  @@map("budgets")
}

model BudgetItem {
  id          String    @id @default(uuid()) @db.Uuid
  budgetId    String    @map("budget_id") @db.Uuid
  budget      Budget    @relation(fields: [budgetId], references: [id])
  
  description String
  quantity    Int
  unitPrice   Int       @map("unit_price")  // cêntimos
  total       Int                           // quantity * unitPrice
  
  // Opcional: linkar a equipamento
  equipmentId String?   @map("equipment_id") @db.Uuid
  
  @@map("budget_items")
}

enum BudgetStatus {
  DRAFT
  SENT
  APPROVED
  REJECTED
  CONVERTED
}
```

==================================================
CUSTOM FIELDS A CRIAR NO TAXHACKER
==================================================

IMPORTANTE: TaxHacker já tem sistema de Custom Fields!
Criar via UI ou seed script:

```typescript
// 1. premio_bruno
{
  code: "premio_bruno",
  type: "number",
  name: "Prémio Bruno",
  isVisibleInList: true
}

// 2. premio_rafael
{
  code: "premio_rafael",
  type: "number",
  name: "Prémio Rafael",
  isVisibleInList: true
}

// 3. socio
{
  code: "socio",
  type: "select",
  options: { values: ["BRUNO", "RAFAEL"] },
  name: "Sócio",
  isRequired: true  // para boletins
}

// 4. cliente_nome
{
  code: "cliente_nome",
  type: "string",
  name: "Cliente"
}

// 5. cliente_nif
{
  code: "cliente_nif",
  type: "string",
  name: "NIF Cliente"
}

// 6. fornecedor_nome
{
  code: "fornecedor_nome",
  type: "string",
  name: "Fornecedor"
}

// 7. estado_pagamento
{
  code: "estado_pagamento",
  type: "select",
  options: { values: ["PENDENTE", "PAGO"] },
  name: "Estado Pagamento"
}
```

==================================================
CATEGORIES E PROJECTS A CRIAR
==================================================

PROJECTS (via seed ou UI):
----------------------------------------

```typescript
// Projeto 1
{
  code: 'EMPRESA',
  name: 'Agora Media',
  color: '#10b981'
}

// Projeto 2
{
  code: 'PESSOAL_BRUNO',
  name: 'Projetos Bruno',
  color: '#3b82f6'
}

// Projeto 3
{
  code: 'PESSOAL_RAFAEL',
  name: 'Projetos Rafael',
  color: '#8b5cf6'
}
```

CATEGORIES (via seed):
----------------------------------------

```typescript
// ========================================
// ESTADOS DE PROJETO
// ========================================

{
  code: 'NAO_FATURADO',
  name: 'Não Faturado',
  color: '#9ca3af'
}

{
  code: 'FATURADO',
  name: 'Faturado',
  color: '#f59e0b'
}

{
  code: 'RECEBIDO',
  name: 'Recebido',
  color: '#22c55e'
}

// ========================================
// TIPOS DE DESPESA
// ========================================

{
  code: 'FIXA_MENSAL',
  name: 'Despesa Fixa',
  color: '#ef4444'
}

{
  code: 'DESPESA_PESSOAL_BRUNO',
  name: 'Despesa Pessoal Bruno',
  color: '#3b82f6'
}

{
  code: 'DESPESA_PESSOAL_RAFAEL',
  name: 'Despesa Pessoal Rafael',
  color: '#8b5cf6'
}

{
  code: 'DESPESA_EQUIPAMENTO',
  name: 'Equipamento',
  color: '#6366f1'
}

{
  code: 'DESPESA_PROJETO',
  name: 'Despesa de Projeto',
  color: '#f97316'
}

// ========================================
// BOLETINS
// ========================================

{
  code: 'BOLETIM',
  name: 'Boletim',
  color: '#ec4899'
}
```

==================================================
VALIDAÇÃO: VALORES MONETÁRIOS
==================================================

⚠️ CRÍTICO: TaxHacker usa CÊNTIMOS (Int)

CONVERSÃO CORRECTA:
```
Python Decimal(1500.00) → TaxHacker 150000
```

FÓRMULA:
```javascript
valor_taxhacker = int(valor_python * 100)
```

EXEMPLOS:
```
1500.00 EUR → 150000
  23.50 EUR →   2350
   0.99 EUR →     99
```

DESPESAS SÃO NEGATIVAS:
```
150.00 EUR → -15000
```

==================================================
