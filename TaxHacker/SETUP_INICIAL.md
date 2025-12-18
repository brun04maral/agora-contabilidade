===============================================================================
SETUP INICIAL: Guia Passo-a-Passo para Fork e Configuração
Instruções detalhadas para começar o desenvolvimento
===============================================================================

==================================================
PRÉ-REQUISITOS
==================================================

SOFTWARE NECESSÁRIO:
--------------------
□ Node.js 20+ (verificar: `node --version`)
□ npm 10+ (verificar: `npm --version`)
□ Git (verificar: `git --version`)
□ PostgreSQL 16+ (local ou remoto)
□ Editor de código (recomendado: VSCode)
□ Docker Desktop (opcional, para produção)

CONTAS/SERVIÇOS:
--------------------
□ Conta GitHub (para fork)
□ Conta TOConline (para API, pode esperar Fase 4)
□ Servidor PostgreSQL (local ou cloud)

CONHECIMENTO RECOMENDADO:
--------------------
⚠️ TypeScript básico
⚠️ React/Next.js (útil mas não obrigatório)
✅ SQL/Prisma (aprende-se facilmente)

==================================================
PASSO 1: FORK DO REPOSITÓRIO
==================================================

1.1 FORK NO GITHUB
--------------------

Via Browser:
1. Ir para: https://github.com/vas3k/TaxHacker
2. Clicar "Fork" (canto superior direito)
3. Owner: selecionar "brun04maral" (ou tua conta)
4. Repository name: "agora-contabilidade"
5. Description: "Sistema de Contabilidade Agora Media (baseado TaxHacker)"
6. ✓ Desmarcar "Copy the main branch only" (queremos histórico completo)
7. Clicar "Create fork"

Resultado:
✅ Tens fork em: github.com/brun04maral/agora-contabilidade

1.2 CLONE LOCAL
--------------------

Terminal:
```bash
# Navegar para pasta de projetos
cd ~/Projects

# Clonar fork
git clone https://github.com/brun04maral/agora-contabilidade.git
cd agora-contabilidade

# Confirmar remote
git remote -v
# origin https://github.com/brun04maral/agora-contabilidade.git (fetch)
# origin https://github.com/brun04maral/agora-contabilidade.git (push)
```

Adicionar upstream (TaxHacker original) - OPCIONAL:
```bash
# Só se quiseres poder fazer cherry-pick de updates futuros
git remote add upstream https://github.com/vas3k/TaxHacker.git
```

1.3 BRANCH STRATEGY
--------------------

DECISÃO: Trabalhar direto na main OU criar branches?

Opção A: Main direto (mais simples, só 2 devs)
```bash
# Trabalham direto na main
git checkout main

# fazer mudanças
git commit -m "feat: adicionar saldos"
git push origin main
```

Opção B: Feature branches (mais organizado)
```bash
# Criar branch por feature
git checkout -b feature/saldos

# fazer mudanças
git commit -m "feat: implementar cálculo saldos"
git push origin feature/saldos

# Criar PR no GitHub
# Merge depois de review
```

RECOMENDAÇÃO: Opção A para começar, migrar para B se necessário

==================================================
PASSO 2: INSTALAR DEPENDÊNCIAS
==================================================

2.1 INSTALAR PACOTES NPM
--------------------

```bash
# Instalar todas as dependências do package.json
npm install

# Aguardar... (pode demorar 2-3 minutos)
# Deve terminar sem erros
```

Verificar instalação:
```bash
npm list --depth=0
```

Dependências principais instaladas:
✅ next@15.2.4
✅ react@19.0.0
✅ prisma@6.6.0
✅ @prisma/client@6.6.0
✅ typescript@5
✅ tailwindcss@3.4.1

2.2 VERIFICAR NODE_MODULES
--------------------

```bash
ls node_modules | wc -l
# Deve ter ~1000+ packages
```

Se houver erros:
```bash
# Limpar e reinstalar
rm -rf node_modules package-lock.json
npm install
```

