# 📊 Estado Atual do Projeto - Agora Contabilidade

**Última atualização:** 2025-11-26 WET
**Branch:** claude/sync-remote-branches-01Frm5T8R4fYXJjn3jEEHnX8
**Status Geral:** ✅ PRODUÇÃO READY

---

## 🚨 NOVA SESSÃO? Importa Contexto Primeiro!

⚠️ Se este branch foi criado do `main`, está **desatualizado**. Usa a frase:

> Esta sessão é continuação de uma anterior. Faz merge do branch da última sessão para este branch atual para teres todo o código e contexto atualizado. Depois lê o README.md e memory/CURRENT_STATE.md para contexto completo.

**Instruções completas:** Ver `/SESSION_IMPORT.md` na raiz.

---

## 📌 Resumo Executivo

**Sprint Atual (26/11/2025):**
- ✅ **Sistema BaseForm - 100% COMPLETO (6/6 FORMS ELEGÍVEIS)** - SPRINT 7 finalizado com ProjetoFormScreen (layout 2 colunas) + Decisões técnicas sobre forms não elegíveis (Orçamento, Boletim mantidos custom) 🎉🚀
- 🎉 **Sistema BaseScreen - 100% COMPLETO** - BaseScreen com **7/7 screens migrados** (Projetos, Orçamentos, Despesas, Boletins, Clientes, Fornecedores, Equipamento) 🎉

**Última Feature Concluída:**
- ✅ **Sistema BaseForm 100% COMPLETO - SPRINT 7** (26/11/2025) - ProjetoFormScreen migrado com layout 2 colunas (PRIMEIRO form a usar!) + Decisões técnicas finais: 6/6 forms elegíveis migrados (Cliente, Fornecedor, Equipamento, Despesa, Projeto). OrcamentoFormScreen (2.175 linhas) e BoletimFormScreen (905 linhas) mantidos custom por complexidade arquitetural (decisão técnica). Framework robusto com 6 tipos campo, 2 layouts (1 e 2 colunas), validação unificada, zero breaking changes. **Ver:** memory/CHANGELOG.md (26/11/2025 - SPRINT 7 + DECISÕES TÉCNICAS FINAIS)

**Próximo Milestone:**
- 📋 Testar e validar sistema BaseScreen completo (7/7 screens)
- 📋 UX/UI Improvements - Orçamentos (DateRangePicker + Context Menus)
- 📋 IRS Retido em Despesas (requisito futuro documentado)
- 📋 Sistema Fiscal (validação TOC + implementação)

**Dados Atuais (Última Importação 15/11/2025):**
- 19 clientes | 44 fornecedores | 75 projetos | 168 despesas | 34 boletins
- 157 registos PAGO (93.5%) | 11 PENDENTE (6.5%)

---

## 🔴 PROBLEMAS ATIVOS (URGENTE)

### 🟢 Nenhum Problema Crítico Ativo

**Último Problema Resolvido:**
- ✅ **BUG-001** (BaseScreen Toolbar Gigante) - Resolvido em 25/11/2025
- Ver: memory/CHANGELOG.md (25/11/2025)
- Ver: memory/BUGS.md (BUG-001 - marcado como resolvido)

---

## ✅ Módulos Implementados

### 🎨 Sistema de Assets e Ícones
**Status:** ✅ Completo  
**Implementado:** 13/11/2025

**Features:**
- 11 ícones PNG Base64 embutidos no código
- Sistema de fallback: SVG → PNG → Emoji
- Logos PNG alta qualidade (71KB, 156KB) fornecidos manualmente
- Aplicado em: Sidebar (27x27), Títulos screens (22x22), Dashboard

**Ver:** `memory/ASSET_SYSTEM.md`

---

### 💾 Base de Dados
**Status:** ✅ Completo
**Última Migration:** 028 (24/11/2025)

**Tabelas Principais (16):**
- Core: socios, clientes, fornecedores
- Projetos: projetos, orcamentos, orcamento_itens, orcamento_reparticoes
- Despesas: despesas, despesa_templates
- Boletins: boletins, boletim_linhas, valores_referencia_anual
- Equipamento: equipamento
- **Externos:** freelancers, freelancer_trabalhos, fornecedor_compras

**Migrations Recentes:**
- ✅ 020: Owner em orçamentos/projetos, rastreabilidade financeira (15/11)
- ✅ 021: Cliente nome e nome_formal (15/11)
- ✅ 022-023: Orçamentos V2 - sistema tipo-específico (16-17/11)
- ✅ 024: Campo projeto_id em orcamentos (17/11)
- ✅ 025: Freelancers e fornecedores multi-entidade (17/11)
- ✅ 026: Percentagem comissões 4 casas decimais (18/11)
- ✅ 027: Campo owner em projetos (24/11)
- ✅ 028: Refatorar TipoProjeto EMPRESA|PESSOAL (24/11)

**Ver:** `memory/DATABASE_SCHEMA.md`

---

