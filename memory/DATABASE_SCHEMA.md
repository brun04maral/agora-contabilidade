# 🗄️ DATABASE_SCHEMA.md - ATUALIZAÇÕES (15/11/2025)

## ⚠️ INSTRUÇÕES
Adicionar esta secção ao final do ficheiro `DATABASE_SCHEMA.md` existente, antes de qualquer secção de "Histórico" ou "Changelog".

---

## 📋 ATUALIZAÇÕES PENDENTES

As seguintes alterações foram documentadas em `BUSINESS_LOGIC.md` e precisam ser implementadas via migrations.

---

### 1. Tabela `orcamentos` - Adicionar Coluna

**Coluna a adicionar:**
```sql
owner VARCHAR(2) NOT NULL  -- 'BA' ou 'RR'
```

**Migration:** 020
**Razão:** Todo orçamento precisa de um responsável (owner) definido. Determina quem gere o orçamento e posteriormente o projeto.

**Default para dados existentes:** 
- Pode usar 'BA' como default ou inferir do cliente
- Avaliar caso a caso durante migration

---

### 2. Tabela `projetos` - Múltiplas Alterações

**Colunas a adicionar:**
```sql
-- Owner (responsável pelo projeto)
owner VARCHAR(2) NOT NULL  -- 'BA' ou 'RR'

-- Rastreabilidade financeira (valores decompostos de orçamento)
valor_empresa DECIMAL(10,2) DEFAULT 0        -- Parcela da empresa
valor_fornecedores DECIMAL(10,2) DEFAULT 0   -- Total pago a fornecedores
valor_equipamento DECIMAL(10,2) DEFAULT 0    -- Rendimento de equipamento usado
valor_despesas DECIMAL(10,2) DEFAULT 0       -- Despesas do projeto

-- Data de pagamento
data_pagamento DATE NULL  -- Quando projeto foi marcado como PAGO
```

**Coluna a alterar:**
```sql
-- ANTES:
estado VARCHAR(20)  -- 'ativo' | 'concluido' | 'cancelado'

-- DEPOIS:
estado VARCHAR(20)  -- 'ATIVO' | 'FINALIZADO' | 'PAGO' | 'ANULADO'
```

**Migration:** 020

**Mapeamento de estados existentes:**
```python
# Durante migration:
'ativo' → 'ATIVO'
'concluido' → 'FINALIZADO'
'cancelado' → 'ANULADO'
```

**Razão das alterações:**
- **owner:** Necessário para gestão e cálculo de saldos pessoais
- **Estados:** 
  - ATIVO: Projeto em curso
  - FINALIZADO: Concluído mas não pago (transição automática por `data_fim`)
  - PAGO: Cliente pagou, prémios distribuídos
  - ANULADO: Cancelado
- **Rastreabilidade:** Permite saber distribuição de valores vindos de orçamentos
- **data_pagamento:** Rastrear quando projeto foi efetivamente pago

**Regra de transição automática:**
```python
# Job diário ou ao carregar dashboard/projetos:
for projeto in projetos:
    if projeto.estado == 'ATIVO' and projeto.data_fim and projeto.data_fim < hoje:
        projeto.estado = 'FINALIZADO'
        projeto.save()
```

---

### 3. Tabela `proposta_reparticoes` - Reestruturação

**Coluna a remover:**
```sql
entidade VARCHAR(10)  -- 'BA' ou 'RR' (DEPRECADO)
```

**Colunas a adicionar:**
```sql
tipo VARCHAR(20) NOT NULL  -- 'BA' | 'RR' | 'EMPRESA' | 'FORNECEDOR' | 'EQUIPAMENTO' | 'DESPESA'
fornecedor_id INTEGER NULL
equipamento_id INTEGER NULL
```

**Constraints a adicionar:**
```sql
FOREIGN KEY (fornecedor_id) REFERENCES fornecedores(id) ON DELETE SET NULL
FOREIGN KEY (equipamento_id) REFERENCES equipamento(id) ON DELETE SET NULL
```

**Migration:** 020

**Mapeamento de dados existentes:**
```python
# Durante migration:
# Repartições antigas com entidade='BA' → tipo='BA', fornecedor_id=NULL, equipamento_id=NULL
# Repartições antigas com entidade='RR' → tipo='RR', fornecedor_id=NULL, equipamento_id=NULL
```

**Razão:** 
- Repartições precisam suportar 6 tipos diferentes
- Tipos FORNECEDOR e EQUIPAMENTO precisam de FKs para rastreabilidade
- Sistema expandido permite distribuição completa de valores de orçamento

