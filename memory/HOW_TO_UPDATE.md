# 🔧 HOW_TO_UPDATE.md - Guia de Atualização do Sistema Memory

Última atualização: 2025-11-17 11:20 WET

Este guia instrui o Claude Code (CC) sobre como atualizar corretamente 
a documentação em /memory/ de forma automática, mantendo organização, 
coerência e evitando redundâncias.

====================================================================
🎯 PARA O UTILIZADOR (BRUNO)
====================================================================

No final de qualquer sessão com Claude Code, usa esta frase:

┌────────────────────────────────────────────────────────────────┐
│                                                                 │
│  "Atualiza memory/. Segue HOW_TO_UPDATE.md."                  │
│                                                                 │
└────────────────────────────────────────────────────────────────┘

Pronto! O CC faz o resto automaticamente.

VARIAÇÕES ACEITES:
- "Atualiza memory/. Segue HOW_TO_UPDATE.md."
- "Atualiza memory/ com as alterações desta sessão. Segue HOW_TO_UPDATE.md."
- "Sync memory/. Segue HOW_TO_UPDATE.md."

====================================================================
📋 PARA O CLAUDE CODE - WORKFLOW COMPLETO
====================================================================

Quando recebes o comando "Atualiza memory/. Segue HOW_TO_UPDATE.md.":

PASSO 1: ANALISAR SESSÃO ATUAL
───────────────────────────────

1.1 Lista TODOS os commits da sessão (git log)
1.2 Identifica alterações por categoria:
    ├─ ✅ Features implementadas (novas funcionalidades)
    ├─ 🐛 Bugs corrigidos (fixes)
    ├─ 📝 Planeamento (specs, decisões sobre futuro)
    ├─ 🗄️ Alterações BD (migrations, tabelas, campos)
    ├─ 🏗️ Alterações arquitetura (novos patterns, refactors)
    └─ 📚 Alterações documentação (README, guides)

1.3 Resume em formato estruturado:
    """
    SESSÃO: [data] - [branch]
    
    FEATURES CONCLUÍDAS:
    - Feature X (commit abc1234)
    - Feature Y (commit def5678)
    
    BUGS CORRIGIDOS:
    - Bug Z (commit ghi9012)
    
    PLANEAMENTO:
    - Sistema W documentado
    
    BD:
    - Migration 025 aplicada
    """

PASSO 2: MAPEAR PARA FICHEIROS (Single Source of Truth)
────────────────────────────────────────────────────────

Consulta este mapa para saber ONDE atualizar cada tipo de info:

┌─────────────────────────────────────────────────────────────────┐
│ TIPO DE ALTERAÇÃO    │ FICHEIROS A ATUALIZAR                    │
├──────────────────────┼──────────────────────────────────────────┤
│ Feature concluída    │ 1. CHANGELOG.md (SSoT - detalhes)        │
│                      │ 2. TODO.md (move 🔥→✅, resumo)          │
│                      │ 3. CURRENT_STATE.md (última feature)     │
├──────────────────────┼──────────────────────────────────────────┤
│ Bug corrigido        │ 1. CHANGELOG.md (SSoT - detalhes)        │
│                      │ 2. CURRENT_STATE.md (remove problema)    │
├──────────────────────┼──────────────────────────────────────────┤
│ Planeamento          │ 1. TODO.md (nova task em prioridade)     │
│                      │ 2. Specs: DATABASE_SCHEMA.md OU          │
│                      │    BUSINESS_LOGIC.md (conforme tipo)     │
├──────────────────────┼──────────────────────────────────────────┤
│ Migration aplicada   │ 1. DATABASE_SCHEMA.md (secção ✅)        │
│                      │ 2. CHANGELOG.md (entry com data)         │
│                      │ 3. CURRENT_STATE.md (atualiza metadata)  │
├──────────────────────┼──────────────────────────────────────────┤
│ Decisão técnica      │ 1. DECISIONS.md (SSoT - ADR completo)    │
│                      │ 2. CHANGELOG.md (entry resumida)         │
├──────────────────────┼──────────────────────────────────────────┤
│ Refactor/Arquitetura │ 1. ARCHITECTURE.md (atualiza secção)     │
│                      │ 2. CHANGELOG.md (entry técnica)          │
└──────────────────────┴──────────────────────────────────────────┘

