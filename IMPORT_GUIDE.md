# 📥 Guia de Importação Incremental - Excel

Script otimizado para importar dados do Excel mantendo a DB local intacta.

---

## 🎯 Workflow

1. **Manter DB de testes** - Dados existentes não são tocados
2. **Importar novos dados** - Só adiciona o que não existe
3. **Preservar modificações** - Alterações locais mantêm-se
4. **Update inteligente** - Prémios de projetos podem ser atualizados

---

## 🚀 Como Usar

### 1️⃣ **Preview (Dry Run)** - Recomendado

Vê o que seria importado **SEM GRAVAR NADA**:

```bash
python scripts/import_from_excel.py --dry-run
```

**Output:**
```
📊 IMPORTAÇÃO INCREMENTAL DO EXCEL - 🔍 DRY RUN (preview)
...
CLIENTES:
  ✅ Novos: 3           # Seriam criados
  ⏭️  Skip: 16          # Já existem
  ❌ Erros: 0

PROJETOS:
  ✅ Novos: 8
  ⏭️  Skip: 67
  🔄 Atualizados: 2     # Prémios atualizados
```

### 2️⃣ **Importar Novos Dados**

Se preview estiver OK, executar sem `--dry-run`:

```bash
python scripts/import_from_excel.py
```

Isto vai:
- ✅ Criar registos novos
- ⏭️  Ignorar registos existentes
- 🔄 Atualizar prémios de projetos (se mudaram)
- 💾 Gravar na DB

### 3️⃣ **Ficheiro Excel Custom**

Especificar caminho diferente:

```bash
python scripts/import_from_excel.py --excel excel/MEU_FICHEIRO.xlsx
```

### 4️⃣ **Limpar e Re-importar** ⚠️

**CUIDADO:** Apaga tudo e importa do zero:

```bash
python scripts/import_from_excel.py --clear-all
```

Vai pedir confirmação:
```
⚠️  ATENÇÃO: Todos os dados serão apagados!
Tem certeza? (sim/não):
```

---

## 🔍 Como Funciona o Matching

O script identifica registos existentes pelo **número do Excel**:

| Entidade | Chave Primária | Exemplo |
|----------|----------------|---------|
| **Clientes** | Número | `#C001`, `#C002` |
| **Fornecedores** | Número | `#F001`, `#F002` |
| **Projetos** | Número | `#P001`, `#P002` |
| **Despesas** | Número | `#D001`, `#D002` |
| **Boletins** | Sócio + Data + Valor | `BRUNO, 2024-01-15, €500` |

### Exemplos:

```bash
# Cliente #C001 já existe na DB
  ⏭️  #C001: Cliente X (já existe)  # SKIP

# Cliente #C020 não existe na DB
  ✅ #C020: Cliente Y (criado)        # INSERT

# Projeto #P005 existe mas prémios mudaram
  🔄 #P005: Bruno: €500 | Rafael: €200 (atualizado)  # UPDATE prémios
```

---

## 📊 Output Detalhado

Durante importação vês:

```bash
================================================================================
📋 IMPORTANDO CLIENTES (modo incremental)
================================================================================
Total de clientes no Excel: 19

  ⏭️  #C001: Cliente A (já existe)
  ⏭️  #C002: Cliente B (já existe)
  ✅ #C019: Cliente Novo (criado)
  ❌ #C020: Cliente Erro - NIF inválido

📊 CLIENTES:
   ✅ Novos: 1
   ⏭️  Skip: 17
   ❌ Erros: 1
   📋 Total processado: 19
```

**Ícones:**
- `✅` - Criado com sucesso
- `⏭️` - Já existe (skip)
- `🔄` - Atualizado
- `❌` - Erro
- `🔍` - Dry run (seria criado)

---

## ⚙️ Opções Avançadas

### Combinar Flags

```bash
# Preview de importação com ficheiro custom
python scripts/import_from_excel.py --dry-run --excel dados_novos.xlsx

# Limpar e importar (com confirmação)
python scripts/import_from_excel.py --clear-all
```

