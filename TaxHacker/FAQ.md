===============================================================================
FAQ: Perguntas Frequentes e Respostas Rápidas
Guia de consulta rápida para dúvidas comuns
===============================================================================

==================================================
CONCEITOS GERAIS
==================================================

Q: O que é TaxHacker?
A: Sistema open-source de gestão financeira self-hosted, desenvolvido por vas3k.
   Fork usado como base para Agora Contabilidade.
   
Q: Porque fork TaxHacker em vez de desenvolver do zero?
A: TaxHacker fornece 80% da funcionalidade core (transactions, categories, 
   projects, auth, UI moderna). Poupança estimada: 6-8 semanas desenvolvimento.
   Ver DECISOES_TECNICAS.md (DT-001) para detalhes.

Q: O que adiciona Agora Contabilidade ao TaxHacker?
A: - Cálculo saldos pessoais (Bruno e Rafael)
   - Dashboard fiscal (IVA, retenções, IRC)
   - Gestão equipamento com amortização
   - Sistema orçamentos profissionais
   - Integração TOConline (facturas AT)

Q: É gratis? Há custos?
A: Software: 100% gratis (open-source)
   Custos:
   - PostgreSQL (gratis se self-hosted)
   - Hosting (gratis se Raspberry Pi, ou ~€10-30/mês cloud)
   - TOConline API (verifica plano actual)

Q: Quem pode usar?
A: Sistema interno Agora Media. Não é multi-tenant SaaS.
   Preparado para 2 users (Bruno e Rafael).

==================================================
INSTALAÇÃO E SETUP
==================================================

Q: Quais os requisitos mínimos?
A: - Node.js 20+
   - PostgreSQL 16+
   - 2GB RAM (para app + database)
   - 10GB disco (database cresce com dados)

Q: Posso rodar no Windows?
A: Sim, mas recomendado Linux/macOS para produção.
   Windows: usar WSL2 ou Docker Desktop.

Q: Quanto tempo demora instalar?
A: - Setup inicial: 30-60 minutos (primeira vez)
   - Migração dados Python: 2-4 horas
   - Deploy produção: 1-2 horas

Q: Preciso saber programar?
A: Para usar: Não (interface web normal)
   Para instalar/manter: Conhecimentos básicos terminal/Docker ajudam
   Para desenvolver: Sim (TypeScript/React)

Q: Posso usar SQLite em vez de PostgreSQL?
A: Não. Prisma schema usa features PostgreSQL (JSON queries, UUIDs).
   SQLite não suportado.

Q: Como faço backup?
A: Automático:
   ```bash
   # Script cron diário (ver MANUTENCAO.md)
   0 2 * * * /opt/agora-contabilidade/scripts/backup-db.sh
   ```
   
   Manual:
   ```bash
   # pg_dump (ver MANUTENCAO.md seção 1.3)
   pg_dump $DATABASE_URL > backup.sql
   
   # Uploads
   tar -czf uploads-backup.tar.gz data/uploads/
   ```

==================================================
USO DIÁRIO
==================================================

Q: Como login?
A: ```
   https://seu-dominio.com/login
   Email: bruno@agoramedia.pt (ou rafael@agoramedia.pt)
   Password: (configurada durante setup)
   ```

Q: Esqueci password, como recuperar?
A: Via Prisma Studio ou SQL:
   
   ```bash
   # 1. Gerar hash nova password
   # Usar: https://bcrypt-generator.com/
   
   # 2. Actualizar na database
   psql $DATABASE_URL
   ```
   
   ```sql
   UPDATE account 
   SET password = '$2a$10$...' 
   WHERE account_id = 'bruno@agoramedia.pt';
   ```
   
   Ou pedir ao outro sócio para alterar via UI (se tiver admin).

Q: Como criar um novo projeto?
A: 1. Sidebar: Transactions → Add Transaction
   2. Type: Income
   3. Name: descrição projeto
   4. Amount: valor sem IVA
   5. Project: escolher EMPRESA / PESSOAL_BRUNO / PESSOAL_RAFAEL
   6. Category: NAO_FATURADO (inicialmente)
   7. Custom fields: preencher prémios se aplicável
   8. Save

