# 📋 TODO.md - NOVAS TAREFAS (15/11/2025)

## ⚠️ INSTRUÇÕES
Adicionar estas tarefas na secção **🟡 Média Prioridade** do ficheiro `TODO.md` existente, logo após o header da secção.

---

## 🟡 Média Prioridade - NOVAS TAREFAS

- [ ] 💾 **Implementar Sistema de Receitas** (NOVO 15/11/2025)
  - **Contexto:** Atualmente não há registo formal de receitas
  - **Problema:** Quando projeto é marcado como PAGO, apenas distribui prémios mas não cria receita
  - **Impacto:** Falta rastreabilidade de pagamentos de clientes
  
  **Estrutura proposta:**
  - Tabela `receitas` (id, numero, projeto_id, cliente_id, valor, data, estado, tipo)
  - Estados: ATIVO, CANCELADO
  - Tipos: PROJETO (receita de projeto), OUTRO (receitas avulsas)
  
  **Lógica:**
  - Ao marcar projeto como PAGO → criar receita automaticamente
  - Ao reverter para FINALIZADO → marcar receita como CANCELADA (não apagar)
  - Link bidirecional: projeto ↔ receita
  
  **UI:**
  - Screen Receitas (CRUD básico)
  - Coluna "Receita" em Projetos (link para receita criada)
  - Filtros: por cliente, por período, por estado
  
  **Relatórios:**
  - Receitas vs Despesas (mensal/anual)
  - Receitas por Cliente
  - Previsão de receitas (projetos FINALIZADOS)
  
  **Ficheiros:**
  - `database/models/receita.py` (novo)
  - `database/migrations/021_receitas.py` (novo)
  - `logic/receitas.py` (novo)
  - `ui/screens/receitas.py` (novo)
  - Atualizar `logic/projetos.py` (criar receita ao marcar PAGO)
  
  **Decisões a tomar:**
  - Receita sempre = valor total do projeto? Ou pode ser parcial?
  - Permitir múltiplas receitas por projeto? (pagamentos faseados)
  - Receitas avulsas (sem projeto)? Ex: subsídios, vendas de equipamento
  
  **Ver:** BUSINESS_LOGIC.md Secção 3.4, DECISIONS.md

- [ ] 🔄 **Remover Sistema de Templates de Boletins** (NOVO 15/11/2025)
  - **Contexto:** Sistema de templates recorrentes é complexo demais
  - **Decisão:** Substituir por funcionalidade "Duplicar Boletim"
  
  **Remover:**
  - Tabela `boletim_templates` (migration reversa ou manter como legacy)
  - UI: Screen `templates_boletins.py` (se existir)
  - UI: Botão "🔁 Gerar Recorrentes" em BoletinsScreen
  - UI: Botão "📋 Templates" em BoletinsScreen
  - Logic: `logic/boletim_templates.py` (se existir)
  - Todas as referências a templates em boletins
  
  **Adicionar:**
  - Botão "📋 Duplicar" em BoletimFormScreen
  - Lógica: método `duplicar_boletim(boletim_id)` que copia:
    - Header completo (sócio, mês, ano, descrição)
    - Todas as linhas de deslocação
    - Permite editar antes de gravar
  
  **Ficheiros afetados:**
  - `ui/screens/boletins.py` (remover 2 botões do header)
  - `ui/screens/boletim_form.py` (adicionar botão Duplicar)
  - `logic/boletins.py` (adicionar método duplicar)
  
  **Impacto:**
  - Remove ~2000 linhas de código complexo
  - Simplifica UI (menos 2-3 botões, menos 1 screen)
  - Melhor UX (utilizador tem controlo total)
  
  **Ver:** BUSINESS_LOGIC.md Secção 2.3, DECISIONS.md

