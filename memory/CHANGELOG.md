## [2025-11-16] Orçamentos v2: Lado Cliente/Empresa, Secções, Repartições & Sincronizações

### ✨ Nova Arquitetura Completa de Orçamentos
- Implementação de modelo duplo: CLIENTE (proposta comercial) e EMPRESA (repartição de receitas, custos e beneficiários)
- Secções fixas: Serviços, Equipamento (com subsecções), Despesas (espelhadas e sincronizadas CLIENTE→EMPRESA)
- Dialogs tabulares para CRUD de cada tipo de item (Serviço, Equipamento, Transporte, Refeição, Outro)
- Beneficiário explicitamente selecionado por item do lado EMPRESA (BA, RR, AGORA, Freelancer, Fornecedor)
- Diálogo especial para Comissões: preenchimento/ajuste automático, percentagem configurável (até 3 casas decimais, bloqueadas por padrão)
- Validação bloqueante: aprovação só possível se TOTAL_CLIENTE = TOTAL_EMPRESA (com comparação/diferença em tempo real)
- Integração de despesa: alterações no CLIENTE refletem obrigatoriamente/intransigentemente no EMPRESA
- CRUD seguro: edição manual apenas onde previsto, todas alterações registadas e testadas (CRUD, batch-copy, duplicação/auto-população)

### 📝 Documentação Técnica e Back-References
- BUSINESS_LOGIC.md: Secção orçamentos documenta fluxos e regras integrais
- DATABASE_SCHEMA.md: Tabelas e enums atualizadas a 16/11/2025
- CURRENT_STATE.md, TODO.md, ARCHITECTURE.md revistas para refletir nova arquitetura

### 🔄 Outras Mudanças e Limpezas
- Removido PLANO_ORCAMENTOS.md (conteúdo fundido e expandido em business_logic)
- Atualizados e simplificados managers, dialogs, componentes e screens

### 🟢 Tests e Validações
- Testes regressivos: CRUD de todos os tipos (clientes reais)
- Testes UX: validação inline, feedback visual, tooltips informativos, bloqueios de aprovação, batch edit vívido

---

## [Commits Importantes - Arquitetura Orçamentos v2]
- `3d565788` BUSINESS_LOGIC.md: Arquitetura detalhada
- `d092784e` TODO.md: Tasks de implementação do fluxo
- `b3fed547` CURRENT_STATE.md atualizado para v2
- `456577de` ARCHITECTURE.md: Managers, dialogs, fluxos
- `aa358b0b` DATABASE_SCHEMA.md: update integral
- `14232fa1` Remoção PLANO_ORCAMENTOS.md legado

---

## [2025-11-15 e anteriores] ver entradas legadas; ciclo legacy fechado a partir da arquitetura atual.
