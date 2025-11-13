# 📝 Changelog - Agora Contabilidade

Registo de mudanças significativas no projeto.

---

## [2025-11-13] Date Pickers Profissionais com Formato Inteligente

### ✨ Adicionado
- 🎨 **DatePickerDropdown** - Calendário inline para seleção de data única
  - Calendário visual com navegação mês/ano
  - Click outside para fechar
  - Integração com CustomTkinter
- 🎨 **DateRangePickerDropdown** - Seleção de período com formato inteligente
  - Formato compacto baseado no contexto:
    - Mesmo mês: `15-20/11/2025`
    - Meses diferentes (mesmo ano): `28/11-05/12/2025`
    - Anos diferentes: `28/12/2024-05/01/2025`
  - Seleção visual de início e fim
  - Range destacado visualmente no calendário
  - Botões "Limpar" e "Confirmar"
- 🎨 **Projetos: Campo "Período do Projeto"**
  - Substituído dois campos separados (Data Início + Data Fim) por um único DateRangePickerDropdown
  - Layout mais limpo e intuitivo
  - Formato inteligente no display

### 🐛 Corrigido
- **AttributeError:** `'str' object has no attribute 'winfo_children'`
  - Adicionado `isinstance(widget, str)` check no `_check_click_outside()`
  - Proteção com `hasattr()` antes de chamar métodos de widget
- **ValueError:** `'width' and 'height' must be passed to constructor`
  - Movido `width` e `height` do `place()` para o construtor do `CTkFrame`
  - Compliance com constraints do CustomTkinter

### 📝 Ficheiros Alterados
- `ui/components/date_picker_dropdown.py` - Bug fixes e comentários
- `ui/components/date_range_picker_dropdown.py` - Formato inteligente + bug fixes
- `ui/screens/projetos.py` - Campo "Período do Projeto" único

### 🔧 Documentação
- Atualizado `SESSION_IMPORT.md` - Workflow mais claro com fluxograma
- Atualizado `memory/README.md` - Sistema de "frase-chave" para atualizar docs
- Atualizado `README.md` - Frase Mágica v2.0 (ordem garantida)

---

## [2025-11-11] Navegação Clicável em Saldos Pessoais

### ✨ Adicionado
- 🎨 **Navegação clicável completa em Saldos Pessoais**
  - 10 botões clicáveis com navegação automática e filtros aplicados
  - INs: Projetos Pessoais, Prémios (para cada sócio)
  - OUTs: Despesas Fixas, Boletins Pendentes, Boletins Pagos, Despesas Pessoais