PASSO 3: EXECUTAR UPDATES
──────────────────────────

Para CADA alteração identificada:

3.1 ATUALIZAR FICHEIRO PRINCIPAL (SSoT)
    → Adiciona informação COMPLETA
    → Usa estrutura existente do ficheiro
    → Inclui data (DD/MM/YYYY)
    → Exemplos de código/queries se relevante
    → Referências a commits (só em CHANGELOG.md)

3.2 ATUALIZAR FICHEIROS SECUNDÁRIOS
    → Adiciona APENAS resumo + link para SSoT
    → Formato: "Feature X - Ver CHANGELOG.md (DD/MM/YYYY)"
    → NÃO duplica informação detalhada

3.3 ADICIONAR LINKS CRUZADOS
    → Sempre que mencionas conceito de outro ficheiro:
      "Ver: memory/FICHEIRO.md (Secção Y)"
    
3.4 MANTER LIMITES
    → TODO.md 🔥 AGORA: máx 3-5 tasks
    → TODO.md ✅ Concluído: máx 5 features recentes
    → Se exceder: arquiva antigas em CHANGELOG.md

PASSO 4: CONFIRMAR E REPORTAR
──────────────────────────────

Apresenta resumo estruturado:

"""
✅ Memory atualizado com sucesso!

FICHEIROS ATUALIZADOS:
├─ CHANGELOG.md
│  └─ 3 features, 2 fixes (17/11/2025)
├─ TODO.md
│  ├─ 2 tasks movidas 🔥→✅
│  └─ 1 task nova em 🔴 Alta
├─ CURRENT_STATE.md
│  ├─ Última feature: ServicoEmpresaDialog
│  └─ Sprint atualizado
└─ DATABASE_SCHEMA.md
   └─ Migration 025 marcada como ✅

PRÓXIMOS PASSOS SUGERIDOS:
- Commit: "docs: atualizar memory/ após sessão [data]"
- Review: verificar links cruzados
"""

====================================================================
📚 MAPA DETALHADO DE RESPONSABILIDADES (SSoT)
====================================================================

Cada ficheiro tem ÚNICO propósito. Consulta antes de atualizar:

CURRENT_STATE.md
────────────────
O QUE VAI AQUI:
- Estado atual do projeto (1 parágrafo)
- Sprint atual (3-5 linhas, máx 3 tasks)
- Última feature concluída (1 parágrafo + data)
- Módulos implementados (lista high-level)
- Problemas ativos (lista atual, não histórico)
- Trabalho em curso (resumo 5-10 linhas)

O QUE NÃO VAI:
- Histórico completo (vai em CHANGELOG.md)
- Detalhes técnicos (commits, código)
- Features antigas (>1 mês)
- Specs completas (vão em DATABASE_SCHEMA/BUSINESS_LOGIC)

ATUALIZAR QUANDO:
- Feature concluída (atualiza "Última feature")
- Novo sprint (atualiza "Sprint atual")
- Problema resolvido (remove de "Problemas ativos")

TODO.md
───────
O QUE VAI AQUI:
- 🔥 AGORA: máx 3-5 tasks em execução
- 🔴 Alta: top 5 próximas 2 semanas
- 🟡 Média: features próximo mês (agrupadas)
- 🟢 Baixa: backlog (máx 10-15 items)
- ✅ Concluído: últimas 5 features APENAS

O QUE NÃO VAI:
- Detalhes de implementação
- Commits e hashes
- Histórico >1 mês (arquiva em CHANGELOG.md)
- Specs completas (link para DATABASE_SCHEMA.md)

ATUALIZAR QUANDO:
- Task iniciada (adiciona em 🔥 AGORA)
- Task concluída (move para ✅, resumo 1 linha)
- Nova task planeada (adiciona em prioridade correta)
- Prioridade muda (move entre secções)

FORMATO ✅ Concluído:
"- ✅ DD/MM: Feature X - Ver CHANGELOG.md (DD/MM/YYYY)"