Q: Como registar despesa?
A: Igual projeto mas:
   - Type: Expense
   - Amount: valor (sistema torna negativo automaticamente)
   - Category: FIXA_MENSAL / DESPESA_PESSOAL_X / etc

Q: Onde vejo os saldos pessoais?
A: Sidebar → Saldos Pessoais
   
   Mostra:
   - INs (projetos pessoais + prémios)
   - OUTs (despesas fixas ÷ 2 + boletins + despesas pessoais)
   - Saldo actual
   - Sugestão boletim

Q: Como emitir boletim?
A: 1. Transactions → Add Transaction
   2. Type: Expense
   3. Name: "Boletim Janeiro 2025" (ou descrição)
   4. Amount: valor boletim
   5. Category: BOLETIM
   6. Custom field "socio": escolher BRUNO ou RAFAEL
   7. Save
   
   Saldo actualiza automaticamente.

Q: Como marcar projeto como facturado?
A: Opção A: Editar transaction, mudar Category para FATURADO
   Opção B: Usar botão "Emitir Factura" (se TOConline configurado)

Q: Como marcar projeto como recebido?
A: Editar transaction, mudar Category para RECEBIDO

Q: Posso anexar ficheiros (PDFs, recibos)?
A: Sim! Transaction → Files → Upload
   
   Formatos: PDF, JPG, PNG
   Limite: configurado no .env (default 10MB)

==================================================
SALDOS PESSOAIS
==================================================

Q: Como são calculados os saldos?
A: ```
   INs (entradas):
   - Projetos pessoais RECEBIDOS 
     (projectCode = PESSOAL_X, category = RECEBIDO)
   - Prémios de projetos empresa 
     (extra.premio_bruno / premio_rafael)
   
   OUTs (saídas):
   - Despesas fixas PAGAS ÷ 2 (repartidas)
   - Boletins emitidos 
     (categoryCode = BOLETIM, socio = X)
   - Despesas pessoais PAGAS 
     (categoryCode = DESPESA_PESSOAL_X)
   
   Saldo = INs - OUTs
   ```

Q: Porque despesas fixas dividem por 2?
A: Regra Agora Media: despesas fixas empresa (contabilidade, software, etc)
   são repartidas igualmente entre Bruno e Rafael.

Q: O que é "sugestão de boletim"?
A: Se saldo > 0, empresa deve dinheiro ao sócio.
   Sugestão = emitir boletim com esse valor para "sacar" dinheiro.

Q: Saldo pode ser negativo?
A: Sim. Significa sócio deve dinheiro à empresa.
   Exemplo: emitiu boletins mas projetos pessoais ainda não recebidos.

Q: Saldo não bate com expectativa, como debug?
A: ```bash
   # 1. Abrir Prisma Studio
   npx prisma studio
   ```
   
   2. Ver Transactions filtradas:
      - userId = teu ID
      - type = income/expense
      - categoryCode
   
   3. Verificar:
      - Valores em cêntimos (x100)? 
      - Despesas negativas?
      - Estados corretos (RECEBIDO vs FATURADO)?
   
   4. Verificar custom fields:
      - Boletins: campo "socio" preenchido?
      - Prémios: premio_bruno/rafael em cêntimos?
   
   5. Re-calcular: forçar refresh página saldos

==================================================
ORÇAMENTOS
==================================================

Q: Como criar orçamento?
A: 1. Sidebar → Orçamentos → Novo Orçamento
   2. Preencher info cliente
   3. Adicionar items:
      - Manual: descrição, quantidade, preço unitário
      - Equipamento: selecionar do catálogo (preenche automático)
   4. Revisar totais (subtotal + IVA)
   5. Definir validade
   6. Save

Q: Como enviar orçamento ao cliente?
A: 1. Abrir orçamento
   2. Botão "Gerar PDF"
   3. Download PDF
   4. Enviar por email manualmente
   
   (Futuro: envio automático email)

Q: Orçamento aprovado, e agora?
A: 1. Marcar orçamento como "Approved"
   2. Botão "Converter em Projeto"
   3. Sistema cria Transaction automaticamente:
      - Type: Income
      - Total: valor orçamento
      - Category: NAO_FATURADO
      - Items copiados para extra JSON

Q: Posso editar orçamento após enviar?
A: Sim, mas boa prática: criar nova versão se já enviado ao cliente.

