# Database Manual Changes - History & Scripts

**Last Updated:** 2025-12-29
**Status:** ✅ Complete

---

## Overview

Este documento regista todas as alterações manuais feitas à database que **não** foram aplicadas via Django migrations.

⚠️ **Importante:** Estas alterações foram necessárias porque a migration 0004 teve de ser `--fake`'ed devido a tabelas já existentes.

---

## Context: Why Manual Changes Were Needed

### The Problem

**Migration 0004** (`agora_web/core/migrations/0004_*.py`) incluía:
1. ✅ Criação do modelo `Socio` (novo)
2. ❌ Criação dos modelos `Equipamento` e `Orcamento` (já existiam!)

Quando tentámos aplicar a migration:
```bash
python manage.py migrate core 0004
```

**Erro:**
```
django.db.utils.ProgrammingError: relation "equipamento" already exists
```

### The Solution

**Step 1:** Fake the entire migration to skip the error
```bash
python manage.py migrate core 0004 --fake
```

**Consequência:** Isto marcou a migration como aplicada, mas **não executou nada** - incluindo a criação da tabela `socios`!

**Step 2:** Criar manualmente todas as mudanças que a migration faria
- Criar tabela `socios`
- Adicionar colunas FK `socio_id` a `projetos`, `boletins`, `orcamentos`

---

## Manual Change 1: Create Socios Table

### File: `scripts/create_socios_table.sql`

```sql
-- Criar tabela de sócios
CREATE TABLE IF NOT EXISTS socios (
    codigo VARCHAR(2) PRIMARY KEY,
    nome_completo VARCHAR(100) NOT NULL,
    nome_curto VARCHAR(50) NOT NULL,
    email VARCHAR(254) NOT NULL,
    telefone VARCHAR(50) DEFAULT '' NOT NULL,
    percentagem_participacao NUMERIC(5,2) DEFAULT 50.00 NOT NULL,
    ativo BOOLEAN DEFAULT true NOT NULL,
    cor_tema VARCHAR(7) DEFAULT '#1976d2',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Inserir sócios iniciais
INSERT INTO socios (codigo, nome_completo, nome_curto, email, percentagem_participacao, ativo, cor_tema)
VALUES
    ('BA', 'Bruno Amaral', 'Bruno', 'bruno@agoramediaproduction.pt', 50.00, true, '#1976d2'),
    ('RR', 'Rafael Reigota', 'Rafael', 'rafael@agoramediaproduction.pt', 50.00, true, '#f57c00')
ON CONFLICT (codigo) DO NOTHING;

-- Criar índices
CREATE INDEX IF NOT EXISTS idx_socios_ativo ON socios(ativo);
CREATE INDEX IF NOT EXISTS idx_socios_email ON socios(email);
```

### Execution

```bash
# Copy script to container
docker cp scripts/create_socios_table.sql agora_db:/tmp/

# Execute in PostgreSQL
docker compose -f docker-compose.cloudflare.yml exec db \
  psql -U agora_user -d agora_db -f /tmp/create_socios_table.sql
```

**Result:**
```
CREATE TABLE
INSERT 0 2
CREATE INDEX
CREATE INDEX
```

### Important Notes

1. **Table name:** `socios` (not `core_socio`) - matches `Meta.db_table` in model
2. **VARCHAR lengths:** Match Django field max_length exactly
3. **TIMESTAMP WITH TIME ZONE:** PostgreSQL equivalent of Django's DateTimeField
4. **ON CONFLICT DO NOTHING:** Idempotent - safe to run multiple times

---

## Manual Change 2: Add Foreign Key Columns

### File: `scripts/add_socio_fk_columns.sql`

```sql
-- Add socio_id FK column to projetos
ALTER TABLE projetos
ADD COLUMN IF NOT EXISTS socio_id VARCHAR(2)
REFERENCES socios(codigo) ON DELETE RESTRICT;

-- Add socio_id FK column to boletins
ALTER TABLE boletins
ADD COLUMN IF NOT EXISTS socio_id VARCHAR(2)
REFERENCES socios(codigo) ON DELETE RESTRICT;

-- Add socio_id FK column to orcamentos
ALTER TABLE orcamentos
ADD COLUMN IF NOT EXISTS socio_id VARCHAR(2)
REFERENCES socios(codigo) ON DELETE RESTRICT;

-- Create indexes for FK columns (performance)
CREATE INDEX IF NOT EXISTS idx_projetos_socio ON projetos(socio_id);
CREATE INDEX IF NOT EXISTS idx_boletins_socio ON boletins(socio_id);
CREATE INDEX IF NOT EXISTS idx_orcamentos_socio ON orcamentos(socio_id);
```

