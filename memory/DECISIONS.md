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

---

## 💰 Sistema Fiscal: Necessidade Identificada e Estrutura

### Obrigações Legais vs Sistema Actual
**Decisão:** Implementar sistema fiscal completo integrado  
**Data:** 2025-11-15  
**Motivação:**
- Agora Media é sociedade por quotas com obrigações fiscais rigorosas
- Prazos legais têm consequências (coimas, juros)
- Sistema atual não suporta gestão fiscal adequada
- TOC precisa de dados organizados para cumprir obrigações

---

### Problema atual:

**Falta rastreabilidade fiscal:**
- ❌ Sem registo de receitas (faturas emitidas/recebidas)
- ❌ Sem controlo IVA trimestral (liquidado vs dedutível)
- ❌ Sem controlo IRS retido a fornecedores freelancers
- ❌ Sem visibilidade de prazos e obrigações
- ❌ Dados dispersos dificultam trabalho do TOC
- ❌ Risco de incumprimento de prazos

**Consequências:**
- Impossível calcular IVA a pagar trimestralmente
- Impossível saber IRS retido mensalmente
- Impossível estimar IRC anual
- TOC tem que recriar tudo manualmente no software contabilidade
- Risco de erros e omissões

---

### Solução proposta:

**Sistema fiscal integrado com 3 pilares:**

1. **RECEITAS** (tabela nova)
   - Registo de todas as faturas emitidas
   - Estados: EMITIDO → RECEBIDO → CANCELADO
   - Cálculo automático IVA liquidado
   - Link com projetos

2. **IRS RETIDO** (campos novos em despesas/fornecedores)
   - Identificar fornecedores freelancers
   - Calcular automaticamente retenção (23%, 25%, etc)
   - Relatório mensal de IRS a entregar

3. **IVA TRIMESTRAL** (cálculo automático)
   - IVA Liquidado (receitas) - IVA Dedutível (despesas)
   - Apuramento por trimestre
   - Alertas de prazos

---

## 💼 Receitas: Tabela Nova vs Campo em Projetos

### Campo em Projetos vs Tabela Separada
**Decisão:** Criar tabela `receitas` separada  
**Data:** 2025-11-15  
**Motivação:**
- Receitas ≠ Projetos (nem todas receitas são de projetos)
- Projetos podem ter múltiplas receitas (pagamentos faseados)
- Receitas avulsas: subsídios, vendas equipamento, etc

---

**Opções consideradas:**

**OPÇÃO 1 (Descartada):** Adicionar campos em `projetos`
```sql
projetos
├─ valor_facturado: DECIMAL
├─ data_fatura: DATE
├─ data_recebimento: DATE
└─ iva_liquidado: DECIMAL
```
- ❌ Só funciona para 1 receita por projeto (pagamento único)
- ❌ Não suporta pagamentos faseados (50% início, 50% fim)
- ❌ Não suporta receitas avulsas (subsídios, vendas)
- ❌ Mistura conceitos (projeto ≠ receita)
- ❌ Difícil controlo fiscal (IVA trimestral)

**OPÇÃO 2 (Escolhida):** Tabela `receitas` separada
```sql
receitas
├─ numero: #R000001
├─ fatura_numero: Fatura #2025/0001
├─ projeto_id: FK (nullable)
├─ cliente_id: FK
├─ valor_sem_iva: DECIMAL
├─ iva_liquidado: DECIMAL
├─ valor_c_iva: DECIMAL
├─ data_fatura: DATE
├─ data_recebimento: DATE
├─ estado: EMITIDO | RECEBIDO | CANCELADO
└─ tipo: PROJETO | OUTRO
```

**Vantagens:**
- ✅ Suporta múltiplas receitas por projeto
- ✅ Suporta receitas avulsas (sem projeto)
- ✅ Separação clara: projeto (trabalho) vs receita (dinheiro)
- ✅ Controlo fiscal preciso (IVA liquidado por período)
- ✅ Rastreabilidade completa (fatura → receita → projeto)
- ✅ Estados claros (emitido vs recebido)
- ✅ Preparado para integração faturação futura

**Casos de uso:**

