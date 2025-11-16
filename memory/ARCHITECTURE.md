## Arquitetura - Camadas & Fluxos (atualizado 16/11/2025)

---

### Visão Geral

O sistema centra-se agora num modelo de orçamentos de dupla perspetiva:
- **Lado CLIENTE:** Proposta comercial com seccionamento fixo (serviços, equipamento, despesas). CRUD avançado por tipo (métodos e dialogs adaptativos).
- **Lado EMPRESA:** Repartição de receitas/custos, beneficiários, comissões automáticas e sincronização plena de despesas (ver BUSINESS_LOGIC.md).

---

#### Camada Logic

├── orcamentos.py            # OrcamentosManager (gestão de ciclo completo: criar, atualizar, aprovar)
├── secao_orcamento.py       # SecoesManager (fixas + subsecções possíveis para equipamento)
├── item_orcamento.py        # ItensManager (CRUD tipo-aware; validações específicas por tipo)
├── reparticoes.py           # ReparticaoManager (CRUD, associar beneficiário, tipologia, auto-preenchimento comissões)
├── despesas.py              # DespesasManager (sincronização cliente→empresa)
├── equipamentos.py          # EquipamentoManager (suporte referência cruzada, amortização)
├── clientes.py, projetos.py, boletins.py, socios.py, ...

---

#### Camada UI

├── screens/
│   ├── orcamento_form.py        # Ecrã principal (tabs cliente, empresa)
│   ├── dialogs/
│   │   ├── item_dialog.py       # Dialog CRUD flexível por tipo (serviço, equipamento, transporte, refeição, outro)
│   │   ├── reparticao_dialog.py # Dialog CRUD + auto-preenchimento de comissões
│   │   └── confirm_dialog.py    # Dialog geral de confirmação/erro
│   ├── componentes/
│   │   ├── data_table_v2.py     # Renderização tabular de rows, suporte strikethrough
│   │   ├── autocomplete_entry.py, date_picker_dropdown.py, ...
│   ├── main_window.py, dashboard.py, ...

Sidebar inclui:
- Menu "Orçamentos" → tabs Cliente/Empresa
- Menus complementares: Projetos, Despesas, Equipamento, Sócios, Fornecedores

---

#### Integração & Fluxos

- Navegação unificada para orçamentos; ciclo: criar → editar secções/items → validar repartições → comparar totais → aprovar (se bater)
- Sincronização automática de despesas CLIENTE→EMPRESA através do manager; bloqueio de edição manual dessas linhas no EMPRESA
- Dialogs reutilizáveis para criação/edição de itens e repartições (fine-tuning por tipo, validação inline dos campos obrigatórios/key fields)
- Exportação para PDF/excel lateral em CLIENTE, integração com TOConline futura lado EMPRESA
- Validação bloqueada por diferença de totais; tooltip sobre campos críticos

---

#### Modelos de Dados

- Seguir draft completo do BUSINESS_LOGIC.md (secção 6). Campos tipo-aware por tabela. Integração com enums para tipo e beneficiário.
---

#### Roadmap Técnico

- Unificação/reutilização de dialogs, menos código duplicado
- Otimização de queries nos managers (foco em join orcamento_itens/reparticoes)
- Onboarding técnico via ficheiros de memória sempre atualizados (esta arquitetura é o ponto de partida central)
