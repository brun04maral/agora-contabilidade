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
│   ├── boletim.py                 # Boletim itinerário (EXPANDIDO ✅)
│   ├── boletim_linha.py           # Linhas de deslocação (NOVO ✅)
│   ├── boletim_template.py        # Templates de boletins (NOVO ✅)
│   ├── valor_referencia_anual.py  # Config valores por ano (NOVO ✅)
│   ├── cliente.py
│   ├── fornecedor.py
│   ├── orcamento.py
│   └── equipamento.py
├── migrations/       # Alembic (versões do schema)
│   ├── 016_create_valores_referencia_anual.py
│   ├── 017_create_boletim_linhas.py
│   ├── 018_create_boletim_templates.py
│   └── 019_expand_boletins.py
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
├── boletins.py                  # BoletinsManager (EXPANDIDO ✅)
├── boletim_linhas.py            # BoletimLinhasManager (NOVO ✅) - recalcular_totais_boletim()
├── boletim_templates.py         # BoletimTemplatesManager (NOVO ✅) - gerar_boletins_recorrentes_mes()
├── valores_referencia.py        # ValoresReferenciaManager (NOVO ✅) - obter_ou_default()
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
├── screens/                # Telas principais (14 completas)
│   ├── dashboard.py
│   ├── saldos.py
│   ├── info.py
│   ├── projetos.py
│   ├── despesas.py
│   ├── templates_despesas.py      # Templates de despesas recorrentes
│   ├── boletins.py                # Lista de boletins (ATUALIZADO ✅) + GerarRecorrentesDialog
│   ├── boletim_form.py            # Editor completo de boletim (NOVO ✅) + LinhaDialog (850L)
│   ├── templates_boletins.py      # Templates de boletins recorrentes (NOVO ✅) (340L)
│   ├── valores_referencia.py      # Config valores por ano (NOVO ✅) (328L)
│   ├── clientes.py
│   ├── fornecedores.py
│   ├── orcamentos.py
│   ├── equipamento.py
│   └── relatorios.py
└── components/         # Componentes reutilizáveis
    ├── sidebar.py
    ├── base_screen.py              # ✅ Template para screens de listagem (NOVO 24/11)
    ├── base_form.py                # 📋 Template para forms (futuro)
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

**Padrão Screen - Legado (pré-24/11/2025):**
```python
class OrcamentosScreen(ctk.CTkFrame):
    def __init__(self, parent, db_session: Session):
        self.manager = OrcamentosManager(db_session)
        self.create_widgets()  # 100-200 linhas de layout
        self.carregar_dados()

    def create_widgets(self):
        # Header manual
        # Filtros manuais
        # Pesquisa manual
        # Tabela DataTableV2
        # Context menu manual
```

**Padrão Screen - Novo (BaseScreen, desde 24/11/2025):**
```python
from ui.components.base_screen import BaseScreen

class ProjectsScreen(BaseScreen):
    def __init__(self, parent, db_session: Session, **kwargs):
        self.manager = ProjetosManager(db_session)

        # Configurar aparência
        self.screen_config = {
            'title': 'Projetos',
            'icon_key': PROJETOS,
            'new_button_text': 'Novo Projeto',
            'search_placeholder': 'Pesquisar...'
        }

        super().__init__(parent, db_session, **kwargs)

    # Métodos abstratos obrigatórios
    def get_table_columns(self): ...
    def load_data(self): ...
    def item_to_dict(self, item): ...

    # Métodos opcionais (sobrescrever conforme necessidade)
    def get_filters_config(self): ...
    def get_context_menu_items(self, data): ...
    def apply_filters(self, items, filters): ...
```

**Benefícios BaseScreen:**
- ✅ Layout consistente (header, search, filters, table) criado automaticamente
- ✅ Redução ~36% código por screen (ProjectsScreen: 661→424 linhas)
- ✅ Funcionalidades comuns centralizadas (pesquisa reactiva, filtros, context menu)
- ✅ Slots para customização (header_slot, filters_slot, footer_slot)
- ✅ Manutenção simplificada (correções aplicam-se a todas screens)

**Ver:** memory/UI_ARCHITECTURE.md (guia completo de uso)

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

---

