========================================
SECÇÃO 1: SISTEMA DE ORÇAMENTOS
========================================

Versão: 2.0
Última atualização: 16/11/2025


========================================
1. VISÃO GERAL
========================================

O sistema de orçamentos permite criar propostas detalhadas para clientes, divididas em duas perspectivas independentes:

- LADO CLIENTE: O que o cliente vê e paga (proposta comercial)
- LADO EMPRESA: Como a receita é distribuída internamente (repartição de custos e beneficiários)

REGRA FUNDAMENTAL:
TOTAL CLIENTE deve ser IGUAL a TOTAL EMPRESA para aprovação do orçamento.


========================================
2. ESTRUTURA DO LADO CLIENTE
========================================

2.1. SECÇÕES PRINCIPAIS (ordem fixa)
------------------------------------
1. Serviços (sem subsecções)
2. Equipamento (com subsecções opcionais)
3. Despesas (sem subsecções)


2.2. SUBSECÇÕES (apenas em Equipamento)
------------------------------------
- Vídeo
- Iluminação
- Som
- Estruturas
- Informática


2.3. TIPOS DE ITEMS
------------------------------------

A) ITEMS DE SERVIÇOS/EQUIPAMENTO

Campos:
- Descrição (texto livre)
- Quantidade (número inteiro)
- Dias (número inteiro)
- Preço unitário (decimal, €)
- Desconto (percentagem, 0-100%, opcional)
- Ordem (número inteiro, para ordenação)

Cálculo:
Total = Quantidade × Dias × Preço_Unitário × (1 - Desconto/100)

Exemplo:
Descrição: "Realização"
Quantidade: 2
Dias: 1
Preço unitário: €175,00
Desconto: 0%
Total = 2 × 1 × €175,00 × 1 = €350,00

Visualização:
Realização | 2 × 1 dia × €175,00 = €350,00


B) ITEMS DE DESPESAS - TRANSPORTE

Campos:
- Tipo: "Transporte" (fixo)
- Descrição: "Transporte" (default, editável)
- Kms (número inteiro ou decimal)
- Valor por Km (decimal, €, default: €0,40)

Cálculo:
Total = Kms × Valor_por_Km

Exemplo:
Descrição: "Transporte"
Kms: 250
Valor/Km: €0,40
Total = 250 × €0,40 = €100,00

Visualização:
Transporte | 250 km × €0,40/km = €100,00


C) ITEMS DE DESPESAS - REFEIÇÃO

Campos:
- Tipo: "Refeição" (fixo)
- Descrição: "Refeição" (default, editável)
- Número de Refeições (número inteiro)
- Valor por Refeição (decimal, €, default: €20,00)

Cálculo:
Total = Nº_Refeições × Valor_por_Refeição

Exemplo:
Descrição: "Refeição"
Nº Refeições: 6
Valor/Refeição: €20,00
Total = 6 × €20,00 = €120,00

Visualização:
Refeição | 6 refeições × €20,00 = €120,00


D) ITEMS DE DESPESAS - OUTRO (valor fixo)

Campos:
- Tipo: "Outro" (fixo)
- Descrição (texto livre)
- Valor (decimal, €)

Cálculo:
Total = Valor

Exemplo:
Descrição: "Estacionamento"
Valor: €50,00
Total = €50,00

Visualização:
Estacionamento | €50,00


2.4. CÁLCULO DE TOTAIS
------------------------------------
- Subtotal da Secção = Soma de todos os items da secção (incluindo subsecções)
- TOTAL CLIENTE = Soma de todos os subtotais de todas as secções


========================================
3. ESTRUTURA DO LADO EMPRESA
========================================

3.1. SECÕES (espelham o CLIENTE)
------------------------------------
1. Serviços
2. Equipamento
3. Despesas (ESPELHADAS automaticamente)
4. Comissões (secção especial)


