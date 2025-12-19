# 🐛 BUGS - Agora Contabilidade

Documentação de bugs ativos e resolvidos do projeto.

---

## 🔴 BUGS ATIVOS

### 🟢 Nenhum Bug Crítico Ativo

---

## ✅ BUGS RESOLVIDOS

### BUG-001: BaseScreen - Toolbar Gigante Causava Espaçamento Excessivo

**Data Identificado:** 24/11/2025
**Data Resolvido:** 25/11/2025
**Severidade:** 🔴 CRÍTICA
**Prioridade:** URGENTE
**Status:** ✅ RESOLVIDO (commit 313aa0f)

**Afeta:**
- `ui/components/base_screen.py`
- `ui/screens/projetos.py` (herda de BaseScreen)
- Futuros screens que herdem BaseScreen

**Descrição:**

Sistema de chips para mostrar filtros ativos e pesquisa não funciona corretamente. Dois problemas simultâneos:

1. **Chips Invisíveis:** Chips de filtros/pesquisa não aparecem visualmente apesar de serem criados no código
2. **Espaçamento Excessivo:** Gap de ~80-100px entre toolbar e tabela mesmo sem chips ativos

**Reprodução:**

```python
# 1. Abrir ProjectsScreen
# 2. Selecionar filtro (ex: "Empresa BA")
# 3. Observar:
#    - Chip azul deveria aparecer abaixo da toolbar
#    - ❌ RESULTADO: Chip não aparece
#    - ❌ RESULTADO: Espaço vazio gigante entre toolbar e tabela

# 4. Digitar na pesquisa (ex: "digital")
# 5. Observar:
#    - Chip verde deveria aparecer com "🔍 digital"
#    - ❌ RESULTADO: Chip não aparece
#    - ❌ RESULTADO: Espaço permanece
```

**Comportamento Esperado:**

```
╔════════════════════════════════╗
║  📁 Projetos    [Novo]         ║  ← Header
║  🔍 [search] [Tipo] [Estado]   ║  ← Toolbar (pady=5,0)
║  🔍 digital  [Empresa BA]      ║  ← Chips (pady=5,0) VISÍVEIS
║  ┌──────────────────────────┐  ║  ← Tabela (COLA nos chips)
║  │ #P0022 | ...              │  ║
╚════════════════════════════════╝
```

**Comportamento Real:**

```
╔════════════════════════════════╗
║  📁 Projetos    [Novo]         ║  ← Header
║  🔍 [search] [Tipo] [Estado]   ║  ← Toolbar
║                                 ║
║         [ESPAÇO VAZIO]          ║  ← ~80-100px GAP
║                                 ║
║  ┌──────────────────────────┐  ║  ← Tabela (longe da toolbar)
║  │ #P0022 | ...              │  ║
╚════════════════════════════════╝
```

**Histórico de Tentativas de Fix:**

| # | Commit  | Abordagem | Resultado |
|---|---------|-----------|-----------|
| 1 | b10b77a | Reduzir pady header/toolbar | ❌ Melhorou mas espaço existe |
| 2 | 9b7024e | Ajustar chips e barra ações | ❌ Chips invisíveis |
| 3-4 | 324ca8c, f22a8d1 | Padding + indicadores | ❌ Espaço visível |
| 5 | 57fd530 | Evitar chips push tabela | ❌ Invisíveis |
| 6 | c71d8b4 | place() overlays absolutos | ❌ Chips sumiram |
| 7 | 69f0470 | lift() para z-order | ❌ Ainda invisíveis |
| 8 | 7865f70 | Reverter para pack() | ❌ Espaço voltou |
| 9 | 84f66b0 | Pack condicional | ❌ ATUAL (não funciona) |

**Código Atual (Não Funcional):**

```python
# ui/components/base_screen.py

def _create_layout(self):
    self._create_header()
    self._create_toolbar()
    self._create_chips_area()     # Cria containers SEM pack
    self._create_selection_bar()  # Cria containers SEM pack
    self._create_table()

def _create_chips_area(self):
    # Container NÃO faz pack no init
    self.chips_container = ctk.CTkFrame(self, fg_color="transparent")
    self.chips_frame = ctk.CTkFrame(self.chips_container, fg_color="transparent")

def _add_filter_chip(self, filter_key: str, value: str):
    # Pack container quando adicionar primeiro chip
    if not self.chips_container.winfo_manager():
        self.chips_container.pack(
            fill="x",
            padx=30,
            pady=0,
            before=self.selection_container  # ⚠️ POSSÍVEL PROBLEMA
        )

    if not self.chips_frame.winfo_manager():
        self.chips_frame.pack(fill="x", pady=(5, 0))

    # Criar chip visual...
```

**Problemas Identificados:**

1. **`before=self.selection_container`:**
   - selection_container também não faz pack no init
   - Pode não existir como widget "manager" quando referenciado
   - Tkinter pode rejeitar silenciosamente o before se widget não estiver no layout

2. **Race Conditions:**
   - Ordem de criação: chips_area → selection_bar → table
   - Mas pack condicional pode quebrar essa ordem
   - selection_container pode fazer pack ANTES de chips_container

3. **pady=(5, 0) ainda cria espaço:**
   - Mesmo com container escondido, frame interno tem padding
   - Pode estar a reservar espaço invisível

4. **winfo_manager() pode retornar None incorretamente:**
   - Widget pode estar "criado" mas não "gerenciado"
   - Condição if pode não funcionar como esperado

