# 📚 BUSINESS_LOGIC.md — Lógica de Negócio - Agora Contabilidade

Última atualização: 2025-11-17 09:40 WET
Branch: claude/sync-latest-updates-012SDyaYGLD1zvqARajAPDPC

====================================================================
1. ORÇAMENTOS
====================================================================

CONCEITO:
* Cada orçamento tem dois lados: CLIENTE e EMPRESA (espelhados).
* CLIENTE: como o cliente vê (serviços, equipamentos, despesas).
* EMPRESA: como a empresa redistribui valor — prémios, fornecedores, equipamentos, empresa.

ESTADOS & FLUXO:
* RASCUNHO   → aprovado pelo user
* APROVADO   → após validação (totais batem entre lados)
* REJEITADO  → anulado, nunca converte

VALIDAÇÕES AUTOMÁTICAS:
* Totais lado CLIENTE e EMPRESA obrigam a bater (verificados ao aprovar).
* EMPRESA: soma beneficiários = total CLIENTE.
* Campos obrigatórios: cliente_id, owner, descricao/tipo de item, valores ≥ 0.
* Ao aprovar: cria automaticamente um PROJETO.

PRINCIPAIS REGRAS:
* Num orçamento, o beneficiário pode ser sócio ('BA', 'RR'), empresa ('AGORA'), freelancer, fornecedor, ou equipamento.
* Cada item tem tipo (serviço, equipamento, transporte, refeição, outro).
* Os tipos de repartição no lado EMPRESA têm lógica própria (comissão, despesa espelhada, prémios).

CASOS DE USO:
* Aprovação em 1 passo: valida tudo e gera novo projeto com FK para orçamento.
* Revisão rápida: dashboards mostram orçamentos “pendentes de aprovação”.
* Itens e repartições geridos via dialogs com validação inline.

====================================================================
2. PROJETOS
====================================================================

TIPOS E RESPONSABILIDADE:
* Tipos: FRONTEND, BACKEND, FULLSTACK, OUTRO.
* Cada projeto tem um owner ('BA' ou 'RR') e reflete “quem gere” e impacta nos saldos.

ESTADOS:
* ATIVO: em curso.
* FINALIZADO: automatico → se data_fim < hoje, não pago.
* PAGO: cliente pagou; prémios distribuídos.
* ANULADO: cancelado (sem impacto posterior).

REGRAS DE TRANSIÇÃO:
* ATIVO → FINALIZADO: automático via data_fim.
* FINALIZADO → PAGO: manual após confirmação de recebimento.
* Todos os estados mantêm históricos; alterações graves requerem logging.

CÁLCULO DE PRÉMIOS:
* Prémio individual atribuído ao owner (campo premio_bruno/premio_rafael).
* Cálculo: depende da repartição EMPRESA no orçamento aprovado.
* Pagamentos só distribuídos no estado PAGO.

RASTREABILIDADE:
* Campos: valor_empresa, valor_fornecedores, valor_equipamento, valor_despesas.
* Data de pagamento registada.

====================================================================
3. DESPESAS
====================================================================

TIPOS E DIVISÃO:
* Tipos: FIXA_MENSAL (50/50), PESSOAL_BRUNO (100% BA), PESSOAL_RAFAEL (100% RR), EQUIPAMENTO (50/50), PROJETO (50/50).
* Apenas despesas com estado 'PAGO' entram nos cálculos de saldos.
* Cálculo da divisão é feito ao gravar cada despesa e refrescado no saldo global.

TEMPLATES RECORRENTES:
* Utiliza-se a tabela despesa_templates para gerir moldes mensais NÃO financeiros.
* Geração automática recorre ao campo 'dia_mes'.
* Todas as despesas geradas têm FK para o template de origem e asterisco visual.

IMPACTO EM SALDOS:
* FIXA_MENSAL/EQUIPAMENTO/PROJETO: cada sócio paga metade do total.
* PESSOAIS: afetam apenas o sócio específico.
* Templates e gastos não pagos não contam para saldo.

====================================================================
4. BOLETINS ITINERÁRIO
====================================================================

CONCEITO:
* Boletim = soma de deslocações (linhas) do mês para ajudas de custo.
* Cada linha representa uma deslocação (dias, tipo, kms, localidade, FK opcional projeto).

ESTADOS:
* PENDENTE: boletim preparado, aguardando pagamento.
* PAGO: pagamento confirmado, desconta dos saldos.

