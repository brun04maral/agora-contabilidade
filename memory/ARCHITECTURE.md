# 🏗️ Arquitetura - Agora Contabilidade

## 📐 Visão Geral

Aplicação desktop em Python com arquitetura em camadas (MVC adaptado).

```
┌─────────────────────────────────────────┐
│          UI Layer (CustomTkinter)       │
│  Screens + Components + Navigation      │
└─────────────┬───────────────────────────┘
              │
┌─────────────▼───────────────────────────┐
│       Logic Layer (Business Logic)      │
│   Managers: Projetos, Despesas, etc.    │
└─────────────┬───────────────────────────┘
              │
┌─────────────▼───────────────────────────┐
│      Database Layer (SQLAlchemy ORM)    │
│   Models + Migrations (Alembic)         │
└─────────────┬───────────────────────────┘
              │
┌─────────────▼───────────────────────────┐
│         Data Layer (SQLite DB)          │
│        agora_media.db (file)            │
└─────────────────────────────────────────┘
```

---

## 📁 Estrutura de Pastas

### `/database/` - Camada de Dados
```python
database/
├── models/           # SQLAlchemy models (ORM)
│   ├── socio.py
│   ├── projeto.py
│   ├── despesa.py
│   ├── despesa_template.py        # Templates de despesas recorrentes
│   ├── boletim.py                 # Boletim itinerário (SERÁ EXPANDIDO)
│   ├── boletim_linha.py           # Linhas de deslocação (NOVO - Planeado)
│   ├── boletim_template.py        # Templates de boletins (NOVO - Planeado)
│   ├── valor_referencia_anual.py  # Config valores por ano (NOVO - Planeado)
│   ├── cliente.py
│   ├── fornecedor.py
│   ├── orcamento.py
│   └── equipamento.py
├── migrations/       # Alembic (versões do schema)
└── seed.py          # Dados iniciais para desenvolvimento
```

**Responsabilidades:**
- Definir estrutura de dados (models)
- Gerir schema (migrations)
- Queries básicas via SQLAlchemy

### `/logic/` - Camada de Lógica de Negócio
```python
logic/
├── saldos.py                    # SaldosCalculator (CORE)
├── projetos.py                  # ProjetosManager
├── despesas.py                  # DespesasManager
├── despesa_templates.py         # DespesaTemplatesManager
├── boletins.py                  # BoletinsManager (SERÁ EXPANDIDO)
├── boletim_linhas.py            # BoletimLinhasManager (NOVO - Planeado)
├── boletim_templates.py         # BoletimTemplatesManager (NOVO - Planeado)
├── valores_referencia.py        # ValoresReferenciaManager (NOVO - Planeado)
├── clientes.py                  # ClientesManager
├── fornecedores.py              # FornecedoresManager
├── orcamentos.py                # OrcamentoManager
├── equipamento.py               # EquipamentoManager
└── relatorios.py                # RelatoriosManager
```

**Responsabilidades:**
- Regras de negócio
- Cálculos complexos (ex: saldos 50/50)
- Validações
- Agregações de dados
- Exportações

**Padrão Manager:**
```python
class ProjetosManager:
    def __init__(self, db_session: Session):
        self.db = db_session

    def listar(self, filtros=None):
        # Query + validação

    def criar(self, dados):
        # Validação + criação

    def atualizar(self, id, dados):
        # Validação + update

    def eliminar(self, id):
        # Soft delete ou hard delete
```

### `/ui/` - Camada de Interface
```python
ui/
├── screens/                # Telas principais (14 planeadas)
│   ├── dashboard.py
│   ├── saldos.py
│   ├── info.py
│   ├── projetos.py
│   ├── despesas.py
│   ├── templates_despesas.py      # Templates de despesas recorrentes
│   ├── boletins.py                # Lista de boletins (SERÁ ATUALIZADO)
│   ├── boletim_form.py            # Editor completo de boletim (NOVO - Planeado)
│   ├── templates_boletins.py      # Templates de boletins recorrentes (NOVO - Planeado)
│   ├── valores_referencia.py      # Config valores por ano (NOVO - Planeado)
│   ├── clientes.py
│   ├── fornecedores.py
│   ├── orcamentos.py
│   ├── equipamento.py
│   └── relatorios.py
└── components/         # Componentes reutilizáveis
    ├── sidebar.py
    ├── data_table_v2.py            # Suporte para strikethrough seletivo
    ├── date_picker_dropdown.py     # Seletor de data único
    ├── date_range_picker_dropdown.py  # Seletor de período
    └── forms/
```

**Responsabilidades:**
- Apresentação (widgets CustomTkinter)
- Eventos de user input
- Navegação entre screens
- Validação básica de formulários

