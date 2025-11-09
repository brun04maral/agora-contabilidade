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
**Última atualização:** 2025-11-09