### PostgreSQL vs Django: ON DELETE

⚠️ **Critical Difference:**

| Django | PostgreSQL |
|--------|------------|
| `on_delete=models.PROTECT` | `ON DELETE RESTRICT` |
| (Not valid in SQL) | (Correct SQL syntax) |

**Why RESTRICT?**
- PostgreSQL doesn't have `PROTECT` keyword
- `RESTRICT` provides same behavior: prevents deletion if FK references exist
- Django's `PROTECT` is a Python-level concept, translated to `RESTRICT` in SQL

**Initial Error:**
```sql
ALTER TABLE projetos ADD COLUMN socio_id ... ON DELETE PROTECT;
-- ERROR:  syntax error at or near "PROTECT"
```

**Fixed:**
```sql
ALTER TABLE projetos ADD COLUMN socio_id ... ON DELETE RESTRICT;
-- SUCCESS
```

### Execution

```bash
# Copy script to container
docker cp scripts/add_socio_fk_columns.sql agora_db:/tmp/

# Execute in PostgreSQL
docker compose -f docker-compose.cloudflare.yml exec db \
  psql -U agora_user -d agora_db -f /tmp/add_socio_fk_columns.sql
```

**Result:**
```
ALTER TABLE
ALTER TABLE
ALTER TABLE
CREATE INDEX
CREATE INDEX
CREATE INDEX
```

### Verification

```sql
-- Check columns were added
\d projetos
-- Should show: socio_id | character varying(2) |

-- Check FK constraints
SELECT conname, conrelid::regclass, confrelid::regclass
FROM pg_constraint
WHERE contype = 'f' AND conname LIKE '%socio%';

-- Should show:
-- projetos_socio_id_fkey    | projetos   | socios
-- boletins_socio_id_fkey    | boletins   | socios
-- orcamentos_socio_id_fkey  | orcamentos | socios
```

---

## Manual Change 3: Data Migration

After creating the table and columns, we migrated existing data using Django management command.

### File: `agora_web/core/management/commands/migrate_socios.py`

**Execution:**
```bash
docker compose -f docker-compose.cloudflare.yml exec web \
  python manage.py migrate_socios
```

**Results:**
```
Migrating Projetos...
  Updated 45 projetos for BA
  Updated 36 projetos for RR
  Total: 81 projetos migrated

Migrating Boletins...
  Updated 18 boletins for BA
  Updated 19 boletins for RR
  Total: 37 boletins migrated

Migrating Orcamentos...
  Updated 1 orcamento for BA
  Updated 0 orcamentos for RR
  Total: 1 orcamento migrated
```

**What it did:**
- Set `socio_id='BA'` where `owner='BA'` (for Projetos)
- Set `socio_id='RR'` where `owner='RR'` (for Projetos)
- Set `socio_id='BA'` where `socio_codigo='BA'` (for Boletins)
- Set `socio_id='RR'` where `socio_codigo='RR'` (for Boletins)
- Same for Orcamentos

---

## Verification & Testing

### 1. Table Exists
```sql
SELECT tablename FROM pg_tables WHERE tablename = 'socios';
-- socios
```

### 2. Data Populated
```sql
SELECT codigo, nome_completo, email FROM socios;
-- BA | Bruno Amaral    | bruno@agoramediaproduction.pt
-- RR | Rafael Reigota  | rafael@agoramediaproduction.pt
```

### 3. Foreign Keys Work
```sql
SELECT p.numero, p.descricao, s.nome_completo
FROM projetos p
JOIN socios s ON p.socio_id = s.codigo
LIMIT 5;
-- Should show projects with partner names
```

### 4. Django ORM Works
```python
from core.models import Socio, Projeto

# Query socios
Socio.objects.all()
# <QuerySet [<Socio: BA>, <Socio: RR>]>

# Query projects with FK
Projeto.objects.filter(socio='BA').count()
# 45

# Join query
projeto = Projeto.objects.select_related('socio').first()
print(f"{projeto.numero} - {projeto.socio.nome_completo}")
# 001 - Bruno Amaral
```

---

## Future Migration Strategy

To avoid this issue in the future:

### Option 1: Squash Migrations (Recommended)
```bash
# Squash all core migrations into one
python manage.py squashmigrations core 0001 0010

# Creates a new migration that replaces 0001-0010
# Test thoroughly before deploying!
```

**Pros:**
- ✅ Cleaner migration history
- ✅ Faster initial setup for new databases

**Cons:**
- ⚠️ Can't rollback to intermediate states
- ⚠️ Requires careful testing

### Option 2: Separate Apps
```bash
# Move Equipamento to separate app
python manage.py startapp equipamentos

# Move model and create new migrations
# Avoids conflicts in future
```

**Pros:**
- ✅ Better separation of concerns
- ✅ Easier to manage large projects

**Cons:**
- ⚠️ More complex initial setup
- ⚠️ Requires refactoring existing code

### Option 3: Better Migration Discipline
- ✅ Always test migrations in staging first
- ✅ Never manually create tables in production DB
- ✅ Use `--plan` to review migrations before applying
- ✅ Keep migrations small and focused

---

## Rollback Plan

If needed to rollback these changes:

### 1. Drop Foreign Keys
```sql
ALTER TABLE projetos DROP CONSTRAINT IF EXISTS projetos_socio_id_fkey;
ALTER TABLE boletins DROP CONSTRAINT IF EXISTS boletins_socio_id_fkey;
ALTER TABLE orcamentos DROP CONSTRAINT IF EXISTS orcamentos_socio_id_fkey;
```

### 2. Drop Columns
```sql
ALTER TABLE projetos DROP COLUMN IF EXISTS socio_id;
ALTER TABLE boletins DROP COLUMN IF EXISTS socio_id;
ALTER TABLE orcamentos DROP COLUMN IF EXISTS socio_id;
```

### 3. Drop Table
```sql
DROP TABLE IF EXISTS socios CASCADE;
```

### 4. Un-fake Migration
```sql
DELETE FROM django_migrations WHERE app = 'core' AND name = '0004_*';
```

### 5. Update Code
```bash
git revert <commit-hash>
```

---

## Lessons Learned

1. ⚠️ **Always check production DB** before running migrations
2. ⚠️ **Never assume migrations are idempotent** - they can fail halfway
3. ⚠️ **Faking migrations** should be last resort - creates debt
4. ✅ **Manual SQL is acceptable** when migrations fail in production
5. ✅ **PostgreSQL vs Django differences** - know the translation (PROTECT→RESTRICT)
6. ✅ **Document everything** - future you (or others) will thank you
7. ✅ **Test in shell** before applying to production
8. ✅ **Idempotent scripts** (IF NOT EXISTS, ON CONFLICT) are safer

---

## Appendix: Full SQL Execution Log

```bash
# Session log from 2025-12-29

# 1. Create socios table
postgres=# CREATE TABLE IF NOT EXISTS socios (...);
CREATE TABLE

# 2. Insert initial data
postgres=# INSERT INTO socios (codigo, nome_completo, ...) VALUES ...;
INSERT 0 2

# 3. Verify data
postgres=# SELECT * FROM socios;
 codigo | nome_completo   | nome_curto | email                          | ...
--------+-----------------+------------+--------------------------------+-----
 BA     | Bruno Amaral    | Bruno      | bruno@agoramediaproduction.pt  | ...
 RR     | Rafael Reigota  | Rafael     | rafael@agoramediaproduction.pt | ...

# 4. Add FK columns
postgres=# ALTER TABLE projetos ADD COLUMN socio_id VARCHAR(2) ...;
ALTER TABLE

postgres=# ALTER TABLE boletins ADD COLUMN socio_id VARCHAR(2) ...;
ALTER TABLE

postgres=# ALTER TABLE orcamentos ADD COLUMN socio_id VARCHAR(2) ...;
ALTER TABLE

# 5. Create indexes
postgres=# CREATE INDEX idx_projetos_socio ON projetos(socio_id);
CREATE INDEX

# 6. Verify constraints
postgres=# \d projetos
                                     Table "public.projetos"
    Column    |          Type          |                       Modifiers
--------------+------------------------+-------------------------------------------------------
 ...
 socio_id     | character varying(2)   |
Indexes:
    "idx_projetos_socio" btree (socio_id)
Foreign-key constraints:
    "projetos_socio_id_fkey" FOREIGN KEY (socio_id) REFERENCES socios(codigo) ON DELETE RESTRICT

# SUCCESS!
```

---

**Documentation by:** Claude Code
**Last Updated:** 2025-12-29
