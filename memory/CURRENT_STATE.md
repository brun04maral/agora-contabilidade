# 📊 Estado Atual do Projeto - Agora Contabilidade

**Última atualização:** 2025-11-13
**Sessão:** claude/merge-context-update-011CV57sbRiu7taAq2DCiwhA

---

## 🚨 IMPORTANTE - Nova Sessão Claude Code?

**SE ESTA É UMA NOVA SESSÃO:** O novo branch foi criado do `main` (desatualizado). O código atualizado está no branch da sessão anterior!

**FRASE MÁGICA - Usa sempre:**
```
Esta sessão é continuação de uma anterior. Faz merge do branch da última sessão para este branch atual para teres todo o código e contexto atualizado. Depois lê o README.md e memory/CURRENT_STATE.md para contexto completo.
```

**Isto vai:** Fazer merge do branch anterior + Ler documentação = Contexto completo!

**Instruções completas:** Ver `/SESSION_IMPORT.md` na raiz do projeto.

---

## ✅ Features Completas e Funcionais

### 🎨 Sistema de Assets e Ícones (COMPLETO)
- ✅ Ícones PNG Base64 embutidos no código (11 ícones disponíveis)
- ✅ Sistema de fallback: SVG → PNG → Emoji
- ✅ Logos PNG de alta qualidade fornecidos manualmente (71KB, 156KB)
- ✅ Ícones aplicados em:
  - Sidebar (10 menus + Info) - 27x27 pixels
  - Títulos de todas as screens (10 screens) - 22x22 pixels
  - Dashboard com ícones nas secções (5 secções)
- ✅ Documentação em `memory/ASSET_SYSTEM.md`

### 💾 Sistema de Base de Dados (COMPLETO)
- ✅ SQLAlchemy ORM com SQLite
- ✅ Migrations com Alembic
- ✅ Modelos: Sócio, Projeto, Despesa, Boletim, Cliente, Fornecedor, Orçamento, Equipamento
- ✅ Relacionamentos e constraints
- ✅ Seed data para desenvolvimento

### 🖥️ Interface Gráfica (COMPLETO)
- ✅ CustomTkinter (tema moderno)
- ✅ 10 screens funcionais + Info screen:
  - Dashboard (com ícones nas secções + navegação interativa em cards)
  - Saldos Pessoais (CORE) - **Com navegação clicável completa**
    - 10 botões clicáveis com filtros automáticos (Projetos, Prémios, Despesas, Boletins)
    - Cores semânticas: Verde para INs, Laranja para OUTs
    - Ícones PNG customizados (ins.png, outs.png)
    - Boletins separados (Pendentes e Pagos)
  - Projetos
  - Orçamentos
  - Despesas
  - Boletins
  - Clientes
  - Fornecedores
  - Equipamento
  - Relatórios
  - Info (versão v0.0.1, créditos)
- ✅ Componentes reutilizáveis (DataTableV2, forms)
- ✅ **Date Pickers Profissionais** (NOVO 13/11)
  - `DatePickerDropdown` - Seleção de data única com calendário inline
  - `DateRangePickerDropdown` - Seleção de período com formato inteligente:
    - Mesmo mês: `15-20/11/2025`
    - Meses diferentes: `28/11-05/12/2025`
    - Anos diferentes: `28/12/2024-05/01/2025`
  - Usado em **todos os 6 screens CRUD:** Projetos, Despesas, Boletins, Orçamentos, Equipamento, Fornecedores
  - Calendário visual com navegação mês/ano
  - Proteção contra bugs (widget string, CustomTkinter constraints)
- ✅ **Fornecedores: Enhancements** (NOVO 13/11)
  - **Website clicável:** Campo de texto + botão "🔗 Abrir" que abre URL no browser
  - **Seguro dinâmico:** Campo "Validade Seguro Trabalho" só visível para FREELANCER
  - Migration 012 aplicada (coluna `website` adicionada)
- ✅ Sidebar com scroll vertical
  - Logo fixo no topo
  - Menus scrollable (27x27 icons)
  - Info e Sair fixos no fundo
  - Separador visual
- ✅ Navegação intuitiva e profissional

### 💰 Lógica de Negócio (COMPLETO)
- ✅ Cálculo de saldos pessoais (50/50)
- ✅ Gestão de projetos (tipos, estados, prémios)
- ✅ Gestão de despesas (tipos, pagamentos)
- ✅ **Sistema de Templates de Despesas Recorrentes** (NOVO 13/11)
  - Tabela separada `despesa_templates` para moldes de despesas fixas mensais
  - Template ID único: #TD000001, #TD000002, etc.
  - Templates armazenam dia do mês (1-31) em vez de data completa
  - Geração automática mensal via botão "🔁 Gerar Recorrentes"
  - Indicador visual: asterisco (*) em despesas geradas (ex: "Fixa Mensal*")
  - Screen dedicado com CRUD completo (acesso via "📝 Editar Recorrentes")
  - Templates NÃO entram em cálculos financeiros
  - Link rastreável entre template e despesas geradas
- ✅ Gestão de boletins (cálculos automáticos)
- ✅ Sistema de orçamentos (versões, aprovações)
- ✅ Relatórios exportáveis (Excel)

