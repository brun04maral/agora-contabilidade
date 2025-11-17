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
5. CÁLCULOS FINANCEIROS
====================================================================

SALDOS PESSOAIS:
* Saldos = Σ (projetos ganhos + prémios + receitas) - Σ (despesas pagas + boletins pagos)
* Cada sócio tem regra de partilha definida (50/50 ou 100% casos pessoais).

FÓRMULA:
BA = 
  Σ [projetos.owner='BA' and estado='PAGO' → prémio_bruno] +
  Σ [orcamentos.owner='BA' and estado='PAGO' → valor_empresa] +
  Σ [saldo_fixo_mensal/2, equipamento/2, projeto/2, pessoal_bruno]
  - Σ [despesas pagas (ver tipos relevantes)]
  - Σ [boletins sócio BA pagos]

DIVISÃO:
* Despesas:
  - MIXTO (equipamento, projeto, fixa_mensal): paga metade cada sócio
  - PESSOAL: afeta só o próprio
* Boletins: cada sócio vê só os seus.

INs E OUTs:
* IN: prémios, receitas empresa, prémios freelancer se aplicável
* OUT: despesas, boletins, repartições especiais.

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
NOTAS FINAIS E FONTE DE VERDADE:
====================================================================

- Toda a estrutura de dados detalhada está em DATABASE_SCHEMA.md.
- Para fluxos e decisões técnicas, ver DECISIONS.md; dúvidas fiscais específicas ver FISCAL.md; roadmap e tarefas ver TODO.md.

- Qualquer alteração de lógica aqui deve obrigatoriamente ser refletida na implementação (database/models/ e logic/).

Mantido por: Equipa Agora
Última revisão lógica: 2025-11-17 09:40 WET

