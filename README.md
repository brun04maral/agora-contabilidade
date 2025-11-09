# 💰 Agora Media - Sistema de Contabilidade

Sistema de gestão contabilística para a Agora Media Production, com foco especial no **cálculo de Saldos Pessoais** dos sócios.

## ⚙️ Requisitos do Sistema

**Python:** 3.10-3.12 (testado e recomendado: Python 3.12)

**Para verificar compatibilidade:**
```bash
python check_python_version.py
```

**Windows:** Consulte [WINDOWS_SETUP.md](WINDOWS_SETUP.md) para instruções detalhadas

## ✨ Funcionalidades Principais

### 🎯 Saldos Pessoais (CORE do Sistema)
- **Cálculo automático** dos saldos de cada sócio
- **INs (Entradas)**: Projetos pessoais + Prémios de projetos da empresa
- **OUTs (Saídas)**: Despesas fixas ÷ 2 + Boletins emitidos + Despesas pessoais
- **Sugestão automática** de valor de boletim para zerar saldo
- **Visualização clara** em cards lado a lado

### 📊 Outras Funcionalidades
- ✅ Gestão de Projetos (Empresa / Pessoal Bruno / Pessoal Rafael)
- ✅ Gestão de Despesas (Fixas / Pessoais / Equipamento)
- ✅ Emissão e controlo de Boletins
- ✅ Base de dados de Clientes
- ✅ Base de dados de Fornecedores
- 🔄 Dashboard (em desenvolvimento)
- 🔄 Relatórios e análises (em desenvolvimento)

## 🚀 Setup Rápido

### 1. Instalar Dependências

```bash
pip install -r requirements.txt
```

### 2. Configurar Base de Dados

**Opção A: SQLite (Local - para desenvolvimento)**
```bash
# Já está configurado no .env por defeito
python3 setup_database.py
```

**Opção B: Supabase (Cloud - para produção)**
```bash
# Editar .env e descomentar a linha do PostgreSQL
# DATABASE_URL=postgresql://...
python3 setup_database.py
```

### 3. Executar Aplicação

```bash
python main.py
```

### 4. Login

Use uma das contas criadas automaticamente:
- **Bruno**: `bruno@agoramedia.pt` / `bruno123`
- **Rafael**: `rafael@agoramedia.pt` / `rafael123`

## 📂 Estrutura do Projeto

```
agora-contabilidade/
├── main.py                 # Ponto de entrada
├── setup_database.py       # Script de setup da BD
├── test_saldos.py         # Testes da lógica de saldos
│
├── database/
│   ├── models/            # Modelos SQLAlchemy
│   │   ├── user.py
│   │   ├── cliente.py
│   │   ├── fornecedor.py
│   │   ├── projeto.py     # ⭐ Com tipos: EMPRESA/PESSOAL_BRUNO/PESSOAL_RAFAEL
│   │   ├── despesa.py     # ⭐ Com tipos: FIXA_MENSAL/PESSOAL_X/EQUIPAMENTO
│   │   ├── boletim.py     # ⭐ Desconta ao ser emitido
│   │   └── equipamento.py
│   └── migrations/        # Scripts de migração
│
├── logic/
│   ├── auth.py           # Autenticação JWT
│   └── saldos.py         # ⭐⭐⭐ LÓGICA CORE - Cálculo de saldos
│
├── ui/
│   ├── main_window.py    # Janela principal com sidebar
│   ├── components/
│   │   └── sidebar.py    # Menu lateral
│   └── screens/
│       ├── login.py      # Tela de login
│       └── saldos.py     # ⭐ Tela de Saldos Pessoais
│
└── utils/
    └── session.py        # Gestão de sessões
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

- **Interface**: CustomTkinter (moderna e responsiva)
- **Base de Dados**: PostgreSQL (Supabase) ou SQLite
- **ORM**: SQLAlchemy
- **Autenticação**: JWT + bcrypt
- **Python**: 3.11+

## 📝 Próximos Passos

- [ ] Tela de gestão de Projetos (CRUD completo)
- [ ] Tela de gestão de Despesas (CRUD completo)
- [ ] Tela de gestão de Boletins
- [ ] Dashboard com indicadores
- [ ] Relatórios e gráficos
- [ ] Histórico mensal de saldos
- [ ] Exportar para Excel
- [ ] Integração TOConline API
- [ ] Dark/Light theme toggle

## 🆘 Resolução de Problemas

### Erro: "No module named..."
```bash
pip install -r requirements.txt
```

### Erro: Base de dados não conecta
Verifique o `.env` e as credenciais do Supabase.

### Resetar base de dados
```bash
rm agora_media.db  # Se usando SQLite
python3 setup_database.py
```

## 📞 Suporte

Para dúvidas ou problemas:
- Bruno Amaral: bruno@agoramedia.pt
- Rafael Reigota: rafael@agoramedia.pt

---

**© 2025 Agora Media Production**