CHANGELOG.md
────────────
O QUE VAI AQUI (É O ÚNICO COM HISTÓRICO COMPLETO):
- TODAS as alterações com data
- Detalhes técnicos completos
- Commits (hash + mensagem)
- Decisões de implementação
- Código/queries/exemplos
- Problemas encontrados e soluções
- Performance, testes, validações

O QUE NÃO VAI:
- Estado atual (vai em CURRENT_STATE.md)
- Tasks futuras (vão em TODO.md)

ATUALIZAR QUANDO:
- Qualquer commit importante
- Feature concluída (entry detalhada)
- Bug corrigido (problema + solução)
- Migration aplicada (número + alterações)
- Decisão técnica (contexto completo)

FORMATO:
"""
DD/MM/YYYY - tipo: Título

Descrição detalhada...

Commits:
- abc1234: mensagem commit

Alterações:
- Ficheiro X: mudança Y
- Ficheiro Z: mudança W

Ver: [links para outros docs se relevante]
"""

DATABASE_SCHEMA.md
──────────────────
O QUE VAI AQUI:
- Estrutura de TODAS as tabelas
  - Campos (nome, tipo, constraints)
  - Enums (valores possíveis)
  - Relações (FKs, ON DELETE)
  - Índices
- Migrations aplicadas (✅ com data)
- Migrations planeadas (📋 com spec completa)
- Queries comuns (exemplos SQL)
- Diagramas ER (ASCII art)

O QUE NÃO VAI:
- Lógica de negócio (vai em BUSINESS_LOGIC.md)
- Como calcular (vai em BUSINESS_LOGIC.md)
- Regras de validação (vai em BUSINESS_LOGIC.md)
- Código Python (vai em ARCHITECTURE.md ou CHANGELOG.md)

ATUALIZAR QUANDO:
- Nova tabela criada (adiciona na categoria correta)
- Campo adicionado/alterado (atualiza tabela)
- Migration aplicada (move de Planeadas→Aplicadas)
- Migration planeada (adiciona spec em Planeadas)
- Índice adicionado (atualiza secção Índices)

BUSINESS_LOGIC.md
─────────────────
O QUE VAI AQUI:
- Regras de negócio (como funciona)
- Fórmulas de cálculo (matemática)
- Validações (quando/porquê)
- Estados e transições (diagramas)
- Fluxos de trabalho (sequências)
- Casos de uso (exemplos práticos)

O QUE NÃO VAI:
- Estrutura de tabelas (vai em DATABASE_SCHEMA.md)
- Como implementar código (vai em ARCHITECTURE.md)
- Decisões técnicas (vão em DECISIONS.md)

ORGANIZAÇÃO:
Secções por módulo (Orçamentos, Projetos, Despesas, etc)
Cada secção: Conceito → Regras → Cálculos → Casos de uso

ATUALIZAR QUANDO:
- Nova regra de negócio
- Cálculo alterado (atualiza fórmula)
- Nova validação (adiciona em secção correta)
- Fluxo modificado (atualiza diagrama)

ARCHITECTURE.md
───────────────
O QUE VAI AQUI:
- Padrões de design (Manager→Model→Screen)
- Estrutura de pastas (organização)
- Componentes reutilizáveis (DataTableV2, DatePicker)
- Exemplos de código (Python)
- Diagramas de fluxo (aprovação, etc)
- Como estender (adicionar nova feature)

O QUE NÃO VAI:
- Lógica de negócio (vai em BUSINESS_LOGIC.md)
- Estrutura BD (vai em DATABASE_SCHEMA.md)
- Porquês e trade-offs (vão em DECISIONS.md)

ATUALIZAR QUANDO:
- Novo pattern introduzido
- Componente reutilizável criado
- Refactor arquitetural
- Nova estrutura de pastas

DECISIONS.md
────────────
O QUE VAI AQUI:
- ADRs (Architecture Decision Records)
- Porquê escolhemos X e não Y
- Trade-offs considerados
- Alternativas avaliadas
- Contexto histórico da decisão
- Consequências (positivas e negativas)

