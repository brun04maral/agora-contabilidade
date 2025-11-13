# 🎯 Decisões Técnicas - Registo

Registo de decisões importantes tomadas durante o desenvolvimento, com contexto e motivação.

---

## 🗄️ Base de Dados

### SQLite vs PostgreSQL/MySQL
**Decisão:** SQLite
**Data:** Início do projeto
**Motivação:**
- Aplicação desktop (não web/server)
- Apenas 2 usuários simultâneos (BA e RR)
- Simplicidade de deployment (ficheiro único)
- Backup trivial (copiar ficheiro)
- Sem necessidade de servidor DB separado

**Trade-offs:**
- ❌ Não escala para múltiplos usuários remotos
- ✅ Perfeitamente adequado para uso local
- ✅ Performance excelente para este caso de uso

---

## 🎨 Interface Gráfica

### Tkinter vs Qt vs Electron
**Decisão:** CustomTkinter (sobre Tkinter)
**Data:** Início do projeto
**Motivação:**
- Tkinter: nativo Python, sem dependências extras
- CustomTkinter: visual moderno (vs Tkinter "antigo")
- Leve: ~5MB empacotado (vs Qt ~50MB, Electron ~100MB)
- Cross-platform: Windows, Mac, Linux

**Trade-offs:**
- ❌ Menos flexível que Qt/Electron
- ✅ Mais que suficiente para necessidades do projeto
- ✅ Desenvolvimento rápido

**Alternativas consideradas:**
- Qt (PyQt5/PySide6): muito pesado
- Electron: requer JavaScript, bundle enorme
- Kivy: mobile-first, não ideal desktop

---

## 📦 Sistema de Assets

### Conversão Automática SVG→PNG vs PNGs Manuais
**Decisão:** PNGs mantidos manualmente
**Data:** 2025-11-09
**Motivação:**
- Logo SVG contém PNG embutido (não é vetorial verdadeiro)
- CairoSVG degradava qualidade na conversão
- Controlo total sobre qualidade final
- Simplicidade (sem dependência Cairo em produção)

**Evolução:**
1. Tentativa inicial: cairosvg converter SVG
   - ❌ Qualidade péssima (logo "ratado")
2. Segunda tentativa: super-sampling + LANCZOS
   - ❌ Ainda não satisfatório
3. **Solução final:** PNGs de alta qualidade manuais
   - ✅ Qualidade perfeita (71KB, 156KB)
   - ✅ Sem dependências extras

**Documentação:** `BUILD_ASSETS_README.md`, `media/logos/README.md`

---

### Ícones: Ficheiros vs Base64 Embutido
**Decisão:** Base64 embutido em código
**Data:** 2025-11-08
**Motivação:**
- Distribuição simplificada (sem pasta icons/)
- Sem problemas de paths em PyInstaller
- Tamanho total ~100KB (aceitável)
- Carregar instantâneo (já em memória)

**Trade-offs:**
- ❌ `resources.py` ficou grande (~5000 linhas)
- ✅ Zero configuração para distribuição
- ✅ Zero problemas de "icon não encontrado"

**Alternativas consideradas:**
- Pasta `icons/` empacotada: problemático com PyInstaller paths
- Resource file (.qrc): requer Qt

---

## 🧮 Lógica de Negócio

### Cálculo de Saldos: 50/50 Fixo
**Decisão:** Divisão 50/50 hard-coded
**Data:** Início do projeto
**Motivação:**
- BA e RR são sócios 50/50 (sociedade por quotas)
- Não há previsão de mudança
- Simplifica código e cálculos

**Se precisar mudar no futuro:**
- Adicionar campo `percentagem` em `Socio`
- Ajustar `SaldosCalculator.calcular_saldos_socios()`

---

### Prémios: Individuais vs Partilhados
**Decisão:** Prémios individuais por projeto
**Data:** Início do projeto
**Motivação:**
- Diferentes sócios têm contribuições diferentes
- Permite reconhecer quem trouxe cliente
- Permite reconhecer esforço extra
- Transparência total entre sócios