Q: Posso eliminar orçamento?
A: Sim, se ainda não convertido em projeto.
   Se já convertido: não eliminar (manter histórico).

==================================================
EQUIPAMENTO
==================================================

Q: Como adicionar equipamento?
A: Sidebar → Equipamento → Adicionar
   
   Campos:
   - Nome: "Sony A7S III"
   - Categoria: "Câmaras"
   - Data compra: quando foi comprado
   - Valor compra: preço pago
   - Vida útil: anos (ex: 5)
   - Taxa diária: para orçamentos (opcional)

Q: Como funciona amortização?
A: Método linear:
   ```
   Valor Actual = Valor Compra × (1 - (Idade / Vida Útil))
   
   Exemplo:
   - Compra: €3000
   - Vida útil: 5 anos
   - Idade: 2 anos
   - Valor actual: €3000 × (1 - 2/5) = €1800
   ```

Q: Equipamento usado em orçamento?
A: Ao criar orçamento:
   - Adicionar item → escolher "Selecionar Equipamento"
   - Sistema preenche automático descrição e taxa diária
   - Ajustar quantidade (dias aluguer)

==================================================
TOCONLINE (FACTURAS AT)
==================================================

Q: O que é TOConline?
A: Serviço certificação facturas AT (Autoridade Tributária Portugal).
   Alternativas: InvoiceXpress, Moloni, etc.

Q: É obrigatório usar TOConline?
A: Não! Podes:
   - Emitir facturas manualmente no TOConline
   - Usar outro sistema certificação
   - Marcar projetos como FATURADO manualmente
   
   Integração TOConline só automatiza processo.

Q: Como configurar integração?
A: 1. Obter API key TOConline (conta → settings → API)
   2. App: Sidebar → TOConline → Settings
   3. Inserir API key
   4. Testar conexão

Q: Como emitir factura?
A: 1. Abrir transaction (projeto)
   2. Botão "Emitir Factura"
   3. Confirmar dados cliente
   4. Sistema:
      - Cria/actualiza cliente TOConline
      - Emite factura certificada
      - Download PDF
      - Actualiza transaction para FATURADO

Q: E se TOConline API falhar?
A: 1. Verificar API key válida
   2. Verificar saldo conta TOConline
   3. Ver logs erro:
      ```bash
      docker-compose logs app | grep toconline
      ```
   4. Retry manual
   5. Se persistir: emitir manualmente no TOConline, marcar FATURADO na app

Q: Factura emitida mas cliente ainda não pagou?
A: Transaction fica FATURADO.
   Quando cliente pagar: editar manualmente para RECEBIDO.
   
   (Futuro: webhook TOConline actualiza automático)

==================================================
TROUBLESHOOTING
==================================================

Q: App não inicia, erro "Port 7331 already in use"
A: Porta ocupada.
   
   Solução A: matar processo
   ```bash
   lsof -ti:7331 | xargs kill -9
   ```
   
   Solução B: mudar porta no .env
   ```bash
   PORT=7332
   ```

Q: Erro "Cannot reach database server"
A: PostgreSQL não acessível.
   
   ```bash
   # 1. Verificar PostgreSQL a correr
   systemctl status postgresql
   
   # 2. Testar conexão manual
   psql $DATABASE_URL
   
   # 3. Verificar DATABASE_URL correcto no .env
   cat .env | grep DATABASE_URL
   
   # 4. Firewall bloqueia porta 5432?
   sudo ufw status
   ```

Q: Erro "Prisma Client not found"
A: Client desactualizado.
   
   Solução:
   ```bash
   npx prisma generate
   npm run build
   ```

Q: Página branca / erro 500
A: ```bash
   # 1. Ver logs
   docker-compose logs -f app
   
   # 2. Abrir DevTools browser (F12) → Console
   
   # 3. Verificar .env tem todas as variáveis
   cat .env
   
   # 4. Verificar migrations aplicadas
   npx prisma migrate status
   ```

Q: Upload ficheiros não funciona
A: ```bash
   # 1. Verificar directório existe
   ls -la ./data/uploads
   
   # 2. Verificar permissões
   chmod 755 ./data/uploads
   
   # 3. Verificar UPLOAD_PATH no .env
   cat .env | grep UPLOAD_PATH
   
   # 4. Verificar limite tamanho ficheiro
   cat .env | grep MAX_FILE_SIZE
   ```

