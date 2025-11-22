# 📊 Estado Atual do Projeto - Agora Contabilidade

Última atualização: 2025-11-22 10:42 WET
Branch: claude/sync-branch-updates-01E272Kg4MfomDai3tRbLKDz
Status Geral: ✅ PRODUÇÃO READY

---

## 🚨 NOVA SESSÃO? Importa Contexto Primeiro

⚠️ Se este branch foi criado do main, está desatualizado.
Frase padrão:
Esta sessão é continuação de uma anterior. Faz merge do branch da última sessão para este branch atual para teres todo o código e contexto atualizado. Depois lê o README.md e memory/CURRENT_STATE.md para contexto completo.
Ver instruções: /SESSION_IMPORT.md

---

## 📌 Resumo Executivo

Sprint Atual (22/11/2025):
- Orçamentos V2 - Menu Context + UX Comissões

Última Feature Concluída:
- Menu Right-Click Orçamentos (21/11/2025) - Menu de contexto completo com todas acções (Visualizar, Editar, Duplicar, Marcar Aprovado/Pago, Anular, Apagar). Botão Duplicar na barra inferior. Backend: duplicar_orcamento(), mudar_status(). Input manual + setas repeat nas comissões. Campo código editável. Ver: memory/CHANGELOG.md (21/11/2025)

Próximo Milestone:
- Testar sistema Orçamentos V2 completo (CLIENTE + EMPRESA)
- UI Gestão Freelancers (screen CRUD)

Dados Atuais (Última Importação 15/11/2025):
- 19 clientes | 44 fornecedores | 75 projetos | 168 despesas | 34 boletins
- 157 registos PAGO (93.5%) | 11 PENDENTE (6.5%)

---

## ✅ Módulos Implementados

Sistema de Assets e Ícones: Completo
Base de Dados: Completo (Migration 026, 18/11/2025)
Interface Gráfica: Completa (10 screens principais)
Lógica de Negócio: Core completo + Multi-entidade (Boletins, Orçamentos, Freelancers, Rastreabilidade)
Sistema de Importação: Completo (scripts/import_from_excel.py)
Sistema de Documentação: Completo e organizado (memory/)
Arquitetura: Manager → Model → Screen (separação clara de concerns)

---

## 🚧 Trabalho em Curso

Sprint Atual: Orçamentos V2 Sistema Multi-Entidade - COMPLETO (17/11/2025)
Dialogs CLIENTE (5/5), Dialogs EMPRESA (3/3), Migration 025, Beneficiários multi-entidade.
Managers/CRUD freelancers e fornecedores, pagamentos rastreáveis, lógica aprovação.

Funcionalidades em Teste:
Boletim Itinerário (valores ref 2024-2026, templates, boletins, edge cases, cálculos auto)
Status: Implementação completa, em testes locais.

---

## 📋 Documentação de Features Planeadas

Sistema Fiscal (Alta Prioridade)
- Toda a arquitetura fiscal encontra-se no FISCAL.md
- Tabelas: receitas, despesa, IVA trimestral, IRS retido, IRC anual, SS, export SAF-T
- Migration 025 planeada, dependente do TOC, revisão em TODO.md

---

## 🟢 Integrações Planeadas (TOConline, BizDocs, BPI)

(Estado: apenas planeadas, não prioritárias, NÃO implementado)

- Encontra-se documentado em INTEGRACOES.md (ver detalhes e roadmap)
- Prevê-se a futura integração manual (CSV) para:
  - Faturas TOConline (import manual e/ou sugestão API futura)
  - Despesas BizDocs (import manual CSV, API apenas se volume justificar)
  - Movimentos bancários BPI (export extrato, matching automático com despesas/receitas)

- Matching e reconciliação serão implementados como features futuras de baixa prioridade.
- Nenhuma ligação automática/API ativa neste momento; sistema preparado na base de dados para extensões.
- Revisão TAG: backlog 🟢 no TODO.md

---

## 🐛 Problemas Conhecidos

Scroll em Popups Modais (postponed)
Logo SVG contém PNG (resolvido)
Ver secção detalhada original para histórico do relatório

---

## 🔗 Documentação Relacionada

- README.md - Índice sistema memory
- TODO.md - Tarefas priorizadas
- ARCHITECTURE.md - Arquitetura e fluxos
- DATABASE_SCHEMA.md - Schema completo
- BUSINESS_LOGIC.md - Regras de negócio detalhadas
- FISCAL.md - Sistema fiscal completo
- INTEGRACOES.md - Especificação de integrações externas

---

## Próximos Passos Imediatos
Ver TODO.md para lista completa priorizada.

🔥 AGORA: Implementar dialogs EMPRESA, testar boletins itinerário
🔴 Alta Prioridade: UX Orçamentos e Boletins, validação fiscal, tabela receitas
🟡 Média Prioridade: Sistema Freelancers, Testes integração, Build Windows

---

Mantido por: Equipa Agora
Sempre começar por README.md para contexto
