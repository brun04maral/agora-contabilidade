# 📋 DECISIONS.md - NOVAS DECISÕES (15/11/2025)

## ⚠️ INSTRUÇÕES
Adicionar estas decisões ao final do ficheiro `DECISIONS.md` existente.

---

## 💼 Orçamentos: Dois Lados Espelhados vs Formulário Único

### Cliente + Empresa vs Campos Simples
**Decisão:** Modelo de dois lados espelhados (Cliente + Empresa)  
**Data:** 2025-11-15  
**Motivação:**
- Orçamento precisa de duas perspectivas distintas:
  1. **Cliente:** O que prometemos (secções, itens, PDF bonito)
  2. **Empresa:** Como distribuímos internamente (BA, RR, fornecedores, equipamento)
- Total Cliente DEVE = Total Empresa (validação crítica antes de aprovar)

**Opções consideradas:**

**OPÇÃO 1 (Descartada):** Formulário único com todos os campos misturados
- ❌ Mistura informação do cliente com distribuição interna
- ❌ Confuso para utilizador (o que vai para PDF vs o que é interno?)
- ❌ Difícil validar que totais coincidem
- ❌ PDF exportado incluiria informação interna por engano

**OPÇÃO 2 (Escolhida):** Dois lados espelhados (Cliente | Empresa)
- ✅ Separação clara: Cliente (PDF) vs Empresa (interno)
- ✅ Validação visual imediata (diferença destacada em tempo real)
- ✅ Flexibilidade: repartições linkam com fornecedores/equipamento (FKs)
- ✅ Rastreabilidade: saber exatamente quanto foi para onde
- ✅ PDF limpo: apenas lado Cliente exportado

**Implementação:**
```
┌─────────────────────────────────┬─────────────────────────────────┐
│ LADO CLIENTE (PDF)              │ LADO EMPRESA (Interno)          │
├─────────────────────────────────┼─────────────────────────────────┤
│ Secções                         │ Repartições                     │
│  └─ Itens (qtd × preço)         │  ├─ BA: €2.000                  │
│                                 │  ├─ RR: €1.500                  │
│ Secção: Vídeo                   │  ├─ EMPRESA: €500               │
│  - Câmara: €1.000               │  ├─ FORNECEDOR: Sara €300       │
│  - Edição: €2.000               │  ├─ EQUIPAMENTO: PTZ €200       │
│  - Deslocações: €500            │  └─ DESPESA: €100               │
│                                 │                                 │
│ TOTAL: €3.500                   │ TOTAL: €3.600 ⚠️ Dif: +€100    │
└─────────────────────────────────┴─────────────────────────────────┘
```

**Estrutura de dados:**
- Lado CLIENTE: `proposta_secoes` → `proposta_itens`
- Lado EMPRESA: `proposta_reparticoes` com 6 tipos:
  - BA, RR (prémios)
  - EMPRESA (margem)
  - FORNECEDOR (requer `fornecedor_id` FK)
  - EQUIPAMENTO (requer `equipamento_id` FK, atualiza rendimento)
  - DESPESA (outros custos)

**Validação crítica:**
```python
if total_cliente != total_empresa:
    raise ValidationError(f"Totais não coincidem (diferença: €{abs(diff):.2f})")
    # Bloqueia aprovação até corrigir
```

**Trade-offs:**
- ❌ Mais complexo de implementar (~500 linhas vs ~200)
- ❌ Mais campos para preencher
- ✅ Muito mais claro e profissional
- ✅ Facilita auditorias e relatórios
- ✅ Escalável para futuras integrações (contabilidade, faturação)

**Aplicável a:** Sistema de orçamentos único

---

## 📋 Boletins: Templates Recorrentes vs Duplicar

### Sistema Automático vs Manual Controlado
**Decisão:** Remover templates, adicionar "Duplicar"  
**Data:** 2025-11-15  
**Motivação:**
- Templates recorrentes adicionam complexidade sem valor real
- Boletins mensais são similares mas não idênticos (projetos mudam)
- Utilizador prefere controlo manual e visibilidade

**Opções consideradas:**

