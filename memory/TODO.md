# 📋 TODO.md - Tarefas Priorizadas

Última atualização: 2025-11-24 WET

====================================================================
LEGENDA DE PRIORIDADES
====================================================================

🔥 AGORA      - Sprint atual (máx 3-5 tasks em execução)
🔴 Alta       - Próximas 2 semanas (features críticas)
🟡 Média      - Próximo mês (melhorias importantes)
🟢 Baixa      - Backlog (nice-to-have)

====================================================================
🔥 AGORA - Sprint Atual (22/11/2025)
====================================================================

1. Testar Sistema Boletim Itinerário
   ├─ Criar dados de teste (valores ref 2024-2026)
   ├─ Criar 2 templates recorrentes (BA + RR)
   ├─ Gerar boletins de teste com múltiplas linhas
   └─ Validar cálculos automáticos (dias × valor, kms × valor)
   
   Status: Implementação completa ✅, aguarda testes
   Ver: memory/BUSINESS_LOGIC.md (Secção 4)

====================================================================
🔴 Alta Prioridade - Próximas 2 Semanas
====================================================================

4. UX/UI Improvements - Orçamentos (20 melhorias)

   **Concluído (21/11/2025):**
   ├─ ✅ Menu right-click na lista de orçamentos (Visualizar, Editar, Duplicar, Status, Anular, Apagar)
   ├─ ✅ Botão "Duplicar Orçamento" na barra inferior (seleção múltipla)
   ├─ ✅ Input manual de percentagem nas comissões (click no label)
   ├─ ✅ Setas repeat nas comissões (hold para incremento contínuo)
   └─ ✅ Campo código editável no formulário

   **Pendentes:**
   ├─ 🆕 DateRangePicker para "data do evento" (substituir Entry atual)
   │   - Usar componente DateRangePickerDropdown existente
   │   - Formato inteligente (DD-DD/MM/YYYY)
   │   - Update em orcamento_form.py campo data_evento
   └─ 🆕 Context menus (right-click) em tabelas de items CLIENTE/EMPRESA
       - Adicionar a tabelas de items (renderizar_item_cliente/empresa)
       - Ações: Editar, Apagar, Duplicar item

   Críticas:
   ├─ Wizard multi-step (Dados Gerais → Items → Repartições → Preview)
   ├─ Preview lateral ao editar items (recalcula totais live)
   ├─ Gráfico pizza repartições EMPRESA (visual distribuição)
   └─ Validação inline com mensagens claras

   Nice-to-have:
   ├─ Filtros avançados (cliente, status, período, owner)
   ├─ Export PDF melhorado (template profissional)
   └─ Histórico de versões (orçamentos editados)

   Ver: memory/TODO.md (versão anterior, linha 80-120 para detalhes completos)

5. UX/UI Improvements - Boletins (mínimo 10 melhorias)
   
   Críticas:
   ├─ View em cards (mês, total, botão expandir)
   ├─ Edição inline de linhas (sem modal)
   ├─ Calculadora visual (preview dias × valor)
   └─ Filtros (sócio, mês, ano, estado)
   
   Nice-to-have:
   ├─ Gráficos de evolução mensal
   ├─ Export PDF boletim completo
   └─ Sugestão automática de deslocações (baseada em projetos)

6. Sistema Fiscal - Validação TOC
   
   ├─ Marcar reunião com TOC (Técnico Oficial de Contas)
   ├─ Validar regras IVA, IRS, IRC, SS
   ├─ Confirmar periodicidade e formatos
   └─ Ajustar FISCAL.md com feedback
   
   Status: Documentação completa (39KB)
   Ver: memory/FISCAL.md

7. Sistema de Totais por Beneficiário e Rastreabilidade

   ├─ Totais por beneficiário no form orçamento (lado EMPRESA)
   │  - Frame dedicado com cards coloridos por tipo
   │  - Cálculo em tempo real ao adicionar/editar items
   │  - Cores: Verde (sócios), Azul (empresa), Laranja (externos)
   ├─ Conversão automática em campos projeto (prémios/receita/fornecedores)
   │  - premio_bruno, premio_rafael (sum beneficiario BA/RR)
   │  - valor_empresa (sum beneficiario AGORA)
   │  - valor_fornecedores (sum FREELANCER_* + FORNECEDOR_*)
   ├─ Screens ficha freelancer/fornecedor com histórico
   │  - Tabela trabalhos/compras (status, valor, data)
   │  - Botão marcar como pago em cada linha
   │  - Totais: a_pagar, pago, total geral
   └─ Cards dashboard (freelancers a pagar, fornecedores a pagar)
      - Navegação para screen com filtro status=a_pagar

   Estimativa: 2-3 sessões
   Ver: memory/BUSINESS_LOGIC.md (Secção 6), memory/ARCHITECTURE.md (Orçamentos V2)

8. Implementar Tabela Receitas (Migration 027)

   Após validação TOC:
   ├─ Criar migration 027_receitas.py
   ├─ Adicionar modelo Receita (database/models/)
   ├─ Criar ReceitasManager (logic/)
   ├─ Implementar screen Receitas (ui/screens/)
   └─ Integrar com projetos (criar receita ao marcar PAGO)

   Estimativa: 1 semana após validação
   Ver: memory/FISCAL.md (Secção 1), memory/DATABASE_SCHEMA.md (Migration 027)

