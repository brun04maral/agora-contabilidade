# 🔄 IMPORTAR SESSÃO ANTERIOR - Claude Code

## ⚠️ CRÍTICO - Ler PRIMEIRO em CADA Nova Sessão!

O Claude Code cria um **novo branch** a cada sessão baseado no `main` (que está desatualizado).
O branch da sessão anterior tem todo o código atualizado.

**ORDEM CORRETA:**
```
1. Fazer merge do branch anterior
2. Ler README.md
3. Ler memory/CURRENT_STATE.md
```

**❌ NUNCA:** Ler docs → Merge (contexto errado!)
**✅ SEMPRE:** Merge → Ler docs (contexto certo!)

---

## ✅ FRASE MÁGICA v2.0 - Copia e Cola
```
IMPORTANTE: Estás num branch novo criado do main (desatualizado). Antes de fazer QUALQUER coisa:

1. Lista todos os branches remotos com 'git branch -r'
2. Identifica o branch da sessão anterior (mais recente, excluindo main)
3. Faz merge desse branch para o branch atual
4. SÓ DEPOIS lê README.md e memory/CURRENT_STATE.md

Não leias documentação antes do merge ou terás contexto desatualizado!
```

---

## 🔄 O Que o Claude Vai Fazer (Ordem Garantida)
```
┌─────────────────────────────────────┐
│ 1. Listar branches remotos          │
│    git branch -r                    │
└────────────┬────────────────────────┘
             │
┌────────────▼────────────────────────┐
│ 2. Identificar branch mais recente  │
│    (ex: claude/feature-xyz-123)     │
└────────────┬────────────────────────┘
             │
┌────────────▼────────────────────────┐
│ 3. Fazer merge                      │
│    git merge origin/claude/...      │
└────────────┬────────────────────────┘
             │
┌────────────▼────────────────────────┐
│ 4. Ler documentação                 │
│    - README.md                      │
│    - memory/CURRENT_STATE.md        │
└─────────────────────────────────────┘
```

---

## 📝 Exemplo Prático do Fluxo
```bash
# Nova sessão inicia automaticamente
# Claude Code cria: claude/nova-feature-20251113-abc123
# Este branch vem do main (desatualizado!)

# ❌ ERRADO (ordem antiga):
# 1. Ler README.md (contexto desatualizado!)
# 2. Fazer merge (tarde demais)

# ✅ CORRETO (ordem nova):
# 1. git branch -r  # Ver branches disponíveis
origin/main
origin/claude/implementar-xyz-20251112-xyz789  ← Mais recente!
origin/claude/fix-bug-20251110-abc456
origin/claude/old-feature-20251109-def123

# 2. Identificar mais recente (excluir main)
BRANCH_ANTERIOR="origin/claude/implementar-xyz-20251112-xyz789"

# 3. Fazer merge
git merge $BRANCH_ANTERIOR

# 4. Agora sim, ler documentação
cat README.md
cat memory/CURRENT_STATE.md
```

---

## 🚨 AVISOS IMPORTANTES

### ❌ NÃO faças isto:
- Ler documentação antes do merge
- Assumir que tens código atualizado
- Começar a trabalhar sem fazer merge

### ✅ SEMPRE faz isto:
1. **Merge primeiro** (git merge origin/...)
2. **Docs depois** (README + CURRENT_STATE)
3. **Trabalhar com contexto completo**

---

## 🎯 Como Identificar o Branch Correto

O branch da sessão anterior é:
- ✅ Começa com `origin/claude/`
- ✅ Tem data recente (ex: 20251112)
- ✅ NÃO é `origin/main`
- ✅ É o mais recente (data maior)

**Exemplo:**
```bash
origin/claude/implementar-xyz-20251112-xyz789  ← ESTE! (mais recente)
origin/claude/fix-bug-20251110-abc456          ← Não (mais antigo)
origin/main                                     ← NUNCA!
```

---

## 💡 Troubleshooting

### "Não vejo branches remotos"
```bash
git fetch origin  # Atualizar lista de branches
git branch -r     # Listar novamente
```

### "Não sei qual é o mais recente"
Procura pela **data maior** no nome do branch:
- `20251113` > `20251112` > `20251110`

### "Conflitos no merge"
```bash
# Aceitar versão do branch anterior (geralmente correto)
git checkout --theirs <ficheiro-conflito>
git add <ficheiro-conflito>
git commit
```

---

## 📚 Documentação Disponível (Após Merge)

- ✅ `README.md` - Overview e instruções
- ✅ `memory/CURRENT_STATE.md` - Estado atual do projeto
- ✅ `memory/TODO.md` - Tarefas pendentes
- ✅ `memory/ARCHITECTURE.md` - Arquitetura técnica
- ✅ `memory/DATABASE_SCHEMA.md` - Estrutura da BD
- ✅ Todo o código atualizado!

---

## ⚡ Frase-Chave para Atualizar Documentação

Quando o utilizador disser:
```
Atualiza a documentação em memory/ com o trabalho feito (CURRENT_STATE, TODO, CHANGELOG e outros relevantes).
```

**Deves avaliar e atualizar:**

### Sempre atualizar:
1. ✅ **CURRENT_STATE.md** - Features completas, problemas resolvidos
2. ✅ **TODO.md** - Mover tarefas para ✅ Concluído Recentemente
3. ✅ **CHANGELOG.md** - Adicionar entrada com data

### Atualizar se aplicável ao trabalho feito:
4. 📐 **ARCHITECTURE.md** - Se mudou estrutura/arquitetura
5. 🎯 **DECISIONS.md** - Se houve decisão técnica importante
6. 🗄️ **DATABASE_SCHEMA.md** - Se alterou models/migrations
7. ⚙️ **DEV_SETUP.md** - Se mudou processo de setup

**O utilizador decide quando esta atualização faz sentido!**

---

**📍 Lembrete Final:**

# MERGE PRIMEIRO, DOCS DEPOIS! 🔄📖

Sem o merge, estás a trabalhar com código e contexto desatualizados.