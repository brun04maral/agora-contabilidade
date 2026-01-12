# Changelog - Agora Contabilidade

All notable changes to this project will be documented in this file.

## [2.2.0] - 2026-01-12

### Changed - UI Improvements

- **Logo coloring fixed in Saldos and Fiscal dashboards**
  - Logo now displays in golden color (#d4af37) consistently across all pages
  - Added CSS filter directly to custom dashboard templates (Saldos Pessoais, Estado Fiscal)
  - Issue: Custom dashboards extended `admin/base_site.html` instead of `skeleton.html`
  - Solution: Duplicated logo CSS filter in both templates' extrahead block
  - Files: `agora_web/core/templates/admin/core/saldo/changelist.html`, `agora_web/core/templates/admin/core/fiscal/changelist.html`
  - Commit: 2bb2180

- **Smart search with field prefixes in all list views**
  - Implemented Django search field prefixes for intelligent search prioritization
  - `^field` - Starts with (exact match at beginning, highest priority)
  - `field` - Contains (default)

  **Projetos** (8 searchable fields):
  - Priority: `^numero` (exact code match)
  - Includes: descricao, cliente (nome + nome_formal), tipo, socio, estado, nota

  **Despesas** (10 searchable fields):
  - Priority: `^numero`, `^projeto__numero`
  - Includes: descricao, credor, tags (codigo + nome), tipo_original, estado, nota

  **Boletins** (9 searchable fields):
  - Priority: `^numero`
  - Includes: socio (codigo + nome_completo + nome_curto), mes, ano, estado, descricao, nota

  **Orçamentos** (12 searchable fields):
  - Priority: `^codigo`, `^projeto__numero`
  - Includes: titulo_cliente, cliente, projeto, socio, status, local_evento, descricao_proposta, notas_contratuais, descricao_cliente

  Files: `agora_web/core/admin.py` (lines 148-157, 238-249, 319-329, 464-477)

  **Note:** Full-text search prefix `@` was removed due to Django compatibility issues

- **Date hierarchy filter added to Projetos list**
  - Added `date_hierarchy = 'data_faturacao'` in ProjetoAdmin
  - Enables year/month/day navigation in list header (same as Despesas, Boletins, Orçamentos)
  - File: `agora_web/core/admin.py:160`
  - Commit: 3b0defc

### Added - Progressive Web App (PWA)
- **PWA Manifest** (`/media/manifest.json`)
  - App name, icons, colors, and shortcuts configured
  - Theme color: #d4af37 (golden Agora)
  - Shortcuts to Projetos, Despesas, Saldos
  - Installable on desktop and mobile devices

- **Service Worker** (`/media/sw.js`)
  - Basic offline support with resource caching
  - Version: v1.0.0
  - Scoped to /media/ only for security

- **PWA Meta Tags** (in `core/templates/unfold/layouts/skeleton.html`)
  - theme-color, apple-mobile-web-app-capable, mobile-web-app-capable
  - Open Graph tags for social media
  - Custom install prompt in Portuguese

### Added - Branding System
- **Logo transparente** configured
  - Using `a (yellow).svg` (transparent SVG)
  - Configured in Unfold SITE_LOGO and SITE_ICON
  - Appears in sidebar, favicon, and PWA icons

- **Primary color theme**: #d4af37 (golden Agora)
  - Complete color scale (50-950) in Unfold config
  - Applied to buttons, links, focus states, theme-color

- **Custom Templates**
  - `skeleton.html` - PWA meta tags and Service Worker registration
  - `base_simple.html` - Footer placeholder

### Added - Audit Trail System
- **django-simple-history integration**
  - Complete change history for all models
  - Inline "Ver Histórico" button in change forms
  - Auto-populate created_by/updated_by fields
  - Custom history visualization templates

### Documentation
- **docs/PWA_BRANDING.md** - Complete technical guide
- **BRANDING-PWA-IMPLEMENTATION.md** - Executive summary
- **media/BRANDING-PWA-README.md** - Detailed guide
- **media/logos/PWA-ICONS-README.md** - Icon generation instructions
- **README.md** - Updated with v2.2 release notes
- **docs/README.md** - Updated index with PWA links

### Changed
- **Template loading priority** - core/templates loads first for Unfold overrides
- **Unfold configuration** - Updated with new logo and color scheme
- **README structure** - Added PWA features and audit trail

### Fixed
- Template override structure (using skeleton.html instead of base.html)
- Logo transparency issue (SVG instead of PNG with white background)
- Template discovery by Django (DIRS priority corrected)

### Technical Details
**Commits:** 10 commits including docs
- feat: implementar branding completo e PWA (4b988d0)
- fix: corrigir template PWA para usar skeleton.html (6f3e053)
- fix: priorizar templates do core para override (9b7d92d)
- feat: usar logo novo na sidebar e ícones (f845298)
- fix: usar logo 'a' amarelo transparente (ddc2e1e)
- docs: documentação completa PWA (9ea2f92, f9e0510)

**Files Changed:** 14+ files, 700+ lines added

**Known Issues:**
- PWA icon PNGs not generated yet (192x192, 512x512, apple-touch-icon needed)
- New amp logo has white background (using temporary transparent 'a' logo)
- Login page customization removed (caused template conflicts)

### Testing
- [x] Manifest.json accessible and valid
- [x] Service Worker registered and active
- [x] PWA meta tags present in HTML
- [x] Logo appears in sidebar
- [x] Theme color #d4af37 applied
- [x] Install prompt works (Desktop Chrome)
- [ ] PNG icons generated (pending)
- [ ] Tested on Android/iOS (pending)
- [ ] Lighthouse PWA audit (pending)

---

## [2.1.5] - 2026-01-05

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

**Versão Atual:** 2.2.0
**Data:** 2026-01-12
