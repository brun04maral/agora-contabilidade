# Análise da Aba CAIXA - Lógica de Saldos Pessoais

**Data:** 03 Janeiro 2026
**Fonte:** CONTABILIDADE_FINAL_20251231.xlsx

---

## 📊 Estrutura da Aba

A aba CAIXA contém o cálculo de saldos pessoais dos sócios.

### Headers (Linha 2)

- **B**: SÓCIO
- **C**: INs
- **H**: OUTs
- **L**: SALDO PESSOAL
(com investimento + salários em atraso)
- **M**: SALDO PESSOAL
(sem idem)
- **N**: €14 500
2024/2025

### Linhas de Dados

| Linha | Sócio | Descrição |
|-------|-------|-----------|
| 4 | BA | Bruno Amaral |
| 5 | RR | Rafael Reigota |

---

## 💡 Fórmulas Principais

### INs (Entradas - Empresa DEVE ao sócio)

#### Investimento Inicial (C4)

**Valor (BA):** €5,200.00


#### Prémios (pagos) (D4)

**Valor (BA):** €666.00


```excel
=IFERROR(__xludf.DUMMYFUNCTION("IFERROR(SUM(FILTER(DESPESAS!$P$6:$P1002,
            DESPESAS!$E$6:$E1002=""Bruno Amaral"",
            REGEXMATCH(DESPESAS!$G$6:$G1002, ""Ordenado|Sub. Alimentação""),
            DATE(DESPESAS!$B$6:$B1002, DESPESAS!$C$6:$C1002, DESPESAS!$D$6:$D1002)<=TO"&"DAY(),
            DESPESAS!$T$6:$T1002="""")),
0)
"),666.0)
```

#### Projetos Pessoais (pagos) (E4)

**Valor (BA):** €21,880.00

**Lógica:** Soma projetos pessoais PAGOS

```excel
=SUMIFS(PROJETOS!F4:F1002, PROJETOS!O4:O1002, "pessoal", PROJETOS!P4:P1002, "Bruno Amaral", PROJETOS!H4:H1002, ">0")
```

#### Prémios não faturados (F4)

**Valor (BA):** €5,844.67

**Lógica:** Filtra e soma prémios pagos

```excel
=IFERROR(__xludf.DUMMYFUNCTION("SUM(FILTER(DESPESAS!$P$6:$P1002, REGEXMATCH(DESPESAS!$G$6:$G1002, ""Prémio|Comissão venda""), DESPESAS!$E$6:$E1002=""Bruno Amaral""))
"),5844.67)
```

#### TOTAL INs (G4)

**Valor (BA):** €33,590.67

**Fórmula:** Valor fixo

### OUTs (Saídas - Empresa PAGOU ao sócio)

#### Despesas Fixas Mensais (H4)

**Valor (BA):** €13,911.70

**Lógica:** Soma despesas fixas mensais ÷ 2

```excel
=SUMIFS(DESPESAS!$P$6:$P1002, 
        DESPESAS!$I$6:$I1002, "Mensal",  
        DESPESAS!$T$6:$T1002, "<>"&"") / 2
```

#### Boletins (ajudas de custo) (I4)

**Valor (BA):** €1,826.49


```excel
=IFERROR(__xludf.DUMMYFUNCTION("IFERROR(
  SUM(
    FILTER(
      DESPESAS!$P$6:$P1002,
      REGEXMATCH(DESPESAS!$U$6:$U1002, ""Bruno Amaral""),
      REGEXMATCH(DESPESAS!$G$6:$G1002, ""Pessoal""),
      NOT(ISBLANK(DESPESAS!$T$6:$T1002)),
      DESPESAS!$T$6:$T1002 <= TODAY()
    )
  "&"),
  0
)
"),1826.4853)
```

#### Despesas Pessoais (J4)

**Valor (BA):** €8,530.57


```excel
=IFERROR(__xludf.DUMMYFUNCTION("SUM(FILTER(DESPESAS!$P$6:$P1002, REGEXMATCH(DESPESAS!$G$6:$G1002, ""Deslocação, Pessoal|Per Diem PT, Pessoal|Per Diem FORA, Pessoal""), DESPESAS!$E$6:$E1002=""Bruno Amaral"", DESPESAS!$T$6:$T1002=""""))"),8530.57)
```

---

## 🔍 Comparação com SaldosCalculator

O comando de gestão Django permite validar se os cálculos implementados no sistema correspondem às fórmulas Excel:

```bash
python manage.py analisar_caixa
```

### Resultados da Validação

A implementação em [agora_web/core/utils/saldos.py](../agora_web/core/utils/saldos.py) replica fielmente a lógica Excel:

**Componentes Validados:**
- ✅ **INs (Entradas):**
  - Investimento inicial (valor fixo por sócio)
  - Prémios pagos (filtro de despesas tipo "Ordenado|Sub. Alimentação")
  - Projetos pessoais pagos (SUMIFS em projetos)
  - Prémios não faturados (filtro de "Prémio|Comissão venda")

- ✅ **OUTs (Saídas):**
  - Despesas fixas mensais divididas por 2 sócios
  - Boletins (ajudas de custo pessoais)
  - Despesas pessoais (deslocações, per diems)

- ✅ **Cálculo do Saldo:**
  - Com investimento + salários em atraso
  - Sem investimento + salários em atraso

### Diferenças Identificadas

**Nenhuma diferença significativa** entre cálculo Excel e Django. Pequenas discrepâncias de arredondamento (<€0.01) são esperadas devido a diferenças de precisão numérica.

### Documentação Relacionada

Para detalhes sobre a implementação do dashboard de saldos, consultar:
- [SALDOS_DASHBOARD.md](./SALDOS_DASHBOARD.md) - Implementação completa do dashboard
- [SALDOS_CROSSCHECK.md](./SALDOS_CROSSCHECK.md) - Validação cruzada Excel vs DB
- [SALDOS_VALIDATION_RESULTS.md](./SALDOS_VALIDATION_RESULTS.md) - Resultados detalhados

---

## 📋 Conclusão

A aba CAIXA do Excel implementa uma lógica de saldos pessoais baseada em:
1. **Entradas** (INs): O que a empresa deve ao sócio
2. **Saídas** (OUTs): O que a empresa já pagou ao sócio
3. **Saldo**: Diferença entre INs e OUTs

Esta lógica foi **replicada com sucesso** no sistema Django através do `SaldosCalculator`, permitindo cálculo dinâmico e em tempo real dos saldos pessoais de cada sócio.

---

**Last Updated:** 2026-01-03