3.2. BENEFICIÁRIOS DISPONÍVEIS
------------------------------------
- BA (sócio)
- RR (sócio)
- AGORA (empresa)
- Freelancer [nome] (da lista de fornecedores, tipo FREELANCER)
- Fornecedor [nome] (da lista de fornecedores, tipo EMPRESA)


3.3. TIPOS DE ITEMS
------------------------------------

A) ITEMS DE SERVIÇOS

Campos:
- Descrição (texto livre)
- Beneficiário (dropdown: BA, RR, Freelancer [nome])
- Quantidade (número inteiro)
- Dias (número inteiro)
- Valor unitário (decimal, €) - pode ser diferente do lado CLIENTE
- Ordem

Cálculo:
Total = Quantidade × Dias × Valor_Unitário

Notas:
- Valor unitário pode ser diferente do lado CLIENTE (custo real vs valor cobrado)
- Beneficiário indica quem recebe este valor


B) ITEMS DE EQUIPAMENTO

Campos:
- Descrição (texto livre ou da lista de equipamentos)
- Beneficiário (dropdown: AGORA, BA, RR, Fornecedor [nome])
- Quantidade (número inteiro)
- Dias (número inteiro)
- Valor unitário (decimal, €) - valor de amortização ou aluguer
- Equipamento_ID (opcional, se selecionado da lista)
- Ordem

Notas:
- Se escolhido da lista de equipamentos, beneficiário = AGORA (default)
- Valor unitário = valor de amortização (não o valor cobrado ao cliente)
- Este valor é registado na DB do equipamento para controlo de amortização


C) ITEMS DE DESPESAS (ESPELHADAS)

REGRA: Despesas são automaticamente espelhadas do lado CLIENTE para o lado EMPRESA.

Características:
- Sincronização automática (não editáveis no lado EMPRESA)
- Beneficiário fixo: AGORA
- Valores idênticos aos do lado CLIENTE
- Descrição, cálculo e total replicados

Visualização:
⚠️ Sincronizado automaticamente do lado CLIENTE


D) ITEMS DE COMISSÕES

Campos:
- Descrição (texto fixo)
- Tipo (dropdown: "Comissão Venda" ou "Comissão Empresa")
- Percentagem (decimal, 3 casas decimais, editável)
- Base de cálculo (auto: TOTAL EMPRESA antes das comissões)
- Beneficiário (auto-determinado pelo tipo)

Tipos de Comissões:
1. COMISSÃO VENDA (5% default) → Owner (BA ou RR)
2. COMISSÃO EMPRESA (10% default) → AGORA

Cálculo:
Total = Base_de_Cálculo × (Percentagem / 100)

Notas:
- Percentagem editável até 3 casas decimais (ex: 5,125%)
- As comissões aplicam-se sobre o total ANTES das próprias comissões


3.4. CÁLCULO DE TOTAIS
------------------------------------
Ordem de cálculo:
1. Subtotal Serviços = Soma items de Serviços
2. Subtotal Equipamento = Soma items de Equipamento
3. Subtotal Despesas = Soma items de Despesas (espelhadas)
4. Base para Comissões = Subtotal Serviços + Subtotal Equipamento + Subtotal Despesas
5. Valor Comissão Venda = Base × (% Comissão Venda / 100)
6. Valor Comissão Empresa = Base × (% Comissão Empresa / 100)
7. TOTAL EMPRESA = Base + Valor Comissão Venda + Valor Comissão Empresa


========================================
4. VALIDAÇÕES E REGRAS DE NEGÓCIO
========================================

4.1. VALIDAÇÃO CRÍTICA
------------------------------------
REGRA: TOTAL EMPRESA = TOTAL CLIENTE

Se TOTAL EMPRESA ≠ TOTAL CLIENTE:
- Mostrar aviso visual em vermelho
- Exibir diferença em tempo real
- Bloquear aprovação do orçamento
- Permitir ajuste das comissões (percentagens) para igualar