**OPÇÃO 1 (Descartada):** Sistema de templates com geração automática
- Tabela `boletim_templates` com configuração de templates
- Botão "Gerar Recorrentes" cria boletins do mês automaticamente
- Prevenção de duplicados por mês/ano/sócio
- Templates podem ter linhas pré-definidas (opcional)
- ❌ Complexo: ~2000 linhas de código (tabelas, migrations, UI, logic)
- ❌ Templates ficam rapidamente desatualizados (projetos mudam constantemente)
- ❌ Geração automática pode criar erros silenciosos (valores errados)
- ❌ Manutenção: precisa atualizar templates regularmente
- ❌ Pouco flexível: difícil adaptar a situações únicas
- ❌ Confunde utilizador: "O que é template? O que é boletim real?"

**OPÇÃO 2 (Escolhida):** Botão "Duplicar" em boletins existentes
- Copiar boletim completo (header: sócio, mês, ano + todas as linhas)
- Permite editar ANTES de gravar (seguro)
- Simples e direto
- ✅ Utilizador tem controlo total (vê exatamente o que está a fazer)
- ✅ ~50 linhas de código (um método simples)
- ✅ Não precisa manutenção de templates
- ✅ Mais rápido na prática (1 clique vs navegar templates)
- ✅ Flexível: duplica de qualquer boletim (não só "templates")
- ✅ Transparente: utilizador vê exatamente o que foi copiado

**Implementação:**
```python
def duplicar_boletim(boletim_id):
    """Duplica boletim completo (header + linhas)"""
    original = Boletim.get(boletim_id)
    
    # Copiar header
    novo = Boletim(
        socio = original.socio,
        mes = original.mes,  # Utilizador pode mudar
        ano = original.ano,
        descricao = f"{original.descricao} (cópia)"
    )
    
    # Copiar todas as linhas
    for linha_original in original.linhas:
        BoletimLinha(
            boletim = novo,
            data_inicio = linha_original.data_inicio,
            data_fim = linha_original.data_fim,
            dias_nacional = linha_original.dias_nacional,
            dias_estrangeiro = linha_original.dias_estrangeiro,
            kms = linha_original.kms,
            projeto_id = linha_original.projeto_id,
            nota = linha_original.nota
        )
    
    return novo  # Abrir em BoletimFormScreen para editar
```

**Remover:**
- Tabela `boletim_templates` (ou manter como legacy sem UI)
- Screen `templates_boletins.py`
- Botão "📋 Templates" no header de BoletinsScreen
- Botão "🔁 Gerar Recorrentes" no header de BoletinsScreen
- Lógica de geração automática (~500 linhas)

**Adicionar:**
- Botão "📋 Duplicar" em BoletimFormScreen (ao lado de Gravar)
- ~50 linhas de código

**Impacto:**
- Remove ~2000 linhas de código complexo
- Simplifica UI (menos 2 botões, menos 1 screen)
- Melhor UX (mais previsível e transparente)
- Manutenção reduzida drasticamente

**Aplicável a:** Qualquer entidade que precise de duplicação (Orçamentos também?)

---

## 🎯 Projetos: Estados Expandidos (ATIVO/FINALIZADO/PAGO)

### 3 Estados vs 4 Estados
**Decisão:** 4 estados (ATIVO, FINALIZADO, PAGO, ANULADO)  
**Data:** 2025-11-15  
**Motivação:**
- Projeto completo ≠ Projeto pago (ciclos diferentes)
- Necessário distinguir trabalho feito vs dinheiro recebido
- Prémios só devem contar para saldos quando projeto PAGO

**Opções consideradas:**

**OPÇÃO 1 (Descartada):** Manter 3 estados (ativo, concluído, cancelado)
- ❌ Não distingue "trabalho terminado" de "cliente pagou"
- ❌ Quando contar prémios para saldos? Logo ao concluir ou quando pagar?
- ❌ Difícil rastrear receitas futuras (sem tabela receitas)
- ❌ Não permite calcular "Prémios Não Faturados" (expectativa vs realidade)

**OPÇÃO 2 (Escolhida):** 4 estados com lógica clara e transições definidas
```
ATIVO → FINALIZADO → PAGO → ANULADO
  ↑                    │              │
  └─────── todas reversíveis ─────────┘
```

**Estados:**
- **ATIVO:** Trabalho em curso, projeto ativo
  - Pode ter `data_fim` definida (prazo) ou não
  - Transição: manual ou automática (quando `data_fim` < hoje)
  