**UC1: Pagamento único**
```
Projeto #P0050 (€10.000)
└─ Receita #R0001 (€10.000) - pagamento total
```

**UC2: Pagamentos faseados**
```
Projeto #P0051 (€20.000)
├─ Receita #R0002 (€10.000) - 50% início
└─ Receita #R0003 (€10.000) - 50% entrega
```

**UC3: Receita avulsa**
```
Receita #R0004 (€5.000) - Subsídio COVID-19
└─ projeto_id = NULL
```

**Trade-offs:**
- ❌ Mais uma tabela (complexidade)
- ❌ Precisa UI adicional
- ✅ Arquitetura correta (separação conceitos)
- ✅ Escalável (faturação futura)
- ✅ Compliance fiscal (obrigatório)

---

## 🧾 IRS Retido: Declaração Mensal vs Modelo 10 Anual

### Como Declarar Retenções IRS
**Decisão:** A validar com TOC (pendente)  
**Data:** 2025-11-15  
**Motivação:**
- Agora tem contabilidade organizada
- Paga fornecedores freelancers (recibos verdes)
- Obrigação legal: comunicar retenções à AT

---

**Opções disponíveis:**

**OPÇÃO A: Declaração Mensal (DMR ou equiv.)**
- Declarar retenções todos os meses
- Prazo: até dia 20 do mês seguinte
- Pagar até dia 25 do mês seguinte
- ✅ Fluxo contínuo (mais previsível)
- ✅ Valores menores mensalmente
- ❌ Mais trabalho administrativo (12× por ano)
- ❌ Mais pontos de falha (12 prazos)

**OPÇÃO B: Modelo 10 Anual**
- Declarar todas as retenções do ano de uma vez
- Prazo: até 10 de Fevereiro do ano seguinte
- Prorrogável até fim de Fevereiro
- ✅ Menos trabalho administrativo (1× por ano)
- ✅ Menos prazos para falhar
- ❌ Montante maior de uma vez (cashflow)
- ❌ Concentra risco (se falhar prazo, coima maior)

**RECOMENDAÇÃO PROVISÓRIA:** Mensal
- Mais previsível para fornecedores (recebem declaração mensal)
- Cashflow distribuído ao longo do ano
- Alinhado com IVA trimestral (obrigações regulares)

**DECISÃO FINAL:** Aguarda validação TOC
- TOC pode ter preferência baseada em workflow deles
- Pode haver integração com software contabilidade
- Validar custos de processamento (se houver)

---

## 📊 IVA: Regime de Caixa vs Regime Geral

### Quando Contabilizar IVA
**Decisão:** Regime Geral (IVA à data de emissão fatura)  
**Data:** 2025-11-15  
**Motivação:**
- Regime Geral é o padrão para empresas
- Agora não tem problemas de cashflow graves
- Mais simples de gerir

---

**Opções:**

**OPÇÃO A: Regime Geral (escolhido)**
- IVA liquidado: à data de **emissão** da fatura
- IVA dedutível: à data de **recebimento** da fatura fornecedor
- ✅ Regime padrão (sem pedidos especiais)
- ✅ Mais simples
- ❌ Paga IVA antes de receber do cliente
- ❌ Impacto cashflow (mas Agora aguenta)

**OPÇÃO B: Regime de Caixa (não escolhido)**
- IVA liquidado: à data de **recebimento** do cliente
- IVA dedutível: à data de **pagamento** ao fornecedor
- ✅ Alinha IVA com cashflow
- ✅ Bom para empresas com recebimentos atrasados
- ❌ Requer pedido explícito à AT
- ❌ Obrigações adicionais (controlo recebimentos)
- ❌ Complexidade extra

**Implementação no sistema:**
```python
# Regime Geral
iva_liquidado_trimestre = sum(
    receita.iva_liquidado 
    for receita in receitas
    if receita.data_fatura in trimestre  # Data FATURA
)

# Se fosse Regime Caixa
iva_liquidado_trimestre = sum(
    receita.iva_liquidado 
    for receita in receitas
    if receita.data_recebimento in trimestre  # Data RECEBIMENTO
)
```

