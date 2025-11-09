# 🔴 PROBLEMA ENCONTRADO: Despesas Fixas Incorretas

## Resumo do Problema

**Tens razão!** Os valores das despesas fixas na base de dados **NÃO batem** com o Excel.

### Números

| Métrica | Excel | Base de Dados | Diferença |
|---------|-------|---------------|-----------|
| **Quantidade PAGAS** | 36 | 40 | **+4** ❌ |
| **Valor Total** | €7,826.01 | €7,939.66 | **+€113.65** ❌ |
| **Por sócio (÷2)** | €3,913.01 | €3,969.83 | **+€56.82** ❌ |

### Impacto nos Saldos

Cada sócio está a descontar **€56.82 a mais** do que deveria!

- Bruno: €295.28 (atual) → **€352.10** (correto) = **+€56.82** 💰
- Rafael: €17.09 (atual) → **€73.91** (correto) = **+€56.82** 💰

## Causa do Problema

A importação está a marcar **31 despesas como FIXA_MENSAL** quando não deveriam ser:

### Exemplos de Despesas Incorretas

| Número | Descrição | Valor | Excel Periodicidade | Excel Tipo | DB Tipo |
|--------|-----------|-------|---------------------|------------|---------|
| #D000019 | Contabilidade empresa | €209.10 | **Único** ❌ | Produção | FIXA_MENSAL |
| #D000020 | Manutenção conta | €8.31 | **Único** ❌ | Administrativo | FIXA_MENSAL |
| #D000029 | TSU NOV | €417.00 | Mensal | **Sub. Alimentação** ❌ | FIXA_MENSAL |
| #D000030 | Contabilidade empresa | €209.10 | **Único** ❌ | Administrativo | FIXA_MENSAL |
| #D000046 | TSU JAN | €417.00 | **Único** ❌ | Deslocação, Pessoal | FIXA_MENSAL |
| #D000054 | Contabilidade empresa | €209.10 | Mensal | **Ordenado** ❌ | FIXA_MENSAL |
| #D000059 | Almoço RR + BA | €29.10 | **Único** ❌ | Deslocação, Pessoal | FIXA_MENSAL |
| #D000060 | Almoço Agora | €46.95 | **Único** ❌ | Per Diem PT, Pessoal | FIXA_MENSAL |

**Total: 31 despesas incorretas = €5,419.84**

### Problemas Identificados

1. **Despesas com periodicidade "Único"** estão a ser marcadas como FIXA_MENSAL
2. **Despesas tipo "Ordenado/Sub. Alimentação"** estão como FIXA_MENSAL (deveriam ser PESSOAL_*)
3. **26 despesas** que deveriam estar na DB não estão

## Solução Necessária

### Opção 1: Corrigir o Bug e Re-importar

1. Identificar e corrigir o bug na lógica de import_from_excel.py
2. Limpar a base de dados
3. Re-importar do Excel

### Opção 2: Refatoração Arquitetural

Aproveitar este momento para implementar a refatoração que sugeriste:

- Criar modelo **"Movimento"** unificado
- Usar **categorias** em vez de tipos separados
- Simplificar lógica de cálculo de saldos
- Reduzir redundância de código

## Próximos Passos

Qual preferes?

A. **Corrigir o bug atual** e re-importar (mais rápido, mantém arquitetura)
B. **Refatoração completa** com novo modelo Movimento (mais demorado, melhor a longo prazo)
C. **Híbrido**: Corrigir bug primeiro, refatorar depois

---

**Nota**: Este problema explica por que os saldos não batiam certo. A correção vai adicionar €56.82 ao saldo de cada sócio.