### Variáveis de Ambiente

O script usa `DATABASE_URL` do `.env`:

```bash
# .env
DATABASE_URL=sqlite:///./agora_media.db
```

---

## 🐛 Troubleshooting

### Erro: "Excel não encontrado"

```
❌ Erro ao abrir Excel: No such file or directory
```

**Solução:** Verificar caminho do ficheiro:
```bash
ls -la excel/CONTABILIDADE_FINAL_20251108.xlsx
```

### Muitos registos "skip"

Isto é **normal e esperado**! Se já fizeste importação antes:
```
📊 CLIENTES:
   ✅ Novos: 0
   ⏭️  Skip: 19      # Todos já existiam!
```

Significa que a DB já tem tudo.

### Prémios não atualizados

Prémios **só** são atualizados se:
1. Projeto já existe na DB
2. Valor do prémio mudou no Excel
3. Não é dry run

---

## 💡 Dicas

### 1. Sempre usar `--dry-run` primeiro

```bash
# 1. Preview
python scripts/import_from_excel.py --dry-run

# 2. Se OK, executar para real
python scripts/import_from_excel.py
```

### 2. Verificar resumo final

No fim da importação:
```
📊 RESUMO FINAL DA IMPORTAÇÃO

CLIENTES:
  ✅ Novos: 3
  ⏭️  Skip: 16

PROJETOS:
  ✅ Novos: 8
  ⏭️  Skip: 67
  🔄 Atualizados: 2

...

✅ IMPORTAÇÃO INCREMENTAL CONCLUÍDA!
```

### 3. Backup antes de `--clear-all`

Se vais limpar tudo:
```bash
# Fazer backup da DB
cp agora_media.db agora_media.db.backup

# Limpar e importar
python scripts/import_from_excel.py --clear-all

# Se algo correu mal, restaurar
mv agora_media.db.backup agora_media.db
```

---

## 🎓 Exemplos Práticos

### Cenário 1: Primeiro uso (DB vazia)

```bash
python scripts/import_from_excel.py --dry-run
# Vê: "Novos: 19, 44, 75, 162, 34"

python scripts/import_from_excel.py
# Importa tudo
```

### Cenário 2: Já tenho dados, Excel atualizado

```bash
python scripts/import_from_excel.py --dry-run
# Vê: "Novos: 2, 3, 5, 8, 1" (só o que é novo)

python scripts/import_from_excel.py
# Importa só os novos
```

### Cenário 3: Alterei dados na app, Excel tem updates

```bash
python scripts/import_from_excel.py
# Skip automático dos existentes
# Tuas alterações mantêm-se intactas ✅
```

### Cenário 4: Excel tem novos prémios

```bash
python scripts/import_from_excel.py
# Projetos existentes → Skip
# Mas prémios são atualizados se mudaram 🔄
```

---

## 📝 Notas Importantes

1. **Números do Excel são fixos** - Usados como chave primária
2. **Skip preserva dados** - Alterações locais nunca são sobrescritas
3. **Prémios são exceção** - Podem ser atualizados mesmo em projetos existentes
4. **Dry run é seguro** - Podes executar quantas vezes quiseres
5. **Rollback automático** - Se algo falhar, nada é gravado

---

## ✅ Checklist de Importação

Antes de importar:
- [ ] Ficheiro Excel está na pasta `excel/`
- [ ] Executei `--dry-run` para preview
- [ ] Verifiquei estatísticas (Novos/Skip/Erros)
- [ ] Se usar `--clear-all`, fiz backup da DB

Após importação:
- [ ] Verifiquei resumo final
- [ ] Sem erros críticos
- [ ] Abri app e verifiquei dados: `python main.py`
- [ ] Saldos calculados corretamente

---

**Script:** `scripts/import_from_excel.py`
**Excel default:** `excel/CONTABILIDADE_FINAL_20251108.xlsx`
**DB:** `agora_media.db`

**Dúvidas?** Ver código do script - está bem documentado!