**Implementação:**
- `Projeto.premio_bruno` (Decimal)
- `Projeto.premio_rafael` (Decimal)
- Somados no cálculo de saldos

---

## 🔢 Tipos Enumerados

### Enum vs Strings vs Foreign Keys
**Decisão:** Python Enum
**Data:** Início do projeto
**Motivação:**
- Type safety em Python
- Autocomplete no IDE
- Validação automática SQLAlchemy
- Não precisa de tabelas lookup separadas

**Exemplo:**
```python
class TipoProjeto(enum.Enum):
    FRONTEND = "frontend"
    BACKEND = "backend"
    FULLSTACK = "fullstack"
```

**Trade-offs:**
- ❌ Adicionar novo tipo requer migration
- ✅ Valores controlados (não há "frnontend" typo)
- ✅ Código mais limpo

---

## 📊 Exportação de Dados

### Excel vs CSV vs PDF
**Decisão:** Excel (XLSX) primário
**Data:** Início do projeto
**Motivação:**
- Utilizadores familiares com Excel
- Formatação (cores, bordas, fórmulas)
- Múltiplas sheets num ficheiro
- Português tem vírgula decimal (CSV problemático)

**Biblioteca:** `openpyxl`

**CSV disponível** quando:
- Export simples de tabela única
- Integração com outras ferramentas

---

## 🔄 Migrações de Schema

### Alembic vs Manuais
**Decisão:** Alembic
**Data:** Início do projeto
**Motivação:**
- Controlo de versão do schema
- Migrações reversíveis (upgrade/downgrade)
- Autogenerate poupa tempo
- Standard da indústria com SQLAlchemy

**Workflow:**
```bash
# Alterar model
# Gerar migration
alembic revision --autogenerate -m "descrição"
# Aplicar
alembic upgrade head
```

---

## 📝 Gestão de Estado UI

### Refresh Manual vs Auto-refresh
**Decisão:** Refresh manual (botão "Atualizar")
**Data:** Início do projeto
**Motivação:**
- Aplicação local (não multi-user)
- User controla quando ver dados frescos
- Evita queries desnecessárias
- Performance (não polling DB)

**Se precisar auto-refresh:**
- Adicionar `self.after(interval, self.carregar_dados)`
- Configurar intervalo por screen

---

## 🔐 Autenticação

### Sistema de Login vs Sem Login
**Decisão:** SEM login
**Data:** Início do projeto
**Motivação:**
- Apenas 2 usuários (BA e RR)
- Aplicação roda em computador pessoal
- Windows/Mac já têm autenticação de sistema
- Simplicidade de uso

**Se precisar adicionar:**
- Tabela `Usuario`
- Hash passwords (bcrypt)
- Session management

---

## 📦 Distribuição

### PyInstaller vs Outras Ferramentas
**Decisão:** PyInstaller
**Data:** Planeado (não implementado ainda)
**Motivação:**
- Standard para Python GUI apps
- Suporta CustomTkinter
- One-file ou one-folder
- Cross-platform

**Alternativas consideradas:**
- cx_Freeze: menos popular
- py2exe: Windows only
- Nuitka: compilado (complexo)

---

## 🧪 Testes

### Cobertura de Testes
**Decisão:** Testes manuais inicialmente
**Data:** Início do projeto
**Estado:** Em progresso

**Próximo passo:** Testes unitários para Managers
```python
# Exemplo futuro
def test_criar_projeto():
    manager = ProjetosManager(test_db)
    projeto = manager.criar({...})
    assert projeto.id is not None
```

---

## 🔁 Sistema de Recorrência

### Templates Separados vs Campos na Tabela Principal
**Decisão:** Tabela separada `despesa_templates`
**Data:** 2025-11-13
**Motivação:**
- **Separação clara:** Templates não são despesas reais, não devem entrar em cálculos financeiros
- **Rastreabilidade:** FK permite saber quais despesas vieram de qual template
- **Flexibilidade:** Templates podem ser editados/deletados sem afetar histórico
- **Arquitetura limpa:** Cada entidade tem propósito claro