### 🖥️ Interface Gráfica
**Status:** ✅ Completo (10 screens funcionais)

**Screens:**
- Dashboard (cards interativos com navegação)
- Saldos Pessoais (navegação clicável completa, 10 botões com filtros)
- Projetos, Orçamentos, Despesas, Boletins
- Clientes, Fornecedores, Equipamento
- Relatórios, Info

**Componentes:**
- DataTableV2 (tabelas com sort, filtros, context menu)
- DatePickerDropdown e DateRangePickerDropdown (calendários visuais)
- Forms reutilizáveis com validação

**Framework:** CustomTkinter (tema moderno, cross-platform)

---

### 💰 Lógica de Negócio
**Status:** ✅ Core completo + Multi-Entidade

**Sistemas Implementados:**
- ✅ Cálculo saldos pessoais (50/50)
- ✅ Gestão projetos (tipos, estados, prémios, transições automáticas)
- ✅ Despesas recorrentes (templates + geração automática)
- ✅ Boletim Itinerário completo (linhas múltiplas, valores anuais, cálculos auto)
- ✅ Orçamentos V2 - Lado CLIENTE completo (5 tipos de items)
- ✅ Orçamentos V2 - Lado EMPRESA completo (3 dialogs multi-entidade)
- ✅ Freelancers e Fornecedores (managers CRUD completos)
- ✅ Rastreabilidade pagamentos (trabalhos/compras automáticos)

**Managers Implementados:**
- FreelancersManager (CRUD, listar_ativos, gerar_proximo_numero)
- FornecedoresManager (expandido com listar_ativos)
- FreelancerTrabalhosManager (CRUD, marcar_como_pago, calcular_total_a_pagar)
- FornecedorComprasManager (CRUD, marcar_como_pago, calcular_total_a_pagar)

**Ver:** `memory/BUSINESS_LOGIC.md` (33KB, 5 secções)

---

### 📦 Sistema de Importação
**Status:** ✅ Completo  
**Última Importação:** 15/11/2025

