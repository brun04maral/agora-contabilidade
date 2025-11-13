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
Atualiza a documentação em memory/ com o trabalho feito (CURRENT_STATE, TODO, CHANGELOG e outros relevantes).
```

**O Claude vai avaliar e atualizar:**

### Sempre atualizar:
1. ✅ **CURRENT_STATE.md** - Adicionar features completas, problemas resolvidos
2. ✅ **TODO.md** - Mover tarefas para ✅ Concluído Recentemente
3. ✅ **CHANGELOG.md** - Adicionar entrada com data e descrição

### Atualizar se aplicável ao trabalho feito:
4. 📐 **ARCHITECTURE.md** - Se mudaste estrutura do código, pastas, ou arquitetura
5. 🎯 **DECISIONS.md** - Se tomaste decisão técnica importante (porquê X e não Y)
6. 🗄️ **DATABASE_SCHEMA.md** - Se criaste/alteraste models, migrations ou schema
7. ⚙️ **DEV_SETUP.md** - Se mudaste processo de instalação ou configuração

**Quando usar:**
- Após completar feature importante
- No fim de sessão produtiva
- Quando fizeres mudanças significativas
- **Tu decides quando faz sentido!**

### Variações Úteis
```bash
# Atualização completa (padrão)
"Atualiza a documentação em memory/ com o trabalho feito (CURRENT_STATE, TODO, CHANGELOG e outros relevantes)."

# Só marcar tarefa concluída
"Marca esta tarefa como concluída no TODO."

# Registar decisão técnica específica
"Documenta esta decisão no DECISIONS.md: [explicação da decisão]"

# Atualizar schema após migration
"Atualiza DATABASE_SCHEMA.md com as mudanças na BD."

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