**Padrão Screen:**
```python
class ProjetosScreen(ctk.CTkFrame):
    def __init__(self, parent, db_session: Session):
        self.manager = ProjetosManager(db_session)
        self.create_widgets()
        self.carregar_dados()

    def create_widgets(self):
        # Criar UI

    def carregar_dados(self):
        # Chamar manager.listar()
        # Atualizar tabela
```

### `/assets/` - Recursos Visuais
```python
assets/
├── resources.py      # Ícones Base64 + funções de carregamento
└── icons/           # (não usado - ícones já em Base64)
```

**Sistema de Ícones:**
- Ícones embutidos como constantes Base64
- Função `get_icon(ICON, size)` retorna PIL.Image
- Conversão para CTkImage na UI

### `/media/` - Logos e Assets Binários
```
media/
└── logos/
    ├── logo.svg              # Referência (contém PNG embutido)
    ├── logo_sidebar.png      # 100x60 (71KB)
    ├── logo_sidebar@2x.png   # 200x120 (156KB)
    ├── logo_login.png        # 313x80 (71KB)
    └── logo_login@2x.png     # 626x160 (156KB)
```

**Sistema de Logos:**
- PNGs mantidos manualmente (alta qualidade)
- Fallback: SVG (Cairo) → PNG → Texto
- Função `get_logo_with_fallback()`

---

## 🔄 Fluxo de Dados

### Exemplo: Criar Novo Projeto

```
1. User preenche formulário
   └─> ProjetosScreen.on_save()

2. Screen valida campos básicos
   └─> self.manager.criar(dados)

3. Manager valida regras de negócio
   └─> projeto = Projeto(**dados)
   └─> db.add(projeto)
   └─> db.commit()

4. Manager retorna resultado
   └─> Screen atualiza tabela
   └─> Screen mostra mensagem sucesso
```

### Exemplo: Calcular Saldos Pessoais (CORE)

```
1. SaldosScreen solicita dados
   └─> calculator = SaldosCalculator(db_session)
   └─> saldos = calculator.calcular_saldos_socios()

2. Calculator agrega dados:
   - Projetos (receitas + prémios)
   - Despesas (50% cada)
   - Boletins (valores)

3. Calculator calcula:
   - Total IN por sócio
   - Total OUT por sócio
   - Saldo = IN - OUT

4. Screen apresenta:
   - Cards com saldos
   - Breakdown detalhado
```

---

## 🗄️ Modelo de Dados (Resumo)

### Entidades Principais

**Sócio** (2 fixos: BA, RR)
- Identificação
- Dados bancários
- Relacionamentos com projetos/despesas/boletins

**Projeto**
- Cliente, tipo, estado
- Valores (frontend, backend, total)
- Prémios por sócio
- Pagamentos

**Despesa**
- Tipo (fixa/variável)
- Valor, data, estado
- Sócio responsável

**Boletim**
- Mês/ano
- Sócio
- Valores (vencimento, contribuições, IRS)

**Orçamento**
- Cliente, versão
- Estado (pendente/aprovado/rejeitado)
- Linhas de orçamento

---

## 🎯 Princípios de Design

### Separation of Concerns
- **UI** apenas apresenta e captura eventos
- **Logic** contém regras de negócio
- **Database** apenas define estrutura

### Single Responsibility
- Cada Manager gere uma entidade
- Cada Screen apresenta uma funcionalidade
- Cada Model representa uma tabela

### DRY (Don't Repeat Yourself)
- Componentes reutilizáveis (DataTableV2)
- Managers evitam código duplicado
- Funções helper em `assets.resources`

### Testability
- Managers testáveis (sem UI)
- Session injetada (mock fácil)
- Lógica separada de apresentação

---

## 🔌 Dependências Principais

```python
# Core
python = "3.12+"
sqlalchemy = "ORM"
alembic = "Migrations"

# UI
customtkinter = "Interface moderna"
pillow = "Imagens"

# Excel/Relatórios
openpyxl = "Exportar Excel"
pandas = "Manipulação dados"

# Utils
python-dateutil = "Datas"
```

---

## 🚀 Padrões de Extensão

### Adicionar Nova Entidade

1. **Model** em `/database/models/nova_entidade.py`
2. **Migration** via `alembic revision --autogenerate`
3. **Manager** em `/logic/nova_entidade.py`
4. **Screen** em `/ui/screens/nova_entidade.py`
5. **Ícone** em `/assets/resources.py`
6. **Sidebar** adicionar menu em `ui/components/sidebar.py`

### Adicionar Nova Feature a Entidade Existente

1. **Alterar Model** → criar migration
2. **Estender Manager** com nova lógica
3. **Atualizar Screen** com novos campos/botões

---

**Mantido por:** Equipa Agora
**Última revisão:** 2025-11-13