- **FINALIZADO:** Trabalho completo, aguarda pagamento
  - **Transição automática:** quando `data_fim` passa (job diário)
  - Prémios aparecem em "Prémios Não Faturados" (expectativa)
  - NÃO conta para Saldo Atual (conservador)
  - Pode voltar para ATIVO se trabalho reiniciou
  
- **PAGO:** Cliente pagou o projeto
  - **Transição manual:** botão "Marcar como Pago"
  - Distribui prémios BA/RR aos saldos (INs)
  - Cria receita (quando implementado - ver TODO)
  - Prémios contam para Saldo Atual (confirmado)
  - Pode voltar para FINALIZADO se marcado por engano
  
- **ANULADO:** Projeto cancelado (cliente desistiu, orçamento rejeitado)
  - Não conta para saldos (nem atual nem projetado)
  - Pode voltar para ATIVO se reativar projeto
  - Se tem orçamento linkado → orçamento também anula

**Vantagens:**
- ✅ Separação clara: trabalho concluído vs pagamento recebido
- ✅ Permite calcular "Prémios Não Faturados" (projetos FINALIZADOS)
- ✅ Saldos conservadores: só PAGO conta (evita inflação de saldos)
- ✅ Facilita futura integração com tabela `receitas`
- ✅ Rastreabilidade: saber exatamente quando trabalho terminou vs quando pagou
- ✅ Relatórios: "Quanto temos a receber?" (FINALIZADOS)

**Transições:**
```python
# Automática (job diário):
ATIVO → FINALIZADO  # quando data_fim < hoje

# Manual (botões):
ATIVO → ANULADO
FINALIZADO → PAGO
FINALIZADO → ATIVO  # corrigir: trabalho não estava terminado
PAGO → FINALIZADO   # corrigir: marcou por engano
PAGO → ANULADO
```

**Feature adicional: Prémios Não Faturados**
```
Saldos Pessoais - BA
├─ Saldo Atual: €12.120,98
├─ Saldo Projetado: €14.120,98 (+€2.000)  ← só mostrar se houver
│
├─ INs
│  ├─ Projetos pessoais (PAGO): €10.000
│  ├─ Prémios (PAGO): €5.000
│  └─ 💡 Prémios não faturados (FINALIZADO): €2.000  ← NOVO
│      └─ Clicável → filtra Projetos por FINALIZADO
```

**Cálculo:**
- **Saldo Atual:** só projetos PAGO
- **Saldo Projetado:** Atual + Prémios Não Faturados (FINALIZADOS)
- Cor diferente (laranja claro) para distinguir

**Trade-offs:**
- ❌ Mais um estado para gerir
- ✅ Muito mais claro e honesto (realidade vs expectativa)
- ✅ Permite decisões informadas ("Posso gastar X? Tenho Y confirmado + Z por receber")
- ✅ Escalável para futuras features (faturação, previsões)

---

## 💰 Sistema de Receitas: Necessidade Identificada

### Status Atual vs Sistema Completo
**Decisão:** Implementar tabela `receitas` (TODO - Prioridade Média)  
**Data:** 2025-11-15  
**Motivação:**
- Atualmente não há registo formal de receitas/pagamentos
- Projetos PAGO apenas distribuem prémios mas não criam receita rastreável
- Falta rastreabilidade de quando e quanto cliente pagou

**Problema atual:**
- ❌ Não sabemos QUANDO cliente pagou (apenas que projeto está PAGO)
- ❌ Impossível gerar relatório "Receitas vs Despesas" mensal
- ❌ Difícil auditar pagamentos (backtracking)
- ❌ Ao reverter projeto PAGO→FINALIZADO, prémios somem sem histórico
- ❌ Não há conceito de receitas avulsas (subsídios, vendas equipamento)
- ❌ Impossível prever cash-flow (receitas esperadas vs realizadas)

**Solução proposta:**
Tabela `receitas` com link bidirecional para projetos

