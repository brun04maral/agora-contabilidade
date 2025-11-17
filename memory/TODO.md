# 📋 TODO.md - Tarefas Priorizadas

Última atualização: 2025-11-17 09:55 WET

====================================================================
LEGENDA DE PRIORIDADES
====================================================================

🔥 AGORA      - Sprint atual (máx 3-5 tasks em execução)
🔴 Alta       - Próximas 2 semanas (features críticas)
🟡 Média      - Próximo mês (melhorias importantes)
🟢 Baixa      - Backlog (nice-to-have)

====================================================================
🔥 AGORA - Sprint Atual (17/11/2025)
====================================================================

1. Orçamentos V2 - Lado EMPRESA (5 dialogs)
   ├─ Implementar ServicoEmpresaDialog (beneficiário + campos)
   ├─ Implementar EquipamentoEmpresaDialog (beneficiário + equipamento_id)
   ├─ Implementar DespesaDialog (espelhamento automático lado CLIENTE)
   ├─ Implementar ComissaoDialog (% sobre base de cálculo)
   └─ Implementar AluguerEquipamentoDialog (equipamento + dias)
   
   Status: 5/5 dialogs CLIENTE concluídos ✅
   Próximo: Começar dialogs EMPRESA
   Ver: memory/ARCHITECTURE.md (Secção Orçamentos V2)

2. Auditoria Sistema Memory (FASE 2)
   ├─ ✅ FASE 1: Reorganizar DATABASE_SCHEMA, CURRENT_STATE, BUSINESS_LOGIC
   └─ 🚧 FASE 2: Melhorar navegação (README.md, links cruzados)
   
   Status: FASE 1 completa, FASE 2 em curso
   Ver: Esta conversa (17/11/2025)

3. Testar Sistema Boletim Itinerário
   ├─ Criar dados de teste (valores ref 2024-2026)
   ├─ Criar 2 templates recorrentes (BA + RR)
   ├─ Gerar boletins de teste com múltiplas linhas
   └─ Validar cálculos automáticos (dias × valor, kms × valor)
   
   Status: Implementação completa ✅, aguarda testes
   Ver: memory/BUSINESS_LOGIC.md (Secção 4)

====================================================================
🔴 Alta Prioridade - Próximas 2 Semanas
====================================================================

4. UX/UI Improvements - Orçamentos (18 melhorias)
   
   Críticas:
   ├─ Wizard multi-step (Dados Gerais → Items → Repartições → Preview)
   ├─ Preview lateral ao editar items (recalcula totais live)
   ├─ Gráfico pizza repartições EMPRESA (visual distribuição)
   ├─ Validação inline com mensagens claras
   └─ Botão "Duplicar Orçamento" (copia completo)
   
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

7. Implementar Tabela Receitas (Migration 025)
   
   Após validação TOC:
   ├─ Criar migration 025_receitas.py
   ├─ Adicionar modelo Receita (database/models/)
   ├─ Criar ReceitasManager (logic/)
   ├─ Implementar screen Receitas (ui/screens/)
   └─ Integrar com projetos (criar receita ao marcar PAGO)
   
   Estimativa: 1 semana após validação
   Ver: memory/FISCAL.md (Secção 1), memory/DATABASE_SCHEMA.md (Migration 025)

====================================================================
🟡 Média Prioridade - Próximo Mês
====================================================================

8. Sistema Freelancers e Fornecedores (Migration 024)
   
   ├─ Criar migrations (freelancers, freelancer_trabalhos, fornecedor_compras)
   ├─ Adicionar modelos e managers
   ├─ Expandir fornecedores (numero, categoria, iban)
   ├─ Implementar screens CRUD
   └─ Integrar com orçamentos (beneficiários FREELANCER_[id], FORNECEDOR_[id])
   
   Estimativa: 1-2 semanas
   Ver: memory/DATABASE_SCHEMA.md (fim), memory/BUSINESS_LOGIC.md (Secção 5)

9. Testes de Integração Completos
   
   ├─ Testes E2E principais fluxos (criar projeto, aprovar orçamento, etc)
   ├─ Testes unitários managers críticos
   ├─ Testes de cálculos financeiros (saldos, totais)
   └─ CI/CD básico (GitHub Actions)
   
   Framework: pytest

10. Build para Windows (PyInstaller)
    
    ├─ Configurar spec file
    ├─ Testar em Windows 10/11
    ├─ Empacotar com base de dados exemplo
    ├─ Criar instalador (opcional: Inno Setup)
    └─ Documentar processo de build
    
    Ver: memory/DEV_SETUP.md (adicionar secção Build)

11. Dashboard Fiscal (após Migration 025)
    
    ├─ Card IVA a pagar (trimestre atual)
    ├─ Card IRS retido (mês atual)
    ├─ Card SS a pagar (mês atual)
    ├─ Calendário de obrigações fiscais
    └─ Alertas de prazos próximos
    
    Ver: memory/FISCAL.md (Secção 8)

====================================================================
🟢 Baixa Prioridade - Backlog
====================================================================

12. Notificações e Alertas
    - Despesas vencidas
    - Orçamentos aguardando aprovação há > 7 dias
    - Projetos sem movimento há > 30 dias
    - Prazos fiscais próximos

13. Sistema de Backup Automático
    - Backup diário da BD (agora_media.db)
    - Rotação (manter últimos 7 dias)
    - Opcional: upload cloud (Google Drive, Dropbox)

14. Relatórios Avançados
    - Relatório de rendibilidade por cliente
    - Relatório de custos por tipo
    - Análise de margens (receitas vs custos)
    - Export multi-formato (PDF, Excel, CSV)

15. Multi-utilizador (Futuro distante)
    - Sistema de autenticação
    - Permissões por role
    - Auditoria de alterações
    - Nota: Não prioritário (apenas 2 sócios)

16. App Mobile (Exploratório)
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

Últimas 5 features (Novembro 2025):
- ✅ 17/11: Orçamentos V2 - 5/5 dialogs CLIENTE implementados
- ✅ 17/11: Auditoria Memory - DATABASE_SCHEMA, CURRENT_STATE, BUSINESS_LOGIC reorganizados
- ✅ 15/11: Migration 021 - Cliente nome e nome_formal
- ✅ 15/11: Migration 020 - Owner em projetos/orçamentos, rastreabilidade
- ✅ 13/11: Sistema Boletim Itinerário completo (Migrations 016-019)

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
