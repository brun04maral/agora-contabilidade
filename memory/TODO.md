# 📝 TODO - Agora Contabilidade

**Última atualização:** 16/11/2025

---

## 🔥 AGORA (Foco Imediato)

- [ ] ✨ **Implementar Arquitetura de Orçamentos V2 (Cliente/Empresa)**
  - Refatorar lógica de orçamentos para modelo lado CLIENTE vs EMPRESA totalmente separado
  - Implementar secções fixas (serviços, equipamento, despesas)
  - CRUD de itens com dialogs tabulares distintos por tipo (serviço, equipamento, transporte, refeição, outro)
  - Sincronização automática de despesas de CLIENTE → EMPRESA
  - Criação e ajuste de repartições e comissões (dialog auto-preenchimento, percentagens editáveis)
  - Validação bloqueio de aprovação até TOTALS batem
  - Integração dos modelos na base de dados (ver DATABASE_SCHEMA)
  - Atualizar/plano de testes de fluxo de ponta a ponta (exemplos reais)

- [ ] ✨ **UX/Usabilidade Avançada para Orçamentos**
  - Botão "Duplicar Orçamento"
  - Feedback visual em tempo real de diferença CLIENTE ↔ EMPRESA
  - Tooltips explicativos nos campos críticos
  - Validação inline de campos obrigatórios
  - Preview lateral/rodapé de totais antes de submeter
  - Exportação/preview PDF lado CLIENTE

- [ ] 📄 **Atualizar Documentação Técnica e Onboarding**
  - Atualizar DATABASE_SCHEMA.md (novo modelo de orçamentos)
  - Atualizar CURRENT_STATE.md (estado do fluxo atual, listas, secções espelhadas)
  - Atualizar ARCHITECTURE.md (diagramas, managers, dialogs)
  - Atualizar CHANGELOG.md (entrada resumo da arquitetura V2)

- [ ] ✨ **Implementar Página Individual de Sócio**
  - Criar ecrã de seleção/listagem de sócios (BA, RR)
  - Implementar card único com todos os campos informativos/editáveis
  - Migration 022 - Expandir tabela `socios` (adicionar/atualizar campos)
  - Criar SociosManager
  - Criar SocioScreen
  - Garantir navegação sidebar, validações e persistência
  - **Testes:** Modo edição, persistência, navegação, rollback migration
  - Atualizar documentação (DATABASE_SCHEMA.md, ARCHITECTURE.md, CURRENT_STATE.md)

---

## 📋 Próximos Passos (Backlog)

- [ ] Integração TOConline API para sincronização de clientes e despesas
- [ ] Dashboard visual para repartições de orçamentos (pie chart por beneficiário)
- [ ] Filtros e pesquisa global inteligente por projeto, cliente, orçamento, fornecedor
- [ ] Exportação total para Excel das listas principais (clientes, fornecedores, projetos, orçamentos)
- [ ] Dark/Light Theme Global
- [ ] Otimização performance inicialização app/refresh massivo

---