FORMATO ADR:
"""
## ADR-XXX: Título da Decisão

Data: DD/MM/YYYY
Status: Aceite / Rejeitada / Substituída

Contexto:
[Problema que levou à decisão]

Decisão:
[O que decidimos]

Alternativas Consideradas:
1. Opção A - [prós/contras]
2. Opção B - [prós/contras]

Consequências:
- Positivas: ...
- Negativas: ...

Ver: [links para implementação]
"""

ATUALIZAR QUANDO:
- Decisão técnica importante tomada
- Pattern escolhido (e porquê)
- Framework/lib escolhida (justificação)
- Tradeoff feito conscientemente

====================================================================
✅ REGRAS DE OURO
====================================================================

1. SINGLE SOURCE OF TRUTH (SSoT)
   ✅ Informação completa num ÚNICO ficheiro
   ✅ Outros ficheiros REFERENCIAM com links
   ❌ NUNCA duplica informação detalhada

2. LINKS CRUZADOS
   ✅ Sempre adiciona: "Ver: memory/FICHEIRO.md (Secção X)"
   ✅ Formato consistente
   ❌ Nunca deixa referência "solta" sem link

3. DATAS
   ✅ Sempre inclui data: DD/MM/YYYY
   ✅ Em features, bugs, migrations, decisões
   ❌ Nunca "recentemente" ou "há uns dias"

4. COMMITS
   ✅ Detalhes APENAS em CHANGELOG.md
   ✅ Outros ficheiros: "Ver CHANGELOG.md (data)"
   ❌ Nunca hashes/commits fora de CHANGELOG.md

5. HISTÓRICO
   ✅ CHANGELOG.md: completo e ilimitado
   ✅ TODO.md ✅: máx 5 features recentes
   ✅ CURRENT_STATE.md: só última feature
   ❌ Nunca acumula histórico antigo em TODO/CURRENT_STATE

6. ESTRUTURA
   ✅ Mantém formatação existente de cada ficheiro
   ✅ Adiciona na secção apropriada
   ✅ Usa emojis consistentes (🔥/🔴/🟡/🟢 em TODO.md)
   ❌ Nunca cria secções novas sem necessidade

====================================================================
❌ O QUE NÃO FAZER (ANTI-PATTERNS)
====================================================================

❌ DUPLICAÇÃO
Exemplo errado: Mesma spec em TODO.md e DATABASE_SCHEMA.md
Correto: Spec completa em DATABASE_SCHEMA.md, link em TODO.md

❌ MISTURAR CONCEITOS
Exemplo errado: Lógica negócio em DATABASE_SCHEMA.md
Correto: Estrutura em DATABASE_SCHEMA, lógica em BUSINESS_LOGIC

❌ HISTÓRICO INFINITO
Exemplo errado: TODO.md com 30 features em ✅ Concluído
Correto: Máx 5 em TODO.md, resto em CHANGELOG.md

❌ DETALHES TÉCNICOS FORA DE LUGAR
Exemplo errado: Commits em TODO.md
Correto: Commits só em CHANGELOG.md

❌ SEM DATAS
Exemplo errado: "Feature implementada"
Correto: "Feature implementada (17/11/2025)"

❌ SEM LINKS
Exemplo errado: "Ver estrutura da tabela X"
Correto: "Ver: memory/DATABASE_SCHEMA.md (Secção X)"

====================================================================
📝 EXEMPLO COMPLETO: Feature Concluída
====================================================================

CENÁRIO: ServicoEmpresaDialog implementado nesta sessão

ANÁLISE (Passo 1):
──────────────────
Commits encontrados:
- abc1234: "feat: implementar ServicoEmpresaDialog"
- def5678: "test: adicionar testes ServicoEmpresaDialog"

MAPEAMENTO (Passo 2):
─────────────────────
Tipo: Feature concluída
Ficheiros: CHANGELOG.md, TODO.md, CURRENT_STATE.md

EXECUÇÃO (Passo 3):
───────────────────

