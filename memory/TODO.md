# 📝 TODO - Agora Contabilidade

**Última atualização:** 16/11/2025

---

- [ ] ✨ **Implementar Dialogs CRUD Específicos por Tipo - Orçamentos V2**
  - Lado CLIENTE: ServicoDialog, EquipamentoDialog, TransporteDialog, RefeicaoDialog, OutroDialog
  - Lado EMPRESA: ServicoEmpresaDialog, EquipamentoEmpresaDialog, ComissaoDialog
  - Renderização tabular de items por tipo
  - Sincronização automática despesas CLIENTE→EMPRESA
  - Validação bloqueio aprovação (TOTAL_CLIENTE = TOTAL_EMPRESA)
  - Auto-preenchimento de comissões
  - Testes de fluxo completo (criar, editar, aprovar)

## 🔥 AGORA (Foco Imediato)

- [ ] ✨ **Implementar Página Individual de Sócio**
  - Criar ecrã de seleção/listagem de sócios (BA, RR)
  - Implementar card único com todos os campos informativos/editáveis
      * Nome completo
      * Cargo
      * Data nascimento
      * NIF
      * NISS
      * Morada
      * Salário base
      * Subsídio de alimentação
  - Migration 022 - Expandir tabela `socios` (adicionar/atualizar campos)
  - Criar SociosManager
  - Criar SocioScreen
  - Garantir navegação sidebar, validações e persistência
  - **Testes:** Modo edição, persistência, navegação, rollback migration
  - Atualizar documentação (PLANO_SOCIOS.md, DATABASE_SCHEMA.md, ARCHITECTURE.md, CURRENT_STATE.md)

---

## 📋 Próximos Passos (Restantes tarefas mantêm-se conforme backlog)

[restante conteúdo intacto]
