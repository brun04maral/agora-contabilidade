### MODELO DE DADOS - ORÇAMENTOS v2 (16/11/2025)

---

#### orcamentos
- id (PK)
- codigo
- cliente_id (FK → clientes)
- status (enum)
- owner (BA, RR)
- data_criacao
- data_evento
- local_evento
- valor_total (calculado CLIENTE)
- ...

#### orcamento_secoes
- id
- orcamento_id (FK)
- nome
- tipo ("servicos", "equipamento", "despesas")
- parent_id (FK → orcamento_secoes) (apenas para subsecções Equipamento)
- ordem
- subtotal (calculado)

#### orcamento_itens
- id
- orcamento_id (FK)
- secao_id (FK)
- descricao
- tipo ("servico", "equipamento", "transporte", "refeicao", "outro")
- quantidade
- dias
- preco_unitario (decimal)
- desconto (decimal, %) (opcional)
- total (calculado)
- ordem
- equipamento_id (opcional, FK)

#### orcamento_reparticoes
- id
- orcamento_id (FK)
- tipo ("servico", "equipamento", "despesa", "comissao")
- descricao
- beneficiario ("BA", "RR", "AGORA", "FREELANCER_[id]", "FORNECEDOR_[id]")
- quantidade
- dias
- valor_unitario
- percentagem (decimal, 3 casas, para "comissao")
- total (calculado)
- ordem
- equipamento_id (opcional, FK)
- fornecedor_id (opcional, FK)

---

#### enums
- status (orcamento): "rascunho", "aprovado", "rejeitado"
- tipo (secao): ver acima
- tipo (item/reparticao): ver acima
- beneficiario: ver acima

---

#### Integrações & regras
- Despesas: CLIENTE e EMPRESA replicadas, nunca editáveis manualmente no EMPRESA
- Comissões: percentagem/beneficiário fixos mas editáveis
- FK equip/fornecedor: referenciam linhas de respetivas tabelas

---

#### Checklist de migração
- Campos e enums existentes (ver código + BUSINESS_LOGIC.md)
- Índices para performance (orcamento_id, tipo, beneficiario)
- Testes: CRUD de todos os tipos, espelhamento de despesas, bloqueio aprovação