1. CHANGELOG.md (SSoT - informação completa):
   """
   17/11/2025 - feat: Implementar ServicoEmpresaDialog
   
   Dialog para adicionar repartição tipo 'servico' no lado EMPRESA 
   de orçamentos. Permite associar beneficiário (BA/RR/AGORA/
   FREELANCER_X/FORNECEDOR_X) com campos quantidade, dias, valor.
   
   Commits:
   - abc1234: feat: implementar ServicoEmpresaDialog
   - def5678: test: adicionar testes ServicoEmpresaDialog
   
   Alterações:
   - ui/screens/orcamentos/dialogs/servico_empresa_dialog.py (NOVO)
   - tests/test_servico_empresa_dialog.py (NOVO)
   
   Campos:
   - beneficiario (dropdown: BA/RR/AGORA/...)
   - quantidade (int, ≥0)
   - dias (int, ≥0)
   - valor_unitario (decimal, ≥0)
   - descricao (text)
   
   Validações:
   - beneficiario obrigatório
   - valores ≥ 0
   - pelo menos 1 campo numérico > 0
   
   Total calculado: quantidade × dias × valor_unitario
   
   Ver: memory/ARCHITECTURE.md (Secção Orçamentos V2)
   """

2. TODO.md:
   Move "Implementar ServicoEmpresaDialog" de:
   🔥 AGORA → ✅ Concluído
   
   Formato:
   "✅ 17/11: ServicoEmpresaDialog - Ver CHANGELOG.md (17/11/2025)"
   
   Verifica limites:
   - ✅ Concluído tem 5 items? Se sim, remove mais antigo
   - 🔥 AGORA tem <5 tasks? OK

3. CURRENT_STATE.md:
   Atualiza secção "Última Feature Concluída":
   """
   **Última Feature Concluída:**
   - ✅ **ServicoEmpresaDialog** (17/11/2025) - Dialog EMPRESA para
     repartições tipo serviço com beneficiário
   
   **Ver:** memory/CHANGELOG.md (17/11/2025)
   """

CONFIRMAÇÃO (Passo 4):
──────────────────────
"""
✅ Memory atualizado!

FICHEIROS:
├─ CHANGELOG.md: Entry completa ServicoEmpresaDialog
├─ TODO.md: Task movida 🔥→✅
└─ CURRENT_STATE.md: Última feature atualizada
"""

====================================================================
📝 EXEMPLO COMPLETO: Bug Corrigido
====================================================================

CENÁRIO: Corrigido cálculo de totais em Boletins

ANÁLISE:
────────
Commit: ghi9012 "fix: corrigir cálculo totais boletim"

MAPEAMENTO:
───────────
Tipo: Bug corrigido
Ficheiros: CHANGELOG.md, CURRENT_STATE.md

EXECUÇÃO:
─────────

1. CHANGELOG.md:
   """
   17/11/2025 - fix: Corrigir cálculo de totais em Boletins
   
   Problema:
   Valores de kms não eram somados corretamente quando tipo=NACIONAL.
   Cálculo ignorava linhas com dias=0.
   
   Solução:
   Alterado cálculo em BoletimManager.recalcular_totais():
   - Inclui todas as linhas independente de dias
   - Soma kms separadamente de dias
   - Total kms = Σ(kms) × val_km (independente de tipo)
   
   Commit: ghi9012
   
   Ficheiro: logic/boletim_manager.py (linhas 156-178)
   
   Testes:
   - Adicionado teste com dias=0, kms>0
   - Validado cálculo com linhas mistas
   
   Ver: memory/BUSINESS_LOGIC.md (Secção 4.4)
   """

2. CURRENT_STATE.md:
   Se bug estava em "Problemas Conhecidos":
   - Remove entrada
   - Adiciona nota:
     """
     ### 🟢 Cálculo Boletins Kms (Resolvido)
     **Status:** ✅ Corrigido (17/11/2025)
     **Problema:** Kms não somados em certas condições
     **Solução:** Ver CHANGELOG.md (17/11/2025)
     """

====================================================================
📝 EXEMPLO COMPLETO: Planeamento
====================================================================

CENÁRIO: Documentado Sistema Freelancers (Migration 024)

ANÁLISE:
────────
Nenhum commit (só planeamento/documentação)
Spec completa escrita em DATABASE_SCHEMA.md

MAPEAMENTO:
───────────
Tipo: Planeamento
Ficheiros: TODO.md (nova task), DATABASE_SCHEMA.md (já tem spec)