**Evolução:**
1. **Tentativa inicial (Descartada):** Campos `is_recorrente` e `dia_recorrencia` na tabela `despesas`
   - ❌ Mistura conceitos (template vs despesa real)
   - ❌ Dificulta gestão de templates
   - ❌ Confusão na UI (campos de recorrência no formulário de despesas)
2. **Solução final:** Tabela separada `despesa_templates`
   - ✅ Separação total entre moldes e despesas reais
   - ✅ Templates não entram em saldo/relatórios
   - ✅ UI dedicada para gestão de templates
   - ✅ Link rastreável template→despesa via FK

**Implementação:**
- Migration 014: Criar `despesa_templates` (numero, tipo, credor, projeto, descricao, valores, dia_mes, nota)
- Migration 015: Remover `is_recorrente` e `dia_recorrencia` de `despesas`
- FK: `despesas.despesa_template_id` → `despesa_templates.id`
- UI: Screen dedicado via botão "📝 Editar Recorrentes" (modal 1000x700)
- Geração: Botão "🔁 Gerar Recorrentes" cria despesas do mês baseado em templates

**Trade-offs:**
- ❌ Adiciona tabela extra (complexidade schema)
- ✅ Arquitetura mais correta e sustentável
- ✅ Código mais limpo e manutenível
- ✅ UI mais intuitiva

**Benefícios comprovados:**
- Removeu 100+ linhas de código confuso do FormularioDespesaDialog
- Interface mais simples para criar despesas normais
- Templates podem ser geridos independentemente
- Indicador visual claro (asterisco) em despesas geradas

**Aplicável a:** Boletins recorrentes (arquitetura idêntica aplicada)

---

## 🎨 UX: Silent Success vs Explicit Feedback

### Popups de Sucesso vs Feedback Visual
**Decisão:** Remover todos os popups de sucesso
**Data:** 2025-11-13
**Motivação:**
- **Filosofia:** "Silent success, loud failure"
- Popups de sucesso interrompem fluxo de trabalho
- Usuário vê feedback imediato (lista atualizada)
- Apenas erros precisam de atenção explícita

**Implementação:**
- ❌ Removidos: ~24 `messagebox.showinfo("Sucesso", ...)` em 7 screens
- ✅ Mantidos: Todos `messagebox.showerror("Erro", ...)`
- ✅ Feedback: Listas atualizam automaticamente após gravar

**Trade-offs:**
- ❌ Sem confirmação visual explícita de sucesso
- ✅ Workflow 2-3 segundos mais rápido
- ✅ Interface menos intrusiva
- ✅ Mais profissional (padrão em apps modernas)

**Screens afetados:**
- projetos.py, despesas.py, templates_despesas.py, boletins.py
- equipamento.py, orcamentos.py, relatorios.py

---

## 🎨 UI: Strikethrough Seletivo em Tabelas

### Strikethrough via CTkFont vs CSS/Tags
**Decisão:** CTkFont com `overstrike=True` + parâmetro de exclusão
**Data:** 2025-11-13
**Motivação:**
- Projetos anulados precisam de indicação visual clara
- Manter cores de fundo (cinza) + adicionar texto riscado
- Permitir excluir colunas específicas (ex: "Estado")

**Implementação:**
```python
# Row data
data = {
    'id': 1,
    'campo1': 'valor',
    '_strikethrough_except': ['estado']  # Lista de colunas a NÃO riscar
}

# DataTableV2 rendering
should_strikethrough = ('_strikethrough_except' in data and
                       col['key'] not in data['_strikethrough_except'])
font = ctk.CTkFont(size=12, overstrike=should_strikethrough)
```

