# 🎬 Agora Media Contabilidade

Sistema de gestão contabilística para Agora Media Production (BA + RR).

---

## 🚀 **FRASE MÁGICA** - Iniciar Nova Sessão Claude Code

Quando abrires uma nova sessão no Claude Code, usa esta frase:

```
Lê memory/CURRENT_STATE.md e memory/TODO.md para contexto do projeto
```

Isto dá ao Claude contexto completo em **segundos**:
- ✅ Estado atual (features implementadas)
- ✅ Próximos passos e tarefas
- ✅ Toda a informação necessária

**Contexto adicional:** Consulta `/memory/` para arquitetura, decisões, schema, etc.

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
- Quando **EMITIDOS** → Descontam **IMEDIATAMENTE** do saldo
- Quando **PAGOS** → Apenas muda estado (já tinha descontado)

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