**Investigações Necessárias (Próxima Sessão):**

```python
# 1. Debug Visual - Adicionar cores de fundo
self.chips_container.configure(fg_color="red")  # Verificar se renderiza
self.chips_frame.configure(fg_color="blue")     # Verificar se existe

# 2. Debug Console - Print estados
print(f"Container managed: {self.chips_container.winfo_manager()}")
print(f"Frame managed: {self.chips_frame.winfo_manager()}")
print(f"Container height: {self.chips_container.winfo_height()}")

# 3. Teste sem before parameter
self.chips_container.pack(fill="x", padx=30, pady=0)  # SEM before=

# 4. Verificar ordem no _create_layout
# Mover table PARA CIMA antes dos containers?

# 5. Alternativa - Grid layout
self.chips_container.grid(row=2, column=0, sticky="ew")

# 6. Alternativa - Containers sempre visíveis com height=0
self.chips_container.pack(fill="x", padx=30, pady=0)
self.chips_container.configure(height=0)  # Escondido mas no layout
# Depois configure(height=40) quando adicionar chips
```

**Soluções Alternativas a Considerar:**

1. **Grid Layout em vez de Pack:**
   ```python
   # Usar grid() para controle preciso de posicionamento
   header.grid(row=0)
   toolbar.grid(row=1)
   chips.grid(row=2)  # Pode ter height=0
   table.grid(row=3)
   ```

2. **Containers Sempre Visíveis com height=0:**
   ```python
   # Pack containers no init com height=0
   self.chips_container.pack(fill="x", padx=30, pady=0)
   self.chips_container.configure(height=0)

   # Quando adicionar chip: configure(height=40)
   # Quando remover último: configure(height=0)
   ```

3. **Separador Visual (Workaround):**
   ```python
   # Adicionar separador fino entre toolbar e tabela
   # Pelo menos elimina espaço vazio visualmente
   separator = ctk.CTkFrame(self, height=1, fg_color="gray")
   separator.pack(fill="x", padx=30, pady=5)
   ```

**Screenshots:**
- Ver `screenshots/Captura de ecrã 2025-11-24, às 20.08.33.png`
- Ver `screenshots/Captura de ecrã 2025-11-24, às 20.33.26.png`
- Ver `screenshots/Captura de ecrã 2025-11-24, às 20.33.41.png`

**Links:**
- Ver: memory/CHANGELOG.md (24/11/2025 20:00-20:40)
- Ver: memory/UI_ARCHITECTURE.md (Secção BaseScreen)

**Impacto no Projeto:**

- 🔴 Bloqueia user experience adequada em ProjectsScreen
- 🔴 Bloqueia migração de outros screens (Orçamentos, Despesas, Boletins)
- 🟡 Reduz confiança na arquitetura BaseScreen
- 🟡 10 commits desperdiçados em tentativas iterativas

**Prioridade Justificação:**

Este bug é CRÍTICO porque afeta a funcionalidade core do sistema de templates UI que foi desenvolvida nesta sessão. Sem chips visíveis e com espaçamento excessivo, a UX está degradada e o sistema não pode ser expandido para outros screens.

---

### ✅ SOLUÇÃO IMPLEMENTADA (25/11/2025)

**Diagnóstico Final (Debug Visual):**

Implementado debug com cores temporárias:
```python
header_frame = ctk.CTkFrame(self, fg_color="blue")
toolbar = ctk.CTkFrame(self, fg_color="red")           # ← CULPADO!
chips_container = ctk.CTkFrame(self, fg_color="green")
selection_container = ctk.CTkFrame(self, fg_color="yellow")
```

Screenshot revelou: **Toolbar VERMELHO estava ~150-200px de altura em vez de ~35-40px**

**ROOT CAUSE:**
```python
# PROBLEMA:
toolbar = ctk.CTkFrame(self, fg_color="red")
toolbar.pack(fill="x", padx=30, pady=(0, 10))
# ^^^ SEM height control! Frame expandia verticalmente sem limite
```

**FIX IMPLEMENTADO (commit 313aa0f):**
```python
# SOLUÇÃO:
toolbar = ctk.CTkFrame(self, fg_color="transparent", height=40)
toolbar.pack(fill="x", padx=30, pady=(0, 10))
toolbar.pack_propagate(False)  # ← Previne expansão automática
```

**Mudanças Completas:**
1. Toolbar: `height=40` fixo + `pack_propagate(False)`
2. Chips container: `height=40` fixo (já estava, mantido)
3. Selection bar: `height=50` fixo (já estava, mantido)
4. Removidas cores debug

**Resultado:**
✅ Toolbar com altura normal (~40px)
✅ Espaçamento compacto (~30px entre título e pesquisa)
✅ Chips visíveis quando adicionados
✅ Tabela estável (não é empurrada)

**Lição Aprendida:**
- Debug visual com cores é EXTREMAMENTE eficaz para identificar problemas de layout
- pack_propagate(False) é essencial para containers com height fixo
- 9 tentativas sem debug visual vs 1 tentativa com debug = debug sempre!

**Ver Detalhes Completos:**
- memory/CHANGELOG.md (25/11/2025) - Processo completo de resolução
- screenshots/ (04.27.10.png) - Screenshot diagnóstico

---

**Mantido por:** Equipa Agora
**Última Atualização:** 25/11/2025 04:30 WET
