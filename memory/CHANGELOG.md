# 📝 Changelog - Agora Contabilidade

Registo de mudanças significativas no projeto.

---

## [2025-11-13] Sistema de Templates de Despesas Recorrentes

### ✨ Adicionado
- 🔁 **Sistema de Templates de Despesas Recorrentes**
  - Tabela separada `despesa_templates` para moldes de despesas fixas mensais
  - Template ID único: formato #TD000001, #TD000002, etc.
  - Templates armazenam dia do mês (1-31) em vez de data completa
  - Templates NÃO entram em cálculos financeiros
  - Geração automática de despesas mensais a partir de templates
  - Link entre despesas geradas e template de origem (FK)
- 🎨 **UI para Templates de Despesas**
  - Screen dedicado `TemplatesDespesasScreen` com CRUD completo
  - Botão "📝 Editar Recorrentes" no screen Despesas
  - Janela modal para gestão de templates (1000x700px)
  - FormularioTemplateDialog com validação de dia do mês (1-31)
  - Barra de seleção com botão "Apagar Selecionados"
  - Info text explicando que templates não são despesas reais
- ✨ **Indicadores Visuais**
  - Asterisco (*) no tipo quando despesa foi gerada de template (ex: "Fixa Mensal*")
  - Botão "🗑️ Apagar Selecionadas" em Despesas e Templates
  - Confirmação especial ao apagar despesas geradas de templates
  - Aviso: despesas apagadas não serão recriadas automaticamente
- 🔄 **Lógica de Geração Automática**
  - Botão "🔁 Gerar Recorrentes" gera despesas do mês atual
  - Verifica se despesa já foi gerada para evitar duplicados
  - Tratamento inteligente de meses com diferentes dias (Feb 31 → Feb 28/29)
  - Mantém link template-despesa via `despesa_template_id`

### 🐛 Corrigido
- **ValueError:** `['show_actions', 'on_edit', 'on_delete'] are not supported arguments`
  - DataTableV2 não suporta parâmetros show_actions, on_edit, on_delete
  - Solução: Botão "Apagar Selecionadas" na barra de seleção
  - Mantido double-click para editar (on_row_double_click)
  - Interface consistente entre Despesas e Templates

### ♻️ Refatorado
- **Migração do sistema de recorrência**
  - ANTES: Campos `is_recorrente` e `dia_recorrencia` na tabela despesas
  - DEPOIS: Tabela separada `despesa_templates` (arquitetura mais limpa)
  - Separação clara: Templates vs Despesas Reais
  - Migration 014: Criar tabela despesa_templates
  - Migration 015: Remover campos obsoletos de recorrência de despesas
- **DespesasManager refatorado**
  - Método `gerar_despesas_recorrentes_mes()` agora usa DespesaTemplate
  - Removidos parâmetros is_recorrente/dia_recorrencia de criar() e atualizar()
  - FK despesa_template_id agora aponta para despesa_templates.id
- **UI de Despesas limpa**
  - Removidos 100+ linhas de código de recorrência do FormularioDespesaDialog
  - Removidos campos checkbox e dia_recorrencia do formulário
  - Interface mais simples e focada

### 📦 Commits
- `dcf5a9c` - 🔄 Refactor: Sistema de Templates de Despesas Recorrentes (Parte 1/2)
- `898a18d` - ♻️ Refactor: Atualizar DespesasManager para usar templates (Parte 2a)
- `04f333c` - ♻️ Refactor: Remover campos obsoletos de recorrência (Parte 2b)
- `48ae2ca` - ✨ Feature: UI completa para Templates de Despesas Recorrentes
- `f6d1a7f` - 🐛 Fix: Corrigir parâmetros inválidos do DataTableV2

### 📝 Ficheiros Criados
- `database/models/despesa_template.py` - Model DespesaTemplate
- `database/migrations/014_create_despesa_templates.py` - Criar tabela templates
- `database/migrations/015_remove_recorrencia_from_despesas.py` - Limpar despesas
- `logic/despesa_templates.py` - DespesaTemplatesManager com CRUD
- `ui/screens/templates_despesas.py` - Screen e dialog de templates (450+ linhas)
- `run_migration_014.py` - Script para aplicar migration 014
- `run_migration_015.py` - Script para aplicar migration 015