- [ ] 🗑️ **Remover FormularioBoletimDialog (Legacy)** (NOVO 15/11/2025)
  - **Contexto:** Dois sistemas de edição de boletins coexistem (antigo e novo)
  - **Decisão:** Usar apenas BoletimFormScreen (com linhas de deslocação)
  
  **Remover completamente:**
  - Classe `FormularioBoletimDialog` em `ui/screens/boletins.py`
  - Botão "🟧 Emitir Boletim" (laranja) no header de BoletinsScreen
  - Todos os métodos relacionados com dialog antigo
  - ~300-400 linhas de código legacy
  
  **Atualizar fluxos:**
  - Duplo-clique em boletim → abre BoletimFormScreen (novo)
  - Botão "➕ Novo Boletim" → abre BoletimFormScreen vazio
  - Edição sempre via BoletimFormScreen
  
  **Verificações:**
  - Procurar todas as referências a `FormularioBoletimDialog`
  - Garantir nenhum código chama o dialog antigo
  - Testar criação, edição, duplicação de boletins
  
  **Ficheiros afetados:**
  - `ui/screens/boletins.py` (remoção major)
  
  **Impacto:**
  - Código mais limpo e manutenível
  - UI consistente (um único fluxo)
  - Menos confusão para utilizador
  
  **Ver:** BUSINESS_LOGIC.md Secção 2.10

- [ ] ⚙️ **Implementar Transição Automática ATIVO → FINALIZADO** (NOVO 15/11/2025)
  - **Contexto:** Projetos com `data_fim` passada devem automaticamente mudar para FINALIZADO
  - **Comportamento:** Job que verifica diariamente (ou ao carregar app) e atualiza estados
  
  **Lógica:**
  ```python
  def atualizar_estados_projetos():
      """
      Atualiza projetos ATIVO para FINALIZADO quando data_fim < hoje
      """
      hoje = date.today()
      projetos_a_finalizar = session.query(Projeto).filter(
          Projeto.estado == 'ATIVO',
          Projeto.data_fim.isnot(None),
          Projeto.data_fim < hoje
      ).all()
      
      for projeto in projetos_a_finalizar:
          projeto.estado = 'FINALIZADO'
          logger.info(f"Projeto {projeto.codigo} finalizado automaticamente")
      
      session.commit()
      return len(projetos_a_finalizar)
  ```
  
  **Implementar em:**
  - `logic/projetos.py` → método `atualizar_estados_automaticos()`
  - `ui/main_window.py` → chamar ao inicializar app
  - `ui/screens/projetos.py` → chamar ao carregar/atualizar screen
  
  **Opcional - Notificação:**
  - Badge no Dashboard: "3 projetos finalizados recentemente"
  - Popup discreto: "2 projetos foram finalizados automaticamente"
  - Log no ficheiro para auditoria
  
  **Testes:**
  - Criar projeto com `data_fim` no passado
  - Verificar transição automática ao carregar app
  - Testar que não afeta projetos sem `data_fim`
  - Testar que só afeta projetos ATIVO (não PAGO/ANULADO)
  
  **Ver:** BUSINESS_LOGIC.md Secção 3.2