4.2. OUTRAS VALIDAÇÕES
------------------------------------
- Não permitir beneficiários duplicados em Serviços/Equipamento da mesma pessoa
- Campos obrigatórios: descrição, quantidade, dias, valores
- Valores numéricos devem ser > 0
- Percentagens devem estar entre 0 e 100
- Kms e refeições devem ser > 0


4.3. ESTADOS DO ORÇAMENTO
------------------------------------
- RASCUNHO: editável, não validado
- APROVADO: validado (totais batem), não editável (apenas anulável)
- REJEITADO/ANULADO: não editável, arquivado

Transições:
RASCUNHO → APROVADO: apenas se TOTAL EMPRESA = TOTAL CLIENTE
APROVADO → REJEITADO: a qualquer momento
REJEITADO: estado final (não pode voltar)


========================================
5. FUNCIONALIDADES ESPECIAIS
========================================

5.1. AUTO-PREENCHER COMISSÕES
------------------------------------
Botão "🔄 Auto-preencher Comissões" no lado EMPRESA:
Cria Comissão Venda (5%) e Comissão Empresa (10%) conforme regra base, se não existirem.


5.2. SELEÇÃO DE EQUIPAMENTO/FREELANCER DA LISTA
------------------------------------
Ao adicionar item, dialog permite escolher "Da lista" ou "Personalizado". Se da lista, preenche descrição e valor sugerido automaticamente, valor editável para ajuste de amortização/custo.


5.3. SINCRONIZAÇÃO DE DESPESAS
------------------------------------
Qualquer alteração nas despesas do lado CLIENTE é refletida automaticamente no lado EMPRESA. Não são editáveis no EMPRESA. Beneficiário sempre AGORA.


========================================
6. MODELO DE DADOS (resumo)
========================================

Tabelas principais:
- orcamentos (id, codigo, cliente_id, status, owner, data_criacao, data_evento, local_evento, valor_total)
- orcamento_secoes (id, orcamento_id, nome, tipo, parent_id, ordem, subtotal)
- orcamento_itens (id, orcamento_id, secao_id, descricao, quantidade, dias, preco_unitario, desconto, total, ordem, equipamento_id)
- orcamento_reparticoes (id, orcamento_id, tipo, descricao, beneficiario, quantidade, dias, valor_unitario, percentagem, total, ordem, equipamento_id, fornecedor_id)

Campos especiais:
- orcamento_itens.tipo: "servico", "equipamento", "transporte", "refeicao", "outro"
- orcamento_reparticoes.tipo: "servico", "equipamento", "despesa", "comissao"
- orcamento_reparticoes.beneficiario: "BA", "RR", "AGORA", "FREELANCER_[id]", "FORNECEDOR_[id]"


========================================
7. FLUXO DE TRABALHO TÍPICO
========================================

1. Criar novo orçamento (preencher header: código, owner, cliente, datas)
2. LADO CLIENTE:
   a. Adicionar secção "Serviços"
   b. Adicionar items de serviços
   c. Adicionar secção "Equipamento"
   d. Adicionar items de equipamento (com subsecções se necessário)
   e. Adicionar secção "Despesas"
   f. Adicionar despesas (transporte, refeições, outros)
   g. Verificar TOTAL CLIENTE

3. LADO EMPRESA:
   a. Adicionar items de Serviços (definir beneficiários)
   b. Adicionar items de Equipamento (definir beneficiários e valores reais)
   c. Despesas são espelhadas automaticamente
   d. Clicar "Auto-preencher Comissões" ou adicionar manualmente
   e. Ajustar percentagens das comissões se necessário
   f. Verificar se TOTAL EMPRESA = TOTAL CLIENTE

4. Aprovação:
   a. Se totais batem: aprovar orçamento
   b. Se não batem: ajustar items/comissões até igualar
   c. Orçamento aprovado fica bloqueado para edição

========================================
FIM DA SECÇÃO 1
========================================
