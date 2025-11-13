# 🎬 Agora Contabilidade

Sistema de gestão contabilística para Agora Media Production (BA + RR).

---

## 🚨 NOVA SESSÃO CLAUDE CODE? → [Lê Isto Primeiro](./SESSION_IMPORT.md)

**⚠️ CRÍTICO:** O Claude cria novo branch do `main` (desatualizado). Código novo está no branch anterior!

**FRASE MÁGICA v2.0 - Copia e cola sempre:**
```
IMPORTANTE: Estás num branch novo criado do main (desatualizado). Antes de fazer QUALQUER coisa:

1. Lista todos os branches remotos com 'git branch -r'
2. Identifica o branch da sessão anterior (mais recente, excluindo main)
3. Faz merge desse branch para o branch atual
4. SÓ DEPOIS lê README.md e memory/CURRENT_STATE.md

Não leias documentação antes do merge ou terás contexto desatualizado!
```

**O que faz:**
1. ✅ Lista branches remotos (vê o que existe)
2. ✅ Identifica o mais recente (código atualizado)
3. ✅ Faz merge para o branch atual
4. ✅ Lê README.md e memory/CURRENT_STATE.md (contexto completo)

**Instruções detalhadas:** Ver [SESSION_IMPORT.md](./SESSION_IMPORT.md)