- [ ] 💡 **Implementar Prémios Não Faturados em Saldos** (NOVO 15/11/2025)
  - **Contexto:** Mostrar prémios de projetos FINALIZADOS (trabalho feito mas não pago)
  - **Feature:** Distinção entre Saldo Atual vs Saldo Projetado
  
  **Cálculo:**
  ```python
  # Prémios não faturados (projetos FINALIZADOS)
  premios_nao_faturados_ba = sum(
      projeto.premio_ba 
      for projeto in projetos 
      if projeto.estado == 'FINALIZADO' and projeto.premio_ba > 0
  )
  
  # Saldos
  saldo_atual_ba = total_ins_ba - total_outs_ba
  saldo_projetado_ba = saldo_atual_ba + premios_nao_faturados_ba
  ```
  
  **UI - Saldos Pessoais:**
  - Adicionar linha "💡 Prémios não faturados" após "Prémios"
  - Cor laranja claro (#FFF4E6 bg, #CC6600 text)
  - Clicável → navega para Projetos filtrados por FINALIZADO
  - Tooltip: "Projetos concluídos aguardando pagamento"
  
  **UI - Header do Card:**
  ```
  Saldo Atual: €12.120,98
  Saldo Projetado: €14.120,98 (+€2.000)  ← só mostrar se houver não faturados
  ```
  
  **Ficheiros:**
  - `logic/saldos.py` → adicionar cálculo de prémios não faturados
  - `ui/screens/saldos.py` → adicionar linha e saldo projetado
  
  **Comportamento:**
  - Se `premios_nao_faturados == 0` → não mostrar linha nem saldo projetado
  - Se `premios_nao_faturados > 0` → mostrar ambos
  - Clicar em "Prémios não faturados" → `navigate_to_projetos(filtro_estado='FINALIZADO')`
  
  **Ver:** BUSINESS_LOGIC.md Secção 3.5

- [ ] 🎯 **Migration 020: Orçamentos e Projetos Completos** (NOVO 15/11/2025)
  - **Contexto:** Implementar todas as alterações documentadas em DATABASE_SCHEMA.md
  - **Prioridade:** Alta (bloqueia implementação de features acima)
  
  **Alterações a implementar:**
  1. `orcamentos.owner` VARCHAR(2) NOT NULL
  2. `projetos.owner` VARCHAR(2) NOT NULL
  3. `projetos.estado` → atualizar enum (ATIVO/FINALIZADO/PAGO/ANULADO)
  4. `projetos.valor_empresa` DECIMAL(10,2) DEFAULT 0
  5. `projetos.valor_fornecedores` DECIMAL(10,2) DEFAULT 0
  6. `projetos.valor_equipamento` DECIMAL(10,2) DEFAULT 0
  7. `projetos.valor_despesas` DECIMAL(10,2) DEFAULT 0
  8. `projetos.data_pagamento` DATE NULL
  9. `proposta_reparticoes.entidade` → remover
  10. `proposta_reparticoes.tipo` VARCHAR(20) NOT NULL
  11. `proposta_reparticoes.fornecedor_id` INTEGER NULL + FK
  12. `proposta_reparticoes.equipamento_id` INTEGER NULL + FK
  13. `equipamento.rendimento_acumulado` DECIMAL(10,2) DEFAULT 0
  
  **Script:** `database/migrations/020_orcamentos_projetos_completo.py`
  
  **Atenção - Migração de dados:**
  - `orcamentos.owner` → usar 'BA' como default ou inferir
  - `projetos.owner` → inferir de `tipo` (PESSOAL_BA→BA, PESSOAL_RR→RR, EMPRESA→?)
  - `projetos.estado` → mapear: ativo→ATIVO, concluido→FINALIZADO, cancelado→ANULADO
  - `proposta_reparticoes.tipo` → mapear: entidade='BA'→tipo='BA', entidade='RR'→tipo='RR'
  
  **Testes pós-migration:**
  - Verificar todos os projetos têm owner
  - Verificar estados mapeados corretamente
  - Verificar repartições antigas convertidas
  - Verificar FKs criadas sem erros
  
  **Ver:** DATABASE_SCHEMA.md (secção atualizações)

---

## 🔗 Notas Adicionais

**Ordem de implementação sugerida:**
1. Migration 020 (bloqueia resto)
2. Transição automática ATIVO→FINALIZADO (quick win)
3. Prémios Não Faturados (quick win + valor imediato)
4. Remover Templates Boletins (cleanup)
5. Remover FormularioBoletimDialog (cleanup)
6. Sistema de Receitas (feature maior, pode ser faseada)

**Dependências:**
- Prémios Não Faturados depende de Migration 020 (novos estados)
- Sistema Receitas depende de Migration 020 (estado PAGO)

---

_Última atualização: 15/11/2025_