EXECUÇÃO:
─────────

1. DATABASE_SCHEMA.md:
   Spec completa já existe na secção "Migration 024 - Planeadas"
   Verifica se está atualizada. Se não:
   - Adiciona detalhes em falta
   - Mantém estrutura existente

2. TODO.md:
   Adiciona nova task em 🟡 Média Prioridade:
   """
   8. Sistema Freelancers e Fornecedores (Migration 024)
      
      ├─ Criar migrations (freelancers, trabalhos, compras)
      ├─ Adicionar modelos e managers
      ├─ Expandir fornecedores (numero, categoria, iban)
      ├─ Implementar screens CRUD
      └─ Integrar com orçamentos (beneficiários)
      
      Estimativa: 1-2 semanas
      Prioridade: Após Sistema Fiscal
      Ver: memory/DATABASE_SCHEMA.md (Migration 024)
   """

3. CHANGELOG.md:
   Adiciona entry de planeamento:
   """
   17/11/2025 - docs: Planeamento Sistema Freelancers
   
   Documentada Migration 024 completa em DATABASE_SCHEMA.md.
   
   Escopo:
   - 3 novas tabelas (freelancers, trabalhos, compras)
   - Expansão fornecedores (3 campos)
   - Integração com orçamentos (beneficiários)
   
   Status: Planeado, aguarda priorização
   Estimativa: 1-2 semanas implementação
   
   Ver: memory/DATABASE_SCHEMA.md (fim do ficheiro)
   Ver: memory/TODO.md (task #8)
   """

====================================================================
🚨 VALIDAÇÕES ANTES DE FINALIZAR
====================================================================

Antes de confirmar updates, verifica:

□ Todas as datas no formato DD/MM/YYYY?
□ Todos os links cruzados funcionam? (ficheiro existe, secção existe)
□ Nenhuma informação duplicada entre ficheiros?
□ TODO.md 🔥 AGORA tem ≤5 tasks?
□ TODO.md ✅ Concluído tem ≤5 features?
□ CURRENT_STATE.md "Última Feature" está atualizada?
□ CHANGELOG.md tem entry para todas as alterações importantes?
□ Commits mencionados só em CHANGELOG.md?
□ Specs técnicas em DATABASE_SCHEMA ou BUSINESS_LOGIC (não em TODO)?
□ Formatação consistente com ficheiro existente?

Se TODOS ✅: confirma e reporta
Se algum ❌: corrige antes de confirmar

====================================================================
📊 TEMPLATE DE CONFIRMAÇÃO
====================================================================

Usa sempre este formato ao confirmar:

"""
✅ Memory atualizado com sucesso!

SESSÃO: [data] - [branch]

ALTERAÇÕES PROCESSADAS:
├─ Features: X concluídas
├─ Bugs: Y corrigidos
├─ Planeamento: Z documentados
└─ Migrations: W aplicadas

FICHEIROS ATUALIZADOS:
├─ CHANGELOG.md
│  └─ [resumo entries]
├─ TODO.md
│  ├─ [tasks movidas]
│  └─ [tasks novas]
├─ CURRENT_STATE.md
│  └─ [alterações principais]
└─ [outros ficheiros]
   └─ [alterações]

ESTATÍSTICAS:
- Commits processados: N
- Entries CHANGELOG: N
- Tasks TODO atualizadas: N
- Links cruzados adicionados: N

PRÓXIMOS PASSOS:
1. Commit: "docs: atualizar memory/ após sessão [data]"
2. Review: verificar links cruzados
3. Push para branch
"""

====================================================================
🆘 EM CASO DE DÚVIDA
====================================================================

Se não tens certeza onde atualizar:

1. Consulta MAPA SSoT (secção acima)
2. Procura exemplos similares em CHANGELOG.md
3. Em dúvida: adiciona em CHANGELOG.md (sempre seguro)
4. Depois pede review humano

Prioridade de segurança:
CHANGELOG.md > TODO.md > CURRENT_STATE.md > outros

====================================================================

Mantido por: Equipa Agora
Versão: 1.0 (2025-11-17)

Este ficheiro segue as próprias regras que documenta! :)