**Trade-offs:**
- ❌ Regime Geral pode atrasar cashflow
- ✅ Mas Agora tem margem (não é crítico)
- ✅ Simplicidade > complexidade

---

## 💡 Receitas: Criar ao Emitir Fatura vs Ao Receber Pagamento

### Momento de Criar Receita no Sistema
**Decisão:** Criar ao emitir fatura (estado EMITIDO)  
**Data:** 2025-11-15  
**Motivação:**
- Receita existe quando fatura é emitida (obrigação cliente pagar)
- Permite controlo: receitas emitidas vs recebidas
- Alinhado com Regime Geral de IVA

---

**Opções:**

**OPÇÃO 1 (Escolhida):** Criar ao emitir fatura
```
Fluxo:
1. Projeto #P0050 concluído
2. Emitir fatura → Criar receita (estado=EMITIDO)
3. Cliente paga → Atualizar receita (estado=RECEBIDO, data_recebimento)
```
- ✅ Rastreabilidade completa (faturas emitidas vs recebidas)
- ✅ Permite calcular "receitas a receber" (EMITIDO)
- ✅ Alinhado com IVA (liquidado à emissão)
- ✅ Controlo de cobrança (quantas faturas por receber?)

**OPÇÃO 2 (Não escolhida):** Criar ao receber pagamento
```
Fluxo:
1. Projeto #P0050 concluído
2. Emitir fatura (fora do sistema)
3. Cliente paga → Criar receita (estado=RECEBIDO)
```
- ❌ Perde rastreabilidade (faturas emitidas não registadas)
- ❌ Não permite calcular "receitas a receber"
- ❌ IVA trimestral incorreto (faltam faturas emitidas)

**Implementação:**
```python
# Ao aprovar projeto (marcar PAGO)
def marcar_projeto_pago(projeto):
    # 1. Criar receita (estado EMITIDO)
    receita = Receita(
        projeto_id = projeto.id,
        estado = 'EMITIDO',
        data_fatura = hoje,
        valor_sem_iva = projeto.valor,
        iva_liquidado = projeto.valor * 0.23,
        ...
    )
    
    # 2. Quando cliente pagar
    receita.estado = 'RECEBIDO'
    receita.data_recebimento = data_pagamento
    receita.save()
```

**Relatórios possíveis:**
- Receitas emitidas mas não recebidas (risco cobrança)
- Tempo médio de recebimento (KPI)
- Previsão cashflow (receitas EMITIDO)

---

## 🏢 TOC: Integração Manual vs Automática

### Como Partilhar Dados com TOC
**Decisão:** Começar com exports Excel, evoluir para SAF-T  
**Data:** 2025-11-15  
**Motivação:**
- Pragmatismo: começar simples, evoluir depois
- TOC pode não ter API disponível
- Excel é universal

---

**Roadmap de integração:**

**FASE 1 (Imediato): Exports Excel**
- Receitas mensais (lista completa)
- Despesas mensais (lista completa)
- IVA trimestral (resumo)
- IRS retido mensal (resumo)
- ✅ Simples de implementar
- ✅ TOC pode importar em qualquer software
- ❌ Manual (enviar email com ficheiros)

**FASE 2 (Médio prazo): SAF-T XML**
- Export SAF-T de faturação (standard PT)
- Export SAF-T de contabilidade (se aplicável)
- ✅ Standard aceite por todos software contabilidade
- ✅ Elimina retrabalho TOC
- ❌ Mais complexo de implementar

**FASE 3 (Longo prazo): API/Integração Direta**
- Integração com TOConline ou software contabilidade
- Sincronização automática (tempo real ou diária)
- ✅ Zero trabalho manual
- ✅ Sempre atualizado
- ❌ Depende de API disponível
- ❌ Complexo de manter

**Decisão:** Validar com TOC qual é preferência deles

---

## 🔢 IVA Dedutível: Todas Despesas vs Só Empresariais

### Quais Despesas Têm IVA Dedutível
**Decisão:** TODAS as despesas são empresariais (para efeitos fiscais)  
**Data:** 2025-11-15  
**Motivação:**
- Despesas "pessoais" (BA/RR) são oficialmente empresariais
- Simplifica lógica (não há exceções)
- TOC valida e ajusta se necessário

