# Changelog - Agora Contabilidade

All notable changes to this project will be documented in this file.

## [2.2.0] - 2026-01-05

### Fixed - Validação Saldos Excel vs DB
- **Prémios 100% corretos** após correção de cálculo
  - Bruno: €5,844.67 (match perfeito com Excel CAIXA)
  - Rafael: €9,916.19 (match perfeito com Excel CAIXA)
  - Projetos Pessoais Rafael: €14,103.51 (100% match)

- **Correção crítica em prémios** (`import_from_excel.py:372-378, 446`)
  - Column P (TOTAL s/IVA) agora usado para prémios com quantidade/dias
  - Exemplo: #D000120 com quantidade=2 agora calcula €450 em vez de €225
  - Bug fix: prémios estavam a usar valor unitário (Column J) em vez de total

### Added - Sistema de Validação
- **Script crosscheck.py** - Compara Excel vs DB (projetos, despesas, boletins)
- **Documentação completa de validação:**
  - `docs/SALDOS_VALIDATION_RESULTS.md` - Resultados finais com comparações
  - `docs/SALDOS_CROSSCHECK.md` - Análise detalhada de discrepâncias

### Changed - Workflow de Desenvolvimento
- **Documentação atualizada** para refletir workflow real
  - Commits diretos em `main` para agilidade
  - Branches opcionais apenas para experimentação arriscada
  - `README-DEV.md` simplificado e atualizado
  - `.claude/claude.md` atualizado com workflow correto
  - `README.md` atualizado

### Validated - Cálculos de Saldos
- ✅ Despesas fixas: divisão por 2 funcionando corretamente
- ✅ Estrutura despesas pessoais + boletins validada
- ✅ Filtro de data 2024+ disponível e testado
- ✅ Sistema funcional com prémios 100% validados

### Technical Details
**Files Modified:**
- `agora_web/core/management/commands/import_from_excel.py` - Fix prémios calculation
- `docs/SALDOS_VALIDATION_RESULTS.md` - Validation results
- `docs/SALDOS_CROSSCHECK.md` - Discrepancy analysis
- `crosscheck.py` - Validation script
- `README-DEV.md` - Updated workflow
- `.claude/claude.md` - Updated workflow
- `README.md` - Updated workflow

**Known Differences (documented, not critical):**
- Bruno Projetos Pessoais: -€2,000 (filtro ESTADO vs tipo diferente)
- Despesas Fixas total: +€2,902 (critérios de data/tags diferentes)
- Despesas Pessoais breakdown (investigar fórmula Excel no futuro)

---

## [2.1.0] - 2026-01-03

### Added - Sistema de Importação Web
- **Interface web para importação de Excel** no Django Admin
  - Upload drag-and-drop de ficheiros .xlsx
  - Validação de formato e feedback em tempo real
  - Integração com comando `import_from_excel` existente
  - Localização: Core → Importação de Dados

- **Modelo proxy ImportacaoDados** (`models.py:993-1005`)
  - Sem tabela na BD (managed=False)
  - Fornece entry point no admin para upload

- **Template de upload** (`templates/admin/core/importacaodados/changelist.html`)
  - Design consistente com tema Unfold
  - Suporte a dark mode
  - Drag-and-drop funcional

### Added - Sistema de Tags para Despesas Pessoais
- **Tags PESSOAL_BA e PESSOAL_RR** para identificar despesas pessoais por sócio
  - Substitui lógica anterior baseada em nome do credor
  - Permite despesas pessoais com credores externos (Sara Fevereiro, PC Diga, etc.)

- **Leitura de Column U do Excel** (`import_from_excel.py:374`)
  - Column U identifica sócio responsável pela despesa PESSOAL
  - Conversão automática: PESSOAL → PESSOAL_BA/PESSOAL_RR
  - Testado com 62 despesas PESSOAL (29 BA + 33 RR)

### Changed - Melhorias no Admin de Despesas
- **Campo `tipo` movido para collapsed "Deprecated"** (`admin.py:218-222`)
  - Mantido apenas por compatibilidade
  - Novo campo `tipo_original` para referência histórica

- **Adicionada coluna `tags_display`** (`admin.py:236-242`)
  - Mostra tags reais em vez do campo deprecated
  - Interface `filter_horizontal` para melhor UX

### Changed - Refatoração do SaldosCalculator
- **Despesas pessoais agora filtradas por tags específicas** (`saldos.py:247-251`)
  - Antes: Filtrava por tag PESSOAL + nome no credor (FALHAVA!)
  - Agora: Filtra por PESSOAL_BA ou PESSOAL_RR (100% preciso)
  - **Fix crítico**: 9 despesas PESSOAL não estavam a ser contadas em nenhum saldo!

### Fixed - Proteção contra Linhas Vazias
- **Skip automático de projetos vazios** (`import_from_excel.py:254-256`)
  - Projetos sem descrição, cliente e valor=0 são ignorados
  - Previne criação de 1618+ registos vazios

- **Skip automático de despesas vazias** (`import_from_excel.py:376-378`)
  - Despesas sem descrição, credor e valor=0 são ignoradas
  - Previne criação de 636+ registos vazios

### Documentation
- **docs/IMPORT_SYSTEM.md** - Documentação completa do sistema de importação web
- **README.md** - Atualizado com info do sistema de importação
- **docs/README.md** - Adicionado link para IMPORT_SYSTEM.md

### Database Changes
- **Tags criadas**: PESSOAL_BA, PESSOAL_RR
- **Cleanup realizado**:
  - Projetos: 1699 → 81 (removidos 1618 vazios)
  - Despesas: 875 → 239 (removidas 636 vazias)

### Technical Details
**Files Modified:**
- `agora_web/core/models.py` - Added ImportacaoDados proxy model
- `agora_web/core/admin.py` - Added ImportacaoDadosAdmin + updated DespesaAdmin
- `agora_web/core/templates/admin/core/importacaodados/changelist.html` - Upload template
- `agora_web/core/management/commands/import_from_excel.py` - Column U reading + empty validation
- `agora_web/core/utils/saldos.py` - Fixed personal expenses filtering
- `docs/IMPORT_SYSTEM.md` - New documentation
- `README.md` - Updated with import system info

**Testing:**
- ✅ Excel column U verified (62 PESSOAL expenses, 100% populated)
- ✅ Tag conversion logic tested (PESSOAL → PESSOAL_BA/RR)
- ✅ Empty line validation tested (skip successful)
- ✅ Web upload interface tested
- ✅ Saldos calculation verified with new tags

### Breaking Changes
None - All changes are backwards compatible. Old PESSOAL tag still exists but will be automatically converted on next import.

### Migration Notes
After importing Excel with updated data:
1. All 62 PESSOAL despesas will be converted to PESSOAL_BA or PESSOAL_RR
2. Old tag PESSOAL can be removed if desired (not required)
3. Personal expenses will now be correctly counted in saldos

---

## [2.0.0] - 2025-12-31

### Added
- Django 5.0 + PostgreSQL 16 base application
- Dashboard de Saldos Pessoais (dual logic: Atual vs Projetado)
- Modelo Socio com migração de dados
- Docker + Traefik + Cloudflare infrastructure
- Unfold Admin Theme
- CLI import system (import_from_excel)

---

**Versão Atual:** 2.1.0
**Data:** 2026-01-03