## 📊 Orçamentos V2 - Arquitetura Detalhada (16/11/2025)

### Camada Logic - Managers

logic/
├── orcamentos.py          # OrcamentoManager (CRUD, aprovação, validação totais)
├── orcamento_items.py     # ItemManager (CRUD tipo-aware: servico, equipamento, despesas)
├── orcamento_reparticoes.py # ReparticaoManager (CRUD beneficiarios, comissões)

### Camada UI - Screens & Dialogs

#### Arquitetura Base de Dialogs (Refatoração 21/11/2025)

Todos os dialogs modais herdam de classes base em `utils/base_dialogs.py`:

**Classes Disponíveis:**
- `BaseDialogMedium` - Maioria dos dialogs (500x450)
- `BaseDialogLarge` - Layouts maiores

**Padrão de Uso:**
```python
from utils.base_dialogs import BaseDialogMedium

class MeuDialog(BaseDialogMedium):
    def __init__(self, parent, ...):
        super().__init__(parent, title="Título", width=500, height=450)
        self.create_widgets()

    def create_widgets(self):
        main = self.main_frame  # Frame com scroll automático
        # Widgets aqui
```

**Regras UX Uniformizadas:**
- ✅ Scroll automático (sem overflows)
- ✅ Layout/tamanho/padding centralizados
- ✅ Modal (transient + grab_set)
- ❌ **SEM popups de sucesso** - apenas `messagebox.showerror/warning`
- ❌ SEM geometry/scroll manual

**Ao Gravar:**
- Sucesso → `self.success = True` + `self.destroy()`
- Erro → `messagebox.showerror("Erro", msg)`

---

ui/screens/
├── orcamento_form.py      # Screen principal (tabs CLIENTE/EMPRESA, validação)
└── dialogs/               # Todos herdam BaseDialogMedium
    ├── servico_dialog.py       # CLIENTE: descrição, qtd, dias, preço, desconto
    ├── equipamento_dialog.py   # CLIENTE: idem + seleção de lista
    ├── transporte_dialog.py    # CLIENTE: kms × valor/km
    ├── refeicao_dialog.py      # CLIENTE: nº refeições × valor/refeição
    ├── outro_dialog.py         # CLIENTE: valor fixo
    ├── servico_empresa_dialog.py    # EMPRESA: + beneficiário
    ├── equipamento_empresa_dialog.py # EMPRESA: + beneficiário
    └── comissao_dialog.py      # EMPRESA: tipo, %, base, beneficiário

### Fluxos Críticos

**1. Sincronização Despesas CLIENTE→EMPRESA:**

Ao criar/editar despesa no CLIENTE:
1. ItemManager.criar_item(tipo='transporte|refeicao|outro')
2. Trigger automático: ReparticaoManager.espelhar_despesa(item_id)
3. Cria repartição com:
   - tipo='despesa'
   - beneficiario='AGORA'
   - item_cliente_id=item.id
   - readonly=True
4. Ao editar/apagar item cliente → propaga para empresa

**2. Validação de Totais:**

Em tempo real no OrcamentoFormScreen:
- total_cliente = sum(item.total for item in items_cliente)
- total_empresa = sum(rep.total for rep in reparticoes_empresa)
- Se abs(total_cliente - total_empresa) < 0.01: Verde (pode aprovar)
- Senão: Vermelho (bloqueio aprovação) + mostrar diferença

**3. Auto-preenchimento Comissões:**

Botão "Auto-preencher" no EMPRESA:
- base = total_empresa_antes_comissoes
- Comissão venda: tipo='comissao', beneficiario=owner (BA/RR), %=5.000
- Comissão empresa: tipo='comissao', beneficiario='AGORA', %=10.000

### Referências Técnicas
- BUSINESS_LOGIC.md (Secção 1-7)
- DATABASE_SCHEMA.md (tabelas, enums, FKs)
- Migration 022 (schema V2)

---

### Totais por Beneficiário (PLANEADO)

**STATUS:** 📝 Especificado, aguarda implementação (próximo sprint)

