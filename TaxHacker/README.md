===============================================================================
AGORA CONTABILIDADE
Sistema de Contabilidade Interno baseado em TaxHacker
===============================================================================

Sistema de gestão contabilística desenvolvido para a Agora Media, baseado no
fork do TaxHacker (https://github.com/vas3k/TaxHacker).

Desenvolvido para gerir contabilidade interna, calcular saldos pessoais dos
sócios, emitir orçamentos e integrar com TOConline para facturação automática.

==================================================
O QUE É
==================================================

Aplicação web self-hosted para:

✓ Gestão de receitas e despesas
✓ Cálculo automático de saldos pessoais (Bruno e Rafael)
✓ Dashboard fiscal (IVA, retenções, IRC)
✓ Catálogo de equipamento com amortização
✓ Sistema de orçamentos profissionais
✓ Emissão automática de facturas AT (via TOConline)

SUBSTITUÍ: Aplicação Python anterior (Flask + SQLAlchemy)

STACK TECNOLÓGICO:
- Frontend: Next.js 15 + React 19 + TypeScript
- Backend: Next.js API Routes
- Database: PostgreSQL 16+
- ORM: Prisma 6
- UI: Tailwind CSS + Shadcn UI
- Auth: Better Auth
- Deploy: Docker / Self-hosted

==================================================
POR QUE TAXHACKER COMO BASE?
==================================================

TaxHacker já fornece 80% da funcionalidade core:

✅ Sistema de transações (receitas/despesas)
✅ Categorias e Projetos customizáveis
✅ Custom Fields (campos adicionais via JSON)
✅ Upload de ficheiros (PDFs, imagens)
✅ Multi-currency com conversão histórica
✅ Export para CSV
✅ UI moderna e responsiva
✅ Autenticação completa
✅ Self-hosted friendly

POUPANÇA ESTIMADA: ~6 semanas de desenvolvimento

O QUE ADICIONÁMOS:
- Cálculo saldos pessoais (lógica Agora Media)
- Dashboard fiscal (IVA, IRC, retenções)
- Gestão de equipamento
- Sistema de orçamentos
- Integração TOConline

==================================================
FEATURES PRINCIPAIS
==================================================

1. SALDOS PESSOAIS
   Cálculo automático do que a empresa deve a cada sócio
   
   INs (Entradas):
   - Projetos pessoais facturados pela empresa
   - Prémios de projetos da empresa
   
   OUTs (Saídas):
   - Despesas fixas mensais (÷2)
   - Boletins emitidos
   - Despesas pessoais
   
   Saldo = INs - OUTs
   
   Dashboard com breakdown detalhado e sugestão de boletim

2. GESTÃO FISCAL
   Dashboards para impostos
   
   - IVA trimestral (liquidado vs dedutível)
   - Retenções na fonte
   - IRC estimado com pagamentos trimestrais
   - Exportação para contabilista

3. EQUIPAMENTO
   Catálogo de equipamento com amortização
   
   - Registo de câmaras, drones, iluminação, áudio
   - Cálculo automático de amortização (método linear)
   - Valor actual vs valor compra
   - Taxa diária de aluguer
   - Uso em orçamentos

4. ORÇAMENTOS
   Sistema profissional de orçamentos
   
   - Criar orçamentos com items
   - Incluir equipamento com taxas automáticas
   - Gerar PDFs profissionais
   - Converter orçamentos aprovados em projetos
   - Tracking de taxa de conversão

5. INTEGRAÇÃO TOCONLINE
   Emissão automática de facturas AT
   
   - Emitir facturas certificadas
   - Sync automático de clientes
   - Download PDFs certificados
   - Actualização automática de estados (FATURADO)

==================================================
QUICK START
==================================================

REQUISITOS:
- Node.js 20+
- PostgreSQL 16+
- Docker (opcional)

INSTALAÇÃO LOCAL:

1. Clone repo
```bash
git clone https://github.com/brun04maral/agora-contabilidade.git
cd agora-contabilidade
```

2. Instalar dependências
```bash
npm install
```

3. Configurar ambiente
```bash
cp .env.example .env
# Editar .env com credenciais PostgreSQL
```

4. Setup database
```bash
npx prisma generate
npx prisma migrate dev
```

5. Rodar aplicação
```bash
npm run dev
```

6. Abrir browser
```
http://localhost:7331
```

INSTALAÇÃO DOCKER:

1. Configurar .env

2. Subir containers
```bash
docker-compose up -d
```

3. Verificar logs
```bash
docker-compose logs -f app
```

4. Abrir browser
```
http://localhost:7331
```

==================================================
MIGRAÇÃO DA APP PYTHON
==================================================

Se vens da aplicação Python anterior:

1. Fazer backup dos dados Python
```bash
python backup_database.py
```

2. Configurar TaxHacker
   (seguir SETUP_INICIAL.md)

3. Executar migração
```bash
npx ts-node lib/migrations/run-all.ts
```

4. Validar saldos
   Comparar com app Python - devem bater ao cêntimo

5. Testar todas as features
   □ Login
   □ Ver transactions
   □ Calcular saldos
   □ Export CSV

6. Prod quando confiante
```bash
docker-compose up -d
```

Ver: MIGRACAO_DADOS.md para detalhes completos

==================================================
DOCUMENTAÇÃO COMPLETA
==================================================

Consultar INDEX.md para navegação completa.

Documentos principais:
- INDEX.md - Navegação geral
- SETUP_INICIAL.md - Setup passo-a-passo
- FEATURES_CUSTOMIZADAS.md - Implementação features
- MANUTENCAO.md - Operações e troubleshooting

Quick links:
- Mapeamento dados: MAPEAMENTO_DADOS.md
- Arquitetura: ARQUITETURA.md
- Roadmap: ROADMAP_IMPLEMENTACAO.md
- Migração: MIGRACAO_DADOS.md

==================================================
ESTRUTURA DO PROJETO
==================================================

```
agora-contabilidade/
├── app/                      # Next.js app
│   ├── (app)/                # Rotas autenticadas
│   │   ├── saldos/           # Dashboard saldos ⭐ CUSTOM
│   │   ├── impostos/         # Dashboard fiscal ⭐ CUSTOM
│   │   ├── equipamento/      # Catálogo equipamento ⭐ CUSTOM
│   │   ├── orcamentos/       # Sistema orçamentos ⭐ CUSTOM
│   │   ├── transactions/     # Lista transações (TaxHacker)
│   │   └── ...               # Outras rotas TaxHacker
│   └── api/                  # API routes
│       ├── agora/            # Endpoints custom ⭐
│       └── ...               # Endpoints TaxHacker
│
├── lib/                      # Lógica negócio
│   ├── agora/                # Lógica Agora Media ⭐ CUSTOM
│   │   ├── saldos.ts
│   │   ├── impostos.ts
│   │   ├── equipamento.ts
│   │   ├── orcamentos.ts
│   │   └── toconline/
│   ├── migrations/           # Scripts migração Python ⭐
│   └── ...                   # Utils TaxHacker
│
├── components/               # React components
│   ├── agora/                # Componentes custom ⭐
│   └── ui/                   # Shadcn UI
│
├── prisma/
│   ├── schema.prisma         # Database schema (extended)
│   └── migrations/           # Migrations
│
├── scripts/                  # Scripts operacionais ⭐
│   ├── backup-db.sh
│   └── health-check.sh
│
├── TaxHacker/                # Documentação ⭐
│   ├── INDEX.md
│   ├── README.md
│   ├── MAPEAMENTO_DADOS.md
│   ├── ARQUITETURA.md
│   ├── ROADMAP_IMPLEMENTACAO.md
│   ├── SETUP_INICIAL.md
│   ├── FEATURES_CUSTOMIZADAS.md
│   ├── MIGRACAO_DADOS.md
│   └── MANUTENCAO.md
│
└── docker-compose.yml        # Deploy Docker

⭐ = Extensões Agora Media (não existem no TaxHacker original)
```

==================================================
CONTRIBUIR
==================================================

WORKFLOW:

1. Criar branch
```bash
git checkout -b feature/nome-feature
```

2. Desenvolver
   - Seguir convenções em INDEX.md
   - Adicionar testes se aplicável
   - Actualizar documentação

3. Commit
```bash
git commit -m "feat: descrição"
# (usar: feat, fix, chore, docs, refactor)
```

4. Push
```bash
git push origin feature/nome-feature
```

5. Pull Request (se trabalho em equipa)
   Ou merge directo na main (se sozinho)

CONVENÇÕES:
- TypeScript strict mode
- ESLint + Prettier
- Componentes funcionais com hooks
- Server Components quando possível
- API routes com validação

==================================================
LICENÇA
==================================================

Baseado no TaxHacker (MIT License)
https://github.com/vas3k/TaxHacker

Extensões Agora Media: Proprietary
© 2025 Agora Media

==================================================
SUPORTE
==================================================

Issues técnicos:
  GitHub Issues no repo

Dúvidas:
  Consultar documentação em TaxHacker/

Emergências produção:
  Contactos em MANUTENCAO.md

==================================================
LINKS ÚTEIS
==================================================

Repo: https://github.com/brun04maral/agora-contabilidade
TaxHacker Original: https://github.com/vas3k/TaxHacker
Documentação: ./TaxHacker/INDEX.md

Next.js: https://nextjs.org/docs
Prisma: https://www.prisma.io/docs
Shadcn UI: https://ui.shadcn.com

==================================================
ROADMAP FUTURO
==================================================

v1.0 (Actual):
✅ Migração completa Python → TaxHacker
✅ Cálculo saldos
✅ Dashboard fiscal
✅ Equipamento
✅ Orçamentos
✅ TOConline

v1.1 (Futuro):
□ Mobile app (React Native)
□ Notificações (email/push)
□ Relatórios personalizados
□ API pública
□ Webhooks TOConline

v2.0 (Ideias):
□ Multi-empresa (não só Agora Media)
□ Integrações bancárias
□ AI para categorização automática
□ Dashboard analytics avançado

==================================================
CHANGELOG
==================================================

Ver CHANGELOG.md para histórico detalhado

v1.0.0 - 2025-01-15
  Initial release
  - Migração completa de app Python
  - Todas as features core implementadas
  - Documentação completa
  - Prod ready

==================================================
CRÉDITOS
==================================================

Desenvolvido por: Bruno Amaral
Baseado em: TaxHacker by Vasily Zubarev (vas3k)
Stack: Next.js, Prisma, PostgreSQL, Shadcn UI

==================================================