**Trade-offs:**
- ✅ Controlo granular por coluna
- ✅ Reutilizável em outras tabelas
- ✅ Sem complicações com tags Tkinter
- ❌ Parâmetro especial `_strikethrough_except` em dados

**Aplicável a:** Qualquer tabela que precise de strikethrough condicional

---

## 📋 Boletim Itinerário: Sistema Completo vs Simplificado

### Sistema Completo com Deslocações vs Template Simples
**Decisão:** Sistema completo com múltiplas deslocações
**Data:** 2025-11-13
**Contexto:** Análise de PDF real revelou necessidade de boletim detalhado

**Opções consideradas:**

**OPÇÃO 1 (Descartada):** Template simples
- Template armazena: socio, dia_mes, valor fixo mensal
- Gera boletim com valor total único
- ✅ Rápido (2-3h)
- ❌ Não captura detalhes de deslocações
- ❌ Não reflete realidade do negócio

**OPÇÃO 2 (Escolhida):** Sistema completo de Boletim Itinerário
- Suporte para múltiplas linhas de deslocação
- Cálculos automáticos (ajudas nacional/estrangeiro + kms)
- Dropdown de projetos opcional
- Templates para geração recorrente
- ✅ Reflete realidade do negócio
- ✅ Cálculos automáticos evitam erros
- ✅ Rastreabilidade (deslocação → projeto)
- ❌ Mais complexo (10-15h)

**Sub-decisões:**

1. **Valores de referência (72.65€, 167.07€, 0.40€):**
   - **Decisão:** Tabela separada editável por ano
   - **Razão:** Valores podem mudar anualmente (leis laborais)
   - **Localização:** Botão escondido em configurações

2. **Campo "Dias":**
   - **Decisão:** Inserido manualmente (Decimal)
   - **Razão:** Cálculo complexo (horas trabalhadas, tipo de dia), usuário decide

3. **Horas (início/fim):**
   - **Decisão:** Informativas apenas (Type: Time)
   - **Razão:** Documentação para auditorias, não para cálculo automático

4. **Dados do Sócio (Matrícula, Contribuinte, Categoria):**
   - **Decisão:** Dicionário fixo em Python
   - **Razão:** Dados fixos, usados apenas em PDF, não precisam de BD

5. **Templates - Linhas pré-definidas:**
   - **Decisão:** Cabeçalho vazio (sem linhas)
   - **Nice-to-have:** Pré-preencher com projetos do mês automaticamente
   - **Razão:** Evita complexidade, cada mês é diferente

6. **Relação com Projetos:**
   - **Decisão:** Dropdown opcional em deslocações
   - **Razão:** Maioria das deslocações são por projeto, mas nem todas (ex: reuniões)
   - **FK:** projeto_id NULLABLE, SET NULL se projeto apagado

**Arquitetura resultante:**
- 4 tabelas: valores_referencia_anual, boletins (expandida), boletim_linhas, boletim_templates
- 3 telas novas: valores_referencia.py, boletim_form.py, templates_boletins.py
- 1 tela atualizada: boletins.py (adicionar coluna + botão)

**Benefícios esperados:**
- ✅ Conformidade com formato fiscal exigido
- ✅ Cálculos automáticos (reduz erros)
- ✅ Rastreabilidade projeto → deslocação
- ✅ Templates para automação mensal
- ✅ Escalável para novos requisitos

---

## 💼 Orçamentos → Projetos

### Conversão de Orçamento Aprovado em Projeto
**Decisão:** Botão manual "🔄 Converter em Projeto" (não automático)
**Data:** 13/11/2025
**Status:** 📋 Planeado (não implementado)

**Contexto:**
- Atualmente: Processo totalmente manual
- Quando orçamento é aprovado → criar projeto manualmente copiando dados
- Propenso a erros (esquecer prémios, copiar valores errados)
- Trabalho repetitivo

**Problema a resolver:**
- Repartições de orçamento (BA: €1,500, RR: €800) devem virar prémios do projeto
- Cliente, valor total, descrição devem ser copiados
- Processo atual: ~5 minutos por orçamento, com risco de erro