**OrcamentoForm - Método calcular_totais_beneficiarios():**
```python
def calcular_totais_beneficiarios(self) -> Dict[str, Decimal]:
    """
    Percorre todas reparticoes EMPRESA e agrega por beneficiário.

    Retorna: {
        'BA': Decimal('1500.00'),
        'RR': Decimal('800.00'),
        'AGORA': Decimal('400.00'),
        'FREELANCER_2': Decimal('500.00'),
        'FORNECEDOR_5': Decimal('200.00')
    }
    """
    totais = {}
    for reparticao in self.reparticoes_empresa:
        beneficiario = reparticao.beneficiario
        totais[beneficiario] = totais.get(beneficiario, Decimal('0')) + reparticao.total
    return totais
```

**UI - Frame Dedicado com Cards Coloridos:**
- Localização: OrcamentoForm, abaixo da tabela reparticoes EMPRESA
- Atualiza em tempo real ao adicionar/editar/apagar items
- Cards coloridos por tipo:
  - 🟢 VERDE: Sócios (BA, RR)
  - 🔵 AZUL: Empresa (AGORA)
  - 🟠 LARANJA: Externos (FREELANCER_*, FORNECEDOR_*)
- Display: "BA - Bruno: €1.500,00"
- Validação visual: soma == TOTAL EMPRESA (check verde ou warning laranja)

**Conversão em Projeto:**

Método `converter_em_projeto()` distribui valores nos campos de rastreabilidade:

```python
def converter_em_projeto(self, orcamento_id):
    totais = self.calcular_totais_beneficiarios()

    # Separar por categoria
    premio_bruno = totais.get('BA', 0)
    premio_rafael = totais.get('RR', 0)
    valor_empresa = totais.get('AGORA', 0)
    valor_fornecedores = sum([
        v for k, v in totais.items()
        if k.startswith('FREELANCER_') or k.startswith('FORNECEDOR_')
    ])

    # Criar projeto com campos preenchidos
    projeto = ProjetoManager.criar(
        cliente_id=orcamento.cliente_id,
        valor_total=orcamento.total_cliente,
        premio_bruno=premio_bruno,
        premio_rafael=premio_rafael,
        valor_empresa=valor_empresa,
        valor_fornecedores=valor_fornecedores,
        # ... outros campos
    )
```

**Campos Projeto Preenchidos Automaticamente:**
- `premio_bruno`: sum(reparticoes WHERE beneficiario='BA')
- `premio_rafael`: sum(reparticoes WHERE beneficiario='RR')
- `valor_empresa`: sum(reparticoes WHERE beneficiario='AGORA')
- `valor_fornecedores`: sum(reparticoes WHERE beneficiario LIKE 'FREELANCER_%' OR LIKE 'FORNECEDOR_%')

**Screens Novos a Criar:**

1. **ui/screens/freelancer_form.py** - Ficha Individual Freelancer
   - Secção superior: dados cadastrais (nome, NIF, IBAN, especialidade, notas)
   - Secção inferior: tabela trabalhos históricos
   - Colunas: Data | Orçamento | Projeto | Descrição | Valor | Status | Ações
   - Botão "Marcar como Pago" em cada linha status='a_pagar'
   - Footer: Total A Pagar | Total Pago | Total Geral

2. **ui/screens/fornecedor_form.py** - Expandir Existente
   - Adicionar secção: tabela compras históricas
   - Mesmo layout e funcionalidades que freelancer_form.py

3. **ui/components/totais_beneficiarios_frame.py** - Frame Reutilizável
   - Recebe dict de totais
   - Renderiza cards coloridos
   - Mostra validação visual (soma vs total)

**Dashboard - Novos Cards:**

1. Card "💰 Freelancers A Pagar"
   - Valor: FreelancerTrabalhosManager.calcular_total_a_pagar()
   - Clique: navega para FreelancersScreen com filtro status='a_pagar'

2. Card "🏢 Fornecedores A Pagar"
   - Valor: FornecedorComprasManager.calcular_total_a_pagar()
   - Clique: navega para FornecedoresScreen com filtro status='a_pagar'

**Ficheiros a Modificar:**
- `ui/screens/orcamento_form.py` (+150 linhas)
- `ui/screens/dashboard.py` (+80 linhas)
- `logic/orcamentos.py` (converter_em_projeto: +30 linhas)

**Estimativa:** 2-3 sessões de implementação