==================================================
PASSO 3: CONFIGURAR AMBIENTE
==================================================

3.1 CRIAR FICHEIRO .env
--------------------

```bash
# Copiar exemplo
cp .env.example .env

# Editar com editor
nano .env
# ou
code .env
```

3.2 CONFIGURAR VARIÁVEIS .env
--------------------

```bash
================================
# DATABASE
================================
# OPÇÃO A: PostgreSQL Local
DATABASE_URL="postgresql://postgres:password@localhost:5432/agora_contabilidade"

# OPÇÃO B: PostgreSQL Cloud (Supabase/Railway/Neon)
# DATABASE_URL="postgresql://user:pass@host:5432/dbname"

================================
# APP
================================
PORT=7331
BASE_URL="http://localhost:7331"

# Self-hosted mode (permite custom API keys, auto-login dev)
SELF_HOSTED_MODE=true

# Desabilitar signup público (só Bruno e Rafael)
DISABLE_SIGNUP=true

================================
# AUTH
================================
# Gerar secret aleatório (min 16 chars):
# node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"
BETTER_AUTH_SECRET="cole-aqui-o-secret-gerado"

================================
# UPLOADS
================================
UPLOAD_PATH="./data/uploads"

================================
# EMAIL (OPCIONAL - Fase 4)
================================
# Resend API Key (para enviar emails)
# RESEND_API_KEY="re_..."

================================
# TOCONLINE (FASE 4)
================================
# TOConline API Key (configurar depois)
# TOCONLINE_API_KEY="toc_..."

================================
# AI/LLM (NÃO USAR - Features desnecessárias)
================================
OPENAI_API_KEY=""
GOOGLE_API_KEY=""
MISTRAL_API_KEY=""
```

GERAR BETTER_AUTH_SECRET:
```bash
node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"
# Copiar output para .env
```

3.3 CRIAR DATABASE
--------------------

OPÇÃO A: PostgreSQL Local (Mac)
```bash
# Instalar PostgreSQL (se ainda não tens)
brew install postgresql@16
brew services start postgresql@16

# Criar database
psql postgres
```

```sql
CREATE DATABASE agora_contabilidade;
CREATE USER agora_user WITH PASSWORD 'secure_password_123';
GRANT ALL PRIVILEGES ON DATABASE agora_contabilidade TO agora_user;
\q
```

Actualizar .env:
```bash
DATABASE_URL="postgresql://agora_user:secure_password_123@localhost:5432/agora_contabilidade"
```

OPÇÃO B: PostgreSQL Local (Linux)
```bash
sudo apt-get install postgresql-16
sudo systemctl start postgresql

sudo -u postgres psql
```

```sql
CREATE DATABASE agora_contabilidade;
CREATE USER agora_user WITH PASSWORD 'secure_password_123';
GRANT ALL PRIVILEGES ON DATABASE agora_contabilidade TO agora_user;
\q
```

OPÇÃO C: PostgreSQL Cloud (Supabase)
1. Ir para: https://supabase.com
2. Criar novo projeto
3. Nome: "agora-contabilidade"
4. Database password: criar senha forte
5. Region: Europe (Frankfurt)
6. Aguardar provisioning (~2 min)
7. Settings → Database → Connection string
8. Copiar "URI" para .env

OPÇÃO D: Docker PostgreSQL
```bash
docker run -d \
  --name agora-postgres \
  -e POSTGRES_DB=agora_contabilidade \
  -e POSTGRES_USER=agora_user \
  -e POSTGRES_PASSWORD=secure_password_123 \
  -p 5432:5432 \
  -v pgdata:/var/lib/postgresql/data \
  postgres:16

# Actualizar .env
DATABASE_URL="postgresql://agora_user:secure_password_123@localhost:5432/agora_contabilidade"
```

==================================================
PASSO 4: INICIALIZAR DATABASE
==================================================

4.1 GERAR PRISMA CLIENT
--------------------