**Estrutura (a refinar):**
```sql
receitas
├─ numero: VARCHAR(20) UNIQUE  -- #R000001, #R000002
├─ projeto_id: INTEGER NULL    -- FK → projetos (nullable para receitas avulsas)
├─ cliente_id: INTEGER NULL    -- FK → clientes
├─ descricao: TEXT
├─ valor: DECIMAL(10,2)
├─ data: DATE                  -- Data do pagamento
├─ estado: VARCHAR(20)         -- ATIVO | CANCELADO
├─ tipo: VARCHAR(20)           -- PROJETO | OUTRO (subsídios, vendas, etc)
└─ created_at, updated_at
```

**Comportamento:**
1. **Ao marcar projeto como PAGO:**
   ```python
   receita = Receita(
       numero = gerar_numero_receita(),
       projeto_id = projeto.id,
       cliente_id = projeto.cliente_id,
       descricao = f"Projeto {projeto.codigo} - {projeto.cliente.nome}",
       valor = projeto.valor,
       data = hoje,
       estado = 'ATIVO',
       tipo = 'PROJETO'
   )
   projeto.receita_id = receita.id  # Link bidirecional
   ```

2. **Ao reverter projeto para FINALIZADO:**
   ```python
   receita.estado = 'CANCELADO'  # NÃO apagar (histórico)
   receita.updated_at = agora
   projeto.receita_id = None  # Deslinkar
   ```

3. **Receitas avulsas (sem projeto):**
   ```python
   receita = Receita(
       projeto_id = None,
       cliente_id = None,  # Ou cliente genérico "Outros"
       descricao = "Subsídio COVID-19",
       valor = 5000,
       tipo = 'OUTRO'
   )
   ```

**UI necessária:**
- Screen Receitas (CRUD básico)
- Coluna "Receita" em Projetos (link clicável)
- Filtros: por cliente, por período, por estado, por tipo
- Relatório: Receitas vs Despesas (mensal/anual)

**Relatórios possíveis:**
- Receitas vs Despesas (mensal/trimestral/anual)
- Receitas por Cliente (quem paga mais?)
- Previsão de receitas (projetos FINALIZADOS aguardando pagamento)
- Cash-flow: entradas vs saídas por mês
- Evolução de receitas ano-a-ano

**Trade-offs:**
- ❌ Adiciona complexidade (mais uma tabela + UI + logic)
- ❌ Precisa screen adicional (Receitas CRUD)
- ❌ Mais campos para preencher? (ou automático ao marcar PAGO)
- ✅ Rastreabilidade completa de pagamentos
- ✅ Relatórios profissionais (essenciais para gestão)
- ✅ Facilita contabilidade oficial (IRS, impostos)
- ✅ Histórico preservado (mesmo se reverter projeto)
- ✅ Suporta receitas avulsas (não só projetos)

**Decisões pendentes (a discutir antes de implementar):**
1. **Receita sempre = valor total do projeto?**
   - Ou pode ser parcial? (pagamento faseado: 50% início, 50% fim)
   - Se parcial: permitir múltiplas receitas por projeto?

2. **Receitas avulsas:**
   - Subsídios estatais (ex: COVID, apoios culturais)
   - Vendas de equipamento usado
   - Outras fontes de rendimento não relacionadas com projetos
   - Como gerir? Cliente genérico "Outros"? Sem cliente?

3. **Campos adicionais necessários?**
   - Método de pagamento? (Transferência, MB, Dinheiro)
   - Referência bancária?
   - Fatura emitida? (link para sistema faturação futuro)
   - Notas/observações?

4. **Integração futura:**
   - Sistema de faturação (emitir faturas automáticas)
   - Contabilidade oficial (exportar para TOC)
   - Reconciliação bancária (import extratos)

**Status:** Documentado, aguarda priorização e refinamento de requisitos

**Ver:** 
- TODO.md (tarefa de implementação)
- BUSINESS_LOGIC.md Secção 3.4 (impacto financeiro de projetos PAGO)
- DATABASE_SCHEMA.md (estrutura proposta)

---

## 🔗 Autocomplete: Padrão Unificado (Cliente/Fornecedor/Equipamento/Projeto)

### Dropdown Simples vs Autocomplete com "Criar Novo"
**Decisão:** Autocomplete com "➕ Criar Novo" em todos os campos de relação  
**Data:** 2025-11-15  
**Motivação:**
- Workflow frequentemente interrompido ao precisar criar entidade nova
- Utilizador sai do formulário → perde contexto → frustrante
- Padrão consistente melhora UX drasticamente