- 🎨 **Cores semânticas consistentes**
  - Verde (#E8F5E0/#4A7028) para INs - match Recebido
  - Laranja (#FFE5D0/#8B4513) para OUTs - match Não Faturado
- 🖼️ **Ícones PNG customizados**
  - ins.png e outs.png (convertidos para Base64)
  - Substituem emojis 💰 e 💸
- ✨ **Efeitos hover profissionais**
  - Border width aumenta 2→3 pixels
  - Cursor hand2 em toda a extensão do card
  - Texto branco para melhor contraste

### 🔧 Alterado
- **Boletins** separados em duas linhas: "Boletins pendentes" e "Boletins pagos"
- **Títulos** simplificados: "INs (Entradas)" → "INs" e "OUTs (Saídas)" → "OUTs"
- **TOTAL** sem bullet point (separadores visuais em vez de "• TOTAL")
- Filtros propagados para Projetos, Despesas, Boletins (filtro_tipo, filtro_premio_socio, filtro_estado, filtro_socio)

### 🐛 Problemas Identificados
- **Scroll em popup de Projetos** propaga para lista por trás
  - Múltiplas tentativas: bind_all, event detection, unbind parent
  - Código implementado mas ainda não resolvido
  - Documentado em memory/TODO.md como Alta Prioridade

### 📝 Ficheiros Alterados
- `ui/screens/saldos.py` - Navegação, cores, ícones, boletins separados
- `logic/saldos.py` - Boletins separados em pendentes/pagos
- `assets/resources.py` - Novos ícones INS e OUTS (Base64)
- `ui/main_window.py` - Propagação de filtros (show_projetos, show_despesas, show_boletins)
- `ui/screens/projetos.py` - Tentativa de fix para scroll no popup
- `ui/screens/despesas.py` - Suporte para filtro_tipo
- `ui/screens/boletins.py` - Suporte para filtro_socio

---

## [2025-11-09] Sistema de Memória & Ícones Completo

### ✨ Adicionado
- 🧠 **Sistema de Memória** completo em `/memory/`
  - `CURRENT_STATE.md` - estado atual do projeto
  - `ARCHITECTURE.md` - arquitetura detalhada
  - `DECISIONS.md` - decisões técnicas registadas
  - `CHANGELOG.md` - este ficheiro
  - `README.md` - guia do sistema de memória
- 🎨 **Ícones PNG aplicados a TODAS as screens**
  - Dashboard, Saldos, Projetos, Orçamentos, Despesas
  - Boletins, Clientes, Fornecedores, Equipamento, Relatórios
- 🖼️ **Logos PNG de alta qualidade** (fornecidos manualmente)
  - 71KB e 156KB (muito melhor que os 4KB-17KB anteriores)
  - Sistema de PNGs manuais (não conversão automática)

### 🔧 Alterado
- Movidos ficheiros de dev para `/memory/`
  - `GUIA_COMPLETO.md`
  - `PLANO_ORCAMENTOS.md`
  - `TODO.md`
  - `BUILD_ASSETS_README.md` → `ASSET_SYSTEM.md`
- Sistema de assets simplificado (PNGs manuais)

### 🗑️ Removido
- Scripts de conversão automática SVG→PNG
  - `extract_logo_png.py`
  - `build_assets.py` → deprecado para `_build_assets.py.deprecated`
- `logo_original.png` (temporário, não necessário)

---

## [2025-11-08] Sistema de Ícones Base64

### ✨ Adicionado
- Sistema de ícones PNG embutidos como Base64
- Ícones aplicados na sidebar (10 menus)
- Conversão automática Excel→Base64 (`convert_icons_to_base64.py`)
- 10 ícones PNG profissionais

### 🔧 Alterado
- Sidebar usa ícones PNG em vez de emojis
- Sistema de fallback para ícones (Base64 → Emoji)

---

## [2025-11-07] Importação de Dados Legados

### ✨ Adicionado
- Script de importação Excel → SQLite
- Mapeamento de dados antigos para novo schema
- Validações e limpeza de dados
- Documentação em `IMPORTACAO_*.md`

### 🐛 Corrigido
- Encoding issues com dados portugueses
- Conversão de datas inconsistentes
- Valores decimais com vírgula vs ponto

---

## [2025-11-06] Sistema de Orçamentos

### ✨ Adicionado
- Model `Orcamento` com versões
- Screen de gestão de orçamentos
- Estados: Pendente, Aprovado, Rejeitado
- Integração com Clientes

### 📝 Documentação
- `PLANO_ORCAMENTOS.md` - plano completo da feature

---

## [2025-11-05] Core Features Completas

### ✨ Adicionado
- **Saldos Pessoais** (CORE) - cálculo 50/50
- **Projetos** - gestão completa
- **Despesas** - gestão completa
- **Boletins** - gestão completa
- **Clientes** - gestão completa
- **Fornecedores** - gestão completa
- **Relatórios** - exportação Excel

### 🔧 Alterado
- DataTable V2 - componente melhorado
- Forms reutilizáveis

---

## [2025-11-04] Setup Inicial

### ✨ Adicionado
- Estrutura base do projeto
- SQLAlchemy + Alembic
- CustomTkinter UI
- Models base: Sócio, Projeto, Despesa, Boletim
- Dashboard inicial

### 📝 Documentação
- `README.md` - setup e uso básico
- `GUIA_COMPLETO.md` - documentação detalhada

---

## Formato

Seguimos [Keep a Changelog](https://keepachangelog.com/):
- **Adicionado** - novas features
- **Alterado** - mudanças em features existentes
- **Deprecado** - features que serão removidas
- **Removido** - features removidas
- **Corrigido** - bug fixes
- **Segurança** - vulnerabilidades

---

**Mantido por:** Equipa Agora