Q: Saldos calculam errado
A: 1. Verificar valores em cêntimos:
      ```
      Transaction.total deve ser valor × 100
      Exemplo: €150.00 → 15000
      ```
   
   2. Verificar despesas negativas:
      ```
      Expenses devem ter total < 0
      ```
      
   3. Verificar estados:
      ```
      Receitas: só RECEBIDO conta
      Despesas: só PAGO conta
      ```
      
   4. Verificar custom fields:
      - Boletins: campo "socio" preenchido?
      - Prémios: premio_bruno/rafael em cêntimos?
   
   5. Re-calcular: forçar refresh página saldos

Q: Não consigo fazer login
A: ```bash
   # 1. Verificar email correcto
   
   # 2. Reset password (ver FAQ acima)
   
   # 3. Verificar Better Auth configurado
   echo $BETTER_AUTH_SECRET
   
   # 4. Ver logs auth
   docker-compose logs app | grep auth
   ```

Q: Backup automático não está a correr
A: ```bash
   # 1. Verificar cron activo
   systemctl status cron
   
   # 2. Ver crontab
   crontab -l
   
   # 3. Testar script manual
   ./scripts/backup-db.sh
   
   # 4. Ver logs
   cat /var/log/agora-backup.log
   ```

Q: App lenta / queries demoram
A: ```bash
   # 1. Verificar indexes database (ver MANUTENCAO.md)
   
   # 2. Enable query logging
   echo "DEBUG=prisma:query" >> .env
   
   # 3. Identificar queries lentas nos logs
   docker-compose logs app | grep "prisma:query"
   
   # 4. Adicionar indexes conforme necessário
   
   # 5. Considerar VACUUM PostgreSQL
   psql $DATABASE_URL -c "VACUUM ANALYZE;"
   ```

==================================================
MIGRAÇÃO DADOS PYTHON
==================================================

Q: Tenho de migrar dados Python?
A: Se já usam app Python com dados: Sim.
   Se começarem do zero: Não.

Q: Migração demora quanto tempo?
A: - Preparar scripts: 1-2 horas
   - Executar migração: 5-15 minutos (depende volume dados)
   - Validar dados: 30-60 minutos
   
   Total: 2-4 horas

Q: Dados Python ficam intactos?
A: Sim! Migração só LEIA dados Python, não altera.
   Backup recomendado na mesma (segurança).

Q: E se migração correr mal?
A: ```bash
   # 1. Parar imediatamente (Ctrl+C)
   
   # 2. Limpar database TaxHacker
   npx prisma migrate reset --force
   
   # 3. Corrigir scripts
   
   # 4. Tentar novamente
   npx ts-node lib/migrations/run-all.ts
   ```
   
   Dados Python intactos!

Q: Após migração, ainda preciso app Python?
A: Não. Podes:
   - Manter como backup 1-2 meses
   - Arquivar código (git)
   - Desligar servidor Python

Q: Saldos migrados não batem?
A: Ver MIGRACAO_DADOS.md script validação.
   
   Causas comuns:
   - Conversão cêntimos errada (x100)
   - Filtros estado diferentes (PAGO vs RECEBIDO)
   - Despesas fixas divisão por 2
   - Datas filtro diferentes

==================================================
DESENVOLVIMENTO
==================================================

Q: Como contribuir com código?
A: 1. Fork repo (ou branch no repo principal)
   2. Fazer alterações
   3. Testar localmente
   4. Commit com mensagem descritiva
   5. Push
   6. Criar PR (ou merge se permissões)

Q: Como rodar em modo desenvolvimento?
A: ```bash
   npm run dev
   ```
   
   Abre http://localhost:7331
   Hot reload activo (alterações actualizam automático)

Q: Como fazer debug?
A: 1. `console.log()` no código (old school funciona!)
   2. VS Code debugger (attach to process)
   3. React DevTools (browser extension)
   4. Prisma Studio:
      ```bash
      npx prisma studio
      ```
   5. Logs:
      ```bash
      docker-compose logs -f app
      ```