VALORES DE REFERÊNCIA:
* Variação por ANO: val_dia_nacional, val_dia_estrangeiro, val_km (ver valores_referencia_anual).
* Defaults: 72.65€/167.07€/0.40€, valores podem ser customizados para o ano.

CÁLCULOS:
* total_ajudas_nacionais = Σ dias tipo NACIONAL × val_dia_nacional
* total_ajudas_estrangeiro = Σ dias tipo ESTRANGEIRO × val_dia_estrangeiro
* total_kms = Σ kms × val_km
* valor_total = soma dos 3 totais

LINHAS DE DESLOCAÇÃO:
* Campos: ordem, projeto_id (nullable), serviço, localidade, datas, tipo, kms
* Servem para reporting ao TOC e apoio IRS.
* Adicionar linha: atualiza totals do boletim.

IMPACTO FINANCEIRO:
* Só desconta saldos do sócio quando estado = PAGO.
* Cálculo é sempre automático; edits na linha atualizam header.

====================================================================
5. CÁLCULOS FINANCEIROS - SALDOS PESSOAIS
====================================================================

ESTRUTURA COMPLETA DOS SALDOS:

INs (Entradas):
────────────────
  PAGOS:
    - Projetos Pessoais PAGOS (tipo=PESSOAL, estado=PAGO, owner=sócio)
    - Prémios PAGOS (estado=PAGO, premio_X > 0)

  PENDENTES:
    - Projetos Pessoais não pagos (tipo=PESSOAL, estado=FINALIZADO, owner=sócio)
    - Prémios não pagos (estado=FINALIZADO, premio_X > 0)

OUTs (Saídas):
──────────────
  PAGOS:
    - Fixas Mensais ÷2 (tipo=FIXA_MENSAL, estado=PAGO)
    - Boletins pagos (estado=PAGO)
    - Despesas pessoais (tipo=PESSOAL_X, estado=PAGO)

  PENDENTES:
    - Boletins Pendentes (estado=PENDENTE)

TOTAIS:
───────
- TOTAL INs Pagos = Pessoais PAGOS + Prémios PAGOS
- TOTAL INs Pendentes = Pessoais não pagos + Prémios não pagos
- TOTAL INs Projetado = Pagos + Pendentes

- TOTAL OUTs Pagos = Fixas + Boletins pagos + Despesas pessoais
- TOTAL OUTs Pendentes = Boletins Pendentes
- TOTAL OUTs Projetado = Pagos + Pendentes

SALDOS:
───────
- Saldo Atual = TOTAL INs Pagos - TOTAL OUTs Pagos
- Saldo Projetado = TOTAL INs Projetado - TOTAL OUTs Projetado
- Diferença = Saldo Projetado - Saldo Atual

DIVISÃO DE DESPESAS:
────────────────────
* Despesas MIXTAS (equipamento, projeto, fixa_mensal): ÷2 cada sócio
* Despesas PESSOAIS: afeta só o próprio sócio
* Boletins: cada sócio vê apenas os seus

SUGESTÃO DE BOLETIM (AUTOMATISMO):
──────────────────────────────────
Conceito: Distribuir o excedente projetado pelos meses restantes do ano.

Fórmula:
  Sugestão Boletim = Saldo Projetado ÷ Meses Restantes

Onde:
  - Saldo Projetado = diferença entre projetado e atual
  - Meses Restantes = meses até fim do ano SEM boletim emitido

Exemplo Novembro 2025:
  SP = €4.241,67
  Meses restantes = 2 (Nov + Dez)
  Sugestão = €4.241,67 ÷ 2 = €2.120,84/mês

Objetivo: Zerar saldo no final do ano fiscal.

Implementação: Campo sugestao_boletim no retorno de calcular_saldo_X()

====================================================================
6. EQUIPAMENTO
====================================================================

RENDIMENTO ACUMULADO:
* Campo rendimento_acumulado incrementa sempre que orçamento aprovado inclui repartição tipo 'EQUIPAMENTO'.
* Não decrementa mesmo se orçamento é revertido.

RELAÇÃO COM ORÇAMENTOS:
* Cada repartição de orçamento pode associar FK equipamento_id.
* Reporting por equipamento possível (quanto rendeu cada ativo).

====================================================================
7. SISTEMA DE TOTAIS POR BENEFICIÁRIO (PLANEADO)
====================================================================

STATUS: 📝 Especificado, aguarda implementação (próximo sprint)

7.1 VISUALIZAÇÃO EM ORÇAMENTOS
-------------------------------