**Ver:** TODO.md (Tarefa 7), BUSINESS_LOGIC.md (Secção 7), DATABASE_SCHEMA.md (Migration 025)

---

---

## 🔄 SISTEMA DE BENEFICIÁRIOS - Fluxos e Integrações

### Managers Necessários

Novos ficheiros a criar:

logic/freelancers.py - FreelancerManager
- listar_todos(ativo=None)
- obter(freelancer_id)
- criar(nome, nif, email, iban, ...)
- atualizar(freelancer_id, ...)
- ativar_desativar(freelancer_id)
- registar_trabalho(freelancer_id, orcamento_id, valor, ...)
- obter_trabalhos(freelancer_id, status=None)
- marcar_trabalho_pago(trabalho_id)

logic/fornecedores.py - FornecedorManager (EXPANDIR EXISTENTE)
Métodos novos:
- registar_compra(fornecedor_id, orcamento_id, valor, ...)
- obter_compras(fornecedor_id, status=None)
- marcar_compra_paga(compra_id)

utils/beneficiario_utils.py - Funções utilitárias
- resolver_beneficiario_display(beneficiario, db_session)
- validar_beneficiario(beneficiario, db_session)
- extrair_id_beneficiario(beneficiario)

### UI Components Necessários

Novos ficheiros a criar:

ui/dialogs/beneficiario_selector_dialog.py
- BeneficiarioSelectorDialog (modal com tabs Freelancers/Fornecedores)
- Campo pesquisa, tabela, botão selecionar
- Botão "+ Criar Novo" → abre quick dialogs

ui/dialogs/freelancer_quick_dialog.py
- FreelancerQuickDialog (criação rápida: nome, NIF, IBAN)

ui/dialogs/fornecedor_quick_dialog.py
- FornecedorQuickDialog (criação rápida: nome, NIF)

ui/screens/freelancers_screen.py (NOVA)
- CRUD completo de freelancers
- Tabela com histórico de trabalhos
- Filtros por status (a_pagar, pago)

ui/screens/fornecedores_screen.py (EXPANDIR EXISTENTE)
- Adicionar tab "Histórico de Compras"
- Mostrar compras por fornecedor

### Fluxo: Seleção de Beneficiário

Nos dialogs EMPRESA (ServicoEmpresaDialog, EquipamentoEmpresaDialog, ComissaoDialog):

Nível 1 - Dropdown rápido:
[BA | RR | AGORA | Outro... ▼]

Nível 2 - Se "Outro..." selecionado:
Abre BeneficiarioSelectorDialog com tabs [Freelancers] [Fornecedores]

Retorno:
- codigo: "FREELANCER_123" ou "FORNECEDOR_456"
- nome_display: "João Silva" ou "TechRent Lda"

### Fluxo: Integrações ao Aprovar Orçamento

Trigger: OrcamentoManager.aprovar_orcamento()

1. Validar totais coincidem
2. Calcular resumo de beneficiários
3. Para cada beneficiário:
   - Se BA ou RR → PremioManager.criar(...)
   - Se AGORA → (futuro) ReceitaManager.criar(...)
   - Se FREELANCER_[id] → FreelancerManager.registar_trabalho(...)
   - Se FORNECEDOR_[id] → FornecedorManager.registar_compra(...)
4. Criar projeto (fluxo existente)
5. Atualizar status orçamento

### Fluxo: Resumo de Beneficiários

Nova tab no OrcamentoFormScreen: "💰 RESUMO BENEFICIÁRIOS"

Mostra tabela agregada:
Beneficiário | Tipo | Nº Items | Total € | % Total

Funcionalidades:
- Clique → detalha repartições
- Validação: soma = total empresa
- Exportação para Excel/PDF

### Validações

Ao criar/editar reparticão:
- Beneficiário não vazio
- Se FREELANCER_[id] → verificar existe e ativo
- Se FORNECEDOR_[id] → verificar existe e ativo
- Alertar se inativo (permite gravar)

Ao aprovar orçamento:
- Todos beneficiários válidos
- Freelancers/fornecedores existem
- Total por beneficiário > 0

---


**Mantido por:** Equipa Agora
**Última revisão:** 2025-11-17