**Features:**
- Modo incremental (skip registos existentes)
- Flags: `--dry-run`, `--excel PATH`, `--clear-all`
- Matching inteligente por número (#C001, #P001)
- Estatísticas detalhadas (NEW/SKIP/UPDATED/ERROR)

**Script:** `scripts/import_from_excel.py`

---

### 🧠 Sistema de Documentação
**Status:** ✅ Completo e organizado

**Pasta memory/ (13 ficheiros):**
- CURRENT_STATE.md (este ficheiro)
- TODO.md (tarefas priorizadas, 34KB)
- ARCHITECTURE.md (arquitetura, 15KB)
- DECISIONS.md (ADRs, 30KB)
- DATABASE_SCHEMA.md (schema completo, reorganizado 17/11)
- BUSINESS_LOGIC.md (regras negócio, 33KB)
- FISCAL.md (sistema fiscal, 39KB - planeado)
- CHANGELOG.md (histórico completo, 53KB)
- DEV_SETUP.md, GUIA_COMPLETO.md, PLANO_SOCIOS.md
- ASSET_SYSTEM.md, README.md

**Sistema "Frase-Chave":**
- Atualização flexível de docs via prompt específico
- Ver `memory/README.md` e `/SESSION_IMPORT.md`

**Pasta archive/:** Documentação histórica (não poluir memória ativa)

---

## 🚧 Trabalho em Curso

### Sprint Atual: Orçamentos V2 Sistema Multi-Entidade - COMPLETO ✅

**Concluído (17/11/2025):**

**PARTE 1 - Dialogs CLIENTE (5/5):**
- ✅ ServicoDialog (Commit: 59e4504)
- ✅ EquipamentoDialog (Commit: 75085bd)
- ✅ TransporteDialog (Commit: 7baf6d1)
- ✅ RefeicaoDialog (Commit: 86be721)
- ✅ OutroDialog (Commit: 48eec23)

**PARTE 2 - Dialogs EMPRESA (3/3):**
- ✅ ServicoEmpresaDialog (Commit: 7bf6580)
- ✅ EquipamentoEmpresaDialog (Commit: 7bf6580)
- ✅ ComissaoDialog (Commit: febbff8)

**PARTE 3 - Migration 025 + Beneficiários Multi-Entidade:**
- ✅ Migration 025: freelancers, trabalhos, compras (Commit: 7592a88)
- ✅ Beneficiários multi-entidade em todos dialogs EMPRESA (Commit: 1aa4ee5)
- ✅ Managers: FreelancersManager, FreelancerTrabalhosManager, FornecedorComprasManager
- ✅ Lógica aprovação com registos históricos automáticos (Commit: 1b6d2e1)

**Próximo Sprint:**
- 📋 UX Improvements - DateRangePicker + Context Menus em Orçamentos
- 📋 UI Gestão Freelancers (screen CRUD)
- 📋 UI Trabalhos/Compras (listar, marcar como pago)

**Ver:** `memory/TODO.md`, `memory/CHANGELOG.md` (17/11/2025)

---

### Funcionalidades em Teste

**Boletim Itinerário (Fase 4 - Testes):**
- [ ] Criar dados de teste (valores ref 2024-2026, templates, boletins)
- [ ] Validar cálculos automáticos (ajudas + kms)
- [ ] Testar geração recorrente (duplicados, edge cases)
- [ ] Edge cases (zeros, projeto apagado, ano sem valores)

**Status:** Implementação completa (Migrations 016-019) ✅ | Aguarda testes locais

---

## 📋 Documentação de Features Planeadas

### 💰 Sistema Fiscal (Alta Prioridade)
**Documentação:** 📄 `memory/FISCAL.md` (39KB, 9 secções completas)  
**Status:** 📝 Planeado, aguarda validação TOC  
**Prioridade:** 🔴 Alta

**Escopo:**
1. Receitas e Faturação (tabela `receitas`)
2. IVA Trimestral (periodicidade mensal)
3. IRS Retido na Fonte (11.5%)
4. IRC Anual (21%)
5. Segurança Social (21.4% + 11%)
6. SAF-T (PT) - Exportação trimestral
7. Calendário Fiscal completo

**Migration:** 025 (planeada)  
**Estimativa:** 3-4 semanas após validação  
**Ver:** `memory/TODO.md` (linha 25), `memory/FISCAL.md`

---

## 🐛 Problemas Conhecidos

### ⚠️ Scroll em Popups Modais (Postponed)
**Descrição:** Scroll em popup modal propaga para lista de fundo  
**Impacto:** UX menor, não bloqueia funcionalidades  
**Status:** Issue postponed após 7+ tentativas sem sucesso (11/11/2025)  
**Decisão:** Aguardar solução framework ou investigação futura  
**Ver:** `memory/TODO.md` (linha 20) para histórico técnico completo

---

### 🟢 Logo SVG Contém PNG (Resolvido)
**Descrição:** Logo SVG não é vetorial verdadeiro  
**Solução:** PNGs mantidos manualmente com alta qualidade (71KB, 156KB)  
**Status:** ✅ Resolvido com workaround

---

## 🏗️ Arquitetura

agora-contabilidade/
├── main.py                 # Entry point
├── database/              
│   ├── models/            # SQLAlchemy models (13 tabelas)
│   └── migrations/        # Migration scripts (001-023)
├── logic/                 # Business logic (managers)
├── ui/
│   ├── screens/          # 10 screens principais
│   └── components/       # DataTableV2, DatePickers, Forms
├── scripts/              # Importação, migrations, utilidades
├── assets/               # Ícones Base64
├── media/                # Logos PNG
└── memory/               # 📚 Documentação desenvolvimento (13 ficheiros)

**Padrão:** Manager → Model → Screen (separação clara de concerns)

---

## 🔗 Documentação Relacionada

**Leitura obrigatória para novas sessões:**
1. 📄 **memory/README.md** - Índice sistema memory
2. 📄 **memory/TODO.md** - Tarefas priorizadas (🔥/🔴/🟡/🟢)
3. 📄 **memory/ARCHITECTURE.md** - Como funciona (fluxos, padrões)
4. 📄 **memory/BUSINESS_LOGIC.md** - Regras de negócio detalhadas

**Referência técnica:**
5. 📄 **memory/DATABASE_SCHEMA.md** - Schema completo (reorganizado 17/11)
6. 📄 **memory/DECISIONS.md** - ADRs (Architecture Decision Records)
7. 📄 **memory/CHANGELOG.md** - Histórico completo de alterações

**Features futuras:**
8. 📄 **memory/FISCAL.md** - Sistema fiscal (39KB, aguarda validação)
9. 📄 **memory/PLANO_SOCIOS.md** - Planeamento features sócios

**Setup e guias:**
10. 📄 **memory/DEV_SETUP.md** - Setup ambiente desenvolvimento
11. 📄 **memory/GUIA_COMPLETO.md** - Guia utilizador final
12. 📄 **/SESSION_IMPORT.md** (raiz) - Importar contexto entre sessões

---

## 🎯 Próximos Passos Imediatos

**Ver TODO.md para lista completa priorizada.**

**🔥 AGORA (Esta/Próxima Sessão):**
1. Implementar 5 dialogs EMPRESA (Orçamentos V2)
2. Testar sistema Boletim Itinerário (criar dados teste)

**🔴 Alta Prioridade (Próximas 2 semanas):**
3. UX/UI Improvements - Orçamentos e Boletins (18 melhorias)
4. Validar sistema fiscal com TOC
5. Implementar tabela receitas (Migration 025)

**🟡 Média Prioridade (Próximo mês):**
6. Sistema Freelancers/Fornecedores (Migration 024)
7. Testes integração completos
8. Build Windows (PyInstaller)

---

**Mantido por:** Equipa Agora  
**Para contexto completo:** Começa sempre por `memory/README.md`
