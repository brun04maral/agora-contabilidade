### 🆕 EM DESENVOLVIMENTO: Página Individual de Sócio
- Implementação prioritária da feature Sócios: página individual por sócio (BA ou RR), com seleção inicial e card informativo/editável
- Migration 022 para expansão da tabela `socios` (cargo, data nascimento, niss, morada, salário base, sub. alimentação, etc)
- Novo SociosManager (logic/) e SocioScreen (ui/screens/)
- UI/UX: Navegação sidebar → sócios → card único por sócio
- Estado: Especificação e plano enviados (`PLANO_SOCIOS.md`) e tasks abertas no TODO
- Após migration, atualizar CURRENT_STATE e CHANGELOG

---

### ✅ CONCLUÍDO RECENTEMENTE: Orçamentos V2 - Arquitetura Base (16/11/2025)

**Fase 1-2 Completas:**
- ✅ Modelos de dados atualizados (Orcamento, OrcamentoItem, OrcamentoReparticao)
- ✅ Migration 022 criada, testada e aplicada
- ✅ OrcamentoFormScreen V2 reescrita do zero (estrutura base completa)
- ✅ Tabs CLIENTE/EMPRESA separadas com validação de totais em tempo real

**Em Curso - Fase 3:**
- ⏳ Implementação de dialogs CRUD específicos por tipo
- ⏳ Renderização e CRUD completo de items
- ⏳ Sincronização automática de despesas
- ⏳ Auto-preenchimento de comissões

**Referências:**
- BUSINESS_LOGIC.md (Secção 1-7: Sistema de Orçamentos V2)
- DATABASE_SCHEMA.md (Modelo V2 completo)
- Commits: 087fb08, d4afcf6, 2882cdc, 3b589f7

---