**Frame Totais por Beneficiário (Lado EMPRESA):**
- Localização: OrcamentoForm, abaixo da tabela de repartições EMPRESA
- Mostra totais agrupados por beneficiário em tempo real
- Cálculo dinâmico: atualiza ao adicionar/editar/apagar items EMPRESA

**Cards Coloridos por Tipo:**
- 🟢 VERDE (Sócios): BA, RR
  - Display: "BA - Bruno: €1.500,00"
  - Display: "RR - Rafael: €800,00"
- 🔵 AZUL (Empresa): AGORA
  - Display: "AGORA - Empresa: €400,00"
- 🟠 LARANJA (Externos): FREELANCER_*, FORNECEDOR_*
  - Display: "FREELANCER_2 - João Silva: €500,00"
  - Display: "FORNECEDOR_5 - Rental Co: €200,00"

**Método calcular_totais_beneficiarios():**
```python
def calcular_totais_beneficiarios(self) -> Dict[str, Decimal]:
    """
    Retorna: {
        'BA': Decimal('1500.00'),
        'RR': Decimal('800.00'),
        'AGORA': Decimal('400.00'),
        'FREELANCER_2': Decimal('500.00'),
        'FORNECEDOR_5': Decimal('200.00')
    }
    """
    totais = {}
    for reparticao in self.reparticoes:
        beneficiario = reparticao.beneficiario
        totais[beneficiario] = totais.get(beneficiario, Decimal('0')) + reparticao.total
    return totais
```

**Validação Visual:**
- Soma de todos beneficiários == TOTAL EMPRESA
- Se diferença > 0.01€ → mostrar warning laranja
- Se coincidir → check verde

---

7.2 CONVERSÃO AUTOMÁTICA EM PROJETO
------------------------------------

**Ao converter orçamento aprovado em projeto:**

```python
def converter_em_projeto(orcamento_id):
    totais = calcular_totais_beneficiarios(orcamento_id)

    # Distribuir valores nos campos de rastreabilidade
    projeto = Projeto(
        premio_bruno = totais.get('BA', 0),
        premio_rafael = totais.get('RR', 0),
        valor_empresa = totais.get('AGORA', 0),
        valor_fornecedores = sum([
            v for k, v in totais.items()
            if k.startswith('FREELANCER_') or k.startswith('FORNECEDOR_')
        ])
    )
```

**Campos Projeto Preenchidos Automaticamente:**
- `premio_bruno`: soma de todas repartições com beneficiario='BA'
- `premio_rafael`: soma de todas repartições com beneficiario='RR'
- `valor_empresa`: soma de todas repartições com beneficiario='AGORA'
- `valor_fornecedores`: soma de FREELANCER_* + FORNECEDOR_*
- `valor_total`: total CLIENTE (já existente)

**Exemplo:**
```
Orçamento #O000042:
- TOTAL CLIENTE: €3.400,00

Repartições EMPRESA:
- BA: €1.500,00 (serviços)
- RR: €800,00 (serviços)
- AGORA: €400,00 (comissão)
- FREELANCER_2: €500,00 (edição)
- FORNECEDOR_5: €200,00 (equipamento alugado)

→ Projeto #P0084 criado:
  - valor_total: €3.400,00
  - premio_bruno: €1.500,00
  - premio_rafael: €800,00
  - valor_empresa: €400,00
  - valor_fornecedores: €700,00 (500+200)
```

---

7.3 RASTREABILIDADE FREELANCERS
--------------------------------

**Tabela: freelancer_trabalhos** (já implementada Migration 025)

**Criação Automática:**
- Quando orçamento aprovado tem repartição FREELANCER_X
- Manager: FreelancerTrabalhosManager.criar()
- Campos: freelancer_id, orcamento_id, projeto_id, descricao, valor, data, status='a_pagar'

**Status Workflow:**
- `a_pagar` → Trabalho concluído, aguarda pagamento
- `pago` → Freelancer já recebeu (data_pagamento preenchida)
- `cancelado` → Orçamento anulado ou trabalho cancelado

**Ficha Individual Freelancer:**
- Screen: FreelancerForm (novo)
- Secção superior: dados cadastrais (nome, NIF, IBAN, especialidade)
- Secção inferior: tabela de trabalhos históricos
- Colunas tabela: Data, Orçamento, Projeto, Descrição, Valor, Status, Ações
- Botão "Marcar como Pago" em cada linha com status='a_pagar'
- Totais no footer: Total A Pagar | Total Pago | Total Geral

**Dashboard Card:**
- Título: "💰 Freelancers A Pagar"
- Valor: sum(valor WHERE status='a_pagar')
- Clique: navega para FreelancersScreen com filtro status='a_pagar'

