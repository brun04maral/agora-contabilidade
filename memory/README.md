# 📚 Sistema Memory - Documentação de Desenvolvimento

Última atualização: 2025-11-17 09:50 WET

Este diretório contém toda a documentação técnica e de contexto do projeto Agora Contabilidade.

====================================================================
LEITURA OBRIGATÓRIA PARA NOVAS SESSÕES
====================================================================

1. CURRENT_STATE.md - Estado atual do projeto (sprint, features, issues)
2. TODO.md - Tarefas priorizadas (🔥/🔴/🟡/🟢)
3. ARCHITECTURE.md - Como funciona (fluxos, padrões, componentes)

====================================================================
DOCUMENTAÇÃO TÉCNICA
====================================================================

DATABASE_SCHEMA.md (22KB, 806 linhas)
├─ Estrutura completa da base de dados
├─ 13 tabelas documentadas (campos, enums, relações)
├─ Histórico de migrations (001-023 aplicadas)
├─ Migrations planeadas (024-025)
└─ Índices, queries comuns, backup

BUSINESS_LOGIC.md (10KB, ~400 linhas)
├─ Regras de negócio por módulo
├─ 1. Orçamentos (validações, conversão)
├─ 2. Projetos (estados, prémios, transições)
├─ 3. Despesas (tipos, divisão 50/50, templates)
├─ 4. Boletins Itinerário (cálculos, valores ref)
├─ 5. Cálculos Financeiros (saldos pessoais)
└─ 6. Equipamento (rendimento acumulado)

DECISIONS.md (30KB)
├─ ADRs (Architecture Decision Records)
├─ Decisões técnicas importantes
├─ Trade-offs e justificações
└─ Histórico de escolhas (framework, patterns)

ARCHITECTURE.md (15KB)
├─ Visão geral da arquitetura
├─ Padrão Manager → Model → Screen
├─ Fluxos principais (orçamentos, projetos)
├─ Componentes reutilizáveis
└─ Organização de pastas

====================================================================
FEATURES PLANEADAS
====================================================================

FISCAL.md (39KB, 9 secções)
├─ Sistema fiscal completo (documentado)
├─ 1. Receitas e Faturação (tabela receitas)
├─ 2. IVA Trimestral (periodicidade mensal)
├─ 3. IRS Retido na Fonte (11.5%)
├─ 4. IRC Anual (21%)
├─ 5. Segurança Social (21.4% + 11%)
├─ 6. SAF-T (PT) - Exportação trimestral
├─ 7. Calendário Fiscal
├─ Status: Planeado, aguarda validação TOC
└─ Migration: 025 (estimativa 3-4 semanas)

PLANO_SOCIOS.md
├─ Features específicas para gestão de sócios
├─ Planeamento e ideias
└─ Status: Documentação inicial

====================================================================
HISTÓRICO E LOGS
====================================================================

CHANGELOG.md (53KB)
├─ Histórico completo de alterações
├─ Organizado por data (mais recente primeiro)
├─ Commits importantes documentados
└─ Referência cruzada com migrations

TODO.md (34KB)
├─ Tarefas priorizadas por urgência
├─ 🔥 AGORA - Sprint atual
├─ 🔴 Alta Prioridade - Próximas 2 semanas
├─ 🟡 Média Prioridade - Próximo mês
└─ 🟢 Baixa Prioridade - Backlog

====================================================================
GUIAS E SETUP
====================================================================

DEV_SETUP.md
├─ Setup do ambiente de desenvolvimento
├─ Dependências (Python, SQLAlchemy, CustomTkinter)
├─ Configuração da base de dados
└─ Primeiros passos

GUIA_COMPLETO.md
├─ Guia para utilizador final
├─ Como usar cada screen
├─ Fluxos de trabalho comuns
└─ Dicas e boas práticas

ASSET_SYSTEM.md
├─ Sistema de assets e ícones
├─ Ícones PNG Base64 embutidos
├─ Logos PNG de alta qualidade
└─ Como adicionar novos assets

====================================================================
ARQUIVO HISTÓRICO
====================================================================

archive/
├─ Documentação obsoleta ou substituída
├─ Versões antigas de ficheiros importantes
└─ Referência histórica (não poluir memória ativa)

====================================================================
SISTEMA DE ATUALIZAÇÃO AUTOMÁTICA
====================================================================

📖 Guia completo: memory/HOW_TO_UPDATE.md

CHAVE MÁGICA (usa no final de sessões com Claude Code):

┌────────────────────────────────────────────────────────────────┐
│                                                                 │
│  "Atualiza memory/. Segue HOW_TO_UPDATE.md."                  │
│                                                                 │
└────────────────────────────────────────────────────────────────┘

O Claude Code analisa automaticamente:
- Commits da sessão
- Features implementadas  
- Bugs corrigidos
- Alterações em BD/arquitetura

E atualiza os ficheiros corretos:
- CHANGELOG.md (histórico completo)
- TODO.md (move tasks)
- CURRENT_STATE.md (estado atual)
- Outros conforme necessário

VARIAÇÕES ACEITES:
- "Atualiza memory/. Segue HOW_TO_UPDATE.md."
- "Sync memory/. Segue HOW_TO_UPDATE.md."

Ver HOW_TO_UPDATE.md para:
- Workflow completo do CC
- Mapa de responsabilidades (Single Source of Truth)
- Exemplos detalhados
- Regras e validações

====================================================================
IMPORTAÇÃO DE CONTEXTO ENTRE SESSÕES
====================================================================

Ficheiro raiz: /SESSION_IMPORT.md

Frase mágica para novas sessões:
"Esta sessão é continuação de uma anterior. Faz merge do branch da 
última sessão para este branch atual para teres todo o código e 
contexto atualizado. Depois lê o README.md e memory/CURRENT_STATE.md 
para contexto completo."

====================================================================
NAVEGAÇÃO RÁPIDA
====================================================================

CONTEXTO GERAL:
→ CURRENT_STATE.md - Onde estamos agora?
→ TODO.md - O que falta fazer?
→ CHANGELOG.md - O que mudou?

IMPLEMENTAÇÃO:
→ ARCHITECTURE.md - Como funciona?
→ DATABASE_SCHEMA.md - Estrutura de dados?
→ BUSINESS_LOGIC.md - Regras de negócio?

DECISÕES:
→ DECISIONS.md - Porquê desta forma?
→ FISCAL.md - Sistema fiscal (futuro)

AJUDA:
→ DEV_SETUP.md - Como configurar?
→ GUIA_COMPLETO.md - Como usar?

====================================================================
PRINCÍPIOS DO SISTEMA MEMORY
====================================================================

1. Single Source of Truth - Cada informação num só lugar
2. Links Cruzados - Documentos referem-se entre si
3. Estrutura Clara - Fácil navegar e encontrar informação
4. Sempre Atualizado - Reflete estado atual do projeto
5. Histórico em Archive - Documentação obsoleta não polui

====================================================================

Mantido por: Equipa Agora
Para começar: Lê CURRENT_STATE.md → TODO.md → ARCHITECTURE.md