### 📦 Importação de Dados (COMPLETO)
- ✅ Script de importação Excel → SQLite
- ✅ Mapeamento de dados antigos
- ✅ Validações e limpeza
- ✅ Documentação em `memory/archive/importacao/`

### 🧠 Sistema de Documentação e Organização (COMPLETO)
- ✅ Pasta `memory/` com documentação estruturada:
  - CURRENT_STATE.md (estado atual)
  - TODO.md (tarefas priorizadas)
  - ARCHITECTURE.md (arquitetura)
  - DECISIONS.md (decisões técnicas)
  - DATABASE_SCHEMA.md (esquema DB)
  - DEV_SETUP.md (setup dev)
  - CHANGELOG.md (histórico)
  - GUIA_COMPLETO.md (guia completo)
  - ASSET_SYSTEM.md (assets/ícones)
  - PLANO_ORCAMENTOS.md (plano orçamentos)
  - README.md (índice)
- ✅ `memory/archive/` para documentação histórica
- ✅ README.md raiz com "Frase Mágica" para novas sessões
- ✅ Repositório limpo e organizado

---

## 🚧 Em Desenvolvimento

**Nada atualmente** - Projeto em fase de manutenção e melhorias incrementais

---

## 📝 Próximas Tarefas (ver `TODO.md`)

1. Testes de integração completos
2. Build para Windows (PyInstaller)
3. Documentação de usuário final
4. Backup automático de base de dados

---

## 🐛 Problemas Conhecidos

### Alta Prioridade
- **Scroll em popups modais propaga para lista de fundo** ⏸️ **POSTPONED**
  - **Problema:** Ao fazer scroll em qualquer popup modal (edição/criação), a lista por trás também faz scroll
  - **Comportamento esperado:** Scroll apenas dentro do popup, lista não deve mover
  - **Requerimento crítico:** Trackpad deve funcionar normalmente no popup
  - **Tentativas exaustivas (7+ abordagens testadas em 11/11/2025):**
    1. **Unbind/rebind mousewheel events** - Bloqueou eventos do parent mas desabilitou trackpad no popup
    2. **Smart detection com winfo_toplevel()** - Tentativa de redirecionar eventos para widget correto, mas lista continuou scrollando
    3. **Enter/Leave bindings com bind_all/unbind_all** - Trackpad não funcionou no popup
    4. **Manual scroll redirection com bind_all + "break"** - Quebrou bindings internos do DataTableV2 (TypeError: lambda missing argument)
    5. **Corrigido com add=True em bind_all** - Resolveu erro do DataTableV2 mas lista continuou scrollando
    6. **Bind com "break" diretamente no tree** - Lista continuou scrollando
    7. **bindtags() save/disable/restore** - Desabilitou completamente bindtags do tree durante popup, mas lista continuou scrollando
  - **Decisão final:** Issue postponed após múltiplas tentativas sem sucesso
  - **Razão técnica:** Provável limitação do CustomTkinter/Tkinter com eventos de scroll em modal dialogs. CTkScrollableFrame usa canvas interno que pode estar capturando eventos antes do bind_all.
  - **Ficheiros afetados:** Todos os dialogs modais da aplicação
    - `ui/screens/projetos.py` (FormularioProjetoDialog)
    - `ui/screens/despesas.py` (FormularioDespesaDialog)
    - `ui/screens/boletins.py` (FormularioBoletimDialog)
    - `ui/screens/clientes.py` (FormularioClienteDialog)
    - `ui/screens/fornecedores.py` (FormularioFornecedorDialog)
    - `ui/screens/equipamento.py` (FormularioEquipamentoDialog)
    - `ui/screens/orcamentos.py` (FormularioOrcamentoDialog)
  - **Impacto:** Issue de UX menor que não bloqueia funcionalidades críticas
  - **Próximos passos possíveis:**
    - Pesquisar soluções específicas na comunidade CustomTkinter
    - Investigar eventos internos do CTkScrollableFrame
    - Aguardar updates do framework que possam resolver
    - Considerar implementação de modal overlay completo (solução complexa)
  - **Ver:** `memory/TODO.md` linha 20 para mais detalhes técnicos

### Baixa Prioridade
- Logo SVG contém PNG embutido (não é vetorial verdadeiro)
  - **Solução:** PNGs mantidos manualmente com alta qualidade
  - **Estado:** Resolvido com workaround

---

## 🏗️ Arquitetura Atual

```
agora-contabilidade/
├── main.py                 # Entry point
├── database/              # SQLAlchemy models + migrations
├── logic/                 # Business logic (managers)
├── ui/
│   ├── screens/          # 10 screens principais
│   └── components/       # Componentes reutilizáveis
├── assets/               # Recursos (ícones Base64)
├── media/                # Logos PNG
└── memory/               # 🧠 Esta pasta (documentação dev)
```

---

## 💡 Decisões Técnicas Importantes

1. **Assets:** PNGs mantidos manualmente (não conversão automática)
2. **Ícones:** Base64 embutidos no código (distribuição simples)
3. **DB:** SQLite (simplicidade, backup fácil)
4. **UI:** CustomTkinter (moderno, cross-platform)
5. **Lógica:** Managers separados (testabilidade)

---

## 🎯 Estado Geral: ✅ PRODUÇÃO READY

A aplicação está **funcional e completa** para uso em produção.
Tarefas restantes são melhorias opcionais.
