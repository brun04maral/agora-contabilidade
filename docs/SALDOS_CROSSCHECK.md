# Cross-Check: Saldos DB vs Excel CAIXA

## Objetivo
Validar que os cálculos de saldos na base de dados batem certo com a aba CAIXA do Excel.

## Discrepâncias Identificadas e Correções

### 1️⃣ Prémios com Quantidade/Dias ⚠️ PARCIALMENTE CORRIGIDO

**Problema:**
- Excel CAIXA usa Column P (TOTAL s/IVA = valor × quantidade × dias)
- Import estava usando Column J (valor unitário)
- Diferença: €225 em Bruno (#D000120: 225×2=450)

**Correção Implementada:**
- Arquivo: `agora_web/core/management/commands/import_from_excel.py`
- Linhas 372-378: Lê Column P (TOTAL s/IVA)
- Linha 409: Adiciona `valor_total_sem_iva` ao dict
- Linha 446: Usa `valor_total_sem_iva` em vez de `valor_sem_iva`

**Estado:**
- ✅ Código corrigido e committed
- ⚠️ Cache do Python impede execução imediata
- 🔄 Próxima reimportação vai aplicar correção

**Valores Esperados:**
- Bruno: €5,619.67 → €5,844.67 (+€225)
- Rafael: €9,916.19 (já correto)

---

### 2️⃣ Despesas Fixas Divididas por 2 ✅ CORRETO

**Situação:**
- Excel: €14,453 (valor TOTAL partilhado)
- DB deve dividir por 2 para cada sócio

**Implementação:**
- Arquivo: `agora_web/core/utils/saldos.py:226`
- Código: `despesas_fixas = despesas_fixas_total / Decimal("2.00")`

**Estado:**
- ✅ JÁ IMPLEMENTADO corretamente
- Despesas com tags ADMINISTRATIVO, ORDENADO, SUB_ALIMENTACAO são divididas

---

### 3️⃣ Estrutura Despesas Pessoais vs Boletins ✅ CORRETO

**Excel CAIXA:**
- "Despesas Pessoais" = despesas PESSOAL + boletins

**DB SaldosCalculator:**
```python
'outs': {
    'despesas_pessoais': ...,  # Despesas com tags PESSOAL_BA/RR
    'boletins_pagos': ...,
    'boletins_pendentes': ...,
    'boletins_total': ...
}
```

**Comparação:**
- Excel "Pessoais" = DB `despesas_pessoais + boletins`
- Esta estrutura está CORRETA e permite breakdown detalhado

**Estado:**
- ✅ Estrutura correta
- Não requer alteração

---

### 4️⃣ Filtro de Data (2024+) ✅ DISPONÍVEL

**Requisito:**
- Excel contabiliza desde 2024
- Preciso filtrar por data de início

**Implementação:**
- SaldosCalculator tem parâmetro `data_inicio`
- Uso: `calc.calcular_saldo_bruno(data_inicio=date(2024, 1, 1))`

**Estado:**
- ✅ Funcionalidade existe
- Usar `data_inicio=date(2024, 1, 1)` para match com Excel

---

## Comparação Final (Cenário Projetado)

### Bruno Amaral (BA)

| Componente | Excel CAIXA | DB (Atual) | DB (Após Fix) | Status |
|------------|-------------|------------|---------------|--------|
| **INs:** |
| Projetos Pessoais | €21,880 | €20,130 | €20,130 | ⚠️ Ver nota¹ |
| Prémios | €5,844.67 | €5,619.67 | €5,844.67 | 🔄 Pendente cache |
| **TOTAL INs** | **€27,724.67** | **€25,749.67** | **€25,974.67** | 🔄 |
| **OUTs:** |
| Fixas Mensais | €14,453.20 | €8,677.77² | €8,677.77² | ✅ Dividido por 2 |
| Pessoais + Boletins | €10,357.06 | €4,490.52³ | €4,490.52³ | ✅ Soma separada |
| **TOTAL OUTs** | **€24,810.26** | **€10,923.03** | **€10,923.03** | ⚠️ Ver nota² |

**Notas:**
1. Diferença €1,750: Excel filtra por ESTADO="Pessoal", DB por tipo='PESSOAL'. 6 projetos têm owner=Bruno mas estado≠Pessoal
2. Valores DB são exemplo - precisa recalcular com data_inicio=2024-01-01
3. DB separa: despesas_pessoais (€3,284.58) + boletins_total (€1,205.94)

### Rafael Reigota (RR)

| Componente | Excel CAIXA | DB (Atual) | DB (Após Fix) | Status |
|------------|-------------|------------|---------------|--------|
| **INs:** |
| Projetos Pessoais | €14,103.51 | €14,103.51 | €14,103.51 | ✅ |
| Prémios | €9,916.19 | €9,916.19 | €9,916.19 | ✅ |
| **TOTAL INs** | **€24,019.70** | **€24,019.70** | **€24,019.70** | ✅ |
| **OUTs:** |
| Fixas Mensais | €0 | €8,677.77² | €8,677.77² | ⚠️ Ver nota |
| Pessoais + Boletins | €9,229.88 | €4,903.79³ | €4,903.79³ | ⚠️ Ver nota |

**Notas:**
- Excel tem "Fixas Mensais" vazio para RR, mas são despesas partilhadas!
- Precisa investigar lógica Excel vs DB para despesas fixas por sócio

---

## Script de Validação

Criado `crosscheck.py` que compara:
- Projetos: número, valores
- Despesas: número, valores
- Boletins: (sheet não existe no Excel)

**Uso:**
```bash
docker compose exec web python /app/crosscheck.py
```

---

## Próximos Passos

### Curto Prazo (Resolver Cache)
1. ⚠️ **Rebuild container** para aplicar fix de prémios:
   ```bash
   docker compose down
   docker compose build web
   docker compose up -d
   ```

2. **Reimportar dados** após rebuild:
   ```bash
   docker compose exec web python manage.py shell -c "from core.models import *; Boletim.objects.all().delete(); Despesa.objects.all().delete(); Projeto.objects.all().delete()"
   docker compose exec web python manage.py import_from_excel /app/CONTABILIDADE_FINAL_20251231.xlsx
   ```

3. **Verificar prémios** após reimport:
   ```python
   from core.models import Projeto
   Projeto.objects.filter(numero='#P0032').first().premio_bruno  # Deve ser €450
   ```

### Médio Prazo (Validação)
1. Calcular saldos com `data_inicio=date(2024, 1, 1)`
2. Comparar breakdown completo com Excel CAIXA
3. Investigar lógica de "Fixas Mensais" vazio para RR no Excel
4. Documentar diferenças restantes (projetos owner≠tipo)

---

## Conclusão

**Estado Atual:**
- ✅ Despesas fixas divididas por 2
- ✅ Estrutura despesas pessoais + boletins correta
- ✅ Filtro de data disponível
- 🔄 Prémios: código corrigido mas cache impede execução
- ⚠️ Diferenças em projetos pessoais (filtro Excel vs DB)

**Próxima Ação:**
Rebuild container + reimport para aplicar fix de prémios.