Q: Como adicionar nova rota/página?
A: Next.js 15 App Router:
   
   ```bash
   # 1. Criar pasta
   mkdir -p app/(app)/nova-rota/
   
   # 2. Criar page.tsx
   ```
   
   ```typescript
   // app/(app)/nova-rota/page.tsx
   export default function NovaRotaPage() {
     return <div>Conteúdo</div>
   }
   ```
   
   3. Adicionar ao menu sidebar (app/(app)/layout.tsx)
   4. Criar actions.ts se precisar server actions

Q: Como adicionar novo modelo database?
A: ```bash
   # 1. Editar prisma/schema.prisma
   # (adicionar novo model)
   
   # 2. Criar migration
   npx prisma migrate dev --name add_new_model
   
   # 3. Gerar client
   npx prisma generate
   ```
   
   ```typescript
   // 4. Usar no código
   await prisma.newModel.create({ data: {...} })
   ```

Q: Como testar antes de deploy?
A: ```bash
   # 1. Rodar testes (quando implementados)
   npm run test
   
   # 2. Build produção
   npm run build
   
   # 3. Verificar sem erros TypeScript
   npx tsc --noEmit
   
   # 4. Testar workflows críticos manualmente
   
   # 5. Verificar em ambiente staging (se existir)
   ```

==================================================
PRODUÇÃO
==================================================

Q: Onde hostear em produção?
A: Opções:
   - Raspberry Pi (recomendado Agora, €0/mês)
   - VPS (DigitalOcean, Hetzner, ~€5-10/mês)
   - Railway / Render (~€15-25/mês)
   - Vercel + Database (~€20-50/mês)
   
   Ver DECISOES_TECNICAS.md (DT-008)

Q: Como fazer deploy?
A: Docker (recomendado):
   
   ```bash
   # 1. Actualizar código
   git pull origin main
   
   # 2. Build
   docker-compose build
   
   # 3. Reiniciar
   docker-compose down
   docker-compose up -d
   
   # 4. Verificar
   curl http://localhost:7331/api/health
   ```

