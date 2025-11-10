# 🔄 IMPORTAR SESSÃO ANTERIOR - Claude Code

## ⚠️ IMPORTANTE - Ler PRIMEIRO em CADA Nova Sessão!

O Claude Code cria um **novo branch** a cada sessão e **NÃO importa automaticamente** o contexto da sessão anterior.

---

## ✅ O QUE FAZER SEMPRE

### Passo 1: Importar Sessão Anterior

Copia e cola esta frase **EXATAMENTE** na nova sessão:

```
Esta sessão é continuação de uma anterior. Importa a sessão anterior para teres contexto completo do que foi feito.
```

### Passo 2: Aguardar Importação

O Claude Code vai:
1. ✅ Mostrar lista de sessões anteriores disponíveis
2. ✅ Importar a sessão mais recente (ou a que escolheres)
3. ✅ Ter contexto completo de todas as alterações

### Passo 3: Continuar Trabalho

Agora podes continuar normalmente! O Claude tem todo o contexto:
- ✅ Código alterado nas sessões anteriores
- ✅ Decisões tomadas
- ✅ Problemas resolvidos
- ✅ Próximos passos

---

## 📖 Contexto Adicional (Se Necessário)

Se a sessão anterior não tiver informação suficiente, ou se quiseres refresh de contexto geral do projeto:

```
Lê memory/CURRENT_STATE.md e memory/TODO.md para contexto completo do projeto
```

---

## 🚨 NÃO FAÇAS ISTO

❌ **NÃO** inicies nova sessão sem importar contexto anterior
❌ **NÃO** assumes que o Claude sabe o que foi feito antes
❌ **NÃO** expliques tudo manualmente (usa importação!)

---

## 💡 Dica: Atalho Rápido

Marca esta frase como favorito no teu editor:

```
Esta sessão é continuação de uma anterior. Importa a sessão anterior para teres contexto completo do que foi feito.
```

---

## 🔄 No Final da Sessão: Merge para Main

**IMPORTANTE:** Quando terminares uma sessão de trabalho, **SEMPRE** faz merge do branch para main:

```bash
# 1. Commit todas as alterações
git add -A
git commit -m "mensagem descritiva"

# 2. Muda para main
git checkout main

# 3. Faz merge do branch da sessão
git merge nome-do-branch-da-sessao

# 4. Push para main
git push origin main
```

**Porquê?**
- ✅ Próximas sessões começam do main atualizado
- ✅ Têm acesso a estas instruções e todo o código novo
- ✅ Evita branches desatualizados
- ✅ Documentação sempre acessível

---

**📍 Lembrete:** Este ficheiro existe para te poupar tempo! Usa-o sempre.
