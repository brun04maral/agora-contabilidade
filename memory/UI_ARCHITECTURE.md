# UI Architecture - Agora Contabilidade

**Última atualização:** 2025-11-24

---

## Templates Base: Screens & Forms

### Visão Geral

Estratégia de componentização para UI consistente e manutenível através de templates base reutilizáveis.

### ✨ Refinamentos Visuais (24/11/2025)

**Melhorias aplicadas ao BaseScreen:**

1. **Barra de Pesquisa Compacta**
   - Só ícone lupa 🔍 (sem texto "Pesquisar:")
   - Width reduzida: 320px
   - Botão limpar sem moldura (só ícone ✖)
   - Height: 32px (antes 35px)

2. **Filtros Horizontais com Multi-Seleção**
   - Alinhados à direita da pesquisa
   - Seleção múltipla (OR logic)
   - Dropdowns compactos (height: 32px)
   - Placeholder mostra label do filtro
   - Indicador visual: texto azul quando filtro tem seleções ativas

3. **Chips/Badges de Filtros Ativos**
   - Material Design style
   - Cores filtros: azul (#E3F2FD light / #1E3A5F dark)
   - Cor pesquisa: verde (#E8F5E9 light / #1B5E20 dark)
   - Chip de pesquisa mostra termo com ícone 🔍
   - Botão ✕ para remover individual
   - Área oculta quando sem chips

4. **Tabela Expandida**
   - `fill="both"` + `expand=True`
   - Ocupa máximo espaço vertical disponível
   - Padding reduzido (30px)

5. **Barra de Ações Contextual**
   - Só aparece quando há seleção
   - Visual flutuante com borda
   - Botões compactos (height: 32px)
   - Mostra contagem + total

6. **Espaçamentos Otimizados** ✅ FINAL
   - Header: pady=(20, 5) - Espaço top adequado, mínimo bottom
   - Toolbar: pady=(0, 5) - Compacto entre título e tabela
   - Removido header_slot (frame vazio a causar espaço)
   - Botões: height=32px (antes 35px)
   - **Espaço título ↔ pesquisa: ~5px** (antes ~40px)

7. **Overlay Containers** (Não Empurram Tabela)
   - overlay_container para chips (height=0→35px)
   - selection_container para barra (height=0→45px)
   - pack_propagate(False) = não expandem automaticamente
   - Aparecem/desaparecem sem afetar posição da tabela
   - Tabela mantém posição fixa sempre

**API Changes:**
- `apply_filters(items, filters: Dict[str, List[str]])` - Aceita listas para multi-seleção
- `get_current_filters()` → `Dict[str, List[str]]` - Retorna listas

**Backward Compatibility:**
- ProjectsScreen atualizado para nova API
- Método `_on_filter_change()` mantido para compatibilidade

### Fase 1: BaseScreen (Implementado)

**Objetivo:** Template base para screens de listagem principal.

**Localização:** `ui/components/base_screen.py`

**Screens Alvo:**
- ✅ Projetos (migrado)
- 📋 Orçamentos (pendente)
- 📋 Despesas (pendente)
- 📋 Boletins (pendente)

### Como Usar BaseScreen

```python
from ui.components.base_screen import BaseScreen
from assets.resources import PROJETOS

class ProjectsScreen(BaseScreen):
    def __init__(self, parent, db_session, **kwargs):
        # 1. Inicializar managers ANTES do super().__init__
        self.manager = ProjetosManager(db_session)

        # 2. Configurar screen_config
        self.screen_config = {
            'title': 'Projetos',
            'icon_key': PROJETOS,
            'icon_fallback': '📁',
            'new_button_text': 'Novo Projeto',
            'new_button_color': ('#4CAF50', '#388E3C'),
            'search_placeholder': 'Pesquisar...',
            'table_height': 400,
        }

        # 3. Chamar super().__init__
        super().__init__(parent, db_session, initial_filters={...}, **kwargs)

    # ========== Métodos Obrigatórios ==========

    def get_table_columns(self) -> List[Dict]:
        """Define colunas da tabela"""
        return [
            {'key': 'numero', 'label': 'ID', 'width': 80},
            {'key': 'valor', 'label': 'Valor', 'width': 100,
             'formatter': lambda v: f"€{v:,.2f}"},
        ]

    def load_data(self) -> list:
        """Carrega dados da BD"""
        return self.manager.listar_todos()

    def item_to_dict(self, item) -> dict:
        """Converte objeto para dict da tabela"""
        return {
            'id': item.id,
            'numero': item.numero,
            '_bg_color': ('#E8F5E0', '#4A7028'),  # Cores por estado
            '_item': item  # Referência ao objeto original
        }

    # ========== Métodos Opcionais ==========

    def get_filters_config(self) -> List[Dict]:
        """Define filtros disponíveis"""
        return [
            {'key': 'estado', 'label': 'Estado:',
             'values': ['Todos', 'Ativo', 'Pago'], 'width': 150},
        ]

    def get_header_buttons(self) -> List[Dict]:
        """Botões adicionais no header"""
        return [
            {'text': '🔁 Gerar', 'command': self.gerar,
             'fg_color': '#2196F3', 'width': 140},
        ]

    def get_selection_actions(self) -> List[Dict]:
        """Ações na barra de seleção"""
        return [
            {'text': '📊 Relatório', 'command': self.relatorio,
             'fg_color': ('#9C27B0', '#7B1FA2')},
        ]

    def get_context_menu_items(self, data: dict) -> List[Dict]:
        """Itens do context menu"""
        return [
            {'label': '✏️ Editar', 'command': lambda: self.editar(data)},
            {'separator': True},
            {'label': '🗑️ Apagar', 'command': lambda: self.apagar(data)},
        ]

    def filter_by_search(self, items: list, search_text: str) -> list:
        """Filtra por texto de pesquisa"""
        return self.manager.filtrar_por_texto(search_text)

    def apply_filters(self, items: list, filters: Dict) -> list:
        """Aplica filtros aos items"""
        if filters.get('estado') != 'Todos':
            items = [i for i in items if i.estado == filters['estado']]
        return items

    def calculate_selection_total(self, selected_data: list) -> float:
        """Calcula total dos selecionados"""
        return sum(item.get('valor', 0) for item in selected_data)

    def on_item_double_click(self, data: dict):
        """Ação ao duplo clique"""
        self.abrir_formulario(data.get('_item'))

    def on_new_item(self):
        """Ação do botão 'Novo'"""
        self.abrir_formulario(None)
```

### Métodos do BaseScreen

#### Métodos Públicos (usar nas subclasses)

| Método | Descrição |
|--------|-----------|
| `refresh_data()` | Recarrega dados com filtros aplicados |
| `get_selected_data()` | Retorna dados das linhas selecionadas |
| `get_current_filters()` | Retorna valores atuais dos filtros |

#### Propriedades Disponíveis

| Propriedade | Descrição |
|-------------|-----------|
| `self.table` | Instância DataTableV2 |
| `self.search_var` | StringVar da pesquisa |
| `self.header_slot` | Frame para conteúdo custom no header |
| `self.filters_slot` | Frame para filtros adicionais |
| `self.footer_slot` | Frame para conteúdo no footer |

### screen_config Options

| Chave | Tipo | Default | Descrição |
|-------|------|---------|-----------|
| `title` | str | 'Screen' | Título do screen |
| `icon_key` | str | None | Chave do ícone (assets.resources) |
| `icon_fallback` | str | '' | Emoji fallback se ícone não carregar |
| `new_button_text` | str | 'Novo' | Texto do botão novo |
| `new_button_color` | tuple | Verde | Cor (light, dark) |
| `new_button_hover` | tuple | - | Cor hover |
| `search_placeholder` | str | 'Pesquisar...' | Placeholder da pesquisa |
| `table_height` | int | 400 | Altura da tabela |
| `show_search` | bool | True | Mostrar barra de pesquisa |

### Fase 2: BaseForm (Futuro)

**Objetivo:** Template base para forms de criação/edição.

**Localização:** `ui/components/base_form.py` (a criar)

**Forms Alvo:**
- ProjetoForm
- OrcamentoForm
- DespesaForm
- BoletimForm

**Responsabilidades:**
- Layout de campos (grid, sections)
- Validações centralizadas
- Tooltips e help text
- Popups de confirmação
- Botões padrão (Guardar, Cancelar)
- Gestão de estado (novo/editar)

### Roadmap

| Fase | Componente | Status |
|------|------------|--------|
| 1.1 | BaseScreen scaffold | ✅ Completo |
| 1.2 | Migrar ProjectsScreen | ✅ Completo |
| 1.3 | Testar e validar ProjectsScreen | 📋 Pendente |
| 1.4 | Migrar OrcamentosScreen | 📋 Pendente |
| 1.5 | Migrar DespesasScreen | 📋 Pendente |
| 1.6 | Migrar BoletinsScreen | 📋 Pendente |
| 2.1 | BaseForm scaffold | 📋 Futuro |
| 2.2 | Migrar forms | 📋 Futuro |

### Benefícios

1. **Consistência** - Todas as screens seguem mesmo padrão
2. **Manutenção** - Correções aplicam-se a todas as screens
3. **Produtividade** - Novas screens em minutos
4. **UX** - Comportamento previsível

### Notas de Implementação

- ProjectsScreen reduziu de 661 para 424 linhas (36% menos código)
- Testar screen migrada antes de continuar com as outras
- Manter compatibilidade com screens não migradas
- Considerar sistema de themes/cores no futuro

---

## Estrutura Atual UI

```
ui/
├── main_window.py           # Janela principal
├── screens/                  # 10+ screens
│   ├── dashboard.py
│   ├── projetos.py          # ✅ Migrado para BaseScreen
│   ├── orcamentos.py
│   ├── despesas.py
│   ├── boletins.py
│   ├── clientes.py
│   ├── fornecedores.py
│   ├── equipamento.py
│   ├── relatorios.py
│   ├── saldos.py
│   └── ...
├── components/               # Componentes reutilizáveis
│   ├── base_screen.py       # ✅ Template screens
│   ├── base_form.py         # 📋 Template forms (futuro)
│   ├── data_table_v2.py     # Tabela avançada
│   ├── date_picker_dropdown.py
│   ├── date_range_picker_dropdown.py
│   ├── sidebar.py
│   └── autocomplete_entry.py
└── dialogs/                  # Dialogs específicos
    ├── servico_dialog.py
    ├── equipamento_dialog.py
    └── ...
```

---

## Sugestões para Customização Futura

### Por Tipo de Screen

**Projetos:**
- Quick actions (marcar pago em 1 clique)
- Status badges coloridos
- Filtro por período

**Orçamentos:**
- Preview inline
- Duplicar com 1 clique
- Badges de aprovação

**Despesas:**
- Gráficos inline de gastos
- Alertas de vencimento
- Recorrência visual

**Boletins:**
- Sumário de valores
- Calendário de emissões
- Templates rápidos

### Melhorias Gerais

- Sistema de favoritos/pinned items
- Atalhos de teclado (Ctrl+N, Ctrl+F, etc.)
- Export rápido (seleção → Excel)
- Bulk actions melhoradas
- Themes customizáveis

---

**Ver também:**
- `memory/ARCHITECTURE.md` - Arquitetura geral
- `memory/DECISIONS.md` - Decisões técnicas
- `ui/components/base_screen.py` - Código fonte do template