### 📝 Ficheiros Alterados
- `database/models/despesa.py` - FK agora aponta para despesa_templates
- `logic/despesas.py` - Refatorado para usar templates
- `ui/screens/despesas.py` - UI limpa + botões de gestão

### 🎯 Benefícios
- ✅ Separação clara entre templates e despesas reais
- ✅ Templates podem ser editados/deletados sem afetar despesas já geradas
- ✅ Rastreabilidade: despesas sabem de qual template vieram
- ✅ Não há duplicação de lógica de recorrência
- ✅ Interface intuitiva e profissional

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
- 🎨 **Date Pickers em TODOS os screens CRUD**
  - **Projetos:** Campo "Período do Projeto" único (DateRangePickerDropdown)
    - Substituído dois campos separados (Data Início + Data Fim)
    - Layout mais limpo e intuitivo
    - Formato inteligente no display
  - **Despesas:** DatePickerDropdown para "Data" e "Data Pagamento"
  - **Boletins:** DatePickerDropdown para "Data Emissão" (default=hoje)
  - **Orçamentos:** Substituídos antigos DatePickerEntry e DateRangePicker
  - **Equipamento:** DatePickerDropdown para "Data Compra"
  - **Fornecedores:** DatePickerDropdown para "Validade Seguro Trabalho"
- 🎨 **Fornecedores: Campo Website com Link Clicável**
  - Campo de texto para URL do website
  - Botão "🔗 Abrir" que abre URL no browser
  - Adiciona automaticamente `https://` se necessário
  - Integrado com módulo `webbrowser` do Python
- 🎨 **Fornecedores: Seguro visível apenas para FREELANCER**
  - Campo "Validade Seguro Trabalho" só aparece se Estatuto = FREELANCER
  - Toggle dinâmico ao mudar radio buttons de estatuto
  - Método `_toggle_seguro_field()` com pack/pack_forget

### 🐛 Corrigido
- **AttributeError:** `'str' object has no attribute 'winfo_children'`
  - Adicionado `isinstance(widget, str)` check no `_check_click_outside()`
  - Proteção com `hasattr()` antes de chamar métodos de widget
- **ValueError:** `'width' and 'height' must be passed to constructor`
  - Movido `width` e `height` do `place()` para o construtor do `CTkFrame`
  - Compliance com constraints do CustomTkinter
- **ImportError:** `cannot import name 'engine' from 'database.models.base'`
  - Script `run_migration_012.py` tentava importar engine não exportado
  - Corrigido: engine criado localmente com `create_engine()`
  - Carrega DATABASE_URL do .env com fallback
- **TypeError:** `FornecedoresManager.atualizar() got an unexpected keyword argument 'website'`
  - Parâmetro `website` não estava nos métodos `criar()` e `atualizar()`
  - Adicionado parâmetro em ambos os métodos
  - Incluída lógica de criação e update do campo website
- **TclError:** `window isn't packed` ao fazer toggle de seguro_frame
  - Pack inicial do seguro_frame causava conflito com toggle
  - Removido pack() inicial, agora controlado apenas por `_toggle_seguro_field()`
  - Corrigido `before=self.nota_entry.master` para `before=self.nota_entry`

### 📝 Ficheiros Alterados
- `ui/components/date_picker_dropdown.py` - Bug fixes e comentários
- `ui/components/date_range_picker_dropdown.py` - Formato inteligente + bug fixes
- `ui/screens/projetos.py` - Campo "Período do Projeto" único
- `ui/screens/despesas.py` - DatePickerDropdown para Data e Data Pagamento
- `ui/screens/boletins.py` - DatePickerDropdown para Data Emissão
- `ui/screens/orcamentos.py` - Substituir antigos date pickers
- `ui/screens/equipamento.py` - DatePickerDropdown para Data Compra
- `ui/screens/fornecedores.py` - Website clicável + Seguro dinâmico + Bug fixes
- `logic/fornecedores.py` - Adicionado parâmetro website aos métodos criar/atualizar
- `database/models/fornecedor.py` - Adicionada coluna `website`
- `database/migrations/012_add_website_to_fornecedor.py` - Migration criada
- `run_migration_012.py` - Script de migration corrigido

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
