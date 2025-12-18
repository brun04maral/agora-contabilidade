===============================================================================
ÍNDICE GERAL - Documentação Agora Contabilidade
Navegação completa da documentação técnica
===============================================================================

==================================================
VISÃO GERAL
==================================================

Este é o sistema de contabilidade interno da Agora Media, baseado no fork
do TaxHacker (https://github.com/vas3k/TaxHacker).

REPO: https://github.com/brun04maral/agora-contabilidade
STACK: Next.js 15 + TypeScript + Prisma + PostgreSQL
DEPLOYMENT: Self-hosted (Docker)

==================================================
DOCUMENTOS DISPONÍVEIS
==================================================

1. README.md
   Resumo executivo do projeto
   
   Conteúdo:
   - O que é o sistema
   - Por que TaxHacker como base
   - Features principais
   - Quick start
   
   Audiência: Todos (overview)
   Tempo leitura: 3 minutos

---

2. MAPEAMENTO_DADOS_REAL.md
   Análise detalhada de schemas e conversões
   
   Conteúdo:
   - Schema TaxHacker (Prisma) existente
   - Modelos Python SQLAlchemy originais
   - Mapeamento campo-a-campo
   - Exemplos concretos de conversão
   - Entidades a criar (Equipment, Budget)
   - Custom fields necessários
   
   Audiência: Developers (implementação)
   Tempo leitura: 20 minutos
   
   Use quando:
   - Começar migração de dados
   - Entender estrutura de dados
   - Implementar features

---

3. ARQUITETURA.md
   Estrutura técnica e organização do código
   
   Conteúdo:
   - Estrutura de pastas TaxHacker base
   - Extensões Agora Media (/lib/agora, /app/agora)
   - Modelos Prisma adicionais
   - Fluxos de dados (saldos, orçamentos)
   - Integração TOConline
   - Componentes UI principais
   
   Audiência: Developers (implementação)
   Tempo leitura: 25 minutos
   
   Use quando:
   - Adicionar novas features
   - Entender onde colocar código
   - Debug de fluxos

---

4. ROADMAP_IMPLEMENTACAO.md
   Plano faseado de desenvolvimento
   
   Conteúdo:
   - Fase 0: Preparação (1 semana)
   - Fase 1: Migração dados (1.5 semanas)
   - Fase 2: Features core (2 semanas)
   - Fase 3: Equipamento + Orçamentos (2 semanas)
   - Fase 4: TOConline (1.5 semanas)
   - Fase 5: Polish + Deploy (1 semana)
   - Sprints detalhados com tarefas
   - Validações e checkpoints
   
   Audiência: Project managers + Developers
   Tempo leitura: 30 minutos
   
   Use quando:
   - Planear trabalho
   - Tracking progresso
   - Estimar tempo

---

5. SETUP_INICIAL.md
   Guia passo-a-passo para começar
   
   Conteúdo:
   - Pré-requisitos (software, contas)
   - Fork e clone do repo
   - Instalar dependências
   - Configurar .env
   - Setup PostgreSQL
   - Primeira execução
   - Troubleshooting comum
   - Deploy Docker
   
   Audiência: Developers (setup)
   Tempo leitura: 15 minutos
   Tempo execução: 1-2 horas
   
   Use quando:
   - Setup ambiente dev
   - Onboarding novo developer
   - Deploy produção

---

6. FEATURES_CUSTOMIZADAS.md
   Implementação detalhada de cada feature
   
   Conteúdo:
   
   Feature 1: Cálculo Saldos Pessoais
   - Lógica TypeScript (lib/agora/saldos.ts)
   - API endpoints
   - Componentes UI (SaldoCard)
   - Página dashboard
   
   Feature 2: Gestão Fiscal (Impostos)
   - Cálculo IVA trimestral
   - Retenções na fonte
   - IRC estimado
   - Componentes fiscais
   
   Feature 3: Gestão Equipamento
   - CRUD equipamento
   - Cálculo amortização
   - Catálogo com filtros
   - Stats por categoria
   
   Feature 4: Sistema Orçamentos
   - Criar orçamentos profissionais
   - Items com equipamento
   - Conversão para projetos
   - Geração PDF
   
   Feature 5: Integração TOConline
   - Cliente API
   - Emissão facturas AT
   - Sync clientes
   - Download PDFs
   
   Audiência: Developers (implementação)
   Tempo leitura: 45 minutos
   
   Use quando:
   - Implementar feature específica
   - Entender lógica de negócio
   - Debug cálculos

---

7. MIGRACAO_DADOS.md
   Procedimentos para migrar dados Python → Prisma
   
   Conteúdo:
   - Backup dados originais
   - Scripts de migração (TypeScript)
   - Migrar: users, projetos, despesas, boletins
   - Validação de saldos
   - Troubleshooting migração
   - Rollback procedures
   
   Audiência: Developers (migração)
   Tempo leitura: 25 minutos
   Tempo execução: 4-6 horas
   
   Use quando:
   - Fazer migração inicial
   - Re-migrar após ajustes
   - Validar integridade dados

---

8. MANUTENCAO.md
   Operações, backup e troubleshooting
   
   Conteúdo:
   - Backups automáticos (scripts)
   - Restaurar backups
   - Actualizações (npm, Prisma, Docker)
   - Monitorização e health checks
   - Troubleshooting comum:
     * App não inicia
     * Queries lentas
     * Saldos errados
     * Uploads não funcionam
     * Erros TOConline
   - Procedimentos emergência
   - Segurança
   - Checklist mensal
   
   Audiência: DevOps + Sysadmins
   Tempo leitura: 30 minutos
   
   Use quando:
   - Setup backups
   - Sistema em produção
   - Resolver problemas
   - Manutenção rotina

---

9. INDEX.md (este ficheiro)
   Navegação da documentação

==================================================
FLUXO DE LEITURA RECOMENDADO
==================================================

PAPEL: Product Owner / Decision Maker
--------------------
1. README.md (entender o que é)
2. ROADMAP_IMPLEMENTACAO.md (ver plano)
3. FEATURES_CUSTOMIZADAS.md (ver capacidades)

Total: ~1 hora

PAPEL: Developer (Novo no Projeto)
--------------------
1. README.md (contexto)
2. SETUP_INICIAL.md (setup ambiente)
3. MAPEAMENTO_DADOS_REAL.md (entender dados)
4. ARQUITETURA.md (estrutura código)
5. FEATURES_CUSTOMIZADAS.md (implementar)

Total: ~2 horas leitura + prática

PAPEL: Developer (Implementação)
--------------------
Consultar conforme necessário:
- FEATURES_CUSTOMIZADAS.md → implementar feature
- ARQUITETURA.md → onde colocar código
- MAPEAMENTO_DADOS_REAL.md → entender conversões

PAPEL: DevOps / Sysadmin
--------------------
1. SETUP_INICIAL.md (deploy)
2. MANUTENCAO.md (operações)
3. MIGRACAO_DADOS.md (se migração necessária)

Total: ~1.5 horas

==================================================
QUICK REFERENCE
==================================================

COMANDOS MAIS USADOS:
--------------------

Setup inicial:
  git clone https://github.com/brun04maral/agora-contabilidade.git
  cd agora-contabilidade
  npm install
  cp .env.example .env
  # (configurar .env)
  npx prisma generate
  npx prisma migrate dev
  npm run dev

Desenvolvimento:
  npm run dev              # Dev server
  npx prisma studio        # GUI database
  npx prisma migrate dev   # Nova migration
  npm run build            # Build produção

Migração dados:
  npx ts-node lib/migrations/run-all.ts

Backup:
  ./scripts/backup-db.sh

Deploy:
  docker-compose up -d
  docker-compose logs -f app

PATHS IMPORTANTES:
--------------------

Lógica negócio:
  lib/agora/saldos.ts      # Cálculo saldos
  lib/agora/impostos.ts    # Cálculos fiscais
  lib/agora/equipamento.ts # Gestão equipamento
  lib/agora/orcamentos.ts  # Sistema orçamentos
  lib/agora/toconline/     # Integração TOConline

API routes:
  app/api/agora/saldos/route.ts
  app/api/agora/impostos/route.ts
  app/api/agora/equipamento/route.ts
  app/api/agora/orcamentos/route.ts
  app/api/agora/toconline/invoices/route.ts

Páginas:
  app/(app)/saldos/page.tsx
  app/(app)/impostos/page.tsx
  app/(app)/equipamento/page.tsx
  app/(app)/orcamentos/page.tsx

Componentes:
  components/agora/saldo-card.tsx
  components/agora/equipment-table.tsx
  components/agora/budget-form.tsx

Database:
  prisma/schema.prisma     # Schema
  prisma/migrations/       # Migrations

Scripts:
  scripts/backup-db.sh     # Backup database
  scripts/health-check.sh  # Monitorização
  lib/migrations/          # Migração Python→Prisma

==================================================
CONVENÇÕES DE CÓDIGO
==================================================

NAMING:
- Ficheiros: kebab-case (saldo-card.tsx)
- Componentes: PascalCase (SaldoCard)
- Funções: camelCase (calculateSaldo)
- Constants: UPPER_SNAKE_CASE (USER_IDS)

ESTRUTURA COMPONENTES:
---
'use client' // Se necessário

import { ... } from '...'

interface Props { ... }

export function ComponentName({ props }: Props) {
  // Estado
  // Handlers
  // Render
}
---

ESTRUTURA API ROUTES:
---
import { NextRequest, NextResponse } from 'next/server'
import { auth } from '@/lib/auth'

export async function GET(request: NextRequest) {
  const session = await auth.api.getSession(...)
  if (!session) return NextResponse.json({ error: '...' }, { status: 401 })
  
  // Lógica
  
  return NextResponse.json(data)
}
---

COMENTÁRIOS:
- Código deve ser self-explanatory
- Comentar apenas lógica complexa
- Explicar "porquê", não "o quê"

COMMITS:
  feat: nova feature
  fix: bug fix
  chore: manutenção
  docs: documentação
  refactor: refactoring

==================================================
FAQ - PERGUNTAS FREQUENTES
==================================================

P: Posso usar o TaxHacker original sem fork?
R: Não. Precisas do fork para adicionar features Agora Media específicas.

P: Por que não partir do zero?
R: TaxHacker já tem 80% da funcionalidade core (auth, transactions, UI).
   Poupar ~6 semanas de desenvolvimento.

P: Como actualizar do TaxHacker upstream?
R: git remote add upstream https://github.com/vas3k/TaxHacker.git
   git fetch upstream
   git cherry-pick commits específicos (cuidado com conflitos)

P: Valores em cêntimos ou euros?
R: Database: SEMPRE cêntimos (Int)
   UI: Mostrar em euros com formatEuros()
   Conversão: euros * 100 = cêntimos

P: Onde guardar configurações?
R: Usar tabela 'settings' (já existe no TaxHacker)
   Exemplo: TOConline API key

P: Como adicionar nova feature?
R: 1. Ler ARQUITETURA.md para saber onde colocar código
   2. Adicionar lógica em lib/agora/
   3. Criar API route em app/api/agora/
   4. Criar página em app/(app)/
   5. Criar componentes em components/agora/

P: Como testar localmente?
R: npm run dev
   Abrir http://localhost:7331
   Usar Prisma Studio para ver dados: npx prisma studio

P: Backups automáticos?
R: Ver MANUTENCAO.md secção 1.1
   Script: scripts/backup-db.sh
   Cron: 0 3 * * * (3h da manhã)

P: Como restaurar backup?
R: Ver MANUTENCAO.md secção 1.3
   Resumo: parar app → restaurar SQL → reiniciar

P: Erros de cálculo de saldos?
R: Ver MANUTENCAO.md secção 4.3
   Verificar: cêntimos (x100), negativos (despesas), filtros (RECEBIDO/PAGO)

P: TOConline não funciona?
R: Ver MANUTENCAO.md secção 4.5
   Verificar: API key, cliente existe, rate limits

==================================================
GLOSSÁRIO
==================================================

INs: Entradas - valores que a empresa DEVE ao sócio
OUTs: Saídas - valores que a empresa já PAGOU ao sócio

Saldo: INs - OUTs (quanto a empresa ainda deve)

Projetos PESSOAIS: Trabalhos freelance do sócio facturados pela empresa
Projetos EMPRESA: Trabalhos da empresa (sócios recebem prémios)

Prémio: Comissão/cachet que sócio recebe de projeto da empresa

Despesas FIXAS: Despesas mensais recorrentes (divididas por 2 entre sócios)
Despesas PESSOAIS: Despesas específicas de um sócio

Boletim: Pagamento ao sócio para regularizar saldo

Transaction: Modelo principal TaxHacker (receitas e despesas)
  - type: 'income' (receita) ou 'expense' (despesa)
  - total: valor em cêntimos (negativo se despesa)
  - extra: JSON livre para dados custom

Cêntimos: Valores monetários guardados como Int (multiply by 100)
  150.00 EUR = 15000 cêntimos

Custom Fields: Campos adicionais configuráveis na UI TaxHacker
  Guardados em JSON 'extra' das transactions

==================================================
RECURSOS EXTERNOS
==================================================

DOCUMENTAÇÃO:
- TaxHacker: https://github.com/vas3k/TaxHacker
- Next.js: https://nextjs.org/docs
- Prisma: https://www.prisma.io/docs
- React: https://react.dev
- TypeScript: https://www.typescriptlang.org/docs
- Tailwind CSS: https://tailwindcss.com/docs
- Shadcn UI: https://ui.shadcn.com

APIs:
- TOConline: https://www.toconline.pt/api-docs

COMUNIDADES:
- TaxHacker Issues: https://github.com/vas3k/TaxHacker/issues
- Next.js Discord: https://nextjs.org/discord
- Prisma Discord: https://pris.ly/discord

==================================================
SUPPORT
==================================================

ISSUES TÉCNICOS:
- GitHub Issues: https://github.com/brun04maral/agora-contabilidade/issues
- Consultar MANUTENCAO.md secção Troubleshooting

DÚVIDAS IMPLEMENTAÇÃO:
- Consultar documentação relevante
- Verificar código TaxHacker original
- Criar issue no repo

EMERGÊNCIAS PRODUÇÃO:
- Contactos em MANUTENCAO.md secção 7.1
- Seguir procedimentos emergência

==================================================
ACTUALIZAÇÕES DOCUMENTAÇÃO
==================================================

Esta documentação é viva. Actualizar quando:
- Nova feature implementada
- Problemas recorrentes descobertos
- Procedimentos mudaram
- Lessons learned

COMO ACTUALIZAR:
1. Editar ficheiro Markdown relevante
2. Actualizar CHANGELOG.md
3. Commit: docs: descrição mudança
4. Se mudança major, notificar equipa

ÚLTIMA ACTUALIZAÇÃO: 18 Dezembro 2025

==================================================