Q: Como configurar domínio?
A: 1. Apontar DNS para IP servidor
   2. Configurar Nginx reverse proxy
   3. Obter certificado SSL (Let's Encrypt):
      ```bash
      certbot --nginx -d seu-dominio.com
      ```
   4. Actualizar BASE_URL no .env:
      ```bash
      BASE_URL=https://seu-dominio.com
      ```

Q: Backup automático está configurado?
A: Sim, se seguiste MANUTENCAO.md.
   
   Verificar:
   ```bash
   # Cron a correr
   crontab -l
   
   # Backups recentes
   ls -lh /var/backups/agora-contabilidade/
   
   # Testar restore (ver MANUTENCAO.md seção 1.3)
   ```

Q: Como monitorizar sistema?
A: 1. Health check endpoint: `/api/health`
   2. Logs:
      ```bash
      docker-compose logs -f app
      ```
   3. Métricas PostgreSQL:
      ```sql
      SELECT pg_size_pretty(pg_database_size('agora_contabilidade'));
      ```
   4. Espaço disco:
      ```bash
      df -h
      ```
   5. Uptime: usar serviço externo (UptimeRobot, etc)

Q: Como actualizar sistema?
A: ```bash
   # 1. Backup primeiro!
   ./scripts/backup-db.sh
   
   # 2. Actualizar código
   git pull origin main
   
   # 3. Instalar dependências (se package.json mudou)
   npm install
   
   # 4. Aplicar migrations (se schema mudou)
   npx prisma migrate deploy
   
   # 5. Build
   npm run build
   
   # 6. Reiniciar (ou rebuild se Dockerfile mudou)
   docker-compose restart
   # OU
   docker-compose up -d --build
   
   # 7. Testar
   curl http://localhost:7331/api/health
   ```

Q: Sistema down, o que fazer?
A: Ver MANUTENCAO.md seção 5 (Procedimentos Emergência)
   
   Quick steps:
   ```bash
   # 1. Verificar logs
   docker-compose logs app | tail -100
   
   # 2. Reiniciar
   docker-compose restart
   
   # 3. Se persistir: restaurar último backup
   ./scripts/restore-db.sh /var/backups/agora-*/latest.sql
   
   # 4. Notificar equipa
   ```

==================================================
SEGURANÇA
==================================================

Q: Sistema é seguro?
A: Sim, se seguires boas práticas:
   ✅ Passwords fortes (>16 chars)
   ✅ HTTPS habilitado (certficado SSL)
   ✅ Firewall configurado (só portas necessárias)
   ✅ Database não exposta publicamente
   ✅ Backups encriptados
   ✅ Updates regulares (dependências)

Q: Como mudar password?
A: User logado:
   ```
   Settings → Profile → Change Password
   ```
   
   Ou via SQL (emergency):
   (ver FAQ "Esqueci password" acima)

Q: Dados estão encriptados?
A: - Em trânsito: Sim (HTTPS)
   - Em repouso: Depende configuração PostgreSQL
   - Backups: Opcional (ver MANUTENCAO.md backup encryption)

Q: Quem tem acesso aos dados?
A: Self-hosted: Só quem tem acesso servidor.
   Cloud: Tu + provedor hosting (ler ToS provedor).

Q: Como revogar acesso user?
A: Database:
   ```sql
   DELETE FROM account WHERE user_id = 'user-uuid';
   ```
   
   Ou desactivar (futuro):
   ```sql
   UPDATE users SET active = false WHERE id = 'user-uuid';
   ```

==================================================
PERFORMANCE
==================================================

Q: Quantas transactions suporta?
A: PostgreSQL: milhões (com indexes correctos)
   Agora Media: ~100-500/ano previsto
   Performance: excelente para essa escala

Q: Queries lentas, como optimizar?
A: 1. Adicionar indexes (ver MANUTENCAO.md)
   2. Usar select (só campos necessários)
   3. Paginação (limitar resultados)
   4. Cache (futuro: Redis para dashboards)

Q: Database cresce muito?
A: Crescimento estimado:
   ```
   - 500 transactions/ano ≈ 5MB/ano
   - Ficheiros uploads: varia (PDFs/imagens)
   
   10 anos ≈ 50MB database + uploads
   ```
   
   Não é problema.

Q: Posso eliminar dados antigos?
A: Sim, mas NÃO RECOMENDADO (contabilidade = histórico importante).
   
   Se necessário:
   ```bash
   # 1. Exportar para CSV (backup)
   # Via UI: Transactions → Export → CSV
   
   # 2. Arquivar noutra database
   pg_dump ... > archive-2020.sql
   
   # 3. Eliminar
   psql $DATABASE_URL
   ```
   
   ```sql
   DELETE FROM transactions WHERE "issuedAt" < '2020-01-01';
   ```

==================================================
SUPORTE
==================================================

Q: Onde pedir ajuda?
A: 1. Este FAQ (primeira linha!)
   2. Documentação /memory/*.md
   3. Logs sistema:
      ```bash
      docker-compose logs -f app
      ```
   4. Issues GitHub repo
   5. Contactar equipa desenvolvimento

Q: Encontrei bug, como reportar?
A: GitHub Issues:
   1. Descrever problema
   2. Steps para reproduzir
   3. Comportamento esperado vs actual
   4. Screenshots/logs
   5. Versão sistema:
      ```bash
      git log -1 --oneline
      ```

Q: Quero feature nova, como pedir?
A: GitHub Issues:
   1. Descrever use case
   2. Porquê é necessário
   3. Como imaginam funcionar
   4. Prioridade (nice-to-have vs crítico)

Q: Posso contratar desenvolvimento?
A: Sistema interno Agora Media, mas podes:
   - Desenvolver tu (open-source)
   - Contratar freelancer (acesso ao código)
   - Pedir ajuda comunidade TaxHacker

==================================================
OUTRAS PERGUNTAS
==================================================

Q: TaxHacker original recebe updates, como integrar?
A: ```bash
   # 1. Adicionar upstream
   git remote add upstream https://github.com/vas3k/TaxHacker.git
   
   # 2. Fetch
   git fetch upstream
   
   # 3. Review changes
   git log upstream/main
   
   # 4. Cherry-pick features interessantes
   git cherry-pick <commit>
   
   # 5. Resolver conflitos
   
   # 6. Testar!
   npm run dev
   ```
   
   ATENÇÃO: Só integrar se realmente necessário.

Q: Posso usar para outra empresa?
A: Sim! É open-source.
   
   Ajustar:
   - Remover lógica específica Agora (saldos pessoais)
   - Customizar categories/projects
   - Adaptar cálculos fiscais (se outro país)

Q: Há app mobile?
A: Não. Web responsive funciona em mobile.
   Futuro: PWA (instalar como app) possível.

Q: Posso exportar todos os dados?
A: Sim!
   
   ```bash
   # Transactions: Export → CSV (via UI)
   
   # Database completa
   pg_dump $DATABASE_URL > full-export.sql
   
   # Ficheiros
   tar -czf uploads-export.tar.gz data/uploads/
   ```
   
   Zero vendor lock-in!

Q: Licença software?
A: TaxHacker: MIT License (permissivo)
   Agora Contabilidade: (definir - provavelmente MIT também)
   
   Podes:
   ✅ Usar comercialmente
   ✅ Modificar
   ✅ Distribuir
   ✅ Sublicenciar
   
   Obrigatório:
   ✅ Incluir copyright notice
   ✅ Incluir license text

==================================================
RECURSOS ÚTEIS
==================================================

DOCUMENTAÇÃO SISTEMA:
- INDEX.md - Índice completo
- README.md - Overview e quick start
- SETUP_INICIAL.md - Instalação passo-a-passo
- MAPEAMENTO_DADOS.md - Estrutura dados
- ARQUITETURA.md - Organização código
- ROADMAP_IMPLEMENTACAO.md - Plano desenvolvimento
- MIGRACAO_DADOS.md - Migrar de Python
- MANUTENCAO.md - Operações e backup
- DECISOES_TECNICAS.md - Rationale escolhas
- FAQ.md - Este ficheiro!

DOCUMENTAÇÃO EXTERNA:
- TaxHacker: https://github.com/vas3k/TaxHacker
- Next.js: https://nextjs.org/docs
- Prisma: https://www.prisma.io/docs
- React: https://react.dev
- TypeScript: https://www.typescriptlang.org/docs
- PostgreSQL: https://www.postgresql.org/docs
- Docker: https://docs.docker.com

COMANDOS RÁPIDOS:

```bash
# ========================================
# DESENVOLVIMENTO
# ========================================
npm run dev                  # Rodar app dev
npx prisma studio            # GUI database
npm run build                # Build produção

# ========================================
# DATABASE
# ========================================
npx prisma migrate dev       # Criar migration
npx prisma migrate deploy    # Aplicar em prod
npx prisma generate          # Gerar client
npx prisma db push           # Push schema (dev)

# ========================================
# DOCKER
# ========================================
docker-compose up -d         # Iniciar
docker-compose logs -f app   # Ver logs
docker-compose restart       # Reiniciar
docker-compose down          # Parar

# ========================================
# BACKUP
# ========================================
./scripts/backup-db.sh       # Backup manual
ls /var/backups/agora-*/     # Ver backups
```

==================================================
GLOSSÁRIO
==================================================

```
Transaction      Registo financeiro (receita ou despesa)
Project          Agrupamento transactions (EMPRESA, PESSOAL_BRUNO, PESSOAL_RAFAEL)
Category         Estado/tipo transaction (RECEBIDO, FATURADO, FIXA_MENSAL, etc)
Custom Field     Campo adicional configurado pelo user
Extra JSON       Campo livre para dados específicos (premio_bruno, cliente_nome, etc)
Saldo            INs - OUTs de um sócio
Boletim          Pagamento empresa → sócio (ajudas custo, etc)
Prémio           Bonus sócio em projeto empresa
Cêntimos         Valores monetários guardados como Int (x100)
Prisma           ORM (Object-Relational Mapping) usado
Migration        Script alteração schema database
Seed             Popular database com dados iniciais
Self-hosted      Hospetar em infraestrutura própria (vs cloud SaaS)
Fork             Cópia repositório para desenvolvimento independente
```

==================================================

TENS OUTRA PERGUNTA?

Adiciona aqui! Ficheiro vivo, actualizar quando surgirem dúvidas frequentes.

Formato:
```
Q: Pergunta clara?
A: Resposta concisa e prática.
   Bullets se vários pontos.
   Links se relevante.
```

==================================================