**Tipos de repartição:**
- **BA:** Prémio para Bruno Amaral
- **RR:** Prémio para Rafael Reigota  
- **EMPRESA:** Valor que fica na empresa
- **FORNECEDOR:** Pago a fornecedor específico (requer `fornecedor_id`)
- **EQUIPAMENTO:** Rendimento de equipamento usado (requer `equipamento_id`)
- **DESPESA:** Outras despesas do orçamento

---

### 4. Tabela `equipamento` - Adicionar Coluna

**Coluna a adicionar:**
```sql
rendimento_acumulado DECIMAL(10,2) DEFAULT 0
```

**Migration:** 020

**Razão:** Rastrear quanto cada equipamento já rendeu ao longo do tempo através de repartições em orçamentos.

**Atualização:**
- Ao aprovar orçamento com repartição tipo='EQUIPAMENTO' → incrementa rendimento
- Não reverte se projeto/orçamento anulado (mantém histórico)

---

### 5. Sistema de Templates de Boletins - A REMOVER

**Status:** Sistema será removido da UI mas tabelas podem permanecer (legacy)

**Tabelas afetadas:**
- `boletim_templates` (pode manter ou remover em limpeza futura)

**Razão:** Sistema de templates é demasiado complexo. Substituído por funcionalidade "Duplicar Boletim".

**Ver:** DECISIONS.md, TODO.md

---

### 6. NOVA Tabela `receitas` - A IMPLEMENTAR (Futuro)

**Status:** ⏳ Documentado mas não implementado
**Prioridade:** Média
**Migration:** 021 (futura)

**Estrutura proposta (a discutir):**
```sql
CREATE TABLE receitas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    numero VARCHAR(20) UNIQUE NOT NULL,  -- #R000001, #R000002, etc
    
    -- Relações
    projeto_id INTEGER NULL,
    cliente_id INTEGER NULL,
    
    -- Dados principais
    descricao TEXT NOT NULL,
    valor DECIMAL(10,2) NOT NULL,
    data DATE NOT NULL,
    
    -- Estado
    estado VARCHAR(20) NOT NULL,  -- 'ATIVO' | 'CANCELADO'
    tipo VARCHAR(20) NOT NULL,    -- 'PROJETO' | 'OUTRO'
    
    -- Metadata
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    FOREIGN KEY (projeto_id) REFERENCES projetos(id) ON DELETE SET NULL,
    FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE SET NULL
);

CREATE INDEX idx_receitas_projeto ON receitas(projeto_id);
CREATE INDEX idx_receitas_cliente ON receitas(cliente_id);
CREATE INDEX idx_receitas_data ON receitas(data);
CREATE INDEX idx_receitas_estado ON receitas(estado);
```

**Comportamento:**
- Ao marcar projeto como PAGO → criar receita ATIVO automaticamente
- Ao reverter projeto para FINALIZADO → marcar receita como CANCELADO (não apagar)
- Permite receitas avulsas (sem projeto): subsídios, vendas de equipamento, etc

**Decisões pendentes:**
- Receita sempre = valor total do projeto? Ou pode ser parcial?
- Permitir múltiplas receitas por projeto? (pagamentos faseados)
- Campos adicionais? (método pagamento, referência, etc)

**Ver:** 
- TODO.md (tarefa de implementação)
- DECISIONS.md (decisão sobre necessidade de receitas)
- BUSINESS_LOGIC.md Secção 3.4

---

## 📊 Resumo de Alterações

**Migration 020 (Prioritária):**
- ✅ `orcamentos.owner` (novo)
- ✅ `projetos.owner` (novo)
- ✅ `projetos.estado` (atualizar enum)
- ✅ `projetos.valor_empresa` (novo)
- ✅ `projetos.valor_fornecedores` (novo)
- ✅ `projetos.valor_equipamento` (novo)
- ✅ `projetos.valor_despesas` (novo)
- ✅ `projetos.data_pagamento` (novo)
- ✅ `proposta_reparticoes.entidade` (remover)
- ✅ `proposta_reparticoes.tipo` (novo)
- ✅ `proposta_reparticoes.fornecedor_id` (novo + FK)
- ✅ `proposta_reparticoes.equipamento_id` (novo + FK)
- ✅ `equipamento.rendimento_acumulado` (novo)

**Migration 021 (Futura):**
- ⏳ Criar tabela `receitas` completa

---

## 🔗 Referências

- **BUSINESS_LOGIC.md:** Lógica de negócio detalhada
- **DECISIONS.md:** Decisões técnicas e trade-offs
- **TODO.md:** Tarefas de implementação priorizadas

---

_Última atualização: 15/11/2025_