```bash
npx prisma generate

# Output esperado:
# ✔ Generated Prisma Client
```

Isto cria tipos TypeScript baseados no schema.prisma

4.2 RODAR MIGRATIONS
--------------------

```bash
npx prisma migrate dev --name initial_setup

# Output esperado:
# Applying migration `20251218000000_initial_setup`
# ✔ Generated Prisma Client
# Database synchronized with Prisma schema.
```

Isto cria todas as tabelas no PostgreSQL.

4.3 VERIFICAR TABELAS
--------------------

Abrir Prisma Studio (GUI para ver dados):
```bash
npx prisma studio

# Abre browser em http://localhost:5555
# Deves ver modelos:
# - User
# - Transaction
# - Category
# - Project
# - Field
# - File
# - etc.
```

OU verificar via psql:
```bash
psql $DATABASE_URL

\dt          # Lista todas as tabelas
\d users     # Descreve estrutura tabela users
\q           # Sair
```

==================================================
PASSO 5: SEED INICIAL (OPCIONAL)
==================================================

5.1 CRIAR FICHEIRO SEED
--------------------

Ficheiro: `prisma/seed.ts`

```typescript
import { PrismaClient } from '@prisma/client'

const prisma = new PrismaClient()

async function main() {
  console.log('🌱 Seeding database...')
  
  // Criar categories Agora Media
  const categories = [
    { code: 'RECEBIDO', name: 'Recebido', color: '#22c55e' },
    { code: 'FATURADO', name: 'Faturado', color: '#f59e0b' },
    { code: 'NAO_FATURADO', name: 'Não Faturado', color: '#9ca3af' },
    { code: 'FIXA_MENSAL', name: 'Despesa Fixa', color: '#ef4444' },
    { code: 'DESPESA_PESSOAL_BRUNO', name: 'Despesa Bruno', color: '#3b82f6' },
    { code: 'DESPESA_PESSOAL_RAFAEL', name: 'Despesa Rafael', color: '#8b5cf6' },
    { code: 'BOLETIM', name: 'Boletim', color: '#ec4899' }
  ]
  
  for (const cat of categories) {
    await prisma.category.upsert({
      where: { userId_code: { userId: 'system', code: cat.code } },
      update: {},
      create: {
        userId: 'system', // placeholder, actualizar depois
        ...cat
      }
    })
  }
  
  console.log('✅ Categories criadas')
  
  // Criar projects
  const projects = [
    { code: 'EMPRESA', name: 'Agora Media', color: '#10b981' },
    { code: 'PESSOAL_BRUNO', name: 'Projetos Bruno', color: '#3b82f6' },
    { code: 'PESSOAL_RAFAEL', name: 'Projetos Rafael', color: '#8b5cf6' }
  ]
  
  for (const proj of projects) {
    await prisma.project.upsert({
      where: { userId_code: { userId: 'system', code: proj.code } },
      update: {},
      create: {
        userId: 'system',
        ...proj
      }
    })
  }
  
  console.log('✅ Projects criados')
  console.log('🎉 Seed completo!')
}

main()
  .catch((e) => {
    console.error(e)
    process.exit(1)
  })
  .finally(async () => {
    await prisma.$disconnect()
  })
```

5.2 CONFIGURAR PACKAGE.JSON
--------------------

Adicionar ao `package.json`:

```json
{
  "prisma": {
    "seed": "ts-node --compiler-options {\"module\":\"CommonJS\"} prisma/seed.ts"
  }
}
```

Instalar ts-node:
```bash
npm install -D ts-node
```

5.3 RODAR SEED
--------------------

```bash
npx prisma db seed

# Output:
# 🌱 Seeding database...
# ✅ Categories criadas
# ✅ Projects criados
# 🎉 Seed completo!
```

==================================================
PASSO 6: RODAR APLICAÇÃO
==================================================

6.1 MODO DESENVOLVIMENTO
--------------------

