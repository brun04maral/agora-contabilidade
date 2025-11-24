# UI Architecture - Agora Contabilidade

**Última atualização:** 2025-11-24

---

## Templates Base: Screens & Forms

### Visão Geral

Estratégia de componentização para UI consistente e manutenível através de templates base reutilizáveis.

### Fase 1: BaseScreen (Sprint Atual)

**Objetivo:** Criar template base para screens de listagem principal.

**Localização:** `ui/components/base_screen.py`

**Screens Alvo:**
- Projetos
- Orçamentos
- Despesas
- Boletins

**Sintaxe:**
```python
from ui.components.base_screen import BaseScreen

class ProjectsScreen(BaseScreen):
    def __init__(self, parent):
        super().__init__(parent)
        self.configure_table(columns=[...])
        self.configure_filters([...])
        self.configure_actions([...])
```

**Responsabilidades BaseScreen:**
- Layout consistente (header, filtros, tabela, footer)
- Gestão de DataTableV2
- Filtros e pesquisa
- Context menus
- Ações CRUD (criar, editar, eliminar)
- Paginação
- Atalhos de teclado

### Fase 2: BaseForm (Após Validação Screens)

**Objetivo:** Criar template base para forms de criação/edição.

**Localização:** `ui/components/base_form.py`

**Forms Alvo:**
- ProjetoForm
- OrcamentoForm
- DespesaForm
- BoletimForm

**Sintaxe:**
```python
from ui.components.base_form import BaseForm

class ProjectForm(BaseForm):
    def __init__(self, parent, projeto=None):
        super().__init__(parent)
        self.define_fields([...])
        self.define_validations([...])
        self.configure_layout()
```

**Responsabilidades BaseForm:**
- Layout de campos (grid, sections)
- Validações centralizadas
- Tooltips e help text
- Popups de confirmação
- Botões padrão (Guardar, Cancelar)
- Gestão de estado (novo/editar)
- Handlers de eventos

### Princípios de Design

#### 1. Componentização via Slots
```python
class BaseScreen:
    def get_header_slot(self):
        """Override para header customizado"""
        pass

    def get_filter_slot(self):
        """Override para filtros específicos"""
        pass

    def get_action_buttons(self):
        """Override para botões de ação"""
        return ["Novo", "Editar", "Eliminar"]
```

#### 2. Configuração por Instância
```python
class DespesasScreen(BaseScreen):
    table_config = {
        "columns": [...],
        "sortable": True,
        "filterable": True
    }

    filter_config = {
        "date_range": True,
        "search": True,
        "estado": ["PAGO", "PENDENTE"]
    }
```

#### 3. Lógica Comum Centralizada
- Tooltips automáticos
- Handlers de teclado (Ctrl+N, Ctrl+S, Delete)
- Popovers de ajuda
- Validação básica (campos obrigatórios, formatos)
- Gestão de loading states

#### 4. Extensibilidade
- Hooks para antes/depois de ações
- Eventos customizáveis
- Sem breaking changes em expansões futuras

### Benefícios Esperados

1. **Consistência** - Todas as screens seguem mesmo padrão
2. **Manutenção** - Correções aplicam-se a todas as screens
3. **Produtividade** - Novas screens em minutos, não horas
4. **UX** - Comportamento previsível para utilizador

### Roadmap

| Fase | Componente | Status | Estimativa |
|------|------------|--------|------------|
| 1.1 | BaseScreen scaffold | 📋 Planeado | - |
| 1.2 | Migrar ProjectsScreen | 📋 Planeado | - |
| 1.3 | Migrar restantes screens | 📋 Planeado | - |
| 2.1 | BaseForm scaffold | 📋 Futuro | - |
| 2.2 | Migrar forms | 📋 Futuro | - |

### Notas de Implementação

- Manter compatibilidade com screens existentes durante migração
- Testes manuais após cada screen migrada
- Documentar breaking changes se necessário
- Considerar sistema de themes/cores no futuro

---

## Estrutura Atual UI

```
ui/
├── main_window.py           # Janela principal
├── screens/                  # 10 screens
│   ├── dashboard.py
│   ├── projetos.py
│   ├── orcamentos.py
│   ├── despesas.py
│   ├── boletins.py
│   ├── clientes.py
│   ├── fornecedores.py
│   ├── equipamento.py
│   ├── relatorios.py
│   └── saldos.py
├── components/               # Componentes reutilizáveis
│   ├── base_screen.py       # [FUTURO] Template screens
│   ├── base_form.py         # [FUTURO] Template forms
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

**Ver também:**
- `memory/ARCHITECTURE.md` - Arquitetura geral
- `memory/DECISIONS.md` - Decisões técnicas