---

**Princípio:**
```
Para a AT (Autoridade Tributária):
TODAS as despesas da Agora são empresariais
```

**Tipos de despesa (todos dedutíveis):**
- FIXA_MENSAL → empresarial ✅
- PESSOAL_BA → empresarial ✅ (não precisa AT saber)
- PESSOAL_RR → empresarial ✅ (não precisa AT saber)
- EQUIPAMENTO → empresarial ✅
- PROJETO → empresarial ✅

**Cálculo IVA dedutível:**
```python
# TODAS as despesas PAGAS no trimestre
iva_dedutivel = sum(
    despesa.iva_dedutivel
    for despesa in despesas
    if despesa.estado == 'PAGO'
    and despesa.data_pagamento in trimestre
)
# Sem filtro por tipo - TODAS contam
```

**Trade-offs:**
- ✅ Lógica simples
- ✅ Maximiza IVA dedutível
- ⚠️ TOC valida se alguma despesa não é aceite fiscalmente
- ⚠️ Despesas não aceites: TOC faz correção na declaração

**Despesas tipicamente não dedutíveis (TOC trata):**
- Multas
- Coimas
- Despesas sem fatura
- Despesas sem NIF

**Sistema:** Assume tudo dedutível, TOC ajusta se necessário

---

## 📅 Calendário Fiscal: Alertas vs Manual

### Como Gerir Prazos Fiscais
**Decisão:** Implementar sistema de alertas automáticos  
**Data:** 2025-11-15  
**Motivação:**
- Coimas por atraso são caras
- Prazos são fixos e previsíveis
- Alertas previnem esquecimentos

---

**Sistema de alertas:**

**Níveis:**
1. **30 dias antes:** Notificação informativa
2. **7 dias antes:** Alerta amarelo
3. **3 dias antes:** Alerta vermelho
4. **No dia:** Alerta crítico
5. **Após prazo:** Notificação atraso

**Canais:**
- Dashboard badge (contador obrigações pendentes)
- Notificação in-app (popup)
- Email automático (opcional)
- Email para TOC (opcional)

**Obrigações monitorizadas:**
- IVA trimestral (declaração dia 20, pagamento dia 25)
- IRS retido mensal (declaração dia 20, pagamento dia 25)
- Modelo 10 anual (Fevereiro)
- Modelo 22 IRC (Maio)
- SAF-T mensal (dia 5)
- DMR mensal (dia 10)
- Segurança Social (dia 20)

**Implementação:**
```python
def check_alertas_fiscais():
    hoje = date.today()
    alertas = []
    
    # IVA trimestre atual
    trimestre_atual = get_trimestre_atual()
    prazo_declaracao = get_prazo_iva_declaracao(trimestre_atual)
    dias_faltam = (prazo_declaracao - hoje).days
    
    if dias_faltam <= 7:
        alertas.append({
            'tipo': 'IVA',
            'nivel': 'AMARELO' if dias_faltam > 3 else 'VERMELHO',
            'mensagem': f'IVA {trimestre_atual} vence em {dias_faltam} dias',
            'prazo': prazo_declaracao
        })
    
    return alertas
```

---

## 📚 Resumo de Decisões Fiscais

| Decisão | Escolha | Razão |
|---------|---------|-------|
| Receitas | Tabela separada | Múltiplas receitas/projeto, receitas avulsas |
| IRS Retido | A validar com TOC | Mensal vs Modelo 10 anual |
| Regime IVA | Regime Geral | Padrão, mais simples |
| Criar receita | Ao emitir fatura | Rastreabilidade completa |
| Integração TOC | Excel → SAF-T → API | Evoluir progressivamente |
| IVA Dedutível | Todas despesas | Simplificar, TOC ajusta |
| Alertas | Sistema automático | Prevenir coimas |

---



**Mantido por:** Equipa Agora
**Formato:** ADR simplificado (Architecture Decision Records)
_Última atualização: 15/11/2025_  
_Próxima revisão: Após validação com TOC_