**Problema atual:**
```
Utilizador está a criar orçamento
→ Campo Cliente: precisa selecionar cliente
→ Cliente não existe na lista
→ Tem que:
   1. Cancelar orçamento (ou deixar a meio)
   2. Ir ao screen Clientes
   3. Criar cliente novo
   4. Voltar a Orçamentos
   5. Começar de novo (perdeu preenchimento)
→ Frustrante! ❌
```

**Solução:**
```
Utilizador está a criar orçamento
→ Campo Cliente: começa a escrever "Euro..."
→ Filtragem em tempo real mostra resultados
→ Não encontra? Clica "➕ Criar Novo Cliente"
→ Abre dialog inline (modal pequeno)
→ Cria cliente rapidamente
→ Dialog fecha, cliente novo auto-selecionado
→ Continua orçamento sem perder contexto
→ Feliz! ✅
```

**Implementação:**
Componente reutilizável `AutocompleteWithCreate` (custom widget)

```python
class AutocompleteWithCreate(CTkFrame):
    def __init__(self, parent, entity_type, on_create_callback):
        """
        entity_type: 'cliente' | 'fornecedor' | 'equipamento' | 'projeto'
        on_create_callback: função que abre dialog de criação
        """
        self.entry = CTkEntry(...)  # Campo de texto
        self.dropdown = CTkScrollableFrame(...)  # Lista de resultados
        
    def filter_results(self, text):
        """Filtra entidades em tempo real"""
        if entity_type == 'cliente':
            results = query_clientes(nome__contains=text)
        # ... etc
        
        # Sempre adicionar opção "Criar Novo"
        results.append({"id": None, "text": "➕ Criar Novo Cliente"})
        
    def on_select(self, item):
        if item.id is None:  # "Criar Novo"
            new_entity = self.on_create_callback()
            self.set_value(new_entity)  # Auto-seleciona
```

**Aplicar em:**

1. **Orçamentos:**
   - Cliente: busca por nome, NIF → "➕ Criar Novo Cliente"
   - Fornecedor (repartições): busca nome, estatuto → "➕ Criar Novo Fornecedor"
   - Equipamento (repartições): busca produto, tipo → "➕ Criar Novo Equipamento"

2. **Projetos:**
   - Cliente: (mesmo que orçamentos)

3. **Despesas:**
   - Fornecedor: (mesmo que orçamentos)
   - Projeto: busca código, cliente, descrição → "➕ Criar Novo Projeto"

4. **Boletins (linhas):**
   - Projeto: (mesmo que despesas)

5. **Equipamento:**
   - Fornecedor: (mesmo que orçamentos)

**Busca inteligente:**
```python
# Cliente: busca em múltiplos campos
query_clientes(
    OR(
        nome__icontains=text,
        nif__contains=text,
        email__icontains=text
    )
)

# Fornecedor: busca nome, área, função
query_fornecedores(
    OR(
        nome__icontains=text,
        area__icontains=text,
        funcao__icontains=text
    )
)

# Equipamento: busca produto, tipo
query_equipamento(
    OR(
        produto__icontains=text,
        tipo__icontains=text
    )
)

# Projeto: busca código, cliente
query_projetos(
    OR(
        codigo__icontains=text,
        cliente__nome__icontains=text
    )
)
```

**Trade-offs:**
- ❌ Componente custom mais complexo (~200-300 linhas)
- ❌ Precisa manutenção (bugs, edge cases)
- ✅ UX muito superior (fluidez, sem interrupções)
- ✅ Reduz drasticamente número de cliques
- ✅ Padrão consistente em toda app (aprendizagem única)
- ✅ Escalável: fácil adicionar em novos formulários

**Comportamento esperado:**
- Typing → filtra em tempo real (debounce 300ms)
- Enter → seleciona primeiro resultado
- ↑↓ → navega resultados com teclado
- Esc → fecha dropdown
- Click fora → fecha dropdown
- "Criar Novo" sempre visível (no fim da lista ou fixo)
- Após criar → auto-seleciona e fecha dialog

**Acessibilidade:**
- Navegação por teclado completa
- Screen reader friendly (ARIA labels)
- Feedback visual claro (item selecionado)

---

_Última atualização: 15/11/2025_