**Opções consideradas:**

**OPÇÃO 1 (Escolhida):** Botão "🔄 Converter em Projeto"
- **Como funciona:**
  * Botão visível apenas quando `status = 'aprovado'`
  * Click abre dialog de confirmação com preview dos dados
  * Sistema cria projeto automaticamente:
    - Tipo: EMPRESA
    - Cliente: `orcamento.cliente_id`
    - Valor: `orcamento.valor_total`
    - **Prémio BA:** `SUM(reparticoes.valor WHERE entidade='BA')`
    - **Prémio RR:** `SUM(reparticoes.valor WHERE entidade='RR')`
    - Descrição: "Projeto criado a partir do orçamento {codigo}"
    - Data início: data aprovação do orçamento
  * Mostra notificação: "✅ Projeto #P0123 criado com sucesso!"
  * Opcional: Link bidirecional (projeto.orcamento_id ↔ orcamento.projeto_id)
- ✅ Controlo manual (usuário decide quando converter)
- ✅ Preview dos dados antes de criar
- ✅ Evita duplicações acidentais
- ✅ Permite ajustes manuais depois se necessário
- ❌ Requer click extra (mas é intencional)

**OPÇÃO 2 (Rejeitada):** Conversão automática ao aprovar
- Ao mudar status para "aprovado" → cria projeto automaticamente
- ✅ Zero clicks (mais rápido)
- ❌ Menos controlo (pode criar projetos indesejados)
- ❌ Difícil de desfazer se houver erro
- ❌ Usuário pode não estar pronto para criar projeto

**OPÇÃO 3 (Rejeitada):** Manter processo manual
- Sem automação, apenas helper/reminder
- ✅ Controlo total
- ❌ Não resolve problema de erros de cópia
- ❌ Não economiza tempo

**Implementação planeada:**
```python
# logic/orcamentos.py
def converter_em_projeto(self, orcamento_id: int) -> Tuple[bool, Optional[Projeto], Optional[str]]:
    """
    Converte orçamento aprovado em projeto

    1. Verifica se orçamento está aprovado
    2. Verifica se já foi convertido (evitar duplicados)
    3. Calcula prémios somando repartições BA/RR
    4. Cria projeto com dados do orçamento
    5. Opcional: cria link bidirecional
    """
    pass

# ui/screens/orcamentos.py
# Botão visível apenas para status='aprovado'
if orcamento.status == 'aprovado':
    converter_btn = ctk.CTkButton(
        text="🔄 Converter em Projeto",
        command=self.converter_em_projeto
    )
```

**Benefícios esperados:**
- ✅ Reduz tempo de 5min → 10seg
- ✅ Elimina erros de cópia manual
- ✅ Garante prémios calculados corretamente
- ✅ Rastreabilidade (projeto.orcamento_id)
- ✅ Workflow mais profissional

**Ficheiros afetados:**
- `logic/orcamentos.py` - novo método `converter_em_projeto()`
- `logic/projetos.py` - pode precisar de `criar_de_orcamento()`
- `ui/screens/orcamentos.py` - botão + dialog de confirmação
- `database/models/projeto.py` - opcional: adicionar campo `orcamento_id`
- `database/models/orcamento.py` - opcional: adicionar campo `projeto_id`

**Prioridade:** 🟡 Média (TODO.md)

---

## 📅 Datas e Timezone

### Timezone Awareness
**Decisão:** Naive datetimes (sem timezone)
**Data:** Início do projeto
**Motivação:**
- Aplicação local (Portugal apenas)
- Sem necessidade de coordenar timezones
- Simplicidade

**Se internacionalizar:**
- Usar `datetime.timezone.utc`
- Converter para timezone local na UI

---

**Mantido por:** Equipa Agora
**Formato:** ADR simplificado (Architecture Decision Records)
**Última atualização:** 2025-11-13
