# 🔄 IMPORTAR SESSÃO ANTERIOR - Claude Code

## ⚠️ IMPORTANTE - Ler PRIMEIRO em CADA Nova Sessão!

O Claude Code cria um **novo branch** a cada sessão baseado no `main` (que pode estar desatualizado).
A sessão anterior tem todo o código novo, mas está num branch diferente.

**Solução:** Fazer merge do branch da sessão anterior para este novo branch.

---

## ✅ FRASE MÁGICA - Copia e Cola

Quando iniciares uma nova sessão, **SEMPRE** usa esta frase:

```
Esta sessão é continuação de uma anterior. Faz merge do branch da última sessão para este branch atual para teres todo o código e contexto atualizado. Depois lê o README.md e memory/CURRENT_STATE.md para contexto completo.
```

---

## 📝 O Que o Claude Vai Fazer

1. ✅ **Identificar** o branch da sessão anterior (mais recente)
2. ✅ **Fazer merge** desse branch para o branch atual
3. ✅ **Ler** README.md e documentação em `/memory/`
4. ✅ **Ter contexto completo** de todo o código e decisões

---

## 🔄 Fluxo Completo

```
Nova Sessão → Branch novo criado do main (desatualizado)
     ↓
Frase Mágica → Merge branch anterior + Ler docs
     ↓
Trabalhar → Código atualizado + Contexto completo
```

---

## 🚨 NÃO FAÇAS ISTO

❌ **NÃO** inicies nova sessão sem fazer merge do branch anterior
❌ **NÃO** assumes que tens o código mais recente (o main está desatualizado!)
❌ **NÃO** expliques tudo manualmente ao Claude

---

## 💡 Exemplo Prático

```bash
# O Claude vai fazer isto automaticamente quando usares a frase mágica:

# 1. Ver branches disponíveis
git branch -a

# 2. Identificar o branch mais recente (ex: claude/import-excel-20251108-*)
git fetch origin

# 3. Fazer merge do branch anterior
git merge origin/nome-do-branch-anterior

# 4. Ler documentação
# README.md → Instruções gerais
# memory/CURRENT_STATE.md → Estado atual do projeto
# memory/TODO.md → Próximos passos
```

---

## 📚 Documentação Disponível

Após o merge, o Claude terá acesso a:
- ✅ `README.md` - Overview e setup
- ✅ `memory/CURRENT_STATE.md` - Features e estado atual
- ✅ `memory/TODO.md` - Tarefas pendentes
- ✅ `memory/ARCHITECTURE.md` - Arquitetura técnica
- ✅ `memory/DATABASE_SCHEMA.md` - Estrutura da BD
- ✅ Todo o código atualizado das sessões anteriores

---

**📍 Lembrete:** Guarda a frase mágica! Usa-a em TODAS as novas sessões.