```bash
npm run dev

# Output esperado:
# ▲ Next.js 15.2.4
# - Local:        http://localhost:7331
# - Environments: .env
# ✓ Ready in 3.2s
```

6.2 ABRIR BROWSER
--------------------

Navegar para: http://localhost:7331

Deve aparecer:
- Landing page do TaxHacker (se não autenticado)
- Login screen

6.3 CRIAR PRIMEIRO USER
--------------------

Se `DISABLE_SIGNUP=false`:
- Clicar "Sign up"
- Email: bruno@agoramedia.pt
- Password: (criar senha segura)
- Name: Bruno Amaral

Se `DISABLE_SIGNUP=true`:
- Criar via Prisma Studio ou SQL:

```sql
-- Abrir psql
psql $DATABASE_URL

-- Criar user
INSERT INTO users (id, email, name, created_at, updated_at)
VALUES (
  gen_random_uuid(),
  'bruno@agoramedia.pt',
  'Bruno Amaral',
  NOW(),
  NOW()
);

-- Criar account (password hash)
-- Usar bcrypt online para gerar hash de "bruno123"
-- https://bcrypt-generator.com/
INSERT INTO account (id, account_id, provider_id, user_id, password)
VALUES (
  gen_random_uuid(),
  'bruno@agoramedia.pt',
  'credential',
  (SELECT id FROM users WHERE email = 'bruno@agoramedia.pt'),
  '$2a$10$...' -- cole hash aqui
);
```

OU usar Better Auth CLI (se disponível):
```bash
npx better-auth create-user \
  --email bruno@agoramedia.pt \
  --password bruno123 \
  --name "Bruno Amaral"
```

6.4 FAZER LOGIN
--------------------

- Email: bruno@agoramedia.pt
- Password: (a que criaste)

Deve entrar no dashboard TaxHacker.

==================================================
PASSO 7: VERIFICAR INSTALAÇÃO
==================================================

CHECKLIST:
--------------------

□ App rodando em http://localhost:7331
□ Consegues fazer login
□ Dashboard carrega sem erros
□ Prisma Studio funciona (`npx prisma studio`)
□ Podes criar transaction teste na UI
□ Navegação funciona (sidebar)
□ Não há erros no terminal

TROUBLESHOOTING COMUM:
--------------------

ERRO: "Can't reach database server"
→ Verificar DATABASE_URL no .env
→ Confirmar PostgreSQL está a correr
→ Testar conexão: `psql $DATABASE_URL`

ERRO: "BETTER_AUTH_SECRET must be at least 16 characters"
→ Gerar novo secret (ver Passo 3.2)

ERRO: "Port 7331 is already in use"
→ Mudar PORT no .env
→ OU matar processo: `lsof -ti:7331 | xargs kill`

ERRO: Prisma Client não encontrado
→ Rodar: `npx prisma generate`

==================================================
PASSO 8: COMMIT INICIAL
==================================================

8.1 ADICIONAR .gitignore
--------------------

Verificar `.gitignore` tem:
```
node_modules/
.env
.env.local
.next/
data/uploads/
*.log
.DS_Store
prisma/client/
```

8.2 COMMIT SETUP
--------------------

```bash
# Ver mudanças
git status

# Adicionar ficheiros
git add .env.example
git add prisma/seed.ts  # se criaste
git add package.json package-lock.json  # se modificaste

# Commit
git commit -m "chore: setup inicial Agora Contabilidade

- Configurar .env.example
- Adicionar seed categories/projects
- Actualizar README com instruções específicas"

# Push
git push origin main
```

==================================================
PASSO 9: PREPARAR REMOVER FEATURES DESNECESSÁRIAS
==================================================

OPCIONAL mas recomendado: Limpar código TaxHacker que não vão usar

9.1 FEATURES A REMOVER/DESABILITAR
--------------------

□ AI/LLM Processing (`lib/llm-providers.ts`)
  - Comentar imports
  - Desabilitar na UI

□ Stripe Billing (`lib/stripe.ts`)
  - Remover routes `/api/stripe`
  - Remover da UI