---

7.4 RASTREABILIDADE FORNECEDORES
---------------------------------

**Tabela: fornecedor_compras** (já implementada Migration 025)

**Estrutura Idêntica a freelancer_trabalhos:**
- Campos: fornecedor_id, orcamento_id, projeto_id, descricao, valor, data, status
- Mesmo status workflow: a_pagar → pago → cancelado

**Ficha Individual Fornecedor:**
- Screen: FornecedorForm (expandir existente)
- Adicionar secção: tabela de compras históricas
- Mesmo layout e funcionalidades que FreelancerForm

**Dashboard Card:**
- Título: "🏢 Fornecedores A Pagar"
- Valor: sum(valor WHERE status='a_pagar')
- Clique: navega para FornecedoresScreen com filtro status='a_pagar'

---

7.5 FLUXO COMPLETO END-TO-END
------------------------------

**1. CRIAR ORÇAMENTO:**
- User adiciona items CLIENTE (serviços, equipamentos, etc)
- User adiciona repartições EMPRESA (beneficiários: BA, RR, AGORA, FREELANCER_2, FORNECEDOR_5)
- Frame "Totais por Beneficiário" mostra distribuição em tempo real
- User valida visualmente que totais coincidem

**2. APROVAR ORÇAMENTO:**
- Botão "Aprovar Orçamento" → validação automática (totais CLIENTE = EMPRESA)
- Se válido:
  - Status muda para 'aprovado'
  - Sistema cria automaticamente registos em freelancer_trabalhos e fornecedor_compras
  - Cada registo com status='a_pagar', data=hoje, links para orcamento_id e projeto_id

**3. CONVERTER EM PROJETO:**
- Botão "Converter em Projeto" → criar projeto
- Campos rastreabilidade preenchidos automaticamente:
  - premio_bruno, premio_rafael, valor_empresa, valor_fornecedores
- Link bidirecional: orcamento.projeto_id ↔ projeto.orcamentos

**4. DASHBOARD:**
- Cards mostram totais pendentes:
  - "Freelancers A Pagar: €500,00"
  - "Fornecedores A Pagar: €200,00"
- User clica → navega para screen com filtro

**5. MARCAR COMO PAGO:**
- User abre ficha individual (FreelancerForm ou FornecedorForm)
- Vê tabela com todos trabalhos/compras
- Clica "Marcar como Pago" numa linha com status='a_pagar'
- Sistema:
  - Atualiza status='pago'
  - Preenche data_pagamento=hoje
  - Recalcula totais da ficha
  - Dashboard atualiza automaticamente

**6. HISTÓRICO PERMANENTE:**
- Registos NUNCA são apagados (histórico contabilístico)
- Status 'cancelado' permite anular sem perder rastreabilidade
- Relatórios futuros: quanto pago a cada freelancer/fornecedor por ano

---

7.6 IMPLEMENTAÇÃO TÉCNICA
--------------------------

**Ficheiros a Criar:**
- ui/screens/freelancer_form.py (screen ficha individual)
- ui/components/totais_beneficiarios_frame.py (frame reutilizável)

**Ficheiros a Modificar:**
- ui/screens/orcamento_form.py (+150 linhas: frame totais, cálculo dinâmico)
- ui/screens/dashboard.py (+2 cards: freelancers a_pagar, fornecedores a_pagar)
- ui/screens/fornecedor_form.py (+tabela compras históricas)
- logic/orcamentos.py (converter_em_projeto: preencher campos rastreabilidade)

**Managers Já Existentes (Migration 025):**
- FreelancerTrabalhosManager: calcular_total_a_pagar(), marcar_como_pago()
- FornecedorComprasManager: calcular_total_a_pagar(), marcar_como_pago()

**Estimativa:** 2-3 sessões de implementação

**Ver:** TODO.md (Tarefa 7), ARCHITECTURE.md (Orçamentos V2), DATABASE_SCHEMA.md (Migration 025)

====================================================================
NOTAS FINAIS E FONTE DE VERDADE:
====================================================================

- Toda a estrutura de dados detalhada está em DATABASE_SCHEMA.md.
- Para fluxos e decisões técnicas, ver DECISIONS.md; dúvidas fiscais específicas ver FISCAL.md; roadmap e tarefas ver TODO.md.

- Qualquer alteração de lógica aqui deve obrigatoriamente ser refletida na implementação (database/models/ e logic/).

Mantido por: Equipa Agora
Última revisão lógica: 2025-11-17 18:30 WET

