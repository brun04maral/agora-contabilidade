# 🧠 Memory - Sistema de Contexto para Desenvolvimento

Esta pasta contém toda a **memória do projeto** - documentação de referência para desenvolvimento que permite continuar o trabalho em qualquer sessão.

## 📁 Estrutura

### 📋 Estado Atual
- **`CURRENT_STATE.md`** - Estado atual do projeto (features implementadas, próximos passos)
- **`TODO.md`** - Lista de tarefas organizadas por prioridade

### 🏗️ Arquitetura & Decisões
- **`ARCHITECTURE.md`** - Visão geral da arquitetura da aplicação
- **`DECISIONS.md`** - Decisões técnicas importantes e motivações
- **`DATABASE_SCHEMA.md`** - Estrutura da base de dados

### 📚 Guias de Desenvolvimento
- **`GUIA_COMPLETO.md`** - Guia completo do sistema
- **`PLANO_ORCAMENTOS.md`** - Plano específico para funcionalidade de orçamentos
- **`ASSET_SYSTEM.md`** - Como funciona o sistema de assets (logos, ícones)

### 📝 Histórico
- **`CHANGELOG.md`** - Registo de mudanças importantes

### ⚙️ Setup & Deploy
- **`DEV_SETUP.md`** - Como configurar ambiente de desenvolvimento

## 🎯 Como Usar

### Iniciar Nova Sessão
1. Ler `CURRENT_STATE.md` - perceber onde estamos
2. Ler `TODO.md` - ver próximas tarefas
3. Consultar `ARCHITECTURE.md` se necessário - entender estrutura

### Durante Desenvolvimento
- Consultar guias específicos conforme necessário
- Quando completares trabalho importante, usa a **frase-chave** para atualizar docs

### Fim de Sessão
- Usa a **frase-chave** para atualizar documentação

---

## ⚡ Frase-Chave para Atualizar Documentação

Quando quiseres que o Claude atualize a documentação do projeto, usa:
```
Atualiza CURRENT_STATE, TODO e CHANGELOG com o trabalho feito.
```

**O Claude vai:**
1. ✅ Atualizar `memory/CURRENT_STATE.md` - Adicionar features completas
2. ✅ Atualizar `memory/TODO.md` - Mover tarefas para ✅ Concluído
3. ✅ Atualizar `memory/CHANGELOG.md` - Adicionar entrada com data

**Quando usar:**
- Após completar feature importante
- No fim de sessão produtiva
- Quando fizeres mudanças significativas
- **Tu decides quando faz sentido!**

### Variações Úteis
```bash
# Atualização completa (padrão)
"Atualiza CURRENT_STATE, TODO e CHANGELOG com o trabalho feito."

# Só marcar tarefa concluída
"Marca esta tarefa como concluída no TODO."

# Registar decisão técnica
"Documenta esta decisão no DECISIONS.md"

# Resumo rápido de sessão
"Quick doc update - resume o que fizemos hoje."
```

---

## 💡 Filosofia

> **"Context is King"** - Cada ficheiro aqui existe para dar contexto rápido e completo, permitindo retomar desenvolvimento em segundos, não horas.

> **"Tu controlas quando documentar"** - Usa a frase-chave quando fizer sentido para ti.

---

**Mantido por:** Equipa de desenvolvimento Agora Media
**Última atualização:** 2025-11-13