□ Landing Page Pública (`app/landing/`)
  - Substituir por redirect para `/login`

□ OCR Document Parsing
  - Manter código mas não usar

DECISÃO: Fazer agora OU depois?
→ RECOMENDAÇÃO: Depois, na Fase 0 do Roadmap

9.2 FEATURES A MANTER
--------------------

✅ Transactions (core)
✅ Categories & Projects
✅ Custom Fields
✅ File uploads
✅ Export CSV
✅ Auth (Better Auth)
✅ Email (Resend)

==================================================
PASSO 10: PRÓXIMOS PASSOS
==================================================

AGORA TENS:
✅ Fork TaxHacker configurado
✅ Database PostgreSQL a correr
✅ App funcional em localhost
✅ User criado e podes fazer login

PRÓXIMO:
→ Ver ROADMAP_IMPLEMENTACAO.md
→ Começar Fase 1: Migração de Dados
→ Ou experimentar criar transactions teste na UI

RECURSOS ÚTEIS:
--------------------

Prisma Docs: https://www.prisma.io/docs
Next.js Docs: https://nextjs.org/docs
TaxHacker Issues: https://github.com/vas3k/TaxHacker/issues
TypeScript Handbook: https://www.typescriptlang.org/docs/

==================================================
CONFIGURAÇÃO DOCKER (OPCIONAL)
==================================================

Para produção self-hosted:

10.1 DOCKER COMPOSE
--------------------

Ficheiro: `docker-compose.yml` (já existe no TaxHacker)

Modificar:
```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "7331:7331"
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/agora_contabilidade
      - SELF_HOSTED_MODE=true
      - BETTER_AUTH_SECRET=${BETTER_AUTH_SECRET}
      - UPLOAD_PATH=/app/data/uploads
    volumes:
      - ./data:/app/data
    depends_on:
      - db
    restart: unless-stopped

  db:
    image: postgres:16
    environment:
      - POSTGRES_DB=agora_contabilidade
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
    volumes:
      - pgdata:/var/lib/postgresql/data
    restart: unless-stopped

volumes:
  pgdata:
```

10.2 RODAR COM DOCKER
--------------------

```bash
# Build
docker-compose build

# Start
docker-compose up -d

# Ver logs
docker-compose logs -f app

# Parar
docker-compose down
```

10.3 DEPLOY RASPBERRY PI
--------------------

1. SSH para Raspberry Pi
```bash
ssh pi@192.168.1.100
```

2. Instalar Docker
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker pi
```

3. Clone repo
```bash
git clone https://github.com/brun04maral/agora-contabilidade.git
cd agora-contabilidade
```

4. Configurar .env
```bash
cp .env.example .env
nano .env
# Preencher variáveis
```

5. Deploy
```bash
docker-compose up -d
```

6. Aceder
- Local: http://192.168.1.100:7331
- Ou configurar domínio/nginx

==================================================
SUPPORT & AJUDA
==================================================

Se tiveres problemas durante setup:

1. Verificar logs:
```bash
npm run dev  # ver output terminal
docker-compose logs app  # se Docker
```

2. Prisma Studio para debug database:
```bash
npx prisma studio
```

3. Console browser (F12) para erros frontend

4. Consultar docs:
- TaxHacker: GitHub repo
- Next.js: nextjs.org
- Prisma: prisma.io

5. Issues GitHub:
- Criar issue no teu fork
- Descrever problema + logs
- Screenshots se UI problem

==================================================
CHECKLIST FINAL SETUP
==================================================

Antes de começar desenvolvimento:

□ App roda sem erros
□ Database conectada
□ Consegues fazer login
□ Prisma Studio funciona
□ Git configurado (commits funcionam)
□ .env correctamente preenchido
□ Dependências todas instaladas
□ TypeScript compila (`npm run build`)
□ Conheces estrutura básica código
□ ROADMAP lido e compreendido

SE TUDO ✅ → Pronto para Fase 1!

==================================================