====================================================================
🟡 Média Prioridade - Próximo Mês
====================================================================

9. UI Gestão Freelancers e Trabalhos/Compras

   ├─ Screen CRUD Freelancers (listar, criar, editar, inativar)
   ├─ Screen Trabalhos Freelancers (listar a_pagar, marcar como pago, filtros)
   ├─ Screen Compras Fornecedores (listar a_pagar, marcar como pago, filtros)
   └─ Dashboard: cards "A Pagar Freelancers" e "A Pagar Fornecedores"

   Estimativa: 1 semana
   Ver: memory/CHANGELOG.md (17/11/2025 - Orçamentos V2 Sistema Multi-Entidade)

10. Testes de Integração Completos
   
   ├─ Testes E2E principais fluxos (criar projeto, aprovar orçamento, etc)
   ├─ Testes unitários managers críticos
   ├─ Testes de cálculos financeiros (saldos, totais)
   └─ CI/CD básico (GitHub Actions)
   
   Framework: pytest

11. Build para Windows (PyInstaller)
    
    ├─ Configurar spec file
    ├─ Testar em Windows 10/11
    ├─ Empacotar com base de dados exemplo
    ├─ Criar instalador (opcional: Inno Setup)
    └─ Documentar processo de build
    
    Ver: memory/DEV_SETUP.md (adicionar secção Build)

12. Dashboard Fiscal (após Migration 027)
    
    ├─ Card IVA a pagar (trimestre atual)
    ├─ Card IRS retido (mês atual)
    ├─ Card SS a pagar (mês atual)
    ├─ Calendário de obrigações fiscais
    └─ Alertas de prazos próximos
    
    Ver: memory/FISCAL.md (Secção 8)

====================================================================
🟢 Baixa Prioridade - Backlog
====================================================================

13. Integração TOConline, BizDocs, BPI Net Empresas (importação manual)
    - Importação manual (CSV) de faturas TOConline, despesas BizDocs e movimentos da conta BPI Empresas
    - Sem automação/API nesta fase (MVP)
    - Matching associativo: sugestão automática de projeto/despesa/receita para reconciliação
    - Referências: INTEGRACOES.md, FISCAL.md, DATABASE_SCHEMA.md
    - Pendente revisão futura, não prioritário

14. Notificações e Alertas
    - Despesas vencidas
    - Orçamentos aguardando aprovação há > 7 dias
    - Projetos sem movimento há > 30 dias
    - Prazos fiscais próximos

15. Sistema de Backup Automático
    - Backup diário da BD (agora_media.db)
    - Rotação (manter últimos 7 dias)
    - Opcional: upload cloud (Google Drive, Dropbox)

16. Relatórios Avançados
    - Relatório de rendibilidade por cliente
    - Relatório de custos por tipo
    - Análise de margens (receitas vs custos)
    - Export multi-formato (PDF, Excel, CSV)

17. Multi-utilizador (Futuro distante)
    - Sistema de autenticação
    - Permissões por role
    - Auditoria de alterações
    - Nota: Não prioritário (apenas 2 sócios)

18. App Mobile (Exploratório)
    - Consulta rápida de saldos
    - Adicionar despesas em movimento
    - Push notifications
    - Nota: Avaliar necessidade real

====================================================================
📚 Referências Cruzadas
====================================================================

Para detalhes técnicos completos:
- memory/ARCHITECTURE.md - Como implementar
- memory/DATABASE_SCHEMA.md - Estrutura de dados
- memory/BUSINESS_LOGIC.md - Regras de negócio
- memory/FISCAL.md - Sistema fiscal completo

Para contexto e decisões:
- memory/CURRENT_STATE.md - Estado atual
- memory/DECISIONS.md - Porquê destas escolhas
- memory/CHANGELOG.md - O que mudou

====================================================================
✅ CONCLUÍDO RECENTEMENTE
====================================================================

Ver memory/CHANGELOG.md para histórico completo.

Últimas 6 features (Novembro 2025):
- ✅ 24/11: Refatoração Screens Dedicados - fornecedores e equipamento (padrão projetos 6/6)
- ✅ 24/11: Conversão Dialogs BaseDialogMedium/Large - 8 ficheiros, ~300 linhas removidas
- ✅ 17/11: Orçamentos V2 Sistema Multi-Entidade COMPLETO
- ✅ 17/11: Sistema Aprovação e Conversão Orçamentos
- ✅ 17/11: Orçamentos V2 - 5/5 dialogs CLIENTE + 3/3 dialogs EMPRESA
- ✅ 15/11: Migration 021 - Cliente nome e nome_formal

Para histórico anterior: Ver memory/CHANGELOG.md

====================================================================
💡 SISTEMA DE ATUALIZAÇÃO
====================================================================

Ao completar uma tarefa:
1. Mover de [prioridade] para "✅ Concluído Recentemente"
2. Adicionar entrada em CHANGELOG.md com data e detalhes
3. Atualizar CURRENT_STATE.md (secção "Última Feature")
4. Arquivar tarefas antigas (>1 mês) para CHANGELOG.md

Ao adicionar tarefa nova:
1. Definir prioridade (🔥/🔴/🟡/🟢)
2. Estimar tempo se possível
3. Adicionar referências cruzadas (Ver: memory/X.md)

====================================================================

Mantido por: Equipa Agora
Para planeamento de sprint: Foca em 🔥 AGORA + top 3 de 🔴 Alta