💡 **Dica:** Outras frases úteis no [Cheat Sheet](#-cheat-sheet---frases-mágicas) abaixo.

---

## ⚙️ Requisitos do Sistema

- **Python:** 3.12+ (recomendado)
- **SO:** Windows, macOS, Linux
- **Dependências:** Ver `requirements.txt`

## ✨ Funcionalidades (Todas Completas ✅)

### 💰 Saldos Pessoais (CORE)
- Cálculo automático 50/50
- Visualização em cards lado a lado
- Breakdown detalhado (INs/OUTs)

### 📊 Gestão Completa
- ✅ **Dashboard** - Visão geral do sistema
- ✅ **Projetos** - Gestão com prémios individuais
- ✅ **Orçamentos** - Versões e aprovações
- ✅ **Despesas** - Fixas e variáveis
- ✅ **Boletins** - RVs com cálculos automáticos
- ✅ **Clientes** - Base de dados completa
- ✅ **Fornecedores** - Base de dados completa
- ✅ **Equipamento** - Inventário
- ✅ **Relatórios** - Exportação Excel

### 🎨 Interface
- Ícones PNG profissionais (Base64)
- Logos de alta qualidade
- CustomTkinter moderno

## 🚀 Setup Rápido
```bash
# 1. Criar ambiente virtual (recomendado)
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# 2. Instalar dependências
pip install -r requirements.txt

# 3. Configurar base de dados
alembic upgrade head

# 4. (Opcional) Dados de teste
python -c "from database.seed import seed_database; seed_database()"

# 5. Executar
python main.py
```

**Detalhes completos:** Consulta `memory/DEV_SETUP.md`

## 📂 Estrutura do Projeto
```
agora-contabilidade/
├── main.py              # Entry point
├── agora_media.db       # SQLite (gitignored)
│
├── database/            # Camada de dados
│   ├── models/         # SQLAlchemy models
│   └── migrations/     # Alembic migrations
│
├── logic/              # Lógica de negócio
│   ├── saldos.py      # ⭐ CORE - Cálculo 50/50
│   └── ...            # Outros managers
│
├── ui/                 # Interface gráfica
│   ├── screens/       # 10 screens principais
│   └── components/    # Componentes reutilizáveis
│
├── assets/            # Ícones Base64
├── media/             # Logos PNG
│
└── memory/            # 🧠 Documentação dev
    ├── CURRENT_STATE.md  ⭐ COMEÇA AQUI!
    ├── TODO.md
    ├── ARCHITECTURE.md
    └── ...
```

## 💡 Como Funciona o Cálculo de Saldos

### Conceito
Os sócios fazem trabalhos **pessoais** (como freelancers) mas **faturam pela empresa**. Isto cria "dívidas" da empresa para os sócios.

### Fórmula
```
Saldo = INs - OUTs

INs (empresa DEVE ao sócio):
  • Projetos pessoais faturados pela empresa
  • Prémios recebidos de projetos da empresa

OUTs (empresa PAGA ao sócio):
  • Despesas fixas mensais ÷ 2
  • Boletins emitidos
  • Despesas pessoais excecionais
```

### Exemplo Real
```
Bruno em Janeiro:

INs:
  • Projeto pessoal: €1.500
  • Prémio de projeto empresa: €500
  = €2.000 TOTAL

OUTs:
  • Despesas fixas: €350 ÷ 2 = €175
  • Boletim emitido: €600
  = €775 TOTAL

Saldo = €2.000 - €775 = €1.225
```

## 🔑 Regras de Negócio Importantes

### Projetos
- **EMPRESA**: Valor não entra nos saldos, apenas prémios
- **PESSOAL_BRUNO/RAFAEL**: Valor total entra nos INs do sócio
- Apenas projetos **RECEBIDOS** contam para saldos

### Despesas
- **FIXA_MENSAL**: Divide por 2, cada sócio desconta metade
- **PESSOAL_BRUNO/RAFAEL**: Desconta apenas do sócio específico
- **EQUIPAMENTO**: Pode descontar se para uso pessoal
- Apenas despesas **PAGAS** contam para saldos

### Boletins
- Quando **EMITIDOS** → NÃO descontam do saldo (ainda não pagos)
- Quando **PAGOS** → Descontam do saldo nesse momento

## 🎨 Stack Tecnológica

- **Interface:** CustomTkinter
- **Base de Dados:** SQLite
- **ORM:** SQLAlchemy + Alembic
- **Python:** 3.12+
- **Exportação:** openpyxl (Excel)

## 📝 Próximos Passos

Ver `memory/TODO.md` para lista completa. Destaques:
- [ ] Testes automatizados
- [ ] Build para Windows (PyInstaller)
- [ ] Backup automático da BD
- [ ] Integração TOConline API (futuro)

## 🔧 Comandos Úteis

### Base de Dados
```bash
# Ver estado migrations
alembic current

# Aplicar migrations
alembic upgrade head

# Criar nova migration
alembic revision --autogenerate -m "descrição"

# Reset completo (dev)
rm agora_media.db
alembic upgrade head
```

### Git
```bash
git status
git add .
git commit -m "mensagem"
git push
```

## 🆘 Troubleshooting

### Erro: "No module named..."
```bash
pip install -r requirements.txt
```

### DB locked
Fecha todas as instâncias da app e remove `.db-journal`

### Logos não aparecem
Verifica `media/logos/*.png` - devem existir 4 ficheiros

**Mais ajuda:** Consulta `memory/DEV_SETUP.md`

---

## 🎯 Cheat Sheet - Frases Mágicas

Usa estas frases para comandos rápidos durante desenvolvimento com Claude Code:

| Situação | Frase Mágica | O que faz |
|----------|--------------|-----------|
| 🆕 **Nova sessão** | `IMPORTANTE: Estás num branch novo criado do main...` [(ver acima)](#-nova-sessão-claude-code--lê-isto-primeiro) | Importa branch anterior + lê contexto completo |
| ✅ **Trabalho concluído** | `Atualiza a documentação em memory/ com o trabalho feito (CURRENT_STATE, TODO, CHANGELOG e outros relevantes).` | Atualiza docs principais + outros se aplicável |
| 📋 **Só marcar tarefa** | `Marca esta tarefa como concluída no TODO.` | Move tarefa específica para ✅ Concluído |
| 🎯 **Decisão técnica** | `Documenta esta decisão no DECISIONS.md: [explicação]` | Regista decisão técnica importante |
| 🗄️ **Schema alterado** | `Atualiza DATABASE_SCHEMA.md com as mudanças na BD.` | Atualiza documentação do schema |
| 📝 **Resumo sessão** | `Quick doc update - resume o que fizemos hoje.` | Atualização rápida e sumária |

📖 **Mais detalhes:** Ver [memory/README.md](./memory/README.md) para explicação completa do sistema de documentação.

---

## 📚 Documentação Completa

Toda a documentação técnica está em `/memory/`:
- `CURRENT_STATE.md` ⭐ - Estado atual
- `ARCHITECTURE.md` - Como funciona
- `DECISIONS.md` - Porquê fizemos assim
- `DATABASE_SCHEMA.md` - Estrutura da BD
- `DEV_SETUP.md` - Setup detalhado

---

**© 2025 Agora Media Production**
**Status:** ✅ Produção Ready